#!/usr/bin/env python3
"""
CAMADA BRONZE - Ingestão de Dados Brutos
Coleta dados de APIs governamentais e armazena em formato Parquet
"""

import requests
import pandas as pd
from minio import Minio
from minio.error import S3Error
import io
from datetime import datetime
import json
import random

# Configurações
import os

# Ler chave API de variável de ambiente ou usar padrão
# Tenta várias possibilidades de nomes de variáveis
PORTAL_TRANSPARENCIA_API_KEY = (
    os.getenv('PORTAL_TRANSPARENCIA_API_KEY') or 
    os.getenv('TRANSPARENCIA_API_KEY') or 
    os.getenv('PORTAL_API_KEY') or 
    os.getenv('GOVBR_API_KEY') or 
    os.getenv('API_KEY') or 
    os.getenv('CHAVE_API_DADOS') or
    "2c56919ba91b8c1b13473dcef43fb031"  # Fallback padrão
)

# Debug: mostrar qual chave está sendo usada (apenas primeiros caracteres)
if PORTAL_TRANSPARENCIA_API_KEY and PORTAL_TRANSPARENCIA_API_KEY != "2c56919ba91b8c1b13473dcef43fb031":
    print(f"🔑 Usando chave API de variável de ambiente: {PORTAL_TRANSPARENCIA_API_KEY[:20]}...")
else:
    print("⚠️  Usando chave API padrão (configure PORTAL_TRANSPARENCIA_API_KEY no env para dados reais)")

MINIO_SERVER_URL = os.getenv('MINIO_SERVER_URL') or "ch8ai-minio.l6zv5a.easypanel.host"
MINIO_ROOT_USER = os.getenv('MINIO_ROOT_USER') or "admin"
MINIO_ROOT_PASSWORD = os.getenv('MINIO_ROOT_PASSWORD') or "1q2w3e4r"
BUCKET_NAME = "govbr"

# API migrada - usar HTTPS no novo endpoint
transparency_url_novo = "https://api.portaldatransparencia.gov.br/api-de-dados"
transparency_url_antigo = "https://portaldatransparencia.gov.br/api-de-dados"
transparency_url = transparency_url_novo  # Usar novo endpoint por padrão
ibge_url = "https://servicodados.ibge.gov.br/api/v1"

headers = {
    'chave-api-dados': PORTAL_TRANSPARENCIA_API_KEY
}

# Cliente MinIO
minio_client = Minio(
    MINIO_SERVER_URL,
    access_key=MINIO_ROOT_USER,
    secret_key=MINIO_ROOT_PASSWORD,
    secure=True
)

# Verificar/criar bucket
if not minio_client.bucket_exists(BUCKET_NAME):
    minio_client.make_bucket(BUCKET_NAME)
    print(f"✅ Bucket '{BUCKET_NAME}' criado")

def save_to_bronze(df, dataset_name, source, partition_date=None):
    """Salva DataFrame na camada Bronze em formato Parquet"""
    if partition_date is None:
        partition_date = datetime.now().strftime('%Y%m%d')

    object_name = f"bronze/{source}/{dataset_name}/dt={partition_date}/data.parquet"

    try:
        # Converter para Parquet
        buffer = io.BytesIO()
        df.to_parquet(buffer, index=False, engine='pyarrow', compression='snappy')
        buffer.seek(0)

        # Upload para MinIO
        minio_client.put_object(
            BUCKET_NAME,
            object_name,
            buffer,
            length=buffer.getbuffer().nbytes,
            content_type='application/octet-stream'
        )

        print(f"✅ Bronze: {object_name} ({len(df)} registros, {buffer.getbuffer().nbytes/1024:.2f} KB)")
        return True
    except Exception as e:
        print(f"❌ Erro ao salvar {object_name}: {e}")
        return False

print("=" * 80)
print("CAMADA BRONZE - INGESTÃO DE DADOS BRUTOS")
print("=" * 80)

