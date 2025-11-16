#!/usr/bin/env python3
"""
Script para testar os notebooks criados
Este script pode ser executado dentro do ambiente Jupyter
"""

import json
import sys

def testar_notebook(notebook_path):
    """Testa se um notebook pode ser executado"""
    print(f"\n{'='*80}")
    print(f"Testando: {notebook_path}")
    print(f"{'='*80}")
    
    try:
        with open(notebook_path, 'r', encoding='utf-8') as f:
            notebook = json.load(f)
        
        print(f"✅ Notebook carregado: {len(notebook['cells'])} células")
        
        # Verificar estrutura
        tipos_celulas = {}
        for cell in notebook['cells']:
            tipo = cell['cell_type']
            tipos_celulas[tipo] = tipos_celulas.get(tipo, 0) + 1
        
        print(f"   • Tipos de células:")
        for tipo, count in tipos_celulas.items():
            print(f"     - {tipo}: {count}")
        
        # Verificar se tem código Python
        codigo_cells = [c for c in notebook['cells'] if c['cell_type'] == 'code']
        print(f"   • Células de código: {len(codigo_cells)}")
        
        # Verificar imports principais
        imports_encontrados = set()
        for cell in codigo_cells:
            source = ''.join(cell['source'])
            if 'import' in source:
                for line in source.split('\n'):
                    if 'import' in line and ('pandas' in line or 'minio' in line or 'normalizar' in line):
                        imports_encontrados.add(line.strip())
        
        if imports_encontrados:
            print(f"   • Imports principais encontrados:")
            for imp in sorted(imports_encontrados)[:5]:
                print(f"     - {imp}")
        
        return True
        
    except FileNotFoundError:
        print(f"❌ Arquivo não encontrado: {notebook_path}")
        return False
    except json.JSONDecodeError as e:
        print(f"❌ Erro ao ler JSON: {e}")
        return False
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    notebooks = [
        'notebook_normalizacao_enderecos_prata.ipynb',
        'notebook_ranking_enderecos_ouro.ipynb'
    ]
    
    print("="*80)
    print("TESTE DE NOTEBOOKS")
    print("="*80)
    
    resultados = []
    for notebook in notebooks:
        resultado = testar_notebook(notebook)
        resultados.append((notebook, resultado))
    
    print(f"\n{'='*80}")
    print("RESUMO")
    print(f"{'='*80}")
    
    for notebook, resultado in resultados:
        status = "✅ OK" if resultado else "❌ ERRO"
        print(f"{status}: {notebook}")
    
    todos_ok = all(r for _, r in resultados)
    
    if todos_ok:
        print(f"\n✅ Todos os notebooks estão válidos!")
        print(f"\n📝 Próximos passos:")
        print(f"   1. Abra o Jupyter Lab")
        print(f"   2. Execute o notebook_normalizacao_enderecos_prata.ipynb")
        print(f"   3. Execute o notebook_ranking_enderecos_ouro.ipynb")
    else:
        print(f"\n❌ Alguns notebooks têm problemas")
        sys.exit(1)
