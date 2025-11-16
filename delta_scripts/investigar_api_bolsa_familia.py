#!/usr/bin/env python3
"""
Investigação completa da API de Bolsa Família
Testa diferentes formatos, períodos e endpoints
"""

import requests
import json
from datetime import datetime, timedelta

CHAVE_API = "2c56919ba91b8c1b13473dcef43fb031"

print("=" * 80)
print("🔍 INVESTIGAÇÃO COMPLETA - API BOLSA FAMÍLIA")
print("=" * 80)

transparency_url = "https://api.portaldatransparencia.gov.br/api-de-dados"
headers = {
    'chave-api-dados': CHAVE_API,
    'Accept': 'application/json'
}

# 1. Verificar documentação Swagger
print("\n[1/5] Verificando documentação Swagger...")
try:
    swagger_url = "https://api.portaldatransparencia.gov.br/swagger-ui.html"
    response = requests.get(swagger_url, timeout=10)
    if response.status_code == 200:
        print("  ✅ Swagger disponível")
        print(f"  URL: {swagger_url}")
        
        # Tentar pegar JSON da documentação
        api_docs_url = "https://api.portaldatransparencia.gov.br/v3/api-docs"
        try:
            docs_response = requests.get(api_docs_url, timeout=10)
            if docs_response.status_code == 200:
                docs = docs_response.json()
                print("  ✅ Documentação JSON disponível")
                
                # Procurar endpoint de Bolsa Família
                if 'paths' in docs:
                    bolsa_paths = {k: v for k, v in docs['paths'].items() if 'bolsa' in k.lower() or 'familia' in k.lower()}
                    if bolsa_paths:
                        print(f"\n  📋 Endpoints encontrados relacionados a Bolsa Família:")
                        for path, details in bolsa_paths.items():
                            print(f"    - {path}")
                            if 'get' in details:
                                params = details['get'].get('parameters', [])
                                if params:
                                    print(f"      Parâmetros:")
                                    for p in params[:5]:
                                        print(f"        {p.get('name')}: {p.get('description', 'N/A')}")
        except Exception as e:
            print(f"  ⚠️  Erro ao acessar documentação JSON: {e}")
except Exception as e:
    print(f"  ⚠️  Erro ao acessar Swagger: {e}")

# 2. Testar diferentes formatos de código IBGE
print("\n[2/5] Testando diferentes formatos de código IBGE...")
codigos_teste = [
    ('3550308', 'São Paulo - 7 dígitos'),
    ('03550308', 'São Paulo - 8 dígitos com zero'),
    ('355030', 'São Paulo - 6 dígitos'),
]

for codigo, desc in codigos_teste:
    try:
        response = requests.get(
            f"{transparency_url}/bolsa-familia-por-municipio",
            headers=headers,
            params={'mesAno': '202312', 'codigoIbge': codigo},
            timeout=10
        )
        print(f"\n  {desc} ({codigo}):")
        print(f"    Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list):
                print(f"    Resultado: Lista com {len(data)} itens")
                if len(data) > 0:
                    print(f"    ✅ DADOS ENCONTRADOS!")
                    print(f"    Primeiro registro: {json.dumps(data[0], indent=2)[:300]}")
                    break
            elif isinstance(data, dict):
                print(f"    Resultado: Objeto JSON")
                print(f"    Chaves: {list(data.keys())}")
    except Exception as e:
        print(f"    Erro: {e}")

# 3. Testar períodos mais antigos (2022, 2021)
print("\n[3/5] Testando períodos mais antigos...")
periodos_antigos = [
    '202212', '202211', '202210', '202209',
    '202112', '202111', '202110',
    '202012', '202011', '202010',
]

print("  Testando São Paulo (3550308)...")
for periodo in periodos_antigos:
    try:
        response = requests.get(
            f"{transparency_url}/bolsa-familia-por-municipio",
            headers=headers,
            params={'mesAno': periodo, 'codigoIbge': '3550308'},
            timeout=8
        )
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list) and len(data) > 0:
                print(f"  ✅ SUCESSO! Período {periodo}: {len(data)} registros")
                print(f"     Primeiro registro:")
                primeiro = data[0]
                for key in list(primeiro.keys())[:8]:
                    print(f"       {key}: {primeiro.get(key)}")
                break
    except:
        continue

# 4. Testar endpoint sem filtro de município
print("\n[4/5] Testando endpoint sem filtro de município...")
try:
    response = requests.get(
        f"{transparency_url}/bolsa-familia-por-municipio",
        headers=headers,
        params={'mesAno': '202312'},
        timeout=10
    )
    print(f"  Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"  Tipo: {type(data)}")
        if isinstance(data, list):
            print(f"  Tamanho: {len(data)}")
            if len(data) > 0:
                print(f"  ✅ DADOS ENCONTRADOS!")
        elif isinstance(data, dict):
            print(f"  Chaves: {list(data.keys())}")
            if 'data' in data or 'resultado' in data:
                print(f"  ✅ Possível estrutura de dados encontrada")
    elif response.status_code == 400:
        print(f"  ⚠️  400 Bad Request - precisa especificar município")
except Exception as e:
    print(f"  Erro: {e}")

# 5. Testar outros endpoints relacionados
print("\n[5/5] Testando outros endpoints relacionados...")
endpoints_alternativos = [
    '/bolsa-familia',
    '/bolsa-familia-por-municipio-e-mes',
    '/auxilio-brasil-por-municipio',
    '/beneficios-por-municipio',
]

for endpoint in endpoints_alternativos:
    try:
        response = requests.get(
            f"{transparency_url}{endpoint}",
            headers=headers,
            params={'mesAno': '202312', 'codigoIbge': '3550308'},
            timeout=8
        )
        print(f"\n  {endpoint}:")
        print(f"    Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list) and len(data) > 0:
                print(f"    ✅ DADOS ENCONTRADOS! {len(data)} registros")
                break
            elif isinstance(data, dict):
                print(f"    Objeto JSON: {list(data.keys())}")
    except Exception as e:
        if 'timeout' not in str(e).lower():
            print(f"    Erro: {e}")

print("\n" + "=" * 80)
print("📊 RESUMO DA INVESTIGAÇÃO")
print("=" * 80)
print("\nExecute este script para verificar:")
print("1. Documentação da API")
print("2. Formatos de código IBGE")
print("3. Períodos disponíveis")
print("4. Endpoints alternativos")
print("\n" + "=" * 80)
