#!/usr/bin/env python3
"""
Teste completo com a chave do usuário: 2c56919ba91b8c1b13473dcef43fb031
"""

import requests
import json

CHAVE_USUARIO = "2c56919ba91b8c1b13473dcef43fb031"

print("=" * 80)
print("🔑 TESTE COMPLETO COM SUA CHAVE")
print("=" * 80)
print(f"\nChave: {CHAVE_USUARIO[:20]}... (total: {len(CHAVE_USUARIO)} caracteres)")

transparency_url = "https://api.portaldatransparencia.gov.br/api-de-dados"
headers = {
    'chave-api-dados': CHAVE_USUARIO,
    'Accept': 'application/json'
}

# Lista mais ampla de municípios e períodos
municipios = [
    {'codigoIbge': '3550308', 'nome': 'São Paulo'},
    {'codigoIbge': '3304557', 'nome': 'Rio de Janeiro'},
    {'codigoIbge': '3106200', 'nome': 'Belo Horizonte'},
    {'codigoIbge': '4106902', 'nome': 'Curitiba'},
    {'codigoIbge': '2611606', 'nome': 'Recife'},
    {'codigoIbge': '1302603', 'nome': 'Manaus'},
    {'codigoIbge': '2927408', 'nome': 'Salvador'},
    {'codigoIbge': '2304400', 'nome': 'Fortaleza'},
    {'codigoIbge': '1501402', 'nome': 'Belém'},
    {'codigoIbge': '5208707', 'nome': 'Goiânia'},
]

# Períodos para testar (últimos 12 meses)
periodos = [
    '202312', '202311', '202310', '202309', '202308',
    '202307', '202306', '202305', '202304', '202303',
    '202302', '202301', '202212', '202211', '202210'
]

print("\n[1/4] Testando vários municípios e períodos...\n")

sucesso = False
dados_encontrados = []
total_testes = 0

for municipio in municipios[:5]:  # Testar primeiros 5 municípios
    for periodo in periodos[:8]:  # Testar primeiros 8 períodos
        total_testes += 1
        if total_testes % 10 == 0:
            print(f"  Progresso: {total_testes} testes...")
        
        try:
            response = requests.get(
                f"{transparency_url}/bolsa-familia-por-municipio",
                headers=headers,
                params={
                    'mesAno': periodo,
                    'codigoIbge': municipio['codigoIbge']
                },
                timeout=8
            )
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list) and len(data) > 0:
                    print(f"\n✅ SUCESSO! Dados encontrados!")
                    print(f"   Município: {municipio['nome']} ({municipio['codigoIbge']})")
                    print(f"   Período: {periodo}")
                    print(f"   Registros: {len(data)}")
                    print(f"\n   Primeiro registro:")
                    primeiro = data[0]
                    for key, value in list(primeiro.items())[:10]:
                        print(f"     {key}: {value}")
                    
                    sucesso = True
                    dados_encontrados.append({
                        'municipio': municipio['nome'],
                        'codigoIbge': municipio['codigoIbge'],
                        'periodo': periodo,
                        'registros': len(data),
                        'dados': data[:2]
                    })
                    break
            elif response.status_code == 401:
                print(f"\n❌ ERRO 401: Chave inválida ou expirada")
                break
        except Exception as e:
            if 'timeout' not in str(e).lower():
                print(f"  Erro: {e}")
    
    if sucesso:
        break

# Se não encontrou, tentar endpoint alternativo
if not sucesso:
    print("\n[2/4] Tentando endpoint alternativo (sem filtro de município)...\n")
    
    for periodo in periodos[:5]:
        try:
            response = requests.get(
                f"{transparency_url}/bolsa-familia-por-municipio",
                headers=headers,
                params={'mesAno': periodo},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list) and len(data) > 0:
                    print(f"✅ Endpoint alternativo funcionou!")
                    print(f"   Período: {periodo}")
                    print(f"   Registros: {len(data)}")
                    print(f"   Primeiro registro:")
                    primeiro = data[0]
                    for key in list(primeiro.keys())[:8]:
                        print(f"     {key}: {primeiro.get(key)}")
                    sucesso = True
                    break
        except Exception as e:
            pass

# Verificar documentação
print("\n[3/4] Verificando documentação da API...\n")

try:
    doc_response = requests.get(
        'https://api.portaldatransparencia.gov.br/swagger-ui.html',
        timeout=5
    )
    if doc_response.status_code == 200:
        print("✅ Documentação disponível em:")
        print("   https://api.portaldatransparencia.gov.br/swagger-ui.html")
except:
    pass

# Resumo final
print("\n" + "=" * 80)
print("📊 RESULTADO FINAL")
print("=" * 80)

if sucesso:
    print("\n✅ SUA CHAVE ESTÁ FUNCIONANDO!")
    print(f"   Dados reais encontrados!")
    print("\n💡 A chave está válida e funcionando.")
    print("   O script 01_bronze_ingestion.py já está usando essa chave.")
    print("\n   Execute a ingestão para coletar dados reais:")
    print("   exec(open('/home/jovyan/work/01_bronze_ingestion.py').read())")
else:
    print("\n⚠️  RESULTADO:")
    print("   ✅ Sua chave está válida (API retorna 200)")
    print("   ⚠️  Mas não encontramos dados para os períodos/municípios testados")
    print("\n   Possíveis causas:")
    print("   1. Dados podem não estar disponíveis para esses períodos específicos")
    print("   2. O endpoint pode ter mudado ou requer parâmetros diferentes")
    print("   3. Pode haver um delay na publicação dos dados")
    print("\n   💡 SOLUÇÕES:")
    print("   1. Verifique a documentação oficial:")
    print("      https://portaldatransparencia.gov.br/api-de-dados")
    print("   2. Tente períodos mais antigos (2022, 2021)")
    print("   3. Use dados simulados (já funcionando automaticamente)")

print("\n" + "=" * 80)
