# SciSolve — Scientific Computing Assistant

SciSolve is a Python-based web application that provides an interactive interface for solving mathematical and scientific computing problems.

It combines a responsive web interface with Python scientific-computing libraries to provide calculations, visualizations, and step-by-step solutions.

---

## Features

### 🧮 Algebra
Solve and analyze algebraic expressions and equations.

Supported operations include:
- Linear equations
- Quadratic equations
- Polynomial equations
- Factorization
- Simplification
- Expansion
- Natural mathematical input

Example:

    Solve x^2 - 5x + 6 = 0

---

### 📊 Statistics
Perform common statistical calculations on numerical datasets.

Supported operations:
- Mean
- Median
- Mode
- Variance
- Standard deviation
- Range

Example:

    Calculate the mean of 10, 20, 30, 40, 50

---

### 🔢 Matrices
Perform common matrix operations using NumPy.

Supported operations:
- Matrix addition
- Matrix subtraction
- Matrix multiplication
- Transpose
- Determinant
- Inverse

Example:

    Multiply [[1,2],[3,4]] and [[5,6],[7,8]]

---

### 📐 Numerical Methods
Solve numerical problems using iterative numerical techniques.

Supported methods:
- Bisection method
- Newton-Raphson method
- Secant method

The application displays the iterations used to approximate the solution.

Example:

    Find root of x^2 - 4 using bisection from 0 to 3

---

### ⚛️ Scientific Formulas
Calculate values using commonly used scientific and physics formulas.

Supported formulas:
- Kinetic Energy
- Potential Energy
- Force
- Ohm's Law
- Ideal Gas Law
- Simple Pendulum

Example:

    Kinetic energy of a 2 kg object moving at 3 m/s

---

### 📈 Graphing
Plot mathematical functions using Matplotlib.

Supported examples include:
- Polynomial functions
- Trigonometric functions
- Rational functions
- Multiple functions on the same graph
- Custom x-axis ranges

Examples:

    Plot y = x^2 from -5 to 5

    Plot sin(x) and cos(x) from 0 to 6.28

---

## Step-by-Step Solutions

SciSolve is designed to show the working process instead of returning only the final answer.

For example, a scientific formula calculation displays:
1. Given values
2. Formula
3. Substitution
4. Calculation
5. Final answer

Numerical methods also display the iterations used to reach an approximate solution.

---

## Technology Stack

### Frontend
- HTML5
- CSS3
- JavaScript

### Backend
- Python
- Flask

### Scientific Computing
- SymPy
- NumPy
- Matplotlib

---

## Project Architecture

```text
User
  ↓
Web Interface
  ↓
Flask Backend
  ↓
Input Normalization
  ↓
Problem / Intent Detection
  ↓
Scientific Module
  ↓
SymPy / NumPy / Matplotlib
  ↓
Step-by-Step Result
  ↓
Web Interface