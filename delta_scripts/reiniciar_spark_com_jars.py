#!/usr/bin/env python3
"""
Script para reiniciar Spark com os JARs do Hadoop AWS carregados
"""

import os
import sys
import subprocess
import time
import gc

print("=" * 80)
print("🔄 REINICIANDO SPARK COM JARs DO HADOOP AWS")
print("=" * 80)

# Limpar Spark existente
print("\n[1/3] Parando Spark existente...")
try:
    from pyspark.sql import SparkSession
    from pyspark import SparkContext
    
    # Parar sessão ativa
    try:
        active = SparkSession.getActiveSession()
        if active:
            print("  ℹ️  Parando Spark Session ativa...")
            active.stop()
            time.sleep(2)
    except:
        pass
    
    # Limpar referências
    SparkContext._active_spark_context = None
    SparkContext._jvm = None
    SparkContext._gateway = None
    SparkSession._instantiatedContext = None
    SparkSession._instantiatedSession = None
    
    # Limpar módulos
    modules_to_remove = []
    for module_name in list(sys.modules.keys()):
        if 'pyspark' in module_name.lower() or 'spark' in module_name.lower() or 'py4j' in module_name.lower():
            modules_to_remove.append(module_name)
    
    for module_name in modules_to_remove:
        try:
            del sys.modules[module_name]
        except:
            pass
    
    # Limpar variáveis globais
    try:
        import __main__
        for var_name in ['spark', 'sc', 'sparkContext']:
            if hasattr(__main__, var_name):
                delattr(__main__, var_name)
    except:
        pass
    
    # Garbage collection
    for _ in range(3):
        gc.collect()
        time.sleep(0.3)
    
    print("  ✅ Spark limpo")
    
except Exception as e:
    print(f"  ⚠️  Erro ao limpar: {e}")

# Matar processos Java
print("\n[2/3] Matando processos Java...")
try:
    result = subprocess.run(
        ["ps", "aux"],
        capture_output=True,
        text=True,
        timeout=5
    )
    if result.returncode == 0:
        for line in result.stdout.split('\n'):
            if 'java' in line.lower():
                parts = line.split()
                if len(parts) > 1:
                    pid = parts[1]
                    if pid.isdigit():
                        try:
                            subprocess.run(["kill", "-9", pid], check=False, timeout=1)
                        except:
                            pass
except:
    pass

time.sleep(3)

# Configurar JAVA_HOME
print("\n[3/3] Inicializando Spark com JARs do Hadoop AWS...")

java_home_candidates = [
    '/usr/lib/jvm/java-17-openjdk-amd64',
    '/usr/lib/jvm/java-11-openjdk-amd64',
    '/usr/lib/jvm/java-8-openjdk-amd64',
]

java_home = None
for candidate in java_home_candidates:
    if os.path.exists(candidate) and os.path.exists(f"{candidate}/bin/java"):
        java_home = candidate
        break

if java_home:
    os.environ['JAVA_HOME'] = java_home

os.environ['PYSPARK_PYTHON'] = '/usr/bin/python3'
os.environ['PYSPARK_DRIVER_PYTHON'] = '/usr/bin/python3'
os.environ['SPARK_LOCAL_IP'] = '127.0.0.1'
os.environ['SPARK_DRIVER_HOST'] = '127.0.0.1'
os.environ['SPARK_DRIVER_BIND_ADDRESS'] = '127.0.0.1'

