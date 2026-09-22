import tkinter as tk

class CadastrosView(tk.Frame):
    """Tela de Cadastros."""
    
    def __init__(self, parent, colors, on_back):
        super().__init__(parent)
        self.colors = colors
        self.on_back = on_back
        self.configure(bg=colors['bg_primary'])
        
        self.create_widgets()
    
    def create_widgets(self):
        header = tk.Frame(self, bg=self.colors['bg_primary'])
        header.pack(fill='x', padx=40, pady=30)
        
        btn_back = tk.Button(
            header,
            text='← Voltar',
            font=('Segoe UI', 10),
            fg=self.colors['text_secondary'],
            bg=self.colors['bg_secondary'],
            activebackground=self.colors['bg_tertiary'],
            activeforeground=self.colors['text_primary'],
            borderwidth=0,
            padx=15,
            pady=8,
            cursor='hand2',
            command=self.on_back
        )
        btn_back.pack(anchor='w')
        btn_back.bind('<Enter>', lambda e: e.widget.configure(bg=self.colors['bg_tertiary']))
        btn_back.bind('<Leave>', lambda e: e.widget.configure(bg=self.colors['bg_secondary']))
        
        title = tk.Label(
            self,
            text='📋 Cadastros',
            font=('Segoe UI', 24, 'bold'),
            fg=self.colors['text_primary'],
            bg=self.colors['bg_primary']
        )
        title.pack(pady=20)
        
        content = tk.Label(
            self,
            text='Formulario de cadastro em desenvolvimento...',
            font=('Segoe UI', 11),
            fg=self.colors['text_secondary'],
            bg=self.colors['bg_primary']
        )
        content.pack(pady=40)
