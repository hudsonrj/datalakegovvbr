#!/usr/bin/env python3
"""
CAMADA PRATA - Transformação e Relacionamento de Dados
Trata dados brutos da camada Bronze, relaciona tabelas e cria estruturas prontas para análise
"""

import pandas as pd
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
    """Lê DataFrame da camada Bronze"""
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
    """Salva DataFrame na camada Prata em formato Parquet"""
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

# 1. Ler dados da Bronze
print("\n[1/4] Carregando dados da camada Bronze...")

df_municipios = read_from_bronze('ibge', 'municipios')
df_estados = read_from_bronze('ibge', 'estados')
df_orgaos = read_from_bronze('portal_transparencia', 'orgaos_siafi')
df_bpc = read_from_bronze('portal_transparencia', 'bpc_municipios')
df_bolsa_familia = read_from_bronze('portal_transparencia', 'bolsa_familia_municipios')
df_populacao_estados = read_from_bronze('ibge', 'populacao_estados')
df_populacao_municipios = read_from_bronze('ibge', 'populacao_municipios')

# Debug: mostrar status dos dados carregados
print("\n📊 Status dos dados Bronze carregados:")
print(f"  - Municípios: {'✅' if df_municipios is not None and len(df_municipios) > 0 else '❌'} ({len(df_municipios) if df_municipios is not None else 0} registros)")
print(f"  - Estados: {'✅' if df_estados is not None and len(df_estados) > 0 else '❌'} ({len(df_estados) if df_estados is not None else 0} registros)")
print(f"  - Órgãos: {'✅' if df_orgaos is not None and len(df_orgaos) > 0 else '❌'} ({len(df_orgaos) if df_orgaos is not None else 0} registros)")
print(f"  - BPC: {'✅' if df_bpc is not None and len(df_bpc) > 0 else '❌'} ({len(df_bpc) if df_bpc is not None else 0} registros)")
print(f"  - Bolsa Família: {'✅' if df_bolsa_familia is not None and len(df_bolsa_familia) > 0 else '❌'} ({len(df_bolsa_familia) if df_bolsa_familia is not None else 0} registros)")
print(f"  - População Estados: {'✅' if df_populacao_estados is not None and len(df_populacao_estados) > 0 else '❌'} ({len(df_populacao_estados) if df_populacao_estados is not None else 0} registros)")
print(f"  - População Municípios: {'✅' if df_populacao_municipios is not None and len(df_populacao_municipios) > 0 else '❌'} ({len(df_populacao_municipios) if df_populacao_municipios is not None else 0} registros)")

if df_municipios is None or df_estados is None:
    print("❌ Erro: Dados essenciais não encontrados na Bronze")
    exit(1)

# 2. Tratamento e Limpeza de Dados
print("\n[2/4] Tratando e limpando dados...")

# Normalizar nomes de colunas
df_municipios.columns = df_municipios.columns.str.lower().str.strip()
df_estados.columns = df_estados.columns.str.lower().str.strip()

# Remover duplicatas
df_municipios = df_municipios.drop_duplicates(subset=['codigo_ibge'])
df_estados = df_estados.drop_duplicates(subset=['uf_id'])

# Padronizar tipos de dados
df_municipios['codigo_ibge'] = df_municipios['codigo_ibge'].astype(str)
if 'codigo_ibge' in df_bpc.columns:
    df_bpc['codigo_ibge'] = df_bpc['codigo_ibge'].astype(str)

# Criar dimensão de municípios enriquecida
print("\n[3/4] Criando dimensões e relacionamentos...")

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

# Adicionar população por município (preferencial) ou por estado (fallback)
if df_populacao_municipios is not None and len(df_populacao_municipios) > 0:
    # Tratar duplicatas: somar população quando há múltiplos registros para mesmo município/ano
    # Pegar o ano mais recente disponível
    df_pop_mun_clean = df_populacao_municipios.copy()
    df_pop_mun_clean['codigo_ibge'] = df_pop_mun_clean['codigo_ibge'].astype(str)
    
    # Agrupar por código_ibge e ano, somando população (caso haja múltiplos registros)
    df_pop_mun_agg = df_pop_mun_clean.groupby(['codigo_ibge', 'ano'])['populacao'].sum().reset_index()
    
    # Pegar o ano mais recente para cada município
    df_pop_mun_latest = df_pop_mun_agg.loc[df_pop_mun_agg.groupby('codigo_ibge')['ano'].idxmax()]
    
    # Merge com municípios
    dim_municipios = dim_municipios.merge(
        df_pop_mun_latest[['codigo_ibge', 'populacao', 'ano']],
        on='codigo_ibge',
        how='left',
        suffixes=('', '_municipio')
    )
    print(f"  ✅ População por município adicionada ({len(df_pop_mun_latest)} municípios)")
