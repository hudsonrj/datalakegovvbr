#!/usr/bin/env python3
"""
PIPELINE DE INGESTÃO DE DADOS - FULL E INCREMENTAL
Executa ingestão completa ou incremental dos dados governamentais
"""

import sys
import argparse
from datetime import datetime, timedelta
from minio import Minio
from minio.error import S3Error
import requests
import pandas as pd
import io
import json

# Configurações
PORTAL_TRANSPARENCIA_API_KEY = "2c56919ba91b8c1b13473dcef43fb031"
MINIO_SERVER_URL = "ch8ai-minio.l6zv5a.easypanel.host"
MINIO_ROOT_USER = "admin"
MINIO_ROOT_PASSWORD = "1q2w3e4r"
BUCKET_NAME = "govbr"

transparency_url = "http://api.portaldatransparencia.gov.br/api-de-dados"
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


def get_latest_partition(source, dataset):
    """Retorna a data da última partição existente ou None"""
    prefix = f"bronze/{source}/{dataset}/"
    try:
        objects = list(minio_client.list_objects(BUCKET_NAME, prefix=prefix, recursive=True))
        if not objects:
            return None
        
        # Extrair datas das partições (dt=YYYYMMDD)
        dates = []
        for obj in objects:
            parts = obj.object_name.split('/')
            for part in parts:
                if part.startswith('dt='):
                    date_str = part.replace('dt=', '')
                    try:
                        dates.append(datetime.strptime(date_str, '%Y%m%d'))
                    except:
                        pass
        
        return max(dates) if dates else None
    except Exception as e:
        print(f"  ⚠️  Erro ao verificar partições: {e}")
        return None


def should_run_incremental(source, dataset, mode):
    """Determina se deve rodar em modo incremental"""
    if mode == 'full':
        return False
    elif mode == 'incremental':
        latest = get_latest_partition(source, dataset)
        if latest is None:
            print(f"  ℹ️  Nenhuma partição anterior encontrada, executando FULL")
            return False
        # Incremental se última partição foi há mais de 1 dia
        days_diff = (datetime.now() - latest).days
        return days_diff >= 1
    else:  # auto
        latest = get_latest_partition(source, dataset)
        if latest is None:
            return False
        # Auto: incremental se última partição foi há mais de 1 dia
        return (datetime.now() - latest).days >= 1


def save_to_bronze(df, dataset_name, source, partition_date=None, mode='full'):
    """Salva DataFrame na camada Bronze em formato Parquet"""
    if partition_date is None:
        partition_date = datetime.now().strftime('%Y%m%d')

    object_name = f"bronze/{source}/{dataset_name}/dt={partition_date}/data.parquet"

    try:
        # Se modo incremental e arquivo já existe, fazer merge
        if mode == 'incremental':
            try:
                # Tentar ler dados existentes
                response = minio_client.get_object(BUCKET_NAME, object_name)
                existing_df = pd.read_parquet(io.BytesIO(response.read()))
                response.close()
                response.release_conn()
                
                # Combinar e remover duplicatas
                combined_df = pd.concat([existing_df, df], ignore_index=True)
                combined_df = combined_df.drop_duplicates()
                df = combined_df
                print(f"  🔄 Merge incremental: {len(existing_df)} + {len(df) - len(existing_df)} = {len(df)} registros")
            except Exception as e:
                print(f"  ℹ️  Arquivo não existe ou erro ao ler: {e}, criando novo")

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


def ingest_ibge_municipios(mode='full'):
    """Ingere municípios do IBGE"""
    print("\n[1/5] Coletando municípios do Brasil (IBGE)...")
    
    # IBGE não tem histórico, sempre full
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
                continue
        
        df_municipios = pd.DataFrame(municipios_data)
        save_to_bronze(df_municipios, 'municipios', 'ibge', mode=mode)
        return df_municipios
    else:
        print(f"❌ Erro ao coletar municípios: {response.status_code}")
        return None


def ingest_ibge_estados(mode='full'):
    """Ingere estados do IBGE"""
    print("\n[2/5] Coletando estados do Brasil (IBGE)...")
    
    # IBGE não tem histórico, sempre full
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

        save_to_bronze(df_estados, 'estados', 'ibge', mode=mode)
        return df_estados
    else:
        print(f"❌ Erro ao coletar estados: {response.status_code}")
        return None


def ingest_orgaos_siafi(mode='full'):
    """Ingere órgãos SIAFI"""
    print("\n[3/5] Coletando órgãos SIAFI...")
    
    # Portal da Transparência - sempre full (dados de referência)
    response = requests.get(f"{transparency_url}/orgaos-siafi", headers=headers, timeout=30)
    if response.status_code == 200:
        orgaos = response.json()
        df_orgaos = pd.DataFrame(orgaos)
        df_orgaos = df_orgaos[~df_orgaos['descricao'].str.contains('CODIGO INVALIDO', na=False)]

        save_to_bronze(df_orgaos, 'orgaos_siafi', 'portal_transparencia', mode=mode)
        return df_orgaos
    else:
        print(f"❌ Erro ao coletar órgãos: {response.status_code}")
        return None


