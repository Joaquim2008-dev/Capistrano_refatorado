import streamlit as st
import pandas as pd
import plotly.express as px
from utils.text_processing import padronizar_reu, padronizar_competencia


def analise_reus_procedencia(df_analise):
    """
    Separa a lógica da aba "Réus & competência".
    Recebe df_analise já filtrado (não aplica filtros aqui).
    """

    # preparar réus padronizados e estatísticas antes de criar colunas (cards fora das colunas)
    total_reus_unicos = 0
    percent_inss = 0.0
    reu_mais_comum = None
    percentual_top = 0.0
    top_reus_full = pd.Series(dtype=int)

    if 'reu' in df_analise.columns:
        try:
            df_analise['reu_ajustado'] = df_analise['reu'].apply(padronizar_reu)
        except Exception:
            df_analise['reu_ajustado'] = df_analise['reu']

        if 'reu_ajustado' in df_analise.columns and len(df_analise) > 0:
            total_reus_unicos = int(df_analise['reu_ajustado'].nunique())
            count_inss = df_analise['reu_ajustado'].str.contains('INSS', case=False, na=False).sum()
            percent_inss = (count_inss / len(df_analise) * 100) if len(df_analise) > 0 else 0.0

            top_reus_full = df_analise['reu_ajustado'].value_counts()
            if len(top_reus_full) > 0:
                reu_mais_comum = top_reus_full.index[0]
                processos_reu_top = int(top_reus_full.iloc[0])
                percentual_top = (processos_reu_top / len(df_analise) * 100) if len(df_analise) > 0 else 0.0
    else:
        st.warning("Coluna 'reu' não encontrada")

    # Cards horizontais azuis (fora das colunas) — Réus únicos | % INSS | Réu mais comum + participação
    st.markdown(f"""
        <div style="display:flex;gap:8px;align-items:stretch;margin-bottom:8px;">
            <div style="background-color:#062e6f;color:#ffffff;padding:6px 8px;border-radius:8px;min-width:120px;text-align:center;line-height:1;">
                <div style="font-size:10px;opacity:0.9;">Réus únicos</div>
                <div style="font-size:12px;font-weight:700;margin-top:3px;">{total_reus_unicos:,}</div>
            </div>
            <div style="background-color:#062e6f;color:#ffffff;padding:6px 8px;border-radius:8px;min-width:120px;text-align:center;line-height:1;">
                <div style="font-size:10px;opacity:0.9;">% INSS</div>
                <div style="font-size:12px;font-weight:700;margin-top:3px;">{percent_inss:.1f}%</div>
            </div>
            <div style="background-color:#062e6f;color:#ffffff;padding:6px 8px;border-radius:8px;min-width:160px;text-align:left;line-height:1;">
                <div style="font-size:10px;opacity:0.9;">Réu mais comum</div>
                <div style="font-size:12px;font-weight:700;margin-top:3px;">{reu_mais_comum or 'N/A'}</div>
                <div style="font-size:10px;opacity:0.85;margin-top:6px;">Participação do top</div>
                <div style="font-size:12px;font-weight:700;margin-top:3px;">{percentual_top:.1f}%</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # agora as colunas com o gráfico e painel direito
    col_reu1, col_reu2 = st.tabs(['top 10 réus', 'top 5 réus - Ação Cível'])

    with col_reu1:
        top_reus = top_reus_full.head(10) if not top_reus_full.empty else pd.Series(dtype=int)

        if len(top_reus) > 0:
            valor_max = int(top_reus.iloc[0])
            padding = valor_max * 0.2

            # barras horizontais: x = contagens, y = nomes dos réus
            fig_reus = px.bar(
                x=top_reus.values,
                y=top_reus.index,
                orientation='h',
                color_discrete_sequence=['steelblue']
            )

            fig_reus.update_layout(
                yaxis={'categoryorder': 'total ascending'},
                height=280,
                margin=dict(l=150, r=20, t=20, b=20),  # mais espaço à esquerda para nomes
                xaxis_title="",
                yaxis_title="",
                xaxis=dict(range=[0, valor_max + padding], automargin=True)
            )

            # esconder ticks/labels do eixo X (valores) se quiser apenas mostrar os números nas barras
            fig_reus.update_xaxes(showticklabels=False, ticks="", showgrid=False, zeroline=False, showline=False)

            # mostrar valores no fim das barras e garantir labels dos réus visíveis
            fig_reus.update_traces(
                texttemplate='%{x}',
                textposition='outside'
            )
            fig_reus.update_yaxes(automargin=True)

            st.plotly_chart(fig_reus, use_container_width=True, key='grafico_reus')
        else:
            st.warning("Nenhum réu encontrado")

    with col_reu2:
        # Top 5 Réus - Ação Cível como gráfico de barras horizontais
        if 'tipoPrincipal' in df_analise.columns and 'reu_ajustado' in df_analise.columns:
            df_civel = df_analise[df_analise['tipoPrincipal'] == 'ACAO CIVEL']
            if len(df_civel) > 0:
                top_reus_civel = df_civel['reu_ajustado'].value_counts().head(5)

                # parâmetros para escala
                valor_max_civel = int(top_reus_civel.iloc[0]) if len(top_reus_civel) > 0 else 0
                padding_civel = max(1, valor_max_civel * 0.15)

                fig_civel = px.bar(
                    x=top_reus_civel.values,
                    y=top_reus_civel.index,
                    orientation='h',
                    color_discrete_sequence=['#2b7fb8']
                )

                fig_civel.update_layout(
                    yaxis={'categoryorder': 'total ascending'},
                    height=280,
                    margin=dict(l=150, r=20, t=10, b=20),
                    xaxis_title="",
                    yaxis_title="",
                    xaxis=dict(range=[0, valor_max_civel + padding_civel], automargin=True)
                )

                # esconder ticks/labels do eixo X (valores)
                fig_civel.update_xaxes(showticklabels=False, ticks="", showgrid=False, zeroline=False, showline=False)

                fig_civel.update_traces(
                    texttemplate='%{x}',
                    textposition='outside'
                )
                fig_civel.update_yaxes(automargin=True)

                st.plotly_chart(fig_civel, use_container_width=True, key='grafico_reus_civel')
            else:
                st.write("Nenhum processo de Ação Cível encontrado")
        else:
            st.write("Dados de tipo de processo não disponíveis")


def competencia(df_analise):
    """
    Gráfico Top 10 Competências (horizontal).
    Copiado/adaptado do gráfico Top 10 Réus.
    """
    if 'competencia' not in df_analise.columns:
        st.warning("Coluna 'competencia' não encontrada")
        return

    # padronizar se possível
    try:
        df_analise['competencia_ajustada'] = df_analise['competencia'].apply(padronizar_competencia)
    except Exception:
        df_analise['competencia_ajustada'] = df_analise['competencia']

    top_comp = df_analise['competencia_ajustada'].value_counts().head(10)
    if top_comp.empty:
        st.warning("Nenhuma competência encontrada")
        return

    valor_max = int(top_comp.iloc[0])
    padding = valor_max * 0.2

    fig_comp = px.bar(
        x=top_comp.values,
        y=top_comp.index,
        orientation='h',
        color_discrete_sequence=['#4b8bbe']
    )

    fig_comp.update_layout(
        yaxis={'categoryorder': 'total ascending'},
        height=350,
        margin=dict(l=150, r=20, t=20, b=20),
        xaxis_title="",
        yaxis_title="",
        xaxis=dict(range=[0, valor_max + padding], automargin=True)
    )

    # esconder ticks/labels do eixo X (valores) e deixar números nas barras
    fig_comp.update_xaxes(showticklabels=False, ticks="", showgrid=False, zeroline=False, showline=False)
    fig_comp.update_traces(texttemplate='%{x}', textposition='outside')
    fig_comp.update_yaxes(automargin=True)

    st.markdown("Top 10 Competências")
    st.plotly_chart(fig_comp, use_container_width=True, key='grafico_competencias_top10')
