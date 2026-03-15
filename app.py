from flask import Flask, request, jsonify
from flask_cors import CORS
import torch
from sentence_transformers import SentenceTransformer
from retrain_v2 import RecruitmentBrain
from preprocess_data import clean_text
import PyPDF2
import io
import os

app = Flask(__name__)
CORS(app) # Allows our website to talk to this server

# --- TEACHER'S NOTE: THE EXTRACTOR ---
def extract_text_from_pdf(pdf_file):
    """
    Opens the 'PDF Envelope' and pulls out the words.
    """
    reader = PyPDF2.PdfReader(pdf_file)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text

# --- TEACHER'S NOTE: THE LOADING DOCK ---
# We load the Brain and the Eyes once, when the server starts.
print("🧠 Loading the Recruitment Brain (v2)...")
model_sbert = SentenceTransformer('all-MiniLM-L6-v2')
brain = RecruitmentBrain(input_dim=768)
DECISION_THRESHOLD = 0.5  # default, overridden by saved threshold below

if os.path.exists('recruitment_model.pth'):
    checkpoint = torch.load('recruitment_model.pth', map_location='cpu')
    # Support both old-style (plain state_dict) and new-style (dict with threshold)
    if isinstance(checkpoint, dict) and 'model_state' in checkpoint:
        brain.load_state_dict(checkpoint['model_state'])
        DECISION_THRESHOLD = checkpoint.get('threshold', 0.5)
        print(f"✨ v2 Model loaded | Threshold = {DECISION_THRESHOLD}")
    else:
        brain.load_state_dict(checkpoint)
        print("✨ v1 Model loaded | Threshold = 0.5 (default)")
    brain.eval()
else:
    print("⚠️ WARNING: No model weights found. Predictions will be random!")

@app.route('/upload_pdf', methods=['POST'])
def upload_pdf():
    """
    New endpoint to handle PDF file uploads.
    """
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if file and file.filename.endswith('.pdf'):
        text = extract_text_from_pdf(file)
        return jsonify({'text': text})
    
    return jsonify({'error': 'Only PDF files are supported'}), 400

@app.route('/predict', methods=['POST'])
def predict():
    """
    This is the endpoint our website will 'POST' data to.
    """
    data = request.json
    
    # Get the 3 pieces of info from the UI
    resume = data.get('resume', '')
    transcript = data.get('transcript', '')
    job_desc = data.get('job_description', '')
    
    # 1. CLEANING
    cand_text = clean_text(resume + " " + transcript)
    job_text = clean_text(job_desc)
    
    # 2. EMBEDDING (Dual Pass)
    with torch.no_grad():
        cand_emb = model_sbert.encode([cand_text], convert_to_tensor=True)
        job_emb = model_sbert.encode([job_text], convert_to_tensor=True)
        
        # Concatenate for the 768-dim brain
        full_emb = torch.cat((cand_emb, job_emb), dim=1)
        
        # 3. PREDICTING (use predict_proba to get 0-1 probability — Sigmoid applied here)
        prediction = brain.predict_proba(full_emb)
        probability = float(prediction.item())
    
    # 4. DECIDING (use calibrated threshold)
    decision = "SELECT" if probability >= DECISION_THRESHOLD else "REJECT"
    
    print(f"Prediction made: {decision} ({probability:.2f})")
    
    return jsonify({
        'probability': round(probability * 100, 4),
        'decision': decision,
        'message': f"Candidate processed with {probability*100:.4f}% selection confidence."
    })

if __name__ == "__main__":
    print("\n🚀 AI SERVER RUNNING ON http://127.0.0.1:5000")
    print("Open your index.html and start evaluating candidates!")
    app.run(port=5000)
