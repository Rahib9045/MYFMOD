"""
app.py — AI Recruitment Intelligence API.

Two portals share one API:
  RECRUITER — post vacancies, review applicants, screen candidates by hand
  SEEKER    — upload a CV, get ranked matching vacancies, apply

Two evaluation engines:
  1. Local SBERT + MLP (recruitment_model.pth) — ranks one CV against every
     open vacancy in a single batch. Fast enough to score hundreds of jobs.
  2. Groq (llama-3.3-70b-versatile) — the deep write-up for a single pairing.

Ranking many jobs is a batch problem, so it uses the local model; a detailed
verdict on one job is a reasoning problem, so it uses Groq.
"""

import json
import os
import random

import numpy as np
import torch
from dotenv import load_dotenv
from flask import Flask, g, jsonify, request
from flask_cors import CORS
from groq import Groq
from sentence_transformers import SentenceTransformer
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import selectinload

import PyPDF2
from auth import (
    create_token,
    hash_password,
    require_auth,
    require_role,
    validate_credentials,
    verify_password,
)
from db import get_session, init_db
from models import (
    APPLICATION_STATUSES,
    JOB_CLOSED,
    JOB_OPEN,
    ROLE_RECRUITER,
    ROLE_SEEKER,
    VALID_ROLES,
    Analysis,
    Application,
    Job,
    Portfolio,
    User,
)
from preprocess_data import clean_text
from retrain_v2 import RecruitmentBrain

load_dotenv()

# ─── CONFIG ──────────────────────────────────────────────────────────────────
GROQ_API_KEY = os.getenv("GROQ_API_KEY") or os.getenv("BRAIN_INIT_TOKEN")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
# Random noise on the score. Off by default: analyses are now stored as a
# record, and jitter makes the same input produce a different saved verdict.
DEMO_JITTER = os.getenv("DEMO_JITTER", "0") == "1"
MAX_UPLOAD_BYTES = 10 * 1024 * 1024
EMBED_DIM = 384
# ─────────────────────────────────────────────────────────────────────────────

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = MAX_UPLOAD_BYTES

