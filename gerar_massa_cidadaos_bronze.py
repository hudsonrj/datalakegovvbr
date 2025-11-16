#!/usr/bin/env python3
"""
Geração de Massa de Dados - Cidadãos
Cria 1 milhão de cidadãos, cada um com 1 a 15 endereços diferentes
Cada registro contém: CPF, nome, endereço completo, telefone e email
Endereços simulados baseados em dados reais com 150+ variações de formatação
Cada endereço do mesmo cidadão terá uma variação diferente de formatação
"""

import pandas as pd
import random
import re
from minio import Minio
from minio.error import S3Error
import io
from datetime import datetime
from faker import Faker
import numpy as np

# Configurações
MINIO_SERVER_URL = "ch8ai-minio.l6zv5a.easypanel.host"
MINIO_ROOT_USER = "admin"
MINIO_ROOT_PASSWORD = "1q2w3e4r"
BUCKET_NAME = "govbr"

# Inicializar Faker para português brasileiro
fake = Faker('pt_BR')
Faker.seed(42)  # Para reprodutibilidade
random.seed(42)
np.random.seed(42)

# Cliente MinIO
minio_client = Minio(
    MINIO_SERVER_URL,
    access_key=MINIO_ROOT_USER,
    secret_key=MINIO_ROOT_PASSWORD,
    secure=True
)

# Verificar/criar bucket
if not minio_client.bucket_exists(BUCKET_NAME):
    minio_client.make_bucket(BUCKET_NAME)
    print(f"✅ Bucket '{BUCKET_NAME}' criado")

# Dados reais de endereços brasileiros (exemplos)
LOGRADOUROS = [
    "Rua", "Avenida", "Praça", "Travessa", "Alameda", "Estrada", "Rodovia",
    "Viela", "Beco", "Largo", "Vila", "Jardim", "Parque", "Conjunto",
    "Quadra", "Setor", "Chácara", "Fazenda", "Sítio", "Loteamento"
]

NOMES_RUAS = [
    "das Flores", "da Paz", "São Paulo", "Brasil", "da Liberdade", "do Comércio",
    "Principal", "Central", "Nova", "Velha", "do Sol", "da Lua", "dos Pássaros",
    "das Palmeiras", "do Campo", "da Praia", "das Acácias", "dos Ipês",
    "Getúlio Vargas", "Juscelino Kubitschek", "Tancredo Neves", "Dom Pedro II",
    "Tiradentes", "Independência", "República", "Constituição", "Democracia"
]

BAIRROS = [
    "Centro", "Jardim América", "Vila Nova", "São José", "Santa Maria",
    "Bela Vista", "Alto da Boa Vista", "Morumbi", "Copacabana", "Ipanema",
    "Barra da Tijuca", "Tijuca", "Botafogo", "Flamengo", "Laranjeiras",
    "Vila Madalena", "Pinheiros", "Butantã", "Moema", "Vila Olímpia"
]

CIDADES_UF = [
    ("São Paulo", "SP"), ("Rio de Janeiro", "RJ"), ("Belo Horizonte", "MG"),
    ("Salvador", "BA"), ("Brasília", "DF"), ("Curitiba", "PR"),
    ("Recife", "PE"), ("Porto Alegre", "RS"), ("Fortaleza", "CE"),
    ("Manaus", "AM"), ("Belém", "PA"), ("Goiânia", "GO"),
    ("Vitória", "ES"), ("Florianópolis", "SC"), ("Natal", "RN"),
    ("Campinas", "SP"), ("São Luís", "MA"), ("Maceió", "AL"),
    ("João Pessoa", "PB"), ("Aracaju", "SE"), ("Teresina", "PI"),
    ("Cuiabá", "MT"), ("Campo Grande", "MS"), ("Palmas", "TO"),
    ("Rio Branco", "AC"), ("Boa Vista", "RR"), ("Macapá", "AP")
]

COMPLEMENTOS = [
    "Apto", "Apartamento", "Casa", "Sala", "Loja", "Galpão", "Sobrado",
    "Bloco", "Torre", "Conjunto", "Lote", "Quadra", "Chácara", "Sítio"
]

TIPOS_TELEFONE = [
    "residencial", "celular", "comercial", "recado"
]

# Função para gerar CPF válido
def gerar_cpf():
    """Gera um CPF válido formatado"""
    def calcula_digito(cpf, peso):
        soma = sum(int(cpf[i]) * peso[i] for i in range(len(peso)))
        resto = soma % 11
        return 0 if resto < 2 else 11 - resto
    
    cpf = [random.randint(0, 9) for _ in range(9)]
    
    # Primeiro dígito verificador
    peso1 = list(range(10, 1, -1))
    cpf.append(calcula_digito(cpf, peso1))
    
    # Segundo dígito verificador
    peso2 = list(range(11, 1, -1))
    cpf.append(calcula_digito(cpf, peso2))
    
    return ''.join(map(str, cpf))

# Função para formatar CPF
def formatar_cpf(cpf):
    """Formata CPF com ou sem pontuação"""
    if random.random() < 0.3:  # 30% sem formatação
        return cpf
    return f"{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:]}"

