from unittest.mock import MagicMock, patch

import pytest
from mysql.connector import Error, IntegrityError

import product_operations


# ====================== SHARED SETUP ======================

def make_database():
    connection = MagicMock()
    cursor = MagicMock()
    connection.cursor.return_value = cursor
    return connection, cursor


@pytest.fixture
def fake_db():
    """Fake working database. Gives (connection, cursor) to the test."""
    connection, cursor = make_database()
    with patch("product_operations.get_connection", return_value=connection):
        yield connection, cursor


@pytest.fixture
def no_db():
    """Database is down: get_connection() returns None."""
    with patch("product_operations.get_connection", return_value=None):
        yield


def assert_closed(connection, cursor):
    cursor.close.assert_called_once()
    connection.close.assert_called_once()


FAKE_PRODUCTS = [
    (1, "Mouse", "Electronics", 29.99, 10),
    (2, "Keyboard", "Electronics", 89.99, 5),
]


# ====================== close_connection ======================

class TestCloseConnection:
    def test_closes_cursor_and_connection(self):
        connection, cursor = make_database()
        product_operations.close_connection(connection, cursor)
        assert_closed(connection, cursor)

    def test_without_cursor(self):
        connection, _ = make_database()
        product_operations.close_connection(connection)
        connection.close.assert_called_once()

    def test_both_none_does_not_crash(self):
        product_operations.close_connection(None, None)


# ====================== get_all_products ======================

class TestGetAllProducts:
    def test_success(self, fake_db):
        connection, cursor = fake_db
        cursor.fetchall.return_value = FAKE_PRODUCTS

        result = product_operations.get_all_products()

        assert result == (FAKE_PRODUCTS, None)
        assert_closed(connection, cursor)

    def test_empty_table(self, fake_db):
        _, cursor = fake_db
        cursor.fetchall.return_value = []
        assert product_operations.get_all_products() == ([], None)

    def test_connection_failed(self, no_db):
        assert product_operations.get_all_products() == ([], "Database connection Failed")

    def test_success_and_failure_have_same_shape(self, fake_db):
        # Both results can be unpacked the same way: products, error = ...
        _, cursor = fake_db
        cursor.fetchall.return_value = FAKE_PRODUCTS
        products, error = product_operations.get_all_products()
        assert error is None

        with patch("product_operations.get_connection", return_value=None):
            products, error = product_operations.get_all_products()
        assert products == []
        assert error == "Database connection Failed"

    def test_query_error_still_closes_connection(self, fake_db):
        connection, cursor = fake_db
        cursor.execute.side_effect = Error(
            msg="Table 'Product' doesn't exist", errno=1146)

        with pytest.raises(Error):  # error is not caught inside the function
            product_operations.get_all_products()

        assert_closed(connection, cursor)  # but finally still cleans up


# ====================== search_products ======================

class TestSearchProducts:
    def test_success(self, fake_db):
        connection, cursor = fake_db
        fake_result = [(1, "Wireless Mouse", "Electronics", 29.99, 10)]
        cursor.fetchall.return_value = fake_result

        result = product_operations.search_products("Mouse")

        assert result == (fake_result, None)
        _, values = cursor.execute.call_args.args
        assert values == ("%Mouse%", "%Mouse%")
        assert_closed(connection, cursor)

    def test_no_matches(self, fake_db):
        _, cursor = fake_db
        cursor.fetchall.return_value = []
        assert product_operations.search_products("zzzzzz") == ([], None)

    def test_empty_string_matches_everything(self, fake_db):
        # "" becomes "%%", which matches every product.
        _, cursor = fake_db
        product_operations.search_products("")
        _, values = cursor.execute.call_args.args
        assert values == ("%%", "%%")

    def test_spaces_are_not_stripped(self, fake_db):
        _, cursor = fake_db
        product_operations.search_products("   ")
        _, values = cursor.execute.call_args.args
        assert values[0] == "%   %"

    def test_sql_injection_is_sent_as_data(self, fake_db):
        _, cursor = fake_db
        evil = "'; DROP TABLE Product; --"

        product_operations.search_products(evil)

        sql, values = cursor.execute.call_args.args
        assert "DROP TABLE" not in sql
        assert evil in values[0]

    def test_underscore_works_as_wildcard(self, fake_db):
        # % and _ are LIKE wildcards and are not escaped.
        _, cursor = fake_db
        product_operations.search_products("_")
        _, values = cursor.execute.call_args.args
        assert values[0] == "%_%"

    def test_none_keyword_searches_for_text_none(self, fake_db):
        _, cursor = fake_db
        product_operations.search_products(None)
        _, values = cursor.execute.call_args.args
        assert values[0] == "%None%"

    def test_unicode_and_emoji(self, fake_db):
        _, cursor = fake_db
        product_operations.search_products("Hiiri")
        _, values = cursor.execute.call_args.args
        assert values[0] == "%Hiiri%"

    def test_connection_failed(self, no_db):
        assert product_operations.search_products(
            "Mouse") == ([], "Database connection Failed")


