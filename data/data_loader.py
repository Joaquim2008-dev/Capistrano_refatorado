# data/data_loader.py
import streamlit as st
import pandas as pd
import sys
import os
from pathlib import Path
from unidecode import unidecode

# Adicionar path da API se necessário
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))
sys.path.append(str(project_root / "api"))

# Importar suas funções da API
try:
    from api.db_api import baixar_dados_processos, baixar_dados_clientes
    API_DISPONIVEL = True
except ImportError as e:
    API_DISPONIVEL = False

# REMOVER @st.cache_data do nível do módulo
def carregar_e_processar_dados():
    """Carrega dados das APIs e combina processos e clientes"""
    
    # Aplicar cache apenas quando streamlit está rodando
    @st.cache_data(ttl=3600)  # Cache por 1 hora
    def _carregar_dados_cached():
        if not API_DISPONIVEL:
            return None
        
        try:
            # Baixar dados
            df_processos = baixar_dados_processos()
            df_clientes = baixar_dados_clientes()
            
            if df_processos is None or df_clientes is None:
                return None
            
            # Fazer merge dos dados
            df = df_processos.merge(df_clientes, on='idCliente', how='left', suffixes=('', '_cliente'))
            
            return df
            
        except Exception as e:
            st.error(f"Erro ao carregar dados: {e}")
            return None
    
    return _carregar_dados_cached()

def corrigir_municipios(nome):
    """Corrige o nome dos municípios com base em regras específicas"""
    if pd.isna(nome):
        return ''
    
    nome_lower = unidecode(str(nome).lower())
    
    if 'socorro' in nome_lower or 'socoro' in nome_lower:
        return 'NOSSA SENHORA DO SOCORRO'
    elif 'itaporanga' in nome_lower:
        return "ITAPORANGA D'AJUDA"
    elif 'barra' in nome_lower and 'coqu' in nome_lower:
        return 'BARRA DOS COQUEIROS'
    elif 'japarat' in nome_lower:
        return 'JAPARATUBA'
    elif 'sao cristovao' in nome_lower or 'cristovao' in nome_lower or 'sao cris' in nome_lower:
        return 'SAO CRISTOVAO'
    elif 'neopolois' in nome_lower or 'neopolis' in nome_lower:
        return 'NEOPOLIS'
    elif 'maynard' in nome_lower:
        return 'GENERAL MAYNARD'
    elif 'santa rosa' in nome_lower:
        return 'SANTA ROSA DE LIMA'
    elif 'aracau' in nome_lower or 'aracaiu' in nome_lower:
        return 'ARACAJU'
    elif 'das flores' in nome_lower:
        return 'ILHA DAS FLORES'
    elif 'senhora apar' in nome_lower:
        return 'NOSSA SENHORA APARECIDA'
    elif 'aquibada' in nome_lower:
        return 'AQUIDABA'
    elif 'porto' in nome_lower and 'folha' in nome_lower:
        return 'PORTO DA FOLHA'
    elif 'propria' in nome_lower:
        return 'PROPRIA'
    elif 'tobias' in nome_lower:
        return 'TOBIAS BARRETO'
    elif 'estancia' in nome_lower:
        return 'ESTANCIA'
    elif 'lagarto' in nome_lower:
        return 'LAGARTO'
    elif 'itabaiana' in nome_lower and 'inha' not in nome_lower:
        return 'ITABAIANA'
    elif 'simao' in nome_lower:
        return 'SIMAO DIAS'
    elif 'caninde' in nome_lower:
        return 'CANINDE DE SAO FRANCISCO'
    
    return nome.upper()

def filtrar_sergipe(df):
    """Filtra apenas registros de Sergipe com correção de nomes"""
    if df is None or 'cidade' not in df.columns:
        return None
    
    # Lista de cidades de Sergipe
    cidades_sergipe = [
        'AMPARO DE SAO FRANCISCO', 'AQUIDABA', 'ARACAJU', 'ARAUA',
        'AREIA BRANCA', 'BARRA DOS COQUEIROS', 'BOQUIM', 'BREJO GRANDE',
        'CAMPO DO BRITO', 'CANHOBA', 'CANINDE DE SAO FRANCISCO', 'CAPELA',
        'CARIRA', 'CARMOPOLIS', 'CEDRO DE SAO JOAO', 'CRISTINAPOLIS', 'CUMBE',
        'DIVINA PASTORA', 'ESTANCIA', 'FEIRA NOVA', 'FREI PAULO', 'GARARU',
        'GENERAL MAYNARD', 'GRACHO CARDOSO', 'ILHA DAS FLORES', 'INDIAROBA',
        'ITABAIANA', 'ITABAIANINHA', 'ITABI', "ITAPORANGA D'AJUDA", 'JAPARATUBA',
        'JAPOATA', 'LAGARTO', 'LARANJEIRAS', 'MACAMBIRA', 'MALHADA DOS BOIS',
        'MALHADOR', 'MARUIM', 'MOITA BONITA', 'MONTE ALEGRE DE SERGIPE',
        'MURIBECA', 'NEOPOLIS', 'NOSSA SENHORA APARECIDA', 'NOSSA SENHORA DA GLORIA',
        'NOSSA SENHORA DAS DORES', 'NOSSA SENHORA DE LOURDES', 'NOSSA SENHORA DO SOCORRO',
        'PACATUBA', 'PEDRA MOLE', 'PEDRINHAS', 'PINHAO',
        'PIRAMBU', 'POCO REDONDO', 'POCO VERDE', 'PORTO DA FOLHA',
        'PROPRIA', 'RIACHAO DO DANTAS', 'RIACHUELO', 'RIBEIROPOLIS',
        'ROSARIO DO CATETE', 'SALGADO', 'SANTA LUZIA DO ITANHY', 'SANTA ROSA DE LIMA',
        'SANTANA DO SAO FRANCISCO', 'SANTO AMARO DAS BROTAS', 'SAO CRISTOVAO',
        'SAO DOMINGOS', 'SAO FRANCISCO', 'SAO MIGUEL DO ALEIXO', 'SIMAO DIAS',
        'SIRIRI', 'TELHA', 'TOBIAS BARRETO', 'TOMAR DO GERU', 'UMBAUBA'
    ]
    
    # Normalizar e corrigir nomes
    df_clean = df.dropna(subset=['cidade']).copy()
    df_clean['cidade_upper'] = df_clean['cidade'].str.upper().str.strip()
    
    # Aplicar correção de nomes
    df_clean['cidade_upper_corrigido'] = df_clean['cidade_upper'].apply(corrigir_municipios)
    
    # Filtrar apenas processos ativos
    df_clean = df_clean[df_clean['status'] == 'Ativo'].copy()
    
    # Filtrar cidades de Sergipe usando nomes corrigidos
    df_sergipe = df_clean[df_clean['cidade_upper_corrigido'].isin(cidades_sergipe)]
    
    # Renomear para usar na função do mapa
    df_sergipe['cidade_upper'] = df_sergipe['cidade_upper_corrigido']
    
    return df_sergipe