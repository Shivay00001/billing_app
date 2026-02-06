"""
Data Models - ORM-like operations for database entities
"""

from dataclasses import dataclass, field, asdict
from datetime import date, datetime
from typing import Optional, List
from decimal import Decimal
import json


@dataclass
class Customer:
    """Customer data model."""
    id: Optional[int] = None
    name: str = ''
    gstin: str = ''
    phone: str = ''
    email: str = ''
    address: str = ''
    city: str = ''
    state: str = ''
    state_code: str = ''
    pincode: str = ''
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def to_dict(self) -> dict:
        return {k: v for k, v in asdict(self).items() if v is not None}
    
    @classmethod
    def from_row(cls, row) -> 'Customer':
        if row is None:
            return None
        return cls(**{k: row[k] for k in row.keys()})


@dataclass
class Product:
    """Product/Service data model."""
    id: Optional[int] = None
    name: str = ''
    hsn_sac: str = ''
    unit: str = 'NOS'
    rate: float = 0.0
    gst_rate: float = 18.0
    description: str = ''
    is_service: bool = False
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def to_dict(self) -> dict:
        return {k: v for k, v in asdict(self).items() if v is not None}
    
    @classmethod
    def from_row(cls, row) -> 'Product':
        if row is None:
            return None
        return cls(**{k: row[k] for k in row.keys()})


@dataclass
class InvoiceItem:
    """Invoice line item data model."""
    id: Optional[int] = None
    invoice_id: Optional[int] = None
    product_id: Optional[int] = None
    sr_no: int = 1
    description: str = ''
    hsn_sac: str = ''
    quantity: float = 1.0
    unit: str = 'NOS'
    rate: float = 0.0
    discount_percent: float = 0.0
    discount_amount: float = 0.0
    taxable_amount: float = 0.0
    gst_rate: float = 0.0
    cgst_rate: float = 0.0
    cgst_amount: float = 0.0
    sgst_rate: float = 0.0
    sgst_amount: float = 0.0
    igst_rate: float = 0.0
    igst_amount: float = 0.0
    total: float = 0.0
    
    def calculate(self, is_igst: bool = False):
        """Calculate item amounts."""
        # Gross amount
        gross = self.quantity * self.rate
        
        # Apply discount
        if self.discount_percent > 0:
            self.discount_amount = round(gross * self.discount_percent / 100, 2)
        self.taxable_amount = round(gross - self.discount_amount, 2)
        
        # Calculate tax
        if is_igst:
            self.igst_rate = self.gst_rate
            self.igst_amount = round(self.taxable_amount * self.igst_rate / 100, 2)
            self.cgst_rate = 0
            self.cgst_amount = 0
            self.sgst_rate = 0
            self.sgst_amount = 0
        else:
            self.cgst_rate = self.gst_rate / 2
            self.sgst_rate = self.gst_rate / 2
            self.cgst_amount = round(self.taxable_amount * self.cgst_rate / 100, 2)
            self.sgst_amount = round(self.taxable_amount * self.sgst_rate / 100, 2)
            self.igst_rate = 0
            self.igst_amount = 0
        
        # Total
        self.total = round(
            self.taxable_amount + self.cgst_amount + self.sgst_amount + self.igst_amount,
            2
        )
    
    def to_dict(self) -> dict:
        return {k: v for k, v in asdict(self).items() if v is not None}
    
    @classmethod
    def from_row(cls, row) -> 'InvoiceItem':
        if row is None:
            return None
        return cls(**{k: row[k] for k in row.keys()})


