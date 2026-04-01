# Lesson 5: Hyperparameter Tuning (Tuning the Knobs)

Your model hit **58.78% accuracy**. In the world of AI, this is called a **"Base Model"**. It's better than a coin flip (50%), which means the AI *is* learning, but it's still a bit "dim".

In a school project, showing how you **improved** a model is often worth more marks than having a perfect model on the first try!

## 1. Why 58%?
Neural Networks are like students. Sometimes they need:
- **More Study Time (Epochs)**: We only did 5 laps. Maybe it needs 10 or 20 to see the patterns.
- **A Bigger Brain (Hidden Layers)**: Maybe our 128/64 neurons aren't enough to understand 10,000 resumes.
- **A Slower Teacher (Learning Rate)**: If the learning rate is too high, the optimizer "jumps" over the best settings.

## 2. Common "Tuning Knobs" (Hyperparameters)
These are settings we choose *before* training starts:
1.  **Learning Rate (lr)**: How big a step the optimizer takes. (Usually 0.001 or 0.0001).
2.  **Epochs**: How many times we show the data to the AI.
3.  **Layer Size**: The number of neurons in the hidden layers.

## 3. The "Overfitting" Trap
If we train for 1,000 epochs, the AI might just *memorize* the 10,000 names instead of learning how to judge a resume. This is like a student who memorizes the practice exam but fails the real one!

---

# 🎓 Tuning Quiz

**Q1: If we want to give the AI "more time to study," which setting should we increase?**

**Q2: If the AI is "memorizing" instead of "learning" (high accuracy on training data, low accuracy on new data), what is this called?**

**Q3: Looking at your `train_model.py`, we have 5 epochs. What happens to yours if you change that number to 10?**

---
**Next Step**: Answer these, and then we will update the script to **"Tuned Model v2"** and try to cross that 70% mark!
