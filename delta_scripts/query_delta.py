#!/usr/bin/env python3
"""
Script para consultar dados Delta Lake como banco relacional
"""

from pyspark.sql import SparkSession
from delta import configure_spark_with_delta_pip

# Configurações MinIO
MINIO_ENDPOINT = "ch8ai-minio.l6zv5a.easypanel.host"
MINIO_ACCESS_KEY = "admin"
MINIO_SECRET_KEY = "1q2w3e4r"
BUCKET_NAME = "govbr"

# Configurar Spark com Delta Lake
builder = SparkSession.builder \
    .appName("GovBR Delta Lake Query") \
    .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension") \
    .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog") \
    .config("spark.hadoop.fs.s3a.endpoint", f"https://{MINIO_ENDPOINT}") \
    .config("spark.hadoop.fs.s3a.access.key", MINIO_ACCESS_KEY) \
    .config("spark.hadoop.fs.s3a.secret.key", MINIO_SECRET_KEY) \
    .config("spark.hadoop.fs.s3a.path.style.access", "true") \
    .config("spark.hadoop.fs.s3a.connection.ssl.enabled", "true") \
    .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem")

spark = configure_spark_with_delta_pip(builder).getOrCreate()

# Registrar tabelas Delta
s3_base = f"s3a://{BUCKET_NAME}/delta"

tables_config = {
    "bronze_municipios": f"{s3_base}/bronze/bronze_municipios",
    "bronze_estados": f"{s3_base}/bronze/bronze_estados",
    "bronze_bpc": f"{s3_base}/bronze/bronze_bpc",
    "prata_dim_municipios": f"{s3_base}/prata/prata_dim_municipios",
    "prata_dim_estados": f"{s3_base}/prata/prata_dim_estados",
    "prata_fato_bpc": f"{s3_base}/prata/prata_fato_bpc",
    "ouro_dim_municipios": f"{s3_base}/ouro/ouro_dim_municipios",
    "ouro_dim_estados": f"{s3_base}/ouro/ouro_dim_estados",
    "ouro_fato_bpc": f"{s3_base}/ouro/ouro_fato_bpc",
    "ouro_agregacao_regiao": f"{s3_base}/ouro/ouro_agregacao_regiao",
    "ouro_agregacao_estado": f"{s3_base}/ouro/ouro_agregacao_estado",
    "ouro_top_municipios": f"{s3_base}/ouro/ouro_top_municipios"
}

print("=" * 80)
print("REGISTRANDO TABELAS DELTA LAKE")
print("=" * 80)

for table_name, delta_path in tables_config.items():
    try:
        spark.sql(f"""
            CREATE TABLE IF NOT EXISTS {table_name}
            USING DELTA
            LOCATION '{delta_path}'
        """)
        print(f"  ✅ {table_name}")
    except Exception as e:
        print(f"  ⚠️  {table_name}: {e}")

# Exemplos de consultas SQL
print("\n" + "=" * 80)
print("EXEMPLOS DE CONSULTAS SQL")
print("=" * 80)

# 1. Consulta simples
print("\n1. Top 5 estados por população:")
try:
    spark.sql("""
        SELECT uf_sigla, uf_nome, populacao 
        FROM ouro_dim_estados 
        WHERE populacao IS NOT NULL
        ORDER BY populacao DESC 
        LIMIT 5
    """).show(truncate=False)
except Exception as e:
    print(f"Erro: {e}")

# 2. Join entre tabelas
print("\n2. BPC por estado com informações de população:")
try:
    spark.sql("""
        SELECT 
            e.uf_sigla,
            e.uf_nome,
            e.populacao,
            SUM(f.valor) as total_bpc,
            SUM(f.quantidade_beneficiados) as total_beneficiados
        FROM ouro_fato_bpc f
        JOIN ouro_dim_estados e ON f.uf_sigla = e.uf_sigla
        GROUP BY e.uf_sigla, e.uf_nome, e.populacao
        ORDER BY total_bpc DESC
    """).show(truncate=False)
except Exception as e:
    print(f"Erro: {e}")

# 3. Agregações
print("\n3. Agregação por região:")
try:
    spark.sql("""
        SELECT 
            regiao_nome,
            COUNT(*) as total_municipios,
            AVG(populacao) as media_populacao
        FROM ouro_dim_municipios
        WHERE regiao_nome IS NOT NULL
        GROUP BY regiao_nome
        ORDER BY total_municipios DESC
    """).show(truncate=False)
except Exception as e:
    print(f"Erro: {e}")

# 4. Top municípios
print("\n4. Top 10 municípios por valor BPC:")
try:
    spark.sql("""
        SELECT 
            nome_municipio,
            uf_sigla,
            valor,
            quantidade_beneficiados
        FROM ouro_top_municipios
        ORDER BY valor DESC
    """).show(truncate=False)
except Exception as e:
    print(f"Erro: {e}")

print("\n" + "=" * 80)
print("✅ Consultas executadas!")
print("=" * 80)
print("\nVocê pode executar consultas SQL diretamente usando:")
print("  spark.sql('SELECT * FROM ouro_dim_estados').show()")

spark.stop()
