import database
from datetime import datetime

def search_products(query):
    """
    Search for products by name or category.
    Returns a list of dictionaries.
    """
    with database.get_db_connection() as conn:
        cursor = conn.cursor()
        sql = "SELECT * FROM products WHERE name LIKE ? OR category LIKE ?"
        args = (f'%{query}%', f'%{query}%')
        cursor.execute(sql, args)
        rows = cursor.fetchall()
        return [dict(row) for row in rows]

def get_product_by_id(product_id):
    with database.get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM products WHERE product_id = ?", (product_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

def calculate_bill_total(cart_items, discount_percent=0, tax_percent=0):
    """
    cart_items: list of dicts {'product_id', 'price', 'quantity', ...}
    Returns dictionary with subtotal, discount_amount, tax_amount, grand_total
    """
    subtotal = sum(item['price'] * item['quantity'] for item in cart_items)
    
    discount_amount = (subtotal * discount_percent) / 100
    taxable_amount = subtotal - discount_amount
    tax_amount = (taxable_amount * tax_percent) / 100
    
    grand_total = taxable_amount + tax_amount
    
    return {
        'subtotal': round(subtotal, 2),
        'discount_amount': round(discount_amount, 2),
        'tax_amount': round(tax_amount, 2),
        'grand_total': round(grand_total, 2)
    }

def process_sale(cart_items, payment_method, discount_percent=0, tax_percent=0):
    """
    Commits the sale to database.
    cart_items: list of dicts containing product_id, price, quantity.
    """
    if not cart_items:
        raise ValueError("Cart is empty")

    totals = calculate_bill_total(cart_items, discount_percent, tax_percent)
    
    with database.get_db_connection() as conn:
        try:
            cursor = conn.cursor()
            
            # Create Sale Record
            cursor.execute('''
                INSERT INTO sales (total_amount, payment_method, date)
                VALUES (?, ?, ?)
            ''', (totals['grand_total'], payment_method, datetime.now()))
            
            bill_id = cursor.lastrowid
            
            # Insert Sale Items
            for item in cart_items:
                cursor.execute('''
                    INSERT INTO sale_items (bill_id, product_id, quantity, price)
                    VALUES (?, ?, ?, ?)
                ''', (bill_id, item['product_id'], item['quantity'], item['price']))
            
            conn.commit()
            return bill_id
        except Exception as e:
            conn.rollback()
            raise e
