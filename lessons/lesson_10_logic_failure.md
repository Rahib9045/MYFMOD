# Lesson 10: The "Genius Chef" Paradox (AI Logic Failure)

You found a huge bug! When we gave it a **Chef**, it gave a **99.9% Select** score. Here is the technical reason why this happened:

## 1. The Model is a "Quality Detector", not a "Role Matcher"
Our model was trained on 10,000 tech resumes. In that data:
- **Selects** = 5,000 high-quality, professional resumes.
- **Rejects** = 5,000 low-quality or incomplete resumes.

The model learned: *"If the text looks professional and has lots of experience, it's a SELECT."*

## 2. No "Hard Negatives" (Role Mismatch)
The AI has **never seen** a high-quality Chef in its training. Because the Chef's resume is beautifully written (Le Cordon Bleu, Executive Chef), the AI says: *"Wow, this is a very high-quality professional! I've learned that high-quality professionals are always SELECT.*"

It doesn't realize that "Kitchen Management" is zero-percent related to "Python Coding" because it was never told to care about that mismatch.

## 3. How to fix it (Negative Sampling)
In professional AI, we fix this by creating **Synthetic Mismatches**:
- We take a "Select" Data Scientist resume.
- We pair it with a "Chef" Job Description.
- We tell the model: *"Even though this resume is great, the answer is REJECT because they don't match!"*

---

### 💡 The "A++" Presentation Answer:
If your teacher asks about this, you can say:
> *"Our model currently suffers from a **Domain Bias**. It has learned to recognize 'Professionalism' but hasn't been trained on 'Role Mismatches' (Negative Sampling). This is a common flaw in early AI models that focus on quality rather than specific alignment."*

---
**Next Step**: Do you want me to try and "Teach" the model about role mismatches so the Chef gets rejected?
