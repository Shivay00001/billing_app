"""
Billing View - Invoice creation and editing
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date, datetime
from typing import Optional, List

from core.navigation import BaseView
from database.models import Invoice, InvoiceItem, Customer, Product
from database.models import InvoiceRepository, CustomerRepository, ProductRepository


class BillingView(BaseView):
    """Invoice creation and editing view."""
    
    INVOICE_TYPES = ['GST', 'NON_GST', 'ESTIMATE', 'PROFORMA']
    UNITS = ['NOS', 'PCS', 'KG', 'GM', 'LTR', 'ML', 'MTR', 'CM', 'SQM', 'HR', 'DAY']
    GST_RATES = [0, 5, 12, 18, 28]
    
    def __init__(self, frame, db_manager, license_manager, nav_manager):
        super().__init__(frame, db_manager, license_manager, nav_manager)
        self.invoice_repo = InvoiceRepository(db_manager)
        self.customer_repo = CustomerRepository(db_manager)
        self.product_repo = ProductRepository(db_manager)
        
        self.current_invoice: Optional[Invoice] = None
        self.items: List[InvoiceItem] = []
        self.item_widgets = []
    
    def setup(self):
        """Setup the billing form."""
        # Check if can create invoice
        can_create, message = self.license_manager.can_create_invoice()
        if not can_create:
            self._show_limit_reached(message)
            return
        
        self.create_header("New Invoice", "Create a new invoice")
        
        # Main container with scroll
        self.main_canvas = tk.Canvas(self.frame, bg='#1E293B', highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self.frame, orient='vertical', command=self.main_canvas.yview)
        self.scroll_frame = tk.Frame(self.main_canvas, bg='#1E293B')
        
        self.scroll_frame.bind("<Configure>", lambda e: self.main_canvas.configure(scrollregion=self.main_canvas.bbox("all")))
        self.main_canvas.create_window((0, 0), window=self.scroll_frame, anchor="nw")
        self.main_canvas.configure(yscrollcommand=self.scrollbar.set)
        
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.main_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=30, pady=(0, 20))
        
        self.main_canvas.bind_all("<MouseWheel>", lambda e: self.main_canvas.yview_scroll(int(-1*(e.delta/120)), "units"))
        
        # Build form sections
        self._build_invoice_header()
        self._build_customer_section()
        self._build_items_section()
        self._build_totals_section()
        self._build_action_buttons()
        
        # Initialize new invoice
        self._init_new_invoice()
    
    def _show_limit_reached(self, message: str):
        """Show limit reached message."""
        frame = tk.Frame(self.frame, bg='#1E293B')
        frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=30)
        
        tk.Label(frame, text="⚠️", font=('Segoe UI', 48), fg='#F59E0B', bg='#1E293B').pack(pady=(50, 20))
        tk.Label(frame, text="Invoice Limit Reached", font=('Segoe UI', 18, 'bold'), fg='#F8FAFC', bg='#1E293B').pack()
        tk.Label(frame, text=message, font=('Segoe UI', 11), fg='#94A3B8', bg='#1E293B').pack(pady=(10, 30))
        
        tk.Button(
            frame, text="Upgrade Now", font=('Segoe UI', 11, 'bold'),
            fg='#F8FAFC', bg='#6366F1', bd=0, padx=20, pady=10, cursor='hand2',
            command=lambda: self.nav_manager.navigate('settings')
        ).pack()
    
    def _build_invoice_header(self):
        """Build invoice header section."""
        header = tk.Frame(self.scroll_frame, bg='#0F172A', padx=20, pady=20)
        header.pack(fill=tk.X, pady=(20, 15))
        
        row = tk.Frame(header, bg='#0F172A')
        row.pack(fill=tk.X)
        
        # Invoice Type
        type_frame = tk.Frame(row, bg='#0F172A')
        type_frame.pack(side=tk.LEFT, padx=(0, 20))
        tk.Label(type_frame, text="Invoice Type", font=('Segoe UI', 10), fg='#94A3B8', bg='#0F172A').pack(anchor='w')
        self.type_var = tk.StringVar(value='GST')
        self.type_combo = ttk.Combobox(type_frame, textvariable=self.type_var, values=self.INVOICE_TYPES, state='readonly', width=15)
        self.type_combo.pack(pady=(5, 0))
        self.type_combo.bind('<<ComboboxSelected>>', self._on_type_change)
        
        # Invoice Number
        num_frame = tk.Frame(row, bg='#0F172A')
        num_frame.pack(side=tk.LEFT, padx=(0, 20))
        tk.Label(num_frame, text="Invoice Number", font=('Segoe UI', 10), fg='#94A3B8', bg='#0F172A').pack(anchor='w')
        self.inv_number_var = tk.StringVar()
        self.inv_number_entry = ttk.Entry(num_frame, textvariable=self.inv_number_var, width=18)
        self.inv_number_entry.pack(pady=(5, 0))
        
        # Date
        date_frame = tk.Frame(row, bg='#0F172A')
        date_frame.pack(side=tk.LEFT, padx=(0, 20))
        tk.Label(date_frame, text="Date", font=('Segoe UI', 10), fg='#94A3B8', bg='#0F172A').pack(anchor='w')
        self.date_var = tk.StringVar(value=date.today().strftime('%d/%m/%Y'))
        self.date_entry = ttk.Entry(date_frame, textvariable=self.date_var, width=12)
        self.date_entry.pack(pady=(5, 0))
        
        # Due Date
        due_frame = tk.Frame(row, bg='#0F172A')
        due_frame.pack(side=tk.LEFT)
        tk.Label(due_frame, text="Due Date", font=('Segoe UI', 10), fg='#94A3B8', bg='#0F172A').pack(anchor='w')
        self.due_date_var = tk.StringVar()
        self.due_date_entry = ttk.Entry(due_frame, textvariable=self.due_date_var, width=12)
        self.due_date_entry.pack(pady=(5, 0))
    
    def _build_customer_section(self):
        """Build customer selection section."""
        section = tk.Frame(self.scroll_frame, bg='#0F172A', padx=20, pady=20)
        section.pack(fill=tk.X, pady=(0, 15))
        
        header = tk.Frame(section, bg='#0F172A')
        header.pack(fill=tk.X, pady=(0, 15))
        tk.Label(header, text="Customer Details", font=('Segoe UI', 12, 'bold'), fg='#F8FAFC', bg='#0F172A').pack(side=tk.LEFT)
        tk.Button(header, text="+ Add New", font=('Segoe UI', 9), fg='#6366F1', bg='#0F172A', bd=0, cursor='hand2',
                  command=self._show_add_customer).pack(side=tk.RIGHT)
        
        # Customer search
        search_frame = tk.Frame(section, bg='#0F172A')
        search_frame.pack(fill=tk.X, pady=(0, 10))
        tk.Label(search_frame, text="Search Customer", font=('Segoe UI', 10), fg='#94A3B8', bg='#0F172A').pack(anchor='w')
        self.customer_var = tk.StringVar()
        self.customer_combo = ttk.Combobox(search_frame, textvariable=self.customer_var, width=40)
        self.customer_combo.pack(anchor='w', pady=(5, 0))
        self.customer_combo.bind('<KeyRelease>', self._search_customers)
        self.customer_combo.bind('<<ComboboxSelected>>', self._on_customer_select)
        
        # Customer details display
        details = tk.Frame(section, bg='#0F172A')
        details.pack(fill=tk.X)
        
        row1 = tk.Frame(details, bg='#0F172A')
        row1.pack(fill=tk.X, pady=(5, 0))
        
        # Name
        name_f = tk.Frame(row1, bg='#0F172A')
        name_f.pack(side=tk.LEFT, padx=(0, 20))
        tk.Label(name_f, text="Name", font=('Segoe UI', 10), fg='#94A3B8', bg='#0F172A').pack(anchor='w')
        self.cust_name_var = tk.StringVar()
        ttk.Entry(name_f, textvariable=self.cust_name_var, width=25).pack(pady=(5, 0))
        
        # GSTIN
        gstin_f = tk.Frame(row1, bg='#0F172A')
        gstin_f.pack(side=tk.LEFT, padx=(0, 20))
        tk.Label(gstin_f, text="GSTIN", font=('Segoe UI', 10), fg='#94A3B8', bg='#0F172A').pack(anchor='w')
        self.cust_gstin_var = tk.StringVar()
        ttk.Entry(gstin_f, textvariable=self.cust_gstin_var, width=20).pack(pady=(5, 0))
        
        # State
        state_f = tk.Frame(row1, bg='#0F172A')
        state_f.pack(side=tk.LEFT)
        tk.Label(state_f, text="State", font=('Segoe UI', 10), fg='#94A3B8', bg='#0F172A').pack(anchor='w')
        self.cust_state_var = tk.StringVar()
        ttk.Entry(state_f, textvariable=self.cust_state_var, width=20).pack(pady=(5, 0))
        
        row2 = tk.Frame(details, bg='#0F172A')
        row2.pack(fill=tk.X, pady=(10, 0))
        
        # Address
        addr_f = tk.Frame(row2, bg='#0F172A')
        addr_f.pack(side=tk.LEFT)
        tk.Label(addr_f, text="Address", font=('Segoe UI', 10), fg='#94A3B8', bg='#0F172A').pack(anchor='w')
        self.cust_addr_var = tk.StringVar()
        ttk.Entry(addr_f, textvariable=self.cust_addr_var, width=60).pack(pady=(5, 0))
    
    def _build_items_section(self):
        """Build invoice items section."""
        section = tk.Frame(self.scroll_frame, bg='#0F172A', padx=20, pady=20)
        section.pack(fill=tk.X, pady=(0, 15))
        
        header = tk.Frame(section, bg='#0F172A')
        header.pack(fill=tk.X, pady=(0, 10))
        tk.Label(header, text="Invoice Items", font=('Segoe UI', 12, 'bold'), fg='#F8FAFC', bg='#0F172A').pack(side=tk.LEFT)
        tk.Button(header, text="+ Add Item", font=('Segoe UI', 10, 'bold'), fg='#F8FAFC', bg='#6366F1', bd=0, padx=15, pady=5, cursor='hand2',
                  command=self._add_item_row).pack(side=tk.RIGHT)
        
        # Items header
        items_header = tk.Frame(section, bg='#1E293B')
        items_header.pack(fill=tk.X)
        
        headers = [('#', 30), ('Description', 180), ('HSN/SAC', 80), ('Qty', 50), ('Unit', 60), ('Rate', 80), ('Disc%', 50), ('GST%', 50), ('Amount', 100), ('', 30)]
        for text, width in headers:
            tk.Label(items_header, text=text, font=('Segoe UI', 9, 'bold'), fg='#94A3B8', bg='#1E293B', width=width//8).pack(side=tk.LEFT, padx=2, pady=8)
        
        # Items container
        self.items_container = tk.Frame(section, bg='#0F172A')
        self.items_container.pack(fill=tk.X)
        
        # Add first item
        self._add_item_row()
    
    def _add_item_row(self):
        """Add a new item row."""
        idx = len(self.item_widgets)
        row = tk.Frame(self.items_container, bg='#0F172A')
        row.pack(fill=tk.X, pady=2)
        
        widgets = {}
        
        # Serial number
        widgets['sr'] = tk.Label(row, text=str(idx + 1), font=('Segoe UI', 10), fg='#F8FAFC', bg='#0F172A', width=3)
        widgets['sr'].pack(side=tk.LEFT, padx=2)
        
        # Description
        widgets['desc_var'] = tk.StringVar()
        widgets['desc'] = ttk.Entry(row, textvariable=widgets['desc_var'], width=22)
        widgets['desc'].pack(side=tk.LEFT, padx=2)
        
        # HSN/SAC
        widgets['hsn_var'] = tk.StringVar()
        widgets['hsn'] = ttk.Entry(row, textvariable=widgets['hsn_var'], width=10)
        widgets['hsn'].pack(side=tk.LEFT, padx=2)
        
        # Quantity
        widgets['qty_var'] = tk.StringVar(value='1')
        widgets['qty'] = ttk.Entry(row, textvariable=widgets['qty_var'], width=6)
        widgets['qty'].pack(side=tk.LEFT, padx=2)
        widgets['qty'].bind('<KeyRelease>', lambda e, i=idx: self._calculate_row(i))
        
        # Unit
        widgets['unit_var'] = tk.StringVar(value='NOS')
        widgets['unit'] = ttk.Combobox(row, textvariable=widgets['unit_var'], values=self.UNITS, width=6, state='readonly')
        widgets['unit'].pack(side=tk.LEFT, padx=2)
        
        # Rate
        widgets['rate_var'] = tk.StringVar(value='0')
        widgets['rate'] = ttk.Entry(row, textvariable=widgets['rate_var'], width=10)
        widgets['rate'].pack(side=tk.LEFT, padx=2)
        widgets['rate'].bind('<KeyRelease>', lambda e, i=idx: self._calculate_row(i))
        
        # Discount %
        widgets['disc_var'] = tk.StringVar(value='0')
        widgets['disc'] = ttk.Entry(row, textvariable=widgets['disc_var'], width=6)
        widgets['disc'].pack(side=tk.LEFT, padx=2)
        widgets['disc'].bind('<KeyRelease>', lambda e, i=idx: self._calculate_row(i))
        
        # GST %
        widgets['gst_var'] = tk.StringVar(value='18')
        widgets['gst'] = ttk.Combobox(row, textvariable=widgets['gst_var'], values=self.GST_RATES, width=5)
        widgets['gst'].pack(side=tk.LEFT, padx=2)
        widgets['gst'].bind('<<ComboboxSelected>>', lambda e, i=idx: self._calculate_row(i))
        
        # Amount (calculated)
        widgets['amount_var'] = tk.StringVar(value='0.00')
        widgets['amount'] = tk.Label(row, textvariable=widgets['amount_var'], font=('Segoe UI', 10, 'bold'), fg='#10B981', bg='#0F172A', width=12)
        widgets['amount'].pack(side=tk.LEFT, padx=2)
        
        # Delete button
        widgets['delete'] = tk.Button(row, text="×", font=('Segoe UI', 12), fg='#EF4444', bg='#0F172A', bd=0, cursor='hand2',
                                       command=lambda i=idx: self._delete_item_row(i))
        widgets['delete'].pack(side=tk.LEFT, padx=2)
        
        widgets['row'] = row
        self.item_widgets.append(widgets)
    
    def _delete_item_row(self, idx: int):
        """Delete an item row."""
        if len(self.item_widgets) <= 1:
            return
        
        widgets = self.item_widgets[idx]
        widgets['row'].destroy()
        self.item_widgets.pop(idx)
        
        # Renumber remaining rows
        for i, w in enumerate(self.item_widgets):
            w['sr'].config(text=str(i + 1))
        
        self._calculate_totals()
    
    def _calculate_row(self, idx: int):
        """Calculate a single row amount."""
        if idx >= len(self.item_widgets):
            return
        
        w = self.item_widgets[idx]
        try:
            qty = float(w['qty_var'].get() or 0)
            rate = float(w['rate_var'].get() or 0)
            disc = float(w['disc_var'].get() or 0)
            gst = float(w['gst_var'].get() or 0)
            
            gross = qty * rate
            disc_amt = gross * disc / 100
            taxable = gross - disc_amt
            tax = taxable * gst / 100
            total = taxable + tax
            
            w['amount_var'].set(f"{total:,.2f}")
        except ValueError:
            w['amount_var'].set("0.00")
        
        self._calculate_totals()
    
    def _build_totals_section(self):
        """Build totals section."""
        section = tk.Frame(self.scroll_frame, bg='#0F172A', padx=20, pady=20)
        section.pack(fill=tk.X, pady=(0, 15))
        
        # Two columns
        left = tk.Frame(section, bg='#0F172A')
        left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        right = tk.Frame(section, bg='#0F172A')
        right.pack(side=tk.RIGHT)
        
        # Notes
        tk.Label(left, text="Notes", font=('Segoe UI', 10), fg='#94A3B8', bg='#0F172A').pack(anchor='w')
        self.notes_text = tk.Text(left, height=4, width=40, bg='#1E293B', fg='#F8FAFC', insertbackground='#F8FAFC')
        self.notes_text.pack(anchor='w', pady=(5, 0))
        
        # Totals
        self.subtotal_var = tk.StringVar(value='₹0.00')
        self.discount_var = tk.StringVar(value='₹0.00')
        self.cgst_var = tk.StringVar(value='₹0.00')
        self.sgst_var = tk.StringVar(value='₹0.00')
        self.igst_var = tk.StringVar(value='₹0.00')
        self.total_var = tk.StringVar(value='₹0.00')
        
        totals = [
            ('Subtotal:', self.subtotal_var),
            ('Discount:', self.discount_var),
            ('CGST:', self.cgst_var),
            ('SGST:', self.sgst_var),
            ('IGST:', self.igst_var),
        ]
        
        for label, var in totals:
            row = tk.Frame(right, bg='#0F172A')
            row.pack(fill=tk.X, pady=2)
            tk.Label(row, text=label, font=('Segoe UI', 10), fg='#94A3B8', bg='#0F172A', width=12, anchor='e').pack(side=tk.LEFT)
            tk.Label(row, textvariable=var, font=('Segoe UI', 10), fg='#F8FAFC', bg='#0F172A', width=12, anchor='e').pack(side=tk.LEFT)
        
        # Grand total
        total_row = tk.Frame(right, bg='#0F172A')
        total_row.pack(fill=tk.X, pady=(10, 0))
        tk.Label(total_row, text="TOTAL:", font=('Segoe UI', 14, 'bold'), fg='#F8FAFC', bg='#0F172A', width=8, anchor='e').pack(side=tk.LEFT)
        tk.Label(total_row, textvariable=self.total_var, font=('Segoe UI', 14, 'bold'), fg='#10B981', bg='#0F172A', width=10, anchor='e').pack(side=tk.LEFT)
    
    def _build_action_buttons(self):
        """Build action buttons."""
        section = tk.Frame(self.scroll_frame, bg='#1E293B')
        section.pack(fill=tk.X, pady=(0, 30))
        
        buttons = tk.Frame(section, bg='#1E293B')
        buttons.pack(pady=10)
        
        tk.Button(buttons, text="💾 Save Invoice", font=('Segoe UI', 11, 'bold'), fg='#F8FAFC', bg='#10B981', bd=0, padx=20, pady=10, cursor='hand2',
                  command=self._save_invoice).pack(side=tk.LEFT, padx=5)
        
        tk.Button(buttons, text="🖨️ Save & Print", font=('Segoe UI', 11, 'bold'), fg='#F8FAFC', bg='#6366F1', bd=0, padx=20, pady=10, cursor='hand2',
                  command=self._save_and_print).pack(side=tk.LEFT, padx=5)
        
        tk.Button(buttons, text="📄 Save as PDF", font=('Segoe UI', 11, 'bold'), fg='#F8FAFC', bg='#3B82F6', bd=0, padx=20, pady=10, cursor='hand2',
                  command=self._save_as_pdf).pack(side=tk.LEFT, padx=5)
        
        tk.Button(buttons, text="🔄 Clear", font=('Segoe UI', 11), fg='#F8FAFC', bg='#334155', bd=0, padx=20, pady=10, cursor='hand2',
                  command=self._clear_form).pack(side=tk.LEFT, padx=5)
    
    def _init_new_invoice(self):
        """Initialize a new invoice."""
        prefix = self.db_manager.get_setting('invoice_prefix', 'INV')
        next_num = self.invoice_repo.get_next_invoice_number(prefix)
        self.inv_number_var.set(next_num)
        self.current_invoice = None
    
    def _calculate_totals(self):
        """Calculate invoice totals."""
        subtotal = 0
        cgst = 0
        sgst = 0
        
        for w in self.item_widgets:
            try:
                qty = float(w['qty_var'].get() or 0)
                rate = float(w['rate_var'].get() or 0)
                disc = float(w['disc_var'].get() or 0)
                gst = float(w['gst_var'].get() or 0)
                
                gross = qty * rate
                disc_amt = gross * disc / 100
                taxable = gross - disc_amt
                
                subtotal += taxable
                cgst += taxable * (gst / 2) / 100
                sgst += taxable * (gst / 2) / 100
            except ValueError:
                pass
        
        total = subtotal + cgst + sgst
        
        self.subtotal_var.set(f"₹{subtotal:,.2f}")
        self.cgst_var.set(f"₹{cgst:,.2f}")
        self.sgst_var.set(f"₹{sgst:,.2f}")
        self.igst_var.set("₹0.00")
        self.total_var.set(f"₹{total:,.2f}")
    
    def _save_invoice(self) -> Optional[Invoice]:
        """Save the current invoice."""
        # Validate
        if not self.inv_number_var.get().strip():
            self.show_error("Invoice number is required")
            return None
        
        if not any(w['desc_var'].get().strip() for w in self.item_widgets):
            self.show_error("At least one item is required")
            return None
        
        # Build invoice
        invoice = Invoice()
        invoice.invoice_number = self.inv_number_var.get().strip()
        invoice.invoice_type = self.type_var.get()
        
        try:
            invoice.date = datetime.strptime(self.date_var.get(), '%d/%m/%Y').date()
        except:
            invoice.date = date.today()
        
        if self.due_date_var.get():
            try:
                invoice.due_date = datetime.strptime(self.due_date_var.get(), '%d/%m/%Y').date()
            except:
                pass
        
        invoice.customer_name = self.cust_name_var.get()
        invoice.customer_gstin = self.cust_gstin_var.get()
        invoice.customer_state = self.cust_state_var.get()
        invoice.customer_address = self.cust_addr_var.get()
        invoice.notes = self.notes_text.get('1.0', tk.END).strip()
        
        # Build items
        business_state = self.db_manager.get_setting('business_state_code', '27')
        
        for i, w in enumerate(self.item_widgets):
            desc = w['desc_var'].get().strip()
            if not desc:
                continue
            
            item = InvoiceItem()
            item.sr_no = i + 1
            item.description = desc
            item.hsn_sac = w['hsn_var'].get()
            item.quantity = float(w['qty_var'].get() or 0)
            item.unit = w['unit_var'].get()
            item.rate = float(w['rate_var'].get() or 0)
            item.discount_percent = float(w['disc_var'].get() or 0)
            item.gst_rate = float(w['gst_var'].get() or 0)
            
            invoice.items.append(item)
        
        # Calculate totals
        invoice.calculate_totals(business_state)
        
        # Save
        try:
            if self.current_invoice:
                invoice.id = self.current_invoice.id
                self.invoice_repo.update(invoice)
            else:
                self.invoice_repo.create(invoice)
            
            self.show_success(f"Invoice {invoice.invoice_number} saved successfully!")
            self.current_invoice = invoice
            self._has_unsaved_changes = False
            return invoice
        except Exception as e:
            self.show_error(f"Error saving invoice: {str(e)}")
            return None
    
    def _save_and_print(self):
        """Save and print the invoice."""
        invoice = self._save_invoice()
        if invoice:
            from utils.printer import print_invoice
            print_invoice(invoice, self.db_manager)
    
    def _save_as_pdf(self):
        """Save invoice as PDF."""
        if not self.license_manager.has_feature('pdf_export'):
            self.show_warning("PDF export is not available in Trial mode. Please upgrade.")
            return
        
        invoice = self._save_invoice()
        if invoice:
            from utils.pdf_generator import generate_invoice_pdf
            from tkinter import filedialog
            
            filepath = filedialog.asksaveasfilename(
                defaultextension='.pdf',
                filetypes=[('PDF files', '*.pdf')],
                initialfile=f"{invoice.invoice_number}.pdf"
            )
            if filepath:
                generate_invoice_pdf(invoice, self.db_manager, filepath)
                self.show_success(f"PDF saved to {filepath}")
    
    def _clear_form(self):
        """Clear the form for a new invoice."""
        if self._has_unsaved_changes:
            if not self.confirm("Discard unsaved changes?"):
                return
        
        self._init_new_invoice()
        self.cust_name_var.set('')
        self.cust_gstin_var.set('')
        self.cust_state_var.set('')
        self.cust_addr_var.set('')
        self.notes_text.delete('1.0', tk.END)
        
        # Clear items
        for w in self.item_widgets[1:]:
            w['row'].destroy()
        self.item_widgets = [self.item_widgets[0]]
        
        w = self.item_widgets[0]
        w['desc_var'].set('')
        w['hsn_var'].set('')
        w['qty_var'].set('1')
        w['rate_var'].set('0')
        w['disc_var'].set('0')
        w['gst_var'].set('18')
        w['amount_var'].set('0.00')
        
        self._calculate_totals()
        self._has_unsaved_changes = False
    
    def _search_customers(self, event):
        """Search customers for autocomplete."""
        query = self.customer_var.get()
        if len(query) < 2:
            return
        
        customers = self.customer_repo.get_all(search=query, limit=10)
        values = [f"{c.name} | {c.gstin or 'No GSTIN'}" for c in customers]
        self.customer_combo['values'] = values
        self._customer_cache = {v: c for v, c in zip(values, customers)}
    
    def _on_customer_select(self, event):
        """Handle customer selection."""
        selected = self.customer_var.get()
        if hasattr(self, '_customer_cache') and selected in self._customer_cache:
            c = self._customer_cache[selected]
            self.cust_name_var.set(c.name)
            self.cust_gstin_var.set(c.gstin)
            self.cust_state_var.set(c.state)
            self.cust_addr_var.set(c.address)
    
    def _show_add_customer(self):
        """Show add customer dialog."""
        self.nav_manager.navigate('customers')
    
    def _on_type_change(self, event):
        """Handle invoice type change."""
        self._has_unsaved_changes = True
    
    def refresh(self):
        """Refresh the view."""
        pass
    
    def save_current(self):
        """Save current invoice."""
        self._save_invoice()
    
    def has_unsaved_changes(self) -> bool:
        return self._has_unsaved_changes
