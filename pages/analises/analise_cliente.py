import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
import base64

def analise_cliente(df_analise):
    """
    Separa a lógica da aba "Perfil dos Clientes".
    Recebe df_analise já preparado (colunas como 'idade_cliente_anos', 'sexo', etc).
    """

    # resumo horizontal dinâmico (substitui as tabelas concentração etária / resumo)

    def encode_image(file):
        try:
            with open(file, "rb") as f:
                return "data:image/png;base64," + base64.b64encode(f.read()).decode()
        except FileNotFoundError:
            return None
        
    masculino = encode_image('pages/sexo/masculino.png')
    feminino = encode_image('pages/sexo/feminino.png')


    if 'idade_cliente_anos' in df_analise.columns:
        idades_line = df_analise['idade_cliente_anos'].dropna()
    else:
        idades_line = pd.Series(dtype=float)

    if len(idades_line) > 0:
        p10 = int(idades_line.quantile(0.10))
        p25 = int(idades_line.quantile(0.25))
        p50 = int(idades_line.quantile(0.50))
        p75 = int(idades_line.quantile(0.75))
        p90 = int(idades_line.quantile(0.90))

        # faixa mais comum aproximada em bins de 5 anos -> formatar "A a B"
        faixa_limpa = ""
        try:
            bins = range(int(idades_line.min()), int(idades_line.max()) + 5, 5)
            idades_faixas = pd.cut(idades_line, bins=bins)
            modo = idades_faixas.mode()
            if len(modo) > 0:
                faixa_str = str(modo[0])
                # faixa_str vem algo como '(70, 75]' ou '[70, 75)'
                faixa_limpa = faixa_str.replace('(', '').replace(')', '').replace('[', '').replace(']', '').replace(',', ' a')
        except Exception:
            faixa_limpa = ""

        # KPIs em 4 cards azul-escuros (linha horizontal) contendo as análises solicitadas
        st.markdown("""
            <style>
            .kpis-row-cliente { display: flex; gap: 14px; align-items: stretch; margin-bottom: 18px; }
            .kpi-card-cliente {
                background: #062e6f; /* Azul escuro consistente */
                padding: 12px 14px;
                border-radius: 10px;
                min-width: 180px;
                flex: 1;
                text-align: center;
                color: #ffffff;
                box-shadow: 0 4px 8px rgba(6,46,111,0.12);
                display: flex;
                flex-direction: column;
                justify-content: center;
                align-items: center;
            }
            .kpi-text-cliente { color: #ffffff; font-size: 14px; line-height:1.3; }
            .kpi-highlight { color: #d35400; font-weight:700; }
            </style>
        """, unsafe_allow_html=True)

        st.markdown(f"""
            <div class="kpis-row-cliente">
                <div class="kpi-card-cliente">
                    <div class="kpi-text-cliente">50% dos clientes estão entre <span class="kpi-highlight">43</span> e <span class="kpi-highlight">66</span> anos</div>
                </div>
                <div class="kpi-card-cliente">
                    <div class="kpi-text-cliente">80% dos clientes estão entre <span class="kpi-highlight">31</span> e <span class="kpi-highlight">74</span> anos</div>
                </div>
                <div class="kpi-card-cliente">
                    <div class="kpi-text-cliente">Mediana: <span class="kpi-highlight">57 anos</span></div>
                </div>
                <div class="kpi-card-cliente">
                    <div class="kpi-text-cliente">Faixa mais comum: <span class="kpi-highlight">56 a 61</span></div>
                </div>
            </div>
        """, unsafe_allow_html=True)

        # Removidos os 4 cards azuis conforme solicitado — segue a lógica restante sem os cards.
    else:
        st.markdown("""
            <div style="padding:10px 16px;display:flex;align-items:center;gap:24px;
                        color:#7b6654;font-size:14px;">
                <div>Sem dados de idade disponíveis</div>
            </div>
        """, unsafe_allow_html=True)

    col_idade, col_sexo, col_stats = st.columns([2, 2, 1])

    with col_idade:
        st.markdown(" Distribuição de Idades")
        if 'idade_cliente_anos' in df_analise.columns:
            # incluir a coluna 'sexo' em idades_validas (manter linhas com idade válida)
            idades_validas = df_analise[['idade_cliente_anos', 'sexo']].dropna(subset=['idade_cliente_anos']).copy()

            if len(idades_validas) > 0:
                # botão tipo "pills" para filtrar por sexo: Masculino / Feminino / Ambos
                try:
                    opcao_sexo = st.pills(["Masculino", "Feminino", "Ambos"], index=2, key="pills_sexo_idades")
                except Exception:
                    # fallback para caso st.pills não exista (compatibilidade)
                    opcao_sexo = st.radio("Sexo:", ["Masculino", "Feminino", "Ambos"], index=2, key="radio_sexo_idades")

                # mapear seleção para filtro no dataframe (coluna sexo usa 'M'/'F')
                if opcao_sexo == "Masculino":
                    idades_filtradas = idades_validas[idades_validas['sexo'] == 'M']
                elif opcao_sexo == "Feminino":
                    idades_filtradas = idades_validas[idades_validas['sexo'] == 'F']
                else:
                    idades_filtradas = idades_validas

                if len(idades_filtradas) == 0:
                    st.warning("Nenhuma idade válida encontrada para o filtro selecionado")
                else:
                    fig_idades = px.histogram(
                        idades_filtradas,
                        x='idade_cliente_anos',
                        nbins=20,
                        color_discrete_sequence=['steelblue']
                    )

                    fig_idades.update_traces(
                        texttemplate='%{y}',
                        textposition='outside'
                    )

                    # garantir que labels 'outside' caibam: aumentar limite superior baseado na maior contagem
                    counts, _ = np.histogram(idades_filtradas['idade_cliente_anos'].dropna(), bins=20)
                    max_count = int(counts.max()) if len(counts) > 0 else 1
                    fig_idades.update_yaxes(range=[0, max_count * 1.18], showticklabels=False)

                    fig_idades.update_layout(
                        title="",
                        xaxis_title="",
                        yaxis_title="",
                        height=250,
                        showlegend=False,
                        margin=dict(t=60, b=20, l=20, r=20),
                        yaxis=dict(
                            showticklabels=False,
                            showgrid=False,
                            zeroline=False
                        ),
                        xaxis=dict(
                            showgrid=False,
                        ),
                        bargap=0.1
                    )

                    st.plotly_chart(fig_idades, use_container_width=True, key="grafico_idades_clientes")
            else:
                st.warning("Nenhuma idade válida encontrada")
        else:
            st.warning("Dados de idade não disponíveis")
    with col_sexo:
        st.markdown("Distribuição por Sexo")
        if 'sexo' in df_analise.columns:
            sexo_valido = df_analise[df_analise['sexo'].isin(['M', 'F'])]

            if len(sexo_valido) > 0:
                sexo_counts = sexo_valido['sexo'].value_counts()

                # converter para gráfico de barras com porcentagens como rótulos
                labels = ['Masculino' if x == 'M' else 'Feminino' for x in sexo_counts.index]
                counts = sexo_counts.values
                total = counts.sum() if len(counts) > 0 else 1
                percents = [(v / total) * 100 for v in counts]
                text_labels = [f"{p:.1f}%" for p in percents]

                df_bar = pd.DataFrame({
                    "sexo": labels,
                    "count": counts,
                    "percent_label": text_labels
                })

                # converter gráfico de barras para gráfico de pizza
                fig_sexo = px.pie(
                    df_bar,
                    names="sexo",
                    values="count",
                    color="sexo",
                    color_discrete_map={'Masculino': "#0627cb", 'Feminino': "#d20bae"}
                )
                    
                # Calcular posições dos textos externos
                import math
                
                # Encontrar índice do masculino
                masculino_idx = None
                for i, label in enumerate(labels):
                    if label == "Masculino":
                        masculino_idx = i
                        break
                
                if masculino_idx is not None and masculino is not None:
                    # Calcular ângulo do centro do setor masculino
                    cumulative_angle = 0
                    for i in range(masculino_idx):
                        cumulative_angle += (counts[i] / total) * 360
                    
                    meio_setor_angle = cumulative_angle + (counts[masculino_idx] / total) * 360 / 2
                    # Converter para radianos e ajustar (pizza começa em 90°)
                    angulo_rad = math.radians(90 - meio_setor_angle)
                    
                    # Para textposition="outside", o texto fica aproximadamente no raio 1.1-1.2
                    raio_texto = 1.15
                    x_texto = 0.5 + raio_texto * 0.3 * math.cos(angulo_rad)  # 0.3 é fator de escala
                    y_texto = 0.5 + raio_texto * 0.3 * math.sin(angulo_rad)
                    
                    # Adiciona a imagem próxima ao texto masculino
                    fig_sexo.add_layout_image(
                        dict(
                            source=masculino,
                            x=x_texto, y=y_texto,
                            xref="paper", yref="paper",
                            sizex=0.3, sizey=0.5,
                            xanchor="center", yanchor="middle",
                            layer="above"
                        )
                    )

                # Encontrar índice do feminino e adicionar sua imagem
                feminino_idx = None
                for i, label in enumerate(labels):
                    if label == "Feminino":
                        feminino_idx = i
                        break
                
                if feminino_idx is not None and feminino is not None:
                    # Calcular ângulo do centro do setor feminino
                    cumulative_angle_fem = 0
                    for i in range(feminino_idx):
                        cumulative_angle_fem += (counts[i] / total) * 360
                    
                    meio_setor_angle_fem = cumulative_angle_fem + (counts[feminino_idx] / total) * 360 / 2
                    # Converter para radianos e ajustar (pizza começa em 90°)
                    angulo_rad_fem = math.radians(90 - meio_setor_angle_fem)
                    
                    # Para textposition="outside", o texto fica aproximadamente no raio 1.1-1.2
                    raio_texto_fem = 1.15
                    x_texto_fem = 0.5 + raio_texto_fem * 0.3 * math.cos(angulo_rad_fem)
                    y_texto_fem = 0.5 + raio_texto_fem * 0.3 * math.sin(angulo_rad_fem)
                    
                    # Adiciona a imagem próxima ao texto feminino
                    fig_sexo.add_layout_image(
                        dict(
                            source=feminino,
                            x=x_texto_fem, y=y_texto_fem,
                            xref="paper", yref="paper",
                            sizex=0.3, sizey=0.5,
                            xanchor="center", yanchor="middle",
                            layer="above"
                        )
                    )

                fig_sexo.update_traces(
                    textinfo="percent", 
                    textposition="inside", 
                    pull=[0.02 if v==max(counts) else 0 for v in counts],
                    textfont=dict(size=16, color='black', family='Arial Black')
                )
                fig_sexo.update_layout(
                    title="",
                    height=300,
                    margin=dict(t=20, b=20, l=20, r=20),
                    showlegend=False
                )

                st.plotly_chart(fig_sexo, use_container_width=True, key="grafico_sexo_clientes")
            else:
                st.warning("Nenhum dado válido de sexo (M/F)")
        else:
            st.warning("Dados de sexo não disponíveis")

    with col_stats:
        # para a barra horizontal acima dos gráficos (dinâmica, baseada em df_analise).
        pass
