import pandas as pd
import re
import os

def clean_text(text, job_text=None):
    # CRITICAL FIX: Put Job Text at the START so SBERT doesn't truncate it!
    if job_text:
        text = "JOB: " + str(job_text) + " | CANDIDATE: " + str(text)
    """
    Teacher's Note: This is our cleaning department! 
    Every bit of text passes through here.
    """
    if pd.isna(text):
        return ""
    
    # 1. Convert to string and Lowercase
    # Why? So 'Python' and 'python' match.
    text = str(text).lower()
    
    # 2. Remove Newlines and extra spaces
    # You found '\n' in the practice! We swap it for a single space.
    text = text.replace('\n', ' ')
    
    # 3. Remove Punctuation and Special Characters
    # You found '!!!!' and '...'. This Regex finds everything NOT a letter or number.
    text = re.sub(r'[^a-zA-Z0-9\s]', '', text)
    
    # 4. Remove extra whitespace
    # Changes "hello     world" to "hello world"
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text

def preprocess_pipeline(input_file):
    print(f"Reading {input_file}...")
    df = pd.read_csv(input_file)
    
    # The columns we want to clean
    text_columns = ['Resume', 'Transcript', 'Job_Description']
    
    print("Starting the cleaning process for 10,000+ records...")
    for col in text_columns:
        print(f"Cleaning column: {col}...")
        # .apply() runs our clean_text function on EVERY row automatically!
        df[col] = df[col].apply(clean_text)
    
    output_file = 'cleaned_dataset.csv'
    df.to_csv(output_file, index=False)
    print(f"✨ Success! Cleaned data saved to {output_file}")
    
    # Let's show a "Before and After" for learning
    return df.iloc[0]['Resume'][:100]

if __name__ == "__main__":
    raw_csv = r'e:\PRTFLIO\ai recrut\archive\dataset.csv'
    if os.path.exists(raw_csv):
        sample = preprocess_pipeline(raw_csv)
        print(f"\nSample Cleaned Text: {sample}...")
    else:
        print("Error: Could not find dataset.csv in /archive.")
