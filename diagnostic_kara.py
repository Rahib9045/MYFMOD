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

def diagnose_kara():
    print("🔬 DIAGNOSING KARA HARVEY PREDICTION...")
    
    model_sbert = SentenceTransformer('all-MiniLM-L6-v2')
    brain = RecruitmentBrain(input_dim=768)
    brain.load_state_dict(torch.load('recruitment_model.pth'))
    brain.eval()

    resume = "Kara Harvey. Full Stack Developer. Expert in React, Node.js, and MongoDB. Professional summary includes building large scale web applications and managing cloud infrastructure. Skills: JavaScript, Python, AWS, SQL."
    transcript = "I have been developing software for 5 years. I specialize in building responsive frontends and reliable backends. My last project served 10,000 users daily."
    job_desc = "We are seeking a Full Stack Developer to join our core team. Must be proficient in modern JS frameworks and AWS."

    print(f"\nCleaning text...")
    cand_text = clean_text(resume + " " + transcript)
    job_text = clean_text(job_desc)
    print(f"Cleaned Candidate: {cand_text[:50]}...")
    print(f"Cleaned Job: {job_text[:50]}...")

    with torch.no_grad():
        cand_emb = model_sbert.encode([cand_text], convert_to_tensor=True)
        job_emb = model_sbert.encode([job_text], convert_to_tensor=True)
        full_emb = torch.cat((cand_emb, job_emb), dim=1)
        
        print(f"\nVector Stats:")
        print(f"Candidate Emb Sum: {cand_emb.sum().item():.4f}")
        print(f"Job Emb Sum: {job_emb.sum().item():.4f}")
        
        prediction = brain(full_emb)
        prob = prediction.item()
        print(f"\nFINAL PROBABILITY: {prob*100:.8f}%")

if __name__ == "__main__":
    diagnose_kara()
