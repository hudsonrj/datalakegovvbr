#!/usr/bin/env python3
"""
Script para converter scripts Python de ingestão em notebooks Jupyter
"""

import json
import re

def criar_notebook_bronze():
    """Cria notebook Bronze a partir do script Python"""
    
    # Ler script Python
    with open('01_bronze_ingestion.py', 'r') as f:
        script_content = f.read()
    
    cells = []
    
    # Célula 1: Markdown título
    cells.append({
        'cell_type': 'markdown',
        'metadata': {},
        'source': [
            '# 🥉 Camada Bronze - Ingestão de Dados Brutos\n',
            '\n',
            'Este notebook executa a ingestão de dados brutos de APIs governamentais e armazena na camada Bronze em formato Parquet.\n',
            '\n',
            '## Fontes de Dados:\n',
            '- **IBGE**: Municípios, Estados, População\n',
            '- **Portal da Transparência**: Órgãos SIAFI, BPC por Município\n',
            '\n',
            '## Estrutura de Saída:\n',
            '```\n',
            'bronze/\n',
            '├── ibge/\n',
            '│   ├── municipios/dt=YYYYMMDD/data.parquet\n',
            '│   ├── estados/dt=YYYYMMDD/data.parquet\n',
            '│   └── populacao_estados/dt=YYYYMMDD/data.parquet\n',
            '└── portal_transparencia/\n',
            '    ├── orgaos_siafi/dt=YYYYMMDD/data.parquet\n',
            '    └── bpc_municipios/dt=YYYYMMDD/data.parquet\n',
            '```'
        ]
    })
    
    # Célula 2: Instalar dependências
    cells.append({
        'cell_type': 'code',
        'metadata': {},
        'source': ['# Instalar dependências se necessário\n', '!pip install -q requests pandas minio pyarrow']
    })
    
    # Dividir script em seções baseado em comentários
    sections = re.split(r'(# \d+\.|print\(.*\[.*/.*\].*\))', script_content)
    
    current_code = []
    section_num = 0
    
    for i, section in enumerate(sections):
        if section.strip().startswith('#') or 'print(' in section:
            # Nova seção - salvar código anterior e criar markdown
            if current_code:
                cells.append({
                    'cell_type': 'code',
                    'metadata': {},
                    'source': current_code
                })
                current_code = []
            
            # Criar markdown para seção
            if '[1/5]' in section:
                cells.append({
                    'cell_type': 'markdown',
                    'metadata': {},
                    'source': ['## [1/5] Coletando Municípios do Brasil (IBGE)']
                })
            elif '[2/5]' in section:
                cells.append({
                    'cell_type': 'markdown',
                    'metadata': {},
                    'source': ['## [2/5] Coletando Estados do Brasil (IBGE)']
                })
            elif '[3/5]' in section:
                cells.append({
                    'cell_type': 'markdown',
                    'metadata': {},
                    'source': ['## [3/5] Coletando Órgãos SIAFI (Portal da Transparência)']
                })
            elif '[4/5]' in section:
                cells.append({
                    'cell_type': 'markdown',
                    'metadata': {},
                    'source': ['## [4/5] Coletando Dados de BPC (Portal da Transparência)']
                })
            elif '[5/5]' in section:
                cells.append({
                    'cell_type': 'markdown',
                    'metadata': {},
                    'source': ['## [5/5] Coletando População por Estado (IBGE)']
                })
        else:
            # Adicionar código à célula atual
            lines = section.split('\n')
            for line in lines:
                if line.strip() and not line.strip().startswith('#!/usr/bin'):
                    current_code.append(line + '\n')
    
    # Adicionar última célula de código
    if current_code:
        cells.append({
            'cell_type': 'code',
            'metadata': {},
            'source': current_code
        })
    
    # Adicionar célula de resumo
    cells.append({
        'cell_type': 'markdown',
        'metadata': {},
        'source': ['## Resumo da Ingestão']
    })
    
    cells.append({
        'cell_type': 'code',
        'metadata': {},
        'source': [
            '# Listar arquivos Bronze\n',
            'print("\\n" + "=" * 80)\n',
            'print("RESUMO DA INGESTÃO")\n',
            'print("=" * 80)\n',
            '\n',
            'objects = minio_client.list_objects(BUCKET_NAME, prefix="bronze/", recursive=True)\n',
            'bronze_files = list(objects)\n',
            '\n',
            'print(f"\\nTotal de arquivos na camada Bronze: {len(bronze_files)}")\n',
            'total_size = 0\n',
            'for obj in bronze_files:\n',
            '    size_kb = obj.size / 1024\n',
            '    total_size += obj.size\n',
            '    print(f"  📁 {obj.object_name} ({size_kb:.2f} KB)")\n',
            '\n',
            'print(f"\\nTamanho total: {total_size/1024:.2f} KB")\n',
            'print("\\n✅ Ingestão Bronze concluída!")'
        ]
    })
    
    # Criar notebook
    notebook = {
        'cells': cells,
        'metadata': {
            'kernelspec': {
                'display_name': 'Python 3',
                'language': 'python',
                'name': 'python3'
            },
            'language_info': {
                'name': 'python',
                'version': '3.10.0'
            }
        },
        'nbformat': 4,
        'nbformat_minor': 4
    }
    
    # Salvar
    with open('NOTEBOOK_01_BRONZE_INGESTION.ipynb', 'w', encoding='utf-8') as f:
        json.dump(notebook, f, indent=2, ensure_ascii=False)
    
    print("✅ Notebook Bronze criado: NOTEBOOK_01_BRONZE_INGESTION.ipynb")

