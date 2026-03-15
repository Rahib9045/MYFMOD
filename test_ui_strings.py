import torch
import torch.nn as nn
from sentence_transformers import SentenceTransformer
import re

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

def test_ui_strings():
    print("🔬 TESTING UI STRINGS...")
    model_sbert = SentenceTransformer('all-MiniLM-L6-v2')
    brain = RecruitmentBrain(input_dim=768)
    brain.load_state_dict(torch.load('recruitment_model.pth'))
    brain.eval()

    # The exact strings from index.html
    ds_resume = "Jeffrey Taylor\nData Scientist\n\nResults-driven data scientist with 5+ years of experience in developing and implementing data-driven solutions. Skilled in statistics, machine learning, deep learning, SQL, and data visualization."
    ds_transcript = "Jeffrey Taylor: I have a background in computer science and mathematics, and I've been working in data analysis for about five years now... I've used Python for a variety of tasks, from data cleaning to machine learning."
    ds_job = "We're seeking a talented Data Scientist to work on AI model development and bring new ideas to life."

    c_text = clean_text(ds_resume + " " + ds_transcript)
    j_text = clean_text(ds_job)

    with torch.no_grad():
        c_emb = model_sbert.encode([c_text], convert_to_tensor=True)
        j_emb = model_sbert.encode([j_text], convert_to_tensor=True)
        full_emb = torch.cat((c_emb, job_emb), dim=1) if 'job_emb' in locals() else torch.cat((c_emb, j_emb), dim=1)
        prob = brain(full_emb).item()
        print(f"Jeffrey Taylor UI Match Prob: {prob*100:.4f}%")

    # Let's try Game Dev (which supposedly works)
    gd_resume = "Cynthia Avila\nGame Developer\n\nHighly motivated and experienced game developer with a strong background in Unity and Unreal Engine. Skilled in C++ and Java."
    gd_transcript = "Cynthia Avila: So, I've been working in the gaming industry for about five years now, starting as a junior programmer and working my way up to lead programmer... I've always been passionate about game development."
    gd_job = "As a Game Developer, you will play a pivotal role in shaping the future of healthcare."

    c_text = clean_text(gd_resume + " " + gd_transcript)
    j_text = clean_text(gd_job)

    with torch.no_grad():
        c_emb = model_sbert.encode([c_text], convert_to_tensor=True)
        j_emb = model_sbert.encode([j_text], convert_to_tensor=True)
        full_emb = torch.cat((c_emb, j_emb), dim=1)
        prob = brain(full_emb).item()
        print(f"Cynthia Avila UI Match Prob: {prob*100:.4f}%")

if __name__ == "__main__":
    test_ui_strings()
