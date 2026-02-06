import database

def get_total_earnings(start_date=None, end_date=None):
    """
    Returns total earnings within a date range.
    If dates are None, returns all-time total.
    """
    with database.get_db_connection() as conn:
        cursor = conn.cursor()
        if start_date and end_date:
            cursor.execute("SELECT SUM(total_amount) FROM sales WHERE date BETWEEN ? AND ?", (start_date, end_date))
        else:
            cursor.execute("SELECT SUM(total_amount) FROM sales")
        result = cursor.fetchone()[0]
        return result if result else 0.0

def get_sales_count(start_date=None, end_date=None):
    with database.get_db_connection() as conn:
        cursor = conn.cursor()
        if start_date and end_date:
            cursor.execute("SELECT COUNT(*) FROM sales WHERE date BETWEEN ? AND ?", (start_date, end_date))
        else:
            cursor.execute("SELECT COUNT(*) FROM sales")
        return cursor.fetchone()[0]

def get_payment_method_stats(start_date=None, end_date=None):
    """
    Returns list of (method, count) tuples.
    """
    with database.get_db_connection() as conn:
        cursor = conn.cursor()
        query = "SELECT payment_method, COUNT(*) as count FROM sales"
        params = []
        
        if start_date and end_date:
            query += " WHERE date BETWEEN ? AND ?"
            params.extend([start_date, end_date])
            
        query += " GROUP BY payment_method"
        cursor.execute(query, tuple(params))
        return cursor.fetchall()

def get_product_performance(limit=10, order='DESC'):
    """
    Returns top selling items (quantity based).
    Order: DESC for best selling, ASC for low selling.
    Analytics must be receipt-based (using sale_items).
    """
    with database.get_db_connection() as conn:
        cursor = conn.cursor()
        # Join sale_items with products to get names
        # Group by product_id and sum quantity
        sql = f'''
            SELECT p.name, SUM(si.quantity) as total_qty
            FROM sale_items si
            JOIN products p ON si.product_id = p.product_id
            GROUP BY si.product_id
            ORDER BY total_qty {order}
            LIMIT ?
        '''
        cursor.execute(sql, (limit,))
        return cursor.fetchall()
