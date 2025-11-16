# 🚀 Guia Rápido Completo - Pipeline GovBR Data Lake

## 📋 Visão Geral

Este guia fornece instruções rápidas para executar todo o pipeline de dados GovBR, desde a ingestão Bronze até a geração de visualizações Ouro.

## 🎯 Scripts Principais

### 1. Validação Completa (Execute Primeiro!)
```python
exec(open('/home/jovyan/work/validacao_completa_pipeline.py').read())
```
**O que faz:** Valida todo o pipeline (Bronze, Prata, Ouro) e mostra o que está faltando.

### 2. Correção Automática Completa
```python
# Corrige Prata e Ouro em sequência
exec(open('/home/jovyan/work/gerar_camada_ouro_completa.py').read())
```
**O que faz:** 
- Verifica e corrige Prata
- Gera camada Ouro completa
- Valida resultados

### 3. Teste Completo com Gráficos
```python
exec(open('/home/jovyan/work/teste_completo_com_graficos.py').read())
```
**O que faz:**
- Verifica todas as camadas
- Executa ingestão/transformação se necessário
- Gera dashboard com 9 gráficos
- Salva em `/home/jovyan/work/dashboard_analise.png`

## 🔧 Scripts de Correção Individual

### Corrigir Fatos Prata
```python
exec(open('/home/jovyan/work/corrigir_fatos_prata.py').read())
```
**Quando usar:** Se `fato_bpc` ou `fato_bolsa_familia` não aparecerem na Prata.

### Gerar Dados Simulados Bolsa Família
```python
exec(open('/home/jovyan/work/gerar_dados_simulados_bolsa_familia.py').read())
```
**Quando usar:** Se a API de Bolsa Família não estiver disponível.

### Gerar Camada Ouro
```python
exec(open('/home/jovyan/work/03_ouro_enriquecimento.py').read())
```
**Quando usar:** Se os datasets Ouro não estiverem disponíveis.

## 📊 Scripts de Pipeline Completo

### Ingestão Bronze
```python
exec(open('/home/jovyan/work/01_bronze_ingestion.py').read())
```
**O que faz:**
- Coleta dados de APIs (IBGE, Portal Transparência)
- Gera dados simulados se APIs falharem
- Salva na camada Bronze

### Transformação Prata
```python
exec(open('/home/jovyan/work/02_prata_transformacao.py').read())
```
**O que faz:**
- Lê dados Bronze
- Transforma e relaciona dados
- Calcula métricas (percentuais, valores médios)
- Salva na camada Prata

### Enriquecimento Ouro
```python
exec(open('/home/jovyan/work/03_ouro_enriquecimento.py').read())
```
**O que faz:**
- Enriquece dados Prata com métricas avançadas
- Cria rankings e agregações
- Salva na camada Ouro

## 📈 Visualizações

### Notebook Interativo
Abra o notebook: `TESTE_COMPLETO_GRAFICOS.ipynb`

### Dashboard DEMO
Abra o notebook: `DEMO_APRESENTACAO.ipynb`

## 🔍 Diagnósticos

### Verificar Dados Bronze
```python
exec(open('/home/jovyan/work/verificar_bronze.py').read())
```

### Diagnóstico de Fatos
```python
exec(open('/home/jovyan/work/diagnostico_fatos.py').read())
```

## 🎯 Fluxo Recomendado (Primeira Execução)

1. **Validar Pipeline:**
   ```python
   exec(open('/home/jovyan/work/validacao_completa_pipeline.py').read())
   ```

2. **Se faltar dados Bronze:**
   ```python
   exec(open('/home/jovyan/work/01_bronze_ingestion.py').read())
   ```

3. **Se faltar dados Prata:**
   ```python
   exec(open('/home/jovyan/work/corrigir_fatos_prata.py').read())
   ```

4. **Se faltar dados Ouro:**
   ```python
   exec(open('/home/jovyan/work/gerar_camada_ouro_completa.py').read())
   ```

5. **Gerar Visualizações:**
   ```python
   exec(open('/home/jovyan/work/teste_completo_com_graficos.py').read())
   ```

## 📁 Estrutura de Dados Esperada

### 🥉 Bronze (6 datasets)
- `municipios`
- `estados`
- `populacao_estados`
- `orgaos_siafi`
- `bpc_municipios`
- `bolsa_familia_municipios`

### 🥈 Prata (5 datasets)
- `dim_municipios`
- `dim_estados`
- `dim_orgaos`
- `fato_bpc`
- `fato_bolsa_familia`

### 🏆 Ouro (5 datasets)
- `municipios_enriquecidos`
- `estados_enriquecidos`
- `bpc_analytics`
- `rankings`
- `agregacoes_regionais`

## ⚠️ Solução de Problemas

### Erro S3A (ClassNotFoundException)
```python
exec(open('/home/jovyan/work/spark_com_jars_manual.py').read())
```

### Spark não inicializa
```python
exec(open('/home/jovyan/work/inicializar_spark.py').read())
```

### Dados não aparecem
1. Execute validação completa
2. Execute correção específica da camada
3. Verifique logs de erro

## 📊 Métricas Importantes

### Dados Esperados
- **Municípios:** ~5.570 registros
- **Estados:** 27 registros
- **População:** 27 estados com dados
- **BPC:** ~50 municípios (amostra SP)
- **Bolsa Família:** ~50 municípios (amostra SP ou simulados)

### Percentuais Calculados
- **% Beneficiários:** Quantidade de beneficiários / População * 100
- **Valor Médio:** Valor Total / Quantidade de Beneficiários

## 🎉 Pronto!

Após executar os scripts, você terá:
- ✅ Dados completos nas 3 camadas
- ✅ Métricas calculadas
- ✅ Visualizações prontas
- ✅ Dashboard gerado

**Execute a validação completa para verificar o status atual!**
