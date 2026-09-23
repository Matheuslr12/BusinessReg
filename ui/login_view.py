import tkinter as tk
from tkinter import messagebox

from database import authenticate_user, create_master_user, master_exists


class LoginView(tk.Frame):
    """Tela de primeiro acesso e autenticação do usuário master."""

    def __init__(self, parent, colors, on_authenticated):
        super().__init__(parent)
        self.colors = colors
        self.on_authenticated = on_authenticated
        self.configure(bg=colors['bg_primary'])
        self.show_screen()

    def show_screen(self):
        for widget in self.winfo_children():
            widget.destroy()
        if master_exists():
            self.create_login_screen()
        else:
            self.create_first_access_screen()

    def create_base(self, title, subtitle):
        card = tk.Frame(
            self,
            bg=self.colors['bg_secondary'],
            highlightbackground=self.colors['border'],
            highlightthickness=1
        )
        card.place(relx=0.5, rely=0.5, anchor='center', width=430)

        content = tk.Frame(card, bg=self.colors['bg_secondary'])
        content.pack(fill='both', expand=True, padx=36, pady=34)

        tk.Label(
            content, text='Amicom', font=('Segoe UI', 26, 'bold'),
            fg=self.colors['accent'], bg=self.colors['bg_secondary']
        ).pack(anchor='w')
        tk.Label(
            content, text='Sistema Integrado de Informações', font=('Segoe UI', 10),
            fg=self.colors['text_secondary'], bg=self.colors['bg_secondary']
        ).pack(anchor='w', pady=(2, 30))
        tk.Label(
            content, text=title, font=('Segoe UI', 18, 'bold'),
            fg=self.colors['text_primary'], bg=self.colors['bg_secondary']
        ).pack(anchor='w')
        tk.Label(
            content, text=subtitle, font=('Segoe UI', 10),
            fg=self.colors['text_secondary'], bg=self.colors['bg_secondary'],
            wraplength=350, justify='left'
        ).pack(anchor='w', pady=(6, 24))
        return content

    def create_first_access_screen(self):
        content = self.create_base(
            'Primeiro acesso',
            'Crie a senha da conta master. Essa conta terá acesso completo ao sistema.'
        )

        tk.Label(
            content, text='Usuário', font=('Segoe UI', 10),
            fg=self.colors['text_secondary'], bg=self.colors['bg_secondary']
        ).pack(anchor='w', pady=(0, 6))
        master_entry = tk.Entry(
            content, font=('Segoe UI', 11), fg=self.colors['text_secondary'],
            bg=self.colors['bg_primary'], relief='flat', borderwidth=0
        )
        master_entry.pack(fill='x', ipady=10)
        master_entry.insert(0, 'master')
        master_entry.configure(state='disabled')

        password_var = tk.StringVar()
        confirm_var = tk.StringVar()
        password_entry = self.create_password_field(content, 'Defina uma senha', password_var)
        self.create_password_field(content, 'Confirme a senha', confirm_var)

        button = self.create_button(
            content, 'Criar conta master',
            lambda: self.create_master(password_var.get(), confirm_var.get())
        )
        button.pack(fill='x', pady=(26, 0))
        content.bind_all('<Return>', lambda event: self.create_master(password_var.get(), confirm_var.get()))
        password_entry.focus_set()

    def create_login_screen(self):
        content = self.create_base(
            'Entrar no sistema',
            'Informe a senha da conta master para acessar o Amicom.'
        )

        tk.Label(
            content, text='Usuário', font=('Segoe UI', 10),
            fg=self.colors['text_secondary'], bg=self.colors['bg_secondary']
        ).pack(anchor='w', pady=(0, 6))
        username_var = tk.StringVar(value='master')
        username_entry = tk.Entry(
            content, textvariable=username_var, font=('Segoe UI', 11),
            fg=self.colors['text_secondary'], bg=self.colors['bg_primary'],
            relief='flat', borderwidth=0
        )
        username_entry.pack(fill='x', ipady=10)
        username_entry.configure(state='disabled')

        password_var = tk.StringVar()
        password_entry = self.create_password_field(content, 'Senha', password_var)
        button = self.create_button(
            content, 'Entrar', lambda: self.login('master', password_var.get())
        )
        button.pack(fill='x', pady=(26, 0))
        content.bind_all('<Return>', lambda event: self.login('master', password_var.get()))
        password_entry.focus_set()

    def create_password_field(self, parent, label, variable):
        tk.Label(
            parent, text=label, font=('Segoe UI', 10),
            fg=self.colors['text_secondary'], bg=self.colors['bg_secondary']
        ).pack(anchor='w', pady=(18, 6))
        entry = tk.Entry(
            parent, textvariable=variable, show='•', font=('Segoe UI', 12),
            fg=self.colors['text_primary'], bg=self.colors['bg_primary'],
            insertbackground=self.colors['text_primary'], relief='flat', borderwidth=0
        )
        entry.pack(fill='x', ipady=10)
        return entry

    def create_button(self, parent, text, command):
        button = tk.Button(
            parent, text=text, command=command, font=('Segoe UI', 11, 'bold'),
            fg=self.colors['text_primary'], bg=self.colors['accent'],
            activebackground=self.colors['bg_tertiary'],
            activeforeground=self.colors['text_primary'], borderwidth=0,
            pady=12, cursor='hand2'
        )
        button.bind('<Enter>', lambda event: event.widget.configure(bg=self.colors['bg_tertiary']))
        button.bind('<Leave>', lambda event: event.widget.configure(bg=self.colors['accent']))
        return button

    def create_master(self, password, confirmation):
        if len(password) < 4:
            messagebox.showwarning('Senha inválida', 'Defina uma senha com pelo menos 4 caracteres.', parent=self.winfo_toplevel())
            return
        if password != confirmation:
            messagebox.showwarning('Senhas diferentes', 'A confirmação de senha não corresponde.', parent=self.winfo_toplevel())
            return
        try:
            create_master_user(password)
        except Exception:
            messagebox.showerror('Erro', 'Não foi possível criar a conta master.', parent=self.winfo_toplevel())
            return
        messagebox.showinfo('Conta criada', 'A conta master foi criada com sucesso.', parent=self.winfo_toplevel())
        self.on_authenticated({'usuario': 'master', 'papel': 'master'})

    def login(self, username, password):
        if not password:
            messagebox.showwarning('Senha obrigatória', 'Informe a senha para entrar.', parent=self.winfo_toplevel())
            return
        user = authenticate_user(username, password)
        if not user:
            messagebox.showerror('Acesso negado', 'Senha incorreta.', parent=self.winfo_toplevel())
            return
        self.on_authenticated(user)
