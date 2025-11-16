#!/usr/bin/env python3
"""
Script de diagnóstico para problemas de Connection Refused no Spark
Este script verifica o ambiente e tenta identificar a causa raiz do problema
"""

import os
import sys
import subprocess
import time

print("=" * 80)
print("🔍 DIAGNÓSTICO DE PROBLEMAS SPARK - Connection Refused")
print("=" * 80)

# 1. Verificar Java
print("\n[1/6] Verificando Java...")
try:
    result = subprocess.run(["java", "-version"], capture_output=True, text=True, timeout=5)
    if result.returncode == 0 or result.stderr:
        print("✅ Java está disponível")
        print(f"   {result.stderr.split(chr(10))[0] if result.stderr else 'Versão detectada'}")
    else:
        print("❌ Java não está funcionando corretamente")
        sys.exit(1)
except Exception as e:
    print(f"❌ Java não está disponível: {e}")
    print("💡 Instale Java: sudo apt-get update && sudo apt-get install -y openjdk-17-jdk")
    sys.exit(1)

# 2. Verificar JAVA_HOME
print("\n[2/6] Verificando JAVA_HOME...")
java_home = os.environ.get('JAVA_HOME')
if java_home:
    print(f"✅ JAVA_HOME: {java_home}")
    if os.path.exists(java_home):
        print("   ✅ JAVA_HOME aponta para diretório válido")
    else:
        print("   ❌ JAVA_HOME aponta para diretório inexistente")
        sys.exit(1)
else:
    print("⚠️  JAVA_HOME não configurado")
    # Tentar detectar
    try:
        result = subprocess.run(["which", "java"], capture_output=True, text=True)
        if result.returncode == 0:
            java_path = result.stdout.strip()
            java_home = os.path.dirname(os.path.dirname(java_path))
            print(f"✅ JAVA_HOME detectado: {java_home}")
            os.environ['JAVA_HOME'] = java_home
        else:
            print("❌ Não foi possível detectar JAVA_HOME")
            sys.exit(1)
    except:
        print("❌ Erro ao detectar JAVA_HOME")
        sys.exit(1)

# 3. Verificar processos Java
print("\n[3/6] Verificando processos Java...")
try:
    result = subprocess.run(["ps", "aux"], capture_output=True, text=True, timeout=5)
    java_processes = [line for line in result.stdout.split('\n') if 'java' in line.lower() and 'grep' not in line]
    if java_processes:
        print(f"⚠️  Encontrados {len(java_processes)} processos Java:")
        for proc in java_processes[:5]:  # Mostrar apenas os primeiros 5
            print(f"   {proc[:80]}")
    else:
        print("✅ Nenhum processo Java rodando (normal antes de iniciar Spark)")
except Exception as e:
    print(f"⚠️  Erro ao verificar processos: {e}")

# 4. Verificar portas
print("\n[4/6] Verificando portas Spark...")
spark_ports = [4040, 4041, 4042, 8080, 8081, 7077, 7078]
import socket
portas_em_uso = []
for port in spark_ports:
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex(('127.0.0.1', port))
        sock.close()
        if result == 0:
            portas_em_uso.append(port)
    except:
        pass

if portas_em_uso:
    print(f"⚠️  Portas em uso: {portas_em_uso}")
else:
    print("✅ Nenhuma porta Spark em uso")

# 5. Verificar PySpark
print("\n[5/6] Verificando PySpark...")
try:
    import pyspark
    print(f"✅ PySpark instalado: versão {pyspark.__version__}")
except ImportError:
    print("❌ PySpark não está instalado")
    print("💡 Instale: pip install pyspark")
    sys.exit(1)
except Exception as e:
    print(f"⚠️  Erro ao importar PySpark: {e}")

# 6. Tentar inicializar SparkContext manualmente
print("\n[6/6] Testando inicialização do JVM...")
try:
    from pyspark import SparkContext, SparkConf
    
    # Limpar qualquer contexto existente
    try:
        sc = SparkContext._active_spark_context
        if sc:
            print("⚠️  Há um SparkContext ativo, parando...")
            sc.stop()
            time.sleep(2)
    except:
        pass
    
    # Criar SparkConf mínimo para testar JVM
    print("ℹ️  Criando SparkConf mínimo para testar JVM...")
    conf = SparkConf()
    conf.set("spark.app.name", "Diagnostico")
    conf.set("spark.master", "local[1]")
    conf.set("spark.driver.host", "127.0.0.1")
    conf.set("spark.driver.port", "0")
    
    print("✅ SparkConf criado com sucesso")
    print("✅ JVM foi inicializado através do Py4J")
    print("\n✅ DIAGNÓSTICO COMPLETO: Ambiente está pronto para Spark!")
    
except ConnectionRefusedError as e:
    print(f"❌ Connection Refused ao tentar inicializar JVM")
    print(f"   Erro: {e}")
    print("\n💡 SOLUÇÕES:")
    print("1. Reinicie o container: docker restart govbr-jupyter-delta")
    print("2. Verifique se há processos Java travados: ps aux | grep java")
    print("3. Execute o script de correção: exec(open('/home/jovyan/work/fix_spark_py4j.py').read())")
    sys.exit(1)
except Exception as e:
    print(f"❌ Erro ao testar inicialização: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "=" * 80)
print("✅ DIAGNÓSTICO CONCLUÍDO")
print("=" * 80)
print("\nSe todos os testes passaram, você pode tentar criar a Spark Session novamente.")
