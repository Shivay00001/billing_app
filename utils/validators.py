"""
Validators Utility - Input validation helpers
"""

import re

def validate_gstin(gstin: str) -> bool:
    """Validate GSTIN format (15 chars, alphanumeric pattern)."""
    if not gstin:
        return True # Optional
    pattern = re.compile(r'^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$')
    return bool(pattern.match(gstin.upper()))

def validate_phone(phone: str) -> bool:
    """Validate Indian phone number."""
    if not phone:
        return True
    pattern = re.compile(r'^[6-9]\d{9}$')
    return bool(pattern.match(phone))

def validate_email(email: str) -> bool:
    """Validate email address."""
    if not email:
        return True
    pattern = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    return bool(pattern.match(email))

def validate_numeric(value: str) -> bool:
    """Validate numeric input."""
    try:
        float(value)
        return True
    except ValueError:
        return False
