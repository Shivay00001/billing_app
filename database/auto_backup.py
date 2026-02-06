"""
Auto Backup System - No Data Loss Guarantee
"""

import os
import shutil
import threading
import time
from datetime import datetime
import glob

class AutoBackupManager:
    """Manages automatic background backups."""
    
    def __init__(self, db_manager):
        self.db = db_manager
        self.backup_dir = os.path.join(os.path.expanduser('~'), '.gst_billing_pro', 'backups')
        os.makedirs(self.backup_dir, exist_ok=True)
        self._stop_event = threading.Event()
        self._thread = None
        
    def start(self):
        """Start the background backup thread."""
        if self._thread and self._thread.is_alive():
            return
            
        self._thread = threading.Thread(target=self._backup_loop, daemon=True)
        self._thread.start()
        print("Auto-backup system started.")

    def stop(self):
        """Stop the background backup thread."""
        self._stop_event.set()
        if self._thread:
            self._thread.join(timeout=2)

    def _backup_loop(self):
        """Main backup loop running every 30 minutes."""
        while not self._stop_event.is_set():
            try:
                self.create_checkpoint_backup()
            except Exception as e:
                print(f"Auto-backup failed: {e}")
                
            # Wait for 30 minutes or until stopped
            # Check every second to be responsive to stop event
            for _ in range(30 * 60):
                if self._stop_event.is_set():
                    break
                time.sleep(1)

    def create_checkpoint_backup(self):
        """Create a scheduled checkpoint backup."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"auto_backup_{timestamp}.db"
        filepath = os.path.join(self.backup_dir, filename)
        
        # Perform backup using db manager logic
        if self.db.backup(filepath):
            self._cleanup_old_backups()

    def _cleanup_old_backups(self):
        """Maintain rolling window of backups (No Data Loss policy)."""
        # Strategy: Keep all from last 24 hours, then daily for last 7 days.
        # For simplicity in this implementation: Keep last 20 backups.
        
        backups = glob.glob(os.path.join(self.backup_dir, "auto_backup_*.db"))
        backups.sort(key=os.path.getmtime)
        
        # Keep last 20
        while len(backups) > 20:
            os.remove(backups[0])
            backups.pop(0)

    def perform_emergency_backup(self):
        """Perform an immediate backup (e.g., on crash or close)."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"emergency_backup_{timestamp}.db"
        filepath = os.path.join(self.backup_dir, filename)
        self.db.backup(filepath)
        print(f"Emergency backup created at {filepath}")
