"""
Settings View - Application configuration
"""

import tkinter as tk
from tkinter import ttk, filedialog
import os
import shutil
from datetime import datetime

from core.navigation import BaseView


class SettingsView(BaseView):
    """Application settings view."""
    
    def setup(self):
        """Setup the settings UI."""
        self.create_header("Settings", "Configure your business and application")
        
        # Notebook for categorized settings
        notebook = ttk.Notebook(self.frame)
        notebook.pack(fill=tk.BOTH, expand=True, padx=30, pady=(0, 30))
        
        # Tabs
        self.business_tab = ttk.Frame(notebook)
        self.invoice_tab = ttk.Frame(notebook)
        self.payment_tab = ttk.Frame(notebook)
        self.system_tab = ttk.Frame(notebook)
        self.license_tab = ttk.Frame(notebook)
        
        notebook.add(self.business_tab, text="Business Profile")
        notebook.add(self.invoice_tab, text="Invoice Configuration")
        notebook.add(self.payment_tab, text="Payment Configuration")
        notebook.add(self.system_tab, text="System & Backup")
        notebook.add(self.license_tab, text="License & Plan")
        
        self._build_business_tab()
        self._build_invoice_tab()
        self._build_payment_tab()
        self._build_system_tab()
        self._build_license_tab()
        
    def _build_business_tab(self):
        """Build business profile settings."""
        frame = tk.Frame(self.business_tab, bg='#1E293B', padx=30, pady=30)
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Load current settings
        settings = self.db_manager.get_settings(prefix='business_')
        
        self.biz_vars = {}
        fields = [
            ('Business Name', 'business_name', 40),
            ('GSTIN', 'business_gstin', 20),
            ('Phone', 'business_phone', 20),
            ('Email', 'business_email', 40),
            ('City', 'business_city', 30),
            ('Pincode', 'business_pincode', 10),
        ]
        
        for label, key, width in fields:
            f = tk.Frame(frame, bg='#1E293B')
            f.pack(fill=tk.X, pady=5)
            tk.Label(f, text=label, font=('Segoe UI', 10), fg='#94A3B8', bg='#1E293B', width=15, anchor='w').pack(side=tk.LEFT)
            var = tk.StringVar(value=settings.get(key, ''))
            self.biz_vars[key] = var
            ttk.Entry(f, textvariable=var, width=width).pack(side=tk.LEFT)
            
        # Address
        f = tk.Frame(frame, bg='#1E293B')
        f.pack(fill=tk.X, pady=5)
        tk.Label(f, text="Address", font=('Segoe UI', 10), fg='#94A3B8', bg='#1E293B', width=15, anchor='w').pack(side=tk.LEFT, anchor='n', pady=5)
        self.biz_addr = tk.Text(f, height=3, width=40, bg='#0F172A', fg='#F8FAFC', insertbackground='#F8FAFC')
        self.biz_addr.insert('1.0', settings.get('business_address', ''))
        self.biz_addr.pack(side=tk.LEFT)
        
        # State Code
        f = tk.Frame(frame, bg='#1E293B')
        f.pack(fill=tk.X, pady=5)
        tk.Label(f, text="State Code", font=('Segoe UI', 10), fg='#94A3B8', bg='#1E293B', width=15, anchor='w').pack(side=tk.LEFT)
        self.biz_vars['business_state_code'] = tk.StringVar(value=settings.get('business_state_code', '27'))
        ttk.Entry(f, textvariable=self.biz_vars['business_state_code'], width=10).pack(side=tk.LEFT)
        
        # Save Button
        tk.Button(frame, text="Save Business Profile", font=('Segoe UI', 10, 'bold'), 
                  fg='#F8FAFC', bg='#6366F1', bd=0, padx=20, pady=10, cursor='hand2',
                  command=self._save_business_settings).pack(pady=30, anchor='w')

    def _build_invoice_tab(self):
        """Build invoice settings."""
        frame = tk.Frame(self.invoice_tab, bg='#1E293B', padx=30, pady=30)
        frame.pack(fill=tk.BOTH, expand=True)
        
        settings = self.db_manager.get_settings(prefix='invoice_')
        
        self.inv_vars = {}
        
        # Prefix
        f = tk.Frame(frame, bg='#1E293B')
        f.pack(fill=tk.X, pady=5)
        tk.Label(f, text="Invoice Prefix", font=('Segoe UI', 10), fg='#94A3B8', bg='#1E293B', width=20, anchor='w').pack(side=tk.LEFT)
        self.inv_vars['invoice_prefix'] = tk.StringVar(value=settings.get('invoice_prefix', 'INV'))
        ttk.Entry(f, textvariable=self.inv_vars['invoice_prefix'], width=15).pack(side=tk.LEFT)
        
        # Start Number
        f = tk.Frame(frame, bg='#1E293B')
        f.pack(fill=tk.X, pady=5)
        tk.Label(f, text="Starting Sequence", font=('Segoe UI', 10), fg='#94A3B8', bg='#1E293B', width=20, anchor='w').pack(side=tk.LEFT)
        self.inv_vars['invoice_start_number'] = tk.StringVar(value=settings.get('invoice_start_number', '1'))
        ttk.Entry(f, textvariable=self.inv_vars['invoice_start_number'], width=15).pack(side=tk.LEFT)
        
        # Terms & Conditions
        f = tk.Frame(frame, bg='#1E293B')
        f.pack(fill=tk.X, pady=15)
        tk.Label(f, text="Default Terms & Conditions", font=('Segoe UI', 10), fg='#94A3B8', bg='#1E293B', width=20, anchor='w').pack(side=tk.LEFT, anchor='n')
        self.terms_text = tk.Text(f, height=5, width=50, bg='#0F172A', fg='#F8FAFC', insertbackground='#F8FAFC')
        self.terms_text.insert('1.0', settings.get('invoice_terms', ''))
        self.terms_text.pack(side=tk.LEFT)
        
        # Save Button
        tk.Button(frame, text="Save Invoice Settings", font=('Segoe UI', 10, 'bold'), 
                  fg='#F8FAFC', bg='#6366F1', bd=0, padx=20, pady=10, cursor='hand2',
                  command=self._save_invoice_settings).pack(pady=20, anchor='w')

    def _build_payment_tab(self):
        """Build payment configuration settings."""
        frame = tk.Frame(self.payment_tab, bg='#1E293B', padx=30, pady=30)
        frame.pack(fill=tk.BOTH, expand=True)

        # UPI Configuration
        grp = tk.LabelFrame(frame, text="UPI Configuration", bg='#1E293B', fg='#F8FAFC', font=('Segoe UI', 10, 'bold'), padx=20, pady=20)
        grp.pack(fill=tk.X, pady=(0, 20))
        
        settings = self.db_manager.get_settings(prefix='payment_')
        self.pay_vars = {}

        # VPA
        f = tk.Frame(grp, bg='#1E293B')
        f.pack(fill=tk.X, pady=5)
        tk.Label(f, text="UPI ID / VPA", font=('Segoe UI', 10), fg='#94A3B8', bg='#1E293B', width=20, anchor='w').pack(side=tk.LEFT)
        self.pay_vars['payment_upi_vpa'] = tk.StringVar(value=settings.get('payment_upi_vpa', ''))
        ttk.Entry(f, textvariable=self.pay_vars['payment_upi_vpa'], width=30).pack(side=tk.LEFT)
        tk.Label(f, text="(Required for Dynamic QR)", font=('Segoe UI', 9), fg='#64748B', bg='#1E293B').pack(side=tk.LEFT, padx=10)

        # Payee Name
        f = tk.Frame(grp, bg='#1E293B')
        f.pack(fill=tk.X, pady=5)
        tk.Label(f, text="Payee Name", font=('Segoe UI', 10), fg='#94A3B8', bg='#1E293B', width=20, anchor='w').pack(side=tk.LEFT)
        self.pay_vars['payment_payee_name'] = tk.StringVar(value=settings.get('payment_payee_name', ''))
        ttk.Entry(f, textvariable=self.pay_vars['payment_payee_name'], width=30).pack(side=tk.LEFT)

        # QR Upload
        f = tk.Frame(grp, bg='#1E293B')
        f.pack(fill=tk.X, pady=15)
        tk.Label(f, text="Static QR Image", font=('Segoe UI', 10), fg='#94A3B8', bg='#1E293B', width=20, anchor='w').pack(side=tk.LEFT)
        tk.Button(f, text="Upload Image", font=('Segoe UI', 9), command=self._upload_qr).pack(side=tk.LEFT)
        self.qr_status_label = tk.Label(f, text="No file selected", font=('Segoe UI', 9), fg='#64748B', bg='#1E293B')
        self.qr_status_label.pack(side=tk.LEFT, padx=10)

        # Gateway Configuration
        grp2 = tk.LabelFrame(frame, text="Payment Gateway (API)", bg='#1E293B', fg='#F8FAFC', font=('Segoe UI', 10, 'bold'), padx=20, pady=20)
        grp2.pack(fill=tk.X)

        f = tk.Frame(grp2, bg='#1E293B')
        f.pack(fill=tk.X, pady=5)
        tk.Label(f, text="API Key", font=('Segoe UI', 10), fg='#94A3B8', bg='#1E293B', width=20, anchor='w').pack(side=tk.LEFT)
        self.pay_vars['payment_gateway_key'] = tk.StringVar(value=settings.get('payment_gateway_key', ''))
        ttk.Entry(f, textvariable=self.pay_vars['payment_gateway_key'], show='*', width=40).pack(side=tk.LEFT)

        f = tk.Frame(grp2, bg='#1E293B')
        f.pack(fill=tk.X, pady=5)
        tk.Label(f, text="Secret Key", font=('Segoe UI', 10), fg='#94A3B8', bg='#1E293B', width=20, anchor='w').pack(side=tk.LEFT)
        self.pay_vars['payment_gateway_secret'] = tk.StringVar(value=settings.get('payment_gateway_secret', ''))
        ttk.Entry(f, textvariable=self.pay_vars['payment_gateway_secret'], show='*', width=40).pack(side=tk.LEFT)

        # Save Button
        tk.Button(frame, text="Save Payment Settings", font=('Segoe UI', 10, 'bold'), 
                  fg='#F8FAFC', bg='#6366F1', bd=0, padx=20, pady=10, cursor='hand2',
                  command=self._save_payment_settings).pack(pady=30, anchor='w')

    def _upload_qr(self):
        filename = filedialog.askopenfilename(filetypes=[('Images', '*.png;*.jpg;*.jpeg')])
        if filename:
            from core.payments_config import PaymentConfigManager
            mgr = PaymentConfigManager(self.db_manager)
            path = mgr.upload_qr_image(filename)
            if path:
                self.qr_status_label.config(text="QR Uploaded!", fg='#10B981')
                self.show_success("QR Code uploaded successfully.")
            else:
                self.show_error("Failed to upload QR.")

    def _save_payment_settings(self):
        """Save payment settings."""
        for key, var in self.pay_vars.items():
            self.db_manager.set_setting(key, var.get().strip())
            
        # Set dynamic if VPA is present
        if self.pay_vars['payment_upi_vpa'].get():
            self.db_manager.set_setting('payment_qr_type', 'DYNAMIC')
        else:
            # Revert to static if no VPA, or stay static
            pass
            
        self.show_success("Payment settings saved!")

    def _build_system_tab(self):
        """Build system settings (Backup/Restore)."""
        frame = tk.Frame(self.system_tab, bg='#1E293B', padx=30, pady=30)
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Backup Section
        grp = tk.LabelFrame(frame, text="Database Backup", bg='#1E293B', fg='#F8FAFC', font=('Segoe UI', 10, 'bold'), padx=20, pady=20)
        grp.pack(fill=tk.X, pady=(0, 20))
        
        tk.Label(grp, text="Create a backup of your data to keep it safe.", 
                 font=('Segoe UI', 10), fg='#94A3B8', bg='#1E293B').pack(anchor='w', pady=(0, 10))
        
        tk.Button(grp, text="Create Backup", font=('Segoe UI', 10), 
                  fg='#F8FAFC', bg='#10B981', bd=0, padx=15, pady=8, cursor='hand2',
                  command=self._create_backup).pack(anchor='w')
                  
        # Restore Section
        grp2 = tk.LabelFrame(frame, text="Restore Data", bg='#1E293B', fg='#F8FAFC', font=('Segoe UI', 10, 'bold'), padx=20, pady=20)
        grp2.pack(fill=tk.X)
        
        tk.Label(grp2, text="Restore data from a previous backup file.\nWARNING: Current data will be replaced.", 
                 font=('Segoe UI', 10), fg='#EF4444', bg='#1E293B', justify='left').pack(anchor='w', pady=(0, 10))
        
        tk.Button(grp2, text="Restore Backup", font=('Segoe UI', 10), 
                  fg='#F8FAFC', bg='#EF4444', bd=0, padx=15, pady=8, cursor='hand2',
                  command=self._restore_backup).pack(anchor='w')

    def _build_license_tab(self):
        """Build license settings."""
        frame = tk.Frame(self.license_tab, bg='#1E293B', padx=30, pady=30)
        frame.pack(fill=tk.BOTH, expand=True)
        
        info = self.license_manager.get_license_info()
        
        # Status Card
        card = tk.Frame(frame, bg='#0F172A', padx=20, pady=20)
        card.pack(fill=tk.X, pady=(0, 30))
        
        tk.Label(card, text="Current Plan", font=('Segoe UI', 10), fg='#94A3B8', bg='#0F172A').pack(anchor='w')
        
        plan = info.get('plan', 'TRIAL')
        color = '#10B981' if plan == 'PRO' else '#3B82F6' if plan == 'BASIC' else '#F59E0B'
        
        tk.Label(card, text=plan, font=('Segoe UI', 24, 'bold'), fg=color, bg='#0F172A').pack(anchor='w', pady=5)
        
        details = []
        if plan == 'TRIAL':
            details.append(f"Invoices Remaining: {info.get('invoices_remaining', 0)}")
        
        if info.get('expiry_date'):
            details.append(f"Expires On: {info.get('expiry_date')}")
            
        details.append(f"Machine ID: {info.get('machine_id')}")
        
        for d in details:
            tk.Label(card, text=d, font=('Segoe UI', 10), fg='#F8FAFC', bg='#0F172A').pack(anchor='w', pady=2)
            
        # Activation
        act = tk.Frame(frame, bg='#1E293B')
        act.pack(fill=tk.X)
        
        tk.Label(act, text="Enter License Key", font=('Segoe UI', 10, 'bold'), fg='#F8FAFC', bg='#1E293B').pack(anchor='w', pady=(0, 10))
        tk.Label(act, text="(Contact Admin to purchase a key)", font=('Segoe UI', 9), fg='#64748B', bg='#1E293B').pack(anchor='w', pady=(0, 5))
        
        self.license_key_var = tk.StringVar()
        ttk.Entry(act, textvariable=self.license_key_var, width=50, font=('Consolas', 11)).pack(anchor='w', pady=(0, 10))
        
        tk.Button(act, text="Activate / Renew License", font=('Segoe UI', 10, 'bold'), 
                  fg='#F8FAFC', bg='#6366F1', bd=0, padx=20, pady=10, cursor='hand2',
                  command=self._activate_license).pack(anchor='w')

    def _save_business_settings(self):
        """Save business profile."""
        for key, var in self.biz_vars.items():
            self.db_manager.set_setting(key, var.get().strip())
        
        self.db_manager.set_setting('business_address', self.biz_addr.get('1.0', tk.END).strip())
        self.show_success("Business profile updated!")

    def _save_invoice_settings(self):
        """Save invoice settings."""
        for key, var in self.inv_vars.items():
            self.db_manager.set_setting(key, var.get().strip())
        
        self.db_manager.set_setting('invoice_terms', self.terms_text.get('1.0', tk.END).strip())
        self.show_success("Invoice settings updated!")

    def _create_backup(self):
        """Create database backup."""
        if not self.license_manager.has_feature('backup'):
            self.show_warning("Backup feature requires PRO plan.")
            return

        filename = filedialog.asksaveasfilename(
            defaultextension='.db',
            filetypes=[('SQLite Database', '*.db')],
            initialfile=f"billing_backup_{date.today().strftime('%Y%m%d')}.db"
        )
        if filename:
            if self.db_manager.backup(filename):
                self.show_success(f"Backup created successfully at {filename}")
            else:
                self.show_error("Backup failed!")

    def _restore_backup(self):
        """Restore database from backup."""
        if not self.license_manager.has_feature('backup'):
            self.show_warning("Backup/Restore requires PRO plan.")
            return
            
        if not self.confirm("This will overwrite current data. Are you sure?"):
            return

        filename = filedialog.askopenfilename(filetypes=[('SQLite Database', '*.db')])
        if filename:
            if self.db_manager.restore(filename):
                self.show_success("Data restored successfully! Please restart the application.")
                self.frame.quit()
            else:
                self.show_error("Restore failed! Invalid backup file.")

    def _activate_license(self):
        """Activate license."""
        key = self.license_key_var.get().strip()
        if not key:
            return
            
        success, msg = self.license_manager.activate_license(key)
        if success:
            self.show_success(msg)
            # Refresh to update license status UI
            self.nav_manager.refresh_current_view()
            # Also refresh sidebar to show new badge
            self.nav_manager.setup() # Re-render sidebar
        else:
            self.show_error(msg)
