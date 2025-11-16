# 🚀 Guia Rápido - Configuração Spark nos Notebooks

## ✅ Arquivos Disponíveis

Os seguintes arquivos estão disponíveis em `/home/jovyan/work/`:

- ✅ `spark_setup_fixed.py` - Script de configuração corrigido
- ✅ `notebook_spark_setup.ipynb` - Notebook com configuração passo a passo

## 📝 Como Usar no Jupyter Lab

### Opção 1: Usar o Notebook Dedicado (Recomendado)

1. Abra o Jupyter Lab: http://localhost:8889
2. No navegador de arquivos, procure por: `notebook_spark_setup.ipynb`
3. Abra o notebook
4. Execute todas as células

### Opção 2: Executar Script em Qualquer Notebook

No início do seu notebook, adicione esta célula:

```python
# Configuração do Spark - Resolve problemas de conexão
exec(open('spark_setup_fixed.py').read())
```

### Opção 3: Configuração Manual (Se necessário)

Se os arquivos não aparecerem, use esta configuração direta:

```python
import os

# Configurar variáveis de ambiente
os.environ['PYSPARK_PYTHON'] = 'python3'
os.environ['PYSPARK_DRIVER_PYTHON'] = 'python3'
os.environ['JAVA_HOME'] = '/usr/lib/jvm/java-17-openjdk-amd64'
os.environ['SPARK_LOCAL_IP'] = '127.0.0.1'
os.environ['SPARK_MASTER'] = 'local[*]'
os.environ['SPARK_DRIVER_HOST'] = '127.0.0.1'
os.environ['SPARK_DRIVER_BIND_ADDRESS'] = '127.0.0.1'

from pyspark.sql import SparkSession
from delta import configure_spark_with_delta_pip

# Parar sessão existente
try:
    existing_spark = SparkSession.getActiveSession()
    if existing_spark:
        existing_spark.stop()
        import time
        time.sleep(2)
except:
    pass

# Criar Spark Session
builder = SparkSession.builder \
    .appName("GovBR Data Lake") \
    .master("local[*]") \
    .config("spark.driver.host", "127.0.0.1") \
    .config("spark.driver.bindAddress", "127.0.0.1") \
    .config("spark.driver.memory", "2g") \
    .config("spark.executor.memory", "2g") \
    .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension") \
    .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog") \
    .config("spark.hadoop.fs.s3a.endpoint", "https://ch8ai-minio.l6zv5a.easypanel.host") \
    .config("spark.hadoop.fs.s3a.access.key", "admin") \
    .config("spark.hadoop.fs.s3a.secret.key", "1q2w3e4r") \
    .config("spark.hadoop.fs.s3a.path.style.access", "true") \
    .config("spark.hadoop.fs.s3a.connection.ssl.enabled", "true") \
    .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem") \
    .config("spark.hadoop.fs.s3a.aws.credentials.provider", "org.apache.hadoop.fs.s3a.SimpleAWSCredentialsProvider") \
    .config("spark.driver.extraJavaOptions", "-Dio.netty.tryReflectionSetAccessible=true") \
    .config("spark.executor.extraJavaOptions", "-Dio.netty.tryReflectionSetAccessible=true") \
    .config("spark.network.timeout", "800s")

spark = configure_spark_with_delta_pip(builder).getOrCreate()

print(f"✅ Spark Session criada: {spark.version}")
```

## 🔍 Verificar se Funcionou

Após executar a configuração, teste:

```python
# Verificar Spark
print(f"Versão Spark: {spark.version}")
print(f"App Name: {spark.sparkContext.appName}")
print(f"Master: {spark.sparkContext.master}")

# Teste básico
test_df = spark.range(5)
print(f"Teste: {test_df.count()} registros")
test_df.show()
```

## 📍 Localização dos Arquivos

No Jupyter Lab, os arquivos estão em:
- **Diretório**: `/home/jovyan/work/`
- **Arquivos**:
  - `spark_setup_fixed.py`
  - `notebook_spark_setup.ipynb`

## 🔄 Se os Arquivos Não Aparecerem

1. **Recarregue a página do Jupyter Lab** (F5)
2. **Verifique o diretório correto**: Certifique-se de estar em `/home/jovyan/work/`
3. **Use a configuração manual** (Opção 3 acima)
4. **Reinicie o container**:
   ```bash
   docker restart govbr-jupyter-delta
   ```

## ✅ Pronto!

Após executar a configuração, você pode usar o Spark normalmente:

```python
# Ler dados do MinIO
df = spark.read.parquet("s3a://govbr/bronze/ibge/municipios/")
df.show()

# Executar consultas SQL
df.createOrReplaceTempView("municipios")
result = spark.sql("SELECT * FROM municipios LIMIT 10")
result.show()
```
