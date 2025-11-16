#!/usr/bin/env python3
"""
Gera relatório completo e visual para um CPF pesquisado
"""

import requests
import pandas as pd
from datetime import datetime, timedelta
import json
from minio import Minio
import io

# Configurações
PORTAL_TRANSPARENCIA_API_KEY = "2c56919ba91b8c1b13473dcef43fb031"
transparency_url = "https://api.portaldatransparencia.gov.br/api-de-dados"
MINIO_SERVER_URL = "ch8ai-minio.l6zv5a.easypanel.host"
MINIO_ROOT_USER = "admin"
MINIO_ROOT_PASSWORD = "1q2w3e4r"
BUCKET_NAME = "govbr"

headers = {
    'chave-api-dados': PORTAL_TRANSPARENCIA_API_KEY,
    'Accept': 'application/json'
}

minio_client = Minio(
    MINIO_SERVER_URL,
    access_key=MINIO_ROOT_USER,
    secret_key=MINIO_ROOT_PASSWORD,
    secure=True
)

def formatar_cpf(cpf):
    return ''.join(filter(str.isdigit, str(cpf)))

def mascarar_cpf(cpf):
    cpf_limpo = formatar_cpf(cpf)
    if len(cpf_limpo) == 11:
        return f"{cpf_limpo[:3]}.{cpf_limpo[3:6]}.{cpf_limpo[6:9]}-{cpf_limpo[9:]}"
    return cpf_limpo

def consultar_endpoint(endpoint, params):
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
                return {'status': 'success', 'data': data, 'count': len(data) if isinstance(data, list) else 1}
            return {'status': 'empty', 'data': [], 'count': 0}
        return {'status': 'error', 'data': [], 'count': 0, 'error': f"Status {response.status_code}"}
    except Exception as e:
        return {'status': 'error', 'data': [], 'count': 0, 'error': str(e)}

def salvar_relatorio_json(dados, cpf):
    """Salva relatório em JSON"""
    arquivo = f"relatorio_cpf_{cpf}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(arquivo, 'w', encoding='utf-8') as f:
        json.dump(dados, f, indent=2, ensure_ascii=False, default=str)
    return arquivo

def salvar_relatorio_minio(dados, cpf):
    """Salva relatório no MinIO"""
    try:
        arquivo_json = json.dumps(dados, indent=2, ensure_ascii=False, default=str)
        object_name = f"relatorios/cpf_{cpf}/relatorio_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        buffer = io.BytesIO(arquivo_json.encode('utf-8'))
        minio_client.put_object(
            BUCKET_NAME,
            object_name,
            buffer,
            length=len(arquivo_json.encode('utf-8')),
            content_type='application/json'
        )
        return object_name
    except Exception as e:
        print(f"⚠️  Erro ao salvar no MinIO: {e}")
        return None

# CPF para relatório
CPF_INPUT = "03388984760"
CPF = formatar_cpf(CPF_INPUT)
CPF_MASCARADO = mascarar_cpf(CPF)

