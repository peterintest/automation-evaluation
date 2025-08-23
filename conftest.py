"""
Fixtures for Playwright browser and page setup.

This module provides pytest fixtures for launching a Chromium browser
and creating a new page context for automated tests.
"""

import pytest
from playwright.sync_api import Browser, Page, sync_playwright
from tests.pages.shopping_cart_page import ShoppingCartPage

DEFAULT_TIMEOUT_MS = 20000


@pytest.fixture
def shopping_cart(page: Page) -> ShoppingCartPage:
    """
    Create a new ShoppingCartPage instance.

    Args:
        page (Page): A Playwright page instance.

    Returns:
        ShoppingCartPage: A page object for interacting with the shopping cart.
    """
    cart = ShoppingCartPage(page)
    cart.goto()
    yield cart


@pytest.fixture(scope="session")
def browser() -> Browser:
    """
    Launch a Chromium browser session.

    Returns:
        Browser: A Playwright Chromium browser instance.
    """
    with sync_playwright() as p:
        browser: Browser = p.chromium.launch(headless=False)
        yield browser
        browser.close()


@pytest.fixture
def page(browser: Browser) -> Page:
    """
    Create a new browser page context.

    Args:
        browser (Browser): A Playwright browser instance.

    Returns:
        Page: A new browser page object.
    """
    context = browser.new_context()
    page: Page = context.new_page()
    page.set_default_timeout(DEFAULT_TIMEOUT_MS)
    yield page
    context.close()
