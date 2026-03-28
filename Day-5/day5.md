# 🚢 Titanic Dataset Analysis (EDA Project)

## 📌 Overview

This project performs **Exploratory Data Analysis (EDA)** on the Titanic dataset to uncover patterns and factors affecting passenger survival.

The dataset includes information such as passenger class, gender, age, fare, and embarkation port.

---

## 🎯 Objectives

* Understand survival patterns
* Analyze impact of gender, class, and age
* Handle missing data
* Perform grouping, aggregation, and visualization

---

## 🛠️ Tools & Libraries

* Python
* Pandas
* Matplotlib
* Seaborn

---

## 📂 Dataset

* Source: Kaggle Titanic Dataset
* Rows: ~891 passengers
* Features include:

  * Survived (0 = No, 1 = Yes)
  * Pclass (Passenger Class)
  * Sex
  * Age
  * Fare
  * Embarked

---

## 🔍 Data Cleaning

* Filled missing **Age** values with mean
* Filled missing **Embarked** values with mode
* Dropped irrelevant or highly missing columns where necessary

---

## 📊 Key Insights

### 🧑‍🤝‍🧑 Gender vs Survival

* Females had a **significantly higher survival rate** than males
* Indicates priority given to women during evacuation

---

### 🏷️ Passenger Class vs Survival

* **1st Class** passengers had the highest survival rate
* **3rd Class** passengers had the lowest survival rate
* Suggests socio-economic status influenced survival chances

---

### 🎂 Age Distribution

* Younger passengers had slightly better survival chances
* However, age was **less influential** compared to gender and class

---

### 🌍 Embarkation Port Analysis

* Passengers from **Cherbourg (C)** had the highest survival rate
* Southampton (S) had the lowest
* Could be linked to class distribution across ports

---

## 📈 Techniques Used

* Data exploration (`head`, `info`, `describe`)
* Filtering and selection
* Handling missing values (`fillna`, `dropna`)
* GroupBy operations
* Pivot tables
* Data visualization (bar plots, pie charts)

---

## 🧠 Conclusion

* Survival was strongly influenced by:

  * Gender (female > male)
  * Passenger class (1st > 2nd > 3rd)
* Socio-economic factors played a major role in survival outcomes
