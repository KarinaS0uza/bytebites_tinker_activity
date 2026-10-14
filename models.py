"""Backend models for the ByteBites campus food ordering app.

The module exposes four classes:
    Customer: Validated customer names and purchase history.
    MenuItem: Validated product details with Decimal prices.
    Menu: Bounded item collections with filtering and sorting.
    Order: Bounded item selections with Decimal totals.

Author: Karina Souza.
"""

from __future__ import annotations

from decimal import Decimal


class Customer:
    """A ByteBites customer with a validated name and purchase history.

    Purchase history accepts up to MAX_ORDERS nonempty orders. Recording
    the same Order instance twice is rejected for this customer.
    Verification checks for a nonempty history rather than
    authenticating
    identity.

    Attributes:
        MIN_NAME_LENGTH (int): Minimum accepted name length (1).
        MAX_NAME_LENGTH (int): Maximum accepted name length (40).
        DEFAULT_NAME (str): Fallback name for invalid initial input.
        MAX_ORDERS (int): Maximum number of recorded orders (100).
    """

    MIN_NAME_LENGTH = 1
    MAX_NAME_LENGTH = 40
    DEFAULT_NAME = "Unnamed Customer"
    MAX_ORDERS = 100

    def __init__(self, name: str | None) -> None:
        """Initialize a customer with an empty purchase history.

        Args:
            name: The customer's name. An invalid name uses
                DEFAULT_NAME.
        """
        self._name: str = self.DEFAULT_NAME
        self._purchase_history: list[Order] = []
        self.set_name(name)

    @property
    def name(self) -> str:
        """The customer's validated name.

        This property is read-only. Use set_name() to update it.
        """
        return self._name

    @property
    def purchase_history(self) -> list[Order]:
        """A shallow copy of the customer's purchase history.

        Adding or removing entries in this list does not affect stored
        history. The Order instances remain shared. Use
        record_purchase()
        to add an order to stored history.
        """
        return self.get_purchase_history()

    def set_name(self, name: str | None) -> bool:
        """Set the customer's name if it meets the name rules.

        Args:
            name: New name, with 1 to 40 characters and no leading
                space.

        Returns:
            True if the name was set, otherwise False. A rejected name
            leaves
            the previous value unchanged.
        """
        if (
            not isinstance(name, str)
            or not self.MIN_NAME_LENGTH <= len(name) <= self.MAX_NAME_LENGTH
            or name.startswith(" ")
        ):
            return False
        self._name = name
        return True

    def get_order_count(self) -> int:
        """Return the number of orders in the purchase history."""
        return len(self._purchase_history)

    def get_order(self, index: int) -> Order | None:
        """Return the recorded order at a position starting at zero.

        Args:
            index: The position of the order in the purchase history.

        Returns:
            The original order object, or None if the index is not an
            integer
            position in the purchase history. Boolean indices are
            rejected.
        """
        if (
            not isinstance(index, int)
            or isinstance(index, bool)
            or not 0 <= index < len(self._purchase_history)
        ):
            return None
        return self._purchase_history[index]

    def record_purchase(self, order: Order | None) -> bool:
        """Record an order in the customer's purchase history.

        The supplied Order instance is stored without copying it. Empty
        orders, invalid inputs, and orders already in this customer's
        history are rejected. Call this after a purchase has been made;
        it does not confirm payment or enforce exclusive order
        ownership.

        Args:
            order: The order to record in the purchase history.

        Returns:
            True if the order was recorded, otherwise False if it was
            rejected
            or the history is full. A rejected order leaves history
            unchanged.
        """
        if (
            not isinstance(order, Order)
            or order.get_item_count() == 0
            or len(self._purchase_history) >= self.MAX_ORDERS
        ):
            return False
        for recorded_order in self._purchase_history:
            if recorded_order is order:
                return False
        self._purchase_history.append(order)
        return True

    def get_purchase_history(self) -> list[Order]:
        """Return a shallow copy of the customer's purchase history.

        The list contains the original Order instances. Adding or
        removing
        entries does not change stored history; the instances remain
        shared.

        Returns:
            Recorded orders in insertion order, or an empty list if none
            have been recorded.
        """
        return list(self._purchase_history)

    def browse_menu(
        self, menu: Menu | None, category: str | None
    ) -> list[MenuItem]:
        """Find the items in one category of a supplied menu.

        Args:
            menu: The menu to browse. The customer does not keep the
                menu.
            category: The category to look for, such as "Drinks".

        Returns:
            A new list of matching items, or an empty list if nothing
            matches,
            the menu is invalid, or the category is not a string.
        """
        if not isinstance(menu, Menu):
            return []
        return menu.filter_by_category(category)

    def is_verified_user(self) -> bool:
        """Check whether the customer has a recorded purchase history.

        Returns:
            True if at least one order has been recorded, otherwise
            False.
        """
        return len(self._purchase_history) > 0


