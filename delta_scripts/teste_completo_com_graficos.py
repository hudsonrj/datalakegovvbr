#!/usr/bin/env python3
"""
Teste completo do pipeline com visualizações
Verifica todos os dados e gera gráficos
"""

import sys
import os
sys.path.insert(0, '/home/jovyan/work')

print("=" * 80)
print("🧪 TESTE COMPLETO DO PIPELINE COM VISUALIZAÇÕES")
print("=" * 80)

# 1. Verificar e inicializar Spark
print("\n[1/6] Inicializando Spark...")
try:
    exec(open('/home/jovyan/work/spark_com_jars_manual.py').read())
    spark = globals()['spark']
    print("✅ Spark inicializado com sucesso")
except Exception as e:
    print(f"⚠️  Erro ao inicializar Spark: {e}")
    print("   Tentando abordagem alternativa...")
    try:
        exec(open('/home/jovyan/work/inicializar_spark.py').read())
        spark = globals()['spark']
        print("✅ Spark inicializado com sucesso (abordagem alternativa)")
    except Exception as e2:
        print(f"❌ Falha ao inicializar Spark: {e2}")
        sys.exit(1)

# 2. Verificar dados Bronze
print("\n[2/6] Verificando dados Bronze...")
bronze_datasets = {
    'municipios': 's3a://govbr/bronze/ibge/municipios/',
    'estados': 's3a://govbr/bronze/ibge/estados/',
    'populacao_estados': 's3a://govbr/bronze/ibge/populacao_estados/',
    'bpc_municipios': 's3a://govbr/bronze/portal_transparencia/bpc_municipios/',
    'bolsa_familia_municipios': 's3a://govbr/bronze/portal_transparencia/bolsa_familia_municipios/',
    'orgaos_siafi': 's3a://govbr/bronze/portal_transparencia/orgaos_siafi/'
}

bronze_status = {}
for nome, path in bronze_datasets.items():
    try:
        df = spark.read.parquet(path)
        count = df.count()
        bronze_status[nome] = {'status': '✅', 'count': count, 'df': df}
        print(f"  ✅ {nome}: {count:,} registros")
    except Exception as e:
        bronze_status[nome] = {'status': '❌', 'count': 0, 'error': str(e)[:100]}
        print(f"  ❌ {nome}: {str(e)[:100]}")

# 3. Se faltar dados Bronze, executar ingestão
missing_bronze = [k for k, v in bronze_status.items() if v['status'] == '❌']
if missing_bronze:
    print(f"\n⚠️  Faltam {len(missing_bronze)} datasets Bronze: {', '.join(missing_bronze)}")
    print("   Executando ingestão Bronze...")
    try:
        exec(open('/home/jovyan/work/01_bronze_ingestion.py').read())
        print("✅ Ingestão Bronze concluída")
        
        # Verificar novamente
        print("\n   Verificando novamente...")
        for nome in missing_bronze:
            path = bronze_datasets[nome]
            try:
                df = spark.read.parquet(path)
                count = df.count()
                bronze_status[nome] = {'status': '✅', 'count': count, 'df': df}
                print(f"  ✅ {nome}: {count:,} registros")
            except Exception as e:
                print(f"  ❌ {nome}: ainda não disponível")
    except Exception as e:
        print(f"❌ Erro na ingestão Bronze: {e}")
        import traceback
        traceback.print_exc()

# 4. Verificar dados Prata
print("\n[3/6] Verificando dados Prata...")
prata_datasets = {
    'dim_municipios': 's3a://govbr/prata/dim_municipios/',
    'dim_estados': 's3a://govbr/prata/dim_estados/',
    'dim_orgaos': 's3a://govbr/prata/dim_orgaos/',
    'fato_bpc': 's3a://govbr/prata/fato_bpc/',
    'fato_bolsa_familia': 's3a://govbr/prata/fato_bolsa_familia/'
}

