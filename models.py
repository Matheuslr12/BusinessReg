from datetime import datetime

class Empresa:
    """Modelo de dados para Empresa."""
    
    def __init__(self, id=None, nome='', cnpj='', endereco='', 
                 telefone='', email='', segmento='', 
                 status='ativa', observacoes='', data_cadastro=None):
        self.id = id
        self.nome = nome
        self.cnpj = cnpj
        self.endereco = endereco
        self.telefone = telefone
        self.email = email
        self.segmento = segmento
        self.status = status
        self.observacoes = observacoes
        self.data_cadastro = data_cadastro or datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    def to_dict(self):
        """Converte o objeto para dicion˜ario."""
        return {
            'id': self.id,
            'nome': self.nome,
            'cnpj': self.cnpj,
            'endereco': self.endereco,
            'telefone': self.telefone,
            'email': self.email,
            'segmento': self.segmento,
            'status': self.status,
            'observacoes': self.observacoes,
            'data_cadastro': self.data_cadastro
        }
    
    @classmethod
    def from_row(cls, row):
        """Cria uma instˆancia a partir de uma linha do banco de dados."""
        if row is None:
            return None
        return cls(
            id=row['id'],
            nome=row['nome'],
            cnpj=row['cnpj'],
            endereco=row['endereco'],
            telefone=row['telefone'],
            email=row['email'],
            segmento=row['segmento'],
            status=row['status'],
            observacoes=row['observacoes'],
            data_cadastro=row['data_cadastro']
        )
