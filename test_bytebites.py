import unittest
from decimal import Decimal

from models import Customer, Menu, MenuItem, Order


class MenuTests(unittest.TestCase):
    def setUp(self) -> None:
        self.burger = MenuItem("Spicy Burger", Decimal("9.50"), "Food", 4.8)
        self.soda = MenuItem("Large Soda", Decimal("2.50"), "Drinks", 4.5)
        self.tea = MenuItem("Iced Tea", Decimal("2.50"), "Drinks", 4.5)
        self.cake = MenuItem("Cake", Decimal("5.00"), "Desserts", 4.9)
        self.items = [self.burger, self.soda, self.tea, self.cake]
        self.menu = Menu()
        for item in self.items:
            self.menu.add_item(item)

    def test_filter_ignores_capitalization(self) -> None:
        for category in ["drinks", "Drinks", "DRINKS"]:
            with self.subTest(category=category):
                self.assertEqual(
                    self.menu.filter_by_category(category), [self.soda, self.tea]
                )
        self.assertEqual(self.menu.items, self.items)

    def test_filter_unknown_category_returns_empty_list(self) -> None:
        self.assertEqual(self.menu.filter_by_category("Breakfast"), [])

    def test_filter_empty_menu_returns_empty_list(self) -> None:
        self.assertEqual(Menu().filter_by_category("Drinks"), [])

    def test_filter_returns_a_new_list_without_changing_menu(self) -> None:
        drinks = self.menu.filter_by_category("Drinks")
        self.assertIsNot(drinks, self.menu.items)
        drinks.clear()
        self.assertEqual(self.menu.items, self.items)

    def test_sort_by_price_default_is_ascending_and_stable(self) -> None:
        self.assertEqual(
            self.menu.sort_by_price(self.menu.get_all_items()),
            [self.soda, self.tea, self.cake, self.burger],
        )

    def test_sort_by_price_descending_is_stable(self) -> None:
        self.assertEqual(
            self.menu.sort_by_price(self.menu.get_all_items(), descending=True),
            [self.burger, self.cake, self.soda, self.tea],
        )

    def test_sort_by_popularity_default_is_descending_and_stable(self) -> None:
        self.assertEqual(
            self.menu.sort_by_popularity(self.menu.get_all_items()),
            [self.cake, self.burger, self.soda, self.tea],
        )

    def test_sort_by_popularity_ascending_is_stable(self) -> None:
        self.assertEqual(
            self.menu.sort_by_popularity(self.menu.get_all_items(), descending=False),
            [self.soda, self.tea, self.burger, self.cake],
        )

    def test_sorting_empty_lists_returns_new_empty_lists(self) -> None:
        for sort in [self.menu.sort_by_price, self.menu.sort_by_popularity]:
            for descending in [False, True]:
                with self.subTest(method=sort.__name__, descending=descending):
                    items = []
                    result = sort(items, descending=descending)
                    self.assertEqual(result, [])
                    self.assertIsNot(result, items)

    def test_sorting_preserves_menu_and_input_lists(self) -> None:
        drinks = self.menu.filter_by_category("Drinks")
        for sort in [self.menu.sort_by_price, self.menu.sort_by_popularity]:
            for items in [self.menu.items, self.menu.get_all_items(), drinks]:
                for descending in [False, True]:
                    with self.subTest(
                        method=sort.__name__, count=len(items), descending=descending
                    ):
                        original_items = list(items)
                        result = sort(items, descending=descending)
                        self.assertIsNot(result, items)
                        result.clear()
                        self.assertEqual(items, original_items)
                        self.assertEqual(self.menu.items, self.items)

    def test_sorting_filtered_items_orders_only_matches(self) -> None:
        coffee = MenuItem("Coffee", Decimal("3.50"), "Drinks", 4.9)
        self.menu.add_item(coffee)
        drinks = self.menu.filter_by_category("drinks")
        self.assertEqual(
            self.menu.sort_by_price(drinks), [self.soda, self.tea, coffee]
        )
        self.assertEqual(
            self.menu.sort_by_price(drinks, descending=True),
            [coffee, self.soda, self.tea],
        )
        self.assertEqual(
            self.menu.sort_by_popularity(drinks), [coffee, self.soda, self.tea]
        )
        self.assertEqual(
            self.menu.sort_by_popularity(drinks, descending=False),
            [self.soda, self.tea, coffee],
        )
        self.assertEqual(drinks, [self.soda, self.tea, coffee])


