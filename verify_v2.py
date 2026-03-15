"""
verify_v2.py — Quick spot-check of the new v2 model.
Tests known roles vs matching AND mismatching job descriptions.
"""
import torch
import re
from sentence_transformers import SentenceTransformer
from retrain_v2 import RecruitmentBrain

def clean_text(text):
    text = str(text).lower()
    text = re.sub(r'[^a-zA-Z0-9\s]', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

print("Loading model v2...")
sbert = SentenceTransformer('all-MiniLM-L6-v2')
brain = RecruitmentBrain(input_dim=768)
checkpoint = torch.load('recruitment_model.pth', map_location='cpu')
brain.load_state_dict(checkpoint['model_state'])
THRESHOLD = checkpoint['threshold']
brain.eval()
print(f"Threshold: {THRESHOLD}\n")

def predict(cand, job):
    cand_emb = sbert.encode([clean_text(cand)], convert_to_tensor=True)
    job_emb  = sbert.encode([clean_text(job)],  convert_to_tensor=True)
    with torch.no_grad():
        prob = brain.predict_proba(torch.cat((cand_emb, job_emb), dim=1)).item()
    decision = "SELECT ✅" if prob >= THRESHOLD else "REJECT ❌"
    return prob, decision

tests = [
    # (Label, Candidate Text, Job Description)
    ("SHOULD SELECT — Data Scientist",
     "Jose Morrison Data Scientist 5 years of experience in machine learning deep learning python tensorflow data analysis predictive models statistics regression classification neural networks",
     "We need a Data Scientist skilled in machine learning model development python tensorflow statistical analysis"),

    ("SHOULD SELECT — Game Developer",
     "Cynthia Avila Game Developer Unity Unreal Engine C++ Java 5 years game development 3D modeling gameplay programming",
     "Game Developer role building interactive game experiences Unity Unreal Engine C++ gameplay systems 3D environments"),

    ("SHOULD SELECT — Cloud Engineer",
     "Jessica Hall Cloud Engineer AWS Certified Solutions Architect Terraform Kubernetes CI/CD infrastructure as code serverless microservices DevOps",
     "Cloud Architect role designing scalable secure cloud infrastructure AWS Terraform Kubernetes DevOps pipelines"),

    ("SHOULD REJECT — Content Writer vs Data Scientist",
     "David Moore Content Writer SEO copywriting technical writing blog posts editorial content social media writing proofreading",
     "We need a Data Scientist skilled in machine learning model development python tensorflow statistical analysis"),

    ("SHOULD REJECT — HR Specialist vs Cloud Engineer",
     "Patrick Mcclain HR Specialist recruitment talent acquisition onboarding employee relations HRIS conflict resolution",
     "Cloud Architect role designing scalable secure cloud infrastructure AWS Terraform Kubernetes DevOps pipelines"),

    ("SHOULD REJECT — Game Developer vs Data Scientist",
     "Cynthia Avila Game Developer Unity Unreal Engine C++ Java gameplay programming 3D modeling game mechanics",
     "We need a Data Scientist skilled in machine learning model development python tensorflow statistical analysis"),
]

print("=" * 65)
print(f"{'Test':<45} {'Prob':>6}  {'Decision'}")
print("=" * 65)
for label, cand, job in tests:
    prob, decision = predict(cand, job)
    print(f"{label:<45} {prob*100:>5.1f}%  {decision}")
print("=" * 65)