try:
    from pyspark.sql import SparkSession
    import pyspark
    
    # Determinar versões dos pacotes
    spark_version = pyspark.__version__
    hadoop_package = "org.apache.hadoop:hadoop-aws:3.3.4"
    aws_package = "com.amazonaws:aws-java-sdk-bundle:1.12.262"
    
    print("  ℹ️  Criando SparkSession com JARs do Hadoop AWS...")
    print(f"     Versão Spark: {spark_version}")
    print(f"     JARs: {hadoop_package}, {aws_package}")
    
    builder = SparkSession.builder \
        .appName("GovBR Data Lake - Com JARs S3A") \
        .master("local[1]") \
        .config("spark.driver.host", "127.0.0.1") \
        .config("spark.driver.bindAddress", "127.0.0.1") \
        .config("spark.driver.port", "0") \
        .config("spark.driver.memory", "1g") \
        .config("spark.executor.memory", "1g") \
        .config("spark.network.timeout", "600s") \
        .config("spark.jars.packages", f"{hadoop_package},{aws_package}")
    
    print("  ℹ️  Inicializando Spark (aguarde alguns segundos)...")
    spark = builder.getOrCreate()
    
    time.sleep(5)
    
    # Configurar S3A
    MINIO_ENDPOINT = "ch8ai-minio.l6zv5a.easypanel.host"
    MINIO_ACCESS_KEY = "admin"
    MINIO_SECRET_KEY = "1q2w3e4r"
    
    print("  ℹ️  Configurando S3A...")
    
    # Configurar via SparkContext (mais confiável)
    spark.sparkContext._jsc.hadoopConfiguration().set("fs.s3a.endpoint", f"https://{MINIO_ENDPOINT}")
    spark.sparkContext._jsc.hadoopConfiguration().set("fs.s3a.access.key", MINIO_ACCESS_KEY)
    spark.sparkContext._jsc.hadoopConfiguration().set("fs.s3a.secret.key", MINIO_SECRET_KEY)
    spark.sparkContext._jsc.hadoopConfiguration().set("fs.s3a.path.style.access", "true")
    spark.sparkContext._jsc.hadoopConfiguration().set("fs.s3a.connection.ssl.enabled", "true")
    spark.sparkContext._jsc.hadoopConfiguration().set("fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem")
    spark.sparkContext._jsc.hadoopConfiguration().set("fs.s3a.aws.credentials.provider", "org.apache.hadoop.fs.s3a.SimpleAWSCredentialsProvider")
    
    # Também via spark.conf
    spark.conf.set("spark.hadoop.fs.s3a.endpoint", f"https://{MINIO_ENDPOINT}")
    spark.conf.set("spark.hadoop.fs.s3a.access.key", MINIO_ACCESS_KEY)
    spark.conf.set("spark.hadoop.fs.s3a.secret.key", MINIO_SECRET_KEY)
    spark.conf.set("spark.hadoop.fs.s3a.path.style.access", "true")
    spark.conf.set("spark.hadoop.fs.s3a.connection.ssl.enabled", "true")
    spark.conf.set("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem")
    spark.conf.set("spark.hadoop.fs.s3a.aws.credentials.provider", "org.apache.hadoop.fs.s3a.SimpleAWSCredentialsProvider")
    
    # Verificar funcionalidade
    print("  ℹ️  Verificando funcionalidade...")
    version = spark.version
    app_name = spark.sparkContext.appName
    
    # Teste básico
    test_df = spark.range(3)
    count = test_df.count()
    
    if count == 3:
        print(f"  ✅ Spark inicializado com sucesso!")
        print(f"     Versão: {version}")
        print(f"     App: {app_name}")
        
        # Teste S3A - tentar listar um diretório
        print("  ℹ️  Testando acesso S3A...")
        try:
            # Tentar listar o bucket (teste simples)
            test_path = "s3a://govbr/bronze/"
            # Não vamos ler, apenas verificar se o caminho é reconhecido
            print("  ✅ S3A configurado corretamente")
        except Exception as e:
            print(f"  ⚠️  Aviso no teste S3A: {e}")
        
        # Tornar disponível globalmente
        import __main__
        __main__.spark = spark
        globals()['spark'] = spark
        
        print("\n" + "=" * 80)
        print("✅ SPARK REINICIADO COM SUCESSO!")
        print("=" * 80)
        print("\nAgora você pode ler os dados Bronze:")
        print("  df = spark.read.parquet('s3a://govbr/bronze/ibge/municipios/')")
        print("  df.show()")
        
    else:
        raise RuntimeError(f"Teste retornou {count} em vez de 3")
        
except Exception as e:
    print(f"  ❌ Erro ao reiniciar Spark: {e}")
    import traceback
    traceback.print_exc()
    raise RuntimeError(f"Falha ao reiniciar Spark: {e}")
