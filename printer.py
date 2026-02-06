import os
from datetime import datetime

def format_line(left, right, width):
    """
    Formats a line with left aligned text and right aligned text.
    """
    len_left = len(left)
    len_right = len(right)
    spaces = width - len_left - len_right
    if spaces < 0:
        spaces = 1 # Force at least one space
        
    return left + " " * spaces + right

def generate_receipt_text(shop_name, bill_id, date, items, totals, width=58):
    """
    Generates receipt text suitable for ESC/POS printers.
    Width: 32 chars for 58mm (approx), 48 chars for 80mm (approx).
    Let's use 32 as default for 58mm usually.
    Note: 58mm printer usually prints ~32 characters per line.
    """
    # Adjust char width based on mm (Very rough approximation)
    # 58mm ~ 32 chars
    # 80mm ~ 48 chars
    char_width = 32 if width == 58 else 48
    
    lines = []
    lines.append(shop_name.center(char_width))
    lines.append("=" * char_width)
    lines.append(f"Bill No: {bill_id}")
    lines.append(f"Date: {date}")
    lines.append("-" * char_width)
    
    # Headers
    # Item Qty Price
    # We might need to handle long names
    
    for item in items:
        name = item['name']
        qty = item['quantity']
        price = item['price'] * qty
        
        # Line 1: Name
        lines.append(name[:char_width])
        # Line 2: Qty x UnitPrice -> Total
        line2 = f"{qty} x {item['price']:.2f}"
        line2_right = f"{price:.2f}"
        lines.append(format_line(line2, line2_right, char_width))
        
    lines.append("-" * char_width)
    lines.append(format_line("Subtotal", f"{totals['subtotal']:.2f}", char_width))
    if totals.get('discount_amount', 0) > 0:
        lines.append(format_line("Discount", f"-{totals['discount_amount']:.2f}", char_width))
    if totals.get('tax_amount', 0) > 0:
        lines.append(format_line("Tax", f"{totals['tax_amount']:.2f}", char_width))
        
    lines.append("=" * char_width)
    lines.append(format_line("TOTAL", f"{totals['grand_total']:.2f}", char_width))
    lines.append("=" * char_width)
    lines.append("Thank You!".center(char_width))
    lines.append("\n\n") # Feed
    
    return "\n".join(lines)

def print_receipt(receipt_text, printer_name=None):
    """
    Simulates printing by saving to file and trying to print to default printer if possible.
    For robustness in this task, we will save to a 'receipts' folder.
    """
    # Ensure receipts dir exists
    receipts_dir = os.path.join(os.path.dirname(__file__), 'logs', 'receipts')
    if not os.path.exists(receipts_dir):
        os.makedirs(receipts_dir)
        
    filename = f"receipt_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    filepath = os.path.join(receipts_dir, filename)
    
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(receipt_text)
        
    print(f"Receipt saved to {filepath}")
    
    # Optional Real Printing (Windows)
    # Using 'print' verb
    try:
        # This sends to default printer. 
        # Uncomment in production environment.
        # os.startfile(filepath, "print") 
        pass
    except Exception as e:
        print(f"Printing failed: {e}")
        
    return filepath
