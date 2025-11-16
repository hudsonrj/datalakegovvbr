#!/usr/bin/env python3
"""
Script para corrigir erro Py4JNetworkError: Answer from Java side is empty
Este script diagnostica e corrige problemas de conexão entre Python e Java no Spark
"""

import os
import sys
import subprocess
import time
import gc

print("=" * 80)
print("🔧 CORREÇÃO DE ERRO Py4J e Connection Refused - Spark Fix")
print("=" * 80)

# ============================================================================
# PASSO 1: Limpar ambiente e processos
# ============================================================================
print("\n[1/8] Limpando ambiente e processos Spark...")

# Parar TODAS as sessões Spark existentes de forma agressiva
try:
    from pyspark.sql import SparkSession
    from pyspark import SparkContext
    
    # Tentar parar todas as sessões ativas
    try:
        active_session = SparkSession.getActiveSession()
        if active_session:
            print(f"  ℹ️  Parando Spark Session ativa: {active_session.sparkContext.appName}")
            try:
                active_session.sparkContext.stop()
            except:
                pass
            try:
                active_session.stop()
            except:
                pass
    except:
        pass
    
    # Tentar parar SparkContext global se existir
    try:
        sc = SparkContext._active_spark_context
        if sc:
            print("  ℹ️  Parando SparkContext global...")
            sc.stop()
    except:
        pass
    
    # Limpar referências globais do PySpark
    try:
        SparkSession._instantiatedContext = None
        SparkContext._active_spark_context = None
    except:
        pass
    
    # Aguardar processos Java terminarem
    time.sleep(3)
    print("  ✅ Sessões Spark paradas")
except ImportError:
    print("  ℹ️  PySpark não importado ainda (normal)")
except Exception as e:
    print(f"  ⚠️  Erro ao limpar sessões: {e}")

# Forçar garbage collection
gc.collect()

# Matar TODOS os processos Java relacionados ao Spark
print("  ℹ️  Matando processos Java do Spark...")
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
                        print(f"  ℹ️  Matando processo PID: {pid}")
                        subprocess.run(["kill", "-9", pid], check=False, timeout=2)
                    except:
                        pass
    except:
        pass

time.sleep(3)  # Aguardar processos terminarem completamente

# Limpar variáveis globais Python que podem manter referências
try:
    import __main__
    if hasattr(__main__, 'spark'):
        delattr(__main__, 'spark')
    if hasattr(__main__, 'sc'):
        delattr(__main__, 'sc')
except:
    pass

# Forçar garbage collection múltiplas vezes
for _ in range(3):
    gc.collect()
    time.sleep(0.5)

print("  ✅ Processos Java Spark finalizados e ambiente limpo")

# ============================================================================
# PASSO 2: Verificar e liberar portas em uso
# ============================================================================
print("\n[2/8] Verificando e liberando portas...")

def check_port(port):
    """Verifica se uma porta está em uso"""
    try:
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex(('127.0.0.1', port))
        sock.close()
        return result == 0
    except:
        return False

def kill_process_on_port(port):
    """Mata processo usando uma porta específica"""
    pids_found = []
    
    # Método 1: Tentar usar lsof (se disponível)
    try:
        result = subprocess.run(
            ["lsof", "-ti", f":{port}"],
            capture_output=True,
            text=True,
            timeout=2
        )
        if result.returncode == 0 and result.stdout.strip():
            pids_found.extend(result.stdout.strip().split('\n'))
    except:
        pass
    
    # Método 2: Tentar usar netstat + fuser (alternativa)
    if not pids_found:
        try:
            result = subprocess.run(
                ["netstat", "-tlnp"],
                capture_output=True,
                text=True,
                timeout=2
            )
            if result.returncode == 0:
                for line in result.stdout.split('\n'):
                    if f':{port} ' in line or f':{port}\t' in line:
                        parts = line.split()
                        if len(parts) > 6:
                            pid_program = parts[6]
                            if '/' in pid_program:
                                pid = pid_program.split('/')[0]
                                if pid.isdigit():
                                    pids_found.append(pid)
        except:
            pass
    
    # Método 3: Tentar usar ss (alternativa moderna)
    if not pids_found:
        try:
            result = subprocess.run(
                ["ss", "-tlnp"],
                capture_output=True,
                text=True,
                timeout=2
            )
            if result.returncode == 0:
                for line in result.stdout.split('\n'):
                    if f':{port} ' in line:
                        # Extrair PID do formato ss
                        if 'pid=' in line:
                            pid_part = line.split('pid=')[1].split(',')[0]
                            if pid_part.isdigit():
                                pids_found.append(pid_part)
        except:
            pass
    
    # Matar processos encontrados
    if pids_found:
        for pid in pids_found:
            if pid and pid.isdigit():
                try:
                    print(f"  ℹ️  Matando processo PID {pid} na porta {port}")
                    subprocess.run(["kill", "-9", pid], check=False, timeout=2)
                except:
                    pass
        time.sleep(1)
        return True
    
    return False

