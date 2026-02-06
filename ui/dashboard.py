import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import reports

class DashboardFrame(ttk.Frame):
    def __init__(self, master, **kwargs):
        super().__init__(master, padding=20, **kwargs)
        self.pack(fill=BOTH, expand=YES)
        
        # Title
        lbl_title = ttk.Label(self, text="Business Dashboard", font=("Helvetica", 24, "bold"))
        lbl_title.pack(pady=(0, 20), anchor=W)
        
        # KPI Cards Frame
        kpi_frame = ttk.Frame(self)
        kpi_frame.pack(fill=X, pady=10)
        
        self.card_1 = self.create_kpi_card(kpi_frame, "Total Earnings", "$0.00", "success")
        self.card_2 = self.create_kpi_card(kpi_frame, "Total Bills", "0", "info")
        self.card_3 = self.create_kpi_card(kpi_frame, "Avg Bill Value", "$0.00", "warning")
        
        # Charts Frame
        charts_frame = ttk.Frame(self)
        charts_frame.pack(fill=BOTH, expand=YES, pady=20)
        
        # Left Chart (Bar)
        self.fig1, self.ax1 = plt.subplots(figsize=(5, 4), dpi=100)
        self.canvas1 = FigureCanvasTkAgg(self.fig1, master=charts_frame)
        self.canvas1.get_tk_widget().pack(side=LEFT, fill=BOTH, expand=YES, padx=10)
        
        # Right Chart (Pie)
        self.fig2, self.ax2 = plt.subplots(figsize=(5, 4), dpi=100)
        self.canvas2 = FigureCanvasTkAgg(self.fig2, master=charts_frame)
        self.canvas2.get_tk_widget().pack(side=RIGHT, fill=BOTH, expand=YES, padx=10)
        
        # Refresh Button
        btn_refresh = ttk.Button(self, text="Refresh Data", command=self.refresh_data, bootstyle=OUTLINE)
        btn_refresh.pack(anchor=E, pady=10)
        
        self.refresh_data()

    def create_kpi_card(self, parent, title, value, color):
        # Frame supports standard colors (e.g. 'success'), not 'success-inverse'
        card = ttk.Frame(parent, bootstyle=color, padding=15)
        card.pack(side=LEFT, fill=X, expand=YES, padx=5)
        
        # Labels need to match the background of the frame (so 'success-inverse')
        # This provides white text on the colored background
        lbl_title = ttk.Label(card, text=title, font=("Helvetica", 12), bootstyle=f"{color}-inverse")
        lbl_title.pack(anchor=W)
        
        lbl_value = ttk.Label(card, text=value, font=("Helvetica", 18, "bold"), bootstyle=f"{color}-inverse")
        lbl_value.pack(anchor=W)
        return lbl_value

    def refresh_data(self):
        # Fetch Data
        total_earnings = reports.get_total_earnings()
        total_bills = reports.get_sales_count()
        avg_bill = total_earnings / total_bills if total_bills else 0
        
        # Update Cards
        self.card_1.config(text=f"${total_earnings:,.2f}")
        self.card_2.config(text=str(total_bills))
        self.card_3.config(text=f"${avg_bill:,.2f}")
        
        # Update Bar Chart (Top Products)
        top_products = reports.get_product_performance(limit=5, order='DESC')
        names = [p['name'] for p in top_products]
        quantities = [p['total_qty'] for p in top_products]
        
        self.ax1.clear()
        self.ax1.bar(names, quantities, color='#3498db')
        self.ax1.set_title("Top Selling Products")
        self.ax1.set_ylabel("Quantity Sold")
        self.ax1.tick_params(axis='x', rotation=45, labelsize=8)
        self.fig1.tight_layout()
        self.canvas1.draw()
        
        # Update Pie Chart (Payment Methods)
        payment_stats = reports.get_payment_method_stats()
        # payment_stats is list of (method, count)
        if payment_stats:
            labels = [p[0] for p in payment_stats]
            sizes = [p[1] for p in payment_stats]
            self.ax2.clear()
            self.ax2.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
            self.ax2.set_title("Payment Methods")
        else:
            self.ax2.clear()
            self.ax2.text(0.5, 0.5, "No Data", ha='center')
            
        self.canvas2.draw()
