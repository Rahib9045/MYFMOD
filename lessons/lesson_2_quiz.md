# 🎓 Lesson 2 Review: The Cleaning Quiz

Great job identifying the noise! Now let's see if you understand the *logic* behind the code I just wrote.

**Q1: In my code, I used something called `re.sub(r'[^a-zA-Z0-9\s]', '', text)`. In simple terms, what is this "Regex" doing?**
- A) Deleting only the vowels.
- B) Keeping only letters, numbers, and spaces (and deleting everything else like `!`, `@`, `#`).
- C) Scanning for viruses.

**Q2: Why do we use `.apply(clean_text)` in Pandas instead of a `for` loop?**
- *Hint*: Think about speed and the 10,000 rows.

**Q3: If we DON'T remove the `!!!` or `...`, how might that affect the SBERT embeddings?**

---
**Next Step**: Answer these, and then you can run `python preprocess_data.py` to actually clean your data for the first time!
