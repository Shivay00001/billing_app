"""
Machine ID Generator - Unique machine fingerprint for license binding
"""

import hashlib
import platform
import subprocess
import uuid


def get_machine_id() -> str:
    """Generate a unique machine identifier based on hardware."""
    components = []
    
    # Get CPU ID (Windows)
    if platform.system() == 'Windows':
        try:
            result = subprocess.run(
                ['wmic', 'cpu', 'get', 'processorid'],
                capture_output=True, text=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            lines = result.stdout.strip().split('\n')
            if len(lines) >= 2:
                components.append(lines[1].strip())
        except Exception:
            pass
    
    # Fallback: MAC address and hostname
    if not components:
        components.append(hex(uuid.getnode()))
        components.append(platform.node())
    
    # Create hash
    combined = '|'.join(components)
    return hashlib.sha256(combined.encode()).hexdigest()[:32].upper()


def validate_machine_id(stored_id: str) -> bool:
    """Validate current machine matches stored ID."""
    return get_machine_id() == stored_id
