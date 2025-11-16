# 🔧 Configuração do Spark - Arquivos Disponíveis

## 📚 Arquivos de Configuração

### Notebooks (Execute primeiro!)
1. **`00_SPARK_SETUP.ipynb`** ⭐ **PRINCIPAL** - Execute este primeiro!
   - Configuração completa passo a passo
   - Resolve problemas de "Connection refused"
   - Testes automáticos

2. **`notebook_spark_setup.ipynb`** - Alternativo
   - Versão alternativa do notebook de setup

### Scripts Python
- **`spark_setup_fixed.py`** - Script de configuração corrigido
  - Use em qualquer notebook: `exec(open('spark_setup_fixed.py').read())`

### Documentação
- **`GUIA_RAPIDO_SPARK_SETUP.md`** - Guia rápido de uso

## 🚀 Como Usar

### Opção 1: Notebook Principal (Recomendado)
1. Abra o Jupyter Lab
2. Procure por: **`00_SPARK_SETUP.ipynb`**
3. Abra e execute todas as células na ordem

### Opção 2: Script Python
Em qualquer notebook, adicione no início:
```python
exec(open('spark_setup_fixed.py').read())
```

## ✅ Após Executar

Teste se funcionou:
```python
print(f"✅ Spark: {spark.version}")
test_df = spark.range(5)
test_df.show()
```

## 📍 Localização

Todos os arquivos estão em: `/home/jovyan/work/`

## 🔄 Se Não Aparecer

1. Recarregue a página do Jupyter Lab (F5)
2. Verifique se está no diretório `/home/jovyan/work/`
3. Use a busca do Jupyter Lab: procure por "SPARK" ou "setup"
