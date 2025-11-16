#!/usr/bin/env python3
"""
Script para testar se a API do Bolsa Família está disponível
"""

import requests
import sys

# Configurações da API
transparency_url = "https://portaldatransparencia.gov.br/api-de-dados"
headers = {
    'Accept': 'application/json',
    'chave-api-dados': 'SuaChaveAPI'  # Substituir se necessário
}

print("=" * 80)
print("🔍 TESTE DA API DO BOLSA FAMÍLIA")
print("=" * 80)

# Testar diferentes endpoints possíveis
endpoints_teste = [
    {
        'nome': 'Bolsa Família por Município',
        'url': f"{transparency_url}/bolsa-familia-por-municipio",
        'params': {'mesAno': '202412', 'codigoIbge': '3550308', 'pagina': 1}  # São Paulo
    },
    {
        'nome': 'Auxílio Emergencial por Município',
        'url': f"{transparency_url}/auxilio-emergencial-por-municipio",
        'params': {'mesAno': '202412', 'codigoIbge': '3550308', 'pagina': 1}
    },
    {
        'nome': 'Benefícios por Município',
        'url': f"{transparency_url}/beneficios-por-municipio",
        'params': {'mesAno': '202412', 'codigoIbge': '3550308', 'pagina': 1}
    },
    {
        'nome': 'Bolsa Família (endpoint alternativo)',
        'url': f"{transparency_url}/bolsa-familia",
        'params': {'mesAno': '202412', 'codigoIbge': '3550308'}
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
            timeout=10
        )
        
        print(f"  Status Code: {response.status_code}")
        
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
                        endpoints_com_erro.append({
                            'endpoint': endpoint,
                            'erro': 'Resposta vazia ou formato inesperado'
                        })
                else:
                    print(f"  ⚠️  Resposta vazia")
                    endpoints_com_erro.append({
                        'endpoint': endpoint,
                        'erro': 'Resposta vazia'
                    })
            except Exception as e:
                print(f"  ⚠️  Erro ao parsear JSON: {e}")
                print(f"     Resposta: {response.text[:200]}")
                endpoints_com_erro.append({
                    'endpoint': endpoint,
                    'erro': f'Erro JSON: {e}'
                })
        elif response.status_code == 401:
            print(f"  ❌ ERRO 401: Não autorizado (chave API inválida ou ausente)")
            endpoints_com_erro.append({
                'endpoint': endpoint,
                'erro': '401 - Não autorizado'
            })
        elif response.status_code == 404:
            print(f"  ❌ ERRO 404: Endpoint não encontrado")
            endpoints_com_erro.append({
                'endpoint': endpoint,
                'erro': '404 - Não encontrado'
            })
        elif response.status_code == 403:
            print(f"  ❌ ERRO 403: Acesso negado")
            endpoints_com_erro.append({
                'endpoint': endpoint,
                'erro': '403 - Acesso negado'
            })
        else:
            print(f"  ❌ ERRO {response.status_code}: {response.text[:200]}")
            endpoints_com_erro.append({
                'endpoint': endpoint,
                'erro': f'Status {response.status_code}'
            })
            
    except requests.exceptions.Timeout:
        print(f"  ❌ TIMEOUT: API não respondeu em 10 segundos")
        endpoints_com_erro.append({
            'endpoint': endpoint,
            'erro': 'Timeout'
        })
    except requests.exceptions.ConnectionError:
        print(f"  ❌ ERRO DE CONEXÃO: Não foi possível conectar à API")
        endpoints_com_erro.append({
            'endpoint': endpoint,
            'erro': 'Erro de conexão'
        })
    except Exception as e:
        print(f"  ❌ ERRO: {e}")
        endpoints_com_erro.append({
            'endpoint': endpoint,
            'erro': str(e)
        })
    
    print()

# 2. Verificar se há dados simulados disponíveis
print("\n[2/3] Verificando dados simulados disponíveis...")
try:
    from minio import Minio
    
    MINIO_SERVER_URL = "ch8ai-minio.l6zv5a.easypanel.host"
    MINIO_ROOT_USER = "admin"
    MINIO_ROOT_PASSWORD = "1q2w3e4r"
    BUCKET_NAME = "govbr"
    
    minio_client = Minio(
        MINIO_SERVER_URL,
        access_key=MINIO_ROOT_USER,
        secret_key=MINIO_ROOT_PASSWORD,
        secure=True
    )
    
    prefix = "bronze/portal_transparencia/bolsa_familia_municipios/"
    objects = list(minio_client.list_objects(BUCKET_NAME, prefix=prefix, recursive=True))
    
    if objects:
        print(f"  ✅ Dados simulados encontrados: {len(objects)} arquivo(s)")
        latest = max(objects, key=lambda x: x.last_modified)
        print(f"     Último arquivo: {latest.object_name}")
        print(f"     Data: {latest.last_modified}")
    else:
        print(f"  ⚠️  Nenhum dado simulado encontrado")
        
except Exception as e:
    print(f"  ⚠️  Erro ao verificar MinIO: {e}")

# 3. Resumo e Recomendações
print("\n" + "=" * 80)
print("📊 RESUMO E RECOMENDAÇÕES")
print("=" * 80)

if endpoints_funcionando:
    print(f"\n✅ {len(endpoints_funcionando)} endpoint(s) funcionando:")
    for ep in endpoints_funcionando:
        print(f"   - {ep['nome']}")
    print("\n💡 Use os dados reais da API!")
else:
    print(f"\n❌ Nenhum endpoint da API está funcionando")
    print(f"\n📋 Erros encontrados:")
    for erro in endpoints_com_erro:
        print(f"   - {erro['endpoint']['nome']}: {erro['erro']}")

print("\n💡 SOLUÇÕES:")

if not endpoints_funcionando:
    print("\n1. ✅ Use dados simulados (já implementado):")
    print("   O script de ingestão já gera dados simulados automaticamente")
    print("   quando a API não está disponível.")
    print("\n2. 🔧 Para gerar dados simulados manualmente:")
    print("   exec(open('/home/jovyan/work/gerar_dados_simulados_bolsa_familia.py').read())")
    print("\n3. 🔑 Se a API requer chave:")
    print("   - Verifique se precisa de cadastro no Portal da Transparência")
    print("   - Atualize a chave no script 01_bronze_ingestion.py")
    print("   - Endpoint: https://portaldatransparencia.gov.br/api-de-dados")
else:
    print("\n✅ A API está funcionando! Use os dados reais.")
    print("   O script de ingestão tentará usar a API primeiro.")

print("\n" + "=" * 80)
print("✅ TESTE CONCLUÍDO")
print("=" * 80)
