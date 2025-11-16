#!/usr/bin/env python3
"""
Script completo para gerar a camada Ouro
Verifica pré-requisitos e executa tudo em sequência
"""

import sys
import os
sys.path.insert(0, '/home/jovyan/work')

print("=" * 80)
print("🏆 GERANDO CAMADA OURO COMPLETA")
print("=" * 80)

# 1. Verificar e corrigir Prata primeiro
print("\n[1/5] Verificando camada Prata (pré-requisito)...")
try:
    exec(open('/home/jovyan/work/corrigir_fatos_prata.py').read())
    print("✅ Verificação Prata concluída")
except Exception as e:
    print(f"⚠️  Erro na verificação Prata: {e}")
    print("   Continuando mesmo assim...")

# 2. Verificar dados Prata via Spark
print("\n[2/5] Verificando dados Prata via Spark...")
try:
    # Inicializar Spark
    try:
        spark
    except NameError:
        exec(open('/home/jovyan/work/spark_com_jars_manual.py').read())
        spark = globals()['spark']
    
    prata_datasets = {
        'dim_municipios': 's3a://govbr/prata/dim_municipios/',
        'dim_estados': 's3a://govbr/prata/dim_estados/',
        'fato_bpc': 's3a://govbr/prata/fato_bpc/',
        'fato_bolsa_familia': 's3a://govbr/prata/fato_bolsa_familia/'
    }
    
    prata_status = {}
    for nome, path in prata_datasets.items():
        try:
            df = spark.read.parquet(path)
            count = df.count()
            prata_status[nome] = {'status': '✅', 'count': count}
            print(f"  ✅ {nome}: {count:,} registros")
        except Exception as e:
            prata_status[nome] = {'status': '❌', 'error': str(e)[:100]}
            print(f"  ❌ {nome}: {str(e)[:100]}")
    
    # Verificar se temos o mínimo necessário
    essenciais = ['dim_municipios', 'dim_estados']
    if all(prata_status.get(k, {}).get('status') == '✅' for k in essenciais):
        print("\n✅ Dados essenciais Prata disponíveis")
    else:
        print("\n❌ Dados essenciais Prata faltando!")
        print("   Execute: exec(open('/home/jovyan/work/02_prata_transformacao.py').read())")
        sys.exit(1)
        
except Exception as e:
    print(f"❌ Erro ao verificar Prata: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# 3. Executar enriquecimento Ouro
print("\n[3/5] Executando enriquecimento Ouro...")
try:
    exec(open('/home/jovyan/work/03_ouro_enriquecimento.py').read())
    print("✅ Enriquecimento Ouro executado")
except Exception as e:
    print(f"❌ Erro no enriquecimento Ouro: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# 4. Verificar dados Ouro gerados
print("\n[4/5] Verificando dados Ouro gerados...")
ouro_datasets = {
    'municipios_enriquecidos': 's3a://govbr/ouro/municipios_enriquecidos/',
    'estados_enriquecidos': 's3a://govbr/ouro/estados_enriquecidos/',
    'bpc_analytics': 's3a://govbr/ouro/bpc_analytics/',
    'rankings': 's3a://govbr/ouro/rankings/',
    'agregacoes_regionais': 's3a://govbr/ouro/agregacoes_regionais/'
}

ouro_status = {}
for nome, path in ouro_datasets.items():
    try:
        df = spark.read.parquet(path)
        count = df.count()
        ouro_status[nome] = {'status': '✅', 'count': count}
        print(f"  ✅ {nome}: {count:,} registros")
        
        # Mostrar algumas colunas
        if count > 0:
            print(f"     Colunas: {', '.join(df.columns[:5])}...")
    except Exception as e:
        ouro_status[nome] = {'status': '❌', 'error': str(e)[:100]}
        print(f"  ❌ {nome}: {str(e)[:100]}")

# 5. Resumo final
print("\n" + "=" * 80)
print("📊 RESUMO FINAL")
print("=" * 80)

total_ouro = sum(1 for v in ouro_status.values() if v['status'] == '✅')
print(f"\n✅ Datasets Ouro gerados: {total_ouro}/{len(ouro_datasets)}")

if total_ouro == len(ouro_datasets):
    print("\n🎉 TODOS OS DATASETS OURO FORAM GERADOS COM SUCESSO!")
else:
    print(f"\n⚠️  {len(ouro_datasets) - total_ouro} datasets não foram gerados")
    for nome, info in ouro_status.items():
        if info['status'] == '❌':
            print(f"   - {nome}: {info.get('error', 'Erro desconhecido')}")

print("\n💡 Próximos passos:")
print("   1. Visualize os dados no notebook DEMO_APRESENTACAO.ipynb")
print("   2. Execute o teste completo com gráficos:")
print("      exec(open('/home/jovyan/work/teste_completo_com_graficos.py').read())")

print("\n" + "=" * 80)
print("✅ PROCESSO CONCLUÍDO")
print("=" * 80)