print("=" * 100)
print("📊 RELATÓRIO COMPLETO - CPF: " + CPF_MASCARADO)
print("=" * 100)
print(f"Data/Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
print("=" * 100)

resultados = {}
relatorio_completo = {
    'cpf': CPF_MASCARADO,
    'cpf_limpo': CPF,
    'data_pesquisa': datetime.now().isoformat(),
    'resultados': {}
}

# 1. Bolsa Família
print("\n[1/7] 🔍 Consultando Bolsa Família...")
bolsa_familia_resultados = []
for i in range(12):
    data_ref = (datetime.now() - timedelta(days=30*i)).strftime('%Y%m')
    result = consultar_endpoint(
        '/bolsa-familia-por-cpf-ou-nis',
        {'cpfOuNis': CPF, 'mesAno': data_ref, 'pagina': 1}
    )
    if result['status'] == 'success' and result['count'] > 0:
        bolsa_familia_resultados.extend(result['data'])

resultados['bolsa_familia'] = {
    'status': 'success' if bolsa_familia_resultados else 'empty',
    'data': bolsa_familia_resultados,
    'count': len(bolsa_familia_resultados)
}
relatorio_completo['resultados']['bolsa_familia'] = resultados['bolsa_familia']
print(f"   {'✅' if bolsa_familia_resultados else '⚠️ '} {len(bolsa_familia_resultados)} registro(s)")

# 2. Servidores
print("\n[2/7] 🔍 Consultando Servidores Públicos...")
mes_atual = datetime.now().strftime('%Y%m')
result_servidores = consultar_endpoint(
    '/servidores',
    {'cpf': CPF, 'mesAnoReferencia': mes_atual, 'pagina': 1}
)
resultados['servidores'] = result_servidores
relatorio_completo['resultados']['servidores'] = result_servidores
print(f"   {'✅' if result_servidores['count'] > 0 else '⚠️ '} {result_servidores['count']} registro(s)")

# 3. CEIS
print("\n[3/7] 🔍 Consultando CEIS (Empresas Inidôneas)...")
result_ceis = consultar_endpoint('/ceis', {'cpfOuCnpj': CPF, 'pagina': 1})
resultados['ceis'] = result_ceis
relatorio_completo['resultados']['ceis'] = result_ceis
print(f"   {'✅' if result_ceis['count'] > 0 else '⚠️ '} {result_ceis['count']} registro(s)")

# 4. CNEP
print("\n[4/7] 🔍 Consultando CNEP (Empresas Punidas)...")
result_cnep = consultar_endpoint('/cnep', {'cpfOuCnpj': CPF, 'pagina': 1})
resultados['cnep'] = result_cnep
relatorio_completo['resultados']['cnep'] = result_cnep
print(f"   {'✅' if result_cnep['count'] > 0 else '⚠️ '} {result_cnep['count']} registro(s)")

# 5. Despesas
print("\n[5/7] 🔍 Consultando Despesas Públicas...")
mes_inicio = (datetime.now() - timedelta(days=365)).strftime('%Y%m')
mes_fim = datetime.now().strftime('%Y%m')
result_despesas = consultar_endpoint(
    '/despesas/documentos',
    {'cpfCnpjFornecedor': CPF, 'mesAnoInicio': mes_inicio, 'mesAnoFim': mes_fim, 'pagina': 1}
)
resultados['despesas'] = result_despesas
relatorio_completo['resultados']['despesas'] = result_despesas
print(f"   {'✅' if result_despesas['count'] > 0 else '⚠️ '} {result_despesas['count']} registro(s)")

# 6. Convênios
print("\n[6/7] 🔍 Consultando Convênios...")
data_inicio = (datetime.now() - timedelta(days=365)).strftime('%d/%m/%Y')
data_fim = datetime.now().strftime('%d/%m/%Y')
result_convenios = consultar_endpoint(
    '/convenios',
    {'cpfCnpjProponente': CPF, 'dataInicialCelebracao': data_inicio, 'dataFinalCelebracao': data_fim, 'pagina': 1}
)
resultados['convenios'] = result_convenios
relatorio_completo['resultados']['convenios'] = result_convenios
print(f"   {'✅' if result_convenios['count'] > 0 else '⚠️ '} {result_convenios['count']} registro(s)")

# 7. Contratos
print("\n[7/7] 🔍 Consultando Contratos...")
data_inicio_contrato = (datetime.now() - timedelta(days=365)).strftime('%d/%m/%Y')
data_fim_contrato = datetime.now().strftime('%d/%m/%Y')
result_contratos = consultar_endpoint(
    '/contratos',
    {'cpfCnpjContratado': CPF, 'dataInicial': data_inicio_contrato, 'dataFinal': data_fim_contrato, 'pagina': 1}
)
resultados['contratos'] = result_contratos
relatorio_completo['resultados']['contratos'] = result_contratos
print(f"   {'✅' if result_contratos['count'] > 0 else '⚠️ '} {result_contratos['count']} registro(s)")

# RESUMO
print("\n" + "=" * 100)
print("📊 RESUMO EXECUTIVO")
print("=" * 100)

total_registros = 0
resumo_tabela = []

for categoria, resultado in resultados.items():
    count = resultado.get('count', 0)
    status_emoji = '✅' if count > 0 else '⚠️'
    status_texto = 'ENCONTRADO' if count > 0 else 'NÃO ENCONTRADO'
    
    resumo_tabela.append({
        'Categoria': categoria.replace('_', ' ').title(),
        'Status': status_texto,
        'Registros': count
    })
    total_registros += count

df_resumo = pd.DataFrame(resumo_tabela)
print("\n" + df_resumo.to_string(index=False))
print(f"\n📈 TOTAL DE REGISTROS ENCONTRADOS: {total_registros}")

relatorio_completo['resumo'] = {
    'total_registros': total_registros,
    'categorias_encontradas': sum(1 for r in resultados.values() if r.get('count', 0) > 0),
    'categorias_nao_encontradas': sum(1 for r in resultados.values() if r.get('count', 0) == 0)
}

# DETALHAMENTO
print("\n" + "=" * 100)
print("📋 DETALHAMENTO POR CATEGORIA")
print("=" * 100)

# CEIS
if resultados['ceis']['count'] > 0:
    print("\n" + "─" * 100)
    print("🔴 CEIS - CADASTRO DE EMPRESAS INIDÔNEAS E SUSPENSAS")
    print("─" * 100)
    df_ceis = pd.DataFrame(resultados['ceis']['data'])
    
    # Estatísticas CEIS
    print(f"\n📊 Total de Sanções: {len(df_ceis)}")
    
    if 'tipoSancao' in df_ceis.columns:
        tipos = df_ceis['tipoSancao'].apply(lambda x: x.get('descricaoResumida', 'N/A') if isinstance(x, dict) else 'N/A')
        print(f"\n📌 Tipos de Sanções:")
        for tipo, count in tipos.value_counts().head(5).items():
            print(f"   • {tipo}: {count} ocorrência(s)")
    
    if 'dataInicioSancao' in df_ceis.columns:
        datas = pd.to_datetime(df_ceis['dataInicioSancao'], format='%d/%m/%Y', errors='coerce')
        print(f"\n📅 Período das Sanções:")
        print(f"   • Mais antiga: {datas.min().strftime('%d/%m/%Y') if not pd.isna(datas.min()) else 'N/A'}")
        print(f"   • Mais recente: {datas.max().strftime('%d/%m/%Y') if not pd.isna(datas.max()) else 'N/A'}")
    
    if 'orgaoSancionador' in df_ceis.columns:
        orgaos = df_ceis['orgaoSancionador'].apply(lambda x: x.get('nome', 'N/A') if isinstance(x, dict) else 'N/A')
        print(f"\n🏛️  Órgãos Sancionadores (Top 5):")
        for orgao, count in orgaos.value_counts().head(5).items():
            print(f"   • {orgao}: {count} sanção(ões)")
    
    print(f"\n📄 Primeiros 3 registros:")
    print(df_ceis[['id', 'dataInicioSancao', 'dataFimSancao']].head(3).to_string(index=False))
    
    relatorio_completo['analise_ceis'] = {
        'total_sancoes': len(df_ceis),
        'tipos_sancoes': tipos.value_counts().to_dict() if 'tipoSancao' in df_ceis.columns else {},
        'orgaos_sancionadores': orgaos.value_counts().head(10).to_dict() if 'orgaoSancionador' in df_ceis.columns else {}
    }

# CNEP
if resultados['cnep']['count'] > 0:
    print("\n" + "─" * 100)
    print("🟠 CNEP - CADASTRO NACIONAL DE EMPRESAS PUNIDAS")
    print("─" * 100)
    df_cnep = pd.DataFrame(resultados['cnep']['data'])
    
    print(f"\n📊 Total de Punições: {len(df_cnep)}")
    
    if 'tipoSancao' in df_cnep.columns:
        tipos = df_cnep['tipoSancao'].apply(lambda x: x.get('descricaoResumida', 'N/A') if isinstance(x, dict) else 'N/A')
        print(f"\n📌 Tipos de Punições:")
        for tipo, count in tipos.value_counts().head(5).items():
            print(f"   • {tipo}: {count} ocorrência(s)")
    
    print(f"\n📄 Primeiros 3 registros:")
    print(df_cnep[['id', 'dataInicioSancao', 'dataFimSancao']].head(3).to_string(index=False))
    
    relatorio_completo['analise_cnep'] = {
        'total_punicoes': len(df_cnep),
        'tipos_punicoes': tipos.value_counts().to_dict() if 'tipoSancao' in df_cnep.columns else {}
    }

# Outras categorias (se houver dados)
for categoria in ['bolsa_familia', 'servidores', 'despesas', 'convenios', 'contratos']:
    if resultados[categoria]['count'] > 0:
        print(f"\n" + "─" * 100)
        print(f"📌 {categoria.replace('_', ' ').title().upper()}")
        print("─" * 100)
        df = pd.DataFrame(resultados[categoria]['data'])
        print(f"\nTotal: {len(df)} registro(s)")
        print(df.head(5).to_string(index=False))

# SALVAR RELATÓRIO
print("\n" + "=" * 100)
print("💾 SALVANDO RELATÓRIO")
print("=" * 100)

# Salvar JSON local
arquivo_json = salvar_relatorio_json(relatorio_completo, CPF)
print(f"✅ Relatório JSON salvo: {arquivo_json}")

# Salvar no MinIO
arquivo_minio = salvar_relatorio_minio(relatorio_completo, CPF)
if arquivo_minio:
    print(f"✅ Relatório salvo no MinIO: {arquivo_minio}")

# RESUMO FINAL
print("\n" + "=" * 100)
print("✅ RELATÓRIO GERADO COM SUCESSO")
print("=" * 100)
print(f"\n📊 Resumo:")
print(f"   • CPF: {CPF_MASCARADO}")
print(f"   • Total de registros: {total_registros}")
print(f"   • Categorias com dados: {relatorio_completo['resumo']['categorias_encontradas']}")
print(f"   • Arquivo gerado: {arquivo_json}")
print("\n" + "=" * 100)