# Only the configured frontends may call this API — it spends real API credit.
_origins = [o.strip() for o in os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")]
CORS(app, resources={r"/*": {"origins": _origins}}, supports_credentials=True)

_groq_client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None

init_db()

print("🧠 Loading the Recruitment Brain (v2)...")
model_sbert = SentenceTransformer("all-MiniLM-L6-v2")
brain = RecruitmentBrain(input_dim=768)
DECISION_THRESHOLD = 0.5  # overridden by the threshold saved in the checkpoint

if os.path.exists("recruitment_model.pth"):
    checkpoint = torch.load("recruitment_model.pth", map_location="cpu")
    if isinstance(checkpoint, dict) and "model_state" in checkpoint:
        brain.load_state_dict(checkpoint["model_state"])
        DECISION_THRESHOLD = checkpoint.get("threshold", 0.5)
        print(f"✨ v2 Model loaded | Threshold = {DECISION_THRESHOLD}")
    else:
        brain.load_state_dict(checkpoint)
        print("✨ v1 Model loaded | Threshold = 0.5 (default)")
    brain.eval()
else:
    print("⚠️ WARNING: No model weights found. Local predictions will be random!")

print(f"🤖 Groq engine: {'ENABLED (' + GROQ_MODEL + ')' if _groq_client else 'DISABLED — using local MLP'}")


# ─── EMBEDDING HELPERS ───────────────────────────────────────────────────────
def encode(texts: list[str]) -> np.ndarray:
    """SBERT-encode a batch of texts to float32 vectors."""
    return model_sbert.encode(texts, convert_to_numpy=True, batch_size=32).astype(np.float32)


def compute_job_embedding(job: Job) -> bytes:
    """Encode a vacancy and return raw bytes for the cached column."""
    return encode([clean_text(job.match_text())])[0].tobytes()


def decode_embedding(raw: bytes) -> np.ndarray:
    return np.frombuffer(raw, dtype=np.float32)


def rank_jobs_for_cv(cv_text: str, jobs: list[Job]) -> list[dict]:
    """Score one CV against many vacancies in a single batched pass.

    Returns two independent numbers per job:

      relevance — raw cosine similarity between the CV and job embeddings:
                  "is this the same kind of work?" This drives the ranking.
      fit       — the trained MLP's selection probability: "would this
                  candidate be picked for it?" Advisory only.

    Ranking deliberately uses relevance alone. The MLP was trained on the
    Kaggle resume/transcript-vs-prose-job-description distribution, and a short
    CV against a short structured vacancy is out of distribution for it — in
    practice it returns near-zero for every job, including obviously good
    matches, so blending it in only compresses the scale without reordering
    anything. It is still returned so the UI can show it and so the gap stays
    visible rather than hidden inside a combined number.

    Cosine is used raw rather than rescaled from [-1, 1] to [0, 1]. Sentence
    embeddings are rarely negative, so that rescale just squashes everything
    into the top half and makes an unrelated job look like a 0.6 match.
    """
    if not jobs:
        return []

    cv_vec = encode([clean_text(cv_text)])[0]

    job_matrix = np.stack([decode_embedding(job.embedding) for job in jobs])
    cv_matrix = np.tile(cv_vec, (len(jobs), 1))

    cv_norm = np.linalg.norm(cv_vec) or 1.0
    job_norms = np.linalg.norm(job_matrix, axis=1)
    job_norms[job_norms == 0] = 1.0
    relevance = np.clip((job_matrix @ cv_vec) / (job_norms * cv_norm), 0.0, 1.0)

    # The MLP expects the same concatenation order used in training.
    with torch.no_grad():
        features = torch.from_numpy(np.hstack([cv_matrix, job_matrix]))
        fit = brain.predict_proba(features).squeeze(-1).numpy()

    results = []
    for i, job in enumerate(jobs):
        results.append(
            {
                "job": job,
                "relevance": round(float(relevance[i]), 4),
                "fit": round(float(fit[i]), 4),
                "match_score": round(float(relevance[i]), 4),
            }
        )

    results.sort(key=lambda r: r["match_score"], reverse=True)
    return results


# ─── EVALUATION ENGINES ──────────────────────────────────────────────────────
def groq_analysis(resume: str, transcript: str, job_desc: str) -> dict | None:
    """Ask the Groq-hosted LLM for a hiring verdict. Returns None on failure."""
    prompt = f"""
    You are an expert AI Recruiter. Analyze the following candidate and job description.

    JOB DESCRIPTION:
    {job_desc}

    CANDIDATE RESUME:
    {resume}

    INTERVIEW TRANSCRIPT:
    {transcript}

    TASKS:
    1. Determine a selection probability (0.0001 to 0.9999) with 4 decimal places.
    2. Decide if the candidate should be "SELECT" or "REJECT".
    3. Advice: If decision is "SELECT", give 2 specific resume improvement points.
       If decision is "REJECT" and the role is a total mismatch (e.g. Accountant vs Chef),
       the advice MUST be "Resume does not match the core job category."

    Respond with ONLY a JSON object in this exact shape:
    {{
      "probability": float,
      "decision": "SELECT" or "REJECT",
      "advice": "Your advice string here"
    }}
    """
    try:
        response = _groq_client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": "You are a professional HR intelligence system. Be decisive and precise. Always reply with valid JSON.",
                },
                {"role": "user", "content": prompt},
            ],
            response_format={"type": "json_object"},
            temperature=0.3,
        )
        result = json.loads(response.choices[0].message.content)

        # Never trust the model's shape — coerce and clamp before it reaches the DB.
        probability = float(result["probability"])
        if probability > 1:  # some models answer in percent
            probability /= 100
        probability = min(0.9999, max(0.0001, probability))
        decision = "SELECT" if str(result.get("decision", "")).upper() == "SELECT" else "REJECT"

        return {
            "probability": probability,
            "decision": decision,
            "advice": str(result.get("advice", "")).strip(),
        }
    except Exception as exc:
        print(f"❌ Groq engine error: {type(exc).__name__}: {exc}")
        return None


