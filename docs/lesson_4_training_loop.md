# Lesson 4: The Training Loop (Learning from Mistakes)

This is the final theoretical hurdle before we run the code. "Training" is essentially a repetitive cycle where the AI tries, fails, and learns.

## 1. Terminology: Epochs and Batches
- **Epoch**: One complete pass through all 10,000 records. (If we train for 10 Epochs, the AI "reads" every resume 10 times).
- **Batch**: Since 10,000 records is a lot, we feed the AI a small "snack" (e.g., 32 resumes) at a time. It updates its knowledge after every snack.

## 2. The 4 Steps of a Training Loop
Every time the AI sees a batch, it goes through these steps:

1.  **The Forward Pass**: The AI makes a guess. "I think this candidate is 'Selected' (80% probability)."
2.  **Calculate the Loss**: We compare the guess to the actual human decision. If the person was actually 'Rejected', the **Loss** (error) is high.
3.  **The Backward Pass (Backprop)**: The AI works backward to see which neurons were responsible for the wrong guess.
4.  **The Optimizer (The Mechanic)**: A tool called **Adam** (think of it as a smart mechanic) tweaks the weights of those neurons to make the error smaller next time.

## 3. Why repeat it 10 or 20 times?
The AI starts with random weights. It knows nothing! It's only by failing thousands of times and getting "corrected" by the loss function that it starts to see patterns (e.g., "Oh, the word 'Leadership' in the Transcript is usually linked to a 'Select' decision").

---

# 🎓 Training Master Quiz

**Q1: If the "Loss" number is going DOWN after every Epoch, is our AI learning or getting more confused?**

**Q2: We use an Optimizer called "Adam". What is its primary job during training?**
- A) To delete the dataset.
- B) To adjust the Weights so the Loss gets smaller.
- C) To print the final results.

**Q3: Explain the difference between an "Epoch" and a "Batch" using a real-world analogy (like reading a textbook).**

---
**Next Step**: Answer these, and then we will run the **Training Pipeline**! 🚀
