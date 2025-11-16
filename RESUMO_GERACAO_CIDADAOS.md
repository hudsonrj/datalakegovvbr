# 📊 Resumo da Geração de Massa de Dados - Cidadãos

## ✅ Implementação Concluída

### Script Criado
- **Arquivo**: `gerar_massa_cidadaos_bronze.py`
- **Função**: Gera massa de dados de cidadãos brasileiros com múltiplos endereços

### Características dos Dados

#### Estrutura dos Registros
Cada registro contém:
- **cpf**: CPF do cidadão (formatado ou não)
- **nome**: Nome completo do cidadão
- **endereco**: Endereço completo com uma das 150+ variações de formatação
- **telefone**: Telefone (residencial, celular, comercial ou recado)
- **email**: Email baseado no nome do cidadão
- **tipo_telefone**: Tipo do telefone
- **numero_endereco**: Índice do endereço (1, 2, 3, ..., até 15)
- **total_enderecos**: Total de endereços deste cidadão

#### Especificações
- **Total de cidadãos**: 1.000.000
- **Endereços por cidadão**: 1 a 15 (aleatório)
- **Média esperada**: ~8 endereços por cidadão
- **Total de registros**: ~8.000.000 de registros de endereços
- **Variações de formatação**: 150 tipos diferentes

### Variações de Formatação de Endereços

O script implementa **150 variações diferentes** de formatação de endereços, incluindo:

1. **Grupo 1-20**: Formato padrão com variações de pontuação
   - Com/sem vírgulas
   - Com/sem hífens
   - Com/sem CEP
   - Diferentes separadores

2. **Grupo 21-40**: Com complemento
   - Apartamento, casa, sala, etc.
   - Diferentes formatos de complemento

3. **Grupo 41-60**: Abreviações de logradouro
   - R., Av., Pça., Tv., etc.

4. **Grupo 61-80**: Sem vírgulas ou com diferentes separadores
   - Espaços simples
   - Barras (/)
   - Pipes (|)

5. **Grupo 81-100**: Maiúsculas/minúsculas variadas
   - Tudo maiúsculo
   - Tudo minúsculo
   - Title case
   - Misturado

6. **Grupo 101-120**: Espaços extras ou compacto
   - Múltiplos espaços
   - Sem espaços
   - Compacto

7. **Grupo 121-140**: Ordem diferente dos componentes
   - Bairro primeiro
   - Cidade primeiro
   - Com labels (Bairro:, Cidade:)

8. **Grupo 141-150**: Caracteres especiais e formatações únicas
   - Barras duplas
   - Formatações especiais

### Estrutura de Armazenamento

```
bronze/
└── simulado/
    └── cidadaos/
        └── dt=YYYYMMDD/
            └── data.parquet
```

### Como Executar

#### Teste Rápido (10 cidadãos)
```bash
python3 testar_geracao_cidadaos.py
```

#### Geração Completa (1 milhão de cidadãos)
```bash
python3 gerar_massa_cidadaos_bronze.py
```

### Progresso da Geração

O script exibe progresso em tempo real:
- Progresso de cidadãos processados
- Total de registros de endereços gerados
- Salvamento em lotes (a cada 500k registros ou no final)

### Exemplo de Dados Gerados

```
CPF: 377.192.667-06
Nome: Gustavo Henrique Correia
Total de endereços: 13

Endereços:
1. Largo das Acácias, 3976, Botafogo, Vitória/ES
2. Est. Getúlio Vargas, 6171, Botafogo, Curitiba/PR
3. Boa Vista/RR - Laranjeiras - Travessa República, 6795
4. Jardim Brasil, 2772, Chácara N. 69 - Pinheiros, Campo Grande/MS
5. Viela Constituição 6382 - Moema - Palmas - TO
...
```

### Estatísticas Esperadas

- **Cidadãos únicos**: 1.000.000
- **Registros de endereços**: ~8.000.000
- **Média de endereços por cidadão**: ~8.0
- **Mínimo de endereços**: 1
- **Máximo de endereços**: 15
- **Tamanho estimado do arquivo**: ~300 MB (com compressão snappy)

### Dependências

```bash
pip install faker pandas pyarrow minio numpy
```

### Notas Técnicas

- **Geração de CPF**: Algoritmo válido com dígitos verificadores
- **Nomes**: Gerados usando Faker com locale pt_BR
- **Endereços**: Baseados em dados reais brasileiros (cidades, estados, bairros)
- **Telefones**: Formatos variados brasileiros (DDD + número)
- **Emails**: Baseados no nome do cidadão com domínios brasileiros comuns
- **Salvamento**: Formato Parquet com compressão snappy
- **Processamento**: Em lotes para otimizar memória

### Status Atual

✅ Script criado e testado
✅ Geração em andamento (processo em background)
⏳ Aguardando conclusão da geração completa

### Próximos Passos

Após a conclusão da geração:
1. Validar total de registros gerados
2. Verificar distribuição de endereços por cidadão
3. Validar todas as 150 variações de formatação
4. Preparar dados para camada Prata (transformação)
