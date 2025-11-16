#!/usr/bin/env python3
"""
Script para gerar dados simulados de Bolsa Família quando a API não está disponível
"""

import sys
import os
sys.path.insert(0, '/home/jovyan/work')

import pandas as pd
from minio import Minio
import io
from datetime import datetime
import random

# Configurações MinIO
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

def read_from_bronze(source, dataset_name):
    """Lê DataFrame da camada Bronze"""
    prefix = f"bronze/{source}/{dataset_name}/"
    objects = list(minio_client.list_objects(BUCKET_NAME, prefix=prefix, recursive=True))
    if not objects:
        return None
    
    latest = max(objects, key=lambda x: x.last_modified)
    object_name = latest.object_name
    
    try:
        response = minio_client.get_object(BUCKET_NAME, object_name)
        df = pd.read_parquet(io.BytesIO(response.read()))
        response.close()
        response.release_conn()
        return df
    except Exception as e:
        print(f"Erro ao ler {object_name}: {e}")
        return None

def save_to_bronze(df, dataset_name, source):
    """Salva DataFrame na camada Bronze"""
    from datetime import datetime
    import pyarrow.parquet as pq
    
    dt = datetime.now().strftime("%Y%m%d")
    object_name = f"bronze/{source}/{dataset_name}/dt={dt}/data.parquet"
    
    # Converter para Parquet em memória
    buffer = io.BytesIO()
    df.to_parquet(buffer, index=False, engine='pyarrow')
    buffer.seek(0)
    
    # Upload para MinIO
    try:
        minio_client.put_object(
            BUCKET_NAME,
            object_name,
            buffer,
            length=buffer.getbuffer().nbytes,
            content_type='application/parquet'
        )
        print(f"✅ Salvo: {object_name} ({len(df)} registros)")
    except Exception as e:
        print(f"❌ Erro ao salvar {object_name}: {e}")
        raise

print("=" * 80)
print("📊 GERANDO DADOS SIMULADOS DE BOLSA FAMÍLIA")
print("=" * 80)

# 1. Carregar municípios de SP
print("\n[1/3] Carregando municípios de SP...")
df_municipios = read_from_bronze('ibge', 'municipios')

if df_municipios is None or len(df_municipios) == 0:
    print("❌ Erro: Municípios não encontrados na Bronze")
    print("   Execute primeiro: exec(open('/home/jovyan/work/01_bronze_ingestion.py').read())")
    sys.exit(1)

# Filtrar municípios de SP (ou usar todos se não houver muitos)
df_municipios_sp = df_municipios[df_municipios['uf_sigla'] == 'SP'].head(50)
if len(df_municipios_sp) == 0:
    # Se não houver SP, usar primeiros 50 de qualquer estado
    df_municipios_sp = df_municipios.head(50)

print(f"✅ {len(df_municipios_sp)} municípios carregados")

# 2. Gerar dados simulados
print("\n[2/3] Gerando dados simulados...")

# Fixar seed para reprodutibilidade
random.seed(42)

bolsa_familia_simulado = []

for idx, row in df_municipios_sp.iterrows():
    codigo_ibge = str(row['codigo_ibge'])
    nome_municipio = row['municipio']
    uf_sigla = row['uf_sigla']
    
    # Simular dados realistas
    # População estimada do município (baseado no índice para variar)
    base_populacao = random.randint(10000, 800000)
    
    # Percentual de beneficiários varia entre 8% e 30% da população
    # (valores realistas para Bolsa Família)
    percentual_benef = random.uniform(8, 30)
    quantidade_beneficiarios = int(base_populacao * percentual_benef / 100)
    
    # Valor médio por beneficiário (Bolsa Família varia entre R$ 150 e R$ 600)
    # Valores mais realistas baseados em dados reais
    valor_medio = random.uniform(250, 450)
    valor_total = quantidade_beneficiarios * valor_medio
    
    bolsa_familia_simulado.append({
        'id': f"BF_{codigo_ibge}_{202412}",
        'data_referencia': '2024-12-01',
        'codigo_ibge': codigo_ibge,
        'nome_municipio': nome_municipio,
        'uf_sigla': uf_sigla,
        'uf_nome': None,
        'regiao_nome': None,
        'valor_total': round(valor_total, 2),
        'quantidade_beneficiarios': quantidade_beneficiarios
    })

if bolsa_familia_simulado:
    df_bolsa_familia = pd.DataFrame(bolsa_familia_simulado)
    
    # 3. Salvar na Bronze
    print("\n[3/3] Salvando dados na camada Bronze...")
    save_to_bronze(df_bolsa_familia, 'bolsa_familia_municipios', 'portal_transparencia')
    
    print("\n" + "=" * 80)
    print("✅ DADOS SIMULADOS GERADOS COM SUCESSO")
    print("=" * 80)
    print(f"\n📊 Resumo:")
    print(f"   Municípios: {len(df_bolsa_familia)}")
    print(f"   Total de beneficiários: {df_bolsa_familia['quantidade_beneficiarios'].sum():,.0f}")
    print(f"   Valor total: R$ {df_bolsa_familia['valor_total'].sum()/1e6:.2f} milhões")
    print(f"   Valor médio por beneficiário: R$ {df_bolsa_familia['valor_total'].sum() / df_bolsa_familia['quantidade_beneficiarios'].sum():.2f}")
    print(f"   % médio de beneficiários: {df_bolsa_familia['quantidade_beneficiarios'].mean() / (df_bolsa_familia['quantidade_beneficiarios'].sum() / len(df_bolsa_familia)):.2f}%")
    
    print("\n💡 Próximos passos:")
    print("   1. Execute a transformação Prata:")
    print("      exec(open('/home/jovyan/work/02_prata_transformacao.py').read())")
    print("   2. Execute o teste completo com gráficos:")
    print("      exec(open('/home/jovyan/work/teste_completo_com_graficos.py').read())")
else:
    print("❌ Erro ao gerar dados simulados")
