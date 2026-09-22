import tkinter as tk
from tkinter import ttk

class ContentArea(tk.Frame):
    """Area de conteudo principal."""
    
    def __init__(self, parent, colors):
        super().__init__(parent)
        self.colors = colors
        self.configure(bg=colors['bg_primary'])
        
        self.create_widgets()
    
    def create_widgets(self):
        main_frame = tk.Frame(self, bg=self.colors['bg_primary'])
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        welcome_frame = tk.Frame(main_frame, bg=self.colors['bg_primary'])
        welcome_frame.pack(fill='x', pady=(0, 30))
        
        welcome_label = tk.Label(
            welcome_frame,
            text='Bem-vindo ao BusinessReg',
            font=('Segoe UI', 24, 'bold'),
            fg=self.colors['text_primary'],
            bg=self.colors['bg_primary']
        )
        welcome_label.pack(anchor='w')
        
        subtitle_label = tk.Label(
            welcome_frame,
            text='Selecione uma opcao no menu lateral para comecar',
            font=('Segoe UI', 11),
            fg=self.colors['text_secondary'],
            bg=self.colors['bg_primary']
        )
        subtitle_label.pack(anchor='w', pady=(5, 0))
        
        cards_frame = tk.Frame(main_frame, bg=self.colors['bg_primary'])
        cards_frame.pack(fill='both', expand=True)
        
        self.create_card(cards_frame, '📋 Cadastros', 'Registre novas empresas', 0)
        self.create_card(cards_frame, '📊 Gerenciamento', 'Gerencie empresas cadastradas', 1)
        self.create_card(cards_frame, '⚙️ Configuracoes', 'Ajuste preferencias', 2)
    
    def create_card(self, parent, title, desc, index):
        card = tk.Frame(
            parent,
            bg=self.colors['bg_secondary'],
            highlightbackground=self.colors['border'],
            highlightthickness=1
        )
        card.grid(row=0, column=index, sticky='nsew', padx=10, pady=10)
        parent.columnconfigure(index, weight=1)
        
        content = tk.Frame(card, bg=self.colors['bg_secondary'])
        content.pack(fill='both', expand=True, padx=20, pady=20)
        
        tk.Label(
            content,
            text=title,
            font=('Segoe UI', 14, 'bold'),
            fg=self.colors['text_primary'],
            bg=self.colors['bg_secondary']
        ).pack(anchor='w', pady=(0, 10))
        
        tk.Label(
            content,
            text=desc,
            font=('Segoe UI', 10),
            fg=self.colors['text_secondary'],
            bg=self.colors['bg_secondary'],
            wraplength=250,
            justify='left'
        ).pack(anchor='w')
