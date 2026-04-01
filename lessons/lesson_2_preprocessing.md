# Lesson 2: The Art of Text Cleaning (Preprocessing)

Now that you know how the "Brain" (Neural Network) works, we need to make sure the "Food" (Data) we give it is clean. Neural Networks are powerful, but they are also sensitive to noise.

## 1. Why Preprocess?
Imagine a computer trying to understand these two sentences:
1. "I am an expert in Python."
2. "i am an expert in python!!!"

To us, they are identical. To a computer, "Python." and "python!!!" look like completely different tokens because of the capital letters and punctuation.

## 2. Common Cleaning Steps
In our script, we will perform:
- **Lowercasing**: Converting everything to lowercase.
- **Punctuation Removal**: Getting rid of `!!!`, `???`, and `...` which don't help with ranking.
- **Whitespace Stripping**: Removing extra spaces or hidden "newline" characters (`\n`).

## 3. Handling Large Files (10,000+ rows)
Since our Kaggle dataset has 10k rows, we can't clean it manualy. We will use **Pandas** to apply these cleaning functions to the entire column at once.

---

# 🛠️ Practice: Find the Noise!

Before I write the script, look at this sample "Raw Resume Text" below. **Can you list 3 things in this text that should be "cleaned" before we send it to an AI?**

> **"Contact: Bob@email.com ... \n I have 5+ years of experience in JAVASCRIPT & React.!!!! Visit my site: http://bobcodes.com"**

---
**Next Step**: Once you identify the "noise," I'll show you the Python code that handles it, and we'll run it on your 10,000 Kaggle records!
