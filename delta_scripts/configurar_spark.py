#!/usr/bin/env python3
"""
Configuração robusta do Spark para notebooks - Resolve problemas de conexão
"""

import os
import sys

# Configurar variáveis de ambiente ANTES de importar PySpark
os.environ['PYSPARK_PYTHON'] = 'python3'
os.environ['PYSPARK_DRIVER_PYTHON'] = 'python3'
os.environ['JAVA_HOME'] = '/usr/lib/jvm/java-17-openjdk-amd64'
os.environ['SPARK_LOCAL_IP'] = '127.0.0.1'
os.environ['SPARK_MASTER'] = 'local[*]'

# Configurações para evitar problemas de conexão
os.environ['SPARK_DRIVER_HOST'] = '127.0.0.1'
os.environ['SPARK_DRIVER_BIND_ADDRESS'] = '127.0.0.1'

print("=" * 80)
print("CONFIGURAÇÃO SPARK - RESOLUÇÃO DE PROBLEMAS DE CONEXÃO")
print("=" * 80)

# Verificar JAVA_HOME
java_home = os.environ.get('JAVA_HOME')
if java_home:
    print(f"✅ JAVA_HOME configurado: {java_home}")
    if not os.path.exists(java_home):
        print(f"⚠️  AVISO: JAVA_HOME aponta para diretório inexistente: {java_home}")
else:
    print("⚠️  JAVA_HOME não configurado")

# Configurações MinIO
MINIO_ENDPOINT = "ch8ai-minio.l6zv5a.easypanel.host"
MINIO_ACCESS_KEY = "admin"
MINIO_SECRET_KEY = "1q2w3e4r"
BUCKET_NAME = "govbr"

