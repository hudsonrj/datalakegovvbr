#!/usr/bin/env python3
"""
Teste para verificar se conseguimos obter dados pessoais (endereço, email, telefone) por CPF
"""

import requests
import json
import pandas as pd

# Configurações
PORTAL_TRANSPARENCIA_API_KEY = "2c56919ba91b8c1b13473dcef43fb031"
transparency_url = "https://api.portaldatransparencia.gov.br/api-de-dados"

headers = {
    'chave-api-dados': PORTAL_TRANSPARENCIA_API_KEY,
    'Accept': 'application/json'
}

CPF = "03388984760"

print("=" * 100)
print("🔍 TESTE: Busca de Dados Pessoais por CPF")
print("=" * 100)
print(f"CPF Testado: {CPF[:3]}.{CPF[3:6]}.{CPF[6:9]}-{CPF[9:]}")
print("=" * 100)

# Testar diferentes endpoints que podem conter dados pessoais
endpoints_teste = [
    {
        'nome': 'Servidores Públicos',
        'endpoint': '/servidores',
        'params': {'cpf': CPF, 'mesAnoReferencia': '202411', 'pagina': 1},
        'campos_esperados': ['nome', 'cpf', 'cargo', 'orgao', 'endereco', 'email', 'telefone']
    },
    {
        'nome': 'Bolsa Família por CPF',
        'endpoint': '/bolsa-familia-por-cpf-ou-nis',
        'params': {'cpfOuNis': CPF, 'mesAno': '202411', 'pagina': 1},
        'campos_esperados': ['nome', 'cpf', 'endereco', 'municipio']
    },
    {
        'nome': 'CEIS',
        'endpoint': '/ceis',
        'params': {'cpfOuCnpj': CPF, 'pagina': 1},
        'campos_esperados': ['nome', 'cpf', 'endereco', 'telefone']
    },
    {
        'nome': 'CNEP',
        'endpoint': '/cnep',
        'params': {'cpfOuCnpj': CPF, 'pagina': 1},
        'campos_esperados': ['nome', 'cpf', 'endereco']
    }
]

resultados_detalhados = {}

