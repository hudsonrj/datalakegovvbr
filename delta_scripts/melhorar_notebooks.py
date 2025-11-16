#!/usr/bin/env python3
"""
Script para melhorar a estrutura dos notebooks de ingestão
Divide o código em células bem organizadas
"""

import json
import re

def criar_notebook_bronze_melhorado():
    """Cria notebook Bronze com estrutura melhorada"""
    
    with open('01_bronze_ingestion.py', 'r') as f:
        script = f.read()
    
    cells = []
    
    # Título
    cells.append({
        'cell_type': 'markdown',
        'metadata': {},
        'source': [
            '# 🥉 Camada Bronze - Ingestão de Dados Brutos\n',
            '\n',
            'Este notebook executa a ingestão de dados brutos de APIs governamentais e armazena na camada Bronze em formato Parquet.\n',
            '\n',
            '## Fontes de Dados:\n',
            '- **IBGE**: Municípios, Estados, População\n',
            '- **Portal da Transparência**: Órgãos SIAFI, BPC por Município\n',
            '\n',
            '## Estrutura de Saída:\n',
            '```\n',
            'bronze/\n',
            '├── ibge/\n',
            '│   ├── municipios/dt=YYYYMMDD/data.parquet\n',
            '│   ├── estados/dt=YYYYMMDD/data.parquet\n',
            '│   └── populacao_estados/dt=YYYYMMDD/data.parquet\n',
            '└── portal_transparencia/\n',
            '    ├── orgaos_siafi/dt=YYYYMMDD/data.parquet\n',
            '    └── bpc_municipios/dt=YYYYMMDD/data.parquet\n',
            '```'
        ]
    })
    
    # Instalar dependências
    cells.append({
        'cell_type': 'code',
        'metadata': {},
        'source': ['# Instalar dependências se necessário\n', '!pip install -q requests pandas minio pyarrow']
    })
    
    # Configurações e imports
    config_code = """import requests
import pandas as pd
from minio import Minio
from minio.error import S3Error
import io
from datetime import datetime
import json

# Configurações
PORTAL_TRANSPARENCIA_API_KEY = "2c56919ba91b8c1b13473dcef43fb031"
MINIO_SERVER_URL = "ch8ai-minio.l6zv5a.easypanel.host"
MINIO_ROOT_USER = "admin"
MINIO_ROOT_PASSWORD = "1q2w3e4r"
BUCKET_NAME = "govbr"

transparency_url = "http://api.portaldatransparencia.gov.br/api-de-dados"
ibge_url = "https://servicodados.ibge.gov.br/api/v1"

headers = {
    'chave-api-dados': PORTAL_TRANSPARENCIA_API_KEY
}

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
else:
    print(f"✅ Bucket '{BUCKET_NAME}' já existe")

def save_to_bronze(df, dataset_name, source, partition_date=None):
    \"\"\"Salva DataFrame na camada Bronze em formato Parquet\"\"\"
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

        print(f"✅ Bronze: {object_name} ({len(df)} registros, {buffer.getbuffer().nbytes/1024:.2f} KB)")
        return True
    except Exception as e:
        print(f"❌ Erro ao salvar {object_name}: {e}")
        return False

print("=" * 80)
print("CAMADA BRONZE - INGESTÃO DE DADOS BRUTOS")
print("=" * 80)
"""
    
    cells.append({
        'cell_type': 'code',
        'metadata': {},
        'source': config_code.split('\n')
    })
    
    # Seção 1: Municípios
    cells.append({
        'cell_type': 'markdown',
        'metadata': {},
        'source': ['## [1/5] Coletando Municípios do Brasil (IBGE)']
    })
    
    municipios_code = """# IBGE - Municípios
print("\\n[1/5] Coletando municípios do Brasil (IBGE)...")
response = requests.get(f"{ibge_url}/localidades/municipios", timeout=30)
if response.status_code == 200:
    municipios = response.json()
    municipios_data = []
    for m in municipios:
        try:
            microrregiao = m.get('microrregiao', {})
            mesorregiao = microrregiao.get('mesorregiao', {}) if microrregiao else {}
            uf = mesorregiao.get('UF', {}) if mesorregiao else {}
            regiao = uf.get('regiao', {}) if uf else {}
            
            municipios_data.append({
                'codigo_ibge': m.get('id'),
                'municipio': m.get('nome'),
                'uf_sigla': uf.get('sigla'),
                'uf_nome': uf.get('nome'),
                'regiao_id': regiao.get('id'),
                'regiao_nome': regiao.get('nome'),
                'microrregiao_id': microrregiao.get('id') if microrregiao else None,
                'microrregiao_nome': microrregiao.get('nome') if microrregiao else None,
                'mesorregiao_id': mesorregiao.get('id') if mesorregiao else None,
                'mesorregiao_nome': mesorregiao.get('nome') if mesorregiao else None
            })
        except Exception as e:
            print(f"  ⚠️  Erro ao processar município {m.get('id', 'N/A')}: {e}")
            continue
    
    df_municipios = pd.DataFrame(municipios_data)
    print(f"✅ {len(df_municipios)} municípios coletados")
    save_to_bronze(df_municipios, 'municipios', 'ibge')
else:
    print(f"❌ Erro ao coletar municípios: {response.status_code}")
"""
    
    cells.append({
        'cell_type': 'code',
        'metadata': {},
        'source': municipios_code.split('\n')
    })
    
    # Seção 2: Estados
    cells.append({
        'cell_type': 'markdown',
        'metadata': {},
        'source': ['## [2/5] Coletando Estados do Brasil (IBGE)']
    })
    
    estados_code = """# IBGE - Estados
print("\\n[2/5] Coletando estados do Brasil (IBGE)...")
response = requests.get(f"{ibge_url}/localidades/estados", timeout=30)
if response.status_code == 200:
    estados = response.json()
    df_estados = pd.DataFrame([{
        'uf_id': e['id'],
        'uf_sigla': e['sigla'],
        'uf_nome': e['nome'],
        'regiao_id': e['regiao']['id'],
        'regiao_sigla': e['regiao']['sigla'],
        'regiao_nome': e['regiao']['nome']
    } for e in estados])

    print(f"✅ {len(df_estados)} estados coletados")
    save_to_bronze(df_estados, 'estados', 'ibge')
else:
    print(f"❌ Erro ao coletar estados: {response.status_code}")
"""
    
    cells.append({
        'cell_type': 'code',
        'metadata': {},
        'source': estados_code.split('\n')
    })
    
    # Seção 3: Órgãos SIAFI
    cells.append({
        'cell_type': 'markdown',
        'metadata': {},
        'source': ['## [3/5] Coletando Órgãos SIAFI (Portal da Transparência)']
    })
    
    orgaos_code = """# Portal da Transparência - Órgãos SIAFI
print("\\n[3/5] Coletando órgãos SIAFI...")
response = requests.get(f"{transparency_url}/orgaos-siafi", headers=headers, timeout=30)
if response.status_code == 200:
    orgaos = response.json()
    df_orgaos = pd.DataFrame(orgaos)
    # Filtrar órgãos válidos
    df_orgaos = df_orgaos[~df_orgaos['descricao'].str.contains('CODIGO INVALIDO', na=False)]
    
    print(f"✅ {len(df_orgaos)} órgãos coletados")
    save_to_bronze(df_orgaos, 'orgaos_siafi', 'portal_transparencia')
else:
    print(f"❌ Erro ao coletar órgãos: {response.status_code}")
"""
    
    cells.append({
        'cell_type': 'code',
        'metadata': {},
        'source': orgaos_code.split('\n')
    })
    
    # Seção 4: BPC
    cells.append({
        'cell_type': 'markdown',
        'metadata': {},
        'source': ['## [4/5] Coletando Dados de BPC (Portal da Transparência)']
    })
    
    bpc_code = """# Portal da Transparência - BPC por município (amostra de SP)
print("\\n[4/5] Coletando dados de BPC (amostra SP - primeiros 50 municípios)...")

# Pegar municípios de SP
if 'df_municipios' in locals() and df_municipios is not None and len(df_municipios) > 0:
    df_municipios_sp = df_municipios[df_municipios['uf_sigla'] == 'SP'].head(50)
else:
    print("  ⚠️  Municípios não disponíveis, pulando coleta de BPC")
    df_municipios_sp = pd.DataFrame()

bpc_data = []

if len(df_municipios_sp) > 0:
    for idx, row in df_municipios_sp.iterrows():
        codigo = str(row['codigo_ibge'])
        nome = row['municipio']

        if idx % 10 == 0:
            print(f"  Progresso: {idx}/{len(df_municipios_sp)} municípios...")

        try:
            response = requests.get(
                f"{transparency_url}/bpc-por-municipio",
                headers=headers,
                params={'mesAno': '202412', 'codigoIbge': codigo, 'pagina': 1},
                timeout=10
            )

            if response.status_code == 200 and response.json():
                data = response.json()[0]
                # Flatten nested structure
                record = {
                    'id': data.get('id'),
                    'data_referencia': data.get('dataReferencia'),
                    'codigo_ibge': data['municipio']['codigoIBGE'],
                    'nome_municipio': data['municipio']['nomeIBGE'],
                    'uf_sigla': data['municipio']['uf']['sigla'],
                    'uf_nome': data['municipio']['uf']['nome'],
                    'regiao_nome': data['municipio']['nomeRegiao'],
                    'tipo_id': data['tipo']['id'],
                    'tipo_descricao': data['tipo']['descricao'],
                    'tipo_descricao_detalhada': data['tipo']['descricaoDetalhada'],
                    'valor': data.get('valor'),
                    'quantidade_beneficiados': data.get('quantidadeBeneficiados')
                }
                bpc_data.append(record)
        except Exception as e:
            print(f"  ⚠️  Erro em {nome}: {e}")

if len(df_municipios_sp) > 0 and bpc_data:
    df_bpc = pd.DataFrame(bpc_data)
    save_to_bronze(df_bpc, 'bpc_municipios', 'portal_transparencia')
    print(f"  ✅ {len(bpc_data)} municípios com dados de BPC")
else:
    print("  ❌ Nenhum dado de BPC coletado")
"""
    
    cells.append({
        'cell_type': 'code',
        'metadata': {},
        'source': bpc_code.split('\n')
    })
    
    # Seção 5: População
    cells.append({
        'cell_type': 'markdown',
        'metadata': {},
        'source': ['## [5/5] Coletando População por Estado (IBGE)']
    })
    
    populacao_code = """# IBGE - População estimada por estado
print("\\n[5/5] Coletando estimativas de população por estado...")
try:
    populacao_data = []
    if 'df_estados' not in locals() or df_estados is None or len(df_estados) == 0:
        raise Exception("Estados não disponíveis")
    
    for idx, row in df_estados.iterrows():
        uf_id = row['uf_id']
        uf_sigla = row['uf_sigla']

        # Endpoint de projeção de população
        response = requests.get(
            f"{ibge_url}/projecoes/populacao/{uf_id}",
            timeout=10
        )

        if response.status_code == 200:
            data = response.json()
            if data and 'projecao' in data:
                populacao_data.append({
                    'uf_id': uf_id,
                    'uf_sigla': uf_sigla,
                    'ano': 2024,
                    'populacao': data['projecao']['populacao']
                })

    if populacao_data:
        df_populacao = pd.DataFrame(populacao_data)
        print(f"✅ {len(df_populacao)} estados com dados de população")
        save_to_bronze(df_populacao, 'populacao_estados', 'ibge')
    else:
        raise Exception("Nenhum dado de população coletado")
        
except Exception as e:
    print(f"  ⚠️  Endpoint de população não disponível, usando dados manuais: {e}")
    # Dados de população estimada 2024 (fonte: IBGE)
    populacao_manual = [
        {'uf_sigla': 'SP', 'uf_id': 35, 'ano': 2024, 'populacao': 46649132},
        {'uf_sigla': 'MG', 'uf_id': 31, 'ano': 2024, 'populacao': 21411923},
        {'uf_sigla': 'RJ', 'uf_id': 33, 'ano': 2024, 'populacao': 17463349},
        {'uf_sigla': 'BA', 'uf_id': 29, 'ano': 2024, 'populacao': 14985284},
        {'uf_sigla': 'PR', 'uf_id': 41, 'ano': 2024, 'populacao': 11597484},
    ]
    df_populacao = pd.DataFrame(populacao_manual)
    print(f"✅ {len(df_populacao)} estados com dados manuais de população")
    save_to_bronze(df_populacao, 'populacao_estados', 'ibge')
"""
    
    cells.append({
        'cell_type': 'code',
        'metadata': {},
        'source': populacao_code.split('\n')
    })
    
    # Resumo
    cells.append({
        'cell_type': 'markdown',
        'metadata': {},
        'source': ['## Resumo da Ingestão']
    })
    
    resumo_code = """# Listar arquivos Bronze
print("\\n" + "=" * 80)
print("RESUMO DA INGESTÃO")
print("=" * 80)

objects = minio_client.list_objects(BUCKET_NAME, prefix="bronze/", recursive=True)
bronze_files = list(objects)

print(f"\\nTotal de arquivos na camada Bronze: {len(bronze_files)}")
total_size = 0
for obj in bronze_files:
    size_kb = obj.size / 1024
    total_size += obj.size
    print(f"  📁 {obj.object_name} ({size_kb:.2f} KB)")

print(f"\\nTamanho total: {total_size/1024:.2f} KB")
print("\\n✅ Ingestão Bronze concluída!")
"""
    
    cells.append({
        'cell_type': 'code',
        'metadata': {},
        'source': resumo_code.split('\n')
    })
    
    notebook = {
        'cells': cells,
        'metadata': {
            'kernelspec': {'display_name': 'Python 3', 'language': 'python', 'name': 'python3'},
            'language_info': {'name': 'python', 'version': '3.10.0'}
        },
        'nbformat': 4,
        'nbformat_minor': 4
    }
    
    with open('NOTEBOOK_01_BRONZE_INGESTION.ipynb', 'w', encoding='utf-8') as f:
        json.dump(notebook, f, indent=2, ensure_ascii=False)
    
    print("✅ Notebook Bronze melhorado criado")

