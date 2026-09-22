import tkinter as tk

class MenuView(tk.Frame):
    """Tela de menu principal centralizado."""
    
    def __init__(self, parent, colors, on_navigate):
        super().__init__(parent)
        self.colors = colors
        self.on_navigate = on_navigate
        self.configure(bg=colors['bg_primary'])
        
        self.create_widgets()
    
    def create_widgets(self):
        center_frame = tk.Frame(self, bg=self.colors['bg_primary'])
        center_frame.place(relx=0.5, rely=0.5, anchor='center')
        
        title_label = tk.Label(
            center_frame,
            text='Amicom',
            font=('Segoe UI', 32, 'bold'),
            fg=self.colors['accent'],
            bg=self.colors['bg_primary']
        )
        title_label.pack(pady=(0, 10))
        
        subtitle_label = tk.Label(
            center_frame,
            text='Sistema de Registro de Empresas',
            font=('Segoe UI', 12),
            fg=self.colors['text_secondary'],
            bg=self.colors['bg_primary']
        )
        subtitle_label.pack(pady=(0, 40))
        
        self.btn_cadastros = self.create_menu_button(
            center_frame, '📋 Cadastros', lambda: self.on_navigate('cadastros')
        )
        self.btn_cadastros.pack(fill='x', pady=10, ipadx=40, ipady=10)
        
        self.btn_gerenciamento = self.create_menu_button(
            center_frame, '📊 Gerenciamento', lambda: self.on_navigate('gerenciamento')
        )
        self.btn_gerenciamento.pack(fill='x', pady=10, ipadx=40, ipady=10)
        
        self.btn_configuracoes = self.create_menu_button(
            center_frame, '⚙️ Configuracoes', lambda: self.on_navigate('configuracoes')
        )
        self.btn_configuracoes.pack(fill='x', pady=10, ipadx=40, ipady=10)
    
    def create_menu_button(self, parent, text, command):
        btn = tk.Button(
            parent,
            text=text,
            font=('Segoe UI', 13, 'bold'),
            fg=self.colors['text_primary'],
            bg=self.colors['bg_secondary'],
            activebackground=self.colors['bg_tertiary'],
            activeforeground=self.colors['text_primary'],
            borderwidth=0,
            padx=30,
            pady=15,
            cursor='hand2',
            command=command
        )
        btn.bind('<Enter>', self.on_hover)
        btn.bind('<Leave>', self.on_leave)
        return btn
    
    def on_hover(self, event):
        event.widget.configure(bg=self.colors['bg_tertiary'])
    
    def on_leave(self, event):
        event.widget.configure(bg=self.colors['bg_secondary'])
