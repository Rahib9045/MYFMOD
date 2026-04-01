# Step 1: Exploratory Data Analysis (EDA) & Cleaning

Before we train our Neural Network, we must understand and clean our data. This is a critical section for any school project report.

## 1. What is EDA?
Exploratory Data Analysis is the process of "interviewing" your data. We ask questions like:
- How many candidates were selected vs. rejected? (Class Imbalance)
- Are there any empty (Null) resumes or transcripts?
- What are the most common words in "Selected" transcripts vs. "Rejected" ones?

## 2. Cleaning the Text
Computers are sensitive to noise. We will perform the following steps:
1.  **Lowercasing**: "Python" and "python" should be treated as the same word.
2.  **Removing Special Characters**: Removing punctuation that doesn't add semantic value.
3.  **Handling Nulls**: If a record has a missing `Job_Description`, we can't rank it, so we remove it.

## 3. Handling Class Imbalance
In recruitment datasets, usually there are many more "Rejects" than "Selects". 
- **The Problem**: If 90% are rejects, a "lazy" model could just say "Reject" to everyone and be 90% accurate!
- **Our Solution**: We will check the ratio and potentially use techniques like **Weighted Loss** or **Oversampling** to make sure the model actually learns what a "Select" looks like.

## How to proceed
Once you move the CSV file (likely named `AI_Recruitment_Dataset.csv`) into the `e:\PRTFLIO\ai recrut` folder, we will:
1. Run a script to generate charts (bar charts of decisions, word clouds).
2. Create a "Cleaned" version of the dataset.
3. Begin the SBERT embedding process.
