"""
PDF Generator - Generate professional PDF invoices using ReportLab
"""

import os
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm, mm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
from core.payments_config import PaymentConfigManager

def generate_invoice_pdf(invoice, db_manager, filepath):
    """Generate PDF invoice."""
    
    doc = SimpleDocTemplate(
        filepath,
        pagesize=A4,
        rightMargin=1*cm, leftMargin=1*cm,
        topMargin=1*cm, bottomMargin=1*cm
    )
    
    elements = []
    styles = getSampleStyleSheet()
    
    # Custom Styles
    styles.add(ParagraphStyle(name='BusinessName', fontSize=18, leading=22, spaceAfter=2, textColor=colors.HexColor('#1E293B')))
    styles.add(ParagraphStyle(name='Heading', fontSize=14, leading=18, spaceAfter=10, textColor=colors.HexColor('#6366F1')))
    styles.add(ParagraphStyle(name='NormalSmall', fontSize=9, leading=12))
    styles.add(ParagraphStyle(name='TableHeader', fontSize=9, leading=11, fontName='Helvetica-Bold', textColor=colors.white))
    
    # --- Header Section ---
    biz_name = db_manager.get_setting('business_name', 'My Business')
    biz_addr = db_manager.get_setting('business_address', '').replace('\n', '<br/>')
    biz_gst = db_manager.get_setting('business_gstin', '')
    biz_contact = f"{db_manager.get_setting('business_phone', '')} | {db_manager.get_setting('business_email', '')}"
    
    # Layout using Table for Header (Logo Left, Text Right or vice versa)
    # Simple top-down approach for robustness
    
    elements.append(Paragraph(biz_name, styles['BusinessName']))
    elements.append(Paragraph(biz_addr, styles['NormalSmall']))
    if biz_gst:
        elements.append(Paragraph(f"<b>GSTIN:</b> {biz_gst}", styles['NormalSmall']))
    elements.append(Paragraph(biz_contact, styles['NormalSmall']))
    
    elements.append(Spacer(1, 1*cm))
    
    # --- Title & Invoice Details ---
    title = f"{invoice.invoice_type} INVOICE"
    elements.append(Paragraph(title, ParagraphStyle(name='Title', parent=styles['Heading1'], alignment=TA_CENTER, fontSize=16, textColor=colors.HexColor('#334155'))))
    
    # Details Grid
    data = [
        [f"Invoice No: {invoice.invoice_number}", f"Date: {invoice.date.strftime('%d-%m-%Y')}"],
        [f"Place of Supply: {invoice.customer_state}", f"Due Date: {invoice.due_date.strftime('%d-%m-%Y') if invoice.due_date else '-'}"]
    ]
    
    t = Table(data, colWidths=[9.5*cm, 9.5*cm])
    t.setStyle(TableStyle([
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 10),
        ('BOTTOMPADDING', (0,0), (-1,-1), 10),
    ]))
    elements.append(t)
    
    elements.append(Spacer(1, 0.5*cm))
    
    # --- Customer Details ---
    cust_data = [
        ["Bill To:"],
        [f"<b>{invoice.customer_name}</b>"],
        [invoice.customer_address],
        [f"GSTIN: {invoice.customer_gstin}" if invoice.customer_gstin else ""]
    ]
    
    c_table = Table(cust_data, colWidths=[19*cm])
    c_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (0,0), colors.HexColor('#F1F5F9')),
        ('PADDING', (0,0), (-1,-1), 6),
    ]))
    elements.append(c_table)
    
    elements.append(Spacer(1, 0.5*cm))
    
    # --- Items Table ---
    # Columns: #, Item, HSN, Qty, Rate, Disc, Tax, Amount
    headers = ['#', 'Item Description', 'HSN', 'Qty', 'Rate', 'Disc', 'GST%', 'Amount']
    col_widths = [1*cm, 6*cm, 2*cm, 1.5*cm, 2.5*cm, 2*cm, 1.5*cm, 2.5*cm]
    
    table_data = [headers]
    
    for item in invoice.items:
        row = [
            str(item.sr_no),
            Paragraph(item.description, styles['NormalSmall']),
            item.hsn_sac or '',
            f"{item.quantity} {item.unit}",
            f"{item.rate:,.2f}",
            f"{item.discount_amount:,.2f}",
            f"{item.gst_rate}%",
            f"{item.total:,.2f}"
        ]
        table_data.append(row)
    
    # Add Total Row
    item_table = Table(table_data, colWidths=col_widths, repeatRows=1)
    
    # Styling
    ts = TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1E293B')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('ALIGN', (3,0), (-1,-1), 'RIGHT'), # Numbers right aligned
        ('ALIGN', (0,0), (2,-1), 'LEFT'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
        ('FONTSIZE', (0,0), (-1,-1), 9),
        ('PADDING', (0,0), (-1,-1), 6),
    ])
    item_table.setStyle(ts)
    elements.append(item_table)
    
    # --- Totals Section ---
    elements.append(Spacer(1, 0.5*cm))
    
    # Grid for Totals + QR Code
    # We will use a table with 2 columns: Left for QR/Bank, Right for Totals
    
    # 1. Prepare QR Code
    pay_mgr = PaymentConfigManager(db_manager)
    qr_path = pay_mgr.get_qr_path_for_invoice(invoice.total, invoice.invoice_number)
    
    qr_img = None
    if qr_path and os.path.exists(qr_path):
        qr_img = Image(qr_path, width=3*cm, height=3*cm)

    # 2. Prepare Totals Data
    totals_data = [
        ['', 'Subtotal:', f"{invoice.subtotal:,.2f}"],
        ['', 'Discount:', f"-{invoice.discount_amount:,.2f}"],
        ['', 'CGST:', f"{invoice.cgst_amount:,.2f}"],
        ['', 'SGST:', f"{invoice.sgst_amount:,.2f}"],
        ['', 'IGST:', f"{invoice.igst_amount:,.2f}"],
        ['', 'Grand Total:', f"{invoice.total:,.2f}"]
    ]
    
    totals_subtable = Table(totals_data, colWidths=[1*cm, 4*cm, 3*cm])
    totals_subtable.setStyle(TableStyle([
        ('ALIGN', (1,0), (-1,-1), 'RIGHT'),
        ('FONTNAME', (-2,-1), (-1,-1), 'Helvetica-Bold'),
        ('LINEABOVE', (1,-1), (-1,-1), 1, colors.HexColor('#1E293B')),
    ]))
    
    # Combine QR and Totals
    main_footer_data = [[qr_img if qr_img else "", totals_subtable]]
    main_footer = Table(main_footer_data, colWidths=[11*cm, 8*cm])
    main_footer.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('ALIGN', (0,0), (0,0), 'LEFT'), # QR Left
        ('ALIGN', (1,0), (1,0), 'RIGHT'), # Totals Right
    ]))
    
    elements.append(main_footer)
    
    # --- Footer ---
    elements.append(Spacer(1, 2*cm))
    
    terms = db_manager.get_setting('invoice_terms', '')
    if terms:
        elements.append(Paragraph("Terms & Conditions:", styles['Heading']))
        elements.append(Paragraph(terms, styles['NormalSmall']))
        
    # Signature
    elements.append(Spacer(1, 1.5*cm))
    sig_data = [[f"For {biz_name}", ""], ["", "Authorized Signatory"]]
    sig_table = Table(sig_data, colWidths=[9.5*cm, 9.5*cm])
    sig_table.setStyle(TableStyle([
        ('ALIGN', (1,0), (1,1), 'RIGHT'),
    ]))
    elements.append(sig_table)
    
    doc.build(elements)


