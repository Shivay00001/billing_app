
import hashlib
import hmac
import base64
import json
import argparse
from datetime import datetime, timedelta

# SECRET_KEY must match the one in the application
SECRET_KEY = b"SECRET_KEY_987654321"  # In production, this would be obscured

def generate_license_key(machine_id, days=365, plan='PRO'):
    """
    Generates a signed license key.
    Format: payload_b64.signature_hex
    Payload: {"mid": machine_id, "exp": "YYYY-MM-DD", "plan": plan}
    """
    expiry_date = (datetime.now() + timedelta(days=days)).strftime('%Y-%m-%d')
    
    payload = {
        "mid": machine_id,
        "exp": expiry_date,
        "plan": plan
    }
    
    payload_str = json.dumps(payload)
    payload_b64 = base64.b64encode(payload_str.encode()).decode()
    
    signature = hmac.new(SECRET_KEY, payload_b64.encode(), hashlib.sha256).hexdigest()
    
    license_key = f"{payload_b64}.{signature}"
    return license_key, expiry_date

if __name__ == "__main__":
    print("=== GST Billing App License Generator ===")
    mid = input("Enter Customer Machine ID: ").strip()
    if not mid:
        print("Machine ID is required.")
        exit(1)
        
    try:
        days = int(input("Enter Validity in Days (default 365): ") or "365")
    except ValueError:
        days = 365
        
    key, exp = generate_license_key(mid, days)
    
    print("\n" + "="*50)
    print(f"LICENSE KEY GENERATED")
    print(f"Machine ID: {mid}")
    print(f"Expiry Date: {exp}")
    print(f"Plan: PRO")
    print("-" * 50)
    print(f"\n{key}\n")
    print("="*50)
    print("Copy the key above and send it to the customer.")
