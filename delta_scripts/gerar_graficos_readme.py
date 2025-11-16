#!/usr/bin/env python3
"""
Script para gerar gráficos de exemplo com dados reais para o README
"""

import pandas as pd
from minio import Minio
import io
import matplotlib.pyplot as plt
import seaborn as sns
import os

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

def read_from_storage(camada, dataset_name):
    """Lê DataFrame de qualquer camada"""
    prefix = f"{camada}/{dataset_name}/"
    try:
        objects = list(minio_client.list_objects(BUCKET_NAME, prefix=prefix, recursive=True))
        if not objects:
            return None
        
        # Pegar o mais recente
        latest = max(objects, key=lambda x: x.last_modified)
        object_name = latest.object_name
        
        response = minio_client.get_object(BUCKET_NAME, object_name)
        df = pd.read_parquet(io.BytesIO(response.read()))
        response.close()
        response.release_conn()
        print(f"✅ Lido: {object_name} ({len(df)} registros)")
        return df
    except Exception as e:
        print(f"❌ Erro ao ler {camada}/{dataset_name}: {e}")
        return None

print("=" * 80)
print("📊 GERANDO GRÁFICOS PARA O README")
print("=" * 80)

# Carregar dados
print("\n[1/3] Carregando dados...")
fato_bolsa_familia = read_from_storage('prata', 'fato_bolsa_familia')
fato_bpc = read_from_storage('prata', 'fato_bpc')
dim_estados = read_from_storage('prata', 'dim_estados')

# Verificar se temos dados suficientes
if fato_bolsa_familia is None or len(fato_bolsa_familia) == 0:
    print("⚠️  Dados de Bolsa Família não disponíveis. Execute o pipeline primeiro.")
    exit(1)

print(f"\n✅ Dados carregados:")
print(f"   - Bolsa Família: {len(fato_bolsa_familia)} registros")
if fato_bpc is not None:
    print(f"   - BPC: {len(fato_bpc)} registros")
if dim_estados is not None:
    print(f"   - Estados: {len(dim_estados)} registros")

# Criar diretório para imagens
os.makedirs('docs/images', exist_ok=True)

print("\n[2/3] Gerando gráficos...")

# Configurar estilo
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")

# GRÁFICO 1: Top 10 Municípios - Valor Total Bolsa Família
print("   Gerando gráfico 1: Top 10 Municípios - Valor Total...")
fig, ax = plt.subplots(figsize=(12, 8))
top10_valor = fato_bolsa_familia.nlargest(10, 'valor_total')
municipio_col = 'nome_municipio' if 'nome_municipio' in top10_valor.columns else 'municipio'
uf_col = 'uf_sigla' if 'uf_sigla' in top10_valor.columns else 'uf'

