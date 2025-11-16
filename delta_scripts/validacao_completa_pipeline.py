#!/usr/bin/env python3
"""
Validação completa do pipeline - Bronze, Prata e Ouro
Gera relatório detalhado de todo o pipeline
"""

import sys
import os
sys.path.insert(0, '/home/jovyan/work')

print("=" * 80)
print("🔍 VALIDAÇÃO COMPLETA DO PIPELINE")
print("=" * 80)

# 1. Inicializar Spark
print("\n[1/6] Inicializando Spark...")
try:
    try:
        spark
        # Testar se está funcional
        test_df = spark.range(1)
        test_df.collect()
        print("✅ Spark já está disponível e funcional")
    except NameError:
        print("   Inicializando Spark...")
        exec(open('/home/jovyan/work/spark_com_jars_manual.py').read())
        spark = globals()['spark']
        print("✅ Spark inicializado com sucesso")
except Exception as e:
    print(f"❌ Erro ao inicializar Spark: {e}")
    sys.exit(1)

# 2. Validar Camada Bronze
print("\n[2/6] Validando Camada Bronze...")
bronze_datasets = {
    'municipios': 's3a://govbr/bronze/ibge/municipios/',
    'estados': 's3a://govbr/bronze/ibge/estados/',
    'populacao_estados': 's3a://govbr/bronze/ibge/populacao_estados/',
    'orgaos_siafi': 's3a://govbr/bronze/portal_transparencia/orgaos_siafi/',
    'bpc_municipios': 's3a://govbr/bronze/portal_transparencia/bpc_municipios/',
    'bolsa_familia_municipios': 's3a://govbr/bronze/portal_transparencia/bolsa_familia_municipios/'
}

bronze_results = {}
for nome, path in bronze_datasets.items():
    try:
        df = spark.read.parquet(path)
        count = df.count()
        cols = len(df.columns)
        bronze_results[nome] = {
            'status': '✅',
            'count': count,
            'colunas': cols
        }
        print(f"  ✅ {nome:30s} | {count:>8,} registros | {cols:>3} colunas")
    except Exception as e:
        bronze_results[nome] = {
            'status': '❌',
            'error': str(e)[:80]
        }
        print(f"  ❌ {nome:30s} | {str(e)[:80]}")

bronze_ok = sum(1 for v in bronze_results.values() if v['status'] == '✅')
print(f"\n  📊 Bronze: {bronze_ok}/{len(bronze_datasets)} datasets disponíveis")

# 3. Validar Camada Prata
print("\n[3/6] Validando Camada Prata...")
prata_datasets = {
    'dim_municipios': 's3a://govbr/prata/dim_municipios/',
    'dim_estados': 's3a://govbr/prata/dim_estados/',
    'dim_orgaos': 's3a://govbr/prata/dim_orgaos/',
    'fato_bpc': 's3a://govbr/prata/fato_bpc/',
    'fato_bolsa_familia': 's3a://govbr/prata/fato_bolsa_familia/'
}

prata_results = {}
for nome, path in prata_datasets.items():
    try:
        df = spark.read.parquet(path)
        count = df.count()
        cols = len(df.columns)
        prata_results[nome] = {
            'status': '✅',
            'count': count,
            'colunas': cols
        }
        print(f"  ✅ {nome:30s} | {count:>8,} registros | {cols:>3} colunas")
        
        # Mostrar algumas colunas importantes
        if count > 0:
            important_cols = [c for c in df.columns if any(x in c.lower() for x in ['populacao', 'beneficiar', 'valor', 'percentual'])]
            if important_cols:
                print(f"     📌 Colunas importantes: {', '.join(important_cols[:3])}")
    except Exception as e:
        prata_results[nome] = {
            'status': '❌',
            'error': str(e)[:80]
        }
        print(f"  ❌ {nome:30s} | {str(e)[:80]}")

prata_ok = sum(1 for v in prata_results.values() if v['status'] == '✅')
print(f"\n  📊 Prata: {prata_ok}/{len(prata_datasets)} datasets disponíveis")

# 4. Validar Camada Ouro
print("\n[4/6] Validando Camada Ouro...")
ouro_datasets = {
    'municipios_enriquecidos': 's3a://govbr/ouro/municipios_enriquecidos/',
    'estados_enriquecidos': 's3a://govbr/ouro/estados_enriquecidos/',
    'bpc_analytics': 's3a://govbr/ouro/bpc_analytics/',
    'rankings': 's3a://govbr/ouro/rankings/',
    'agregacoes_regionais': 's3a://govbr/ouro/agregacoes_regionais/'
}

ouro_results = {}
for nome, path in ouro_datasets.items():
    try:
        df = spark.read.parquet(path)
        count = df.count()
        cols = len(df.columns)
        ouro_results[nome] = {
            'status': '✅',
            'count': count,
            'colunas': cols
        }
        print(f"  ✅ {nome:30s} | {count:>8,} registros | {cols:>3} colunas")
    except Exception as e:
        ouro_results[nome] = {
            'status': '❌',
            'error': str(e)[:80]
        }
        print(f"  ❌ {nome:30s} | {str(e)[:80]}")

