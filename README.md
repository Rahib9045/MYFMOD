# 🧠 AI Recruitment Intelligence System

An HR screening tool that matches candidate resumes and interview transcripts against job
descriptions. Users sign in, save candidate portfolios, and keep a permanent history of every
evaluation the system produces.

---

## 📋 Table of Contents

- [Architecture](#-architecture)
- [Prerequisites](#-prerequisites)
- [Step 1: Get a Groq API Key](#step-1-get-a-groq-api-key)
- [Step 2: Create your `.env` file](#step-2-create-your-env-file)
- [Step 3: Run it](#step-3-run-it)
- [Step 4: First-run walkthrough](#step-4-first-run-walkthrough)
- [Configuration reference](#️-configuration-reference)
- [API reference](#-api-reference)
- [Project structure](#-project-structure)
- [Database](#️-database)
- [Troubleshooting](#-troubleshooting)
- [The local model](#-the-local-model)
- [Educational docs](#-educational-journey-lessons--docs)

---

## 🏗️ Architecture

| Layer | What it does |
| :--- | :--- |
| **Next.js frontend** | Sign-in, dashboard, saved portfolios, analysis history |
| **Flask API** | Auth (JWT), portfolio CRUD, evaluation endpoints |
| **Database** | SQLite by default (`DATABASE_URL` swaps in Postgres) |
| **Groq LLM** | `llama-3.3-70b-versatile` — the primary evaluation engine |
| **Local SBERT + MLP** | `recruitment_model.pth` — the trained fallback engine |

The API tries Groq first. If no `GROQ_API_KEY` is set, or the Groq call fails for any reason, it
falls back to the locally trained model automatically. Every response reports which engine
produced it in the `engine` field, and that value is stored alongside the result — so you can
always tell how any given verdict was reached.

---

## ✅ Prerequisites

| Requirement | Version | Notes |
| :--- | :--- | :--- |
| **Python** | 3.11+ | Needed for the backend |
| **Node.js** | 20.9+ | Required by Next.js 16 |
| **Groq API key** | — | Free at [console.groq.com](https://console.groq.com/keys) |
| **Docker** | optional | Only for the one-command path |

You do **not** need a GPU. The local model runs on CPU.

---

## Step 1: Get a Groq API Key

1. Sign up at [console.groq.com](https://console.groq.com).
2. Go to **API Keys** → **Create API Key**.
3. Copy the key (it starts with `gsk_`). You only see it once.

> The app still runs without a key — it just falls back to the local MLP model for every
> evaluation, which is less accurate at spotting role mismatches.

---

## Step 2: Create your `.env` file

Copy the template:

```bash
# macOS / Linux
cp .env.example .env

# Windows (PowerShell)
Copy-Item .env.example .env
```

Open `.env` and fill in two values:

```ini
GROQ_API_KEY=gsk_your_key_here
JWT_SECRET=paste_a_generated_secret_here
```

Generate the `JWT_SECRET` with:

```bash
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

> **`JWT_SECRET` signs login tokens.** If you leave it blank the app generates a temporary one at
> startup and prints a warning — everything works, but every restart logs all users out. Changing
> this value later also logs everyone out.

**Never commit `.env`.** It is already in `.gitignore`, along with `frontend/.env.local` and
`*.db`.

---

## Step 3: Run it

### Option A — Docker (one command)

```bash
docker compose up --build
```

That's it. The database lives in a named volume, so accounts and saved portfolios survive
`docker compose down`.

### Option B — Run locally (two terminals)

**Terminal 1 — backend:**

```bash
pip install -r requirements.txt
python app.py
```

Wait for this output (the first run downloads the SBERT model, ~90 MB):

```
✨ v2 Model loaded | Threshold = 0.2
🤖 Groq engine: ENABLED (llama-3.3-70b-versatile)
🚀 RECRUITMENT INTELLIGENCE SERVER RUNNING
```

If it says `Groq engine: DISABLED`, your `GROQ_API_KEY` is missing or wasn't picked up.

**Terminal 2 — frontend:**

```bash
cd frontend
npm install
npm run dev
```

### Where things run

| Service | URL |
| :--- | :--- |
| Frontend | http://localhost:3000 |
| API | http://localhost:5000 |
| Health check | http://localhost:5000/health |

---

## Step 4: First-run walkthrough

1. Open **http://localhost:3000/register**.
2. Create an account — any email works; the password must be at least 8 characters. There's no
   email verification, so you land straight on the dashboard.
3. Click **🎲 Randomize Case** to load a sample candidate and job from
   `frontend/public/verified_templates.json`. (Or paste your own text, or click **Upload PDF** to
   pull a resume out of a PDF.)
4. Click **Begin Deep Analysis**. You'll get a SELECT/REJECT verdict, a confidence score, and
   recruiter's advice — and it appears in **Analysis History** automatically.
5. Click **Save Portfolio**, name it, and press Enter. It shows up in **Saved Portfolios**; click
   it any time to reload that candidate into the form.
6. Reload the page or sign out and back in — everything is still there. It's in the database, not
   the browser.

To confirm the pieces are wired up, `http://localhost:5000/health` should return:

```json
{"status": "ok", "engine": "groq-llama-3.3-70b-versatile", "threshold": 0.2}
```

---

## ⚙️ Configuration reference

All backend settings live in `.env` (template: `.env.example`).

| Variable | Default | Purpose |
| :--- | :--- | :--- |
| `GROQ_API_KEY` | — | Groq API key. Without it the app uses the local MLP only. |
| `GROQ_MODEL` | `llama-3.3-70b-versatile` | Any chat model available on your Groq account. |
| `JWT_SECRET` | random per boot | Signs login tokens. Set it, or restarts log everyone out. |
| `DATABASE_URL` | `sqlite:///recruitment.db` | Use `postgresql+psycopg://user:pass@host/db` for Postgres. |
| `CORS_ORIGINS` | `http://localhost:3000` | Comma-separated origins allowed to call the API. |
| `DEMO_JITTER` | `0` | Set to `1` to add ±2% random noise to every score. Off by default so a saved result is reproducible. |

The frontend reads `NEXT_PUBLIC_API_URL` from `frontend/.env.local` (defaults to
`http://localhost:5000`).

> `BRAIN_INIT_TOKEN` from earlier versions is still accepted as a fallback name for
> `GROQ_API_KEY`, so old `.env` files keep working.

---

## 🔌 API reference

All routes except `/auth/register`, `/auth/login`, and `/health` require an
`Authorization: Bearer <token>` header.

| Method | Route | Purpose |
| :--- | :--- | :--- |
| `POST` | `/auth/register` | Create an account → `{token, user}` |
| `POST` | `/auth/login` | Sign in → `{token, user}` |
| `GET` | `/auth/me` | Current user |
| `GET` `POST` | `/portfolios` | List / create saved candidate profiles |
| `GET` `PUT` `DELETE` | `/portfolios/<id>` | Read / update / delete one |
| `POST` | `/predict` | Evaluate a candidate; the result is saved automatically |
| `GET` | `/analyses` | Analysis history, newest first (`?limit=N`, max 200) |
| `GET` `DELETE` | `/analyses/<id>` | Full record (with inputs) / delete |
| `POST` | `/upload_pdf` | Extract text from a resume PDF (10 MB max) |
| `GET` | `/health` | Status and active engine |

Portfolios and analyses are scoped to their owner — another account gets a `404`, not the data.

### Example

```bash
# Register and capture the token
TOKEN=$(curl -s -X POST http://localhost:5000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"name":"Ada","email":"ada@example.com","password":"supersecret123"}' \
  | python -c "import sys,json; print(json.load(sys.stdin)['token'])")

# Run an evaluation
curl -s -X POST http://localhost:5000/predict \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"resume":"5 years SQL, Python, Tableau.","transcript":"","job_description":"Data Analyst: SQL, dashboards."}'
```

---

## 📁 Project structure

```
.
├── app.py                  # Flask API — auth, portfolios, analyses, prediction
├── models.py               # SQLAlchemy tables: users, portfolios, analyses
├── db.py                   # Engine + session setup
├── auth.py                 # Password hashing, JWT, @require_auth guard
├── preprocess_data.py      # Text cleaning used at train and inference time
├── retrain_v2.py           # Training script + the RecruitmentBrain model class
├── recruitment_model.pth   # Trained weights (threshold baked in)
├── requirements.txt
├── .env.example            # Config template — copy to .env
├── docker-compose.yml      # Backend + frontend + DB volume
├── Dockerfile              # Backend image
├── frontend/
│   ├── src/lib/api.ts      # All API calls + token handling
│   ├── src/app/login/      # Sign in
│   ├── src/app/register/   # Sign up
│   ├── src/app/dashboard/  # Main workspace
│   └── public/verified_templates.json   # Sample candidates for "Randomize Case"
├── docs/                   # Lessons, guides, final report
└── archive/dataset.csv     # Training data (not tracked)
```

---

## 🗄️ Database

Three tables, created automatically on first boot (`models.py`):

- **`users`** — email, name, hashed password
- **`portfolios`** — a saved candidate profile (resume, transcript, job description)
- **`analyses`** — every verdict: score, decision, advice, and which engine produced it

**To reset everything:**

```bash
# Local
rm recruitment.db          # PowerShell: Remove-Item recruitment.db

# Docker — find the exact name with `docker volume ls | grep recruitment-db`
docker compose down
docker volume rm <project>_recruitment-db
```

**To switch to Postgres**, change one line in `.env` — no code changes needed:

```ini
DATABASE_URL=postgresql+psycopg://user:password@localhost/recruitment
```

---

## 🔧 Troubleshooting

| Symptom | Fix |
| :--- | :--- |
| `Groq engine: DISABLED` at startup | `GROQ_API_KEY` missing from `.env`, or you started the server from a different directory. |
| `⚠️ JWT_SECRET not set` warning | Set `JWT_SECRET` in `.env`, otherwise restarts log everyone out. |
| "Cannot reach the API" in the browser | The backend isn't running, or isn't on port 5000. Check http://localhost:5000/health. |
| CORS errors in the browser console | Add your frontend's origin to `CORS_ORIGINS` in `.env`. |
| Logged out unexpectedly | Token expired (7 days) or `JWT_SECRET` changed. Sign in again. |
| "Session expired" right after signing in | The backend restarted with a temporary `JWT_SECRET`. Set a fixed one. |
| Backend slow to start | First run downloads the SBERT model (~90 MB). Later starts take a few seconds. |
| `npm run dev` fails | Node.js must be 20.9+. Check with `node --version`. |

---

## 🔬 The local model

- **Architecture**: dual-embedding input (candidate 384-d + job 384-d, concatenated to 768) → MLP of 512 → 256 → 64 → 1, with dropout.
- **Training**: `retrain_v2.py` — role-aware hard negatives, `BCEWithLogitsLoss` with class weighting, LR scheduler, and F1-optimal threshold calibration.
- **Weights**: `recruitment_model.pth`; the decision threshold is stored in the checkpoint and loaded at boot.
- **Dataset**: Kaggle job/candidate pairings enriched with role-specific hard negatives.

To retrain (needs `archive/dataset.csv`):

```bash
python retrain_v2.py
```

---

## 📚 Educational Journey (Lessons & Docs)

This repository includes a full curriculum on how the model was built, from data cleaning to
neural architecture:

### 🛠️ Foundations
- [**Theory & Concepts**](docs/theory_and_concepts.md) — The "Why" behind the AI.
- [**EDA & Data Cleaning**](docs/eda_and_cleaning_guide.md) — Preparing the dataset for training.
- [**Kaggle Analysis Report**](docs/kaggle_analysis_report.md) — Insights from the source data.

### 🧠 Core Lessons
1. [**Embeddings & NLP**](docs/lesson_1_embeddings_quiz.md) — How AI "reads" text.
2. [**Preprocessing Logic**](docs/lesson_2_preprocessing.md) — Turning raw text into math.
3. [**Neural Architecture**](docs/lesson_3_architecture.md) — Building the "Brain" (MLP).
4. [**The Training Loop**](docs/lesson_4_training_loop.md) — How the model learns from mistakes.
5. [**Hyperparameter Tuning**](docs/lesson_5_tuning.md) — Optimizing for performance.
6. [**Metrics & Evaluation**](docs/lesson_6_metrics.md) — Measuring success (Precision/Recall).

### 🎨 Implementation & UI
- [**Web Interface (Flask & HTML)**](docs/lesson_7_ui.md) — Connecting the model to a user interface.
- [**PDF Parsing Support**](docs/lesson_8_pdf_parsing.md) — Handling real-world document formats.
- [**Hard Negatives & Retraining**](docs/lesson_9_distribution_gap.md) — Solving the "Chef Paradox" and role mismatches.
- [**Logic Failure Diagnosis**](docs/lesson_10_logic_failure.md) — Debugging common AI pitfalls.

### 🏁 Final Presentation
- [**Walkthrough**](docs/walkthrough.md) — A step-by-step guide to the final system.
- [**Cheat Sheet for Demo**](docs/presentation_cheat_sheet.md) — Key talking points for your presentation.

---
Produced as part of an Advanced AI Coding Collaboration.
