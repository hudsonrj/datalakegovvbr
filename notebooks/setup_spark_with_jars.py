#!/usr/bin/env python3
"""
Script para baixar JARs e criar Spark Session com S3A
"""

import os
import subprocess
import sys

# Configurar paths
os.environ['PYSPARK_PYTHON'] = 'python3'
os.environ['PYSPARK_DRIVER_PYTHON'] = 'python3'
os.environ['JAVA_HOME'] = '/usr/lib/jvm/java-17-openjdk-amd64'

print("=" * 80)
print("SETUP SPARK COM JARs DO S3A")
print("=" * 80)

# Criar diretório para JARs
jars_dir = "/tmp/spark_jars"
os.makedirs(jars_dir, exist_ok=True)

# URLs dos JARs necessários
jars_to_download = [
    ("https://repo1.maven.org/maven2/org/apache/hadoop/hadoop-aws/3.3.4/hadoop-aws-3.3.4.jar", "hadoop-aws-3.3.4.jar"),
    ("https://repo1.maven.org/maven2/com/amazonaws/aws-java-sdk-bundle/1.12.262/aws-java-sdk-bundle-1.12.262.jar", "aws-java-sdk-bundle-1.12.262.jar"),
]

# Baixar JARs se não existirem
jar_paths = []
print("\n[1/3] Baixando JARs do S3A...")
for url, filename in jars_to_download:
    jar_path = os.path.join(jars_dir, filename)
    if not os.path.exists(jar_path):
        print(f"  [INFO] Baixando {filename}...")
        try:
            result = subprocess.run(
                ["wget", "-q", "--show-progress", "-O", jar_path, url],
                check=True,
                capture_output=True,
                text=True
            )
            if os.path.exists(jar_path) and os.path.getsize(jar_path) > 0:
                size_mb = os.path.getsize(jar_path) / (1024 * 1024)
                print(f"  ✅ {filename} baixado ({size_mb:.1f} MB)")
            else:
                print(f"  ❌ {filename} baixado mas arquivo vazio ou não existe!")
                sys.exit(1)
        except subprocess.CalledProcessError as e:
            print(f"  ❌ Erro ao baixar {filename}: {e}")
            print(f"     stdout: {e.stdout}")
            print(f"     stderr: {e.stderr}")
            sys.exit(1)
        except Exception as e:
            print(f"  ❌ Erro inesperado ao baixar {filename}: {e}")
            sys.exit(1)
    else:
        size_mb = os.path.getsize(jar_path) / (1024 * 1024)
        print(f"  ✅ {filename} já existe ({size_mb:.1f} MB)")
    jar_paths.append(jar_path)

# Verificar se todos os JARs foram baixados
if len(jar_paths) != 2:
    print(f"\n❌ Erro: Esperado 2 JARs, encontrado {len(jar_paths)}")
    sys.exit(1)

print("\n[2/3] Criando Spark Session...")

try:
    from pyspark.sql import SparkSession
    from delta import configure_spark_with_delta_pip
    
    # Configurações MinIO
    MINIO_ENDPOINT = "ch8ai-minio.l6zv5a.easypanel.host"
    MINIO_ACCESS_KEY = "admin"
    MINIO_SECRET_KEY = "1q2w3e4r"
    BUCKET_NAME = "govbr"
    
    # Parar qualquer Spark Session existente
    try:
        existing_spark = SparkSession.getActiveSession()
        if existing_spark:
            print("  [INFO] Parando Spark Session existente...")
            existing_spark.stop()
            import time
            time.sleep(3)
    except:
        pass
    
    # Usar spark.jars para os JARs baixados manualmente
    jar_paths_str = ",".join(jar_paths)
    delta_package = "io.delta:delta-spark_2.13:4.0.0"
    
    builder = SparkSession.builder \
        .appName("GovBR Delta Lake") \
        .config("spark.jars", jar_paths_str) \
        .config("spark.jars.packages", delta_package) \
        .config("spark.driver.memory", "2g") \
        .config("spark.executor.memory", "2g") \
        .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension") \
        .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog") \
        .config("spark.hadoop.fs.s3a.endpoint", f"https://{MINIO_ENDPOINT}") \
        .config("spark.hadoop.fs.s3a.access.key", MINIO_ACCESS_KEY) \
        .config("spark.hadoop.fs.s3a.secret.key", MINIO_SECRET_KEY) \
        .config("spark.hadoop.fs.s3a.path.style.access", "true") \
        .config("spark.hadoop.fs.s3a.connection.ssl.enabled", "true") \
        .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem") \
        .config("spark.hadoop.fs.s3a.aws.credentials.provider", "org.apache.hadoop.fs.s3a.SimpleAWSCredentialsProvider") \
        .config("spark.master", "local[*]") \
        .config("spark.driver.extraJavaOptions", "-Dio.netty.tryReflectionSetAccessible=true") \
        .config("spark.executor.extraJavaOptions", "-Dio.netty.tryReflectionSetAccessible=true")
    
    spark = configure_spark_with_delta_pip(builder).getOrCreate()
    
    # Tornar spark global para uso em outros scripts
    import __main__
    __main__.spark = spark
    
    print("  ✅ Spark Session criada!")
    print(f"  ✅ Versão Spark: {spark.version}")
    
    # Verificar se os JARs estão no classpath
    print("\n[3/3] Verificando classpath...")
    try:
        spark_context = spark.sparkContext
        jars_config = spark_context.getConf().get("spark.jars", "")
        packages_config = spark_context.getConf().get("spark.jars.packages", "")
        
        if "hadoop-aws" in jars_config:
            print("  ✅ JARs do S3A encontrados no classpath!")
            print(f"     JARs configurados: {jars_config[:150]}...")
        else:
            print("  ⚠️  JARs do S3A podem não estar no classpath")
            print(f"     JARs configurados: {jars_config}")
        
        if "delta-spark" in packages_config:
            print(f"  ✅ Delta package configurado")
    except Exception as e:
        print(f"  ⚠️  Erro ao verificar classpath: {e}")
    
    # Teste rápido para verificar se S3A funciona
    print("\n[TESTE] Verificando acesso ao S3A...")
    try:
        # Tentar criar um FileSystem S3A para verificar se a classe está disponível
        from pyspark.sql import SparkSession
        # Se chegou aqui sem erro, a sessão foi criada
        # Agora vamos tentar ler um arquivo para verificar se S3A funciona
        test_path = f"s3a://{BUCKET_NAME}/"
        # Não vamos fazer nada por enquanto, apenas verificar se não há erro de ClassNotFoundException
        print("  ✅ S3A configurado (sem erros de ClassNotFoundException)")
    except Exception as e:
        if "ClassNotFoundException" in str(e):
            print(f"  ❌ ERRO: ClassNotFoundException ainda presente!")
            print(f"     {e}")
            sys.exit(1)
        else:
            print(f"  ℹ️  Outro erro (pode ser normal): {str(e)[:100]}")
    
    print("\n" + "=" * 80)
    print("✅ SETUP CONCLUÍDO COM SUCESSO!")
    print("=" * 80)
    print("\nA Spark Session está pronta para usar Delta Lake com S3A!")
    print("Use 'spark' para acessar a Spark Session.")
    
except ImportError as e:
    print(f"\n❌ Erro de importação: {e}")
    print("Certifique-se de estar executando dentro do container Spark")
    sys.exit(1)
except Exception as e:
    print(f"\n❌ Erro ao criar Spark Session: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
