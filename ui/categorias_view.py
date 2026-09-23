import tkinter as tk
from tkinter import ttk, messagebox

from database import create_categoria, delete_categoria, get_categoria, list_categorias, move_categoria, update_categoria


class CategoriasView(tk.Frame):
    """Tela para gerenciar categorias dos campos de cadastro."""

    def __init__(self, parent, colors, on_back):
        super().__init__(parent)
        self.colors = colors
        self.on_back = on_back
        self.configure(bg=colors['bg_primary'])
        self.selected_category = None
        self.categories_data = {}
        self.configure_treeview_style()
        self.create_widgets()
        self.load_categories()

    def refresh_view(self):
        self.load_categories(self.get_current_search())

    def configure_treeview_style(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('Categorias.Treeview', background=self.colors['bg_secondary'], fieldbackground=self.colors['bg_secondary'], foreground=self.colors['text_primary'], rowheight=38, borderwidth=0, font=('Segoe UI', 10))
        style.configure('Categorias.Treeview.Heading', background=self.colors['bg_tertiary'], foreground=self.colors['text_primary'], relief='flat', font=('Segoe UI', 10, 'bold'))
        style.map('Categorias.Treeview', background=[('selected', self.colors['accent'])], foreground=[('selected', self.colors['text_primary'])])

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
        self.create_button(header, '← Voltar', self.on_back, self.colors['bg_secondary'], self.colors['text_secondary'], ('Segoe UI', 10), 15, 8).pack(anchor='w')
        tk.Label(header, text='📁 Categorias', font=('Segoe UI', 24, 'bold'), fg=self.colors['text_primary'], bg=self.colors['bg_primary']).pack(anchor='w', pady=(28, 4))
        tk.Label(header, text='Organize os campos e defina a ordem das categorias no menu de cadastros.', font=('Segoe UI', 10), fg=self.colors['text_secondary'], bg=self.colors['bg_primary']).pack(anchor='w', pady=(0, 22))

    def create_toolbar(self, parent):
        toolbar = tk.Frame(parent, bg=self.colors['bg_primary'])
        toolbar.pack(fill='x', pady=(0, 16))
        search_frame = tk.Frame(toolbar, bg=self.colors['bg_secondary'])
        search_frame.pack(side='left', fill='x', expand=True, padx=(0, 12))
        tk.Label(search_frame, text='⌕', font=('Segoe UI', 14), fg=self.colors['text_secondary'], bg=self.colors['bg_secondary']).pack(side='left', padx=(12, 4))
        self.search_var = tk.StringVar()
        self.search_entry = tk.Entry(search_frame, textvariable=self.search_var, font=('Segoe UI', 10), fg=self.colors['text_secondary'], bg=self.colors['bg_secondary'], insertbackground=self.colors['text_primary'], relief='flat', borderwidth=0)
        self.search_entry.pack(side='left', fill='x', expand=True, padx=(0, 12), pady=10)
        self.search_entry.insert(0, 'Buscar categoria...')
        self.search_entry.bind('<FocusIn>', self.clear_search_placeholder)
        self.search_entry.bind('<FocusOut>', self.restore_search_placeholder)
        self.search_entry.bind('<KeyRelease>', self.filter_categories)
        self.create_button(toolbar, '+ Adicionar Categoria', self.open_add_dialog, self.colors['accent'], self.colors['text_primary'], ('Segoe UI', 10, 'bold'), 18, 10).pack(side='right')

    def create_table(self, parent):
        table_frame = tk.Frame(parent, bg=self.colors['bg_secondary'], highlightbackground=self.colors['border'], highlightthickness=1)
        table_frame.pack(fill='both', expand=True)
        self.tree = ttk.Treeview(table_frame, columns=('ordem', 'nome', 'descricao'), show='headings', style='Categorias.Treeview', selectmode='browse')
        self.tree.heading('ordem', text='ORDEM')
        self.tree.heading('nome', text='NOME DA CATEGORIA')
        self.tree.heading('descricao', text='DESCRIÇÃO')
        self.tree.column('ordem', width=90, minwidth=70, anchor='center', stretch=False)
        self.tree.column('nome', width=300, minwidth=180, anchor='w')
        self.tree.column('descricao', width=500, minwidth=220, anchor='w')
        scrollbar = ttk.Scrollbar(table_frame, orient='vertical', command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side='left', fill='both', expand=True, padx=(1, 0), pady=1)
        scrollbar.pack(side='right', fill='y', padx=(0, 1), pady=1)
        self.tree.bind('<<TreeviewSelect>>', self.on_select_category)
        self.empty_label = tk.Label(table_frame, text='Nenhuma categoria cadastrada\nClique em “+ Adicionar Categoria” para começar.', font=('Segoe UI', 11), fg=self.colors['text_secondary'], bg=self.colors['bg_secondary'], justify='center')

    def create_actions(self, parent):
        actions = tk.Frame(parent, bg=self.colors['bg_primary'])
        actions.pack(fill='x', pady=(16, 0))
        self.btn_up = self.create_button(actions, '↑ Mover para cima', self.move_selected_up, self.colors['bg_tertiary'], self.colors['text_primary'], ('Segoe UI', 10, 'bold'), 16, 10, state='disabled')
        self.btn_up.pack(side='left')
        self.btn_down = self.create_button(actions, '↓ Mover para baixo', self.move_selected_down, self.colors['bg_tertiary'], self.colors['text_primary'], ('Segoe UI', 10, 'bold'), 16, 10, state='disabled')
        self.btn_down.pack(side='left', padx=(10, 0))
        self.btn_edit = self.create_button(actions, '✎ Editar', self.edit_category, self.colors['bg_tertiary'], self.colors['text_primary'], ('Segoe UI', 10, 'bold'), 20, 10, state='disabled')
        self.btn_edit.pack(side='left', padx=(18, 0))
        self.btn_delete = self.create_button(actions, '🗑 Excluir', self.delete_category, self.colors['bg_secondary'], self.colors['text_secondary'], ('Segoe UI', 10, 'bold'), 20, 10, state='disabled')
        self.btn_delete.pack(side='left', padx=(10, 0))

    def create_button(self, parent, text, command, background, foreground, font, padx, pady, state='normal'):
        button = tk.Button(parent, text=text, command=command, font=font, fg=foreground, bg=background, activebackground=self.colors['bg_tertiary'], activeforeground=self.colors['text_primary'], disabledforeground='#666b7c', borderwidth=0, padx=padx, pady=pady, cursor='hand2' if state == 'normal' else 'arrow', state=state)
        if state == 'normal':
            button.bind('<Enter>', lambda e: e.widget.configure(bg=self.colors['accent']))
            button.bind('<Leave>', lambda e: e.widget.configure(bg=background))
        return button

    def clear_search_placeholder(self, event):
        if self.search_var.get() == 'Buscar categoria...':
            self.search_var.set('')
            self.search_entry.configure(fg=self.colors['text_primary'])

    def restore_search_placeholder(self, event):
        if not self.search_var.get().strip():
            self.search_var.set('Buscar categoria...')
            self.search_entry.configure(fg=self.colors['text_secondary'])

    def get_current_search(self):
        search = self.search_var.get().strip()
        return '' if search == 'Buscar categoria...' else search

    def filter_categories(self, event=None):
        self.load_categories(self.get_current_search())

    def load_categories(self, search='', keep_selection=False):
        previous_selection = self.selected_category if keep_selection else None
        for item in self.tree.get_children():
            self.tree.delete(item)
        categorias = list_categorias(search)
        self.categories_data = {categoria['id']: categoria for categoria in categorias}
        for categoria in categorias:
            self.tree.insert('', 'end', iid=str(categoria['id']), values=(categoria['ordem'], categoria['nome'], categoria['descricao'] or '-'))
        if categorias:
            self.empty_label.place_forget()
        else:
            self.empty_label.place(relx=0.5, rely=0.5, anchor='center')
        self.selected_category = None
        self.disable_actions()
        if previous_selection and previous_selection in self.categories_data:
            self.tree.selection_set(str(previous_selection))
            self.tree.focus(str(previous_selection))
            self.on_select_category()

    def on_select_category(self, event=None):
        selection = self.tree.selection()
        self.selected_category = int(selection[0]) if selection else None
        self.update_actions_state()

    def update_actions_state(self):
        if not self.selected_category:
            self.disable_actions()
            return
        categorias = sorted(self.categories_data.values(), key=lambda categoria: (categoria['ordem'], categoria['id']))
        current_index = next(index for index, categoria in enumerate(categorias) if categoria['id'] == self.selected_category)
        self.btn_up.configure(state='normal' if current_index > 0 else 'disabled')
        self.btn_down.configure(state='normal' if current_index < len(categorias) - 1 else 'disabled')
        self.btn_edit.configure(state='normal')
        self.btn_delete.configure(state='normal')

    def disable_actions(self):
        self.btn_up.configure(state='disabled')
        self.btn_down.configure(state='disabled')
        self.btn_edit.configure(state='disabled')
        self.btn_delete.configure(state='disabled')

    def move_selected_up(self):
        if self.selected_category and move_categoria(self.selected_category, 'up'):
            self.load_categories(keep_selection=True)

    def move_selected_down(self):
        if self.selected_category and move_categoria(self.selected_category, 'down'):
            self.load_categories(keep_selection=True)

    def open_add_dialog(self):
        self.open_category_dialog()

    def edit_category(self):
        if not self.selected_category:
            return
        categoria = get_categoria(self.selected_category)
        if categoria:
            self.open_category_dialog(categoria)

    def open_category_dialog(self, categoria=None):
        editing = categoria is not None
        dialog = tk.Toplevel(self)
        dialog.title('Editar Categoria' if editing else 'Adicionar Categoria')
        dialog.configure(bg=self.colors['bg_primary'])
        dialog.resizable(False, False)
        dialog.transient(self.winfo_toplevel())
        dialog.grab_set()
        width, height = 410, 370
        parent = self.winfo_toplevel()
        x = parent.winfo_x() + (parent.winfo_width() - width) // 2
        y = parent.winfo_y() + (parent.winfo_height() - height) // 2
        dialog.geometry(f'{width}x{height}+{x}+{y}')
        content = tk.Frame(dialog, bg=self.colors['bg_primary'])
        content.pack(fill='both', expand=True, padx=28, pady=26)
        tk.Label(content, text='Editar categoria' if editing else 'Adicionar categoria', font=('Segoe UI', 18, 'bold'), fg=self.colors['text_primary'], bg=self.colors['bg_primary']).pack(anchor='w', pady=(0, 20))
        nome_var = tk.StringVar(value=categoria['nome'] if editing else '')
        descricao_var = tk.StringVar(value=categoria['descricao'] if editing else '')
        nome_field, nome_entry = self.create_entry_field(content, 'Nome da categoria *', nome_var)
        nome_field.pack(fill='x', pady=(0, 14))
        descricao_field, _ = self.create_entry_field(content, 'Descrição', descricao_var)
        descricao_field.pack(fill='x')
        actions = tk.Frame(content, bg=self.colors['bg_primary'])
        actions.pack(fill='x', pady=(24, 0))
        self.create_button(actions, 'Cancelar', dialog.destroy, self.colors['bg_secondary'], self.colors['text_secondary'], ('Segoe UI', 10), 16, 9).pack(side='right')
        self.create_button(actions, 'Salvar', lambda: self.save_category(dialog, nome_var.get(), descricao_var.get(), categoria['id'] if editing else None), self.colors['accent'], self.colors['text_primary'], ('Segoe UI', 10, 'bold'), 18, 9).pack(side='right', padx=(0, 10))
        dialog.bind('<Return>', lambda event: self.save_category(dialog, nome_var.get(), descricao_var.get(), categoria['id'] if editing else None))
        dialog.bind('<Escape>', lambda event: dialog.destroy())
        dialog.after(100, nome_entry.focus_set)

    def create_entry_field(self, parent, label_text, variable):
        field = tk.Frame(parent, bg=self.colors['bg_primary'])
        tk.Label(field, text=label_text, font=('Segoe UI', 10), fg=self.colors['text_secondary'], bg=self.colors['bg_primary']).pack(anchor='w', pady=(0, 6))
        entry = tk.Entry(field, textvariable=variable, font=('Segoe UI', 11), fg=self.colors['text_primary'], bg=self.colors['bg_secondary'], insertbackground=self.colors['text_primary'], relief='flat', borderwidth=0)
        entry.pack(fill='x', ipady=10)
        return field, entry

    def save_category(self, dialog, nome, descricao, categoria_id=None):
        if not nome.strip():
            messagebox.showwarning('Campo obrigatório', 'Informe o nome da categoria.', parent=dialog)
            return
        if categoria_id is None:
            create_categoria(nome, descricao)
        else:
            update_categoria(categoria_id, nome, descricao)
        dialog.destroy()
        self.load_categories(self.get_current_search())

    def delete_category(self):
        if not self.selected_category:
            return
        categoria = get_categoria(self.selected_category)
        if not categoria:
            self.load_categories(self.get_current_search())
            return
        confirmed = messagebox.askyesno('Excluir categoria', f'Tem certeza que deseja excluir "{categoria["nome"]}"?\n\nEssa ação não poderá ser desfeita.', icon='warning', parent=self.winfo_toplevel())
        if confirmed:
            delete_categoria(categoria['id'])
            self.load_categories(self.get_current_search())
