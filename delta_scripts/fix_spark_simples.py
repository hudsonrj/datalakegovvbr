#!/usr/bin/env python3
"""
Script SIMPLES para corrigir erro Py4J Connection Refused
Usa abordagem mais direta sem tentar inicializar Py4J manualmente
"""

import os
import sys
import subprocess
import time
import gc

print("=" * 80)
print("🔧 CORREÇÃO Py4J Connection Refused - Abordagem Simples")
print("=" * 80)

# ============================================================================
# PASSO 1: Limpar ambiente completamente
# ============================================================================
print("\n[1/4] Limpando ambiente...")

# Matar TODOS os processos Java
print("  ℹ️  Matando processos Java...")
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

# Limpar módulos Python
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
    time.sleep(0.5)

print(f"  ✅ Ambiente limpo ({len(modules_to_remove)} módulos removidos)")

# ============================================================================
# PASSO 2: Configurar JAVA_HOME
# ============================================================================
print("\n[2/4] Configurando JAVA_HOME...")

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
    print(f"  ✅ JAVA_HOME: {java_home}")
else:
    print("  ⚠️  JAVA_HOME não detectado")

os.environ['PYSPARK_PYTHON'] = '/usr/bin/python3'
os.environ['PYSPARK_DRIVER_PYTHON'] = '/usr/bin/python3'
os.environ['SPARK_LOCAL_IP'] = '127.0.0.1'
os.environ['SPARK_DRIVER_HOST'] = '127.0.0.1'
os.environ['SPARK_DRIVER_BIND_ADDRESS'] = '127.0.0.1'

# ============================================================================
# PASSO 3: Criar Spark Session usando abordagem mais simples
# ============================================================================
print("\n[3/4] Criando Spark Session (abordagem simples)...")

try:
    # Importar PySpark
    from pyspark.sql import SparkSession
    
    # Configurações MinIO
    MINIO_ENDPOINT = "ch8ai-minio.l6zv5a.easypanel.host"
    MINIO_ACCESS_KEY = "admin"
    MINIO_SECRET_KEY = "1q2w3e4r"
    
    print("  ℹ️  Criando SparkSession.builder...")
    
    # Usar builder com configurações mínimas primeiro
    builder = SparkSession.builder \
        .appName("GovBR Data Lake - Simple") \
        .master("local[1]") \
        .config("spark.driver.host", "127.0.0.1") \
        .config("spark.driver.bindAddress", "127.0.0.1") \
        .config("spark.driver.port", "0") \
        .config("spark.driver.memory", "1g") \
        .config("spark.executor.memory", "1g") \
        .config("spark.network.timeout", "600s")
    
    print("  ℹ️  Chamando getOrCreate() (isso pode levar alguns segundos)...")
    print("  ⚠️  Se demorar muito, pode ser necessário reiniciar o container")
    
    # Tentar criar - isso vai inicializar o JVM automaticamente
    spark = builder.getOrCreate()
    
    # Aguardar inicialização
    print("  ℹ️  Aguardando Spark inicializar...")
    time.sleep(8)  # Mais tempo para inicialização
    
    # Verificar
    print("  ℹ️  Verificando funcionalidade...")
    version = spark.version
    app_name = spark.sparkContext.appName
    
    print(f"  ✅ Spark Session criada!")
    print(f"     Versão: {version}")
    print(f"     App: {app_name}")
    
    # Teste básico
    test_df = spark.range(3)
    count = test_df.count()
    
    if count == 3:
        print(f"  ✅ Teste funcional: {count} registros")
    else:
        raise RuntimeError(f"Teste retornou {count} em vez de 3")
    
    # Agora adicionar configurações S3A
    print("  ℹ️  Adicionando configurações S3A...")
    spark.conf.set("spark.hadoop.fs.s3a.endpoint", f"https://{MINIO_ENDPOINT}")
    spark.conf.set("spark.hadoop.fs.s3a.access.key", MINIO_ACCESS_KEY)
    spark.conf.set("spark.hadoop.fs.s3a.secret.key", MINIO_SECRET_KEY)
    spark.conf.set("spark.hadoop.fs.s3a.path.style.access", "true")
    spark.conf.set("spark.hadoop.fs.s3a.connection.ssl.enabled", "true")
    spark.conf.set("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem")
    
    print("  ✅ Configurações S3A adicionadas")
    
except Exception as e:
    print(f"  ❌ Erro ao criar Spark Session: {e}")
    import traceback
    traceback.print_exc()
    
    print("\n" + "=" * 80)
    print("TROUBLESHOOTING")
    print("=" * 80)
    print("1. Reinicie o container: docker restart govbr-jupyter-delta")
    print("2. Verifique Java: docker exec govbr-jupyter-delta java -version")
    print("3. Verifique processos: docker exec govbr-jupyter-delta ps aux | grep java")
    print("4. Verifique memória: docker exec govbr-jupyter-delta free -h")
    
    raise RuntimeError(f"Falha ao criar Spark Session: {e}")

# ============================================================================
# PASSO 4: Tornar disponível globalmente
# ============================================================================
print("\n[4/4] Finalizando...")

try:
    import __main__
    __main__.spark = spark
    globals()['spark'] = spark
    
    print("  ✅ Spark Session disponível como variável global 'spark'")
    
    print("\n" + "=" * 80)
    print("✅ CORREÇÃO CONCLUÍDA!")
    print("=" * 80)
    print("\nA Spark Session está pronta para uso.")
    print("Use 'spark' para acessar a sessão.")
    
except Exception as e:
    print(f"  ⚠️  Erro ao finalizar: {e}")
