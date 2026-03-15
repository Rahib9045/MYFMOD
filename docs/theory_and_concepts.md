# Theoretical Foundations: AI Recruitment via Semantic Search

This document explains the "How" and "Why" behind the system we are building. Use this as a reference for your school report.

## 1. The Evolution of NLP in Recruitment

### Phase 1: Keyword Matching (Boolean Search)
- **Method**: Searching for exact strings like "Python" or "Java".
- **Problem**: Narrow-minded. A candidate might write "Django expert" but the recruiter filters for "Python". The system misses a perfect match because the text doesn't explicitly contain the keyword.

### Phase 2: Word Embeddings (Word2Vec, GloVe)
- **Method**: Representing words as numbers (vectors) where similar words are close together.
- **Problem**: Context-blind. The word "Bank" in "River bank" and "Investment bank" has the same vector. This leads to confusion in complex job descriptions.

### Phase 3: Transformers (BERT, SBERT)
- **Method**: Models like BERT look at the *entire* sentence to understand context.
- **Advantage**: BERT realizes that "leads a team" and "management experience" are semantically identical in a recruitment context.

## 2. Deep Dive: Sentence-BERT (SBERT)

We use **SBERT** (Sentence-BERT), which is a "Siamese" Neural Network.

### Siamese Architecture
Imagine two identical BERT networks side-by-side:
1. One network processes the **Job Description**.
2. The other processes the **Candidate Resume**.
3. Both networks output a "Vector" (a long list of numbers).

### Why "Siamese"?
By using the same weights for both texts, the model ensures that similar meanings result in similar vector coordinates.

## 3. Measuring Success: Cosine Similarity

Once we have the vectors, how do we know they match? We calculate the **Cosine Similarity**.

- **Formula Concept**: It measures the angle between two vectors in space.
- **Visualizing**: 
  - If the "Resume Vector" point in the same direction as the "Job Vector", the angle is $0^\circ$, and the score is **1.0**.
  - If they are completely different, they are "orthogonal" ($90^\circ$ angle), and the score is **0.0**.

## 4. Why This Matters for Your Project
Using SBERT allows your system to be **intelligent**. It can rank a "Software Engineer" resume at the top for a "Coder" job description, even if the word "Engineer" never appears in the resume. This "semantic understanding" is the core of modern AI recruitment.