prata_status = {}
for nome, path in prata_datasets.items():
    try:
        df = spark.read.parquet(path)
        count = df.count()
        prata_status[nome] = {'status': '✅', 'count': count, 'df': df}
        print(f"  ✅ {nome}: {count:,} registros")
    except Exception as e:
        prata_status[nome] = {'status': '❌', 'count': 0, 'error': str(e)[:100]}
        print(f"  ❌ {nome}: {str(e)[:100]}")

# 5. Se faltar dados Prata, executar transformação
missing_prata = [k for k, v in prata_status.items() if v['status'] == '❌']
if missing_prata:
    print(f"\n⚠️  Faltam {len(missing_prata)} datasets Prata: {', '.join(missing_prata)}")
    print("   Executando transformação Prata...")
    try:
        exec(open('/home/jovyan/work/02_prata_transformacao.py').read())
        print("✅ Transformação Prata concluída")
        
        # Verificar novamente
        print("\n   Verificando novamente...")
        for nome in missing_prata:
            path = prata_datasets[nome]
            try:
                df = spark.read.parquet(path)
                count = df.count()
                prata_status[nome] = {'status': '✅', 'count': count, 'df': df}
                print(f"  ✅ {nome}: {count:,} registros")
            except Exception as e:
                print(f"  ❌ {nome}: ainda não disponível")
    except Exception as e:
        print(f"❌ Erro na transformação Prata: {e}")
        import traceback
        traceback.print_exc()

# 6. Carregar dados para visualização
print("\n[4/6] Carregando dados para visualização...")

try:
    # Carregar dados Prata
    df_municipios = prata_status.get('dim_municipios', {}).get('df')
    df_estados = prata_status.get('dim_estados', {}).get('df')
    df_fato_bpc = prata_status.get('fato_bpc', {}).get('df')
    df_fato_bf = prata_status.get('fato_bolsa_familia', {}).get('df')
    
    if df_municipios is None:
        df_municipios = spark.read.parquet(prata_datasets['dim_municipios'])
    if df_estados is None:
        df_estados = spark.read.parquet(prata_datasets['dim_estados'])
    
    # Converter para Pandas para visualização
    print("   Convertendo para Pandas...")
    df_estados_pd = df_estados.toPandas()
    print(f"   ✅ Estados: {len(df_estados_pd)} registros")
    
    if df_fato_bf is not None:
        df_fato_bf_pd = df_fato_bf.toPandas()
        print(f"   ✅ Fato Bolsa Família: {len(df_fato_bf_pd)} registros")
    else:
        try:
            df_fato_bf_pd = spark.read.parquet(prata_datasets['fato_bolsa_familia']).toPandas()
            print(f"   ✅ Fato Bolsa Família: {len(df_fato_bf_pd)} registros")
        except:
            df_fato_bf_pd = None
            print("   ⚠️  Fato Bolsa Família não disponível")
    
    if df_fato_bpc is not None:
        df_fato_bpc_pd = df_fato_bpc.toPandas()
        print(f"   ✅ Fato BPC: {len(df_fato_bpc_pd)} registros")
    else:
        try:
            df_fato_bpc_pd = spark.read.parquet(prata_datasets['fato_bpc']).toPandas()
            print(f"   ✅ Fato BPC: {len(df_fato_bpc_pd)} registros")
        except:
            df_fato_bpc_pd = None
            print("   ⚠️  Fato BPC não disponível")
    
    print("✅ Dados carregados com sucesso")
    
