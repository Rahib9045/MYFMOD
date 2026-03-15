import torch
import torch.nn as nn
from sentence_transformers import SentenceTransformer
from preprocess_data import clean_text
import os

# Dual architecture
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

def verify_dual_embedding():
    print("🕵️ VERIFYING CHEF PARADOX FIX (DUAL-EMBEDDING)...")
    
    # Load model
    model_sbert = SentenceTransformer('all-MiniLM-L6-v2')
    brain = RecruitmentBrain(input_dim=768)
    brain.load_state_dict(torch.load('recruitment_model.pth'))
    brain.eval()

    # The "Chef" Case (Mismatch)
    chef_resume = "EXPERIENCE: Executive Chef at Blue Lagoon Bistro. Culinary Leadership, Food Safety (HACCP). EDUCATION: Culinary Arts Degree from Le Cordon Bleu."
    chef_transcript = "I lead from the front in the kitchen. I ensure the line is organized and communication is seamless."
    job_desc = "Data Scientist needed to lead our predictive modeling team. Experience with Python, SQL, and deep learning required."
    
    # The "Data Scientist" Case (Match)
    ds_resume = "Data Scientist with experience in building machine learning models. Skilled in Python, SQL, and Data Visualization."
    ds_transcript = "I believe in data-driven decisions. My last project involved building a random forest model."

    def get_prob(res, trans, job):
        # 💡 DUAL ENCODING
        cand_text = clean_text(str(res) + " " + str(trans))
        job_text = clean_text(job)
        
        with torch.no_grad():
            cand_emb = model_sbert.encode([cand_text], convert_to_tensor=True)
            job_emb = model_sbert.encode([job_text], convert_to_tensor=True)
            full_emb = torch.cat((cand_emb, job_emb), dim=1)
            return brain(full_emb).item()

    chef_prob = get_prob(chef_resume, chef_transcript, job_desc)
    ds_prob = get_prob(ds_resume, ds_transcript, job_desc)

    print(f"\n👨‍🍳 Chef Score: {chef_prob*100:.2f}%")
    print(f"📊 Data Scientist Score: {ds_prob*100:.2f}%")

    if chef_prob < 40 and ds_prob > 50:
        print("\n✅ SUCCESS: Logic is perfect! Chef is rejected, Scientist is selected.")
    else:
        print("\n❌ FAILED: Still some mismatch.")

if __name__ == "__main__":
    verify_dual_embedding()
