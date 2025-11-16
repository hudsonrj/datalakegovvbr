#!/usr/bin/env python3
"""
Script para testar API com chave fornecida pelo usuário
"""

import requests
import sys

print("=" * 80)
print("🔑 TESTE DA API COM CHAVE")
print("=" * 80)

# Ler chave do script de ingestão
try:
    exec(open('/home/jovyan/work/01_bronze_ingestion.py').read())
    chave_atual = globals().get('PORTAL_TRANSPARENCIA_API_KEY', 'NÃO ENCONTRADA')
    print(f"\n📋 Chave atual no script: {chave_atual[:20]}..." if len(chave_atual) > 20 else f"\n📋 Chave atual no script: {chave_atual}")
except:
    chave_atual = None
    print("\n⚠️  Não foi possível ler a chave do script")

# Permitir que usuário informe nova chave
print("\n" + "=" * 80)
print("💡 INSTRUÇÕES")
print("=" * 80)
print("\n1. Se você já tem uma chave API válida:")
print("   - Edite o arquivo 01_bronze_ingestion.py")
print("   - Atualize: PORTAL_TRANSPARENCIA_API_KEY = 'sua_chave_aqui'")
print("\n2. Se não tem chave ainda:")
print("   - Acesse: https://portaldatransparencia.gov.br/api-de-dados")
print("   - Faça cadastro/login")
print("   - Gere uma chave API")
print("   - Veja o arquivo OBTER_CHAVE_API.md para mais detalhes")

# Testar com chave atual
if chave_atual and chave_atual != 'NÃO ENCONTRADA':
    print("\n" + "=" * 80)
    print("🧪 TESTANDO COM CHAVE ATUAL")
    print("=" * 80)
    
    transparency_url = "https://api.portaldatransparencia.gov.br/api-de-dados"
    headers = {
        'chave-api-dados': chave_atual,
        'Accept': 'application/json'
    }
    
    # Testar endpoint de Bolsa Família
    print("\nTestando endpoint: bolsa-familia-por-municipio")
    print(f"URL: {transparency_url}/bolsa-familia-por-municipio")
    print(f"Parâmetros: mesAno=202412, codigoIbge=3550308 (São Paulo)")
    
    try:
        response = requests.get(
            f"{transparency_url}/bolsa-familia-por-municipio",
            headers=headers,
            params={
                'mesAno': '202412',
                'codigoIbge': '3550308',  # São Paulo
                'pagina': 1
            },
            timeout=10,
            allow_redirects=True
        )
        
        print(f"\nStatus Code: {response.status_code}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                if isinstance(data, list) and len(data) > 0:
                    print(f"✅ SUCESSO! API funcionando!")
                    print(f"   Registros retornados: {len(data)}")
                    print(f"   Primeiro registro:")
                    primeiro = data[0]
                    for key in list(primeiro.keys())[:5]:
                        print(f"     - {key}: {primeiro.get(key)}")
                    print("\n🎉 A chave está funcionando! Execute a ingestão normalmente.")
                elif isinstance(data, dict):
                    print(f"✅ SUCESSO! Retornou objeto JSON")
                    print(f"   Chaves: {list(data.keys())}")
                else:
                    print(f"⚠️  Resposta vazia ou formato inesperado")
                    print(f"   Tipo: {type(data)}")
            except Exception as e:
                print(f"❌ Erro ao parsear JSON: {e}")
                print(f"   Resposta: {response.text[:500]}")
        elif response.status_code == 401:
            print(f"❌ ERRO 401: Não autorizado")
            print(f"   A chave API pode estar inválida ou expirada")
            print(f"   💡 Obtenha uma nova chave em: https://portaldatransparencia.gov.br/api-de-dados")
        elif response.status_code == 403:
            print(f"❌ ERRO 403: Acesso negado")
            print(f"   A chave pode não ter permissão para este endpoint")
        elif response.status_code == 429:
            print(f"⚠️  ERRO 429: Muitas requisições")
            print(f"   Aguarde alguns minutos e tente novamente")
        else:
            print(f"❌ ERRO {response.status_code}")
            print(f"   Resposta: {response.text[:500]}")
            
    except requests.exceptions.Timeout:
        print(f"❌ TIMEOUT: API não respondeu em 10 segundos")
    except requests.exceptions.ConnectionError as e:
        print(f"❌ ERRO DE CONEXÃO: {e}")
    except Exception as e:
        print(f"❌ ERRO: {e}")
        import traceback
        traceback.print_exc()
else:
    print("\n⚠️  Chave não encontrada ou não configurada")
    print("   Configure a chave no script 01_bronze_ingestion.py primeiro")

print("\n" + "=" * 80)
print("📝 PRÓXIMOS PASSOS")
print("=" * 80)

if chave_atual and chave_atual != 'NÃO ENCONTRADA':
    print("\nSe a chave funcionou:")
    print("  ✅ Execute: exec(open('/home/jovyan/work/01_bronze_ingestion.py').read())")
    print("\nSe a chave não funcionou:")
    print("  1. Obtenha uma nova chave em: https://portaldatransparencia.gov.br/api-de-dados")
    print("  2. Atualize PORTAL_TRANSPARENCIA_API_KEY no script")
    print("  3. Execute este teste novamente")
else:
    print("\n1. Obtenha uma chave API em: https://portaldatransparencia.gov.br/api-de-dados")
    print("2. Edite 01_bronze_ingestion.py e atualize PORTAL_TRANSPARENCIA_API_KEY")
    print("3. Execute este teste novamente para validar")

print("\n" + "=" * 80)
