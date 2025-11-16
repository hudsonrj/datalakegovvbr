#!/usr/bin/env python3
"""
Script para limpar processos Java zombie e configurar JAVA_HOME corretamente
"""

import os
import subprocess
import sys

print("=" * 80)
print("🧹 LIMPEZA DE PROCESSOS JAVA ZOMBIE")
print("=" * 80)

# Limpar processos Java zombie
print("\n[1/3] Limpando processos Java zombie...")
try:
    result = subprocess.run(
        ["ps", "aux"],
        capture_output=True,
        text=True,
        timeout=5
    )
    if result.returncode == 0:
        zombie_count = 0
        for line in result.stdout.split('\n'):
            if 'java' in line.lower() and '<defunct>' in line:
                parts = line.split()
                if len(parts) > 1:
                    pid = parts[1]
                    if pid.isdigit():
                        try:
                            print(f"  ℹ️  Matando processo zombie PID: {pid}")
                            subprocess.run(["kill", "-9", pid], check=False, timeout=2)
                            zombie_count += 1
                        except:
                            pass
        
        if zombie_count > 0:
            print(f"  ✅ {zombie_count} processos zombie limpos")
        else:
            print("  ℹ️  Nenhum processo zombie encontrado")
except Exception as e:
    print(f"  ⚠️  Erro ao limpar processos: {e}")

# Configurar JAVA_HOME corretamente
print("\n[2/3] Configurando JAVA_HOME...")
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
        result = subprocess.run(
            ["which", "java"],
            capture_output=True,
            text=True,
            timeout=2
        )
        if result.returncode == 0:
            java_path = result.stdout.strip()
            # Tentar encontrar JAVA_HOME a partir do caminho do java
            if '/usr/lib/jvm' in java_path:
                # Extrair caminho base
                parts = java_path.split('/')
                for i, part in enumerate(parts):
                    if part == 'jvm':
                        java_home = '/'.join(parts[:i+2])
                        break
    except:
        pass

if java_home:
    os.environ['JAVA_HOME'] = java_home
    print(f"  ✅ JAVA_HOME configurado: {java_home}")
    
    # Verificar se funciona
    try:
        result = subprocess.run(
            [f"{java_home}/bin/java", "-version"],
            capture_output=True,
            text=True,
            timeout=2
        )
        if result.returncode == 0:
            version_line = result.stderr.split('\n')[0]
            print(f"  ✅ Java verificado: {version_line}")
    except Exception as e:
        print(f"  ⚠️  Aviso ao verificar Java: {e}")
else:
    print("  ⚠️  JAVA_HOME não pôde ser determinado automaticamente")
    print("  💡 Configure manualmente: export JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64")

# Limpar variáveis de ambiente do Spark
print("\n[3/3] Limpando variáveis de ambiente do Spark...")
spark_vars = [
    'SPARK_LOCAL_IP',
    'SPARK_DRIVER_HOST',
    'SPARK_DRIVER_BIND_ADDRESS',
    'SPARK_MASTER',
]

for var in spark_vars:
    if var in os.environ:
        del os.environ[var]
        print(f"  ℹ️  Removido: {var}")

print("\n" + "=" * 80)
print("✅ LIMPEZA CONCLUÍDA")
print("=" * 80)
print("\n💡 Agora você pode tentar criar uma nova Spark Session:")
print("   from pyspark.sql import SparkSession")
print("   spark = SparkSession.builder.appName('Test').getOrCreate()")
