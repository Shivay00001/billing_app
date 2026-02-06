import csv
import os
import database
from datetime import datetime, timedelta

EXPORTS_DIR = os.path.join(os.path.dirname(__file__), 'exports')

def check_monthly_reminder():
    """
    Checks if an export has been done for the previous month.
    Returns True if reminder is needed (>30 days since last export or prev month not exported).
    To simplify: Check if the folder for last month exists.
    """
    # Simple logic: Check if previous month's export folder exists
    today = datetime.now()
    # First day of this month
    first = today.replace(day=1)
    # Last month object
    last_month = first - timedelta(days=1)
    
    folder_name = last_month.strftime("%Y_%m")
    export_path = os.path.join(EXPORTS_DIR, folder_name)
    
    # If folder exists, we assume export was done.
    # If not, we show reminder.
    return not os.path.exists(export_path)

def export_monthly_data(year, month):
    """
    Exports data for the given year and month (int).
    Creates exports/YYYY_MM/ with CSVs.
    """
    folder_name = f"{year}_{month:02d}"
    export_path = os.path.join(EXPORTS_DIR, folder_name)
    
    if not os.path.exists(export_path):
        os.makedirs(export_path)
        
    start_date = f"{year}-{month:02d}-01"
    # End date calculation is tricky, easiest: like 'YYYY-MM-32' logic or simple string match
    # Better: Use SQL strftime
    
    with database.get_db_connection() as conn:
        cursor = conn.cursor()
        
        # 1. Export Sales
        cursor.execute("SELECT * FROM sales WHERE strftime('%Y-%m', date) = ?", (f"{year}-{month:02d}",))
        sales = cursor.fetchall()
        write_csv(sales, os.path.join(export_path, 'sales.csv'), cursor.description)
        
        # 2. Export Sale Items (Joined with Date to filter)
        cursor.execute('''
            SELECT si.* 
            FROM sale_items si
            JOIN sales s ON si.bill_id = s.bill_id
            WHERE strftime('%Y-%m', s.date) = ?
        ''', (f"{year}-{month:02d}",))
        items = cursor.fetchall()
        write_csv(items, os.path.join(export_path, 'sale_items.csv'), cursor.description)
        
        # 3. Products Snapshot
        cursor.execute("SELECT * FROM products")
        products = cursor.fetchall()
        write_csv(products, os.path.join(export_path, 'products_snapshot.csv'), cursor.description)
        
        # 4. Summary
        # Just writing a simple summary text or csv
        # Total Sales, Total items
        total_sales = sum(row['total_amount'] for row in sales)
        summary_data = [{'Metric': 'Total Revenue', 'Value': total_sales}, {'Metric': 'Total Bills', 'Value': len(sales)}]
        write_csv_dict(summary_data, os.path.join(export_path, 'summary.csv'), ['Metric', 'Value'])
        
    return export_path

def write_csv(rows, filename, description):
    """Helper to write sqlite3.Row objects to CSV"""
    if not rows:
        # Create empty file with headers
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            if description:
                headers = [d[0] for d in description]
                writer.writerow(headers)
        return

    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        # Headers
        headers = list(rows[0].keys())
        writer.writerow(headers)
        # Data
        for row in rows:
            writer.writerow(list(row))

def write_csv_dict(data, filename, fieldnames):
    """Helper for dict lists"""
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)
