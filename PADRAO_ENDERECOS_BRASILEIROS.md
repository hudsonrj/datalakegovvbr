# 📮 Padrão de Endereços Brasileiros - Ontologia e Normas

## 📋 Normas e Padrões Oficiais

### 1. **ABNT NBR 14725** - Endereçamento Postal
Norma técnica brasileira que define o padrão oficial para endereçamento postal no Brasil.

**Elementos obrigatórios:**
1. **Tipo de logradouro** (Rua, Avenida, Praça, etc.)
2. **Nome do logradouro**
3. **Número do imóvel**
4. **Bairro**
5. **Município**
6. **UF** (sigla do estado com 2 letras)
7. **CEP** (Código de Endereçamento Postal - formato: 00000-000)

**Elementos opcionais:**
- **Complemento** (Apartamento, Sala, Bloco, etc.)

### 2. **Correios (ECT)** - Padrão Oficial
Padrão adotado pelos Correios para endereçamento postal.

**Formato padrão:**
```
[Tipo Logradouro] [Nome Logradouro], [Número] - [Complemento] - [Bairro] - [Município]/[UF] - CEP [CEP]
```

**Exemplos:**

**Com complemento:**
```
Rua das Flores, 123 - Apto 45 - Centro - São Paulo/SP - CEP 01234-567
```

**Sem complemento:**
```
Avenida Paulista, 1000 - Bela Vista - São Paulo/SP - CEP 01310-100
```

**Apenas logradouro e número:**
```
Rua Augusta, 1234 - Consolação - São Paulo/SP - CEP 01305-100
```

### 3. **ISO 19160-1** - Padrão Internacional
Padrão internacional para endereços, usado como referência global.

## 🏗️ Estrutura Ontológica

### Hierarquia de Componentes

```
Endereço
├── Logradouro
│   ├── Tipo (Rua, Avenida, Praça, etc.)
│   └── Nome
├── Número do Imóvel
├── Complemento (opcional)
│   ├── Tipo (Apto, Sala, Bloco, etc.)
│   └── Identificador
├── Bairro
├── Localidade
│   ├── Município
│   └── UF (Estado)
└── CEP
```

## 📝 Regras de Formatação

### 1. **Tipo de Logradouro**
- Deve ser escrito por extenso ou abreviado
- Exemplos: Rua, Av., Pça., Tv., Al., Est., Rod.

### 2. **Nome do Logradouro**
- Primeira letra maiúscula
- Nomes próprios com inicial maiúscula
- Exemplos: "Rua das Flores", "Avenida Getúlio Vargas"

### 3. **Número do Imóvel**
- Após vírgula ou hífen
- Pode ser seguido de "nº", "n°", "Nº" ou apenas o número
- Exemplos: ", 123", ", nº 123", ", n° 123"

### 4. **Complemento**
- Separado por hífen
- Formato: "Tipo + Número" ou "Tipo + Número + Detalhes"
- Exemplos: "Apto 45", "Sala 12", "Bloco A", "Torre 1 Apto 45"

### 5. **Bairro**
- Separado por hífen
- Primeira letra maiúscula
- Exemplos: "Centro", "Bela Vista", "Jardim América"

### 6. **Município/UF**
- Formato: "Município/UF"
- Barra (/) separando município e UF
- UF sempre em maiúsculas (2 letras)
- Exemplos: "São Paulo/SP", "Rio de Janeiro/RJ"

### 7. **CEP**
- Formato: 00000-000 (5 dígitos, hífen, 3 dígitos)
- Pode ser precedido por "CEP" ou "CEP:"
- Exemplos: "CEP 01234-567", "CEP: 01234-567", "01234-567"

## ✅ Formato Padrão Recomendado

### Estrutura Completa:
```
[Tipo] [Nome], [Número] - [Complemento] - [Bairro] - [Município]/[UF] - CEP [CEP]
```

### Exemplos Práticos:

**Endereço completo:**
```
Rua das Flores, 123 - Apto 45 - Centro - São Paulo/SP - CEP 01234-567
```

**Sem complemento:**
```
Avenida Paulista, 1000 - Bela Vista - São Paulo/SP - CEP 01310-100
```

**Sem CEP:**
```
Rua Augusta, 1234 - Consolação - São Paulo/SP
```

**Apenas logradouro e número:**
```
Rua das Flores, 123 - São Paulo/SP
```

## 🔍 Tipos de Logradouro Comuns

### Principais:
- **Rua** (R.)
- **Avenida** (Av.)
- **Praça** (Pça.)
- **Travessa** (Tv.)
- **Alameda** (Al.)
- **Estrada** (Est.)
- **Rodovia** (Rod.)
- **Viela**
- **Beco**
- **Largo**
- **Vila**
- **Jardim**
- **Parque**
- **Conjunto**
- **Quadra**
- **Setor**

## 📊 Variações Aceitas (mas não padronizadas)

Embora exista um padrão oficial, na prática encontramos muitas variações:

### Variações de Separadores:
- Vírgula: `Rua X, 123`
- Hífen: `Rua X - 123`
- Barra: `Rua X / 123`
- Sem separador: `Rua X 123`

### Variações de Número:
- `, 123`
- `, nº 123`
- `, n° 123`
- `, Nº 123`
- `, número 123`

### Variações de CEP:
- `CEP 01234-567`
- `CEP: 01234-567`
- `01234-567`
- `CEP 01234567`

### Variações de Maiúsculas/Minúsculas:
- Tudo maiúsculo
- Tudo minúsculo
- Title case
- Misturado

## 🎯 Recomendação para Normalização

Para normalizar endereços brasileiros, recomenda-se:

1. **Extrair componentes** usando regex ou parser
2. **Normalizar cada componente**:
   - Tipo de logradouro: padronizar abreviações
   - Nome: Title case
   - Número: apenas números
   - Complemento: padronizar formato
   - Bairro: Title case
   - Município: Title case
   - UF: sempre maiúsculas
   - CEP: formato 00000-000

3. **Reconstruir** no formato padrão:
   ```
   [Tipo] [Nome], [Número] - [Complemento] - [Bairro] - [Município]/[UF] - CEP [CEP]
   ```

## 📚 Referências

- **ABNT NBR 14725**: Norma Técnica Brasileira para Endereçamento Postal
- **Correios (ECT)**: Padrão oficial dos Correios
- **ISO 19160-1**: Padrão internacional para endereços
- **IBGE**: Classificação de municípios e estados

## 💡 Notas Importantes

1. **CEP é obrigatório** para endereçamento postal, mas pode não estar presente em todos os endereços
2. **Complemento é opcional** e pode ter formatos variados
3. **Bairro pode não existir** em áreas rurais ou pequenos municípios
4. **UF sempre em maiúsculas** e com 2 letras
5. **Município** deve ser o nome oficial conforme IBGE

## 🔧 Ferramentas Úteis

- **API dos Correios**: Validação de CEP
- **IBGE API**: Validação de municípios e estados
- **Parsers de endereço**: Bibliotecas Python como `pycep-correios`, `python-cep`
