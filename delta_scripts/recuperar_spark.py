#!/usr/bin/env python3
"""
Script para recuperar Spark Session quando há Connection Refused
Detecta sessões "zombie" e recria uma sessão funcional
"""

import os
import sys
import subprocess
import time
import gc

print("=" * 80)
print("🔧 RECUPERAÇÃO DE SPARK SESSION - Connection Refused Fix")
print("=" * 80)

# ============================================================================
# PASSO 1: Detectar e parar sessão "zombie"
# ============================================================================
print("\n[1/5] Detectando e parando sessão Spark existente...")

try:
    from pyspark.sql import SparkSession
    from pyspark import SparkContext
    
    # Verificar se há sessão ativa
    try:
        active_session = SparkSession.getActiveSession()
        if active_session:
            print("  ℹ️  Sessão Spark encontrada, verificando funcionalidade...")
            try:
                # Tentar acessar uma propriedade simples
                _ = active_session.sparkContext.appName
                print("  ✅ Sessão parece funcional")
            except Exception as e:
                print(f"  ⚠️  Sessão existe mas não está funcional: {e}")
                print("  ℹ️  Parando sessão 'zombie'...")
                try:
                    active_session.stop()
                    time.sleep(2)
                except:
                    pass
        else:
            print("  ℹ️  Nenhuma sessão ativa encontrada")
    except Exception as e:
        print(f"  ⚠️  Erro ao verificar sessão: {e}")
    
    # Limpar SparkContext
    try:
        sc = SparkContext._active_spark_context
        if sc:
            print("  ℹ️  Parando SparkContext...")
            try:
                sc.stop()
                time.sleep(2)
            except:
                pass
    except:
        pass
    
    # Limpar referências globais
    SparkSession._instantiatedContext = None
    SparkSession._instantiatedSession = None
    SparkContext._active_spark_context = None
    SparkContext._jvm = None
    SparkContext._gateway = None
    
except ImportError:
    print("  ℹ️  PySpark não importado ainda")
except Exception as e:
    print(f"  ⚠️  Erro na limpeza: {e}")

# ============================================================================
# PASSO 2: Matar processos Java do Spark
# ============================================================================
print("\n[2/5] Matando processos Java do Spark...")