@dataclass
class Invoice:
    """Invoice data model."""
    id: Optional[int] = None
    invoice_number: str = ''
    invoice_type: str = 'GST'  # GST, NON_GST, ESTIMATE, PROFORMA
    date: Optional[date] = None
    due_date: Optional[date] = None
    customer_id: Optional[int] = None
    customer_name: str = ''
    customer_gstin: str = ''
    customer_address: str = ''
    customer_state: str = ''
    customer_state_code: str = ''
    subtotal: float = 0.0
    discount_type: str = 'PERCENT'  # PERCENT, AMOUNT
    discount_value: float = 0.0
    discount_amount: float = 0.0
    taxable_amount: float = 0.0
    cgst_amount: float = 0.0
    sgst_amount: float = 0.0
    igst_amount: float = 0.0
    round_off: float = 0.0
    total: float = 0.0
    amount_paid: float = 0.0
    payment_status: str = 'UNPAID'  # UNPAID, PARTIAL, PAID
    payment_method: str = ''
    notes: str = ''
    terms: str = ''
    status: str = 'ACTIVE'  # ACTIVE, CANCELLED
    items: List[InvoiceItem] = field(default_factory=list)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def calculate_totals(self, business_state_code: str = ''):
        """Calculate all invoice totals."""
        # Determine if IGST applies (inter-state)
        is_igst = (
            self.customer_state_code and 
            business_state_code and 
            self.customer_state_code != business_state_code
        )
        
        # Calculate each item
        self.subtotal = 0
        self.taxable_amount = 0
        self.cgst_amount = 0
        self.sgst_amount = 0
        self.igst_amount = 0
        
        for item in self.items:
            item.calculate(is_igst)
            self.subtotal += item.quantity * item.rate
            self.taxable_amount += item.taxable_amount
            self.cgst_amount += item.cgst_amount
            self.sgst_amount += item.sgst_amount
            self.igst_amount += item.igst_amount
        
        # Apply bill-level discount
        if self.discount_value > 0:
            if self.discount_type == 'PERCENT':
                self.discount_amount = round(self.subtotal * self.discount_value / 100, 2)
            else:
                self.discount_amount = self.discount_value
            
            # Proportionally reduce tax
            if self.subtotal > 0:
                discount_ratio = self.discount_amount / self.subtotal
                self.taxable_amount = round(self.taxable_amount * (1 - discount_ratio), 2)
                self.cgst_amount = round(self.cgst_amount * (1 - discount_ratio), 2)
                self.sgst_amount = round(self.sgst_amount * (1 - discount_ratio), 2)
                self.igst_amount = round(self.igst_amount * (1 - discount_ratio), 2)
        
        # Calculate total before round-off
        total_before_round = (
            self.taxable_amount + 
            self.cgst_amount + 
            self.sgst_amount + 
            self.igst_amount
        )
        
        # Round off to nearest rupee
        rounded_total = round(total_before_round)
        self.round_off = round(rounded_total - total_before_round, 2)
        self.total = rounded_total
        
        # Update payment status
        self._update_payment_status()
    
    def _update_payment_status(self):
        """Update payment status based on amount paid."""
        if self.amount_paid >= self.total:
            self.payment_status = 'PAID'
        elif self.amount_paid > 0:
            self.payment_status = 'PARTIAL'
        else:
            self.payment_status = 'UNPAID'
    
    def to_dict(self) -> dict:
        d = asdict(self)
        d.pop('items', None)
        return {k: v for k, v in d.items() if v is not None}
    
    @classmethod
    def from_row(cls, row) -> 'Invoice':
        if row is None:
            return None
        return cls(**{k: row[k] for k in row.keys() if k != 'items'})


@dataclass
class Payment:
    """Payment data model."""
    id: Optional[int] = None
    invoice_id: int = 0
    amount: float = 0.0
    method: str = 'CASH'  # CASH, UPI, BANK, CARD, CHEQUE
    reference: str = ''
    date: Optional[date] = None
    notes: str = ''
    created_at: Optional[datetime] = None
    
    def to_dict(self) -> dict:
        return {k: v for k, v in asdict(self).items() if v is not None}
    
    @classmethod
    def from_row(cls, row) -> 'Payment':
        if row is None:
            return None
        return cls(**{k: row[k] for k in row.keys()})


