# 🧠 Machine Learning Basics – Housing Price Prediction

## 📌 Overview
This project demonstrates a complete machine learning pipeline using a housing dataset.  
It includes data preprocessing, exploratory data analysis (EDA), model training, and evaluation using Linear Regression.

The main objective is to predict housing prices based on features like area, number of bedrooms, bathrooms, and other attributes.

---

## 📂 Dataset
The dataset contains the following features:

- `price` → Target variable (house price)
- `area` → Size of the house
- `bedrooms` → Number of bedrooms
- `bathrooms` → Number of bathrooms
- `stories` → Number of floors
- `mainroad`, `guestroom`, `basement` → Categorical features

---

## ⚙️ Workflow

### 1. Data Preprocessing
- Encoding categorical variables
- Feature scaling using StandardScaler

### 2. Exploratory Data Analysis (EDA)
- Correlation analysis

### 3. Model Building
- Linear Regression model
- Train-test split (typically 80-20)

### 4. Model Evaluation
- R² Score (approximately 0.65)
- Comparing actual vs predicted values

---

## 📊 Results
- Achieved an R² score of ~0.65, indicating moderate predictive performance.
- Feature scaling improved model performance and stability.

---