def local_analysis(resume: str, transcript: str, job_desc: str) -> dict:
    """Score with the locally trained SBERT + MLP model."""
    cand_text = clean_text(resume + " " + transcript)
    job_text = clean_text(job_desc)

    with torch.no_grad():
        cand_emb = model_sbert.encode([cand_text], convert_to_tensor=True)
        job_emb = model_sbert.encode([job_text], convert_to_tensor=True)
        full_emb = torch.cat((cand_emb, job_emb), dim=1)
        probability = float(brain.predict_proba(full_emb).item())

    return {
        "probability": probability,
        "decision": "SELECT" if probability >= DECISION_THRESHOLD else "REJECT",
        "advice": "Focus on aligning specific keywords from the Job Description into your 'Skills' section.",
    }


def evaluate(resume: str, transcript: str, job_desc: str) -> tuple[dict, str]:
    """Run the best available engine. Returns (result, engine_name)."""
    if _groq_client:
        result = groq_analysis(resume, transcript, job_desc)
        if result is not None:
            return result, f"groq-{GROQ_MODEL}"
    return local_analysis(resume, transcript, job_desc), "local-mlp"


# ─── AUTH ROUTES ─────────────────────────────────────────────────────────────
@app.route("/auth/register", methods=["POST"])
def register():
    data = request.get_json(silent=True) or {}
    name = (data.get("name") or "").strip()
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""
    role = (data.get("role") or ROLE_RECRUITER).strip().lower()
    company = (data.get("company") or "").strip()

    error = validate_credentials(email, password, name)
    if error:
        return jsonify({"error": error}), 400
    if role not in VALID_ROLES:
        return jsonify({"error": f"Role must be one of: {', '.join(VALID_ROLES)}."}), 400

    with get_session() as session:
        if session.scalar(select(User).where(User.email == email)):
            return jsonify({"error": "An account with that email already exists."}), 409

        user = User(
            email=email,
            name=name,
            password_hash=hash_password(password),
            role=role,
            company=company if role == ROLE_RECRUITER else "",
        )
        session.add(user)
        try:
            session.commit()
        except IntegrityError:
            session.rollback()
            return jsonify({"error": "An account with that email already exists."}), 409

        return jsonify({"token": create_token(user.id), "user": user.to_dict()}), 201


@app.route("/auth/login", methods=["POST"])
def login():
    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    with get_session() as session:
        user = session.scalar(select(User).where(User.email == email))
        # Same message either way, so this can't be used to enumerate accounts.
        if not user or not verify_password(password, user.password_hash):
            return jsonify({"error": "Invalid email or password."}), 401

        return jsonify({"token": create_token(user.id), "user": user.to_dict()})


@app.route("/auth/me", methods=["GET"])
@require_auth
def me():
    with get_session() as session:
        user = session.get(User, g.user_id)
        if not user:
            return jsonify({"error": "Account no longer exists."}), 401
        return jsonify({"user": user.to_dict()})


# ─── RECRUITER: JOB POSTING ──────────────────────────────────────────────────
_JOB_TEXT_FIELDS = (
    "title",
    "company",
    "location",
    "employment_type",
    "description",
    "requirements",
    "skills",
    "experience_level",
    "salary_range",
)


def _job_payload(data: dict) -> dict:
    """Normalize an incoming job body. `skills` accepts a list or a string."""
    payload = {}
    for field in _JOB_TEXT_FIELDS:
        if field not in data:
            continue
        value = data[field]
        if field == "skills" and isinstance(value, list):
            value = ", ".join(str(s).strip() for s in value if str(s).strip())
        payload[field] = str(value or "").strip()
    return payload


@app.route("/jobs", methods=["POST"])
@require_role(ROLE_RECRUITER)
def create_job():
    data = request.get_json(silent=True) or {}
    payload = _job_payload(data)

    if not payload.get("title"):
        return jsonify({"error": "A job title is required."}), 400
    if not payload.get("description") and not payload.get("requirements"):
        return jsonify({"error": "Add a description or a list of requirements."}), 400

    with get_session() as session:
        recruiter = session.get(User, g.user_id)
        job = Job(recruiter_id=g.user_id, **payload)
        # Fall back to the recruiter's own company name if they left it blank.
        if not job.company:
            job.company = recruiter.company or ""
        job.embedding = compute_job_embedding(job)
        session.add(job)
        session.commit()
        return jsonify({"job": job.to_dict(include_counts=True)}), 201


