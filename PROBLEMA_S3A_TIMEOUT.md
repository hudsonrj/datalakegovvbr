# ⚠️ Problema com S3A FileSystem - Timeout "24h"

## Status Atual

O erro `ClassNotFoundException: Class org.apache.hadoop.fs.s3a.S3AFileSystem not found` foi **RESOLVIDO** ✅, mas agora temos um novo problema:

```
java.lang.NumberFormatException: For input string: "24h"
```

## Causa

O Hadoop S3A está tentando fazer parse de uma propriedade de configuração que tem o valor "24h" (24 horas) como um número Long, mas o parser não suporta o formato "24h".

## Tentativas de Solução

1. ✅ Download manual dos JARs do S3A
2. ✅ Configuração de todas as propriedades de timeout em milissegundos
3. ✅ Configuração de keepalive e threads
4. ✅ Desabilitação do cache de metadados
5. ❌ Arquivo `core-site.xml` customizado (não resolveu)

## Solução Alternativa Recomendada

Como o problema persiste mesmo com todas as configurações, recomendo usar **DuckDB** que já está funcionando e é mais simples:

### Usar DuckDB (Já Funcionando)

O notebook `notebooks/delta_lake_queries_duckdb.ipynb` já está configurado e funcionando. DuckDB pode ler arquivos Parquet diretamente do MinIO usando s3fs.

### Vantagens do DuckDB

- ✅ Mais simples de configurar
- ✅ Não precisa de JARs do Hadoop
- ✅ Leitura direta de Parquet do MinIO
- ✅ SQL completo e performático
- ✅ Já está funcionando no projeto

## Próximos Passos

1. **Usar DuckDB** para consultas SQL nos dados Parquet
2. **Ou** tentar uma versão diferente do `hadoop-aws` (mais antiga ou mais nova)
3. **Ou** usar `s3fs` diretamente com Pandas/Polars em vez de Spark

## Script DuckDB Funcional

O script `notebooks/delta_lake_queries_duckdb.ipynb` já está pronto para uso!
