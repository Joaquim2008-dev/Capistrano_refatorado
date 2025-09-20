import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import sys
from pathlib import Path

def analise_prospectors(df_analise):

        
    if 'prospector' not in df_analise.columns:
        st.warning("Coluna 'prospector' não encontrada")
        return
    
    if 'data_convertida' not in df_analise.columns:
        st.warning("Dados de data não disponíveis para análise temporal")
        return
    
    # Filtrar últimos 12 meses para calcular KPIs
    hoje = pd.Timestamp.now()
    doze_meses_atras = hoje - pd.DateOffset(months=12)
    df_12_meses = df_analise[df_analise['data_convertida'] >= doze_meses_atras]
    
    # Calcular estatísticas do período
    if len(df_12_meses) > 0:
        total_12_meses = len(df_12_meses)
        com_prospector_12m = df_12_meses['prospector'].notna().sum()
        percentual_prospector_12m = (com_prospector_12m / total_12_meses * 100) if total_12_meses > 0 else 0
        
        # KPIs em 3 cards horizontais com fundo azul escuro (classes específicas pp- para evitar conflitos)
        st.markdown(f"""
        <style>
        .pp-kpi-row {{ display:flex; gap:6px; align-items:center; margin-bottom:0px; }}
        .pp-kpi-card {{
          background: linear-gradient(180deg, #062a6a, #04214f);
          color: #ffffff;
          padding: 3px 4px;
          border-radius: 6px;
          box-shadow: 0 2px 4px rgba(2,6,23,0.18);
          width: 120px;
          max-width: 120px;
          text-align: center;
          line-height:1;
          overflow:hidden;
        }}
        .pp-kpi-label {{ font-size:8px; color: rgba(255,255,255,0.85); white-space:nowrap; text-overflow:ellipsis; overflow:hidden; }}
        .pp-kpi-value {{ font-size:10px; font-weight:700; margin-top:2px; }}
        /* escopo adicional para garantir isolamento dentro deste componente */
        div.pp-kpi-wrapper .pp-kpi-card {{ display:inline-block; vertical-align:middle; }}
        </style>
        <div class="pp-kpi-row pp-kpi-wrapper">
          <div class="pp-kpi-card">
            <div class="pp-kpi-label">Total 12 meses</div>
            <div class="pp-kpi-value">{total_12_meses:,}</div>
          </div>
          <div class="pp-kpi-card">
            <div class="pp-kpi-label">Com prospector</div>
            <div class="pp-kpi-value">{com_prospector_12m:,}</div>
          </div>
          <div class="pp-kpi-card">
            <div class="pp-kpi-label">% com prospector</div>
            <div class="pp-kpi-value">{percentual_prospector_12m:.1f}%</div>
          </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.warning("Nenhum processo nos últimos 12 meses")
        return

    # criar dois tabs: 1) gráfico de proporção por mês 2) top 5 prospectors
    tab_graf, tab_top = st.tabs(["Proporção de Ações por Mês (Últimos 12 meses)", "Top 5 Prospectors"])

    with tab_graf:
        
        if len(df_12_meses) > 0:
            # Criar coluna indicando se tem prospector
            df_12_meses = df_12_meses.copy()
            df_12_meses['tem_prospector'] = df_12_meses['prospector'].notna()
            df_12_meses['prospector_categoria'] = df_12_meses['tem_prospector'].map({
                True: 'Com Prospector',
                False: 'Sem Prospector'
            })
            
            # Agrupar por mês e categoria
            df_12_meses['mes_ano'] = df_12_meses['data_convertida'].dt.to_period('M')
            agrupado = df_12_meses.groupby(['mes_ano', 'prospector_categoria']).size().reset_index(name='quantidade')
            agrupado['mes_ano_str'] = agrupado['mes_ano'].astype(str)
            
            # Calcular percentuais manualmente para cada mês
            totais_por_mes = agrupado.groupby('mes_ano_str')['quantidade'].sum().reset_index()
            totais_por_mes.columns = ['mes_ano_str', 'total_mes']
            
            agrupado = agrupado.merge(totais_por_mes, on='mes_ano_str')
            agrupado['percentual'] = (agrupado['quantidade'] / agrupado['total_mes'] * 100)
            
            # Criar gráfico de barras empilhadas usando percentual já calculado
            fig_prospector = px.bar(
                agrupado,
                x='mes_ano_str',
                y='percentual',
                color='prospector_categoria',
                color_discrete_map={
                    'Com Prospector': '#2E8B57',
                    'Sem Prospector': '#CD5C5C'
                }
            )
            
            fig_prospector.update_layout(
                title="",
                xaxis_title="",
                yaxis_title="",
                height=350,
                margin=dict(t=20, b=20, l=20, r=20),
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1
                ),
                yaxis=dict(
                    showticklabels=False,
                    range=[0, 100]
                )
            )
            
            fig_prospector.update_traces(
                texttemplate='%{y:.1f}%',
                textposition='inside'
            )
            
            st.plotly_chart(fig_prospector, use_container_width=True, key="grafico_prospectors_temporal")
        else:
            st.warning("Nenhum processo nos últimos 12 meses")

    with tab_top:
       
        periodo_filtro = st.radio(
            label='',
            options=["Geral", "Ano atual", "Mês atual"],
            index=0,
            horizontal=True,
            key="radio_periodo_prospectors_unique_key_2024"  # CHAVE BEM ÚNICA
        )
        
        # Aplicar filtro baseado na seleção
        if periodo_filtro == "Geral":
            df_filtrado_prospector = df_analise
            periodo_texto = "todos os dados"
        elif periodo_filtro == "Ano atual":
            ano_atual = pd.Timestamp.now().year
            df_filtrado_prospector = df_analise[df_analise['data_convertida'].dt.year == ano_atual]
            periodo_texto = f"ano {ano_atual}"
        else:  # Mês atual
            hoje = pd.Timestamp.now()
            primeiro_dia_mes = hoje.replace(day=1)
            df_filtrado_prospector = df_analise[df_analise['data_convertida'] >= primeiro_dia_mes]
            periodo_texto = f"{hoje.strftime('%B/%Y')}"
        
        # Calcular top 5 prospectors
        prospectors_validos = df_filtrado_prospector['prospector'].dropna()
        
        if len(prospectors_validos) > 0:
            top_prospectors = prospectors_validos.value_counts().head(5)
            total_com_prospector = len(prospectors_validos)
            
            st.markdown(f"**Ranking ({periodo_texto}):**")

            st.markdown("""
            <style>
            .prospector-item {
                display: flex;
                justify-content: space-between;
                align-items: center;
                padding: 6px 0;
                border-bottom: 1px solid #eee;
            }
            .prospector-rank { 
                width: 30px; 
                font-weight: bold; 
            }
            .prospector-name { 
                flex: 1; 
                max-width: 2000px; 
                word-wrap: break-word;
                padding-right: 10px;
            }
            .prospector-count { 
                width: 60px; 
                text-align: center; 
            }
            .prospector-perc { 
                width: 50px; 
                text-align: center; 
            }
            </style>
            """, unsafe_allow_html=True)

            for i, (prospector, count) in enumerate(top_prospectors.items(), 1):
                percentual = (count / total_com_prospector * 100)
                
                st.markdown(f"""
                <div class="prospector-item">
                    <div class="prospector-rank">{i}º</div>
                    <div class="prospector-name">{prospector}</div>
                    <div class="prospector-count">{count}</div>
                    <div class="prospector-perc">{percentual:.1f}%</div>
                </div>
                """, unsafe_allow_html=True)
                        
        else:
            st.warning(f"Nenhum prospector encontrado para {periodo_texto}")