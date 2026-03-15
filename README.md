# 🧠 AI Recruitment Intelligence System

This project is a high-performance HR screening tool that uses **Sentence Transformers (SBERT)** and a **Neural Network (MLP)** to match candidate resumes and interview transcripts against job descriptions with human-like reasoning.

## 🚀 Quick Start

1. **Install Dependencies**:
   ```bash
   pip install flask flask-cors torch sentence-transformers PyPDF2 pandas
   ```

2. **Run the AI Server**:
   ```bash
   python app.py
   ```

3. **Launch the Interface**:
   Open `index.html` in your browser (via a local server like Live Server or by serving it through Flask).

---

## 📚 Educational Journey (Lessons & Docs)

This repository includes a full curriculum on how this AI was built, from data cleaning to neural architecture:

### 🛠️ Foundations
- [**Theory & Concepts**](docs/theory_and_concepts.md) — The "Why" behind the AI.
- [**EDA & Data Cleaning**](docs/eda_and_cleaning_guide.md) — Preparing the dataset for training.
- [**Kaggle Analysis Report**](docs/kaggle_analysis_report.md) — Insights from the source data.

### 🧠 Core Lessons
1. [**Embeddings & NLP**](docs/lesson_1_embeddings_quiz.md) — How AI "reads" text.
2. [**Preprocessing Logic**](docs/lesson_2_preprocessing.md) — Turning raw text into math.
3. [**Neural Architecture**](docs/lesson_3_architecture.md) — Building the "Brain" (MLP).
4. [**The Training Loop**](docs/lesson_4_training_loop.md) — How the model learns from mistakes.
5. [**Hyperparameter Tuning**](docs/lesson_5_tuning.md) — Optimizing for performance.
6. [**Metrics & Evaluation**](docs/lesson_6_metrics.md) — Measuring success (Precision/Recall).

### 🎨 Implementation & UI
- [**Web Interface (Flask & HTML)**](docs/lesson_7_ui.md) — Connecting the model to a user interface.
- [**PDF Parsing Support**](docs/lesson_8_pdf_parsing.md) — Handling real-world document formats.
- [**Hard Negatives & Retraining**](docs/lesson_9_distribution_gap.md) — Solving the "Chef Paradox" and role mismatches.
- [**Logic Failure Diagnosis**](docs/lesson_10_logic_failure.md) — Debugging common AI pitfalls.

### 🏁 Final Presentation
- [**Walkthrough**](docs/walkthrough.md) — A step-by-step guide to the final system.
- [**Cheat Sheet for Demo**](docs/presentation_cheat_sheet.md) — Key talking points for your presentation.

---

## 🔬 Technical Highlights

- **Architecture**: Dual-Embedding Input (Candidate Embedding + Job Embedding) -> 4-layer MLP with Dropout.
- **Model weights**: Saved in `recruitment_model.pth`.
- **Confidence Threshold**: Calibrated to **0.20** for optimal F1-score balance.
- **Dataset**: Real-world job/candidate pairings from Kaggle, enriched with role-specific hard negatives.

---
Produced as part of an Advanced AI Coding Collaboration.
