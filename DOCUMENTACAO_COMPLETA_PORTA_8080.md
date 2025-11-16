# 📚 Documentação Completa - Aplicação Porta 8080
## GovBR Data Lake - Plataforma de Dados Governamentais

---

## 📋 Índice

1. [Visão Geral](#visão-geral)
2. [Arquitetura do Sistema](#arquitetura-do-sistema)
3. [Diagrama Completo](#diagrama-completo)
4. [Componentes da Arquitetura](#componentes-da-arquitetura)
5. [Passo a Passo de Instalação](#passo-a-passo-de-instalação)
6. [Ingestão de Dados](#ingestão-de-dados)
7. [Catálogo de Dados](#catálogo-de-dados)
8. [Fluxo Completo de Dados](#fluxo-completo-de-dados)
9. [Como Usar](#como-usar)
10. [Troubleshooting](#troubleshooting)

---

## 🎯 Visão Geral

A aplicação na **porta 8080** é uma **Dashboard Web** que serve como ponto central de acesso ao **GovBR Data Lake**, uma plataforma completa de ingestão, transformação e análise de dados governamentais brasileiros.

### O que é o GovBR Data Lake?

Um **Data Lake** estruturado em três camadas (Bronze, Prata, Ouro) que:
- **Ingere** dados de APIs governamentais (IBGE, Portal da Transparência)
- **Armazena** dados em formato Parquet no MinIO (S3-compatible)
- **Transforma** dados brutos em estruturas analíticas
- **Enriquece** dados com métricas e análises prontas para consumo
- **Disponibiliza** dados através de Spark e Delta Lake para consultas SQL

### Tecnologias Utilizadas

- **MinIO**: Armazenamento de objetos (S3-compatible)
- **Apache Spark**: Processamento distribuído de dados
- **Delta Lake**: Camada de transações ACID sobre dados Parquet
- **Jupyter Lab**: Ambiente interativo para análise
- **Nginx**: Servidor web para dashboard (porta 8080)
- **Docker**: Containerização de serviços

---

## 🏗️ Arquitetura do Sistema

### Estrutura de Camadas (Medallion Architecture)

```
┌─────────────────────────────────────────────────────────────┐
│                    CAMADA OURO (Gold)                       │
│  Dados Enriquecidos e Prontos para Análise                  │
│  - Métricas calculadas                                       │
│  - Agregações por região/estado                             │
│  - Tabelas analíticas                                       │
└─────────────────────────────────────────────────────────────┘
                            ▲
                            │
┌─────────────────────────────────────────────────────────────┐
│                    CAMADA PRATA (Silver)                     │
│  Dados Tratados e Relacionados                              │
│  - Limpeza e normalização                                    │
│  - Relacionamentos entre tabelas                            │
│  - Dimensões e fatos estruturados                          │
└─────────────────────────────────────────────────────────────┘
                            ▲
                            │
┌─────────────────────────────────────────────────────────────┐
│                    CAMADA BRONZE (Raw)                      │
│  Dados Brutos das APIs                                      │
│  - Dados exatamente como recebidos                          │
│  - Sem transformações                                        │
│  - Particionados por data                                   │
└─────────────────────────────────────────────────────────────┘
                            ▲
                            │
┌─────────────────────────────────────────────────────────────┐
│                    FONTES DE DADOS                          │
│  - IBGE API                                                  │
│  - Portal da Transparência API                              │
└─────────────────────────────────────────────────────────────┘
```

---

## 📊 Diagrama Completo

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                         USUÁRIO / ANALISTA                                    │
└──────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
                    ┌───────────────────────────────┐
                    │   PORTA 8080 - Dashboard Web  │
                    │   (Nginx + HTML/CSS/JS)       │
                    │   http://localhost:8080       │
                    └───────────────────────────────┘
                                    │
                    ┌───────────────┼───────────────┐
                    │               │               │
                    ▼               ▼               ▼
        ┌─────────────────┐ ┌──────────────┐ ┌──────────────┐
        │  Jupyter Lab    │ │   MinIO UI    │ │  Documentação│
        │  Porta 8889     │ │  (Externo)   │ │              │
        └─────────────────┘ └──────────────┘ └──────────────┘
                    │
                    ▼
        ┌─────────────────────────────────────┐
        │     JUPYTER LAB CONTAINER            │
        │  (govbr-jupyter-delta)               │
        │  - Python 3.x                        │
        │  - PySpark                           │
        │  - Delta Spark                       │
        │  - Pandas                            │
        │  - MinIO Client                      │
        └─────────────────────────────────────┘
                    │
                    ▼
        ┌─────────────────────────────────────┐
        │     PIPELINE DE INGESTÃO             │
        │  pipeline_ingestao.py                 │
        │  - Modo FULL / INCREMENTAL / AUTO    │
        └─────────────────────────────────────┘
                    │
        ┌───────────┼───────────┐
        │           │           │
        ▼           ▼           ▼
┌─────────────┐ ┌─────────────┐ ┌─────────────┐
│  01_BRONZE  │ │  02_PRATA   │ │  03_OURO    │
│  Ingestion  │ │ Transform   │ │ Enrichment  │
└─────────────┘ └─────────────┘ └─────────────┘
        │           │           │
        └───────────┼───────────┘
                    │
                    ▼
        ┌─────────────────────────────────────┐
        │         MINIO STORAGE                │
        │  (S3-Compatible Object Storage)     │
        │  Bucket: govbr                       │
        │  Endpoint: ch8ai-minio...easypanel   │
        │                                      │
        │  Estrutura:                          │
        │  govbr/                              │
        │  ├── bronze/                        │
        │  │   ├── ibge/                      │
        │  │   │   ├── municipios/            │
        │  │   │   │   └── dt=YYYYMMDD/       │
        │  │   │   │       └── data.parquet   │
        │  │   │   ├── estados/               │
        │  │   │   └── populacao_estados/     │
        │  │   └── portal_transparencia/      │
        │  │       ├── bpc_municipios/        │
        │  │       └── orgaos_siafi/          │
        │  ├── prata/                         │
        │  │   ├── dim_municipios/            │
        │  │   ├── dim_estados/               │
        │  │   ├── fato_bpc/                  │
        │  │   └── dim_orgaos/                │
        │  └── ouro/                          │
        │      ├── dim_municipios_enriquecida/ │
        │      ├── dim_estados_enriquecida/    │
        │      ├── fato_bpc_enriquecido/       │
        │      ├── agregacao_bpc_por_regiao/   │
        │      └── agregacao_bpc_por_estado/   │
        └─────────────────────────────────────┘
                    │
                    ▼
        ┌─────────────────────────────────────┐
        │      APACHE SPARK + DELTA LAKE       │
        │  (Opcional - para consultas SQL)     │
        │  - Leitura de Parquet                │
        │  - Transformações Spark SQL          │
        │  - Delta Lake para ACID             │
        └─────────────────────────────────────┘
                    │
                    ▼
        ┌─────────────────────────────────────┐
        │      FONTES DE DADOS EXTERNAS       │
        │                                      │
        │  1. IBGE API                         │
        │     https://servicodados.ibge.gov.br│
        │     - Municípios                     │
        │     - Estados                        │
        │     - População                      │
        │                                      │
        │  2. Portal da Transparência          │
        │     http://api.portaldatransparencia │
        │     - BPC por Município              │
        │     - Órgãos SIAFI                   │
        └─────────────────────────────────────┘
```

---

## 🔧 Componentes da Arquitetura

### 1. Dashboard Web (Porta 8080)

**Tecnologia**: Nginx + HTML/CSS/JS estático

**Localização**: `./web-ui/index.html`

**Função**: Interface web que serve como ponto central de acesso, fornecendo:
- Links diretos para Jupyter Lab (porta 8889)
- Links para MinIO Storage
- Status dos serviços
- Informações sobre as camadas de dados
- Interface visual moderna e responsiva

**Configuração Docker**:
```yaml
web-ui:
  image: nginx:alpine
  container_name: govbr-web-ui
  ports:
    - "8080:80"
  volumes:
    - ./web-ui:/usr/share/nginx/html:ro
```

### 2. MinIO (Object Storage)

**Tecnologia**: MinIO (S3-compatible)

**Endpoint**: `https://ch8ai-minio.l6zv5a.easypanel.host`

**Credenciais**:
- Access Key: `admin`
- Secret Key: `1q2w3e4r`
- Bucket: `govbr`

**Função**: Armazenamento de objetos onde são salvos todos os dados nas três camadas (Bronze, Prata, Ouro) em formato Parquet.

**Estrutura de Pastas**:
```
govbr/
├── bronze/              # Dados brutos das APIs
│   ├── ibge/
│   │   ├── municipios/dt=YYYYMMDD/data.parquet
│   │   ├── estados/dt=YYYYMMDD/data.parquet
│   │   └── populacao_estados/dt=YYYYMMDD/data.parquet
│   └── portal_transparencia/
│       ├── bpc_municipios/dt=YYYYMMDD/data.parquet
│       └── orgaos_siafi/dt=YYYYMMDD/data.parquet
├── prata/               # Dados tratados e relacionados
│   ├── dim_municipios/dt=YYYYMMDD/data.parquet
│   ├── dim_estados/dt=YYYYMMDD/data.parquet
│   ├── fato_bpc/dt=YYYYMMDD/data.parquet
│   └── dim_orgaos/dt=YYYYMMDD/data.parquet
└── ouro/                # Dados enriquecidos e analíticos
    ├── dim_municipios_enriquecida/dt=YYYYMMDD/data.parquet
    ├── dim_estados_enriquecida/dt=YYYYMMDD/data.parquet
    ├── fato_bpc_enriquecido/dt=YYYYMMDD/data.parquet
    ├── agregacao_bpc_por_regiao/dt=YYYYMMDD/data.parquet
    └── agregacao_bpc_por_estado/dt=YYYYMMDD/data.parquet
```

### 3. Apache Spark

**Tecnologia**: Apache Spark com PySpark

**Função**: 
- Processamento distribuído de grandes volumes de dados
- Leitura de arquivos Parquet do MinIO
- Transformações e agregações complexas
- Suporte a Spark SQL para consultas

**Configuração**:
- Usa `S3A` filesystem para acessar MinIO
- Configurado com extensões Delta Lake
- Suporta leitura de dados como banco relacional

### 4. Delta Lake

**Tecnologia**: Delta Lake (camada sobre Parquet)

**Função**:
- Transações ACID sobre dados Parquet
- Versionamento de dados
- Time travel (acesso a versões anteriores)
- Schema evolution
- Otimizações de leitura/escrita

**Configuração Spark**:
```python
spark.sql.extensions=io.delta.sql.DeltaSparkSessionExtension
spark.sql.catalog.spark_catalog=org.apache.spark.sql.delta.catalog.DeltaCatalog
```

### 5. Jupyter Lab

**Tecnologia**: Jupyter Lab com kernel Python

**Porta**: 8889

**Função**: Ambiente interativo para:
- Executar notebooks de ingestão
- Analisar dados
- Executar consultas SQL
- Desenvolver e testar transformações
- Visualizar dados

**Pacotes Instalados**:
- `pyspark`
- `delta-spark`
- `pandas`
- `minio`
- `s3fs`
- `boto3`

---

## 📥 Ingestão de Dados

### De Onde Vêm os Dados?

#### 1. IBGE (Instituto Brasileiro de Geografia e Estatística)

**API Base**: `https://servicodados.ibge.gov.br/api/v1`

**Endpoints Utilizados**:

##### a) Municípios
- **URL**: `/localidades/municipios`
- **Método**: GET
- **Autenticação**: Não requerida
- **Dados Coletados**:
  - Código IBGE do município
  - Nome do município
  - UF (sigla e nome)
  - Região (ID e nome)
  - Microrregião (ID e nome)
  - Mesorregião (ID e nome)
- **Formato Resposta**: JSON array
- **Exemplo**:
```json
{
  "id": 3550308,
  "nome": "São Paulo",
  "microrregiao": {
    "id": 35061,
    "nome": "São Paulo",
    "mesorregiao": {
      "id": 3515,
      "nome": "Metropolitana de São Paulo",
      "UF": {
        "id": 35,
        "sigla": "SP",
        "nome": "São Paulo",
        "regiao": {
          "id": 3,
          "sigla": "SE",
          "nome": "Sudeste"
        }
      }
    }
  }
}
```

##### b) Estados
- **URL**: `/localidades/estados`
- **Método**: GET
- **Autenticação**: Não requerida
- **Dados Coletados**:
  - ID do estado
  - Sigla da UF
  - Nome do estado
  - Região (ID, sigla e nome)
- **Formato Resposta**: JSON array
- **Exemplo**:
```json
{
  "id": 35,
  "sigla": "SP",
  "nome": "São Paulo",
  "regiao": {
    "id": 3,
    "sigla": "SE",
    "nome": "Sudeste"
  }
}
```

##### c) População por Estado
- **URL**: `/projecoes/populacao/{uf_id}`
- **Método**: GET
- **Autenticação**: Não requerida
- **Dados Coletados**:
  - UF ID
  - UF Sigla
  - Ano
  - População estimada
- **Formato Resposta**: JSON object
- **Exemplo**:
```json
{
  "projecao": {
    "populacao": 46649132
  }
}
```

#### 2. Portal da Transparência

**API Base**: `http://api.portaldatransparencia.gov.br/api-de-dados`

**Autenticação**: Requer chave API no header
```python
headers = {
    'chave-api-dados': '2c56919ba91b8c1b13473dcef43fb031'
}
```

**Endpoints Utilizados**:

##### a) BPC por Município
- **URL**: `/bpc-por-municipio`
- **Método**: GET
- **Parâmetros**:
  - `mesAno`: Formato YYYYMM (ex: 202412)
  - `codigoIbge`: Código IBGE do município
  - `pagina`: Número da página (padrão: 1)
- **Dados Coletados**:
  - ID do registro
  - Data de referência
  - Município (código IBGE, nome, UF, região)
  - Tipo de benefício (ID, descrição, descrição detalhada)
  - Valor total
  - Quantidade de beneficiados
- **Formato Resposta**: JSON array
- **Exemplo**:
```json
{
  "id": 531632761,
  "dataReferencia": "2024-12-01",
  "municipio": {
    "codigoIBGE": "3550308",
    "nomeIBGE": "SÃO PAULO",
    "uf": {
      "sigla": "SP",
      "nome": "SÃO PAULO"
    },
    "nomeRegiao": "Sudeste"
  },
  "tipo": {
    "id": 5,
    "descricao": "BPC",
    "descricaoDetalhada": "Benefício de Prestação Continuada"
  },
  "valor": 396085837.81,
  "quantidadeBeneficiados": 257350
}
```

##### b) Órgãos SIAFI
- **URL**: `/orgaos-siafi`
- **Método**: GET
- **Parâmetros**: Nenhum
- **Dados Coletados**:
  - Código do órgão
  - Descrição do órgão
- **Formato Resposta**: JSON array
- **Exemplo**:
```json
{
  "codigo": "01001",
  "descricao": "PRESIDENCIA DA REPUBLICA"
}
```

### Como Funciona a Ingestão?

#### Pipeline de Ingestão (`pipeline_ingestao.py`)

O pipeline executa em **3 modos**:

##### 1. Modo FULL
- **Quando usar**: Primeira execução, recarregamento completo, correção de dados
- **Comportamento**:
  - Recarrega **todos** os dados das APIs
  - Substitui dados existentes
  - Garante dados atualizados
- **Comando**:
```bash
python pipeline_ingestao.py --mode full
```

##### 2. Modo INCREMENTAL
- **Quando usar**: Execuções diárias/semanais, atualizações regulares
- **Comportamento**:
  - Verifica última partição existente
  - Coleta apenas dados novos (último mês)
  - Faz merge com dados existentes
  - Remove duplicatas automaticamente
- **Comando**:
```bash
python pipeline_ingestao.py --mode incremental
```

##### 3. Modo AUTO (Padrão)
- **Quando usar**: Execução agendada, automação
- **Comportamento**:
  - Verifica se existe dados anteriores
  - Se não existe → executa FULL
  - Se existe e última partição > 1 dia → executa INCREMENTAL
  - Se última partição < 1 dia → pula execução
- **Comando**:
```bash
python pipeline_ingestao.py --mode auto
# ou simplesmente:
python pipeline_ingestao.py
```

#### Fluxo de Execução da Ingestão

```
1. INICIALIZAÇÃO
   ├── Conectar ao MinIO
   ├── Verificar/criar bucket "govbr"
   └── Determinar modo de execução (FULL/INCREMENTAL/AUTO)

2. INGESTÃO BRONZE - IBGE Municípios
   ├── GET /localidades/municipios
   ├── Transformar JSON em DataFrame
   ├── Normalizar estrutura hierárquica
   └── Salvar em: bronze/ibge/municipios/dt=YYYYMMDD/data.parquet

3. INGESTÃO BRONZE - IBGE Estados
   ├── GET /localidades/estados
   ├── Transformar JSON em DataFrame
   └── Salvar em: bronze/ibge/estados/dt=YYYYMMDD/data.parquet

4. INGESTÃO BRONZE - Portal Transparência - Órgãos SIAFI
   ├── GET /orgaos-siafi (com header de autenticação)
   ├── Filtrar códigos inválidos
   └── Salvar em: bronze/portal_transparencia/orgaos_siafi/dt=YYYYMMDD/data.parquet

5. INGESTÃO BRONZE - Portal Transparência - BPC
   ├── Para cada município (amostra):
   │   ├── GET /bpc-por-municipio?mesAno=YYYYMM&codigoIbge=XXXXX
   │   └── Coletar dados do mês atual (INCREMENTAL) ou últimos 3 meses (FULL)
   ├── Transformar JSON em DataFrame
   └── Salvar em: bronze/portal_transparencia/bpc_municipios/dt=YYYYMMDD/data.parquet

6. INGESTÃO BRONZE - IBGE População
   ├── Para cada estado:
   │   └── GET /projecoes/populacao/{uf_id}
   ├── Transformar JSON em DataFrame
   └── Salvar em: bronze/ibge/populacao_estados/dt=YYYYMMDD/data.parquet

7. RESUMO
   ├── Listar arquivos criados
   ├── Calcular tamanhos
   └── Exibir estatísticas
```

### Formato dos Dados

Todos os dados são salvos em formato **Parquet** com:
- **Compressão**: Snappy
- **Particionamento**: Por data (`dt=YYYYMMDD`)
- **Encoding**: UTF-8
- **Schema**: Preservado do DataFrame Pandas

**Vantagens do Parquet**:
- Formato colunar (otimizado para análise)
- Compressão eficiente
- Schema embutido
- Compatível com Spark, Pandas, DuckDB, etc.

---

## 📚 Catálogo de Dados

### Camada BRONZE (Dados Brutos)

#### 1. `bronze/ibge/municipios/`
**Descrição**: Lista completa de municípios brasileiros

**Schema**:
```python
{
    'codigo_ibge': str,           # Código IBGE do município
    'municipio': str,              # Nome do município
    'uf_sigla': str,               # Sigla da UF (ex: SP, RJ)
    'uf_nome': str,                # Nome completo da UF
    'regiao_id': int,              # ID da região
    'regiao_nome': str,            # Nome da região (Norte, Nordeste, etc.)
    'microrregiao_id': int,        # ID da microrregião
    'microrregiao_nome': str,      # Nome da microrregião
    'mesorregiao_id': int,         # ID da mesorregião
    'mesorregiao_nome': str        # Nome da mesorregião
}
```

**Volume**: ~5.570 municípios

**Frequência de Atualização**: Baixa (dados de referência)

#### 2. `bronze/ibge/estados/`
**Descrição**: Lista de estados brasileiros

**Schema**:
```python
{
    'uf_id': int,                  # ID do estado
    'uf_sigla': str,               # Sigla (SP, RJ, etc.)
    'uf_nome': str,                # Nome completo
    'regiao_id': int,               # ID da região
    'regiao_sigla': str,            # Sigla da região (N, NE, SE, S, CO)
    'regiao_nome': str             # Nome da região
}
```

**Volume**: 27 estados (26 + DF)

**Frequência de Atualização**: Baixa (dados de referência)

#### 3. `bronze/ibge/populacao_estados/`
**Descrição**: Estimativas de população por estado

**Schema**:
```python
{
    'uf_id': int,                  # ID do estado
    'uf_sigla': str,               # Sigla da UF
    'ano': int,                     # Ano da estimativa
    'populacao': int                # População estimada
}
```

**Volume**: 27 registros (um por estado)

**Frequência de Atualização**: Anual

#### 4. `bronze/portal_transparencia/bpc_municipios/`
**Descrição**: Dados de Benefício de Prestação Continuada (BPC) por município

**Schema**:
```python
{
    'id': int,                      # ID do registro
    'data_referencia': str,         # Data de referência (YYYY-MM-DD)
    'codigo_ibge': str,             # Código IBGE do município
    'nome_municipio': str,          # Nome do município
    'uf_sigla': str,                # Sigla da UF
    'uf_nome': str,                 # Nome da UF
    'regiao_nome': str,             # Nome da região
    'tipo_id': int,                 # ID do tipo de benefício
    'tipo_descricao': str,          # Descrição do tipo
    'tipo_descricao_detalhada': str, # Descrição detalhada
    'valor': float,                 # Valor total do benefício
    'quantidade_beneficiados': int  # Quantidade de beneficiados
}
```

**Volume**: Variável (depende da amostra coletada)

**Frequência de Atualização**: Mensal

#### 5. `bronze/portal_transparencia/orgaos_siafi/`
**Descrição**: Lista de órgãos do Sistema Integrado de Administração Financeira

**Schema**:
```python
{
    'codigo': str,                  # Código do órgão
    'descricao': str                # Descrição do órgão
}
```

**Volume**: ~500 órgãos

**Frequência de Atualização**: Baixa (dados de referência)

### Camada PRATA (Dados Tratados)

#### 1. `prata/dim_municipios/`
**Descrição**: Dimensão de municípios enriquecida com dados de estados e população

**Schema**: 
- Todas as colunas de `bronze/ibge/municipios/`
- + `populacao` (do estado, quando disponível)

**Transformações**:
- Remoção de duplicatas
- Normalização de nomes de colunas
- Merge com dados de estados
- Merge com dados de população

#### 2. `prata/dim_estados/`
**Descrição**: Dimensão de estados com agregações de BPC

**Schema**:
- Todas as colunas de `bronze/ibge/estados/`
- + `populacao`
- + `total_valor_bpc` (soma de valores BPC por estado)
- + `total_beneficiados_bpc` (soma de beneficiados por estado)
- + `valor_bpc_per_capita` (valor BPC por habitante)
- + `percentual_beneficiados` (% da população beneficiada)

**Transformações**:
- Agregação de dados de BPC por estado
- Cálculo de métricas per capita

#### 3. `prata/fato_bpc/`
**Descrição**: Fato de BPC relacionado com dimensão de municípios

**Schema**:
- Todas as colunas de `bronze/portal_transparencia/bpc_municipios/`
- + Colunas da dimensão de municípios (merge)
- + `valor_per_capita` (valor por beneficiado)
- + `ano` (extraído de data_referencia)
- + `mes` (extraído de data_referencia)

**Transformações**:
- Merge com dimensão de municípios
- Cálculo de métricas derivadas
- Extração de componentes temporais

#### 4. `prata/dim_orgaos/`
**Descrição**: Dimensão de órgãos tratada

**Schema**:
- Colunas de `bronze/portal_transparencia/orgaos_siafi/`
- Normalizadas (lowercase, trim)

**Transformações**:
- Normalização de nomes
- Remoção de duplicatas

### Camada OURO (Dados Enriquecidos)

#### 1. `ouro/dim_municipios_enriquecida/`
**Descrição**: Municípios com classificações e indicadores

**Schema**:
- Todas as colunas de `prata/dim_municipios/`
- + `classificacao_populacao` (Muito Pequeno, Pequeno, Médio, Grande, Muito Grande)
- + `regiao_sigla` (N, NE, SE, S, CO)
- + `data_processamento` (timestamp)
- + `versao_dados` (versão do schema)

**Enriquecimentos**:
- Classificação por população
- Siglas de região

#### 2. `ouro/dim_estados_enriquecida/`
**Descrição**: Estados com métricas avançadas

**Schema**:
- Todas as colunas de `prata/dim_estados/`
- + `classificacao_populacao` (Pequeno, Médio, Grande, Muito Grande)
- + `densidade_populacional` (estimada)
- + `indicador_bpc_alto` (boolean)
- + `ranking_valor_bpc` (ranking por valor BPC)
- + `data_processamento`
- + `versao_dados`

**Enriquecimentos**:
- Classificações e rankings
- Indicadores booleanos

#### 3. `ouro/fato_bpc_enriquecido/`
**Descrição**: Fato BPC com análises temporais e classificações

**Schema**:
- Todas as colunas de `prata/fato_bpc/`
- + `trimestre` (T1, T2, T3, T4)
- + `semestre` (S1, S2)
- + `faixa_valor` (Baixo, Médio, Alto, Muito Alto)
- + `faixa_beneficiados` (Poucos, Moderado, Muitos, Muitíssimos)
- + `indicador_eficiencia` (razão em relação à mediana)
- + `data_processamento`
- + `versao_dados`

**Enriquecimentos**:
- Agregações temporais
- Classificações por faixas
- Indicadores de eficiência

#### 4. `ouro/agregacao_bpc_por_regiao/`
**Descrição**: Agregações de BPC por região

**Schema**:
```python
{
    'regiao_nome': str,
    'total_valor': float,
    'media_valor': float,
    'mediana_valor': float,
    'total_beneficiados': int,
    'media_beneficiados': float,
    'media_valor_per_capita': float,
    'data_processamento': datetime,
    'versao_dados': str
}
```

#### 5. `ouro/agregacao_bpc_por_estado/`
**Descrição**: Agregações de BPC por estado

**Schema**:
```python
{
    'uf_sigla': str,
    'uf_nome': str,
    'total_valor': float,
    'media_valor': float,
    'total_beneficiados': int,
    'media_beneficiados': float,
    'media_valor_per_capita': float,
    'data_processamento': datetime,
    'versao_dados': str
}
```

#### 6. `ouro/top_10_municipios_valor_bpc/`
**Descrição**: Top 10 municípios por valor de BPC

**Schema**:
- Colunas selecionadas de `ouro/fato_bpc_enriquecido/`
- Ordenados por valor (descendente)
- Limitados a 10 registros

#### 7. `ouro/resumo_geral/`
**Descrição**: Resumo geral do Data Lake

**Schema**:
```python
{
    'metrica': str,                 # Nome da métrica
    'valor_texto': str,             # Valor como texto
    'valor_numerico': float         # Valor numérico (quando aplicável)
}
```

**Métricas**:
- Total Municípios
- Total Estados
- Total Registros BPC
- Data Processamento

---

## 🔄 Fluxo Completo de Dados

### Visão Geral do Fluxo

```
APIS EXTERNAS
     │
     ▼
[INGESTÃO BRONZE]
     │
     ├── Coleta dados brutos
     ├── Sem transformações
     └── Salva em Parquet particionado
     │
     ▼
MINIO (bronze/)
     │
     ▼
[TRANSFORMAÇÃO PRATA]
     │
     ├── Limpeza de dados
     ├── Normalização
     ├── Relacionamentos (joins)
     ├── Cálculo de métricas básicas
     └── Salva em Parquet particionado
     │
     ▼
MINIO (prata/)
     │
     ▼
[ENRIQUECIMENTO OURO]
     │
     ├── Classificações
     ├── Agregações
     ├── Rankings
     ├── Indicadores avançados
     └── Salva em Parquet particionado
     │
     ▼
MINIO (ouro/)
     │
     ▼
[CONSUMO]
     │
     ├── Spark SQL
     ├── Pandas
     ├── Jupyter Notebooks
     └── Análises e Dashboards
```

### Fluxo Detalhado Passo a Passo

#### Etapa 1: Ingestão Bronze

**Script**: `01_bronze_ingestion.py` ou `pipeline_ingestao.py`

**Processo**:

1. **Coleta IBGE Municípios**
   ```
   GET https://servicodados.ibge.gov.br/api/v1/localidades/municipios
   → JSON Array
   → DataFrame Pandas
   → Parquet: bronze/ibge/municipios/dt=20241201/data.parquet
   ```

2. **Coleta IBGE Estados**
   ```
   GET https://servicodados.ibge.gov.br/api/v1/localidades/estados
   → JSON Array
   → DataFrame Pandas
   → Parquet: bronze/ibge/estados/dt=20241201/data.parquet
   ```

3. **Coleta Portal Transparência - Órgãos**
   ```
   GET http://api.portaldatransparencia.gov.br/api-de-dados/orgaos-siafi
   Headers: {'chave-api-dados': '...'}
   → JSON Array
   → Filtrar códigos inválidos
   → DataFrame Pandas
   → Parquet: bronze/portal_transparencia/orgaos_siafi/dt=20241201/data.parquet
   ```

4. **Coleta Portal Transparência - BPC**
   ```
   Para cada município (amostra):
     GET http://api.portaldatransparencia.gov.br/api-de-dados/bpc-por-municipio
     Params: {'mesAno': '202412', 'codigoIbge': '3550308', 'pagina': 1}
     → JSON Array
   → Consolidar todos os resultados
   → DataFrame Pandas
   → Parquet: bronze/portal_transparencia/bpc_municipios/dt=20241201/data.parquet
   ```

5. **Coleta IBGE População**
   ```
   Para cada estado:
     GET https://servicodados.ibge.gov.br/api/v1/projecoes/populacao/{uf_id}
     → JSON Object
   → Consolidar todos os resultados
   → DataFrame Pandas
   → Parquet: bronze/ibge/populacao_estados/dt=20241201/data.parquet
   ```

#### Etapa 2: Transformação Prata

**Script**: `02_prata_transformacao.py`

**Processo**:

1. **Leitura dos Dados Bronze**
   ```
   Ler bronze/ibge/municipios/dt=YYYYMMDD/data.parquet → df_municipios
   Ler bronze/ibge/estados/dt=YYYYMMDD/data.parquet → df_estados
   Ler bronze/portal_transparencia/bpc_municipios/dt=YYYYMMDD/data.parquet → df_bpc
   Ler bronze/ibge/populacao_estados/dt=YYYYMMDD/data.parquet → df_populacao
   Ler bronze/portal_transparencia/orgaos_siafi/dt=YYYYMMDD/data.parquet → df_orgaos
   ```

2. **Tratamento e Limpeza**
   ```
   - Normalizar nomes de colunas (lowercase, trim)
   - Remover duplicatas
   - Padronizar tipos de dados
   - Validar integridade referencial
   ```

3. **Criação de Dimensões**
   ```
   dim_municipios = df_municipios.merge(df_estados, on='uf_sigla')
   dim_municipios = dim_municipios.merge(df_populacao, on='uf_sigla')
   
   dim_estados = df_estados.merge(df_populacao, on=['uf_id', 'uf_sigla'])
   
   dim_orgaos = df_orgaos (tratado)
   ```

4. **Criação de Fatos**
   ```
   fato_bpc = df_bpc.merge(dim_municipios, on='codigo_ibge')
   fato_bpc['valor_per_capita'] = fato_bpc['valor'] / fato_bpc['quantidade_beneficiados']
   fato_bpc['ano'] = fato_bpc['data_referencia'].dt.year
   fato_bpc['mes'] = fato_bpc['data_referencia'].dt.month
   ```

5. **Agregações**
   ```
   bpc_por_estado = df_bpc.groupby('uf_sigla').agg({
       'valor': 'sum',
       'quantidade_beneficiados': 'sum'
   })
   
   dim_estados = dim_estados.merge(bpc_por_estado, on='uf_sigla')
   dim_estados['valor_bpc_per_capita'] = dim_estados['total_valor_bpc'] / dim_estados['populacao']
   ```

6. **Salvamento Prata**
   ```
   Salvar dim_municipios → prata/dim_municipios/dt=YYYYMMDD/data.parquet
   Salvar dim_estados → prata/dim_estados/dt=YYYYMMDD/data.parquet
   Salvar fato_bpc → prata/fato_bpc/dt=YYYYMMDD/data.parquet
   Salvar dim_orgaos → prata/dim_orgaos/dt=YYYYMMDD/data.parquet
   ```

#### Etapa 3: Enriquecimento Ouro

**Script**: `03_ouro_enriquecimento.py`

**Processo**:

1. **Leitura dos Dados Prata**
   ```
   Ler prata/dim_municipios/dt=YYYYMMDD/data.parquet → dim_municipios
   Ler prata/dim_estados/dt=YYYYMMDD/data.parquet → dim_estados
   Ler prata/fato_bpc/dt=YYYYMMDD/data.parquet → fato_bpc
   Ler prata/dim_orgaos/dt=YYYYMMDD/data.parquet → dim_orgaos
   ```

2. **Enriquecimento de Municípios**
   ```
   ouro_municipios = dim_municipios.copy()
   ouro_municipios['classificacao_populacao'] = pd.cut(populacao, bins=[...])
   ouro_municipios['regiao_sigla'] = mapear_regiao(regiao_nome)
   ouro_municipios['data_processamento'] = datetime.now()
   ouro_municipios['versao_dados'] = '1.0'
   ```

3. **Enriquecimento de Estados**
   ```
   ouro_estados = dim_estados.copy()
   ouro_estados['classificacao_populacao'] = pd.cut(populacao, bins=[...])
   ouro_estados['densidade_populacional'] = populacao / area_estimada
   ouro_estados['indicador_bpc_alto'] = total_valor_bpc > mediana
   ouro_estados['ranking_valor_bpc'] = rank(total_valor_bpc)
   ```

4. **Enriquecimento de Fato BPC**
   ```
   ouro_fato_bpc = fato_bpc.copy()
   ouro_fato_bpc['trimestre'] = calcular_trimestre(mes)
   ouro_fato_bpc['semestre'] = calcular_semestre(mes)
   ouro_fato_bpc['faixa_valor'] = pd.cut(valor, bins=[...])
   ouro_fato_bpc['faixa_beneficiados'] = pd.cut(quantidade_beneficiados, bins=[...])
   ouro_fato_bpc['indicador_eficiencia'] = valor_per_capita / mediana
   ```

5. **Criação de Agregações**
   ```
   agregacao_regiao = fato_bpc.groupby('regiao_nome').agg({
       'valor': ['sum', 'mean', 'median'],
       'quantidade_beneficiados': ['sum', 'mean'],
       'valor_per_capita': 'mean'
   })
   
   agregacao_estado = fato_bpc.groupby('uf_sigla').agg({...})
   
   top_10_municipios = fato_bpc.nlargest(10, 'valor')
   ```

6. **Salvamento Ouro**
   ```
   Salvar ouro_municipios → ouro/dim_municipios_enriquecida/dt=YYYYMMDD/data.parquet
   Salvar ouro_estados → ouro/dim_estados_enriquecida/dt=YYYYMMDD/data.parquet
   Salvar ouro_fato_bpc → ouro/fato_bpc_enriquecido/dt=YYYYMMDD/data.parquet
   Salvar agregacao_regiao → ouro/agregacao_bpc_por_regiao/dt=YYYYMMDD/data.parquet
   Salvar agregacao_estado → ouro/agregacao_bpc_por_estado/dt=YYYYMMDD/data.parquet
   Salvar top_10_municipios → ouro/top_10_municipios_valor_bpc/dt=YYYYMMDD/data.parquet
   Salvar resumo_geral → ouro/resumo_geral/dt=YYYYMMDD/data.parquet
   ```

---

## 🚀 Passo a Passo de Instalação

### Pré-requisitos

- Docker e Docker Compose instalados
- Acesso à internet (para baixar imagens e acessar APIs)
- Portas 8080 e 8889 disponíveis

### 1. Clonar/Preparar Repositório

```bash
cd /data/govbr
```

### 2. Verificar Arquivos Necessários

```bash
# Verificar estrutura de diretórios
ls -la web-ui/
ls -la delta_scripts/
ls -la notebooks/

# Verificar docker-compose
cat docker-compose-spark.yml
```

### 3. Iniciar Serviços

#### Opção A: Apenas Dashboard Web (Porta 8080)

```bash
docker compose -f docker-compose-spark.yml up -d web-ui
```

#### Opção B: Dashboard + Jupyter Lab

```bash
# Se usar docker-compose.yml completo
docker compose up -d

# Ou se usar docker-compose-spark.yml
docker compose -f docker-compose-spark.yml up -d
```

### 4. Verificar Status dos Containers

```bash
docker ps --filter "name=govbr"
```

**Saída esperada**:
```
CONTAINER ID   IMAGE              STATUS         PORTS                    NAMES
xxxxxxxxxxxx   nginx:alpine       Up 2 minutes   0.0.0.0:8080->80/tcp    govbr-web-ui
xxxxxxxxxxxx   jupyter/pyspark... Up 2 minutes   0.0.0.0:8889->8888/tcp   govbr-jupyter-delta
```

### 5. Acessar Dashboard

Abra no navegador:
```
http://localhost:8080
```

### 6. Acessar Jupyter Lab

Clique no botão "Abrir Jupyter Lab" no dashboard ou acesse:
```
http://localhost:8889
```

### 7. Executar Pipeline de Ingestão

#### No Jupyter Lab:

1. Abra um novo notebook
2. Execute:

```python
# Executar pipeline completo em modo incremental
!python /home/jovyan/work/pipeline_ingestao.py --mode incremental
```

#### Ou no terminal do container:

```bash
docker exec -it govbr-jupyter-delta bash
cd /home/jovyan/work
python pipeline_ingestao.py --mode incremental
```

### 8. Executar Transformações

```bash
# No container Jupyter
python 02_prata_transformacao.py
python 03_ouro_enriquecimento.py
```

---

## 💻 Como Usar

### Acessando o Dashboard (Porta 8080)

1. **Abrir navegador**: `http://localhost:8080`
2. **Ver status dos serviços**: Dashboard mostra status online/offline
3. **Acessar Jupyter Lab**: Clique em "Abrir Jupyter Lab"
4. **Acessar MinIO**: Clique em "Acessar MinIO" (link externo)

### Executando Ingestão de Dados

#### Modo Interativo (Jupyter Notebook)

```python
# 1. Importar bibliotecas
import sys
sys.path.append('/home/jovyan/work')

# 2. Executar pipeline
exec(open('/home/jovyan/work/pipeline_ingestao.py').read())
```

#### Modo Script (Terminal)

```bash
# Modo FULL (recarrega tudo)
python pipeline_ingestao.py --mode full

# Modo INCREMENTAL (apenas novos dados)
python pipeline_ingestao.py --mode incremental

# Modo AUTO (decide automaticamente)
python pipeline_ingestao.py --mode auto
```

### Consultando Dados no MinIO

```python
from minio import Minio
import pandas as pd
import io

# Conectar ao MinIO
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

# Ler um arquivo Parquet
response = minio_client.get_object("govbr", "bronze/ibge/municipios/dt=20241201/data.parquet")
df = pd.read_parquet(io.BytesIO(response.read()))
response.close()
response.release_conn()

print(df.head())
```

### Consultando Dados com Spark

```python
from pyspark.sql import SparkSession

# Criar sessão Spark
spark = SparkSession.builder \
    .appName("GovBR Data Lake") \
    .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension") \
    .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog") \
    .config("spark.hadoop.fs.s3a.endpoint", "https://ch8ai-minio.l6zv5a.easypanel.host") \
    .config("spark.hadoop.fs.s3a.access.key", "admin") \
    .config("spark.hadoop.fs.s3a.secret.key", "1q2w3e4r") \
    .config("spark.hadoop.fs.s3a.path.style.access", "true") \
    .config("spark.hadoop.fs.s3a.connection.ssl.enabled", "true") \
    .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem") \
    .getOrCreate()

# Ler dados Ouro
df_ouro = spark.read.parquet("s3a://govbr/ouro/dim_municipios_enriquecida/")

# Consulta SQL
df_ouro.createOrReplaceTempView("municipios")
resultado = spark.sql("""
    SELECT 
        regiao_nome,
        COUNT(*) as total_municipios,
        AVG(populacao) as populacao_media
    FROM municipios
    GROUP BY regiao_nome
    ORDER BY total_municipios DESC
""")

resultado.show()
```

### Executando Pipeline Completo

```python
# Executar todas as etapas em sequência
import subprocess

# 1. Bronze
subprocess.run(["python", "pipeline_ingestao.py", "--mode", "incremental"])

# 2. Prata
subprocess.run(["python", "02_prata_transformacao.py"])

# 3. Ouro
subprocess.run(["python", "03_ouro_enriquecimento.py"])
```

---

## 🔍 Troubleshooting

### Problema: Dashboard não abre na porta 8080

**Solução**:
```bash
# Verificar se container está rodando
docker ps --filter "name=govbr-web-ui"

# Ver logs
docker logs govbr-web-ui

# Reiniciar container
docker compose -f docker-compose-spark.yml restart web-ui

# Verificar porta
netstat -tuln | grep 8080
```

### Problema: Erro ao conectar no MinIO

**Solução**:
```python
# Verificar credenciais
MINIO_SERVER_URL = "ch8ai-minio.l6zv5a.easypanel.host"
MINIO_ROOT_USER = "admin"
MINIO_ROOT_PASSWORD = "1q2w3e4r"

# Testar conexão
from minio import Minio
minio_client = Minio(
    MINIO_SERVER_URL,
    access_key=MINIO_ROOT_USER,
    secret_key=MINIO_ROOT_PASSWORD,
    secure=True
)

# Listar buckets
buckets = minio_client.list_buckets()
for bucket in buckets:
    print(bucket.name)
```

### Problema: Erro ao coletar dados das APIs

**Solução**:
```python
# Verificar conectividade
import requests

# Testar IBGE
response = requests.get("https://servicodados.ibge.gov.br/api/v1/localidades/estados", timeout=30)
print(f"IBGE Status: {response.status_code}")

# Testar Portal Transparência
headers = {'chave-api-dados': '2c56919ba91b8c1b13473dcef43fb031'}
response = requests.get(
    "http://api.portaldatransparencia.gov.br/api-de-dados/orgaos-siafi",
    headers=headers,
    timeout=30
)
print(f"Portal Status: {response.status_code}")
```

### Problema: Dados não aparecem no MinIO

**Solução**:
```python
# Verificar se arquivos foram salvos
from minio import Minio

minio_client = Minio(
    "ch8ai-minio.l6zv5a.easypanel.host",
    access_key="admin",
    secret_key="1q2w3e4r",
    secure=True
)

# Listar todos os objetos
objects = minio_client.list_objects("govbr", recursive=True)
for obj in objects:
    print(f"{obj.object_name} - {obj.size} bytes - {obj.last_modified}")
```

### Problema: Erro ao executar pipeline

**Solução**:
```bash
# Verificar se está no diretório correto
pwd
# Deve mostrar: /home/jovyan/work

# Verificar se arquivos existem
ls -la pipeline_ingestao.py
ls -la 01_bronze_ingestion.py

# Verificar dependências
python -c "import pandas, minio, requests"
```

### Problema: Spark não consegue ler dados do MinIO

**Solução**:
```python
# Verificar configurações S3A
spark.conf.set("spark.hadoop.fs.s3a.endpoint", "https://ch8ai-minio.l6zv5a.easypanel.host")
spark.conf.set("spark.hadoop.fs.s3a.access.key", "admin")
spark.conf.set("spark.hadoop.fs.s3a.secret.key", "1q2w3e4r")
spark.conf.set("spark.hadoop.fs.s3a.path.style.access", "true")
spark.conf.set("spark.hadoop.fs.s3a.connection.ssl.enabled", "true")
spark.conf.set("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem")

# Testar leitura
try:
    df = spark.read.parquet("s3a://govbr/bronze/ibge/municipios/")
    df.show(5)
except Exception as e:
    print(f"Erro: {e}")
```

---

## 📊 Resumo da Arquitetura

### Componentes Principais

1. **Dashboard Web (8080)**: Interface de acesso central
2. **Jupyter Lab (8889)**: Ambiente de desenvolvimento e análise
3. **MinIO**: Armazenamento de objetos (S3-compatible)
4. **Pipeline de Ingestão**: Coleta dados de APIs governamentais
5. **Camadas de Dados**: Bronze → Prata → Ouro
6. **Spark + Delta Lake**: Processamento e consultas SQL

### Fluxo de Dados

```
APIs → Bronze (Raw) → Prata (Cleaned) → Ouro (Enriched) → Análise
```

### Tecnologias

- **Storage**: MinIO (S3-compatible)
- **Format**: Parquet (columnar, compressed)
- **Processing**: Apache Spark, Pandas
- **Transactions**: Delta Lake
- **Interface**: Jupyter Lab, Dashboard Web

---

## 📞 Suporte

Para problemas ou dúvidas:

1. Verificar logs dos containers: `docker logs <container-name>`
2. Verificar documentação em `README_PIPELINE.md`
3. Verificar guia de APIs em `GUIA_APIS_FUNCIONANDO.md`
4. Consultar troubleshooting acima

---

**Última atualização**: Dezembro 2024
**Versão**: 1.0
