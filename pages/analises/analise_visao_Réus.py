import streamlit as st
import pandas as pd
import plotly.express as px
from utils.text_processing import padronizar_reu, padronizar_competencia


def analise_reus_procedencia(df_analise):
    """
    Separa a lógica da aba "Réus & competência".
    Recebe df_analise já filtrado (não aplica filtros aqui).
    """

    col_reu1, col_reu2, col_competencia = st.columns(3)

    with col_reu1:
        st.markdown(" Top 10 Réus")

        if 'reu' in df_analise.columns:
            # Aplicar padronização
            try:
                df_analise['reu_ajustado'] = df_analise['reu'].apply(padronizar_reu)
            except Exception:
                df_analise['reu_ajustado'] = df_analise['reu']

            # Contar réus padronizados
            top_reus = df_analise['reu_ajustado'].value_counts().head(10)

            # Estatísticas
            total_reus_unicos = df_analise['reu_ajustado'].nunique() if 'reu_ajustado' in df_analise.columns else 0
            if len(top_reus) > 0:
                reu_mais_comum = top_reus.index[0]
                processos_reu_top = top_reus.iloc[0]
                percentual_top = (processos_reu_top / len(df_analise) * 100) if len(df_analise) > 0 else 0
            else:
                reu_mais_comum = None
                processos_reu_top = 0
                percentual_top = 0

            if len(top_reus) > 0:
                # Calcular padding baseado no valor máximo
                valor_max = top_reus.iloc[0]
                padding = valor_max * 0.2  # 20% de padding

                fig_reus = px.bar(
                    x=top_reus.values,
                    y=top_reus.index,
                    orientation='h',
                    color_discrete_sequence=['steelblue']
                )

                fig_reus.update_layout(
                    yaxis={'categoryorder': 'total ascending'},
                    height=500,
                    margin=dict(l=100, r=50, t=20, b=20),
                    xaxis_title="",
                    yaxis_title="",
                    xaxis=dict(
                        range=[0, valor_max + padding],
                        automargin=True
                    )
                )

                # Adicionar números nas barras
                fig_reus.update_traces(
                    texttemplate='%{x}',
                    textposition='outside'
                )

                st.plotly_chart(fig_reus, use_container_width=True, key='grafico_reus')
        else:
            st.warning("Coluna 'reu' não encontrada")

    with col_reu2:
        # Estatísticas e top específicos
        try:
            st.metric("Réus únicos", total_reus_unicos)
            if reu_mais_comum:
                st.metric(f"% {reu_mais_comum}", f"{percentual_top:.1f}%")
            else:
                st.metric("Top Réu", "N/A")
        except Exception:
            # proteger caso variáveis não existam
            st.metric("Réus únicos", "N/A")

        st.markdown("**Top 5 Réus - Ação Cível:**")
        if 'tipoPrincipal' in df_analise.columns:
            df_civel = df_analise[df_analise['tipoPrincipal'] == 'ACAO CIVEL']
            if len(df_civel) > 0:
                top_reus_civel = df_civel['reu_ajustado'].value_counts().head(5)
                for i, (reu, count) in enumerate(top_reus_civel.items(), 1):
                    percentual = (count / len(df_civel) * 100)
                    st.write(f"{i}. **{reu}**: {count:,} ({percentual:.1f}%)")
            else:
                st.write("Nenhum processo de Ação Cível encontrado")
        else:
            st.write("Dados de tipo de processo não disponíveis")

    with col_competencia:
        st.markdown("**Top 10 Competências**")
        if 'competencia' in df_analise.columns:
            try:
                df_analise['competencia_ajustada'] = df_analise['competencia'].apply(padronizar_competencia)
            except Exception:
                df_analise['competencia_ajustada'] = df_analise['competencia']

            competencia_counts = df_analise['competencia_ajustada'].value_counts()

            if len(competencia_counts) > 0:
                df_competencia = competencia_counts.head(10).reset_index()
                df_competencia.columns = ['Competência', 'Número de Processos']

                valor_max = df_competencia['Número de Processos'].iloc[0]
                padding = valor_max * 0.2

                fig_competencia = px.bar(
                    df_competencia,
                    x='Número de Processos',
                    y='Competência',
                    orientation='h',
                    color_discrete_sequence=['darkgreen']
                )

                fig_competencia.update_layout(
                    yaxis={'categoryorder': 'total ascending'},
                    height=500,
                    margin=dict(l=100, r=50, t=20, b=20),
                    xaxis_title="",
                    yaxis_title="",
                    xaxis=dict(
                        range=[0, valor_max + padding],
                        automargin=True
                    )
                )

                fig_competencia.update_traces(
                    texttemplate='%{x}',
                    textposition='outside'
                )

                st.plotly_chart(fig_competencia, use_container_width=True, key='grafico_competencia')
        else:
            st.warning("Coluna 'competencia' não encontrada")