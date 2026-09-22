import sqlite3
from datetime import datetime

DB_NAME = 'empresas.db'

def get_connection():
    """Cria e retorna uma conex˜ao com o banco de dados."""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Inicializa o banco de dados criando a tabela se n˜ao existir."""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS empresas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            cnpj TEXT,
            endereco TEXT,
            telefone TEXT,
            email TEXT,
            segmento TEXT,
            status TEXT DEFAULT 'ativa',
            observacoes TEXT,
            data_cadastro TEXT
        )
    ''')
    
    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_db()
    print('Banco de dados inicializado com sucesso!')
