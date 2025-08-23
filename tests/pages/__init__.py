"""Pages package for test automation.

This package contains page objects and related exceptions for the shopping cart application.
"""

from .exceptions import ShoppingCartError
from .shopping_cart_page import ShoppingCartPage

__all__ = ["ShoppingCartError", "ShoppingCartPage"]
