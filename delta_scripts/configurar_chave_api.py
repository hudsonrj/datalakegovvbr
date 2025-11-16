#!/usr/bin/env python3
"""
Script para configurar a chave API - permite informar o nome da variável de ambiente
"""

import os
import sys

print("=" * 80)
print("🔑 CONFIGURAR CHAVE API DO PORTAL DA TRANSPARÊNCIA")
print("=" * 80)

print("\n💡 Qual é o nome da variável de ambiente que contém sua chave API?")
print("\nOpções comuns:")
print("  - PORTAL_TRANSPARENCIA_API_KEY")
print("  - TRANSPARENCIA_API_KEY")
print("  - PORTAL_API_KEY")
print("  - API_KEY")
print("  - Outro nome (informe)")

# Verificar todas as variáveis de ambiente
print("\n📋 Variáveis de ambiente disponíveis (contendo 'API', 'KEY', 'PORTAL', 'TRANSPARENCIA'):")
env_vars = {k: v for k, v in os.environ.items() 
            if any(term in k.upper() for term in ['API', 'KEY', 'PORTAL', 'TRANSPARENCIA'])}

if env_vars:
    for key in sorted(env_vars.keys()):
        value = env_vars[key]
        if len(value) > 20:
            masked = value[:10] + "..." + value[-10:]
        else:
            masked = value
        print(f"  {key}: {masked}")
else:
    print("  Nenhuma variável encontrada")

print("\n" + "=" * 80)
print("💡 INSTRUÇÕES")
print("=" * 80)

print("\n1. Se sua chave está em uma variável de ambiente:")
print("   - O script já tenta ler automaticamente")
print("   - Nomes suportados: PORTAL_TRANSPARENCIA_API_KEY, API_KEY, etc.")
print("\n2. Se não está em variável de ambiente:")
print("   - Adicione no docker-compose.yml na seção 'environment'")
print("   - Ou exporte antes de executar:")
print("     export PORTAL_TRANSPARENCIA_API_KEY='sua_chave_aqui'")
print("\n3. Para testar se a chave funciona:")
print("   exec(open('/home/jovyan/work/testar_api_com_chave.py').read())")

print("\n" + "=" * 80)
