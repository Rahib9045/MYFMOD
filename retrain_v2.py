"""
retrain_v2.py  —  AI Recruitment Model v2
Improvements over v1:
  1. Role-aware hard negatives (same-category cross-role pairings)
  2. Deeper MLP with Dropout for regularization
  3. Learning rate scheduler for better convergence
  4. Post-training threshold calibration (F1-optimal)
  5. Clear accuracy report at the end
"""

import pandas as pd
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset
from sentence_transformers import SentenceTransformer
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, f1_score
import numpy as np
import random
import re
import os

# ─── CONFIG ──────────────────────────────────────────────────────────────────
DATASET_PATH  = r'e:\PRTFLIO\ai recrut\archive\dataset.csv'
OUTPUT_MODEL  = 'recruitment_model.pth'
EPOCHS        = 25
LR            = 0.0005
BATCH_SIZE    = 32
NEGATIVES_PER_SELECT = 1   # 1x keeps class ratio close to 50/50
# ─────────────────────────────────────────────────────────────────────────────

def clean_text(text):
    text = str(text).lower()
    text = re.sub(r'[^a-zA-Z0-9\s]', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

# ─── MODEL ───────────────────────────────────────────────────────────────────
class RecruitmentBrain(nn.Module):
    """Deep MLP with Dropout. NOTE: No Sigmoid on output — using BCEWithLogitsLoss."""
    def __init__(self, input_dim=768):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(input_dim, 512),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(512, 256),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(256, 64),
            nn.ReLU(),
            nn.Linear(64, 1)
            # No Sigmoid here — BCEWithLogitsLoss handles it numerically
        )

    def forward(self, x):
        return self.net(x)

    def predict_proba(self, x):
        """Use this at inference time to get a 0-1 probability."""
        return torch.sigmoid(self.forward(x))

# ─── HARD NEGATIVE GENERATION ────────────────────────────────────────────────
def build_training_data(df):
    """
    Smarter hard-negatives: pair each SELECT with jobs from DIFFERENT roles.
    This teaches the model role-specificity, not just keyword matching.
    """
    print("🛠️  Building role-aware hard negatives...")

    selects = df[df['decision'] == 'select'].copy()
    rejects  = df[df['decision'] == 'reject'].copy()

    # Build a map: role → list of job descriptions for that role
    role_to_jobs = df.groupby('Role')['Job_Description'].apply(list).to_dict()
    all_roles = list(role_to_jobs.keys())

    hard_negatives = []
    for _, row in selects.iterrows():
        candidate_role = row['Role']
        # Pick a different role to sample a mismatched job from
        other_roles = [r for r in all_roles if r != candidate_role]
        if not other_roles:
            continue
        for _ in range(NEGATIVES_PER_SELECT):
            wrong_role = random.choice(other_roles)
            wrong_job  = random.choice(role_to_jobs[wrong_role])
            hard_negatives.append({
                'Name': row['Name'],
                'Resume': row['Resume'],
                'Transcript': row['Transcript'],
                'Job_Description': wrong_job,
                'Role': row['Role'],
                'decision': 'reject'
            })

    neg_df = pd.DataFrame(hard_negatives)
    combined = pd.concat([df, neg_df], ignore_index=True)
    print(f"   Original rows:      {len(df):,}")
    print(f"   Hard negatives:     {len(neg_df):,}")
    print(f"   Total training set: {len(combined):,}")
    return combined

# ─── THRESHOLD CALIBRATION ───────────────────────────────────────────────────
def find_best_threshold(brain, X_val, y_val):
    """
    Sweep thresholds from 0.2 to 0.8, pick the one with the highest F1.
    """
    brain.eval()
    with torch.no_grad():
        probs = torch.sigmoid(brain(X_val)).squeeze().numpy()  # apply sigmoid for BCEWithLogitsLoss

    best_t, best_f1 = 0.5, 0.0
    for t in np.arange(0.20, 0.81, 0.01):
        preds = (probs >= t).astype(int)
        f1 = f1_score(y_val.numpy(), preds, zero_division=0)
        if f1 > best_f1:
            best_f1 = f1
            best_t  = round(float(t), 2)

    print(f"\n🎯 Best threshold: {best_t:.2f}  (F1 = {best_f1:.4f})")
    return best_t

