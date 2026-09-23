import tkinter as tk
from tkinter import ttk, messagebox

from database import (
    get_categoria,
    get_valores_empresa_categoria,
    list_campos_por_categoria,
    list_categorias,
    list_empresas,
    save_valores_empresa,
)


class CadastrosView(tk.Frame):
    """Tela para preencher campos organizados por empresa e categoria."""

    def __init__(self, parent, colors, on_back):
        super().__init__(parent)
        self.colors = colors
        self.on_back = on_back
        self.selected_company_id = None
        self.selected_category_id = None
        self.field_entries = {}
        self.category_buttons = {}
        self.configure(bg=colors['bg_primary'])
        self.configure_combo_style()
        self.create_widgets()
        self.refresh_sidebar()
        self.show_welcome()

    def configure_combo_style(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure(
            'Cadastros.TCombobox',
            fieldbackground=self.colors['bg_secondary'],
            background=self.colors['bg_secondary'],
            foreground=self.colors['text_primary'],
            arrowcolor=self.colors['text_primary'],
            borderwidth=0,
            padding=8
        )
        style.map(
            'Cadastros.TCombobox',
            fieldbackground=[('readonly', self.colors['bg_secondary'])],
            selectbackground=[('readonly', self.colors['bg_secondary'])],
            selectforeground=[('readonly', self.colors['text_primary'])]
        )

    def create_widgets(self):
        self.columnconfigure(0, weight=0)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)

        self.sidebar = tk.Frame(self, bg=self.colors['bg_secondary'], width=290)
        self.sidebar.grid(row=0, column=0, sticky='nsew')
        self.sidebar.grid_propagate(False)

        self.content = tk.Frame(self, bg=self.colors['bg_primary'])
        self.content.grid(row=0, column=1, sticky='nsew')

        self.create_sidebar()

    def create_sidebar(self):
        header = tk.Frame(self.sidebar, bg=self.colors['bg_secondary'])
        header.pack(fill='x', padx=20, pady=(24, 18))

        back_button = tk.Button(
            header, text='← Voltar', command=self.on_back,
            font=('Segoe UI', 10), fg=self.colors['text_secondary'],
            bg=self.colors['bg_tertiary'], activebackground=self.colors['accent'],
            activeforeground=self.colors['text_primary'], borderwidth=0,
            padx=14, pady=8, cursor='hand2'
        )
        back_button.pack(anchor='w', pady=(0, 24))

        tk.Label(
            header, text='📋 Cadastros', font=('Segoe UI', 20, 'bold'),
            fg=self.colors['text_primary'], bg=self.colors['bg_secondary']
        ).pack(anchor='w')
        tk.Label(
            header, text='Preencha os dados da empresa', font=('Segoe UI', 9),
            fg=self.colors['text_secondary'], bg=self.colors['bg_secondary']
        ).pack(anchor='w', pady=(4, 0))

        separator = tk.Frame(self.sidebar, bg=self.colors['border'], height=1)
        separator.pack(fill='x', padx=20, pady=(0, 18))

        company_frame = tk.Frame(self.sidebar, bg=self.colors['bg_secondary'])
        company_frame.pack(fill='x', padx=20)
        tk.Label(
            company_frame, text='EMPRESA', font=('Segoe UI', 9, 'bold'),
            fg=self.colors['text_secondary'], bg=self.colors['bg_secondary']
        ).pack(anchor='w', pady=(0, 7))

        self.company_var = tk.StringVar()
        self.company_combo = ttk.Combobox(
            company_frame, textvariable=self.company_var, state='readonly',
            style='Cadastros.TCombobox', font=('Segoe UI', 10)
        )
        self.company_combo.pack(fill='x')
        self.company_combo.bind('<<ComboboxSelected>>', self.on_company_selected)

        tk.Label(
            self.sidebar, text='CATEGORIAS', font=('Segoe UI', 9, 'bold'),
            fg=self.colors['text_secondary'], bg=self.colors['bg_secondary']
        ).pack(anchor='w', padx=20, pady=(28, 10))

        self.categories_frame = tk.Frame(self.sidebar, bg=self.colors['bg_secondary'])
        self.categories_frame.pack(fill='both', expand=True, padx=12, pady=(0, 16))

    def refresh_sidebar(self):
        empresas = list_empresas()
        self.company_map = {
            f"{empresa['nome']} ({empresa['localizacao'] or 'Sem localização'})": empresa['id']
            for empresa in empresas
        }
        self.company_combo['values'] = list(self.company_map.keys())

        if not empresas:
            self.company_var.set('Nenhuma empresa cadastrada')
            self.company_combo.configure(state='disabled')
        else:
            self.company_combo.configure(state='readonly')
            if self.company_var.get() not in self.company_map:
                self.company_var.set('Selecione uma empresa')

        self.render_categories()

    def render_categories(self):
        for widget in self.categories_frame.winfo_children():
            widget.destroy()
        self.category_buttons = {}

        categorias = list_categorias()
        if not categorias:
            tk.Label(
                self.categories_frame, text='Nenhuma categoria cadastrada.',
                font=('Segoe UI', 9), fg=self.colors['text_secondary'],
                bg=self.colors['bg_secondary'], wraplength=230, justify='left'
            ).pack(anchor='w', padx=8, pady=8)
            return

        for categoria in categorias:
            button = tk.Button(
                self.categories_frame, text=categoria['nome'],
                command=lambda cat_id=categoria['id']: self.select_category(cat_id),
                font=('Segoe UI', 10), fg=self.colors['text_primary'],
                bg=self.colors['bg_secondary'], activebackground=self.colors['bg_tertiary'],
                activeforeground=self.colors['text_primary'], borderwidth=0,
                anchor='w', padx=14, pady=11, cursor='hand2'
            )
            button.pack(fill='x', pady=2)
            button.bind('<Enter>', lambda event: self.on_category_hover(event, True))
            button.bind('<Leave>', lambda event: self.on_category_hover(event, False))
            self.category_buttons[categoria['id']] = button

    def on_category_hover(self, event, entering):
        category_id = next((key for key, value in self.category_buttons.items() if value == event.widget), None)
        if category_id != self.selected_category_id:
            event.widget.configure(bg=self.colors['bg_tertiary'] if entering else self.colors['bg_secondary'])

    def on_company_selected(self, event=None):
        self.selected_company_id = self.company_map.get(self.company_var.get())
        self.selected_category_id = None
        self.update_category_selection()
        self.show_choose_category()

    def select_category(self, categoria_id):
        if not self.selected_company_id:
            messagebox.showwarning(
                'Selecione uma empresa',
                'Selecione uma empresa antes de escolher uma categoria.',
                parent=self.winfo_toplevel()
            )
            return
        self.selected_category_id = categoria_id
        self.update_category_selection()
        self.show_category_fields()

    def update_category_selection(self):
        for categoria_id, button in self.category_buttons.items():
            color = self.colors['accent'] if categoria_id == self.selected_category_id else self.colors['bg_secondary']
            button.configure(bg=color)

    def clear_content(self):
        for widget in self.content.winfo_children():
            widget.destroy()
        self.field_entries = {}

    def create_scrollable_content(self):
        wrapper = tk.Frame(self.content, bg=self.colors['bg_primary'])
        wrapper.pack(fill='both', expand=True)

        canvas = tk.Canvas(
            wrapper, bg=self.colors['bg_primary'],
            highlightthickness=0, borderwidth=0
        )
        scrollbar = ttk.Scrollbar(wrapper, orient='vertical', command=canvas.yview)
        scroll_frame = tk.Frame(canvas, bg=self.colors['bg_primary'])

        scroll_frame.bind(
            '<Configure>',
            lambda event: canvas.configure(scrollregion=canvas.bbox('all'))
        )
        canvas_window = canvas.create_window((0, 0), window=scroll_frame, anchor='nw')
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.bind(
            '<Configure>',
            lambda event: canvas.itemconfigure(canvas_window, width=event.width)
        )

        canvas.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

        self.bind_scroll_events(scroll_frame, canvas)
        return scroll_frame, canvas

    def bind_scroll_events(self, widget, canvas):
        widget.bind('<Enter>', lambda event: canvas.bind_all('<MouseWheel>', lambda mouse_event: canvas.yview_scroll(int(-mouse_event.delta / 120), 'units')))
        widget.bind('<Leave>', lambda event: canvas.unbind_all('<MouseWheel>'))

    def show_welcome(self):
        self.clear_content()
        frame = tk.Frame(self.content, bg=self.colors['bg_primary'])
        frame.place(relx=0.5, rely=0.5, anchor='center')
        tk.Label(
            frame, text='Cadastros de empresas', font=('Segoe UI', 24, 'bold'),
            fg=self.colors['text_primary'], bg=self.colors['bg_primary']
        ).pack(pady=(0, 8))
        tk.Label(
            frame, text='Selecione uma empresa no menu lateral para começar.',
            font=('Segoe UI', 11), fg=self.colors['text_secondary'],
            bg=self.colors['bg_primary']
        ).pack()

    def show_choose_category(self):
        self.clear_content()
        frame = tk.Frame(self.content, bg=self.colors['bg_primary'])
        frame.place(relx=0.5, rely=0.5, anchor='center')
        tk.Label(
            frame, text='Escolha uma categoria', font=('Segoe UI', 22, 'bold'),
            fg=self.colors['text_primary'], bg=self.colors['bg_primary']
        ).pack(pady=(0, 8))
        tk.Label(
            frame, text='Selecione uma categoria no menu lateral para preencher os campos.',
            font=('Segoe UI', 11), fg=self.colors['text_secondary'],
            bg=self.colors['bg_primary']
        ).pack()

    def show_category_fields(self):
        self.clear_content()
        categoria = get_categoria(self.selected_category_id)
        campos = list_campos_por_categoria(self.selected_category_id)
        container, canvas = self.create_scrollable_content()
        container.configure(padx=42, pady=34)

        tk.Label(
            container, text=categoria['nome'], font=('Segoe UI', 24, 'bold'),
            fg=self.colors['text_primary'], bg=self.colors['bg_primary']
        ).pack(anchor='w')

        if categoria['descricao']:
            tk.Label(
                container, text=categoria['descricao'], font=('Segoe UI', 10),
                fg=self.colors['text_secondary'], bg=self.colors['bg_primary'],
                wraplength=650, justify='left'
            ).pack(anchor='w', pady=(5, 26))
        else:
            tk.Label(
                container, text='Preencha as informações desta categoria.', font=('Segoe UI', 10),
                fg=self.colors['text_secondary'], bg=self.colors['bg_primary']
            ).pack(anchor='w', pady=(5, 26))

        if not campos:
            tk.Label(
                container, text='Esta categoria ainda não possui campos cadastrados.',
                font=('Segoe UI', 11), fg=self.colors['text_secondary'],
                bg=self.colors['bg_primary']
            ).pack(anchor='w', pady=20)
            return

        values = get_valores_empresa_categoria(self.selected_company_id, self.selected_category_id)
        fields_frame = tk.Frame(container, bg=self.colors['bg_primary'])
        fields_frame.pack(fill='x')

        for campo in campos:
            field = tk.Frame(fields_frame, bg=self.colors['bg_primary'])
            field.pack(fill='x', pady=(0, 18))
            tk.Label(
                field, text=campo['nome'], font=('Segoe UI', 10, 'bold'),
                fg=self.colors['text_primary'], bg=self.colors['bg_primary']
            ).pack(anchor='w', pady=(0, 7))
            entry = tk.Entry(
                field, font=('Segoe UI', 11), fg=self.colors['text_primary'],
                bg=self.colors['bg_secondary'], insertbackground=self.colors['text_primary'],
                relief='flat', borderwidth=0
            )
            entry.pack(fill='x', ipady=10)
            entry.insert(0, values.get(campo['id'], ''))
            self.field_entries[campo['id']] = entry
            self.bind_scroll_events(entry, canvas)

        actions = tk.Frame(container, bg=self.colors['bg_primary'])
        actions.pack(fill='x', pady=(12, 20))
        save_button = tk.Button(
            actions, text='Salvar informações', command=self.save_current_fields,
            font=('Segoe UI', 10, 'bold'), fg=self.colors['text_primary'],
            bg=self.colors['accent'], activebackground=self.colors['bg_tertiary'],
            activeforeground=self.colors['text_primary'], borderwidth=0,
            padx=22, pady=11, cursor='hand2'
        )
        save_button.pack(anchor='e')
        save_button.bind('<Enter>', lambda event: event.widget.configure(bg=self.colors['bg_tertiary']))
        save_button.bind('<Leave>', lambda event: event.widget.configure(bg=self.colors['accent']))
        self.bind_scroll_events(save_button, canvas)

    def save_current_fields(self):
        if not self.selected_company_id or not self.field_entries:
            return
        valores = {campo_id: entry.get() for campo_id, entry in self.field_entries.items()}
        save_valores_empresa(self.selected_company_id, valores)
        messagebox.showinfo(
            'Informações salvas',
            'Os dados da categoria foram salvos com sucesso.',
            parent=self.winfo_toplevel()
        )
