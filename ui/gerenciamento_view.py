import tkinter as tk


class GerenciamentoView(tk.Frame):
    """Tela de Gerenciamento com layout responsivo."""

    def __init__(self, parent, colors, on_back, on_navigate):
        super().__init__(parent)
        self.colors = colors
        self.on_back = on_back
        self.on_navigate = on_navigate
        self.configure(bg=colors['bg_primary'])

        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=0)
        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.create_widgets()

    def create_widgets(self):
        header = tk.Frame(self, bg=self.colors['bg_primary'])
        header.grid(row=0, column=0, sticky='ew', padx=40, pady=(30, 0))

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
            text='📊 Gerenciamento',
            font=('Segoe UI', 24, 'bold'),
            fg=self.colors['text_primary'],
            bg=self.colors['bg_primary']
        )
        title.grid(row=1, column=0, pady=(45, 20))

        menu_frame = tk.Frame(self, bg=self.colors['bg_primary'])
        menu_frame.grid(row=2, column=0, sticky='n', pady=(0, 30))

        self.btn_empresas = self.create_submenu_button(
            menu_frame, '🏢 Empresas', lambda: self.on_navigate('empresas')
        )
        self.btn_empresas.pack(fill='x', pady=8, ipadx=40, ipady=10)

        self.btn_categorias = self.create_submenu_button(
            menu_frame, '📁 Categorias', lambda: self.on_navigate('categorias')
        )
        self.btn_categorias.pack(fill='x', pady=8, ipadx=40, ipady=10)

        self.btn_campos = self.create_submenu_button(
            menu_frame, '🏷️ Campos', lambda: self.on_navigate('campos')
        )
        self.btn_campos.pack(fill='x', pady=8, ipadx=40, ipady=10)

    def create_submenu_button(self, parent, text, command):
        btn = tk.Button(
            parent,
            text=text,
            font=('Segoe UI', 12, 'bold'),
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
        btn.bind('<Enter>', lambda e: e.widget.configure(bg=self.colors['bg_tertiary']))
        btn.bind('<Leave>', lambda e: e.widget.configure(bg=self.colors['bg_secondary']))
        return btn
