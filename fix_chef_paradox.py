import pandas as pd
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset
from sentence_transformers import SentenceTransformer
import os
import re

# Dual-Embedding Architecture
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

def clean_text(text):
    text = str(text).lower()
    text = re.sub(r'[^a-zA-Z0-9\s]', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def train_dual_embedding():
    print("🚀 STARTING DUAL-EMBEDDING RETRAINING FROM SCRATCH...")
    
    if not os.path.exists('mismatch_dataset.csv'):
        os.system("python generate_negatives.py")
        
    df_raw = pd.read_csv('mismatch_dataset.csv')
    
    # Balance: 1 Select to 1 Reject
    selects = df_raw[df_raw['decision'] == 'select']
    rejects = df_raw[df_raw['decision'] == 'reject']
    df = pd.concat([selects, selects, rejects], ignore_index=True)
    
    model_sbert = SentenceTransformer('all-MiniLM-L6-v2')
    brain = RecruitmentBrain(input_dim=768) # Dual Embedding
    print("🧠 768-Dim Brain initialized.")

    print("Encoding Job and Candidate separately...")
    
    # 1. Encode Candidates (Resume + Transcript)
    cand_text = [clean_text(str(r) + " " + str(t)) for r, t in zip(df['Resume'], df['Transcript'])]
    cand_embs = model_sbert.encode(cand_text, show_progress_bar=True, convert_to_tensor=True)
    
    # 2. Encode Jobs (Job Description Only)
    job_text = [clean_text(str(j)) for j in df['Job_Description']]
    job_embs = model_sbert.encode(job_text, show_progress_bar=True, convert_to_tensor=True)
    
    # 3. Concatenate
    print("Concatenating into 768-dim vectors...")
    final_embs = torch.cat((cand_embs, job_embs), dim=1)
    
    labels = torch.tensor(df['decision'].map({'select': 1.0, 'reject': 0.0}).values).float().unsqueeze(1)
    
    dataset = TensorDataset(final_embs.cpu(), labels)
    loader = DataLoader(dataset, batch_size=32, shuffle=True)
    
    criterion = nn.BCELoss()
    optimizer = optim.Adam(brain.parameters(), lr=0.001)
    
    brain.train()
    for epoch in range(20): # More epochs for the more complex task
        total_loss = 0
        for i, (batch_x, batch_y) in enumerate(loader):
            optimizer.zero_grad()
            outputs = brain(batch_x)
            loss = criterion(outputs, batch_y)
            loss.backward()
            optimizer.step()
            total_loss += loss.item()
        print(f"✅ Epoch {epoch+1} | Loss: {total_loss/len(loader):.4f}")

    torch.save(brain.state_dict(), 'recruitment_model.pth')
    print("\n✨ DUAL-EMBEDDING SYSTEM READY!")

if __name__ == "__main__":
    train_dual_embedding()