# 1. IBGE - Municípios
print("\n[1/5] Coletando municípios do Brasil (IBGE)...")
response = requests.get(f"{ibge_url}/localidades/municipios", timeout=30)
if response.status_code == 200:
    municipios = response.json()
    municipios_data = []
    for m in municipios:
        try:
            microrregiao = m.get('microrregiao', {})
            mesorregiao = microrregiao.get('mesorregiao', {}) if microrregiao else {}
            uf = mesorregiao.get('UF', {}) if mesorregiao else {}
            regiao = uf.get('regiao', {}) if uf else {}
            
            municipios_data.append({
                'codigo_ibge': m.get('id'),
                'municipio': m.get('nome'),
                'uf_sigla': uf.get('sigla'),
                'uf_nome': uf.get('nome'),
                'regiao_id': regiao.get('id'),
                'regiao_nome': regiao.get('nome'),
                'microrregiao_id': microrregiao.get('id') if microrregiao else None,
                'microrregiao_nome': microrregiao.get('nome') if microrregiao else None,
                'mesorregiao_id': mesorregiao.get('id') if mesorregiao else None,
                'mesorregiao_nome': mesorregiao.get('nome') if mesorregiao else None
            })
        except Exception as e:
            print(f"  ⚠️  Erro ao processar município {m.get('id', 'N/A')}: {e}")
            continue
    
    df_municipios = pd.DataFrame(municipios_data)

    save_to_bronze(df_municipios, 'municipios', 'ibge')
else:
    print(f"❌ Erro ao coletar municípios: {response.status_code}")

# 2. IBGE - Estados
print("\n[2/5] Coletando estados do Brasil (IBGE)...")
response = requests.get(f"{ibge_url}/localidades/estados", timeout=30)
if response.status_code == 200:
    estados = response.json()
    df_estados = pd.DataFrame([{
        'uf_id': e['id'],
        'uf_sigla': e['sigla'],
        'uf_nome': e['nome'],
        'regiao_id': e['regiao']['id'],
        'regiao_sigla': e['regiao']['sigla'],
        'regiao_nome': e['regiao']['nome']
    } for e in estados])

    save_to_bronze(df_estados, 'estados', 'ibge')
else:
    print(f"❌ Erro ao coletar estados: {response.status_code}")

# 3. Portal da Transparência - Órgãos SIAFI
print("\n[3/5] Coletando órgãos SIAFI...")
response = requests.get(f"{transparency_url}/orgaos-siafi", headers=headers, timeout=30)
if response.status_code == 200:
    orgaos = response.json()
    df_orgaos = pd.DataFrame(orgaos)
    # Filtrar órgãos válidos
    df_orgaos = df_orgaos[~df_orgaos['descricao'].str.contains('CODIGO INVALIDO', na=False)]

    save_to_bronze(df_orgaos, 'orgaos_siafi', 'portal_transparencia')
else:
    print(f"❌ Erro ao coletar órgãos: {response.status_code}")

# 4. Portal da Transparência - BPC por município (amostra de SP)
print("\n[4/5] Coletando dados de BPC (amostra SP - primeiros 50 municípios)...")

# Pegar municípios de SP
if 'df_municipios' in locals() and df_municipios is not None and len(df_municipios) > 0:
    df_municipios_sp = df_municipios[df_municipios['uf_sigla'] == 'SP'].head(50)
else:
    print("  ⚠️  Municípios não disponíveis, pulando coleta de BPC")
    df_municipios_sp = pd.DataFrame()
bpc_data = []

if len(df_municipios_sp) > 0:
    for idx, row in df_municipios_sp.iterrows():
        codigo = str(row['codigo_ibge'])
        nome = row['municipio']

        if idx % 10 == 0:
            print(f"  Progresso: {idx}/{len(df_municipios_sp)} municípios...")

        try:
            response = requests.get(
                f"{transparency_url}/bpc-por-municipio",
                headers=headers,
                params={'mesAno': '202412', 'codigoIbge': codigo, 'pagina': 1},
                timeout=10
            )

            if response.status_code == 200 and response.json():
                data = response.json()[0]
                # Flatten nested structure
                record = {
                    'id': data.get('id'),
                    'data_referencia': data.get('dataReferencia'),
                    'codigo_ibge': data['municipio']['codigoIBGE'],
                    'nome_municipio': data['municipio']['nomeIBGE'],
                    'uf_sigla': data['municipio']['uf']['sigla'],
                    'uf_nome': data['municipio']['uf']['nome'],
                    'regiao_nome': data['municipio']['nomeRegiao'],
                    'tipo_id': data['tipo']['id'],
                    'tipo_descricao': data['tipo']['descricao'],
                    'tipo_descricao_detalhada': data['tipo']['descricaoDetalhada'],
                    'valor': data.get('valor'),
                    'quantidade_beneficiados': data.get('quantidadeBeneficiados')
                }
                bpc_data.append(record)
        except Exception as e:
            print(f"  ⚠️  Erro em {nome}: {e}")

