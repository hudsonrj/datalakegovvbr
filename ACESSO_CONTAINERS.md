# 🚀 Containers Subidos com Sucesso!

## ✅ Status

O container **govbr-jupyter-delta** está rodando!

## 📊 Como Acessar

### 1. Jupyter Lab
**URL:** http://localhost:8889

Abra no seu navegador e você terá acesso a:
- Notebooks interativos
- Terminal Python
- Interface gráfica para consultas

### 2. Verificar Status
```bash
docker compose -f docker-compose-simple.yml ps
```

### 3. Ver Logs
```bash
docker logs govbr-jupyter-delta -f
```

## 📝 Próximos Passos

### Opção 1: Usar Jupyter Lab (Recomendado)

1. Acesse: http://localhost:8889
2. Abra o notebook: `notebooks/consultas_simples_duckdb.ipynb`
3. Execute as células para fazer consultas SQL

### Opção 2: Executar Scripts Dentro do Container

```bash
# Entrar no container
docker exec -it govbr-jupyter-delta bash

# Executar script Python
python /home/jovyan/work/solucao_simples_duckdb.py
```

### Opção 3: Converter para Delta Lake (Opcional)

Se quiser usar Delta Lake completo:

```bash
# Executar setup Delta Lake
docker exec -it govbr-jupyter-delta python /home/jovyan/work/delta_setup_spark.py
```

## 🔧 Comandos Úteis

### Parar containers
```bash
docker compose -f docker-compose-simple.yml down
```

### Reiniciar containers
```bash
docker compose -f docker-compose-simple.yml restart
```

### Ver logs em tempo real
```bash
docker logs govbr-jupyter-delta -f
```

## 📚 Arquivos Disponíveis no Container

- `/home/jovyan/work/` - Scripts Python
- `/home/jovyan/notebooks/` - Notebooks Jupyter
- `/home/jovyan/govbr/` - Todo o projeto

## ✅ Tudo Pronto!

Agora você pode:
1. ✅ Acessar Jupyter Lab em http://localhost:8889
2. ✅ Fazer consultas SQL nos seus dados Parquet
3. ✅ Usar notebooks interativos
4. ✅ Executar scripts Python
