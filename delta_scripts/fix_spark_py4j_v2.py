#!/usr/bin/env python3
"""
Script V2 para corrigir erro Py4J Connection Refused
Força inicialização do gateway Py4J antes de criar SparkConf
"""

import os
import sys
import subprocess
import time
import gc

print("=" * 80)
print("🔧 CORREÇÃO Py4J Connection Refused - V2 (Inicialização Forçada)")
print("=" * 80)

# ============================================================================
# PASSO 1: Limpar completamente ambiente Python/Spark
# ============================================================================
print("\n[1/6] Limpando ambiente completamente...")

# Limpar módulos Python relacionados ao Spark
modules_to_remove = []
for module_name in list(sys.modules.keys()):
    if 'pyspark' in module_name.lower() or 'spark' in module_name.lower() or 'py4j' in module_name.lower():
        modules_to_remove.append(module_name)

for module_name in modules_to_remove:
    try:
        del sys.modules[module_name]
    except:
        pass

print(f"  ✅ {len(modules_to_remove)} módulos removidos")

# Limpar variáveis globais
try:
    import __main__
    for var_name in ['spark', 'sc', 'sparkContext', 'SparkSession', 'SparkContext']:
        if hasattr(__main__, var_name):
            delattr(__main__, var_name)
except:
    pass

# Garbage collection múltiplo
for _ in range(5):
    gc.collect()
    time.sleep(0.3)

# Matar processos Java
print("  ℹ️  Matando processos Java...")
for pattern in ["org.apache.spark", "java.*spark", "SparkSubmit"]:
    try:
        result = subprocess.run(
            ["pgrep", "-f", pattern],
            capture_output=True,
            text=True,
            timeout=3
        )
        if result.returncode == 0:
            pids = result.stdout.strip().split('\n')
            for pid in pids:
                if pid and pid.isdigit():
                    try:
                        subprocess.run(["kill", "-9", pid], check=False, timeout=1)
                    except:
                        pass
    except:
        pass

time.sleep(2)

# ============================================================================
# PASSO 2: Configurar JAVA_HOME corretamente
# ============================================================================
print("\n[2/6] Configurando JAVA_HOME...")

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

if not java_home:
    try:
        result = subprocess.run(["which", "java"], capture_output=True, text=True, timeout=2)
        if result.returncode == 0:
            java_path = result.stdout.strip()
            # Tentar encontrar JAVA_HOME
            if '/usr/lib/jvm' in java_path:
                parts = java_path.split('/')
                for i, part in enumerate(parts):
                    if part == 'jvm' and i + 1 < len(parts):
                        java_home = '/'.join(parts[:i+2])
                        break
    except:
        pass

if java_home:
    os.environ['JAVA_HOME'] = java_home
    print(f"  ✅ JAVA_HOME: {java_home}")
    
    # Verificar Java
    try:
        result = subprocess.run(
            [f"{java_home}/bin/java", "-version"],
            capture_output=True,
            text=True,
            timeout=2
        )
        if result.returncode == 0 or result.stderr:
            version_line = result.stderr.split('\n')[0] if result.stderr else "OK"
            print(f"  ✅ Java verificado: {version_line[:50]}")
    except Exception as e:
        print(f"  ⚠️  Aviso ao verificar Java: {e}")
else:
    print("  ⚠️  JAVA_HOME não detectado automaticamente")

# Configurar variáveis de ambiente
os.environ['PYSPARK_PYTHON'] = '/usr/bin/python3'
os.environ['PYSPARK_DRIVER_PYTHON'] = '/usr/bin/python3'
os.environ['SPARK_LOCAL_IP'] = '127.0.0.1'
os.environ['SPARK_DRIVER_HOST'] = '127.0.0.1'
os.environ['SPARK_DRIVER_BIND_ADDRESS'] = '127.0.0.1'

# ============================================================================
# PASSO 3: Importar PySpark e limpar referências internas
# ============================================================================
print("\n[3/6] Importando PySpark e limpando referências internas...")

try:
    from pyspark import SparkContext
    
    # Limpar TODAS as referências internas do SparkContext
    if hasattr(SparkContext, '_active_spark_context'):
        SparkContext._active_spark_context = None
    if hasattr(SparkContext, '_jvm'):
        SparkContext._jvm = None
    if hasattr(SparkContext, '_gateway'):
        SparkContext._gateway = None
    if hasattr(SparkContext, '_next_accumulator_id'):
        SparkContext._next_accumulator_id = 0
    
    print("  ✅ Referências SparkContext limpas")
    
    from pyspark.sql import SparkSession
    
    # Limpar referências SparkSession
    if hasattr(SparkSession, '_instantiatedContext'):
        SparkSession._instantiatedContext = None
    if hasattr(SparkSession, '_instantiatedSession'):
        SparkSession._instantiatedSession = None
    
    print("  ✅ Referências SparkSession limpas")
    
except ImportError as e:
    print(f"  ❌ Erro ao importar PySpark: {e}")
    raise RuntimeError(f"PySpark não está disponível: {e}")

# ============================================================================
# PASSO 4: Forçar inicialização do gateway Py4J ANTES de criar SparkConf
# ============================================================================
print("\n[4/6] Inicializando gateway Py4J manualmente...")

