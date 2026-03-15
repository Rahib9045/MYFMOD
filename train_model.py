import pandas as pd
import torch
import torch.nn as nn
import torch.optim as optim
from sentence_transformers import SentenceTransformer
from torch.utils.data import DataLoader, TensorDataset
from sklearn.model_selection import train_test_split
import os

# Teacher's Note: Welcome to the Lab!
# This script is where the actual "Intelligence" is born.

# 1. THE BRAIN ARCHITECTURE (MLP - Dual Embedding Edition)
class RecruitmentBrain(nn.Module):
    def __init__(self, input_dim=768): # 384 (Job) + 384 (Candidate)
        super(RecruitmentBrain, self).__init__()
        # Dual Embedding Input
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

def train_system():
    # Load our clean data
    if not os.path.exists('cleaned_dataset.csv'):
        print("Error: Please run preprocess_data.py first!")
        return
    
    df = pd.read_csv('cleaned_dataset.csv')
    
    # --- PHASE 1: DUAL EMBEDDING ---
    print("Loading SBERT model...")
    model_sbert = SentenceTransformer('all-MiniLM-L6-v2')
    
    print("Encoding Candidates and Jobs separately... (Phase 1/2)")
    cand_text = (df['Resume'] + " " + df['Transcript']).tolist()
    job_text = df['Job_Description'].tolist()
    
    cand_embs = model_sbert.encode(cand_text, show_progress_bar=True, convert_to_tensor=True)
    job_embs = model_sbert.encode(job_text, show_progress_bar=True, convert_to_tensor=True)
    
    print("Combining into 768-dim vectors... (Phase 2/2)")
    embeddings = torch.cat((cand_embs, job_embs), dim=1)
    
    # --- PHASE 2: PREPARING THE EXAM ---
    # Convert 'select' to 1 and 'reject' to 0
    labels = torch.tensor(df['decision'].map({'select': 1.0, 'reject': 0.0}).values).float().unsqueeze(1)
    
    # Split into Training and Testing sets (for School Report!)
    # We keep 20% of data secret to test the AI later.
    X_train, X_test, y_train, y_test = train_test_split(embeddings.cpu(), labels, test_size=0.2, random_state=42)
    
    train_loader = DataLoader(TensorDataset(X_train, y_train), batch_size=32, shuffle=True)

    # --- PHASE 3: TRAINING ---
    brain = RecruitmentBrain(input_dim=768)
    optimizer = optim.Adam(brain.parameters(), lr=0.0005)
    criterion = nn.BCELoss()

    num_epochs = 15 # More study time!
    for epoch in range(num_epochs):
        total_loss = 0
        correct = 0
        processed = 0
        
        print(f"\n--- Epoch {epoch+1}/{num_epochs} ---")
        
        for i, (batch_x, batch_y) in enumerate(train_loader):
            # 1. Forward Pass
            predictions = brain(batch_x)
            loss = criterion(predictions, batch_y)
            
            # 2. Backpropagation
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            
            total_loss += loss.item()
            
            # Calculate accuracy for this batch
            predicted_classes = (predictions > 0.5).float()
            correct += (predicted_classes == batch_y).sum().item()
            processed += batch_y.size(0)
            
            # 🎨 ASCII Progress Bar
            if i % 10 == 0 or i == len(train_loader) - 1:
                progress = (i + 1) / len(train_loader)
                bar_len = 20
                filled_len = int(bar_len * progress)
                bar = '█' * filled_len + '-' * (bar_len - filled_len)
                
                # Dynamic logging
                print(f"\rBatch [{i+1}/{len(train_loader)}] |{bar}| Loss: {loss.item():.4f} | Acc: {100 * correct / processed:.1f}%", end="")

        avg_loss = total_loss / len(train_loader)
        epoch_acc = 100 * correct / processed
        print(f"\n✅ Epoch {epoch+1} Summary: Avg Loss: {avg_loss:.4f} | Accuracy: {epoch_acc:.2f}%")

    # Save the brain!
    torch.save(brain.state_dict(), 'recruitment_model.pth')
    print("\n" + "*"*50)
    print("🎉 MISSION ACCOMPLISHED: Model weights saved to 'recruitment_model.pth'")
    print("*"*50)

if __name__ == "__main__":
    train_system()
