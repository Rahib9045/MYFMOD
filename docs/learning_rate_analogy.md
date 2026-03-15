# Lesson 5.5: What is "Learning Rate" ($lr$)?

Since you were a bit confused about this, let's use a simple analogy. It's one of the most important concepts in AI!

## The Mountain Analogy 🏔️
Imagine you are at the top of a foggy mountain (High Loss/Errors) and you want to reach the beautiful valley at the bottom (Low Loss/Success). You can't see the bottom, so you have to feel the slope with your feet.

### 1. High Learning Rate (e.g., $lr=1.0$)
- **The Action**: You take giant, 10-meter leaps.
- **The Result**: You are moving fast, but you are so clumsy that you jump *over* the valley and land on the next mountain peak. You keep jumping back and forth and never reach the bottom.
- **In AI**: The model's accuracy will "bounce" around and never settle.

### 2. Low Learning Rate (e.g., $lr=0.000001$)
- **The Action**: You take tiny, 1-millimeter baby steps.
- **The Result**: You are moving in the right direction, but it will take you 100 years to reach the bottom. 
- **In AI**: Training becomes extremely slow, and you might get stuck in a small "ditch" (Local Minimum) thinking it's the bottom.

### 3. Just Right (e.g., $lr=0.001$)
- **The Action**: You take steady, 1-meter steps.
- **The Result**: You move efficiently and stop exactly where the valley is deepest.

## Why it matters for your script
In `train_model.py`, we set `lr=0.001`. If our accuracy is stuck at 58%, we might try making it **smaller** (like $0.0005$) to be more precise, or **increasing epochs** to give those steps more time to reach the bottom.

---
**Does the mountain analogy help you visualize what the $lr$ is doing?**
