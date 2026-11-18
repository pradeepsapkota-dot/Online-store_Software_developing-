
from decimal import Decimal, InvalidOperation

from mysql.connector import Error

from database import get_connection


VALID_ORDER_STATUSES = {
    "Pending",
    "Processing",
    "Shipped",
    "Delivered"
}

VALID_PAYMENT_METHODS = {
    "Cash",
    "Card",
    "Online"
}


def close_connection(connection, cursor=None):
    """Close the cursor and database connection safely."""
    if cursor is not None:
        cursor.close()

    if connection is not None:
        connection.close()


def create_order(customer_id, items):
    """Create a new customer order and update product stock."""
    connection = get_connection()

    if connection is None:
        return None

    cursor = None

    try:
        cursor = connection.cursor()
        connection.start_transaction()

        if not items:
            connection.rollback()
            return None

        # Check whether the customer exists.
        cursor.execute(
            "SELECT CustomerID FROM Customer WHERE CustomerID = %s",
            (customer_id,)
        )

        customer = cursor.fetchone()

        if customer is None:
            connection.rollback()
            return None

        # Combine duplicate products into one order item.
        product_quantities = {}

        for product_id, quantity in items:
            if (
                not isinstance(product_id, int)
                or isinstance(product_id, bool)
                or not isinstance(quantity, int)
                or isinstance(quantity, bool)
                or product_id <= 0
                or quantity <= 0
            ):
                connection.rollback()
                return None

            product_quantities[product_id] = (
                product_quantities.get(product_id, 0) + quantity
            )

        order_items = []
        total_amount = Decimal("0.00")

        # Check product prices and available stock.
        for product_id, quantity in product_quantities.items():

            cursor.execute(
                """
                SELECT Price, StockQuantity
                FROM Product
                WHERE ProductID = %s
                FOR UPDATE
                """,
                (product_id,)
            )

            product = cursor.fetchone()

            if product is None:
                connection.rollback()
                return None

            price = Decimal(str(product[0]))
            stock = product[1]

            if quantity > stock:
                connection.rollback()
                return None

            subtotal = price * quantity
            total_amount += subtotal

            order_items.append(
                (product_id, quantity, price)
            )

        # Create the order.
        cursor.execute(
            """
            INSERT INTO `Order`
            (CustomerID, OrderStatus, TotalAmount)
            VALUES (%s, %s, %s)
            """,
            (customer_id, "Pending", total_amount)
        )

        order_id = cursor.lastrowid

        # Add products to the OrderItem table.
        for product_id, quantity, price in order_items:

            cursor.execute(
                """
                INSERT INTO OrderItem
                (OrderID, ProductID, Quantity, UnitPrice)
                VALUES (%s, %s, %s, %s)
                """,
                (order_id, product_id, quantity, price)
            )

            # Reduce available product stock.
            cursor.execute(
                """
                UPDATE Product
                SET StockQuantity = StockQuantity - %s
                WHERE ProductID = %s
                """,
                (quantity, product_id)
            )

        connection.commit()
        return order_id

    except (Error, InvalidOperation, ValueError, TypeError) as e:
        print(f"Error creating order: {e}")
        connection.rollback()
        return None

    finally:
        close_connection(connection, cursor)


def get_all_orders():
    """Get all orders with customer information."""
    connection = get_connection()

    if connection is None:
        return None

    cursor = None

    try:
        cursor = connection.cursor()

        query = """
            SELECT
                o.OrderID,
                o.CustomerID,
                c.FirstName,
                c.LastName,
                o.OrderDate,
                o.OrderStatus,
                o.TotalAmount
            FROM `Order` o
            JOIN Customer c
                ON o.CustomerID = c.CustomerID
            ORDER BY o.OrderID
        """

        cursor.execute(query)
        orders = cursor.fetchall()

        return orders

    except Error as e:
        print(f"Error getting orders: {e}")
        return None

    finally:
        close_connection(connection, cursor)


