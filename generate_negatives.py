import pandas as pd
import random

def generate_hard_negatives():
    print("🛠️ GENERATING HARD NEGATIVES (ROLE MISMATCHES)...")
    df = pd.read_csv(r'e:\PRTFLIO\ai recrut\archive\dataset.csv')
    
    # We only care about the qualified candidates (SELECTS)
    selects = df[df['decision'] == 'select'].copy()
    
    negative_samples = []
    
    # List of unique jobs in our dataset
    unique_jobs = list(df['Job_Description'].unique())
    
    for idx, row in selects.iterrows():
        # Pick a job that is NOT the one they applied for
        wrong_job = random.choice(unique_jobs)
        while str(row['Job_Description'])[:50] in str(wrong_job): # Basic check to avoid same job
            wrong_job = random.choice(unique_jobs)
            
        # Create a "Negative" record
        negative_samples.append({
            'Name': row['Name'],
            'Resume': row['Resume'],
            'Transcript': row['Transcript'],
            'Job_Description': wrong_job,
            'decision': 'reject', # We explicitly label this as REJECT
            'Role': row['Role']
        })

    # Combine with original data
    neg_df = pd.DataFrame(negative_samples)
    final_df = pd.concat([df, neg_df], ignore_index=True)
    
    final_df.to_csv('mismatch_dataset.csv', index=False)
    print(f"✅ Created 'mismatch_dataset.csv' with {len(neg_df)} new hard negatives!")
    print(f"Total training samples: {len(final_df)}")

if __name__ == "__main__":
    generate_hard_negatives()