def criar_notebook_prata_melhorado():
    """Cria notebook Prata com estrutura melhorada"""
    
    with open('02_prata_transformacao.py', 'r') as f:
        script = f.read()
    
    cells = []
    
    # Título
    cells.append({
        'cell_type': 'markdown',
        'metadata': {},
        'source': [
            '# 🔄 Camada Prata - Transformação e Relacionamento\n',
            '\n',
            'Este notebook transforma dados brutos da camada Bronze em estruturas relacionadas prontas para análise.\n',
            '\n',
            '## Processos:\n',
            '1. Leitura dos dados Bronze\n',
            '2. Tratamento e limpeza\n',
            '3. Criação de dimensões e fatos\n',
            '4. Relacionamento entre tabelas'
        ]
    })
    
    # Configurações e funções
    config_code = """import pandas as pd
from minio import Minio
from minio.error import S3Error
import io
from datetime import datetime
import pyarrow.parquet as pq

# Configurações
MINIO_SERVER_URL = "ch8ai-minio.l6zv5a.easypanel.host"
MINIO_ROOT_USER = "admin"
MINIO_ROOT_PASSWORD = "1q2w3e4r"
BUCKET_NAME = "govbr"

# Cliente MinIO
minio_client = Minio(
    MINIO_SERVER_URL,
    access_key=MINIO_ROOT_USER,
    secret_key=MINIO_ROOT_PASSWORD,
    secure=True
)

def read_from_bronze(source, dataset_name, partition_date=None):
    \"\"\"Lê DataFrame da camada Bronze\"\"\"
    if partition_date is None:
        # Buscar a partição mais recente
        prefix = f"bronze/{source}/{dataset_name}/"
        objects = list(minio_client.list_objects(BUCKET_NAME, prefix=prefix, recursive=True))
        if not objects:
            return None
        
        # Pegar o mais recente
        latest = max(objects, key=lambda x: x.last_modified)
        object_name = latest.object_name
    else:
        object_name = f"bronze/{source}/{dataset_name}/dt={partition_date}/data.parquet"
    
    try:
        response = minio_client.get_object(BUCKET_NAME, object_name)
        df = pd.read_parquet(io.BytesIO(response.read()))
        response.close()
        response.release_conn()
        print(f"✅ Lido Bronze: {object_name} ({len(df)} registros)")
        return df
    except Exception as e:
        print(f"❌ Erro ao ler {object_name}: {e}")
        return None

def save_to_prata(df, dataset_name, partition_date=None):
    \"\"\"Salva DataFrame na camada Prata em formato Parquet\"\"\"
    if partition_date is None:
        partition_date = datetime.now().strftime('%Y%m%d')
    
    object_name = f"prata/{dataset_name}/dt={partition_date}/data.parquet"
    
    try:
        buffer = io.BytesIO()
        df.to_parquet(buffer, index=False, engine='pyarrow', compression='snappy')
        buffer.seek(0)
        
        minio_client.put_object(
            BUCKET_NAME,
            object_name,
            buffer,
            length=buffer.getbuffer().nbytes,
            content_type='application/octet-stream'
        )
        
        print(f"✅ Prata: {object_name} ({len(df)} registros, {buffer.getbuffer().nbytes/1024:.2f} KB)")
        return True
    except Exception as e:
        print(f"❌ Erro ao salvar {object_name}: {e}")
        return False

print("=" * 80)
print("CAMADA PRATA - TRANSFORMAÇÃO E RELACIONAMENTO")
print("=" * 80)
"""
    
    cells.append({
        'cell_type': 'code',
        'metadata': {},
        'source': config_code.split('\n')
    })
    
    # Seção 1: Ler Bronze
    cells.append({
        'cell_type': 'markdown',
        'metadata': {},
        'source': ['## [1/4] Carregando dados da camada Bronze']
    })
    
    ler_bronze_code = """# Ler dados da Bronze
print("\\n[1/4] Carregando dados da camada Bronze...")

df_municipios = read_from_bronze('ibge', 'municipios')
df_estados = read_from_bronze('ibge', 'estados')
df_orgaos = read_from_bronze('portal_transparencia', 'orgaos_siafi')
df_bpc = read_from_bronze('portal_transparencia', 'bpc_municipios')
df_populacao = read_from_bronze('ibge', 'populacao_estados')

if df_municipios is None or df_estados is None:
    print("❌ Erro: Dados essenciais não encontrados na Bronze")
    raise Exception("Dados Bronze insuficientes")
"""
    
    cells.append({
        'cell_type': 'code',
        'metadata': {},
        'source': ler_bronze_code.split('\n')
    })
    
    # Seção 2: Tratamento
    cells.append({
        'cell_type': 'markdown',
        'metadata': {},
        'source': ['## [2/4] Tratando e limpando dados']
    })
    
    tratamento_code = """# Tratamento e Limpeza de Dados
print("\\n[2/4] Tratando e limpando dados...")

# Normalizar nomes de colunas
df_municipios.columns = df_municipios.columns.str.lower().str.strip()
df_estados.columns = df_estados.columns.str.lower().str.strip()

# Remover duplicatas
df_municipios = df_municipios.drop_duplicates(subset=['codigo_ibge'])
df_estados = df_estados.drop_duplicates(subset=['uf_id'])

# Padronizar tipos de dados
df_municipios['codigo_ibge'] = df_municipios['codigo_ibge'].astype(str)
if df_bpc is not None and 'codigo_ibge' in df_bpc.columns:
    df_bpc['codigo_ibge'] = df_bpc['codigo_ibge'].astype(str)
"""
    
    cells.append({
        'cell_type': 'code',
        'metadata': {},
        'source': tratamento_code.split('\n')
    })
    
    # Seção 3: Dimensões e relacionamentos
    cells.append({
        'cell_type': 'markdown',
        'metadata': {},
        'source': ['## [3/4] Criando dimensões e relacionamentos']
    })
    
    dimensoes_code = """# Criar dimensão de municípios enriquecida
print("\\n[3/4] Criando dimensões e relacionamentos...")

# Selecionar apenas colunas que existem em df_estados
cols_estados = ['uf_id', 'uf_sigla']
if 'uf_nome' in df_estados.columns:
    cols_estados.append('uf_nome')
if 'regiao_id' in df_estados.columns:
    cols_estados.append('regiao_id')
if 'regiao_nome' in df_estados.columns:
    cols_estados.append('regiao_nome')

dim_municipios = df_municipios.merge(
    df_estados[cols_estados],
    on='uf_sigla',
    how='left'
).copy()

# Adicionar população por estado aos municípios
if df_populacao is not None:
    dim_municipios = dim_municipios.merge(
        df_populacao[['uf_sigla', 'populacao']],
        on='uf_sigla',
        how='left'
    )

# Criar fato de BPC enriquecido
if df_bpc is not None and len(df_bpc) > 0:
    # Selecionar apenas colunas que existem
    cols_municipios = ['codigo_ibge', 'municipio', 'uf_sigla']
    if 'uf_nome' in dim_municipios.columns:
        cols_municipios.append('uf_nome')
    if 'regiao_nome' in dim_municipios.columns:
        cols_municipios.append('regiao_nome')
    
    fato_bpc = df_bpc.merge(
        dim_municipios[cols_municipios],
        on='codigo_ibge',
        how='left',
        suffixes=('', '_dim')
    ).copy()
    
    # Adicionar métricas calculadas
    fato_bpc['valor_per_capita'] = fato_bpc['valor'] / fato_bpc['quantidade_beneficiados'].replace(0, 1)
    fato_bpc['data_referencia'] = pd.to_datetime(fato_bpc['data_referencia'], errors='coerce')
    fato_bpc['ano'] = fato_bpc['data_referencia'].dt.year
    fato_bpc['mes'] = fato_bpc['data_referencia'].dt.month
    
    # Salvar fato de BPC
    save_to_prata(fato_bpc, 'fato_bpc')
else:
    print("⚠️  Dados de BPC não disponíveis")
    fato_bpc = None

# Criar dimensão de estados agregada
dim_estados = df_estados.copy()
if df_populacao is not None:
    dim_estados = dim_estados.merge(
        df_populacao,
        on=['uf_id', 'uf_sigla'],
        how='left'
    )

# Agregar dados de BPC por estado (se disponível)
if df_bpc is not None and len(df_bpc) > 0:
    if 'valor' in df_bpc.columns and 'quantidade_beneficiados' in df_bpc.columns:
        bpc_por_estado = df_bpc.groupby('uf_sigla').agg({
            'valor': 'sum',
            'quantidade_beneficiados': 'sum'
        }).reset_index()
        
        bpc_por_estado.columns = ['uf_sigla', 'total_valor_bpc', 'total_beneficiados_bpc']
        
        dim_estados = dim_estados.merge(
            bpc_por_estado,
            on='uf_sigla',
            how='left'
        )
        
        # Calcular métricas apenas se populacao existe
        if 'populacao' in dim_estados.columns:
            dim_estados['valor_bpc_per_capita'] = (
                dim_estados['total_valor_bpc'] / dim_estados['populacao'].replace(0, 1)
            )
            dim_estados['percentual_beneficiados'] = (
                dim_estados['total_beneficiados_bpc'] / dim_estados['populacao'].replace(0, 1) * 100
            )

# Salvar dimensões
save_to_prata(dim_municipios, 'dim_municipios')
save_to_prata(dim_estados, 'dim_estados')

# Criar tabela de órgãos tratada
if df_orgaos is not None:
    dim_orgaos = df_orgaos.copy()
    dim_orgaos.columns = dim_orgaos.columns.str.lower().str.strip()
    dim_orgaos = dim_orgaos.drop_duplicates(subset=['codigo'])
    save_to_prata(dim_orgaos, 'dim_orgaos')
"""
    
    cells.append({
        'cell_type': 'code',
        'metadata': {},
        'source': dimensoes_code.split('\n')
    })
    
    # Seção 4: Resumo
    cells.append({
        'cell_type': 'markdown',
        'metadata': {},
        'source': ['## [4/4] Resumo da Transformação']
    })
    
    resumo_code = """# Criar resumo de transformações
print("\\n[4/4] Criando resumo de transformações...")

print("\\n" + "=" * 80)
print("RESUMO DA TRANSFORMAÇÃO PRATA")
print("=" * 80)
print(f"\\n✅ Municípios tratados: {len(dim_municipios)}")
print(f"✅ Estados tratados: {len(dim_estados)}")
if fato_bpc is not None:
    print(f"✅ Registros BPC tratados: {len(fato_bpc)}")

# Listar arquivos Prata
objects = minio_client.list_objects(BUCKET_NAME, prefix="prata/", recursive=True)
prata_files = list(objects)

print(f"\\nTotal de arquivos na camada Prata: {len(prata_files)}")
total_size = 0
for obj in prata_files:
    size_kb = obj.size / 1024
    total_size += obj.size
    print(f"  📁 {obj.object_name} ({size_kb:.2f} KB)")

print(f"\\nTamanho total: {total_size/1024:.2f} KB")
print("\\n✅ Transformação Prata concluída!")
"""
    
    cells.append({
        'cell_type': 'code',
        'metadata': {},
        'source': resumo_code.split('\n')
    })
    
    notebook = {
        'cells': cells,
        'metadata': {
            'kernelspec': {'display_name': 'Python 3', 'language': 'python', 'name': 'python3'},
            'language_info': {'name': 'python', 'version': '3.10.0'}
        },
        'nbformat': 4,
        'nbformat_minor': 4
    }
    
    with open('NOTEBOOK_02_PRATA_TRANSFORMACAO.ipynb', 'w', encoding='utf-8') as f:
        json.dump(notebook, f, indent=2, ensure_ascii=False)
    
    print("✅ Notebook Prata melhorado criado")