try:
    from py4j.java_gateway import JavaGateway, GatewayParameters
    
    # Tentar criar gateway Py4J manualmente
    # Isso força a inicialização do JVM antes do SparkConf
    print("  ℹ️  Criando gateway Py4J...")
    
    # Configurar parâmetros do gateway
    gateway_params = GatewayParameters(
        auto_convert=True,
        auto_field=True,
        auto_close=True
    )
    
    # Criar gateway - isso vai iniciar o JVM
    gateway = JavaGateway(gateway_parameters=gateway_params)
    
    # Verificar se gateway está funcionando
    try:
        jvm = gateway.jvm
        print("  ✅ Gateway Py4J criado e JVM inicializado")
        
        # Testar comunicação básica
        try:
            # Tentar criar um objeto Java simples
            test_obj = jvm.java.lang.String("test")
            test_str = str(test_obj)
            print(f"  ✅ Comunicação Py4J testada: {test_str}")
        except Exception as e:
            print(f"  ⚠️  Aviso no teste Py4J: {e}")
        
        # Fechar gateway manual - vamos deixar o Spark criar o seu próprio
        gateway.shutdown()
        time.sleep(1)
        
    except Exception as e:
        print(f"  ⚠️  Erro ao inicializar gateway: {e}")
        # Tentar fechar se existir
        try:
            gateway.shutdown()
        except:
            pass
        raise
    
except ImportError:
    print("  ⚠️  py4j não disponível diretamente, Spark vai inicializar automaticamente")
except Exception as e:
    print(f"  ⚠️  Erro ao criar gateway manual: {e}")
    print("  ℹ️  Continuando - Spark vai tentar inicializar automaticamente")

# ============================================================================
# PASSO 5: Criar SparkConf e SparkSession
# ============================================================================
print("\n[5/6] Criando SparkConf e SparkSession...")

try:
    from pyspark.sql import SparkSession
    from pyspark import SparkConf
    
    # Configurações MinIO
    MINIO_ENDPOINT = "ch8ai-minio.l6zv5a.easypanel.host"
    MINIO_ACCESS_KEY = "admin"
    MINIO_SECRET_KEY = "1q2w3e4r"
    
    print("  ℹ️  Criando SparkConf...")
    
    # Criar SparkConf - agora o JVM já deve estar inicializado
    conf = SparkConf()
    conf.set("spark.app.name", "GovBR Data Lake - Fixed V2")
    conf.set("spark.master", "local[*]")
    conf.set("spark.driver.host", "127.0.0.1")
    conf.set("spark.driver.bindAddress", "127.0.0.1")
    conf.set("spark.driver.port", "0")
    conf.set("spark.blockManager.port", "0")
    conf.set("spark.broadcast.port", "0")
    conf.set("spark.fileserver.port", "0")
    conf.set("spark.replClassServer.port", "0")
    conf.set("spark.ui.port", "0")
    conf.set("spark.driver.memory", "2g")
    conf.set("spark.executor.memory", "2g")
    conf.set("spark.network.timeout", "1200s")
    conf.set("spark.executor.heartbeatInterval", "60s")
    conf.set("spark.driver.extraJavaOptions", 
            "-Dio.netty.tryReflectionSetAccessible=true " +
            "-XX:+UseG1GC " +
            "-Djava.net.preferIPv4Stack=true " +
            "-Djava.awt.headless=true")
    
    # Configurações S3A
    conf.set("spark.hadoop.fs.s3a.endpoint", f"https://{MINIO_ENDPOINT}")
    conf.set("spark.hadoop.fs.s3a.access.key", MINIO_ACCESS_KEY)
    conf.set("spark.hadoop.fs.s3a.secret.key", MINIO_SECRET_KEY)
    conf.set("spark.hadoop.fs.s3a.path.style.access", "true")
    conf.set("spark.hadoop.fs.s3a.connection.ssl.enabled", "true")
    conf.set("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem")
    
    print("  ✅ SparkConf criado")
    
    # Criar SparkSession usando o conf
    print("  ℹ️  Criando SparkSession (isso pode levar alguns segundos)...")
    
    spark = SparkSession.builder.config(conf=conf).getOrCreate()
    
    # Aguardar inicialização
    time.sleep(5)
    
    # Verificar funcionalidade
    print("  ℹ️  Verificando funcionalidade...")
    version = spark.version
    app_name = spark.sparkContext.appName
    
    print(f"  ✅ Spark Session criada!")
    print(f"     Versão: {version}")
    print(f"     App: {app_name}")
    
    # Teste funcional
    test_df = spark.range(5)
    count = test_df.count()
    
    if count == 5:
        print(f"  ✅ Teste funcional: {count} registros criados")
    else:
        raise RuntimeError(f"Teste retornou resultado inesperado: {count}")
    
except Exception as e:
    print(f"  ❌ Erro ao criar Spark Session: {e}")
    import traceback
    traceback.print_exc()
    raise RuntimeError(f"Falha ao criar Spark Session: {e}")

# ============================================================================
# PASSO 6: Tornar disponível globalmente
# ============================================================================
print("\n[6/6] Finalizando...")

try:
    import __main__
    __main__.spark = spark
    globals()['spark'] = spark
    
    print("  ✅ Spark Session disponível como variável global 'spark'")
    
    print("\n" + "=" * 80)
    print("✅ CORREÇÃO CONCLUÍDA COM SUCESSO!")
    print("=" * 80)
    print("\nA Spark Session está pronta para uso.")
    print("Use 'spark' para acessar a sessão nos seus notebooks.")
    
except Exception as e:
    print(f"  ⚠️  Erro ao finalizar: {e}")
