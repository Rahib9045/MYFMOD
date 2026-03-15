import pandas as pd
import torch
import torch.nn as nn
from sentence_transformers import SentenceTransformer
from preprocess_data import clean_text
import os

# Architecture
class RecruitmentBrain(nn.Module):
    def __init__(self, input_dim=768):
        super(RecruitmentBrain, self).__init__()
        self.layer1 = nn.Linear(input_dim, 256)
        self.relu = nn.ReLU()
        self.layer2 = nn.Linear(256, 128)
        self.output_layer = nn.Linear(128, 1)
        self.sigmoid = nn.Sigmoid()

    def forward(self, x):
        x = self.relu(self.layer1(x))
        x = self.relu(self.layer2(x))
        x = self.sigmoid(self.output_layer(x))
        return x

def extract_demo_samples():
    print("💎 EXTRACTING REAL DEMO SAMPLES...")
    df = pd.read_csv(r'e:\PRTFLIO\ai recrut\archive\dataset.csv')
    
    model_sbert = SentenceTransformer('all-MiniLM-L6-v2')
    brain = RecruitmentBrain(input_dim=768)
    brain.load_state_dict(torch.load('recruitment_model.pth'))
    brain.eval()

    def get_prob(res, trans, job):
        c_text = clean_text(str(res) + " " + str(trans))
        j_text = clean_text(str(job))
        with torch.no_grad():
            c_emb = model_sbert.encode([c_text], convert_to_tensor=True)
            j_emb = model_sbert.encode([j_text], convert_to_tensor=True)
            full_emb = torch.cat((c_emb, j_emb), dim=1)
            return brain(full_emb).item()

    # Find a strong Game Dev (Select)
    game_devs = df[df['Role'] == 'Game Developer']
    best_dev = None
    max_prob = 0
    for _, row in game_devs.head(50).iterrows():
        p = get_prob(row['Resume'], row['Transcript'], row['Job_Description'])
        if p > max_prob:
            max_prob = p
            best_dev = row
    
    # Find a strong mismatch (Content Writer vs Data Scientist)
    writer_row = df[df['Role'] == 'Content Writer'].iloc[0]
    ds_row = df[df['Role'] == 'Data Scientist'].iloc[0]
    ds_job = ds_row['Job_Description']
    
    writer_mismatch_prob = get_prob(writer_row['Resume'], writer_row['Transcript'], ds_job)
    ds_match_prob = get_prob(ds_row['Resume'], ds_row['Transcript'], ds_job)

    print("\n--- [SELECT] Game Developer (Genuine Sample) ---")
    print(f"Prob: {max_prob*100:.2f}%")
    print(f"Resume: {best_dev['Resume'][:200]}...")
    print(f"Job: {best_dev['Job_Description'][:200]}...")

    print("\n--- [REJECT] Content Writer vs Data Scientist (Genuine Sample) ---")
    print(f"Prob: {writer_mismatch_prob*100:.2f}%")
    print(f"Resume: {writer_row['Resume'][:200]}...")
    print(f"Job: {ds_job[:200]}...")

    # Save to file for easy copy-paste
    with open('demo_samples.txt', 'w', encoding='utf-8') as f:
        f.write("=== GAME DEVELOPER (SELECT) ===\n")
        f.write(f"RESUME: {best_dev['Resume']}\n\n")
        f.write(f"TRANSCRIPT: {best_dev['Transcript']}\n\n")
        f.write(f"JOB: {best_dev['Job_Description']}\n")
        f.write("-" * 50 + "\n\n")
        
        f.write("=== DATA SCIENTIST (SELECT) ===\n")
        f.write(f"RESUME: {ds_row['Resume']}\n\n")
        f.write(f"TRANSCRIPT: {ds_row['Transcript']}\n\n")
        f.write(f"JOB: {ds_row['Job_Description']}\n")
        f.write("-" * 50 + "\n\n")
        
        f.write("=== CONTENT WRITER MISMATCH (REJECT) ===\n")
        f.write(f"RESUME: {writer_row['Resume']}\n\n")
        f.write(f"TRANSCRIPT: {writer_row['Transcript']}\n\n")
        f.write(f"JOB: {ds_job}\n")

if __name__ == "__main__":
    extract_demo_samples()
