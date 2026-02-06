"""
Products View - Product/Service catalog management
"""

import tkinter as tk
from tkinter import ttk

from core.navigation import BaseView
from database.models import Product, ProductRepository


class ProductsView(BaseView):
    """Product/Service management view."""
    
    UNITS = ['NOS', 'PCS', 'KG', 'GM', 'LTR', 'ML', 'MTR', 'CM', 'SQM', 'HR', 'DAY', 'SET', 'BOX']
    GST_RATES = [0, 5, 12, 18, 28]
    
    def setup(self):
        """Setup the products UI."""
        self.product_repo = ProductRepository(self.db_manager)
        self.editing_product = None
        
        self.create_header("Products & Services", "Manage your product catalog")
        
        # Main container
        main = tk.Frame(self.frame, bg='#1E293B')
        main.pack(fill=tk.BOTH, expand=True, padx=30, pady=(0, 30))
        
        # Left: Product list
        left = tk.Frame(main, bg='#0F172A', width=500)
        left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 15))
        left.pack_propagate(False)
        
        self._build_product_list(left)
        
        # Right: Product form
        right = tk.Frame(main, bg='#0F172A', width=350)
        right.pack(side=tk.LEFT, fill=tk.BOTH)
        right.pack_propagate(False)
        
        self._build_product_form(right)
        
        self.refresh()
    
    def _build_product_list(self, parent):
        """Build product list."""
        # Search
        search_frame = tk.Frame(parent, bg='#0F172A', padx=15, pady=15)
        search_frame.pack(fill=tk.X)
        
        self.search_var = tk.StringVar()
        search = ttk.Entry(search_frame, textvariable=self.search_var, width=30)
        search.pack(side=tk.LEFT, fill=tk.X, expand=True)
        search.bind('<KeyRelease>', lambda e: self.refresh())
        
        tk.Button(search_frame, text="+ Add", font=('Segoe UI', 10, 'bold'), fg='#F8FAFC', bg='#6366F1', bd=0, padx=10, pady=5, cursor='hand2',
                  command=self._new_product).pack(side=tk.LEFT, padx=(10, 0))
        
        # List
        list_frame = tk.Frame(parent, bg='#0F172A')
        list_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 15))
        
        columns = ('name', 'hsn', 'rate', 'gst', 'type')
        self.tree = ttk.Treeview(list_frame, columns=columns, show='headings', selectmode='browse')
        
        self.tree.heading('name', text='Name')
        self.tree.heading('hsn', text='HSN/SAC')
        self.tree.heading('rate', text='Rate')
        self.tree.heading('gst', text='GST %')
        self.tree.heading('type', text='Type')
        
        self.tree.column('name', width=180)
        self.tree.column('hsn', width=80)
        self.tree.column('rate', width=80)
        self.tree.column('gst', width=60)
        self.tree.column('type', width=70)
        
        scrollbar = ttk.Scrollbar(list_frame, orient='vertical', command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.tree.bind('<<TreeviewSelect>>', self._on_select)
    
    def _build_product_form(self, parent):
        """Build product form."""
        form = tk.Frame(parent, bg='#0F172A', padx=20, pady=20)
        form.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(form, text="Product Details", font=('Segoe UI', 14, 'bold'), fg='#F8FAFC', bg='#0F172A').pack(anchor='w', pady=(0, 20))
        
        # Name
        tk.Label(form, text="Name *", font=('Segoe UI', 10), fg='#94A3B8', bg='#0F172A').pack(anchor='w')
        self.name_var = tk.StringVar()
        ttk.Entry(form, textvariable=self.name_var, width=30).pack(anchor='w', pady=(5, 15))
        
        # Type (Product/Service)
        tk.Label(form, text="Type", font=('Segoe UI', 10), fg='#94A3B8', bg='#0F172A').pack(anchor='w')
        self.is_service_var = tk.BooleanVar(value=False)
        type_frame = tk.Frame(form, bg='#0F172A')
        type_frame.pack(anchor='w', pady=(5, 15))
        tk.Radiobutton(type_frame, text="Product", variable=self.is_service_var, value=False, bg='#0F172A', fg='#F8FAFC', selectcolor='#1E293B').pack(side=tk.LEFT)
        tk.Radiobutton(type_frame, text="Service", variable=self.is_service_var, value=True, bg='#0F172A', fg='#F8FAFC', selectcolor='#1E293B').pack(side=tk.LEFT, padx=(10, 0))
        
        # HSN/SAC
        tk.Label(form, text="HSN/SAC Code", font=('Segoe UI', 10), fg='#94A3B8', bg='#0F172A').pack(anchor='w')
        self.hsn_var = tk.StringVar()
        ttk.Entry(form, textvariable=self.hsn_var, width=30).pack(anchor='w', pady=(5, 15))
        
        # Rate
        tk.Label(form, text="Rate (₹)", font=('Segoe UI', 10), fg='#94A3B8', bg='#0F172A').pack(anchor='w')
        self.rate_var = tk.StringVar(value='0')
        ttk.Entry(form, textvariable=self.rate_var, width=30).pack(anchor='w', pady=(5, 15))
        
        # Unit
        tk.Label(form, text="Unit", font=('Segoe UI', 10), fg='#94A3B8', bg='#0F172A').pack(anchor='w')
        self.unit_var = tk.StringVar(value='NOS')
        ttk.Combobox(form, textvariable=self.unit_var, values=self.UNITS, width=28, state='readonly').pack(anchor='w', pady=(5, 15))
        
        # GST Rate
        tk.Label(form, text="GST Rate (%)", font=('Segoe UI', 10), fg='#94A3B8', bg='#0F172A').pack(anchor='w')
        self.gst_var = tk.StringVar(value='18')
        ttk.Combobox(form, textvariable=self.gst_var, values=self.GST_RATES, width=28).pack(anchor='w', pady=(5, 15))
        
        # Description
        tk.Label(form, text="Description", font=('Segoe UI', 10), fg='#94A3B8', bg='#0F172A').pack(anchor='w')
        self.desc_text = tk.Text(form, height=3, width=30, bg='#1E293B', fg='#F8FAFC', insertbackground='#F8FAFC')
        self.desc_text.pack(anchor='w', pady=(5, 20))
        
        # Buttons
        btns = tk.Frame(form, bg='#0F172A')
        btns.pack(fill=tk.X)
        
        tk.Button(btns, text="Save", font=('Segoe UI', 10, 'bold'), fg='#F8FAFC', bg='#10B981', bd=0, padx=20, pady=8, cursor='hand2',
                  command=self._save_product).pack(side=tk.LEFT, padx=(0, 10))
        
        tk.Button(btns, text="Delete", font=('Segoe UI', 10), fg='#F8FAFC', bg='#EF4444', bd=0, padx=20, pady=8, cursor='hand2',
                  command=self._delete_product).pack(side=tk.LEFT, padx=(0, 10))
        
        tk.Button(btns, text="Clear", font=('Segoe UI', 10), fg='#F8FAFC', bg='#334155', bd=0, padx=20, pady=8, cursor='hand2',
                  command=self._clear_form).pack(side=tk.LEFT)
    
    def refresh(self):
        """Refresh product list."""
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        products = self.product_repo.get_all(search=self.search_var.get(), limit=500)
        
        for p in products:
            ptype = 'Service' if p.is_service else 'Product'
            self.tree.insert('', tk.END, values=(p.name, p.hsn_sac or '-', f"₹{p.rate:,.2f}", f"{p.gst_rate}%", ptype), tags=(p.id,))
    
    def _on_select(self, event):
        """Handle product selection."""
        selection = self.tree.selection()
        if not selection:
            return
        
        tags = self.tree.item(selection[0], 'tags')
        if tags:
            product = self.product_repo.get_by_id(int(tags[0]))
            if product:
                self.editing_product = product
                self.name_var.set(product.name)
                self.is_service_var.set(product.is_service)
                self.hsn_var.set(product.hsn_sac or '')
                self.rate_var.set(str(product.rate))
                self.unit_var.set(product.unit)
                self.gst_var.set(str(int(product.gst_rate)))
                
                self.desc_text.delete('1.0', tk.END)
                if product.description:
                    self.desc_text.insert('1.0', product.description)
    
    def _new_product(self):
        """Start new product."""
        self.editing_product = None
        self._clear_form()
    
    def _save_product(self):
        """Save product."""
        name = self.name_var.get().strip()
        if not name:
            self.show_error("Name is required")
            return
        
        product = self.editing_product or Product()
        product.name = name
        product.is_service = self.is_service_var.get()
        product.hsn_sac = self.hsn_var.get().strip()
        product.unit = self.unit_var.get()
        product.description = self.desc_text.get('1.0', tk.END).strip()
        
        try:
            product.rate = float(self.rate_var.get() or 0)
            product.gst_rate = float(self.gst_var.get() or 0)
        except ValueError:
            self.show_error("Invalid rate or GST value")
            return
        
        try:
            if product.id:
                self.product_repo.update(product)
            else:
                self.product_repo.create(product)
            
            self.show_success("Product saved!")
            self.refresh()
            self._clear_form()
        except Exception as e:
            self.show_error(f"Error: {str(e)}")
    
    def _delete_product(self):
        """Delete product."""
        if not self.editing_product:
            return
        
        if self.confirm(f"Delete product '{self.editing_product.name}'?"):
            self.product_repo.delete(self.editing_product.id)
            self.show_success("Product deleted")
            self.refresh()
            self._clear_form()
    
    def _clear_form(self):
        """Clear form."""
        self.editing_product = None
        self.name_var.set('')
        self.is_service_var.set(False)
        self.hsn_var.set('')
        self.rate_var.set('0')
        self.unit_var.set('NOS')
        self.gst_var.set('18')
        self.desc_text.delete('1.0', tk.END)
