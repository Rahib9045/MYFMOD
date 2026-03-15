import json
import torch
from sentence_transformers import SentenceTransformer, util
import os

# Filter out common SBERT warnings
os.environ["TOKENIZERS_PARALLELISM"] = "false"

def rank_resumes(job_id):
    # Load data
    with open('data/resumes.json', 'r') as f:
        resumes = json.load(f)
    
    with open('data/job_descriptions.json', 'r') as f:
        job_descriptions = json.load(f)
    
    # Find the target job description
    job = next((j for j in job_descriptions if j['id'] == job_id), None)
    if not job:
        print(f"Job ID {job_id} not found.")
        return

    print(f"\n--- Ranking for Job: {job['title']} ---")
    
    # Initialize model
    model = SentenceTransformer('all-MiniLM-L6-v2')

    # Prepare texts for embedding
    resume_texts = [f"{r['skills']} {r['experience']}" for r in resumes]
    job_text = f"{job['title']} {job['description']}"

    print(f"Job Text: {job_text[:100]}...")

    # Compute embeddings
    resume_embeddings = model.encode(resume_texts, convert_to_tensor=True)
    job_embedding = model.encode(job_text, convert_to_tensor=True)

    # Compute cosine similarity
    # util.cos_sim returns a matrix of shape [len(resumes), len(job_texts)]
    cosine_scores = util.cos_sim(resume_embeddings, job_embedding)

    # Combine results and sort
    results = []
    for i in range(len(resumes)):
        score = cosine_scores[i][0].item()
        results.append({
            "name": resumes[i]['name'],
            "score": score,
            "text": resume_texts[i][:50]
        })

    # Sort by score descending
    results.sort(key=lambda x: x['score'], reverse=True)

    # Display results
    for res in results:
        print(f"Candidate: {res['name']:<15} | Score: {res['score']:.4f} | Skills: {res['text']}...")

if __name__ == "__main__":
    rank_resumes("job_001") # ML Engineer
    rank_resumes("job_002") # Full Stack
