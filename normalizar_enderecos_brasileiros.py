#!/usr/bin/env python3
"""
Normalizador de Endereços Brasileiros
Normaliza endereços conforme padrão ABNT NBR 14725 e Correios (ECT)

Formato padrão:
[Tipo Logradouro] [Nome Logradouro], [Número] - [Complemento] - [Bairro] - [Município]/[UF] - CEP [CEP]
"""

import re
from typing import Dict, Optional, Tuple

class NormalizadorEndereco:
    """Normaliza endereços brasileiros para o formato padrão"""
    
    # Tipos de logradouro e suas abreviações
    TIPOS_LOGRADOURO = {
        'rua': 'Rua',
        'r.': 'Rua',
        'r ': 'Rua',
        'avenida': 'Avenida',
        'av.': 'Avenida',
        'av ': 'Avenida',
        'praça': 'Praça',
        'pça.': 'Praça',
        'pça ': 'Praça',
        'travessa': 'Travessa',
        'tv.': 'Travessa',
        'tv ': 'Travessa',
        'alameda': 'Alameda',
        'al.': 'Alameda',
        'al ': 'Alameda',
        'estrada': 'Estrada',
        'est.': 'Estrada',
        'est ': 'Estrada',
        'rodovia': 'Rodovia',
        'rod.': 'Rodovia',
        'rod ': 'Rodovia',
        'viela': 'Viela',
        'beco': 'Beco',
        'largo': 'Largo',
        'vila': 'Vila',
        'jardim': 'Jardim',
        'parque': 'Parque',
        'conjunto': 'Conjunto',
        'quadra': 'Quadra',
        'setor': 'Setor',
    }
    
    # Estados brasileiros
    ESTADOS = {
        'AC': 'Acre', 'AL': 'Alagoas', 'AP': 'Amapá', 'AM': 'Amazonas',
        'BA': 'Bahia', 'CE': 'Ceará', 'DF': 'Distrito Federal', 'ES': 'Espírito Santo',
        'GO': 'Goiás', 'MA': 'Maranhão', 'MT': 'Mato Grosso', 'MS': 'Mato Grosso do Sul',
        'MG': 'Minas Gerais', 'PA': 'Pará', 'PB': 'Paraíba', 'PR': 'Paraná',
        'PE': 'Pernambuco', 'PI': 'Piauí', 'RJ': 'Rio de Janeiro', 'RN': 'Rio Grande do Norte',
        'RS': 'Rio Grande do Sul', 'RO': 'Rondônia', 'RR': 'Roraima', 'SC': 'Santa Catarina',
        'SP': 'São Paulo', 'SE': 'Sergipe', 'TO': 'Tocantins'
    }
    
    def __init__(self):
        """Inicializa o normalizador"""
        # Compilar regex para melhor performance
        self.regex_cep = re.compile(r'\b(\d{5})-?(\d{3})\b')
        self.regex_numero = re.compile(r'(?:n[º°]?|N[º°]?|número|Número)\s*:?\s*(\d+)|\b(\d+)\b')
        self.regex_uf = re.compile(r'\b([A-Z]{2})\b')
        self.regex_complemento = re.compile(r'\b(Apto|Apartamento|Sala|Loja|Bloco|Torre|Casa|Sobrado|Galpão)\s*(?:n[º°]?|N[º°]?|número|Número)?\s*:?\s*(\d+[A-Z]?)\b', re.IGNORECASE)
    
    def normalizar_tipo_logradouro(self, tipo: str) -> str:
        """Normaliza o tipo de logradouro"""
        if not tipo:
            return ''
        
        tipo_lower = tipo.lower().strip()
        
        # Verificar se já está normalizado
        if tipo[0].isupper() and tipo_lower in self.TIPOS_LOGRADOURO.values():
            return tipo
        
        # Buscar correspondência
        for abrev, completo in self.TIPOS_LOGRADOURO.items():
            if tipo_lower.startswith(abrev):
                return completo
        
        # Se não encontrou, capitalizar primeira letra
        return tipo.capitalize()
    
    def extrair_cep(self, endereco: str) -> Optional[str]:
        """Extrai e normaliza CEP"""
        match = self.regex_cep.search(endereco)
        if match:
            return f"{match.group(1)}-{match.group(2)}"
        return None
    
    def extrair_numero(self, endereco: str) -> Optional[str]:
        """Extrai número do imóvel"""
        # Tentar padrão com "nº" primeiro
        match = re.search(r'(?:n[º°]|N[º°]|número|Número)\s*:?\s*(\d+)', endereco)
        if match:
            return match.group(1)
        
        # Tentar número após vírgula ou hífen
        # Usar classe de caracteres com hífen escapado ou no final
        match = re.search(r'[,\s-]+(\d{1,5})(?:\s|$|,|/|-)', endereco)
        if match:
            return match.group(1)
        
        return None
    
    def extrair_complemento(self, endereco: str) -> Optional[str]:
        """Extrai complemento do endereço"""
        match = self.regex_complemento.search(endereco)
        if match:
            tipo = match.group(1).capitalize()
            numero = match.group(2)
            return f"{tipo} {numero}"
        return None
    
    def extrair_uf(self, endereco: str) -> Optional[str]:
        """Extrai UF do endereço"""
        # Padrão: /UF ou -UF
        match = re.search(r'[/-]\s*([A-Z]{2})(?:\s|$|CEP|,)', endereco)
        if match:
            uf = match.group(1).upper()
            if uf in self.ESTADOS:
                return uf
        return None
    
    def extrair_municipio(self, endereco: str, uf: Optional[str] = None) -> Optional[str]:
        """Extrai município do endereço"""
        # Padrão: município/UF ou município - UF
        if uf:
            pattern = rf'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s*[/-]\s*{uf}'
        else:
            pattern = r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s*[/-]\s*([A-Z]{{2}})'
        
        match = re.search(pattern, endereco)
        if match:
            municipio = match.group(1).strip()
            # Normalizar para Title Case
            palavras = municipio.split()
            municipio_normalizado = ' '.join([p.capitalize() for p in palavras])
            return municipio_normalizado
        
        return None
    
    def extrair_bairro(self, endereco: str) -> Optional[str]:
        """Extrai bairro do endereço"""
        # Bairro geralmente vem antes do município
        # Padrão: - Bairro - ou , Bairro,
        patterns = [
            r'-\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s*-\s*[A-Z]',  # - Bairro - Município
            r',\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s*,\s*[A-Z]',  # , Bairro, Município
            r'-\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s*,\s*[A-Z]',  # - Bairro, Município
        ]
        
        for pattern in patterns:
            match = re.search(pattern, endereco)
            if match:
                bairro = match.group(1).strip()
                # Normalizar para Title Case
                palavras = bairro.split()
                bairro_normalizado = ' '.join([p.capitalize() for p in palavras])
                return bairro_normalizado
        
        return None
    
    def normalizar(self, endereco: str) -> Dict[str, Optional[str]]:
        """
        Normaliza um endereço brasileiro
        
        Retorna um dicionário com os componentes normalizados
        """
        if not endereco:
            return {}
        
        endereco_limpo = endereco.strip()
        
        # Extrair componentes
        cep = self.extrair_cep(endereco_limpo)
        uf = self.extrair_uf(endereco_limpo)
        municipio = self.extrair_municipio(endereco_limpo, uf)
        bairro = self.extrair_bairro(endereco_limpo)
        complemento = self.extrair_complemento(endereco_limpo)
        numero = self.extrair_numero(endereco_limpo)
        
        # Extrair tipo e nome do logradouro
        # Remover componentes já extraídos
        endereco_sem_componentes = endereco_limpo
        if cep:
            endereco_sem_componentes = re.sub(r'CEP\s*:?\s*\d{5}-?\d{3}', '', endereco_sem_componentes)
        if municipio and uf:
            endereco_sem_componentes = re.sub(rf'{re.escape(municipio)}\s*[/-]\s*{uf}', '', endereco_sem_componentes)
        if bairro:
            endereco_sem_componentes = re.sub(re.escape(bairro), '', endereco_sem_componentes)
        if complemento:
            endereco_sem_componentes = re.sub(re.escape(complemento), '', endereco_sem_componentes)
        if numero:
            endereco_sem_componentes = re.sub(rf'(?:n[º°]|N[º°]|número|Número)?\s*:?\s*{numero}', '', endereco_sem_componentes)
        
        # Extrair tipo e nome
        partes_logradouro = endereco_sem_componentes.split(',')[0].split('-')[0].strip().split(maxsplit=1)
        
        tipo_logradouro = ''
        nome_logradouro = ''
        
        if len(partes_logradouro) >= 1:
            tipo_logradouro = self.normalizar_tipo_logradouro(partes_logradouro[0])
        if len(partes_logradouro) >= 2:
            nome_logradouro = partes_logradouro[1].strip()
            # Normalizar para Title Case
            palavras = nome_logradouro.split()
            nome_logradouro = ' '.join([p.capitalize() for p in palavras])
        
        return {
            'tipo_logradouro': tipo_logradouro,
            'nome_logradouro': nome_logradouro,
            'numero': numero,
            'complemento': complemento,
            'bairro': bairro,
            'municipio': municipio,
            'uf': uf,
            'cep': cep
        }
    
    def formatar_padrao(self, componentes: Dict[str, Optional[str]]) -> str:
        """
        Formata componentes no padrão brasileiro
        
        Formato: [Tipo] [Nome], [Número] - [Complemento] - [Bairro] - [Município]/[UF] - CEP [CEP]
        """
        partes = []
        
        # Logradouro
        logradouro = ''
        if componentes.get('tipo_logradouro'):
            logradouro += componentes['tipo_logradouro']
        if componentes.get('nome_logradouro'):
            if logradouro:
                logradouro += ' ' + componentes['nome_logradouro']
            else:
                logradouro = componentes['nome_logradouro']
        
        if logradouro:
            if componentes.get('numero'):
                partes.append(f"{logradouro}, {componentes['numero']}")
            else:
                partes.append(logradouro)
        
        # Complemento
        if componentes.get('complemento'):
            partes.append(componentes['complemento'])
        
        # Bairro
        if componentes.get('bairro'):
            partes.append(componentes['bairro'])
        
        # Município/UF
        if componentes.get('municipio') and componentes.get('uf'):
            partes.append(f"{componentes['municipio']}/{componentes['uf']}")
        elif componentes.get('municipio'):
            partes.append(componentes['municipio'])
        elif componentes.get('uf'):
            partes.append(componentes['uf'])
        
        # CEP
        if componentes.get('cep'):
            partes.append(f"CEP {componentes['cep']}")
        
        # Juntar com hífens
        return ' - '.join(partes)
    
    def normalizar_completo(self, endereco: str) -> str:
        """
        Normaliza e formata um endereço completo no padrão brasileiro
        """
        componentes = self.normalizar(endereco)
        return self.formatar_padrao(componentes)


