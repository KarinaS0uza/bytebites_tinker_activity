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


if __name__ == "__main__":
    unittest.main()
