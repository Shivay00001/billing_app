"""
License Manager - Secure Offline Licensing
"""

from datetime import datetime, date
from typing import Optional
import hashlib
import hmac
import base64
import json
import logging
import urllib.request
import urllib.error

class LicenseManager:
    """Manages secure software licensing with anti-tamper expiry and remote revocation."""
    
    # Must match the key in admin_keygen.py
    SECRET_KEY = b"SECRET_KEY_987654321"
    
    # URL to fetch revoked license IDs (JSON format: ["key1", "key2"])
    # In production, replace with your actual endpoint (e.g., GitHub Gist raw URL)
    REVOCATION_URL = "https://example.com/revoked_licenses.json"
    
    PLANS = {
        'TRIAL': {
            'invoice_limit': 10,
            'pdf_export': False,
            'dashboard': False,
            'charts': False,
            'backup': False,
            'reports': False,
        },
        'PRO': {
            'invoice_limit': -1,
            'pdf_export': True,
            'dashboard': True,
            'charts': True,
            'backup': True,
            'reports': True,
        }
    }
    
    def __init__(self, db_manager):
        self.db = db_manager
        self._license_cache = None

    def get_machine_id(self):
        from license.machine_id import get_machine_id
        return get_machine_id()

    def validate_license(self) -> dict:
        """
        Validate license integrity and expiry.
        Returns: {status, plan, message, expiry_date}
        """
        license_data = self._get_license_data()
        current_mid = self.get_machine_id()
        
        # Default to TRIAL if no license or invalid data
        result = {
            'status': 'invalid',
            'plan': 'TRIAL',
            'message': 'No valid license found.',
            'expiry_date': None
        }

        if not license_data or not license_data.get('license_key'):
            # Check trial limits
            if self._check_trial_exhausted(license_data):
                result['status'] = 'expired'
                result['message'] = 'Trial limit reached. Please activate a license.'
            else:
                result['status'] = 'valid'
                result['message'] = 'Trial Mode'
            return result

        license_key = license_data.get('license_key')
        
        # 1. Validate Signature & Payload
        valid, payload = self._verify_key_signature(license_key)
        if not valid:
            return {'status': 'tampered', 'plan': 'TRIAL', 'message': 'License key is invalid or tampered.'}
            
        # 2. Validate Machine ID Binding
        if payload.get('mid') != current_mid:
            return {'status': 'invalid', 'plan': 'TRIAL', 'message': 'License does not belong to this machine.'}
            
        # 3. Remote Revocation Check (Kill Switch)
        if self._is_revoked(license_key):
             return {'status': 'revoked', 'plan': 'TRIAL', 'message': 'This license has been revoked by the administrator.'}

        # 4. Validate Expiry
        try:
            exp_date = datetime.strptime(payload.get('exp'), '%Y-%m-%d').date()
            if date.today() > exp_date:
                return {
                    'status': 'expired', 
                    'plan': 'TRIAL', 
                    'message': f'License expired on {payload.get("exp")}.',
                    'expiry_date': payload.get("exp")
                }
        except ValueError:
             return {'status': 'invalid', 'plan': 'TRIAL', 'message': 'Invalid expiry date format.'}

        # License is Valid
        return {
            'status': 'valid',
            'plan': payload.get('plan', 'PRO'),
            'expiry_date': payload.get('exp'),
            'message': 'Pro License Active'
        }

    def _verify_key_signature(self, key):
        """Verify the HMAC signature of the key."""
        try:
            if '.' not in key:
                return False, None
                
            payload_b64, signature = key.split('.', 1)
            
            # Re-compute signature
            expected_sig = hmac.new(self.SECRET_KEY, payload_b64.encode(), hashlib.sha256).hexdigest()
            
            if not hmac.compare_digest(signature, expected_sig):
                return False, None
                
            # Decode payload
            payload_json = base64.b64decode(payload_b64).decode()
            payload = json.loads(payload_json)
            return True, payload
        except Exception as e:
            print(f"License verification error: {e}")
            return False, None

    def _check_trial_exhausted(self, license_data):
        if not license_data: return False
        try:
            created = int(license_data.get('invoices_created', 0))
            limit = int(license_data.get('invoice_limit', 10))
            return created >= limit
        except:
            return True

    def activate_license(self, key: str) -> tuple:
        """Attempt to activate a new license key."""
        valid, payload = self._verify_key_signature(key)
        if not valid:
            return False, "Invalid License Key."
            
        if payload.get('mid') != self.get_machine_id():
            return False, "This license key is for a different machine."
            
        # Save to DB
        self.db.set_setting('license_key', key) # Backup in settings
        
        # Update license table
        self.db.execute('''
            UPDATE license SET 
                license_key = ?, 
                plan = ?, 
                expiry_date = ?,
                activated_at = CURRENT_TIMESTAMP 
            WHERE id = 1
        ''', (key, payload['plan'], payload['exp']))
        self.db.commit()
        
        self._license_cache = None
        return True, f"Success! License activated until {payload['exp']}"

    def _get_license_data(self):
        if self._license_cache: return self._license_cache
        res = self.db.fetchone("SELECT * FROM license WHERE id=1")
        if res: self._license_cache = dict(res)
        return self._license_cache

    def get_license_info(self):
        status = self.validate_license()
        return {
            'plan': status['plan'],
            'status': status.get('status'),
            'expiry_date': status.get('expiry_date'),
            'machine_id': self.get_machine_id(),
            'features': self.PLANS.get(status['plan'], self.PLANS['TRIAL'])
        }

    def can_create_invoice(self):
        status = self.validate_license()
        if status['status'] == 'valid': return True, ""
        if status['status'] == 'expired': return False, "License Expired. Contact Admin."
        
        # Check trial
        license_data = self._get_license_data()
            return False, "Trial Limit Reached (10 Invoices). Purchase License."
            
        return True, ""

    def _is_revoked(self, license_key: str) -> bool:
        """
        Check if the license key is in the remote revocation list.
        Uses a short timeout to prevent blocking. Fails safe (allows access on error).
        """
        try:
            # Only check occasionally or on specific events to reduce traffic
            # For this implementation, we check on every validation but with a short timeout
            with urllib.request.urlopen(self.REVOCATION_URL, timeout=2) as response:
                if response.status == 200:
                    data = json.loads(response.read().decode())
                    if license_key in data:
                        logging.warning(f"License {license_key} is revoked.")
                        return True
        except Exception:
            # Fail safe: If internet is down or URL is invalid, assume valid
            pass
            
        return False

    """Manages software licensing and feature restrictions."""
    
    PLANS = {
        'TRIAL': {
            'invoice_limit': 10,
            'pdf_export': False,
            'dashboard': False,
            'charts': False,
            'backup': False,
            'reports': False,
        },
        'BASIC': {
            'invoice_limit': -1,  # Unlimited
            'pdf_export': True,
            'dashboard': True,
            'charts': False,
            'backup': False,
            'reports': True,
        },
        'PRO': {
            'invoice_limit': -1,
            'pdf_export': True,
            'dashboard': True,
            'charts': True,
            'backup': True,
            'reports': True,
        }
    }
    
    def __init__(self, db_manager):
        """Initialize license manager."""
        self.db = db_manager
        self._license_cache = None
    
    def validate_license(self) -> dict:
        """Validate current license status."""
        license_data = self._get_license_data()
        
        if not license_data:
            return {'status': 'invalid', 'plan': 'TRIAL'}
        
        plan = license_data.get('plan', 'TRIAL')
        
        # Check expiry for paid plans
        if plan != 'TRIAL':
            expiry = license_data.get('expiry_date')
            if expiry:
                expiry_date = datetime.strptime(expiry, '%Y-%m-%d').date()
                if date.today() > expiry_date:
                    return {
                        'status': 'expired',
                        'plan': plan,
                        'expiry_date': expiry
                    }
        
        # Check trial limit
        if plan == 'TRIAL':
            invoices_created = license_data.get('invoices_created', 0)
            invoice_limit = license_data.get('invoice_limit', 10)
            if invoices_created >= invoice_limit:
                return {
                    'status': 'trial_exhausted',
                    'plan': 'TRIAL',
                    'invoices_created': invoices_created,
                    'invoice_limit': invoice_limit
                }
        
        return {
            'status': 'valid',
            'plan': plan,
            'expiry_date': license_data.get('expiry_date')
        }
    
    def _get_license_data(self) -> Optional[dict]:
        """Get license data from database."""
        if self._license_cache:
            return self._license_cache
        
        row = self.db.fetchone('SELECT * FROM license WHERE id = 1')
        if row:
            self._license_cache = dict(row)
        return self._license_cache
    
    def get_license_info(self) -> dict:
        """Get license information for display."""
        license_data = self._get_license_data()
        
        if not license_data:
            return {
                'plan': 'TRIAL',
                'invoices_remaining': 10,
                'features': self.PLANS['TRIAL']
            }
        
        plan = license_data.get('plan', 'TRIAL')
        info = {
            'plan': plan,
            'features': self.PLANS.get(plan, self.PLANS['TRIAL']),
            'machine_id': license_data.get('machine_id', ''),
            'expiry_date': license_data.get('expiry_date'),
        }
        
        if plan == 'TRIAL':
            limit = license_data.get('invoice_limit', 10)
            created = license_data.get('invoices_created', 0)
            info['invoices_remaining'] = max(0, limit - created)
            info['invoices_created'] = created
        
        return info
    
    def can_create_invoice(self) -> tuple:
        """Check if user can create a new invoice. Returns (bool, message)."""
        status = self.validate_license()
        
        if status['status'] == 'expired':
            return False, "License expired. Please renew to continue."
        
        if status['status'] == 'trial_exhausted':
            return False, "Trial limit reached. Upgrade to continue."
        
        return True, ""
    
    def has_feature(self, feature: str) -> bool:
        """Check if current plan has a specific feature."""
        info = self.get_license_info()
        features = info.get('features', {})
        return features.get(feature, False)
    
    def activate_license(self, license_key: str) -> tuple:
        """Activate a license key. Returns (success, message)."""
        # Validate key format
        if not self._validate_key_format(license_key):
            return False, "Invalid license key format."
        
        # Decode and validate key
        key_data = self._decode_license_key(license_key)
        if not key_data:
            return False, "Invalid license key."
        
        # Get machine ID
        from license.machine_id import get_machine_id
        machine_id = get_machine_id()
        
        # Update database
        self.db.execute('''
            UPDATE license SET
                license_key = ?,
                plan = ?,
                expiry_date = ?,
                activated_at = CURRENT_TIMESTAMP,
                last_validated = CURRENT_TIMESTAMP
            WHERE id = 1
        ''', (license_key, key_data['plan'], key_data['expiry']))
        self.db.commit()
        
        self._license_cache = None  # Clear cache
        self.db.log_audit('LICENSE_ACTIVATED', 'license', 1, new_value=key_data['plan'])
        
        return True, f"License activated: {key_data['plan']} plan"
    
    def _validate_key_format(self, key: str) -> bool:
        """Validate license key format."""
        # Expected format: XXXX-XXXX-XXXX-XXXX
        parts = key.split('-')
        if len(parts) != 4:
            return False
        return all(len(p) == 4 and p.isalnum() for p in parts)
    
    def _decode_license_key(self, key: str) -> Optional[dict]:
        """Decode and validate license key."""
        try:
            # Remove dashes
            clean_key = key.replace('-', '')
            
            # For demo: simple key structure
            # First 4 chars: plan code, Last 12: hash
            plan_code = clean_key[:4].upper()
            
            plan_map = {
                'BSIC': 'BASIC',
                'PROF': 'PRO',
            }
            
            plan = plan_map.get(plan_code)
            if not plan:
                return None
            
            # Calculate expiry (1 year from activation for demo)
            expiry = (date.today() + timedelta(days=365)).strftime('%Y-%m-%d')
            
            return {
                'plan': plan,
                'expiry': expiry
            }
        except Exception:
            return None
    
    def refresh_cache(self):
        """Refresh the license cache."""
        self._license_cache = None
        self._get_license_data()