def criar_notebook_ouro_melhorado():
    """Cria notebook Ouro com estrutura melhorada"""
    
    with open('03_ouro_enriquecimento.py', 'r') as f:
        script = f.read()
    
    cells = []
    
    # Título
    cells.append({
        'cell_type': 'markdown',
        'metadata': {},
        'source': [
            '# 🏆 Camada Ouro - Enriquecimento e Dados Finais\n',
            '\n',
            'Este notebook enriquece dados da camada Prata com métricas avançadas e análises prontas para consumo.\n',
            '\n',
            '## Processos:\n',
            '1. Leitura dos dados Prata\n',
            '2. Enriquecimento com métricas\n',
            '3. Criação de rankings e classificações\n',
            '4. Agregações regionais'
        ]
    })
    
    # Configurações e funções
    config_code = """import pandas as pd
from minio import Minio
from minio.error import S3Error
import io
from datetime import datetime

# Configurações
MINIO_SERVER_URL = "ch8ai-minio.l6zv5a.easypanel.host"
MINIO_ROOT_USER = "admin"
MINIO_ROOT_PASSWORD = "1q2w3e4r"
BUCKET_NAME = "govbr"

# Cliente MinIO
minio_client = Minio(
    MINIO_SERVER_URL,
    access_key=MINIO_ROOT_USER,
    secret_key=MINIO_ROOT_PASSWORD,
    secure=True
)

def read_from_prata(dataset_name, partition_date=None):
    \"\"\"Lê DataFrame da camada Prata\"\"\"
    if partition_date is None:
        # Buscar a partição mais recente
        prefix = f"prata/{dataset_name}/"
        objects = list(minio_client.list_objects(BUCKET_NAME, prefix=prefix, recursive=True))
        if not objects:
            return None
        
        # Pegar o mais recente
        latest = max(objects, key=lambda x: x.last_modified)
        object_name = latest.object_name
    else:
        object_name = f"prata/{dataset_name}/dt={partition_date}/data.parquet"
    
    try:
        response = minio_client.get_object(BUCKET_NAME, object_name)
        df = pd.read_parquet(io.BytesIO(response.read()))
        response.close()
        response.release_conn()
        print(f"✅ Lido Prata: {object_name} ({len(df)} registros)")
        return df
    except Exception as e:
        print(f"❌ Erro ao ler {object_name}: {e}")
        return None

def save_to_ouro(df, dataset_name, partition_date=None):
    \"\"\"Salva DataFrame na camada Ouro em formato Parquet\"\"\"
    if partition_date is None:
        partition_date = datetime.now().strftime('%Y%m%d')
    
    object_name = f"ouro/{dataset_name}/dt={partition_date}/data.parquet"
    
    try:
        buffer = io.BytesIO()
        df.to_parquet(buffer, index=False, engine='pyarrow', compression='snappy')
        buffer.seek(0)
        
        minio_client.put_object(
            BUCKET_NAME,
            object_name,
            buffer,
            length=buffer.getbuffer().nbytes,
            content_type='application/octet-stream'
        )
        
        print(f"✅ Ouro: {object_name} ({len(df)} registros, {buffer.getbuffer().nbytes/1024:.2f} KB)")
        return True
    except Exception as e:
        print(f"❌ Erro ao salvar {object_name}: {e}")
        return False

print("=" * 80)
print("CAMADA OURO - ENRIQUECIMENTO E DADOS FINAIS")
print("=" * 80)
"""
    
    cells.append({
        'cell_type': 'code',
        'metadata': {},
        'source': config_code.split('\n')
    })
    
    # Seção 1: Ler Prata
    cells.append({
        'cell_type': 'markdown',
        'metadata': {},
        'source': ['## [1/5] Carregando dados da camada Prata']
    })
    
    ler_prata_code = """# Ler dados da Prata
print("\\n[1/5] Carregando dados da camada Prata...")

dim_municipios = read_from_prata('dim_municipios')
dim_estados = read_from_prata('dim_estados')
fato_bpc = read_from_prata('fato_bpc')
dim_orgaos = read_from_prata('dim_orgaos')

if dim_municipios is None or dim_estados is None:
    print("❌ Erro: Dados essenciais não encontrados na Prata")
    raise Exception("Dados Prata insuficientes")
"""
    
    cells.append({
        'cell_type': 'code',
        'metadata': {},
        'source': ler_prata_code.split('\n')
    })
    
    # Seção 2: Enriquecer Municípios
    cells.append({
        'cell_type': 'markdown',
        'metadata': {},
        'source': ['## [2/5] Enriquecendo dimensão de municípios']
    })
    
    enriquecer_municipios_code = """# Enriquecer Dimensão de Municípios
print("\\n[2/5] Enriquecendo dimensão de municípios...")

ouro_municipios = dim_municipios.copy()

# Adicionar classificações
if 'populacao' in ouro_municipios.columns:
    ouro_municipios['classificacao_populacao'] = pd.cut(
        ouro_municipios['populacao'],
        bins=[0, 5000, 20000, 100000, 500000, float('inf')],
        labels=['Muito Pequeno', 'Pequeno', 'Médio', 'Grande', 'Muito Grande']
    )

# Adicionar indicadores regionais
if 'regiao_nome' in ouro_municipios.columns:
    ouro_municipios['regiao_sigla'] = ouro_municipios['regiao_nome'].map({
        'Norte': 'N',
        'Nordeste': 'NE',
        'Centro-Oeste': 'CO',
        'Sudeste': 'SE',
        'Sul': 'S'
    })

# Adicionar timestamp de processamento
ouro_municipios['data_processamento'] = datetime.now()
ouro_municipios['versao_dados'] = '1.0'

save_to_ouro(ouro_municipios, 'municipios_enriquecidos')
"""
    
    cells.append({
        'cell_type': 'code',
        'metadata': {},
        'source': enriquecer_municipios_code.split('\n')
    })
    
    # Seção 3: Enriquecer Estados
    cells.append({
        'cell_type': 'markdown',
        'metadata': {},
        'source': ['## [3/5] Enriquecendo dimensão de estados']
    })
    
    enriquecer_estados_code = """# Enriquecer Dimensão de Estados
print("\\n[3/5] Enriquecendo dimensão de estados...")

ouro_estados = dim_estados.copy()

# Adicionar métricas avançadas
if 'populacao' in ouro_estados.columns:
    ouro_estados['classificacao_populacao'] = pd.cut(
        ouro_estados['populacao'],
        bins=[0, 5000000, 10000000, 20000000, float('inf')],
        labels=['Pequeno', 'Médio', 'Grande', 'Muito Grande']
    )
    
    # Densidade populacional (estimada)
    ouro_estados['densidade_populacional'] = ouro_estados['populacao'] / 1000  # Simplificado

# Adicionar indicadores de BPC
if 'total_valor_bpc' in ouro_estados.columns:
    ouro_estados['indicador_bpc_alto'] = ouro_estados['total_valor_bpc'] > ouro_estados['total_valor_bpc'].median()
    ouro_estados['ranking_valor_bpc'] = ouro_estados['total_valor_bpc'].rank(ascending=False, method='dense')

# Adicionar timestamp
ouro_estados['data_processamento'] = datetime.now()
ouro_estados['versao_dados'] = '1.0'

save_to_ouro(ouro_estados, 'estados_enriquecidos')
"""
    
    cells.append({
        'cell_type': 'code',
        'metadata': {},
        'source': enriquecer_estados_code.split('\n')
    })
    
    # Seção 4: Fato BPC Enriquecido
    cells.append({
        'cell_type': 'markdown',
        'metadata': {},
        'source': ['## [4/5] Criando fato BPC enriquecido']
    })
    
    fato_bpc_code = """# Criar Fato BPC Enriquecido
print("\\n[4/5] Criando fato BPC enriquecido...")

if fato_bpc is not None and len(fato_bpc) > 0:
    ouro_fato_bpc = fato_bpc.copy()
    
    # Adicionar métricas temporais
    if 'mes' in ouro_fato_bpc.columns:
        ouro_fato_bpc['trimestre'] = ouro_fato_bpc['mes'].apply(
            lambda x: f"T{(x-1)//3 + 1}" if pd.notna(x) else None
        )
        ouro_fato_bpc['semestre'] = ouro_fato_bpc['mes'].apply(
            lambda x: 'S1' if pd.notna(x) and x <= 6 else ('S2' if pd.notna(x) else None)
        )
    
    # Adicionar classificações de valor
    if 'valor' in ouro_fato_bpc.columns:
        ouro_fato_bpc['faixa_valor'] = pd.cut(
            ouro_fato_bpc['valor'],
            bins=[0, 100000, 1000000, 10000000, float('inf')],
            labels=['Baixo', 'Médio', 'Alto', 'Muito Alto']
        )
    
    # Adicionar classificações de beneficiados
    if 'quantidade_beneficiados' in ouro_fato_bpc.columns:
        ouro_fato_bpc['faixa_beneficiados'] = pd.cut(
            ouro_fato_bpc['quantidade_beneficiados'],
            bins=[0, 100, 1000, 10000, float('inf')],
            labels=['Poucos', 'Moderado', 'Muitos', 'Muitíssimos']
        )
    
    # Adicionar indicadores calculados
    if 'valor_per_capita' in ouro_fato_bpc.columns:
        median_valor = ouro_fato_bpc['valor_per_capita'].median()
        if pd.notna(median_valor) and median_valor != 0:
            ouro_fato_bpc['indicador_eficiencia'] = (
                ouro_fato_bpc['valor_per_capita'] / median_valor
            )
    
    # Adicionar timestamp
    ouro_fato_bpc['data_processamento'] = datetime.now()
    ouro_fato_bpc['versao_dados'] = '1.0'
    
    save_to_ouro(ouro_fato_bpc, 'bpc_analytics')
else:
    print("⚠️  Dados de BPC não disponíveis para enriquecimento")
    ouro_fato_bpc = None
"""
    
    cells.append({
        'cell_type': 'code',
        'metadata': {},
        'source': fato_bpc_code.split('\n')
    })
    
    # Seção 5: Agregações
    cells.append({
        'cell_type': 'markdown',
        'metadata': {},
        'source': ['## [5/5] Criando tabelas agregadas para análise']
    })
    
    agregacoes_code = """# Criar Tabelas de Agregação e Análise
print("\\n[5/5] Criando tabelas agregadas para análise...")

# Agregação por Região
if fato_bpc is not None and len(fato_bpc) > 0:
    if 'regiao_nome' in fato_bpc.columns:
        agregacao_regiao = fato_bpc.groupby('regiao_nome').agg({
            'valor': ['sum', 'mean', 'median'],
            'quantidade_beneficiados': ['sum', 'mean'],
            'valor_per_capita': 'mean'
        }).reset_index()
    
        agregacao_regiao.columns = [
            'regiao_nome',
            'total_valor',
            'media_valor',
            'mediana_valor',
            'total_beneficiados',
            'media_beneficiados',
            'media_valor_per_capita'
        ]
        
        agregacao_regiao['data_processamento'] = datetime.now()
        agregacao_regiao['versao_dados'] = '1.0'
        
        save_to_ouro(agregacao_regiao, 'agregacoes_regionais')
    
    # Agregação por Estado
    if 'uf_sigla' in fato_bpc.columns:
        groupby_cols = ['uf_sigla']
        if 'uf_nome' in fato_bpc.columns:
            groupby_cols.append('uf_nome')
        
        agregacao_estado = fato_bpc.groupby(groupby_cols).agg({
            'valor': ['sum', 'mean'],
            'quantidade_beneficiados': ['sum', 'mean'],
            'valor_per_capita': 'mean'
        }).reset_index()
    
        col_names = ['uf_sigla']
        if 'uf_nome' in fato_bpc.columns:
            col_names.append('uf_nome')
        col_names.extend(['total_valor', 'media_valor', 'total_beneficiados', 'media_beneficiados', 'media_valor_per_capita'])
        
        agregacao_estado.columns = col_names
        
        agregacao_estado['data_processamento'] = datetime.now()
        agregacao_estado['versao_dados'] = '1.0'
        
        save_to_ouro(agregacao_estado, 'agregacoes_estados')
    
    # Top 10 municípios por valor
    if 'valor' in fato_bpc.columns:
        top_cols = ['uf_sigla', 'valor']
        if 'nome_municipio' in fato_bpc.columns:
            top_cols.insert(0, 'nome_municipio')
        if 'quantidade_beneficiados' in fato_bpc.columns:
            top_cols.append('quantidade_beneficiados')
        
        top_municipios_valor = (
            fato_bpc.nlargest(10, 'valor')[top_cols]
            .copy()
        )
        top_municipios_valor['data_processamento'] = datetime.now()
        top_municipios_valor['versao_dados'] = '1.0'
        
        save_to_ouro(top_municipios_valor, 'rankings')
"""
    
    cells.append({
        'cell_type': 'code',
        'metadata': {},
        'source': agregacoes_code.split('\n')
    })
    
    # Resumo
    cells.append({
        'cell_type': 'markdown',
        'metadata': {},
        'source': ['## Resumo do Enriquecimento']
    })
    
    resumo_code = """# Resumo do Enriquecimento
print("\\n" + "=" * 80)
print("RESUMO DO ENRIQUECIMENTO OURO")
print("=" * 80)
print(f"\\n✅ Municípios enriquecidos: {len(ouro_municipios)}")
print(f"✅ Estados enriquecidos: {len(ouro_estados)}")
if ouro_fato_bpc is not None:
    print(f"✅ Registros BPC enriquecidos: {len(ouro_fato_bpc)}")

# Listar arquivos Ouro
objects = minio_client.list_objects(BUCKET_NAME, prefix="ouro/", recursive=True)
ouro_files = list(objects)

print(f"\\nTotal de arquivos na camada Ouro: {len(ouro_files)}")
total_size = 0
for obj in ouro_files:
    size_kb = obj.size / 1024
    total_size += obj.size
    print(f"  📁 {obj.object_name} ({size_kb:.2f} KB)")

print(f"\\nTamanho total: {total_size/1024:.2f} KB")
print("\\n✅ Enriquecimento Ouro concluído!")
"""
    
    cells.append({
        'cell_type': 'code',
        'metadata': {},
        'source': resumo_code.split('\n')
    })
    
    notebook = {
        'cells': cells,
        'metadata': {
            'kernelspec': {'display_name': 'Python 3', 'language': 'python', 'name': 'python3'},
            'language_info': {'name': 'python', 'version': '3.10.0'}
        },
        'nbformat': 4,
        'nbformat_minor': 4
    }
    
    with open('NOTEBOOK_03_OURO_ENRIQUECIMENTO.ipynb', 'w', encoding='utf-8') as f:
        json.dump(notebook, f, indent=2, ensure_ascii=False)
    
    print("✅ Notebook Ouro melhorado criado")

if __name__ == '__main__':
    print("=" * 80)
    print("MELHORANDO NOTEBOOKS DE INGESTÃO")
    print("=" * 80)
    
    criar_notebook_bronze_melhorado()
    criar_notebook_prata_melhorado()
    criar_notebook_ouro_melhorado()
    
    print("\n✅ Todos os notebooks melhorados criados com sucesso!")