for teste in endpoints_teste:
    print(f"\n{'='*100}")
    print(f"📋 Testando: {teste['nome']}")
    print(f"{'='*100}")
    
    try:
        response = requests.get(
            f"{transparency_url}{teste['endpoint']}",
            headers=headers,
            params=teste['params'],
            timeout=30
        )
        
        print(f"Status HTTP: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            if data and len(data) > 0:
                primeiro_registro = data[0] if isinstance(data, list) else data
                
                print(f"\n✅ Dados encontrados!")
                print(f"Total de registros: {len(data) if isinstance(data, list) else 1}")
                
                # Analisar estrutura do JSON
                print(f"\n📊 Estrutura do JSON:")
                print(f"Tipo: {type(primeiro_registro)}")
                
                if isinstance(primeiro_registro, dict):
                    print(f"Chaves disponíveis: {list(primeiro_registro.keys())[:20]}")
                    
                    # Procurar por campos de dados pessoais
                    print(f"\n🔍 Buscando campos de dados pessoais:")
                    
                    campos_encontrados = {}
                    campos_nao_encontrados = []
                    
                    # Função recursiva para buscar campos
                    def buscar_campos(obj, prefixo=""):
                        campos = {}
                        if isinstance(obj, dict):
                            for key, value in obj.items():
                                chave_completa = f"{prefixo}.{key}" if prefixo else key
                                
                                # Verificar se é um campo de dados pessoais
                                if any(palavra in key.lower() for palavra in ['nome', 'endereco', 'email', 'telefone', 'logradouro', 'cep', 'bairro', 'cidade', 'municipio', 'uf', 'estado']):
                                    if value and str(value).strip() and str(value) != 'None':
                                        campos[chave_completa] = str(value)[:100]  # Limitar tamanho
                                
                                # Continuar buscando recursivamente
                                if isinstance(value, (dict, list)):
                                    campos.update(buscar_campos(value, chave_completa))
                        elif isinstance(obj, list) and len(obj) > 0:
                            campos.update(buscar_campos(obj[0], prefixo))
                        
                        return campos
                    
                    campos_pessoais = buscar_campos(primeiro_registro)
                    
                    if campos_pessoais:
                        print(f"\n✅ CAMPOS DE DADOS PESSOAIS ENCONTRADOS:")
                        for campo, valor in campos_pessoais.items():
                            # Mascarar dados sensíveis
                            if 'cpf' in campo.lower():
                                valor_mascarado = f"***.{valor[-6:-3]}.{valor[-3:]}-{valor[-2:]}" if len(valor) >= 11 else valor
                            elif 'email' in campo.lower():
                                partes = valor.split('@')
                                if len(partes) == 2:
                                    valor_mascarado = f"{partes[0][:2]}***@{partes[1]}"
                                else:
                                    valor_mascarado = valor
                            else:
                                valor_mascarado = valor
                            
                            print(f"   • {campo}: {valor_mascarado}")
                    else:
                        print(f"\n⚠️  NENHUM campo de dados pessoais encontrado")
                    
                    # Mostrar estrutura completa (limitado)
                    print(f"\n📄 Estrutura completa do primeiro registro (primeiras 30 linhas):")
                    json_str = json.dumps(primeiro_registro, indent=2, ensure_ascii=False, default=str)
                    linhas = json_str.split('\n')
                    print('\n'.join(linhas[:30]))
                    if len(linhas) > 30:
                        mais_linhas = len(linhas) - 30
                        print(f"\n... (mais {mais_linhas} linhas)")
                    
                    resultados_detalhados[teste['nome']] = {
                        'status': 'success',
                        'campos_pessoais_encontrados': list(campos_pessoais.keys()),
                        'total_campos_pessoais': len(campos_pessoais),
                        'estrutura': list(primeiro_registro.keys())[:20]
                    }
                else:
                    print(f"⚠️  Formato de dados não reconhecido")
                    resultados_detalhados[teste['nome']] = {
                        'status': 'unknown_format',
                        'tipo': str(type(primeiro_registro))
                    }
            else:
                print(f"⚠️  Nenhum dado retornado")
                resultados_detalhados[teste['nome']] = {
                    'status': 'empty'
                }
        else:
            print(f"❌ Erro HTTP {response.status_code}")
            print(f"Resposta: {response.text[:200]}")
            resultados_detalhados[teste['nome']] = {
                'status': 'error',
                'code': response.status_code
            }
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        resultados_detalhados[teste['nome']] = {
            'status': 'exception',
            'error': str(e)
        }

# RESUMO FINAL
print("\n" + "=" * 100)
print("📊 RESUMO DA ANÁLISE")
print("=" * 100)

print("\n🔍 RESULTADO DA BUSCA POR DADOS PESSOAIS:")
print("-" * 100)

total_campos_encontrados = 0
for nome, resultado in resultados_detalhados.items():
    if resultado.get('status') == 'success':
        campos = resultado.get('campos_pessoais_encontrados', [])
        total_campos_encontrados += len(campos)
        print(f"\n{nome}:")
        if campos:
            print(f"   ✅ {len(campos)} campo(s) encontrado(s): {', '.join(campos[:5])}")
        else:
            print(f"   ⚠️  Nenhum campo de dados pessoais encontrado")

print(f"\n📈 Total de campos de dados pessoais encontrados: {total_campos_encontrados}")

print("\n" + "=" * 100)
print("💡 CONCLUSÃO")
print("=" * 100)

if total_campos_encontrados == 0:
    print("""
❌ RESULTADO: NÃO é possível obter dados pessoais completos (endereço, email, telefone) 
   através das APIs públicas do Portal da Transparência.

📋 MOTIVOS:
   1. Proteção de Privacidade (LGPD)
   2. Dados pessoais sensíveis não são expostos publicamente
   3. APIs retornam apenas informações de transparência pública
   4. Mesmo com CPF, apenas dados agregados são retornados

✅ O QUE ESTÁ DISPONÍVEL:
   • Nome (parcial ou mascarado em alguns casos)
   • CPF (mascarado: ***.***.***-**)
   • Informações de benefícios (valores, períodos)
   • Informações de sanções (tipos, datas, órgãos)
   • Informações de servidores públicos (cargo, órgão - sem endereço completo)

❌ O QUE NÃO ESTÁ DISPONÍVEL:
   • Endereço completo (logradouro, número, CEP)
   • Email pessoal
   • Telefone pessoal
   • Dados de contato completos

💡 ALTERNATIVAS LEGAIS:
   • Consulta na Receita Federal (requer autenticação especial)
   • Consulta em bases autorizadas (com consentimento)
   • APIs privadas com autorização legal específica
    """)
else:
    print(f"""
⚠️  ATENÇÃO: Alguns campos foram encontrados, mas podem estar:
   • Mascarados ou parcialmente ocultos
   • Relacionados apenas a informações públicas
   • Não incluindo dados pessoais completos (endereço, email, telefone)
    """)

print("=" * 100)
