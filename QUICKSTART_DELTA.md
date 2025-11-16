# 🚀 Quick Start - Delta Lake GovBR

Guia rápido para usar Delta Lake e ler dados como banco relacional.

## Opção 1: Usar Jupyter (Mais Simples) ⭐

```bash
# 1. Iniciar container
./iniciar_delta_lake.sh
# Escolha opção 1

# 2. Acessar Jupyter Lab
# Abra: http://localhost:8889

# 3. No Jupyter, executar:
exec(open('/home/jovyan/work/delta_setup_spark.py').read())
```

## Opção 2: Usar Spark Completo

```bash
# 1. Iniciar containers
docker-compose up -d

# 2. Converter Parquet para Delta
docker exec -it govbr-delta-lake python /opt/spark/work-dir/delta_setup.py

# 3. Executar consultas
docker exec -it govbr-delta-lake python /opt/spark/work-dir/query_delta.py
```

## 📊 Consultas SQL Exemplos

### No Jupyter Notebook:

```python
from pyspark.sql import SparkSession
from delta import configure_spark_with_delta_packages

# Configurar Spark (já está no notebook)
# spark = configure_spark_with_delta_packages(builder).getOrCreate()

# Consulta simples
spark.sql("SELECT * FROM ouro_dim_estados LIMIT 10").show()

# Join
spark.sql("""
    SELECT 
        e.uf_sigla,
        e.uf_nome,
        SUM(f.valor) as total_bpc
    FROM ouro_fato_bpc f
    JOIN ouro_dim_estados e ON f.uf_sigla = e.uf_sigla
    GROUP BY e.uf_sigla, e.uf_nome
    ORDER BY total_bpc DESC
""").show()
```

## 🎯 Tabelas Disponíveis

### Bronze
- `bronze_municipios`
- `bronze_estados`
- `bronze_bpc`

### Prata
- `prata_dim_municipios`
- `prata_dim_estados`
- `prata_fato_bpc`

### Ouro
- `ouro_dim_municipios`
- `ouro_dim_estados`
- `ouro_fato_bpc`
- `ouro_agregacao_regiao`
- `ouro_agregacao_estado`
- `ouro_top_municipios`

## 🔧 Troubleshooting

### Container não inicia
```bash
docker-compose down
docker-compose up -d --build
```

### Erro de conexão MinIO
Verifique se o MinIO está acessível:
```bash
curl https://ch8ai-minio.l6zv5a.easypanel.host
```

### Ver logs
```bash
docker-compose logs -f
```

## 📚 Mais Informações

Veja `README_DELTA_LAKE.md` para documentação completa.
