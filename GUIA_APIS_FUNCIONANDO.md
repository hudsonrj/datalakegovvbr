# Guia de APIs do Gov.br que FUNCIONAM

## Problema identificado
O endpoint de Bolsa Família está retornando listas vazias (`[]`). Isso pode ser devido a:
1. Mudanças de nome do programa (Bolsa Família → Auxílio Brasil → Bolsa Família)
2. Dados não disponíveis para os períodos consultados
3. Formato de parâmetros específicos

## ✅ APIs TESTADAS E FUNCIONANDO

### 1. BPC por Município (FUNCIONA!)
```python
import requests
import pandas as pd

PORTAL_TRANSPARENCIA_API_KEY = "2c56919ba91b8c1b13473dcef43fb031"
transparency_url = "http://api.portaldatransparencia.gov.br/api-de-dados"

headers = {
    'chave-api-dados': PORTAL_TRANSPARENCIA_API_KEY
}

# BPC - Benefício de Prestação Continuada
response = requests.get(
    f"{transparency_url}/bpc-por-municipio",
    headers=headers,
    params={
        'mesAno': '202412',
        'codigoIbge': '3550308',  # São Paulo
        'pagina': 1
    },
    timeout=30
)

data = response.json()
df = pd.DataFrame(data)
print(df)
```

**Resposta esperada:**
```json
{
  "id": 531632761,
  "dataReferencia": "2024-12-01",
  "municipio": {
    "codigoIBGE": "3550308",
    "nomeIBGE": "SÃO PAULO",
    "uf": {"sigla": "SP", "nome": "SÃO PAULO"}
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

### 2. Órgãos SIAFI (FUNCIONA!)
```python
response = requests.get(
    f"{transparency_url}/orgaos-siafi",
    headers=headers,
    timeout=30
)

data = response.json()
df = pd.DataFrame(data)

# Filtrar apenas órgãos válidos
df = df[~df['descricao'].str.contains('CODIGO INVALIDO', na=False)]
print(df)
```

### 3. IBGE - Municípios (FUNCIONA!)
```python
# Não precisa de API key
ibge_url = "https://servicodados.ibge.gov.br/api/v1"

# Todos os municípios do Brasil
response = requests.get(f"{ibge_url}/localidades/municipios")
municipios = response.json()

df = pd.DataFrame([{
    'codigo_ibge': m['id'],
    'municipio': m['nome'],
    'uf': m['microrregiao']['mesorregiao']['UF']['sigla']
} for m in municipios])

print(df)
```

### 4. IBGE - Estados (FUNCIONA!)
```python
response = requests.get(f"{ibge_url}/localidades/estados")
estados = response.json()

df = pd.DataFrame([{
    'id': e['id'],
    'sigla': e['sigla'],
    'nome': e['nome'],
    'regiao': e['regiao']['nome']
} for e in estados])

print(df)
```

## ❌ APIs com Problemas

### Bolsa Família / Auxílio Brasil
**Status:** Retorna lista vazia
```python
# Retorna []
response = requests.get(
    f"{transparency_url}/bolsa-familia-por-municipio",
    headers=headers,
    params={'mesAno': '202412', 'codigoIbge': '3550308', 'pagina': 1}
)
```

### Cartões de Pagamento
**Status:** Erro 400 (Bad Request)
```python
# Retorna erro 400
response = requests.get(
    f"{transparency_url}/cartoes",
    headers=headers,
    params={'mesAnoInicio': '202401', 'mesAnoFim': '202401', 'pagina': 1}
)
```

### Despesas
**Status:** Erro 400 (Bad Request)
```python
# Retorna erro 400
response = requests.get(
    f"{transparency_url}/despesas/documentos",
    headers=headers,
    params={'dataInicio': '01/01/2024', 'dataFim': '31/01/2024', 'pagina': 1}
)
```

### Viagens
**Status:** Erro 400 (Bad Request)

### Servidores
**Status:** Erro 400 (Bad Request)

## 💡 Soluções Alternativas

### Para Bolsa Família
Use os **downloads em massa** disponíveis em:
https://portaldatransparencia.gov.br/download-de-dados/bolsa-familia-pagamentos

Estes são arquivos CSV grandes que você pode baixar diretamente.

### Para Despesas e Servidores
Verifique os parâmetros corretos na documentação oficial:
https://portaldatransparencia.gov.br/api-de-dados

Os endpoints podem exigir formatos específicos de data ou parâmetros adicionais.

## 📊 Exemplo Completo: Coletar BPC de Todo um Estado

```python
import requests
import pandas as pd
from minio import Minio
import io

# Configuração
PORTAL_TRANSPARENCIA_API_KEY = "2c56919ba91b8c1b13473dcef43fb031"
MINIO_SERVER_URL = "ch8ai-minio.l6zv5a.easypanel.host"
MINIO_ROOT_USER = "admin"
MINIO_ROOT_PASSWORD = "1q2w3e4r"
BUCKET_NAME = "govbr"

transparency_url = "http://api.portaldatransparencia.gov.br/api-de-dados"
ibge_url = "https://servicodados.ibge.gov.br/api/v1"

headers = {
    'chave-api-dados': PORTAL_TRANSPARENCIA_API_KEY
}

# MinIO client
minio_client = Minio(
    MINIO_SERVER_URL,
    access_key=MINIO_ROOT_USER,
    secret_key=MINIO_ROOT_PASSWORD,
    secure=True
)

# 1. Buscar municípios de São Paulo
response = requests.get(f"{ibge_url}/localidades/estados/35/municipios")
municipios_sp = response.json()

print(f"Total de municípios em SP: {len(municipios_sp)}")

# 2. Coletar BPC de cada município
bpc_data = []

for municipio in municipios_sp:
    codigo_ibge = str(municipio['id'])
    nome = municipio['nome']

    print(f"Buscando {nome}...")

    response = requests.get(
        f"{transparency_url}/bpc-por-municipio",
        headers=headers,
        params={'mesAno': '202412', 'codigoIbge': codigo_ibge, 'pagina': 1},
        timeout=10
    )

    if response.status_code == 200:
        data = response.json()
        if data:
            bpc_data.extend(data)

# 3. Criar DataFrame
df = pd.DataFrame(bpc_data)
print(f"\nTotal de registros: {len(df)}")
print(df.head())

# 4. Salvar no MinIO
csv_data = df.to_csv(index=False).encode('utf-8')
minio_client.put_object(
    BUCKET_NAME,
    "transparencia/bpc_202412_SP_completo.csv",
    io.BytesIO(csv_data),
    length=len(csv_data),
    content_type='text/csv'
)

print("Dados salvos no MinIO!")
```

## 🔍 Dicas de Debug

Para testar qualquer endpoint:

```python
response = requests.get(URL, headers=headers, params=params)

print(f"Status: {response.status_code}")
print(f"Headers: {response.headers}")
print(f"URL completa: {response.url}")
print(f"Resposta: {response.text[:500]}")

if response.status_code == 200:
    data = response.json()
    print(f"Tipo: {type(data)}")
    print(f"Tamanho: {len(data) if isinstance(data, list) else 'N/A'}")
    if isinstance(data, list) and len(data) > 0:
        print(f"Primeiro item: {data[0]}")
```

## 📚 Recursos Adicionais

1. **Documentação oficial:** https://portaldatransparencia.gov.br/api-de-dados
2. **Swagger API:** https://portaldatransparencia.gov.br/swagger-ui.html (se disponível)
3. **Downloads em massa:** https://portaldatransparencia.gov.br/download-de-dados
4. **IBGE API:** https://servicodados.ibge.gov.br/api/docs
