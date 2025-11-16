#!/usr/bin/env python3
"""
Script para executar o pipeline completo:
1. Gerar massa de dados na Bronze
2. Normalizar endereços e salvar na Prata
3. Criar ranking e salvar na Ouro
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gerar_massa_cidadaos_bronze import gerar_massa_cidadaos
from minio import Minio
import io
import pandas as pd
from datetime import datetime
from normalizar_enderecos_brasileiros import NormalizadorEndereco

# Configurações
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

def read_from_bronze():
    """Lê dados da Bronze"""
    prefix = "bronze/simulado/cidadaos/"
    objects = list(minio_client.list_objects(BUCKET_NAME, prefix=prefix, recursive=True))
    if not objects:
        return None
    
    latest = max(objects, key=lambda x: x.last_modified)
    response = minio_client.get_object(BUCKET_NAME, latest.object_name)
    df = pd.read_parquet(io.BytesIO(response.read()))
    response.close()
    response.release_conn()
    print(f"✅ Lido Bronze: {latest.object_name} ({len(df)} registros)")
    return df

def save_to_prata(df, dataset_name, partition_date=None):
    """Salva DataFrame na camada Prata"""
    if partition_date is None:
        partition_date = datetime.now().strftime('%Y%m%d')
    
    object_name = f"prata/{dataset_name}/dt={partition_date}/data.parquet"
    
    try:
        buffer = io.BytesIO()
        df.to_parquet(buffer, index=False, engine='pyarrow', compression='snappy')
        buffer.seek(0)
        
        minio_client.put_object(
            BUCKET_NAME,
            object_name,
            buffer,
            length=buffer.getbuffer().nbytes,
            content_type='application/octet-stream'
        )
        
        tamanho_mb = buffer.getbuffer().nbytes / 1024 / 1024
        print(f"✅ Prata: {object_name} ({len(df):,} registros, {tamanho_mb:.2f} MB)")
        return True
    except Exception as e:
        print(f"❌ Erro ao salvar {object_name}: {e}")
        return False

def normalizar_enderecos():
    """Normaliza endereços da Bronze e salva na Prata"""
    print("\n" + "=" * 80)
    print("NORMALIZAÇÃO DE ENDEREÇOS - BRONZE → PRATA")
    print("=" * 80)
    
    # Carregar dados da Bronze
    df_bronze = read_from_bronze()
    if df_bronze is None:
        print("❌ Nenhum dado encontrado na Bronze")
        return False
    
    print(f"\n🔄 Normalizando {len(df_bronze):,} endereços...")
    
    # Inicializar normalizador
    normalizador = NormalizadorEndereco()
    
    # Normalizar endereços
    dados_normalizados = []
    total = len(df_bronze)
    
    for idx, row in df_bronze.iterrows():
        componentes = normalizador.normalizar(row['endereco'])
        endereco_normalizado = normalizador.normalizar_completo(row['endereco'])
        
        registro = {
            'cpf': row['cpf'],
            'nome': row['nome'],
            'telefone': row['telefone'],
            'tipo_telefone': row['tipo_telefone'],
            'email': row['email'],
            'numero_endereco': row['numero_endereco'],
            'total_enderecos': row['total_enderecos'],
            'endereco_original': row['endereco'],
            'endereco_normalizado': endereco_normalizado,
            'tipo_logradouro': componentes.get('tipo_logradouro'),
            'nome_logradouro': componentes.get('nome_logradouro'),
            'numero_imovel': componentes.get('numero'),
            'complemento': componentes.get('complemento'),
            'bairro': componentes.get('bairro'),
            'municipio': componentes.get('municipio'),
            'uf': componentes.get('uf'),
            'cep': componentes.get('cep'),
            'tem_complemento': componentes.get('complemento') is not None,
            'tem_bairro': componentes.get('bairro') is not None,
            'tem_municipio': componentes.get('municipio') is not None,
            'tem_uf': componentes.get('uf') is not None,
            'tem_cep': componentes.get('cep') is not None,
            'completo': all([
                componentes.get('tipo_logradouro'),
                componentes.get('nome_logradouro'),
                componentes.get('numero'),
                componentes.get('bairro'),
                componentes.get('municipio'),
                componentes.get('uf'),
                componentes.get('cep')
            ])
        }
        
        dados_normalizados.append(registro)
        
        if (idx + 1) % 10000 == 0:
            progresso = ((idx + 1) / total) * 100
            print(f"  Progresso: {idx + 1:,}/{total:,} ({progresso:.1f}%)")
    
    # Criar DataFrame
    df_prata = pd.DataFrame(dados_normalizados)
    
    print(f"\n✅ Normalização concluída!")
    print(f"   • Total: {len(df_prata):,} registros")
    print(f"   • Completos: {df_prata['completo'].sum():,} ({df_prata['completo'].sum()/len(df_prata)*100:.1f}%)")
    
    # Salvar na Prata
    return save_to_prata(df_prata, 'cidadaos_enderecos_normalizados')

if __name__ == "__main__":
    print("=" * 80)
    print("PIPELINE COMPLETO - BRONZE → PRATA")
    print("=" * 80)
    
    # Passo 1: Gerar dados na Bronze (se necessário)
    print("\n[1/2] Verificando dados na Bronze...")
    df_bronze = read_from_bronze()
    
    if df_bronze is None or len(df_bronze) < 1000000:
        print(f"\n[1/2] Gerando massa de dados na Bronze...")
        print("⚠️  Isso pode demorar vários minutos para 1 milhão de cidadãos...")
        gerar_massa_cidadaos(1000000)
    else:
        print(f"✅ Dados já existem na Bronze: {len(df_bronze):,} registros")
    
    # Passo 2: Normalizar e salvar na Prata
    print("\n[2/2] Normalizando endereços e salvando na Prata...")
    sucesso = normalizar_enderecos()
    
    if sucesso:
        print("\n" + "=" * 80)
        print("✅ PIPELINE CONCLUÍDO COM SUCESSO!")
        print("=" * 80)
    else:
        print("\n" + "=" * 80)
        print("❌ ERRO NO PIPELINE")
        print("=" * 80)
