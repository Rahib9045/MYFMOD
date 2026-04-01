# Lesson 3: Building the Brain (Hybrid Architecture)

Now that we have clean data, we need to design the "Brain". In modern AI, we often combine two types of Neural Networks to get the best result. This is called a **Hybrid Model**.

## 1. Feature Extractor: SBERT
We already learned about this. SBERT takes our text and turns it into a list of 384 numbers (a vector). 
- *Analogy*: SBERT is like the "Eyes". It sees the data and understands the meaning.

## 2. Decision Maker: MLP (Multi-Layer Perceptron)
An MLP is a simple, classical Neural Network that takes the numbers from SBERT and learns how to make a final decision (Select or Reject).
- *Analogy*: The MLP is the "Brain". It weighs the information and makes the judgment call.

## 3. The "Hidden Layers"
Inside the MLP, there are layers of "Neurons". 
- **Input Layer**: Receives the SBERT numbers.
- **Hidden Layers**: This is where the magic happens. These layers find complex patterns (e.g., if "Python" is present AND "5 years experience" is mentioned, then probability of Selection goes up).
- **Output Layer**: A single number between 0 and 1. (0.9 = 90% chance of Selection).

---

# 🎓 Lesson 3 Challenge: The Architect

Look at the diagram logic below:

`[Resume Text]` -> **[SBERT]** -> `[384 Numbers]` -> **[Hidden Layer 1]** -> **[Hidden Layer 2]** -> `[Select/Reject]`

**Q1: Why do we need the "Hidden Layers"? Why not just go straight from the 384 numbers to the final decision?**

**Q2: We use an "Activation Function" called 'ReLU'. It's like a gatekeeper. If a neuron's value is negative, ReLU turns it into zero. Why would we want to "silence" neurons that aren't firing?**

**Q3: Based on our balanced dataset (50% Select, 50% Reject), what do you think would be a "good" accuracy score for our model?**
- A) 100%
- B) Higher than 50% (Anything is better than a coin flip!)
- C) Exactly 50%

---
**Next Step**: Once you answer these, we will actually **train** the model on your 10,000 records!