class CustomerRepository:
    """Repository for Customer CRUD operations."""
    
    def __init__(self, db_manager):
        self.db = db_manager
    
    def create(self, customer: Customer) -> int:
        """Create a new customer."""
        cursor = self.db.execute('''
            INSERT INTO customers (name, gstin, phone, email, address, city, state, state_code, pincode)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (customer.name, customer.gstin, customer.phone, customer.email,
              customer.address, customer.city, customer.state, customer.state_code, customer.pincode))
        self.db.commit()
        customer.id = cursor.lastrowid
        self.db.log_audit('CUSTOMER_CREATED', 'customer', customer.id)
        return customer.id
    
    def update(self, customer: Customer) -> bool:
        """Update an existing customer."""
        self.db.execute('''
            UPDATE customers SET
                name = ?, gstin = ?, phone = ?, email = ?, address = ?,
                city = ?, state = ?, state_code = ?, pincode = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (customer.name, customer.gstin, customer.phone, customer.email,
              customer.address, customer.city, customer.state, customer.state_code,
              customer.pincode, customer.id))
        self.db.commit()
        self.db.log_audit('CUSTOMER_UPDATED', 'customer', customer.id)
        return True
    
    def delete(self, customer_id: int) -> bool:
        """Delete a customer."""
        self.db.execute('DELETE FROM customers WHERE id = ?', (customer_id,))
        self.db.commit()
        self.db.log_audit('CUSTOMER_DELETED', 'customer', customer_id)
        return True
    
    def get_by_id(self, customer_id: int) -> Optional[Customer]:
        """Get customer by ID."""
        row = self.db.fetchone('SELECT * FROM customers WHERE id = ?', (customer_id,))
        return Customer.from_row(row)
    
    def get_all(self, search: str = '', limit: int = 100, offset: int = 0) -> List[Customer]:
        """Get all customers with optional search."""
        if search:
            rows = self.db.fetchall('''
                SELECT * FROM customers 
                WHERE name LIKE ? OR gstin LIKE ? OR phone LIKE ?
                ORDER BY name
                LIMIT ? OFFSET ?
            ''', (f'%{search}%', f'%{search}%', f'%{search}%', limit, offset))
        else:
            rows = self.db.fetchall('''
                SELECT * FROM customers ORDER BY name LIMIT ? OFFSET ?
            ''', (limit, offset))
        return [Customer.from_row(row) for row in rows]
    
    def count(self, search: str = '') -> int:
        """Count customers."""
        if search:
            result = self.db.fetchone('''
                SELECT COUNT(*) as count FROM customers 
                WHERE name LIKE ? OR gstin LIKE ? OR phone LIKE ?
            ''', (f'%{search}%', f'%{search}%', f'%{search}%'))
        else:
            result = self.db.fetchone('SELECT COUNT(*) as count FROM customers')
        return result['count'] if result else 0


class ProductRepository:
    """Repository for Product CRUD operations."""
    
    def __init__(self, db_manager):
        self.db = db_manager
    
    def create(self, product: Product) -> int:
        """Create a new product."""
        cursor = self.db.execute('''
            INSERT INTO products (name, hsn_sac, unit, rate, gst_rate, description, is_service)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (product.name, product.hsn_sac, product.unit, product.rate,
              product.gst_rate, product.description, int(product.is_service)))
        self.db.commit()
        product.id = cursor.lastrowid
        self.db.log_audit('PRODUCT_CREATED', 'product', product.id)
        return product.id
    
    def update(self, product: Product) -> bool:
        """Update an existing product."""
        self.db.execute('''
            UPDATE products SET
                name = ?, hsn_sac = ?, unit = ?, rate = ?, gst_rate = ?,
                description = ?, is_service = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (product.name, product.hsn_sac, product.unit, product.rate,
              product.gst_rate, product.description, int(product.is_service), product.id))
        self.db.commit()
        self.db.log_audit('PRODUCT_UPDATED', 'product', product.id)
        return True
    
    def delete(self, product_id: int) -> bool:
        """Delete a product."""
        self.db.execute('DELETE FROM products WHERE id = ?', (product_id,))
        self.db.commit()
        self.db.log_audit('PRODUCT_DELETED', 'product', product_id)
        return True
    
    def get_by_id(self, product_id: int) -> Optional[Product]:
        """Get product by ID."""
        row = self.db.fetchone('SELECT * FROM products WHERE id = ?', (product_id,))
        return Product.from_row(row)
    
    def get_all(self, search: str = '', limit: int = 100, offset: int = 0) -> List[Product]:
        """Get all products with optional search."""
        if search:
            rows = self.db.fetchall('''
                SELECT * FROM products 
                WHERE name LIKE ? OR hsn_sac LIKE ?
                ORDER BY name
                LIMIT ? OFFSET ?
            ''', (f'%{search}%', f'%{search}%', limit, offset))
        else:
            rows = self.db.fetchall('''
                SELECT * FROM products ORDER BY name LIMIT ? OFFSET ?
            ''', (limit, offset))
        return [Product.from_row(row) for row in rows]
    
    def count(self, search: str = '') -> int:
        """Count products."""
        if search:
            result = self.db.fetchone('''
                SELECT COUNT(*) as count FROM products 
                WHERE name LIKE ? OR hsn_sac LIKE ?
            ''', (f'%{search}%', f'%{search}%'))
        else:
            result = self.db.fetchone('SELECT COUNT(*) as count FROM products')
        return result['count'] if result else 0


