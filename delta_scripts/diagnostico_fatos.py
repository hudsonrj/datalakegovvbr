#!/usr/bin/env python3
"""
Script de diagnóstico para verificar dados Bronze e Prata
"""

import sys
import os

# Adicionar caminho do trabalho
sys.path.insert(0, '/home/jovyan/work')

from pyspark.sql import SparkSession
from minio import Minio
from minio.error import S3Error
import pandas as pd

# Configurações MinIO
MINIO_ENDPOINT = "minio:9000"
MINIO_ACCESS_KEY = "minioadmin"
MINIO_SECRET_KEY = "minioadmin"
BUCKET_NAME = "govbr"

# Inicializar cliente MinIO
minio_client = Minio(
    MINIO_ENDPOINT,
    access_key=MINIO_ACCESS_KEY,
    secret_key=MINIO_SECRET_KEY,
    secure=False
)

print("=" * 80)
print("🔍 DIAGNÓSTICO DE DADOS BRONZE E PRATA")
print("=" * 80)

# 1. Verificar dados Bronze diretamente no MinIO
print("\n[1/3] Verificando dados Bronze no MinIO...")
bronze_datasets = {
    'bpc_municipios': 'bronze/portal_transparencia/bpc_municipios/',
    'bolsa_familia_municipios': 'bronze/portal_transparencia/bolsa_familia_municipios/',
    'populacao_estados': 'bronze/ibge/populacao_estados/'
}

bronze_status = {}
for nome, prefixo in bronze_datasets.items():
    try:
        objects = list(minio_client.list_objects(BUCKET_NAME, prefix=prefixo, recursive=True))
        if objects:
            bronze_status[nome] = {
                'status': '✅ Disponível',
                'arquivos': len(objects),
                'tamanho_total': sum(obj.size for obj in objects)
            }
        else:
            bronze_status[nome] = {
                'status': '❌ Não encontrado',
                'arquivos': 0
            }
    except Exception as e:
        bronze_status[nome] = {
            'status': f'❌ Erro: {str(e)}',
            'arquivos': 0
        }

for nome, info in bronze_status.items():
    print(f"  {nome}: {info['status']}")
    if info['arquivos'] > 0:
        print(f"    - Arquivos: {info['arquivos']}")
        print(f"    - Tamanho: {info['tamanho_total'] / 1024:.2f} KB")

# 2. Verificar dados Prata diretamente no MinIO
print("\n[2/3] Verificando dados Prata no MinIO...")
prata_datasets = {
    'fato_bpc': 'prata/fato_bpc/',
    'fato_bolsa_familia': 'prata/fato_bolsa_familia/'
}

prata_status = {}
for nome, prefixo in prata_datasets.items():
    try:
        objects = list(minio_client.list_objects(BUCKET_NAME, prefix=prefixo, recursive=True))
        if objects:
            prata_status[nome] = {
                'status': '✅ Disponível',
                'arquivos': len(objects),
                'tamanho_total': sum(obj.size for obj in objects)
            }
        else:
            prata_status[nome] = {
                'status': '❌ Não encontrado',
                'arquivos': 0
            }
    except Exception as e:
        prata_status[nome] = {
            'status': f'❌ Erro: {str(e)}',
            'arquivos': 0
        }

for nome, info in prata_status.items():
    print(f"  {nome}: {info['status']}")
    if info['arquivos'] > 0:
        print(f"    - Arquivos: {info['arquivos']}")
        print(f"    - Tamanho: {info['tamanho_total'] / 1024:.2f} KB")

