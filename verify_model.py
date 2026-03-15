import pandas as pd
import torch
from train_model import RecruitmentBrain
from sentence_transformers import SentenceTransformer
from preprocess_data import clean_text
import os

def verify_on_real_data():
    print("🔍 VERIFYING MODEL ON ORIGINAL KAGGE DATA")
    
    # 1. Load Data
    df = pd.read_csv(r'e:\PRTFLIO\ai recrut\archive\dataset.csv')
    select_samples = df[df['decision'] == 'select'].head(3)
    
    # 2. Load Model
    model_sbert = SentenceTransformer('all-MiniLM-L6-v2')
    brain = RecruitmentBrain(input_dim=768)
    brain.load_state_dict(torch.load('recruitment_model.pth'))
    brain.eval()

    for idx, row in select_samples.iterrows():
        print(f"\n--- Testing Candidate: {row['Name']} ---")
        cand_text = clean_text(str(row['Resume']) + " " + str(row['Transcript']))
        job_text = clean_text(str(row['Job_Description']))
        
        with torch.no_grad():
            cand_emb = model_sbert.encode([cand_text], convert_to_tensor=True)
            job_emb = model_sbert.encode([job_text], convert_to_tensor=True)
            full_emb = torch.cat((cand_emb, job_emb), dim=1)
            prediction = brain(full_emb)
            prob = prediction.item()
        
        print(f"Prediction Probability: {prob*100:.2f}%")
        print(f"Original Decision: {row['decision']}")

if __name__ == "__main__":
    verify_on_real_data()