class InvoiceRepository:
    """Repository for Invoice CRUD operations."""
    
    def __init__(self, db_manager):
        self.db = db_manager
    
    def create(self, invoice: Invoice) -> int:
        """Create a new invoice with items."""
        cursor = self.db.execute('''
            INSERT INTO invoices (
                invoice_number, invoice_type, date, due_date,
                customer_id, customer_name, customer_gstin, customer_address,
                customer_state, customer_state_code,
                subtotal, discount_type, discount_value, discount_amount,
                taxable_amount, cgst_amount, sgst_amount, igst_amount,
                round_off, total, amount_paid, payment_status, payment_method,
                notes, terms, status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            invoice.invoice_number, invoice.invoice_type, invoice.date, invoice.due_date,
            invoice.customer_id, invoice.customer_name, invoice.customer_gstin,
            invoice.customer_address, invoice.customer_state, invoice.customer_state_code,
            invoice.subtotal, invoice.discount_type, invoice.discount_value, invoice.discount_amount,
            invoice.taxable_amount, invoice.cgst_amount, invoice.sgst_amount, invoice.igst_amount,
            invoice.round_off, invoice.total, invoice.amount_paid, invoice.payment_status,
            invoice.payment_method, invoice.notes, invoice.terms, invoice.status
        ))
        invoice.id = cursor.lastrowid
        
        # Insert items
        for item in invoice.items:
            item.invoice_id = invoice.id
            self._create_item(item)
        
        self.db.commit()
        
        # Update license invoice count
        self._increment_invoice_count()
        
        self.db.log_audit('INVOICE_CREATED', 'invoice', invoice.id)
        return invoice.id
    
    def _create_item(self, item: InvoiceItem):
        """Create an invoice item."""
        self.db.execute('''
            INSERT INTO invoice_items (
                invoice_id, product_id, sr_no, description, hsn_sac,
                quantity, unit, rate, discount_percent, discount_amount,
                taxable_amount, gst_rate, cgst_rate, cgst_amount,
                sgst_rate, sgst_amount, igst_rate, igst_amount, total
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            item.invoice_id, item.product_id, item.sr_no, item.description, item.hsn_sac,
            item.quantity, item.unit, item.rate, item.discount_percent, item.discount_amount,
            item.taxable_amount, item.gst_rate, item.cgst_rate, item.cgst_amount,
            item.sgst_rate, item.sgst_amount, item.igst_rate, item.igst_amount, item.total
        ))
    
    def _increment_invoice_count(self):
        """Increment the invoice count for trial tracking."""
        self.db.execute('''
            UPDATE license SET invoices_created = invoices_created + 1 WHERE id = 1
        ''')
    
    def update(self, invoice: Invoice) -> bool:
        """Update an existing invoice."""
        self.db.execute('''
            UPDATE invoices SET
                invoice_type = ?, date = ?, due_date = ?,
                customer_id = ?, customer_name = ?, customer_gstin = ?,
                customer_address = ?, customer_state = ?, customer_state_code = ?,
                subtotal = ?, discount_type = ?, discount_value = ?, discount_amount = ?,
                taxable_amount = ?, cgst_amount = ?, sgst_amount = ?, igst_amount = ?,
                round_off = ?, total = ?, amount_paid = ?, payment_status = ?,
                payment_method = ?, notes = ?, terms = ?, status = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (
            invoice.invoice_type, invoice.date, invoice.due_date,
            invoice.customer_id, invoice.customer_name, invoice.customer_gstin,
            invoice.customer_address, invoice.customer_state, invoice.customer_state_code,
            invoice.subtotal, invoice.discount_type, invoice.discount_value, invoice.discount_amount,
            invoice.taxable_amount, invoice.cgst_amount, invoice.sgst_amount, invoice.igst_amount,
            invoice.round_off, invoice.total, invoice.amount_paid, invoice.payment_status,
            invoice.payment_method, invoice.notes, invoice.terms, invoice.status, invoice.id
        ))
        
        # Delete existing items and re-insert
        self.db.execute('DELETE FROM invoice_items WHERE invoice_id = ?', (invoice.id,))
        for item in invoice.items:
            item.invoice_id = invoice.id
            self._create_item(item)
        
        self.db.commit()
        self.db.log_audit('INVOICE_UPDATED', 'invoice', invoice.id)
        return True
    
    def cancel(self, invoice_id: int) -> bool:
        """Cancel an invoice."""
        self.db.execute('''
            UPDATE invoices SET status = 'CANCELLED', updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (invoice_id,))
        self.db.commit()
        self.db.log_audit('INVOICE_CANCELLED', 'invoice', invoice_id)
        return True
    
    def get_by_id(self, invoice_id: int) -> Optional[Invoice]:
        """Get invoice by ID with items."""
        row = self.db.fetchone('SELECT * FROM invoices WHERE id = ?', (invoice_id,))
        if not row:
            return None
        
        invoice = Invoice.from_row(row)
        
        # Load items
        item_rows = self.db.fetchall(
            'SELECT * FROM invoice_items WHERE invoice_id = ? ORDER BY sr_no',
            (invoice_id,)
        )
        invoice.items = [InvoiceItem.from_row(r) for r in item_rows]
        
        return invoice
    
    def get_by_number(self, invoice_number: str) -> Optional[Invoice]:
        """Get invoice by invoice number."""
        row = self.db.fetchone(
            'SELECT * FROM invoices WHERE invoice_number = ?', 
            (invoice_number,)
        )
        if not row:
            return None
        return self.get_by_id(row['id'])
    
    def get_all(self, filters: dict = None, limit: int = 100, offset: int = 0) -> List[Invoice]:
        """Get all invoices with optional filters."""
        query = 'SELECT * FROM invoices WHERE 1=1'
        params = []
        
        if filters:
            if filters.get('invoice_type'):
                query += ' AND invoice_type = ?'
                params.append(filters['invoice_type'])
            if filters.get('status'):
                query += ' AND status = ?'
                params.append(filters['status'])
            if filters.get('payment_status'):
                query += ' AND payment_status = ?'
                params.append(filters['payment_status'])
            if filters.get('customer_id'):
                query += ' AND customer_id = ?'
                params.append(filters['customer_id'])
            if filters.get('date_from'):
                query += ' AND date >= ?'
                params.append(filters['date_from'])
            if filters.get('date_to'):
                query += ' AND date <= ?'
                params.append(filters['date_to'])
            if filters.get('search'):
                query += ' AND (invoice_number LIKE ? OR customer_name LIKE ?)'
                params.extend([f"%{filters['search']}%", f"%{filters['search']}%"])
        
        query += ' ORDER BY date DESC, id DESC LIMIT ? OFFSET ?'
        params.extend([limit, offset])
        
        rows = self.db.fetchall(query, tuple(params))
        return [Invoice.from_row(row) for row in rows]
    
    def count(self, filters: dict = None) -> int:
        """Count invoices."""
        query = 'SELECT COUNT(*) as count FROM invoices WHERE 1=1'
        params = []
        
        if filters:
            if filters.get('invoice_type'):
                query += ' AND invoice_type = ?'
                params.append(filters['invoice_type'])
            if filters.get('status'):
                query += ' AND status = ?'
                params.append(filters['status'])
            if filters.get('date_from'):
                query += ' AND date >= ?'
                params.append(filters['date_from'])
            if filters.get('date_to'):
                query += ' AND date <= ?'
                params.append(filters['date_to'])
        
        result = self.db.fetchone(query, tuple(params))
        return result['count'] if result else 0
    
    def get_next_invoice_number(self, prefix: str = 'INV') -> str:
        """Generate next invoice number."""
        result = self.db.fetchone('''
            SELECT invoice_number FROM invoices 
            WHERE invoice_number LIKE ? 
            ORDER BY id DESC LIMIT 1
        ''', (f'{prefix}%',))
        
        if result:
            # Extract number from last invoice
            last_num = result['invoice_number'].replace(prefix, '').replace('-', '')
            try:
                next_num = int(last_num) + 1
            except ValueError:
                next_num = 1
        else:
            # Get starting number from settings
            start = self.db.get_setting('invoice_start_number', '1')
            next_num = int(start)
        
        return f"{prefix}-{next_num:05d}"
    
    def duplicate(self, invoice_id: int) -> Optional[Invoice]:
        """Create a duplicate of an invoice."""
        original = self.get_by_id(invoice_id)
        if not original:
            return None
        
        # Reset for new invoice
        original.id = None
        original.invoice_number = self.get_next_invoice_number(
            self.db.get_setting('invoice_prefix', 'INV')
        )
        original.date = date.today()
        original.due_date = None
        original.status = 'ACTIVE'
        original.payment_status = 'UNPAID'
        original.amount_paid = 0
        
        for item in original.items:
            item.id = None
            item.invoice_id = None
        
        return original


