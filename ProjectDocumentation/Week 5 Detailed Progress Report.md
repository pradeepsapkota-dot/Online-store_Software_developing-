# Software Development – Week 5 Progress Report

**Group Members:**
1. Haroon Afridi
2. Pradeep Sapkota
3. Poshan Oli
4. Lamyae Echaoui

**Week:** Week 5  
**Topic:** Software Quality Improvement, Validation Testing and Code Refactoring

---

### 1. Introduction

During Week 5, we continued developing and improving the Online Store Management System using Python, MySQL, Streamlit and pytest. The main focus was on software testing, code quality, validation and improving the readability of existing code.

The work was divided into two sessions. Session 1 focused on adding validation tests, while Session 2 covered software quality, Ruff code checking and refactoring existing test code.

---

## 2. Week 5 – Session 1: Validation Testing

### 2.1 Objective

The objective of this session was to improve the testing of the application by adding test cases for the validation functions.

### 2.2 Work Completed

A new test file named `test_validation.py` was added to the existing `tests` folder.

The file contains test cases for the validation functions implemented in `validation.py`. These tests check whether the application correctly accepts valid input and rejects invalid input.

The validation areas include:

- Product information, including name, category, price and stock quantity.
- Product ID validation.
- Restocking quantity validation.
- Customer ID and order item validation.
- Order status validation.
- Payment information validation.
- Product search keyword validation.

The purpose of these tests is to identify invalid input before it causes problems in the application or database operations.

### 2.3 Testing

The project tests were executed using pytest. The validation tests were included alongside the existing product, order and stock operation tests.

The test suite completed successfully with 108 passing tests.

**Screenshot 1:** `tests/test_validation.py` showing the newly added validation test cases
![alt text](<../ApplicationScreenshots/Week 5 a.PNG>)

**Screenshot 2:** VS Code terminal showing the successful pytest results
![alt text](<../ApplicationScreenshots/Week 5 b.PNG>)

---

## 3. Week 5 – Session 2: Improving Software Quality

### 3.1 Objective

The objective of Session 2 was to understand and apply software quality practices to the existing project. The lecture covered code readability, PEP 8, avoiding duplicated code, refactoring, Ruff and software testing.

### 3.2 Ruff Code Quality Check

Ruff was used to check the Python project for code quality and style issues.

During the initial check, Ruff identified nine issues. These included import-order problems and nested `with` statements in the stock operation tests.

The automatic fix option was used to correct the import-order issues:

`ruff check . --fix`

The remaining nested context managers in `test_stock_operations.py` were then refactored manually.

After the corrections, Ruff was executed again:

`ruff check .`

The final result was:

`All checks passed!`

This confirmed that Ruff did not identify any remaining issues in the project.

**Screenshot 3:** Initial Ruff findings or Git diff showing the code changes
![alt text](<../ApplicationScreenshots/Week 5 c.PNG>)
**Screenshot 4:** Final Ruff check showing "All checks passed!"
![alt text](<../ApplicationScreenshots/Week 5 e.PNG>)
### 3.3 Refactoring Stock Operation Tests

One improvement was made in `tests/test_stock_operations.py`.

Previously, two nested `with` statements were used when testing invalid stock quantities and invalid product IDs. The context managers were combined into a single `with` block.

This made the test code shorter and easier to read without changing the test logic or expected results.

The same improvement was applied to both relevant test functions.

**Before:** The test functions used nested context managers.

**After:** The context managers were combined into one `with` block.

**Screenshot 5:** Git diff showing the before-and-after code changes.
![alt text](<../ApplicationScreenshots/Week 5 d.PNG>)


### 3.4 Running the Test Suite Again

After the code quality improvements, the pytest test suite was executed again to check that the changes had not affected the existing functionality.

The test suite completed successfully with 108 passing tests.

This helped verify that the refactoring and code cleanup did not introduce test failures.

**Screenshot 7:** Terminal output showing the successful pytest results.
![alt text](<../ApplicationScreenshots/Week 5 f.PNG>)

---
---

## 5. Challenges and Solutions

During this week's work, several code quality issues were identified.

**Import ordering:** Ruff identified import-order issues in multiple Python files. These were corrected using Ruff's automatic fix option.

**Nested context managers:** The stock operation tests contained nested `with` statements. These were combined into a single context manager to improve readability.

**Test coverage:** Additional validation tests were needed to check how the application handles invalid user input. This was addressed by creating `tests/test_validation.py`.

**Maintaining existing functionality:** After making the changes, the complete test suite was executed again to verify that the existing tests continued to pass.

---

## 6. Current Project Status

The following work was completed during Week 5:

- Added `tests/test_validation.py`.
- Added validation test coverage for different input types.
- Checked the project using Ruff.
- Corrected import-order issues.
- Refactored nested context managers in stock operation tests.
- Ran the pytest test suite successfully, with 108 passing tests.
- Committed the changes using Git.

The optional database integration test using a separate test database has not yet been completed.

---

## 7. Conclusion

Week 5 focused on improving the quality and reliability of the Online Store Management System. New validation tests were added, existing code was checked using Ruff, and the stock operation tests were refactored to improve readability.

The successful Ruff check and 108 passing pytest tests provided evidence that the code quality improvements did not introduce test failures.

These improvements make the project easier to maintain, test and develop further.
