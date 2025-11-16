# ✅ Solução Final - S3A FileSystem

## Problema Resolvido!

O erro `ClassNotFoundException: Class org.apache.hadoop.fs.s3a.S3AFileSystem not found` foi **RESOLVIDO**!

## Solução Aplicada

### 1. Download Manual dos JARs

O Spark não estava baixando automaticamente os JARs do Hadoop S3A através de `spark.jars.packages`. A solução foi baixar os JARs manualmente ANTES de criar a Spark Session:

```python
# Baixar JARs usando wget
jars_to_download = [
    ("https://repo1.maven.org/maven2/org/apache/hadoop/hadoop-aws/3.3.4/hadoop-aws-3.3.4.jar", "hadoop-aws-3.3.4.jar"),
    ("https://repo1.maven.org/maven2/com/amazonaws/aws-java-sdk-bundle/1.12.262/aws-java-sdk-bundle-1.12.262.jar", "aws-java-sdk-bundle-1.12.262.jar"),
]
```

### 2. Usar `spark.jars` em vez de `spark.jars.packages` para S3A

```python
jar_paths = ",".join([os.path.join(jars_dir, filename) for _, filename in jars_to_download])

builder = SparkSession.builder \
    .config("spark.jars", jar_paths) \
    .config("spark.jars.packages", "io.delta:delta-spark_2.13:4.0.0") \
    ...
```

### 3. Configurações de Timeout Corrigidas

Adicionadas configurações explícitas de timeout para evitar `NumberFormatException`:

```python
.config("spark.hadoop.fs.s3a.connection.maximum", "15") \
.config("spark.hadoop.fs.s3a.threads.max", "10") \
.config("spark.hadoop.fs.s3a.connection.timeout", "60000") \
.config("spark.hadoop.fs.s3a.attempts.maximum", "3") \
```

## Status

✅ **S3AFileSystem encontrado!** (não há mais ClassNotFoundException)
✅ **JARs baixados manualmente**
✅ **Configurações de timeout corrigidas**

## Próximos Passos

Execute o script novamente:

```bash
docker exec govbr-jupyter-delta python3 /home/jovyan/work/delta_setup_spark.py
```

O script agora deve funcionar corretamente!
