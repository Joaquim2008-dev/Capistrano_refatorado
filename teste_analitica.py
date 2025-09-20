import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import sys
from pathlib import Path
from unidecode import unidecode
from datetime import datetime, timedelta

# Adicionar path do projeto
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from data.data_loader import carregar_e_processar_dados, filtrar_sergipe
from utils.text_processing import padronizar_reu, padronizar_competencia, categorizar_tipo_processo, normalizar_profissao
from utils.calculations import calcular_idade_processos, calcular_idade_clientes
from components.filters import aplicar_filtros_temporais


from pages.analises.Analise_visao_geral import visao_geral
from pages.analises.analise_visao_temporal import analise_temporal
from pages.analises.analise_visao_Réus import analise_reus_procedencia
from pages.analises.analise_cliente import analise_cliente
from pages.analises.analise_profissões import analise_profissoes
from pages.analises.analise_prospectores import analise_prospectors
# =====================================
# CONFIGURAÇÃO DE FILTRO DE ANO
# =====================================
# Descomente UMA das opções abaixo:

# OPÇÃO 1: VERSÃO COMPLETA (todos os anos)
FILTRO_ANO_ATIVO = False
ANO_FILTRO = None

# OPÇÃO 2: VERSÃO APENAS 2025 
# FILTRO_ANO_ATIVO = True
# ANO_FILTRO = 2025

# =====================================

def aplicar_filtro_configurado(df):
    """Aplica filtro de ano baseado na configuração acima"""
    if not FILTRO_ANO_ATIVO or ANO_FILTRO is None:
        return df
    
    if 'data_convertida' in df.columns:
        df_filtrado = df[df['data_convertida'].dt.year == ANO_FILTRO].copy()
        return df_filtrado
    elif 'data' in df.columns:
        # Se ainda não converteu a data
        df['data_convertida'] = pd.to_datetime(df['data'], errors='coerce')
        df_filtrado = df[df['data_convertida'].dt.year == ANO_FILTRO].copy()
        return df_filtrado
    
    return df


def preparar_dados_analise(df_sergipe):
    """Prepara dados específicos para análise"""
    df_analise = df_sergipe.copy()

    # 1. Calcular idades de forma mais robusta
    try:
        df_analise = calcular_idade_processos(df_analise)
    except Exception as e:
        print(f"Erro ao calcular idade dos processos: {e}")
        # Fallback manual
        if 'data' in df_analise.columns:
            try:
                df_analise['data_convertida'] = pd.to_datetime(
                    df_analise['data'], errors='coerce')
                hoje = pd.Timestamp('now')
                df_analise['idade_processo_dias'] = (
                    hoje - df_analise['data_convertida']).dt.days
                df_analise['idade_processo_anos'] = df_analise['idade_processo_dias'] / 365.25
            except:
                df_analise['idade_processo_anos'] = None

    try:
        df_analise = calcular_idade_clientes(df_analise)
    except Exception as e:
        print(f"Erro ao calcular idade dos clientes: {e}")
        df_analise['idade_cliente_anos'] = None

    # 2. Normalizar réus
    if 'reu' in df_analise.columns:
        try:
            df_analise['reu_ajustado'] = df_analise['reu'].apply(
                padronizar_reu)
        except:
            df_analise['reu_ajustado'] = df_analise['reu']

    # 3. Normalizar competência
    if 'competencia' in df_analise.columns:
        try:
            df_analise['competencia_ajustada'] = df_analise['competencia'].apply(
                padronizar_competencia)
        except:
            df_analise['competencia_ajustada'] = df_analise['competencia']

    # 4. Normalizar profissão com nova função robusta
    if 'profissaoTexto' in df_analise.columns:
        try:
            # Primeiro aplicar normalização básica
            df_analise['profissao_basica'] = df_analise['profissaoTexto'].apply(
                lambda x: unidecode(str(x).upper().strip()) if pd.notna(
                    x) and str(x).strip() != '' else 'NÃO INFORMADO'
            )

            # Depois aplicar normalização avançada
            df_analise['profissao_normalizada'] = df_analise['profissao_basica'].apply(
                normalizar_profissao)

        except Exception as e:
            print(f"Erro ao normalizar profissões: {e}")
            df_analise['profissao_normalizada'] = df_analise['profissaoTexto']

    # 5. Categorizar tipos
    if 'tipoProcesso' in df_analise.columns:
        try:
            df_analise['tipoPrincipal'] = df_analise['tipoProcesso'].apply(
                categorizar_tipo_processo)
        except:
            df_analise['tipoPrincipal'] = 'OUTROS'

    return df_analise



