import tkinter as tk
from tkinter import ttk
from ui.sidebar import Sidebar
from ui.content_area import ContentArea

class MainWindow(tk.Tk):
    """Janela principal do aplicativo."""
    
    COLORS = {
        'bg_primary': '#1a1a2e',
        'bg_secondary': '#16213e',
        'bg_tertiary': '#0f3460',
        'accent': '#e94560',
        'text_primary': '#ffffff',
        'text_secondary': '#a0a0a0',
        'border': '#2a2a4e'
    }
    
    def __init__(self):
        super().__init__()
        
        self.title('BusinessReg - Sistema de Registro de Empresas')
        self.geometry('1200x700')
        self.minsize(1000, 600)
        
        self.configure_styles()
        self.configure(bg=self.COLORS['bg_primary'])
        
        self.columnconfigure(0, weight=0)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)
        
        self.create_widgets()
        self.center_window()
    
    def configure_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        
        style.configure(
            'Custom.TButton',
            background=self.COLORS['bg_tertiary'],
            foreground=self.COLORS['text_primary'],
            borderwidth=0,
            padding=10
        )
        
        style.map(
            'Custom.TButton',
            background=[('active', self.COLORS['accent'])]
        )
    
    def center_window(self):
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')
    
    def create_widgets(self):
        self.sidebar = Sidebar(self, self.COLORS)
        self.sidebar.grid(row=0, column=0, sticky='ns')
        
        self.content_area = ContentArea(self, self.COLORS)
        self.content_area.grid(row=0, column=1, sticky='nsew', padx=20, pady=20)


if __name__ == '__main__':
    app = MainWindow()
    app.mainloop()
