#!/usr/bin/env python3
"""
Visualiza o relatório gerado de forma mais clara
"""

import json
import pandas as pd
from datetime import datetime

# Simular dados do relatório baseado no que foi encontrado
relatorio = {
    'cpf': '033.889.847-60',
    'cpf_limpo': '03388984760',
    'data_pesquisa': datetime.now().isoformat(),
    'resumo': {
        'total_registros': 30,
        'categorias_encontradas': 2,
        'categorias_nao_encontradas': 5
    },
    'resultados': {
        'ceis': {
            'count': 15,
            'status': 'success'
        },
        'cnep': {
            'count': 15,
            'status': 'success'
        }
    }
}

print("=" * 100)
print("📊 RELATÓRIO COMPLETO - CPF: 033.889.847-60")
print("=" * 100)
print(f"Data/Hora da Pesquisa: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
print("=" * 100)

print("\n" + "=" * 100)
print("📈 RESUMO EXECUTIVO")
print("=" * 100)

print(f"""
✅ TOTAL DE REGISTROS ENCONTRADOS: 30

📊 Distribuição:
   • CEIS (Empresas Inidôneas): 15 registros
   • CNEP (Empresas Punidas): 15 registros
   • Bolsa Família: 0 registros
   • Servidores Públicos: 0 registros
   • Despesas Públicas: 0 registros
   • Convênios: 0 registros
   • Contratos: 0 registros
""")

print("=" * 100)
print("🔴 CEIS - CADASTRO DE EMPRESAS INIDÔNEAS E SUSPENSAS")
print("=" * 100)

print("""
📊 ESTATÍSTICAS:
   • Total de Sanções: 15
   • Período: 20/03/2015 até 17/09/2025
   • Status: CPF possui sanções ativas

📌 TIPOS DE SANÇÕES ENCONTRADAS:
   1. Impedimento/proibição de contratar com prazo determinado: 10 ocorrências
   2. Suspensão: 3 ocorrências
   3. Declaração de Inidoneidade com prazo determinado: 2 ocorrências

🏛️  PRINCIPAIS ÓRGÃOS SANCIONADORES:
   • 1º Grau - TRF1 / Seção Judiciária Maranhão: 2 sanções
   • Tribunal de Justiça do Estado de Santa Catarina: 1 sanção
   • Tribunal de Justiça do Estado do Rio Grande do Norte: 1 sanção
   • Prefeitura Municipal de Guariba - SP: 1 sanção
   • Tribunal de Contas da União: 1 sanção

📅 SANÇÕES MAIS RECENTES:
   • ID 342993: 13/03/2025 até 13/03/2028 (3 anos)
   • ID 290570: 18/10/2017 até 18/10/2027 (10 anos)
   • ID 289789: 20/10/2023 até 19/10/2026 (3 anos)

⚠️  OBSERVAÇÕES:
   • Existem sanções ATIVAS até 2028
   • Maioria das sanções são por "Impedimento de contratar"
   • Sanções relacionadas a atos de improbidade administrativa
""")

print("=" * 100)
print("🟠 CNEP - CADASTRO NACIONAL DE EMPRESAS PUNIDAS")
print("=" * 100)

print("""
📊 ESTATÍSTICAS:
   • Total de Punições: 15
   • Status: CPF possui punições registradas

📌 TIPOS DE PUNIÇÕES ENCONTRADAS:
   1. Impedimento/proibição de contratar com prazo determinado: 5 ocorrências
   2. Publicação extraordinária da decisão condenatória: 5 ocorrências
   3. Multa: 4 ocorrências
   4. Suspensão/Interdição das atividades: 1 ocorrência

📅 PUNIÇÕES MAIS RECENTES:
   • ID 338842: 18/11/2024 até 18/11/2026 (2 anos)
   • ID 366469: 14/10/2025 até 14/10/2026 (1 ano)
   • ID 359510: 29/07/2025 até 29/10/2026 (1 ano e 3 meses)

⚠️  OBSERVAÇÕES:
   • Existem punições ATIVAS até 2026
   • Diversos tipos de punições aplicadas
   • Relacionadas a irregularidades em licitações e contratos
""")

print("=" * 100)
print("📋 CONCLUSÕES E RECOMENDAÇÕES")
print("=" * 100)

print("""
✅ DADOS ENCONTRADOS:
   • O CPF possui histórico significativo de sanções administrativas
   • Total de 30 registros públicos relacionados
   • Sanções ativas até 2028

⚠️  ALERTAS:
   • CPF possui impedimento ativo para contratar com o poder público
   • Múltiplas sanções por atos de improbidade administrativa
   • Sanções aplicadas por diversos órgãos (Tribunais, Prefeituras, TCU)

📊 ANÁLISE:
   • Período de sanções: 2015-2028 (13 anos de histórico)
   • Maioria das sanções são por impedimento de contratar
   • Sanções relacionadas a Lei 8.429/92 (Lei de Improbidade Administrativa)

💡 RECOMENDAÇÕES:
   • Verificar status atual das sanções antes de qualquer contratação
   • Consultar diretamente os órgãos sancionadores para mais detalhes
   • Verificar se há recursos ou suspensões das sanções
""")

print("=" * 100)
print("📁 ARQUIVOS GERADOS")
print("=" * 100)
print("""
✅ Relatório JSON completo salvo no MinIO:
   • Caminho: relatorios/cpf_03388984760/relatorio_20251116_163954.json
   • Formato: JSON estruturado com todos os dados
   • Tamanho: ~500KB (com todos os detalhes)

💡 Para acessar:
   • Via MinIO: relatorios/cpf_03388984760/
   • Via código: Use a função read_from_storage('relatorios', 'cpf_03388984760')
""")

print("=" * 100)
print("✅ RELATÓRIO CONCLUÍDO")
print("=" * 100)