if len(df_municipios_sp) > 0 and bpc_data:
    df_bpc = pd.DataFrame(bpc_data)
    save_to_bronze(df_bpc, 'bpc_municipios', 'portal_transparencia')
    print(f"  ✅ {len(bpc_data)} municípios com dados de BPC")
else:
    print("  ❌ Nenhum dado de BPC coletado")

# 4b. Portal da Transparência - Bolsa Família por município
print("\n[4b/5] Coletando dados de Bolsa Família por município...")

bolsa_familia_data = []

# Coletar para todos os municípios (ou amostra se muitos)
if 'df_municipios' in locals() and len(df_municipios) > 0:
    # Usar todos os municípios ou amostra de até 500 para não demorar muito
    municipios_para_bolsa = df_municipios.head(500) if len(df_municipios) > 500 else df_municipios
    print(f"  Coletando Bolsa Família para {len(municipios_para_bolsa)} municípios...")
    
    municipios_para_processar = municipios_para_bolsa
elif len(df_municipios_sp) > 0:
    # Fallback: usar apenas SP se não tiver todos os municípios
    municipios_para_processar = df_municipios_sp.head(50)
    print(f"  Coletando Bolsa Família para {len(municipios_para_processar)} municípios de SP...")
else:
    municipios_para_processar = pd.DataFrame()

if len(municipios_para_processar) > 0:
    for idx, row in municipios_para_processar.iterrows():
        codigo = str(row['codigo_ibge'])
        nome = row['municipio']

        if idx % 10 == 0:
            print(f"  Progresso: {idx}/{len(municipios_para_processar)} municípios...")

        try:
            # API de Bolsa Família por município
            # Tentar vários períodos (incluindo períodos mais antigos onde há dados disponíveis)
            # Dados disponíveis a partir de 2021
            periodos_para_tentar = [
                '202412', '202411', '202410', '202409', '202408',
                '202407', '202406', '202405', '202404', '202403',
                '202312', '202311', '202310', '202309', '202308',
                '202307', '202306', '202305', '202304', '202303',
                '202302', '202301', '202212', '202211', '202210',
                '202209', '202208', '202207', '202206', '202205',
                '202204', '202203', '202202', '202201', '202112',
                '202111', '202110', '202109', '202108', '202107',
                '202106', '202105', '202104', '202103', '202102',
                '202101'
            ]
            
            dados_encontrados = False
            endpoints_para_tentar = [
                '/bolsa-familia-por-municipio',  # Endpoint original
                '/novo-bolsa-familia-por-municipio',  # Novo endpoint encontrado na documentação
            ]
            
            for endpoint_path in endpoints_para_tentar:
                if dados_encontrados:
                    break
                    
                for periodo in periodos_para_tentar:
                    try:
                        response = requests.get(
                            f"{transparency_url}{endpoint_path}",
                            headers=headers,
                            params={'mesAno': periodo, 'codigoIbge': codigo, 'pagina': 1},
                            timeout=8,
                            allow_redirects=True
                        )
                        
                        # Se retornar 401, a chave pode estar inválida ou o endpoint requer autenticação diferente
                        if response.status_code == 401:
                            # Tentar sem chave (alguns endpoints públicos não requerem)
                            response = requests.get(
                                f"{transparency_url}{endpoint_path}",
                                headers={'Accept': 'application/json'},
                                params={'mesAno': periodo, 'codigoIbge': codigo, 'pagina': 1},
                                timeout=8,
                                allow_redirects=True
                            )

                        if response.status_code == 200:
                            data_list = response.json()
                            if isinstance(data_list, list) and len(data_list) > 0:
                                data = data_list[0]
                                record = {
                                    'id': data.get('id'),
                                    'data_referencia': data.get('dataReferencia') or f"{periodo[:4]}-{periodo[4:]}-01",
                                    'codigo_ibge': data['municipio']['codigoIBGE'] if 'municipio' in data and isinstance(data['municipio'], dict) and 'codigoIBGE' in data['municipio'] else codigo,
                                    'nome_municipio': data['municipio']['nomeIBGE'] if 'municipio' in data and isinstance(data['municipio'], dict) and 'nomeIBGE' in data['municipio'] else nome,
                                    'uf_sigla': data['municipio']['uf']['sigla'] if 'municipio' in data and isinstance(data['municipio'], dict) and 'uf' in data['municipio'] and isinstance(data['municipio']['uf'], dict) else row['uf_sigla'],
                                    'uf_nome': data['municipio']['uf']['nome'] if 'municipio' in data and isinstance(data['municipio'], dict) and 'uf' in data['municipio'] and isinstance(data['municipio']['uf'], dict) else None,
                                    'regiao_nome': data['municipio'].get('nomeRegiao') if 'municipio' in data and isinstance(data['municipio'], dict) else None,
                                    'valor_total': data.get('valor') or data.get('valorTotal'),
                                    'quantidade_beneficiarios': data.get('quantidadeBeneficiados') or data.get('quantidadeBeneficiarios') or data.get('quantidade')
                                }
                                bolsa_familia_data.append(record)
                                dados_encontrados = True
                                break  # Dados encontrados, parar de tentar outros períodos
                    except:
                        continue  # Tentar próximo período
            
            if not dados_encontrados:
                # Se nenhum período retornou dados, não adicionar nada (será gerado simulado depois)
                pass
        except Exception as e:
            # Se a API não retornar dados, tentar estrutura alternativa
            try:
                # Tentar endpoint alternativo
                response = requests.get(
                    f"{transparency_url}/auxilio-emergencial-por-municipio",
                    headers=headers,
                    params={'mesAno': '202412', 'codigoIbge': codigo, 'pagina': 1},
                    timeout=10
                )
                if response.status_code == 200 and response.json():
                    data_list = response.json()
                    if isinstance(data_list, list) and len(data_list) > 0:
                        data = data_list[0]
                        record = {
                            'id': data.get('id'),
                            'data_referencia': data.get('dataReferencia'),
                            'codigo_ibge': codigo,
                            'nome_municipio': nome,
                            'uf_sigla': row['uf_sigla'],
                            'valor_total': data.get('valor'),
                            'quantidade_beneficiarios': data.get('quantidadeBeneficiarios')
                        }
                        bolsa_familia_data.append(record)
            except Exception as e2:
                print(f"  ⚠️  Erro em {nome}: {e2}")

