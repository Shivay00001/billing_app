import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.toast import ToastNotification
from tkinter import messagebox
import database
import billing
import printer
import exporter
from ui.dashboard import DashboardFrame

class BillingApp(ttk.Window):
    def __init__(self):
        super().__init__(themename="cosmo")
        self.title("Billing & Inventory System")
        self.geometry("1100x700")
        
        # Initialize Database
        database.init_db()
        
        # Set App Icon
        try:
            import os
            icon_path = os.path.join(os.path.dirname(__file__), 'assets', 'icon.ico')
            if os.path.exists(icon_path):
                self.iconbitmap(icon_path)
        except Exception as e:
            print(f"Failed to set icon: {e}")
        
        # Notebook for Tabs
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=BOTH, expand=YES, pady=10)
        
        # TABS
        self.setup_billing_tab()
        self.setup_products_tab()
        self.dashboard_tab = DashboardFrame(self.notebook)
        self.notebook.add(self.dashboard_tab, text="Dashboard")
        
        # Check Reminders
        self.check_reminders()
        
    def setup_billing_tab(self):
        self.billing_frame = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(self.billing_frame, text="Billing")
        
        # Layout: Left (Product Search & List), Right (Cart & Pay)
        
        # --- LEFT PANEL ---
        left_panel = ttk.Frame(self.billing_frame)
        left_panel.pack(side=LEFT, fill=BOTH, expand=YES, padx=(0, 10))
        
        # Search Box
        search_frame = ttk.Labelframe(left_panel, text="Product Search", padding=10)
        search_frame.pack(fill=X, pady=(0, 10))
        
        self.search_var = ttk.StringVar()
        entry_search = ttk.Entry(search_frame, textvariable=self.search_var)
        entry_search.pack(side=LEFT, fill=X, expand=YES, padx=(0, 5))
        entry_search.bind("<Return>", self.perform_search)
        
        btn_search = ttk.Button(search_frame, text="Search", command=self.perform_search, bootstyle=INFO)
        btn_search.pack(side=LEFT)
        
        # Product List (Treeview)
        list_frame = ttk.Labelframe(left_panel, text="Products (Double-click to Add)", padding=10)
        list_frame.pack(fill=BOTH, expand=YES)
        
        self.product_tree = ttk.Treeview(list_frame, columns=("ID", "Name", "Price", "Category"), show="headings", selectmode="browse")
        self.product_tree.heading("ID", text="ID")
        self.product_tree.heading("Name", text="Name")
        self.product_tree.heading("Price", text="Price")
        self.product_tree.heading("Category", text="Category")
        self.product_tree.column("ID", width=50)
        self.product_tree.pack(fill=BOTH, expand=YES)
        self.product_tree.bind("<Double-1>", self.add_to_cart_event)
        
        # --- RIGHT PANEL ---
        right_panel = ttk.Frame(self.billing_frame)
        right_panel.pack(side=RIGHT, fill=BOTH, expand=YES)
        
        # Cart
        cart_frame = ttk.Labelframe(right_panel, text="Current Bill", padding=10)
        cart_frame.pack(fill=BOTH, expand=YES, pady=(0, 10))
        
        self.cart_tree = ttk.Treeview(cart_frame, columns=("ProdID", "Name", "Qty", "Price", "Total"), show="headings")
        self.cart_tree.heading("ProdID", text="ID")
        self.cart_tree.heading("Name", text="Name")
        self.cart_tree.heading("Qty", text="Qty")
        self.cart_tree.heading("Price", text="Price")
        self.cart_tree.heading("Total", text="Total")
        self.cart_tree.column("ProdID", width=40)
        self.cart_tree.column("Qty", width=40)
        self.cart_tree.pack(fill=BOTH, expand=YES)
        
        btn_remove = ttk.Button(cart_frame, text="Remove Selected", command=self.remove_from_cart, bootstyle=DANGER)
        btn_remove.pack(fill=X, pady=5)
        
        # Calculations
        calc_frame = ttk.Labelframe(right_panel, text="Payment", padding=10)
        calc_frame.pack(fill=X)
        
        self.lbl_total = ttk.Label(calc_frame, text="Total: $0.00", font=("Helvetica", 14, "bold"))
        self.lbl_total.pack(anchor=E, pady=5)
        
        # Payment Method
        self.pay_method_var = ttk.StringVar(value="Cash")
        cb_pay = ttk.Combobox(calc_frame, textvariable=self.pay_method_var, values=["Cash", "Card", "UPI"], state="readonly")
        cb_pay.pack(fill=X, pady=5)
        
        btn_checkout = ttk.Button(calc_frame, text="Checkout & Print", command=self.checkout, bootstyle=SUCCESS)
        btn_checkout.pack(fill=X, pady=10)
        
        # State
        self.cart_items = [] # list of dicts: product_id, name, price, quantity
    
    def setup_products_tab(self):
        self.prod_frame = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(self.prod_frame, text="Product Management")
        
        # Add Product Form
        form_frame = ttk.Labelframe(self.prod_frame, text="Add New Product", padding=10)
        form_frame.pack(fill=X, pady=10)
        
        self.prod_name_var = ttk.StringVar()
        self.prod_price_var = ttk.DoubleVar()
        self.prod_cat_var = ttk.StringVar()
        
        ttk.Label(form_frame, text="Name:").pack(side=LEFT, padx=5)
        ttk.Entry(form_frame, textvariable=self.prod_name_var).pack(side=LEFT, padx=5, fill=X, expand=YES)
        
        ttk.Label(form_frame, text="Price:").pack(side=LEFT, padx=5)
        ttk.Entry(form_frame, textvariable=self.prod_price_var, width=10).pack(side=LEFT, padx=5)
        
        ttk.Label(form_frame, text="Category:").pack(side=LEFT, padx=5)
        ttk.Entry(form_frame, textvariable=self.prod_cat_var, width=15).pack(side=LEFT, padx=5)
        
        ttk.Button(form_frame, text="Add Product", command=self.add_product, bootstyle=SUCCESS).pack(side=LEFT, padx=10)
        
    def perform_search(self, event=None):
        query = self.search_var.get()
        results = billing.search_products(query)
        
        # Clear tree
        for i in self.product_tree.get_children():
            self.product_tree.delete(i)
            
        for p in results:
            self.product_tree.insert("", END, values=(p['product_id'], p['name'], p['price'], p['category']))
            
    def add_to_cart_event(self, event):
        selected_item = self.product_tree.focus()
        if not selected_item: return
        values = self.product_tree.item(selected_item, 'values')
        # values: (ID, Name, Price, Category)
        
        pid, name, price, _ = values
        price = float(price)
        pid = int(pid)
        
        # Check if already in cart
        found = False
        for item in self.cart_items:
            if item['product_id'] == pid:
                item['quantity'] += 1
                found = True
                break
        
        if not found:
            self.cart_items.append({
                'product_id': pid,
                'name': name,
                'price': price,
                'quantity': 1
            })
            
        self.update_cart_ui()
        
    def update_cart_ui(self):
        for i in self.cart_tree.get_children():
            self.cart_tree.delete(i)
            
        total = 0
        for item in self.cart_items:
            line_total = item['quantity'] * item['price']
            total += line_total
            self.cart_tree.insert("", END, values=(
                item['product_id'],
                item['name'],
                item['quantity'],
                item['price'],
                f"{line_total:.2f}"
            ))
            
        self.lbl_total.config(text=f"Total: ${total:.2f}")
        
    def remove_from_cart(self):
        selected = self.cart_tree.focus()
        if not selected: return
        # Logic to remove item
        # Simplified: just clear cart for now or remove index
        # To match properly, we find the item ID
        values = self.cart_tree.item(selected, 'values')
        pid = int(values[0])
        
        self.cart_items = [i for i in self.cart_items if i['product_id'] != pid]
        self.update_cart_ui()

    def checkout(self):
        if not self.cart_items:
            messagebox.showwarning("Empty Cart", "Please add items to cart")
            return
            
        try:
            pay_method = self.pay_method_var.get()
            
            # 1. Commit Sale
            bill_id = billing.process_sale(self.cart_items, pay_method)
            
            # 2. Print Receipt
            totals = billing.calculate_bill_total(self.cart_items)
            receipt_text = printer.generate_receipt_text(
                "My Shop", 
                 bill_id, 
                 "Today", 
                 self.cart_items, 
                 totals
            )
            filepath = printer.print_receipt(receipt_text)
            
            # Success
            messagebox.showinfo("Success", f"Bill #{bill_id} Saved!\nReceipt saved to: {filepath}")
            
            self.cart_items = []
            self.update_cart_ui()
            
            # Refresh Dashboard if open
            # self.dashboard_tab.refresh_data() 
            
        except Exception as e:
            messagebox.showerror("Error", f"Transaction Failed: {e}")

    def add_product(self):
        name = self.prod_name_var.get()
        price = self.prod_price_var.get()
        cat = self.prod_cat_var.get()
        
        if not name or price <= 0:
            messagebox.showerror("Error", "Invalid Input")
            return
            
        with database.get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO products (name, price, category) VALUES (?, ?, ?)", 
                          (name, price, cat))
            conn.commit()
            
        ToastNotification(
            title="Success",
            message=f"Added {name}",
            duration=3000,
        ).show_toast()
        
        self.prod_name_var.set("")
        self.prod_price_var.set(0.0)
        self.perform_search() # Refresh list

    def check_reminders(self):
        if exporter.check_monthly_reminder():
            ans = messagebox.askyesno("Monthly Export", "It looks like you haven't exported last month's data.\nDo you want to export now?")
            if ans:
                # Assuming current date logic for 'last month'
                from datetime import datetime, timedelta
                last_month = datetime.now().replace(day=1) - timedelta(days=1)
                year = last_month.year
                month = last_month.month
                
                path = exporter.export_monthly_data(year, month)
                messagebox.showinfo("Exported", f"Data exported to {path}")

if __name__ == "__main__":
    app = BillingApp()
    app.mainloop()
