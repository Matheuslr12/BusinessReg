import tkinter as tk
from tkinter import ttk

class Sidebar(tk.Frame):
    """Menu lateral de navegacao."""
    
    def __init__(self, parent, colors):
        super().__init__(parent)
        self.colors = colors
        self.configure(bg=colors['bg_secondary'], width=250)
        self.pack_propagate(False)
        
        self.create_widgets()
    
    def create_widgets(self):
        title_frame = tk.Frame(self, bg=self.colors['bg_secondary'])
        title_frame.pack(fill='x', padx=20, pady=30)
        
        title_label = tk.Label(
            title_frame,
            text='BusinessReg',
            font=('Segoe UI', 20, 'bold'),
            fg=self.colors['accent'],
            bg=self.colors['bg_secondary']
        )
        title_label.pack(anchor='w')
        
        subtitle_label = tk.Label(
            title_frame,
            text='Sistema de Gestao',
            font=('Segoe UI', 9),
            fg=self.colors['text_secondary'],
            bg=self.colors['bg_secondary']
        )
        subtitle_label.pack(anchor='w')
        
        separator = tk.Frame(self, bg=self.colors['border'], height=1)
        separator.pack(fill='x', padx=20, pady=20)
        
        menu_frame = tk.Frame(self, bg=self.colors['bg_secondary'])
        menu_frame.pack(fill='both', expand=True, padx=10)
        
        self.btn_cadastros = self.create_menu_button(
            menu_frame, '📋 Cadastros', self.on_cadastros_click
        )
        self.btn_cadastros.pack(fill='x', pady=5)
        
        self.btn_gerenciamento = self.create_menu_button(
            menu_frame, '📊 Gerenciamento', self.on_gerenciamento_click
        )
        self.btn_gerenciamento.pack(fill='x', pady=5)
        
        self.btn_configuracoes = self.create_menu_button(
            menu_frame, '⚙️ Configuracoes', self.on_configuracoes_click
        )
        self.btn_configuracoes.pack(fill='x', pady=5)
        
        footer_frame = tk.Frame(self, bg=self.colors['bg_secondary'])
        footer_frame.pack(fill='x', side='bottom', pady=20)
        
        version_label = tk.Label(
            footer_frame,
            text='v1.0.0',
            font=('Segoe UI', 8),
            fg=self.colors['text_secondary'],
            bg=self.colors['bg_secondary']
        )
        version_label.pack()
    
    def create_menu_button(self, parent, text, command):
        btn = tk.Button(
            parent,
            text=text,
            font=('Segoe UI', 11),
            fg=self.colors['text_primary'],
            bg=self.colors['bg_secondary'],
            activebackground=self.colors['bg_tertiary'],
            activeforeground=self.colors['text_primary'],
            borderwidth=0,
            anchor='w',
            padx=20,
            pady=12,
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
    
    def on_cadastros_click(self):
        print('Navegando para: Cadastros')
    
    def on_gerenciamento_click(self):
        print('Navegando para: Gerenciamento')
    
    def on_configuracoes_click(self):
        print('Navegando para: Configuracoes')
