"""Camada de acesso ao banco de dados SQLite para BusinessReg."""

import sqlite3
import hashlib
import secrets
from contextlib import contextmanager
from datetime import datetime
from typing import List, Optional

from models import User


class Database:
    def __init__(self, db_path: str = "businessreg.db"):
        self.db_path = db_path
        self.inicializar_banco()

    @contextmanager
    def conectar(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def inicializar_banco(self):
        with self.conectar() as conn:
            cursor = conn.cursor()
            cursor.execute("CREATE TABLE IF NOT EXISTS empresas (id INTEGER PRIMARY KEY AUTOINCREMENT, nome TEXT NOT NULL, cnpj TEXT UNIQUE, endereco TEXT, telefone TEXT, email TEXT, ativo INTEGER DEFAULT 1, data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP)")
            cursor.execute("CREATE TABLE IF NOT EXISTS campos (id INTEGER PRIMARY KEY AUTOINCREMENT, nome TEXT NOT NULL, tipo TEXT NOT NULL, obrigatorio INTEGER DEFAULT 0, opcoes_select TEXT, ordem INTEGER DEFAULT 0, ativo INTEGER DEFAULT 1, data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP)")
            cursor.execute("CREATE TABLE IF NOT EXISTS categorias (id INTEGER PRIMARY KEY AUTOINCREMENT, nome TEXT NOT NULL UNIQUE, descricao TEXT, cor TEXT DEFAULT '#000000', icone TEXT, ativo INTEGER DEFAULT 1, data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP)")
            cursor.execute("CREATE TABLE IF NOT EXISTS cadastros (id INTEGER PRIMARY KEY AUTOINCREMENT, categoria_id INTEGER, empresa_id INTEGER, valores TEXT NOT NULL DEFAULT '{}', data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP, data_modificacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP, FOREIGN KEY (categoria_id) REFERENCES categorias(id), FOREIGN KEY (empresa_id) REFERENCES empresas(id))")
            cursor.execute("CREATE TABLE IF NOT EXISTS usuarios (id INTEGER PRIMARY KEY AUTOINCREMENT, nome TEXT NOT NULL, email TEXT NOT NULL UNIQUE COLLATE NOCASE, senha_hash TEXT NOT NULL, papel TEXT NOT NULL DEFAULT 'usuario' CHECK(papel IN ('master', 'administrador', 'usuario')), ativo INTEGER NOT NULL DEFAULT 1, data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP, data_ultimo_login TIMESTAMP)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_usuarios_email ON usuarios(email)")
            cursor.execute("SELECT COUNT(*) FROM usuarios")
            if cursor.fetchone()[0] == 0:
                cursor.execute("INSERT INTO usuarios (nome, email, senha_hash, papel) VALUES (?, ?, ?, 'master')", ("Master", "master@businessreg.local", self.gerar_hash_senha("master123")))

    @staticmethod
    def gerar_hash_senha(senha: str, sal: Optional[str] = None) -> str:
        if not senha:
            raise ValueError("A senha não pode ser vazia.")
        if sal is None:
            sal = secrets.token_hex(16)
        senha_hash = hashlib.pbkdf2_hmac("sha256", senha.encode("utf-8"), sal.encode("utf-8"), 260000).hex()
        return f"{sal}${senha_hash}"

    @staticmethod
    def verificar_senha(senha: str, senha_hash: str) -> bool:
        try:
            sal, hash_armazenado = senha_hash.split("$", 1)
            calculado = Database.gerar_hash_senha(senha, sal).split("$", 1)[1]
            return secrets.compare_digest(calculado, hash_armazenado)
        except (ValueError, AttributeError):
            return False

    def _row_para_user(self, row) -> Optional[User]:
        if row is None:
            return None
        return User(id=row["id"], nome=row["nome"], email=row["email"], senha_hash=row["senha_hash"], papel=row["papel"], ativo=bool(row["ativo"]), data_criacao=row["data_criacao"], data_ultimo_login=row["data_ultimo_login"])

    def listar_usuarios(self, busca: str = "") -> List[User]:
        with self.conectar() as conn:
            if busca.strip():
                termo = f"%{busca.strip()}%"
                rows = conn.execute("SELECT * FROM usuarios WHERE nome LIKE ? OR email LIKE ? ORDER BY CASE papel WHEN 'master' THEN 0 WHEN 'administrador' THEN 1 ELSE 2 END, nome", (termo, termo)).fetchall()
            else:
                rows = conn.execute("SELECT * FROM usuarios ORDER BY CASE papel WHEN 'master' THEN 0 WHEN 'administrador' THEN 1 ELSE 2 END, nome").fetchall()
            return [self._row_para_user(row) for row in rows]

    def obter_usuario(self, usuario_id: int) -> Optional[User]:
        with self.conectar() as conn:
            return self._row_para_user(conn.execute("SELECT * FROM usuarios WHERE id = ?", (usuario_id,)).fetchone())

    def criar_usuario(self, nome: str, email: str, senha: str, papel: str = "usuario", ativo: bool = True) -> int:
        if papel not in ("administrador", "usuario"):
            raise ValueError("O papel deve ser Administrador ou Usuário.")
        if not nome.strip() or not email.strip() or not senha:
            raise ValueError("Nome, e-mail e senha são obrigatórios.")
        try:
            with self.conectar() as conn:
                cursor = conn.execute("INSERT INTO usuarios (nome, email, senha_hash, papel, ativo) VALUES (?, ?, ?, ?, ?)", (nome.strip(), email.strip().lower(), self.gerar_hash_senha(senha), papel, int(ativo)))
                return cursor.lastrowid
        except sqlite3.IntegrityError:
            raise ValueError("Já existe um usuário com este e-mail.")

    def atualizar_usuario(self, usuario_id: int, nome: str, email: str, papel: str, ativo: bool, senha: str = ""):
        usuario = self.obter_usuario(usuario_id)
        if not usuario:
            raise ValueError("Usuário não encontrado.")
        if usuario.eh_master():
            papel, ativo = "master", True
        elif papel not in ("administrador", "usuario"):
            raise ValueError("O papel deve ser Administrador ou Usuário.")
        if not nome.strip() or not email.strip():
            raise ValueError("Nome e e-mail são obrigatórios.")
        try:
            with self.conectar() as conn:
                if senha:
                    conn.execute("UPDATE usuarios SET nome=?, email=?, papel=?, ativo=?, senha_hash=? WHERE id=?", (nome.strip(), email.strip().lower(), papel, int(ativo), self.gerar_hash_senha(senha), usuario_id))
                else:
                    conn.execute("UPDATE usuarios SET nome=?, email=?, papel=?, ativo=? WHERE id=?", (nome.strip(), email.strip().lower(), papel, int(ativo), usuario_id))
        except sqlite3.IntegrityError:
            raise ValueError("Já existe um usuário com este e-mail.")

    def excluir_usuario(self, usuario_id: int):
        usuario = self.obter_usuario(usuario_id)
        if not usuario:
            raise ValueError("Usuário não encontrado.")
        if usuario.eh_master():
            raise ValueError("A conta Master não pode ser excluída.")
        with self.conectar() as conn:
            conn.execute("DELETE FROM usuarios WHERE id = ?", (usuario_id,))

    def autenticar_usuario(self, email: str, senha: str) -> Optional[User]:
        with self.conectar() as conn:
            user = self._row_para_user(conn.execute("SELECT * FROM usuarios WHERE email=? AND ativo=1", (email.strip().lower(),)).fetchone())
            if user and self.verificar_senha(senha, user.senha_hash):
                conn.execute("UPDATE usuarios SET data_ultimo_login=CURRENT_TIMESTAMP WHERE id=?", (user.id,))
                return user
        return None

    def listar_empresas(self, apenas_ativas=False):
        with self.conectar() as conn:
            sql = "SELECT * FROM empresas" + (" WHERE ativo=1" if apenas_ativas else "") + " ORDER BY nome"
            return conn.execute(sql).fetchall()

    def obter_empresa(self, empresa_id):
        with self.conectar() as conn:
            return conn.execute("SELECT * FROM empresas WHERE id=?", (empresa_id,)).fetchone()

    def criar_empresa(self, nome, cnpj="", endereco="", telefone="", email="", ativo=True):
        with self.conectar() as conn:
            return conn.execute("INSERT INTO empresas (nome,cnpj,endereco,telefone,email,ativo) VALUES (?,?,?,?,?,?)", (nome,cnpj or None,endereco,telefone,email,int(ativo))).lastrowid

    def atualizar_empresa(self, empresa_id, nome, cnpj="", endereco="", telefone="", email="", ativo=True):
        with self.conectar() as conn:
            conn.execute("UPDATE empresas SET nome=?,cnpj=?,endereco=?,telefone=?,email=?,ativo=? WHERE id=?", (nome,cnpj or None,endereco,telefone,email,int(ativo),empresa_id))

    def excluir_empresa(self, empresa_id):
        with self.conectar() as conn:
            conn.execute("DELETE FROM empresas WHERE id=?", (empresa_id,))

    def listar_campos(self, apenas_ativos=False):
        with self.conectar() as conn:
            sql = "SELECT * FROM campos" + (" WHERE ativo=1" if apenas_ativos else "") + " ORDER BY ordem,nome"
            return conn.execute(sql).fetchall()

    def obter_campo(self, campo_id):
        with self.conectar() as conn:
            return conn.execute("SELECT * FROM campos WHERE id=?", (campo_id,)).fetchone()

    def criar_campo(self, nome, tipo, obrigatorio=False, opcoes_select="", ordem=0, ativo=True):
        with self.conectar() as conn:
            return conn.execute("INSERT INTO campos (nome,tipo,obrigatorio,opcoes_select,ordem,ativo) VALUES (?,?,?,?,?,?)", (nome,tipo,int(obrigatorio),opcoes_select,ordem,int(ativo))).lastrowid

    def atualizar_campo(self, campo_id, nome, tipo, obrigatorio=False, opcoes_select="", ordem=0, ativo=True):
        with self.conectar() as conn:
            conn.execute("UPDATE campos SET nome=?,tipo=?,obrigatorio=?,opcoes_select=?,ordem=?,ativo=? WHERE id=?", (nome,tipo,int(obrigatorio),opcoes_select,ordem,int(ativo),campo_id))

    def excluir_campo(self, campo_id):
        with self.conectar() as conn:
            conn.execute("DELETE FROM campos WHERE id=?", (campo_id,))

    def listar_categorias(self, apenas_ativas=False):
        with self.conectar() as conn:
            sql = "SELECT * FROM categorias" + (" WHERE ativo=1" if apenas_ativas else "") + " ORDER BY nome"
            return conn.execute(sql).fetchall()

    def obter_categoria(self, categoria_id):
        with self.conectar() as conn:
            return conn.execute("SELECT * FROM categorias WHERE id=?", (categoria_id,)).fetchone()

    def criar_categoria(self, nome, descricao="", cor="#000000", icone="", ativo=True):
        with self.conectar() as conn:
            return conn.execute("INSERT INTO categorias (nome,descricao,cor,icone,ativo) VALUES (?,?,?,?,?)", (nome,descricao,cor,icone,int(ativo))).lastrowid

    def atualizar_categoria(self, categoria_id, nome, descricao="", cor="#000000", icone="", ativo=True):
        with self.conectar() as conn:
            conn.execute("UPDATE categorias SET nome=?,descricao=?,cor=?,icone=?,ativo=? WHERE id=?", (nome,descricao,cor,icone,int(ativo),categoria_id))

    def excluir_categoria(self, categoria_id):
        with self.conectar() as conn:
            conn.execute("DELETE FROM categorias WHERE id=?", (categoria_id,))

    def listar_cadastros(self, categoria_id=None, empresa_id=None):
        with self.conectar() as conn:
            sql, params = "SELECT * FROM cadastros WHERE 1=1", []
            if categoria_id: sql += " AND categoria_id=?"; params.append(categoria_id)
            if empresa_id: sql += " AND empresa_id=?"; params.append(empresa_id)
            return conn.execute(sql + " ORDER BY data_criacao DESC", params).fetchall()

    def obter_cadastro(self, cadastro_id):
        with self.conectar() as conn:
            return conn.execute("SELECT * FROM cadastros WHERE id=?", (cadastro_id,)).fetchone()

    def criar_cadastro(self, categoria_id, empresa_id, valores):
        import json
        with self.conectar() as conn:
            return conn.execute("INSERT INTO cadastros (categoria_id,empresa_id,valores) VALUES (?,?,?)", (categoria_id,empresa_id,json.dumps(valores,ensure_ascii=False))).lastrowid

    def atualizar_cadastro(self, cadastro_id, categoria_id, empresa_id, valores):
        import json
        with self.conectar() as conn:
            conn.execute("UPDATE cadastros SET categoria_id=?,empresa_id=?,valores=?,data_modificacao=CURRENT_TIMESTAMP WHERE id=?", (categoria_id,empresa_id,json.dumps(valores,ensure_ascii=False),cadastro_id))

    def excluir_cadastro(self, cadastro_id):
        with self.conectar() as conn:
            conn.execute("DELETE FROM cadastros WHERE id=?", (cadastro_id,))