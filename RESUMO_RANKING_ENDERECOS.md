# 🏆 Ranking e Certificação de Endereços por CPF - Ouro

## 📋 Objetivo

Criar um ranking de endereços por CPF, calculando a probabilidade de cada endereço ser o endereço atual e mais correto, marcando o endereço com maior score como **certificado**.

## 📊 Processo

### 1. **Carregamento (Prata)**
- Lê dados de `prata/cidadaos_enderecos_normalizados/dt=YYYYMMDD/data.parquet`
- Endereços já normalizados e estruturados

### 2. **Cálculo de Score de Confiabilidade**

O score é calculado com base em 4 critérios:

#### **Completude (Peso 40%)**
- Endereço completo: 40 pontos
- Endereço incompleto: pontos proporcionais aos componentes presentes
  - CEP, UF, Município, Bairro, Complemento

#### **Qualidade dos Dados (Peso 20%)**
- CEP válido (8 dígitos): 5 pontos
- UF válida (2 caracteres): 5 pontos
- Município válido (>2 caracteres): 5 pontos
- Número presente: 5 pontos

#### **Ordem do Endereço (Peso 10%)**
- Primeiro endereço (número 1): 10 pontos
- Endereços 2-3: 7 pontos
- Endereços 4-7: 4 pontos
- Endereços 8+: 1 ponto

#### **Frequência (Peso 30%)**
- Calculada após agrupamento por CPF
- Endereços que aparecem mais vezes recebem pontuação maior
- Frequência relativa dentro do CPF

### 3. **Agrupamento e Ranking**

- Agrupa endereços por CPF
- Calcula frequência de cada endereço único por CPF
- Calcula frequência relativa (percentual dentro do CPF)
- Adiciona pontuação de frequência ao score final

### 4. **Criação do Ranking**

- Ordena endereços por score final (maior para menor)
- Atribui ranking (1 = melhor, 2 = segundo melhor, etc.)
- Calcula percentual de probabilidade:
  ```
  percentual = (score_endereco / soma_scores_cpf) * 100
  ```

### 5. **Certificação**

- Marca endereço com `ranking_cpf = 1` como **certificado**
- Campo `endereco_certificado = True` para o melhor endereço de cada CPF

### 6. **Salvamento (Ouro)**

- Salva em `ouro/cidadaos_enderecos_rankings/dt=YYYYMMDD/data.parquet`
- Formato: Parquet com compressão snappy

## 📁 Estrutura dos Dados na Ouro

### Colunas do DataFrame:

**Dados do Cidadão:**
- `cpf`: CPF do cidadão
- `nome`: Nome completo
- `telefone`: Telefone
- `tipo_telefone`: Tipo do telefone
- `email`: Email
- `total_enderecos`: Total de endereços do cidadão

**Endereços:**
- `endereco_normalizado`: Endereço no formato padrão brasileiro
- `endereco_original`: Endereço original (Bronze)

**Componentes Estruturados:**
- `tipo_logradouro`, `nome_logradouro`, `numero_imovel`
- `complemento`, `bairro`, `municipio`, `uf`, `cep`

**Qualidade:**
- `completo`: Boolean (todos componentes presentes)
- `tem_complemento`, `tem_bairro`, `tem_municipio`, `tem_uf`, `tem_cep`

**Ranking e Certificação:**
- `numero_endereco`: Índice original do endereço
- `ranking_cpf`: Posição no ranking (1 = melhor)
- `score_base`: Score sem frequência (0-70 pontos)
- `score_frequencia`: Pontuação de frequência (0-30 pontos)
- `score_final`: Score total (0-100 pontos)
- `percentual_probabilidade`: Probabilidade de ser o endereço atual (%)
- `endereco_certificado`: Boolean (True = endereço principal)
- `frequencia`: Quantas vezes o endereço aparece para o CPF
- `frequencia_relativa`: Percentual de frequência dentro do CPF

## 🎯 Exemplo de Ranking

Para um CPF com 3 endereços:

```
CPF: 123.456.789-00
Nome: João Silva

[1] ✅ CERTIFICADO
   Endereço: Rua das Flores, 123 - Apto 45 - Centro - São Paulo/SP - CEP 01234-567
   Score: 95.50
   Probabilidade: 45.2%
   Frequência: 2 (66.7%)
   Completo: ✅

[2]
   Endereço: Av. Paulista, 1000 - Bela Vista - São Paulo/SP - CEP 01310-100
   Score: 78.30
   Probabilidade: 37.1%
   Frequência: 1 (33.3%)
   Completo: ✅

[3]
   Endereço: Rua X, 50 - São Paulo/SP
   Score: 37.20
   Probabilidade: 17.7%
   Frequência: 1 (33.3%)
   Completo: ❌
```

## 📊 Análises Disponíveis

O notebook inclui análises de:
- Estatísticas dos endereços certificados
- Distribuição por estado
- Distribuição de percentuais de probabilidade
- Exemplos de rankings por CPF
- Qualidade dos endereços certificados

## 🚀 Como Usar

1. **Abrir o notebook:**
   ```bash
   jupyter notebook notebook_ranking_enderecos_ouro.ipynb
   ```

2. **Executar células sequencialmente:**
   - Célula 1: Importar bibliotecas
   - Célula 2: Conectar ao MinIO
   - Célula 3: Definir funções auxiliares
   - Célula 4: Carregar dados da Prata
   - Célula 5: Calcular score base
   - Célula 6: Agrupar por CPF e calcular frequência
   - Célula 7: Calcular score final e ranking
   - Célula 8: Preparar dados para Ouro
   - Célula 9: Análise de endereços certificados
   - Célula 10: Visualizar ranking por CPF
   - Célula 11: Salvar na Ouro
   - Célula 12: Resumo final

3. **Verificar resultados:**
   - Dados salvos em `ouro/cidadaos_enderecos_rankings/dt=YYYYMMDD/data.parquet`
   - Endereços certificados marcados com `endereco_certificado = True`

## ✅ Benefícios

1. **Identificação Automática**: Endereço mais provável identificado automaticamente
2. **Ranking Transparente**: Score e percentual explicam a decisão
3. **Múltiplos Critérios**: Considera completude, frequência, qualidade e ordem
4. **Rastreabilidade**: Mantém todos os endereços com seus scores
5. **Pronto para Uso**: Dados enriquecidos prontos para análise e BI

## 🔍 Interpretação dos Scores

- **Score Final (0-100)**:
  - 80-100: Endereço muito confiável (completo, frequente, de qualidade)
  - 60-79: Endereço confiável (boa qualidade)
  - 40-59: Endereço moderado (alguns componentes faltando)
  - 0-39: Endereço pouco confiável (incompleto ou raro)

- **Percentual de Probabilidade**:
  - Indica a probabilidade relativa de ser o endereço atual
  - Soma dos percentuais de um CPF = 100%
  - Endereço certificado geralmente tem >30% de probabilidade

## 📚 Referências

- **Camada Prata**: `notebook_normalizacao_enderecos_prata.ipynb`
- **Normalizador**: `normalizar_enderecos_brasileiros.py`
- **Padrão Brasileiro**: `PADRAO_ENDERECOS_BRASILEIROS.md`
