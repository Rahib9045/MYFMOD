# Kaggle Dataset Analysis Report (EDA Findings)

I have analyzed your dataset (`dataset.csv`), and the results are excellent for a school project. Here are the key findings you can include in your report:

## 1. Data Scale and Quality
- **Size**: 10,174 unique applicant records. This is a "Goldilocks" size—large enough to train a robust neural network, but small enough to run on a standard laptop.
- **Cleanliness**: 0 missing values! Every candidate has a Name, Role, Transcript, Resume, Decision, and Job Description.

## 2. The Golden Ratio: Class Balance
In most recruitment datasets, you see 90% rejections and 10% selections. However, your dataset is **perfectly balanced**:
- **Reject**: 50.27%
- **Select**: 49.73%

> [!NOTE]
> **Why this matters for your school project**: A balanced dataset means our model won't have a "bias" towards rejecting people. It makes our training process much smoother and our accuracy scores more meaningful.

## 3. Feature Information
- **Resumes (avg. 2,800 chars)**: Standard length for a one or two-page resume.
- **Transcripts (avg. 4,300 chars)**: These are quite detailed! This is the most valuable part of the dataset because it contains the behavioral data that a simple resume lacks.
- **Job Descriptions (avg. 372 chars)**: Short and concise, focusing on the core requirements.

## 4. Proposed Learning Strategy
Since we have these rich "Select/Reject" labels, we will move from a simple **Similarity Matcher** to a **Predictive Neural Network**.

### The Flow:
1. **Combine**: Merge `Resume` + `Transcript`.
2. **Embed**: Use SBERT to turn that text into numbers.
3. **Classify**: Train a Neural Network to look at those numbers and predict if the `decision` will be "Select" or "Reject".

---
**Next Step**: We will create a `preprocess_data.py` script. I will write it as a walkthrough so you can explain each step (Normalizing, Tokenizing) to your teacher.
