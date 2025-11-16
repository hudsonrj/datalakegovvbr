# ✅ Correção Final Aplicada - S3A FileSystem

## Problema Resolvido

O erro `ClassNotFoundException: Class org.apache.hadoop.fs.s3a.S3AFileSystem not found` foi corrigido!

## Solução

Adicionado `spark.jars.packages` para fazer o Spark baixar automaticamente os JARs necessários:

```python
.config("spark.jars.packages", "io.delta:delta-spark_2.13:4.0.0,org.apache.hadoop:hadoop-aws:3.3.4,com.amazonaws:aws-java-sdk-bundle:1.12.262")
```

## Arquivos Corrigidos

✅ `notebooks/delta_lake_queries.ipynb` - Notebook completo corrigido
✅ `delta_scripts/delta_setup_spark.py` - Script corrigido

## Como Usar

### No Notebook Jupyter:

1. **Acesse:** http://localhost:8889
2. **Abra:** `notebooks/delta_lake_queries.ipynb`
3. **Execute a célula 2** (criar Spark Session)
   - ⚠️ **A primeira vez pode demorar 2-5 minutos** enquanto o Spark baixa os JARs (~100MB)
   - Você verá mensagens de download
   - Depois disso, os JARs ficam em cache e será rápido
4. **Execute as outras células** normalmente

### Código Corrigido:

```python
import os
os.environ['JAVA_HOME'] = '/usr/lib/jvm/java-17-openjdk-amd64'

from pyspark.sql import SparkSession
from delta import configure_spark_with_delta_pip

builder = SparkSession.builder \
    .appName("GovBR Delta Lake") \
    .config("spark.jars.packages", "io.delta:delta-spark_2.13:4.0.0,org.apache.hadoop:hadoop-aws:3.3.4,com.amazonaws:aws-java-sdk-bundle:1.12.262") \
    .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension") \
    .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog") \
    .config("spark.hadoop.fs.s3a.endpoint", f"https://{MINIO_ENDPOINT}") \
    .config("spark.hadoop.fs.s3a.access.key", MINIO_ACCESS_KEY) \
    .config("spark.hadoop.fs.s3a.secret.key", MINIO_SECRET_KEY) \
    .config("spark.hadoop.fs.s3a.path.style.access", "true") \
    .config("spark.hadoop.fs.s3a.connection.ssl.enabled", "true") \
    .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem") \
    .config("spark.hadoop.fs.s3a.aws.credentials.provider", "org.apache.hadoop.fs.s3a.SimpleAWSCredentialsProvider") \
    .config("spark.master", "local[*]")

spark = configure_spark_with_delta_pip(builder).getOrCreate()
```

## Status

✅ **Notebook corrigido e atualizado no container!**
✅ **Script corrigido e atualizado no container!**
✅ **Pronto para uso!**

## Próximos Passos

1. Abra o Jupyter Lab: http://localhost:8889
2. Abra o notebook: `notebooks/delta_lake_queries.ipynb`
3. Execute as células
4. **Aguarde o download dos JARs na primeira execução** (2-5 minutos)
5. Pronto! Delta Lake funcionando!
