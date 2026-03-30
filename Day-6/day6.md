# Python Regex Practice: Data Extraction & Cleaning

This repository contains a Jupyter Notebook (`regex-practice.ipynb`) demonstrating practical applications of **Regular Expressions** in Python. It covers essential patterns for data validation, web scraping, and text preprocessing.

---

## 🚀 Overview

The notebook uses Python's built-in `re` module to solve common string manipulation challenges. Each cell targets a specific real-world use case, ranging from extracting contact details to "scrubbing" messy text for Natural Language Processing (NLP).

## 🛠 Features & Scripts

### 1. Identity & Contact Extraction
* **Email Finder**: Matches standard email formats using word boundaries (`\b`).
* **Indian Phone Numbers**: Handles 10-digit numbers with optional `+91` country codes and separators.
* **URL Extractor**: Captures `http` and `https` links from raw text.

### 2. Text Cleaning (Pre-processing)
* **Special Character Removal**: Strips symbols (like `!`, `?`, `#`) while preserving alphanumeric characters and spaces.
* **Whitespace Normalization**: Collapses multiple spaces or tabs into a single space and trims edges.
* **Case-Sensitive Extraction**: Identifies capitalized words, useful for finding Proper Nouns.

### 3. Data & Metadata Extraction
* **Date Formats**: Supports dual formats: `DD-MM-YYYY` and `YYYY/MM/DD`.
* **Time (24hr)**: Extracts timestamps in `HH:MM` format.
* **Hashtags**: Pulls `#tags` from social media strings.
* **Numeric Extraction**: Isolates all standalone digits/numbers from a sentence.

---

## 📖 Pattern Reference Table

| Feature | Regex Pattern | Purpose |
| :--- | :--- | :--- |
| **Emails** | `\b[A-Za-z0-9._%+-]+@[A-Za-z]+\.[A-Za-z]{2,}\b` | Extract valid email addresses |
| **Phone (IN)** | `(?:\+91[\-\s]?)?[6-9]\d{9}` | Match 10-digit Indian mobile numbers |
| **Cleaning** | `[^A-Za-z0-9\s]` | Target symbols for removal |
| **Dates** | `\b\d{2}[-/]\d{2}[-/]\d{4} \| \d{4}[-/]\d{2}[-/]\d{2}\b` | Capture multiple date styles |
| **URLs** | `https?://\S+` | Identify web links |

---

