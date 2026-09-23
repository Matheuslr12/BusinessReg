import tkinter as tk
from tkinter import ttk, messagebox

from database import create_campo, delete_campo, get_campo, list_campos, list_categorias, move_campo, update_campo


class CamposView(tk.Frame):
    """Tela para gerenciar campos organizados por categorias recolhíveis."""

    def __init__(self, parent, colors, on_back):
        super().__init__(parent)
        self.colors = colors
        self.on_back = on_back
        self.configure(bg=colors['bg_primary'])
        self.selected_field = None
        self.field_buttons = {}
        self.field_data = {}
        self.expanded_categories = set()
        self.configure_combo_style()
        self.create_widgets()
        self.load_fields()

    def refresh_view(self):
        self.load_fields(self.get_current_search(), expand_results=bool(self.get_current_search()))

    def configure_combo_style(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('Campos.TCombobox', fieldbackground=self.colors['bg_secondary'], background=self.colors['bg_secondary'], foreground=self.colors['text_primary'], arrowcolor=self.colors['text_primary'], borderwidth=0, padding=8)
        style.map('Campos.TCombobox', fieldbackground=[('readonly', self.colors['bg_secondary'])], selectbackground=[('readonly', self.colors['bg_secondary'])], selectforeground=[('readonly', self.colors['text_primary'])])

    def create_widgets(self):
        container = tk.Frame(self, bg=self.colors['bg_primary'])
        container.pack(fill='both', expand=True, padx=40, pady=30)
        self.create_header(container)
        self.create_toolbar(container)
        self.create_groups_area(container)
        self.create_actions(container)

    def create_header(self, parent):
        header = tk.Frame(parent, bg=self.colors['bg_primary'])
        header.pack(fill='x')
        self.create_button(header, '← Voltar', self.on_back, self.colors['bg_secondary'], self.colors['text_secondary'], ('Segoe UI', 10), 15, 8).pack(anchor='w')
        tk.Label(header, text='🏷️ Campos', font=('Segoe UI', 24, 'bold'), fg=self.colors['text_primary'], bg=self.colors['bg_primary']).pack(anchor='w', pady=(28, 4))
        tk.Label(header, text='Organize os campos por categoria e defina a ordem de preenchimento.', font=('Segoe UI', 10), fg=self.colors['text_secondary'], bg=self.colors['bg_primary']).pack(anchor='w', pady=(0, 22))

    def create_toolbar(self, parent):
        toolbar = tk.Frame(parent, bg=self.colors['bg_primary'])
        toolbar.pack(fill='x', pady=(0, 16))
        search_frame = tk.Frame(toolbar, bg=self.colors['bg_secondary'])
        search_frame.pack(side='left', fill='x', expand=True, padx=(0, 12))
        tk.Label(search_frame, text='⌕', font=('Segoe UI', 14), fg=self.colors['text_secondary'], bg=self.colors['bg_secondary']).pack(side='left', padx=(12, 4))
        self.search_var = tk.StringVar()
        self.search_entry = tk.Entry(search_frame, textvariable=self.search_var, font=('Segoe UI', 10), fg=self.colors['text_secondary'], bg=self.colors['bg_secondary'], insertbackground=self.colors['text_primary'], relief='flat', borderwidth=0)
        self.search_entry.pack(side='left', fill='x', expand=True, padx=(0, 12), pady=10)
        self.search_entry.insert(0, 'Buscar campo...')
        self.search_entry.bind('<FocusIn>', self.clear_search_placeholder)
        self.search_entry.bind('<FocusOut>', self.restore_search_placeholder)
        self.search_entry.bind('<KeyRelease>', self.filter_fields)
        self.create_button(toolbar, '+ Adicionar Campo', self.open_add_dialog, self.colors['accent'], self.colors['text_primary'], ('Segoe UI', 10, 'bold'), 18, 10).pack(side='right')

    def create_groups_area(self, parent):
        groups_container = tk.Frame(parent, bg=self.colors['bg_secondary'], highlightbackground=self.colors['border'], highlightthickness=1)
        groups_container.pack(fill='both', expand=True)
        self.groups_canvas = tk.Canvas(groups_container, bg=self.colors['bg_secondary'], highlightthickness=0, borderwidth=0)
        scrollbar = ttk.Scrollbar(groups_container, orient='vertical', command=self.groups_canvas.yview)
        self.groups_frame = tk.Frame(self.groups_canvas, bg=self.colors['bg_secondary'])
        self.groups_frame.bind('<Configure>', lambda event: self.groups_canvas.configure(scrollregion=self.groups_canvas.bbox('all')))
        self.canvas_window = self.groups_canvas.create_window((0, 0), window=self.groups_frame, anchor='nw')
        self.groups_canvas.configure(yscrollcommand=scrollbar.set)
        self.groups_canvas.bind('<Configure>', lambda event: self.groups_canvas.itemconfigure(self.canvas_window, width=event.width))
        self.groups_canvas.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

    def create_actions(self, parent):
        actions = tk.Frame(parent, bg=self.colors['bg_primary'])
        actions.pack(fill='x', pady=(16, 0))
        self.btn_up = self.create_button(actions, '↑ Mover para cima', self.move_selected_up, self.colors['bg_tertiary'], self.colors['text_primary'], ('Segoe UI', 10, 'bold'), 16, 10, state='disabled')
        self.btn_up.pack(side='left')
        self.btn_down = self.create_button(actions, '↓ Mover para baixo', self.move_selected_down, self.colors['bg_tertiary'], self.colors['text_primary'], ('Segoe UI', 10, 'bold'), 16, 10, state='disabled')
        self.btn_down.pack(side='left', padx=(10, 0))
        self.btn_edit = self.create_button(actions, '✎ Editar', self.edit_field, self.colors['bg_tertiary'], self.colors['text_primary'], ('Segoe UI', 10, 'bold'), 20, 10, state='disabled')
        self.btn_edit.pack(side='left', padx=(18, 0))
        self.btn_delete = self.create_button(actions, '🗑 Excluir', self.delete_field, self.colors['bg_secondary'], self.colors['text_secondary'], ('Segoe UI', 10, 'bold'), 20, 10, state='disabled')
        self.btn_delete.pack(side='left', padx=(10, 0))

    def create_button(self, parent, text, command, background, foreground, font, padx, pady, state='normal'):
        button = tk.Button(parent, text=text, command=command, font=font, fg=foreground, bg=background, activebackground=self.colors['bg_tertiary'], activeforeground=self.colors['text_primary'], disabledforeground='#666b7c', borderwidth=0, padx=padx, pady=pady, cursor='hand2' if state == 'normal' else 'arrow', state=state)
        if state == 'normal':
            button.bind('<Enter>', lambda e: e.widget.configure(bg=self.colors['accent']))
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
        search = self.get_current_search()
        self.load_fields(search, expand_results=bool(search))

    def load_fields(self, search='', expand_results=False, keep_selection=False):
        previous_selection = self.selected_field if keep_selection else None
        for widget in self.groups_frame.winfo_children():
            widget.destroy()
        self.field_buttons = {}
        self.field_data = {}
        self.selected_field = None
        self.disable_actions()
        categorias = list_categorias()
        campos = list_campos(search)
        fields_by_category = {}
        for campo in campos:
            fields_by_category.setdefault(campo['categoria_id'], []).append(campo)
            self.field_data[campo['id']] = campo
        if not categorias:
            self.show_empty_message('Nenhuma categoria cadastrada. Crie uma categoria antes de adicionar campos.')
            return
        has_visible_content = False
        for categoria in categorias:
            category_fields = fields_by_category.get(categoria['id'], [])
            if search and not category_fields:
                continue
            has_visible_content = True
            self.create_category_group(categoria, category_fields, expand_results)
        if not has_visible_content:
            self.show_empty_message('Nenhum campo encontrado para a busca informada.')
        elif previous_selection in self.field_buttons:
            self.select_field(previous_selection)

    def show_empty_message(self, text):
        tk.Label(self.groups_frame, text=text, font=('Segoe UI', 11), fg=self.colors['text_secondary'], bg=self.colors['bg_secondary'], justify='center', wraplength=500).pack(pady=50)

    def create_category_group(self, categoria, campos, expand_results):
        category_id = categoria['id']
        group = tk.Frame(self.groups_frame, bg=self.colors['bg_secondary'])
        group.pack(fill='x', padx=16, pady=(14, 0))
        expanded = expand_results or category_id in self.expanded_categories
        arrow = '⌄' if expanded else '›'
        count_text = f"{len(campos)} campo" + ('' if len(campos) == 1 else 's')
        header = tk.Button(group, text=f'{arrow}  {categoria["nome"]}   ·   {count_text}', command=lambda cat_id=category_id: self.toggle_category(cat_id), font=('Segoe UI', 11, 'bold'), fg=self.colors['text_primary'], bg=self.colors['bg_tertiary'], activebackground=self.colors['accent'], activeforeground=self.colors['text_primary'], borderwidth=0, anchor='w', padx=16, pady=12, cursor='hand2')
        header.pack(fill='x')
        header.bind('<Enter>', lambda event: event.widget.configure(bg=self.colors['accent']))
        header.bind('<Leave>', lambda event: event.widget.configure(bg=self.colors['bg_tertiary']))
        fields_frame = tk.Frame(group, bg=self.colors['bg_secondary'])
        if campos:
            for index, campo in enumerate(campos, start=1):
                self.create_field_row(fields_frame, campo, index)
        else:
            tk.Label(fields_frame, text='Nenhum campo nesta categoria.', font=('Segoe UI', 10), fg=self.colors['text_secondary'], bg=self.colors['bg_secondary']).pack(anchor='w', padx=20, pady=14)
        if expanded:
            fields_frame.pack(fill='x')

    def create_field_row(self, parent, campo, position):
        row = tk.Button(parent, text=f'     {position}.  {campo["nome"]}', command=lambda field_id=campo['id']: self.select_field(field_id), font=('Segoe UI', 10), fg=self.colors['text_primary'], bg=self.colors['bg_secondary'], activebackground=self.colors['bg_tertiary'], activeforeground=self.colors['text_primary'], borderwidth=0, anchor='w', padx=16, pady=10, cursor='hand2')
        row.pack(fill='x', padx=1)
        row.bind('<Enter>', lambda event: self.on_field_hover(event, True))
        row.bind('<Leave>', lambda event: self.on_field_hover(event, False))
        self.field_buttons[campo['id']] = row

    def on_field_hover(self, event, entering):
        if event.widget != self.field_buttons.get(self.selected_field):
            event.widget.configure(bg=self.colors['bg_tertiary'] if entering else self.colors['bg_secondary'])

    def toggle_category(self, category_id):
        if category_id in self.expanded_categories:
            self.expanded_categories.discard(category_id)
        else:
            self.expanded_categories.add(category_id)
        self.load_fields(self.get_current_search(), expand_results=bool(self.get_current_search()))

    def select_field(self, field_id):
        self.selected_field = field_id
        for current_id, button in self.field_buttons.items():
            button.configure(bg=self.colors['accent'] if current_id == field_id else self.colors['bg_secondary'])
        self.update_actions_state()

    def update_actions_state(self):
        if not self.selected_field:
            self.disable_actions()
            return
        campo = self.field_data.get(self.selected_field)
        same_category = sorted([item for item in self.field_data.values() if item['categoria_id'] == campo['categoria_id']], key=lambda item: (item['ordem'], item['id']))
        current_index = next(index for index, item in enumerate(same_category) if item['id'] == campo['id'])
        self.btn_up.configure(state='normal' if current_index > 0 else 'disabled')
        self.btn_down.configure(state='normal' if current_index < len(same_category) - 1 else 'disabled')
        self.btn_edit.configure(state='normal')
        self.btn_delete.configure(state='normal')

    def disable_actions(self):
        self.btn_up.configure(state='disabled')
        self.btn_down.configure(state='disabled')
        self.btn_edit.configure(state='disabled')
        self.btn_delete.configure(state='disabled')

    def move_selected_up(self):
        if self.selected_field and move_campo(self.selected_field, 'up'):
            self.load_fields(keep_selection=True)

    def move_selected_down(self):
        if self.selected_field and move_campo(self.selected_field, 'down'):
            self.load_fields(keep_selection=True)

    def open_add_dialog(self):
        categorias = list_categorias()
        if not categorias:
            messagebox.showwarning('Categoria necessária', 'Cadastre pelo menos uma categoria antes de adicionar campos.', parent=self.winfo_toplevel())
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
        tk.Label(content, text='Editar campo' if editing else 'Adicionar campo', font=('Segoe UI', 18, 'bold'), fg=self.colors['text_primary'], bg=self.colors['bg_primary']).pack(anchor='w', pady=(0, 24))
        category_map = {categoria['nome']: categoria['id'] for categoria in categorias}
        category_names = list(category_map.keys())
        current_category = next((nome for nome, categoria_id in category_map.items() if editing and categoria_id == campo['categoria_id']), category_names[0])
        nome_var = tk.StringVar(value=campo['nome'] if editing else '')
        categoria_var = tk.StringVar(value=current_category)
        nome_field, nome_entry = self.create_entry_field(content, 'Nome do campo *', nome_var)
        nome_field.pack(fill='x', pady=(0, 16))
        self.create_combo_field(content, 'Categoria *', categoria_var, category_names).pack(fill='x')
        actions = tk.Frame(content, bg=self.colors['bg_primary'])
        actions.pack(fill='x', pady=(28, 0))
        self.create_button(actions, 'Cancelar', dialog.destroy, self.colors['bg_secondary'], self.colors['text_secondary'], ('Segoe UI', 10), 16, 9).pack(side='right')
        self.create_button(actions, 'Salvar', lambda: self.save_field(dialog, nome_var.get(), category_map.get(categoria_var.get()), campo['id'] if editing else None), self.colors['accent'], self.colors['text_primary'], ('Segoe UI', 10, 'bold'), 18, 9).pack(side='right', padx=(0, 10))
        dialog.bind('<Return>', lambda event: self.save_field(dialog, nome_var.get(), category_map.get(categoria_var.get()), campo['id'] if editing else None))
        dialog.bind('<Escape>', lambda event: dialog.destroy())
        dialog.after(100, nome_entry.focus_set)

    def create_entry_field(self, parent, label_text, variable):
        field = tk.Frame(parent, bg=self.colors['bg_primary'])
        tk.Label(field, text=label_text, font=('Segoe UI', 10), fg=self.colors['text_secondary'], bg=self.colors['bg_primary']).pack(anchor='w', pady=(0, 6))
        entry = tk.Entry(field, textvariable=variable, font=('Segoe UI', 11), fg=self.colors['text_primary'], bg=self.colors['bg_secondary'], insertbackground=self.colors['text_primary'], relief='flat', borderwidth=0)
        entry.pack(fill='x', ipady=10)
        return field, entry

    def create_combo_field(self, parent, label_text, variable, values):
        field = tk.Frame(parent, bg=self.colors['bg_primary'])
        tk.Label(field, text=label_text, font=('Segoe UI', 10), fg=self.colors['text_secondary'], bg=self.colors['bg_primary']).pack(anchor='w', pady=(0, 6))
        combo = ttk.Combobox(field, textvariable=variable, values=values, state='readonly', style='Campos.TCombobox', font=('Segoe UI', 10))
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
        self.load_fields()

    def delete_field(self):
        if not self.selected_field:
            return
        campo = get_campo(int(self.selected_field))
        if not campo:
            self.load_fields()
            return
        confirmed = messagebox.askyesno('Excluir campo', f'Tem certeza que deseja excluir o campo "{campo["nome"]}"?\n\nEssa ação não poderá ser desfeita.', icon='warning', parent=self.winfo_toplevel())
        if confirmed:
            delete_campo(campo['id'])
            self.load_fields()