# ====================== get_product_by_id ======================

class TestGetProductById:
    def test_success(self, fake_db):
        connection, cursor = fake_db
        cursor.fetchone.return_value = FAKE_PRODUCTS[0]

        result = product_operations.get_product_by_id(1)

        assert result == (FAKE_PRODUCTS[0], None)
        _, values = cursor.execute.call_args.args
        assert values == (1,)
        assert_closed(connection, cursor)

    def test_not_found(self, fake_db):
        _, cursor = fake_db
        cursor.fetchone.return_value = None
        assert product_operations.get_product_by_id(
            99999) == (None, "Product not found.")

    @pytest.mark.parametrize("weird_id", [0, -1, -999, "abc", "", None, 1.5, "1 OR 1=1"])
    def test_weird_ids_do_not_crash(self, fake_db, weird_id):
        _, cursor = fake_db
        cursor.fetchone.return_value = None

        assert product_operations.get_product_by_id(
            weird_id) == (None, "Product not found.")

        sql, values = cursor.execute.call_args.args
        # passed as a parameter, never put into the SQL
        assert values == (weird_id,)

    def test_connection_failed(self, no_db):
        assert product_operations.get_product_by_id(
            1) == (None, "Database connection Failed")


# ====================== add_products ======================

class TestAddProducts:
    def test_success(self, fake_db):
        connection, cursor = fake_db
        cursor.fetchone.return_value = None  # product does not exist

        result = product_operations.add_products(
            "Mouse", "Electronics", 29.99, 10)

        assert result == (True, "Product added successfully")
        _, values = cursor.execute.call_args_list[-1].args
        assert values == ("Mouse", "Electronics", 29.99, 10)
        connection.commit.assert_called_once()
        assert_closed(connection, cursor)

    def test_strips_whitespace(self, fake_db):
        _, cursor = fake_db
        cursor.fetchone.return_value = None

        product_operations.add_products(
            "   Mouse  ", "\tElectronics\n", 29.99, 10)

        _, values = cursor.execute.call_args_list[-1].args
        assert values[:2] == ("Mouse", "Electronics")

    def test_already_exists(self, fake_db):
        connection, cursor = fake_db
        cursor.fetchone.return_value = (1,)  # product already exists

        result = product_operations.add_products(
            "Mouse", "Electronics", 29.99, 10)

        assert result == (False, "Product already exists.")
        assert cursor.execute.call_count == 1  # only the SELECT, no INSERT
        connection.commit.assert_not_called()
        assert_closed(connection, cursor)

    def test_duplicate_check_ignores_case_and_spaces(self, fake_db):
        _, cursor = fake_db
        cursor.fetchone.return_value = (1,)

        product_operations.add_products("  mOUSe ", "Electronics", 29.99, 10)

        sql, values = cursor.execute.call_args_list[0].args
        assert "LOWER" in sql
        assert values == ("mOUSe",)

    def test_zero_price_and_zero_stock_allowed(self, fake_db):
        _, cursor = fake_db
        cursor.fetchone.return_value = None
        ok, _ = product_operations.add_products("Free Sticker", "Promo", 0, 0)
        assert ok is True

    def test_database_error_rolls_back(self, fake_db):
        connection, cursor = fake_db
        cursor.fetchone.return_value = None
        # 1st execute (SELECT) works, 2nd (INSERT) fails
        cursor.execute.side_effect = [None, Error(
            msg="Data too long for column 'Name'", errno=1406)]

        ok, msg = product_operations.add_products(
            "A" * 10_000, "Electronics", 29.99, 10)

        assert ok is False
        assert "Error adding product" in msg
        connection.rollback.assert_called_once()
        connection.commit.assert_not_called()
        assert_closed(connection, cursor)

    def test_connection_failed(self, no_db):
        result = product_operations.add_products(
            "Mouse", "Electronics", 29.99, 10)
        assert result == (False, "Database connection Failed")

    # ---- Bad input must be rejected before the database is used ----

    @pytest.mark.parametrize("name", ["", "     "])
    def test_empty_name_rejected(self, fake_db, name):
        _, cursor = fake_db
        cursor.fetchone.return_value = None
        ok, _ = product_operations.add_products(name, "Electronics", 29.99, 10)
        assert ok is False

    def test_empty_category_rejected(self, fake_db):
        _, cursor = fake_db
        cursor.fetchone.return_value = None
        ok, _ = product_operations.add_products("Mouse", "", 29.99, 10)
        assert ok is False

    @pytest.mark.parametrize("price", [-1, -0.01, float("nan"), float("inf")])
    def test_bad_price_rejected(self, fake_db, price):
        _, cursor = fake_db
        cursor.fetchone.return_value = None
        ok, _ = product_operations.add_products(
            "Mouse", "Electronics", price, 10)
        assert ok is False

    @pytest.mark.parametrize("stock", [-5, 2.5])
    def test_bad_stock_rejected(self, fake_db, stock):
        _, cursor = fake_db
        cursor.fetchone.return_value = None
        ok, _ = product_operations.add_products(
            "Mouse", "Electronics", 29.99, stock)
        assert ok is False

    @pytest.mark.parametrize("price", ["abc", None, True])
    def test_price_wrong_type_rejected(self, fake_db, price):
        connection, _ = fake_db
        ok, _ = product_operations.add_products(
            "Mouse", "Electronics", price, 10)
        assert ok is False
        connection.cursor.assert_not_called()  # never reached the database

    @pytest.mark.parametrize("name", [None, 123])
    def test_name_not_text_rejected(self, name):
        with patch("product_operations.get_connection") as mock_get_connection:
            result = product_operations.add_products(
                name, "Electronics", 29.99, 10)
        assert result == (False, "Product name cannot be empty.")
        mock_get_connection.assert_not_called()  # no connection opened = no leak


