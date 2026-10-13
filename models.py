from __future__ import annotations

from decimal import Decimal


class Customer:
    """Stores a customer's name and purchase history."""

    def __init__(self, name: str) -> None:
        self.name: str = name
        self.purchase_history: list[Order] = []

    def record_purchase(self, order: Order) -> None:
        """Add an order to the purchase history.

        Callers should call this after a purchase is made. This method does
        not confirm that a purchase actually occurred.
        """
        self.purchase_history.append(order)

    def get_purchase_history(self) -> list[Order]:
        """Return a copy of the purchase history list.

        The list is a new list, but it contains the same Order objects as the
        original.
        """
        return list(self.purchase_history)

    def is_verified_user(self) -> bool:
        """Return True if the customer has at least one past purchase.

        This is a simple purchase-history check, not identity authentication.
        """
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
    """Manages the collection of menu items and filters by category."""

    def __init__(self) -> None:
        self.items: list[MenuItem] = []

    def add_item(self, item: MenuItem) -> None:
        self.items.append(item)

    def remove_item(self, item: MenuItem) -> None:
        if item in self.items:
            self.items.remove(item)

    def get_all_items(self) -> list[MenuItem]:
        return list(self.items)

    def filter_by_category(self, category: str) -> list[MenuItem]:
        """Return items in the category, ignoring upper/lower case."""
        matches: list[MenuItem] = []
        for item in self.items:
            if item.category.lower() == category.lower():
                matches.append(item)
        return matches


class Order:
    """Stores selected items and calculates the total cost."""

    def __init__(self) -> None:
        self.selected_items: list[MenuItem] = []

    def add_item(self, item: MenuItem) -> None:
        self.selected_items.append(item)

    def remove_item(self, item: MenuItem) -> None:
        if item in self.selected_items:
            self.selected_items.remove(item)

    def compute_total(self) -> Decimal:
        total = Decimal("0")
        for item in self.selected_items:
            total += item.price
        return total