# Exemplo de uso
if __name__ == "__main__":
    normalizador = NormalizadorEndereco()
    
    # Exemplos de endereços para normalizar
    exemplos = [
        "Rua das Flores, 123 - Apto 45 - Centro - São Paulo/SP - CEP 01234-567",
        "Av. Paulista, 1000 - Bela Vista - São Paulo/SP - CEP 01310-100",
        "rua augusta, nº 1234 - consolação - são paulo/sp - cep 01305-100",
        "ESTRADA DOS IPÊS, 8690, CENTRO, RIO BRANCO/AC - 88504-431",
        "Praça   Independência,   7963,   Vila Nova,   Belo Horizonte/MG",
    ]
    
    print("=" * 80)
    print("NORMALIZAÇÃO DE ENDEREÇOS BRASILEIROS")
    print("=" * 80)
    
    for exemplo in exemplos:
        print(f"\n📝 Original:")
        print(f"   {exemplo}")
        
        componentes = normalizador.normalizar(exemplo)
        print(f"\n🔍 Componentes extraídos:")
        for chave, valor in componentes.items():
            if valor:
                print(f"   • {chave}: {valor}")
        
        normalizado = normalizador.normalizar_completo(exemplo)
        print(f"\n✅ Normalizado:")
        print(f"   {normalizado}")
        print("-" * 80)
