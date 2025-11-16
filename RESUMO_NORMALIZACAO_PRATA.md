# 🏗️ Normalização de Endereços - Bronze → Prata

## 📋 Objetivo

Normalizar todos os endereços da camada Bronze para o formato padrão brasileiro (ABNT NBR 14725 / Correios) e salvar na camada Prata.

## 📊 Processo

### 1. **Carregamento (Bronze)**
- Lê dados de `bronze/simulado/cidadaos/dt=YYYYMMDD/data.parquet`
- Mantém todos os dados originais do cidadão

### 2. **Normalização**
- Aplica normalizador de endereços brasileiros
- Extrai componentes estruturados:
  - Tipo de logradouro
  - Nome do logradouro
  - Número do imóvel
  - Complemento
  - Bairro
  - Município
  - UF
  - CEP

### 3. **Estruturação**
- Cria endereço normalizado no formato padrão
- Adiciona flags de qualidade (tem_complemento, tem_bairro, etc.)
- Mantém endereço original para referência

### 4. **Salvamento (Prata)**
- Salva em `prata/cidadaos_enderecos_normalizados/dt=YYYYMMDD/data.parquet`
- Formato: Parquet com compressão snappy

## 📁 Estrutura dos Dados na Prata

### Colunas do DataFrame:

**Dados do Cidadão (mantidos da Bronze):**
- `cpf`: CPF do cidadão
- `nome`: Nome completo
- `telefone`: Telefone
- `tipo_telefone`: Tipo do telefone
- `email`: Email
- `numero_endereco`: Índice do endereço (1, 2, 3, ...)
- `total_enderecos`: Total de endereços do cidadão

**Endereços:**
- `endereco_original`: Endereço original (Bronze)
- `endereco_normalizado`: Endereço no formato padrão brasileiro

**Componentes Estruturados:**
- `tipo_logradouro`: Tipo (Rua, Avenida, etc.)
- `nome_logradouro`: Nome do logradouro
- `numero_imovel`: Número do imóvel
- `complemento`: Complemento (se houver)
- `bairro`: Bairro
- `municipio`: Município
- `uf`: UF (sigla do estado)
- `cep`: CEP (formato 00000-000)

**Flags de Qualidade:**
- `tem_complemento`: Boolean
- `tem_bairro`: Boolean
- `tem_municipio`: Boolean
- `tem_uf`: Boolean
- `tem_cep`: Boolean
- `completo`: Boolean (todos os componentes presentes)

## 🎯 Formato Padrão Brasileiro

### Estrutura:
```
[Tipo Logradouro] [Nome Logradouro], [Número] - [Complemento] - [Bairro] - [Município]/[UF] - CEP [CEP]
```

### Exemplo:
```
Rua das Flores, 123 - Apto 45 - Centro - São Paulo/SP - CEP 01234-567
```

## 📊 Análises Disponíveis

O notebook inclui análises de:
- Qualidade dos dados normalizados
- Distribuição por estado
- Distribuição por município
- Tipos de logradouro
- Completude dos endereços
- Estatísticas gerais

## 🚀 Como Usar

1. **Abrir o notebook:**
   ```bash
   jupyter notebook notebook_normalizacao_enderecos_prata.ipynb
   ```

2. **Executar células sequencialmente:**
   - Célula 1: Importar bibliotecas
   - Célula 2: Conectar ao MinIO
   - Célula 3: Carregar dados da Bronze
   - Célula 4: Inicializar normalizador
   - Célula 5: Normalizar endereços
   - Célula 6: Visualizar dados
   - Célula 7: Análise de qualidade
   - Célula 8: Salvar na Prata
   - Célula 9: Resumo final

3. **Verificar resultados:**
   - Dados salvos em `prata/cidadaos_enderecos_normalizados/dt=YYYYMMDD/data.parquet`
   - Estatísticas de qualidade exibidas no notebook

## ✅ Benefícios

1. **Padronização**: Todos os endereços no formato oficial brasileiro
2. **Estruturação**: Componentes extraídos e organizados
3. **Qualidade**: Flags indicam completude dos dados
4. **Rastreabilidade**: Mantém endereço original para referência
5. **Pronto para análise**: Dados limpos e estruturados na Prata

## 📚 Referências

- **ABNT NBR 14725**: Norma técnica brasileira para endereçamento postal
- **Correios (ECT)**: Padrão oficial dos Correios
- **Documentação**: `PADRAO_ENDERECOS_BRASILEIROS.md`
- **Normalizador**: `normalizar_enderecos_brasileiros.py`
