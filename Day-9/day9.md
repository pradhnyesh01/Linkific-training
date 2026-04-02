# IMDB Movie Review Sentiment Analysis

This project implements a complete Natural Language Processing (NLP) pipeline to classify movie reviews as either **Positive** or **Negative** using the IMDB dataset.

## 📊 Model Performance

The following metrics were achieved using a Logistic Regression model on a 20% test split (10,000 reviews).

| Metric | Value |
| :--- | :--- |
| **Accuracy Score** | **~89%** |
| **Test Size** | 10,000 samples |
| **Model Type** | Logistic Regression (`max_iter=200`) |
| **Vectorization** | TF-IDF (5,000 features) |

### Classification Report
* **Precision:** High accuracy in identifying both positive and negative sentiments.
* **Recall:** Effectively captures the majority of relevant reviews in each category.

---

## 🛠️ Pipeline Details

### 1. Preprocessing
To clean the raw text, the following steps are applied:
* **HTML Removal:** Strips tags like `<br />` using regex.
* **Text Normalization:** Converts all text to lowercase.
* **Special Character Removal:** Uses `re.sub(r'[^a-zA-Z]', ' ', text)` to remove numbers and symbols, leaving only English letters.
* **Stopword Removal:** Filters out common English words (e.g., "the", "and") using NLTK.
* **Lemmatization:** Uses `WordNetLemmatizer` to reduce words to their base dictionary form.

### 2. Feature Extraction
* **Method:** `TfidfVectorizer`.
* **Vocabulary Limit:** `max_features=5000`. This selects the top 5,000 most important words to keep the model efficient and prevent overfitting.

### 3. Classification
* **Algorithm:** Logistic Regression.
* **Configuration:** `max_iter=200`. This allows the solver extra iterations to find the optimal weights for the dataset.

---

## 🚀 Usage

To use the model for predicting the sentiment of new reviews:

```python
def predict_sentiment(text):
    # Preprocess the input text
    clean_text = preprocess(text)
    # Transform text to TF-IDF vector
    vector = vectorizer.transform([clean_text])
    # Predict
    prediction = model.predict(vector)[0]
    
    return "Positive" if prediction == 1 else "Negative"

# Example
print(predict_sentiment("I enjoyed the thrill and action of the movie!")) # Output: Positive
print(predict_sentiment("It was very boring")) # Output: Negative