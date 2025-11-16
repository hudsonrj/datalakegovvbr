# 🚀 Guia Rápido - Porta 8080

## Acesso Rápido

- **Dashboard Web**: http://localhost:8080
- **Jupyter Lab**: http://localhost:8889
- **MinIO**: https://ch8ai-minio.l6zv5a.easypanel.host

## Comandos Essenciais

### Iniciar Serviços
```bash
docker compose -f docker-compose-spark.yml up -d
```

### Ver Status
```bash
docker ps --filter "name=govbr"
```

### Executar Pipeline
```bash
# No container Jupyter
docker exec -it govbr-jupyter-delta bash
cd /home/jovyan/work
python pipeline_ingestao.py --mode incremental
```

## Estrutura de Dados

```
govbr/
├── bronze/          # Dados brutos das APIs
├── prata/           # Dados tratados
└── ouro/            # Dados enriquecidos
```

## APIs Utilizadas

1. **IBGE**: https://servicodados.ibge.gov.br/api/v1
   - Municípios, Estados, População

2. **Portal Transparência**: http://api.portaldatransparencia.gov.br/api-de-dados
   - BPC por Município, Órgãos SIAFI

## Documentação Completa

📚 **DOCUMENTACAO_COMPLETA_PORTA_8080.md** - Documentação detalhada com:
- Arquitetura completa
- Diagramas do sistema
- Passo a passo detalhado
- Catálogo de dados
- Fluxo de ingestão
- Troubleshooting
