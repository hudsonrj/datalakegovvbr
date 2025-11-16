# 🔧 Solução para Problemas de Conexão no Spark

## Problema

Ao executar notebooks, você pode encontrar o erro:
```
✅ JAVA_HOME configurado: /usr/lib/jvm/java-17-openjdk-amd64
ℹ️  [Errno 111] Connection refused
✅ Pronto para criar nova Spark Session
```

## Causa

Este erro ocorre quando o Spark tenta se conectar a um servidor remoto ou há problemas de configuração de rede.

## Solução

### Opção 1: Usar o Script de Configuração Corrigido (Recomendado)

Execute o script `spark_setup_fixed.py` que resolve automaticamente os problemas de conexão:

```python
# No notebook, execute:
exec(open('spark_setup_fixed.py').read())
```

Ou use o notebook dedicado:
```python
# Abrir notebook_spark_setup.ipynb no Jupyter Lab
```

### Opção 2: Configuração Manual no Notebook

Se preferir configurar manualmente, adicione este código no início do seu notebook:

```python
import os

# Configurar variáveis de ambiente ANTES de importar PySpark
os.environ['PYSPARK_PYTHON'] = 'python3'
os.environ['PYSPARK_DRIVER_PYTHON'] = 'python3'
os.environ['JAVA_HOME'] = '/usr/lib/jvm/java-17-openjdk-amd64'
os.environ['SPARK_LOCAL_IP'] = '127.0.0.1'
os.environ['SPARK_MASTER'] = 'local[*]'
os.environ['SPARK_DRIVER_HOST'] = '127.0.0.1'
os.environ['SPARK_DRIVER_BIND_ADDRESS'] = '127.0.0.1'

from pyspark.sql import SparkSession
from delta import configure_spark_with_delta_pip

# Parar sessão existente se houver
try:
    existing_spark = SparkSession.getActiveSession()
    if existing_spark:
        existing_spark.stop()
        import time
        time.sleep(2)
except:
    pass

# Criar Spark Session com configurações corretas
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

## Verificação

Após configurar, verifique se está funcionando:

```python
# Verificar Spark Session
print(f"Versão Spark: {spark.version}")
print(f"App Name: {spark.sparkContext.appName}")
print(f"Master: {spark.sparkContext.master}")

# Teste básico
test_df = spark.range(10)
print(f"Teste: {test_df.count()} registros")
test_df.show()
```

## Troubleshooting Adicional

### 1. Verificar JAVA_HOME

```python
import os
java_home = os.environ.get('JAVA_HOME')
print(f"JAVA_HOME: {java_home}")

# Verificar se existe
import os.path
if java_home and os.path.exists(java_home):
    print("✅ JAVA_HOME válido")
else:
    print("❌ JAVA_HOME inválido ou não existe")
```

### 2. Verificar Portas em Uso

```bash
# No terminal do container
netstat -tuln | grep -E '4040|8080|7077'
```

### 3. Reiniciar Container

Se o problema persistir, reinicie o container:

```bash
docker restart govbr-jupyter-delta
```

### 4. Verificar Logs

```bash
docker logs govbr-jupyter-delta --tail 100
```

## Configurações Importantes

As seguintes configurações são essenciais para evitar problemas de conexão:

1. **SPARK_LOCAL_IP**: Deve ser `127.0.0.1` para modo local
2. **SPARK_DRIVER_HOST**: Deve ser `127.0.0.1`
3. **spark.master**: Deve ser `local[*]` para execução local
4. **spark.driver.host**: Deve ser `127.0.0.1`
5. **spark.driver.bindAddress**: Deve ser `127.0.0.1`

## Arquivos Criados

- `delta_scripts/spark_setup_fixed.py` - Script de configuração corrigido
- `delta_scripts/notebook_spark_setup.ipynb` - Notebook com configuração passo a passo

## Uso nos Notebooks

Sempre execute a configuração no início dos notebooks que usam Spark:

```python
# Primeira célula do notebook
exec(open('spark_setup_fixed.py').read())

# Agora você pode usar 'spark' normalmente
df = spark.read.parquet("s3a://govbr/bronze/ibge/municipios/")
df.show()
```

## Suporte

Se o problema persistir após seguir estas instruções:

1. Verifique os logs do container
2. Verifique se todas as dependências estão instaladas
3. Tente reiniciar o container
4. Verifique se as portas não estão em uso por outro processo