if len(bolsa_familia_data) > 0:
    df_bolsa_familia = pd.DataFrame(bolsa_familia_data)
    save_to_bronze(df_bolsa_familia, 'bolsa_familia_municipios', 'portal_transparencia')
    print(f"  ✅ {len(bolsa_familia_data)} municípios com dados REAIS de Bolsa Família")
else:
    print("  ⚠️  AVISO: Nenhum dado REAL de Bolsa Família coletado da API")
    print("  ⚠️  A API retorna lista vazia para todos os períodos testados")
    print("  💡 Verifique:")
    print("     1. Se a chave API está válida")
    print("     2. Se há dados disponíveis para os períodos testados")
    print("     3. Documentação: https://api.portaldatransparencia.gov.br/swagger-ui.html")
    print("  ⚠️  Continuando com outros dados (população, etc)...")
    # Não falhar aqui - continuar para coletar população

# 5. IBGE - População por MUNICÍPIO (dados detalhados)
print("\n[5/6] Coletando população por MUNICÍPIO...")
populacao_municipios_data = []

try:
    if 'df_municipios' not in locals() or df_municipios is None or len(df_municipios) == 0:
        raise Exception("Municípios não disponíveis")
    
    # Coletar população para todos os municípios (ou amostra se muitos)
    municipios_para_coletar = df_municipios.head(1000) if len(df_municipios) > 1000 else df_municipios
    
    print(f"  Coletando população para {len(municipios_para_coletar)} municípios...")
    
    for idx, row in municipios_para_coletar.iterrows():
        codigo_ibge = str(row['codigo_ibge'])
        
        if idx % 100 == 0 and idx > 0:
            print(f"  Progresso: {idx}/{len(municipios_para_coletar)} municípios...")
        
        try:
            # API IBGE - Estimativa de população por município
            # Endpoint correto: /pesquisas/23/resultados/{codigo_ibge}
            # Código 23 = Estimativas de População
            # O código IBGE precisa ser sem os últimos 2 dígitos para alguns endpoints
            codigo_ibge_6digitos = codigo_ibge[:6]  # Primeiros 6 dígitos
            
            response = requests.get(
                f"{ibge_url}/pesquisas/23/resultados/{codigo_ibge}",
                timeout=8
            )
            
            if response.status_code == 200:
                data = response.json()
                if data and isinstance(data, list) and len(data) > 0:
                    # Procurar dados de 2024 ou mais recente
                    for item in data:
                        if 'res' in item and isinstance(item['res'], list):
                            for res_item in item['res']:
                                if 'res' in res_item and isinstance(res_item['res'], dict):
                                    # Procurar ano mais recente (2024, 2023, etc)
                                    anos_disponiveis = [int(ano) for ano in res_item['res'].keys() if ano.isdigit()]
                                    if anos_disponiveis:
                                        ano_mais_recente = max(anos_disponiveis)
                                        populacao = res_item['res'].get(str(ano_mais_recente))
                                        if populacao:
                                            populacao_municipios_data.append({
                                                'codigo_ibge': codigo_ibge,
                                                'nome_municipio': row['municipio'],
                                                'uf_sigla': row['uf_sigla'],
                                                'ano': ano_mais_recente,
                                                'populacao': int(populacao)
                                            })
                                            break
                    # Se não encontrou dados estruturados, tentar formato alternativo
                    if len([d for d in populacao_municipios_data if d['codigo_ibge'] == codigo_ibge]) == 0:
                        # Tentar extrair de formato diferente
                        primeiro_item = data[0]
                        if 'res' in primeiro_item:
                            res_data = primeiro_item['res']
                            if isinstance(res_data, list) and len(res_data) > 0:
                                res_item = res_data[0]
                                if 'res' in res_item and isinstance(res_item['res'], dict):
                                    # Pegar o último ano disponível
                                    anos = [int(k) for k in res_item['res'].keys() if k.isdigit()]
                                    if anos:
                                        ano = max(anos)
                                        populacao = int(res_item['res'][str(ano)])
                                        populacao_municipios_data.append({
                                            'codigo_ibge': codigo_ibge,
                                            'nome_municipio': row['municipio'],
                                            'uf_sigla': row['uf_sigla'],
                                            'ano': ano,
                                            'populacao': populacao
                                        })
        except Exception as e:
            # Se API falhar, não usar dados do dataframe - apenas dados reais da API
            continue
    
    if populacao_municipios_data and len(populacao_municipios_data) > 0:
        df_populacao_municipios = pd.DataFrame(populacao_municipios_data)
        print(f"  ✅ {len(df_populacao_municipios)} municípios com dados de população")
        save_to_bronze(df_populacao_municipios, 'populacao_municipios', 'ibge')
    else:
        raise Exception("Nenhum dado de população por município coletado")
        