class MenuItem:
    """A food or drink item with validated product details.

    Setters validate updates and report success or failure. Invalid
    initial
    values use defaults. Prices are Decimal values, and menus and orders
    can share the same MenuItem instance.

    Attributes:
        MIN_NAME_LENGTH (int): Minimum accepted name length (1).
        MAX_NAME_LENGTH (int): Maximum accepted name length (40).
        MIN_CATEGORY_LENGTH (int): Minimum accepted category length (1).
        MAX_CATEGORY_LENGTH (int): Maximum accepted category length
            (20).
        MIN_PRICE (Decimal): Minimum accepted price (0.00).
        MAX_PRICE (Decimal): Maximum accepted price (100.00).
        MIN_POPULARITY_RATING (float): Minimum accepted rating (0.0).
        MAX_POPULARITY_RATING (float): Maximum accepted rating (5.0).
        DEFAULT_NAME (str): Fallback name for invalid initial input.
        DEFAULT_PRICE (Decimal): Fallback price (0.00).
        DEFAULT_CATEGORY (str): Fallback category for invalid initial
            input.
        DEFAULT_POPULARITY_RATING (float): Fallback rating (0.0).
    """

    MIN_NAME_LENGTH = 1
    MAX_NAME_LENGTH = 40
    MIN_CATEGORY_LENGTH = 1
    MAX_CATEGORY_LENGTH = 20
    MIN_PRICE = Decimal("0.00")
    MAX_PRICE = Decimal("100.00")
    MIN_POPULARITY_RATING = 0.0
    MAX_POPULARITY_RATING = 5.0
    DEFAULT_NAME = "Unnamed Item"
    DEFAULT_PRICE = Decimal("0.00")
    DEFAULT_CATEGORY = "Uncategorized"
    DEFAULT_POPULARITY_RATING = 0.0

    def __init__(
        self,
        name: str | None,
        price: Decimal,
        category: str | None,
        popularity_rating: float,
    ) -> None:
        """Initialize a menu item with validated product details.

        Each value is validated separately. A rejected value is replaced
        with
        its corresponding default, while other valid values are
        retained.

        Args:
            name: The item's name, such as "Spicy Burger" or "Large
                Soda".
            price: The item's price in dollars, supplied as a Decimal
                value.
            category: The item's category, such as "Drinks" or
                "Desserts".
            popularity_rating: The item's popularity rating.
        """
        self._name: str = self.DEFAULT_NAME
        self._price: Decimal = self.DEFAULT_PRICE
        self._category: str = self.DEFAULT_CATEGORY
        self._popularity_rating: float = self.DEFAULT_POPULARITY_RATING
        self.set_name(name)
        self.set_price(price)
        self.set_category(category)
        self.set_popularity_rating(popularity_rating)

    @property
    def name(self) -> str:
        """The item's validated name.

        This property is read-only. Use set_name() to update it.
        """
        return self._name

    @property
    def price(self) -> Decimal:
        """The item's price in dollars.

        This property is read-only. Use set_price() to update it.
        """
        return self._price

    @property
    def category(self) -> str:
        """The item's validated category.

        This property is read-only. Use set_category() to update it.
        """
        return self._category

    @property
    def popularity_rating(self) -> float:
        """The item's popularity rating.

        This property is read-only. Use set_popularity_rating() to
        update it.
        """
        return self._popularity_rating

    def set_name(self, name: str | None) -> bool:
        """Set the item's name if it meets the name rules.

        Args:
            name: New name, with 1 to 40 characters and no leading
                space.

        Returns:
            True if the name was set, otherwise False. A rejected name
            leaves
            the previous value unchanged.
        """
        if (
            not isinstance(name, str)
            or not self.MIN_NAME_LENGTH <= len(name) <= self.MAX_NAME_LENGTH
            or name.startswith(" ")
        ):
            return False
        self._name = name
        return True

    def set_price(self, price: Decimal) -> bool:
        """Set a finite Decimal price within the allowed range.

        Args:
            price: A Decimal price from 0.00 to 100.00 dollars,
                inclusive.

        Returns:
            True if the price was set, otherwise False. A rejected value
            leaves
            the previous price unchanged. Other types, NaN, and infinity
            are
            rejected.
        """
        if (
            not isinstance(price, Decimal)
            or not price.is_finite()
            or not self.MIN_PRICE <= price <= self.MAX_PRICE
        ):
            return False
        self._price = price
        return True

    def set_category(self, category: str | None) -> bool:
        """Set the item's category if it meets the category rules.

        Args:
            category: A string of 1 to 20 characters that does not start
                with
                a space. Trailing spaces are preserved.

        Returns:
            True if the category was set, otherwise False. A rejected
            category
            leaves the previous value unchanged.
        """
        if (
            not isinstance(category, str)
            or not (
                self.MIN_CATEGORY_LENGTH <= len(category) <= self.MAX_CATEGORY_LENGTH
            )
            or category.startswith(" ")
        ):
            return False
        self._category = category
        return True

    def set_popularity_rating(self, popularity_rating: float) -> bool:
        """Set a numeric popularity rating within the allowed range.

        Args:
            popularity_rating: An integer or float from 0.0 to 5.0,
                inclusive.

        Returns:
            True if the rating was set, otherwise False. A rejected
            value leaves
            the previous rating unchanged. Booleans, NaN, and infinity
            are
            rejected.
        """
        if (
            not isinstance(popularity_rating, (int, float))
            or isinstance(popularity_rating, bool)
            or not (
                self.MIN_POPULARITY_RATING
                <= popularity_rating
                <= self.MAX_POPULARITY_RATING
            )
        ):
            return False
        self._popularity_rating = float(popularity_rating)
        return True


