"""
Reports View - Sales and tax reporting
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import date, datetime, timedelta
import csv

from core.navigation import BaseView
from database.models import InvoiceRepository


class ReportsView(BaseView):
    """Reports and analytics view."""
    
    def setup(self):
        """Setup the reports UI."""
        self.invoice_repo = InvoiceRepository(self.db_manager)
        
        self.create_header("Reports", "Sales and tax reports")
        
        # Check license
        if not self.license_manager.has_feature('reports'):
            self._show_locked_feature()
            return
            
        # Main container
        main = tk.Frame(self.frame, bg='#1E293B')
        main.pack(fill=tk.BOTH, expand=True, padx=30, pady=(0, 30))
        
        # Controls / Filters
        controls = tk.Frame(main, bg='#0F172A', padx=20, pady=20)
        controls.pack(fill=tk.X, pady=(0, 20))
        
        # Date Range
        tk.Label(controls, text="Date Range:", font=('Segoe UI', 10), fg='#94A3B8', bg='#0F172A').pack(side=tk.LEFT)
        
        self.start_date_var = tk.StringVar(value=date.today().replace(day=1).strftime('%d/%m/%Y'))
        ttk.Entry(controls, textvariable=self.start_date_var, width=12).pack(side=tk.LEFT, padx=10)
        
        tk.Label(controls, text="to", font=('Segoe UI', 10), fg='#94A3B8', bg='#0F172A').pack(side=tk.LEFT)
        
        self.end_date_var = tk.StringVar(value=date.today().strftime('%d/%m/%Y'))
        ttk.Entry(controls, textvariable=self.end_date_var, width=12).pack(side=tk.LEFT, padx=10)
        
        # Report Type
        tk.Label(controls, text="Report:", font=('Segoe UI', 10), fg='#94A3B8', bg='#0F172A').pack(side=tk.LEFT, padx=(20, 10))
        
        self.report_type_var = tk.StringVar(value='Sales Summary')
        types = ['Sales Summary', 'GST Report', 'Item Wise Sales', 'Customer Wise Sales']
        type_combo = ttk.Combobox(controls, textvariable=self.report_type_var, values=types, state='readonly', width=20)
        type_combo.pack(side=tk.LEFT)
        
        # Buttons
        tk.Button(controls, text="Generate", font=('Segoe UI', 10, 'bold'), fg='#F8FAFC', bg='#6366F1', bd=0, padx=15, pady=5, cursor='hand2',
                  command=self._generate_report).pack(side=tk.LEFT, padx=(20, 0))
        
        tk.Button(controls, text="Export CSV", font=('Segoe UI', 10), fg='#F8FAFC', bg='#10B981', bd=0, padx=15, pady=5, cursor='hand2',
                  command=self._export_csv).pack(side=tk.RIGHT)
        
        # Results area
        self.results_frame = tk.Frame(main, bg='#0F172A')
        self.results_frame.pack(fill=tk.BOTH, expand=True)
        
        self._setup_treeview()
        
    def _show_locked_feature(self):
        """Show locked feature message."""
        frame = tk.Frame(self.frame, bg='#1E293B')
        frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=30)
        
        tk.Label(frame, text="🔒", font=('Segoe UI', 48), fg='#94A3B8', bg='#1E293B').pack(pady=(50, 20))
        tk.Label(frame, text="Reports Locked", font=('Segoe UI', 18, 'bold'), fg='#F8FAFC', bg='#1E293B').pack()
        tk.Label(frame, text="Upgrade to Basic or Pro plan to view reports.", font=('Segoe UI', 11), fg='#94A3B8', bg='#1E293B').pack(pady=(10, 30))
        
        tk.Button(frame, text="Upgrade Now", font=('Segoe UI', 11, 'bold'), fg='#F8FAFC', bg='#6366F1', bd=0, padx=20, pady=10, cursor='hand2',
                  command=lambda: self.nav_manager.navigate('settings')).pack()

    def _setup_treeview(self):
        """Setup initial treeview."""
        self.tree = ttk.Treeview(self.results_frame, show='headings', selectmode='browse')
        
        scrollbar_y = ttk.Scrollbar(self.results_frame, orient='vertical', command=self.tree.yview)
        scrollbar_x = ttk.Scrollbar(self.results_frame, orient='horizontal', command=self.tree.xview)
        
        self.tree.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)
    
    def _parse_dates(self):
        """Parse start and end dates."""
        try:
            start = datetime.strptime(self.start_date_var.get(), '%d/%m/%Y').date()
            end = datetime.strptime(self.end_date_var.get(), '%d/%m/%Y').date()
            return start, end
        except ValueError:
            self.show_error("Invalid date format. Use DD/MM/YYYY")
            return None, None
            
    def _generate_report(self):
        """Generate selected report."""
        start_date, end_date = self._parse_dates()
        if not start_date:
            return
            
        report_type = self.report_type_var.get()
        self.current_data = [] # Store for export
        
        # Clear tree
        self.tree.delete(*self.tree.get_children())
        
        columns = []
        rows = []
        
        if report_type == 'Sales Summary':
            columns = ['Date', 'Invoice Count', 'Taxable', 'CGST', 'SGST', 'IGST', 'Total']
            rows = self._get_sales_summary(start_date, end_date)
            
        elif report_type == 'GST Report':
            columns = ['Invoice No', 'Date', 'GSTIN', 'Taxable', 'CGST', 'SGST', 'IGST', 'Total']
            rows = self._get_gst_report(start_date, end_date)
            
        elif report_type == 'Item Wise Sales':
            columns = ['Item Name', 'HSN/SAC', 'Quantity', 'Avg Rate', 'Total Taxable', 'Total Tax']
            rows = self._get_item_sales(start_date, end_date)
            
        elif report_type == 'Customer Wise Sales':
            columns = ['Customer Name', 'GSTIN', 'Invoice Count', 'Total Sales', 'Total Paid', 'Balance']
            rows = self._get_customer_sales(start_date, end_date)
            
        # Configure columns
        self.tree['columns'] = [str(i) for i in range(len(columns))]
        for i, col in enumerate(columns):
            self.tree.heading(str(i), text=col)
            self.tree.column(str(i), width=100 if col != 'Item Name' else 200)
            
        # Insert data
        for row in rows:
            self.tree.insert('', tk.END, values=row)
            
        self.current_data = {'columns': columns, 'rows': rows}
        
    def _get_sales_summary(self, start, end):
        """Get sales summary grouped by date."""
        query = '''
            SELECT 
                date, 
                COUNT(*) as count, 
                SUM(taxable_amount) as taxable,
                SUM(cgst_amount) as cgst,
                SUM(sgst_amount) as sgst,
                SUM(igst_amount) as igst,
                SUM(total) as total
            FROM invoices 
            WHERE date BETWEEN ? AND ? AND status = 'ACTIVE'
            GROUP BY date
            ORDER BY date
        '''
        results = self.db_manager.fetchall(query, (start, end))
        return [(
            r['date'], r['count'], 
            f"₹{r['taxable']:,.2f}", f"₹{r['cgst']:,.2f}", 
            f"₹{r['sgst']:,.2f}", f"₹{r['igst']:,.2f}", 
            f"₹{r['total']:,.2f}"
        ) for r in results]

    def _get_gst_report(self, start, end):
        """Get comprehensive GST report."""
        query = '''
            SELECT 
                invoice_number, date, customer_gstin,
                taxable_amount, cgst_amount, sgst_amount, igst_amount, total
            FROM invoices
            WHERE date BETWEEN ? AND ? AND status = 'ACTIVE' AND invoice_type = 'GST'
            ORDER BY date
        '''
        results = self.db_manager.fetchall(query, (start, end))
        return [(
            r['invoice_number'], r['date'], r['customer_gstin'] or '-',
            f"₹{r['taxable_amount']:,.2f}", f"₹{r['cgst_amount']:,.2f}",
            f"₹{r['sgst_amount']:,.2f}", f"₹{r['igst_amount']:,.2f}",
            f"₹{r['total']:,.2f}"
        ) for r in results]

    def _get_item_sales(self, start, end):
        """Get item wise sales."""
        query = '''
            SELECT 
                ii.description, ii.hsn_sac,
                SUM(ii.quantity) as qty,
                AVG(ii.rate) as avg_rate,
                SUM(ii.taxable_amount) as taxable,
                SUM(ii.cgst_amount + ii.sgst_amount + ii.igst_amount) as tax
            FROM invoice_items ii
            JOIN invoices i ON i.id = ii.invoice_id
            WHERE i.date BETWEEN ? AND ? AND i.status = 'ACTIVE'
            GROUP BY ii.description
            ORDER BY taxable DESC
        '''
        results = self.db_manager.fetchall(query, (start, end))
        return [(
            r['description'], r['hsn_sac'] or '-', r['qty'],
            f"₹{r['avg_rate']:,.2f}", f"₹{r['taxable']:,.2f}", f"₹{r['tax']:,.2f}"
        ) for r in results]

    def _get_customer_sales(self, start, end):
        """Get customer wise sales."""
        query = '''
            SELECT 
                customer_name, customer_gstin,
                COUNT(*) as count,
                SUM(total) as total,
                SUM(amount_paid) as paid
            FROM invoices
            WHERE date BETWEEN ? AND ? AND status = 'ACTIVE'
            GROUP BY customer_name
            ORDER BY total DESC
        '''
        results = self.db_manager.fetchall(query, (start, end))
        return [(
            r['customer_name'] or 'Walk-in', r['customer_gstin'] or '-',
            r['count'], f"₹{r['total']:,.2f}",
            f"₹{r['paid']:,.2f}", f"₹{r['total'] - r['paid']:,.2f}"
        ) for r in results]
        
    def _export_csv(self):
        """Export current report to CSV."""
        if not hasattr(self, 'current_data') or not self.current_data:
            self.show_warning("Generate a report first")
            return
            
        filename = filedialog.asksaveasfilename(
            defaultextension='.csv',
            filetypes=[('CSV Files', '*.csv')]
        )
        if not filename:
            return
            
        try:
            with open(filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(self.current_data['columns'])
                writer.writerows(self.current_data['rows'])
            self.show_success(f"Report exported to {filename}")
        except Exception as e:
            self.show_error(f"Export failed: {e}")