elif df_populacao_estados is not None and len(df_populacao_estados) > 0:
    # Fallback: usar população por estado
    dim_municipios = dim_municipios.merge(
        df_populacao_estados[['uf_sigla', 'populacao']],
        on='uf_sigla',
        how='left'
    )
    print(f"  ✅ População por estado adicionada (fallback)")
else:
    print("  ⚠️  Dados de população não disponíveis")

# Criar fato de BPC enriquecido
if df_bpc is not None and len(df_bpc) > 0:
    print(f"\n[Processando BPC] {len(df_bpc)} registros encontrados")
    
    # Normalizar colunas do BPC
    df_bpc.columns = df_bpc.columns.str.lower().str.strip()
    df_bpc['codigo_ibge'] = df_bpc['codigo_ibge'].astype(str)
    
    # Selecionar apenas colunas que existem
    cols_municipios = ['codigo_ibge', 'municipio', 'uf_sigla']
    if 'uf_nome' in dim_municipios.columns:
        cols_municipios.append('uf_nome')
    if 'regiao_nome' in dim_municipios.columns:
        cols_municipios.append('regiao_nome')
    
    try:
        fato_bpc = df_bpc.merge(
            dim_municipios[cols_municipios],
            on='codigo_ibge',
            how='left',
            suffixes=('', '_dim')
        ).copy()
        
        print(f"  ✅ Merge com dim_municipios concluído ({len(fato_bpc)} registros)")
        
        # Adicionar métricas calculadas
        if 'valor' in fato_bpc.columns and 'quantidade_beneficiados' in fato_bpc.columns:
            fato_bpc['valor_per_capita'] = fato_bpc['valor'] / fato_bpc['quantidade_beneficiados'].replace(0, 1)
        
        if 'data_referencia' in fato_bpc.columns:
            fato_bpc['data_referencia'] = pd.to_datetime(fato_bpc['data_referencia'], errors='coerce')
            fato_bpc['ano'] = fato_bpc['data_referencia'].dt.year
            fato_bpc['mes'] = fato_bpc['data_referencia'].dt.month
        
        # Salvar fato de BPC
        save_to_prata(fato_bpc, 'fato_bpc')
        print(f"  ✅ Fato de BPC salvo com sucesso ({len(fato_bpc)} registros)")
    except Exception as e:
        print(f"  ❌ Erro ao processar BPC: {e}")
        import traceback
        traceback.print_exc()
else:
    print("\n⚠️  Dados de BPC não disponíveis na Bronze")
    print("   💡 Execute: exec(open('/home/jovyan/work/01_bronze_ingestion.py').read())")