def generate_html_content(invoice, db_manager):
    """Generate HTML content for printing."""
    biz_name = db_manager.get_setting('business_name', 'My Business')
    
    # Simple HTML template
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Invoice {invoice.invoice_number}</title>
        <style>
            body {{ font-family: 'Segoe UI', Arial, sans-serif; padding: 20px; }}
            .header {{ display: flex; justify-content: space-between; margin-bottom: 20px; }}
            .title {{ font-size: 24px; font-weight: bold; color: #6366F1; }}
            table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
            th {{ background: #1E293B; color: white; padding: 10px; text-align: left; }}
            td {{ border-bottom: 1px solid #ddd; padding: 10px; }}
            .totals {{ float: right; width: 300px; margin-top: 20px; }}
            .row {{ display: flex; justify-content: space-between; margin: 5px 0; }}
            .bold {{ font-weight: bold; }}
        </style>
    </head>
    <body>
        <div class="header">
            <div>
                <h1>{biz_name}</h1>
                <p>{db_manager.get_setting('business_address', '')}</p>
                <p>GSTIN: {db_manager.get_setting('business_gstin', '')}</p>
            </div>
            <div style="text-align: right;">
                <div class="title">INVOICE</div>
                <p>No: {invoice.invoice_number}</p>
                <p>Date: {invoice.date.strftime('%d-%m-%Y')}</p>
            </div>
        </div>
        
        <div style="background: #f1f5f9; padding: 15px;">
            <strong>Bill To:</strong><br>
            {invoice.customer_name}<br>
            {invoice.customer_address}<br>
            GSTIN: {invoice.customer_gstin}
        </div>
        
        <table>
            <thead>
                <tr>
                    <th>#</th>
                    <th>Item</th>
                    <th>HSN</th>
                    <th>Qty</th>
                    <th>Rate</th>
                    <th>Tax</th>
                    <th>Total</th>
                </tr>
            </thead>
            <tbody>
    """
    
    for item in invoice.items:
        html += f"""
            <tr>
                <td>{item.sr_no}</td>
                <td>{item.description}</td>
                <td>{item.hsn_sac}</td>
                <td>{item.quantity} {item.unit}</td>
                <td>{item.rate}</td>
                <td>{item.gst_rate}%</td>
                <td>{item.total}</td>
            </tr>
        """
        
    html += f"""
            </tbody>
        </table>
        
        <div class="totals">
            <div class="row"><span>Subtotal:</span> <span>{invoice.subtotal}</span></div>
            <div class="row"><span>CGST:</span> <span>{invoice.cgst_amount}</span></div>
            <div class="row"><span>SGST:</span> <span>{invoice.sgst_amount}</span></div>
            <div class="row"><span>IGST:</span> <span>{invoice.igst_amount}</span></div>
            <div class="row bold" style="font-size: 1.2em; border-top: 2px solid #000; padding-top: 5px;">
                <span>Total:</span> <span>{invoice.total}</span>
            </div>
        </div>
        
        <div style="clear: both; margin-top: 50px;">
            <strong>Terms & Conditions:</strong>
            <p>{db_manager.get_setting('invoice_terms', '')}</p>
        </div>
        
        <div style="text-align: right; margin-top: 50px;">
            <p>For {biz_name}</p>
            <br><br>
            <p>Authorized Signatory</p>
        </div>
    </body>
    </html>
    """
    return html