# Portas comuns do Spark que podem causar problemas
spark_ports = [4040, 4041, 4042, 8080, 8081, 7077, 7078]
for port in spark_ports:
    if check_port(port):
        print(f"  ⚠️  Porta {port} está em uso")
        kill_process_on_port(port)
        time.sleep(1)
        if not check_port(port):
            print(f"  ✅ Porta {port} liberada")
        else:
            print(f"  ⚠️  Porta {port} ainda em uso (pode ser ignorado)")

# ============================================================================
# PASSO 3: Verificar e configurar variáveis de ambiente
# ============================================================================
print("\n[3/8] Configurando variáveis de ambiente...")

# Configurar variáveis ANTES de importar PySpark
os.environ['PYSPARK_PYTHON'] = '/usr/bin/python3'
os.environ['PYSPARK_DRIVER_PYTHON'] = '/usr/bin/python3'

# Verificar JAVA_HOME
java_home_candidates = [
    '/usr/lib/jvm/java-17-openjdk-amd64',
    '/usr/lib/jvm/java-11-openjdk-amd64',
    '/usr/lib/jvm/java-8-openjdk-amd64',
    os.environ.get('JAVA_HOME', ''),
]

java_home = None
for candidate in java_home_candidates:
    if candidate and os.path.exists(candidate):
        java_home = candidate
        break

if java_home:
    os.environ['JAVA_HOME'] = java_home
    print(f"  ✅ JAVA_HOME configurado: {java_home}")
