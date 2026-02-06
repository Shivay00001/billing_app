import database
import billing
import reports
import exporter
import os
import shutil

def verify_system():
    print("Verifying System...")
    
    # 1. DB Init
    database.init_db()
    
    # 2. Add Product
    print("Adding test product...")
    with database.get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO products (name, price, category) VALUES (?, ?, ?)", 
                      ("Test Item", 100.0, "Test"))
        pid = cursor.lastrowid
        conn.commit()
    
    # 3. Create Sale
    print("Creating test sale...")
    cart = [{'product_id': pid, 'name': 'Test Item', 'price': 100.0, 'quantity': 2}]
    bill_id = billing.process_sale(cart, "Cash")
    print(f"Sale created. Bill ID: {bill_id}")
    
    # 4. Check Reports
    earnings = reports.get_total_earnings()
    print(f"Total Earnings: {earnings}")
    assert earnings >= 200.0
    
    # 5. Export
    print("Testing Export...")
    from datetime import datetime
    now = datetime.now()
    path = exporter.export_monthly_data(now.year, now.month)
    print(f"Exported to: {path}")
    assert os.path.exists(os.path.join(path, "sales.csv"))
    
    print("verification_complete")

if __name__ == "__main__":
    try:
        verify_system()
    except Exception as e:
        print(f"Verification Failed: {e}")
        exit(1)