# 3. Tentar ler dados via Spark (se disponível)
print("\n[3/3] Tentando ler dados via Spark...")
try:
    # Tentar inicializar Spark
    try:
        exec(open('/home/jovyan/work/spark_com_jars_manual.py').read())
        spark_available = True
    except:
        try:
            exec(open('/home/jovyan/work/inicializar_spark.py').read())
            spark_available = True
        except:
            spark_available = False
            print("  ⚠️  Spark não disponível, pulando verificação via Spark")
    
    if spark_available and 'spark' in globals():
        spark = globals()['spark']
        
        # Verificar BPC Bronze
        try:
            df_bpc_bronze = spark.read.parquet("s3a://govbr/bronze/portal_transparencia/bpc_municipios/")
            count = df_bpc_bronze.count()
            print(f"  ✅ BPC Bronze (Spark): {count} registros")
        except Exception as e:
            print(f"  ❌ BPC Bronze (Spark): {str(e)[:100]}")
        
        # Verificar Bolsa Família Bronze
        try:
            df_bf_bronze = spark.read.parquet("s3a://govbr/bronze/portal_transparencia/bolsa_familia_municipios/")
            count = df_bf_bronze.count()
            print(f"  ✅ Bolsa Família Bronze (Spark): {count} registros")
        except Exception as e:
            print(f"  ❌ Bolsa Família Bronze (Spark): {str(e)[:100]}")
        
        # Verificar População Bronze
        try:
            df_pop_bronze = spark.read.parquet("s3a://govbr/bronze/ibge/populacao_estados/")
            count = df_pop_bronze.count()
            print(f"  ✅ População Bronze (Spark): {count} registros")
        except Exception as e:
            print(f"  ❌ População Bronze (Spark): {str(e)[:100]}")
        
        # Verificar Fato BPC Prata
        try:
            df_bpc_prata = spark.read.parquet("s3a://govbr/prata/fato_bpc/")
            count = df_bpc_prata.count()
            print(f"  ✅ Fato BPC Prata (Spark): {count} registros")
        except Exception as e:
            print(f"  ❌ Fato BPC Prata (Spark): {str(e)[:100]}")
        
        # Verificar Fato Bolsa Família Prata
        try:
            df_bf_prata = spark.read.parquet("s3a://govbr/prata/fato_bolsa_familia/")
            count = df_bf_prata.count()
            print(f"  ✅ Fato Bolsa Família Prata (Spark): {count} registros")
        except Exception as e:
            print(f"  ❌ Fato Bolsa Família Prata (Spark): {str(e)[:100]}")
    
except Exception as e:
    print(f"  ⚠️  Erro ao verificar via Spark: {e}")

print("\n" + "=" * 80)
print("💡 RECOMENDAÇÕES")
print("=" * 80)

if bronze_status.get('bpc_municipios', {}).get('arquivos', 0) == 0:
    print("1. Execute a ingestão Bronze para coletar dados de BPC:")
    print("   exec(open('/home/jovyan/work/01_bronze_ingestion.py').read())")

if bronze_status.get('bolsa_familia_municipios', {}).get('arquivos', 0) == 0:
    print("2. Execute a ingestão Bronze para coletar dados de Bolsa Família:")
    print("   exec(open('/home/jovyan/work/01_bronze_ingestion.py').read())")

if bronze_status.get('populacao_estados', {}).get('arquivos', 0) == 0:
    print("3. Execute a ingestão Bronze para coletar dados de população:")
    print("   exec(open('/home/jovyan/work/01_bronze_ingestion.py').read())")

if bronze_status.get('bpc_municipios', {}).get('arquivos', 0) > 0 and prata_status.get('fato_bpc', {}).get('arquivos', 0) == 0:
    print("4. Execute a transformação Prata para processar dados de BPC:")
    print("   exec(open('/home/jovyan/work/02_prata_transformacao.py').read())")

if bronze_status.get('bolsa_familia_municipios', {}).get('arquivos', 0) > 0 and prata_status.get('fato_bolsa_familia', {}).get('arquivos', 0) == 0:
    print("5. Execute a transformação Prata para processar dados de Bolsa Família:")
    print("   exec(open('/home/jovyan/work/02_prata_transformacao.py').read())")

print("\n✅ Diagnóstico concluído!")
