"""
extract_verified_templates.py
Extracts the best-scoring verified candidate from EACH role in the dataset,
using the v2 model to find candidates that genuinely score high (true positives).
Saves results to verified_templates.json for use in index.html.
"""
import pandas as pd, torch, re, json
from sentence_transformers import SentenceTransformer
from retrain_v2 import RecruitmentBrain

def clean(t):
    t = str(t).lower()
    t = re.sub(r'[^a-zA-Z0-9\s]', '', t)
    return re.sub(r'\s+', ' ', t).strip()

print("Loading model v2...")
sbert = SentenceTransformer('all-MiniLM-L6-v2')
brain = RecruitmentBrain()
ckpt = torch.load('recruitment_model.pth', map_location='cpu')
brain.load_state_dict(ckpt['model_state'])
brain.eval()
T = ckpt['threshold']

df = pd.read_csv(r'e:\PRTFLIO\ai recrut\archive\dataset.csv')

# Focus on a set of roles that matter for the demo
TARGET_ROLES = [
    'Game Developer', 'Data Scientist', 'Cloud Engineer',
    'Content Writer', 'Human Resources Specialist', 'UX Designer',
    'Mobile App Developer', 'Digital Marketing Specialist'
]

verified_candidates = []
verified_jobs = set()

print(f"\nScoring top SELECTs for each target role...")
for role in TARGET_ROLES:
    role_df = df[(df['Role'] == role) & (df['decision'] == 'select')]
    if len(role_df) == 0:
        print(f"  ⚠️  No SELECTs found for: {role}")
        continue

    best_prob = -1
    best_row = None
    for _, row in role_df.iterrows():
        ci = sbert.encode([clean(str(row['Resume']) + ' ' + str(row['Transcript']))], convert_to_tensor=True)
        ji = sbert.encode([clean(str(row['Job_Description']))], convert_to_tensor=True)
        with torch.no_grad():
            p = brain.predict_proba(torch.cat((ci, ji), dim=1)).item()
        if p > best_prob:
            best_prob = p
            best_row = row

    decision = "SELECT ✅" if best_prob >= T else "REJECT ❌"
    print(f"  {role}: {best_row['Name']} — {best_prob*100:.1f}% ({decision})")

    # Add candidate template (include the job desc they were paired with)
    verified_candidates.append({
        "name": best_row['Name'],
        "role": role,
        "resume": str(best_row['Resume']),
        "transcript": str(best_row['Transcript']),
        "job_desc": str(best_row['Job_Description']),
        "confidence": round(best_prob * 100, 1)
    })

    # Add job description (deduplicated)
    jd = str(best_row['Job_Description'])
    if jd not in verified_jobs:
        verified_jobs.add(jd)

# Build job list directly from verified candidates' actual JDs
jobs_list = [{"title": c["role"], "desc": c["job_desc"]} for c in verified_candidates]

output = {
    "candidates": verified_candidates,
    "jobs": jobs_list
}

with open('verified_templates.json', 'w', encoding='utf-8') as f:
    json.dump(output, f, indent=2, ensure_ascii=False)

print(f"\n✅ Saved {len(verified_candidates)} verified candidates to verified_templates.json")
print("   These are REAL dataset rows that the model genuinely scores high.")
