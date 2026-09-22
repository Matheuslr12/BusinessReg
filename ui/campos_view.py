import tkinter as tk
from tkinter import ttk, messagebox

from database import (
    create_campo,
    delete_campo,
    get_campo,
    list_campos,
    list_categorias,
    update_campo,
)


class CamposView(tk.Frame):
    """Tela para gerenciar os campos usados nos cadastros."""

    def __init__(self, parent, colors, on_back):
        super().__init__(parent)
        self.colors = colors
        self.on_back = on_back
        self.configure(bg=colors['bg_primary'])
        self.selected_field = None
        self.configure_treeview_style()
        self.create_widgets()
        self.load_fields()

    def configure_treeview_style(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure(
            'Campos.Treeview',
            background=self.colors['bg_secondary'],
            fieldbackground=self.colors['bg_secondary'],
            foreground=self.colors['text_primary'],
            rowheight=38,
            borderwidth=0,
            font=('Segoe UI', 10)
        )
        style.configure(
            'Campos.Treeview.Heading',
            background=self.colors['bg_tertiary'],
            foreground=self.colors['text_primary'],
            relief='flat',
            font=('Segoe UI', 10, 'bold')
        )
        style.map(
            'Campos.Treeview',
            background=[('selected', self.colors['accent'])],
            foreground=[('selected', self.colors['text_primary'])]
        )
        style.configure(
            'Campos.TCombobox',
            fieldbackground=self.colors['bg_secondary'],
            background=self.colors['bg_secondary'],
            foreground=self.colors['text_primary'],
            arrowcolor=self.colors['text_primary'],
            borderwidth=0,
            padding=8
        )
        style.map(
            'Campos.TCombobox',
            fieldbackground=[('readonly', self.colors['bg_secondary'])],
            selectbackground=[('readonly', self.colors['bg_secondary'])],
            selectforeground=[('readonly', self.colors['text_primary'])]
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
        self.create_button(
            header, '← Voltar', self.on_back,
            self.colors['bg_secondary'], self.colors['text_secondary'],
            ('Segoe UI', 10), 15, 8
        ).pack(anchor='w')
        tk.Label(
            header, text='🏷️ Campos', font=('Segoe UI', 24, 'bold'),
            fg=self.colors['text_primary'], bg=self.colors['bg_primary']
        ).pack(anchor='w', pady=(28, 4))
        tk.Label(
            header,
            text='Crie os campos que serão exibidos nos cadastros, vinculados a uma categoria.',
            font=('Segoe UI', 10), fg=self.colors['text_secondary'],
            bg=self.colors['bg_primary']
        ).pack(anchor='w', pady=(0, 22))

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
        self.search_entry.insert(0, 'Buscar campo...')
        self.search_entry.bind('<FocusIn>', self.clear_search_placeholder)
        self.search_entry.bind('<FocusOut>', self.restore_search_placeholder)
        self.search_entry.bind('<KeyRelease>', self.filter_fields)
        self.create_button(
            toolbar, '+ Adicionar Campo', self.open_add_dialog,
            self.colors['accent'], self.colors['text_primary'],
            ('Segoe UI', 10, 'bold'), 18, 10
        ).pack(side='right')

    def create_table(self, parent):
        table_frame = tk.Frame(
            parent, bg=self.colors['bg_secondary'],
            highlightbackground=self.colors['border'], highlightthickness=1
        )
        table_frame.pack(fill='both', expand=True)
        self.tree = ttk.Treeview(
            table_frame, columns=('id', 'nome', 'categoria'),
            show='headings', style='Campos.Treeview', selectmode='browse'
        )
        self.tree.heading('id', text='ID')
        self.tree.heading('nome', text='NOME DO CAMPO')
        self.tree.heading('categoria', text='CATEGORIA')
        self.tree.column('id', width=80, minwidth=60, anchor='center', stretch=False)
        self.tree.column('nome', width=420, minwidth=200, anchor='w')
        self.tree.column('categoria', width=380, minwidth=180, anchor='w')
        scrollbar = ttk.Scrollbar(table_frame, orient='vertical', command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side='left', fill='both', expand=True, padx=(1, 0), pady=1)
        scrollbar.pack(side='right', fill='y', padx=(0, 1), pady=1)
        self.tree.bind('<<TreeviewSelect>>', self.on_select_field)
        self.empty_label = tk.Label(
            table_frame,
            text='Nenhum campo cadastrado\nClique em “+ Adicionar Campo” para começar.',
            font=('Segoe UI', 11), fg=self.colors['text_secondary'],
            bg=self.colors['bg_secondary'], justify='center'
        )

    def create_actions(self, parent):
        actions = tk.Frame(parent, bg=self.colors['bg_primary'])
        actions.pack(fill='x', pady=(16, 0))
        self.btn_edit = self.create_button(
            actions, '✎ Editar', self.edit_field,
            self.colors['bg_tertiary'], self.colors['text_primary'],
            ('Segoe UI', 10, 'bold'), 20, 10, state='disabled'
        )
        self.btn_edit.pack(side='left')
        self.btn_delete = self.create_button(
            actions, '🗑 Excluir', self.delete_field,
            self.colors['bg_secondary'], self.colors['text_secondary'],
            ('Segoe UI', 10, 'bold'), 20, 10, state='disabled'
        )
        self.btn_delete.pack(side='left', padx=(10, 0))

    def create_button(self, parent, text, command, background, foreground, font, padx, pady, state='normal'):
        button = tk.Button(
            parent, text=text, command=command, font=font, fg=foreground, bg=background,
            activebackground=self.colors['bg_tertiary'], activeforeground=self.colors['text_primary'],
            disabledforeground='#666b7c', borderwidth=0, padx=padx, pady=pady,
            cursor='hand2' if state == 'normal' else 'arrow', state=state
        )
        if state == 'normal':
            button.bind('<Enter>', lambda e: e.widget.configure(bg=self.colors['bg_tertiary']))
            button.bind('<Leave>', lambda e: e.widget.configure(bg=background))
        return button

    def clear_search_placeholder(self, event):
        if self.search_var.get() == 'Buscar campo...':
            self.search_var.set('')
            self.search_entry.configure(fg=self.colors['text_primary'])

    def restore_search_placeholder(self, event):
        if not self.search_var.get().strip():
            self.search_var.set('Buscar campo...')
            self.search_entry.configure(fg=self.colors['text_secondary'])

    def get_current_search(self):
        search = self.search_var.get().strip()
        return '' if search == 'Buscar campo...' else search

    def filter_fields(self, event=None):
        self.load_fields(self.get_current_search())

    def load_fields(self, search=''):
        for item in self.tree.get_children():
            self.tree.delete(item)
        campos = list_campos(search)
        for campo in campos:
            self.tree.insert(
                '', 'end', iid=str(campo['id']),
                values=(campo['id'], campo['nome'], campo['categoria_nome'])
            )
        if campos:
            self.empty_label.place_forget()
        else:
            self.empty_label.place(relx=0.5, rely=0.5, anchor='center')
        self.selected_field = None
        self.btn_edit.configure(state='disabled')
        self.btn_delete.configure(state='disabled')

    def on_select_field(self, event=None):
        selection = self.tree.selection()
        self.selected_field = selection[0] if selection else None
        state = 'normal' if self.selected_field else 'disabled'
        self.btn_edit.configure(state=state)
        self.btn_delete.configure(state=state)

    def open_add_dialog(self):
        categorias = list_categorias()
        if not categorias:
            messagebox.showwarning(
                'Categoria necessária',
                'Cadastre pelo menos uma categoria antes de adicionar campos.',
                parent=self.winfo_toplevel()
            )
            return
        self.open_field_dialog(categorias=categorias)

    def edit_field(self):
        if not self.selected_field:
            return
        campo = get_campo(int(self.selected_field))
        categorias = list_categorias()
        if campo and categorias:
            self.open_field_dialog(campo=campo, categorias=categorias)

    def open_field_dialog(self, campo=None, categorias=None):
        editing = campo is not None
        dialog = tk.Toplevel(self)
        dialog.title('Editar Campo' if editing else 'Adicionar Campo')
        dialog.configure(bg=self.colors['bg_primary'])
        dialog.resizable(False, False)
        dialog.transient(self.winfo_toplevel())
        dialog.grab_set()

        width, height = 450, 370
        parent = self.winfo_toplevel()
        x = parent.winfo_x() + (parent.winfo_width() - width) // 2
        y = parent.winfo_y() + (parent.winfo_height() - height) // 2
        dialog.geometry(f'{width}x{height}+{x}+{y}')

        content = tk.Frame(dialog, bg=self.colors['bg_primary'])
        content.pack(fill='both', expand=True, padx=30, pady=28)
        tk.Label(
            content, text='Editar campo' if editing else 'Adicionar campo',
            font=('Segoe UI', 18, 'bold'), fg=self.colors['text_primary'],
            bg=self.colors['bg_primary']
        ).pack(anchor='w', pady=(0, 24))

        category_map = {categoria['nome']: categoria['id'] for categoria in categorias}
        category_names = list(category_map.keys())
        current_category = next(
            (nome for nome, categoria_id in category_map.items()
             if editing and categoria_id == campo['categoria_id']),
            category_names[0]
        )

        nome_var = tk.StringVar(value=campo['nome'] if editing else '')
        categoria_var = tk.StringVar(value=current_category)

        nome_field, nome_entry = self.create_entry_field(content, 'Nome do campo *', nome_var)
        nome_field.pack(fill='x', pady=(0, 16))
        categoria_field = self.create_combo_field(content, 'Categoria *', categoria_var, category_names)
        categoria_field.pack(fill='x')

        actions = tk.Frame(content, bg=self.colors['bg_primary'])
        actions.pack(fill='x', pady=(28, 0))
        self.create_button(
            actions, 'Cancelar', dialog.destroy,
            self.colors['bg_secondary'], self.colors['text_secondary'],
            ('Segoe UI', 10), 16, 9
        ).pack(side='right')
        self.create_button(
            actions, 'Salvar',
            lambda: self.save_field(
                dialog, nome_var.get(), category_map.get(categoria_var.get()),
                campo['id'] if editing else None
            ),
            self.colors['accent'], self.colors['text_primary'],
            ('Segoe UI', 10, 'bold'), 18, 9
        ).pack(side='right', padx=(0, 10))
        dialog.bind('<Return>', lambda event: self.save_field(
            dialog, nome_var.get(), category_map.get(categoria_var.get()),
            campo['id'] if editing else None
        ))
        dialog.bind('<Escape>', lambda event: dialog.destroy())
        dialog.after(100, nome_entry.focus_set)

    def create_entry_field(self, parent, label_text, variable):
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
        entry.pack(fill='x', ipady=10)
        return field, entry

    def create_combo_field(self, parent, label_text, variable, values):
        field = tk.Frame(parent, bg=self.colors['bg_primary'])
        tk.Label(
            field, text=label_text, font=('Segoe UI', 10),
            fg=self.colors['text_secondary'], bg=self.colors['bg_primary']
        ).pack(anchor='w', pady=(0, 6))
        combo = ttk.Combobox(
            field, textvariable=variable, values=values,
            state='readonly', style='Campos.TCombobox', font=('Segoe UI', 10)
        )
        combo.pack(fill='x')
        return field

    def save_field(self, dialog, nome, categoria_id, campo_id=None):
        if not nome.strip():
            messagebox.showwarning('Campo obrigatório', 'Informe o nome do campo.', parent=dialog)
            return
        if not categoria_id:
            messagebox.showwarning('Categoria obrigatória', 'Selecione uma categoria.', parent=dialog)
            return
        if campo_id is None:
            create_campo(categoria_id, nome)
        else:
            update_campo(campo_id, categoria_id, nome)
        dialog.destroy()
        self.load_fields(self.get_current_search())

    def delete_field(self):
        if not self.selected_field:
            return
        campo = get_campo(int(self.selected_field))
        if not campo:
            self.load_fields(self.get_current_search())
            return
        confirmed = messagebox.askyesno(
            'Excluir campo',
            f'Tem certeza que deseja excluir o campo "{campo["nome"]}"?\n\nEssa ação não poderá ser desfeita.',
            icon='warning', parent=self.winfo_toplevel()
        )
        if confirmed:
            delete_campo(campo['id'])
            self.load_fields(self.get_current_search())