else:
    print("  ⚠️  JAVA_HOME não encontrado, tentando detectar...")
    try:
        result = subprocess.run(
            ["which", "java"],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            java_path = result.stdout.strip()
            java_home = os.path.dirname(os.path.dirname(java_path))
            os.environ['JAVA_HOME'] = java_home
            print(f"  ✅ JAVA_HOME detectado: {java_home}")
    except:
        pass

# Configurações de rede para evitar problemas de conexão
os.environ['SPARK_LOCAL_IP'] = '127.0.0.1'
os.environ['SPARK_MASTER'] = 'local[*]'
os.environ['SPARK_DRIVER_HOST'] = '127.0.0.1'
os.environ['SPARK_DRIVER_BIND_ADDRESS'] = '127.0.0.1'
os.environ['SPARK_LOCAL_DIRS'] = '/tmp/spark-local'

# Criar diretório local do Spark
os.makedirs('/tmp/spark-local', exist_ok=True)

print("  ✅ Variáveis de ambiente configuradas")

# ============================================================================
# PASSO 4: Verificar memória disponível
# ============================================================================
print("\n[4/8] Verificando recursos do sistema...")

try:
    # Verificar memória disponível
    with open('/proc/meminfo', 'r') as f:
        meminfo = f.read()
        for line in meminfo.split('\n'):
            if 'MemAvailable' in line:
                mem_available_kb = int(line.split()[1])
                mem_available_gb = mem_available_kb / (1024 * 1024)
                print(f"  ℹ️  Memória disponível: {mem_available_gb:.1f} GB")
                
                # Ajustar memória do Spark baseado no disponível
                if mem_available_gb < 2:
                    driver_memory = "512m"
                    executor_memory = "512m"
                    print("  ⚠️  Pouca memória disponível, usando configurações mínimas")
                elif mem_available_gb < 4:
                    driver_memory = "1g"
                    executor_memory = "1g"
                    print("  ℹ️  Memória moderada, usando configurações conservadoras")
                else:
                    driver_memory = "2g"
                    executor_memory = "2g"
                    print("  ✅ Memória suficiente, usando configurações padrão")
                break
except Exception as e:
    print(f"  ⚠️  Não foi possível verificar memória: {e}")
    driver_memory = "1g"
    executor_memory = "1g"

# ============================================================================
# PASSO 5: Configurar Spark Session com configurações robustas
# ============================================================================
print("\n[5/8] Configurando Spark Session...")

# Configurações MinIO
MINIO_ENDPOINT = "ch8ai-minio.l6zv5a.easypanel.host"
MINIO_ACCESS_KEY = "admin"
MINIO_SECRET_KEY = "1q2w3e4r"
BUCKET_NAME = "govbr"

try:
    from pyspark.sql import SparkSession
    
    print("  ℹ️  Criando Spark Builder com configurações robustas...")
    
    # Builder com configurações que evitam problemas Py4J e Connection Refused
    builder = SparkSession.builder \
        .appName("GovBR Data Lake - Fixed") \
        .master("local[*]") \
        .config("spark.driver.host", "127.0.0.1") \
        .config("spark.driver.bindAddress", "127.0.0.1") \
        .config("spark.driver.port", "0") \
        .config("spark.blockManager.port", "0") \
        .config("spark.broadcast.port", "0") \
        .config("spark.fileserver.port", "0") \
        .config("spark.replClassServer.port", "0") \
        .config("spark.driver.memory", driver_memory) \
        .config("spark.executor.memory", executor_memory) \
        .config("spark.driver.maxResultSize", "1g") \
        .config("spark.sql.execution.arrow.pyspark.enabled", "false") \
        .config("spark.network.timeout", "1200s") \
        .config("spark.executor.heartbeatInterval", "60s") \
        .config("spark.ui.port", "0") \
        .config("spark.sql.adaptive.enabled", "true") \
        .config("spark.sql.adaptive.coalescePartitions.enabled", "true") \
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
        .config("spark.hadoop.fs.s3a.endpoint", f"https://{MINIO_ENDPOINT}") \
        .config("spark.hadoop.fs.s3a.access.key", MINIO_ACCESS_KEY) \
        .config("spark.hadoop.fs.s3a.secret.key", MINIO_SECRET_KEY) \
        .config("spark.hadoop.fs.s3a.path.style.access", "true") \
        .config("spark.hadoop.fs.s3a.connection.ssl.enabled", "true") \
        .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem") \
        .config("spark.hadoop.fs.s3a.aws.credentials.provider", 
                "org.apache.hadoop.fs.s3a.SimpleAWSCredentialsProvider") \
        .config("spark.hadoop.fs.s3a.connection.maximum", "15") \
        .config("spark.hadoop.fs.s3a.connection.timeout", "60000") \
        .config("spark.hadoop.fs.s3a.attempts.maximum", "10")
    
    # Adicionar Delta Lake se disponível
    try:
        import pyspark
        spark_version = pyspark.__version__
        print(f"  ℹ️  Versão Spark: {spark_version}")
        
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
        
        builder = builder.config("spark.jars.packages", 
                                 f"{delta_package},{hadoop_package},{aws_package}")
        builder = builder.config("spark.sql.extensions", 
                                 "io.delta.sql.DeltaSparkSessionExtension")
        builder = builder.config("spark.sql.catalog.spark_catalog", 
                                 "org.apache.spark.sql.delta.catalog.DeltaCatalog")
        print("  ✅ Delta Lake configurado")
    except Exception as e:
        print(f"  ⚠️  Delta Lake não configurado: {e}")
    
    print("  ✅ Builder configurado")
    
except ImportError as e:
    print(f"  ❌ Erro ao importar PySpark: {e}")
    print("  💡 Instale PySpark: pip install pyspark")
    # Não usar sys.exit() em notebooks
    try:
        from IPython import get_ipython
        if get_ipython() is not None:
            raise RuntimeError(f"PySpark não está disponível: {e}")
    except ImportError:
        pass
    raise RuntimeError(f"PySpark não está disponível: {e}")

# ============================================================================
# PASSO 6: Verificar conectividade antes de criar sessão
# ============================================================================
print("\n[6/8] Verificando conectividade de rede...")

