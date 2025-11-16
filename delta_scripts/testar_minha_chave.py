#!/usr/bin/env python3
"""
Script para testar sua chave API diretamente
Cole sua chave aqui ou defina como variável de ambiente
"""

import requests
import os
import sys

print("=" * 80)
print("🔑 TESTE COM SUA CHAVE API")
print("=" * 80)

# OPÇÃO 1: Cole sua chave aqui diretamente
MINHA_CHAVE = ""  # <-- COLE SUA CHAVE AQUI

# OPÇÃO 2: Ou defina como variável de ambiente antes de executar
# export MINHA_CHAVE_API='sua_chave_aqui'
chave_env = os.getenv('MINHA_CHAVE_API') or os.getenv('PORTAL_TRANSPARENCIA_API_KEY')

# Usar chave informada ou da variável de ambiente
chave_para_teste = MINHA_CHAVE or chave_env

if not chave_para_teste:
    print("\n⚠️  NENHUMA CHAVE ENCONTRADA!")
    print("\n💡 Para testar sua chave, você tem 2 opções:")
    print("\n   OPÇÃO 1: Edite este script e cole sua chave na linha 10:")
    print("            MINHA_CHAVE = 'sua_chave_aqui'")
    print("\n   OPÇÃO 2: Defina variável de ambiente antes de executar:")
    print("            export MINHA_CHAVE_API='sua_chave_aqui'")
    print("            python testar_minha_chave.py")
    print("\n" + "=" * 80)
    sys.exit(1)

print(f"\n🔑 Testando com chave: {chave_para_teste[:20]}... (total: {len(chave_para_teste)} caracteres)")

transparency_url = "https://api.portaldatransparencia.gov.br/api-de-dados"
headers = {
    'chave-api-dados': chave_para_teste,
    'Accept': 'application/json'
}

# Testar vários municípios e períodos
print("\n[1/3] Testando diferentes municípios e períodos...\n")

testes = [
    {'mesAno': '202312', 'codigoIbge': '3550308', 'nome': 'São Paulo'},
    {'mesAno': '202311', 'codigoIbge': '3550308', 'nome': 'São Paulo (nov)'},
    {'mesAno': '202310', 'codigoIbge': '3550308', 'nome': 'São Paulo (out)'},
    {'mesAno': '202312', 'codigoIbge': '3304557', 'nome': 'Rio de Janeiro'},
    {'mesAno': '202312', 'codigoIbge': '3106200', 'nome': 'Belo Horizonte'},
    {'mesAno': '202211', 'codigoIbge': '3550308', 'nome': 'São Paulo (nov/2022)'},
    {'mesAno': '202210', 'codigoIbge': '3550308', 'nome': 'São Paulo (out/2022)'},
]

sucesso = False
dados_encontrados = []

for teste in testes:
    print(f"Testando: {teste['nome']} ({teste['mesAno']})")
    
    try:
        response = requests.get(
            f"{transparency_url}/bolsa-familia-por-municipio",
            headers=headers,
            params={'mesAno': teste['mesAno'], 'codigoIbge': teste['codigoIbge']},
            timeout=10
        )
        
        print(f"  Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list) and len(data) > 0:
                print(f"  ✅ SUCESSO! {len(data)} registros encontrados!")
                print(f"  Primeiro registro:")
                primeiro = data[0]
                for key in list(primeiro.keys())[:8]:
                    print(f"    {key}: {primeiro.get(key)}")
                sucesso = True
                dados_encontrados.append({
                    'teste': teste['nome'],
                    'registros': len(data),
                    'dados': data[:3]  # Primeiros 3 registros
                })
            elif response.status_code == 200:
                print(f"  ⚠️  Lista vazia")
        elif response.status_code == 401:
            print(f"  ❌ 401 Não autorizado - CHAVE INVÁLIDA")
            print(f"  Verifique se sua chave está correta")
            break
        elif response.status_code == 403:
            print(f"  ❌ 403 Acesso negado")
            break
        else:
            print(f"  ❌ Status {response.status_code}: {response.text[:200]}")
    except Exception as e:
        print(f"  ❌ Erro: {e}")

# Testar endpoint alternativo
print("\n[2/3] Testando endpoint sem filtro de município...\n")

try:
    response = requests.get(
        f"{transparency_url}/bolsa-familia-por-municipio",
        headers=headers,
        params={'mesAno': '202312'},
        timeout=10
    )
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        if isinstance(data, list) and len(data) > 0:
            print(f"✅ Endpoint alternativo funcionou! {len(data)} registros")
            sucesso = True
except Exception as e:
    print(f"Erro: {e}")

# Resumo final
print("\n" + "=" * 80)
print("📊 RESULTADO FINAL")
print("=" * 80)

if sucesso:
    print("\n✅ SUA CHAVE ESTÁ FUNCIONANDO!")
    print(f"   Dados reais encontrados em {len(dados_encontrados)} teste(s)")
    print("\n💡 Para usar sua chave no pipeline:")
    print("   1. Adicione no docker-compose-delta.yml:")
    print("      environment:")
    print("        - PORTAL_TRANSPARENCIA_API_KEY=sua_chave_aqui")
    print("\n   2. Ou exporte antes de executar:")
    print("      export PORTAL_TRANSPARENCIA_API_KEY='sua_chave_aqui'")
    print("\n   3. Execute a ingestão:")
    print("      exec(open('/home/jovyan/work/01_bronze_ingestion.py').read())")
else:
    print("\n⚠️  RESULTADO:")
    if any('401' in str(teste) for teste in [testes]):
        print("   ❌ Chave inválida ou expirada")
        print("   💡 Obtenha uma nova chave em: https://portaldatransparencia.gov.br/api-de-dados")
    else:
        print("   ⚠️  API retorna 200 mas sem dados")
        print("   Possíveis causas:")
        print("   1. Dados podem não estar disponíveis para esses períodos")
        print("   2. Endpoint pode ter mudado")
        print("   3. Verifique documentação: https://portaldatransparencia.gov.br/api-de-dados")

print("\n" + "=" * 80)
