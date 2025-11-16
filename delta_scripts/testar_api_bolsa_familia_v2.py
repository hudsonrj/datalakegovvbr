#!/usr/bin/env python3
"""
Script atualizado para testar API do Bolsa Família com novo endpoint
"""

import requests
import sys

# Configurações da API - Novo endpoint
transparency_url_novo = "http://api.portaldatransparencia.gov.br/api-de-dados"
transparency_url_antigo = "https://portaldatransparencia.gov.br/api-de-dados"

headers = {
    'Accept': 'application/json',
    'chave-api-dados': 'SuaChaveAPI'  # Pode não ser necessário para alguns endpoints
}

print("=" * 80)
print("🔍 TESTE DA API DO BOLSA FAMÍLIA (Versão Atualizada)")
print("=" * 80)

# Testar novo endpoint primeiro
endpoints_teste = [
    {
        'nome': 'Bolsa Família por Município (NOVO)',
        'url': f"{transparency_url_novo}/bolsa-familia-por-municipio",
        'params': {'mesAno': '202412', 'codigoIbge': '3550308', 'pagina': 1}
    },
    {
        'nome': 'Bolsa Família por Município (ANTIGO)',
        'url': f"{transparency_url_antigo}/bolsa-familia-por-municipio",
        'params': {'mesAno': '202412', 'codigoIbge': '3550308', 'pagina': 1}
    }
]

print("\n[1/3] Testando endpoints da API...\n")

endpoints_funcionando = []
endpoints_com_erro = []

for endpoint in endpoints_teste:
    print(f"Testando: {endpoint['nome']}")
    print(f"  URL: {endpoint['url']}")
    
    try:
        response = requests.get(
            endpoint['url'],
            headers=headers,
            params=endpoint['params'],
            timeout=10,
            allow_redirects=True
        )
        
        print(f"  Status Code: {response.status_code}")
        print(f"  URL Final (após redirects): {response.url}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                if data:
                    if isinstance(data, list) and len(data) > 0:
                        print(f"  ✅ SUCESSO! Retornou {len(data)} registros")
                        print(f"     Primeiro registro: {list(data[0].keys())[:5]}")
                        endpoints_funcionando.append(endpoint)
                    elif isinstance(data, dict):
                        print(f"  ✅ SUCESSO! Retornou objeto JSON")
                        print(f"     Chaves: {list(data.keys())[:5]}")
                        endpoints_funcionando.append(endpoint)
                    else:
                        print(f"  ⚠️  Retornou vazio ou formato inesperado")
                        print(f"     Tipo: {type(data)}")
                else:
                    print(f"  ⚠️  Resposta vazia")
            except Exception as e:
                print(f"  ⚠️  Erro ao parsear JSON: {e}")
                print(f"     Resposta (primeiros 200 chars): {response.text[:200]}")
        elif response.status_code == 308:
            print(f"  ⚠️  REDIRECIONAMENTO PERMANENTE (308)")
            print(f"     A API pode ter sido migrada")
            print(f"     Location header: {response.headers.get('Location', 'N/A')}")
        elif response.status_code == 401:
            print(f"  ❌ ERRO 401: Não autorizado")
            print(f"     Pode precisar de chave API válida")
        elif response.status_code == 404:
            print(f"  ❌ ERRO 404: Endpoint não encontrado")
        else:
            print(f"  ❌ ERRO {response.status_code}")
            print(f"     Resposta: {response.text[:200]}")
            
    except requests.exceptions.Timeout:
        print(f"  ❌ TIMEOUT: API não respondeu em 10 segundos")
    except requests.exceptions.ConnectionError as e:
        print(f"  ❌ ERRO DE CONEXÃO: {e}")
    except Exception as e:
        print(f"  ❌ ERRO: {e}")
    
    print()

# Resumo
print("\n" + "=" * 80)
print("📊 RESUMO")
print("=" * 80)

if endpoints_funcionando:
    print(f"\n✅ {len(endpoints_funcionando)} endpoint(s) funcionando!")
    for ep in endpoints_funcionando:
        print(f"   - {ep['nome']}")
    print("\n💡 Use o endpoint funcionando no script de ingestão!")
else:
    print(f"\n❌ Nenhum endpoint está funcionando")
    print(f"\n💡 SOLUÇÃO: Use dados simulados")
    print(f"   O script de ingestão já gera dados simulados automaticamente")

print("\n" + "=" * 80)
