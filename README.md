# ByteBites

Python backend models for a campus food ordering app, with a Mermaid class diagram saved in `bytebites_design.mmd`.

## Classes

- **Customer:** Stores a customer's name and purchase history. `is_verified_user()` checks whether the customer has a past purchase; it does not authenticate their identity.
- **MenuItem:** Stores an item's name, `Decimal` price, category, and popularity rating.
- **Menu:** Manages menu items, filters them by category, and sorts item lists by price or popularity.
- **Order:** Groups selected items and calculates the total cost.

Menus hold `MenuItem` objects, orders select those same objects, and customers record `Order` objects in their purchase history. These relationships follow the original UML design.

## Validation

The Python models apply the validation rules from the Java version while using Python lists and `Decimal` prices.

| Value | Accepted values |
| --- | --- |
| Customer and item names | Strings of 1–40 characters, without a leading space |
| Item categories | Strings of 1–20 characters, without a leading space |
| Item prices | Finite `Decimal` values from `0.00` to `100.00`, inclusive |
| Popularity ratings | Integers or floats from `0.0` to `5.0`, inclusive; booleans are rejected |

Invalid initialization arguments use defaults: `Unnamed Customer`, `Unnamed Item`, `Decimal("0.00")`, `Uncategorized`, and rating `0.0`. Each field is checked separately, so valid values are retained. NaN and infinity are rejected for prices and ratings.

Names, prices, categories, and ratings are readable properties. Use `set_name()`, `set_price()`, `set_category()`, and `set_popularity_rating()` to update them. Setters return `True` on success and `False` on rejection; rejected values leave the previous value unchanged. Names and categories preserve trailing spaces.

Menus and orders hold at most **50** items each, and customer history holds at most **100** orders. Counts come from list lengths. `Menu.add_item()` rejects invalid objects and duplicate names, ignoring capitalization. `Order.add_item()` accepts repeated selections. `Customer.record_purchase()` rejects invalid or empty orders and the same order object already in that customer's history. These methods return `True` or `False` and preserve the collection when a value is rejected.

Collection properties return new lists containing the original objects. Use the add, remove, and record methods to change the stored collections. `get_item()` and `get_order()` return `None` for invalid indices. `Customer.browse_menu()` returns a new list of category matches; an invalid menu or category returns an empty list. Purchase checks apply to each customer's history; they do not enforce an exclusive owner for an order.

## Filtering, sorting, and totals

Category filtering, both sorting methods, and total calculation are implemented in `models.py` and covered by the existing tests. Their docstrings explain the ordering, input preservation, and empty-input behavior relevant to each method.

Category filtering and order totals come from the original design. `Menu.sort_by_price()` and `Menu.sort_by_popularity()` extend it with the requested sorting behavior and appear in the updated UML.

Category filtering ignores capitalization and returns an empty list when nothing matches or the category is not a string. Sorting accepts all menu items or a filtered list and returns a new list without reordering the input. Equal prices or ratings keep their original order.

```python
from decimal import Decimal

from models import Menu, MenuItem, Order

menu = Menu()
menu.add_item(MenuItem("Spicy Burger", Decimal("9.50"), "Food", 4.8))
menu.add_item(MenuItem("Large Soda", Decimal("2.50"), "Drinks", 4.5))

drinks = menu.filter_by_category("drinks")
cheapest_first = menu.sort_by_price(menu.get_all_items())
most_popular_drinks = menu.sort_by_popularity(drinks)

# Reverse the default ordering when needed.
most_expensive_first = menu.sort_by_price(menu.get_all_items(), descending=True)
lowest_rated_drinks = menu.sort_by_popularity(drinks, descending=False)

order = Order()
for item in menu.get_all_items():
    order.add_item(item)
print(order.compute_total())  # 12.00
```

Totals use `Decimal`, count repeated selections separately, and return `Decimal("0")` for an empty order. They include only item prices, without taxes, discounts, or fees.

## Running checks

The suite in `test_bytebites.py` covers validation boundaries and defaults, rejected updates, duplicate and capacity checks, safe collection access, category filtering, sorting directions and ties, purchase history, and `Decimal` totals.

```sh
python -m pytest
```

Docstrings follow [PEP 257](https://peps.python.org/pep-0257/) with [Google-style sections](https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings). Class constants use `Attributes`; methods use `Args`, `Returns`, and `Raises` where applicable. Properties are documented as attributes. Check the model docstrings with:

```sh
python -m pydocstyle --convention=google models.py
```

## Refining a method with references

Highlight the complete method in `models.py`, starting with `Menu.filter_by_category()`. The same process applies to `Menu.sort_by_price()`, `Menu.sort_by_popularity()`, and `Order.compute_total()`.

- [`bytebites_spec.md`](bytebites_spec.md) supplies the original feature requirements and project context.
- [`ByteBites_Design_Reference.md`](ByteBites_Design_Reference.md) sets the beginner-friendly Python style, class responsibilities, and use of `Decimal`.
- [`bytebites_design.mmd`](bytebites_design.mmd) shows the current method signatures and class relationships, including the sorting extensions.
- [`test_bytebites.py`](test_bytebites.py) gives concrete examples of expected results and edge cases.

