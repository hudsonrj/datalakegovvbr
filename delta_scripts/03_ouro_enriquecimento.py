#!/usr/bin/env python3
"""
CAMADA OURO - Enriquecimento e Dados Finais
Enriquece dados da camada Prata com métricas avançadas e análises prontas para consumo
"""

import pandas as pd
from minio import Minio
from minio.error import S3Error
import io
from datetime import datetime

# Configurações
MINIO_SERVER_URL = "ch8ai-minio.l6zv5a.easypanel.host"
MINIO_ROOT_USER = "admin"
MINIO_ROOT_PASSWORD = "1q2w3e4r"
BUCKET_NAME = "govbr"

# Cliente MinIO
minio_client = Minio(
    MINIO_SERVER_URL,
    access_key=MINIO_ROOT_USER,
    secret_key=MINIO_ROOT_PASSWORD,
    secure=True
)

def read_from_prata(dataset_name, partition_date=None):
    """Lê DataFrame da camada Prata"""
    if partition_date is None:
        # Buscar a partição mais recente
        prefix = f"prata/{dataset_name}/"
        objects = list(minio_client.list_objects(BUCKET_NAME, prefix=prefix, recursive=True))
        if not objects:
            return None
        
        # Pegar o mais recente
        latest = max(objects, key=lambda x: x.last_modified)
        object_name = latest.object_name
    else:
        object_name = f"prata/{dataset_name}/dt={partition_date}/data.parquet"
    
    try:
        response = minio_client.get_object(BUCKET_NAME, object_name)
        df = pd.read_parquet(io.BytesIO(response.read()))
        response.close()
        response.release_conn()
        print(f"✅ Lido Prata: {object_name} ({len(df)} registros)")
        return df
    except Exception as e:
        print(f"❌ Erro ao ler {object_name}: {e}")
        return None

def save_to_ouro(df, dataset_name, partition_date=None):
    """Salva DataFrame na camada Ouro em formato Parquet"""
    if partition_date is None:
        partition_date = datetime.now().strftime('%Y%m%d')
    
    object_name = f"ouro/{dataset_name}/dt={partition_date}/data.parquet"
    
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
        
        print(f"✅ Ouro: {object_name} ({len(df)} registros, {buffer.getbuffer().nbytes/1024:.2f} KB)")
        return True
    except Exception as e:
        print(f"❌ Erro ao salvar {object_name}: {e}")
        return False

print("=" * 80)
print("CAMADA OURO - ENRIQUECIMENTO E DADOS FINAIS")
print("=" * 80)

# 1. Ler dados da Prata
print("\n[1/5] Carregando dados da camada Prata...")

dim_municipios = read_from_prata('dim_municipios')
dim_estados = read_from_prata('dim_estados')
fato_bpc = read_from_prata('fato_bpc')
fato_bolsa_familia = read_from_prata('fato_bolsa_familia')
dim_orgaos = read_from_prata('dim_orgaos')

if dim_municipios is None or dim_estados is None:
    print("❌ Erro: Dados essenciais não encontrados na Prata")
    exit(1)

# 2. Enriquecer Dimensão de Municípios
print("\n[2/5] Enriquecendo dimensão de municípios...")

ouro_municipios = dim_municipios.copy()

# Adicionar classificações
if 'populacao' in ouro_municipios.columns:
    ouro_municipios['classificacao_populacao'] = pd.cut(
        ouro_municipios['populacao'],
        bins=[0, 5000, 20000, 100000, 500000, float('inf')],
        labels=['Muito Pequeno', 'Pequeno', 'Médio', 'Grande', 'Muito Grande']
    )

# Adicionar indicadores regionais
if 'regiao_nome' in ouro_municipios.columns:
    ouro_municipios['regiao_sigla'] = ouro_municipios['regiao_nome'].map({
        'Norte': 'N',
        'Nordeste': 'NE',
        'Centro-Oeste': 'CO',
        'Sudeste': 'SE',
        'Sul': 'S'
    })

# Adicionar timestamp de processamento
ouro_municipios['data_processamento'] = datetime.now()
ouro_municipios['versao_dados'] = '1.0'

save_to_ouro(ouro_municipios, 'municipios_enriquecidos')

# 3. Enriquecer Dimensão de Estados
print("\n[3/5] Enriquecendo dimensão de estados...")

ouro_estados = dim_estados.copy()

