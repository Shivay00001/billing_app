"""
Advanced Billing & GST Desktop Application
Main Application Entry Point

A production-ready billing solution for Indian SMBs
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.db_init import DatabaseManager
from database.auto_backup import AutoBackupManager
from license.license_manager import LicenseManager
from core.navigation import NavigationManager
from core.theme import ThemeManager


class BillingApplication:
    """Main application class for the Billing & GST Desktop Application."""
    
    APP_NAME = "GST Billing Pro"
    APP_VERSION = "1.0.0"
    MIN_WIDTH = 1024
    MIN_HEIGHT = 700
    
    def __init__(self):
        """Initialize the application."""
        self.root = tk.Tk()
        self.root.title(f"{self.APP_NAME} v{self.APP_VERSION}")
        self.root.geometry(f"{self.MIN_WIDTH}x{self.MIN_HEIGHT}")
        self.root.minsize(self.MIN_WIDTH, self.MIN_HEIGHT)
        
        # Set App Icon
        try:
            icon_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'assets', 'icon.ico')
            if os.path.exists(icon_path):
                self.root.iconbitmap(icon_path)
            else:
                print(f"Icon not found at: {icon_path}")
        except Exception as e:
            print(f"Failed to load icon: {e}")
        
        # Center window on screen
        self._center_window()
        
        # Initialize managers
        self.db_manager = DatabaseManager()
        self.backup_manager = AutoBackupManager(self.db_manager)
        self.license_manager = LicenseManager(self.db_manager)
        self.theme_manager = ThemeManager(self.root)
        
        # Start auto-backup
        self.backup_manager.start()
        
        # Apply modern theme
        self.theme_manager.apply_theme()
        
        # Check license before proceeding
        if not self._validate_license():
            return
        
        # Setup main UI
        self._setup_ui()
        
        # Bind keyboard shortcuts
        self._bind_shortcuts()
        
        # Handle window close
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
    
    def _center_window(self):
        """Center the application window on screen."""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f"{self.MIN_WIDTH}x{self.MIN_HEIGHT}+{x}+{y}")
    
    def _validate_license(self) -> bool:
        """Validate the software license."""
        license_status = self.license_manager.validate_license()
        
        if license_status['status'] == 'expired':
            messagebox.showerror(
                "License Expired",
                "Your license has expired. Please renew to continue using the software.\n\n"
                f"Expired on: {license_status.get('expiry_date', 'Unknown')}"
            )
            self.root.destroy()
            return False
        
        if license_status['status'] == 'invalid':
            # Show activation dialog
            self._show_activation_dialog()
            return True  # Allow trial mode
        
        return True
    
    def _show_activation_dialog(self):
        """Show license activation dialog for new installations."""
        # This will be handled by the license manager UI
        pass
    
    def _setup_ui(self):
        """Setup the main application UI."""
        # Main container
        self.main_container = ttk.Frame(self.root)
        self.main_container.pack(fill=tk.BOTH, expand=True)
        
        # Create navigation manager
        self.nav_manager = NavigationManager(
            self.main_container,
            self.db_manager,
            self.license_manager
        )
        
        # Setup navigation
        self.nav_manager.setup()
    
    def _bind_shortcuts(self):
        """Bind keyboard shortcuts."""
        # Navigation shortcuts
        self.root.bind('<Control-Key-1>', lambda e: self.nav_manager.navigate('dashboard'))
        self.root.bind('<Control-Key-2>', lambda e: self.nav_manager.navigate('new_invoice'))
        self.root.bind('<Control-Key-3>', lambda e: self.nav_manager.navigate('invoices'))
        self.root.bind('<Control-Key-4>', lambda e: self.nav_manager.navigate('customers'))
        self.root.bind('<Control-Key-5>', lambda e: self.nav_manager.navigate('products'))
        self.root.bind('<Control-Key-6>', lambda e: self.nav_manager.navigate('reports'))
        self.root.bind('<Control-Key-7>', lambda e: self.nav_manager.navigate('settings'))
        
        # Quick actions
        self.root.bind('<Control-n>', lambda e: self.nav_manager.navigate('new_invoice'))
        self.root.bind('<Control-p>', lambda e: self._quick_print())
        self.root.bind('<Control-s>', lambda e: self._quick_save())
        self.root.bind('<F1>', lambda e: self._show_help())
        self.root.bind('<Escape>', lambda e: self._handle_escape())
    
    def _quick_print(self):
        """Handle quick print shortcut."""
        current_view = self.nav_manager.get_current_view()
        if hasattr(current_view, 'print_current'):
            current_view.print_current()
    
    def _quick_save(self):
        """Handle quick save shortcut."""
        current_view = self.nav_manager.get_current_view()
        if hasattr(current_view, 'save_current'):
            current_view.save_current()
    
    def _show_help(self):
        """Show help dialog."""
        help_text = """
GST Billing Pro - Keyboard Shortcuts

Navigation:
  Ctrl+1  Dashboard
  Ctrl+2  New Invoice
  Ctrl+3  Invoices List
  Ctrl+4  Customers
  Ctrl+5  Products
  Ctrl+6  Reports
  Ctrl+7  Settings

Actions:
  Ctrl+N  New Invoice
  Ctrl+S  Save Current
  Ctrl+P  Print Current
  F1      Help
  Esc     Cancel/Close Dialog
        """
        messagebox.showinfo("Help - Keyboard Shortcuts", help_text.strip())
    
    def _handle_escape(self):
        """Handle escape key press."""
        current_view = self.nav_manager.get_current_view()
        if hasattr(current_view, 'handle_escape'):
            current_view.handle_escape()
    
    def _on_closing(self):
        """Handle application close."""
        # Check for unsaved changes
        current_view = self.nav_manager.get_current_view()
        if hasattr(current_view, 'has_unsaved_changes') and current_view.has_unsaved_changes():
            result = messagebox.askyesnocancel(
                "Unsaved Changes",
                "You have unsaved changes. Do you want to save before closing?"
            )
            if result is None:  # Cancel
                return
            if result:  # Yes
                current_view.save_current()
        
        # Close database connection
        self.backup_manager.perform_emergency_backup()
        self.backup_manager.stop()
        self.db_manager.close()
        self.root.destroy()
    
    def run(self):
        """Run the application main loop."""
        self.root.mainloop()


def main():
    """Application entry point."""
    try:
        app = BillingApplication()
        app.run()
    except Exception as e:
        messagebox.showerror(
            "Application Error",
            f"An unexpected error occurred:\n\n{str(e)}\n\nPlease contact support."
        )
        raise


if __name__ == "__main__":
    main()
