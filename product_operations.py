from mysql.connector import Error, IntegrityError

from database import get_connection


def close_connection(connection, cursor=None):
    """Created a safely closing cursor and connection function"""
    if cursor is not None:
        cursor.close()
    if connection is not None:
        connection.close()


def get_all_products():
    """Getting all the products from the database"""
    connection = get_connection()
    if connection is None:
        return [], "Database connection Failed"

    cursor = None

    try:
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM Product")
        products = cursor.fetchall()
        return products

    finally:
        close_connection(connection, cursor)


def search_products(keyword):
    """Search products by name or category"""
    connection = get_connection()
    if connection is None:
        return [], "Database connection Failed"

    cursor = None

    try:
        cursor = connection.cursor()

        query = """
            SELECT ProductID, Name, Category, Price, StockQuantity
            FROM Product
            WHERE Name LIKE %s OR Category LIKE %s
        """

        value = f"%{keyword}%"
        cursor.execute(query, (value, value))
        products = cursor.fetchall()
        return products
    finally:
        close_connection(connection, cursor)


def get_product_by_id(product_id):
    """"Getting only one product by ID"""
    connection = get_connection()
    if connection is None:
        return None, "Database connection Failed"

    cursor = None

    try:
        cursor = connection.cursor()

        cursor.execute(
            "SELECT * FROM Product WHERE ProductID = %s",
            (product_id,)
        )
        product = cursor.fetchone()
        return product

    finally:
        close_connection(connection, cursor)


def add_products(name, category, price, stock):
    """Adding a new product"""
    connection = get_connection()
    if connection is None:
        return False, "Database connection Failed"

    cursor = None
    clean_name = name.strip()
    clean_category = category.strip()

    try:
        cursor = connection.cursor()

        cursor.execute("SELECT ProductID FROM Product WHERE LOWER(Name) =LOWER(%s)",
                       (clean_name,))
        existing = cursor.fetchone()

        if existing:
            print("Product already exists.")
            return False

        sql = """
            INSERT INTO Product (Name, Category, Price, StockQuantity)
            VALUES (%s, %s, %s, %s)
        """  # Insert when product does not exist

        cursor.execute(sql, (clean_name, clean_category, price, stock))
        connection.commit()

        return True

    except Error as e:
        print(f"Error adding product: {e}")
        return False

    finally:
        close_connection(connection, cursor)


def delete_products(product_id):
    """Delete a product by ProductID"""
    connection = get_connection()
    if connection is None:
        return False, "Database connection Failed"

    cursor = None

    try:
        cursor = connection.cursor()

        cursor.execute(
            "DELETE FROM Product WHERE ProductID = %s",
            (product_id,)
        )

        connection.commit()
        if cursor.rowcount > 0:
            return True, "Product deleted successfully"
        return False, "Product not found."

    except IntegrityError as e:
        connection.rollback()
        if e.errno == 1451:
            return False, "Cannot delete this product because it is already part of customer order."
        return False, f"Database integrity error: {e.msg}"
    except Error as e:
        connection.rollback()
        return False, f"Database error: {e.msg}"

    finally:
        close_connection(connection, cursor)
