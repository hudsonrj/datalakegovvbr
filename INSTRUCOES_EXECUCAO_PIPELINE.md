# 🚀 Instruções para Executar e Popular Bronze e Prata

## ✅ Status Atual

- ✅ **Notebooks criados e validados**
- ✅ **Scripts de geração prontos**
- ✅ **Dados existentes na Bronze**: ~560k registros

## 📋 Passos para Executar

### Opção 1: Executar via Notebooks (Recomendado)

#### 1. Normalização - Bronze → Prata

1. Abra o Jupyter Lab:
   ```bash
   jupyter lab
   ```

2. Abra o notebook: `notebook_normalizacao_enderecos_prata.ipynb`

3. Execute todas as células sequencialmente (Shift+Enter)

4. O notebook irá:
   - Carregar dados da Bronze
   - Normalizar todos os endereços
   - Salvar na Prata: `prata/cidadaos_enderecos_normalizados/dt=YYYYMMDD/data.parquet`

#### 2. Ranking - Prata → Ouro

1. Abra o notebook: `notebook_ranking_enderecos_ouro.ipynb`

2. Execute todas as células sequencialmente

3. O notebook irá:
   - Carregar dados da Prata
   - Calcular scores e rankings
   - Marcar endereços certificados
   - Salvar na Ouro: `ouro/cidadaos_enderecos_rankings/dt=YYYYMMDD/data.parquet`

### Opção 2: Executar via Script Python

#### Dentro do Container Jupyter

```python
# Executar no Jupyter ou Python
exec(open('/data/govbr/testar_normalizacao_prata.py').read())
```

Ou via terminal dentro do container:

```bash
cd /data/govbr
python3 testar_normalizacao_prata.py
```

## 📊 Verificação dos Dados

### Verificar Bronze

```python
from minio import Minio
import io
import pandas as pd

minio_client = Minio(
    "ch8ai-minio.l6zv5a.easypanel.host",
    access_key="admin",
    secret_key="1q2w3e4r",
    secure=True
)

# Listar arquivos
objects = list(minio_client.list_objects("govbr", prefix="bronze/simulado/cidadaos/", recursive=True))
for obj in objects:
    print(f"{obj.object_name} ({obj.size/1024/1024:.2f} MB)")
```

### Verificar Prata

```python
objects = list(minio_client.list_objects("govbr", prefix="prata/cidadaos_enderecos_normalizados/", recursive=True))
for obj in objects:
    print(f"{obj.object_name} ({obj.size/1024/1024:.2f} MB)")
    
    # Carregar e verificar
    response = minio_client.get_object("govbr", obj.object_name)
    df = pd.read_parquet(io.BytesIO(response.read()))
    print(f"  Registros: {len(df):,}")
    print(f"  Completos: {df['completo'].sum():,}")
    response.close()
    response.release_conn()
```

### Verificar Ouro

```python
objects = list(minio_client.list_objects("govbr", prefix="ouro/cidadaos_enderecos_rankings/", recursive=True))
for obj in objects:
    print(f"{obj.object_name} ({obj.size/1024/1024:.2f} MB)")
    
    # Carregar e verificar
    response = minio_client.get_object("govbr", obj.object_name)
    df = pd.read_parquet(io.BytesIO(response.read()))
    print(f"  Registros: {len(df):,}")
    print(f"  Certificados: {df['endereco_certificado'].sum():,}")
    response.close()
    response.release_conn()
```

## 🔧 Gerar Mais Dados na Bronze (Opcional)

Se quiser gerar mais dados na Bronze (até 1 milhão de cidadãos):

```bash
cd /data/govbr
python3 gerar_massa_cidadaos_bronze.py
```

**Nota**: Isso pode demorar vários minutos/horas dependendo da quantidade.

## 📝 Estrutura Esperada

### Bronze
```
bronze/simulado/cidadaos/dt=YYYYMMDD/data.parquet
```
- Colunas: `cpf`, `nome`, `endereco`, `telefone`, `email`, `tipo_telefone`, `numero_endereco`, `total_enderecos`

### Prata
```
prata/cidadaos_enderecos_normalizados/dt=YYYYMMDD/data.parquet
```
- Colunas: Dados do cidadão + `endereco_normalizado` + componentes estruturados + flags de qualidade

### Ouro
```
ouro/cidadaos_enderecos_rankings/dt=YYYYMMDD/data.parquet
```
- Colunas: Dados da Prata + `ranking_cpf`, `score_final`, `percentual_probabilidade`, `endereco_certificado`

## ⚠️ Troubleshooting

### Erro de Conexão com MinIO

Se houver erro de conexão, verifique:
1. Se está executando dentro do container Jupyter
2. Se o MinIO está acessível: `ch8ai-minio.l6zv5a.easypanel.host`
3. Credenciais corretas: `admin` / `1q2w3e4r`

### Erro de Módulo Não Encontrado

Instale as dependências:
```bash
pip install --break-system-packages pandas pyarrow minio numpy faker matplotlib seaborn
```

### Memória Insuficiente

Se houver problemas de memória:
- Processe em lotes menores
- Use `df.head(10000)` para testar com menos dados primeiro

## ✅ Checklist de Execução

- [ ] Dados na Bronze verificados
- [ ] Notebook de normalização executado
- [ ] Dados na Prata verificados
- [ ] Notebook de ranking executado
- [ ] Dados na Ouro verificados
- [ ] Endereços certificados identificados

## 📚 Documentação Relacionada

- `RESUMO_NORMALIZACAO_PRATA.md`: Detalhes da normalização
- `RESUMO_RANKING_ENDERECOS.md`: Detalhes do ranking
- `PADRAO_ENDERECOS_BRASILEIROS.md`: Padrão brasileiro de endereços
- `normalizar_enderecos_brasileiros.py`: Normalizador de endereços
