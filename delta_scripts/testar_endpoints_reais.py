#!/usr/bin/env python3
"""
Teste dos endpoints reais para verificar se conseguimos coletar dados
"""

import requests
import json

CHAVE_API = "2c56919ba91b8c1b13473dcef43fb031"

print("=" * 80)
print("🔍 TESTE DE ENDPOINTS REAIS")
print("=" * 80)

# 1. Testar API IBGE - População por município
print("\n[1/3] Testando API IBGE - População por município...")
ibge_url = "https://servicodados.ibge.gov.br/api/v1"

# Testar diferentes endpoints do IBGE
endpoints_ibge = [
    f"{ibge_url}/localidades/municipios/3550308",  # São Paulo
    f"{ibge_url}/pesquisas/estimativas/populacao/3550308",
    f"{ibge_url}/localidades/municipios/3550308/estimativas",
]

for endpoint in endpoints_ibge:
    try:
        print(f"\n  Testando: {endpoint}")
        response = requests.get(endpoint, timeout=10)
        print(f"  Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"  Tipo: {type(data)}")
            if isinstance(data, dict):
                print(f"  Chaves: {list(data.keys())[:10]}")
                if 'populacao' in str(data).lower() or 'estimativa' in str(data).lower():
                    print(f"  ✅ Dados de população encontrados!")
                    print(f"  Exemplo: {json.dumps(data, indent=2)[:500]}")
            elif isinstance(data, list) and len(data) > 0:
                print(f"  ✅ Lista com {len(data)} itens")
                print(f"  Primeiro item: {json.dumps(data[0], indent=2)[:500]}")
    except Exception as e:
        print(f"  ❌ Erro: {e}")

# 2. Testar API Portal da Transparência - Bolsa Família
print("\n[2/3] Testando API Portal da Transparência - Bolsa Família...")
transparency_url = "https://api.portaldatransparencia.gov.br/api-de-dados"
headers = {
    'chave-api-dados': CHAVE_API,
    'Accept': 'application/json'
}

# Testar diferentes formatos e municípios
testes_bolsa = [
    {'codigoIbge': '3550308', 'nome': 'São Paulo', 'mesAno': '202312'},
    {'codigoIbge': '3304557', 'nome': 'Rio de Janeiro', 'mesAno': '202312'},
    {'codigoIbge': '3550308', 'nome': 'São Paulo', 'mesAno': '202211'},
    {'codigoIbge': '3550308', 'nome': 'São Paulo', 'mesAno': '202210'},
]

for teste in testes_bolsa:
    try:
        print(f"\n  Testando: {teste['nome']} ({teste['mesAno']})")
        response = requests.get(
            f"{transparency_url}/bolsa-familia-por-municipio",
            headers=headers,
            params={
                'mesAno': teste['mesAno'],
                'codigoIbge': teste['codigoIbge']
            },
            timeout=10
        )
        print(f"  Status: {response.status_code}")
        print(f"  URL: {response.url[:150]}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"  Tipo: {type(data)}")
            if isinstance(data, list):
                print(f"  Tamanho: {len(data)}")
                if len(data) > 0:
                    print(f"  ✅ DADOS REAIS ENCONTRADOS!")
                    print(f"  Primeiro registro:")
                    primeiro = data[0]
                    for key, value in list(primeiro.items())[:10]:
                        print(f"    {key}: {value}")
                    break
                else:
                    print(f"  ⚠️  Lista vazia")
            elif isinstance(data, dict):
                print(f"  Objeto JSON:")
                print(f"  Chaves: {list(data.keys())}")
                print(f"  Conteúdo: {json.dumps(data, indent=2)[:500]}")
        elif response.status_code == 401:
            print(f"  ❌ 401 Não autorizado")
        else:
            print(f"  Resposta: {response.text[:300]}")
    except Exception as e:
        print(f"  ❌ Erro: {e}")

# 3. Verificar documentação da API
print("\n[3/3] Verificando documentação das APIs...")

try:
    doc_ibge = requests.get("https://servicodados.ibge.gov.br/api/docs", timeout=5)
    if doc_ibge.status_code == 200:
        print("  ✅ Documentação IBGE disponível")
except:
    pass

try:
    doc_portal = requests.get("https://api.portaldatransparencia.gov.br/swagger-ui.html", timeout=5)
    if doc_portal.status_code == 200:
        print("  ✅ Documentação Portal da Transparência disponível")
        print("     URL: https://api.portaldatransparencia.gov.br/swagger-ui.html")
except:
    pass

print("\n" + "=" * 80)
print("📊 RESUMO")
print("=" * 80)
print("\nExecute este script para verificar quais endpoints estão funcionando.")
print("=" * 80)