@app.route("/jobs/mine", methods=["GET"])
@require_role(ROLE_RECRUITER)
def my_jobs():
    with get_session() as session:
        jobs = session.scalars(
            select(Job)
            .where(Job.recruiter_id == g.user_id)
            .options(selectinload(Job.applications))
            .order_by(Job.created_at.desc())
        ).all()
        return jsonify({"jobs": [j.to_dict(include_counts=True) for j in jobs]})


@app.route("/jobs", methods=["GET"])
@require_auth
def browse_jobs():
    """Every open vacancy. Both roles can browse."""
    with get_session() as session:
        jobs = session.scalars(
            select(Job).where(Job.status == JOB_OPEN).order_by(Job.created_at.desc())
        ).all()
        return jsonify({"jobs": [j.to_dict() for j in jobs]})


@app.route("/jobs/<int:job_id>", methods=["GET"])
@require_auth
def get_job(job_id: int):
    with get_session() as session:
        job = session.get(Job, job_id)
        if not job:
            return jsonify({"error": "Job not found."}), 404
        return jsonify({"job": job.to_dict(include_counts=True)})


@app.route("/jobs/<int:job_id>", methods=["PUT"])
@require_role(ROLE_RECRUITER)
def update_job(job_id: int):
    data = request.get_json(silent=True) or {}
    with get_session() as session:
        job = session.get(Job, job_id)
        if not job or job.recruiter_id != g.user_id:
            return jsonify({"error": "Job not found."}), 404

        payload = _job_payload(data)
        for field, value in payload.items():
            setattr(job, field, value)

        if "status" in data:
            status = str(data["status"]).lower()
            if status not in (JOB_OPEN, JOB_CLOSED):
                return jsonify({"error": f"Status must be {JOB_OPEN} or {JOB_CLOSED}."}), 400
            job.status = status

        if not job.title.strip():
            return jsonify({"error": "A job title is required."}), 400

        # Any text change invalidates the cached embedding.
        if payload:
            job.embedding = compute_job_embedding(job)

        session.commit()
        return jsonify({"job": job.to_dict(include_counts=True)})


@app.route("/jobs/<int:job_id>", methods=["DELETE"])
@require_role(ROLE_RECRUITER)
def delete_job(job_id: int):
    with get_session() as session:
        job = session.get(Job, job_id)
        if not job or job.recruiter_id != g.user_id:
            return jsonify({"error": "Job not found."}), 404
        session.delete(job)
        session.commit()
        return jsonify({"deleted": job_id})


@app.route("/jobs/<int:job_id>/applications", methods=["GET"])
@require_role(ROLE_RECRUITER)
def job_applications(job_id: int):
    """Applicants for one of my vacancies, best match first."""
    with get_session() as session:
        job = session.get(Job, job_id)
        if not job or job.recruiter_id != g.user_id:
            return jsonify({"error": "Job not found."}), 404

        applications = session.scalars(
            select(Application)
            .where(Application.job_id == job_id)
            .options(selectinload(Application.seeker))
            .order_by(Application.match_score.desc())
        ).all()

        return jsonify(
            {
                "job": job.to_dict(),
                "applications": [a.to_dict(include_cv=True) for a in applications],
            }
        )


@app.route("/applications/<int:application_id>", methods=["PATCH"])
@require_role(ROLE_RECRUITER)
def update_application_status(application_id: int):
    data = request.get_json(silent=True) or {}
    status = str(data.get("status", "")).lower()
    if status not in APPLICATION_STATUSES:
        return jsonify({"error": f"Status must be one of: {', '.join(APPLICATION_STATUSES)}."}), 400

    with get_session() as session:
        application = session.get(Application, application_id)
        # Only the recruiter who owns the vacancy may move an applicant along.
        if not application or application.job.recruiter_id != g.user_id:
            return jsonify({"error": "Application not found."}), 404

        application.status = status
        session.commit()
        return jsonify({"application": application.to_dict(include_cv=True)})


# ─── SEEKER: CV, MATCHING, APPLYING ──────────────────────────────────────────
@app.route("/cv", methods=["GET"])
@require_role(ROLE_SEEKER)
def get_cv():
    with get_session() as session:
        user = session.get(User, g.user_id)
        return jsonify({"cv_text": user.cv_text or "", "cv_filename": user.cv_filename or ""})