# Função para gerar telefone brasileiro
def gerar_telefone():
    """Gera telefone brasileiro com diferentes formatos"""
    tipo = random.choice(TIPOS_TELEFONE)
    
    if tipo == "celular":
        ddd = random.randint(11, 99)
        numero = random.randint(900000000, 999999999)
    else:
        ddd = random.randint(11, 99)
        numero = random.randint(30000000, 99999999)
    
    # Variações de formatação
    formato = random.choice([
        f"({ddd}) {numero}",           # (11) 987654321
        f"{ddd} {numero}",             # 11 987654321
        f"{ddd}-{numero}",             # 11-987654321
        f"({ddd}){numero}",            # (11)987654321
        f"+55 {ddd} {numero}",         # +55 11 987654321
        f"+55 ({ddd}) {numero}",       # +55 (11) 987654321
        f"55{ddd}{numero}",            # 5511987654321
        f"{numero}",                   # 987654321 (sem DDD)
    ])
    
    return formato, tipo

# Função para gerar email
def gerar_email(nome):
    """Gera email baseado no nome"""
    # Limpar nome e criar variações
    nome_limpo = re.sub(r'[^a-zA-Z]', '', nome.lower())
    primeiro_nome = nome_limpo.split()[0] if nome_limpo else "usuario"
    sobrenome = nome_limpo.split()[-1] if len(nome_limpo.split()) > 1 else "silva"
    
    # Variações de domínio
    dominios = [
        "gmail.com", "hotmail.com", "yahoo.com.br", "outlook.com",
        "uol.com.br", "bol.com.br", "terra.com.br", "ig.com.br",
        "globo.com", "r7.com", "live.com", "msn.com"
    ]
    
    # Variações de formato
    formato = random.choice([
        f"{primeiro_nome}.{sobrenome}",
        f"{primeiro_nome}_{sobrenome}",
        f"{primeiro_nome}{sobrenome}",
        f"{primeiro_nome}{random.randint(1, 999)}",
        f"{primeiro_nome}.{sobrenome}{random.randint(1, 99)}",
        f"{sobrenome}.{primeiro_nome}",
        f"{primeiro_nome}{sobrenome[0]}",
    ])
    
    return f"{formato}@{random.choice(dominios)}"

