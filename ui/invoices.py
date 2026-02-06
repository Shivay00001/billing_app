"""
Invoices List View - View and manage all invoices
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date, datetime

from core.navigation import BaseView
from database.models import InvoiceRepository


class InvoicesView(BaseView):
    """Invoices listing and management view."""
    
    def setup(self):
        """Setup the invoices list UI."""
        self.invoice_repo = InvoiceRepository(self.db_manager)
        
        self.create_header("Invoices", "Manage your invoices")
        
        # Filters bar
        self._build_filters()
        
        # Invoices table
        self._build_table()
        
        # Load data
        self.refresh()
    
    def _build_filters(self):
        """Build filters bar."""
        filters = tk.Frame(self.frame, bg='#1E293B')
        filters.pack(fill=tk.X, padx=30, pady=(0, 15))
        
        # Search
        tk.Label(filters, text="Search:", font=('Segoe UI', 10), fg='#94A3B8', bg='#1E293B').pack(side=tk.LEFT)
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(filters, textvariable=self.search_var, width=20)
        search_entry.pack(side=tk.LEFT, padx=(5, 15))
        search_entry.bind('<KeyRelease>', lambda e: self.refresh())
        
        # Type filter
        tk.Label(filters, text="Type:", font=('Segoe UI', 10), fg='#94A3B8', bg='#1E293B').pack(side=tk.LEFT)
        self.type_var = tk.StringVar(value='All')
        type_combo = ttk.Combobox(filters, textvariable=self.type_var, values=['All', 'GST', 'NON_GST', 'ESTIMATE', 'PROFORMA'], state='readonly', width=10)
        type_combo.pack(side=tk.LEFT, padx=(5, 15))
        type_combo.bind('<<ComboboxSelected>>', lambda e: self.refresh())
        
        # Status filter
        tk.Label(filters, text="Status:", font=('Segoe UI', 10), fg='#94A3B8', bg='#1E293B').pack(side=tk.LEFT)
        self.status_var = tk.StringVar(value='ACTIVE')
        status_combo = ttk.Combobox(filters, textvariable=self.status_var, values=['All', 'ACTIVE', 'CANCELLED'], state='readonly', width=10)
        status_combo.pack(side=tk.LEFT, padx=(5, 15))
        status_combo.bind('<<ComboboxSelected>>', lambda e: self.refresh())
        
        # New Invoice button
        tk.Button(filters, text="+ New Invoice", font=('Segoe UI', 10, 'bold'), fg='#F8FAFC', bg='#6366F1', bd=0, padx=15, pady=5, cursor='hand2',
                  command=lambda: self.nav_manager.navigate('new_invoice')).pack(side=tk.RIGHT)
    
    def _build_table(self):
        """Build invoices table."""
        table_frame = tk.Frame(self.frame, bg='#0F172A')
        table_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=(0, 30))
        
        # Table with scrollbar
        columns = ('number', 'date', 'customer', 'type', 'total', 'status', 'payment')
        self.tree = ttk.Treeview(table_frame, columns=columns, show='headings', selectmode='browse')
        
        # Column headings
        self.tree.heading('number', text='Invoice #')
        self.tree.heading('date', text='Date')
        self.tree.heading('customer', text='Customer')
        self.tree.heading('type', text='Type')
        self.tree.heading('total', text='Total')
        self.tree.heading('status', text='Status')
        self.tree.heading('payment', text='Payment')
        
        # Column widths
        self.tree.column('number', width=120)
        self.tree.column('date', width=100)
        self.tree.column('customer', width=200)
        self.tree.column('type', width=80)
        self.tree.column('total', width=100)
        self.tree.column('status', width=80)
        self.tree.column('payment', width=80)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient='vertical', command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Context menu
        self.tree.bind('<Double-1>', self._on_double_click)
        self.tree.bind('<Button-3>', self._show_context_menu)
        
        # Create context menu
        self.context_menu = tk.Menu(self.frame, tearoff=0)
        self.context_menu.add_command(label="View/Edit", command=self._edit_invoice)
        self.context_menu.add_command(label="Duplicate", command=self._duplicate_invoice)
        self.context_menu.add_command(label="Print", command=self._print_invoice)
        self.context_menu.add_command(label="Export PDF", command=self._export_pdf)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Cancel Invoice", command=self._cancel_invoice)
    
    def refresh(self):
        """Refresh the invoices list."""
        # Clear existing
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Build filters
        filters = {}
        if self.type_var.get() != 'All':
            filters['invoice_type'] = self.type_var.get()
        if self.status_var.get() != 'All':
            filters['status'] = self.status_var.get()
        if self.search_var.get():
            filters['search'] = self.search_var.get()
        
        # Load invoices
        invoices = self.invoice_repo.get_all(filters=filters, limit=500)
        
        for inv in invoices:
            date_str = inv.date.strftime('%d/%m/%Y') if inv.date else ''
            self.tree.insert('', tk.END, values=(
                inv.invoice_number,
                date_str,
                inv.customer_name or 'Walk-in',
                inv.invoice_type,
                f"₹{inv.total:,.2f}",
                inv.status,
                inv.payment_status
            ), tags=(inv.id,))
    
    def _on_double_click(self, event):
        """Handle double-click to edit."""
        self._edit_invoice()
    
    def _show_context_menu(self, event):
        """Show context menu."""
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            self.context_menu.post(event.x_root, event.y_root)
    
    def _get_selected_invoice_id(self):
        """Get selected invoice ID."""
        selection = self.tree.selection()
        if not selection:
            return None
        tags = self.tree.item(selection[0], 'tags')
        return int(tags[0]) if tags else None
    
    def _edit_invoice(self):
        """Edit selected invoice."""
        inv_id = self._get_selected_invoice_id()
        if inv_id:
            # Navigate to billing with invoice loaded
            self.nav_manager.navigate('new_invoice')
            # TODO: Load invoice in billing view
    
    def _duplicate_invoice(self):
        """Duplicate selected invoice."""
        inv_id = self._get_selected_invoice_id()
        if inv_id:
            dup = self.invoice_repo.duplicate(inv_id)
            if dup:
                self.invoice_repo.create(dup)
                self.show_success(f"Invoice duplicated as {dup.invoice_number}")
                self.refresh()
    
    def _print_invoice(self):
        """Print selected invoice."""
        inv_id = self._get_selected_invoice_id()
        if inv_id:
            invoice = self.invoice_repo.get_by_id(inv_id)
            if invoice:
                from utils.printer import print_invoice
                print_invoice(invoice, self.db_manager)
    
    def _export_pdf(self):
        """Export invoice to PDF."""
        if not self.license_manager.has_feature('pdf_export'):
            self.show_warning("PDF export requires Basic or Pro plan")
            return
        
        inv_id = self._get_selected_invoice_id()
        if inv_id:
            invoice = self.invoice_repo.get_by_id(inv_id)
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
                    self.show_success(f"PDF saved!")
    
    def _cancel_invoice(self):
        """Cancel selected invoice."""
        inv_id = self._get_selected_invoice_id()
        if inv_id:
            if self.confirm("Are you sure you want to cancel this invoice?"):
                self.invoice_repo.cancel(inv_id)
                self.show_success("Invoice cancelled")
                self.refresh()
