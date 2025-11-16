# ⚠️ Problema: Spark precisa de Java

## Erro Encontrado

```
PySparkRuntimeError: [JAVA_GATEWAY_EXITED] Java gateway process exited before sending its port number.
```

## Causa

O Spark precisa de **Java** para funcionar, mas o container não tinha Java instalado.

## ✅ Soluções Disponíveis

### Opção 1: Usar DuckDB (RECOMENDADO - Mais Simples!)

**Vantagens:**
- ✅ Não precisa de Java
- ✅ Não precisa de Spark
- ✅ Mais rápido para consultas
- ✅ Mais fácil de usar
- ✅ Funciona direto com Parquet

**Como usar:**
1. Abra o notebook: `delta_lake_queries_duckdb.ipynb`
2. Execute as células
3. Pronto! Consultas SQL funcionando!

### Opção 2: Instalar Java no Container (Para usar Spark/Delta Lake)

**Passos:**

1. **Reconstruir o container com Java:**
```bash
docker compose -f docker-compose-simple.yml down
docker compose -f docker-compose-simple.yml up -d
```

2. **Ou instalar Java manualmente no container atual:**
```bash
docker exec -it govbr-jupyter-delta bash
sudo apt-get update
sudo apt-get install -y openjdk-17-jdk-headless
export JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
```

3. **Verificar se Java está instalado:**
```bash
docker exec govbr-jupyter-delta java -version
```

## 📊 Comparação

| Recurso | Spark/Delta Lake | DuckDB |
|---------|-----------------|--------|
| Precisa Java? | ✅ Sim | ❌ Não |
| Complexidade | 🔴 Alta | 🟢 Baixa |
| Velocidade | 🟡 Média | 🟢 Alta |
| Consultas SQL | ✅ Sim | ✅ Sim |
| Joins | ✅ Sim | ✅ Sim |
| Funciona agora? | ⚠️ Precisa Java | ✅ Sim! |

## 🎯 Recomendação

**Use DuckDB!** É muito mais simples e faz tudo que você precisa:
- ✅ Ler Parquet do MinIO
- ✅ Consultas SQL completas
- ✅ Joins entre tabelas
- ✅ Agregações
- ✅ Sem necessidade de Java/Spark

## 📝 Notebooks Disponíveis

1. **`delta_lake_queries_duckdb.ipynb`** ✅ **USE ESTE!** (Funciona sem Java)
2. **`delta_lake_queries.ipynb`** (Precisa Java/Spark)

## ✅ Próximos Passos

1. Abra o Jupyter Lab: http://localhost:8889
2. Abra o notebook: `delta_lake_queries_duckdb.ipynb`
3. Execute as células
4. Pronto! Consultas SQL funcionando!
