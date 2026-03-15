import pandas as pd
import json

def extract_templates():
    print("💎 EXTRACTING 20+ TEMPLATES FOR RANDOMIZER...")
    df = pd.read_csv(r'e:\PRTFLIO\ai recrut\archive\dataset.csv')
    
    # 1. Extract 20 Diverse Candidates
    # We'll take a mix of Selects and Rejects for realism
    candidates = []
    sample_size = 25 # Extra just in case
    
    cand_subset = df.head(sample_size)
    for _, row in cand_subset.iterrows():
        candidates.append({
            'name': row['Name'],
            'resume': str(row['Resume']),
            'transcript': str(row['Transcript']),
            'original_role': row['Role']
        })
    
    # 2. Extract 20 Diverse Job Descriptions
    # Unique roles to ensure variety
    jobs = []
    unique_roles = df['Role'].unique()[:20]
    for role in unique_roles:
        job_desc = df[df['Role'] == role].iloc[0]['Job_Description']
        jobs.append({
            'role': role,
            'desc': str(job_desc)
        })
        
    # Save to JSON for easy JS integration
    templates = {
        'candidates': candidates,
        'jobs': jobs
    }
    
    with open('ui_templates.json', 'w', encoding='utf-8') as f:
        json.dump(templates, f, indent=4)
        
    print(f"✅ Extracted {len(candidates)} candidates and {len(jobs)} jobs into 'ui_templates.json'")

if __name__ == "__main__":
    extract_templates()
