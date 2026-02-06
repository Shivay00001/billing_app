import sqlite3
import os
from contextlib import contextmanager

DB_DIR = os.path.join(os.path.dirname(__file__), 'data')
DB_PATH = os.path.join(DB_DIR, 'app.db')

def init_db():
    """
    Initializes the database.
    Creates the data directory if it doesn't exist.
    Creates tables if they don't exist.
    """
    if not os.path.exists(DB_DIR):
        os.makedirs(DB_DIR)
        print(f"Created directory: {DB_DIR}")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Enable Foreign Keys
    cursor.execute("PRAGMA foreign_keys = ON;")

    # Table: products
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            product_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            price REAL NOT NULL,
            category TEXT
        )
    ''')

    # Table: sales
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sales (
            bill_id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            total_amount REAL NOT NULL,
            payment_method TEXT NOT NULL
        )
    ''')

    # Table: sale_items
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sale_items (
            item_id INTEGER PRIMARY KEY AUTOINCREMENT,
            bill_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            price REAL NOT NULL,
            FOREIGN KEY (bill_id) REFERENCES sales (bill_id),
            FOREIGN KEY (product_id) REFERENCES products (product_id)
        )
    ''')
    
    # Optional: Customers (basic)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS customers (
            customer_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            phone TEXT
        )
    ''')

    conn.commit()
    conn.close()
    print(f"Database initialized at: {DB_PATH}")

@contextmanager
def get_db_connection():
    """
    Context manager for database connection.
    Ensures connection is closed properly.
    Yields a connection object.
    
    Usage:
    with get_db_connection() as conn:
        cursor = conn.cursor()
        ...
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row # Access columns by name
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON;")
    try:
        yield conn
    finally:
        conn.close()

if __name__ == "__main__":
    init_db()