except Exception as e:
    print(f"  ❌ ERRO ao coletar população por município: {e}")
    print("  ⚠️  Não foi possível coletar dados REAIS de população por município")
    print("  💡 Verifique:")
    print("     1. Se a API do IBGE está disponível")
    print("     2. Documentação: https://servicodados.ibge.gov.br/api/docs")
    raise RuntimeError("Não foi possível coletar dados REAIS de população por município.")

# 6. IBGE - População estimada por estado (dados agregados) - mantido para compatibilidade
print("\n[6/6] Coletando estimativas de população por estado (agregado)...")
try:
    populacao_estados_data = []
    if 'df_estados' not in locals() or df_estados is None or len(df_estados) == 0:
        raise Exception("Estados não disponíveis")
    
    for idx, row in df_estados.iterrows():
        uf_id = row['uf_id']
        uf_sigla = row['uf_sigla']

        response = requests.get(
            f"{ibge_url}/projecoes/populacao/{uf_id}",
            timeout=10
        )

        if response.status_code == 200:
            data = response.json()
            if data and 'projecao' in data:
                populacao_estados_data.append({
                    'uf_id': uf_id,
                    'uf_sigla': uf_sigla,
                    'ano': 2024,
                    'populacao': data['projecao']['populacao']
                })

    if populacao_estados_data and len(populacao_estados_data) > 0:
        df_populacao_estados = pd.DataFrame(populacao_estados_data)
        print(f"  ✅ {len(df_populacao_estados)} estados com dados de população da API")
        save_to_bronze(df_populacao_estados, 'populacao_estados', 'ibge')
    else:
        raise Exception("Nenhum dado de população coletado da API")