class Menu:
    """A collection of menu items with filtering and sorting operations.

    The menu accepts up to MAX_ITEMS entries and rejects duplicate names
    on insertion, ignoring capitalization. Filtering and sorting return
    new lists containing references to the original MenuItem instances.

    Attributes:
        MAX_ITEMS (int): Maximum number of items on the menu (50).
    """

    MAX_ITEMS = 50

    def __init__(self) -> None:
        """Initialize an empty menu."""
        self._items: list[MenuItem] = []

    @property
    def items(self) -> list[MenuItem]:
        """A shallow copy of the menu's items in insertion order.

        Adding or removing entries in this list does not affect the
        menu.
        The MenuItem instances remain shared. Use add_item() and
        remove_item() to change the menu's stored entries.
        """
        return self.get_all_items()

    def get_item_count(self) -> int:
        """Return the number of items on the menu."""
        return len(self._items)

    def get_item(self, index: int) -> MenuItem | None:
        """Return the menu item at a position starting at zero.

        Args:
            index: The position of the item on the menu.

        Returns:
            The original item object, or None if the index is not an
            integer
            position on the menu. Boolean indices are rejected.
        """
        if (
            not isinstance(index, int)
            or isinstance(index, bool)
            or not 0 <= index < len(self._items)
        ):
            return None
        return self._items[index]

    def add_item(self, item: MenuItem | None) -> bool:
        """Add an item to the end of the menu.

        The supplied MenuItem instance is stored without copying it.
        Invalid inputs and names matching an existing item, ignoring
        capitalization, are rejected.

        Args:
            item: The menu item to add.

        Returns:
            True if the item was added, otherwise False if it was
            rejected or
            the menu is full. A rejected item leaves the menu unchanged.
        """
        if not isinstance(item, MenuItem) or len(self._items) >= self.MAX_ITEMS:
            return False
        for listed_item in self._items:
            if listed_item.name.lower() == item.name.lower():
                return False
        self._items.append(item)
        return True

    def remove_item(self, item: MenuItem) -> None:
        """Remove the first matching item from the menu.

        The remaining items keep their existing order.

        Args:
            item: The menu item to remove.

        Raises:
            ValueError: If the item is not in the menu.
        """
        self._items.remove(item)

    def get_all_items(self) -> list[MenuItem]:
        """Return a shallow copy of the menu's items.

        The list contains the original MenuItem instances. Adding or
        removing entries does not affect the menu; the instances remain
        shared.

        Returns:
            Menu items in insertion order, or an empty list if the menu
            is empty.
        """
        return list(self._items)

    def filter_by_category(self, category: str | None) -> list[MenuItem]:
        """Find the menu items that belong to one category.

        Matching ignores capitalization but preserves spaces.
        For example, "Drinks " does not match "Drinks". Matching items
        appear in the menu's original order. The returned list contains
        the original MenuItem instances.
        The menu's stored entries are unchanged.

        Args:
            category: The category to look for, such as "Drinks".

        Returns:
            A new list of matching items, or an empty list if nothing
            matches,
            the menu is empty, or the category is not a string.
        """
        matches: list[MenuItem] = []
        if not isinstance(category, str):
            return matches
        category_lower = category.lower()

        for item in self._items:
            if item.category.lower() == category_lower:
                matches.append(item)

        return matches

    def sort_by_price(
        self, items: list[MenuItem], descending: bool = False
    ) -> list[MenuItem]:
        """Return a new list of items sorted by price.

        Items with equal prices retain their input order. The input list
        is unchanged, and the returned list contains references to the
        original MenuItem instances.

        Args:
            items: The items to sort, such as all menu items or a
                filtered list.
            descending: True for highest price first, False for lowest
                price
                first. Defaults to False.

        Returns:
            A new list of items in price order, or an empty list if the
            supplied
            list is empty.
        """
        return sorted(items, key=lambda item: item.price, reverse=descending)

    def sort_by_popularity(
        self, items: list[MenuItem], descending: bool = True
    ) -> list[MenuItem]:
        """Return a new list of items sorted by popularity rating.

        Items with equal ratings retain their input order. The input
        list
        is unchanged, and the returned list contains references to the
        original MenuItem instances.

        Args:
            items: The items to sort, such as all menu items or a
                filtered list.
            descending: True for highest rating first, False for lowest
                rating
                first. Defaults to True.

        Returns:
            A new list of items in popularity order, or an empty list if
            the
            supplied list is empty.
        """
        return sorted(
            items, key=lambda item: item.popularity_rating, reverse=descending
        )