# Criar fato de Bolsa Família enriquecido
if df_bolsa_familia is not None and len(df_bolsa_familia) > 0:
    print(f"\n[Processando Bolsa Família] {len(df_bolsa_familia)} registros encontrados")
    
    # Normalizar colunas
    df_bolsa_familia.columns = df_bolsa_familia.columns.str.lower().str.strip()
    df_bolsa_familia['codigo_ibge'] = df_bolsa_familia['codigo_ibge'].astype(str)
    
    # Selecionar colunas disponíveis dos municípios
    cols_municipios_bf = ['codigo_ibge', 'municipio', 'uf_sigla']
    if 'uf_nome' in dim_municipios.columns:
        cols_municipios_bf.append('uf_nome')
    if 'regiao_nome' in dim_municipios.columns:
        cols_municipios_bf.append('regiao_nome')
    if 'populacao' in dim_municipios.columns:
        cols_municipios_bf.append('populacao')
    
    try:
        fato_bolsa_familia = df_bolsa_familia.merge(
            dim_municipios[cols_municipios_bf],
            on='codigo_ibge',
            how='left',
            suffixes=('', '_dim')
        ).copy()
        
        print(f"  ✅ Merge com dim_municipios concluído ({len(fato_bolsa_familia)} registros)")
        
        # Adicionar métricas calculadas
        if 'quantidade_beneficiarios' in fato_bolsa_familia.columns and 'populacao' in fato_bolsa_familia.columns:
            # Calcular percentual de beneficiários
            fato_bolsa_familia['percentual_beneficiarios'] = (
                fato_bolsa_familia['quantidade_beneficiarios'] / 
                fato_bolsa_familia['populacao'].replace(0, 1) * 100
            )
            fato_bolsa_familia['percentual_beneficiarios'] = fato_bolsa_familia['percentual_beneficiarios'].fillna(0)
            print(f"  ✅ Percentual de beneficiários calculado")
        
        if 'valor_total' in fato_bolsa_familia.columns and 'quantidade_beneficiarios' in fato_bolsa_familia.columns:
            # Calcular valor médio por beneficiário
            fato_bolsa_familia['valor_medio_beneficiario'] = (
                fato_bolsa_familia['valor_total'] / 
                fato_bolsa_familia['quantidade_beneficiarios'].replace(0, 1)
            )
            print(f"  ✅ Valor médio por beneficiário calculado")
        
        if 'data_referencia' in fato_bolsa_familia.columns:
            fato_bolsa_familia['data_referencia'] = pd.to_datetime(fato_bolsa_familia['data_referencia'], errors='coerce')
            fato_bolsa_familia['ano'] = fato_bolsa_familia['data_referencia'].dt.year
            fato_bolsa_familia['mes'] = fato_bolsa_familia['data_referencia'].dt.month
        
        # Salvar fato de Bolsa Família
        save_to_prata(fato_bolsa_familia, 'fato_bolsa_familia')
        print(f"  ✅ Fato de Bolsa Família salvo com sucesso ({len(fato_bolsa_familia)} registros)")
    except Exception as e:
        print(f"  ❌ Erro ao processar Bolsa Família: {e}")
        import traceback
        traceback.print_exc()
else:
    print("\n⚠️  Dados de Bolsa Família não disponíveis na Bronze")
    print("   💡 Execute: exec(open('/home/jovyan/work/01_bronze_ingestion.py').read())")

# Criar dimensão de estados agregada
dim_estados = df_estados.copy()
if df_populacao_estados is not None:
    dim_estados = dim_estados.merge(
        df_populacao_estados,
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

# 4. Criar resumo de transformações
print("\n[4/4] Criando resumo de transformações...")

resumo_transformacoes = pd.DataFrame({
    'camada': ['Bronze', 'Prata'],
    'tabela': ['Dados Brutos', 'Dados Tratados'],
    'registros_municipios': [len(df_municipios), len(dim_municipios)],
    'registros_estados': [len(df_estados), len(dim_estados)],
    'registros_bpc': [len(df_bpc) if df_bpc is not None else 0, len(fato_bpc) if 'fato_bpc' in locals() and df_bpc is not None else 0],
    'data_processamento': [datetime.now().strftime('%Y-%m-%d %H:%M:%S')] * 2
})

print("\n" + "=" * 80)
print("RESUMO DA TRANSFORMAÇÃO PRATA")
print("=" * 80)
print(f"\n✅ Municípios tratados: {len(dim_municipios)}")
print(f"✅ Estados tratados: {len(dim_estados)}")
if df_bpc is not None and 'fato_bpc' in locals():
    print(f"✅ Registros BPC tratados: {len(fato_bpc)}")
if df_bolsa_familia is not None and 'fato_bolsa_familia' in locals():
    print(f"✅ Registros Bolsa Família tratados: {len(fato_bolsa_familia)}")

# Listar arquivos Prata
objects = minio_client.list_objects(BUCKET_NAME, prefix="prata/", recursive=True)
prata_files = list(objects)

print(f"\nTotal de arquivos na camada Prata: {len(prata_files)}")
total_size = 0
for obj in prata_files:
    size_kb = obj.size / 1024
    total_size += obj.size
    print(f"  📁 {obj.object_name} ({size_kb:.2f} KB)")

print(f"\nTamanho total: {total_size/1024:.2f} KB")
print("\n✅ Transformação Prata concluída!")