except Exception as e:
    print(f"  ⚠️  Endpoint de população não disponível, usando dados manuais: {e}")
    populacao_manual = [
        {'uf_sigla': 'AC', 'uf_id': 12, 'ano': 2024, 'populacao': 906876},
        {'uf_sigla': 'AL', 'uf_id': 27, 'ano': 2024, 'populacao': 3365351},
        {'uf_sigla': 'AP', 'uf_id': 16, 'ano': 2024, 'populacao': 877613},
        {'uf_sigla': 'AM', 'uf_id': 13, 'ano': 2024, 'populacao': 4308055},
        {'uf_sigla': 'BA', 'uf_id': 29, 'ano': 2024, 'populacao': 14985284},
        {'uf_sigla': 'CE', 'uf_id': 23, 'ano': 2024, 'populacao': 9240580},
        {'uf_sigla': 'DF', 'uf_id': 53, 'ano': 2024, 'populacao': 3094325},
        {'uf_sigla': 'ES', 'uf_id': 32, 'ano': 2024, 'populacao': 4108508},
        {'uf_sigla': 'GO', 'uf_id': 52, 'ano': 2024, 'populacao': 7206589},
        {'uf_sigla': 'MA', 'uf_id': 21, 'ano': 2024, 'populacao': 7153262},
        {'uf_sigla': 'MT', 'uf_id': 51, 'ano': 2024, 'populacao': 3567234},
        {'uf_sigla': 'MS', 'uf_id': 50, 'ano': 2024, 'populacao': 2839188},
        {'uf_sigla': 'MG', 'uf_id': 31, 'ano': 2024, 'populacao': 21411923},
        {'uf_sigla': 'PA', 'uf_id': 15, 'ano': 2024, 'populacao': 8777124},
        {'uf_sigla': 'PB', 'uf_id': 25, 'ano': 2024, 'populacao': 4059905},
        {'uf_sigla': 'PR', 'uf_id': 41, 'ano': 2024, 'populacao': 11597484},
        {'uf_sigla': 'PE', 'uf_id': 26, 'ano': 2024, 'populacao': 9674793},
        {'uf_sigla': 'PI', 'uf_id': 22, 'ano': 2024, 'populacao': 3289290},
        {'uf_sigla': 'RJ', 'uf_id': 33, 'ano': 2024, 'populacao': 17463349},
        {'uf_sigla': 'RN', 'uf_id': 24, 'ano': 2024, 'populacao': 3560903},
        {'uf_sigla': 'RS', 'uf_id': 43, 'ano': 2024, 'populacao': 11422973},
        {'uf_sigla': 'RO', 'uf_id': 11, 'ano': 2024, 'populacao': 1815278},
        {'uf_sigla': 'RR', 'uf_id': 14, 'ano': 2024, 'populacao': 652713},
        {'uf_sigla': 'SC', 'uf_id': 42, 'ano': 2024, 'populacao': 8064521},
        {'uf_sigla': 'SP', 'uf_id': 35, 'ano': 2024, 'populacao': 46649132},
        {'uf_sigla': 'SE', 'uf_id': 28, 'ano': 2024, 'populacao': 2351592},
        {'uf_sigla': 'TO', 'uf_id': 17, 'ano': 2024, 'populacao': 1607363},
    ]
    df_populacao_estados = pd.DataFrame(populacao_manual)
    print(f"  ✅ {len(df_populacao_estados)} estados com dados manuais de população")
    save_to_bronze(df_populacao_estados, 'populacao_estados', 'ibge')

print("\n" + "=" * 80)
print("RESUMO DA INGESTÃO")
print("=" * 80)

# Listar arquivos Bronze
objects = minio_client.list_objects(BUCKET_NAME, prefix="bronze/", recursive=True)
bronze_files = list(objects)

print(f"\nTotal de arquivos na camada Bronze: {len(bronze_files)}")
total_size = 0
for obj in bronze_files:
    size_kb = obj.size / 1024
    total_size += obj.size
    print(f"  📁 {obj.object_name} ({size_kb:.2f} KB)")

print(f"\nTamanho total: {total_size/1024:.2f} KB")
print("\n✅ Ingestão Bronze concluída!")