# 150+ variações de formatação de endereços
def gerar_endereco_variado(variacao_especifica=None):
    """Gera endereço com uma das 150+ variações de formatação
    Se variacao_especifica for None, escolhe aleatoriamente entre 1-150
    """
    cidade, uf = random.choice(CIDADES_UF)
    logradouro = random.choice(LOGRADOUROS)
    nome_rua = random.choice(NOMES_RUAS)
    numero = random.randint(1, 9999)
    bairro = random.choice(BAIRROS)
    cep = f"{random.randint(10000, 99999)}-{random.randint(100, 999)}"
    
    # Variações de complemento
    tem_complemento = random.random() < 0.4  # 40% têm complemento
    complemento = ""
    if tem_complemento:
        tipo_comp = random.choice(COMPLEMENTOS)
        num_comp = random.randint(1, 500)
        complemento_variacoes = [
            f"{tipo_comp} {num_comp}",
            f"{tipo_comp} {num_comp}",
            f"{tipo_comp} n° {num_comp}",
            f"{tipo_comp} nº {num_comp}",
            f"{tipo_comp} Nº {num_comp}",
            f"{tipo_comp} N. {num_comp}",
            f"{tipo_comp} {num_comp} Bloco {random.choice(['A', 'B', 'C'])}",
            f"{tipo_comp} {num_comp} Torre {random.randint(1, 5)}",
        ]
        complemento = random.choice(complemento_variacoes)
    
    # Selecionar uma das 150+ variações de formatação
    if variacao_especifica is None:
        variacao = random.randint(1, 150)
    else:
        variacao = variacao_especifica
    
    # Grupo 1-20: Formato padrão com variações de pontuação
    if variacao <= 20:
        if variacao == 1:
            endereco = f"{logradouro} {nome_rua}, {numero}"
        elif variacao == 2:
            endereco = f"{logradouro} {nome_rua}, nº {numero}"
        elif variacao == 3:
            endereco = f"{logradouro} {nome_rua}, n° {numero}"
        elif variacao == 4:
            endereco = f"{logradouro} {nome_rua}, Nº {numero}"
        elif variacao == 5:
            endereco = f"{logradouro} {nome_rua}, N. {numero}"
        elif variacao == 6:
            endereco = f"{logradouro} {nome_rua}, número {numero}"
        elif variacao == 7:
            endereco = f"{logradouro} {nome_rua} {numero}"
        elif variacao == 8:
            endereco = f"{logradouro} {nome_rua}, {numero} - {bairro}"
        elif variacao == 9:
            endereco = f"{logradouro} {nome_rua}, {numero}, {bairro}"
        elif variacao == 10:
            endereco = f"{logradouro} {nome_rua}, {numero} - {bairro} - {cidade}/{uf}"
        elif variacao == 11:
            endereco = f"{logradouro} {nome_rua}, {numero}, {bairro}, {cidade}/{uf}"
        elif variacao == 12:
            endereco = f"{logradouro} {nome_rua}, {numero}, {bairro}, {cidade} - {uf}"
        elif variacao == 13:
            endereco = f"{logradouro} {nome_rua}, {numero}, {bairro}, {cidade}, {uf}"
        elif variacao == 14:
            endereco = f"{logradouro} {nome_rua}, {numero} - {bairro}, {cidade}/{uf}"
        elif variacao == 15:
            endereco = f"{logradouro} {nome_rua}, {numero}, {bairro}, {cidade}/{uf} - CEP: {cep}"
        elif variacao == 16:
            endereco = f"{logradouro} {nome_rua}, {numero}, {bairro}, {cidade}/{uf}, CEP {cep}"
        elif variacao == 17:
            endereco = f"{logradouro} {nome_rua}, {numero}, {bairro}, {cidade}/{uf} CEP {cep}"
        elif variacao == 18:
            endereco = f"{logradouro} {nome_rua}, {numero}, {bairro}, {cidade} - {uf}, {cep}"
        elif variacao == 19:
            endereco = f"{logradouro} {nome_rua}, {numero}, {bairro}, {cidade}/{uf} - {cep}"
        elif variacao == 20:
            endereco = f"{logradouro} {nome_rua}, {numero}, {bairro}, {cidade}/{uf}, CEP: {cep}"
    
    # Grupo 21-40: Com complemento
    elif variacao <= 40:
        if complemento:
            if variacao == 21:
                endereco = f"{logradouro} {nome_rua}, {numero}, {complemento}"
            elif variacao == 22:
                endereco = f"{logradouro} {nome_rua}, {numero} - {complemento}"
            elif variacao == 23:
                endereco = f"{logradouro} {nome_rua}, {numero}, {complemento}, {bairro}"
            elif variacao == 24:
                endereco = f"{logradouro} {nome_rua}, {numero} - {complemento} - {bairro}"
            elif variacao == 25:
                endereco = f"{logradouro} {nome_rua}, {numero}, {complemento}, {bairro}, {cidade}/{uf}"
            elif variacao == 26:
                endereco = f"{logradouro} {nome_rua}, {numero} - {complemento} - {bairro} - {cidade}/{uf}"
            elif variacao == 27:
                endereco = f"{logradouro} {nome_rua}, {numero}, {complemento}, {bairro}, {cidade} - {uf}"
            elif variacao == 28:
                endereco = f"{logradouro} {nome_rua}, {numero}, {complemento}, {bairro}, {cidade}, {uf}"
            elif variacao == 29:
                endereco = f"{logradouro} {nome_rua}, {numero}, {complemento}, {bairro}, {cidade}/{uf} - CEP: {cep}"
            elif variacao == 30:
                endereco = f"{logradouro} {nome_rua}, {numero}, {complemento}, {bairro}, {cidade}/{uf}, CEP {cep}"
            elif variacao == 31:
                endereco = f"{logradouro} {nome_rua}, {numero}, {complemento}, {bairro}, {cidade}/{uf} CEP {cep}"
            elif variacao == 32:
                endereco = f"{logradouro} {nome_rua}, {numero}, {complemento}, {bairro}, {cidade} - {uf}, {cep}"
            elif variacao == 33:
                endereco = f"{logradouro} {nome_rua}, {numero}, {complemento}, {bairro}, {cidade}/{uf} - {cep}"
            elif variacao == 34:
                endereco = f"{logradouro} {nome_rua}, {numero}, {complemento}, {bairro}, {cidade}/{uf}, CEP: {cep}"
            elif variacao == 35:
                endereco = f"{logradouro} {nome_rua}, {numero}, {complemento} - {bairro} - {cidade}/{uf}"
            elif variacao == 36:
                endereco = f"{logradouro} {nome_rua}, {numero}, {complemento} - {bairro}, {cidade}/{uf}"
            elif variacao == 37:
                endereco = f"{logradouro} {nome_rua}, {numero}, {complemento}, {bairro} - {cidade}/{uf}"
            elif variacao == 38:
                endereco = f"{logradouro} {nome_rua}, {numero}, {complemento}, {bairro} - {cidade} - {uf}"
            elif variacao == 39:
                endereco = f"{logradouro} {nome_rua}, {numero}, {complemento}, {bairro}, {cidade}/{uf}"
            elif variacao == 40:
                endereco = f"{logradouro} {nome_rua}, {numero}, {complemento}, {bairro}, {cidade}/{uf}, {cep}"
        else:
            endereco = f"{logradouro} {nome_rua}, {numero}, {bairro}, {cidade}/{uf}"
    
    # Grupo 41-60: Abreviações e variações de logradouro
    elif variacao <= 60:
        log_abrev = {
            "Rua": ["R.", "R", "Rua"],
            "Avenida": ["Av.", "Av", "Avenida", "Ave."],
            "Praça": ["Pça.", "Pça", "Praça"],
            "Travessa": ["Tv.", "Tv", "Travessa"],
            "Alameda": ["Al.", "Al", "Alameda"],
            "Estrada": ["Est.", "Est", "Estrada"],
            "Rodovia": ["Rod.", "Rod", "Rodovia"],
        }.get(logradouro, [logradouro])
        
        log_escolhido = random.choice(log_abrev)
        if variacao == 41:
            endereco = f"{log_escolhido} {nome_rua}, {numero}"
        elif variacao == 42:
            endereco = f"{log_escolhido} {nome_rua}, nº {numero}"
        elif variacao == 43:
            endereco = f"{log_escolhido} {nome_rua}, {numero} - {bairro}"
        elif variacao == 44:
            endereco = f"{log_escolhido} {nome_rua}, {numero}, {bairro}"
        elif variacao == 45:
            endereco = f"{log_escolhido} {nome_rua}, {numero} - {bairro} - {cidade}/{uf}"
        elif variacao == 46:
            endereco = f"{log_escolhido} {nome_rua}, {numero}, {bairro}, {cidade}/{uf}"
        elif variacao == 47:
            endereco = f"{log_escolhido} {nome_rua}, {numero}, {bairro}, {cidade} - {uf}"
        elif variacao == 48:
            endereco = f"{log_escolhido} {nome_rua}, {numero}, {bairro}, {cidade}, {uf}"
        elif variacao == 49:
            endereco = f"{log_escolhido} {nome_rua}, {numero} - {bairro}, {cidade}/{uf}"
        elif variacao == 50:
            endereco = f"{log_escolhido} {nome_rua}, {numero}, {bairro}, {cidade}/{uf} - CEP: {cep}"
        elif variacao == 51:
            endereco = f"{log_escolhido} {nome_rua}, {numero}, {bairro}, {cidade}/{uf}, CEP {cep}"
        elif variacao == 52:
            endereco = f"{log_escolhido} {nome_rua}, {numero}, {bairro}, {cidade}/{uf} CEP {cep}"
        elif variacao == 53:
            endereco = f"{log_escolhido} {nome_rua}, {numero}, {bairro}, {cidade} - {uf}, {cep}"
        elif variacao == 54:
            endereco = f"{log_escolhido} {nome_rua}, {numero}, {bairro}, {cidade}/{uf} - {cep}"
        elif variacao == 55:
            endereco = f"{log_escolhido} {nome_rua}, {numero}, {bairro}, {cidade}/{uf}, CEP: {cep}"
        elif variacao == 56:
            endereco = f"{log_escolhido} {nome_rua}, {numero}, {complemento}, {bairro}, {cidade}/{uf}" if complemento else f"{log_escolhido} {nome_rua}, {numero}, {bairro}, {cidade}/{uf}"
        elif variacao == 57:
            endereco = f"{log_escolhido} {nome_rua}, {numero} - {complemento} - {bairro} - {cidade}/{uf}" if complemento else f"{log_escolhido} {nome_rua}, {numero} - {bairro} - {cidade}/{uf}"
        elif variacao == 58:
            endereco = f"{log_escolhido} {nome_rua}, {numero}, {complemento}, {bairro}, {cidade}/{uf} - CEP: {cep}" if complemento else f"{log_escolhido} {nome_rua}, {numero}, {bairro}, {cidade}/{uf} - CEP: {cep}"
        elif variacao == 59:
            endereco = f"{log_escolhido} {nome_rua}, {numero}, {complemento}, {bairro}, {cidade}/{uf}, CEP {cep}" if complemento else f"{log_escolhido} {nome_rua}, {numero}, {bairro}, {cidade}/{uf}, CEP {cep}"
        elif variacao == 60:
            endereco = f"{log_escolhido} {nome_rua}, {numero}, {complemento}, {bairro}, {cidade}/{uf} CEP {cep}" if complemento else f"{log_escolhido} {nome_rua}, {numero}, {bairro}, {cidade}/{uf} CEP {cep}"
    
    # Grupo 61-80: Formato sem vírgulas ou com diferentes separadores
    elif variacao <= 80:
        if variacao == 61:
            endereco = f"{logradouro} {nome_rua} {numero}"
        elif variacao == 62:
            endereco = f"{logradouro} {nome_rua} {numero} {bairro}"
        elif variacao == 63:
            endereco = f"{logradouro} {nome_rua} {numero} {bairro} {cidade}/{uf}"
        elif variacao == 64:
            endereco = f"{logradouro} {nome_rua} {numero} {bairro} {cidade} {uf}"
        elif variacao == 65:
            endereco = f"{logradouro} {nome_rua} {numero} {bairro} {cidade}/{uf} {cep}"
        elif variacao == 66:
            endereco = f"{logradouro} {nome_rua} {numero} - {bairro} - {cidade}/{uf}"
        elif variacao == 67:
            endereco = f"{logradouro} {nome_rua} {numero} / {bairro} / {cidade}/{uf}"
        elif variacao == 68:
            endereco = f"{logradouro} {nome_rua} {numero} | {bairro} | {cidade}/{uf}"
        elif variacao == 69:
            endereco = f"{logradouro} {nome_rua} {numero} - {bairro} - {cidade} - {uf}"
        elif variacao == 70:
            endereco = f"{logradouro} {nome_rua} {numero} - {bairro} - {cidade}/{uf} - {cep}"
        elif variacao == 71:
            endereco = f"{logradouro} {nome_rua} {numero} {complemento} {bairro} {cidade}/{uf}" if complemento else f"{logradouro} {nome_rua} {numero} {bairro} {cidade}/{uf}"
        elif variacao == 72:
            endereco = f"{logradouro} {nome_rua} {numero} - {complemento} - {bairro} - {cidade}/{uf}" if complemento else f"{logradouro} {nome_rua} {numero} - {bairro} - {cidade}/{uf}"
        elif variacao == 73:
            endereco = f"{logradouro} {nome_rua} {numero} {complemento} {bairro} {cidade}/{uf} {cep}" if complemento else f"{logradouro} {nome_rua} {numero} {bairro} {cidade}/{uf} {cep}"
        elif variacao == 74:
            endereco = f"{logradouro} {nome_rua} {numero} - {complemento} - {bairro} - {cidade}/{uf} - {cep}" if complemento else f"{logradouro} {nome_rua} {numero} - {bairro} - {cidade}/{uf} - {cep}"
        elif variacao == 75:
            endereco = f"{logradouro} {nome_rua} {numero} / {complemento} / {bairro} / {cidade}/{uf}" if complemento else f"{logradouro} {nome_rua} {numero} / {bairro} / {cidade}/{uf}"
        elif variacao == 76:
            endereco = f"{logradouro} {nome_rua} {numero} | {complemento} | {bairro} | {cidade}/{uf}" if complemento else f"{logradouro} {nome_rua} {numero} | {bairro} | {cidade}/{uf}"
        elif variacao == 77:
            endereco = f"{logradouro} {nome_rua} {numero} {complemento} - {bairro} - {cidade}/{uf}" if complemento else f"{logradouro} {nome_rua} {numero} - {bairro} - {cidade}/{uf}"
        elif variacao == 78:
            endereco = f"{logradouro} {nome_rua} {numero} {complemento} {bairro} - {cidade}/{uf}" if complemento else f"{logradouro} {nome_rua} {numero} {bairro} - {cidade}/{uf}"
        elif variacao == 79:
            endereco = f"{logradouro} {nome_rua} {numero} {complemento} {bairro} {cidade}/{uf} CEP {cep}" if complemento else f"{logradouro} {nome_rua} {numero} {bairro} {cidade}/{uf} CEP {cep}"
        elif variacao == 80:
            endereco = f"{logradouro} {nome_rua} {numero} {complemento} {bairro} {cidade}/{uf} - CEP: {cep}" if complemento else f"{logradouro} {nome_rua} {numero} {bairro} {cidade}/{uf} - CEP: {cep}"
    
    # Grupo 81-100: Formato com maiúsculas/minúsculas variadas
    elif variacao <= 100:
        base = f"{logradouro} {nome_rua}, {numero}, {bairro}, {cidade}/{uf}"
        if complemento:
            base = f"{logradouro} {nome_rua}, {numero}, {complemento}, {bairro}, {cidade}/{uf}"
        
        if variacao == 81:
            endereco = base.upper()
        elif variacao == 82:
            endereco = base.lower()
        elif variacao == 83:
            endereco = base.title()
        elif variacao == 84:
            endereco = base.capitalize()
        elif variacao == 85:
            palavras = base.split()
            endereco = ' '.join([p.upper() if i % 2 == 0 else p.lower() for i, p in enumerate(palavras)])
        elif variacao == 86:
            endereco = f"{logradouro.upper()} {nome_rua}, {numero}, {bairro}, {cidade.upper()}/{uf}"
        elif variacao == 87:
            endereco = f"{logradouro.lower()} {nome_rua.lower()}, {numero}, {bairro.lower()}, {cidade.lower()}/{uf.lower()}"
        elif variacao == 88:
            endereco = f"{logradouro.title()} {nome_rua.title()}, {numero}, {bairro.title()}, {cidade.title()}/{uf.upper()}"
        elif variacao == 89:
            endereco = f"{logradouro.upper()} {nome_rua}, {numero}, {bairro.upper()}, {cidade}/{uf.upper()}"
        elif variacao == 90:
            endereco = f"{logradouro} {nome_rua.upper()}, {numero}, {bairro}, {cidade.upper()}/{uf}"
        elif variacao == 91:
            endereco = base.upper() + f" - CEP: {cep}"
        elif variacao == 92:
            endereco = base.lower() + f" - cep: {cep}"
        elif variacao == 93:
            endereco = base.title() + f" - Cep: {cep}"
        elif variacao == 94:
            endereco = f"{logradouro.upper()} {nome_rua}, {numero}, {complemento.upper()}, {bairro.upper()}, {cidade.upper()}/{uf}" if complemento else f"{logradouro.upper()} {nome_rua}, {numero}, {bairro.upper()}, {cidade.upper()}/{uf}"
        elif variacao == 95:
            endereco = f"{logradouro.lower()} {nome_rua.lower()}, {numero}, {complemento.lower()}, {bairro.lower()}, {cidade.lower()}/{uf.lower()}" if complemento else f"{logradouro.lower()} {nome_rua.lower()}, {numero}, {bairro.lower()}, {cidade.lower()}/{uf.lower()}"
        elif variacao == 96:
            endereco = f"{logradouro.title()} {nome_rua.title()}, {numero}, {complemento.title()}, {bairro.title()}, {cidade.title()}/{uf.upper()}" if complemento else f"{logradouro.title()} {nome_rua.title()}, {numero}, {bairro.title()}, {cidade.title()}/{uf.upper()}"
        elif variacao == 97:
            endereco = base.upper() + f" CEP {cep}"
        elif variacao == 98:
            endereco = base.lower() + f" cep {cep}"
        elif variacao == 99:
            endereco = base.title() + f" Cep {cep}"
        elif variacao == 100:
            endereco = base + f" - CEP: {cep}"
    
    # Grupo 101-120: Formato com espaços extras ou compacto
    elif variacao <= 120:
        if variacao == 101:
            endereco = f"{logradouro}  {nome_rua},  {numero},  {bairro},  {cidade}/{uf}"
        elif variacao == 102:
            endereco = f"{logradouro}   {nome_rua},   {numero},   {bairro},   {cidade}/{uf}"
        elif variacao == 103:
            endereco = f"{logradouro} {nome_rua},{numero},{bairro},{cidade}/{uf}"
        elif variacao == 104:
            endereco = f"{logradouro}{nome_rua},{numero},{bairro},{cidade}/{uf}"
        elif variacao == 105:
            endereco = f"{logradouro} {nome_rua}, {numero}, {bairro}, {cidade}/{uf}".replace(" ", "")
        elif variacao == 106:
            endereco = f"{logradouro}  {nome_rua},  {numero},  {bairro},  {cidade}/{uf}  -  CEP:  {cep}"
        elif variacao == 107:
            endereco = f"{logradouro} {nome_rua},{numero},{bairro},{cidade}/{uf} CEP:{cep}"
        elif variacao == 108:
            endereco = f"{logradouro}{nome_rua},{numero},{bairro},{cidade}/{uf}CEP{cep}"
        elif variacao == 109:
            endereco = f"{logradouro}  {nome_rua},  {numero},  {complemento},  {bairro},  {cidade}/{uf}" if complemento else f"{logradouro}  {nome_rua},  {numero},  {bairro},  {cidade}/{uf}"
        elif variacao == 110:
            endereco = f"{logradouro} {nome_rua},{numero},{complemento},{bairro},{cidade}/{uf}" if complemento else f"{logradouro} {nome_rua},{numero},{bairro},{cidade}/{uf}"
        elif variacao == 111:
            endereco = f"{logradouro}{nome_rua},{numero},{complemento},{bairro},{cidade}/{uf}" if complemento else f"{logradouro}{nome_rua},{numero},{bairro},{cidade}/{uf}"
        elif variacao == 112:
            endereco = f"{logradouro}  {nome_rua},  {numero},  {complemento},  {bairro},  {cidade}/{uf}  -  CEP:  {cep}" if complemento else f"{logradouro}  {nome_rua},  {numero},  {bairro},  {cidade}/{uf}  -  CEP:  {cep}"
        elif variacao == 113:
            endereco = f"{logradouro} {nome_rua},{numero},{complemento},{bairro},{cidade}/{uf}CEP:{cep}" if complemento else f"{logradouro} {nome_rua},{numero},{bairro},{cidade}/{uf}CEP:{cep}"
        elif variacao == 114:
            endereco = f"{logradouro}{nome_rua},{numero},{complemento},{bairro},{cidade}/{uf}CEP{cep}" if complemento else f"{logradouro}{nome_rua},{numero},{bairro},{cidade}/{uf}CEP{cep}"
        elif variacao == 115:
            endereco = f"{logradouro} {nome_rua}, {numero}, {bairro}, {cidade}/{uf}".replace(" ", "  ")
        elif variacao == 116:
            endereco = f"{logradouro} {nome_rua}, {numero}, {bairro}, {cidade}/{uf}".replace(", ", ",")
        elif variacao == 117:
            endereco = f"{logradouro} {nome_rua}, {numero}, {bairro}, {cidade}/{uf}".replace(" ", "")
        elif variacao == 118:
            endereco = f"{logradouro} {nome_rua}, {numero}, {complemento}, {bairro}, {cidade}/{uf}".replace(" ", "  ") if complemento else f"{logradouro} {nome_rua}, {numero}, {bairro}, {cidade}/{uf}".replace(" ", "  ")
        elif variacao == 119:
            endereco = f"{logradouro} {nome_rua}, {numero}, {complemento}, {bairro}, {cidade}/{uf}".replace(", ", ",") if complemento else f"{logradouro} {nome_rua}, {numero}, {bairro}, {cidade}/{uf}".replace(", ", ",")
        elif variacao == 120:
            endereco = f"{logradouro} {nome_rua}, {numero}, {complemento}, {bairro}, {cidade}/{uf}".replace(" ", "") if complemento else f"{logradouro} {nome_rua}, {numero}, {bairro}, {cidade}/{uf}".replace(" ", "")
    
    # Grupo 121-140: Formato com informações adicionais ou ordem diferente
    elif variacao <= 140:
        if variacao == 121:
            endereco = f"{bairro}, {logradouro} {nome_rua}, {numero}, {cidade}/{uf}"
        elif variacao == 122:
            endereco = f"{cidade}/{uf}, {bairro}, {logradouro} {nome_rua}, {numero}"
        elif variacao == 123:
            endereco = f"{cidade}/{uf} - {bairro} - {logradouro} {nome_rua}, {numero}"
        elif variacao == 124:
            endereco = f"{bairro} - {logradouro} {nome_rua}, {numero} - {cidade}/{uf}"
        elif variacao == 125:
            endereco = f"{cidade}/{uf}, {bairro}, {logradouro} {nome_rua}, {numero}, {complemento}" if complemento else f"{cidade}/{uf}, {bairro}, {logradouro} {nome_rua}, {numero}"
        elif variacao == 126:
            endereco = f"{bairro}, {logradouro} {nome_rua}, {numero}, {complemento}, {cidade}/{uf}" if complemento else f"{bairro}, {logradouro} {nome_rua}, {numero}, {cidade}/{uf}"
        elif variacao == 127:
            endereco = f"{cidade}/{uf} - {bairro} - {logradouro} {nome_rua}, {numero} - {complemento}" if complemento else f"{cidade}/{uf} - {bairro} - {logradouro} {nome_rua}, {numero}"
        elif variacao == 128:
            endereco = f"{bairro} - {logradouro} {nome_rua}, {numero} - {complemento} - {cidade}/{uf}" if complemento else f"{bairro} - {logradouro} {nome_rua}, {numero} - {cidade}/{uf}"
        elif variacao == 129:
            endereco = f"{cidade}/{uf}, {bairro}, {logradouro} {nome_rua}, {numero}, CEP: {cep}"
        elif variacao == 130:
            endereco = f"{bairro}, {logradouro} {nome_rua}, {numero}, {cidade}/{uf}, CEP: {cep}"
        elif variacao == 131:
            endereco = f"{cidade}/{uf} - {bairro} - {logradouro} {nome_rua}, {numero} - CEP: {cep}"
        elif variacao == 132:
            endereco = f"{bairro} - {logradouro} {nome_rua}, {numero} - {cidade}/{uf} - CEP: {cep}"
        elif variacao == 133:
            endereco = f"{cidade}/{uf}, {bairro}, {logradouro} {nome_rua}, {numero}, {complemento}, CEP: {cep}" if complemento else f"{cidade}/{uf}, {bairro}, {logradouro} {nome_rua}, {numero}, CEP: {cep}"
        elif variacao == 134:
            endereco = f"{bairro}, {logradouro} {nome_rua}, {numero}, {complemento}, {cidade}/{uf}, CEP: {cep}" if complemento else f"{bairro}, {logradouro} {nome_rua}, {numero}, {cidade}/{uf}, CEP: {cep}"
        elif variacao == 135:
            endereco = f"{cidade}/{uf} - {bairro} - {logradouro} {nome_rua}, {numero} - {complemento} - CEP: {cep}" if complemento else f"{cidade}/{uf} - {bairro} - {logradouro} {nome_rua}, {numero} - CEP: {cep}"
        elif variacao == 136:
            endereco = f"{bairro} - {logradouro} {nome_rua}, {numero} - {complemento} - {cidade}/{uf} - CEP: {cep}" if complemento else f"{bairro} - {logradouro} {nome_rua}, {numero} - {cidade}/{uf} - CEP: {cep}"
        elif variacao == 137:
            endereco = f"Bairro: {bairro}, {logradouro} {nome_rua}, {numero}, {cidade}/{uf}"
        elif variacao == 138:
            endereco = f"{logradouro} {nome_rua}, {numero}, Bairro: {bairro}, {cidade}/{uf}"
        elif variacao == 139:
            endereco = f"{logradouro} {nome_rua}, {numero}, {bairro}, Cidade: {cidade}/{uf}"
        elif variacao == 140:
            endereco = f"{logradouro} {nome_rua}, {numero}, {bairro}, {cidade}/{uf}, CEP: {cep}"
    
    # Grupo 141-150: Formato com caracteres especiais ou formatações únicas
    else:
        if variacao == 141:
            endereco = f"{logradouro} {nome_rua}, {numero}, {bairro}, {cidade} / {uf}"
        elif variacao == 142:
            endereco = f"{logradouro} {nome_rua}, {numero}, {bairro}, {cidade} / {uf} / CEP: {cep}"
        elif variacao == 143:
            endereco = f"{logradouro} {nome_rua}, {numero}, {bairro}, {cidade} / {uf} / {cep}"
        elif variacao == 144:
            endereco = f"{logradouro} {nome_rua}, {numero}, {bairro}, {cidade} / {uf} - {cep}"
        elif variacao == 145:
            endereco = f"{logradouro} {nome_rua}, {numero}, {complemento}, {bairro}, {cidade} / {uf}" if complemento else f"{logradouro} {nome_rua}, {numero}, {bairro}, {cidade} / {uf}"
        elif variacao == 146:
            endereco = f"{logradouro} {nome_rua}, {numero}, {complemento}, {bairro}, {cidade} / {uf} / CEP: {cep}" if complemento else f"{logradouro} {nome_rua}, {numero}, {bairro}, {cidade} / {uf} / CEP: {cep}"
        elif variacao == 147:
            endereco = f"{logradouro} {nome_rua}, {numero}, {complemento}, {bairro}, {cidade} / {uf} / {cep}" if complemento else f"{logradouro} {nome_rua}, {numero}, {bairro}, {cidade} / {uf} / {cep}"
        elif variacao == 148:
            endereco = f"{logradouro} {nome_rua}, {numero}, {complemento}, {bairro}, {cidade} / {uf} - {cep}" if complemento else f"{logradouro} {nome_rua}, {numero}, {bairro}, {cidade} / {uf} - {cep}"
        elif variacao == 149:
            endereco = f"{logradouro} {nome_rua}, {numero}, {bairro}, {cidade}/{uf} - CEP {cep}"
        elif variacao == 150:
            endereco = f"{logradouro} {nome_rua}, {numero}, {complemento}, {bairro}, {cidade}/{uf} - CEP {cep}" if complemento else f"{logradouro} {nome_rua}, {numero}, {bairro}, {cidade}/{uf} - CEP {cep}"
    
    return endereco

