#!/bin/bash
# Script para iniciar Delta Lake com GovBR

echo "=========================================="
echo "DELTA LAKE - GOVBR"
echo "=========================================="

# Verificar se Docker está instalado
if ! command -v docker &> /dev/null; then
    echo "❌ Docker não está instalado. Por favor, instale Docker primeiro."
    exit 1
fi

# Verificar se docker-compose está instalado
if ! command -v docker-compose &> /dev/null; then
    echo "❌ docker-compose não está instalado. Por favor, instale docker-compose primeiro."
    exit 1
fi

echo ""
echo "Escolha uma opção:"
echo "1) Iniciar Jupyter com Delta Lake (recomendado - mais simples)"
echo "2) Iniciar Spark completo com Delta Lake (mais recursos)"
echo ""
read -p "Opção (1 ou 2): " opcao

case $opcao in
    1)
        echo ""
        echo "🚀 Iniciando Jupyter com Delta Lake..."
        docker-compose -f docker-compose-simple.yml up -d
        
        echo ""
        echo "⏳ Aguardando container iniciar..."
        sleep 5
        
        echo ""
        echo "✅ Container iniciado!"
        echo ""
        echo "📊 Acesse Jupyter Lab em: http://localhost:8889"
        echo ""
        echo "📝 Para converter Parquet em Delta Lake, execute no Jupyter:"
        echo "   exec(open('/home/jovyan/work/delta_setup_spark.py').read())"
        echo ""
        echo "💡 Ou use o notebook: notebooks/delta_lake_queries.ipynb"
        ;;
    2)
        echo ""
        echo "🚀 Iniciando Spark completo com Delta Lake..."
        docker-compose up -d
        
        echo ""
        echo "⏳ Aguardando containers iniciarem..."
        sleep 10
        
        echo ""
        echo "✅ Containers iniciados!"
        echo ""
        echo "📊 Acesse:"
        echo "   - Spark UI: http://localhost:8080"
        echo "   - Jupyter Lab: http://localhost:8889"
        echo ""
        echo "📝 Para converter Parquet em Delta Lake:"
        echo "   docker exec -it govbr-delta-lake python /opt/spark/work-dir/delta_setup.py"
        ;;
    *)
        echo "❌ Opção inválida"
        exit 1
        ;;
esac

echo ""
echo "Para parar os containers:"
echo "   docker-compose down"
echo ""
