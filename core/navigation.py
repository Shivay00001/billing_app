"""
Navigation Manager - Sidebar Navigation System
"""

import tkinter as tk
from tkinter import ttk
from typing import Dict, Callable, Optional, Any


class NavigationManager:
    """Manages sidebar navigation and content frame switching."""
    
    # Navigation items configuration
    NAV_ITEMS = [
        {'id': 'dashboard', 'label': '📊  Dashboard', 'shortcut': 'Ctrl+1'},
        {'id': 'new_invoice', 'label': '➕  New Invoice', 'shortcut': 'Ctrl+2'},
        {'id': 'invoices', 'label': '📄  Invoices', 'shortcut': 'Ctrl+3'},
        {'id': 'customers', 'label': '👥  Customers', 'shortcut': 'Ctrl+4'},
        {'id': 'products', 'label': '📦  Products', 'shortcut': 'Ctrl+5'},
        {'id': 'reports', 'label': '📈  Reports', 'shortcut': 'Ctrl+6'},
        {'id': 'settings', 'label': '⚙️  Settings', 'shortcut': 'Ctrl+7'},
    ]
    
    SIDEBAR_WIDTH = 220
    
    def __init__(self, parent: ttk.Frame, db_manager, license_manager):
        """Initialize navigation manager."""
        self.parent = parent
        self.db_manager = db_manager
        self.license_manager = license_manager
        
        self.current_view: Optional[str] = None
        self.current_frame: Optional[ttk.Frame] = None
        self.nav_buttons: Dict[str, ttk.Button] = {}
        self.view_cache: Dict[str, Any] = {}
        
        # Import views lazily to avoid circular imports
        self.view_classes = {}
    
    def setup(self):
        """Setup the navigation UI."""
        self._create_sidebar()
        self._create_content_area()
        self._import_views()
        
        # Navigate to dashboard by default
        self.navigate('dashboard')
    
    def _create_sidebar(self):
        """Create the sidebar navigation panel."""
        # Sidebar container
        self.sidebar = tk.Frame(
            self.parent,
            bg='#0F172A',
            width=self.SIDEBAR_WIDTH
        )
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y)
        self.sidebar.pack_propagate(False)
        
        # Logo/Brand area
        brand_frame = tk.Frame(self.sidebar, bg='#0F172A')
        brand_frame.pack(fill=tk.X, pady=(20, 30))
        
        brand_label = tk.Label(
            brand_frame,
            text="💼 GST Billing Pro",
            font=('Segoe UI', 14, 'bold'),
            fg='#F8FAFC',
            bg='#0F172A'
        )
        brand_label.pack(pady=10)
        
        version_label = tk.Label(
            brand_frame,
            text="v1.0.0",
            font=('Segoe UI', 9),
            fg='#64748B',
            bg='#0F172A'
        )
        version_label.pack()
        
        # Separator
        sep = tk.Frame(self.sidebar, bg='#334155', height=1)
        sep.pack(fill=tk.X, padx=15, pady=(0, 15))
        
        # Navigation buttons
        nav_frame = tk.Frame(self.sidebar, bg='#0F172A')
        nav_frame.pack(fill=tk.BOTH, expand=True, padx=10)
        
        for item in self.NAV_ITEMS:
            btn = self._create_nav_button(nav_frame, item)
            self.nav_buttons[item['id']] = btn
        
        # License status at bottom
        self._create_license_status()
    
    def _create_nav_button(self, parent: tk.Frame, item: dict) -> tk.Button:
        """Create a navigation button."""
        btn_frame = tk.Frame(parent, bg='#0F172A')
        btn_frame.pack(fill=tk.X, pady=2)
        
        btn = tk.Button(
            btn_frame,
            text=item['label'],
            font=('Segoe UI', 11),
            fg='#94A3B8',
            bg='#0F172A',
            activeforeground='#F8FAFC',
            activebackground='#1E293B',
            bd=0,
            padx=15,
            pady=12,
            anchor='w',
            cursor='hand2',
            command=lambda: self.navigate(item['id'])
        )
        btn.pack(fill=tk.X)
        
        # Hover effects
        btn.bind('<Enter>', lambda e, b=btn: self._on_button_hover(b, True))
        btn.bind('<Leave>', lambda e, b=btn: self._on_button_hover(b, False))
        
        return btn
    
    def _on_button_hover(self, button: tk.Button, entering: bool):
        """Handle button hover effect."""
        if button.cget('bg') != '#1E293B':  # Not active
            if entering:
                button.config(bg='#1E293B', fg='#F8FAFC')
            else:
                button.config(bg='#0F172A', fg='#94A3B8')
    
    def _create_license_status(self):
        """Create license status display at bottom of sidebar."""
        license_frame = tk.Frame(self.sidebar, bg='#0F172A')
        license_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=15, pady=15)
        
        # Separator
        sep = tk.Frame(license_frame, bg='#334155', height=1)
        sep.pack(fill=tk.X, pady=(0, 15))
        
        # Get license info
        license_info = self.license_manager.get_license_info()
        plan = license_info.get('plan', 'TRIAL')
        
        # Plan badge
        plan_colors = {
            'TRIAL': ('#F59E0B', '#78350F'),
            'BASIC': ('#3B82F6', '#1E3A8A'),
            'PRO': ('#10B981', '#064E3B')
        }
        fg_color, bg_color = plan_colors.get(plan, plan_colors['TRIAL'])
        
        plan_label = tk.Label(
            license_frame,
            text=f"  {plan}  ",
            font=('Segoe UI', 9, 'bold'),
            fg=fg_color,
            bg=bg_color,
            padx=8,
            pady=4
        )
        plan_label.pack(anchor='w')
        
        # Expiry info
        if plan == 'TRIAL':
            remaining = license_info.get('invoices_remaining', 10)
            status_text = f"{remaining} invoices remaining"
        else:
            expiry = license_info.get('expiry_date', 'N/A')
            status_text = f"Valid until {expiry}"
        
        status_label = tk.Label(
            license_frame,
            text=status_text,
            font=('Segoe UI', 9),
            fg='#64748B',
            bg='#0F172A'
        )
        status_label.pack(anchor='w', pady=(5, 0))
    
    def _create_content_area(self):
        """Create the main content area."""
        self.content_area = tk.Frame(
            self.parent,
            bg='#1E293B'
        )
        self.content_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    
    def _import_views(self):
        """Import view classes lazily."""
        from ui.dashboard import DashboardView
        from ui.billing import BillingView
        from ui.invoices import InvoicesView
        from ui.customers import CustomersView
        from ui.products import ProductsView
        from ui.reports import ReportsView
        from ui.settings import SettingsView
        
        self.view_classes = {
            'dashboard': DashboardView,
            'new_invoice': BillingView,
            'invoices': InvoicesView,
            'customers': CustomersView,
            'products': ProductsView,
            'reports': ReportsView,
            'settings': SettingsView,
        }
    
    def navigate(self, view_id: str):
        """Navigate to a specific view."""
        if view_id == self.current_view:
            return
        
        # Check license restrictions
        if not self._check_view_access(view_id):
            return
        
        # Update button states
        self._update_button_states(view_id)
        
        # Clear current content
        if self.current_frame:
            self.current_frame.destroy()
        
        # Create new content frame
        self.current_frame = tk.Frame(self.content_area, bg='#1E293B')
        self.current_frame.pack(fill=tk.BOTH, expand=True)
        
        # Get or create view
        if view_id in self.view_cache:
            view = self.view_cache[view_id]
            view.set_frame(self.current_frame)
            view.refresh()
        else:
            view_class = self.view_classes.get(view_id)
            if view_class:
                view = view_class(
                    self.current_frame,
                    self.db_manager,
                    self.license_manager,
                    self
                )
                self.view_cache[view_id] = view
                view.setup()
        
        self.current_view = view_id
    
    def _check_view_access(self, view_id: str) -> bool:
        """Check if user has access to the view based on license."""
        license_info = self.license_manager.get_license_info()
        plan = license_info.get('plan', 'TRIAL')
        
        # Trial restrictions
        if plan == 'TRIAL':
            if view_id == 'reports':
                from tkinter import messagebox
                messagebox.showwarning(
                    "Feature Locked",
                    "Reports & Analytics are not available in Trial mode.\n\n"
                    "Upgrade to Basic or Pro to unlock this feature."
                )
                return False
        
        return True
    
    def _update_button_states(self, active_id: str):
        """Update navigation button visual states."""
        for nav_id, btn in self.nav_buttons.items():
            if nav_id == active_id:
                btn.config(
                    bg='#1E293B',
                    fg='#6366F1',
                    font=('Segoe UI', 11, 'bold')
                )
            else:
                btn.config(
                    bg='#0F172A',
                    fg='#94A3B8',
                    font=('Segoe UI', 11)
                )
    
    def get_current_view(self) -> Optional[Any]:
        """Get the current active view instance."""
        if self.current_view and self.current_view in self.view_cache:
            return self.view_cache[self.current_view]
        return None
    
    def refresh_current_view(self):
        """Refresh the current view."""
        view = self.get_current_view()
        if view and hasattr(view, 'refresh'):
            view.refresh()


