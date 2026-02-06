"""
Payments Configuration - UPI and Payment Gateway Settings
"""

import os
import qrcode
from PIL import Image
import shutil
from typing import Optional

class PaymentConfigManager:
    """Manages payment settings and QR generation."""
    
    def __init__(self, db_manager):
        self.db = db_manager
        self.assets_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets')
        os.makedirs(self.assets_dir, exist_ok=True)
        
    def save_upi_config(self, vpa: str, payee_name: str, notes: str = ''):
        """Save UPI configuration to settings."""
        self.db.set_setting('payment_upi_vpa', vpa)
        self.db.set_setting('payment_payee_name', payee_name)
        self.db.set_setting('payment_notes', notes)
        
    def save_gateway_config(self, gateway_name: str, api_key: str, secret_key: str):
        """Save Payment Gateway configuration (e.g., Razorpay/Stripe)."""
        self.db.set_setting('payment_gateway_name', gateway_name)
        # In a real app, encrypt these keys!
        self.db.set_setting('payment_gateway_key', api_key)
        self.db.set_setting('payment_gateway_secret', secret_key)
        
    def upload_qr_image(self, filepath: str) -> str:
        """Upload a static QR code image."""
        try:
            filename = "static_qr.png"
            dest_path = os.path.join(self.assets_dir, filename)
            shutil.copy2(filepath, dest_path)
            self.db.set_setting('payment_qr_type', 'STATIC')
            self.db.set_setting('payment_qr_path', dest_path)
            return dest_path
        except Exception as e:
            print(f"Failed to upload QR: {e}")
            return ""

    def generate_dynamic_qr(self, amount: float, invoice_no: str) -> str:
        """Generate a dynamic UPI QR code for a specific amount."""
        vpa = self.db.get_setting('payment_upi_vpa', '')
        name = self.db.get_setting('payment_payee_name', '')
        
        if not vpa:
            return ""
            
        # UPI URL Format: upi://pay?pa=ADDRESS&pn=NAME&am=AMOUNT&tr=REF_ID&tn=NOTE
        # Note: tn (transaction note) length is limited, keep it short
        amount_str = f"{amount:.2f}"
        note = f"Inv {invoice_no}"
        
        # Proper encoding is handled by qrcode lib usually, but constructing string primarily
        upi_url = f"upi://pay?pa={vpa}&pn={name}&am={amount_str}&tr={invoice_no}&tn={note}"
        
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(upi_url)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Save to temp file
        filename = f"dynamic_qr_{invoice_no}.png"
        path = os.path.join(self.assets_dir, filename)
        img.save(path)
        
        return path

    def get_qr_path_for_invoice(self, amount: float, invoice_no: str) -> str:
        """Get the appropriate QR code path (Static or Dynamic)."""
        qr_type = self.db.get_setting('payment_qr_type', 'NONE')
        
        if qr_type == 'STATIC':
            return self.db.get_setting('payment_qr_path', '')
        elif qr_type == 'DYNAMIC':
            return self.generate_dynamic_qr(amount, invoice_no)
        else:
            return ""
