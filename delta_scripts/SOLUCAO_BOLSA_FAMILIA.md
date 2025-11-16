# 🔧 Solução para Dados de Bolsa Família

## Problema
A API do Portal da Transparência para Bolsa Família não está retornando dados.

## Solução Implementada

### Opção 1: Dados Simulados Automáticos (Recomendado)
O script `01_bronze_ingestion.py` agora **automaticamente gera dados simulados** quando a API não está disponível.

**Como usar:**
```python
# Execute a ingestão Bronze normalmente
exec(open('/home/jovyan/work/01_bronze_ingestion.py').read())
```

Se a API falhar, o script automaticamente:
- ✅ Gera dados simulados realistas para 50 municípios de SP
- ✅ Calcula beneficiários baseado em percentuais realistas (8-30% da população)
- ✅ Calcula valores baseados em médias reais do Bolsa Família (R$ 250-450 por beneficiário)
- ✅ Salva os dados na camada Bronze

### Opção 2: Gerar Dados Simulados Manualmente
Se preferir gerar os dados simulados separadamente:

```python
exec(open('/home/jovyan/work/gerar_dados_simulados_bolsa_familia.py').read())
```

## Dados Simulados

Os dados simulados incluem:
- **Municípios**: 50 municípios de SP (ou primeiros 50 disponíveis)
- **Beneficiários**: Entre 8% e 30% da população estimada
- **Valores**: Entre R$ 250 e R$ 450 por beneficiário
- **Total estimado**: ~R$ 50-200 milhões em valores totais

## Próximos Passos

Após gerar os dados (simulados ou reais):

1. **Executar transformação Prata:**
   ```python
   exec(open('/home/jovyan/work/02_prata_transformacao.py').read())
   ```

2. **Testar com gráficos:**
   ```python
   exec(open('/home/jovyan/work/teste_completo_com_graficos.py').read())
   ```

## Verificação

Para verificar se os dados foram gerados:

```python
from pyspark.sql import SparkSession

# Inicializar Spark se necessário
try:
    spark
except NameError:
    exec(open('/home/jovyan/work/spark_com_jars_manual.py').read())
    spark = globals()['spark']

# Verificar dados Bronze
df_bf_bronze = spark.read.parquet("s3a://govbr/bronze/portal_transparencia/bolsa_familia_municipios/")
print(f"✅ Dados Bronze: {df_bf_bronze.count()} registros")
df_bf_bronze.show(5)

# Verificar dados Prata
df_bf_prata = spark.read.parquet("s3a://govbr/prata/fato_bolsa_familia/")
print(f"✅ Dados Prata: {df_bf_prata.count()} registros")
df_bf_prata.show(5)
```

## Nota Importante

⚠️ **Os dados simulados são apenas para demonstração e testes.** 
Para produção, é necessário configurar corretamente a API do Portal da Transparência ou usar outra fonte de dados oficial.