@app.route("/cv", methods=["PUT"])
@require_role(ROLE_SEEKER)
def save_cv():
    data = request.get_json(silent=True) or {}
    cv_text = (data.get("cv_text") or "").strip()
    if not cv_text:
        return jsonify({"error": "CV text is empty."}), 400

    with get_session() as session:
        user = session.get(User, g.user_id)
        user.cv_text = cv_text
        user.cv_filename = (data.get("cv_filename") or user.cv_filename or "").strip()
        session.commit()
        return jsonify({"saved": True, "user": user.to_dict()})


@app.route("/match", methods=["POST"])
@require_role(ROLE_SEEKER)
def match_jobs():
    """Rank every open vacancy against the seeker's CV."""
    data = request.get_json(silent=True) or {}
    limit = min(int(data.get("limit", 20)), 100)

    with get_session() as session:
        user = session.get(User, g.user_id)
        cv_text = (data.get("cv_text") or user.cv_text or "").strip()
        if not cv_text:
            return jsonify({"error": "Upload or paste a CV first."}), 400

        # Persist the CV so the seeker doesn't have to re-upload next visit.
        if data.get("save_cv") and data.get("cv_text"):
            user.cv_text = cv_text
            if data.get("cv_filename"):
                user.cv_filename = data["cv_filename"]

        jobs = session.scalars(select(Job).where(Job.status == JOB_OPEN)).all()
        if not jobs:
            session.commit()
            return jsonify({"matches": [], "total_open_jobs": 0})

        # Backfill any vacancy missing a cached embedding (e.g. rows created
        # before caching existed, or a failed earlier write).
        stale = [j for j in jobs if not j.embedding or len(j.embedding) != EMBED_DIM * 4]
        if stale:
            vectors = encode([clean_text(j.match_text()) for j in stale])
            for job, vector in zip(stale, vectors):
                job.embedding = vector.tobytes()
            print(f"🔧 Backfilled embeddings for {len(stale)} job(s)")

        ranked = rank_jobs_for_cv(cv_text, jobs)

        # Mark the ones already applied to, so the UI can disable the button.
        applied_ids = set(
            session.scalars(
                select(Application.job_id).where(Application.seeker_id == g.user_id)
            ).all()
        )

        session.commit()

        matches = []
        for entry in ranked[:limit]:
            job = entry["job"]
            matches.append(
                {
                    **job.to_dict(),
                    "match_score": entry["match_score"],
                    "relevance": entry["relevance"],
                    "fit": entry["fit"],
                    "already_applied": job.id in applied_ids,
                }
            )

        return jsonify({"matches": matches, "total_open_jobs": len(jobs)})


@app.route("/jobs/<int:job_id>/analyze", methods=["POST"])
@require_role(ROLE_SEEKER)
def analyze_against_job(job_id: int):
    """Groq deep-dive: how does my CV stack up against this one vacancy?"""
    data = request.get_json(silent=True) or {}

    with get_session() as session:
        job = session.get(Job, job_id)
        if not job or job.status != JOB_OPEN:
            return jsonify({"error": "Job not found."}), 404

        user = session.get(User, g.user_id)
        cv_text = (data.get("cv_text") or user.cv_text or "").strip()
        if not cv_text:
            return jsonify({"error": "Upload or paste a CV first."}), 400

        job_text = f"{job.title}\n{job.description}\n\nRequirements:\n{job.requirements}\n\nSkills: {job.skills}"

    result, engine = evaluate(cv_text, "", job_text)
    return jsonify(
        {
            "job_id": job_id,
            "probability": round(result["probability"] * 100, 2),
            "decision": result["decision"],
            "advice": result["advice"],
            "engine": engine,
        }
    )


