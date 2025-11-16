# 🔑 Como Obter Chave API do Portal da Transparência

## Passo a Passo para Obter Dados Reais

### 1. Acessar o Portal da Transparência

Acesse: **https://portaldatransparencia.gov.br/api-de-dados**

### 2. Cadastrar-se / Fazer Login

- Clique em "Cadastre-se" ou "Entrar"
- Preencha seus dados
- Confirme o email

### 3. Obter Chave API

1. Após fazer login, vá em "Minha Conta" ou "API"
2. Clique em "Gerar Chave API" ou "Minhas Chaves"
3. Copie a chave gerada (formato: string alfanumérica)

### 4. Atualizar no Script

Edite o arquivo `01_bronze_ingestion.py` e atualize:

```python
PORTAL_TRANSPARENCIA_API_KEY = "SUA_CHAVE_AQUI"
```

### 5. Testar a Chave

Execute o script de teste:

```python
exec(open('/home/jovyan/work/testar_api_com_chave.py').read())
```

## Endpoint da API

- **URL Base:** `https://api.portaldatransparencia.gov.br/api-de-dados`
- **Endpoint Bolsa Família:** `/bolsa-familia-por-municipio`
- **Autenticação:** Header `chave-api-dados`

## Exemplo de Uso

```python
import requests

headers = {
    'chave-api-dados': 'SUA_CHAVE_AQUI',
    'Accept': 'application/json'
}

response = requests.get(
    'https://api.portaldatransparencia.gov.br/api-de-dados/bolsa-familia-por-municipio',
    headers=headers,
    params={
        'mesAno': '202412',
        'codigoIbge': '3550308',  # São Paulo
        'pagina': 1
    }
)

if response.status_code == 200:
    data = response.json()
    print(f"Dados coletados: {len(data)} registros")
else:
    print(f"Erro: {response.status_code}")
```

## Limites da API

- A API pode ter limites de requisições por minuto/hora
- Alguns endpoints podem ter limites específicos
- Verifique a documentação oficial para mais detalhes

## Documentação Oficial

- **Site:** https://portaldatransparencia.gov.br/api-de-dados
- **Documentação:** https://portaldatransparencia.gov.br/api-de-dados/swagger-ui.html