def criar_notebook_prata():
    """Cria notebook Prata a partir do script Python"""
    # Similar ao Bronze, mas para Prata
    with open('02_prata_transformacao.py', 'r') as f:
        script_content = f.read()
    
    # Dividir em células baseado em seções
    cells = []
    
    # Título
    cells.append({
        'cell_type': 'markdown',
        'metadata': {},
        'source': [
            '# 🔄 Camada Prata - Transformação e Relacionamento\n',
            '\n',
            'Este notebook transforma dados brutos da camada Bronze em estruturas relacionadas prontas para análise.\n',
            '\n',
            '## Processos:\n',
            '1. Leitura dos dados Bronze\n',
            '2. Tratamento e limpeza\n',
            '3. Criação de dimensões e fatos\n',
            '4. Relacionamento entre tabelas'
        ]
    })
    
    # Adicionar código completo em células organizadas
    code_lines = script_content.split('\n')
    current_section = []
    
    for line in code_lines:
        if line.strip().startswith('#') and ('[1/4]' in line or '[2/4]' in line or '[3/4]' in line or '[4/4]' in line):
            if current_section:
                cells.append({
                    'cell_type': 'code',
                    'metadata': {},
                    'source': current_section
                })
                current_section = []
            
            # Adicionar markdown da seção
            if '[1/4]' in line:
                cells.append({
                    'cell_type': 'markdown',
                    'metadata': {},
                    'source': ['## [1/4] Carregando dados da camada Bronze']
                })
            elif '[2/4]' in line:
                cells.append({
                    'cell_type': 'markdown',
                    'metadata': {},
                    'source': ['## [2/4] Tratando e limpando dados']
                })
            elif '[3/4]' in line:
                cells.append({
                    'cell_type': 'markdown',
                    'metadata': {},
                    'source': ['## [3/4] Criando dimensões e relacionamentos']
                })
            elif '[4/4]' in line:
                cells.append({
                    'cell_type': 'markdown',
                    'metadata': {},
                    'source': ['## [4/4] Criando resumo de transformações']
                })
        
        if line.strip() and not line.strip().startswith('#!/usr/bin'):
            current_section.append(line + '\n')
    
    if current_section:
        cells.append({
            'cell_type': 'code',
            'metadata': {},
            'source': current_section
        })
    
    notebook = {
        'cells': cells,
        'metadata': {
            'kernelspec': {'display_name': 'Python 3', 'language': 'python', 'name': 'python3'},
            'language_info': {'name': 'python', 'version': '3.10.0'}
        },
        'nbformat': 4,
        'nbformat_minor': 4
    }
    
    with open('NOTEBOOK_02_PRATA_TRANSFORMACAO.ipynb', 'w', encoding='utf-8') as f:
        json.dump(notebook, f, indent=2, ensure_ascii=False)
    
    print("✅ Notebook Prata criado: NOTEBOOK_02_PRATA_TRANSFORMACAO.ipynb")

