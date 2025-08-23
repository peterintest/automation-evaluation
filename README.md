# Automated Testing Evaluation

## Overview
This project uses Playwright and pytest with the Page Object Model (POM) design pattern to test a shopping cart web application. It includes end-to-end tests for product filtering, cart management, checkout functionality, and GitHub repository access verification.

---

## Setup Instructions

### 1. Clone this repository
```bash
git clone https://github.com/peterintest/automation-evaluation.git
cd automation-evaluation
```

### 2. Create and activate a virtual environment
```bash
python -m venv venv
source venv/bin/activate   # macOS/Linux
venv\Scripts\activate      # Windows
```

### 3. Install dependencies
```bash
pip install .
playwright install
```

---

## Running Tests

Run all tests:
```bash
pytest
```

Run only app tests:
```bash
pytest tests/test_cart_functionality.py
```

Run only repo accessibility tests:
```bash
pytest tests/test_repo_accessibility.py
```

---

## Test Coverage

### Cart Functionality Tests

| Test Scenario | Description | Status |
|---------------|-------------|--------|
| `test_cart_starts_empty` | Verify cart is empty on page load | ✅ Pass |
| `test_add_multiple_products_to_cart` | Add multiple products using list method | ✅ Pass |
| `test_remove_product_from_cart` | Remove product from cart | ✅ Pass |
| `test_cart_resets_on_reload` | Cart empties after page reload | ✅ Pass |
| `test_checkout_total_calculation_multiple_products` | Checkout total calculation accuracy | ✅ Pass |
| `test_add_same_product_multiple_times` | Add same product twice | ✅ Pass |

### Size Filter Tests

| Test Scenario | Description | Status |
|---------------|-------------|--------|
| `test_available_size_filters` | All expected size filters present | ✅ Pass |
| `test_size_filter_reduces_products` | Size filter reduces product count | ✅ Pass |
| `test_clear_size_filters` | Clearing filters restores all products | ✅ Pass |
| `test_individual_size_filter` | Each size filter works correctly (7 tests) | ✅ Pass |
| `test_multiple_size_filter_combinations` | Multiple filters applied together (5 tests) | ✅ Pass |
| `test_cart_product_size_matches_filter` | Cart products match applied filter (7 tests) | ⚠️ 5 Fail, 2 Pass |

### Repository Accessibility Tests

| Test Scenario | Description | Status |
|---------------|-------------|--------|
| `test_github_repo_accessible` | GitHub repository URL accessible | ✅ Pass |
| `test_can_download_zip` | Repository downloadable as ZIP | ✅ Pass |
| `test_contains_readme` | Repository contains README.md | ✅ Pass |

### Test Results

**Current Test Results:** 26 passing, 5 failing (83.9% pass rate)
**Total Test Count:** 31 tests
- Cart functionality: 6 tests (all passing)
- Size filtering: 19 tests (14 passing, 5 failing due to size display truncation)
- Repository access: 3 tests (all passing)

### Known Test Failures

5 tests fail due to a size display truncation issue in the application:
- `XS` displays as `S` in cart
- `ML`, `L`, `XL`, `XXL` all display as `X` in cart

These failures indicate a potential UX issue where customers cannot distinguish between different sizes in their cart.

---

## Test Assumptions and Limitations

### Lack of Test-Specific Attributes
The application uses dynamic class names like `.sc-1h98xa9-3`. Without test-specific attributes, the test suite relies on these dynamic CSS selectors, creating maintainability concerns.

Current selectors in use:
```python
# Dynamic CSS classes that may change with application updates
self.cart_count = self.page.locator(".sc-1h98xa9-3")
self.product_cards = self.page.locator(".sc-124al1g-2")
self.checkout_button = self.page.locator(".sc-1h98xa9-11")
```

A more sustainable approach would involve adding dedicated test attributes:
```html
<!-- Recommended approach for test stability -->
<div data-testid="cart-quantity">5</div>
<div data-testid="product-card">...</div>
<button data-testid="checkout-button">Checkout</button>
```

This would enable more robust selectors like `self.page.locator('[data-testid="cart-quantity"]')` that remain stable across styling changes.

### Product Size Display In Cart
The test suite assumes that product sizes should be fully displayed in the cart. However, 5 tests fail because the application truncates size labels:

- `XS` and `S` both display as `S` in cart
- `ML`, `L`, `XL`, `XXL` all display as `X` in cart

This behavior prevents customers from distinguishing between different sizes (e.g., both `XL` and `XXL` appear as `X`). The tests assume this is a bug, but it could be an intentional design decision. Tests may need adjustment based on the application's intended behavior.

### Size Filter Detection Challenges
There were difficulties with reliably detecting selected size filters in the shopping cart application. The initial approach using standard Playwright locators such as `self.size_checkboxes.filter(state="checked")` proved inconsistent due to the application's specific DOM structure.

The current implementation in the `get_product_sizes()` method uses JavaScript evaluation as a workaround. While not ideal, this approach provides reliable results.

### Application Scope
The application under test is a React prototype that implements core shopping cart functionality. Some standard e-commerce features are not included:

- Shipping calculations
- Payment processing beyond subtotal
- User registration/login
- Order persistence 
- Additional product attributes e.g. colour
- Checking stock

The test suite is designed around the current features and would need expanding for a production e-commerce application.

### Future Enhancements
The following enhancements would further improve test coverage and robustness:

**Extended Test Scenarios**

Additional test scenarios could include verification of free shipping badges and payment installments within the cart; these were deprioritised given the checkout functionality was not fully implemented.

**Accessibility Testing**

Integration of axe-core for automated WCAG 2.2 Level AA compliance scanning would enhance accessibility coverage. This should include keyboard navigation validation, color contrast verification, and ARIA label testing for screen reader compatibility.

**Cross-Browser and Responsive Testing**

Testing currently runs only on Chromium, missing potential browser compatibility issues. Adding other browsers and such as Firefox, Safari, and Edge and different viewports would ensure consistent functionality across different browsers and device sizes.

**Containerization**

Dockerization would provide a consistent test execution environment. A Docker image would bundle all dependencies (Python, Playwright, browsers) into a portable container, eliminating environment specific issues and simplifying CI/CD integration with GitLab or Jenkins.
