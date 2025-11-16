#!/usr/bin/env python3
"""
CAMADA OURO - Enriquecimento e Dados Finais
Enriquece dados da camada Prata com métricas avançadas e análises prontas para consumo
"""

import pandas as pd
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
    """Lê DataFrame da camada Prata"""
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
    """Salva DataFrame na camada Ouro em formato Parquet"""
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

# 1. Ler dados da Prata
print("\n[1/5] Carregando dados da camada Prata...")

dim_municipios = read_from_prata('dim_municipios')
dim_estados = read_from_prata('dim_estados')
fato_bpc = read_from_prata('fato_bpc')
dim_orgaos = read_from_prata('dim_orgaos')

if dim_municipios is None or dim_estados is None:
    print("❌ Erro: Dados essenciais não encontrados na Prata")
    exit(1)

# 2. Enriquecer Dimensão de Municípios
print("\n[2/5] Enriquecendo dimensão de municípios...")

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

save_to_ouro(ouro_municipios, 'dim_municipios_enriquecida')

# 3. Enriquecer Dimensão de Estados
print("\n[3/5] Enriquecendo dimensão de estados...")

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

save_to_ouro(ouro_estados, 'dim_estados_enriquecida')

# 4. Criar Fato BPC Enriquecido
print("\n[4/5] Criando fato BPC enriquecido...")

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
    
    save_to_ouro(ouro_fato_bpc, 'fato_bpc_enriquecido')
else:
    print("⚠️  Dados de BPC não disponíveis para enriquecimento")

# 5. Criar Tabelas de Agregação e Análise
print("\n[5/5] Criando tabelas agregadas para análise...")

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
        
        save_to_ouro(agregacao_regiao, 'agregacao_bpc_por_regiao')
    
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
        
        save_to_ouro(agregacao_estado, 'agregacao_bpc_por_estado')
    
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
        
        save_to_ouro(top_municipios_valor, 'top_10_municipios_valor_bpc')

# Criar tabela de resumo geral
resumo_geral = pd.DataFrame({
    'metrica': [
        'Total Municípios',
        'Total Estados',
        'Total Registros BPC',
        'Data Processamento'
    ],
    'valor_texto': [
        str(len(ouro_municipios)),
        str(len(ouro_estados)),
        str(len(ouro_fato_bpc) if fato_bpc is not None else 0),
        datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    ],
    'valor_numerico': [
        len(ouro_municipios),
        len(ouro_estados),
        len(ouro_fato_bpc) if fato_bpc is not None else 0,
        None
    ]
})

save_to_ouro(resumo_geral, 'resumo_geral')

print("\n" + "=" * 80)
print("RESUMO DO ENRIQUECIMENTO OURO")
print("=" * 80)
print(f"\n✅ Municípios enriquecidos: {len(ouro_municipios)}")
print(f"✅ Estados enriquecidos: {len(ouro_estados)}")
if fato_bpc is not None:
    print(f"✅ Registros BPC enriquecidos: {len(ouro_fato_bpc)}")

# Listar arquivos Ouro
objects = minio_client.list_objects(BUCKET_NAME, prefix="ouro/", recursive=True)
ouro_files = list(objects)

print(f"\nTotal de arquivos na camada Ouro: {len(ouro_files)}")
total_size = 0
for obj in ouro_files:
    size_kb = obj.size / 1024
    total_size += obj.size
    print(f"  📁 {obj.object_name} ({size_kb:.2f} KB)")

print(f"\nTamanho total: {total_size/1024:.2f} KB")
print("\n✅ Enriquecimento Ouro concluído!")