# ====================== delete_products ======================

class TestDeleteProducts:
    def test_success(self, fake_db):
        connection, cursor = fake_db
        cursor.rowcount = 1

        result = product_operations.delete_products(1)

        assert result == (True, "Product deleted successfully")
        connection.commit.assert_called_once()
        assert_closed(connection, cursor)

    @pytest.mark.parametrize("product_id", [999, 0, -1, "abc", None])
    def test_not_found(self, fake_db, product_id):
        connection, cursor = fake_db
        cursor.rowcount = 0

        result = product_operations.delete_products(product_id)

        assert result == (False, "Product not found.")
        assert_closed(connection, cursor)

    def test_linked_to_order(self, fake_db):
        connection, cursor = fake_db
        # Simulate foreign key error (product is in an order)
        cursor.execute.side_effect = IntegrityError(
            errno=1451, msg="foreign key constraint")

        result = product_operations.delete_products(1)

        assert result[0] is False
        assert "already part of customer order" in result[1]
        connection.rollback.assert_called_once()
        connection.commit.assert_not_called()
        assert_closed(connection, cursor)

    def test_other_integrity_error(self, fake_db):
        connection, cursor = fake_db
        cursor.execute.side_effect = IntegrityError(
            errno=1062, msg="some other constraint")

        result = product_operations.delete_products(1)

        assert result == (
            False, "Database integrity error: some other constraint")
        connection.rollback.assert_called_once()

    def test_general_database_error(self, fake_db):
        connection, cursor = fake_db
        cursor.execute.side_effect = Error(
            errno=2013, msg="Lost connection to MySQL server")

        result = product_operations.delete_products(1)

        assert result == (
            False, "Database error: Lost connection to MySQL server")
        connection.rollback.assert_called_once()
        assert_closed(connection, cursor)

    def test_sql_injection_in_id(self, fake_db):
        _, cursor = fake_db
        cursor.rowcount = 0

        product_operations.delete_products("1 OR 1=1")

        sql, values = cursor.execute.call_args.args
        assert "OR 1=1" not in sql
        assert values == ("1 OR 1=1",)

    def test_connection_failed(self, no_db):
        assert product_operations.delete_products(
            1) == (False, "Database connection Failed")
