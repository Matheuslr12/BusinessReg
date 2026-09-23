"""Modelos de dados para o sistema BusinessReg."""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from datetime import datetime


@dataclass
class Empresa:
    id: Optional[int] = None
    nome: str = ""
    cnpj: str = ""
    endereco: str = ""
    telefone: str = ""
    email: str = ""
    ativo: bool = True
    data_criacao: Optional[datetime] = None


@dataclass
class Campo:
    id: Optional[int] = None
    nome: str = ""
    tipo: str = ""
    obrigatorio: bool = False
    opcoes_select: Optional[str] = None
    ordem: int = 0
    ativo: bool = True
    data_criacao: Optional[datetime] = None


@dataclass
class Categoria:
    id: Optional[int] = None
    nome: str = ""
    descricao: str = ""
    cor: str = "#000000"
    icone: str = ""
    ativo: bool = True
    data_criacao: Optional[datetime] = None


@dataclass
class Cadastro:
    id: Optional[int] = None
    categoria_id: Optional[int] = None
    empresa_id: Optional[int] = None
    valores: Dict[str, Any] = field(default_factory=dict)
    data_criacao: Optional[datetime] = None
    data_modificacao: Optional[datetime] = None


@dataclass
class User:
    """Modelo de Usuário com papéis e verificação de permissão."""
    id: Optional[int] = None
    nome: str = ""
    email: str = ""
    senha_hash: str = ""
    papel: str = "usuario"
    ativo: bool = True
    data_criacao: Optional[datetime] = None
    data_ultimo_login: Optional[datetime] = None

    def eh_master(self) -> bool:
        return self.papel == "master"

    def eh_administrador(self) -> bool:
        return self.papel in ("master", "administrador")

    def pode_acessar(self, modulo: str) -> bool:
        if self.papel == "master":
            return True
        elif self.papel == "administrador":
            return modulo in ("cadastros", "gerenciamento", "configuracoes")
        else:
            return modulo == "cadastros"