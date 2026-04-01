# Lesson 6: Metrics that Matter (Precision vs. Recall)

Congratulations! Your model reached **74.2% accuracy**. This is a huge jump from 58% and shows that your tuning worked.

However, in a school project, "Accuracy" isn't the whole story. We need to know **how** it is failing.

## 1. The Confusion Matrix
Imagine our model makes 100 predictions.
- **True Positives (TP)**: We predicted "Select", and they were actually "Selected". (Good!)
- **True Negatives (TN)**: We predicted "Reject", and they were actually "Rejected". (Good!)
- **False Positives (FP)**: We predicted "Select", but they were actually "Rejected". (False Alarm)
- **False Negatives (FN)**: We predicted "Reject", but they were actually "Selected". (Missed Opportunity)

## 2. Precision vs. Recall
### Precision: "Quality"
- *Question*: Of all the people we called "Selected", how many were actually good?
- *Example*: High Precision means we don't accidentally hire bad candidates.

### Recall: "Quantity"
- *Question*: Of all the good candidates in the 10,000, how many did we actually find?
- *Example*: High Recall means we don't accidentally miss any geniuses.

## 3. Why it matters for Recruitment
In HR, **False Negatives** (missing a great worker) are often worse than **False Positives** (interviewing someone who isn't a fit). We might prefer a model with high **Recall** even if the accuracy is a bit lower.

---

# 🎓 The Final Quiz

**Q1: If our model is "conservative" and only selects people it is 100% sure about, will it have High Precision or High Recall?**

**Q2: We are going to generate a "Confusion Matrix". If that matrix shows a high number of "False Negatives," what is happening in our recruitment process?**

**Q3: Which metric would a recruiter care about more: Accuracy or the F1-Score (which balances Precision and Recall)?**

---
**Next Step**: Answer these, and I will give you the **Evaluation Script** to generate these numbers for your report!
