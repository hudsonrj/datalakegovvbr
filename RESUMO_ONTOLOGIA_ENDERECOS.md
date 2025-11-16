# 📮 Resumo: Ontologia de Endereços Brasileiros

## ✅ Resposta à sua pergunta

**Sim, existe uma ontologia e padrões oficiais para endereços brasileiros!**

## 📋 Padrões Oficiais

### 1. **ABNT NBR 14725** - Norma Técnica Brasileira
- Define o padrão oficial para endereçamento postal
- Estabelece elementos obrigatórios e opcionais
- Referência técnica nacional

### 2. **Correios (ECT)** - Padrão Prático
- Padrão adotado pelos Correios
- Formato recomendado para correspondências

### 3. **ISO 19160-1** - Padrão Internacional
- Referência internacional
- Usado como base para sistemas globais

## 🏗️ Formato Padrão Brasileiro

### Estrutura Completa:
```
[Tipo Logradouro] [Nome Logradouro], [Número] - [Complemento] - [Bairro] - [Município]/[UF] - CEP [CEP]
```

### Exemplo Padrão:
```
Rua das Flores, 123 - Apto 45 - Centro - São Paulo/SP - CEP 01234-567
```

## 📊 Elementos do Endereço

### Obrigatórios:
1. **Tipo de Logradouro**: Rua, Avenida, Praça, etc.
2. **Nome do Logradouro**: Nome da rua/avenida
3. **Número**: Número do imóvel
4. **Bairro**: Bairro ou distrito
5. **Município**: Cidade
6. **UF**: Sigla do estado (2 letras)
7. **CEP**: Código postal (formato: 00000-000)

### Opcionais:
- **Complemento**: Apto, Sala, Bloco, etc.

## 🎯 Regras de Formatação

### Separadores:
- **Vírgula (,)**: Entre logradouro e número
- **Hífen (-)**: Entre componentes principais
- **Barra (/)**: Entre município e UF

### Maiúsculas/Minúsculas:
- **Tipo de logradouro**: Primeira letra maiúscula
- **Nome do logradouro**: Title Case (primeira letra de cada palavra maiúscula)
- **Bairro**: Title Case
- **Município**: Title Case
- **UF**: Sempre MAIÚSCULAS (2 letras)

### CEP:
- Formato: `00000-000` (5 dígitos, hífen, 3 dígitos)
- Pode ser precedido por "CEP" ou "CEP:"

## 📝 Variações na Prática

Embora exista um padrão oficial, na prática encontramos muitas variações:

### Variações Comuns:
- Diferentes separadores (vírgula, hífen, barra)
- Diferentes formatos de número (nº, n°, número, apenas número)
- Diferentes formatos de CEP (com/sem "CEP", com/sem hífen)
- Maiúsculas/minúsculas variadas
- Espaços extras ou compacto
- Ordem diferente dos componentes

## 🔧 Ferramentas Criadas

### 1. Documentação Completa
- `PADRAO_ENDERECOS_BRASILEIROS.md`: Documentação detalhada dos padrões

### 2. Normalizador de Endereços
- `normalizar_enderecos_brasileiros.py`: Classe Python para normalizar endereços

### Funcionalidades do Normalizador:
- ✅ Extrai componentes do endereço
- ✅ Normaliza tipo de logradouro
- ✅ Normaliza formatação (maiúsculas/minúsculas)
- ✅ Formata no padrão brasileiro
- ✅ Valida UF e CEP

## 💡 Uso Prático

### Para Normalizar Endereços:
```python
from normalizar_enderecos_brasileiros import NormalizadorEndereco

normalizador = NormalizadorEndereco()

# Normalizar um endereço
endereco_original = "rua augusta, nº 1234 - consolação - são paulo/sp - cep 01305-100"
endereco_normalizado = normalizador.normalizar_completo(endereco_original)

print(endereco_normalizado)
# Saída: Rua Augusta, 1234 - Consolação - São Paulo/SP - CEP 01305-100
```

## 📚 Referências

- **ABNT NBR 14725**: Norma técnica brasileira
- **Correios**: Padrão oficial dos Correios
- **IBGE**: Classificação de municípios e estados
- **ISO 19160-1**: Padrão internacional

## 🎯 Conclusão

Sim, existe uma ontologia e padrões oficiais para endereços brasileiros. O formato padrão é:

```
[Tipo] [Nome], [Número] - [Complemento] - [Bairro] - [Município]/[UF] - CEP [CEP]
```

Porém, na prática encontramos muitas variações, o que torna necessário normalizar os endereços antes de processá-los.