except Exception as e:
    print(f"❌ Erro ao carregar dados: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# 7. Criar visualizações
print("\n[5/6] Criando visualizações...")

try:
    import matplotlib.pyplot as plt
    import seaborn as sns
    import numpy as np
    
    # Configurar estilo
    plt.style.use('seaborn-v0_8-darkgrid')
    sns.set_palette("husl")
    
    # Criar figura com múltiplos subplots
    fig = plt.figure(figsize=(20, 16))
    
    # 1. População por Estado (Top 10)
    ax1 = plt.subplot(3, 3, 1)
    if 'populacao' in df_estados_pd.columns:
        df_pop = df_estados_pd.nlargest(10, 'populacao') if 'populacao' in df_estados_pd.columns else df_estados_pd.head(10)
        if 'populacao' in df_pop.columns:
            bars = ax1.barh(df_pop['uf_sigla'], df_pop['populacao'] / 1e6, color='steelblue')
            ax1.set_xlabel('População (milhões)', fontsize=10)
            ax1.set_title('Top 10 Estados por População', fontsize=12, fontweight='bold')
            ax1.invert_yaxis()
            # Adicionar valores nas barras
            for i, bar in enumerate(bars):
                width = bar.get_width()
                ax1.text(width, bar.get_y() + bar.get_height()/2, 
                        f'{width:.1f}M', ha='left', va='center', fontsize=9)
    else:
        ax1.text(0.5, 0.5, 'Dados de população\nnão disponíveis', 
                ha='center', va='center', transform=ax1.transAxes)
        ax1.set_title('População por Estado', fontsize=12, fontweight='bold')
    
    # 2. Beneficiários de Bolsa Família por Município (Top 15)
    ax2 = plt.subplot(3, 3, 2)
    if df_fato_bf_pd is not None and len(df_fato_bf_pd) > 0:
        if 'quantidade_beneficiarios' in df_fato_bf_pd.columns:
            df_bf_top = df_fato_bf_pd.nlargest(15, 'quantidade_beneficiarios')
            municipio_nome = 'nome_municipio' if 'nome_municipio' in df_bf_top.columns else 'municipio'
            if municipio_nome in df_bf_top.columns:
                bars = ax2.barh(df_bf_top[municipio_nome].head(15), 
                               df_bf_top['quantidade_beneficiarios'].head(15) / 1000,
                               color='coral')
                ax2.set_xlabel('Beneficiários (mil)', fontsize=10)
                ax2.set_title('Top 15 Municípios - Beneficiários Bolsa Família', fontsize=12, fontweight='bold')
                ax2.invert_yaxis()
                plt.setp(ax2.get_yticklabels(), fontsize=8)
            else:
                ax2.text(0.5, 0.5, 'Coluna de município\nnão encontrada', 
                        ha='center', va='center', transform=ax2.transAxes)
        else:
            ax2.text(0.5, 0.5, 'Dados de beneficiários\nnão disponíveis', 
                    ha='center', va='center', transform=ax2.transAxes)
    else:
        ax2.text(0.5, 0.5, 'Dados de Bolsa Família\nnão disponíveis', 
                ha='center', va='center', transform=ax2.transAxes)
    ax2.set_title('Top 15 Municípios - Bolsa Família', fontsize=12, fontweight='bold')
    
    # 3. Percentual de Beneficiários por Município (Top 15)
    ax3 = plt.subplot(3, 3, 3)
    if df_fato_bf_pd is not None and len(df_fato_bf_pd) > 0:
        if 'percentual_beneficiarios' in df_fato_bf_pd.columns:
            df_perc = df_fato_bf_pd.nlargest(15, 'percentual_beneficiarios')
            municipio_nome = 'nome_municipio' if 'nome_municipio' in df_perc.columns else 'municipio'
            if municipio_nome in df_perc.columns:
                bars = ax3.barh(df_perc[municipio_nome].head(15), 
                               df_perc['percentual_beneficiarios'].head(15),
                               color='mediumseagreen')
                ax3.set_xlabel('Percentual (%)', fontsize=10)
                ax3.set_title('Top 15 Municípios - % População Assistida', fontsize=12, fontweight='bold')
                ax3.invert_yaxis()
                plt.setp(ax3.get_yticklabels(), fontsize=8)
            else:
                ax3.text(0.5, 0.5, 'Coluna de município\nnão encontrada', 
                        ha='center', va='center', transform=ax3.transAxes)
        else:
            ax3.text(0.5, 0.5, 'Percentual não calculado\n(verifique população)', 
                    ha='center', va='center', transform=ax3.transAxes)
    else:
        ax3.text(0.5, 0.5, 'Dados de Bolsa Família\nnão disponíveis', 
                ha='center', va='center', transform=ax3.transAxes)
    ax3.set_title('% População Assistida', fontsize=12, fontweight='bold')
    
    # 4. Valor Total por Município (Top 15)
    ax4 = plt.subplot(3, 3, 4)
    if df_fato_bf_pd is not None and len(df_fato_bf_pd) > 0:
        if 'valor_total' in df_fato_bf_pd.columns:
            df_valor = df_fato_bf_pd.nlargest(15, 'valor_total')
            municipio_nome = 'nome_municipio' if 'nome_municipio' in df_valor.columns else 'municipio'
            if municipio_nome in df_valor.columns:
                bars = ax4.barh(df_valor[municipio_nome].head(15), 
                               df_valor['valor_total'].head(15) / 1e6,
                               color='gold')
                ax4.set_xlabel('Valor Total (R$ milhões)', fontsize=10)
                ax4.set_title('Top 15 Municípios - Valor Total', fontsize=12, fontweight='bold')
                ax4.invert_yaxis()
                plt.setp(ax4.get_yticklabels(), fontsize=8)
            else:
                ax4.text(0.5, 0.5, 'Coluna de município\nnão encontrada', 
                        ha='center', va='center', transform=ax4.transAxes)
        else:
            ax4.text(0.5, 0.5, 'Dados de valor\nnão disponíveis', 
                    ha='center', va='center', transform=ax4.transAxes)
    else:
        ax4.text(0.5, 0.5, 'Dados de Bolsa Família\nnão disponíveis', 
                ha='center', va='center', transform=ax4.transAxes)
    ax4.set_title('Valor Total por Município', fontsize=12, fontweight='bold')
    
    # 5. Distribuição de Beneficiários (Histograma)
    ax5 = plt.subplot(3, 3, 5)
    if df_fato_bf_pd is not None and len(df_fato_bf_pd) > 0:
        if 'quantidade_beneficiarios' in df_fato_bf_pd.columns:
            ax5.hist(df_fato_bf_pd['quantidade_beneficiarios'] / 1000, bins=20, 
                    color='skyblue', edgecolor='black', alpha=0.7)
            ax5.set_xlabel('Beneficiários (mil)', fontsize=10)
            ax5.set_ylabel('Frequência', fontsize=10)
            ax5.set_title('Distribuição de Beneficiários', fontsize=12, fontweight='bold')
            ax5.grid(True, alpha=0.3)
        else:
            ax5.text(0.5, 0.5, 'Dados de beneficiários\nnão disponíveis', 
                    ha='center', va='center', transform=ax5.transAxes)
    else:
        ax5.text(0.5, 0.5, 'Dados de Bolsa Família\nnão disponíveis', 
                ha='center', va='center', transform=ax5.transAxes)
    ax5.set_title('Distribuição de Beneficiários', fontsize=12, fontweight='bold')
    
    # 6. Beneficiários vs População (Scatter)
    ax6 = plt.subplot(3, 3, 6)
    if df_fato_bf_pd is not None and len(df_fato_bf_pd) > 0:
        if 'quantidade_beneficiarios' in df_fato_bf_pd.columns and 'populacao' in df_fato_bf_pd.columns:
            ax6.scatter(df_fato_bf_pd['populacao'] / 1000, 
                       df_fato_bf_pd['quantidade_beneficiarios'] / 1000,
                       alpha=0.6, s=50, color='purple')
            ax6.set_xlabel('População (mil)', fontsize=10)
            ax6.set_ylabel('Beneficiários (mil)', fontsize=10)
            ax6.set_title('Beneficiários vs População', fontsize=12, fontweight='bold')
            ax6.grid(True, alpha=0.3)
        else:
            ax6.text(0.5, 0.5, 'Dados insuficientes\npara scatter plot', 
                    ha='center', va='center', transform=ax6.transAxes)
    else:
        ax6.text(0.5, 0.5, 'Dados de Bolsa Família\nnão disponíveis', 
                ha='center', va='center', transform=ax6.transAxes)
    ax6.set_title('Beneficiários vs População', fontsize=12, fontweight='bold')
    
    # 7. Resumo por Estado (se disponível)
    ax7 = plt.subplot(3, 3, 7)
    if df_fato_bf_pd is not None and len(df_fato_bf_pd) > 0:
        if 'uf_sigla' in df_fato_bf_pd.columns and 'quantidade_beneficiarios' in df_fato_bf_pd.columns:
            df_uf = df_fato_bf_pd.groupby('uf_sigla')['quantidade_beneficiarios'].sum().reset_index()
            df_uf = df_uf.sort_values('quantidade_beneficiarios', ascending=False).head(10)
            bars = ax7.bar(df_uf['uf_sigla'], df_uf['quantidade_beneficiarios'] / 1000, color='teal')
            ax7.set_ylabel('Beneficiários (mil)', fontsize=10)
            ax7.set_xlabel('Estado (UF)', fontsize=10)
            ax7.set_title('Top 10 Estados - Total Beneficiários', fontsize=12, fontweight='bold')
            plt.setp(ax7.get_xticklabels(), rotation=45, ha='right')
            # Adicionar valores
            for bar in bars:
                height = bar.get_height()
                ax7.text(bar.get_x() + bar.get_width()/2., height,
                        f'{height:.0f}K', ha='center', va='bottom', fontsize=8)
        else:
            ax7.text(0.5, 0.5, 'Dados insuficientes\npara agregação', 
                    ha='center', va='center', transform=ax7.transAxes)
    else:
        ax7.text(0.5, 0.5, 'Dados de Bolsa Família\nnão disponíveis', 
                ha='center', va='center', transform=ax7.transAxes)
    ax7.set_title('Beneficiários por Estado', fontsize=12, fontweight='bold')
    
    # 8. Valor Médio por Beneficiário (Top 15)
    ax8 = plt.subplot(3, 3, 8)
    if df_fato_bf_pd is not None and len(df_fato_bf_pd) > 0:
        if 'valor_medio_beneficiario' in df_fato_bf_pd.columns:
            df_medio = df_fato_bf_pd.nlargest(15, 'valor_medio_beneficiario')
            municipio_nome = 'nome_municipio' if 'nome_municipio' in df_medio.columns else 'municipio'
            if municipio_nome in df_medio.columns:
                bars = ax8.barh(df_medio[municipio_nome].head(15), 
                               df_medio['valor_medio_beneficiario'].head(15),
                               color='salmon')
                ax8.set_xlabel('Valor Médio (R$)', fontsize=10)
                ax8.set_title('Top 15 Municípios - Valor Médio/Beneficiário', fontsize=12, fontweight='bold')
                ax8.invert_yaxis()
                plt.setp(ax8.get_yticklabels(), fontsize=8)
            else:
                ax8.text(0.5, 0.5, 'Coluna de município\nnão encontrada', 
                        ha='center', va='center', transform=ax8.transAxes)
        else:
            ax8.text(0.5, 0.5, 'Valor médio não calculado', 
                    ha='center', va='center', transform=ax8.transAxes)
    else:
        ax8.text(0.5, 0.5, 'Dados de Bolsa Família\nnão disponíveis', 
                ha='center', va='center', transform=ax8.transAxes)
    ax8.set_title('Valor Médio por Beneficiário', fontsize=12, fontweight='bold')
    
    # 9. Resumo Estatístico (Texto)
    ax9 = plt.subplot(3, 3, 9)
    ax9.axis('off')
    
    stats_text = "📊 RESUMO ESTATÍSTICO\n" + "="*40 + "\n\n"
    
    if df_fato_bf_pd is not None and len(df_fato_bf_pd) > 0:
        if 'quantidade_beneficiarios' in df_fato_bf_pd.columns:
            total_benef = df_fato_bf_pd['quantidade_beneficiarios'].sum()
            stats_text += f"Total Beneficiários: {total_benef:,.0f}\n"
            stats_text += f"Média por Município: {df_fato_bf_pd['quantidade_beneficiarios'].mean():,.0f}\n\n"
        
        if 'valor_total' in df_fato_bf_pd.columns:
            total_valor = df_fato_bf_pd['valor_total'].sum()
            stats_text += f"Valor Total: R$ {total_valor/1e6:.2f} milhões\n"
            stats_text += f"Média por Município: R$ {df_fato_bf_pd['valor_total'].mean()/1e3:.2f} mil\n\n"
        
        if 'percentual_beneficiarios' in df_fato_bf_pd.columns:
            stats_text += f"% Médio Assistido: {df_fato_bf_pd['percentual_beneficiarios'].mean():.2f}%\n"
            stats_text += f"% Máximo: {df_fato_bf_pd['percentual_beneficiarios'].max():.2f}%\n\n"
        
        stats_text += f"Municípios com Dados: {len(df_fato_bf_pd)}\n"
    else:
        stats_text += "Dados de Bolsa Família\nnão disponíveis"
    
    if 'populacao' in df_estados_pd.columns:
        total_pop = df_estados_pd['populacao'].sum()
        stats_text += f"\nPopulação Total (Estados):\n{total_pop:,.0f}"
    
    ax9.text(0.1, 0.5, stats_text, fontsize=10, family='monospace',
            verticalalignment='center', transform=ax9.transAxes)
    
    plt.suptitle('Dashboard - Análise de Bolsa Família e População', 
                fontsize=16, fontweight='bold', y=0.995)
    plt.tight_layout(rect=[0, 0, 1, 0.99])
    
    # Salvar figura
    output_path = '/home/jovyan/work/dashboard_analise.png'
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    print(f"✅ Gráficos salvos em: {output_path}")
    
    # Mostrar resumo
    print("\n" + "="*80)
    print("📊 RESUMO DOS DADOS")
    print("="*80)
    
    if df_fato_bf_pd is not None and len(df_fato_bf_pd) > 0:
        print(f"\n✅ Fato Bolsa Família: {len(df_fato_bf_pd)} registros")
        if 'quantidade_beneficiarios' in df_fato_bf_pd.columns:
            print(f"   Total de Beneficiários: {df_fato_bf_pd['quantidade_beneficiarios'].sum():,.0f}")
        if 'valor_total' in df_fato_bf_pd.columns:
            print(f"   Valor Total: R$ {df_fato_bf_pd['valor_total'].sum()/1e6:.2f} milhões")
        if 'percentual_beneficiarios' in df_fato_bf_pd.columns:
            print(f"   % Médio de População Assistida: {df_fato_bf_pd['percentual_beneficiarios'].mean():.2f}%")
    else:
        print("\n⚠️  Fato Bolsa Família não disponível")
    
    if 'populacao' in df_estados_pd.columns:
        print(f"\n✅ População por Estado: {len(df_estados_pd)} estados")
        print(f"   População Total: {df_estados_pd['populacao'].sum():,.0f}")
    else:
        print("\n⚠️  Dados de população não disponíveis")
    
    print("\n✅ Visualizações criadas com sucesso!")
    
except ImportError as e:
    print(f"⚠️  Bibliotecas de visualização não disponíveis: {e}")
    print("   Instalando matplotlib e seaborn...")
    import subprocess
    subprocess.run(['pip', 'install', 'matplotlib', 'seaborn', '--quiet'], check=False)
    print("   Por favor, execute novamente o script")
except Exception as e:
    print(f"❌ Erro ao criar visualizações: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*80)
print("✅ TESTE COMPLETO FINALIZADO")
print("="*80)
