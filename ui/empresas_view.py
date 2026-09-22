import tkinter as tk
from tkinter import ttk, messagebox

from database import create_empresa, list_empresas


class EmpresasView(tk.Frame):
    """Tela para gerenciar empresas cadastradas."""

    def __init__(self, parent, colors, on_back):
        super().__init__(parent)
        self.colors = colors
        self.on_back = on_back
        self.configure(bg=colors['bg_primary'])

        self.selected_company = None
        self.configure_treeview_style()
        self.create_widgets()
        self.load_companies()

    def configure_treeview_style(self):
        style = ttk.Style()
        style.theme_use('clam')

        style.configure(
            'Empresas.Treeview',
            background=self.colors['bg_secondary'],
            fieldbackground=self.colors['bg_secondary'],
            foreground=self.colors['text_primary'],
            rowheight=38,
            borderwidth=0,
            font=('Segoe UI', 10)
        )
        style.configure(
            'Empresas.Treeview.Heading',
            background=self.colors['bg_tertiary'],
            foreground=self.colors['text_primary'],
            relief='flat',
            font=('Segoe UI', 10, 'bold')
        )
        style.map(
            'Empresas.Treeview',
            background=[('selected', self.colors['accent'])],
            foreground=[('selected', self.colors['text_primary'])]
        )

    def create_widgets(self):
        container = tk.Frame(self, bg=self.colors['bg_primary'])
        container.pack(fill='both', expand=True, padx=40, pady=30)

        self.create_header(container)
        self.create_toolbar(container)
        self.create_table(container)
        self.create_actions(container)

    def create_header(self, parent):
        header = tk.Frame(parent, bg=self.colors['bg_primary'])
        header.pack(fill='x')

        btn_back = self.create_button(
            header, '← Voltar', self.on_back,
            self.colors['bg_secondary'], self.colors['text_secondary'],
            ('Segoe UI', 10), 15, 8
        )
        btn_back.pack(anchor='w')

        title = tk.Label(
            header, text='🏢 Empresas', font=('Segoe UI', 24, 'bold'),
            fg=self.colors['text_primary'], bg=self.colors['bg_primary']
        )
        title.pack(anchor='w', pady=(28, 4))

        subtitle = tk.Label(
            header, text='Adicione, edite ou exclua empresas cadastradas.',
            font=('Segoe UI', 10), fg=self.colors['text_secondary'],
            bg=self.colors['bg_primary']
        )
        subtitle.pack(anchor='w', pady=(0, 22))

    def create_toolbar(self, parent):
        toolbar = tk.Frame(parent, bg=self.colors['bg_primary'])
        toolbar.pack(fill='x', pady=(0, 16))

        search_frame = tk.Frame(toolbar, bg=self.colors['bg_secondary'])
        search_frame.pack(side='left', fill='x', expand=True, padx=(0, 12))

        tk.Label(
            search_frame, text='⌕', font=('Segoe UI', 14),
            fg=self.colors['text_secondary'], bg=self.colors['bg_secondary']
        ).pack(side='left', padx=(12, 4))

        self.search_var = tk.StringVar()
        self.search_entry = tk.Entry(
            search_frame, textvariable=self.search_var, font=('Segoe UI', 10),
            fg=self.colors['text_secondary'], bg=self.colors['bg_secondary'],
            insertbackground=self.colors['text_primary'], relief='flat', borderwidth=0
        )
        self.search_entry.pack(side='left', fill='x', expand=True, padx=(0, 12), pady=10)
        self.search_entry.insert(0, 'Buscar empresa...')
        self.search_entry.bind('<FocusIn>', self.clear_search_placeholder)
        self.search_entry.bind('<FocusOut>', self.restore_search_placeholder)
        self.search_entry.bind('<KeyRelease>', self.filter_companies)

        self.btn_add = self.create_button(
            toolbar, '+ Adicionar Empresa', self.open_add_dialog,
            self.colors['accent'], self.colors['text_primary'],
            ('Segoe UI', 10, 'bold'), 18, 10
        )
        self.btn_add.pack(side='right')

    def create_table(self, parent):
        table_frame = tk.Frame(
            parent, bg=self.colors['bg_secondary'],
            highlightbackground=self.colors['border'], highlightthickness=1
        )
        table_frame.pack(fill='both', expand=True)

        columns = ('id', 'nome', 'localizacao')
        self.tree = ttk.Treeview(
            table_frame, columns=columns, show='headings',
            style='Empresas.Treeview', selectmode='browse'
        )

        self.tree.heading('id', text='ID')
        self.tree.heading('nome', text='NOME DA EMPRESA')
        self.tree.heading('localizacao', text='LOCALIZAÇÃO')

        self.tree.column('id', width=80, minwidth=60, anchor='center', stretch=False)
        self.tree.column('nome', width=400, minwidth=220, anchor='w')
        self.tree.column('localizacao', width=360, minwidth=180, anchor='w')

        scrollbar = ttk.Scrollbar(table_frame, orient='vertical', command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side='left', fill='both', expand=True, padx=(1, 0), pady=1)
        scrollbar.pack(side='right', fill='y', padx=(0, 1), pady=1)
        self.tree.bind('<<TreeviewSelect>>', self.on_select_company)

        self.empty_label = tk.Label(
            table_frame,
            text='Nenhuma empresa cadastrada\nClique em “+ Adicionar Empresa” para começar.',
            font=('Segoe UI', 11), fg=self.colors['text_secondary'],
            bg=self.colors['bg_secondary'], justify='center'
        )

    def create_actions(self, parent):
        actions = tk.Frame(parent, bg=self.colors['bg_primary'])
        actions.pack(fill='x', pady=(16, 0))

        self.btn_edit = self.create_button(
            actions, '✎ Editar', self.edit_company,
            self.colors['bg_tertiary'], self.colors['text_primary'],
            ('Segoe UI', 10, 'bold'), 20, 10, state='disabled'
        )
        self.btn_edit.pack(side='left')

        self.btn_delete = self.create_button(
            actions, '🗑 Excluir', self.delete_company,
            self.colors['bg_secondary'], self.colors['text_secondary'],
            ('Segoe UI', 10, 'bold'), 20, 10, state='disabled'
        )
        self.btn_delete.pack(side='left', padx=(10, 0))

    def create_button(self, parent, text, command, background, foreground, font, padx, pady, state='normal'):
        button = tk.Button(
            parent, text=text, command=command, font=font, fg=foreground, bg=background,
            activebackground=self.colors['bg_tertiary'],
            activeforeground=self.colors['text_primary'], disabledforeground='#666b7c',
            borderwidth=0, padx=padx, pady=pady,
            cursor='hand2' if state == 'normal' else 'arrow', state=state
        )
        if state == 'normal':
            button.bind('<Enter>', lambda e: e.widget.configure(bg=self.colors['bg_tertiary']))
            button.bind('<Leave>', lambda e: e.widget.configure(bg=background))
        return button

    def clear_search_placeholder(self, event):
        if self.search_var.get() == 'Buscar empresa...':
            self.search_var.set('')
            self.search_entry.configure(fg=self.colors['text_primary'])

    def restore_search_placeholder(self, event):
        if not self.search_var.get().strip():
            self.search_var.set('Buscar empresa...')
            self.search_entry.configure(fg=self.colors['text_secondary'])

    def filter_companies(self, event=None):
        search = self.search_var.get()
        if search == 'Buscar empresa...':
            search = ''
        self.load_companies(search)

    def load_companies(self, search=''):
        for item in self.tree.get_children():
            self.tree.delete(item)

        empresas = list_empresas(search)
        for empresa in empresas:
            self.tree.insert('', 'end', iid=str(empresa['id']), values=(
                empresa['id'], empresa['nome'], empresa['localizacao'] or '-'
            ))

        if empresas:
            self.empty_label.place_forget()
        else:
            self.empty_label.place(relx=0.5, rely=0.5, anchor='center')

        self.selected_company = None
        self.btn_edit.configure(state='disabled')
        self.btn_delete.configure(state='disabled')

    def on_select_company(self, event=None):
        selection = self.tree.selection()
        self.selected_company = selection[0] if selection else None
        state = 'normal' if self.selected_company else 'disabled'
        self.btn_edit.configure(state=state)
        self.btn_delete.configure(state=state)

    def open_add_dialog(self):
        dialog = tk.Toplevel(self)
        dialog.title('Adicionar Empresa')
        dialog.configure(bg=self.colors['bg_primary'])
        dialog.resizable(False, False)
        dialog.transient(self.winfo_toplevel())
        dialog.grab_set()

        width, height = 430, 300
        parent = self.winfo_toplevel()
        x = parent.winfo_x() + (parent.winfo_width() - width) // 2
        y = parent.winfo_y() + (parent.winfo_height() - height) // 2
        dialog.geometry(f'{width}x{height}+{x}+{y}')

        content = tk.Frame(dialog, bg=self.colors['bg_primary'])
        content.pack(fill='both', expand=True, padx=28, pady=26)

        tk.Label(
            content, text='Adicionar empresa', font=('Segoe UI', 18, 'bold'),
            fg=self.colors['text_primary'], bg=self.colors['bg_primary']
        ).pack(anchor='w', pady=(0, 20))

        nome_var = tk.StringVar()
        localizacao_var = tk.StringVar()

        nome_entry = self.create_form_field(content, 'Nome da empresa *', nome_var)
        nome_entry.pack(fill='x', pady=(0, 14))
        self.create_form_field(content, 'Localização', localizacao_var).pack(fill='x')

        actions = tk.Frame(content, bg=self.colors['bg_primary'])
        actions.pack(fill='x', pady=(24, 0))

        cancel_button = self.create_button(
            actions, 'Cancelar', dialog.destroy,
            self.colors['bg_secondary'], self.colors['text_secondary'],
            ('Segoe UI', 10), 16, 9
        )
        cancel_button.pack(side='right')

        save_button = self.create_button(
            actions, 'Salvar',
            lambda: self.save_new_company(dialog, nome_var.get(), localizacao_var.get()),
            self.colors['accent'], self.colors['text_primary'],
            ('Segoe UI', 10, 'bold'), 18, 9
        )
        save_button.pack(side='right', padx=(0, 10))

        dialog.bind('<Return>', lambda event: self.save_new_company(dialog, nome_var.get(), localizacao_var.get()))
        dialog.bind('<Escape>', lambda event: dialog.destroy())
        dialog.after(100, nome_entry.focus_set)

    def create_form_field(self, parent, label_text, variable):
        field = tk.Frame(parent, bg=self.colors['bg_primary'])
        tk.Label(
            field, text=label_text, font=('Segoe UI', 10),
            fg=self.colors['text_secondary'], bg=self.colors['bg_primary']
        ).pack(anchor='w', pady=(0, 6))
        entry = tk.Entry(
            field, textvariable=variable, font=('Segoe UI', 11),
            fg=self.colors['text_primary'], bg=self.colors['bg_secondary'],
            insertbackground=self.colors['text_primary'], relief='flat', borderwidth=0
        )
        entry.pack(fill='x', ipady=9)
        return entry

    def save_new_company(self, dialog, nome, localizacao):
        if not nome.strip():
            messagebox.showwarning('Campo obrigatório', 'Informe o nome da empresa.', parent=dialog)
            return

        create_empresa(nome, localizacao)
        dialog.destroy()
        self.load_companies()

    def edit_company(self):
        if self.selected_company:
            messagebox.showinfo('Em desenvolvimento', 'A edição será implementada no próximo passo.')

    def delete_company(self):
        if self.selected_company:
            messagebox.showinfo('Em desenvolvimento', 'A exclusão será implementada no próximo passo.')
