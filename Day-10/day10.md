# NLP Practice Repository

This repository contains a collection of Jupyter notebooks exploring various Natural Language Processing (NLP) techniques, ranging from foundational machine learning to modern transformer-based models.

## Notebooks Overview

### 1. [huggingface-practice.ipynb](cite: 1)
An introductory guide to utilizing the **Hugging Face Transformers** library.
* **Key Features**:
    * **Sentiment Analysis**: Uses the default `pipeline` for text classification.
    * **Summarization**: Implements the `sshleifer/distilbart-cnn-12-6` model to condense text.
    * **Zero-Shot Classification**: Categorizes text into arbitrary labels without specific training.

### 2. [model-practice.ipynb](cite: 2)
Focuses on evaluating the performance of a pre-trained transformer model on a standardized dataset.
* **Model**: `distilbert-base-uncased-finetuned-sst-2-english`.
* **Dataset**: IMDB Movie Reviews (subset of 10,000 reviews for testing).
* **Process**: Loads the dataset, applies the Hugging Face pipeline with truncation enabled, and calculates comprehensive classification metrics.

### 3. [nlp-basics.ipynb](cite: 3)
Demonstrates the traditional "Bag-of-Words" approach to NLP.
* **Preprocessing**: Includes HTML tag removal, special character filtering, tokenization, stopword removal, and lemmatization.
* **Vectorization**: Uses `TfidfVectorizer` with a maximum of 5,000 features.
* **Model**: A `LogisticRegression` classifier trained on the processed text.

---

## Evaluation Comparison: Modern vs. Traditional

The following table compares the performance of the **Transformer-based pipeline** (`model-practice.ipynb`) against the **Traditional Machine Learning** approach (`nlp-basics.ipynb`) on the IMDB sentiment analysis task.

| Metric | `model-practice.ipynb` (DistilBERT) | `nlp-basics.ipynb` (Logistic Regression) |
| :--- | :--- | :--- |
| **Approach** | Pre-trained Transformer | TF-IDF + Logistic Regression |
| **Accuracy** | **0.90** | **0.89** |
| **Precision** | **0.895** | 0.89 (weighted avg) |
| **Recall** | **0.89** | 0.885 (weighted avg) |
| **F1-Score** | **0.895** | 0.89 (weighted avg) |

### Comparison Summary
* **Accuracy**: Both approaches achieved nearly identical accuracy (approximately **89% - 90%**).
* **Precision vs. Recall**: The DistilBERT model showed higher **Precision** (**0.895** vs **0.89**), indicating fewer false positive predictions. However, the Logistic Regression model had higher **Recall** (**0.89** vs **0.885**), meaning it was better at identifying the total number of positive instances in the test set.
* **Ease of Use**: The Transformer approach (`model-practice.ipynb`) required significantly less manual preprocessing compared to the extensive cleaning pipeline required for the traditional approach in `nlp-basics.ipynb`.