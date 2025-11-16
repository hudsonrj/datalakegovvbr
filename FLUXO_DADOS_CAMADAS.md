# 🔄 Fluxo de Dados: Como Funciona o Pipeline de Bronze, Prata e Ouro

## 📊 Resultados do Teste - CPF: 033.889.847-60

### ✅ Dados Encontrados:
- **CEIS (Empresas Inidôneas)**: 15 registros
- **CNEP (Empresas Punidas)**: 15 registros
- **Total**: 30 registros

### ⚠️ Não Encontrado:
- Bolsa Família
- Servidores Públicos
- Despesas Públicas
- Convênios
- Contratos

---

## 🏗️ Arquitetura Medallion: Bronze → Prata → Ouro

O pipeline segue a arquitetura **Medallion** (Medalhão), que organiza os dados em três camadas:

```
┌─────────────────────────────────────────────────────────────┐
│                    FONTES EXTERNAS                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │ Portal Trans.│  │    IBGE      │  │  Outras APIs │     │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘     │
│         │                 │                 │              │
│         └─────────────────┴─────────────────┘              │
│                           │                                 │
└───────────────────────────┼─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    🥉 CAMADA BRONZE                          │
│              (Dados Brutos - Raw Data)                       │
│                                                              │
│  • Dados coletados diretamente das APIs                     │
│  • Formato original (JSON/Parquet)                          │
│  • Sem transformações                                       │
│  • Particionado por data (dt=YYYYMMDD)                      │
│  • Localização: bronze/{fonte}/{dataset}/dt={data}/         │
│                                                              │
│  Exemplo:                                                    │
│  bronze/portal_transparencia/ceis/dt=20251116/data.parquet  │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            │ [Transformação]
                            │ • Limpeza
                            │ • Validação
                            │ • Normalização
                            │ • Joins
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    🥈 CAMADA PRATA                           │
│          (Dados Limpos e Relacionados)                      │
│                                                              │
│  • Dados limpos e validados                                 │
│  • Estrutura dimensional (Fato/Dimensão)                    │
│  • Relacionamentos entre tabelas                            │
│  • Enriquecimento com dados geográficos                     │
│  • Localização: prata/{dataset}/dt={data}/                  │
│                                                              │
│  Exemplo:                                                    │
│  prata/fato_ceis/dt=20251116/data.parquet                   │
│  prata/dim_pessoas/dt=20251116/data.parquet                 │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            │ [Enriquecimento]
                            │ • Métricas calculadas
                            │ • Agregações
                            │ • Rankings
                            │ • Análises pré-calculadas
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    🥇 CAMADA OURO                            │
│        (Dados Prontos para Análise)                         │
│                                                              │
│  • Dados enriquecidos com métricas                          │
│  • Agregações por região/estado/município                   │
│  • Rankings e top N                                        │
│  • Análises pré-calculadas                                  │
│  • Prontos para visualização e BI                           │
│  • Localização: ouro/{dataset}/dt={data}/                   │
│                                                              │
│  Exemplo:                                                    │
│  ouro/pessoas_sancionadas_analytics/dt=20251116/           │
│  ouro/rankings_sancionados/dt=20251116/                     │
└─────────────────────────────────────────────────────────────┘
```

---

## 📝 Processo Detalhado: Como os Dados Flutuam

### 1️⃣ **INGESTÃO (Bronze)** - `01_bronze_ingestion.py`

**O que faz:**
- Conecta nas APIs externas (Portal da Transparência, IBGE)
- Coleta dados brutos
- Salva em formato Parquet no MinIO
- Organiza por partição de data

**Exemplo prático:**
```python
# 1. Consulta API
response = requests.get(
    f"{transparency_url}/ceis",
    headers=headers,
    params={'cpfOuCnpj': '03388984760', 'pagina': 1}
)

# 2. Converte para DataFrame
df = pd.DataFrame(response.json())

# 3. Salva na camada Bronze
save_to_bronze(
    df, 
    dataset_name='ceis',
    source='portal_transparencia',
    partition_date='20251116'
)

# 4. Arquivo salvo em:
# bronze/portal_transparencia/ceis/dt=20251116/data.parquet
```

