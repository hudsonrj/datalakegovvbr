# Delta Lake - GovBR

Este projeto configura Delta Lake para ler os dados do MinIO como um banco relacional.

## 🚀 Início Rápido

### Opção 1: Usar Docker Compose (Recomendado)

```bash
# 1. Criar diretórios necessários
mkdir -p delta_scripts notebooks

# 2. Subir containers
docker-compose up -d

# 3. Executar setup inicial (converter Parquet para Delta)
docker exec -it govbr-delta-lake python /opt/spark/work-dir/delta_setup.py

# 4. Acessar Jupyter Lab
# Abra: http://localhost:8889
```

### Opção 2: Executar Localmente

```bash
# 1. Instalar dependências
pip install delta-spark pyspark s3fs boto3

# 2. Executar setup
python delta_scripts/delta_setup.py

# 3. Executar consultas
python delta_scripts/query_delta.py
```

## 📊 Estrutura de Tabelas

### Camada Bronze
- `bronze_municipios` - Municípios do IBGE
- `bronze_estados` - Estados do IBGE
- `bronze_bpc` - Dados BPC brutos
- `bronze_orgaos` - Órgãos SIAFI

### Camada Prata
- `prata_dim_municipios` - Dimensão de municípios tratada
- `prata_dim_estados` - Dimensão de estados tratada
- `prata_fato_bpc` - Fato BPC tratado
- `prata_dim_orgaos` - Dimensão de órgãos

### Camada Ouro
- `ouro_dim_municipios` - Municípios enriquecidos
- `ouro_dim_estados` - Estados enriquecidos
- `ouro_fato_bpc` - Fato BPC enriquecido
- `ouro_agregacao_regiao` - Agregação por região
- `ouro_agregacao_estado` - Agregação por estado
- `ouro_top_municipios` - Top 10 municípios

## 🔍 Exemplos de Consultas SQL

### Consulta Simples
```sql
SELECT * FROM ouro_dim_estados LIMIT 10;
```

### Join entre Tabelas
```sql
SELECT 
    e.uf_sigla,
    e.uf_nome,
    SUM(f.valor) as total_bpc
FROM ouro_fato_bpc f
JOIN ouro_dim_estados e ON f.uf_sigla = e.uf_sigla
GROUP BY e.uf_sigla, e.uf_nome
ORDER BY total_bpc DESC;
```

### Agregações
```sql
SELECT 
    regiao_nome,
    COUNT(*) as total_municipios,
    AVG(populacao) as media_populacao
FROM ouro_dim_municipios
GROUP BY regiao_nome;
```

## 🐍 Usando Python/Spark

```python
from pyspark.sql import SparkSession
from delta import configure_spark_with_delta_packages

# Configurar Spark
builder = SparkSession.builder \
    .appName("GovBR Delta") \
    .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension") \
    .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog")

spark = configure_spark_with_delta_packages(builder).getOrCreate()

# Ler tabela Delta
df = spark.read.format("delta").table("ouro_dim_estados")
df.show()

# Consulta SQL
spark.sql("SELECT * FROM ouro_dim_estados LIMIT 10").show()
```

## 🔧 Configuração

### Variáveis de Ambiente
- `AWS_ACCESS_KEY_ID`: Chave de acesso MinIO (admin)
- `AWS_SECRET_ACCESS_KEY`: Chave secreta MinIO
- `AWS_ENDPOINT_URL`: URL do MinIO
- `MINIO_BUCKET`: Nome do bucket (govbr)

### Portas
- `8080`: Spark UI
- `4040`: Spark Application UI
- `8889`: Jupyter Lab

## 📝 Notas

- Delta Lake fornece transações ACID sobre dados Parquet
- Suporta versionamento e time travel
- Compatível com SQL padrão
- Integração nativa com Spark

## 🆘 Troubleshooting

### Erro de conexão com MinIO
Verifique se as credenciais estão corretas e o endpoint está acessível.

### Tabelas não encontradas
Execute `delta_setup.py` para converter Parquet em Delta Lake.

### Problemas com SSL
Se houver problemas com SSL, ajuste `spark.hadoop.fs.s3a.connection.ssl.enabled` para `false`.
