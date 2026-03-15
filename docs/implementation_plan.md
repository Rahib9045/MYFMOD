# AI Recruitment System: Educational Implementation Plan

This plan is redesigned for a **school project**, focusing on the theoretical foundations of Natural Language Processing (NLP) and Neural Networks in the context of recruitment.

## Kaggle Dataset Integration: AI Recruitment Pipeline

We will use the **AI Recruitment Pipeline Dataset** which contains over 10,000 records.

### Key Data Columns:
- **Resume & Job_Description**: Used for semantic similarity.
- **Transcript**: Provides deep context from interviews.
- **Decision (Select/Reject)**: Our "Ground Truth" for training a classification model.

## Proposed Architecture (Enhanced)

### 1. Semantic Ranking (Unsupervised)
We will calculate the similarity between the `Resume` + `Transcript` and the `Job_Description`. This gives us a raw "Match Score".

### 2. Decision Prediction (Supervised Learning)
Given that we have historical hiring decisions, we can train a **Neural Network Classifier**:
- **Input**: The combined SBERT embeddings of the resume, transcript, and job description.
- **Architecture**: A Multi-Layer Perceptron (MLP) with Dense layers and Dropout for regularization.
- **Output**: Probability of the candidate being "Selected".

## Implementation Workflow (Learning Focused)
1. **Initial Analysis**: Clean the Kaggle CSV and handle missing values.
2. **Feature Fusion**: Combine the `Resume` and `Transcript` into a single "Candidate Profile".
3. **SBERT Transformers**: Batch process the 10k records to generate embeddings.
4. **Training the MLP**: Build and train a neural network using `PyTorch` or `TensorFlow`.
5. **Validation**: Test the model's accuracy, precision, and recall against the original human decisions.



## Interactive Demo (Presentation Layer)

To make the school presentation "pop," we will build a web interface.

### 1. Technology Stack
- **Backend**: Flask (Python). This will load our `recruitment_model.pth` and run predictions.
- **Frontend**: HTML5, Vanilla CSS (Glassmorphism), and JavaScript (Fetch API).
- **Communication**: The frontend will send a POST request with the text, and the backend will return the probability.

### 2. UI Features
- Text areas for **Resume**, **Transcript**, and **Job Description**.
- A "Analyze Candidate" button.
- A **"Randomize Case"** button that pairs a random candidate with a random job description from a library of 20+ templates.
- Dynamic result display (Visual progress bar for probability).
- Select/Reject badge.

