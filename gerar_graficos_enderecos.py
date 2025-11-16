#!/usr/bin/env python3
"""
Script para gerar gráficos de exemplo sobre a funcionalidade de endereços
"""

import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, Rectangle
import seaborn as sns
import numpy as np
from pathlib import Path

# Configurar estilo
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 6)
plt.rcParams['font.size'] = 10

# Criar diretório para imagens
Path("docs/images").mkdir(parents=True, exist_ok=True)

# Dados simulados para exemplos
np.random.seed(42)

print("🎨 Gerando gráficos de exemplo...")

# 1. Distribuição de endereços por cidadão
fig, ax = plt.subplots(figsize=(10, 6))
# Probabilidades normalizadas (soma = 1.0)
probs = [0.1, 0.12, 0.15, 0.15, 0.12, 0.10, 0.08, 0.06, 0.05, 0.03, 0.02, 0.01, 0.005, 0.002, 0.001]
probs = np.array(probs) / np.sum(probs)  # Normalizar
enderecos_por_cidadao = np.random.choice(range(1, 16), size=1000, p=probs)
ax.hist(enderecos_por_cidadao, bins=15, edgecolor='black', alpha=0.7, color='#2E86AB')
ax.set_xlabel('Número de Endereços por Cidadão', fontsize=12, fontweight='bold')
ax.set_ylabel('Quantidade de Cidadãos', fontsize=12, fontweight='bold')
ax.set_title('Distribuição de Endereços por Cidadão', fontsize=14, fontweight='bold', pad=20)
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('docs/images/distribuicao_enderecos_cidadao.png', dpi=300, bbox_inches='tight')
plt.close()
print("  ✅ Gráfico 1: Distribuição de endereços por cidadão")

# 2. Qualidade dos endereços normalizados
fig, ax = plt.subplots(figsize=(10, 6))
componentes = ['CEP', 'UF', 'Município', 'Bairro', 'Complemento', 'Completo']
percentuais = [95.2, 98.5, 97.8, 89.3, 45.6, 78.4]
cores = ['#A23B72' if p < 50 else '#F18F01' if p < 80 else '#06A77D' for p in percentuais]
bars = ax.barh(componentes, percentuais, color=cores, edgecolor='black', alpha=0.8)
ax.set_xlabel('Percentual (%)', fontsize=12, fontweight='bold')
ax.set_title('Qualidade dos Endereços Normalizados\n(Percentual de Componentes Presentes)', 
              fontsize=14, fontweight='bold', pad=20)
ax.set_xlim(0, 100)
for i, (bar, pct) in enumerate(zip(bars, percentuais)):
    ax.text(pct + 1, i, f'{pct:.1f}%', va='center', fontweight='bold')
ax.grid(True, alpha=0.3, axis='x')
plt.tight_layout()
plt.savefig('docs/images/qualidade_enderecos.png', dpi=300, bbox_inches='tight')
plt.close()
print("  ✅ Gráfico 2: Qualidade dos endereços normalizados")

# 3. Distribuição de scores de confiabilidade
fig, ax = plt.subplots(figsize=(10, 6))
scores = np.random.normal(75, 15, 1000)
scores = np.clip(scores, 0, 100)
ax.hist(scores, bins=30, edgecolor='black', alpha=0.7, color='#06A77D')
ax.axvline(np.mean(scores), color='#F18F01', linestyle='--', linewidth=2, label=f'Média: {np.mean(scores):.1f}')
ax.axvline(np.median(scores), color='#A23B72', linestyle='--', linewidth=2, label=f'Mediana: {np.median(scores):.1f}')
ax.set_xlabel('Score de Confiabilidade', fontsize=12, fontweight='bold')
ax.set_ylabel('Quantidade de Endereços', fontsize=12, fontweight='bold')
ax.set_title('Distribuição de Scores de Confiabilidade dos Endereços', 
              fontsize=14, fontweight='bold', pad=20)
ax.legend()
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('docs/images/distribuicao_scores.png', dpi=300, bbox_inches='tight')
plt.close()
print("  ✅ Gráfico 3: Distribuição de scores de confiabilidade")

# 4. Top 10 Estados por quantidade de endereços
fig, ax = plt.subplots(figsize=(10, 6))
estados = ['SP', 'RJ', 'MG', 'RS', 'PR', 'SC', 'BA', 'GO', 'PE', 'CE']
quantidades = [125000, 98000, 87000, 65000, 58000, 52000, 48000, 42000, 38000, 35000]
cores_estados = plt.cm.viridis(np.linspace(0.2, 0.9, len(estados)))
bars = ax.barh(estados, quantidades, color=cores_estados, edgecolor='black', alpha=0.8)
ax.set_xlabel('Quantidade de Endereços', fontsize=12, fontweight='bold')
ax.set_title('Top 10 Estados por Quantidade de Endereços', 
              fontsize=14, fontweight='bold', pad=20)
for i, (bar, qtd) in enumerate(zip(bars, quantidades)):
    ax.text(qtd + 2000, i, f'{qtd:,}', va='center', fontweight='bold')
ax.grid(True, alpha=0.3, axis='x')
plt.tight_layout()
plt.savefig('docs/images/top_estados.png', dpi=300, bbox_inches='tight')
plt.close()
print("  ✅ Gráfico 4: Top 10 estados")

