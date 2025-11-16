#!/usr/bin/env python3
"""
Script ÚNICO para inicializar Spark - Tenta todas as abordagens automaticamente
Execute este script no notebook e ele tentará todas as soluções até funcionar
"""

import os
import sys
import subprocess
import time
import gc

print("=" * 80)
print("🚀 INICIALIZAÇÃO AUTOMÁTICA DO SPARK")
print("=" * 80)
print("Este script tentará múltiplas abordagens até conseguir inicializar o Spark")
print("=" * 80)

# ============================================================================
# FUNÇÃO AUXILIAR: Limpar ambiente
# ============================================================================
def limpar_ambiente():
    """Limpa completamente o ambiente Python/Spark"""
    print("\n🧹 Limpando ambiente...")
    
    # Matar processos Java
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
    
    time.sleep(2)
    
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
        time.sleep(0.3)
    
    print(f"  ✅ Ambiente limpo ({len(modules_to_remove)} módulos removidos)")

# ============================================================================
# FUNÇÃO AUXILIAR: Configurar JAVA_HOME
# ============================================================================
def configurar_java_home():
    """Configura JAVA_HOME automaticamente"""
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
        print("  ⚠️  JAVA_HOME não detectado automaticamente")
    
    os.environ['PYSPARK_PYTHON'] = '/usr/bin/python3'
    os.environ['PYSPARK_DRIVER_PYTHON'] = '/usr/bin/python3'
    os.environ['SPARK_LOCAL_IP'] = '127.0.0.1'
    os.environ['SPARK_DRIVER_HOST'] = '127.0.0.1'
    os.environ['SPARK_DRIVER_BIND_ADDRESS'] = '127.0.0.1'

# ============================================================================
# ABORDAGEM 1: Método Simples (mais provável de funcionar)
# ============================================================================
def tentar_abordagem_simples():
    """Tenta criar Spark Session com configurações mínimas"""
    print("\n" + "=" * 80)
    print("📋 ABORDAGEM 1: Método Simples")
    print("=" * 80)
    
    try:
        from pyspark.sql import SparkSession
        
        print("  ℹ️  Criando SparkSession com configurações mínimas...")
        
        # Configurar pacotes necessários para S3/MinIO
        import pyspark
        spark_version = pyspark.__version__
        
        # Determinar versões dos pacotes baseado na versão do Spark
        if spark_version.startswith("4."):
            hadoop_package = "org.apache.hadoop:hadoop-aws:3.3.4"
            aws_package = "com.amazonaws:aws-java-sdk-bundle:1.12.262"
        else:
            # Spark 3.x
            hadoop_package = "org.apache.hadoop:hadoop-aws:3.3.4"
            aws_package = "com.amazonaws:aws-java-sdk-bundle:1.12.262"
        
        builder = SparkSession.builder \
            .appName("GovBR Data Lake") \
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
        
        # Verificar
        version = spark.version
        app_name = spark.sparkContext.appName
        
        # Teste básico
        test_df = spark.range(3)
        count = test_df.count()
        
        if count == 3:
            print(f"  ✅ Spark inicializado com sucesso!")
            print(f"     Versão: {version}")
            print(f"     App: {app_name}")
            
            # Adicionar configurações S3A ANTES de usar
            MINIO_ENDPOINT = "ch8ai-minio.l6zv5a.easypanel.host"
            MINIO_ACCESS_KEY = "admin"
            MINIO_SECRET_KEY = "1q2w3e4r"
            
            # Configurar S3A usando SparkContext para garantir que seja aplicado
            spark.sparkContext._jsc.hadoopConfiguration().set("fs.s3a.endpoint", f"https://{MINIO_ENDPOINT}")
            spark.sparkContext._jsc.hadoopConfiguration().set("fs.s3a.access.key", MINIO_ACCESS_KEY)
            spark.sparkContext._jsc.hadoopConfiguration().set("fs.s3a.secret.key", MINIO_SECRET_KEY)
            spark.sparkContext._jsc.hadoopConfiguration().set("fs.s3a.path.style.access", "true")
            spark.sparkContext._jsc.hadoopConfiguration().set("fs.s3a.connection.ssl.enabled", "true")
            spark.sparkContext._jsc.hadoopConfiguration().set("fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem")
            spark.sparkContext._jsc.hadoopConfiguration().set("fs.s3a.aws.credentials.provider", "org.apache.hadoop.fs.s3a.SimpleAWSCredentialsProvider")
            
            # Também configurar via spark.conf para compatibilidade
            spark.conf.set("spark.hadoop.fs.s3a.endpoint", f"https://{MINIO_ENDPOINT}")
            spark.conf.set("spark.hadoop.fs.s3a.access.key", MINIO_ACCESS_KEY)
            spark.conf.set("spark.hadoop.fs.s3a.secret.key", MINIO_SECRET_KEY)
            spark.conf.set("spark.hadoop.fs.s3a.path.style.access", "true")
            spark.conf.set("spark.hadoop.fs.s3a.connection.ssl.enabled", "true")
            spark.conf.set("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem")
            spark.conf.set("spark.hadoop.fs.s3a.aws.credentials.provider", "org.apache.hadoop.fs.s3a.SimpleAWSCredentialsProvider")
            
            return spark
        else:
            raise RuntimeError(f"Teste retornou {count} em vez de 3")
            
    except Exception as e:
        print(f"  ❌ Abordagem 1 falhou: {e}")
        return None