if municipio_col in top10_valor.columns and uf_col in top10_valor.columns:
    labels = top10_valor[municipio_col].str[:20] + ' - ' + top10_valor[uf_col]
    bars = ax.barh(range(len(top10_valor)), top10_valor['valor_total'] / 1000, color='steelblue')
    ax.set_yticks(range(len(top10_valor)))
    ax.set_yticklabels(labels, fontsize=10)
    ax.set_xlabel('Valor Total (R$ mil)', fontsize=12)
    ax.set_title('Top 10 Municípios - Valor Total Bolsa Família', fontsize=14, fontweight='bold')
    ax.grid(axis='x', alpha=0.3)
    
    # Adicionar valores nas barras
    for i, bar in enumerate(bars):
        width = bar.get_width()
        ax.text(width, bar.get_y() + bar.get_height()/2, 
                f'R$ {width:.0f}K', ha='left', va='center', fontsize=9, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig('docs/images/grafico_top10_valor.png', dpi=150, bbox_inches='tight')
    plt.close()
    print("   ✅ Gráfico 1 salvo")

# GRÁFICO 2: Top 10 Municípios - Beneficiários
print("   Gerando gráfico 2: Top 10 Municípios - Beneficiários...")
fig, ax = plt.subplots(figsize=(12, 8))
top10_benef = fato_bolsa_familia.nlargest(10, 'quantidade_beneficiarios')
if municipio_col in top10_benef.columns and uf_col in top10_benef.columns:
    labels = top10_benef[municipio_col].str[:20] + ' - ' + top10_benef[uf_col]
    bars = ax.barh(range(len(top10_benef)), top10_benef['quantidade_beneficiarios'] / 1000, color='coral')
    ax.set_yticks(range(len(top10_benef)))
    ax.set_yticklabels(labels, fontsize=10)
    ax.set_xlabel('Número de Beneficiários (mil)', fontsize=12)
    ax.set_title('Top 10 Municípios - Número de Beneficiários Bolsa Família', fontsize=14, fontweight='bold')
    ax.grid(axis='x', alpha=0.3)
    
    for i, bar in enumerate(bars):
        width = bar.get_width()
        ax.text(width, bar.get_y() + bar.get_height()/2, 
                f'{width:.1f}K', ha='left', va='center', fontsize=9, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig('docs/images/grafico_top10_beneficiarios.png', dpi=150, bbox_inches='tight')
    plt.close()
    print("   ✅ Gráfico 2 salvo")

# GRÁFICO 3: Distribuição de Valores
print("   Gerando gráfico 3: Distribuição de Valores...")
fig, ax = plt.subplots(figsize=(10, 6))
ax.hist(fato_bolsa_familia['valor_total'] / 1000, bins=30, color='skyblue', edgecolor='black', alpha=0.7)
ax.set_xlabel('Valor Total (R$ mil)', fontsize=12)
ax.set_ylabel('Frequência', fontsize=12)
ax.set_title('Distribuição de Valores Totais - Bolsa Família', fontsize=14, fontweight='bold')
ax.grid(alpha=0.3)
plt.tight_layout()
plt.savefig('docs/images/grafico_distribuicao_valores.png', dpi=150, bbox_inches='tight')
plt.close()
print("   ✅ Gráfico 3 salvo")

# GRÁFICO 4: Comparação Bolsa Família vs BPC (se disponível)
if fato_bpc is not None and len(fato_bpc) > 0:
    print("   Gerando gráfico 4: Comparação Bolsa Família vs BPC...")
    fig, axes = plt.subplots(1, 3, figsize=(18, 6))
    
    comparacao = pd.DataFrame({
        'Programa': ['Bolsa Família', 'BPC'],
        'Total Investido (R$ milhões)': [
            fato_bolsa_familia['valor_total'].sum() / 1e6,
            fato_bpc['valor'].sum() / 1e6 if 'valor' in fato_bpc.columns else 0
        ],
        'Total Beneficiários (mil)': [
            fato_bolsa_familia['quantidade_beneficiarios'].sum() / 1000,
            fato_bpc['quantidade_beneficiados'].sum() / 1000 if 'quantidade_beneficiados' in fato_bpc.columns else 0
        ],
        'Valor Médio (R$)': [
            fato_bolsa_familia['valor_total'].sum() / fato_bolsa_familia['quantidade_beneficiarios'].sum(),
            fato_bpc['valor'].sum() / fato_bpc['quantidade_beneficiados'].sum() if 'valor' in fato_bpc.columns and 'quantidade_beneficiados' in fato_bpc.columns else 0
        ]
    })
    
    # Gráfico 1: Valor Total
    axes[0].bar(comparacao['Programa'], comparacao['Total Investido (R$ milhões)'], 
                color=['steelblue', 'purple'], alpha=0.7)
    axes[0].set_ylabel('Valor Total (R$ milhões)', fontsize=11)
    axes[0].set_title('Valor Total Investido', fontsize=12, fontweight='bold')
    axes[0].grid(axis='y', alpha=0.3)
    for i, v in enumerate(comparacao['Total Investido (R$ milhões)']):
        axes[0].text(i, v, f'R$ {v:.1f}M', ha='center', va='bottom', fontweight='bold', fontsize=10)
    
    # Gráfico 2: Beneficiários
    axes[1].bar(comparacao['Programa'], comparacao['Total Beneficiários (mil)'], 
                color=['coral', 'orange'], alpha=0.7)
    axes[1].set_ylabel('Beneficiários (mil)', fontsize=11)
    axes[1].set_title('Total de Beneficiários', fontsize=12, fontweight='bold')
    axes[1].grid(axis='y', alpha=0.3)
    for i, v in enumerate(comparacao['Total Beneficiários (mil)']):
        axes[1].text(i, v, f'{v:.1f}K', ha='center', va='bottom', fontweight='bold', fontsize=10)
    
    # Gráfico 3: Valor Médio
    axes[2].bar(comparacao['Programa'], comparacao['Valor Médio (R$)'], 
                color=['lightgreen', 'teal'], alpha=0.7)
    axes[2].set_ylabel('Valor Médio (R$)', fontsize=11)
    axes[2].set_title('Valor Médio por Beneficiário', fontsize=12, fontweight='bold')
    axes[2].grid(axis='y', alpha=0.3)
    for i, v in enumerate(comparacao['Valor Médio (R$)']):
        axes[2].text(i, v, f'R$ {v:.2f}', ha='center', va='bottom', fontweight='bold', fontsize=10)
    
    plt.tight_layout()
    plt.savefig('docs/images/grafico_comparacao_programas.png', dpi=150, bbox_inches='tight')
    plt.close()
    print("   ✅ Gráfico 4 salvo")

# GRÁFICO 5: Beneficiários por Estado (se disponível)
if 'uf_sigla' in fato_bolsa_familia.columns:
    print("   Gerando gráfico 5: Beneficiários por Estado...")
    fig, ax = plt.subplots(figsize=(14, 8))
    df_uf = fato_bolsa_familia.groupby('uf_sigla')['quantidade_beneficiarios'].sum().reset_index()
    df_uf = df_uf.sort_values('quantidade_beneficiarios', ascending=False).head(15)
    
    bars = ax.barh(range(len(df_uf)), df_uf['quantidade_beneficiarios'] / 1000, color='teal')
    ax.set_yticks(range(len(df_uf)))
    ax.set_yticklabels(df_uf['uf_sigla'], fontsize=11)
    ax.set_xlabel('Beneficiários (mil)', fontsize=12)
    ax.set_title('Top 15 Estados - Total de Beneficiários Bolsa Família', fontsize=14, fontweight='bold')
    ax.grid(axis='x', alpha=0.3)
    ax.invert_yaxis()
    
    for i, bar in enumerate(bars):
        width = bar.get_width()
        ax.text(width, bar.get_y() + bar.get_height()/2, 
                f'{width:.0f}K', ha='left', va='center', fontsize=9, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig('docs/images/grafico_beneficiarios_por_estado.png', dpi=150, bbox_inches='tight')
    plt.close()
    print("   ✅ Gráfico 5 salvo")

print("\n[3/3] ✅ Todos os gráficos gerados com sucesso!")
print(f"\n📁 Gráficos salvos em: docs/images/")
print("\nGráficos gerados:")
print("  - grafico_top10_valor.png")
print("  - grafico_top10_beneficiarios.png")
print("  - grafico_distribuicao_valores.png")
if fato_bpc is not None:
    print("  - grafico_comparacao_programas.png")
if 'uf_sigla' in fato_bolsa_familia.columns:
    print("  - grafico_beneficiarios_por_estado.png")

print("\n" + "=" * 80)
print("✅ PROCESSO CONCLUÍDO")
print("=" * 80)