class Order:
    """An order containing selected menu items and their total cost.

    Orders start empty and accept up to MAX_ITEMS selections. Repeated
    selections count separately. The total uses each MenuItem instance's
    current price and includes only item prices.

    Attributes:
        MAX_ITEMS (int): Maximum number of selected items (50).
    """

    MAX_ITEMS = 50

    def __init__(self) -> None:
        """Initialize an empty order."""
        self._selected_items: list[MenuItem] = []

    @property
    def selected_items(self) -> list[MenuItem]:
        """A shallow copy of the order's selected items.

        Adding or removing entries in this list does not affect the
        order.
        The MenuItem instances remain shared. Use add_item() and
        remove_item() to change the stored selections.
        """
        return list(self._selected_items)

    def get_item_count(self) -> int:
        """Return the selection count, including repeated items."""
        return len(self._selected_items)

    def get_item(self, index: int) -> MenuItem | None:
        """Return the selected item at a position starting at zero.

        Args:
            index: The position of the selected item in the order.

        Returns:
            The original item object, or None if the index is not an
            integer
            position in the order. Boolean indices are rejected.
        """
        if (
            not isinstance(index, int)
            or isinstance(index, bool)
            or not 0 <= index < len(self._selected_items)
        ):
            return None
        return self._selected_items[index]

    def add_item(self, item: MenuItem | None) -> bool:
        """Add an item to the end of the order's selected items.

        The supplied MenuItem instance is stored without copying it.
        Repeated selections are accepted and counted separately in the
        total.

        Args:
            item: The menu item to add to the order.

        Returns:
            True if the item was added, otherwise False if the item is
            invalid
            or the order is full. A rejected item leaves the order
            unchanged.
        """
        if (
            not isinstance(item, MenuItem)
            or len(self._selected_items) >= self.MAX_ITEMS
        ):
            return False
        self._selected_items.append(item)
        return True

    def remove_item(self, item: MenuItem) -> None:
        """Remove the first matching item from the order.

        If the item was selected more than once, the other selections
        remain.

        Args:
            item: The selected menu item to remove.

        Raises:
            ValueError: If the item is not selected in the order.
        """
        self._selected_items.remove(item)

    def compute_total(self) -> Decimal:
        """Return the Decimal total of the selected items.

        Each item's current price is used, and an item selected more
        than once
        is counted each time. The total includes only item prices,
        without
        taxes, discounts, or fees.

        Returns:
            The total cost as a Decimal value, or Decimal("0") for an
            empty
            order.
        """
        return sum((item.price for item in self._selected_items), Decimal("0"))