try:
    from pyspark.sql import SparkSession
    # NÃO importar configure_spark_with_delta_pip - causa problemas de versão
    # from delta import configure_spark_with_delta_pip
    
    print("\n[1/4] Verificando Spark Sessions existentes...")
    
    # Parar qualquer Spark Session existente
    try:
        existing_spark = SparkSession.getActiveSession()
        if existing_spark:
            print("  ℹ️  Parando Spark Session existente...")
            existing_spark.stop()
            import time
            time.sleep(2)
            print("  ✅ Spark Session anterior parada")
    except Exception as e:
        print(f"  ℹ️  Nenhuma sessão anterior encontrada: {e}")
    
    print("\n[2/4] Configurando Spark Builder...")
    
    # Builder com configurações robustas para evitar problemas de conexão Py4J e Connection Refused
    # ⭐ IMPORTANTE: Portas dinâmicas (0) evitam "Connection refused"
    builder = SparkSession.builder \
        .appName("GovBR Data Lake") \
        .master("local[*]") \
        .config("spark.driver.host", "127.0.0.1") \
        .config("spark.driver.bindAddress", "127.0.0.1") \
        .config("spark.driver.port", "0") \
        .config("spark.blockManager.port", "0") \
        .config("spark.broadcast.port", "0") \
        .config("spark.fileserver.port", "0") \
        .config("spark.replClassServer.port", "0") \
        .config("spark.ui.port", "0") \
        .config("spark.driver.memory", "2g") \
        .config("spark.executor.memory", "2g") \
        .config("spark.driver.maxResultSize", "1g") \
        .config("spark.sql.execution.arrow.pyspark.enabled", "false") \
        .config("spark.network.timeout", "1200s") \
        .config("spark.executor.heartbeatInterval", "60s") \
        .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension") \
        .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog") \
        .config("spark.hadoop.fs.s3a.endpoint", f"https://{MINIO_ENDPOINT}") \
        .config("spark.hadoop.fs.s3a.access.key", MINIO_ACCESS_KEY) \
        .config("spark.hadoop.fs.s3a.secret.key", MINIO_SECRET_KEY) \
        .config("spark.hadoop.fs.s3a.path.style.access", "true") \
        .config("spark.hadoop.fs.s3a.connection.ssl.enabled", "true") \
        .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem") \
        .config("spark.hadoop.fs.s3a.aws.credentials.provider", "org.apache.hadoop.fs.s3a.SimpleAWSCredentialsProvider") \
        .config("spark.hadoop.fs.s3a.connection.maximum", "15") \
        .config("spark.hadoop.fs.s3a.connection.timeout", "60000") \
        .config("spark.hadoop.fs.s3a.attempts.maximum", "10") \
        .config("spark.driver.extraJavaOptions", 
                "-Dio.netty.tryReflectionSetAccessible=true " +
                "-XX:+UseG1GC " +
                "-XX:MaxGCPauseMillis=200 " +
                "-Djava.net.preferIPv4Stack=true " +
                "-Djava.awt.headless=true") \
        .config("spark.executor.extraJavaOptions", 
                "-Dio.netty.tryReflectionSetAccessible=true " +
                "-XX:+UseG1GC " +
                "-Djava.net.preferIPv4Stack=true " +
                "-Djava.awt.headless=true") \
        .config("spark.sql.adaptive.enabled", "true") \
        .config("spark.sql.adaptive.coalescePartitions.enabled", "true")
    
    print("  ✅ Builder configurado")
    
    print("\n[3/4] Criando Spark Session...")
    
    # Verificar versão do Spark para usar Delta compatível
    import pyspark
    spark_version = pyspark.__version__
    print(f"  ℹ️  Versão Spark detectada: {spark_version}")
    
    # Determinar versão do Delta Lake compatível
    if spark_version.startswith("4."):
        # Spark 4.x usa Delta Lake 4.0.0 com Scala 2.13
        delta_package = "io.delta:delta-spark_2.13:4.0.0"
        hadoop_package = "org.apache.hadoop:hadoop-aws:3.3.4"
        aws_package = "com.amazonaws:aws-java-sdk-bundle:1.12.262"
        print(f"  ℹ️  Usando Delta Lake 4.0.0 para Spark 4.x")
    elif spark_version.startswith("3.5"):
        # Spark 3.5.x usa Delta Lake 3.0.0
        delta_package = "io.delta:delta-spark_2.12:3.0.0"
        hadoop_package = "org.apache.hadoop:hadoop-aws:3.3.4"
        aws_package = "com.amazonaws:aws-java-sdk-bundle:1.12.262"
        print(f"  ℹ️  Usando Delta Lake 3.0.0 para Spark 3.5.x")
    else:
        # Versão padrão para Spark 3.x
        delta_package = "io.delta:delta-spark_2.12:2.4.0"
        hadoop_package = "org.apache.hadoop:hadoop-aws:3.3.4"
        aws_package = "com.amazonaws:aws-java-sdk-bundle:1.12.262"
        print(f"  ℹ️  Usando Delta Lake 2.4.0 (padrão)")
    
    # Adicionar pacotes JAR ao builder SEM usar configure_spark_with_delta_pip
    # Isso evita conflitos de versão do Delta Lake
    builder = builder.config("spark.jars.packages", f"{delta_package},{hadoop_package},{aws_package}")
    
    # Criar Spark Session SEM usar configure_spark_with_delta_pip
    # Isso evita problemas de incompatibilidade de versão
    try:
        print("  ℹ️  Criando Spark Session com Delta Lake (sem configure_spark_with_delta_pip)...")
        print("  ℹ️  Isso evita problemas de incompatibilidade de versão")
        spark = builder.getOrCreate()
        print("  ✅ Spark Session criada com sucesso!")
    except Exception as e:
        print(f"  ⚠️  Erro ao criar Spark Session com Delta: {e}")
        print("  ℹ️  Tentando criar Spark Session sem Delta (modo fallback)...")
        
        # Fallback: criar Spark Session sem Delta
        builder_fallback = SparkSession.builder \
            .appName("GovBR Data Lake (Fallback)") \
            .master("local[*]") \
            .config("spark.driver.host", "127.0.0.1") \
            .config("spark.driver.bindAddress", "127.0.0.1") \
            .config("spark.driver.memory", "2g") \
            .config("spark.executor.memory", "2g") \
            .config("spark.jars.packages", f"{hadoop_package},{aws_package}") \
            .config("spark.hadoop.fs.s3a.endpoint", f"https://{MINIO_ENDPOINT}") \
            .config("spark.hadoop.fs.s3a.access.key", MINIO_ACCESS_KEY) \
            .config("spark.hadoop.fs.s3a.secret.key", MINIO_SECRET_KEY) \
            .config("spark.hadoop.fs.s3a.path.style.access", "true") \
            .config("spark.hadoop.fs.s3a.connection.ssl.enabled", "true") \
            .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem")
        
        spark = builder_fallback.getOrCreate()
        print("  ✅ Spark Session criada em modo fallback (sem Delta)")
        print("  ⚠️  ATENÇÃO: Delta Lake não está disponível. Use apenas Parquet.")
    
    print("\n[4/4] Verificando Spark Session...")
    print(f"  ✅ Versão Spark: {spark.version}")
    print(f"  ✅ App Name: {spark.sparkContext.appName}")
    print(f"  ✅ Master: {spark.sparkContext.master}")
    
    # Teste básico
    try:
        test_df = spark.range(10)
        count = test_df.count()
        print(f"  ✅ Teste básico: {count} registros criados")
    except Exception as e:
        print(f"  ⚠️  Erro no teste básico: {e}")
    
    print("\n" + "=" * 80)
    print("✅ SPARK SESSION PRONTA PARA USO!")
    print("=" * 80)
    print("\nA variável 'spark' está disponível para uso nos notebooks.")
    print("Use spark para criar DataFrames e executar consultas SQL.")
    
    # Tornar spark disponível globalmente
    import __main__
    __main__.spark = spark
    
    # Retornar spark para uso direto
    globals()['spark'] = spark
    
except ImportError as e:
    print(f"\n❌ Erro de importação: {e}")
    print("\nSoluções possíveis:")
    print("1. Instalar PySpark: pip install pyspark")
    print("2. Verificar se está no container correto")
    print("3. Delta Lake será carregado via JARs, não precisa do pacote Python")
    sys.exit(1)
    
except Exception as e:
    print(f"\n❌ Erro ao configurar Spark: {e}")
    import traceback
    traceback.print_exc()
    print("\n" + "=" * 80)
    print("TROUBLESHOOTING")
    print("=" * 80)
    print("1. Verifique se JAVA_HOME está correto")
    print("2. Verifique se as portas não estão em uso")
    print("3. Tente reiniciar o container")
    print("4. Verifique os logs: docker logs govbr-jupyter-delta")
    sys.exit(1)
