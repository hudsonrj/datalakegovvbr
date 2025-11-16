#!/usr/bin/env python3
"""
Script de teste para validar a geração de massa de dados de cidadãos
Testa com um pequeno número de registros antes de gerar 1 milhão
"""

import sys
sys.path.insert(0, '/data/govbr')

from gerar_massa_cidadaos_bronze import gerar_massa_cidadaos

if __name__ == "__main__":
    print("🧪 TESTE DE GERAÇÃO DE DADOS DE CIDADÃOS")
    print("=" * 80)
    print("Gerando 10 cidadãos para teste...")
    print("=" * 80)
    
    # Testar com apenas 10 cidadãos primeiro
    gerar_massa_cidadaos(10)
    
    print("\n" + "=" * 80)
    print("✅ TESTE CONCLUÍDO!")
    print("=" * 80)
    print("\nSe o teste funcionou corretamente, execute:")
    print("  python gerar_massa_cidadaos_bronze.py")
    print("\nPara gerar 1 milhão de cidadãos completos.")
