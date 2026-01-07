# Comprehensive Pytest Testing Guide

# GitHub Repository Tracker Application

## Table of Contents

1. [Getting Started](#getting-started)
2. [Basic Pytest Commands](#basic-pytest-commands)
3. [Understanding Test Structure](#understanding-test-structure)
4. [Running Tests - Step by Step](#running-tests-step-by-step)
5. [Advanced Testing Techniques](#advanced-testing-techniques)
6. [Debugging Failed Tests](#debugging-failed-tests)
7. [Writing Your Own Tests](#writing-your-own-tests)
8. [Best Practices](#best-practices)

---

## Getting Started

### Prerequisites Check

Before running tests, ensure:

- ✅ PostgreSQL is running on localhost:5432
- ✅ Test database exists: `github_tracker_test`
- ✅ Virtual environment is activated
- ✅ Dependencies are installed

### Quick Setup

````bash

cd C:\Users\ADMIN\github_repo_tracker

.\venv\Scripts\activate

pytest --version


---

```bash
pytest tests/
````

**What it does:** Runs all test files in the tests/ directory

### 2. Run Tests with Verbose Output

```bash
pytest tests/ -v
```

**What it does:** Shows each test name and result (PASSED/FAILED)

### 3. Run Specific Test File

```bash
pytest tests/test_repos.py
```
