# 🧠 AI Recruitment Intelligence System

A two-sided recruitment platform. **Recruiters** post vacancies and review applicants ranked by
CV match. **Job seekers** drop in a CV, get every open vacancy scored and ranked against it, and
apply in one click. Recruiters also keep the original manual screening tool for evaluating a
candidate against a pasted job description.

You pick your role when you register, and each role gets its own portal.

> **Setting this up for the first time?** Go straight to
> [**Setup From Scratch**](#-setup-from-scratch) below. It assumes you have never run a project
> like this before and explains every step, including what to install and what each command does.

---

## 📋 Table of Contents

- [Setup From Scratch](#-setup-from-scratch) ← **start here**
- [Running it again later](#-running-it-again-later)
- [Running with Docker](#-running-with-docker-optional)
- [Architecture](#-architecture)
- [Configuration reference](#-configuration-reference)
- [API reference](#-api-reference)
- [Project structure](#-project-structure)
- [Database](#-database)
- [Troubleshooting](#-troubleshooting)
- [The local model](#-the-local-model)
- [Educational docs](#-educational-journey-lessons--docs)

---

# 🚀 Setup From Scratch

This walkthrough takes about 20 minutes. You will install two programs, get one free API key,
create one text file, and run two commands. Do the parts in order and don't skip ahead.

**The app has two halves that both need to be running at the same time:**

- the **backend** (the AI brain — Python)
- the **frontend** (the website you click on — Node.js)

That's why you'll end up with two terminal windows open. Both must stay open while you use the
app. Closing one breaks the app until you start it again.

---

## Part 1 — Open a terminal

A "terminal" is the black window where you type commands. You'll use it a lot.

- **Windows:** press `Win + X`, then click **Terminal** (or **Windows PowerShell**).
- **Mac:** press `Cmd + Space`, type `Terminal`, press Enter.
- **Linux:** press `Ctrl + Alt + T`.

Keep it open. When this guide says "run" something, it means: type it into the terminal and press
Enter.

---

## Part 2 — Install Python

Python runs the AI backend.

1. Go to **https://www.python.org/downloads/** and download the latest version.
2. Run the installer.
3. 🚨 **On Windows, tick the box that says "Add python.exe to PATH" on the very first screen.**
   It is easy to miss and it is at the bottom. If you skip it, your terminal will not be able to
   find Python and nothing in this guide will work.
4. Click through the rest of the installer.
5. **Close your terminal and open a new one** (it only notices new programs when it restarts).
6. Check it worked:

   ```bash
   python --version
   ```

   You should see something like `Python 3.12.2`. **It must be 3.11 or higher.**

   > If you get "command not found" or "not recognized", Python isn't on your PATH. On Windows,
   > re-run the installer, choose **Modify**, and make sure the PATH box is ticked. On Mac, try
   > `python3 --version` instead — and use `python3` everywhere this guide says `python`.

---

## Part 3 — Install Node.js

Node.js runs the website half.

1. Go to **https://nodejs.org** and download the **LTS** version (the left-hand button).
2. Run the installer and click through it. No special boxes to tick.
3. **Close your terminal and open a new one again.**
4. Check it worked:

   ```bash
   node --version
   ```

   You should see something like `v20.11.0`. **It must be 20.9 or higher.** If it's lower, install
   the LTS version again — this project will not build on older Node.

---

## Part 4 — Get the project onto your computer

**If you have Git installed:**

```bash
git clone https://github.com/Rahib9045/MYFMOD.git
cd MYFMOD
```

**If you don't:** open the GitHub page in a browser, click the green **Code** button →
**Download ZIP**, then unzip it somewhere you'll remember (like your Desktop).

Now point your terminal at that folder. Type `cd `, then **drag the project folder from your file
explorer onto the terminal window** — it fills in the path for you — then press Enter.

```bash
cd "C:\Users\YourName\Desktop\MYFMOD"     # Windows example
cd ~/Desktop/MYFMOD                        # Mac/Linux example
```

Confirm you're in the right place:

```bash
ls        # Mac/Linux
dir       # Windows
```

You should see `app.py`, `requirements.txt`, and a `frontend` folder in the list. If you don't,
you're in the wrong folder — `cd` again.

---

## Part 5 — Have your Groq API key ready

Groq is the AI service that reads the resumes. **Use your own key** — you'll paste it into the
`.env` file in the next step. It starts with `gsk_`.

Don't have it to hand? Get it from **https://console.groq.com** → **API Keys** in the sidebar.
It's free. If you create a new one, copy it immediately — the site only shows it once.

> No key is stored in this project, so you have to supply your own.

---

## Part 6 — Create the `.env` file

`.env` is a small text file holding your secrets. The project ships with a template called
`.env.example`. You're going to copy it and fill it in.

Run this in the project folder:

```bash
# Windows (PowerShell)
Copy-Item .env.example .env

# Mac/Linux
cp .env.example .env
```

Now you need a second secret — a random string used to keep logins secure. Generate one:

```bash
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

It prints a long jumble of characters. Copy it.

Open the new `.env` file in any text editor (Notepad is fine) and fill in the two blank lines:

```ini
GROQ_API_KEY=gsk_paste_your_groq_key_here
JWT_SECRET=paste_the_long_random_jumble_here
```

Leave every other line exactly as it is. Save and close.

> ⚠️ **Never send this file to anyone or upload it to GitHub.** It's already set up to be ignored
> by Git, so as long as you don't go out of your way, you're fine.

---

## Part 7 — Start the backend (Terminal 1)

In your terminal, in the project folder, run:

```bash
pip install -r requirements.txt
```

This downloads everything Python needs. **It takes 5–15 minutes and downloads about 2 GB** — one
of the pieces (PyTorch) is genuinely enormous. Lots of text will scroll past. That's normal. Go
make a coffee.

When it finishes, start the server:

```bash
python app.py
```

The first time only, it downloads the AI language model (~90 MB), so give it a minute. You're
looking for these lines:

```
✨ v2 Model loaded | Threshold = 0.2
🤖 Groq engine: ENABLED (llama-3.3-70b-versatile)
🚀 RECRUITMENT INTELLIGENCE SERVER RUNNING
```

✅ **`Groq engine: ENABLED` is the line that matters.** If it says `DISABLED`, your `GROQ_API_KEY`
didn't get read — go back to Part 6 and check the `.env` file is in the project folder, is named
exactly `.env`, and has your key on the `GROQ_API_KEY=` line with no spaces or quotes.

**Leave this terminal open and running.** It looks like it's frozen. It isn't — that's the server
waiting for work. Don't press Ctrl+C.

---

## Part 8 — Start the frontend (Terminal 2)

Open a **brand new terminal window**. Don't reuse the first one.

Navigate to the project folder again, then into the `frontend` folder:

```bash
cd "C:\Users\YourName\Desktop\MYFMOD\frontend"    # your path here
```

Install and run:

```bash
npm install
npm run dev
```

`npm install` takes a few minutes the first time. When `npm run dev` is ready you'll see:

```
▲ Next.js 16.2.2
- Local:  http://localhost:3000
✓ Ready
```

**Leave this terminal open too.** You now have two terminals running. That's correct.

> There is no config file to create for the frontend. It automatically talks to the backend on
> `localhost:5000`.

---

## Part 9 — Use it

### Quickest path: load the demo data

With the backend running, open a third terminal in the project folder and run:

```bash
python seed_demo.py
```

That creates one recruiter, one job seeker with a CV, and five realistic vacancies, then prints
the ranking so you can see the matcher working. Safe to re-run — it skips anything that already
exists. Sign in at http://localhost:3000/login with:

| Role | Email | Password |
| :--- | :--- | :--- |
| Recruiter | `recruiter@demo.com` | `demo12345` |
| Job seeker | `seeker@demo.com` | `demo12345` |

### Or do it by hand

Open **http://localhost:3000**, click **Register now**, and pick a role. Any email works — nothing
is verified and no email is sent. Passwords must be at least 8 characters.

**As a recruiter:**

1. You land on **Vacancies**. Click **Post a Vacancy**.
2. Fill in the title, description, requirements and skills. All of those feed the matching model,
   so the more specific they are, the better the ranking.
3. Publish it. The vacancy is now scored against every job seeker's CV automatically.
4. Click the **applicants** button on a vacancy to see who applied, ranked by CV match, with each
   person's full CV and contact details.
5. Move an applicant through **submitted → reviewed → shortlisted / rejected**. They see the
   status change on their side.
6. **Manual Screening** in the top nav is the original tool: paste a CV and a job description and
   get a one-off verdict.

**As a job seeker:**

1. You land on **Find Jobs**. Upload your CV as a PDF, or paste the text.
2. Click **Find Matching Jobs**. Every open vacancy is scored and ranked against your CV.
3. Open a match to read the full posting and see the two scores behind it.
4. Click **Get AI feedback** for a written verdict on that specific vacancy.
5. Add an optional note and **Apply**. It appears under **My Applications**, where you can track
   the recruiter's decision.
6. **CV Analysis** in the top nav works on *any* job description — including one you found
   somewhere else entirely. Paste it in and you get a shortlist likelihood plus specific advice on
   improving your CV for that role. Every analysis is saved so you can reopen it later.

🎉 That's it. It works.

### Did it actually work? Check these four things

If anything below is wrong, find the matching row in [Troubleshooting](#-troubleshooting).

1. **Terminal 1 says `Groq engine: ENABLED`.** If it says `DISABLED`, the app still runs but uses
   the weaker offline model — your `.env` isn't being read.
2. **http://localhost:5000/health returns JSON** that looks like
   `{"status":"ok","engine":"groq-llama-3.3-70b-versatile","threshold":0.2}`. Paste that URL into
   your browser. If nothing loads, Terminal 1 isn't running.
3. **A real analysis comes back.** A good match should score high, and a deliberate mismatch
   should score near zero. Try shuffling to a nonsense pairing — a chef's resume against a machine
   learning job should come back **REJECT** with "Resume does not match the core job category."
4. **Your data survives a refresh.** Save a portfolio, press F5. If it disappears, the backend
   isn't storing it.

> This walkthrough was tested by cloning the repository fresh and following it start to finish, so
> the steps and the expected output above are what you should actually see.

---

## 🔁 Running it again later

You only do the setup once. Every time after that, it's just two terminals:

**Terminal 1** (in the project folder):
```bash
python app.py
```

**Terminal 2** (in the `frontend` folder):
```bash
npm run dev
```

Then open http://localhost:3000. No reinstalling, no re-creating `.env`.

To stop the app, press `Ctrl + C` in each terminal.

---

## 🐳 Running with Docker (optional)

If you already have Docker Desktop installed and running, you can skip Parts 2, 3, 7 and 8
entirely. You still need Parts 4–6 (the `.env` file).

```bash
docker compose up --build
```

> 🚨 **Check your free disk space first — you need at least 15 GB.** The backend image is ~9 GB
> (PyTorch is enormous) and the build cache adds another ~11 GB on top before you can clear it. If
> your drive fills up mid-build, Docker doesn't fail cleanly — the engine wedges and starts
> returning `500 Internal Server Error` on every command. **If that happens:** free up space,
> then run `wsl --shutdown` and restart Docker Desktop.
>
> If you're short on space, use the normal setup (Parts 1–9) instead. It needs about 3 GB.

The first build takes 10–20 minutes. After that, `docker compose up` starts in seconds. Then open
http://localhost:3000.

To reclaim space afterwards: `docker builder prune -af` clears the build cache (safe — it's
regenerable). On Windows that frees space *inside* the virtual disk but doesn't return it to
Windows until you compact it, which needs Docker and WSL fully shut down first.

Notes:
- The AI language model is **baked into the image at build time**, so containers start instantly
  and work with no internet connection.
- The database lives in a named volume, so accounts survive `docker compose down`.
- To stop it: `docker compose down`.

### Production mode

The default stack runs development servers — fine for a demo, not for real deployment. To swap in
gunicorn and an optimized frontend build:

```bash
docker compose -f docker-compose.yml -f docker-compose.prod.yml up --build
```

> Set `NEXT_PUBLIC_API_URL` in `.env` to the address browsers will actually use **before**
> building for production. It gets compiled into the browser bundle at build time, so changing it
> later needs a rebuild, not just a restart.

---

## 🏗️ Architecture

| Layer | What it does |
| :--- | :--- |
| **Next.js frontend** | Role-aware portals: `/recruiter`, `/seeker`, `/dashboard` |
| **Flask API** | Auth (JWT + roles), vacancies, CV matching, applications |
| **Database** | SQLite by default (`DATABASE_URL` swaps in Postgres) |
| **SBERT + MLP** | Ranks one CV against every open vacancy, in one batch |
| **Groq LLM** | `llama-3.3-70b-versatile` — the deep write-up on a single pairing |

### Which engine does what, and why

Ranking a CV against *every* vacancy is a batch problem: SBERT encodes the CV once and scores
hundreds of jobs in milliseconds, while Groq would need one API call per job. So **matching uses
the local model**, and **Groq handles the detailed verdict** on one job at a time.

Every match returns two independent numbers:

- **relevance** — cosine similarity between the CV and the vacancy. "Is this the same kind of
  work?" **This drives the ranking.**
- **fit** — the trained MLP's selection probability. "Would this candidate be picked?"
  **Advisory only.**

> **An honest note on `fit`.** The MLP was trained on the Kaggle
> resume-and-transcript-vs-prose-job-description distribution. A short CV against a short,
> structured vacancy is out of distribution for it, and in practice it returns near-zero for
> every job — including obviously good matches. Blending it into the ranking only compressed the
> scale without reordering anything, so it is reported separately instead of being hidden inside
> a combined score. If you want it to genuinely contribute, it needs retraining on
> vacancy-shaped data.

For the manual screening tool, the API tries Groq first and falls back to the local model if no
`GROQ_API_KEY` is set or the call fails. Every response reports which engine produced it in the
`engine` field, and that value is stored with the result.

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

**The frontend needs no config file.** It reads `NEXT_PUBLIC_API_URL` if set, and otherwise falls
back to `http://localhost:5000`, which is correct for local use. A fresh clone has no
`frontend/.env.local` and doesn't need one — only create it if your backend runs somewhere else.

> `BRAIN_INIT_TOKEN` from earlier versions is still accepted as a fallback name for
> `GROQ_API_KEY`, so old `.env` files keep working.

---

## 🔌 API reference

All routes except `/auth/register`, `/auth/login`, and `/health` require an
`Authorization: Bearer <token>` header.

**Any signed-in account**

| Method | Route | Purpose |
| :--- | :--- | :--- |
| `POST` | `/auth/register` | Create an account (`role`: `recruiter` \| `seeker`) → `{token, user}` |
| `POST` | `/auth/login` | Sign in → `{token, user}` |
| `GET` | `/auth/me` | Current user, including role |
| `GET` | `/jobs` | Browse every open vacancy |
| `GET` | `/jobs/<id>` | One vacancy |
| `POST` | `/predict` | Analyse one CV against one pasted job description; saved to history |
| `GET` | `/analyses` | Your analysis history (`?limit=N`, max 200) |
| `GET` `DELETE` | `/analyses/<id>` | Full record / delete |
| `POST` | `/upload_pdf` | Extract text from a PDF (10 MB max) |
| `GET` | `/health` | Status and active engine |

`/predict` serves both roles because the mechanics are identical — a recruiter is screening a
candidate, a seeker is checking their own CV against a posting. Seekers may omit `resume` and it
falls back to their saved CV. Histories are per-account and invisible to everyone else.

**Recruiter only** — anything else gets `403`

| Method | Route | Purpose |
| :--- | :--- | :--- |
| `POST` | `/jobs` | Post a vacancy (embedding computed on save) |
| `GET` | `/jobs/mine` | My vacancies, with applicant counts |
| `PUT` `DELETE` | `/jobs/<id>` | Edit (re-embeds) / delete. `status`: `open` \| `closed` |
| `GET` | `/jobs/<id>/applications` | Applicants, best match first, with CV and contact |
| `PATCH` | `/applications/<id>` | Set status: `submitted` \| `reviewed` \| `shortlisted` \| `rejected` |
| `GET` `POST` | `/portfolios` | List / create saved candidate profiles |
| `GET` `PUT` `DELETE` | `/portfolios/<id>` | Read / update / delete one |

**Job seeker only** — anything else gets `403`

| Method | Route | Purpose |
| :--- | :--- | :--- |
| `GET` `PUT` | `/cv` | Read / save my CV |
| `POST` | `/match` | Rank every open vacancy against my CV |
| `POST` | `/jobs/<id>/analyze` | Groq write-up on how I fit one vacancy |
| `POST` | `/jobs/<id>/apply` | Apply (one per vacancy; the match score is recorded) |
| `GET` | `/applications/mine` | My applications and their status |

Everything is scoped to its owner. Another recruiter asking for your vacancy's applicants gets a
`404`, not the data — and using the wrong role gets a `403`.

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
├── app.py                  # Flask API — auth, vacancies, matching, applications
├── models.py               # SQLAlchemy tables (5) + role/status constants
├── db.py                   # Engine, session setup, additive column migrations
├── auth.py                 # Password hashing, JWT, @require_auth / @require_role
├── seed_demo.py            # Creates a demo recruiter, seeker and 5 vacancies
├── preprocess_data.py      # Text cleaning used at train and inference time
├── retrain_v2.py           # Training script + the RecruitmentBrain model class
├── recruitment_model.pth   # Trained weights (threshold baked in)
├── requirements.txt        # Python dependencies
├── .env.example            # Config template — copy to .env
├── docker-compose.yml      # Backend + frontend + DB volume (dev)
├── docker-compose.prod.yml # Production overrides (gunicorn, built frontend)
├── Dockerfile              # Backend image
├── frontend/
│   ├── src/lib/api.ts      # All API calls + token handling
│   ├── src/lib/useAuth.ts  # Session check + role guard hook
│   ├── src/components/     # Shared role-aware header
│   ├── src/app/login/      # Sign in (redirects by role)
│   ├── src/app/register/   # Sign up with role picker
│   ├── src/app/recruiter/  # Post vacancies, review applicants
│   ├── src/app/seeker/     # CV upload, ranked matches, CV analysis, applications
│   ├── src/app/dashboard/  # Manual screening (recruiter only)
│   └── public/verified_templates.json   # Sample candidates for "Randomize Case"
├── docs/                   # Lessons, guides, final report
└── archive/dataset.csv     # Training data (not tracked in git)
```

---

## 🗄️ Database

Five tables, created automatically on first boot (`models.py`):

- **`users`** — email, name, hashed password, role, company (recruiters), saved CV (seekers)
- **`jobs`** — vacancies, plus a cached SBERT embedding so matching never re-encodes them
- **`applications`** — one row per seeker per vacancy, with the CV snapshot and match score
- **`portfolios`** — a recruiter's saved candidate profile
- **`analyses`** — every manual-screening verdict and which engine produced it

**Upgrading an existing database is automatic.** `create_all()` adds new tables but never alters
existing ones, so `db.py` also patches in columns added later (`role`, `company`, `cv_text`,
`cv_filename`). Accounts created before roles existed become **recruiters**, which preserves
exactly what they could do before. You'll see `🔧 Schema updated: added users.role` on the first
boot after upgrading.

**To wipe everything and start fresh:**

```bash
# Local — just delete the database file, it rebuilds itself on next start
rm recruitment.db                    # Mac/Linux
Remove-Item recruitment.db           # Windows

# Docker — find the exact name with `docker volume ls`
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
| `python` / `pip` "not recognized" | Python isn't on your PATH. Reinstall it and tick **Add python.exe to PATH**, then open a new terminal. On Mac use `python3` and `pip3`. |
| `npm` "not recognized" | Node.js isn't installed, or you didn't open a new terminal after installing it. |
| `Groq engine: DISABLED` at startup | `GROQ_API_KEY` missing from `.env`, the file isn't in the project folder, or you started the server from a different folder. |
| `⚠️ JWT_SECRET not set` warning | Set `JWT_SECRET` in `.env`. Without it, every restart logs everyone out. |
| "Cannot reach the API" in the browser | Terminal 1 isn't running. Check http://localhost:5000/health — it should return JSON. |
| Website won't load at all | Terminal 2 isn't running, or something else is using port 3000. |
| `Port 5000 is already in use` | Another program has the port (on Mac, AirPlay Receiver is a common culprit — turn it off in System Settings → General → AirDrop & Handoff). |
| "This requires a recruiter account" (403) | You registered as the other role. Roles are fixed at registration — make a second account with the role you need. |
| Job seeker sees no matches | No recruiter has posted a vacancy yet. Run `python seed_demo.py`, or post one from a recruiter account. |
| Match scores look low across the board | Expected. The score is raw cosine similarity: ~70%+ is a strong match, ~30% or below is a different field. It is not a percentage-of-requirements-met. |
| A vacancy edit didn't change the ranking | Only the text fields re-embed. Changing just `status` or `salary_range` deliberately leaves the embedding alone. |
| Logged out unexpectedly | Token expired (7 days) or `JWT_SECRET` changed. Just sign in again. |
| "Session expired" right after signing in | The backend restarted with a temporary `JWT_SECRET`. Set a fixed one in `.env`. |
| `pip install` fails or seems stuck | It downloads ~2 GB. Give it 15 minutes on a slow connection before assuming it's broken. |
| Backend slow to start (first time) | It downloads the AI model (~90 MB) once. Later starts take seconds. Docker images have it pre-baked. |
| CORS errors in the browser console | Add your frontend's origin to `CORS_ORIGINS` in `.env`. |
| `docker compose up` fails immediately | `.env` must exist — compose requires it. Do Part 6 first. |
| Production frontend can't reach the API | `NEXT_PUBLIC_API_URL` is compiled in at build time. Set it in `.env` and **rebuild**. |
| Docker build can't find a file it should copy | Check `.dockerignore`. Patterns use Go's `filepath.Match`, so `*` does not cross `/` — `*.csv` misses `archive/dataset.csv`, and broad rules like `*.txt` will silently swallow `requirements.txt` unless negated with `!`. |

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
