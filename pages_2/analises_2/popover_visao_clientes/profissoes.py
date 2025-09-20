import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import sys
from pathlib import Path



def analise_profissoes(df_analise):

    
    # Layout principal
    tab1, tab2 = st.tabs(['top profissões', 'análise por sexo'])
    
    with tab1:
        st.write(f"**Total de profissões únicas:** {df_analise['profissao_normalizada'].nunique()}")
        
        if 'profissao_normalizada' in df_analise.columns:
            top_profissoes = df_analise['profissao_normalizada'].value_counts().head(10)
            
            # Calcular padding baseado no valor máximo
            valor_max = top_profissoes.iloc[0]
            padding = valor_max * 0.2
            
            fig_prof = px.bar(
                x=top_profissoes.values,
                y=top_profissoes.index,
                orientation='h',
                color_discrete_sequence=['darkgreen']
            )
            
            fig_prof.update_layout(
                yaxis={'categoryorder':'total ascending'},
                height=300,
                margin=dict(l=150, r=50, t=20, b=20),
                xaxis_title="",
                yaxis_title="",
                xaxis=dict(
                    range=[0, valor_max + padding],
                    automargin=True
                )
            )
            
            fig_prof.update_traces(
                texttemplate='%{x}',
                textposition='outside'
            )
            fig_prof.update_xaxes(
            showticklabels=False,  # esconde rótulos dos ticks
            ticks="",              # remove as marcas de tick
            showgrid=False,        # remove linhas de grid verticais
            zeroline=False,        # remove linha no zero
            showline=False   
            )
            
            st.plotly_chart(fig_prof, use_container_width=True, key="grafico_profissoes_geral")
            
        else:
            st.warning("Dados de profissão não disponíveis")
    

    with tab2:
        col_masc, col_fem = st.columns(2)
        if 'profissao_normalizada' in df_analise.columns and 'sexo' in df_analise.columns:
            # Filtrar apenas M e F
            df_genero = df_analise[df_analise['sexo'].isin(['M', 'F'])]

            if len(df_genero) > 0:
                with col_masc:
                    st.markdown("**Top 5 - Masculino**")
                    masculino = df_genero[df_genero['sexo'] == 'M']
                    
                    if len(masculino) > 0:
                        # Card azul escuro com total masculino (acima da tabela)
                        st.markdown(f"""
                            <div style="display:flex;gap:8px;align-items:center;margin-bottom:8px;">
                                <div style="background-color:#062e6f;color:#ffffff;padding:10px 14px;border-radius:8px;min-width:160px;">
                                    <div style="font-size:10px;opacity:0.9;">Total Masculino</div>
                                    <div style="font-size:10px;font-weight:700;margin-top:4px;">{len(masculino):,}</div>
                                </div>
                            </div>
                        """, unsafe_allow_html=True)

                        top_masc = masculino['profissao_normalizada'].value_counts().head(5)
                        
                        # Criar DataFrame para tabela
                        tabela_masc = []
                        for prof, count in top_masc.items():
                            percentual = (count / len(masculino) * 100)
                            tabela_masc.append({
                                'Profissão': prof,
                                'Pessoas': count,
                                'Percentual': f"{percentual:.1f}%"
                            })
                        
                        df_tabela_masc = pd.DataFrame(tabela_masc)
                        
                        st.dataframe(
                            df_tabela_masc,
                            use_container_width=True,
                            hide_index=True,
                            height=200,
                            column_config={
                                "Profissão": st.column_config.TextColumn(
                                    "Profissão",
                                    help="Nome da profissão"
                                ),
                                "Pessoas": st.column_config.NumberColumn(
                                    "Pessoas",
                                    help="Número de pessoas",
                                    format="%d"
                                ),
                                "Percentual": st.column_config.TextColumn(
                                    "%",
                                    help="Percentual do total masculino"
                                )
                            }
                        )
                        
                        # st.metric removido
                        
                    else:
                        st.warning("Nenhum dado masculino")
                
                with col_fem:
                    st.markdown("**Top 5 - Feminino**")
                    feminino = df_genero[df_genero['sexo'] == 'F']
                    
                    if len(feminino) > 0:
                        # Card azul escuro com total feminino (acima da tabela)
                        st.markdown(f"""
                            <div style="display:flex;gap:8px;align-items:center;margin-bottom:8px;">
                                <div style="background-color:#062e6f;color:#ffffff;padding:10px 14px;border-radius:8px;min-width:160px;">
                                    <div style="font-size:12px;opacity:0.9;">Total Feminino</div>
                                    <div style="font-size:10px;font-weight:700;margin-top:4px;">{len(feminino):,}</div>
                                </div>
                            </div>
                        """, unsafe_allow_html=True)

                        top_fem = feminino['profissao_normalizada'].value_counts().head(5)
                        
                        # Criar DataFrame para tabela
                        tabela_fem = []
                        for prof, count in top_fem.items():
                            percentual = (count / len(feminino) * 100)
                            tabela_fem.append({
                                'Profissão': prof,
                                'Pessoas': count,
                                'Percentual': f"{percentual:.1f}%"
                            })
                        
                        df_tabela_fem = pd.DataFrame(tabela_fem)
                        
                        st.dataframe(
                            df_tabela_fem,
                            use_container_width=True,
                            hide_index=True,
                            height=200,
                            column_config={
                                "Profissão": st.column_config.TextColumn(
                                    "Profissão",
                                    help="Nome da profissão"
                                ),
                                "Pessoas": st.column_config.NumberColumn(
                                    "Pessoas",
                                    help="Número de pessoas",
                                    format="%d"
                                ),
                                "Percentual": st.column_config.TextColumn(
                                    "%",
                                    help="Percentual do total feminino"
                                )
                            }
                        )
                        
                        # st.metric removido
                        
                    else:
                        st.warning("Nenhum dado feminino")
            
            else:
                st.warning("Nenhum dado de gênero válido (M/F)")
        else:
            st.warning("Dados de profissão ou sexo não disponíveis")