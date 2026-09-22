import sqlite3
from datetime import datetime

DB_NAME = 'empresas.db'


def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    conn.execute('PRAGMA foreign_keys = ON')
    return conn


def column_exists(cursor, table_name, column_name):
    cursor.execute(f'PRAGMA table_info({table_name})')
    return any(column['name'] == column_name for column in cursor.fetchall())


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

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS campos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            categoria_id INTEGER NOT NULL,
            nome TEXT NOT NULL,
            tipo TEXT NOT NULL DEFAULT 'Texto',
            obrigatorio INTEGER NOT NULL DEFAULT 0,
            ordem INTEGER NOT NULL DEFAULT 0,
            data_cadastro TEXT NOT NULL,
            FOREIGN KEY (categoria_id) REFERENCES categorias(id)
        )
    ''')

    if not column_exists(cursor, 'campos', 'ordem'):
        cursor.execute('ALTER TABLE campos ADD COLUMN ordem INTEGER NOT NULL DEFAULT 0')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS valores_campos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            empresa_id INTEGER NOT NULL,
            campo_id INTEGER NOT NULL,
            valor TEXT,
            data_atualizacao TEXT NOT NULL,
            UNIQUE(empresa_id, campo_id),
            FOREIGN KEY (empresa_id) REFERENCES empresas(id) ON DELETE CASCADE,
            FOREIGN KEY (campo_id) REFERENCES campos(id) ON DELETE CASCADE
        )
    ''')

    cursor.execute('SELECT id, categoria_id FROM campos WHERE ordem = 0 ORDER BY categoria_id, id')
    campos_sem_ordem = cursor.fetchall()
    current_category = None
    position = 0
    for campo in campos_sem_ordem:
        if campo['categoria_id'] != current_category:
            current_category = campo['categoria_id']
            cursor.execute('SELECT COALESCE(MAX(ordem), 0) AS max_ordem FROM campos WHERE categoria_id = ?', (current_category,))
            position = cursor.fetchone()['max_ordem']
        position += 1
        cursor.execute('UPDATE campos SET ordem = ? WHERE id = ?', (position, campo['id']))

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
    cursor.execute('SELECT id, nome, localizacao, data_cadastro FROM empresas WHERE id = ?', (empresa_id,))
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
               WHERE nome LIKE ? OR localizacao LIKE ? ORDER BY nome COLLATE NOCASE''',
            (termo, termo)
        )
    else:
        cursor.execute('SELECT id, nome, localizacao, data_cadastro FROM empresas ORDER BY nome COLLATE NOCASE')
    empresas = cursor.fetchall()
    conn.close()
    return empresas


def update_empresa(empresa_id, nome, localizacao=''):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE empresas SET nome = ?, localizacao = ? WHERE id = ?', (nome.strip(), localizacao.strip(), empresa_id))
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
    cursor.execute('SELECT id, nome, descricao, data_cadastro FROM categorias WHERE id = ?', (categoria_id,))
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
               WHERE nome LIKE ? OR descricao LIKE ? ORDER BY nome COLLATE NOCASE''',
            (termo, termo)
        )
    else:
        cursor.execute('SELECT id, nome, descricao, data_cadastro FROM categorias ORDER BY nome COLLATE NOCASE')
    categorias = cursor.fetchall()
    conn.close()
    return categorias


def update_categoria(categoria_id, nome, descricao=''):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE categorias SET nome = ?, descricao = ? WHERE id = ?', (nome.strip(), descricao.strip(), categoria_id))
    conn.commit()
    conn.close()