class BaseView:
    """Base class for all views."""
    
    def __init__(self, frame: tk.Frame, db_manager, license_manager, nav_manager):
        """Initialize base view."""
        self.frame = frame
        self.db_manager = db_manager
        self.license_manager = license_manager
        self.nav_manager = nav_manager
        self._has_unsaved_changes = False
    
    def set_frame(self, frame: tk.Frame):
        """Set the frame for this view."""
        self.frame = frame
    
    def setup(self):
        """Setup the view UI. Override in subclasses."""
        pass
    
    def refresh(self):
        """Refresh view data. Override in subclasses."""
        pass
    
    def has_unsaved_changes(self) -> bool:
        """Check if view has unsaved changes."""
        return self._has_unsaved_changes
    
    def save_current(self):
        """Save current state. Override in subclasses."""
        pass
    
    def print_current(self):
        """Print current content. Override in subclasses."""
        pass
    
    def handle_escape(self):
        """Handle escape key. Override in subclasses."""
        pass
    
    def create_header(self, title: str, subtitle: str = ""):
        """Create a standard page header."""
        header = tk.Frame(self.frame, bg='#1E293B')
        header.pack(fill=tk.X, padx=30, pady=(30, 20))
        
        title_label = tk.Label(
            header,
            text=title,
            font=('Segoe UI', 24, 'bold'),
            fg='#F8FAFC',
            bg='#1E293B'
        )
        title_label.pack(anchor='w')
        
        if subtitle:
            subtitle_label = tk.Label(
                header,
                text=subtitle,
                font=('Segoe UI', 11),
                fg='#94A3B8',
                bg='#1E293B'
            )
            subtitle_label.pack(anchor='w', pady=(5, 0))
        
        return header
    
    def create_card(self, parent: tk.Frame, **kwargs) -> tk.Frame:
        """Create a styled card container."""
        card = tk.Frame(
            parent,
            bg='#0F172A',
            padx=kwargs.get('padx', 20),
            pady=kwargs.get('pady', 20)
        )
        return card
    
    def show_success(self, message: str):
        """Show success message."""
        from tkinter import messagebox
        messagebox.showinfo("Success", message)
    
    def show_error(self, message: str):
        """Show error message."""
        from tkinter import messagebox
        messagebox.showerror("Error", message)
    
    def show_warning(self, message: str):
        """Show warning message."""
        from tkinter import messagebox
        messagebox.showwarning("Warning", message)
    
    def confirm(self, message: str) -> bool:
        """Show confirmation dialog."""
        from tkinter import messagebox
        return messagebox.askyesno("Confirm", message)
