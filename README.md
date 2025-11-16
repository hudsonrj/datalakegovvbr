# 🏛️ DataLake GovBR - Pipeline de Dados Governamentais

Pipeline completo de ingestão, transformação e análise de dados governamentais brasileiros usando arquitetura medallion (Bronze, Prata, Ouro).

## 📋 Sobre o Projeto

Este projeto implementa um data lake para coletar, processar e analisar dados de APIs governamentais brasileiras:

- **Portal da Transparência**: Bolsa Família, BPC, Órgãos SIAFI
- **IBGE**: Municípios, Estados, População

## 🏗️ Arquitetura

O projeto segue a arquitetura **Medallion** (Bronze, Prata, Ouro):

### 🥉 Camada Bronze (Ingestão)
- Dados brutos coletados diretamente das APIs
- Formato: Parquet
- Localização: `bronze/`

### 🥈 Camada Prata (Transformação)
- Dados limpos, validados e relacionados
- Enriquecimento com joins entre tabelas
- Formato: Parquet
- Localização: `prata/`

### 🥇 Camada Ouro (Enriquecimento)
- Dados prontos para análise
- Métricas calculadas e agregações
- Rankings e análises pré-calculadas
- Formato: Parquet
- Localização: `ouro/`

## 🚀 Tecnologias

- **Python 3.11**
- **Pandas** - Manipulação de dados
- **MinIO** - Armazenamento S3-compatible
- **PyArrow** - Formato Parquet
- **Matplotlib/Seaborn** - Visualizações
- **Jupyter Lab** - Análises interativas
- **Docker** - Containerização

## 📁 Estrutura do Projeto

```
datalakegovvbr/
├── delta_scripts/          # Scripts principais do pipeline
│   ├── 01_bronze_ingestion.py
│   ├── 02_prata_transformacao.py
│   └── 03_ouro_enriquecimento.py
├── notebooks/               # Notebooks Jupyter
│   └── notebook_analises.ipynb
├── docker-compose.yml      # Configuração Docker
├── Dockerfile.jupyter-delta
└── README.md
```

## 🔧 Configuração

### Pré-requisitos

- Docker e Docker Compose
- Python 3.11+
- Acesso à internet (para APIs governamentais)

### Variáveis de Ambiente

Crie um arquivo `.env` com:

```bash
# MinIO
MINIO_SERVER_URL=seu-minio-server
MINIO_ROOT_USER=admin
MINIO_ROOT_PASSWORD=sua-senha
BUCKET_NAME=govbr

# Portal da Transparência
PORTAL_TRANSPARENCIA_API_KEY=sua-chave-api
```

### Instalação

1. Clone o repositório:
```bash
git clone https://github.com/hudsonrj28/datalakegovvbr.git
cd datalakegovvbr
```

2. Inicie os containers:
```bash
docker-compose -f docker-compose-delta.yml up -d
```

3. Acesse o Jupyter Lab:
```
http://localhost:8888
```

## 📊 Uso

### Executar Pipeline Completo

```bash
# No container Jupyter
cd /home/jovyan/work
python3 delta_scripts/01_bronze_ingestion.py
python3 delta_scripts/02_prata_transformacao.py
python3 delta_scripts/03_ouro_enriquecimento.py
```

### Análises no Jupyter

Abra o notebook `notebook_analises.ipynb` no Jupyter Lab para análises interativas.

## 📈 Dados Coletados

### Bolsa Família
- 500 municípios
- Período: Outubro/2021
- Dados: Valor total, beneficiários, percentuais

### BPC (Benefício de Prestação Continuada)
- 50 municípios de SP
- Período: Dezembro/2024
- Dados: Valor total, beneficiários

### População
- 982 municípios únicos
- Dados: População por município (2010)

### Municípios e Estados
- 5.571 municípios brasileiros
- 27 estados
- Dados geográficos completos

## 🔐 Segurança

⚠️ **IMPORTANTE**: Não commite chaves API ou credenciais no repositório!

- Use variáveis de ambiente para credenciais
- O arquivo `.gitignore` está configurado para proteger dados sensíveis
- Nunca exponha senhas ou chaves API no código

## 📝 Documentação

- [README_PIPELINE.md](README_PIPELINE.md) - Documentação do pipeline
- [DELTA_LAKE_FUNCIONANDO.md](DELTA_LAKE_FUNCIONANDO.md) - Guia Delta Lake
- [GUIA_RAPIDO_SPARK_SETUP.md](GUIA_RAPIDO_SPARK_SETUP.md) - Setup Spark

## 🤝 Contribuindo

Contribuições são bem-vindas! Por favor:

1. Faça um fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

## 👤 Autor

**Hudson RJ28**
- GitHub: [@hudsonrj28](https://github.com/hudsonrj28)

## 🙏 Agradecimentos

- Portal da Transparência do Governo Federal
- IBGE - Instituto Brasileiro de Geografia e Estatística
- Comunidade open source Python

---

⭐ Se este projeto foi útil para você, considere dar uma estrela no repositório!
