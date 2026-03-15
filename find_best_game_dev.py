"""
find_best_game_dev.py — Finds the highest-confidence Game Developer SELECT
from the real dataset using the v2 model, then prints full text for the UI.
"""
import pandas as pd, torch, re
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
print(f"Threshold: {T}\n")

df = pd.read_csv(r'e:\PRTFLIO\ai recrut\archive\dataset.csv')
devs = df[(df['Role'] == 'Game Developer') & (df['decision'] == 'select')]
print(f"Found {len(devs)} Game Developer SELECTs. Scoring all...\n")

results = []
for _, row in devs.iterrows():
    ci = sbert.encode([clean(str(row['Resume']) + ' ' + str(row['Transcript']))], convert_to_tensor=True)
    ji = sbert.encode([clean(str(row['Job_Description']))], convert_to_tensor=True)
    with torch.no_grad():
        p = brain.predict_proba(torch.cat((ci, ji), dim=1)).item()
    results.append((p, row['Name'], row))

results.sort(reverse=True)

print("=" * 60)
print("TOP 5 GAME DEVELOPER SELECTS:")
print("=" * 60)
for i, (prob, name, row) in enumerate(results[:5]):
    decision = "SELECT ✅" if prob >= T else "REJECT ❌"
    print(f"  {i+1}. {name}: {prob*100:.1f}% — {decision}")

best_prob, best_name, best = results[0]
print(f"\n🏆 Best: {best_name} ({best_prob*100:.1f}%)")
print("\n=== JOB DESCRIPTION ===")
print(best['Job_Description'])
print("\n=== RESUME ===")
print(str(best['Resume']))
print("\n=== TRANSCRIPT ===")
print(str(best['Transcript']))
