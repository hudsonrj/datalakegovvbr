#!/usr/bin/env python3
"""
Solução SIMPLES usando DuckDB para ler Parquet como banco relacional
NÃO precisa de Docker, Spark ou Delta Lake!
"""

import duckdb
import pandas as pd
from minio import Minio
import io

# Configurações MinIO
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

def read_parquet_from_minio(path):
    """Lê arquivo Parquet do MinIO"""
    try:
        response = minio_client.get_object(BUCKET_NAME, path)
        df = pd.read_parquet(io.BytesIO(response.read()))
        response.close()
        response.release_conn()
        return df
    except Exception as e:
        print(f"❌ Erro ao ler {path}: {e}")
        return None

print("=" * 80)
print("SOLUÇÃO SIMPLES - DUCKDB (SEM DOCKER!)")
print("=" * 80)

# Criar conexão DuckDB (banco em memória)
conn = duckdb.connect()

# 1. Carregar dados da camada Ouro
print("\n[1/3] Carregando dados...")

# Estados
df_estados = read_parquet_from_minio("ouro/dim_estados_enriquecida/dt=20251114/data.parquet")
if df_estados is not None:
    conn.register('estados', df_estados)
    print(f"  ✅ Estados carregados: {len(df_estados)} registros")

# Municípios
df_municipios = read_parquet_from_minio("ouro/dim_municipios_enriquecida/dt=20251114/data.parquet")
if df_municipios is not None:
    conn.register('municipios', df_municipios)
    print(f"  ✅ Municípios carregados: {len(df_municipios)} registros")

# Fato BPC
df_bpc = read_parquet_from_minio("ouro/fato_bpc_enriquecido/dt=20251114/data.parquet")
if df_bpc is not None:
    conn.register('bpc', df_bpc)
    print(f"  ✅ BPC carregado: {len(df_bpc)} registros")

# 2. Exemplos de Consultas SQL
print("\n[2/3] Exemplos de Consultas SQL:")
print("=" * 80)

# Consulta 1: Estados
print("\n1. Top 5 estados por população:")
result = conn.execute("""
    SELECT uf_sigla, uf_nome, populacao 
    FROM estados 
    WHERE populacao IS NOT NULL
    ORDER BY populacao DESC 
    LIMIT 5
""").fetchdf()
print(result.to_string(index=False))

# Consulta 2: Join
print("\n2. BPC por estado:")
if df_bpc is not None and df_estados is not None:
    result = conn.execute("""
        SELECT 
            e.uf_sigla,
            e.uf_nome,
            SUM(b.valor) as total_bpc,
            SUM(b.quantidade_beneficiados) as total_beneficiados
        FROM bpc b
        JOIN estados e ON b.uf_sigla = e.uf_sigla
        GROUP BY e.uf_sigla, e.uf_nome
        ORDER BY total_bpc DESC
    """).fetchdf()
    print(result.to_string(index=False))

# Consulta 3: Agregação
print("\n3. Municípios por região:")
if df_municipios is not None:
    result = conn.execute("""
        SELECT 
            regiao_nome,
            COUNT(*) as total_municipios
        FROM municipios
        WHERE regiao_nome IS NOT NULL
        GROUP BY regiao_nome
        ORDER BY total_municipios DESC
    """).fetchdf()
    print(result.to_string(index=False))

# 3. Interface Interativa
print("\n[3/3] Interface Interativa")
print("=" * 80)
print("\n✅ Você pode fazer consultas SQL agora!")
print("\nExemplos:")
print("  conn.execute('SELECT * FROM estados LIMIT 5').fetchdf()")
print("  conn.execute('SELECT * FROM bpc WHERE valor > 1000000').fetchdf()")
print("\nOu use conn.sql() para consultas mais complexas:")
print("  conn.sql('SELECT uf_sigla, COUNT(*) FROM municipios GROUP BY uf_sigla').show()")

# Manter conexão aberta para uso interativo
print("\n" + "=" * 80)
print("✅ DuckDB pronto para uso!")
print("=" * 80)
print("\nA conexão 'conn' está disponível para consultas SQL.")
print("Use: conn.execute('SUA QUERY SQL').fetchdf()")

# Exemplo de uso contínuo
print("\n" + "=" * 80)
print("EXECUTANDO CONSULTA FINAL DE EXEMPLO")
print("=" * 80)
result = conn.execute("SELECT COUNT(*) as total FROM estados").fetchdf()
print(f"Total de estados: {result['total'].iloc[0]}")

print("\n💡 Dica: Execute este script e depois use 'conn' para fazer suas consultas!")
