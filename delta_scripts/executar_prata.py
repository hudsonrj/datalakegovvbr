#!/usr/bin/env python3
"""
Script para executar a transformação da camada Prata
Verifica pré-requisitos e executa o pipeline de transformação
"""

import sys
import os

print("=" * 80)
print("🔄 EXECUTANDO TRANSFORMAÇÃO - CAMADA PRATA")
print("=" * 80)

# Verificar se Spark está disponível e funcional
print("\n[1/3] Verificando Spark...")
try:
    spark
    # Testar se está funcional
    test_df = spark.range(1)
    test_df.collect()
    print("✅ Spark está disponível e funcional")
except NameError:
    print("❌ Spark não está configurado!")
    print("💡 Execute CONFIGURAR_SPARK.ipynb primeiro")
    sys.exit(1)
except Exception as e:
    print(f"❌ Spark não está funcional: {e}")
    print("💡 Execute recuperar_spark.py ou CONFIGURAR_SPARK.ipynb")
    sys.exit(1)

# Verificar se há dados Bronze disponíveis
print("\n[2/3] Verificando dados Bronze...")
bronze_paths = [
    "s3a://govbr/bronze/ibge/municipios/",
    "s3a://govbr/bronze/ibge/estados/",
    "s3a://govbr/bronze/portal_transparencia/bpc_municipios/",
    "s3a://govbr/bronze/portal_transparencia/orgaos_siafi/"
]

bronze_ok = []
for path in bronze_paths:
    try:
        df = spark.read.parquet(path)
        count = df.count()
        dataset_name = path.split('/')[-2]
        bronze_ok.append(dataset_name)
        print(f"✅ {dataset_name}: {count:,} registros")
    except Exception as e:
        dataset_name = path.split('/')[-2]
        print(f"⚠️  {dataset_name}: Não disponível")

if len(bronze_ok) < 2:
    print("\n❌ Dados Bronze insuficientes para gerar Prata")
    print("💡 Execute primeiro: exec(open('/home/jovyan/work/01_bronze_ingestion.py').read())")
    sys.exit(1)

print(f"\n✅ {len(bronze_ok)} datasets Bronze disponíveis")

# Executar transformação Prata
print("\n[3/3] Executando transformação Prata...")
print("=" * 80)

try:
    # Executar o script de transformação
    exec(open('/home/jovyan/work/02_prata_transformacao.py').read())
    
    print("\n" + "=" * 80)
    print("✅ TRANSFORMAÇÃO PRATA CONCLUÍDA!")
    print("=" * 80)
    
    # Verificar resultados
    print("\n📊 Verificando dados Prata gerados...")
    prata_paths = [
        "s3a://govbr/prata/dim_municipios/",
        "s3a://govbr/prata/dim_estados/",
        "s3a://govbr/prata/dim_orgaos/",
        "s3a://govbr/prata/fato_bpc/"
    ]
    
    for path in prata_paths:
        try:
            df = spark.read.parquet(path)
            count = df.count()
            dataset_name = path.split('/')[-2]
            print(f"✅ {dataset_name}: {count:,} registros")
        except Exception as e:
            dataset_name = path.split('/')[-2]
            print(f"⚠️  {dataset_name}: Não gerado")
    
except Exception as e:
    print(f"\n❌ Erro ao executar transformação Prata: {e}")
    import traceback
    traceback.print_exc()
    print("\n💡 Verifique os logs acima para mais detalhes")
    sys.exit(1)

print("\n✅ Pronto! Dados Prata estão disponíveis para uso.")
