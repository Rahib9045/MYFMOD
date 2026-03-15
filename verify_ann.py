import torch
import torch.nn as nn
from sentence_transformers import SentenceTransformer
from preprocess_data import clean_text
import os

# Independent architecture
class RecruitmentBrain(nn.Module):
    def __init__(self, input_dim):
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

def verify_ann_marshall():
    print("🕵️ VERIFYING ANN MARSHALL (GAME DEV) SCORE...")
    
    # Load model
    model_sbert = SentenceTransformer('all-MiniLM-L6-v2')
    brain = RecruitmentBrain(input_dim=384)
    brain.load_state_dict(torch.load('recruitment_model.pth'))
    brain.eval()

    ann_resume = "Here is a professional resume for Ann Marshall: Highly motivated Software Engineer with a focus on game development. Expert in Unity and C++. Senior Game Developer at GamePro Studios."
    ann_transcript = "I've been working at GamePro Studios for five years. I love building immersive experiences and optimizing C++ code."
    ann_job = "Looking for a Game Developer with C++ and Unity experience. Help us build mobile games!"

    def get_prob(res, trans, job):
        text = clean_text(str(res) + " " + str(trans), job_text=job)
        with torch.no_grad():
            emb = model_sbert.encode([text], convert_to_tensor=True)
            return brain(emb).item()

    ann_prob = get_prob(ann_resume, ann_transcript, ann_job)
    print(f"\n🎮 Ann Marshall Score: {ann_prob*100:.2f}%")

    if ann_prob > 0.5:
        print("\n✅ SUCCESS: Ann still passes!")
    else:
        print("\n❌ FAILED: The model is now too strict.")

if __name__ == "__main__":
    verify_ann_marshall()