# Adicionar métricas avançadas
if 'populacao' in ouro_estados.columns:
    ouro_estados['classificacao_populacao'] = pd.cut(
        ouro_estados['populacao'],
        bins=[0, 5000000, 10000000, 20000000, float('inf')],
        labels=['Pequeno', 'Médio', 'Grande', 'Muito Grande']
    )
    
    # Densidade populacional (estimada)
    ouro_estados['densidade_populacional'] = ouro_estados['populacao'] / 1000  # Simplificado

# Adicionar indicadores de BPC
if 'total_valor_bpc' in ouro_estados.columns:
    ouro_estados['indicador_bpc_alto'] = ouro_estados['total_valor_bpc'] > ouro_estados['total_valor_bpc'].median()
    ouro_estados['ranking_valor_bpc'] = ouro_estados['total_valor_bpc'].rank(ascending=False, method='dense')

# Adicionar timestamp
ouro_estados['data_processamento'] = datetime.now()
ouro_estados['versao_dados'] = '1.0'

save_to_ouro(ouro_estados, 'estados_enriquecidos')

# 4. Criar Fato BPC Enriquecido
print("\n[4/5] Criando fato BPC enriquecido...")

if fato_bpc is not None and len(fato_bpc) > 0:
    ouro_fato_bpc = fato_bpc.copy()
    
    # Adicionar métricas temporais
    if 'mes' in ouro_fato_bpc.columns:
        ouro_fato_bpc['trimestre'] = ouro_fato_bpc['mes'].apply(
            lambda x: f"T{(x-1)//3 + 1}" if pd.notna(x) else None
        )
        ouro_fato_bpc['semestre'] = ouro_fato_bpc['mes'].apply(
            lambda x: 'S1' if pd.notna(x) and x <= 6 else ('S2' if pd.notna(x) else None)
        )
    
    # Adicionar classificações de valor
    if 'valor' in ouro_fato_bpc.columns:
        ouro_fato_bpc['faixa_valor'] = pd.cut(
            ouro_fato_bpc['valor'],
            bins=[0, 100000, 1000000, 10000000, float('inf')],
            labels=['Baixo', 'Médio', 'Alto', 'Muito Alto']
        )
    
    # Adicionar classificações de beneficiados
    if 'quantidade_beneficiados' in ouro_fato_bpc.columns:
        ouro_fato_bpc['faixa_beneficiados'] = pd.cut(
            ouro_fato_bpc['quantidade_beneficiados'],
            bins=[0, 100, 1000, 10000, float('inf')],
            labels=['Poucos', 'Moderado', 'Muitos', 'Muitíssimos']
        )
    
    # Adicionar indicadores calculados
    if 'valor_per_capita' in ouro_fato_bpc.columns:
        median_valor = ouro_fato_bpc['valor_per_capita'].median()
        if pd.notna(median_valor) and median_valor != 0:
            ouro_fato_bpc['indicador_eficiencia'] = (
                ouro_fato_bpc['valor_per_capita'] / median_valor
            )
    
    # Adicionar timestamp
    ouro_fato_bpc['data_processamento'] = datetime.now()
    ouro_fato_bpc['versao_dados'] = '1.0'
    
    save_to_ouro(ouro_fato_bpc, 'bpc_analytics')
else:
    print("⚠️  Dados de BPC não disponíveis para enriquecimento")

# 4b. Criar Analytics de Bolsa Família
print("\n[4b/5] Criando analytics de Bolsa Família...")

