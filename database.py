import sqlite3
from datetime import datetime

DB_NAME = 'empresas.db'


def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS empresas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            localizacao TEXT,
            data_cadastro TEXT NOT NULL
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS categorias (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            descricao TEXT,
            data_cadastro TEXT NOT NULL
        )
    ''')

    conn.commit()
    conn.close()


def create_empresa(nome, localizacao=''):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        '''INSERT INTO empresas (nome, localizacao, data_cadastro)
           VALUES (?, ?, ?)''',
        (nome.strip(), localizacao.strip(), datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    )
    empresa_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return empresa_id


def get_empresa(empresa_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        'SELECT id, nome, localizacao, data_cadastro FROM empresas WHERE id = ?',
        (empresa_id,)
    )
    empresa = cursor.fetchone()
    conn.close()
    return empresa


def list_empresas(search=''):
    conn = get_connection()
    cursor = conn.cursor()
    if search.strip():
        termo = f'%{search.strip()}%'
        cursor.execute(
            '''SELECT id, nome, localizacao, data_cadastro FROM empresas
               WHERE nome LIKE ? OR localizacao LIKE ?
               ORDER BY nome COLLATE NOCASE''',
            (termo, termo)
        )
    else:
        cursor.execute(
            '''SELECT id, nome, localizacao, data_cadastro FROM empresas
               ORDER BY nome COLLATE NOCASE'''
        )
    empresas = cursor.fetchall()
    conn.close()
    return empresas


def update_empresa(empresa_id, nome, localizacao=''):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        '''UPDATE empresas SET nome = ?, localizacao = ? WHERE id = ?''',
        (nome.strip(), localizacao.strip(), empresa_id)
    )
    conn.commit()
    conn.close()


def delete_empresa(empresa_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM empresas WHERE id = ?', (empresa_id,))
    conn.commit()
    conn.close()


def create_categoria(nome, descricao=''):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        '''INSERT INTO categorias (nome, descricao, data_cadastro)
           VALUES (?, ?, ?)''',
        (nome.strip(), descricao.strip(), datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    )
    categoria_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return categoria_id


def get_categoria(categoria_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        'SELECT id, nome, descricao, data_cadastro FROM categorias WHERE id = ?',
        (categoria_id,)
    )
    categoria = cursor.fetchone()
    conn.close()
    return categoria


def list_categorias(search=''):
    conn = get_connection()
    cursor = conn.cursor()
    if search.strip():
        termo = f'%{search.strip()}%'
        cursor.execute(
            '''SELECT id, nome, descricao, data_cadastro FROM categorias
               WHERE nome LIKE ? OR descricao LIKE ?
               ORDER BY nome COLLATE NOCASE''',
            (termo, termo)
        )
    else:
        cursor.execute(
            '''SELECT id, nome, descricao, data_cadastro FROM categorias
               ORDER BY nome COLLATE NOCASE'''
        )
    categorias = cursor.fetchall()
    conn.close()
    return categorias


def update_categoria(categoria_id, nome, descricao=''):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        '''UPDATE categorias SET nome = ?, descricao = ? WHERE id = ?''',
        (nome.strip(), descricao.strip(), categoria_id)
    )
    conn.commit()
    conn.close()


def delete_categoria(categoria_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM categorias WHERE id = ?', (categoria_id,))
    conn.commit()
    conn.close()


if __name__ == '__main__':
    init_db()
    print('Banco de dados inicializado com sucesso!')
