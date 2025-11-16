#!/usr/bin/env python3
"""
Teste detalhado da API do Bolsa Família
"""

import requests
import os
import json

# Ler chave do script
exec(open('/home/jovyan/work/01_bronze_ingestion.py').read())
chave = globals().get('PORTAL_TRANSPARENCIA_API_KEY', '')

print("=" * 80)
print("🔍 TESTE DETALHADO DA API BOLSA FAMÍLIA")
print("=" * 80)

print(f"\n🔑 Chave sendo usada: {chave[:20]}... (total: {len(chave)} caracteres)")

transparency_url = "https://api.portaldatransparencia.gov.br/api-de-dados"
headers = {
    'chave-api-dados': chave,
    'Accept': 'application/json'
}

# Testar com diferentes municípios e períodos
testes = [
    {'mesAno': '202412', 'codigoIbge': '3550308', 'nome': 'São Paulo'},
    {'mesAno': '202411', 'codigoIbge': '3550308', 'nome': 'São Paulo (nov/2024)'},
    {'mesAno': '202410', 'codigoIbge': '3550308', 'nome': 'São Paulo (out/2024)'},
    {'mesAno': '202412', 'codigoIbge': '3304557', 'nome': 'Rio de Janeiro'},
    {'mesAno': '202412', 'codigoIbge': '3106200', 'nome': 'Belo Horizonte'},
]

print("\n[1/3] Testando diferentes municípios e períodos...\n")

sucesso = False
for i, teste in enumerate(testes, 1):
    print(f"Teste {i}: {teste['nome']}")
    print(f"  Parâmetros: mesAno={teste['mesAno']}, codigoIbge={teste['codigoIbge']}")
    
    try:
        response = requests.get(
            f"{transparency_url}/bolsa-familia-por-municipio",
            headers=headers,
            params={
                'mesAno': teste['mesAno'],
                'codigoIbge': teste['codigoIbge'],
                'pagina': 1
            },
            timeout=10,
            allow_redirects=True
        )
        
        print(f"  Status: {response.status_code}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"  Tipo resposta: {type(data)}")
                
                if isinstance(data, list):
                    print(f"  Tamanho lista: {len(data)}")
                    if len(data) > 0:
                        print(f"  ✅ SUCESSO! Dados encontrados!")
                        print(f"  Primeiro registro:")
                        primeiro = data[0]
                        for key, value in list(primeiro.items())[:8]:
                            print(f"    {key}: {value}")
                        sucesso = True
                        break
                    else:
                        print(f"  ⚠️  Lista vazia (sem dados para este município/período)")
                elif isinstance(data, dict):
                    print(f"  Objeto JSON:")
                    print(f"  Chaves: {list(data.keys())}")
                    if 'data' in data:
                        print(f"  Campo 'data': {type(data['data'])}")
                        if isinstance(data['data'], list) and len(data['data']) > 0:
                            print(f"  ✅ Dados em campo 'data'!")
                            sucesso = True
                            break
                else:
                    print(f"  Formato inesperado: {type(data)}")
                    print(f"  Conteúdo: {str(data)[:200]}")
            except json.JSONDecodeError as e:
                print(f"  ❌ Erro ao parsear JSON: {e}")
                print(f"  Resposta (primeiros 500 chars): {response.text[:500]}")
        elif response.status_code == 401:
            print(f"  ❌ 401 Não autorizado - chave inválida")
            break
        else:
            print(f"  ❌ Erro {response.status_code}")
            print(f"  Resposta: {response.text[:200]}")
            
    except Exception as e:
        print(f"  ❌ Erro: {e}")
    
    print()

# Testar endpoint alternativo
print("\n[2/3] Testando endpoint alternativo (sem especificar município)...\n")

try:
    # Tentar listar todos (pode não funcionar, mas vamos testar)
    response = requests.get(
        f"{transparency_url}/bolsa-familia-por-municipio",
        headers=headers,
        params={'mesAno': '202412', 'pagina': 1},
        timeout=10
    )
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        if isinstance(data, list) and len(data) > 0:
            print(f"✅ Endpoint alternativo funcionou! {len(data)} registros")
            sucesso = True
        else:
            print(f"⚠️  Resposta vazia ou formato diferente")
except Exception as e:
    print(f"❌ Erro: {e}")

# Resumo
print("\n" + "=" * 80)
print("📊 RESUMO")
print("=" * 80)

if sucesso:
    print("\n✅ API FUNCIONANDO!")
    print("   A chave está válida e retornando dados.")
    print("\n💡 Execute a ingestão para coletar dados reais:")
    print("   exec(open('/home/jovyan/work/01_bronze_ingestion.py').read())")
else:
    print("\n⚠️  API retornou 200 mas sem dados")
    print("   Possíveis causas:")
    print("   1. Não há dados para os municípios/períodos testados")
    print("   2. Formato da resposta mudou")
    print("   3. Endpoint requer parâmetros diferentes")
    print("\n💡 Vamos tentar coletar mesmo assim - pode funcionar para outros municípios")

print("\n" + "=" * 80)
