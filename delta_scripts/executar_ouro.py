#!/usr/bin/env python3
"""
Script para executar o enriquecimento da camada Ouro
Verifica pré-requisitos (Prata) e executa o pipeline de enriquecimento
"""

import sys
import os

print("=" * 80)
print("🏆 EXECUTANDO ENRIQUECIMENTO - CAMADA OURO")
print("=" * 80)

# Verificar se Spark está disponível e funcional
print("\n[1/4] Verificando Spark...")
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

# Verificar se há dados Prata disponíveis
print("\n[2/4] Verificando dados Prata (pré-requisito)...")
prata_paths = [
    "s3a://govbr/prata/dim_municipios/",
    "s3a://govbr/prata/dim_estados/",
    "s3a://govbr/prata/fato_bpc/"
]

prata_ok = []
for path in prata_paths:
    try:
        df = spark.read.parquet(path)
        count = df.count()
        dataset_name = path.split('/')[-2]
        prata_ok.append(dataset_name)
        print(f"✅ {dataset_name}: {count:,} registros")
    except Exception as e:
        dataset_name = path.split('/')[-2]
        print(f"⚠️  {dataset_name}: Não disponível")

if len(prata_ok) < 2:
    print("\n❌ Dados Prata insuficientes para gerar Ouro")
    print("💡 Execute primeiro: exec(open('/home/jovyan/work/02_prata_transformacao.py').read())")
    sys.exit(1)

print(f"\n✅ {len(prata_ok)} datasets Prata disponíveis")

# Executar enriquecimento Ouro
print("\n[3/4] Executando enriquecimento Ouro...")
print("=" * 80)

try:
    # Executar o script de enriquecimento
    exec(open('/home/jovyan/work/03_ouro_enriquecimento.py').read())
    
    print("\n" + "=" * 80)
    print("✅ ENRIQUECIMENTO OURO CONCLUÍDO!")
    print("=" * 80)
    
    # Verificar resultados
    print("\n📊 Verificando dados Ouro gerados...")
    ouro_paths = [
        "s3a://govbr/ouro/municipios_enriquecidos/",
        "s3a://govbr/ouro/estados_enriquecidos/",
        "s3a://govbr/ouro/bpc_analytics/",
        "s3a://govbr/ouro/rankings/",
        "s3a://govbr/ouro/agregacoes_regionais/"
    ]
    
    for path in ouro_paths:
        try:
            df = spark.read.parquet(path)
            count = df.count()
            dataset_name = path.split('/')[-2]
            print(f"✅ {dataset_name}: {count:,} registros")
        except Exception as e:
            dataset_name = path.split('/')[-2]
            print(f"⚠️  {dataset_name}: Não gerado")
    
except Exception as e:
    print(f"\n❌ Erro ao executar enriquecimento Ouro: {e}")
    import traceback
    traceback.print_exc()
    print("\n💡 Verifique os logs acima para mais detalhes")
    sys.exit(1)

print("\n✅ Pronto! Dados Ouro estão disponíveis para uso.")