**Características:**
- ✅ Dados brutos (como vieram da API)
- ✅ Sem transformações
- ✅ Histórico completo (uma partição por dia)
- ✅ Permite reprocessamento

---

### 2️⃣ **TRANSFORMAÇÃO (Prata)** - `02_prata_transformacao.py`

**O que faz:**
- Lê dados da camada Bronze
- Limpa e valida dados
- Cria estrutura dimensional (Fato/Dimensão)
- Faz joins entre tabelas
- Enriquece com dados geográficos

**Exemplo prático:**
```python
# 1. Ler dados Bronze
df_ceis_bronze = read_from_bronze('portal_transparencia', 'ceis')

# 2. Limpar e normalizar
df_ceis_limpo = df_ceis_bronze.copy()
df_ceis_limpo['cpf'] = df_ceis_limpo['pessoa']['cpfFormatado'].str.replace('*', '')
df_ceis_limpo['nome'] = df_ceis_limpo['pessoa']['nome']
df_ceis_limpo['tipo_sancao'] = df_ceis_limpo['tipoSancao']['descricaoResumida']

# 3. Criar tabela Fato
fato_ceis = df_ceis_limpo[[
    'id', 'cpf', 'dataInicioSancao', 'dataFimSancao',
    'tipo_sancao', 'orgaoSancionador', 'valor'
]]

# 4. Criar tabela Dimensão
dim_pessoas = df_ceis_limpo[[
    'cpf', 'nome', 'tipo'
]].drop_duplicates()

# 5. Salvar na camada Prata
save_to_prata(fato_ceis, 'fato_ceis')
save_to_prata(dim_pessoas, 'dim_pessoas')
```

**Características:**
- ✅ Dados limpos e validados
- ✅ Estrutura dimensional (Fato/Dimensão)
- ✅ Relacionamentos entre tabelas
- ✅ Pronto para análises

---

### 3️⃣ **ENRIQUECIMENTO (Ouro)** - `03_ouro_enriquecimento.py`

**O que faz:**
- Lê dados da camada Prata
- Calcula métricas e agregações
- Cria rankings e análises
- Gera dados prontos para visualização

**Exemplo prático:**
```python
# 1. Ler dados Prata
fato_ceis = read_from_prata('fato_ceis')
dim_pessoas = read_from_prata('dim_pessoas')

# 2. Join para enriquecer
df_enriquecido = fato_ceis.merge(
    dim_pessoas, 
    on='cpf', 
    how='left'
)

# 3. Calcular métricas
analytics = df_enriquecido.groupby('cpf').agg({
    'id': 'count',
    'dataInicioSancao': 'min',
    'dataFimSancao': 'max'
}).rename(columns={'id': 'total_sancoes'})

# 4. Criar ranking
ranking = analytics.sort_values('total_sancoes', ascending=False).head(100)

# 5. Salvar na camada Ouro
save_to_ouro(analytics, 'pessoas_sancionadas_analytics')
save_to_ouro(ranking, 'ranking_top_sancionados')
```

**Características:**
- ✅ Métricas pré-calculadas
- ✅ Rankings e top N
- ✅ Agregações por região
- ✅ Pronto para BI e visualizações

---

## 🔄 Fluxo Completo: CPF 033.889.847-60

### Passo 1: Coleta (Bronze)
```
API Portal Transparência
    ↓
/ceis?cpfOuCnpj=03388984760
    ↓
15 registros JSON brutos
    ↓
Salvo em: bronze/portal_transparencia/ceis/dt=20251116/data.parquet
```

### Passo 2: Transformação (Prata)
```
Lê: bronze/portal_transparencia/ceis/dt=20251116/data.parquet
    ↓
Limpa e normaliza dados
    ↓
Cria estrutura dimensional:
  - fato_ceis (eventos de sanção)
  - dim_pessoas (informações das pessoas)
    ↓
Salvo em: 
  - prata/fato_ceis/dt=20251116/data.parquet
  - prata/dim_pessoas/dt=20251116/data.parquet
```

### Passo 3: Enriquecimento (Ouro)
```
Lê: prata/fato_ceis e prata/dim_pessoas
    ↓
Calcula métricas:
  - Total de sanções por pessoa
  - Período de sanções
  - Tipos de sanções
    ↓
Cria rankings e análises
    ↓
Salvo em:
  - ouro/pessoas_sancionadas_analytics/dt=20251116/data.parquet
  - ouro/ranking_sancionados/dt=20251116/data.parquet
```

