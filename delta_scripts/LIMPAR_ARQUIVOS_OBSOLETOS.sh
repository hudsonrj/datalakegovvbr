#!/bin/bash
# Script para limpar arquivos obsoletos e duplicados

echo "🧹 Limpando arquivos obsoletos..."

# Arquivos .jovyan (cópias de teste)
rm -f *.jovyan
rm -f *.ipynb.jovyan
rm -f *.md.jovyan

# Cópias duplicadas
rm -f *COPI*.ipynb
rm -f *COPI*.py

# Arquivos antigos de setup (substituídos por CONFIGURAR_SPARK)
rm -f 00_SPARK_SETUP.ipynb
rm -f SPARK_SETUP.ipynb
rm -f notebook_spark_setup.ipynb
rm -f spark_setup_fixed.py

# Arquivos de setup antigos
rm -f setup_delta_simple.py
rm -f delta_setup.py
rm -f delta_setup_spark.py

# Arquivos de teste antigos
rm -f test_delta_correto.py
rm -f test_delta_lake.py

# Guias duplicados (manter apenas GUIA_SPARK.md)
rm -f GUIA_SPARK_SETUP.md
rm -f README_SPARK_SETUP.md

# Notebook antigo de início (substituído por CONFIGURAR_SPARK)
rm -f 🚀_INICIE_AQUI_SPARK.ipynb

echo "✅ Limpeza concluída!"
echo ""
echo "Arquivos mantidos (principais):"
echo "  ✅ CONFIGURAR_SPARK.ipynb - Notebook principal"
echo "  ✅ configurar_spark.py - Script principal"
echo "  ✅ EXEMPLO_01_BRONZE.ipynb - Exemplo Bronze"
echo "  ✅ EXEMPLO_02_PRATA.ipynb - Exemplo Prata"
echo "  ✅ EXEMPLO_03_OURO.ipynb - Exemplo Ouro"
echo "  ✅ DEMO_APRESENTACAO.ipynb - Demo completo"
echo "  ✅ GUIA_SPARK.md - Guia rápido"
