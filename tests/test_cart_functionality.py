"""
Automated tests for the shopping cart functionality
"""

import pytest
from tests.pages.shopping_cart_page import ShoppingCartPage

ALL_SIZES = ["XS", "S", "M", "ML", "L", "XL", "XXL"]


def test_cart_starts_empty(shopping_cart: ShoppingCartPage) -> None:
    """
    Verify that the cart is empty when the homepage loads.
    """
    assert shopping_cart.get_cart_count() == 0


def test_add_multiple_products_to_cart(shopping_cart: ShoppingCartPage) -> None:
    """
    Verify that adding multiple products increases the cart count accordingly.
    """
    initial_count = shopping_cart.get_cart_count()
    products = shopping_cart.get_visible_products()
    assert len(products) >= 6, "Not enough products available for test"

    products_to_add = products[:6]
    shopping_cart.add_products_to_cart(products_to_add)

    assert shopping_cart.get_cart_count() == initial_count + len(products_to_add)


def test_remove_product_from_cart(shopping_cart: ShoppingCartPage) -> None:
    """
    Verify that removing a product decreases the cart count.
    """
    products = shopping_cart.get_visible_products()
    assert products, "No products available for test"

    shopping_cart.add_products_to_cart(products[:3])
    initial_count = shopping_cart.get_cart_count()
    shopping_cart.remove_first_product_from_cart()
    assert shopping_cart.get_cart_count() == initial_count - 1


def test_cart_resets_on_reload(shopping_cart: ShoppingCartPage) -> None:
    """
    Verify that cart is empty after page reload since this is a frontend prototype.
    """
    products = shopping_cart.get_visible_products()
    assert products, "No products available for test"
    shopping_cart.add_product_to_cart(products[0])
    assert shopping_cart.get_cart_count() > 0

    shopping_cart.reload_page()
    shopping_cart.wait_for_cart_count(0)
    assert shopping_cart.get_cart_count() == 0


def test_checkout_total_calculation_multiple_products(shopping_cart: ShoppingCartPage) -> None:
    """
    Verify that the checkout total correctly calculates the sum of multiple products.

    This test verifies:
    1. Cart total matches expected sum of product prices
    2. Checkout alert displays the correct total
    """
    products = shopping_cart.get_visible_products()
    assert len(products) >= 4, "Not enough products available for test"

    products_to_add = products[:4]
    expected_total = sum(shopping_cart.get_product_price(product) for product in products_to_add)

    shopping_cart.add_products_to_cart(products_to_add)

    cart_total = shopping_cart.get_cart_total()
    assert cart_total == expected_total, (
        f"Cart total ${cart_total} does not match expected total ${expected_total} "
        f"for {len(products_to_add)} products"
    )

    alert_message = shopping_cart.click_checkout()
    assert alert_message is not None, "No alert appeared after clicking checkout"

    alert_total = shopping_cart.get_alert_checkout_total(alert_message)
    assert alert_total == expected_total, (
        f"Alert total ${alert_total} does not match expected total "
        f"${expected_total} for {len(products_to_add)} products. Alert: '{alert_message}'"
    )


def test_add_same_product_multiple_times(shopping_cart: ShoppingCartPage) -> None:
    """
    Verify that the same product can be added multiple times.
    """
    initial_count = shopping_cart.get_cart_count()

    products = shopping_cart.get_visible_products()
    assert products, "No products available for test"

    shopping_cart.add_product_to_cart(products[0])
    shopping_cart.add_product_to_cart(products[0])

    assert shopping_cart.get_cart_count() == initial_count + 2


def test_available_size_filters(shopping_cart: ShoppingCartPage) -> None:
    """
    Verify that all expected size filters are available.
    """
    sizes = shopping_cart.get_available_sizes()
    assert set(sizes) == set(ALL_SIZES)


def test_size_filter_reduces_products(shopping_cart: ShoppingCartPage) -> None:
    """
    Verify that applying a size filter reduces the number of visible products.
    """
    initial_count = shopping_cart.count_visible_products()

    sizes = shopping_cart.get_available_sizes()
    shopping_cart.apply_size_filter(sizes[0])

    filtered_count = shopping_cart.count_visible_products()
    assert filtered_count < initial_count, "Size filter did not reduce product count"


def test_clear_size_filters(shopping_cart: ShoppingCartPage) -> None:
    """
    Verify that clearing size filters restores all products.
    """
    initial_count = shopping_cart.count_visible_products()

    shopping_cart.apply_size_filter("M")
    assert shopping_cart.count_visible_products() < initial_count

    shopping_cart.clear_size_filters()
    assert shopping_cart.count_visible_products() == initial_count


@pytest.mark.parametrize("size", ALL_SIZES)
def test_individual_size_filter(shopping_cart: ShoppingCartPage, size: str) -> None:
    """
    Test that each individual size filter works correctly.
    Verifies filter application and product filtering.
    """
    initial_count = shopping_cart.count_visible_products()
    assert initial_count > 0, "No products found on initial load"

    shopping_cart.apply_size_filter(size)

    active_sizes = shopping_cart.get_product_sizes()
    assert size in active_sizes, f"Size {size} not shown as selected"
    assert len(active_sizes) == 1, f"Only {size} should be selected, but found: {active_sizes}"

    filtered_count = shopping_cart.count_visible_products()
    assert filtered_count > 0, f"No products found for size {size}"
    assert filtered_count <= initial_count, (
        f"Size {size} filter did not reduce or maintain product count"
    )


@pytest.mark.parametrize(
    "size1,size2",
    [
        ("XS", "S"),
        ("S", "M"),
        ("M", "L"),
        ("L", "XL"),
        ("XL", "XXL"),
    ],
)
def test_multiple_size_filter_combinations(
    shopping_cart: ShoppingCartPage, size1: str, size2: str
) -> None:
    """
    Test that multiple size filters can be applied together correctly.
    Verifies that combining filters shows appropriate product counts.
    """
    initial_count = shopping_cart.count_visible_products()

    shopping_cart.apply_size_filter(size1)
    count_with_first = shopping_cart.count_visible_products()
    assert count_with_first > 0, f"No products found for size {size1}"

    shopping_cart.apply_size_filter(size2)
    count_with_both = shopping_cart.count_visible_products()

    # Combined filters should show more or equal products than individual
    assert count_with_both >= count_with_first, (
        f"Adding second filter {size2} reduced products from "
        f"{count_with_first} to {count_with_both}"
    )

    active_sizes = shopping_cart.get_product_sizes()
    assert size1 in active_sizes, f"Size {size1} was deselected"
    assert size2 in active_sizes, f"Size {size2} not shown as selected"

    assert count_with_both <= initial_count, "Combined filters should not exceed total products"


@pytest.mark.parametrize("test_size", ALL_SIZES)
def test_cart_product_size_matches_filter(shopping_cart: ShoppingCartPage, test_size: str) -> None:
    """
    Test that products added to cart have the correct size when size filters are applied.
    """
    shopping_cart.apply_size_filter(test_size)

    active_sizes = shopping_cart.get_product_sizes()
    assert test_size in active_sizes, f"Size filter {test_size} not applied correctly"

    filtered_products = shopping_cart.get_visible_products()
    assert filtered_products, f"No products found for size {test_size}"

    shopping_cart.add_product_to_cart(filtered_products[0], expected_size=test_size)

    assert shopping_cart.get_cart_count() == 1
    cart_product_sizes = shopping_cart.get_cart_product_sizes()
    assert test_size in cart_product_sizes, (
        f"Expected size {test_size} in cart, but got {cart_product_sizes}"
    )