if fato_bolsa_familia is not None and len(fato_bolsa_familia) > 0:
    ouro_bf_analytics = fato_bolsa_familia.copy()
    
    # Adicionar métricas temporais
    if 'mes' in ouro_bf_analytics.columns:
        ouro_bf_analytics['trimestre'] = ouro_bf_analytics['mes'].apply(
            lambda x: f"T{(x-1)//3 + 1}" if pd.notna(x) else None
        )
        ouro_bf_analytics['semestre'] = ouro_bf_analytics['mes'].apply(
            lambda x: 'S1' if pd.notna(x) and x <= 6 else ('S2' if pd.notna(x) else None)
        )
    
    # Adicionar classificações
    if 'quantidade_beneficiarios' in ouro_bf_analytics.columns:
        ouro_bf_analytics['faixa_beneficiarios'] = pd.cut(
            ouro_bf_analytics['quantidade_beneficiarios'],
            bins=[0, 500, 2000, 10000, float('inf')],
            labels=['Pequeno', 'Médio', 'Grande', 'Muito Grande']
        )
    
    if 'percentual_beneficiarios' in ouro_bf_analytics.columns:
        ouro_bf_analytics['faixa_percentual'] = pd.cut(
            ouro_bf_analytics['percentual_beneficiarios'],
            bins=[0, 10, 20, 30, float('inf')],
            labels=['Baixo', 'Médio', 'Alto', 'Muito Alto']
        )
    
    # Adicionar timestamp
    ouro_bf_analytics['data_processamento'] = datetime.now()
    ouro_bf_analytics['versao_dados'] = '1.0'
    
    # Adicionar ao bpc_analytics ou criar dataset separado
    # Por enquanto, vamos adicionar ao bpc_analytics se existir
    try:
        # Tentar ler bpc_analytics existente
        prefix = f"ouro/bpc_analytics/"
        objects = list(minio_client.list_objects(BUCKET_NAME, prefix=prefix, recursive=True))
        if objects:
            # Combinar com BPC se existir
            ouro_bf_analytics['tipo_programa'] = 'Bolsa Família'
            if fato_bpc is not None and len(fato_bpc) > 0:
                ouro_fato_bpc['tipo_programa'] = 'BPC'
                df_analytics_combinado = pd.concat([ouro_fato_bpc, ouro_bf_analytics], ignore_index=True)
                save_to_ouro(df_analytics_combinado, 'bpc_analytics')
            else:
                save_to_ouro(ouro_bf_analytics, 'bpc_analytics')
        else:
            save_to_ouro(ouro_bf_analytics, 'bpc_analytics')
    except:
        save_to_ouro(ouro_bf_analytics, 'bpc_analytics')
    
    print(f"  ✅ Analytics de Bolsa Família criado ({len(ouro_bf_analytics)} registros)")
else:
    print("⚠️  Dados de Bolsa Família não disponíveis para enriquecimento")

# 5. Criar Tabelas de Agregação e Análise
print("\n[5/5] Criando tabelas agregadas para análise...")

