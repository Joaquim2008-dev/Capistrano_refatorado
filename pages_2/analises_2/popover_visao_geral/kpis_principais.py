import streamlit as st
import pandas as pd

def mostrar_kpis_principais(df_analise):
    """Mostra KPIs principais com cards customizados"""
    # APLICAR FILTRO AQUI TAMBÉM

    # CSS para os cards (fonte reduzida)
    st.markdown("""
        <style>
        .kpi-card {
            background-color: #062e6f;
            padding: 12px;
            border-radius: 8px;
            text-align: center;
            height: 96px;
            display: flex;
            flex-direction: column;
            justify-content: center;
            box-shadow: 0 2px 4px rgba(0,0,0,0.08);
            font-family: inherit;
            font-size: 12px;
        }
        .kpi-title {
            color: rgba(255, 255, 255, 0.9);
            font-size: 12px;
            font-weight: 500;
            margin-bottom: 6px;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }
        .kpi-value {
            color: white;
            font-size: 18px;
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


    
    