def save_to_bronze(df, dataset_name, source="simulado", partition_date=None):
    """Salva DataFrame na camada Bronze em formato Parquet"""
    if partition_date is None:
        partition_date = datetime.now().strftime('%Y%m%d')

    object_name = f"bronze/{source}/{dataset_name}/dt={partition_date}/data.parquet"

    try:
        # Converter para Parquet
        buffer = io.BytesIO()
        df.to_parquet(buffer, index=False, engine='pyarrow', compression='snappy')
        buffer.seek(0)

        # Upload para MinIO
        minio_client.put_object(
            BUCKET_NAME,
            object_name,
            buffer,
            length=buffer.getbuffer().nbytes,
            content_type='application/octet-stream'
        )

        print(f"✅ Bronze: {object_name} ({len(df)} registros, {buffer.getbuffer().nbytes/1024/1024:.2f} MB)")
        return True
    except Exception as e:
        print(f"❌ Erro ao salvar {object_name}: {e}")
        return False

def gerar_massa_cidadaos(num_cidadaos=1000000):
    """Gera massa de dados de cidadãos
    Cada cidadão terá de 1 a 15 endereços diferentes
    """
    print("=" * 80)
    print(f"GERAÇÃO DE MASSA DE DADOS - {num_cidadaos:,} CIDADÃOS")
    print("Cada cidadão terá de 1 a 15 endereços (variação aleatória)")
    print("=" * 80)
    
    dados = []
    batch_size = 10000  # Processar em lotes para não sobrecarregar memória
    total_registros_gerados = 0
    cidadaos_processados = 0
    
    # Processar cidadãos em lotes
    for batch_start in range(0, num_cidadaos, batch_size):
        batch_end = min(batch_start + batch_size, num_cidadaos)
        print(f"\n📊 Processando cidadãos {batch_start+1:,} a {batch_end:,}...")
        
        batch_data = []
        for i in range(batch_start, batch_end):
            # Gerar CPF único para este cidadão
            cpf = gerar_cpf()
            cpf_formatado = formatar_cpf(cpf)
            
            # Gerar nome único para este cidadão
            nome = fake.name()
            
            # Gerar telefone para este cidadão (pode ter múltiplos telefones)
            telefone, tipo_telefone = gerar_telefone()
            
            # Gerar email baseado no nome do cidadão
            email = gerar_email(nome)
            
            # Cada cidadão terá de 1 a 15 endereços
            num_enderecos = random.randint(1, 15)
            
            # Garantir que cada endereço do mesmo cidadão tenha uma variação diferente
            # Selecionar variações únicas para este cidadão
            variacoes_disponiveis = list(range(1, 151))
            random.shuffle(variacoes_disponiveis)
            
            for endereco_idx in range(num_enderecos):
                # Usar uma variação diferente para cada endereço
                # Se tiver mais de 150 endereços (não vai acontecer, mas por segurança)
                if endereco_idx < len(variacoes_disponiveis):
                    variacao = variacoes_disponiveis[endereco_idx]
                else:
                    variacao = random.randint(1, 150)
                
                # Gerar endereço com variação específica
                endereco = gerar_endereco_variado(variacao_especifica=variacao)
                
                # Adicionar índice do endereço para identificar múltiplos endereços do mesmo cidadão
                batch_data.append({
                    'cpf': cpf_formatado,
                    'nome': nome,
                    'endereco': endereco,
                    'telefone': telefone,
                    'email': email,
                    'tipo_telefone': tipo_telefone,
                    'numero_endereco': endereco_idx + 1,  # 1, 2, 3, ..., até 15
                    'total_enderecos': num_enderecos  # Total de endereços deste cidadão
                })
                total_registros_gerados += 1
            
            cidadaos_processados += 1
            
            if cidadaos_processados % 100 == 0:
                print(f"  Progresso: {cidadaos_processados:,}/{num_cidadaos:,} cidadãos ({((cidadaos_processados)/num_cidadaos*100):.1f}%) | {total_registros_gerados:,} registros de endereços gerados")
        
        dados.extend(batch_data)
        
        # Salvar em lotes para não sobrecarregar memória
        # Acumular dados e salvar quando atingir um tamanho grande ou no final
        if len(dados) >= 500000 or batch_end == num_cidadaos:  # Salvar a cada 500k registros ou no final
            df_batch = pd.DataFrame(dados)
            print(f"\n💾 Salvando lote de {len(df_batch):,} registros de endereços...")
            
            # Se já existe arquivo, ler e fazer merge
            partition_date = datetime.now().strftime('%Y%m%d')
            object_name = f"bronze/simulado/cidadaos/dt={partition_date}/data.parquet"
            
            try:
                # Tentar ler arquivo existente
                response = minio_client.get_object(BUCKET_NAME, object_name)
                df_existente = pd.read_parquet(io.BytesIO(response.read()))
                print(f"  📂 Arquivo existente encontrado com {len(df_existente):,} registros")
                # Combinar com novos dados
                df_batch = pd.concat([df_existente, df_batch], ignore_index=True)
                print(f"  🔄 Combinando com novos dados: {len(df_batch):,} registros totais")
            except Exception:
                # Arquivo não existe, criar novo
                print(f"  📝 Criando novo arquivo")
            
            # Salvar arquivo combinado
            save_to_bronze(df_batch, 'cidadaos', 'simulado')
            dados = []  # Limpar lista após salvar
    
    print("\n" + "=" * 80)
    print("✅ GERAÇÃO DE MASSA DE DADOS CONCLUÍDA!")
    print("=" * 80)
    print(f"\n📊 Estatísticas:")
    print(f"   • Total de cidadãos: {num_cidadaos:,}")
    print(f"   • Total de registros de endereços: {total_registros_gerados:,}")
    print(f"   • Média de endereços por cidadão: {total_registros_gerados/num_cidadaos:.2f}")
    print(f"\n📁 Localização: bronze/simulado/cidadaos/dt=YYYYMMDD/data.parquet")

if __name__ == "__main__":
    # Gerar 1 milhão de registros
    gerar_massa_cidadaos(1000000)
