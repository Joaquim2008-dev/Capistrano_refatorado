import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

st.set_page_config(page_title="Teste Gráficos Temporais - Solução B", layout="wide")

# gerar dados fictícios
np.random.seed(42)
hoje = pd.Timestamp.now().normalize()

# 1) Processos por Mês (Últimos 12 meses)
meses = pd.period_range(end=hoje.to_period("M"), periods=12, freq="M")
processos_mes = pd.DataFrame({
    "mes_ano": meses.astype(str),
    "quantidade": np.random.randint(5, 60, size=len(meses))
})
media_mensal_12m = processos_mes["quantidade"].mean()
max_mes = processos_mes["quantidade"].max() if len(processos_mes) > 0 else 1

# 2) Média por Dia da Semana (Últimos 12 meses) - dados fictícios baseados em dias úteis
sim_days = []
start = hoje - pd.DateOffset(months=12)
date_range = pd.date_range(start=start, end=hoje, freq="D")
for d in date_range:
    if d.weekday() < 5:
        sim_days.append({"data": d, "count": np.random.poisson(8)})
df_sim = pd.DataFrame(sim_days)
media_por_dia = df_sim.groupby(df_sim['data'].dt.weekday)['count'].mean().reset_index()
media_por_dia.columns = ['weekday', 'count']
media_por_dia['dia_pt'] = media_por_dia['weekday'].map({0: "Segunda", 1: "Terça", 2: "Quarta", 3: "Quinta", 4: "Sexta"})
media_por_dia = media_por_dia.sort_values('weekday')
media_por_dia_val = media_por_dia['count'].mean()
max_dia = media_por_dia['count'].max() if len(media_por_dia) > 0 else 1

# 3) Semana Corrente (Segunda a Sexta) - dados fictícios
dias_desde_segunda = hoje.weekday()
inicio_semana = hoje - pd.Timedelta(days=dias_desde_segunda)
dias_semana = [inicio_semana + pd.Timedelta(days=i) for i in range(5)]
valores_semana = np.random.randint(0, 15, size=5)
df_semana = pd.DataFrame({
    "dia": ["Segunda", "Terça", "Quarta", "Quinta", "Sexta"],
    "data": [d.strftime("%d/%m") for d in dias_semana],
    "processos": valores_semana
})
media_semana_atual = df_semana["processos"].mean()
max_sem = df_semana['processos'].max() if len(df_semana) > 0 else 1



st.markdown("### Teste B — Ajuste das configurações dos gráficos (limites + margem superior)", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

# cores usadas para linha de média / traço / texto (usar mesma cor para consistência)
line_rgba = "rgba(0,150,136,0.6)"      # linha mais transparente (verde-azulado, diferente de azul escuro)
label_rgba = "rgba(0,150,136,0.95)"    # cor para o traço acima do gráfico

with col1:
    st.markdown('<div class="chart-box">', unsafe_allow_html=True)
    st.markdown('<div class="chart-title">Processos por Mês (ajustado)</div>', unsafe_allow_html=True)

    # Mostrar valor da média acima do gráfico com um traço colorido à esquerda
    st.markdown(f"""
        <div style="display:flex;align-items:center;gap:6px;margin-bottom:2px;margin-top:4px;">
            <span style="display:inline-block;width:34px;height:6px;background:{label_rgba};border-radius:3px;"></span>
            <div style="font-size:13px;color:#ffffff;line-height:1;"><b>Média</b>: {media_mensal_12m:.1f}</div>
        </div>
    """, unsafe_allow_html=True)

    fig_mes_adj = px.bar(processos_mes, x="mes_ano", y="quantidade", color_discrete_sequence=["steelblue"])
    fig_mes_adj.update_traces(texttemplate='%{y}', textposition='outside')
    # garantir espaço superior para labels "outside"
    fig_mes_adj.update_yaxes(range=[0, max_mes * 1.18], showticklabels=False)
    # linha de média sem anotação (apenas evidencia a média)
    fig_mes_adj.add_hline(y=media_mensal_12m, line_color=line_rgba, line_width=2, line_dash="dash")
    fig_mes_adj.update_layout(xaxis_title="", yaxis_title="", height=250,
                              margin=dict(t=40, b=30, l=20, r=20), showlegend=False)
    st.plotly_chart(fig_mes_adj, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="chart-box">', unsafe_allow_html=True)
    st.markdown('<div class="chart-title">Média por Dia (ajustado)</div>', unsafe_allow_html=True)

    # Mostrar valor da média acima do gráfico com um traço colorido à esquerda
    st.markdown(f"""
        <div style="display:flex;align-items:center;gap:6px;margin-bottom:2px;margin-top:4px;">
            <span style="display:inline-block;width:34px;height:6px;background:{label_rgba};border-radius:3px;"></span>
            <div style="font-size:13px;color:#ffffff;line-height:1;"><b>Média</b>: {media_por_dia_val:.1f}</div>
        </div>
    """, unsafe_allow_html=True)

    fig_dia_adj = px.bar(media_por_dia, x='dia_pt', y='count', color_discrete_sequence=['#8B4513'])
    fig_dia_adj.update_traces(texttemplate='%{y:.1f}', textposition='outside')
    fig_dia_adj.update_yaxes(range=[0, max_dia * 1.18], showticklabels=False)
    fig_dia_adj.add_hline(y=media_por_dia_val, line_color=line_rgba, line_width=2, line_dash="dash")
    fig_dia_adj.update_layout(xaxis_title="", yaxis_title="", height=250,
                              margin=dict(t=40, b=30, l=20, r=20), showlegend=False)
    st.plotly_chart(fig_dia_adj, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

with col3:
    st.markdown('<div class="chart-box">', unsafe_allow_html=True)
    st.markdown('<div class="chart-title">Semana Corrente (ajustado)</div>', unsafe_allow_html=True)

    # Mostrar valor da média acima do gráfico com um traço colorido à esquerda
    st.markdown(f"""
        <div style="display:flex;align-items:center;gap:6px;margin-bottom:2px;margin-top:4px;">
            <span style="display:inline-block;width:34px;height:6px;background:{label_rgba};border-radius:3px;"></span>
            <div style="font-size:13px;color:#ffffff;line-height:1;"><b>Média</b>: {media_semana_atual:.1f}</div>
        </div>
    """, unsafe_allow_html=True)

    fig_semana_adj = px.bar(df_semana, x='dia', y='processos', hover_data=['data'], color_discrete_sequence=['#006400'])
    fig_semana_adj.update_traces(texttemplate='%{y}', textposition='outside')
    fig_semana_adj.update_yaxes(range=[0, max_sem * 1.18], showticklabels=False)
    fig_semana_adj.add_hline(y=media_semana_atual, line_color=line_rgba, line_width=2, line_dash="dash")
    fig_semana_adj.update_layout(xaxis_title="", yaxis_title="", height=250,
                                margin=dict(t=40, b=30, l=20, r=20), showlegend=False)
    st.plotly_chart(fig_semana_adj, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)