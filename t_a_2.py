import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import sys
from pathlib import Path
from unidecode import unidecode
from datetime import datetime, timedelta
from style.css import criar_css

# Adicionar path do projeto
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from data.data_loader import carregar_e_processar_dados, filtrar_sergipe
from utils.text_processing import padronizar_reu, padronizar_competencia, categorizar_tipo_processo, normalizar_profissao
from utils.calculations import calcular_idade_processos, calcular_idade_clientes
from components.filters import aplicar_filtros_temporais

#Importar popover_visao_geral
from pages_2.analises_2.popover_visao_geral.A_visao_geral import visao_geral_6
from pages_2.analises_2.popover_visao_geral.kpis_principais import mostrar_kpis_principais

#importar popover_visao_temporal
from pages_2.analises_2.popover_visao_temporal.cards_ho_4 import render_4_cards_temporal, render_graficos_temporal


#import popover_visao_clientes:
from pages_2.analises_2.popover_visao_clientes.perfil_clientes import criar_perfil_cliente
from pages_2.analises_2.popover_visao_clientes.profissoes import analise_profissoes

#import popover_visao_reus_competencia
from pages_2.analises_2.popover_reus_competencia.reus_e_competencia import analise_reus_procedencia, competencia

#import popover_prospectores
from pages_2.analises_2.popover_prospectores.prospectores import analise_prospectors

st.set_page_config(layout='wide')


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



def main():
    """Função principal"""
    
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

    df_analise = aplicar_filtros_temporais(df_analise)
    


    #Análise inicial:

    #Popovers:
    criar_css()

    co1, co2, co3, co4, co5 = st.columns(5)
    with co1:
        with st.popover('Visão Geral', use_container_width=True):
            st.markdown("""
            <div style="
                width: 650px; 
                min-width: 650px; 
                height: 1px; 
                background: transparent; 
                margin: 0; 
                padding: 0;
                overflow: hidden;
            "></div>
            """, unsafe_allow_html=True)


            visao_geral_6(df_analise)

            st.markdown("<br>", unsafe_allow_html=True)

            mostrar_kpis_principais(df_analise)
            
                
    with co2:
        with st.popover("Visão temporal", use_container_width=True):
            st.markdown("""
            <div style="
                width: 650px; 
                min-width: 650px; 
                height: 1px; 
                background: transparent; 
                margin: 0; 
                padding: 0;
                overflow: hidden;
            "></div>
            """, unsafe_allow_html=True)
              
            render_graficos_temporal(df_analise)

    with co3:
        with st.popover("Visão clientes", use_container_width=True):
            st.markdown("""
            <div style="
                width: 800px; 
                min-width: 700px; 
                height: 1px; 
                background: transparent; 
                margin: 0; 
                padding: 0;
                overflow: hidden;
            "></div>
            """, unsafe_allow_html=True)

            tipo_analise = st.selectbox("Escolha o tipo de análise",
                                        ["Perfil dos clientes", "Profissões"])
            
            if tipo_analise == "Perfil dos clientes":
                criar_perfil_cliente(df_analise)


            if tipo_analise == "Profissões":
                analise_profissoes(df_analise)
    
    with co4:
        with st.popover("Competência & Réus", use_container_width=True):
            st.markdown("""
            <div style="
                width: 800px; 
                min-width: 700px; 
                height: 1px; 
                background: transparent; 
                margin: 0; 
                padding: 0;
                overflow: hidden;
            "></div>
            """, unsafe_allow_html=True)

            tipo_analise = st.selectbox("Escolha o tipo de análise",
                                       ['Reús', 'Competência'])
            
            if tipo_analise == 'Reús':

                analise_reus_procedencia(df_analise)
            
            if tipo_analise == 'Competência':

                competencia(df_analise)
        
    with co5:
        with st.popover("Prospectores", use_container_width=True):
            st.markdown("""
            <div style="
                width: 800px; 
                min-width: 700px; 
                height: 1px; 
                background: transparent; 
                margin: 0; 
                padding: 0;
                overflow: hidden;
            "></div>
            """, unsafe_allow_html=True)

            analise_prospectors(df_analise)
              

    st.markdown('---')
    st.markdown("### 📋 Últimos 5 Processos")

    df_filtrado = df_analise
        
    if len(df_filtrado) > 0:
        # Ordenar por data (mais recentes primeiro)
        if 'data_convertida' in df_filtrado.columns:
            df_recentes = df_filtrado.sort_values('data_convertida', ascending=False).head(5)
        else:
            df_recentes = df_filtrado.head(5)
        
        # Preparar dados para a tabela
        tabela_processos = []
        
        for _, row in df_recentes.iterrows():
            # Número do processo
            num_processo = row.get('numeroProcesso', row.get('numero', 'N/A'))
            
            # Data formatada
            if 'data_convertida' in row and pd.notna(row['data_convertida']):
                data_formatada = row['data_convertida'].strftime('%d/%m/%Y')
            else:
                data_formatada = 'N/A'
            
            # Nome do cliente
            nome_cliente = row.get('nome', row.get('nomeCliente', 'N/A'))
            if pd.notna(nome_cliente) and len(str(nome_cliente)) > 30:
                nome_cliente = str(nome_cliente)[:27] + "..."
            
            # MUDANÇA: usar tipoProcesso ao invés de tipoPrincipal
            tipo_processo = row.get('tipoProcesso', 'N/A')
            
            # Cidade
            cidade = row.get('cidade_upper', row.get('cidade', 'N/A'))
            if pd.notna(cidade) and len(str(cidade)) > 20:
                cidade = str(cidade)[:17] + "..."
            
            tabela_processos.append({
                'Nº Processo': num_processo,
                'Data': data_formatada,
                'Cliente': nome_cliente,
                'Tipo': tipo_processo,  # Agora usando tipoProcesso
                'Cidade': cidade
            })
        
        # Criar DataFrame
        df_tabela = pd.DataFrame(tabela_processos)
        
        # Exibir tabela
        st.dataframe(
            df_tabela,
            use_container_width=True,
            hide_index=True,
            height=220,
            column_config={
                "Nº Processo": st.column_config.TextColumn(
                    "Nº Processo",
                    help="Número do processo"
                ),
                "Data": st.column_config.TextColumn(
                    "Data",
                    help="Data de registro"
                ),
                "Cliente": st.column_config.TextColumn(
                    "Cliente",
                    help="Nome do cliente"
                ),
                "Tipo": st.column_config.TextColumn(
                    "Tipo do Processo",
                    help="Tipo original do processo"
                ),
                "Cidade": st.column_config.TextColumn(
                    "Cidade",
                    help="Cidade do cliente"
                )
            }
        )
                   
    else:
        st.warning("⚠️ Nenhum processo encontrado com os filtros aplicados")

    

if __name__ == "__main__":
    main()

