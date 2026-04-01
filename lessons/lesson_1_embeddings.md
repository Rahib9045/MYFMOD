# Lesson 1: Understanding "Digital Meaning" (Embeddings)

In this lesson, we explain how computers "read" text. This is the foundation of your AI project.

## 1. What is an Embedding?
Think of a word like a "point" in a giant map. In this map:
- Words with similar meanings (e.g., "Python" and "Coding") are physically close to each other.
- Words with different meanings (e.g., "Python" and "Pizza") are very far apart.

An **Embedding** is just the set of coordinates (numbers) for that point. A typical SBERT embedding has 384 numbers!

## 2. Why Transformers (SBERT)?
Early AI models looked at words one by one. Transformers are different because they look at the **context**.
- *Example*: "He had a **break** at work" vs "He will **break** the glass."
- A transformer realizes that "break" means two different things based on the words surrounding it.

---

# 🎓 Quick Quiz (Test Yourself!)

Read the questions below and try to answer them. I will check your answers in our chat!

**Q1: If the Cosine Similarity score between a Resume and a Job is 0.95, what does that tell you?**
- A) They are almost identical in meaning.
- B) They have absolutely no relation.
- C) They share exactly 95 words.

**Q2: Why is "Semantic Search" better than "Keyword Search" for recruitment?**

**Q3: What does the 'S' in SBERT stand for, and why is it important for moving from words to full Resumes?**

---
**Next Step**: Once you answer these, we will move to **Lesson 2: Data Cleaning** where you'll help me write the code to clean the Kaggle dataset!