# ─── MAIN ────────────────────────────────────────────────────────────────────
def main():
    print("=" * 55)
    print("   AI RECRUITMENT MODEL v2 — FULL RETRAIN")
    print("=" * 55)

    # 1. Load & build dataset
    print("\n📂 Loading dataset...")
    df = pd.read_csv(DATASET_PATH)
    print(f"   Loaded {len(df):,} rows. Roles: {df['Role'].nunique()}")

    df = build_training_data(df)

    # 2. Encode with SBERT (dual embedding)
    print("\n🔡 Loading SBERT encoder...")
    sbert = SentenceTransformer('all-MiniLM-L6-v2')

    cand_texts = [clean_text(str(r) + " " + str(t))
                  for r, t in zip(df['Resume'], df['Transcript'])]
    job_texts  = [clean_text(str(j)) for j in df['Job_Description']]

    print("   Encoding candidates (this takes a few minutes)...")
    cand_embs = sbert.encode(cand_texts, batch_size=128, show_progress_bar=True,
                             convert_to_tensor=True)
    print("   Encoding jobs...")
    job_embs  = sbert.encode(job_texts,  batch_size=128, show_progress_bar=True,
                             convert_to_tensor=True)

    X = torch.cat((cand_embs, job_embs), dim=1).cpu()
    y = torch.tensor(
        df['decision'].map({'select': 1.0, 'reject': 0.0}).values
    ).float().unsqueeze(1)

    # 3. Train / val split
    X_train, X_val, y_train, y_val = train_test_split(
        X, y, test_size=0.15, random_state=42, stratify=y
    )

    train_loader = DataLoader(
        TensorDataset(X_train, y_train), batch_size=BATCH_SIZE, shuffle=True
    )

    # 4. Train
    n_pos = int(y_train.sum().item())
    n_neg = len(y_train) - n_pos
    pos_weight = torch.tensor([n_neg / n_pos]) if n_pos > 0 else torch.tensor([1.0])
    print(f"\n⚖️  Class balance — SELECT: {n_pos}, REJECT: {n_neg}, pos_weight: {pos_weight.item():.2f}")

    print(f"\n🧠 Training deeper MLP with Dropout ({EPOCHS} epochs)...")
    brain     = RecruitmentBrain(input_dim=768)
    criterion = nn.BCEWithLogitsLoss(pos_weight=pos_weight)  # numerically stable + handles imbalance
    optimizer = optim.Adam(brain.parameters(), lr=LR, weight_decay=1e-4)
    scheduler = optim.lr_scheduler.StepLR(optimizer, step_size=8, gamma=0.5)

    brain.train()
    for epoch in range(EPOCHS):
        total_loss = 0
        for bx, by in train_loader:
            optimizer.zero_grad()
            loss = criterion(brain(bx), by)
            loss.backward()
            optimizer.step()
            total_loss += loss.item()
        scheduler.step()
        if (epoch + 1) % 5 == 0 or epoch == 0:
            print(f"   Epoch {epoch+1:02d}/{EPOCHS} | Loss: {total_loss/len(train_loader):.4f}")

    # 5. Calibrate threshold on val set
    best_threshold = find_best_threshold(brain, X_val, y_val.squeeze())

    # 6. Final accuracy report
    brain.eval()
    with torch.no_grad():
        val_probs = torch.sigmoid(brain(X_val)).squeeze().numpy()
    val_preds = (val_probs >= best_threshold).astype(int)
    print("\n📊 VALIDATION REPORT")
    print(classification_report(y_val.squeeze().numpy(), val_preds,
                                target_names=['REJECT', 'SELECT']))

    # 7. Save model + threshold
    torch.save({
        'model_state': brain.state_dict(),
        'threshold':   best_threshold
    }, OUTPUT_MODEL)
    print(f"\n✅ Model saved → {OUTPUT_MODEL}")
    print(f"   Threshold baked in: {best_threshold}")
    print("\n⚠️  Also update app.py to load the new threshold from the saved file.")

if __name__ == "__main__":
    main()
