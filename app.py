"""
app.py — AI Recruitment Intelligence API.

Two evaluation paths:
  1. Groq (llama-3.3-70b-versatile) — used when GROQ_API_KEY is set.
  2. Local SBERT + MLP (recruitment_model.pth) — the trained fallback.

Every verdict is persisted against the signed-in user, so accounts keep their
saved portfolios and their analysis history.
"""

import json
import os
import random

import torch
from dotenv import load_dotenv
from flask import Flask, g, jsonify, request
from flask_cors import CORS
from groq import Groq
from sentence_transformers import SentenceTransformer
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

import PyPDF2
from auth import (
    create_token,
    hash_password,
    require_auth,
    validate_credentials,
    verify_password,
)
from db import get_session, init_db
from models import Analysis, Portfolio, User
from preprocess_data import clean_text
from retrain_v2 import RecruitmentBrain

load_dotenv()

# ─── CONFIG ──────────────────────────────────────────────────────────────────
GROQ_API_KEY = os.getenv("GROQ_API_KEY") or os.getenv("BRAIN_INIT_TOKEN")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
# Random noise on the score. Off by default: analyses are now stored as a
# record, and jitter makes the same input produce a different saved verdict.
# Set DEMO_JITTER=1 to restore the old demo behaviour.
DEMO_JITTER = os.getenv("DEMO_JITTER", "0") == "1"
MAX_UPLOAD_BYTES = 10 * 1024 * 1024
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
    # Support both old-style (plain state_dict) and new-style (dict with threshold)
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


# ─── AUTH ROUTES ─────────────────────────────────────────────────────────────
@app.route("/auth/register", methods=["POST"])
def register():
    data = request.get_json(silent=True) or {}
    name = (data.get("name") or "").strip()
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    error = validate_credentials(email, password, name)
    if error:
        return jsonify({"error": error}), 400

    with get_session() as session:
        if session.scalar(select(User).where(User.email == email)):
            return jsonify({"error": "An account with that email already exists."}), 409

        user = User(email=email, name=name, password_hash=hash_password(password))
        session.add(user)
        try:
            session.commit()
        except IntegrityError:
            # Lost a race with a concurrent signup for the same email.
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


# ─── PORTFOLIO ROUTES ────────────────────────────────────────────────────────
@app.route("/portfolios", methods=["GET"])
@require_auth
def list_portfolios():
    with get_session() as session:
        rows = session.scalars(
            select(Portfolio)
            .where(Portfolio.user_id == g.user_id)
            .order_by(Portfolio.updated_at.desc())
        ).all()
        return jsonify({"portfolios": [p.to_dict() for p in rows]})


@app.route("/portfolios", methods=["POST"])
@require_auth
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
@require_auth
def get_portfolio(portfolio_id: int):
    with get_session() as session:
        portfolio = session.get(Portfolio, portfolio_id)
        if not portfolio or portfolio.user_id != g.user_id:
            return jsonify({"error": "Portfolio not found."}), 404
        return jsonify({"portfolio": portfolio.to_dict()})


@app.route("/portfolios/<int:portfolio_id>", methods=["PUT"])
@require_auth
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
@require_auth
def delete_portfolio(portfolio_id: int):
    with get_session() as session:
        portfolio = session.get(Portfolio, portfolio_id)
        if not portfolio or portfolio.user_id != g.user_id:
            return jsonify({"error": "Portfolio not found."}), 404
        session.delete(portfolio)
        session.commit()
        return jsonify({"deleted": portfolio_id})


# ─── ANALYSIS HISTORY ROUTES ─────────────────────────────────────────────────
@app.route("/analyses", methods=["GET"])
@require_auth
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
@require_auth
def get_analysis(analysis_id: int):
    with get_session() as session:
        analysis = session.get(Analysis, analysis_id)
        if not analysis or analysis.user_id != g.user_id:
            return jsonify({"error": "Analysis not found."}), 404
        return jsonify({"analysis": analysis.to_dict(include_inputs=True)})


@app.route("/analyses/<int:analysis_id>", methods=["DELETE"])
@require_auth
def delete_analysis(analysis_id: int):
    with get_session() as session:
        analysis = session.get(Analysis, analysis_id)
        if not analysis or analysis.user_id != g.user_id:
            return jsonify({"error": "Analysis not found."}), 404
        session.delete(analysis)
        session.commit()
        return jsonify({"deleted": analysis_id})


# ─── CORE PREDICTION ─────────────────────────────────────────────────────────
@app.route("/predict", methods=["POST"])
@require_auth
def predict():
    data = request.get_json(silent=True) or {}
    resume = data.get("resume", "")
    transcript = data.get("transcript", "")
    job_desc = data.get("job_description", "")
    portfolio_id = data.get("portfolio_id")

    if not resume.strip() or not job_desc.strip():
        return jsonify({"error": "A resume and a job description are both required."}), 400

    result = None
    engine = f"groq-{GROQ_MODEL}"

    if _groq_client:
        print(f"🤖 Evaluating via Groq ({GROQ_MODEL})...")
        result = groq_analysis(resume, transcript, job_desc)

    if result is None:
        print("⚡ Falling back to the local SBERT + MLP model...")
        result = local_analysis(resume, transcript, job_desc)
        engine = "local-mlp"

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


# ─── PDF UPLOAD ──────────────────────────────────────────────────────────────
@app.route("/upload_pdf", methods=["POST"])
@require_auth
def upload_pdf():
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

    return jsonify({"text": text})


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