def delete_categoria(categoria_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM categorias WHERE id = ?', (categoria_id,))
    conn.commit()
    conn.close()


def create_campo(categoria_id, nome):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT COALESCE(MAX(ordem), 0) + 1 AS proxima_ordem FROM campos WHERE categoria_id = ?', (categoria_id,))
    ordem = cursor.fetchone()['proxima_ordem']
    cursor.execute(
        '''INSERT INTO campos (categoria_id, nome, tipo, obrigatorio, ordem, data_cadastro)
           VALUES (?, ?, 'Texto', 0, ?, ?)''',
        (categoria_id, nome.strip(), ordem, datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    )
    campo_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return campo_id


def get_campo(campo_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT id, categoria_id, nome, ordem, data_cadastro FROM campos WHERE id = ?', (campo_id,))
    campo = cursor.fetchone()
    conn.close()
    return campo


def list_campos(search=''):
    conn = get_connection()
    cursor = conn.cursor()
    if search.strip():
        termo = f'%{search.strip()}%'
        cursor.execute(
            '''SELECT campos.id, campos.categoria_id, campos.nome, campos.ordem,
                      categorias.nome AS categoria_nome
               FROM campos
               INNER JOIN categorias ON categorias.id = campos.categoria_id
               WHERE campos.nome LIKE ? OR categorias.nome LIKE ?
               ORDER BY categorias.nome COLLATE NOCASE, campos.ordem, campos.id''',
            (termo, termo)
        )
    else:
        cursor.execute(
            '''SELECT campos.id, campos.categoria_id, campos.nome, campos.ordem,
                      categorias.nome AS categoria_nome
               FROM campos
               INNER JOIN categorias ON categorias.id = campos.categoria_id
               ORDER BY categorias.nome COLLATE NOCASE, campos.ordem, campos.id'''
        )
    campos = cursor.fetchall()
    conn.close()
    return campos


def list_campos_por_categoria(categoria_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        '''SELECT id, categoria_id, nome, ordem FROM campos
           WHERE categoria_id = ? ORDER BY ordem, id''',
        (categoria_id,)
    )
    campos = cursor.fetchall()
    conn.close()
    return campos


def update_campo(campo_id, categoria_id, nome):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT categoria_id FROM campos WHERE id = ?', (campo_id,))
    campo_atual = cursor.fetchone()
    if campo_atual and campo_atual['categoria_id'] != categoria_id:
        cursor.execute('SELECT COALESCE(MAX(ordem), 0) + 1 AS proxima_ordem FROM campos WHERE categoria_id = ?', (categoria_id,))
        nova_ordem = cursor.fetchone()['proxima_ordem']
        cursor.execute('UPDATE campos SET categoria_id = ?, nome = ?, ordem = ? WHERE id = ?', (categoria_id, nome.strip(), nova_ordem, campo_id))
    else:
        cursor.execute('UPDATE campos SET nome = ? WHERE id = ?', (nome.strip(), campo_id))
    conn.commit()
    conn.close()


def move_campo(campo_id, direction):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT id, categoria_id, ordem FROM campos WHERE id = ?', (campo_id,))
    campo = cursor.fetchone()
    if not campo:
        conn.close()
        return False

    operator = '<' if direction == 'up' else '>'
    order_by = 'DESC' if direction == 'up' else 'ASC'
    cursor.execute(
        f'''SELECT id, ordem FROM campos
            WHERE categoria_id = ? AND ordem {operator} ?
            ORDER BY ordem {order_by}, id {order_by}
            LIMIT 1''',
        (campo['categoria_id'], campo['ordem'])
    )
    neighbor = cursor.fetchone()
    if not neighbor:
        conn.close()
        return False

    cursor.execute('UPDATE campos SET ordem = ? WHERE id = ?', (neighbor['ordem'], campo['id']))
    cursor.execute('UPDATE campos SET ordem = ? WHERE id = ?', (campo['ordem'], neighbor['id']))
    conn.commit()
    conn.close()
    return True


def delete_campo(campo_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM campos WHERE id = ?', (campo_id,))
    conn.commit()
    conn.close()


def get_valores_empresa_categoria(empresa_id, categoria_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        '''SELECT valores_campos.campo_id, valores_campos.valor
           FROM valores_campos
           INNER JOIN campos ON campos.id = valores_campos.campo_id
           WHERE valores_campos.empresa_id = ? AND campos.categoria_id = ?''',
        (empresa_id, categoria_id)
    )
    valores = {row['campo_id']: row['valor'] or '' for row in cursor.fetchall()}
    conn.close()
    return valores


def save_valores_empresa(empresa_id, valores):
    conn = get_connection()
    cursor = conn.cursor()
    data_atualizacao = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    for campo_id, valor in valores.items():
        cursor.execute(
            '''INSERT INTO valores_campos (empresa_id, campo_id, valor, data_atualizacao)
               VALUES (?, ?, ?, ?)
               ON CONFLICT(empresa_id, campo_id)
               DO UPDATE SET valor = excluded.valor,
                             data_atualizacao = excluded.data_atualizacao''',
            (empresa_id, campo_id, valor.strip(), data_atualizacao)
        )
    conn.commit()
    conn.close()


if __name__ == '__main__':
    init_db()
    print('Banco de dados inicializado com sucesso!')