---

## 📂 Estrutura de Arquivos no MinIO

```
govbr/
├── bronze/
│   └── portal_transparencia/
│       ├── ceis/
│       │   └── dt=20251116/
│       │       └── data.parquet  ← Dados brutos
│       └── cnep/
│           └── dt=20251116/
│               └── data.parquet
│
├── prata/
│   ├── fato_ceis/
│   │   └── dt=20251116/
│   │       └── data.parquet  ← Dados limpos
│   ├── dim_pessoas/
│   │   └── dt=20251116/
│   │       └── data.parquet
│   └── fato_cnep/
│       └── dt=20251116/
│           └── data.parquet
│
└── ouro/
    ├── pessoas_sancionadas_analytics/
    │   └── dt=20251116/
    │       └── data.parquet  ← Dados enriquecidos
    └── ranking_sancionados/
        └── dt=20251116/
            └── data.parquet
```

---

## 🚀 Como Executar o Pipeline Completo

### Opção 1: Executar Tudo de Uma Vez
```bash
# No container Jupyter
cd /home/jovyan/work
python3 01_bronze_ingestion.py
python3 02_prata_transformacao.py
python3 03_ouro_enriquecimento.py
```

### Opção 2: Executar Passo a Passo
```bash
# 1. Coletar dados brutos
python3 01_bronze_ingestion.py

# 2. Verificar dados coletados
# (verificar no MinIO ou logs)

# 3. Transformar dados
python3 02_prata_transformacao.py

# 4. Enriquecer dados
python3 03_ouro_enriquecimento.py
```

---

## 💡 Vantagens da Arquitetura Medallion

1. **Reprocessamento**: Pode reprocessar qualquer camada sem perder dados brutos
2. **Histórico**: Mantém histórico completo em cada camada
3. **Qualidade**: Cada camada melhora a qualidade dos dados
4. **Flexibilidade**: Pode criar novas análises a partir de qualquer camada
5. **Rastreabilidade**: Sabe exatamente de onde vieram os dados

---

## 📊 Exemplo Prático: Dados do CPF Testado

### Dados Encontrados (Bronze):
- **CEIS**: 15 sanções encontradas
- **CNEP**: 15 punições encontradas
- **Total**: 30 registros brutos

### Após Transformação (Prata):
- Tabela `fato_ceis` com 15 registros estruturados
- Tabela `fato_cnep` com 15 registros estruturados
- Tabela `dim_pessoas` com informações normalizadas

### Após Enriquecimento (Ouro):
- Métricas: Total de sanções, período ativo, tipos
- Rankings: Posição entre pessoas sancionadas
- Análises: Tendências e padrões

---

## 🔍 Consultar Dados em Cada Camada

### Consultar Bronze (Dados Brutos)
```python
from minio import Minio
import pandas as pd
import io

# Ler dados Bronze
response = minio_client.get_object(
    'govbr',
    'bronze/portal_transparencia/ceis/dt=20251116/data.parquet'
)
df_bronze = pd.read_parquet(io.BytesIO(response.read()))
```

### Consultar Prata (Dados Limpos)
```python
# Ler dados Prata
response = minio_client.get_object(
    'govbr',
    'prata/fato_ceis/dt=20251116/data.parquet'
)
df_prata = pd.read_parquet(io.BytesIO(response.read()))
```

### Consultar Ouro (Dados Enriquecidos)
```python
# Ler dados Ouro
response = minio_client.get_object(
    'govbr',
    'ouro/pessoas_sancionadas_analytics/dt=20251116/data.parquet'
)
df_ouro = pd.read_parquet(io.BytesIO(response.read()))
```

---

## ✅ Conclusão

O pipeline Medallion permite:
- ✅ Coletar dados brutos (Bronze)
- ✅ Limpar e estruturar (Prata)
- ✅ Enriquecer e analisar (Ouro)
- ✅ Manter histórico completo
- ✅ Reprocessar quando necessário

**Resultado**: Dados organizados, limpos e prontos para análise! 🎯