@app.route("/jobs/<int:job_id>/apply", methods=["POST"])
@require_role(ROLE_SEEKER)
def apply_to_job(job_id: int):
    data = request.get_json(silent=True) or {}

    with get_session() as session:
        job = session.get(Job, job_id)
        if not job:
            return jsonify({"error": "Job not found."}), 404
        if job.status != JOB_OPEN:
            return jsonify({"error": "This vacancy is closed."}), 400

        user = session.get(User, g.user_id)
        cv_text = (data.get("cv_text") or user.cv_text or "").strip()
        if not cv_text:
            return jsonify({"error": "Upload or paste a CV before applying."}), 400

        if session.scalar(
            select(Application).where(
                Application.job_id == job_id, Application.seeker_id == g.user_id
            )
        ):
            return jsonify({"error": "You have already applied to this vacancy."}), 409

        if not job.embedding:
            job.embedding = compute_job_embedding(job)

        score = rank_jobs_for_cv(cv_text, [job])[0]["match_score"]

        application = Application(
            job_id=job_id,
            seeker_id=g.user_id,
            cv_text=cv_text,
            cover_note=(data.get("cover_note") or "").strip(),
            match_score=score,
        )
        session.add(application)
        try:
            session.commit()
        except IntegrityError:
            # Lost a race with a double-submit.
            session.rollback()
            return jsonify({"error": "You have already applied to this vacancy."}), 409

        return jsonify({"application": application.to_dict(include_job=True)}), 201


@app.route("/applications/mine", methods=["GET"])
@require_role(ROLE_SEEKER)
def my_applications():
    with get_session() as session:
        applications = session.scalars(
            select(Application)
            .where(Application.seeker_id == g.user_id)
            .options(selectinload(Application.job))
            .order_by(Application.created_at.desc())
        ).all()
        return jsonify({"applications": [a.to_dict(include_job=True) for a in applications]})


# ─── RECRUITER: MANUAL SCREENING (portfolios + analyses) ─────────────────────
@app.route("/portfolios", methods=["GET"])
@require_role(ROLE_RECRUITER)
def list_portfolios():
    with get_session() as session:
        rows = session.scalars(
            select(Portfolio)
            .where(Portfolio.user_id == g.user_id)
            .order_by(Portfolio.updated_at.desc())
        ).all()
        return jsonify({"portfolios": [p.to_dict() for p in rows]})


@app.route("/portfolios", methods=["POST"])
@require_role(ROLE_RECRUITER)
def create_portfolio():
    data = request.get_json(silent=True) or {}
    title = (data.get("title") or "").strip()
    if not title:
        return jsonify({"error": "A title is required."}), 400

    with get_session() as session:
        portfolio = Portfolio(
            user_id=g.user_id,
            title=title,
            resume=data.get("resume", ""),
            transcript=data.get("transcript", ""),
            job_description=data.get("job_description", ""),
        )
        session.add(portfolio)
        session.commit()
        return jsonify({"portfolio": portfolio.to_dict()}), 201


@app.route("/portfolios/<int:portfolio_id>", methods=["GET"])
@require_role(ROLE_RECRUITER)
def get_portfolio(portfolio_id: int):
    with get_session() as session:
        portfolio = session.get(Portfolio, portfolio_id)
        if not portfolio or portfolio.user_id != g.user_id:
            return jsonify({"error": "Portfolio not found."}), 404
        return jsonify({"portfolio": portfolio.to_dict()})


@app.route("/portfolios/<int:portfolio_id>", methods=["PUT"])
@require_role(ROLE_RECRUITER)
def update_portfolio(portfolio_id: int):
    data = request.get_json(silent=True) or {}
    with get_session() as session:
        portfolio = session.get(Portfolio, portfolio_id)
        if not portfolio or portfolio.user_id != g.user_id:
            return jsonify({"error": "Portfolio not found."}), 404

        for field in ("title", "resume", "transcript", "job_description"):
            if field in data:
                setattr(portfolio, field, data[field])
        if not portfolio.title.strip():
            return jsonify({"error": "A title is required."}), 400

        session.commit()
        return jsonify({"portfolio": portfolio.to_dict()})


@app.route("/portfolios/<int:portfolio_id>", methods=["DELETE"])
@require_role(ROLE_RECRUITER)
def delete_portfolio(portfolio_id: int):
    with get_session() as session:
        portfolio = session.get(Portfolio, portfolio_id)
        if not portfolio or portfolio.user_id != g.user_id:
            return jsonify({"error": "Portfolio not found."}), 404
        session.delete(portfolio)
        session.commit()
        return jsonify({"deleted": portfolio_id})