# ============================================================================
# ABORDAGEM 2: Com limpeza mais agressiva
# ============================================================================
def tentar_abordagem_agressiva():
    """Tenta com limpeza mais agressiva"""
    print("\n" + "=" * 80)
    print("📋 ABORDAGEM 2: Limpeza Agressiva")
    print("=" * 80)
    
    limpar_ambiente()
    configurar_java_home()
    
    try:
        from pyspark import SparkContext
        
        # Limpar referências internas
        if hasattr(SparkContext, '_active_spark_context'):
            SparkContext._active_spark_context = None
        if hasattr(SparkContext, '_jvm'):
            SparkContext._jvm = None
        if hasattr(SparkContext, '_gateway'):
            SparkContext._gateway = None
        
        from pyspark.sql import SparkSession
        
        if hasattr(SparkSession, '_instantiatedContext'):
            SparkSession._instantiatedContext = None
        if hasattr(SparkSession, '_instantiatedSession'):
            SparkSession._instantiatedSession = None
        
        print("  ℹ️  Criando SparkSession após limpeza agressiva...")
        
        # Configurar pacotes necessários
        import pyspark
        spark_version = pyspark.__version__
        
        if spark_version.startswith("4."):
            hadoop_package = "org.apache.hadoop:hadoop-aws:3.3.4"
            aws_package = "com.amazonaws:aws-java-sdk-bundle:1.12.262"
        else:
            hadoop_package = "org.apache.hadoop:hadoop-aws:3.3.4"
            aws_package = "com.amazonaws:aws-java-sdk-bundle:1.12.262"
        
        builder = SparkSession.builder \
            .appName("GovBR Data Lake - Clean") \
            .master("local[1]") \
            .config("spark.driver.host", "127.0.0.1") \
            .config("spark.driver.bindAddress", "127.0.0.1") \
            .config("spark.driver.port", "0") \
            .config("spark.driver.memory", "1g") \
            .config("spark.executor.memory", "1g") \
            .config("spark.jars.packages", f"{hadoop_package},{aws_package}")
        
        spark = builder.getOrCreate()
        time.sleep(5)
        
        # Verificar
        test_df = spark.range(3)
        count = test_df.count()
        
        if count == 3:
            print(f"  ✅ Spark inicializado após limpeza agressiva!")
            
            # Adicionar S3A usando SparkContext
            MINIO_ENDPOINT = "ch8ai-minio.l6zv5a.easypanel.host"
            spark.sparkContext._jsc.hadoopConfiguration().set("fs.s3a.endpoint", f"https://{MINIO_ENDPOINT}")
            spark.sparkContext._jsc.hadoopConfiguration().set("fs.s3a.access.key", "admin")
            spark.sparkContext._jsc.hadoopConfiguration().set("fs.s3a.secret.key", "1q2w3e4r")
            spark.sparkContext._jsc.hadoopConfiguration().set("fs.s3a.path.style.access", "true")
            spark.sparkContext._jsc.hadoopConfiguration().set("fs.s3a.connection.ssl.enabled", "true")
            spark.sparkContext._jsc.hadoopConfiguration().set("fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem")
            spark.sparkContext._jsc.hadoopConfiguration().set("fs.s3a.aws.credentials.provider", "org.apache.hadoop.fs.s3a.SimpleAWSCredentialsProvider")
            
            # Também via spark.conf
            spark.conf.set("spark.hadoop.fs.s3a.endpoint", f"https://{MINIO_ENDPOINT}")
            spark.conf.set("spark.hadoop.fs.s3a.access.key", "admin")
            spark.conf.set("spark.hadoop.fs.s3a.secret.key", "1q2w3e4r")
            spark.conf.set("spark.hadoop.fs.s3a.path.style.access", "true")
            spark.conf.set("spark.hadoop.fs.s3a.connection.ssl.enabled", "true")
            spark.conf.set("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem")
            spark.conf.set("spark.hadoop.fs.s3a.aws.credentials.provider", "org.apache.hadoop.fs.s3a.SimpleAWSCredentialsProvider")
            
            return spark
        else:
            raise RuntimeError(f"Teste retornou {count}")
            
    except Exception as e:
        print(f"  ❌ Abordagem 2 falhou: {e}")
        return None

# ============================================================================
# EXECUÇÃO PRINCIPAL
# ============================================================================

# Limpar ambiente inicial
limpar_ambiente()
configurar_java_home()

# Tentar abordagem 1
spark = tentar_abordagem_simples()

# Se não funcionou, tentar abordagem 2
if spark is None:
    print("\n⚠️  Abordagem 1 não funcionou, tentando abordagem 2...")
    spark = tentar_abordagem_agressiva()

# Se ainda não funcionou
if spark is None:
    print("\n" + "=" * 80)
    print("❌ NENHUMA ABORDAGEM FUNCIONOU")
    print("=" * 80)
    print("\n💡 SOLUÇÕES:")
    print("1. Reinicie o container: docker restart govbr-jupyter-delta")
    print("2. Execute no terminal do container:")
    print("   docker exec -it govbr-jupyter-delta bash")
    print("   ps aux | grep java")
    print("   killall -9 java")
    print("3. Verifique memória: free -h")
    print("4. Verifique Java: java -version")
    print("\nDepois de reiniciar, execute este script novamente.")
    raise RuntimeError("Não foi possível inicializar o Spark. Tente reiniciar o container.")

# Tornar disponível globalmente
try:
    import __main__
    __main__.spark = spark
    globals()['spark'] = spark
    
    print("\n" + "=" * 80)
    print("✅ SPARK INICIALIZADO COM SUCESSO!")
    print("=" * 80)
    print(f"\nVersão: {spark.version}")
    print(f"App: {spark.sparkContext.appName}")
    print("\nA variável 'spark' está disponível para uso.")
    print("\nExemplo:")
    print("  df = spark.range(10)")
    print("  df.show()")
    
except Exception as e:
    print(f"⚠️  Erro ao tornar disponível globalmente: {e}")