class CustomerTests(unittest.TestCase):
    def test_purchase_history_records_orders_and_verifies_customer(self) -> None:
        customer = Customer("Alex")
        self.assertEqual(customer.get_purchase_history(), [])
        self.assertFalse(customer.is_verified_user())

        menu = Menu()
        soda = MenuItem("Large Soda", Decimal("2.50"), "Drinks", 4.5)
        menu.add_item(soda)
        order = Order()
        order.add_item(menu.get_all_items()[0])
        customer.record_purchase(order)

        history = customer.get_purchase_history()
        self.assertTrue(customer.is_verified_user())
        self.assertEqual(history, [order])
        self.assertIs(history[0], order)
        self.assertIs(order.selected_items[0], soda)
        self.assertEqual(order.compute_total(), Decimal("2.50"))

        history.clear()
        self.assertEqual(customer.get_purchase_history(), [order])


class OrderTests(unittest.TestCase):
    def setUp(self) -> None:
        self.burger = MenuItem("Spicy Burger", Decimal("9.50"), "Food", 4.8)
        self.soda = MenuItem("Large Soda", Decimal("2.50"), "Drinks", 4.5)
        self.order = Order()

    def test_empty_order_total_is_decimal_zero(self) -> None:
        total = self.order.compute_total()
        self.assertIsInstance(total, Decimal)
        self.assertEqual(total, Decimal("0"))

    def test_total_adds_prices_exactly(self) -> None:
        self.order.add_item(self.burger)
        self.order.add_item(self.soda)
        total = self.order.compute_total()
        self.assertIsInstance(total, Decimal)
        self.assertEqual(total, Decimal("12.00"))

    def test_total_counts_repeated_selections(self) -> None:
        self.order.add_item(self.soda)
        self.order.add_item(self.soda)
        self.assertEqual(self.order.compute_total(), Decimal("5.00"))

    def test_total_updates_after_adding_and_removing_items(self) -> None:
        self.order.add_item(self.burger)
        self.assertEqual(self.order.compute_total(), Decimal("9.50"))
        self.order.add_item(self.soda)
        self.assertEqual(self.order.compute_total(), Decimal("12.00"))
        self.order.remove_item(self.burger)
        self.assertEqual(self.order.compute_total(), Decimal("2.50"))
        self.order.remove_item(self.soda)
        self.assertEqual(self.order.compute_total(), Decimal("0"))


class CustomerValidationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.customer = Customer("Alex")
        self.item = MenuItem("Soda", Decimal("2.50"), "Drinks", 4.5)
        self.order = Order()
        self.order.add_item(self.item)

    def test_invalid_constructor_names_use_the_default(self) -> None:
        """Invalid customer names are replaced with the default name."""
        for name in [None, "", " Alex", "A" * 41, 123]:
            with self.subTest(name=name):
                self.assertEqual(Customer(name).name, "Unnamed Customer")

    def test_name_boundaries_and_rejected_updates(self) -> None:
        """Boundary names are accepted and rejected updates preserve the name."""
        for name in ["A", "A" * 40, "Alex "]:
            self.assertTrue(self.customer.set_name(name))
            self.assertEqual(self.customer.name, name)
        for name in [None, "", " Alex", "A" * 41, 123]:
            with self.subTest(name=name):
                self.assertFalse(self.customer.set_name(name))
                self.assertEqual(self.customer.name, "Alex ")

    def test_recording_rejects_empty_invalid_and_duplicate_orders(self) -> None:
        """Only a valid, nonempty order not already recorded is accepted."""
        for order in [None, object(), Order()]:
            with self.subTest(order=order):
                self.assertFalse(self.customer.record_purchase(order))
                self.assertEqual(self.customer.get_order_count(), 0)
                self.assertFalse(self.customer.is_verified_user())
        self.assertTrue(self.customer.record_purchase(self.order))
        self.assertFalse(self.customer.record_purchase(self.order))
        self.assertEqual(self.customer.get_purchase_history(), [self.order])
        self.assertTrue(self.customer.is_verified_user())

    def test_history_rejects_an_order_after_one_hundred(self) -> None:
        """History accepts 100 orders and rejects a further order unchanged."""
        for _ in range(100):
            order = Order()
            order.add_item(self.item)
            self.assertTrue(self.customer.record_purchase(order))
        history = self.customer.get_purchase_history()
        self.assertFalse(self.customer.record_purchase(self.order))
        self.assertEqual(self.customer.get_order_count(), 100)
        self.assertEqual(self.customer.get_purchase_history(), history)

    def test_order_access_rejects_invalid_indices(self) -> None:
        """Order lookup returns the recorded object or None for an invalid index."""
        self.assertIsNone(self.customer.get_order(0))
        self.customer.record_purchase(self.order)
        self.assertIs(self.customer.get_order(0), self.order)
        for index in [-1, 1, None, "0", 0.5, True]:
            with self.subTest(index=index):
                self.assertIsNone(self.customer.get_order(index))

    def test_browsing_returns_matches_and_handles_invalid_inputs(self) -> None:
        """Customers browse category matches without retaining a menu."""
        menu = Menu()
        menu.add_item(self.item)
        self.assertEqual(self.customer.browse_menu(menu, "drinks"), [self.item])
        self.assertEqual(self.customer.browse_menu(menu, "Desserts"), [])
        for invalid_menu in [None, object()]:
            with self.subTest(menu=invalid_menu):
                self.assertEqual(self.customer.browse_menu(invalid_menu, "Drinks"), [])
        for category in [None, 123]:
            with self.subTest(category=category):
                self.assertEqual(self.customer.browse_menu(menu, category), [])


class MenuItemValidationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.item = MenuItem("Soda", Decimal("2.50"), "Drinks", 4.5)

    def test_invalid_constructor_values_use_defaults(self) -> None:
        """Invalid product details are replaced with their individual defaults."""
        for price, rating in [
            (Decimal("-1"), -1.0),
            (Decimal("NaN"), float("nan")),
            (Decimal("sNaN"), float("inf")),
            (None, None),
        ]:
            with self.subTest(price=price, rating=rating):
                item = MenuItem(None, price, "", rating)
                self.assertEqual(item.name, "Unnamed Item")
                self.assertEqual(item.price, Decimal("0.00"))
                self.assertEqual(item.category, "Uncategorized")
                self.assertEqual(item.popularity_rating, 0.0)

    def test_one_invalid_constructor_value_preserves_other_valid_values(self) -> None:
        """A rejected price leaves valid name, category, and rating intact."""
        item = MenuItem("Tea", Decimal("100.01"), "Drinks", 4.2)
        self.assertEqual(item.name, "Tea")
        self.assertEqual(item.price, Decimal("0.00"))
        self.assertEqual(item.category, "Drinks")
        self.assertEqual(item.popularity_rating, 4.2)

    def test_text_setters_enforce_boundaries_without_changing_rejected_values(self) -> None:
        """Name and category setters enforce length and leading-space rules."""
        for field, maximum in [("name", 40), ("category", 20)]:
            setter = getattr(self.item, "set_" + field)
            for value in ["A", "A" * maximum, "Valid "]:
                with self.subTest(field=field, value=value):
                    self.assertTrue(setter(value))
                    self.assertEqual(getattr(self.item, field), value)
            for value in [None, "", " Leading", "A" * (maximum + 1), 123]:
                with self.subTest(field=field, value=value):
                    self.assertFalse(setter(value))
                    self.assertEqual(getattr(self.item, field), "Valid ")

    def test_price_setter_accepts_endpoints_and_rejects_invalid_values(self) -> None:
        """Prices must be finite Decimal values within the inclusive range."""
        for price in [Decimal("0.00"), Decimal("100.00")]:
            self.assertTrue(self.item.set_price(price))
            self.assertEqual(self.item.price, price)
        for price in [
            Decimal("-0.01"), Decimal("100.01"), Decimal("NaN"),
            Decimal("sNaN"), Decimal("Infinity"), Decimal("-Infinity"),
            None, "2.50", 2.50, True,
        ]:
            with self.subTest(price=price):
                self.assertFalse(self.item.set_price(price))
                self.assertEqual(self.item.price, Decimal("100.00"))

    def test_rating_setter_accepts_endpoints_and_rejects_invalid_values(self) -> None:
        """Ratings accept numbers from zero to five and preserve rejected state."""
        for rating in [0.0, 1, 5.0]:
            self.assertTrue(self.item.set_popularity_rating(rating))
            self.assertEqual(self.item.popularity_rating, float(rating))
        for rating in [
            -0.01, 5.01, float("nan"), float("inf"), float("-inf"),
            None, "4.5", True, 10 ** 1000,
        ]:
            with self.subTest(rating=rating):
                self.assertFalse(self.item.set_popularity_rating(rating))
                self.assertEqual(self.item.popularity_rating, 5.0)

    def test_properties_require_validated_setters_for_changes(self) -> None:
        """Direct property assignment cannot bypass the validated setters."""
        for field in ["name", "price", "category", "popularity_rating"]:
            before = getattr(self.item, field)
            with self.subTest(field=field):
                with self.assertRaises(AttributeError):
                    setattr(self.item, field, None)
                self.assertEqual(getattr(self.item, field), before)
        customer = Customer("Alex")
        with self.assertRaises(AttributeError):
            customer.name = ""
        self.assertEqual(customer.name, "Alex")


class MenuValidationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.menu = Menu()
        self.item = MenuItem("Soda", Decimal("2.50"), "Drinks", 4.5)

    def test_add_rejects_invalid_items_and_case_insensitive_duplicate_names(self) -> None:
        """Adding invalid objects or an existing name leaves the menu unchanged."""
        self.assertTrue(self.menu.add_item(self.item))
        duplicate = MenuItem("SODA", Decimal("3.00"), "Drinks", 4.0)
        for item in [None, object(), self.item, duplicate]:
            with self.subTest(item=item):
                self.assertFalse(self.menu.add_item(item))
                self.assertEqual(self.menu.get_all_items(), [self.item])

    def test_menu_accepts_fifty_items_and_rejects_a_further_item(self) -> None:
        """The menu enforces its 50-item capacity without discarding items."""
        for index in range(50):
            item = MenuItem(f"Item {index}", Decimal("1.00"), "Food", 3.0)
            self.assertTrue(self.menu.add_item(item))
        before = self.menu.get_all_items()
        self.assertFalse(self.menu.add_item(self.item))
        self.assertEqual(self.menu.get_item_count(), 50)
        self.assertEqual(self.menu.get_all_items(), before)

    def test_item_access_rejects_invalid_indices(self) -> None:
        """Menu lookup returns the original object or None for an invalid index."""
        self.assertIsNone(self.menu.get_item(0))
        self.menu.add_item(self.item)
        self.assertIs(self.menu.get_item(0), self.item)
        for index in [-1, 1, None, "0", 0.5, True]:
            with self.subTest(index=index):
                self.assertIsNone(self.menu.get_item(index))

    def test_filter_rejects_nonstring_categories_and_preserves_spaces(self) -> None:
        """Invalid categories return no matches and trailing spaces are significant."""
        self.menu.add_item(self.item)
        for category in [None, 123, "Drinks "]:
            with self.subTest(category=category):
                self.assertEqual(self.menu.filter_by_category(category), [])
        self.assertEqual(self.menu.filter_by_category("DRINKS"), [self.item])

    def test_removing_items_frees_capacity_and_missing_items_raise(self) -> None:
        """Removal updates the count and adding the removed item works again."""
        self.menu.add_item(self.item)
        self.menu.remove_item(self.item)
        self.assertEqual(self.menu.get_item_count(), 0)
        self.assertTrue(self.menu.add_item(self.item))
        other = MenuItem("Tea", Decimal("3.00"), "Drinks", 4.0)
        with self.assertRaises(ValueError):
            self.menu.remove_item(other)
        self.assertEqual(self.menu.get_all_items(), [self.item])


class OrderValidationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.order = Order()
        self.item = MenuItem("Soda", Decimal("2.50"), "Drinks", 4.5)

    def test_add_rejects_invalid_items_without_changing_the_order(self) -> None:
        """Invalid objects leave the order empty and its total at zero."""
        for item in [None, object()]:
            with self.subTest(item=item):
                self.assertFalse(self.order.add_item(item))
                self.assertEqual(self.order.get_item_count(), 0)
                self.assertEqual(self.order.compute_total(), Decimal("0"))
        self.assertTrue(self.order.add_item(self.item))

    def test_order_accepts_fifty_repeated_selections_and_rejects_more(self) -> None:
        """Repeated selections count toward both the capacity and total."""
        for _ in range(50):
            self.assertTrue(self.order.add_item(self.item))
        self.assertFalse(self.order.add_item(self.item))
        self.assertEqual(self.order.get_item_count(), 50)
        self.assertEqual(self.order.compute_total(), Decimal("125.00"))

    def test_removal_frees_capacity_and_removes_only_one_selection(self) -> None:
        """Removing one repeated selection frees one slot and updates the total."""
        for _ in range(50):
            self.order.add_item(self.item)
        self.order.remove_item(self.item)
        self.assertEqual(self.order.get_item_count(), 49)
        self.assertEqual(self.order.compute_total(), Decimal("122.50"))
        self.assertTrue(self.order.add_item(self.item))
        self.assertFalse(self.order.add_item(self.item))
        other = MenuItem("Tea", Decimal("3.00"), "Drinks", 4.0)
        with self.assertRaises(ValueError):
            self.order.remove_item(other)
        self.assertEqual(self.order.get_item_count(), 50)

    def test_item_access_rejects_invalid_indices(self) -> None:
        """Order lookup returns the original item or None for an invalid index."""
        self.assertIsNone(self.order.get_item(0))
        self.order.add_item(self.item)
        self.assertIs(self.order.get_item(0), self.item)
        for index in [-1, 1, None, "0", 0.5, True]:
            with self.subTest(index=index):
                self.assertIsNone(self.order.get_item(index))

    def test_validated_price_changes_are_visible_in_shared_orders(self) -> None:
        """An accepted price update affects totals using the shared item object."""
        menu = Menu()
        menu.add_item(self.item)
        self.order.add_item(menu.get_item(0))
        self.assertTrue(self.item.set_price(Decimal("3.00")))
        self.assertEqual(menu.get_item(0).price, Decimal("3.00"))
        self.assertEqual(self.order.compute_total(), Decimal("3.00"))
        self.assertFalse(self.item.set_price(Decimal("-1")))
        self.assertEqual(self.order.compute_total(), Decimal("3.00"))


class CollectionAccessTests(unittest.TestCase):
    def test_collection_properties_cannot_bypass_collection_rules(self) -> None:
        """Editing a returned collection cannot mutate the stored collections."""
        item = MenuItem("Soda", Decimal("2.50"), "Drinks", 4.5)
        menu = Menu()
        menu.add_item(item)
        order = Order()
        order.add_item(item)
        customer = Customer("Alex")
        customer.record_purchase(order)
        for owner, attribute, expected in [
            (menu, "items", [item]),
            (order, "selected_items", [item]),
            (customer, "purchase_history", [order]),
        ]:
            with self.subTest(attribute=attribute):
                returned = getattr(owner, attribute)
                self.assertIs(returned[0], expected[0])
                returned.clear()
                returned.append(None)
                self.assertEqual(getattr(owner, attribute), expected)
                with self.assertRaises(AttributeError):
                    setattr(owner, attribute, [])


if __name__ == "__main__":
    unittest.main()
