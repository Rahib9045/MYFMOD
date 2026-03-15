import pandas as pd
import os

def perform_eda(file_path):
    print(f"Loading dataset from: {file_path}...")
    df = pd.read_csv(file_path)
    
    print("\n--- Basic Information ---")
    print(df.info())
    
    print("\n--- First 5 Rows ---")
    print(df.head())
    
    print("\n--- Missing Values ---")
    print(df.isnull().sum())
    
    print("\n--- decision Distribution ---")
    dist = df['decision'].value_counts(normalize=True) * 100
    print(dist)
    
    print("\n--- Unique Roles ---")
    print(df['Role'].unique()[:10]) # Show first 10 for brevity
    
    # Calculate average lengths of text fields
    print("\n--- Average Text Lengths (Characters) ---")
    for col in ['Resume', 'Transcript', 'Job_Description']:
        avg_len = df[col].apply(lambda x: len(str(x))).mean()
        print(f"{col}: {avg_len:.2f}")

if __name__ == "__main__":
    csv_path = r'e:\PRTFLIO\ai recrut\archive\dataset.csv'
    if os.path.exists(csv_path):
        perform_eda(csv_path)
    else:
        print(f"Error: {csv_path} not found.")
