"""
Database Initialization - SQLite Auto-creation and Schema Management
"""

import sqlite3
import os
from datetime import datetime
from typing import Optional
import json
import threading

class DatabaseManager:
    """Manages SQLite database connection and schema."""
    
    DB_VERSION = 1
    
    def __init__(self, db_path: Optional[str] = None):
        """Initialize database manager."""
        if db_path is None:
            # Default to user's app data directory
            app_data = os.path.join(os.path.expanduser('~'), '.gst_billing_pro')
            os.makedirs(app_data, exist_ok=True)
            db_path = os.path.join(app_data, 'billing.db')
        
        self.db_path = db_path
        self.connection: Optional[sqlite3.Connection] = None
        self._lock = threading.RLock()
        
        # Initialize database
        self._connect()
        self._init_schema()
        self._seed_defaults()
    
    def _connect(self):
        """Establish database connection."""
        self.connection = sqlite3.connect(self.db_path, check_same_thread=False)
        self.connection.row_factory = sqlite3.Row
        # Enable foreign keys
        self.connection.execute("PRAGMA foreign_keys = ON")
        # Enable Write-Ahead Logging (WAL) for concurrency
        self.connection.execute("PRAGMA journal_mode = WAL")
    
    def _init_schema(self):
        """Initialize database schema."""
        cursor = self.connection.cursor()
        
        # Settings table (includes schema version)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Check schema version
        cursor.execute("SELECT value FROM settings WHERE key = 'schema_version'")
        result = cursor.fetchone()
        current_version = int(result['value']) if result else 0
        
        if current_version < self.DB_VERSION:
            self._create_tables(cursor)
            cursor.execute('''
                INSERT OR REPLACE INTO settings (key, value, updated_at)
                VALUES ('schema_version', ?, CURRENT_TIMESTAMP)
            ''', (str(self.DB_VERSION),))
        
        self.connection.commit()
    
    def _create_tables(self, cursor):
        """Create all database tables."""
        
        # Customers table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS customers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                gstin TEXT,
                phone TEXT,
                email TEXT,
                address TEXT,
                city TEXT,
                state TEXT,
                state_code TEXT,
                pincode TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Products table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                hsn_sac TEXT,
                unit TEXT DEFAULT 'NOS',
                rate REAL DEFAULT 0,
                gst_rate REAL DEFAULT 18,
                description TEXT,
                is_service INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Invoices table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS invoices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                invoice_number TEXT UNIQUE NOT NULL,
                invoice_type TEXT NOT NULL DEFAULT 'GST',
                date DATE NOT NULL,
                due_date DATE,
                customer_id INTEGER,
                customer_name TEXT,
                customer_gstin TEXT,
                customer_address TEXT,
                customer_state TEXT,
                customer_state_code TEXT,
                subtotal REAL DEFAULT 0,
                discount_type TEXT DEFAULT 'PERCENT',
                discount_value REAL DEFAULT 0,
                discount_amount REAL DEFAULT 0,
                taxable_amount REAL DEFAULT 0,
                cgst_amount REAL DEFAULT 0,
                sgst_amount REAL DEFAULT 0,
                igst_amount REAL DEFAULT 0,
                round_off REAL DEFAULT 0,
                total REAL DEFAULT 0,
                amount_paid REAL DEFAULT 0,
                payment_status TEXT DEFAULT 'UNPAID',
                payment_method TEXT,
                notes TEXT,
                terms TEXT,
                status TEXT DEFAULT 'ACTIVE',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (customer_id) REFERENCES customers(id)
            )
        ''')
        
        # Invoice Items table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS invoice_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                invoice_id INTEGER NOT NULL,
                product_id INTEGER,
                sr_no INTEGER,
                description TEXT NOT NULL,
                hsn_sac TEXT,
                quantity REAL DEFAULT 1,
                unit TEXT DEFAULT 'NOS',
                rate REAL DEFAULT 0,
                discount_percent REAL DEFAULT 0,
                discount_amount REAL DEFAULT 0,
                taxable_amount REAL DEFAULT 0,
                gst_rate REAL DEFAULT 0,
                cgst_rate REAL DEFAULT 0,
                cgst_amount REAL DEFAULT 0,
                sgst_rate REAL DEFAULT 0,
                sgst_amount REAL DEFAULT 0,
                igst_rate REAL DEFAULT 0,
                igst_amount REAL DEFAULT 0,
                total REAL DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (invoice_id) REFERENCES invoices(id) ON DELETE CASCADE,
                FOREIGN KEY (product_id) REFERENCES products(id)
            )
        ''')
        
        # Payments table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS payments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                invoice_id INTEGER NOT NULL,
                amount REAL NOT NULL,
                method TEXT DEFAULT 'CASH',
                reference TEXT,
                date DATE NOT NULL,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (invoice_id) REFERENCES invoices(id) ON DELETE CASCADE
            )
        ''')
        
        # License table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS license (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                machine_id TEXT,
                license_key TEXT,
                plan TEXT DEFAULT 'TRIAL',
                invoice_limit INTEGER DEFAULT 10,
                invoices_created INTEGER DEFAULT 0,
                expiry_date DATE,
                features TEXT,
                activated_at TIMESTAMP,
                last_validated TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Audit Logs table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS audit_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                action TEXT NOT NULL,
                entity_type TEXT,
                entity_id INTEGER,
                old_value TEXT,
                new_value TEXT,
                user_info TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create indexes for performance
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_invoices_date ON invoices(date)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_invoices_customer ON invoices(customer_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_invoices_status ON invoices(status)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_invoice_items_invoice ON invoice_items(invoice_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_payments_invoice ON payments(invoice_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_customers_name ON customers(name)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_products_name ON products(name)')
    
    def _seed_defaults(self):
        """Seed default data."""
        cursor = self.connection.cursor()
        
        # Default settings
        defaults = {
            'business_name': 'My Business',
            'business_gstin': '',
            'business_address': '',
            'business_city': '',
            'business_state': 'Maharashtra',
            'business_state_code': '27',
            'business_pincode': '',
            'business_phone': '',
            'business_email': '',
            'business_logo': '',
            'invoice_prefix': 'INV',
            'invoice_start_number': '1',
            'invoice_terms': 'Thank you for your business!',
            'default_gst_rate': '18',
            'enable_igst': '1',
            'currency_symbol': '₹',
            'date_format': '%d/%m/%Y',
        }
        
        for key, value in defaults.items():
            cursor.execute('''
                INSERT OR IGNORE INTO settings (key, value, updated_at)
                VALUES (?, ?, CURRENT_TIMESTAMP)
            ''', (key, value))
        
        # Initialize license if not exists
        cursor.execute('SELECT id FROM license WHERE id = 1')
        if not cursor.fetchone():
            from license.machine_id import get_machine_id
            machine_id = get_machine_id()
            cursor.execute('''
                INSERT INTO license (id, machine_id, plan, invoice_limit, invoices_created)
                VALUES (1, ?, 'TRIAL', 10, 0)
            ''', (machine_id,))
        
        self.connection.commit()
    
    def execute(self, query: str, params: tuple = ()) -> sqlite3.Cursor:
        """Execute a query and return cursor."""
        with self._lock:
            return self.connection.execute(query, params)

    def executemany(self, query: str, params_list: list) -> sqlite3.Cursor:
        """Execute a query with multiple parameter sets."""
        with self._lock:
            return self.connection.executemany(query, params_list)

    def commit(self):
        """Commit current transaction."""
        with self._lock:
            self.connection.commit()

    def rollback(self):
        """Rollback current transaction."""
        with self._lock:
            self.connection.rollback()
    
    def fetchone(self, query: str, params: tuple = ()) -> Optional[sqlite3.Row]:
        """Execute query and fetch one result."""
        cursor = self.execute(query, params)
        return cursor.fetchone()
    
    def fetchall(self, query: str, params: tuple = ()) -> list:
        """Execute query and fetch all results."""
        cursor = self.execute(query, params)
        return cursor.fetchall()
    
    def get_setting(self, key: str, default: str = '') -> str:
        """Get a setting value."""
        result = self.fetchone(
            'SELECT value FROM settings WHERE key = ?', (key,)
        )
        return result['value'] if result else default
    
    def set_setting(self, key: str, value: str):
        """Set a setting value."""
        self.execute('''
            INSERT OR REPLACE INTO settings (key, value, updated_at)
            VALUES (?, ?, CURRENT_TIMESTAMP)
        ''', (key, value))
        self.commit()
    
    def get_settings(self, prefix: str = '') -> dict:
        """Get all settings, optionally filtered by prefix."""
        if prefix:
            rows = self.fetchall(
                'SELECT key, value FROM settings WHERE key LIKE ?',
                (f'{prefix}%',)
            )
        else:
            rows = self.fetchall('SELECT key, value FROM settings')
        return {row['key']: row['value'] for row in rows}
    
    def log_audit(self, action: str, entity_type: str = None, 
                  entity_id: int = None, old_value: str = None, 
                  new_value: str = None):
        """Log an audit entry."""
        with self._lock:
            self.execute('''
                INSERT INTO audit_logs (action, entity_type, entity_id, old_value, new_value)
                VALUES (?, ?, ?, ?, ?)
            ''', (action, entity_type, entity_id, old_value, new_value))
            self.commit()
    
    def backup(self, backup_path: str) -> bool:
        """Create a backup of the database."""
        try:
            import shutil
            self.connection.commit()
            shutil.copy2(self.db_path, backup_path)
            self.log_audit('BACKUP_CREATED', new_value=backup_path)
            return True
        except Exception as e:
            print(f"Backup failed: {e}")
            return False
    
    def restore(self, backup_path: str) -> bool:
        """Restore database from backup."""
        try:
            import shutil
            self.close()
            shutil.copy2(backup_path, self.db_path)
            self._connect()
            self.log_audit('BACKUP_RESTORED', new_value=backup_path)
            return True
        except Exception as e:
            print(f"Restore failed: {e}")
            self._connect()
            return False
    
    def close(self):
        """Close database connection."""
        if self.connection:
            self.connection.close()
            self.connection = None
