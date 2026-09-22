import tkinter as tk
from ui.menu_view import MenuView
from ui.cadastros_view import CadastrosView
from ui.gerenciamento_view import GerenciamentoView
from ui.config_view import ConfigView

class MainWindow(tk.Tk):
    """Janela principal com navegacao entre telas."""
    
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
        
        self.title('BusinessReg')
        self.geometry('1000x600')
        self.minsize(800, 500)
        self.configure(bg=self.COLORS['bg_primary'])
        
        self.current_view = None
        
        self.create_views()
        self.show_menu()
        self.center_window()
    
    def center_window(self):
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')
    
    def create_views(self):
        self.menu_view = MenuView(self, self.COLORS, self.navigate)
        self.cadastros_view = CadastrosView(self, self.COLORS, self.show_menu)
        self.gerenciamento_view = GerenciamentoView(self, self.COLORS, self.show_menu)
        self.config_view = ConfigView(self, self.COLORS, self.show_menu)
    
    def navigate(self, screen):
        self.hide_all()
        
        if screen == 'cadastros':
            self.cadastros_view.pack(fill='both', expand=True)
            self.current_view = 'cadastros'
        elif screen == 'gerenciamento':
            self.gerenciamento_view.pack(fill='both', expand=True)
            self.current_view = 'gerenciamento'
        elif screen == 'configuracoes':
            self.config_view.pack(fill='both', expand=True)
            self.current_view = 'configuracoes'
    
    def show_menu(self):
        self.hide_all()
        self.menu_view.pack(fill='both', expand=True)
        self.current_view = 'menu'
    
    def hide_all(self):
        for view in [self.menu_view, self.cadastros_view, self.gerenciamento_view, self.config_view]:
            view.pack_forget()


if __name__ == '__main__':
    app = MainWindow()
    app.mainloop()
