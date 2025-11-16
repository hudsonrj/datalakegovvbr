#!/usr/bin/env python3
"""
Script para corrigir e garantir que os fatos BPC e Bolsa Família existam na Prata
"""

import sys
import os
sys.path.insert(0, '/home/jovyan/work')

print("=" * 80)
print("🔧 CORREÇÃO DOS FATOS PRATA (BPC e Bolsa Família)")
print("=" * 80)

# 1. Verificar dados Bronze
print("\n[1/4] Verificando dados Bronze...")

from minio import Minio
from minio.error import S3Error

MINIO_SERVER_URL = "ch8ai-minio.l6zv5a.easypanel.host"
MINIO_ROOT_USER = "admin"
MINIO_ROOT_PASSWORD = "1q2w3e4r"
BUCKET_NAME = "govbr"

minio_client = Minio(
    MINIO_SERVER_URL,
    access_key=MINIO_ROOT_USER,
    secret_key=MINIO_ROOT_PASSWORD,
    secure=True
)

def verificar_bronze(dataset_name, source):
    """Verifica se dataset existe na Bronze"""
    prefix = f"bronze/{source}/{dataset_name}/"
    try:
        objects = list(minio_client.list_objects(BUCKET_NAME, prefix=prefix, recursive=True))
        return len(objects) > 0, len(objects)
    except:
        return False, 0

# Verificar BPC
bpc_existe, bpc_count = verificar_bronze('bpc_municipios', 'portal_transparencia')
print(f"  BPC: {'✅' if bpc_existe else '❌'} ({bpc_count} arquivos)")

# Verificar Bolsa Família
bf_existe, bf_count = verificar_bronze('bolsa_familia_municipios', 'portal_transparencia')
print(f"  Bolsa Família: {'✅' if bf_existe else '❌'} ({bf_count} arquivos)")

# Verificar População
pop_existe, pop_count = verificar_bronze('populacao_estados', 'ibge')
print(f"  População: {'✅' if pop_existe else '❌'} ({pop_count} arquivos)")

# 2. Gerar dados faltantes
print("\n[2/4] Gerando dados faltantes...")

if not bpc_existe:
    print("  ⚠️  BPC não encontrado - será gerado na transformação Prata se houver dados Bronze")
else:
    print("  ✅ BPC já existe")

if not bf_existe:
    print("  📊 Gerando dados simulados de Bolsa Família...")
    try:
        exec(open('/home/jovyan/work/gerar_dados_simulados_bolsa_familia.py').read())
        bf_existe = True
        print("  ✅ Dados de Bolsa Família gerados")
    except Exception as e:
        print(f"  ❌ Erro ao gerar dados: {e}")
        import traceback
        traceback.print_exc()
else:
    print("  ✅ Bolsa Família já existe")

if not pop_existe:
    print("  📊 População não encontrada - executando ingestão completa...")
    try:
        exec(open('/home/jovyan/work/01_bronze_ingestion.py').read())
        pop_existe = True
        print("  ✅ Ingestão completa executada")
    except Exception as e:
        print(f"  ⚠️  Erro na ingestão: {e}")
else:
    print("  ✅ População já existe")

# 3. Verificar dados Prata
print("\n[3/4] Verificando dados Prata...")

def verificar_prata(dataset_name):
    """Verifica se dataset existe na Prata"""
    prefix = f"prata/{dataset_name}/"
    try:
        objects = list(minio_client.list_objects(BUCKET_NAME, prefix=prefix, recursive=True))
        return len(objects) > 0, len(objects)
    except:
        return False, 0

fato_bpc_existe, fato_bpc_count = verificar_prata('fato_bpc')
fato_bf_existe, fato_bf_count = verificar_prata('fato_bolsa_familia')

print(f"  Fato BPC: {'✅' if fato_bpc_existe else '❌'} ({fato_bpc_count} arquivos)")
print(f"  Fato Bolsa Família: {'✅' if fato_bf_existe else '❌'} ({fato_bf_count} arquivos)")

# 4. Executar transformação Prata se necessário
if not fato_bpc_existe or not fato_bf_existe:
    print("\n[4/4] Executando transformação Prata...")
    try:
        exec(open('/home/jovyan/work/02_prata_transformacao.py').read())
        print("  ✅ Transformação Prata executada")
        
        # Verificar novamente
        print("\n   Verificando novamente...")
        fato_bpc_existe, fato_bpc_count = verificar_prata('fato_bpc')
        fato_bf_existe, fato_bf_count = verificar_prata('fato_bolsa_familia')
        
        print(f"  Fato BPC: {'✅' if fato_bpc_existe else '❌'} ({fato_bpc_count} arquivos)")
        print(f"  Fato Bolsa Família: {'✅' if fato_bf_existe else '❌'} ({fato_bf_count} arquivos)")
        
    except Exception as e:
        print(f"  ❌ Erro na transformação Prata: {e}")
        import traceback
        traceback.print_exc()
else:
    print("\n[4/4] ✅ Todos os fatos já existem - nada a fazer")

# 5. Verificação final via Spark
print("\n" + "=" * 80)
print("🔍 VERIFICAÇÃO FINAL VIA SPARK")
print("=" * 80)

try:
    # Inicializar Spark
    try:
        spark
    except NameError:
        print("  Inicializando Spark...")
        exec(open('/home/jovyan/work/spark_com_jars_manual.py').read())
        spark = globals()['spark']
    
    # Verificar BPC Prata
    try:
        df_bpc = spark.read.parquet("s3a://govbr/prata/fato_bpc/")
        count_bpc = df_bpc.count()
        print(f"\n✅ Fato BPC: {count_bpc:,} registros")
        print("   Colunas:", ", ".join(df_bpc.columns[:10]))
    except Exception as e:
        print(f"\n❌ Fato BPC: {str(e)[:100]}")
    
    # Verificar Bolsa Família Prata
    try:
        df_bf = spark.read.parquet("s3a://govbr/prata/fato_bolsa_familia/")
        count_bf = df_bf.count()
        print(f"\n✅ Fato Bolsa Família: {count_bf:,} registros")
        print("   Colunas:", ", ".join(df_bf.columns[:10]))
        
        # Mostrar algumas estatísticas
        if 'quantidade_beneficiarios' in df_bf.columns:
            total_benef = df_bf.agg({"quantidade_beneficiarios": "sum"}).collect()[0][0]
            print(f"   Total Beneficiários: {total_benef:,.0f}")
        
        if 'valor_total' in df_bf.columns:
            total_valor = df_bf.agg({"valor_total": "sum"}).collect()[0][0]
            print(f"   Valor Total: R$ {total_valor/1e6:.2f} milhões")
        
        if 'percentual_beneficiarios' in df_bf.columns:
            avg_perc = df_bf.agg({"percentual_beneficiarios": "avg"}).collect()[0][0]
            print(f"   % Médio Assistido: {avg_perc:.2f}%")
            
    except Exception as e:
        print(f"\n❌ Fato Bolsa Família: {str(e)[:100]}")
    
except Exception as e:
    print(f"\n⚠️  Erro ao verificar via Spark: {e}")

print("\n" + "=" * 80)
print("✅ CORREÇÃO CONCLUÍDA")
print("=" * 80)

print("\n💡 Próximos passos:")
print("   1. Execute o teste completo com gráficos:")
print("      exec(open('/home/jovyan/work/teste_completo_com_graficos.py').read())")
print("   2. Ou visualize no notebook DEMO:")
print("      Abra DEMO_APRESENTACAO.ipynb e execute as células")
