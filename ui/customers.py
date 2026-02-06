"""
Customers View - Customer management
"""

import tkinter as tk
from tkinter import ttk, messagebox

from core.navigation import BaseView
from database.models import Customer, CustomerRepository


class CustomersView(BaseView):
    """Customer management view."""
    
    INDIAN_STATES = [
        ('01', 'Jammu & Kashmir'), ('02', 'Himachal Pradesh'), ('03', 'Punjab'),
        ('04', 'Chandigarh'), ('05', 'Uttarakhand'), ('06', 'Haryana'),
        ('07', 'Delhi'), ('08', 'Rajasthan'), ('09', 'Uttar Pradesh'),
        ('10', 'Bihar'), ('11', 'Sikkim'), ('12', 'Arunachal Pradesh'),
        ('13', 'Nagaland'), ('14', 'Manipur'), ('15', 'Mizoram'),
        ('16', 'Tripura'), ('17', 'Meghalaya'), ('18', 'Assam'),
        ('19', 'West Bengal'), ('20', 'Jharkhand'), ('21', 'Odisha'),
        ('22', 'Chhattisgarh'), ('23', 'Madhya Pradesh'), ('24', 'Gujarat'),
        ('27', 'Maharashtra'), ('29', 'Karnataka'), ('32', 'Kerala'),
        ('33', 'Tamil Nadu'), ('36', 'Telangana'), ('37', 'Andhra Pradesh'),
    ]
    
    def setup(self):
        """Setup the customers UI."""
        self.customer_repo = CustomerRepository(self.db_manager)
        self.editing_customer = None
        
        self.create_header("Customers", "Manage your customers")
        
        # Main container
        main = tk.Frame(self.frame, bg='#1E293B')
        main.pack(fill=tk.BOTH, expand=True, padx=30, pady=(0, 30))
        
        # Left: Customer list
        left = tk.Frame(main, bg='#0F172A', width=400)
        left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 15))
        left.pack_propagate(False)
        
        self._build_customer_list(left)
        
        # Right: Customer form
        right = tk.Frame(main, bg='#0F172A', width=400)
        right.pack(side=tk.LEFT, fill=tk.BOTH)
        right.pack_propagate(False)
        
        self._build_customer_form(right)
        
        self.refresh()
    
    def _build_customer_list(self, parent):
        """Build customer list."""
        # Search
        search_frame = tk.Frame(parent, bg='#0F172A', padx=15, pady=15)
        search_frame.pack(fill=tk.X)
        
        self.search_var = tk.StringVar()
        search = ttk.Entry(search_frame, textvariable=self.search_var, width=30)
        search.pack(side=tk.LEFT, fill=tk.X, expand=True)
        search.bind('<KeyRelease>', lambda e: self.refresh())
        
        tk.Button(search_frame, text="+ Add", font=('Segoe UI', 10, 'bold'), fg='#F8FAFC', bg='#6366F1', bd=0, padx=10, pady=5, cursor='hand2',
                  command=self._new_customer).pack(side=tk.LEFT, padx=(10, 0))
        
        # List
        list_frame = tk.Frame(parent, bg='#0F172A')
        list_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 15))
        
        columns = ('name', 'gstin', 'phone')
        self.tree = ttk.Treeview(list_frame, columns=columns, show='headings', selectmode='browse')
        
        self.tree.heading('name', text='Name')
        self.tree.heading('gstin', text='GSTIN')
        self.tree.heading('phone', text='Phone')
        
        self.tree.column('name', width=150)
        self.tree.column('gstin', width=120)
        self.tree.column('phone', width=100)
        
        scrollbar = ttk.Scrollbar(list_frame, orient='vertical', command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.tree.bind('<<TreeviewSelect>>', self._on_select)
    
    def _build_customer_form(self, parent):
        """Build customer form."""
        form = tk.Frame(parent, bg='#0F172A', padx=20, pady=20)
        form.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(form, text="Customer Details", font=('Segoe UI', 14, 'bold'), fg='#F8FAFC', bg='#0F172A').pack(anchor='w', pady=(0, 20))
        
        # Name
        tk.Label(form, text="Name *", font=('Segoe UI', 10), fg='#94A3B8', bg='#0F172A').pack(anchor='w')
        self.name_var = tk.StringVar()
        ttk.Entry(form, textvariable=self.name_var, width=35).pack(anchor='w', pady=(5, 15))
        
        # GSTIN
        tk.Label(form, text="GSTIN", font=('Segoe UI', 10), fg='#94A3B8', bg='#0F172A').pack(anchor='w')
        self.gstin_var = tk.StringVar()
        ttk.Entry(form, textvariable=self.gstin_var, width=35).pack(anchor='w', pady=(5, 15))
        
        # Phone
        tk.Label(form, text="Phone", font=('Segoe UI', 10), fg='#94A3B8', bg='#0F172A').pack(anchor='w')
        self.phone_var = tk.StringVar()
        ttk.Entry(form, textvariable=self.phone_var, width=35).pack(anchor='w', pady=(5, 15))
        
        # Email
        tk.Label(form, text="Email", font=('Segoe UI', 10), fg='#94A3B8', bg='#0F172A').pack(anchor='w')
        self.email_var = tk.StringVar()
        ttk.Entry(form, textvariable=self.email_var, width=35).pack(anchor='w', pady=(5, 15))
        
        # State
        tk.Label(form, text="State", font=('Segoe UI', 10), fg='#94A3B8', bg='#0F172A').pack(anchor='w')
        self.state_var = tk.StringVar()
        state_values = [f"{code} - {name}" for code, name in self.INDIAN_STATES]
        self.state_combo = ttk.Combobox(form, textvariable=self.state_var, values=state_values, width=33)
        self.state_combo.pack(anchor='w', pady=(5, 15))
        
        # Address
        tk.Label(form, text="Address", font=('Segoe UI', 10), fg='#94A3B8', bg='#0F172A').pack(anchor='w')
        self.address_text = tk.Text(form, height=3, width=35, bg='#1E293B', fg='#F8FAFC', insertbackground='#F8FAFC')
        self.address_text.pack(anchor='w', pady=(5, 20))
        
        # Buttons
        btns = tk.Frame(form, bg='#0F172A')
        btns.pack(fill=tk.X)
        
        tk.Button(btns, text="Save", font=('Segoe UI', 10, 'bold'), fg='#F8FAFC', bg='#10B981', bd=0, padx=20, pady=8, cursor='hand2',
                  command=self._save_customer).pack(side=tk.LEFT, padx=(0, 10))
        
        tk.Button(btns, text="Delete", font=('Segoe UI', 10), fg='#F8FAFC', bg='#EF4444', bd=0, padx=20, pady=8, cursor='hand2',
                  command=self._delete_customer).pack(side=tk.LEFT, padx=(0, 10))
        
        tk.Button(btns, text="Clear", font=('Segoe UI', 10), fg='#F8FAFC', bg='#334155', bd=0, padx=20, pady=8, cursor='hand2',
                  command=self._clear_form).pack(side=tk.LEFT)
    
    def refresh(self):
        """Refresh customer list."""
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        customers = self.customer_repo.get_all(search=self.search_var.get(), limit=500)
        
        for c in customers:
            self.tree.insert('', tk.END, values=(c.name, c.gstin or '-', c.phone or '-'), tags=(c.id,))
    
    def _on_select(self, event):
        """Handle customer selection."""
        selection = self.tree.selection()
        if not selection:
            return
        
        tags = self.tree.item(selection[0], 'tags')
        if tags:
            customer = self.customer_repo.get_by_id(int(tags[0]))
            if customer:
                self.editing_customer = customer
                self.name_var.set(customer.name)
                self.gstin_var.set(customer.gstin or '')
                self.phone_var.set(customer.phone or '')
                self.email_var.set(customer.email or '')
                
                if customer.state_code and customer.state:
                    self.state_var.set(f"{customer.state_code} - {customer.state}")
                else:
                    self.state_var.set('')
                
                self.address_text.delete('1.0', tk.END)
                if customer.address:
                    self.address_text.insert('1.0', customer.address)
    
    def _new_customer(self):
        """Start new customer."""
        self.editing_customer = None
        self._clear_form()
    
    def _save_customer(self):
        """Save customer."""
        name = self.name_var.get().strip()
        if not name:
            self.show_error("Name is required")
            return
        
        customer = self.editing_customer or Customer()
        customer.name = name
        customer.gstin = self.gstin_var.get().strip()
        customer.phone = self.phone_var.get().strip()
        customer.email = self.email_var.get().strip()
        customer.address = self.address_text.get('1.0', tk.END).strip()
        
        state_val = self.state_var.get()
        if state_val and ' - ' in state_val:
            customer.state_code, customer.state = state_val.split(' - ', 1)
        
        try:
            if customer.id:
                self.customer_repo.update(customer)
            else:
                self.customer_repo.create(customer)
            
            self.show_success("Customer saved!")
            self.refresh()
            self._clear_form()
        except Exception as e:
            self.show_error(f"Error: {str(e)}")
    
    def _delete_customer(self):
        """Delete customer."""
        if not self.editing_customer:
            return
        
        if self.confirm(f"Delete customer '{self.editing_customer.name}'?"):
            self.customer_repo.delete(self.editing_customer.id)
            self.show_success("Customer deleted")
            self.refresh()
            self._clear_form()
    
    def _clear_form(self):
        """Clear form."""
        self.editing_customer = None
        self.name_var.set('')
        self.gstin_var.set('')
        self.phone_var.set('')
        self.email_var.set('')
        self.state_var.set('')
        self.address_text.delete('1.0', tk.END)
