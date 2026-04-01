# Lesson 7: Connecting AI to the Web (The Interface)

You've built the "Brain" and the "Eyes". Now, we need the "Face". In professional AI, this is called **Deployment**.

## 1. How does a Web App talk to AI?
We use a **Client-Server Architecture**:
- **The Client (Frontend)**: The website you see. It takes your input (Resume text) and sends it over the internet.
- **The Server (Backend)**: Our Python code! It waits for the text, gives it to the Neural Network, and sends the answer back.

## 2. What is Flask?
Flask is a "Micro Web Framework" for Python. It is the bridge between your website and your Neural Network code.

## 3. Inference: The AI in Action
During training, the model learned from 10,000 records. Now, in the UI, we perform **Inference**. 
- **Inference** means taking a brand-new, unseen resume and asking the AI to give us its best guess based on what it learned earlier.

---

# 🎓 The UI Quiz

**Q1: When we run the AI in a website, do we need to retrain it every time a user types a resume?**

**Q2: We use a POST request to send the text to the server. Why is POST better than GET for long resumes?**
- *Hint*: Think about URL length limits!

**Q3: How would a "Interactive Demo" improve your school presentation compared to just showing a terminal full of numbers?**

---
**Next Step**: Answer these, and we will build the **Flask Backend** and **Stunning Frontend**!
