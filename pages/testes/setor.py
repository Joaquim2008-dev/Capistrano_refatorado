import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
import base64


def encode_image(file):
        try:
            with open(file, "rb") as f:
                return "data:image/png;base64," + base64.b64encode(f.read()).decode()
        except FileNotFoundError:
            return None


masculino = encode_image('pages/sexo/masculino.png')
feminino = encode_image('pages/sexo/feminino.png')

st.title("Teste: Gráfico de Sexo por Filtro de Processo (dados fictícios)")

# Se já existir df_analise no escopo (ex.: importado de outro módulo), não sobrescreve.
if 'df_analise' not in globals():
    # Gerar dados fictícios reprodutíveis
    np.random.seed(42)
    n = 300
    sexos = np.random.choice(['M', 'F'], size=n, p=[0.53, 0.47])
    tipos = np.random.choice(
        ['ACAO TRABALHISTA', 'ACAO PREVIDENCIARIA', 'ACAO CIVIL', 'OUTROS'],
        size=n,
        p=[0.35, 0.30, 0.20, 0.15]
    )
    df_analise = pd.DataFrame({
        'sexo': sexos,
        'tipoProcesso': tipos
    })

# Filtros simples para simular seleção de tipo de processo
filtro_opcoes = ['Todos', 'ACAO TRABALHISTA', 'ACAO PREVIDENCIARIA', 'ACAO CIVIL', 'OUTROS']
filtro_selecionado = st.selectbox("Filtrar por tipo de processo", filtro_opcoes)

if filtro_selecionado != 'Todos':
    df_filtrado = df_analise[df_analise['tipoProcesso'] == filtro_selecionado]
else:
    df_filtrado = df_analise.copy()

st.write(f"Registros após filtro: {len(df_filtrado)}")

# Validar coluna sexo e calcular contagens
st.markdown("Distribuição por Sexo")
if 'sexo' in df_filtrado.columns:  # Mudança aqui: usar df_filtrado
        sexo_valido = df_filtrado[df_filtrado['sexo'].isin(['M', 'F'])]  # E aqui também

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
                textposition="outside", 
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