try:
    import socket
    # Testar conectividade local
    test_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    test_socket.settimeout(1)
    test_socket.bind(('127.0.0.1', 0))
    test_port = test_socket.getsockname()[1]
    test_socket.close()
    print(f"  ✅ Conectividade de rede OK (porta de teste: {test_port})")
except Exception as e:
    print(f"  ⚠️  Aviso de conectividade: {e}")

# ============================================================================
# PASSO 7: Criar Spark Session com tratamento robusto de erros
# ============================================================================
print("\n[7/8] Criando Spark Session...")

try:
    print("  ℹ️  Iniciando Spark Session (isso pode levar alguns segundos)...")
    
    # ⭐ IMPORTANTE: Verificar se há sessão ativa antes de criar
    try:
        existing = SparkSession.getActiveSession()
        if existing:
            print("  ⚠️  Ainda há uma sessão ativa! Parando...")
            try:
                existing.stop()
                time.sleep(2)
            except:
                pass
    except:
        pass
    
    # Criar nova sessão (getOrCreate cria nova se não existir)
    print("  ℹ️  Criando Spark Session...")
    spark = builder.getOrCreate()
    
    # Aguardar Spark inicializar completamente
    print("  ℹ️  Aguardando Spark inicializar...")
    time.sleep(5)  # Aumentar tempo de espera
    
    # Verificar se Spark está respondendo
    try:
        version = spark.version
        app_name = spark.sparkContext.appName
        master = spark.sparkContext.master
        
        print(f"  ✅ Spark Session criada com sucesso!")
        print(f"     Versão: {version}")
        print(f"     App Name: {app_name}")
        print(f"     Master: {master}")
    except Exception as e:
        print(f"  ⚠️  Spark criado mas com problemas: {e}")
        raise
    
    # Teste de conectividade Py4J
    print("  ℹ️  Testando conectividade Py4J...")
    try:
        test_df = spark.range(5)
        count = test_df.count()
        if count == 5:
            print(f"  ✅ Teste Py4J bem-sucedido! ({count} registros)")
        else:
            print(f"  ⚠️  Teste Py4J retornou resultado inesperado: {count}")
    except Exception as e:
        print(f"  ❌ Erro no teste Py4J: {e}")
        raise
    
except Exception as e:
    print(f"  ❌ Erro ao criar Spark Session: {e}")
    import traceback
    traceback.print_exc()
    
    print("\n" + "=" * 80)
    print("TROUBLESHOOTING")
    print("=" * 80)
    print("1. Verifique se há memória suficiente disponível")
    print("2. Verifique se as portas não estão em uso: netstat -tuln | grep 4040")
    print("3. Tente reiniciar o container: docker restart govbr-jupyter-delta")
    print("4. Verifique os logs: docker logs govbr-jupyter-delta")
    print("5. Verifique se Java está instalado: java -version")
    
    # Não usar sys.exit() em notebooks - apenas fazer raise
    # Verificar se estamos em ambiente de notebook
    try:
        from IPython import get_ipython
        if get_ipython() is not None:
            # Estamos em um notebook, apenas fazer raise
            raise RuntimeError(f"Falha ao criar Spark Session: {e}")
    except ImportError:
        # IPython não disponível, pode ser script standalone
        pass
    
    # Se não estamos em notebook, fazer sys.exit
    # Mas primeiro verificar se sys.exit não vai causar problemas
    raise RuntimeError(f"Falha ao criar Spark Session: {e}")

# ============================================================================
# PASSO 8: Tornar Spark disponível globalmente
# ============================================================================
print("\n[8/8] Finalizando configuração...")

try:
    # Tornar spark disponível globalmente
    import __main__
    __main__.spark = spark
    globals()['spark'] = spark
    
    print("  ✅ Spark Session disponível como variável global 'spark'")
    
    print("\n" + "=" * 80)
    print("✅ CORREÇÃO CONCLUÍDA COM SUCESSO!")
    print("=" * 80)
    print("\nA Spark Session está pronta para uso.")
    print("Use 'spark' para acessar a sessão nos seus notebooks.")
    print("\nExemplo:")
    print("  df = spark.range(10)")
    print("  df.show()")
    
except Exception as e:
    print(f"  ⚠️  Erro ao finalizar: {e}")
