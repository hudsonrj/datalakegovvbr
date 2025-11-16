#!/usr/bin/env python3
"""
Script para testar pesquisa por CPF
"""

import requests
import pandas as pd
from datetime import datetime, timedelta
import json

# Configurações
PORTAL_TRANSPARENCIA_API_KEY = "2c56919ba91b8c1b13473dcef43fb031"
transparency_url = "https://api.portaldatransparencia.gov.br/api-de-dados"

headers = {
    'chave-api-dados': PORTAL_TRANSPARENCIA_API_KEY,
    'Accept': 'application/json'
}

def formatar_cpf(cpf):
    """Remove formatação do CPF"""
    return ''.join(filter(str.isdigit, str(cpf)))

def mascarar_cpf(cpf):
    """Mascara CPF para exibição"""
    cpf_limpo = formatar_cpf(cpf)
    if len(cpf_limpo) == 11:
        return f"{cpf_limpo[:3]}.{cpf_limpo[3:6]}.{cpf_limpo[6:9]}-{cpf_limpo[9:]}"
    return cpf_limpo

def consultar_endpoint(endpoint, params, descricao):
    """Consulta um endpoint da API"""
    try:
        response = requests.get(
            f"{transparency_url}{endpoint}",
            headers=headers,
            params=params,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            if data and len(data) > 0:
                return {
                    'status': 'success',
                    'data': data,
                    'count': len(data) if isinstance(data, list) else 1
                }
            else:
                return {
                    'status': 'empty',
                    'data': [],
                    'count': 0
                }
        elif response.status_code == 401:
            return {
                'status': 'unauthorized',
                'data': [],
                'count': 0,
                'error': 'Não autorizado'
            }
        else:
            return {
                'status': 'error',
                'data': [],
                'count': 0,
                'error': f"Status {response.status_code}"
            }
    except Exception as e:
        return {
            'status': 'error',
            'data': [],
            'count': 0,
            'error': str(e)
        }

# CPF para teste
CPF_INPUT = "03388984760"
CPF = formatar_cpf(CPF_INPUT)
CPF_MASCARADO = mascarar_cpf(CPF)

print("=" * 80)
print(f"🔍 TESTE DE PESQUISA POR CPF: {CPF_MASCARADO}")
print("=" * 80)

resultados = {}

# 1. Bolsa Família
print("\n[1/7] Consultando Bolsa Família...")
bolsa_familia_resultados = []
for i in range(6):  # Últimos 6 meses
    data_ref = (datetime.now() - timedelta(days=30*i)).strftime('%Y%m')
    result = consultar_endpoint(
        '/bolsa-familia-por-cpf-ou-nis',
        {'cpfOuNis': CPF, 'mesAno': data_ref, 'pagina': 1},
        f'Bolsa Família - {data_ref}'
    )
    if result['status'] == 'success' and result['count'] > 0:
        bolsa_familia_resultados.extend(result['data'])

resultados['bolsa_familia'] = {
    'status': 'success' if bolsa_familia_resultados else 'empty',
    'data': bolsa_familia_resultados,
    'count': len(bolsa_familia_resultados)
}
print(f"   {'✅' if bolsa_familia_resultados else '⚠️ '} {len(bolsa_familia_resultados)} registro(s)")

# 2. Servidores
print("\n[2/7] Consultando Servidores Públicos...")
mes_atual = datetime.now().strftime('%Y%m')
result_servidores = consultar_endpoint(
    '/servidores',
    {'cpf': CPF, 'mesAnoReferencia': mes_atual, 'pagina': 1},
    'Servidores'
)
resultados['servidores'] = result_servidores
print(f"   {'✅' if result_servidores['count'] > 0 else '⚠️ '} {result_servidores['count']} registro(s)")

# 3. CEIS
print("\n[3/7] Consultando CEIS...")
result_ceis = consultar_endpoint(
    '/ceis',
    {'cpfOuCnpj': CPF, 'pagina': 1},
    'CEIS'
)
resultados['ceis'] = result_ceis
print(f"   {'✅' if result_ceis['count'] > 0 else '⚠️ '} {result_ceis['count']} registro(s)")

# 4. CNEP
print("\n[4/7] Consultando CNEP...")
result_cnep = consultar_endpoint(
    '/cnep',
    {'cpfOuCnpj': CPF, 'pagina': 1},
    'CNEP'
)
resultados['cnep'] = result_cnep
print(f"   {'✅' if result_cnep['count'] > 0 else '⚠️ '} {result_cnep['count']} registro(s)")

# 5. Despesas
print("\n[5/7] Consultando Despesas...")
mes_inicio = (datetime.now() - timedelta(days=365)).strftime('%Y%m')
mes_fim = datetime.now().strftime('%Y%m')
result_despesas = consultar_endpoint(
    '/despesas/documentos',
    {'cpfCnpjFornecedor': CPF, 'mesAnoInicio': mes_inicio, 'mesAnoFim': mes_fim, 'pagina': 1},
    'Despesas'
)
resultados['despesas'] = result_despesas
print(f"   {'✅' if result_despesas['count'] > 0 else '⚠️ '} {result_despesas['count']} registro(s)")

# 6. Convênios
print("\n[6/7] Consultando Convênios...")
data_inicio = (datetime.now() - timedelta(days=365)).strftime('%d/%m/%Y')
data_fim = datetime.now().strftime('%d/%m/%Y')
result_convenios = consultar_endpoint(
    '/convenios',
    {'cpfCnpjProponente': CPF, 'dataInicialCelebracao': data_inicio, 'dataFinalCelebracao': data_fim, 'pagina': 1},
    'Convênios'
)
resultados['convenios'] = result_convenios
print(f"   {'✅' if result_convenios['count'] > 0 else '⚠️ '} {result_convenios['count']} registro(s)")

# 7. Contratos
print("\n[7/7] Consultando Contratos...")
data_inicio_contrato = (datetime.now() - timedelta(days=365)).strftime('%d/%m/%Y')
data_fim_contrato = datetime.now().strftime('%d/%m/%Y')
result_contratos = consultar_endpoint(
    '/contratos',
    {'cpfCnpjContratado': CPF, 'dataInicial': data_inicio_contrato, 'dataFinal': data_fim_contrato, 'pagina': 1},
    'Contratos'
)
resultados['contratos'] = result_contratos
print(f"   {'✅' if result_contratos['count'] > 0 else '⚠️ '} {result_contratos['count']} registro(s)")

# Resumo
print("\n" + "=" * 80)
print("📊 RESUMO DOS RESULTADOS")
print("=" * 80)

total_registros = 0
for categoria, resultado in resultados.items():
    count = resultado.get('count', 0)
    status_emoji = '✅' if count > 0 else '⚠️'
    print(f"{status_emoji} {categoria.replace('_', ' ').title()}: {count} registro(s)")
    total_registros += count

print(f"\n📈 Total: {total_registros} registro(s) encontrado(s)")

# Detalhes
if total_registros > 0:
    print("\n" + "=" * 80)
    print("📋 DETALHES DOS RESULTADOS")
    print("=" * 80)
    
    for categoria, resultado in resultados.items():
        if resultado['count'] > 0:
            print(f"\n📌 {categoria.replace('_', ' ').title()}:")
            print("-" * 80)
            try:
                df = pd.DataFrame(resultado['data'])
                print(df.to_string(index=False))
            except:
                print(json.dumps(resultado['data'][:3], indent=2, ensure_ascii=False))

print("\n" + "=" * 80)
print("✅ Teste concluído!")
print("=" * 80)