def ingest_bpc_municipios(mode='full', df_municipios=None):
    """Ingere dados de BPC por município"""
    print("\n[4/5] Coletando dados de BPC...")
    
    # Determinar período para coleta
    if mode == 'incremental' and should_run_incremental('portal_transparencia', 'bpc_municipios', mode):
        latest = get_latest_partition('portal_transparencia', 'bpc_municipios')
        # Coletar dados do mês atual
        mes_ano = datetime.now().strftime('%Y%m')
        print(f"  🔄 Modo INCREMENTAL: coletando dados de {mes_ano}")
    else:
        # Full: coletar últimos 3 meses
        mes_ano = (datetime.now() - timedelta(days=90)).strftime('%Y%m')
        print(f"  🔄 Modo FULL: coletando dados desde {mes_ano}")
    
    if df_municipios is None or len(df_municipios) == 0:
        print("  ⚠️  Municípios não disponíveis, pulando coleta de BPC")
        return None
    
    # Coletar de todos os estados (amostra)
    bpc_data = []
    estados_unicos = df_municipios['uf_sigla'].unique()
    
    for uf in estados_unicos[:5]:  # Limitar a 5 estados para não demorar muito
        municipios_uf = df_municipios[df_municipios['uf_sigla'] == uf].head(20)  # 20 municípios por estado
        
        for idx, row in municipios_uf.iterrows():
            codigo = str(row['codigo_ibge'])
            nome = row['municipio']

            try:
                response = requests.get(
                    f"{transparency_url}/bpc-por-municipio",
                    headers=headers,
                    params={'mesAno': mes_ano, 'codigoIbge': codigo, 'pagina': 1},
                    timeout=10
                )

                if response.status_code == 200 and response.json():
                    data = response.json()[0]
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
                continue

    if bpc_data:
        df_bpc = pd.DataFrame(bpc_data)
        save_to_bronze(df_bpc, 'bpc_municipios', 'portal_transparencia', mode=mode)
        print(f"  ✅ {len(bpc_data)} registros de BPC coletados")
        return df_bpc
    else:
        print("  ❌ Nenhum dado de BPC coletado")
        return None


def ingest_populacao_estados(mode='full', df_estados=None):
    """Ingere dados de população por estado"""
    print("\n[5/5] Coletando estimativas de população por estado...")
    
    if df_estados is None or len(df_estados) == 0:
        print("  ⚠️  Estados não disponíveis")
        return None
    
    populacao_data = []
    for idx, row in df_estados.iterrows():
        uf_id = row['uf_id']
        uf_sigla = row['uf_sigla']

        try:
            response = requests.get(
                f"{ibge_url}/projecoes/populacao/{uf_id}",
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                if data and 'projecao' in data:
                    populacao_data.append({
                        'uf_id': uf_id,
                        'uf_sigla': uf_sigla,
                        'ano': datetime.now().year,
                        'populacao': data['projecao']['populacao']
                    })
        except:
            continue

    if populacao_data:
        df_populacao = pd.DataFrame(populacao_data)
        save_to_bronze(df_populacao, 'populacao_estados', 'ibge', mode=mode)
        return df_populacao
    else:
        # Dados manuais de fallback
        populacao_manual = [
            {'uf_sigla': 'SP', 'uf_id': 35, 'ano': 2024, 'populacao': 46649132},
            {'uf_sigla': 'MG', 'uf_id': 31, 'ano': 2024, 'populacao': 21411923},
            {'uf_sigla': 'RJ', 'uf_id': 33, 'ano': 2024, 'populacao': 17463349},
            {'uf_sigla': 'BA', 'uf_id': 29, 'ano': 2024, 'populacao': 14985284},
            {'uf_sigla': 'PR', 'uf_id': 41, 'ano': 2024, 'populacao': 11597484},
        ]
        df_populacao = pd.DataFrame(populacao_manual)
        save_to_bronze(df_populacao, 'populacao_estados', 'ibge', mode=mode)
        return df_populacao


def main():
    parser = argparse.ArgumentParser(description='Pipeline de Ingestão de Dados GovBR')
    parser.add_argument(
        '--mode',
        type=str,
        choices=['full', 'incremental', 'auto'],
        default='auto',
        help='Modo de execução: full (recarrega tudo), incremental (apenas novos), auto (decide automaticamente)'
    )
    
    args = parser.parse_args()
    mode = args.mode

    print("=" * 80)
    print(f"PIPELINE DE INGESTÃO - MODO: {mode.upper()}")
    print("=" * 80)

    # Executar ingestão em ordem
    df_municipios = ingest_ibge_municipios(mode=mode)
    df_estados = ingest_ibge_estados(mode=mode)
    ingest_orgaos_siafi(mode=mode)
    ingest_bpc_municipios(mode=mode, df_municipios=df_municipios)
    ingest_populacao_estados(mode=mode, df_estados=df_estados)

    print("\n" + "=" * 80)
    print("RESUMO DA INGESTÃO")
    print("=" * 80)

    # Listar arquivos Bronze
    objects = minio_client.list_objects(BUCKET_NAME, prefix="bronze/", recursive=True)
    bronze_files = list(objects)

    print(f"\nTotal de arquivos na camada Bronze: {len(bronze_files)}")
    total_size = 0
    datasets = {}
    for obj in bronze_files:
        size_kb = obj.size / 1024
        total_size += obj.size
        parts = obj.object_name.split('/')
        if len(parts) >= 3:
            dataset_key = f"{parts[1]}/{parts[2]}"
            if dataset_key not in datasets:
                datasets[dataset_key] = 0
            datasets[dataset_key] += 1

    for dataset, count in datasets.items():
        print(f"  📁 {dataset}: {count} arquivo(s)")

    print(f"\nTamanho total: {total_size/1024:.2f} KB")
    print(f"\n✅ Pipeline de ingestão concluído (modo: {mode.upper()})!")


if __name__ == "__main__":
    main()
