#!/usr/bin/env python3
"""
Script para informar chave API e testar
"""

import requests
import sys

print("=" * 80)
print("🔑 INFORMAR CHAVE API E TESTAR")
print("=" * 80)

print("\n💡 Por favor, informe sua chave API do Portal da Transparência")
print("   (ou pressione Enter para usar a chave atual do script)")
print("\n   Você pode encontrar sua chave em:")
print("   https://portaldatransparencia.gov.br/api-de-dados")

# Tentar ler chave atual
try:
    exec(open('/home/jovyan/work/01_bronze_ingestion.py').read())
    chave_atual = globals().get('PORTAL_TRANSPARENCIA_API_KEY', '')
    print(f"\n📋 Chave atual no script: {chave_atual[:20]}...")
except:
    chave_atual = ''

# Em ambiente não-interativo, usar chave atual ou pedir via variável
import os
chave_nova = os.getenv('MINHA_CHAVE_API') or os.getenv('CHAVE_API') or chave_atual

if not chave_nova or chave_nova == chave_atual:
    print("\n⚠️  Para testar com sua chave:")
    print("   1. Defina variável: export MINHA_CHAVE_API='sua_chave'")
    print("   2. Ou edite este script e coloque sua chave diretamente")
    print("\n   Usando chave atual do script para teste...")
    chave_para_teste = chave_atual
else:
    print(f"\n✅ Usando chave da variável de ambiente")
    chave_para_teste = chave_nova

# Testar
print(f"\n🔍 Testando com chave: {chave_para_teste[:20]}... (total: {len(chave_para_teste)} chars)")

transparency_url = "https://api.portaldatransparencia.gov.br/api-de-dados"
headers = {
    'chave-api-dados': chave_para_teste,
    'Accept': 'application/json'
}

# Testar vários municípios e períodos
testes = [
    {'mesAno': '202312', 'codigoIbge': '3550308', 'nome': 'São Paulo'},
    {'mesAno': '202312', 'codigoIbge': '3304557', 'nome': 'Rio de Janeiro'},
    {'mesAno': '202312', 'codigoIbge': '3106200', 'nome': 'Belo Horizonte'},
    {'mesAno': '202211', 'codigoIbge': '3550308', 'nome': 'São Paulo (nov/2022)'},
]

print("\n[1/2] Testando API...\n")

sucesso = False
for teste in testes:
    print(f"Testando: {teste['nome']} ({teste['mesAno']})")
    
    try:
        response = requests.get(
            f"{transparency_url}/bolsa-familia-por-municipio",
            headers=headers,
            params={'mesAno': teste['mesAno'], 'codigoIbge': teste['codigoIbge']},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list) and len(data) > 0:
                print(f"  ✅ SUCESSO! {len(data)} registros encontrados!")
                print(f"  Primeiro registro:")
                primeiro = data[0]
                for key in list(primeiro.keys())[:8]:
                    print(f"    {key}: {primeiro.get(key)}")
                sucesso = True
                break
            else:
                print(f"  ⚠️  Status 200 mas lista vazia")
        elif response.status_code == 401:
            print(f"  ❌ 401 Não autorizado - chave inválida")
            break
        else:
            print(f"  ❌ Status {response.status_code}")
    except Exception as e:
        print(f"  ❌ Erro: {e}")

print("\n" + "=" * 80)
print("📊 RESULTADO")
print("=" * 80)

if sucesso:
    print("\n✅ SUA CHAVE ESTÁ FUNCIONANDO!")
    print("   Dados reais foram encontrados na API.")
    print("\n💡 Para usar sua chave:")
    print("   1. Adicione no docker-compose.yml:")
    print("      environment:")
    print("        - PORTAL_TRANSPARENCIA_API_KEY=sua_chave_aqui")
    print("\n   2. Ou exporte antes de executar:")
    print("      export PORTAL_TRANSPARENCIA_API_KEY='sua_chave_aqui'")
    print("\n   3. Execute a ingestão:")
    print("      exec(open('/home/jovyan/work/01_bronze_ingestion.py').read())")
else:
    print("\n⚠️  API retorna 200 mas sem dados")
    print("   Possíveis causas:")
    print("   1. Dados podem não estar disponíveis para esses períodos")
    print("   2. Endpoint pode ter mudado")
    print("   3. Verifique documentação: https://portaldatransparencia.gov.br/api-de-dados")
    print("\n💡 SOLUÇÃO TEMPORÁRIA:")
    print("   Use dados simulados (já funcionando automaticamente)")

print("\n" + "=" * 80)
