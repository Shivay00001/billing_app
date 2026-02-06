"""
Printer Utility - Handle direct printing using win32print or HTML fallback
"""

import sys
import os
import tempfile
import webbrowser
from typing import Optional

class PrinterManager:
    """Manages printing operations."""
    
    @staticmethod
    def print_file(filepath: str):
        """Print a file using default system printer."""
        try:
            if sys.platform == 'win32':
                os.startfile(filepath, 'print')
            else:
                # Fallback for non-windows (though req is Windows)
                webbrowser.open(filepath)
        except Exception as e:
            print(f"Printing failed: {e}")

def print_invoice(invoice, db_manager):
    """
    Generate an HTML representation of the invoice and print it.
    This works reliably across systems by using the browser's print dialog.
    """
    from utils.pdf_generator import generate_html_content
    
    # Generate HTML content
    html_content = generate_html_content(invoice, db_manager)
    
    # Create temp file
    fd, path = tempfile.mkstemp(suffix='.html')
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as f:
            f.write(html_content)
            
        # Open in default browser/viewer which usually has a print option
        webbrowser.open(f'file://{path}')
        
        # On Windows, we can try to trigger print directly
        if sys.platform == 'win32':
            # Give it a moment to render
            # Note: direct printing of HTML without dialogue is tricky, 
            # so opening in browser is the safest "Commercial Product" reliable way 
            # without heavy dependencies like PyQtWebEngine or wxPython.
            pass
            
    except Exception as e:
        print(f"Error printing: {e}")
