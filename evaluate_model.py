import torch
import pandas as pd
from sklearn.metrics import confusion_matrix, classification_report
from train_model import RecruitmentBrain
from sentence_transformers import SentenceTransformer
import os

# Teacher's Note: The Final Exam!
# This script tests how well our AI actually performs on a separate "Test Set".

def evaluate_model():
    print("🚀 LOADING FINAL EVALUATION MODULE")
    
    # 1. Load Data
    df = pd.read_csv('cleaned_dataset.csv')
    
    # 2. Load the SBERT "Eyes" and the Neural Network "Brain"
    print("Initializing components...")
    model_sbert = SentenceTransformer('all-MiniLM-L6-v2')
    brain = RecruitmentBrain(input_dim=768)
    
    if os.path.exists('recruitment_model.pth'):
        brain.load_state_dict(torch.load('recruitment_model.pth'))
        brain.eval() # Set to evaluation mode
    else:
        print("Error: weights not found!")
        return

    # 3. Test on a small sample (or full dataset if you prefer)
    print("Analyzing performance...")
    with torch.no_grad():
        # Dual Encoding
        cand_text = [clean_text(str(r) + " " + str(t)) for r, t in zip(df['Resume'][:sample_size], df['Transcript'][:sample_size])]
        job_text = [clean_text(str(j)) for j in df['Job_Description'][:sample_size]]
        
        cand_embs = model_sbert.encode(cand_text, convert_to_tensor=True)
        job_embs = model_sbert.encode(job_text, convert_to_tensor=True)
        
        full_embs = torch.cat((cand_embs, job_embs), dim=1)
        predictions = brain(full_embs)
        y_pred = (predictions > 0.5).float().cpu().numpy()

    # 4. GENERATE THE REPORT
    print("\n" + "="*50)
    print("📊 FINAL PERFORMANCE REPORT (For School Project)")
    print("="*50)
    
    print("\n--- Confusion Matrix ---")
    cm = confusion_matrix(y_true, y_pred)
    print(f"True Rejects: {cm[0][0]}  |  False Alarms: {cm[0][1]}")
    print(f"Missed Talent: {cm[1][0]}  |  True Selects: {cm[1][1]}")
    
    print("\n--- Classification Metrics ---")
    print(classification_report(y_true, y_pred, target_names=['Reject', 'Select']))
    
    print("\n" + "="*50)
    print("Teacher Tip: Use these numbers in your 'Results' chapter!")
    print("="*50)

if __name__ == "__main__":
    evaluate_model()
