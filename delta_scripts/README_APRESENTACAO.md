# 🎯 GovBR Data Lake - Guia de Apresentação

## 📋 Visão Geral

Solução completa de Data Lake usando Arquitetura Medallion (Bronze, Prata, Ouro) com:
- **Apache Spark 4.0.1** para processamento distribuído
- **Delta Lake** para ACID transactions e versionamento
- **MinIO** para armazenamento S3-compatible
- **Python/PySpark** para desenvolvimento

## 🚀 Início Rápido

### 1. Configurar Spark

**Opção A: Notebook (Recomendado)**
```python
# Abrir: CONFIGURAR_SPARK.ipynb
# Executar todas as células
```

**Opção B: Script Python**
```python
exec(open('configurar_spark.py').read())
```

### 2. Explorar as Camadas

#### 🥉 Camada Bronze
- **Notebook**: `EXEMPLO_01_BRONZE.ipynb`
- **Dados**: Brutos das APIs (IBGE, Portal da Transparência)
- **Formato**: Parquet particionado por data

#### 🔄 Camada Prata
- **Notebook**: `EXEMPLO_02_PRATA.ipynb`
- **Dados**: Transformados e relacionados
- **Estrutura**: Dimensões e Fatos

#### 🏆 Camada Ouro
- **Notebook**: `EXEMPLO_03_OURO.ipynb`
- **Dados**: Enriquecidos com métricas
- **Uso**: Pronto para dashboards

### 3. Demonstração Completa

**Notebook**: `DEMO_APRESENTACAO.ipynb`
- Visão geral das três camadas
- Análises demonstrativas
- Resumo da arquitetura

## 📁 Estrutura de Arquivos

### Notebooks Principais (Execute nesta ordem)

```
delta_scripts/
├── CONFIGURAR_SPARK.ipynb      # ⭐ 1. Configuração Spark (EXECUTE PRIMEIRO!)
├── FIX_PY4J_ERROR.ipynb        # 🔧 Correção de erros Py4J (se necessário)
├── DEMO_APRESENTACAO.ipynb     # 🎯 2. Demo completo (visão geral)
├── EXEMPLO_01_BRONZE.ipynb     # 📊 3. Exemplo Bronze (visualização)
├── EXEMPLO_02_PRATA.ipynb      # 🔄 4. Exemplo Prata (visualização)
└── EXEMPLO_03_OURO.ipynb       # 🏆 5. Exemplo Ouro (visualização)
```

### Scripts Python

```
delta_scripts/
├── configurar_spark.py         # Script de configuração Spark
├── fix_spark_py4j.py           # Script de correção Py4J
├── 01_bronze_ingestion.py     # Ingestão Bronze
├── 02_prata_transformacao.py  # Transformação Prata
├── 03_ouro_enriquecimento.py  # Enriquecimento Ouro
└── pipeline_ingestao.py        # Pipeline completo
```

### Documentação

```
delta_scripts/
├── README_APRESENTACAO.md     # Este arquivo
├── README_PIPELINE.md         # Documentação do pipeline
├── GUIA_SPARK.md              # Guia rápido Spark
└── GUIA_CORRECAO_PY4J.md     # Guia correção Py4J
```

## 🔧 Scripts de Pipeline

- `01_bronze_ingestion.py` - Ingestão de dados brutos
- `02_prata_transformacao.py` - Transformação e relacionamento
- `03_ouro_enriquecimento.py` - Enriquecimento com métricas

## 📊 Dados Disponíveis

### Camada Bronze
- Municípios (IBGE)
- Estados (IBGE)
- População por Estado (IBGE)
- Órgãos SIAFI (Portal da Transparência)
- BPC por Município (Portal da Transparência)

### Camada Prata
- Dimensão: Municípios
- Dimensão: Estados
- Dimensão: Órgãos
- Fato: BPC
- Fato: População

### Camada Ouro
- Municípios Enriquecidos
- Estados Enriquecidos
- BPC Analytics
- Rankings
- Agregações Regionais

## 🎯 Pontos para Apresentação

### 1. Arquitetura
- ✅ Medallion Architecture (Bronze → Prata → Ouro)
- ✅ Processamento distribuído com Spark
- ✅ Armazenamento escalável com MinIO

### 2. Tecnologias
- ✅ Apache Spark 4.0.1
- ✅ Delta Lake (via JARs compatíveis)
- ✅ MinIO (S3-compatible)
- ✅ Python/PySpark

### 3. Benefícios
- ✅ Escalabilidade
- ✅ Flexibilidade
- ✅ Versionamento de dados
- ✅ Processamento distribuído

### 4. Casos de Uso
- ✅ Análise de dados governamentais
- ✅ Dashboards e relatórios
- ✅ ETL distribuído
- ✅ Data Lake moderno

## 📝 Ordem de Execução para Demo

### Passo 1: Configurar Spark (OBRIGATÓRIO)
```python
# Execute o notebook: CONFIGURAR_SPARK.ipynb
# Ou execute o script:
exec(open('/home/jovyan/work/fix_spark_py4j.py').read())
```

### Passo 2: Executar Notebooks de Visualização
1. **DEMO_APRESENTACAO.ipynb** - Visão geral completa (recomendado primeiro)
2. **EXEMPLO_01_BRONZE.ipynb** - Detalhes Bronze
3. **EXEMPLO_02_PRATA.ipynb** - Detalhes Prata
4. **EXEMPLO_03_OURO.ipynb** - Detalhes Ouro

### ⚠️ IMPORTANTE
- **SEMPRE execute CONFIGURAR_SPARK.ipynb primeiro**
- Os notebooks EXEMPLO_* verificam se Spark está configurado
- Se Spark não estiver configurado, eles tentam configurar automaticamente

## 🔍 Consultas de Exemplo

### Bronze
```python
df = spark.read.parquet("s3a://govbr/bronze/ibge/municipios/")
df.show()
```

### Prata
```python
df = spark.read.parquet("s3a://govbr/prata/dim_municipio/")
df.show()
```

### Ouro
```python
df = spark.read.parquet("s3a://govbr/ouro/municipios_enriquecidos/")
df.show()
```

## ✅ Checklist para Apresentação

- [ ] Spark configurado e funcionando
- [ ] Dados Bronze disponíveis
- [ ] Dados Prata disponíveis
- [ ] Dados Ouro disponíveis
- [ ] Notebooks de exemplo funcionando
- [ ] Demo completo executado

## 📚 Documentação Adicional

- `GUIA_SPARK.md` - Guia rápido de configuração
- `README_PIPELINE.md` - Documentação do pipeline
- Web UI: http://localhost:8080 - Dashboard principal

## 🆘 Troubleshooting

### Spark não inicia
- Execute `CONFIGURAR_SPARK.ipynb`
- Verifique JAVA_HOME
- Verifique logs: `docker logs govbr-jupyter-delta`

### Dados não aparecem
- Execute scripts de ingestão (`01_bronze_ingestion.py`)
- Verifique MinIO: http://localhost:9000
- Verifique paths S3A

### Erros de conexão
- Verifique rede entre containers
- Verifique variáveis de ambiente
- Reinicie containers se necessário
