#!/usr/bin/env python3
"""
Exemplo FUNCIONAL de coleta de dados do Portal da Transparência
Este código FOI TESTADO e FUNCIONA!
"""

import requests
import json

# Suas credenciais
PORTAL_TRANSPARENCIA_API_KEY = "2c56919ba91b8c1b13473dcef43fb031"
transparency_url = "http://api.portaldatransparencia.gov.br/api-de-dados"

headers = {
    'chave-api-dados': PORTAL_TRANSPARENCIA_API_KEY
}

print("=" * 80)
print("EXEMPLO 1: BPC (Benefício de Prestação Continuada) - São Paulo")
print("=" * 80)

response = requests.get(
    f"{transparency_url}/bpc-por-municipio",
    headers=headers,
    params={
        'mesAno': '202412',
        'codigoIbge': '3550308',  # São Paulo
        'pagina': 1
    },
    timeout=30
)

if response.status_code == 200:
    data = response.json()
    if data:
        print(f"✅ Sucesso! Encontrados {len(data)} registros")
        print(json.dumps(data[0], indent=2, ensure_ascii=False))
    else:
        print("❌ Lista vazia retornada")
else:
    print(f"❌ Erro {response.status_code}: {response.text}")

print("\n" + "=" * 80)
print("EXEMPLO 2: Órgãos do Governo Federal (SIAFI)")
print("=" * 80)

response = requests.get(
    f"{transparency_url}/orgaos-siafi",
    headers=headers,
    timeout=30
)

if response.status_code == 200:
    data = response.json()
    # Filtrar órgãos válidos
    orgaos_validos = [org for org in data if 'CODIGO INVALIDO' not in org.get('descricao', '')]
    print(f"✅ Sucesso! Encontrados {len(orgaos_validos)} órgãos válidos")
    print("\nPrimeiros 10 órgãos:")
    for i, org in enumerate(orgaos_validos[:10], 1):
        print(f"{i}. [{org['codigo']}] {org['descricao']}")
else:
    print(f"❌ Erro {response.status_code}")

print("\n" + "=" * 80)
print("EXEMPLO 3: Municípios do Brasil (IBGE - sem API key)")
print("=" * 80)

ibge_url = "https://servicodados.ibge.gov.br/api/v1"
response = requests.get(f"{ibge_url}/localidades/estados/35/municipios")

if response.status_code == 200:
    municipios = response.json()
    print(f"✅ Sucesso! Encontrados {len(municipios)} municípios em SP")
    print("\nPrimeiros 5 municípios:")
    for i, mun in enumerate(municipios[:5], 1):
        print(f"{i}. [{mun['id']}] {mun['nome']}")
else:
    print(f"❌ Erro {response.status_code}")

print("\n" + "=" * 80)
print("EXEMPLO 4: Coletar BPC de múltiplos municípios")
print("=" * 80)

# Pegar primeiros 5 municípios
municipios_teste = municipios[:5]
total_beneficiados = 0
total_valor = 0

for mun in municipios_teste:
    codigo = str(mun['id'])
    nome = mun['nome']

    response = requests.get(
        f"{transparency_url}/bpc-por-municipio",
        headers=headers,
        params={'mesAno': '202412', 'codigoIbge': codigo, 'pagina': 1},
        timeout=10
    )

    if response.status_code == 200 and response.json():
        data = response.json()[0]
        beneficiados = data.get('quantidadeBeneficiados', 0)
        valor = data.get('valor', 0)
        total_beneficiados += beneficiados
        total_valor += valor
        print(f"✅ {nome}: {beneficiados:,} beneficiados - R$ {valor:,.2f}")
    else:
        print(f"❌ {nome}: Sem dados")

print(f"\nTotal: {total_beneficiados:,} beneficiados - R$ {total_valor:,.2f}")

print("\n" + "=" * 80)
print("✅ Todos os exemplos executados!")
print("=" * 80)
