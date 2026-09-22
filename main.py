#!/usr/bin/env python3
"""
BusinessReg - Sistema de Registro de Empresas
Aplicaç´´˜ao principal
"""

from database import init_db

def main():
    """Funç´´˜ao principal do aplicativo."""
    print('=' * 50)
    print('BusinessReg - Sistema de Registro de Empresas')
    print('=' * 50)
    
    # Inicializa o banco de dados
    init_db()
    print('\nBanco de dados inicializado!')
    print('\nPró´´´ximos passos: Interface gr˜afica em desenvolvimento...')
    print('\nPressione Enter para sair.')
    input()

if __name__ == '__main__':
    main()