def mostrar_kpis_principais(df_analise):
    """Mostra KPIs principais com cards customizados"""
    # APLICAR FILTRO AQUI TAMBÉM
    df_analise = aplicar_filtro_configurado(df_analise)

    # CSS para os cards
    st.markdown("""
        <style>
        .kpi-card {
            background-color: #062e6f; /* Azul escuro (mesmo de Analise_visao_geral) */
            padding: 20px;
            border-radius: 10px;
            text-align: center;
            height: 120px;
            display: flex;
            flex-direction: column;
            justify-content: center;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .kpi-title {
            color: rgba(255, 255, 255, 0.95);
            font-size: 14px;
            font-weight: 500;
            margin-bottom: 8px;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }
        .kpi-value {
            color: white;
            font-size: 28px;
            font-weight: 700;
            margin: 0;
        }
        </style>
    """, unsafe_allow_html=True)

    # st.markdown("---")

    # Calcular valores dos KPIs
    # KPI 1: Idade Média Processos
    if 'idade_processo_anos' in df_analise.columns:
        idade_media_processos = df_analise['idade_processo_anos'].mean()
        kpi1_value = f"{idade_media_processos:.1f} anos" if pd.notna(
            idade_media_processos) else "N/A"
    else:
        kpi1_value = "N/A"

    # KPI 2: Idade Média Clientes
    if 'idade_cliente_anos' in df_analise.columns:
        idade_media_clientes = df_analise['idade_cliente_anos'].mean()
        kpi2_value = f"{idade_media_clientes:.1f} anos" if pd.notna(
            idade_media_clientes) else "N/A"
    else:
        kpi2_value = "N/A"

    # KPI 3: Processos no Período
    total_processos_periodo = len(df_analise)
    kpi3_value = f"{total_processos_periodo:,}"

    # KPI 4: % com Prospector
    if 'prospector' in df_analise.columns:
        com_prospector = df_analise['prospector'].notna().sum()
        percentual_prospector = (
            com_prospector / len(df_analise) * 100) if len(df_analise) > 0 else 0
        kpi4_value = f"{percentual_prospector:.1f}%"
    else:
        kpi4_value = "N/A"

    # Criar colunas para os cards
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-title">Idade Média Processos</div>
                <div class="kpi-value">{kpi1_value}</div>
            </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-title">Idade Média Clientes</div>
                <div class="kpi-value">{kpi2_value}</div>
            </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-title">Processos no Período</div>
                <div class="kpi-value">{kpi3_value}</div>
            </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-title">% com Prospector</div>
                <div class="kpi-value">{kpi4_value}</div>
            </div>
        """, unsafe_allow_html=True)

def pagina_visao_analitica():
    """Página de análise detalhada dos processos"""
    
    # CSS customizado para reduzir espaços
    st.markdown("""
        <style>
        /* OPÇÃO 1: Reduzir padding superior do container principal */
        .block-container {
            padding-top: 3rem !important;
            padding-bottom: 0rem !important;
        }

    
        </style>
    """, unsafe_allow_html=True)

    # Subtítulo com margem negativa para aproximar do topo
    if FILTRO_ANO_ATIVO and ANO_FILTRO:
        st.markdown(
            f"<p style='font-size: 18px; margin-top: -3rem !important;'>Análises detalhadas - Ano {ANO_FILTRO}</p>", unsafe_allow_html=True)
    else:
        st.markdown("<p style='font-size: 18px; margin-top: -3rem !important;'>Análises detalhadas sobre perfil, idade e características dos processos</p>", unsafe_allow_html=True)
    
    # Carregar e preparar dados
    df = carregar_e_processar_dados()
    if df is None:
        st.error("Erro ao carregar dados das APIs")
        st.stop()
    
    df_sergipe = filtrar_sergipe(df)
    if df_sergipe is None or len(df_sergipe) == 0:
        st.warning("Nenhum processo encontrado em Sergipe")
        st.stop()
    
    # APLICAR FILTRO CONFIGURADO
    df_sergipe = aplicar_filtro_configurado(df_sergipe)
    
    if len(df_sergipe) == 0:
        st.warning(f"Nenhum processo encontrado em Sergipe para {ANO_FILTRO}")
        st.stop()
    
    # Preparar dados para análise
    df_analise = preparar_dados_analise(df_sergipe)
    
    # FILTROS - OCULTAR SE FILTRO DE ANO ATIVO
    if FILTRO_ANO_ATIVO and ANO_FILTRO:
        # Não mostrar filtros, apenas informação
        df_filtrado = df_analise  # Usar dados sem filtros adicionais
    else:
        # Mostrar filtros normais
        df_filtrado = aplicar_filtros_temporais(df_analise)
    
    
    # KPIs
    mostrar_kpis_principais(df_filtrado)
    
    # Adicionar espaço entre KPIs e abas
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Abas - VOLTAR PARA O PADRÃO SIMPLES
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "📊 Visão Geral",
        "📈 Análise Temporal", 
        "⚖️ Réus & Competência", 
        "👥 Perfil dos Clientes", 
        "💼 Profissões",
        "🎯 Prospectores"
    ])


    with tab1:
        visao_geral(df_filtrado, aplicar_filtro_configurado)
    
    with tab2:
        analise_temporal(df_filtrado)
    
    with tab3:
        analise_reus_procedencia(df_filtrado)
    
    with tab4:
        analise_cliente(df_filtrado)
    
    with tab5:
        analise_profissoes(df_filtrado, aplicar_filtro_configurado)
    
    with tab6:
        analise_prospectors(df_filtrado, aplicar_filtro_configurado)
