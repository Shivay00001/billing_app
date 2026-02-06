"""
Theme Manager - Modern Premium Dark Theme
"""

import tkinter as tk
from tkinter import ttk


class ThemeManager:
    """Manages application theming with a premium dark aesthetic."""
    
    # Color Palette - Premium Slate & Indigo
    COLORS = {
        # Primary colors
        'primary': '#6366F1',           # Indigo 500
        'primary_hover': '#818CF8',     # Indigo 400
        'primary_dark': '#4F46E5',      # Indigo 600
        
        # Background colors
        'bg_dark': '#020617',           # Slate 950 (Main Window)
        'bg_medium': '#0F172A',         # Slate 900 (Content Areas)
        'bg_light': '#1E293B',          # Slate 800 (Cards/Inputs)
        'bg_card': '#1E293B',           # Card Background
        
        # Text colors
        'text_primary': '#F8FAFC',      # Slate 50
        'text_secondary': '#CBD5E1',    # Slate 300
        'text_muted': '#64748B',        # Slate 500
        
        # Accent colors
        'success': '#10B981',           # Emerald 500
        'warning': '#F59E0B',           # Amber 500
        'error': '#EF4444',             # Red 500
        'info': '#3B82F6',              # Blue 500
        
        # Border colors
        'border': '#334155',
        'border_light': '#475569',
        
        # Sidebar
        'sidebar_bg': '#020617',        # Slate 950
        'sidebar_active': '#1E293B',    # Slate 800
        'sidebar_hover': '#1E293B',
        
        # Input colors
        'input_bg': '#0F172A',          # Darker inputs
        'input_border': '#334155',
        'input_focus': '#6366F1',
    }
    
    # Font configurations - Larger & Cleaner
    FONTS = {
        'heading_large': ('Segoe UI', 26, 'bold'),
        'heading': ('Segoe UI', 20, 'bold'),
        'subheading': ('Segoe UI', 15, 'bold'),
        'body': ('Segoe UI', 11),       # Increased readability
        'body_bold': ('Segoe UI', 11, 'bold'),
        'small': ('Segoe UI', 10),
        'button': ('Segoe UI', 11, 'bold'),
        'monospace': ('Consolas', 11),
    }
    
    def __init__(self, root: tk.Tk):
        """Initialize theme manager."""
        self.root = root
        self.style = ttk.Style()
    
    def apply_theme(self):
        """Apply the modern dark theme to all widgets."""
        # Set theme base
        self.style.theme_use('clam')
        
        # Configure root window
        self.root.configure(bg=self.COLORS['bg_dark'])
        
        # Configure global options
        self.root.option_add('*tearOff', False)
        self.root.option_add('*Menu.background', self.COLORS['bg_light'])
        self.root.option_add('*Menu.foreground', self.COLORS['text_primary'])
        self.root.option_add('*Menu.activeBackground', self.COLORS['primary'])
        self.root.option_add('*Menu.activeForeground', self.COLORS['text_primary'])
        
        # Configure ttk styles
        self._configure_frame_styles()
        self._configure_label_styles()
        self._configure_button_styles()
        self._configure_entry_styles()
        self._configure_treeview_styles()
        self._configure_notebook_styles()
        self._configure_scrollbar_styles()
        self._configure_combobox_styles()
        self._configure_checkbutton_styles()
        self._configure_separator_styles()
        self._configure_progressbar_styles()
    
    def _configure_frame_styles(self):
        """Configure frame styles."""
        self.style.configure('TFrame', background=self.COLORS['bg_dark'])
        self.style.configure('Card.TFrame', background=self.COLORS['bg_card'], relief='flat')
        self.style.configure('Sidebar.TFrame', background=self.COLORS['sidebar_bg'])
        self.style.configure('Content.TFrame', background=self.COLORS['bg_medium'])
        
        # Scrollable Frame
        self.style.configure('Scroll.TFrame', background=self.COLORS['bg_medium'])
    
    def _configure_label_styles(self):
        """Configure label styles."""
        base = {'background': self.COLORS['bg_dark'], 'foreground': self.COLORS['text_primary'], 'font': self.FONTS['body']}
        
        self.style.configure('TLabel', **base)
        self.style.configure('Heading.TLabel', font=self.FONTS['heading'], **base)
        self.style.configure('HeadingLarge.TLabel', font=self.FONTS['heading_large'], **base)
        self.style.configure('Subheading.TLabel', font=self.FONTS['subheading'], **base)
        self.style.configure('Secondary.TLabel', background=self.COLORS['bg_dark'], foreground=self.COLORS['text_secondary'], font=self.FONTS['body'])
        self.style.configure('Muted.TLabel', background=self.COLORS['bg_dark'], foreground=self.COLORS['text_muted'], font=self.FONTS['small'])
        
        # Card Labels (Background matching Card.TFrame)
        self.style.configure('Card.TLabel', background=self.COLORS['bg_card'], foreground=self.COLORS['text_primary'], font=self.FONTS['body'])
        
        # Status Labels
        self.style.configure('Success.TLabel', foreground=self.COLORS['success'], font=self.FONTS['body_bold'], background=self.COLORS['bg_dark'])
        self.style.configure('Error.TLabel', foreground=self.COLORS['error'], font=self.FONTS['body'], background=self.COLORS['bg_dark'])
        self.style.configure('Warning.TLabel', foreground=self.COLORS['warning'], font=self.FONTS['body'], background=self.COLORS['bg_dark'])
    
    def _configure_button_styles(self):
        """Configure premium button styles."""
        # Primary button
        self.style.configure(
            'Primary.TButton',
            background=self.COLORS['primary'],
            foreground=self.COLORS['text_primary'],
            font=self.FONTS['button'],
            padding=(24, 12),  # Spacious padding
            borderwidth=0,
            relief='flat'
        )
        self.style.map(
            'Primary.TButton',
            background=[
                ('active', self.COLORS['primary_hover']),
                ('pressed', self.COLORS['primary_dark']),
                ('disabled', self.COLORS['bg_light'])
            ]
        )
        
        # Secondary button
        self.style.configure(
            'Secondary.TButton',
            background=self.COLORS['bg_light'],
            foreground=self.COLORS['text_primary'],
            font=self.FONTS['button'],
            padding=(24, 12),
            borderwidth=0
        )
        self.style.map(
            'Secondary.TButton',
            background=[('active', self.COLORS['border_light'])]
        )
        
        # Sidebar button (Navigation)
        self.style.configure(
            'Sidebar.TButton',
            background=self.COLORS['sidebar_bg'],
            foreground=self.COLORS['text_secondary'],
            font=self.FONTS['body'],
            padding=(20, 15),
            borderwidth=0,
            anchor='w'
        )
        self.style.map(
            'Sidebar.TButton',
            background=[('active', self.COLORS['sidebar_active'])],
            foreground=[('active', self.COLORS['text_primary'])]
        )
        # Active sidebar state
        self.style.configure(
            'SidebarActive.TButton',
            background=self.COLORS['sidebar_active'],
            foreground=self.COLORS['primary'],
            font=self.FONTS['body_bold'],
            padding=(20, 15),
            borderwidth=0,
            anchor='w'
        )
    
    def _configure_entry_styles(self):
        """Configure entry styles."""
        self.style.configure(
            'TEntry',
            fieldbackground=self.COLORS['input_bg'],
            foreground=self.COLORS['text_primary'],
            insertcolor=self.COLORS['text_primary'],
            bordercolor=self.COLORS['input_border'],
            lightcolor=self.COLORS['input_border'],
            darkcolor=self.COLORS['input_border'],
            padding=(12, 10),
            relief='flat'
        )
        self.style.map(
            'TEntry',
            bordercolor=[('focus', self.COLORS['input_focus'])],
            lightcolor=[('focus', self.COLORS['input_focus'])]
        )
    
    def _configure_treeview_styles(self):
        """Configure spacious treeview/table styles."""
        self.style.configure(
            'Treeview',
            background=self.COLORS['bg_medium'],
            foreground=self.COLORS['text_primary'],
            fieldbackground=self.COLORS['bg_medium'],
            borderwidth=0,
            font=self.FONTS['body'],
            rowheight=45  # Taller rows for readability
        )
        self.style.configure(
            'Treeview.Heading',
            background=self.COLORS['bg_light'],
            foreground=self.COLORS['text_primary'],
            font=self.FONTS['body_bold'],
            borderwidth=0,
            padding=(15, 12)
        )
        self.style.map(
            'Treeview',
            background=[('selected', self.COLORS['primary_dark'])],
            foreground=[('selected', self.COLORS['text_primary'])]
        )
    
    def _configure_notebook_styles(self):
        """Configure notebook/tab styles."""
        self.style.configure(
            'TNotebook',
            background=self.COLORS['bg_medium'],
            borderwidth=0
        )
        self.style.configure(
            'TNotebook.Tab',
            background=self.COLORS['bg_media'],
            foreground=self.COLORS['text_secondary'],
            padding=(25, 12),
            font=self.FONTS['body'],
            borderwidth=0
        )
        self.style.map(
            'TNotebook.Tab',
            background=[('selected', self.COLORS['bg_light'])],
            foreground=[('selected', self.COLORS['primary'])]
        )
    
    def _configure_scrollbar_styles(self):
        self.style.configure(
            'TScrollbar',
            background=self.COLORS['bg_light'],
            troughcolor=self.COLORS['bg_medium'],
            borderwidth=0,
            arrowsize=0,
            width=12
        )
        self.style.map('TScrollbar', background=[('active', self.COLORS['border_light'])])
    
    def _configure_combobox_styles(self):
        self.style.configure(
            'TCombobox',
            fieldbackground=self.COLORS['input_bg'],
            background=self.COLORS['bg_light'],
            foreground=self.COLORS['text_primary'],
            arrowcolor=self.COLORS['text_secondary'],
            padding=(12, 10)
        )
        
    def _configure_checkbutton_styles(self):
        self.style.configure(
            'TCheckbutton',
            background=self.COLORS['bg_dark'],
            foreground=self.COLORS['text_primary'],
            font=self.FONTS['body']
        )
    
    def _configure_separator_styles(self):
        self.style.configure('TSeparator', background=self.COLORS['border'])
    
    def _configure_progressbar_styles(self):
        self.style.configure(
            'TProgressbar',
            background=self.COLORS['primary'],
            troughcolor=self.COLORS['bg_light'],
            borderwidth=0
        )
    
    @classmethod
    def get_color(cls, name: str) -> str:
        return cls.COLORS.get(name, '#FFFFFF')
    
    @classmethod
    def get_font(cls, name: str) -> tuple:
        return cls.FONTS.get(name, ('Segoe UI', 11))

    
    # Color Palette
    COLORS = {
        # Primary colors
        'primary': '#6366F1',           # Indigo
        'primary_hover': '#818CF8',
        'primary_dark': '#4F46E5',
        
        # Background colors
        'bg_dark': '#0F172A',           # Slate 900
        'bg_medium': '#1E293B',         # Slate 800
        'bg_light': '#334155',          # Slate 700
        'bg_card': '#1E293B',
        
        # Text colors
        'text_primary': '#F8FAFC',      # Slate 50
        'text_secondary': '#94A3B8',    # Slate 400
        'text_muted': '#64748B',        # Slate 500
        
        # Accent colors
        'success': '#10B981',           # Emerald 500
        'success_bg': '#064E3B',
        'warning': '#F59E0B',           # Amber 500
        'warning_bg': '#78350F',
        'error': '#EF4444',             # Red 500
        'error_bg': '#7F1D1D',
        'info': '#3B82F6',              # Blue 500
        
        # Border colors
        'border': '#334155',
        'border_light': '#475569',
        
        # Sidebar
        'sidebar_bg': '#0F172A',
        'sidebar_active': '#1E293B',
        'sidebar_hover': '#1E293B',
        
        # Input colors
        'input_bg': '#1E293B',
        'input_border': '#334155',
        'input_focus': '#6366F1',
    }
    
    # Font configurations
    FONTS = {
        'heading_large': ('Segoe UI', 24, 'bold'),
        'heading': ('Segoe UI', 18, 'bold'),
        'subheading': ('Segoe UI', 14, 'bold'),
        'body': ('Segoe UI', 11),
        'body_bold': ('Segoe UI', 11, 'bold'),
        'small': ('Segoe UI', 9),
        'button': ('Segoe UI', 10, 'bold'),
        'monospace': ('Consolas', 10),
    }
    
    def __init__(self, root: tk.Tk):
        """Initialize theme manager."""
        self.root = root
        self.style = ttk.Style()
    
    def apply_theme(self):
        """Apply the modern dark theme to all widgets."""
        # Set theme base
        self.style.theme_use('clam')
        
        # Configure root window
        self.root.configure(bg=self.COLORS['bg_dark'])
        
        # Configure ttk styles
        self._configure_frame_styles()
        self._configure_label_styles()
        self._configure_button_styles()
        self._configure_entry_styles()
        self._configure_treeview_styles()
        self._configure_notebook_styles()
        self._configure_scrollbar_styles()
        self._configure_combobox_styles()
        self._configure_checkbutton_styles()
        self._configure_separator_styles()
        self._configure_progressbar_styles()
    
    def _configure_frame_styles(self):
        """Configure frame styles."""
        self.style.configure(
            'TFrame',
            background=self.COLORS['bg_dark']
        )
        
        self.style.configure(
            'Card.TFrame',
            background=self.COLORS['bg_card'],
            relief='flat'
        )
        
        self.style.configure(
            'Sidebar.TFrame',
            background=self.COLORS['sidebar_bg']
        )
        
        self.style.configure(
            'Content.TFrame',
            background=self.COLORS['bg_medium']
        )
    
    def _configure_label_styles(self):
        """Configure label styles."""
        self.style.configure(
            'TLabel',
            background=self.COLORS['bg_dark'],
            foreground=self.COLORS['text_primary'],
            font=self.FONTS['body']
        )
        
        self.style.configure(
            'Heading.TLabel',
            background=self.COLORS['bg_dark'],
            foreground=self.COLORS['text_primary'],
            font=self.FONTS['heading']
        )
        
        self.style.configure(
            'HeadingLarge.TLabel',
            background=self.COLORS['bg_dark'],
            foreground=self.COLORS['text_primary'],
            font=self.FONTS['heading_large']
        )
        
        self.style.configure(
            'Subheading.TLabel',
            background=self.COLORS['bg_dark'],
            foreground=self.COLORS['text_primary'],
            font=self.FONTS['subheading']
        )
        
        self.style.configure(
            'Secondary.TLabel',
            background=self.COLORS['bg_dark'],
            foreground=self.COLORS['text_secondary'],
            font=self.FONTS['body']
        )
        
        self.style.configure(
            'Muted.TLabel',
            background=self.COLORS['bg_dark'],
            foreground=self.COLORS['text_muted'],
            font=self.FONTS['small']
        )
        
        self.style.configure(
            'Card.TLabel',
            background=self.COLORS['bg_card'],
            foreground=self.COLORS['text_primary'],
            font=self.FONTS['body']
        )
        
        self.style.configure(
            'Success.TLabel',
            foreground=self.COLORS['success'],
            font=self.FONTS['body_bold']
        )
        
        self.style.configure(
            'Error.TLabel',
            foreground=self.COLORS['error'],
            font=self.FONTS['body']
        )
        
        self.style.configure(
            'Warning.TLabel',
            foreground=self.COLORS['warning'],
            font=self.FONTS['body']
        )
    
    def _configure_button_styles(self):
        """Configure button styles."""
        # Primary button
        self.style.configure(
            'Primary.TButton',
            background=self.COLORS['primary'],
            foreground=self.COLORS['text_primary'],
            font=self.FONTS['button'],
            padding=(20, 10),
            borderwidth=0
        )
        self.style.map(
            'Primary.TButton',
            background=[
                ('active', self.COLORS['primary_hover']),
                ('pressed', self.COLORS['primary_dark'])
            ]
        )
        
        # Secondary button
        self.style.configure(
            'Secondary.TButton',
            background=self.COLORS['bg_light'],
            foreground=self.COLORS['text_primary'],
            font=self.FONTS['button'],
            padding=(20, 10),
            borderwidth=0
        )
        self.style.map(
            'Secondary.TButton',
            background=[
                ('active', self.COLORS['border_light'])
            ]
        )
        
        # Success button
        self.style.configure(
            'Success.TButton',
            background=self.COLORS['success'],
            foreground=self.COLORS['text_primary'],
            font=self.FONTS['button'],
            padding=(20, 10),
            borderwidth=0
        )
        
        # Danger button
        self.style.configure(
            'Danger.TButton',
            background=self.COLORS['error'],
            foreground=self.COLORS['text_primary'],
            font=self.FONTS['button'],
            padding=(20, 10),
            borderwidth=0
        )
        
        # Sidebar button
        self.style.configure(
            'Sidebar.TButton',
            background=self.COLORS['sidebar_bg'],
            foreground=self.COLORS['text_secondary'],
            font=self.FONTS['body'],
            padding=(15, 12),
            borderwidth=0,
            anchor='w'
        )
        self.style.map(
            'Sidebar.TButton',
            background=[
                ('active', self.COLORS['sidebar_hover']),
                ('selected', self.COLORS['sidebar_active'])
            ],
            foreground=[
                ('active', self.COLORS['text_primary']),
                ('selected', self.COLORS['primary'])
            ]
        )
        
        # Active sidebar button
        self.style.configure(
            'SidebarActive.TButton',
            background=self.COLORS['sidebar_active'],
            foreground=self.COLORS['primary'],
            font=self.FONTS['body_bold'],
            padding=(15, 12),
            borderwidth=0,
            anchor='w'
        )
        
        # Icon button (minimal)
        self.style.configure(
            'Icon.TButton',
            background=self.COLORS['bg_dark'],
            foreground=self.COLORS['text_secondary'],
            padding=(8, 8),
            borderwidth=0
        )
    
    def _configure_entry_styles(self):
        """Configure entry styles."""
        self.style.configure(
            'TEntry',
            fieldbackground=self.COLORS['input_bg'],
            foreground=self.COLORS['text_primary'],
            insertcolor=self.COLORS['text_primary'],
            bordercolor=self.COLORS['input_border'],
            lightcolor=self.COLORS['input_border'],
            darkcolor=self.COLORS['input_border'],
            padding=(10, 8)
        )
        self.style.map(
            'TEntry',
            bordercolor=[('focus', self.COLORS['input_focus'])],
            lightcolor=[('focus', self.COLORS['input_focus'])]
        )
    
    def _configure_treeview_styles(self):
        """Configure treeview/table styles."""
        self.style.configure(
            'Treeview',
            background=self.COLORS['bg_medium'],
            foreground=self.COLORS['text_primary'],
            fieldbackground=self.COLORS['bg_medium'],
            borderwidth=0,
            font=self.FONTS['body'],
            rowheight=40
        )
        self.style.configure(
            'Treeview.Heading',
            background=self.COLORS['bg_light'],
            foreground=self.COLORS['text_primary'],
            font=self.FONTS['body_bold'],
            borderwidth=0,
            padding=(10, 8)
        )
        self.style.map(
            'Treeview',
            background=[('selected', self.COLORS['primary_dark'])],
            foreground=[('selected', self.COLORS['text_primary'])]
        )
    
    def _configure_notebook_styles(self):
        """Configure notebook/tab styles."""
        self.style.configure(
            'TNotebook',
            background=self.COLORS['bg_dark'],
            borderwidth=0
        )
        self.style.configure(
            'TNotebook.Tab',
            background=self.COLORS['bg_medium'],
            foreground=self.COLORS['text_secondary'],
            padding=(20, 10),
            font=self.FONTS['body']
        )
        self.style.map(
            'TNotebook.Tab',
            background=[('selected', self.COLORS['bg_dark'])],
            foreground=[('selected', self.COLORS['text_primary'])]
        )
    
    def _configure_scrollbar_styles(self):
        """Configure scrollbar styles."""
        self.style.configure(
            'TScrollbar',
            background=self.COLORS['bg_light'],
            troughcolor=self.COLORS['bg_dark'],
            borderwidth=0,
            arrowsize=0
        )
        self.style.map(
            'TScrollbar',
            background=[('active', self.COLORS['border_light'])]
        )
    
    def _configure_combobox_styles(self):
        """Configure combobox/dropdown styles."""
        self.style.configure(
            'TCombobox',
            fieldbackground=self.COLORS['input_bg'],
            background=self.COLORS['bg_light'],
            foreground=self.COLORS['text_primary'],
            arrowcolor=self.COLORS['text_secondary'],
            bordercolor=self.COLORS['input_border'],
            padding=(10, 8)
        )
        self.style.map(
            'TCombobox',
            fieldbackground=[('readonly', self.COLORS['input_bg'])],
            bordercolor=[('focus', self.COLORS['input_focus'])]
        )
        
        # Combobox dropdown list
        self.root.option_add('*TCombobox*Listbox.background', self.COLORS['bg_medium'])
        self.root.option_add('*TCombobox*Listbox.foreground', self.COLORS['text_primary'])
        self.root.option_add('*TCombobox*Listbox.selectBackground', self.COLORS['primary'])
        self.root.option_add('*TCombobox*Listbox.selectForeground', self.COLORS['text_primary'])
    
    def _configure_checkbutton_styles(self):
        """Configure checkbutton styles."""
        self.style.configure(
            'TCheckbutton',
            background=self.COLORS['bg_dark'],
            foreground=self.COLORS['text_primary'],
            font=self.FONTS['body']
        )
        self.style.map(
            'TCheckbutton',
            background=[('active', self.COLORS['bg_dark'])]
        )
    
    def _configure_separator_styles(self):
        """Configure separator styles."""
        self.style.configure(
            'TSeparator',
            background=self.COLORS['border']
        )
    
    def _configure_progressbar_styles(self):
        """Configure progressbar styles."""
        self.style.configure(
            'TProgressbar',
            background=self.COLORS['primary'],
            troughcolor=self.COLORS['bg_light'],
            borderwidth=0,
            lightcolor=self.COLORS['primary'],
            darkcolor=self.COLORS['primary']
        )
    
    @classmethod
    def get_color(cls, name: str) -> str:
        """Get a color value by name."""
        return cls.COLORS.get(name, '#FFFFFF')
    
    @classmethod
    def get_font(cls, name: str) -> tuple:
        """Get a font configuration by name."""
        return cls.FONTS.get(name, ('Segoe UI', 11))
