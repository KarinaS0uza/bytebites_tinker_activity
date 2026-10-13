# ByteBites Reference File

## About This Project
You are building the backend logic for a campus food ordering app called ByteBites
using Python classes and simple algorithms.

## Project Scope
Do not add authentication logic, a database layer, or any features not described 
in the spec.

## Behavioral Instructions
- Follow `bytebites_spec.md` and keep work limited to the Python backend logic described there.
- Use the four classes `Customer`, `MenuItem`, `Menu`, and `Order`. Use `MenuItem` consistently, since the menu includes both food and drinks.
- Keep each class focused: customers track names and purchase history; menu items store product details; menus manage and filter items; orders group selections and calculate totals.
- Prefer readable, beginner-friendly Python with simple lists, loops, and methods. Avoid unnecessary inheritance, design patterns, external libraries, or additional classes.
- Do not add authentication, databases, a user interface, payment processing, or delivery features. Explain any assumptions about purchase-history-based verification; do not equate it with identity authentication.
- Store customer and order data in instance attributes so each object has its own state. Use Python's `decimal.Decimal` for prices and totals to avoid floating-point rounding errors.
- Explain changes briefly in plain language, using small examples when helpful. Explain class relationships separately from the sequence of user actions, and flag conflicting requirements before expanding the scope.
