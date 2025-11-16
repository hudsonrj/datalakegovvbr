#!/usr/bin/env python3
"""
Setup Delta Lake usando Spark (versão completa)
Este script deve ser executado dentro do container Spark
"""

import sys
import os

# Adicionar paths necessários
os.environ['PYSPARK_PYTHON'] = 'python3'
os.environ['PYSPARK_DRIVER_PYTHON'] = 'python3'

try:
    from pyspark.sql import SparkSession
    
    print("=" * 80)
    print("DELTA LAKE SETUP COM SPARK")
    print("=" * 80)
    
    # Configurações MinIO
    MINIO_ENDPOINT = "ch8ai-minio.l6zv5a.easypanel.host"
    MINIO_ACCESS_KEY = "admin"
    MINIO_SECRET_KEY = "1q2w3e4r"
    BUCKET_NAME = "govbr"
    
    # IMPORTANTE: Usar a Spark Session existente do notebook
    # Não criar uma nova sessão para evitar problemas com JARs
    print("\n[INFO] Verificando Spark Session existente...")
    spark = SparkSession.getActiveSession()
    
    if spark is None:
        print("⚠️  Nenhuma Spark Session ativa encontrada!")
        print("⚠️  Execute primeiro as células 1-3 do notebook delta_lake_setup.ipynb")
        raise RuntimeError("Spark Session não encontrada. Execute as células 1-3 do notebook primeiro.")
    
    print("✅ Usando Spark Session existente do notebook")
    print(f"✅ Versão Spark: {spark.version}")
    
    # Verificar se os JARs estão no classpath
    print("\n[INFO] Verificando classpath...")
    try:
        spark_context = spark.sparkContext
        packages = spark_context.getConf().get("spark.jars.packages", "")
        jars = spark_context.getConf().get("spark.jars", "")
        if "hadoop-aws" in packages or "hadoop-aws" in jars:
            print("✅ JARs do S3A encontrados no classpath!")
            print(f"   Packages: {packages[:150]}...")
        else:
            print("⚠️  JARs do S3A podem não estar no classpath")
            print(f"   Packages configurados: {packages[:200]}...")
            print(f"   JARs configurados: {jars[:200]}...")
            print("⚠️  Se houver erro de ClassNotFoundException, execute novamente a Célula 3 do notebook")
    except Exception as e:
        print(f"⚠️  Erro ao verificar classpath: {e}")
    
    # Base path S3
    s3_base = f"s3a://{BUCKET_NAME}"
    
    # Função para converter Parquet em Delta
    def convert_to_delta(parquet_path, delta_path, table_name):
        try:
            print(f"\n[Convertendo] {table_name}")
            print(f"  Parquet: {parquet_path}")
            print(f"  Delta: {delta_path}")
            
            # Verificar se o arquivo Parquet existe
            try:
                print(f"  [INFO] Tentando ler Parquet...")
                df = spark.read.parquet(parquet_path)
                count = df.count()
                print(f"  ✅ Lido: {count} registros")
            except Exception as e:
                error_msg = str(e)
                print(f"  ❌ Erro ao ler Parquet: {error_msg[:200]}")
                print(f"  ⚠️  Arquivo pode não existir: {parquet_path}")
                if "Path does not exist" in error_msg or "does not exist" in error_msg.lower():
                    print(f"  💡 Dica: Verifique se o arquivo existe no MinIO")
                return False
            
            # Escrever como Delta
            print(f"  [INFO] Escrevendo Delta Lake...")
            try:
                df.write.format("delta").mode("overwrite").save(delta_path)
                print(f"  ✅ Delta escrito em: {delta_path}")
            except Exception as e:
                print(f"  ❌ Erro ao escrever Delta: {e}")
                import traceback
                traceback.print_exc()
                return False
            
            # Criar tabela no catalog
            print(f"  [INFO] Registrando tabela no catalog...")
            try:
                spark.sql(f"""
                    CREATE TABLE IF NOT EXISTS {table_name}
                    USING DELTA
                    LOCATION '{delta_path}'
                """)
                print(f"  ✅ Tabela registrada no catalog")
            except Exception as e:
                print(f"  ⚠️  Erro ao registrar tabela: {e}")
                # Continuar mesmo assim, pode ser que a tabela já exista
            
            # Verificar se a tabela foi criada e pode ser consultada
            try:
                test_df = spark.sql(f"SELECT COUNT(*) as cnt FROM {table_name}")
                test_count = test_df.collect()[0]['cnt']
                print(f"  ✅ Tabela verificada: {table_name} ({test_count} registros)")
            except Exception as e:
                print(f"  ⚠️  Tabela criada mas não pode ser consultada: {e}")
                print(f"  💡 Tente consultar diretamente: SELECT * FROM delta.`{delta_path}`")
                return False
            
            return True
        except Exception as e:
            print(f"  ❌ Erro ao converter {table_name}: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    # Converter camada Bronze
    print("\n" + "=" * 80)
    print("[1/3] CONVERTENDO BRONZE")
    print("=" * 80)
    bronze_tables = {
        "bronze_municipios": (f"{s3_base}/bronze/ibge/municipios/dt=20251114/data.parquet",
                              f"{s3_base}/delta/bronze/bronze_municipios"),
        "bronze_estados": (f"{s3_base}/bronze/ibge/estados/dt=20251114/data.parquet",
                           f"{s3_base}/delta/bronze/bronze_estados"),
        "bronze_bpc": (f"{s3_base}/bronze/portal_transparencia/bpc_municipios/dt=20251114/data.parquet",
                       f"{s3_base}/delta/bronze/bronze_bpc"),
    }
    
    bronze_success = []
    bronze_failed = []
    for table_name, (parquet_path, delta_path) in bronze_tables.items():
        if convert_to_delta(parquet_path, delta_path, table_name):
            bronze_success.append(table_name)
        else:
            bronze_failed.append(table_name)
    
    # Converter camada Prata
    print("\n" + "=" * 80)
    print("[2/3] CONVERTENDO PRATA")
    print("=" * 80)
    prata_tables = {
        "prata_dim_municipios": (f"{s3_base}/prata/dim_municipios/dt=20251114/data.parquet",
                                 f"{s3_base}/delta/prata/prata_dim_municipios"),
        "prata_dim_estados": (f"{s3_base}/prata/dim_estados/dt=20251114/data.parquet",
                              f"{s3_base}/delta/prata/prata_dim_estados"),
        "prata_fato_bpc": (f"{s3_base}/prata/fato_bpc/dt=20251114/data.parquet",
                           f"{s3_base}/delta/prata/prata_fato_bpc"),
    }
    
    prata_success = []
    prata_failed = []
    for table_name, (parquet_path, delta_path) in prata_tables.items():
        if convert_to_delta(parquet_path, delta_path, table_name):
            prata_success.append(table_name)
        else:
            prata_failed.append(table_name)
    
    # Converter camada Ouro
    print("\n" + "=" * 80)
    print("[3/3] CONVERTENDO OURO")
    print("=" * 80)
    ouro_tables = {
        "ouro_dim_municipios": (f"{s3_base}/ouro/dim_municipios_enriquecida/dt=20251114/data.parquet",
                                f"{s3_base}/delta/ouro/ouro_dim_municipios"),
        "ouro_dim_estados": (f"{s3_base}/ouro/dim_estados_enriquecida/dt=20251114/data.parquet",
                             f"{s3_base}/delta/ouro/ouro_dim_estados"),
        "ouro_fato_bpc": (f"{s3_base}/ouro/fato_bpc_enriquecido/dt=20251114/data.parquet",
                          f"{s3_base}/delta/ouro/ouro_fato_bpc"),
    }
    
    ouro_success = []
    ouro_failed = []
    for table_name, (parquet_path, delta_path) in ouro_tables.items():
        if convert_to_delta(parquet_path, delta_path, table_name):
            ouro_success.append(table_name)
        else:
            ouro_failed.append(table_name)
    
    # Resumo
    print("\n" + "=" * 80)
    print("RESUMO DA CONVERSÃO")
    print("=" * 80)
    print(f"\n✅ Bronze criadas ({len(bronze_success)}): {', '.join(bronze_success) if bronze_success else 'Nenhuma'}")
    if bronze_failed:
        print(f"❌ Bronze falharam ({len(bronze_failed)}): {', '.join(bronze_failed)}")
    print(f"\n✅ Prata criadas ({len(prata_success)}): {', '.join(prata_success) if prata_success else 'Nenhuma'}")
    if prata_failed:
        print(f"❌ Prata falharam ({len(prata_failed)}): {', '.join(prata_failed)}")
    print(f"\n✅ Ouro criadas ({len(ouro_success)}): {', '.join(ouro_success) if ouro_success else 'Nenhuma'}")
    if ouro_failed:
        print(f"❌ Ouro falharam ({len(ouro_failed)}): {', '.join(ouro_failed)}")
    
    # Listar tabelas
    print("\n" + "=" * 80)
    print("TABELAS REGISTRADAS NO CATALOG")
    print("=" * 80)
    try:
        tables = spark.sql("SHOW TABLES").collect()
        if tables:
            for table in tables:
                print(f"  📊 {table.tableName}")
        else:
            print("  ⚠️  Nenhuma tabela encontrada no catalog")
            print("  ℹ️  Isso pode significar que:")
            print("     - Os arquivos Parquet não existem nos caminhos especificados")
            print("     - Houve erro durante a conversão")
            print("     - As tabelas foram criadas mas não registradas no catalog")
    except Exception as e:
        print(f"  ❌ Erro ao listar tabelas: {e}")
    
    # Teste de consulta - apenas para tabelas criadas com sucesso
    print("\n" + "=" * 80)
    print("TESTE DE CONSULTA")
    print("=" * 80)
    
    # Lista de todas as tabelas que foram criadas com sucesso
    all_success_tables = bronze_success + prata_success + ouro_success
    
    if all_success_tables:
        print(f"\n✅ Testando {len(all_success_tables)} tabela(s) criada(s) com sucesso...")
        for table_name in all_success_tables:
            try:
                count_df = spark.sql(f"SELECT COUNT(*) as cnt FROM {table_name}")
                count = count_df.collect()[0]['cnt']
                print(f"✅ {table_name}: {count} registros")
            except Exception as e:
                print(f"❌ {table_name}: Erro ao consultar - {str(e)[:100]}")
        
        # Tentar uma consulta de exemplo com a primeira tabela disponível
        if ouro_success:
            example_table = ouro_success[0]
            try:
                print(f"\n[Exemplo] Consultando {example_table}:")
                spark.sql(f"SELECT * FROM {example_table} LIMIT 3").show(truncate=False)
            except Exception as e:
                print(f"⚠️  Erro ao consultar exemplo: {e}")
        elif prata_success:
            example_table = prata_success[0]
            try:
                print(f"\n[Exemplo] Consultando {example_table}:")
                spark.sql(f"SELECT * FROM {example_table} LIMIT 3").show(truncate=False)
            except Exception as e:
                print(f"⚠️  Erro ao consultar exemplo: {e}")
        elif bronze_success:
            example_table = bronze_success[0]
            try:
                print(f"\n[Exemplo] Consultando {example_table}:")
                spark.sql(f"SELECT * FROM {example_table} LIMIT 3").show(truncate=False)
            except Exception as e:
                print(f"⚠️  Erro ao consultar exemplo: {e}")
    else:
        print("\n⚠️  Nenhuma tabela foi criada com sucesso!")
        print("ℹ️  Verifique:")
        print("   - Se os arquivos Parquet existem nos caminhos especificados")
        print("   - Se há erros de permissão no MinIO")
        print("   - Os logs acima para mais detalhes sobre os erros")
    
    print("\n✅ Setup concluído!")
    # NÃO parar a Spark Session - ela será usada pelo notebook
    # spark.stop()
    
except ImportError as e:
    print(f"❌ Erro de importação: {e}")
    print("Certifique-se de estar executando dentro do container Spark")
    sys.exit(1)
except Exception as e:
    print(f"❌ Erro: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
