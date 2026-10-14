from __future__ import annotations

from decimal import Decimal


class Customer:
    """Stores a customer's name and purchase history."""

    def __init__(self, name: str) -> None:
        self.name: str = name
        self.purchase_history: list[Order] = []

    def record_purchase(self, order: Order) -> None:
        """Add an order to the purchase history."""
        self.purchase_history.append(order)

    def get_purchase_history(self) -> list[Order]:
        """Return a copy of the purchase history list."""
        return list(self.purchase_history)

    def is_verified_user(self) -> bool:
        """Return True if the customer has at least one past purchase."""
        return len(self.purchase_history) > 0


class MenuItem:
    """Stores an item's name, price, category, and popularity rating."""

    def __init__(
        self, name: str, price: Decimal, category: str, popularity_rating: float
    ) -> None:
        self.name: str = name
        self.price: Decimal = price
        self.category: str = category
        self.popularity_rating: float = popularity_rating


class Menu:
    """Manages menu items, filters by category, and sorts item lists."""

    def __init__(self) -> None:
        self.items: list[MenuItem] = []

    def add_item(self, item: MenuItem) -> None:
        self.items.append(item)

    def remove_item(self, item: MenuItem) -> None:
        self.items.remove(item)

    def get_all_items(self) -> list[MenuItem]:
        return list(self.items)

    def filter_by_category(self, category: str) -> list[MenuItem]:
        """Return matching items in a new list, ignoring capitalization.

        Keep the menu's original order. Return an empty list if nothing matches.
        """
        matches: list[MenuItem] = []
        category_lower = category.lower()

        for item in self.items:
            if item.category.lower() == category_lower:
                matches.append(item)

        return matches

    def sort_by_price(
        self, items: list[MenuItem], descending: bool = False
    ) -> list[MenuItem]:
        """Return a new list sorted cheapest first, or highest first if descending.

        Keep equal-price items in their original order and leave items unchanged.
        """
        return sorted(items, key=lambda item: item.price, reverse=descending)

    def sort_by_popularity(
        self, items: list[MenuItem], descending: bool = True
    ) -> list[MenuItem]:
        """Return a new list sorted highest rating first, or lowest if not descending.

        Keep equal-rating items in their original order and leave items unchanged.
        """
        return sorted(
            items, key=lambda item: item.popularity_rating, reverse=descending
        )


class Order:
    """Stores selected items and calculates the total cost."""

    def __init__(self) -> None:
        self.selected_items: list[MenuItem] = []

    def add_item(self, item: MenuItem) -> None:
        self.selected_items.append(item)

    def remove_item(self, item: MenuItem) -> None:
        self.selected_items.remove(item)

    def compute_total(self) -> Decimal:
        """Add selected prices using Decimal, counting each repeated selection.

        Return Decimal("0") for an empty order. Include only item prices.
        """
        return sum((item.price for item in self.selected_items), Decimal("0"))
