#!/usr/bin/env python3
"""
Teste com diferentes formatos de parâmetros da API
"""

import requests
import os

# Ler chave
exec(open('/home/jovyan/work/01_bronze_ingestion.py').read())
chave = globals().get('PORTAL_TRANSPARENCIA_API_KEY', '')

print("=" * 80)
print("🔍 TESTE COM DIFERENTES FORMATOS DE PARÂMETROS")
print("=" * 80)

transparency_url = "https://api.portaldatransparencia.gov.br/api-de-dados"
headers = {
    'chave-api-dados': chave,
    'Accept': 'application/json'
}

# Testar diferentes formatos
testes = [
    # Formato 1: mesAno como YYYYMM
    {'params': {'mesAno': '202412', 'codigoIbge': '3550308'}, 'desc': 'Formato padrão (YYYYMM)'},
    # Formato 2: mesAno como MM/YYYY
    {'params': {'mesAno': '12/2024', 'codigoIbge': '3550308'}, 'desc': 'Formato alternativo (MM/YYYY)'},
    # Formato 3: separar mês e ano
    {'params': {'mes': '12', 'ano': '2024', 'codigoIbge': '3550308'}, 'desc': 'Mês e ano separados'},
    # Formato 4: apenas código IBGE (sem mês)
    {'params': {'codigoIbge': '3550308'}, 'desc': 'Apenas código IBGE'},
    # Formato 5: código IBGE com 7 dígitos
    {'params': {'mesAno': '202412', 'codigoIbge': '03550308'}, 'desc': 'Código IBGE com zeros à esquerda'},
]

print(f"\n🔑 Chave: {chave[:20]}...")
print(f"\n[1/2] Testando diferentes formatos de parâmetros...\n")

for i, teste in enumerate(testes, 1):
    print(f"Teste {i}: {teste['desc']}")
    print(f"  Parâmetros: {teste['params']}")
    
    try:
        response = requests.get(
            f"{transparency_url}/bolsa-familia-por-municipio",
            headers=headers,
            params=teste['params'],
            timeout=10
        )
        
        print(f"  Status: {response.status_code}")
        print(f"  URL chamada: {response.url[:150]}")
        
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list):
                if len(data) > 0:
                    print(f"  ✅ SUCESSO! {len(data)} registros encontrados!")
                    print(f"  Primeiro registro:")
                    for key, value in list(data[0].items())[:5]:
                        print(f"    {key}: {value}")
                    print("\n🎉 FORMATO CORRETO ENCONTRADO!")
                    break
                else:
                    print(f"  ⚠️  Lista vazia")
            else:
                print(f"  Tipo: {type(data)}")
                print(f"  Conteúdo: {str(data)[:200]}")
        elif response.status_code == 400:
            print(f"  ❌ 400 Bad Request - formato de parâmetros inválido")
        else:
            print(f"  ❌ Erro {response.status_code}")
            
    except Exception as e:
        print(f"  ❌ Erro: {e}")
    
    print()

# Tentar endpoint de documentação ou listar municípios disponíveis
print("\n[2/2] Verificando documentação da API...\n")

try:
    # Tentar acessar swagger ou documentação
    doc_urls = [
        'https://api.portaldatransparencia.gov.br/swagger-ui.html',
        'https://portaldatransparencia.gov.br/api-de-dados/swagger-ui.html',
    ]
    
    for url in doc_urls:
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                print(f"✅ Documentação encontrada: {url}")
                break
        except:
            pass
except:
    pass

print("\n" + "=" * 80)
print("💡 RECOMENDAÇÃO")
print("=" * 80)
print("\nA API está respondendo (200), mas retorna lista vazia.")
print("Isso pode significar:")
print("1. ✅ Sua chave está funcionando (não é erro 401)")
print("2. ⚠️  Pode não haver dados para os períodos testados")
print("3. ⚠️  O formato dos parâmetros pode precisar de ajuste")
print("\n💡 SOLUÇÃO:")
print("   - Verifique a documentação oficial:")
print("     https://portaldatransparencia.gov.br/api-de-dados")
print("   - Ou use dados simulados (já funcionando)")
print("   - Ou tente períodos mais antigos (2023, 2022)")

print("\n" + "=" * 80)