class PaymentRepository:
    """Repository for Payment operations."""
    
    def __init__(self, db_manager):
        self.db = db_manager
    
    def create(self, payment: Payment) -> int:
        """Create a payment and update invoice."""
        cursor = self.db.execute('''
            INSERT INTO payments (invoice_id, amount, method, reference, date, notes)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (payment.invoice_id, payment.amount, payment.method,
              payment.reference, payment.date, payment.notes))
        payment.id = cursor.lastrowid
        
        # Update invoice amount_paid
        self.db.execute('''
            UPDATE invoices SET 
                amount_paid = amount_paid + ?,
                payment_status = CASE 
                    WHEN amount_paid + ? >= total THEN 'PAID'
                    WHEN amount_paid + ? > 0 THEN 'PARTIAL'
                    ELSE 'UNPAID'
                END,
                payment_method = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (payment.amount, payment.amount, payment.amount, payment.method, payment.invoice_id))
        
        self.db.commit()
        self.db.log_audit('PAYMENT_CREATED', 'payment', payment.id)
        return payment.id
    
    def get_by_invoice(self, invoice_id: int) -> List[Payment]:
        """Get all payments for an invoice."""
        rows = self.db.fetchall(
            'SELECT * FROM payments WHERE invoice_id = ? ORDER BY date DESC',
            (invoice_id,)
        )
        return [Payment.from_row(row) for row in rows]
    
    def get_total_by_method(self, date_from: date = None, date_to: date = None) -> dict:
        """Get total payments grouped by method."""
        query = 'SELECT method, SUM(amount) as total FROM payments WHERE 1=1'
        params = []
        
        if date_from:
            query += ' AND date >= ?'
            params.append(date_from)
        if date_to:
            query += ' AND date <= ?'
            params.append(date_to)
        
        query += ' GROUP BY method'
        
        rows = self.db.fetchall(query, tuple(params))
        return {row['method']: row['total'] for row in rows}
