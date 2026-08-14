"""
seed_demo.py — Populate the database with a demo recruiter, job seeker and a
handful of realistic vacancies, so the portals have something to show.

Run it with the backend already running:

    python seed_demo.py

Safe to re-run: accounts and vacancies that already exist are skipped.
"""

import sys

import requests

BASE = "http://127.0.0.1:5000"
PASSWORD = "demo12345"

RECRUITER = {
    "name": "Rita Chen",
    "email": "recruiter@demo.com",
    "password": PASSWORD,
    "role": "recruiter",
    "company": "Northwind Data",
}

SEEKER = {
    "name": "Sam Okafor",
    "email": "seeker@demo.com",
    "password": PASSWORD,
    "role": "seeker",
}

SEEKER_CV = """Sam Okafor — Data Analyst

6 years turning messy operational data into decisions people actually use.

EXPERIENCE
Senior Data Analyst, Grocero (2021-present)
  - Rebuilt the weekly trading report in Tableau; cut prep time from 2 days to 20 minutes.
  - Led the migration of 40+ legacy SQL reports onto dbt with full test coverage.
  - Partner to the buying team on price elasticity and promotion analysis.

Data Analyst, Kestrel Logistics (2019-2021)
  - Built the depot performance dashboard used daily by 12 regional managers.
  - A/B tested route-planning changes worth £1.2m in annual savings.

SKILLS
SQL (advanced), Python (pandas, scikit-learn), Tableau, dbt, Airflow,
statistics, A/B testing, stakeholder communication.

EDUCATION
BSc Statistics, University of Manchester.
"""

JOBS = [
    {
        "title": "Senior Data Analyst",
        "location": "London (hybrid)",
        "employment_type": "Full-time",
        "experience_level": "Senior",
        "salary_range": "£60k – £75k",
        "description": "Own analytics for our retail division. You will build the reporting that the trading team runs on, and partner directly with buyers and merchandisers on pricing and promotion decisions.",
        "requirements": "5+ years in an analytics role. Advanced SQL and confident Python. Experience owning a BI tool end to end (we use Tableau). Comfortable presenting to non-technical stakeholders. Degree in a numerate subject.",
        "skills": ["SQL", "Python", "Tableau", "dbt", "stakeholder reporting"],
    },
    {
        "title": "Analytics Engineer",
        "location": "Remote (UK)",
        "employment_type": "Full-time",
        "experience_level": "Mid",
        "salary_range": "£55k – £68k",
        "description": "Build and maintain the transformation layer that every dashboard in the business depends on.",
        "requirements": "Strong SQL and dbt. Familiarity with Airflow or similar orchestration. You care about testing and documentation as much as the models themselves.",
        "skills": ["dbt", "SQL", "Airflow", "data modelling", "testing"],
    },
    {
        "title": "Machine Learning Engineer",
        "location": "Remote",
        "employment_type": "Contract",
        "experience_level": "Mid",
        "salary_range": "£500 – £650/day",
        "description": "Ship recommendation and ranking models into production and keep them healthy there.",
        "requirements": "PyTorch or TensorFlow in production. Solid Python engineering. Experience with model serving, monitoring and retraining pipelines.",
        "skills": ["PyTorch", "Python", "MLOps", "model serving"],
    },
    {
        "title": "Executive Chef",
        "location": "Paris",
        "employment_type": "Full-time",
        "experience_level": "Lead",
        "salary_range": "€70k – €85k",
        "description": "Lead the kitchen brigade at a fine-dining restaurant and design the seasonal menus.",
        "requirements": "10+ years in professional kitchens with at least 3 leading a brigade. Menu costing, supplier relationships, food safety certification.",
        "skills": ["menu design", "food costing", "kitchen management", "food safety"],
    },
    {
        "title": "Frontend Engineer",
        "location": "Berlin (hybrid)",
        "employment_type": "Full-time",
        "experience_level": "Mid",
        "salary_range": "€65k – €80k",
        "description": "Build the customer-facing web experience in React and TypeScript.",
        "requirements": "Strong React and TypeScript. CSS you are not afraid of. Experience with Next.js and an eye for accessibility and performance.",
        "skills": ["React", "TypeScript", "Next.js", "CSS", "accessibility"],
    },
]


def sign_up_or_in(payload: dict) -> str:
    """Register the account, or log in if it already exists."""
    r = requests.post(f"{BASE}/auth/register", json=payload, timeout=30)
    if r.status_code == 201:
        print(f"  created {payload['email']}")
        return r.json()["token"]
    if r.status_code == 409:
        r = requests.post(
            f"{BASE}/auth/login",
            json={"email": payload["email"], "password": payload["password"]},
            timeout=30,
        )
        if r.ok:
            print(f"  {payload['email']} already existed — signed in")
            return r.json()["token"]
    raise SystemExit(f"Could not set up {payload['email']}: {r.status_code} {r.text[:200]}")


def main() -> None:
    try:
        health = requests.get(f"{BASE}/health", timeout=10)
        health.raise_for_status()
    except requests.RequestException:
        raise SystemExit("Backend is not running. Start it with `python app.py` first.")

    print(f"Engine: {health.json().get('engine')}\n")

    print("Accounts:")
    rec_token = sign_up_or_in(RECRUITER)
    seek_token = sign_up_or_in(SEEKER)
    rec_headers = {"Authorization": f"Bearer {rec_token}"}
    seek_headers = {"Authorization": f"Bearer {seek_token}"}

    print("\nVacancies:")
    existing = {
        j["title"] for j in requests.get(f"{BASE}/jobs/mine", headers=rec_headers, timeout=30).json()["jobs"]
    }
    created = 0
    for job in JOBS:
        if job["title"] in existing:
            print(f"  skipped (exists) {job['title']}")
            continue
        r = requests.post(f"{BASE}/jobs", headers=rec_headers, json=job, timeout=30)
        if r.status_code == 201:
            print(f"  posted {job['title']}")
            created += 1
        else:
            print(f"  FAILED {job['title']}: {r.status_code} {r.text[:150]}")

    print("\nSeeker CV:")
    r = requests.put(
        f"{BASE}/cv",
        headers=seek_headers,
        json={"cv_text": SEEKER_CV, "cv_filename": "sam_okafor_cv.pdf"},
        timeout=30,
    )
    print("  saved" if r.ok else f"  FAILED: {r.text[:150]}")

    print("\nMatch preview for the demo seeker:")
    r = requests.post(f"{BASE}/match", headers=seek_headers, json={}, timeout=60)
    if r.ok:
        for m in r.json()["matches"]:
            bar = "█" * int(m["match_score"] * 30)
            print(f"  {m['match_score'] * 100:5.1f}%  {bar:<30}  {m['title']}")
    else:
        print(f"  FAILED: {r.text[:200]}")

    print(f"\nDone. {created} new vacancies.")
    print("\nSign in at http://localhost:3000/login")
    print(f"  Recruiter   recruiter@demo.com / {PASSWORD}")
    print(f"  Job seeker  seeker@demo.com   / {PASSWORD}")


if __name__ == "__main__":
    sys.exit(main())
