# 📊 Pipeline de Ingestão de Dados - GovBR

## 📁 Arquivos Disponíveis na Pasta de Trabalho do Jupyter

Todos os arquivos foram copiados para `/home/jovyan/work/` no container Jupyter:

### Notebooks de Visualização
- ✅ `EXEMPLO_01_BRONZE.ipynb` - Visualização de dados Bronze
- ✅ `EXEMPLO_02_PRATA.ipynb` - Visualização de dados Prata
- ✅ `EXEMPLO_03_OURO.ipynb` - Visualização de dados Ouro
- ✅ `DEMO_APRESENTACAO.ipynb` - Demonstração completa

### Notebooks de Configuração
- ✅ `CONFIGURAR_SPARK.ipynb` - Configuração do Spark (execute primeiro!)
- ✅ `FIX_PY4J_ERROR.ipynb` - Correção de erros Py4J

### Scripts Python
- ✅ `01_bronze_ingestion.py` - Script de ingestão Bronze
- ✅ `02_prata_transformacao.py` - Script de transformação Prata
- ✅ `03_ouro_enriquecimento.py` - Script de enriquecimento Ouro
- ✅ `pipeline_ingestao.py` - **Pipeline completo com modo FULL e INCREMENTAL**

## 🚀 Como Usar o Pipeline de Ingestão

### Modo FULL (Recarrega Tudo)
```bash
# No terminal do container ou notebook
python pipeline_ingestao.py --mode full
```

### Modo INCREMENTAL (Apenas Novos Dados)
```bash
python pipeline_ingestao.py --mode incremental
```

### Modo AUTO (Decide Automaticamente)
```bash
python pipeline_ingestao.py --mode auto
# ou simplesmente:
python pipeline_ingestao.py
```

## 📝 Modos de Execução

### 1. FULL Mode
- **Quando usar**: Primeira execução, recarregamento completo, correção de dados
- **Comportamento**: 
  - Recarrega todos os dados das APIs
  - Substitui dados existentes
  - Garante dados atualizados

### 2. INCREMENTAL Mode
- **Quando usar**: Execuções diárias/semanais, atualizações regulares
- **Comportamento**:
  - Verifica última partição existente
  - Coleta apenas dados novos (último mês)
  - Faz merge com dados existentes
  - Remove duplicatas automaticamente

### 3. AUTO Mode (Padrão)
- **Quando usar**: Execução agendada, automação
- **Comportamento**:
  - Verifica se existe dados anteriores
  - Se não existe → executa FULL
  - Se existe e última partição > 1 dia → executa INCREMENTAL
  - Se última partição < 1 dia → pula execução

## 📊 Estrutura de Dados

### Camada Bronze
```
bronze/
├── ibge/
│   ├── municipios/dt=YYYYMMDD/data.parquet
│   ├── estados/dt=YYYYMMDD/data.parquet
│   └── populacao_estados/dt=YYYYMMDD/data.parquet
└── portal_transparencia/
    ├── bpc_municipios/dt=YYYYMMDD/data.parquet
    └── orgaos_siafi/dt=YYYYMMDD/data.parquet
```

## 🔄 Fluxo de Execução

1. **Bronze** → `pipeline_ingestao.py` ou `01_bronze_ingestion.py`
2. **Prata** → `02_prata_transformacao.py`
3. **Ouro** → `03_ouro_enriquecimento.py`

## 💡 Exemplos de Uso

### No Jupyter Notebook
```python
# Executar pipeline completo em modo incremental
!python pipeline_ingestao.py --mode incremental

# Executar apenas Bronze
exec(open('01_bronze_ingestion.py').read())

# Executar Prata
exec(open('02_prata_transformacao.py').read())

# Executar Ouro
exec(open('03_ouro_enriquecimento.py').read())
```

### No Terminal do Container
```bash
# Acessar container
docker exec -it govbr-jupyter-delta bash

# Executar pipeline
cd /home/jovyan/work
python pipeline_ingestao.py --mode incremental
```

## ⚙️ Configuração

O pipeline usa as seguintes configurações (definidas no script):
- **MinIO**: `ch8ai-minio.l6zv5a.easypanel.host`
- **Bucket**: `govbr`
- **APIs**: IBGE e Portal da Transparência

## 📈 Monitoramento

O pipeline exibe:
- ✅ Status de cada etapa
- 📊 Quantidade de registros coletados
- 💾 Tamanho dos arquivos gerados
- 📁 Resumo final com todos os datasets

## 🔍 Verificação

Para verificar dados coletados:
```python
from minio import Minio

minio_client = Minio(
    "ch8ai-minio.l6zv5a.easypanel.host",
    access_key="admin",
    secret_key="1q2w3e4r",
    secure=True
)

# Listar arquivos Bronze
objects = minio_client.list_objects("govbr", prefix="bronze/", recursive=True)
for obj in objects:
    print(f"{obj.object_name} ({obj.size/1024:.2f} KB)")
```