ouro_ok = sum(1 for v in ouro_results.values() if v['status'] == '✅')
print(f"\n  📊 Ouro: {ouro_ok}/{len(ouro_datasets)} datasets disponíveis")

# 5. Análise de Qualidade dos Dados
print("\n[5/6] Análise de Qualidade dos Dados...")

# Verificar se temos dados de população e beneficiários
if prata_results.get('dim_estados', {}).get('status') == '✅':
    try:
        df_estados = spark.read.parquet(prata_datasets['dim_estados'])
        if 'populacao' in df_estados.columns:
            total_pop = df_estados.agg({"populacao": "sum"}).collect()[0][0]
            print(f"  ✅ População total (estados): {total_pop:,.0f}")
        else:
            print(f"  ⚠️  Coluna 'populacao' não encontrada em dim_estados")
    except:
        pass

if prata_results.get('fato_bolsa_familia', {}).get('status') == '✅':
    try:
        df_bf = spark.read.parquet(prata_datasets['fato_bolsa_familia'])
        if 'quantidade_beneficiarios' in df_bf.columns:
            total_benef = df_bf.agg({"quantidade_beneficiarios": "sum"}).collect()[0][0]
            print(f"  ✅ Total beneficiários Bolsa Família: {total_benef:,.0f}")
        
        if 'percentual_beneficiarios' in df_bf.columns:
            avg_perc = df_bf.agg({"percentual_beneficiarios": "avg"}).collect()[0][0]
            print(f"  ✅ % Médio de população assistida: {avg_perc:.2f}%")
        
        if 'valor_total' in df_bf.columns:
            total_valor = df_bf.agg({"valor_total": "sum"}).collect()[0][0]
            print(f"  ✅ Valor total Bolsa Família: R$ {total_valor/1e6:.2f} milhões")
    except Exception as e:
        print(f"  ⚠️  Erro ao analisar Bolsa Família: {str(e)[:80]}")

# 6. Relatório Final
print("\n" + "=" * 80)
print("📊 RELATÓRIO FINAL DO PIPELINE")
print("=" * 80)

total_bronze = len(bronze_datasets)
total_prata = len(prata_datasets)
total_ouro = len(ouro_datasets)

print(f"\n🥉 CAMADA BRONZE:")
print(f"   ✅ Datasets disponíveis: {bronze_ok}/{total_bronze}")
if bronze_ok < total_bronze:
    missing = [k for k, v in bronze_results.items() if v['status'] == '❌']
    print(f"   ⚠️  Faltando: {', '.join(missing)}")

print(f"\n🥈 CAMADA PRATA:")
print(f"   ✅ Datasets disponíveis: {prata_ok}/{total_prata}")
if prata_ok < total_prata:
    missing = [k for k, v in prata_results.items() if v['status'] == '❌']
    print(f"   ⚠️  Faltando: {', '.join(missing)}")

print(f"\n🏆 CAMADA OURO:")
print(f"   ✅ Datasets disponíveis: {ouro_ok}/{total_ouro}")
if ouro_ok < total_ouro:
    missing = [k for k, v in ouro_results.items() if v['status'] == '❌']
    print(f"   ⚠️  Faltando: {', '.join(missing)}")

# Status geral
total_ok = bronze_ok + prata_ok + ouro_ok
total_datasets = total_bronze + total_prata + total_ouro
percentual = (total_ok / total_datasets) * 100

print(f"\n📈 STATUS GERAL:")
print(f"   ✅ Total de datasets disponíveis: {total_ok}/{total_datasets} ({percentual:.1f}%)")

if percentual == 100:
    print("\n🎉 PARABÉNS! Pipeline 100% completo e funcional!")
    print("   Todos os dados estão disponíveis e prontos para análise.")
elif percentual >= 80:
    print("\n✅ Pipeline quase completo! Alguns datasets podem estar faltando.")
    print("   Execute os scripts de correção se necessário.")
else:
    print("\n⚠️  Pipeline incompleto. Execute os scripts de correção:")
    if bronze_ok < total_bronze:
        print("   - exec(open('/home/jovyan/work/01_bronze_ingestion.py').read())")
    if prata_ok < total_prata:
        print("   - exec(open('/home/jovyan/work/corrigir_fatos_prata.py').read())")
    if ouro_ok < total_ouro:
        print("   - exec(open('/home/jovyan/work/gerar_camada_ouro_completa.py').read())")

# Recomendações
print("\n💡 RECOMENDAÇÕES:")
if bronze_ok == total_bronze and prata_ok == total_prata and ouro_ok == total_ouro:
    print("   ✅ Execute o teste completo com gráficos:")
    print("      exec(open('/home/jovyan/work/teste_completo_com_graficos.py').read())")
    print("   ✅ Visualize no notebook DEMO_APRESENTACAO.ipynb")
else:
    print("   🔧 Corrija os datasets faltantes primeiro")
    print("   📊 Depois execute o teste completo com gráficos")

print("\n" + "=" * 80)
print("✅ VALIDAÇÃO CONCLUÍDA")
print("=" * 80)