# Agregação por Região
if fato_bpc is not None and len(fato_bpc) > 0:
    if 'regiao_nome' in fato_bpc.columns:
        agregacao_regiao = fato_bpc.groupby('regiao_nome').agg({
            'valor': ['sum', 'mean', 'median'],
            'quantidade_beneficiados': ['sum', 'mean'],
            'valor_per_capita': 'mean'
        }).reset_index()
    
        agregacao_regiao.columns = [
            'regiao_nome',
            'total_valor',
            'media_valor',
            'mediana_valor',
            'total_beneficiados',
            'media_beneficiados',
            'media_valor_per_capita'
        ]
        
        agregacao_regiao['data_processamento'] = datetime.now()
        agregacao_regiao['versao_dados'] = '1.0'
        
        # Salvar como agregacoes_regionais (nome esperado pelo DEMO)
        agregacao_regiao['tipo_agregacao'] = 'regiao'
        save_to_ouro(agregacao_regiao, 'agregacoes_regionais')
    
    # Agregação por Estado
    if 'uf_sigla' in fato_bpc.columns:
        groupby_cols = ['uf_sigla']
        if 'uf_nome' in fato_bpc.columns:
            groupby_cols.append('uf_nome')
        
        agregacao_estado = fato_bpc.groupby(groupby_cols).agg({
            'valor': ['sum', 'mean'],
            'quantidade_beneficiados': ['sum', 'mean'],
            'valor_per_capita': 'mean'
        }).reset_index()
    
        col_names = ['uf_sigla']
        if 'uf_nome' in fato_bpc.columns:
            col_names.append('uf_nome')
        col_names.extend(['total_valor', 'media_valor', 'total_beneficiados', 'media_beneficiados', 'media_valor_per_capita'])
        
        agregacao_estado.columns = col_names
        
        agregacao_estado['data_processamento'] = datetime.now()
        agregacao_estado['versao_dados'] = '1.0'
        
        # Adicionar ao agregacoes_regionais também
        agregacao_estado['tipo_agregacao'] = 'estado'
        # Ler agregacoes existentes e adicionar
        try:
            prefix = f"ouro/agregacoes_regionais/"
            objects = list(minio_client.list_objects(BUCKET_NAME, prefix=prefix, recursive=True))
            if objects:
                latest = max(objects, key=lambda x: x.last_modified)
                response = minio_client.get_object(BUCKET_NAME, latest.object_name)
                df_agreg_existente = pd.read_parquet(io.BytesIO(response.read()))
                response.close()
                response.release_conn()
                # Combinar
                df_agreg_combinado = pd.concat([df_agreg_existente, agregacao_estado], ignore_index=True)
                save_to_ouro(df_agreg_combinado, 'agregacoes_regionais')
            else:
                save_to_ouro(agregacao_estado, 'agregacoes_regionais')
        except:
            # Se não conseguir ler, criar novo
            save_to_ouro(agregacao_estado, 'agregacoes_regionais')
    
    # Top 10 municípios por valor
    if 'valor' in fato_bpc.columns:
        top_cols = ['uf_sigla', 'valor']
        if 'nome_municipio' in fato_bpc.columns:
            top_cols.insert(0, 'nome_municipio')
        if 'quantidade_beneficiados' in fato_bpc.columns:
            top_cols.append('quantidade_beneficiados')
        
        top_municipios_valor = (
            fato_bpc.nlargest(10, 'valor')[top_cols]
            .copy()
        )
        top_municipios_valor['data_processamento'] = datetime.now()
        top_municipios_valor['versao_dados'] = '1.0'
        
        save_to_ouro(top_municipios_valor, 'top_10_municipios_valor_bpc')
        
        # Criar rankings consolidados
        rankings_data = []
        
        # Ranking por valor total
        if 'valor' in fato_bpc.columns:
            top_valor = fato_bpc.nlargest(20, 'valor')
            for idx, row in top_valor.iterrows():
                rankings_data.append({
                    'tipo_ranking': 'valor_total',
                    'posicao': len(rankings_data) + 1,
                    'municipio': row.get('nome_municipio', 'N/A'),
                    'uf_sigla': row.get('uf_sigla', 'N/A'),
                    'valor': row.get('valor', 0),
                    'quantidade_beneficiados': row.get('quantidade_beneficiados', 0)
                })
        
        # Ranking por beneficiários
        if 'quantidade_beneficiados' in fato_bpc.columns:
            top_benef = fato_bpc.nlargest(20, 'quantidade_beneficiados')
            for idx, row in top_benef.iterrows():
                rankings_data.append({
                    'tipo_ranking': 'beneficiarios',
                    'posicao': len([r for r in rankings_data if r['tipo_ranking'] == 'beneficiarios']) + 1,
                    'municipio': row.get('nome_municipio', 'N/A'),
                    'uf_sigla': row.get('uf_sigla', 'N/A'),
                    'valor': row.get('valor', 0),
                    'quantidade_beneficiados': row.get('quantidade_beneficiados', 0)
                })
        
        if rankings_data:
            df_rankings = pd.DataFrame(rankings_data)
            df_rankings['data_processamento'] = datetime.now()
            df_rankings['versao_dados'] = '1.0'
            save_to_ouro(df_rankings, 'rankings')

# Criar tabela de resumo geral
resumo_geral = pd.DataFrame({
    'metrica': [
        'Total Municípios',
        'Total Estados',
        'Total Registros BPC',
        'Data Processamento'
    ],
    'valor_texto': [
        str(len(ouro_municipios)),
        str(len(ouro_estados)),
        str(len(ouro_fato_bpc) if fato_bpc is not None else 0),
        datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    ],
    'valor_numerico': [
        len(ouro_municipios),
        len(ouro_estados),
        len(ouro_fato_bpc) if fato_bpc is not None else 0,
        None
    ]
})

save_to_ouro(resumo_geral, 'resumo_geral')

print("\n" + "=" * 80)
print("RESUMO DO ENRIQUECIMENTO OURO")
print("=" * 80)
print(f"\n✅ Municípios enriquecidos: {len(ouro_municipios)}")
print(f"✅ Estados enriquecidos: {len(ouro_estados)}")
if fato_bpc is not None:
    print(f"✅ Registros BPC enriquecidos: {len(ouro_fato_bpc)}")

# Listar arquivos Ouro
objects = minio_client.list_objects(BUCKET_NAME, prefix="ouro/", recursive=True)
ouro_files = list(objects)

print(f"\nTotal de arquivos na camada Ouro: {len(ouro_files)}")
total_size = 0
for obj in ouro_files:
    size_kb = obj.size / 1024
    total_size += obj.size
    print(f"  📁 {obj.object_name} ({size_kb:.2f} KB)")

print(f"\nTamanho total: {total_size/1024:.2f} KB")
print("\n✅ Enriquecimento Ouro concluído!")
