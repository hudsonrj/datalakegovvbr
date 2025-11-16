# 🔧 Guia de Correção - Erro Py4J Network Error

## ❌ Erro Encontrado

```
Py4JNetworkError: Answer from Java side is empty
```

Este erro ocorre quando há problemas de comunicação entre Python (PySpark) e Java (Spark).

## ✅ Solução Rápida

### Opção 1: Usar o Notebook de Correção (Recomendado)

1. Abra o Jupyter Lab: http://49.13.203.251:8889
2. Navegue até o arquivo: `FIX_PY4J_ERROR.ipynb`
3. Execute todas as células em ordem
4. Aguarde a conclusão (pode levar alguns segundos)

### Opção 2: Executar Script Python Diretamente

No Jupyter Lab, crie uma nova célula e execute:

```python
# Executar script de correção
exec(open('/home/jovyan/work/fix_spark_py4j.py').read())
```

### Opção 3: Usar Script de Configuração Atualizado

```python
# Usar script de configuração atualizado
exec(open('/home/jovyan/work/configurar_spark.py').read())
```

## 🔍 O que o Script Faz

O script `fix_spark_py4j.py` executa os seguintes passos:

1. **Limpa Ambiente**
   - Para todas as sessões Spark existentes
   - Finaliza processos Java do Spark
   - Limpa memória (garbage collection)

2. **Verifica e Libera Portas** ⭐ NOVO
   - Verifica portas comuns do Spark (4040, 8080, 7077, etc.)
   - Mata processos que estão usando essas portas
   - Evita erros "Connection refused"

3. **Configura Variáveis de Ambiente**
   - Configura `JAVA_HOME` automaticamente
   - Define variáveis de rede (`SPARK_LOCAL_IP`, `SPARK_DRIVER_HOST`)
   - Configura paths do Python

4. **Verifica Recursos**
   - Verifica memória disponível
   - Ajusta configurações de memória do Spark automaticamente

5. **Cria Spark Session Robusta**
   - Configurações de timeout aumentadas
   - Garbage Collector otimizado (G1GC)
   - Configurações de rede IPv4
   - **Portas dinâmicas (0)** para evitar conflitos ⭐ NOVO
   - Suporte a S3A (MinIO)

6. **Verifica Conectividade de Rede** ⭐ NOVO
   - Testa conectividade de socket antes de criar sessão
   - Identifica problemas de rede precocemente

7. **Testa Conectividade Py4J**
   - Testa comunicação Py4J
   - Verifica se Spark está respondendo

## 📋 Configurações Aplicadas

### Memória
- **Driver Memory**: 2GB (ou menos se pouca memória disponível)
- **Executor Memory**: 2GB (ou menos se pouca memória disponível)
- **Max Result Size**: 1GB

### Timeouts
- **Network Timeout**: 1200s (20 minutos)
- **Heartbeat Interval**: 60s
- **S3A Connection Timeout**: 60000ms

### Portas
- **Portas Dinâmicas**: Todas as portas do Spark são configuradas como `0` (dinâmicas)
  - `spark.driver.port = 0`
  - `spark.blockManager.port = 0`
  - `spark.broadcast.port = 0`
  - `spark.fileserver.port = 0`
  - `spark.replClassServer.port = 0`
  - `spark.ui.port = 0`
- Isso evita conflitos de porta e erros "Connection refused"

### Java Options
- `-Dio.netty.tryReflectionSetAccessible=true` - Permite reflexão do Netty
- `-XX:+UseG1GC` - Usa G1 Garbage Collector
- `-XX:MaxGCPauseMillis=200` - Limita pausas do GC
- `-Djava.net.preferIPv4Stack=true` - Prefere IPv4
- `-Djava.awt.headless=true` - Modo headless (sem interface gráfica)

## 🚨 Se o Erro Persistir

### 1. Reiniciar Container

```bash
docker restart govbr-jupyter-delta
```

Aguarde alguns segundos e tente novamente.

### 2. Verificar Logs

```bash
docker logs govbr-jupyter-delta
```

Procure por erros relacionados a:
- Memória (OutOfMemoryError)
- Portas em uso
- Problemas de Java

### 3. Verificar Memória Disponível

```bash
docker exec -it govbr-jupyter-delta free -h
```

Se houver pouca memória disponível, o script ajustará automaticamente.

### 4. Verificar Processos Java

```bash
docker exec -it govbr-jupyter-delta ps aux | grep java
```

Se houver muitos processos Java, pode ser necessário reiniciar o container.

### 5. Verificar Portas

```bash
docker exec -it govbr-jupyter-delta netstat -tuln | grep -E "4040|8080"
```

Se as portas estiverem em uso, pode ser necessário parar outros serviços.

## 💡 Dicas

1. **Sempre execute o script de correção primeiro** antes de usar Spark em um novo notebook
2. **Não execute múltiplas sessões Spark simultaneamente** - pare uma antes de criar outra
3. **Se o erro ocorrer durante uma operação longa**, pode ser falta de memória - reduza o tamanho dos dados processados
4. **Use `spark.stop()`** quando terminar de usar Spark para liberar recursos

## 📝 Exemplo de Uso Após Correção

```python
# 1. Executar correção (se necessário)
exec(open('/home/jovyan/work/fix_spark_py4j.py').read())

# 2. Usar Spark normalmente
df = spark.range(10)
df.show()

# 3. Ler dados do MinIO
df = spark.read.parquet("s3a://govbr/bronze/ibge/municipios/")
df.show(5)

# 4. Quando terminar, parar Spark (opcional)
# spark.stop()
```

## 🔗 Arquivos Relacionados

- `fix_spark_py4j.py` - Script principal de correção
- `FIX_PY4J_ERROR.ipynb` - Notebook de correção
- `configurar_spark.py` - Script de configuração padrão (atualizado)
- `CONFIGURAR_SPARK.ipynb` - Notebook de configuração padrão

## 📞 Suporte

Se o problema persistir após seguir todos os passos:

1. Verifique os logs completos do container
2. Verifique a versão do Spark: `spark.version`
3. Verifique a versão do Java: `java -version`
4. Verifique a memória disponível no sistema