for pattern in ["org.apache.spark", "java.*spark", "SparkSubmit"]:
    try:
        result = subprocess.run(
            ["pgrep", "-f", pattern],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            pids = result.stdout.strip().split('\n')
            for pid in pids:
                if pid and pid.isdigit():
                    try:
                        subprocess.run(["kill", "-9", pid], check=False, timeout=2)
                        print(f"  ℹ️  Processo {pid} terminado")
                    except:
                        pass
    except:
        pass

time.sleep(3)

# ============================================================================
# PASSO 3: Verificar e liberar portas
# ============================================================================
print("\n[3/5] Verificando e liberando portas...")

import socket

def kill_process_on_port(port):
    try:
        result = subprocess.run(
            ["lsof", "-ti", f":{port}"],
            capture_output=True,
            text=True,
            timeout=2
        )
        if result.returncode == 0 and result.stdout.strip():
            pids = result.stdout.strip().split('\n')
            for pid in pids:
                if pid and pid.isdigit():
                    subprocess.run(["kill", "-9", pid], check=False, timeout=2)
            return True
    except:
        pass
    return False

spark_ports = [4040, 4041, 4042, 8080, 8081, 7077, 7078]
for port in spark_ports:
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex(('127.0.0.1', port))
        sock.close()
        if result == 0:
            if kill_process_on_port(port):
                print(f"  ✅ Porta {port} liberada")
    except:
        pass

# ============================================================================
# PASSO 4: Configurar ambiente
# ============================================================================
print("\n[4/5] Configurando ambiente...")

os.environ['PYSPARK_PYTHON'] = '/usr/bin/python3'
os.environ['PYSPARK_DRIVER_PYTHON'] = '/usr/bin/python3'

# Verificar JAVA_HOME
java_home = os.environ.get('JAVA_HOME')
if not java_home or not os.path.exists(java_home):
    java_home_candidates = [
        '/usr/lib/jvm/java-17-openjdk-amd64',
        '/usr/lib/jvm/java-11-openjdk-amd64',
        '/usr/lib/jvm/java-8-openjdk-amd64',
    ]
    for candidate in java_home_candidates:
        if os.path.exists(candidate):
            java_home = candidate
            break
    
    if not java_home:
        try:
            result = subprocess.run(["which", "java"], capture_output=True, text=True)
            if result.returncode == 0:
                java_path = result.stdout.strip()
                java_home = os.path.dirname(os.path.dirname(java_path))
        except:
            pass
    
    if java_home:
        os.environ['JAVA_HOME'] = java_home
        print(f"  ✅ JAVA_HOME: {java_home}")

os.environ['SPARK_LOCAL_IP'] = '127.0.0.1'
os.environ['SPARK_DRIVER_HOST'] = '127.0.0.1'
os.environ['SPARK_DRIVER_BIND_ADDRESS'] = '127.0.0.1'

# Garbage collection
for _ in range(3):
    gc.collect()
    time.sleep(0.5)

# ============================================================================
# PASSO 5: Recriar Spark Session
# ============================================================================
print("\n[5/5] Recriando Spark Session...")

try:
    from pyspark.sql import SparkSession
    import pyspark
    
    # Configurações MinIO
    MINIO_ENDPOINT = "ch8ai-minio.l6zv5a.easypanel.host"
    MINIO_ACCESS_KEY = "admin"
    MINIO_SECRET_KEY = "1q2w3e4r"
    
    # Determinar versão do Delta Lake
    spark_version = pyspark.__version__
    if spark_version.startswith("4."):
        delta_package = "io.delta:delta-spark_2.13:4.0.0"
        hadoop_package = "org.apache.hadoop:hadoop-aws:3.3.4"
        aws_package = "com.amazonaws:aws-java-sdk-bundle:1.12.262"
    elif spark_version.startswith("3.5"):
        delta_package = "io.delta:delta-spark_2.12:3.0.0"
        hadoop_package = "org.apache.hadoop:hadoop-aws:3.3.4"
        aws_package = "com.amazonaws:aws-java-sdk-bundle:1.12.262"
    else:
        delta_package = "io.delta:delta-spark_2.12:2.4.0"
        hadoop_package = "org.apache.hadoop:hadoop-aws:3.3.4"
        aws_package = "com.amazonaws:aws-java-sdk-bundle:1.12.262"
    
    # Criar builder
    builder = SparkSession.builder \
        .appName("GovBR Data Lake - Recovered") \
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
        .config("spark.network.timeout", "1200s") \
        .config("spark.executor.heartbeatInterval", "60s") \
        .config("spark.jars.packages", f"{delta_package},{hadoop_package},{aws_package}") \
        .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension") \
        .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog") \
        .config("spark.hadoop.fs.s3a.endpoint", f"https://{MINIO_ENDPOINT}") \
        .config("spark.hadoop.fs.s3a.access.key", MINIO_ACCESS_KEY) \
        .config("spark.hadoop.fs.s3a.secret.key", MINIO_SECRET_KEY) \
        .config("spark.hadoop.fs.s3a.path.style.access", "true") \
        .config("spark.hadoop.fs.s3a.connection.ssl.enabled", "true") \
        .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem") \
        .config("spark.driver.extraJavaOptions", 
                "-Dio.netty.tryReflectionSetAccessible=true " +
                "-XX:+UseG1GC " +
                "-XX:MaxGCPauseMillis=200 " +
                "-Djava.net.preferIPv4Stack=true " +
                "-Djava.awt.headless=true")
    
    print("  ℹ️  Criando nova Spark Session...")
    spark = builder.getOrCreate()
    
    # Aguardar inicialização
    time.sleep(5)
    
    # Verificar funcionalidade
    print("  ℹ️  Verificando funcionalidade...")
    test_df = spark.range(5)
    count = test_df.count()
    
    if count == 5:
        version = spark.version
        app_name = spark.sparkContext.appName
        
        print(f"\n✅ Spark Session recuperada com sucesso!")
        print(f"   Versão: {version}")
        print(f"   App: {app_name}")
        print(f"   Teste: {count} registros criados")
        
        # Tornar disponível globalmente
        import __main__
        __main__.spark = spark
        globals()['spark'] = spark
        
        print("\n✅ Spark está pronto para uso!")
        
    else:
        raise Exception(f"Teste retornou resultado inesperado: {count}")
        
except Exception as e:
    print(f"\n❌ Erro ao recuperar Spark Session: {e}")
    import traceback
    traceback.print_exc()
    print("\n💡 SOLUÇÕES:")
    print("1. Reinicie o container: docker restart govbr-jupyter-delta")
    print("2. Execute diagnóstico: exec(open('/home/jovyan/work/diagnostico_spark.py').read())")
    print("3. Execute correção completa: exec(open('/home/jovyan/work/fix_spark_py4j.py').read())")
    raise

print("\n" + "=" * 80)
