import re

from playwright.sync_api import Page, Locator, expect
from .exceptions import ShoppingCartError

DOLLAR_AMOUNT_PATTERN = re.compile(r"\$\s*([0-9]+\.?[0-9]*)")


class ShoppingCartPage:
    """Page Object Model for the shopping cart application.

    Provides methods for product browsing, cart functionality, size filtering, and checkout.

    Args:
        page: Playwright page instance
    """

    BASE_URL: str = "https://automated-test-evaluation.web.app/"

    PRODUCT_TITLE_SELECTOR = ".sc-124al1g-4"
    PRODUCT_PRICE_SELECTOR = ".sc-124al1g-5 .sc-124al1g-6"

    def __init__(self, page: Page) -> None:
        self.page = page

        # Shopping cart locators
        self.cart_count = self.page.locator(".sc-1h98xa9-3")
        self.cart_icon = self.page.locator(".sc-1h98xa9-2")
        self.cart_container = self.page.locator(".sc-1h98xa9-1")
        self.cart_button = self.page.locator(".sc-1h98xa9-2")
        self.cart_close_button = self.page.locator(".sc-1h98xa9-0")
        self.remove_button = self.page.locator(".sc-11uohgb-5")
        self.cart_product_desc = self.page.locator(".sc-11uohgb-3")
        self.cart_product_prices = self.page.locator(".sc-11uohgb-4")

        # Product locators
        self.products_container = self.page.locator(".sc-uhudcz-0")
        self.product_cards = self.page.locator(".sc-124al1g-2")
        self.product_prices = self.page.locator(".sc-124al1g-5")

        # Filter locators
        self.size_filters = self.page.locator(".checkmark")
        self.size_checkboxes = self.page.locator('.filters-available-size input[type="checkbox"]')
        self.filter_labels = self.page.locator("label.filters-available-size")

        # Checkout locators
        self.checkout_button = self.page.locator(".sc-1h98xa9-11")
        self.subtotal_section = self.page.locator(".sc-1h98xa9-7")
        self.subtotal_value = self.page.locator(".sc-1h98xa9-9")

    def get_product_title_locator(self, product_name: str) -> Locator:
        """Get locator for a specific product title."""
        return self.page.locator(f'{self.PRODUCT_TITLE_SELECTOR}:text-is("{product_name}")')

    def get_size_filter_locator(self, size: str) -> Locator:
        """Get locator for a specific size filter."""
        return self.page.get_by_text(size, exact=True)

    def goto(self) -> None:
        """Navigate to the shopping cart page."""
        self.page.goto(self.BASE_URL)

    def get_cart_count(self) -> int:
        """Get the current count of items in the shopping cart.

        Returns:
            The number of items in the shopping cart.
        """
        try:
            self.cart_count.wait_for(state="visible")
            text = self.cart_count.inner_text().strip()
            return int(text) if text and text.isdigit() else 0
        except (TimeoutError, ValueError):
            return 0

    def wait_for_cart_count(self, expected_count: int) -> None:
        """Wait for the cart count to reach the expected value.

        Args:
            expected_count: The expected number of items in cart

        Raises:
            TimeoutError: If the cart count doesn't reach the expected value within timeout
        """
        self.cart_count.wait_for(state="visible")
        expect(self.cart_count).to_have_text(str(expected_count))

    def add_products_to_cart(self, products: list[dict], expected_size: str = None) -> None:
        """Add multiple products to the cart.

        Args:
            products: A list of products
            expected_size: If provided, verifies products have this size before adding
        """
        initial_count = self.get_cart_count()

        for product in products:
            product_name = product["title"]
            title_locator = self.get_product_title_locator(product_name)
            product_container = self.product_cards.filter(has=title_locator)

            try:
                product_container.wait_for(state="visible")
            except TimeoutError:
                raise ShoppingCartError(f"Product '{product_name}' not found or not visible")

            add_button = product_container.locator("button")
            if not add_button.is_visible():
                raise ShoppingCartError(
                    f"Add to cart button not visible for product '{product_name}'"
                )

            if expected_size:
                active_filters = self.get_product_sizes()
                if expected_size not in active_filters:
                    raise ShoppingCartError(
                        f"Size filter {expected_size} is not active. "
                        f"Current filters: {active_filters}"
                    )

            add_button.scroll_into_view_if_needed()
            add_button.click()
            self.close_cart()

        expected_final_count = initial_count + len(products)
        self.wait_for_cart_count(expected_final_count)

    def add_product_to_cart(self, product: dict, expected_size: str = None) -> None:
        """Add a single product to the cart.

        Args:
            product: A product dictionary
            expected_size: If provided, verifies the product has this size before adding
        """
        self.add_products_to_cart([product], expected_size)

    def close_cart(self):
        """Close the shopping cart using the close button"""
        if not self.cart_container.is_visible():
            return

        if self.cart_close_button.is_visible():
            self.cart_close_button.click()
            self.page.wait_for_timeout(500)

    def open_cart(self):
        """Open the shopping cart if it's not already visible"""
        if self.subtotal_section.is_visible():
            return

        self.cart_icon.click()
        self.cart_container.wait_for(state="visible")
        expect(self.subtotal_section).to_be_visible()
        expect(self.subtotal_value).to_be_visible()

    def click_checkout(self) -> None:
        """Open cart and click the checkout button.

        This method handles the checkout button click and the alert that appears.
        """
        self.open_cart()

        alert_text = None

        def handle_alert(dialog):
            nonlocal alert_text
            alert_text = dialog.message
            dialog.accept()

        self.page.on("dialog", handle_alert)

        self.checkout_button.click()
        self.page.wait_for_timeout(1000)
        self.page.remove_listener("dialog", handle_alert)

        return alert_text

    def get_product_price(self, product: dict) -> float:
        """Get the price of a specific product.

        Args:
            product: A product dictionary

        Returns:
            The product price as a float

        Raises:
            ShoppingCartError: If the product price cannot be found or parsed
        """
        product_name = product["title"]
        title_locator = self.get_product_title_locator(product_name)
        product_container = self.product_cards.filter(has=title_locator)

        try:
            product_container.wait_for(state="visible")
            price_element = product_container.locator(self.PRODUCT_PRICE_SELECTOR)
            price_text = price_element.inner_text()
            price = price_text.replace("$", "").replace(" ", "").strip()
            return float(price)
        except (TimeoutError, ValueError) as e:
            raise ShoppingCartError(f"Could not get price for product '{product_name}': {str(e)}")

    def get_cart_total(self) -> float:
        """Get the total from the cart view (before checkout).

        Returns:
            The cart total

        Raises:
            ShoppingCartError: If the cart total cannot be found or parsed
        """
        try:
            self.open_cart()

            total_text = self.subtotal_value.inner_text()

            if "$" not in total_text:
                raise ShoppingCartError(f"Cart total '{total_text}' does not contain '$' symbol")

            total = total_text.replace("$", "").replace(" ", "").strip()
            return float(total)
        except (TimeoutError, ValueError) as e:
            raise ShoppingCartError(f"Could not get cart total: {str(e)}")

    def get_checkout_total(self) -> float:
        """Get the checkout total from either alert message or cart view after clicking checkout.

        Returns:
            The checkout total as a float

        Raises:
            ShoppingCartError: If the checkout total cannot be found or parsed
        """
        try:
            expect(self.subtotal_section).to_be_visible()
            expect(self.subtotal_value).to_be_visible()
            self.subtotal_value.wait_for(state="visible")
            total_text = self.subtotal_value.inner_text()

            if "$" not in total_text:
                raise ShoppingCartError(
                    f"Checkout total '{total_text}' does not contain '$' symbol"
                )

            total = total_text.replace("$", "").replace(" ", "").strip()
            return float(total)
        except (TimeoutError, ValueError) as e:
            raise ShoppingCartError(f"Could not get checkout total: {str(e)}")

    def get_alert_checkout_total(self, alert_message: str) -> float:
        """Extract checkout total from alert message.

        Args:
            alert_message: The alert message text

        Returns:
            The total amount as a float

        Raises:
            ShoppingCartError: If total cannot be extracted from alert message
        """
        try:
            amount_matches = DOLLAR_AMOUNT_PATTERN.findall(alert_message)
            if amount_matches:
                return float(amount_matches[0])
            else:
                raise ShoppingCartError(f"No dollar amount found in alert: '{alert_message}'")
        except (ValueError, IndexError) as e:
            raise ShoppingCartError(f"Could not parse total from alert '{alert_message}': {str(e)}")

    def reload_page(self) -> None:
        """Reload the page and wait for it to load."""
        self.page.reload()
        self.products_container.wait_for(state="visible")

    def get_available_sizes(self) -> list[str]:
        """Get a list of all available size filters."""
        self.size_filters.first.wait_for(state="visible")
        return [size.inner_text() for size in self.size_filters.all()]

    def apply_size_filter(self, size: str) -> None:
        """Apply a size filter.

        Args:
            size: The size to filter by (XS, S, M, L, XL, XXL)
        """
        size = size.upper()
        size_filter = self.get_size_filter_locator(size)
        size_filter.click()
        self.products_container.wait_for(state="visible")
        self.page.wait_for_timeout(500)

    def get_product_sizes(self) -> list[str]:
        """Get a list of all available size filters that are currently checked."""
        return self.page.evaluate("""() => {
            const checkedSizes = [];
            document.querySelectorAll('label').forEach(label => {
                if (label.querySelector('input[type="checkbox"]:checked')) {
                    const size = label.textContent.trim();
                    if (size) checkedSizes.push(size);
                }
            });
            return checkedSizes;
        }""")

    def clear_size_filters(self) -> None:
        """Clear all applied size filters."""
        self.reload_page()
        self.products_container.wait_for(state="visible")

    def get_visible_products(self) -> list[dict]:
        """Get a list of visible products with title and visibility status."""
        self.product_cards.first.wait_for(state="visible")
        products = []
        for card in self.product_cards.all():
            title = card.locator(self.PRODUCT_TITLE_SELECTOR).inner_text()
            if title:
                products.append({"title": title, "visible": card.is_visible()})
        return products

    def count_visible_products(self) -> int:
        """Get the number of currently visible products."""
        return len(self.product_cards.all())

    def remove_first_product_from_cart(self) -> None:
        """Remove the first product from the cart."""
        self.open_cart()

        initial_count = self.get_cart_count()
        if initial_count == 0:
            return

        delete_button = self.remove_button.first
        try:
            delete_button.wait_for(state="visible")
            delete_button.click()
            self.wait_for_cart_count(initial_count - 1)
        except (TimeoutError, AssertionError) as e:
            raise ShoppingCartError(f"Failed to remove product from cart: {str(e)}")

    def get_cart_product_sizes(self) -> list[str]:
        """Get the sizes of products currently in the cart.

        Returns:
            A list of size strings (e.g., ['M', 'L'])
        """
        self.open_cart()

        size_elements = self.cart_product_desc
        sizes = []

        for i in range(size_elements.count()):
            desc_text = size_elements.nth(i).inner_text()
            # Extract size from text like "M | Tule Quantity: 1"
            if "|" in desc_text:
                size = desc_text.split("|")[0].strip()
                if size:
                    sizes.append(size)

        return sizes
