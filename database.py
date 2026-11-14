
import mysql.connector
import os
from dotenv import load_dotenv
from mysql.connector import Error

load_dotenv()


def get_connection():
    """Create and return a connection to the MySQL database."""
    try:
        connection = mysql.connector.connect(
            host=os.getenv("MySQL_HOST"),
            user=os.getenv("MySQL_USER"),
            password=os.getenv("MySQL_PASSWORD"),
            database=os.getenv("MySQL_DATABASE")
        )
        if connection.is_connected():
            return connection

    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None