@app.route("/analyses", methods=["GET"])
@require_role(ROLE_RECRUITER)
def list_analyses():
    limit = min(int(request.args.get("limit", 50)), 200)
    with get_session() as session:
        rows = session.scalars(
            select(Analysis)
            .where(Analysis.user_id == g.user_id)
            .order_by(Analysis.created_at.desc())
            .limit(limit)
        ).all()
        return jsonify({"analyses": [a.to_dict() for a in rows]})


@app.route("/analyses/<int:analysis_id>", methods=["GET"])
@require_role(ROLE_RECRUITER)
def get_analysis(analysis_id: int):
    with get_session() as session:
        analysis = session.get(Analysis, analysis_id)
        if not analysis or analysis.user_id != g.user_id:
            return jsonify({"error": "Analysis not found."}), 404
        return jsonify({"analysis": analysis.to_dict(include_inputs=True)})


@app.route("/analyses/<int:analysis_id>", methods=["DELETE"])
@require_role(ROLE_RECRUITER)
def delete_analysis(analysis_id: int):
    with get_session() as session:
        analysis = session.get(Analysis, analysis_id)
        if not analysis or analysis.user_id != g.user_id:
            return jsonify({"error": "Analysis not found."}), 404
        session.delete(analysis)
        session.commit()
        return jsonify({"deleted": analysis_id})


@app.route("/predict", methods=["POST"])
@require_role(ROLE_RECRUITER)
def predict():
    data = request.get_json(silent=True) or {}
    resume = data.get("resume", "")
    transcript = data.get("transcript", "")
    job_desc = data.get("job_description", "")
    portfolio_id = data.get("portfolio_id")

    if not resume.strip() or not job_desc.strip():
        return jsonify({"error": "A resume and a job description are both required."}), 400

    result, engine = evaluate(resume, transcript, job_desc)

    probability = result["probability"]
    if DEMO_JITTER and 0 < probability < 1:
        probability = min(0.9999, max(0.0001, probability + random.uniform(-0.02, 0.02)))

    # Only link a portfolio the caller actually owns.
    with get_session() as session:
        if portfolio_id is not None:
            owned = session.get(Portfolio, portfolio_id)
            if not owned or owned.user_id != g.user_id:
                portfolio_id = None

        analysis = Analysis(
            user_id=g.user_id,
            portfolio_id=portfolio_id,
            resume=resume,
            transcript=transcript,
            job_description=job_desc,
            probability=probability,
            decision=result["decision"],
            advice=result["advice"],
            engine=engine,
        )
        session.add(analysis)
        session.commit()
        analysis_id = analysis.id

    print(f"Final Score: {result['decision']} ({probability:.6f}) via {engine}")

    return jsonify(
        {
            "analysis_id": analysis_id,
            "probability": round(probability * 100, 5),
            "decision": result["decision"],
            "advice": result["advice"],
            "engine": engine,
            "message": f"Analyzed candidate with a {probability * 100:.2f}% match score.",
        }
    )


# ─── SHARED ──────────────────────────────────────────────────────────────────
@app.route("/upload_pdf", methods=["POST"])
@require_auth
def upload_pdf():
    """Extract text from a PDF. Used for recruiter resumes and seeker CVs."""
    if "file" not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400
    if not file.filename.lower().endswith(".pdf"):
        return jsonify({"error": "Only PDF files are supported"}), 400

    try:
        reader = PyPDF2.PdfReader(file)
        text = "".join(page.extract_text() or "" for page in reader.pages)
    except Exception as exc:
        return jsonify({"error": f"Could not read that PDF: {type(exc).__name__}"}), 400

    if not text.strip():
        return jsonify({"error": "No text found — this PDF may be a scanned image."}), 400

    return jsonify({"text": text, "filename": file.filename})


@app.route("/health", methods=["GET"])
def health():
    return jsonify(
        {
            "status": "ok",
            "engine": f"groq-{GROQ_MODEL}" if _groq_client else "local-mlp",
            "threshold": DECISION_THRESHOLD,
        }
    )


@app.errorhandler(413)
def too_large(_error):
    return jsonify({"error": "File is too large (10 MB max)."}), 413


if __name__ == "__main__":
    print("\n🚀 RECRUITMENT INTELLIGENCE SERVER RUNNING")
    print("Backend Endpoint: http://0.0.0.0:5000")
    app.run(host="0.0.0.0", port=5000)
