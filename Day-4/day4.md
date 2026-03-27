# 📘 NumPy Practice Notebook

## 📌 Overview
This notebook demonstrates the **basics of NumPy**, a powerful Python library for numerical computing. It covers array creation, indexing, operations, reshaping, and random number generation.

---

## 🧰 Topics Covered

### 1. Creating Arrays
- Using `np.arange()` to generate sequences
- Creating 1D, 2D, and 3D arrays
- Understanding array shapes

---

### 2. Array Indexing & Slicing
- Accessing elements using indices
- Slicing arrays (`a[2:5]`, `a[::-1]`)
- Multi-dimensional indexing

---

### 3. Array Operations
- Element-wise operations:
  - Addition
  - Subtraction
  - Multiplication
  - Division

---

### 4. Aggregation Functions
- `np.sum()` for totals
- Axis-based summation
- Mean and standard deviation:
  - `mean()`
  - `std()`

---

### 5. Broadcasting
- Performing operations on arrays of different shapes
- Example: adding a column vector to a row vector

---

### 6. Reshaping & Flattening
- Reshaping arrays using `.reshape()`
- Flattening arrays using `.ravel()`

---

### 7. Adding Dimensions
- Using `np.newaxis` to convert:
  - 1D → row vector
  - 1D → column vector

---

### 8. Random Number Generation
- Using `np.random.default_rng()`
- Generating:
  - Random floats (`rng.random`)
  - Random integers (`rng.integers`)
- Using seeds (e.g., `42`, `2026`) for reproducibility

---

### 9. Boolean Masking
- Creating conditions (`a > 4`)
- Filtering arrays using masks

---

### 10. Fancy Indexing
- Accessing elements using index arrays

---

### 11. Concatenation
- Combining arrays using `np.concatenate()`
- Concatenating along rows and columns

---

### 12. Sorting
- Sorting arrays using `np.sort()`

---

### 13. Array Properties
- `ndim` → number of dimensions
- `size` → total elements
- `shape` → structure of the array

---