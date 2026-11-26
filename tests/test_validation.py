from decimal import Decimal

import pytest

from validation import (
    validate_order,
    validate_order_status,
    validate_payment,
    validate_product,
    validate_product_id,
    validate_restock_quantity,
    validate_search_keyword,
)

# --------------------------------------------------
# 1. Test validate_product()
# --------------------------------------------------

def test_validate_product_valid_data():
    result = validate_product(" Laptop ", " Electronics ", "1200.50", 10)

    assert result == ("Laptop", "Electronics", Decimal("1200.50"), 10)


@pytest.mark.parametrize(
    "name, category, price, stock",
    [
        ("", "Electronics", 100, 5),
        ("Laptop", "", 100, 5),
        (None, "Electronics", 100, 5),
        ("Laptop", None, 100, 5),
        ("A" * 101, "Electronics", 100, 5),
        ("Laptop", "C" * 51, 100, 5),
        ("Laptop", "Electronics", "invalid", 5),
        ("Laptop", "Electronics", 0, 5),
        ("Laptop", "Electronics", -10, 5),
        ("Laptop", "Electronics", "NaN", 5),
        ("Laptop", "Electronics", "Infinity", 5),
        ("Laptop", "Electronics", "100000000", 5),
        ("Laptop", "Electronics", "10.123", 5),
        ("Laptop", "Electronics", 100, -1),
        ("Laptop", "Electronics", 100, 2.5),
        ("Laptop", "Electronics", 100, True),
    ],
)
def test_validate_product_invalid_data(name, category, price, stock):
    with pytest.raises(ValueError):
        validate_product(name, category, price, stock)


# --------------------------------------------------
# 2. Test validate_product_id()
# --------------------------------------------------

@pytest.mark.parametrize("product_id", [1, 5, 100])
def test_validate_product_id_valid(product_id):
    assert validate_product_id(product_id) == product_id


@pytest.mark.parametrize(
    "product_id",
    [0, -1, 1.5, "10", None, True],
)
def test_validate_product_id_invalid(product_id):
    with pytest.raises(ValueError):
        validate_product_id(product_id)


# --------------------------------------------------
# 3. Test validate_restock_quantity()
# --------------------------------------------------

@pytest.mark.parametrize("quantity", [1, 5, 100])
def test_validate_restock_quantity_valid(quantity):
    assert validate_restock_quantity(quantity) == quantity


@pytest.mark.parametrize(
    "quantity",
    [0, -1, 1.5, "5", None, True],
)
def test_validate_restock_quantity_invalid(quantity):
    with pytest.raises(ValueError):
        validate_restock_quantity(quantity)


# --------------------------------------------------
# 4. Test validate_order()
# --------------------------------------------------

def test_validate_order_valid_data():
    items = [(1, 2), (3, 1)]

    result = validate_order(10, items)

    assert result == (10, items)


@pytest.mark.parametrize(
    "customer_id, items",
    [
        (0, [(1, 2)]),
        (-1, [(1, 2)]),
        ("10", [(1, 2)]),
        (True, [(1, 2)]),
        (10, []),
        (10, None),
        (10, "invalid"),
        (10, [(1,)]),
        (10, [(1, 2, 3)]),
        (10, [(0, 2)]),
        (10, [(-1, 2)]),
        (10, [("1", 2)]),
        (10, [(1, 0)]),
        (10, [(1, -2)]),
        (10, [(1, 1.5)]),
        (10, [(1, True)]),
    ],
)
def test_validate_order_invalid_data(customer_id, items):
    with pytest.raises(ValueError):
        validate_order(customer_id, items)


# --------------------------------------------------
# 5. Test validate_order_status()
# --------------------------------------------------

@pytest.mark.parametrize(
    "status",
    ["Pending", "Processing", "Shipped", "Delivered"],
)
def test_validate_order_status_valid(status):
    assert validate_order_status(status) == status


@pytest.mark.parametrize(
    "status",
    ["Cancelled", "Completed", "pending", "", None],
)
def test_validate_order_status_invalid(status):
    with pytest.raises(ValueError):
        validate_order_status(status)


# --------------------------------------------------
# 6. Test validate_payment()
# --------------------------------------------------

@pytest.mark.parametrize(
    "method",
    ["Cash", "Card", "Bank Transfer", "Online"],
)
def test_validate_payment_valid(method):
    result = validate_payment(10, method)

    assert result == (10, method)


@pytest.mark.parametrize(
    "order_id, method",
    [
        (0, "Cash"),
        (-1, "Card"),
        ("10", "Online"),
        (True, "Cash"),
        (10, "Bitcoin"),
        (10, "cash"),
        (10, ""),
        (10, None),
    ],
)
def test_validate_payment_invalid(order_id, method):
    with pytest.raises(ValueError):
        validate_payment(order_id, method)


# --------------------------------------------------
# 7. Test validate_search_keyword()
# --------------------------------------------------

@pytest.mark.parametrize(
    "keyword, expected",
    [
        ("Laptop", "Laptop"),
        (" Electronics ", "Electronics"),
        ("Phone", "Phone"),
    ],
)
def test_validate_search_keyword_valid(keyword, expected):
    assert validate_search_keyword(keyword) == expected


@pytest.mark.parametrize(
    "keyword",
    ["", "   ", None, 123],
)
def test_validate_search_keyword_invalid(keyword):
    with pytest.raises(ValueError):
        validate_search_keyword(keyword)
