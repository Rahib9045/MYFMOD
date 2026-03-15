import pandas as pd
import torch
import torch.nn as nn
from sentence_transformers import SentenceTransformer
from preprocess_data import clean_text
import re

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

def debug_model():
    print("🔬 DEBUGGING MODEL ON REAL DATA...")
    
    df = pd.read_csv('mismatch_dataset.csv')
    sample_select = df[df['decision'] == 'select'].iloc[0]
    sample_reject = df[df['decision'] == 'reject'].iloc[0]

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

    print("\n--- Testing REAL Select Sample ---")
    prob_s = get_prob(sample_select['Resume'], sample_select['Transcript'], sample_select['Job_Description'])
    print(f"Prob: {prob_s*100:.2f}% (Expected >50%)")

    print("\n--- Testing REAL Reject Sample ---")
    prob_r = get_prob(sample_reject['Resume'], sample_reject['Transcript'], sample_reject['Job_Description'])
    print(f"Prob: {prob_r*100:.2f}% (Expected <50%)")

if __name__ == "__main__":
    debug_model()