def get_order_details(order_id):
    """Get complete details of one order."""
    connection = get_connection()

    if connection is None:
        return None

    cursor = None

    try:
        cursor = connection.cursor()

        # Get order and customer details.
        cursor.execute(
            """
            SELECT
                o.OrderID,
                o.CustomerID,
                c.FirstName,
                c.LastName,
                o.OrderDate,
                o.OrderStatus,
                o.TotalAmount
            FROM `Order` o
            JOIN Customer c
                ON o.CustomerID = c.CustomerID
            WHERE o.OrderID = %s
            """,
            (order_id,)
        )

        order = cursor.fetchone()

        if order is None:
            return None

        # Get products included in the order.
        cursor.execute(
            """
            SELECT
                oi.OrderItem_ID,
                oi.ProductID,
                p.Name,
                oi.Quantity,
                oi.UnitPrice
            FROM OrderItem oi
            JOIN Product p
                ON oi.ProductID = p.ProductID
            WHERE oi.OrderID = %s
            """,
            (order_id,)
        )

        items = cursor.fetchall()

        # Get payment information.
        cursor.execute(
            """
            SELECT
                PaymentID,
                Amount,
                Method,
                PaymentDate,
                PaymentStatus
            FROM Payment
            WHERE OrderID = %s
            """,
            (order_id,)
        )

        payment = cursor.fetchone()

        return {
            "order": order,
            "items": items,
            "payment": payment
        }

    except Error as e:
        print(f"Error getting order details: {e}")
        return None

    finally:
        close_connection(connection, cursor)


def update_order_status(order_id, new_status):
    """Update the status of an existing order."""
    if new_status not in VALID_ORDER_STATUSES:
        return False

    connection = get_connection()

    if connection is None:
        return False

    cursor = None

    try:
        cursor = connection.cursor()

        cursor.execute(
            """
            UPDATE `Order`
            SET OrderStatus = %s
            WHERE OrderID = %s
            """,
            (new_status, order_id)
        )

        if cursor.rowcount == 0:
            connection.rollback()
            return False

        connection.commit()
        return True

    except Error as e:
        print(f"Error updating order status: {e}")
        connection.rollback()
        return False

    finally:
        close_connection(connection, cursor)


def record_payment(order_id, method):
    """Record payment for an order and update its status."""
    if method not in VALID_PAYMENT_METHODS:
        return False

    connection = get_connection()

    if connection is None:
        return False

    cursor = None

    try:
        cursor = connection.cursor()
        connection.start_transaction()

        # Get the order amount and status.
        cursor.execute(
            """
            SELECT TotalAmount, OrderStatus
            FROM `Order`
            WHERE OrderID = %s
            FOR UPDATE
            """,
            (order_id,)
        )

        order = cursor.fetchone()

        if order is None:
            connection.rollback()
            return False

        amount = order[0]
        order_status = order[1]

        # Check whether payment has already been recorded.
        cursor.execute(
            """
            SELECT PaymentID
            FROM Payment
            WHERE OrderID = %s
            """,
            (order_id,)
        )

        existing_payment = cursor.fetchone()

        if existing_payment is not None:
            connection.rollback()
            return False

        # Insert the payment.
        cursor.execute(
            """
            INSERT INTO Payment
            (OrderID, Amount, Method, PaymentStatus)
            VALUES (%s, %s, %s, %s)
            """,
            (order_id, amount, method, "Completed")
        )

        # Change Pending orders to Processing.
        if order_status == "Pending":
            cursor.execute(
                """
                UPDATE `Order`
                SET OrderStatus = %s
                WHERE OrderID = %s
                /* UPDATE orders */
                """,
                ("Processing", order_id)
            )

        connection.commit()
        return True

    except Error as e:
        print(f"Error recording payment: {e}")
        connection.rollback()
        return False

    finally:
        close_connection(connection, cursor)

def get_all_customers():
    """Get all customers for the order form."""
    connection = get_connection()

    if connection is None:
        return None

    cursor = None

    try:
        cursor = connection.cursor()
        cursor.execute(
            """
            SELECT CustomerID, FirstName, LastName
            FROM Customer
            ORDER BY CustomerID
            """
        )
        return cursor.fetchall()

    except Error as e:
        print(f"Error getting customers: {e}")
        return None

    finally:
        close_connection(connection, cursor)
