import pandas as pd
import torch
from train_model import RecruitmentBrain
from sentence_transformers import SentenceTransformer
from preprocess_data import clean_text
import os

def find_super_selects():
    print("💎 FINDING HIGH-CONFIDENCE CANDIDATES...")
    df = pd.read_csv(r'e:\PRTFLIO\ai recrut\archive\dataset.csv')
    
    model_sbert = SentenceTransformer('all-MiniLM-L6-v2')
    brain = RecruitmentBrain(input_dim=768)
    brain.load_state_dict(torch.load('recruitment_model.pth'))
    brain.eval()

    candidates = []
    
    # Check first 200 selects to find the best demo candidates
    select_indices = df[df['decision'] == 'select'].index[:200]
    
    for idx in select_indices:
        row = df.loc[idx]
        cand_text = clean_text(str(row['Resume']) + " " + str(row['Transcript']))
        job_text = clean_text(str(row['Job_Description']))
        
        with torch.no_grad():
            cand_emb = model_sbert.encode([cand_text], convert_to_tensor=True)
            job_emb = model_sbert.encode([job_text], convert_to_tensor=True)
            full_emb = torch.cat((cand_emb, job_emb), dim=1)
            prob = brain(full_emb).item()
        
        candidates.append({
            'prob': prob,
            'name': row['Name'],
            'role': row['Role'],
            'resume': row['Resume'],
            'transcript': row['Transcript'],
            'job_desc': row['Job_Description']
        })
    
    # Sort by probability
    candidates.sort(key=lambda x: x['prob'], reverse=True)
    
    print("\n🏆 TOP 3 DEMO CANDIDATES:")
    for i in range(3):
        c = candidates[i]
        print(f"\n[{i+1}] {c['name']} ({c['role']}) - PROB: {c['prob']*100:.2f}%")
        print(f"Text available in memory for update.")

    return candidates[:3]

if __name__ == "__main__":
    find_super_selects()
