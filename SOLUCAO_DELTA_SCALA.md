# 🔧 Solução: Erro scala.collection.SeqOps no Delta Lake

## ❌ Problema

Erro ao usar Delta Lake com Spark:
```
java.lang.NoClassDefFoundError: scala/collection/SeqOps
```

## 🔍 Causa

Incompatibilidade entre versões do Delta Lake e Spark. O erro ocorre porque:
- Spark 4.0.1 está instalado
- Delta Lake 4.0.0 pode ter incompatibilidade de versão do Scala
- Os JARs do Delta Lake não estão sendo carregados corretamente

## ✅ Solução

O script `configurar_spark.py` e o notebook `CONFIGURAR_SPARK.ipynb` foram atualizados para:

1. **Detectar automaticamente a versão do Spark**
2. **Usar os JARs corretos do Delta Lake** compatíveis com cada versão:
   - Spark 4.x → Delta Lake 4.0.0 (Scala 2.13)
   - Spark 3.5.x → Delta Lake 3.0.0 (Scala 2.12)
   - Spark 3.x → Delta Lake 2.4.0 (Scala 2.12)

3. **Carregar os JARs explicitamente** via `spark.jars.packages`

## 🚀 Como Usar

### Opção 1: Usar o Notebook Atualizado

1. Abra o Jupyter Lab: http://localhost:8889/lab
2. Abra: `CONFIGURAR_SPARK.ipynb`
3. Execute todas as células na ordem

### Opção 2: Usar o Script Python

```python
exec(open('configurar_spark.py').read())
```

## 📋 Versões Compatíveis

| Spark | Delta Lake | Scala | Pacote JAR |
|-------|-----------|-------|------------|
| 4.0.x | 4.0.0 | 2.13 | `io.delta:delta-spark_2.13:4.0.0` |
| 3.5.x | 3.0.0 | 2.12 | `io.delta:delta-spark_2.12:3.0.0` |
| 3.x   | 2.4.0 | 2.12 | `io.delta:delta-spark_2.12:2.4.0` |

## 🔄 Fallback

Se o Delta Lake não funcionar, o script cria uma Spark Session sem Delta (modo fallback) que permite usar Parquet normalmente.

## ✅ Verificação

Após executar, teste:

```python
# Verificar Spark
print(f"Versão Spark: {spark.version}")

# Teste básico
test_df = spark.range(5)
test_df.show()
```

Se funcionar sem erros, está tudo correto!