# 5. Fluxo de transformação Bronze → Prata → Ouro
fig, ax = plt.subplots(figsize=(14, 6))
ax.axis('off')

# Definir posições
bronze_x, bronze_y = 2, 0.5
prata_x, prata_y = 6, 0.5
ouro_x, ouro_y = 10, 0.5

# Bronze
bronze_box = Rectangle((bronze_x-1, bronze_y-0.4), 2, 0.8, 
                       facecolor='#CD7F32', edgecolor='black', linewidth=2, alpha=0.8)
ax.add_patch(bronze_box)
ax.text(bronze_x, bronze_y, '🥉 BRONZE\nDados Brutos\n560k registros', 
        ha='center', va='center', fontsize=11, fontweight='bold', color='white')

# Prata
prata_box = Rectangle((prata_x-1, prata_y-0.4), 2, 0.8, 
                      facecolor='#C0C0C0', edgecolor='black', linewidth=2, alpha=0.8)
ax.add_patch(prata_box)
ax.text(prata_x, prata_y, '🥈 PRATA\nNormalizados\n560k registros', 
        ha='center', va='center', fontsize=11, fontweight='bold', color='black')

# Ouro
ouro_box = Rectangle((ouro_x-1, ouro_y-0.4), 2, 0.8, 
                    facecolor='#FFD700', edgecolor='black', linewidth=2, alpha=0.8)
ax.add_patch(ouro_box)
ax.text(ouro_x, ouro_y, '🥇 OURO\nRanking/Certificado\n560k registros', 
        ha='center', va='center', fontsize=11, fontweight='bold', color='black')

# Setas
arrow1 = FancyArrowPatch((bronze_x+1, bronze_y), (prata_x-1, prata_y),
                         arrowstyle='->', mutation_scale=30, linewidth=2, color='#2E86AB')
ax.add_patch(arrow1)
ax.text((bronze_x+prata_x)/2, bronze_y+0.3, 'Normalização', 
        ha='center', fontsize=10, fontweight='bold', color='#2E86AB')

arrow2 = FancyArrowPatch((prata_x+1, prata_y), (ouro_x-1, ouro_y),
                         arrowstyle='->', mutation_scale=30, linewidth=2, color='#06A77D')
ax.add_patch(arrow2)
ax.text((prata_x+ouro_x)/2, prata_y+0.3, 'Ranking/Score', 
        ha='center', fontsize=10, fontweight='bold', color='#06A77D')

ax.set_xlim(0, 12)
ax.set_ylim(0, 1)
ax.set_title('Fluxo de Transformação e Enriquecimento de Endereços', 
              fontsize=16, fontweight='bold', pad=30)
plt.tight_layout()
plt.savefig('docs/images/fluxo_transformacao.png', dpi=300, bbox_inches='tight')
plt.close()
print("  ✅ Gráfico 5: Fluxo de transformação")

# 6. Comparação antes/depois da normalização
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

# Antes (Bronze)
exemplos_antes = [
    "Rua das Flores, 123 - Centro - SP",
    "Av. Paulista, 1000, Bela Vista",
    "R. São Paulo, 50 - Apto 45",
    "Estrada X, km 5 - Zona Rural",
    "Praça da República, s/n"
]
ax1.text(0.5, 0.95, 'ANTES (Bronze)\nEndereços em Formatos Variados', 
         ha='center', va='top', fontsize=14, fontweight='bold', 
         transform=ax1.transAxes, color='#A23B72')
y_pos = 0.8
for i, endereco in enumerate(exemplos_antes):
    ax1.text(0.1, y_pos - i*0.15, f"{i+1}. {endereco}", 
             fontsize=10, transform=ax1.transAxes, 
             bbox=dict(boxstyle='round', facecolor='#FFE5E5', alpha=0.7))
ax1.axis('off')

# Depois (Prata)
exemplos_depois = [
    "Rua Das Flores, 123 - Centro - São Paulo/SP - CEP 01234-567",
    "Avenida Paulista, 1000 - Bela Vista - São Paulo/SP - CEP 01310-100",
    "Rua São Paulo, 50 - Apto 45 - Centro - São Paulo/SP - CEP 01000-000",
    "Estrada X, Km 5 - Zona Rural - São Paulo/SP - CEP 00000-000",
    "Praça Da República, S/N - Centro - São Paulo/SP - CEP 01045-000"
]
ax2.text(0.5, 0.95, 'DEPOIS (Prata)\nEndereços Normalizados Padrão Brasileiro', 
         ha='center', va='top', fontsize=14, fontweight='bold', 
         transform=ax2.transAxes, color='#06A77D')
for i, endereco in enumerate(exemplos_depois):
    ax2.text(0.1, y_pos - i*0.15, f"{i+1}. {endereco}", 
             fontsize=10, transform=ax2.transAxes,
             bbox=dict(boxstyle='round', facecolor='#E5FFE5', alpha=0.7))
ax2.axis('off')

plt.suptitle('Comparação: Antes e Depois da Normalização', 
             fontsize=16, fontweight='bold', y=0.98)
plt.tight_layout()
plt.savefig('docs/images/comparacao_normalizacao.png', dpi=300, bbox_inches='tight')
plt.close()
print("  ✅ Gráfico 6: Comparação antes/depois")

print("\n✅ Todos os gráficos gerados com sucesso!")
print("📁 Gráficos salvos em: docs/images/")