def criar_notebook_ouro():
    """Cria notebook Ouro a partir do script Python"""
    with open('03_ouro_enriquecimento.py', 'r') as f:
        script_content = f.read()
    
    cells = []
    
    cells.append({
        'cell_type': 'markdown',
        'metadata': {},
        'source': [
            '# 🏆 Camada Ouro - Enriquecimento e Dados Finais\n',
            '\n',
            'Este notebook enriquece dados da camada Prata com métricas avançadas e análises prontas para consumo.\n',
            '\n',
            '## Processos:\n',
            '1. Leitura dos dados Prata\n',
            '2. Enriquecimento com métricas\n',
            '3. Criação de rankings e classificações\n',
            '4. Agregações regionais'
        ]
    })
    
    code_lines = script_content.split('\n')
    current_section = []
    
    for line in code_lines:
        if line.strip().startswith('#') and ('[1/5]' in line or '[2/5]' in line or '[3/5]' in line or '[4/5]' in line or '[5/5]' in line):
            if current_section:
                cells.append({
                    'cell_type': 'code',
                    'metadata': {},
                    'source': current_section
                })
                current_section = []
            
            if '[1/5]' in line:
                cells.append({
                    'cell_type': 'markdown',
                    'metadata': {},
                    'source': ['## [1/5] Carregando dados da camada Prata']
                })
            elif '[2/5]' in line:
                cells.append({
                    'cell_type': 'markdown',
                    'metadata': {},
                    'source': ['## [2/5] Enriquecendo dimensão de municípios']
                })
            elif '[3/5]' in line:
                cells.append({
                    'cell_type': 'markdown',
                    'metadata': {},
                    'source': ['## [3/5] Enriquecendo dimensão de estados']
                })
            elif '[4/5]' in line:
                cells.append({
                    'cell_type': 'markdown',
                    'metadata': {},
                    'source': ['## [4/5] Criando fato BPC enriquecido']
                })
            elif '[5/5]' in line:
                cells.append({
                    'cell_type': 'markdown',
                    'metadata': {},
                    'source': ['## [5/5] Criando tabelas agregadas para análise']
                })
        
        if line.strip() and not line.strip().startswith('#!/usr/bin'):
            current_section.append(line + '\n')
    
    if current_section:
        cells.append({
            'cell_type': 'code',
            'metadata': {},
            'source': current_section
        })
    
    notebook = {
        'cells': cells,
        'metadata': {
            'kernelspec': {'display_name': 'Python 3', 'language': 'python', 'name': 'python3'},
            'language_info': {'name': 'python', 'version': '3.10.0'}
        },
        'nbformat': 4,
        'nbformat_minor': 4
    }
    
    with open('NOTEBOOK_03_OURO_ENRIQUECIMENTO.ipynb', 'w', encoding='utf-8') as f:
        json.dump(notebook, f, indent=2, ensure_ascii=False)
    
    print("✅ Notebook Ouro criado: NOTEBOOK_03_OURO_ENRIQUECIMENTO.ipynb")

if __name__ == '__main__':
    print("=" * 80)
    print("CRIANDO NOTEBOOKS DE INGESTÃO")
    print("=" * 80)
    
    criar_notebook_bronze()
    criar_notebook_prata()
    criar_notebook_ouro()
    
    print("\n✅ Todos os notebooks criados com sucesso!")
