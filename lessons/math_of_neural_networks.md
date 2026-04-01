# Lesson 3.5: The Math Behind the Brain

Since this is a school project, your teacher will be very impressed if you can explain the basic equations. Don't worry, it's simpler than it looks!

## 1. The Core Equation: $y = wx + b$
Every neuron in our network is basically a tiny math problem.
- **$x$ (Input)**: The 384 numbers we got from SBERT.
- **$w$ (Weight)**: How important is this input? (e.g., if $x_1$ is the word "Python", it might have a high weight for a Dev role).
- **$b$ (Bias)**: An extra number that helps the neuron decide when to "fire".
- **$y$ (Output)**: The result.

**In class, you can say**: "A neuron calculates the *weighted sum* of its inputs plus a bias."

## 2. Activation Function: ReLU
You asked about this! ReLU stands for **Rectified Linear Unit**.
- **The Math**: $f(x) = \max(0, x)$
- **What it does**: If the neuron's result is negative (dead), it turns it into zero. If it's positive, it passes it through.
- **Why?**: It creates "Sparsity". By silencing non-essential neurons, the network focuses only on the most important features. It also helps the math "flow" faster through the layers.

## 3. The "Learning" Math: Loss and Backpropagation
How does the AI know it's wrong?
1. **Loss Function**: It calculates the "Error" (Distance between the AI's guess and the actual Hiring Decision).
2. **Backpropagation**: This uses **Calculus** (specifically the Chain Rule) to work backward from the error and slightly tweak every single **Weight ($w$)** in the network to be better next time.

---

# 🎓 Training Quiz (Final One before Code!)

**Q1: If our model is 50% accurate, it is effectively just "Guessing" (like flipping a coin). True or False?**

**Q2: If "Backpropagation" is the teacher correcting a student, what are the "Weights"?**
- A) The student's grades.
- B) The student's knowledge/memory that gets adjusted.
- C) The school building.

**Q3: We have 10,000 records. If we train on all of them at once, it might crash the RAM. We instead use "Batches" (e.g., 32 records at a time). Why is "Batching" helpful for learning?**

---
**Next Step**: Answer these, and I will unveil the **Training Script**!
