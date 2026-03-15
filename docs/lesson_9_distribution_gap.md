# Lesson 9: The Distribution Gap (Why it Rejected!)

You noticed that even a "perfect" candidate got rejected with a 0.02% score. Why?

## 1. The Length Bias
Your AI was trained on 10,174 real-world resumes that are very long. 
- **Training Data**: 2,800 characters on average.
- **Your Sample**: 150 characters.

The AI's "Brain" (the MLP) has learned that successful candidates are detailed. When you give it a "Tweet-sized" resume, it thinks: *"This person didn't provide enough information, so they must be a Reject."*

## 2. Information Density
SBERT turns text into a vector (numbers). If the text is short, the vector is very "sparse" (less information). The MLP sees this sparse vector as a signal of a "Weak Candidate."

## 3. How to fix it: "Feed the Beast"
To get a **SELECT** result, the text needs to "look" like the training data. This means:
- Adding more Bullet Points.
- Using professional headers (EXPERIENCE, EDUCATION, PROJECTS).
- Providing more context in the Interview Transcript.

---

### 💡 School Presentation Tip:
*"Our AI demonstrated a clear 'Detail Bias'. It rejected short samples because it was trained on comprehensive, long-form professional documents. This shows that AI doesn't just look for keywords—it looks for the **pattern of a professional application**."*
