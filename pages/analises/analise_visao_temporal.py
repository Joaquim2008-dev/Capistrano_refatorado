# ...existing code...
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


def analise_temporal(df_analise, aplicar_filtro_configurado=None):
    """
    Análise referente à aba "Análise Temporal".
    df_analise: DataFrame já preparado.
    aplicar_filtro_configurado: função opcional para aplicar filtro de ano.
    """
    if aplicar_filtro_configurado is not None:
        df_analise = aplicar_filtro_configurado(df_analise)

    if df_analise is None or 'data_convertida' not in df_analise.columns:
        st.warning("Dados de data não disponíveis")
        return

    # garantir datetime e remover nulos
    df_analise = df_analise.copy()
    df_analise['data_convertida'] = pd.to_datetime(
        df_analise['data_convertida'], errors='coerce')
    df_analise = df_analise.dropna(subset=['data_convertida'])
    if df_analise.empty:
        st.warning("Sem datas válidas para análise temporal.")
        return

    hoje = pd.Timestamp.now()

    # Filtrar últimos 12 meses
    doze_meses_atras = hoje - pd.DateOffset(months=12)
    df_12_meses = df_analise[df_analise['data_convertida'] >= doze_meses_atras]

    if len(df_12_meses) == 0:
        st.warning("Nenhum processo nos últimos 12 meses")
        return

    # --- calcular métricas que serão exibidas como KPIs horizontais acima dos gráficos ---
    df_12_meses = df_12_meses.copy()
    df_12_meses['mes_ano'] = df_12_meses['data_convertida'].dt.to_period('M')
    processos_por_mes = df_12_meses.groupby('mes_ano').size().reset_index(name='quantidade')
    processos_por_mes['mes_ano_str'] = processos_por_mes['mes_ano'].astype(str)

    total_12_meses = len(df_12_meses)
    media_mensal_12m = processos_por_mes['quantidade'].mean() if len(processos_por_mes) > 0 else 0

    if len(processos_por_mes) > 0:
        max_mes = int(processos_por_mes['quantidade'].max())
        mes_max = processos_por_mes.loc[processos_por_mes['quantidade'].idxmax(), 'mes_ano_str']
    else:
        max_mes = None
        mes_max = None

    # dias úteis nos últimos 12 meses
    df_12_meses['dia_semana'] = df_12_meses['data_convertida'].dt.dayofweek
    df_dias_uteis = df_12_meses[df_12_meses['dia_semana'].between(0, 4)]
    if 'df_dias_uteis' in locals() and len(df_dias_uteis) > 0:
        weeks_count = df_dias_uteis['data_convertida'].dt.to_period('W').nunique()
        media_dia_util = len(df_dias_uteis) / max(weeks_count * 5, 1)
    else:
        media_dia_util = None

    # determinar cor do delta do pico mensal comparando com a média mensal (verde se acima, vermelho se abaixo)
    if max_mes is not None:
        if max_mes >= media_mensal_12m:
            pico_class = "delta-green-temporal"
        else:
            pico_class = "delta-red-temporal"
    else:
        pico_class = "delta-neutral-temporal"

    # cores para linha de média (usar mesma cor para traço acima do gráfico) - ATUALIZADAS
    line_rgba = "rgba(211,84,0,0.6)"    # linha no gráfico (transparente) - cor laranja
    label_rgba = "rgba(123,102,84,0.95)"  # barra/label acima do gráfico (mais opaco) - cor marrom

    # CSS específico para KPIs da análise temporal
    st.markdown("""
        <style>
        .kpis-row-temporal { display: flex; gap: 18px; align-items: center; margin-bottom: 18px; }
        .kpi-temporal {
            background: transparent;
            padding: 8px 12px;
            border-radius: 6px;
            min-width: 160px;
            text-align: center;
        }
        .kpi-title-temporal { color: #7b6654; font-size: 13px; margin-bottom: 6px; }
        .kpi-value-temporal { color: #d35400; font-size: 18px; font-weight: 600; display: inline-block; vertical-align: middle; }
        /* delta agora fica inline ao lado do valor */
        .kpi-delta-temporal { display: inline-block; margin-left: 8px; font-size: 13px; vertical-align: middle; }
        .delta-green-temporal { color: #4CAF50; font-weight:600; }
        .delta-red-temporal { color: #f44336; font-weight:600; }
        .delta-neutral-temporal { color: #FFC107; font-weight:600; }
        </style>
    """, unsafe_allow_html=True)

    # montar o snippet do delta (agora inline)
    kpi_pico_extra = ""
    if mes_max:
        kpi_pico_extra = f"<span class='kpi-delta-temporal {pico_class}'>em {mes_max}</span>"

    st.markdown(f"""
        <div class="kpis-row-temporal">
            <div class="kpi-temporal">
                <div class="kpi-title-temporal">Total 12 meses</div>
                <div class="kpi-value-temporal">{total_12_meses:,}</div>
            </div>
            <div class="kpi-temporal">
                <div class="kpi-title-temporal">Média mensal</div>
                <div class="kpi-value-temporal">{media_mensal_12m:.1f}</div>
            </div>
            <div class="kpi-temporal">
                <div class="kpi-title-temporal">Pico mensal</div>
                <div>
                    <span class="kpi-value-temporal">{max_mes if max_mes is not None else 'N/A'}</span>
                    {kpi_pico_extra}
                </div>
            </div>
            <div class="kpi-temporal">
                <div class="kpi-title-temporal">Média/dia útil</div>
                <div class="kpi-value-temporal">{media_dia_util:.1f}</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # --- novos gráficos: primeiro bloco (mês corrente) ---
    # Filtrar mês corrente (ano+mes)
    mes_atual = hoje.month
    ano_atual = hoje.year
    df_mes_corrente = df_analise[
        (df_analise['data_convertida'].dt.month == mes_atual) &
        (df_analise['data_convertida'].dt.year == ano_atual)
    ].copy()

    # considerar apenas dias úteis (segunda a sexta) para os novos gráficos
    df_mes_corrente['dia_semana'] = df_mes_corrente['data_convertida'].dt.dayofweek
    df_mes_corrente_uteis = df_mes_corrente[df_mes_corrente['dia_semana'].between(0, 4)]

    # layout: primeira linha com dois gráficos (dia-a-dia no mês corrente e média por dia da semana no mês corrente)
    col_top1, col_top2 = st.columns(2)

    with col_top1:
        st.markdown("**Nº de processos por dia no mês corrente (somente dias úteis)**")
        if df_mes_corrente_uteis.empty:
            st.info("Nenhum processo no mês corrente (dias úteis).")
        else:
            # contar por dia
            df_mes_corrente_uteis['data_only'] = df_mes_corrente_uteis['data_convertida'].dt.date
            processos_por_dia_mes = df_mes_corrente_uteis.groupby('data_only').size().reset_index(name='processos')
            processos_por_dia_mes = processos_por_dia_mes.sort_values('data_only')
            # preparar labels dd/mm
            processos_por_dia_mes['dia_label'] = processos_por_dia_mes['data_only'].apply(lambda d: pd.Timestamp(d).strftime('%d/%m'))

            # média para o mês corrente (diária)
            media_mes_corrente = processos_por_dia_mes['processos'].mean() if len(processos_por_dia_mes) > 0 else 0

            # mostrar média acima do gráfico com traço colorido à esquerda
            st.markdown(f"""
                <div style="display:flex;align-items:center;gap:6px;margin-bottom:2px;margin-top:4px;">
                    <span style="display:inline-block;width:34px;height:6px;background:{label_rgba};border-radius:3px;"></span>
                    <div style="font-size:13px;color:#7b6654;line-height:1;"><b>Média</b>: <span style="color:#d35400;font-weight:600;">{media_mes_corrente:.1f}</span></div>
                </div>
            """, unsafe_allow_html=True)

            fig_dia_mes = px.bar(processos_por_dia_mes, x='dia_label', y='processos', color_discrete_sequence=['#5B9BD5'])
            fig_dia_mes.update_traces(texttemplate='%{y}', textposition='outside')
            max_chart_day = processos_por_dia_mes['processos'].max() if len(processos_por_dia_mes) > 0 else 1
            fig_dia_mes.update_yaxes(range=[0, max_chart_day * 1.18], showticklabels=False)
            fig_dia_mes.add_hline(y=media_mes_corrente, line_color=line_rgba, line_width=2, line_dash="dash")
            fig_dia_mes.update_layout(xaxis_title="", yaxis_title="", height=250, showlegend=False,
                                      margin=dict(t=40, b=20, l=20, r=20))
            st.plotly_chart(fig_dia_mes, use_container_width=True, key='grafico_dia_mes_corrente')

    with col_top2:
        st.markdown("**Número médio de processos por dia da semana — mês corrente**")
        if df_mes_corrente_uteis.empty:
            st.info("Nenhum processo no mês corrente (dias úteis).")
        else:
            # construir série diária e calcular média por weekday no mês corrente
            df_counts = df_mes_corrente_uteis.copy()
            df_counts['data_only'] = df_counts['data_convertida'].dt.date
            counts_per_date = df_counts.groupby('data_only').size().reset_index(name='processos')
            counts_per_date['weekday'] = pd.to_datetime(counts_per_date['data_only']).dt.weekday
            # média por weekday (média dos valores de cada dia do mês para aquele weekday)
            media_por_weekday_mes = counts_per_date.groupby('weekday')['processos'].mean().reset_index()
            weekday_map = {0: 'Segunda', 1: 'Terça', 2: 'Quarta', 3: 'Quinta', 4: 'Sexta'}
            media_por_weekday_mes['dia_pt'] = media_por_weekday_mes['weekday'].map(weekday_map)
            media_por_weekday_mes = media_por_weekday_mes.sort_values('weekday')
            media_weekday_val = media_por_weekday_mes['processos'].mean() if len(media_por_weekday_mes) > 0 else 0

            # mostrar média acima do gráfico com traço colorido à esquerda
            st.markdown(f"""
                <div style="display:flex;align-items:center;gap:6px;margin-bottom:2px;margin-top:4px;">
                    <span style="display:inline-block;width:34px;height:6px;background:{label_rgba};border-radius:3px;"></span>
                    <div style="font-size:13px;color:#7b6654;line-height:1;"><b>Média</b>: <span style="color:#d35400;font-weight:600;">{media_weekday_val:.1f}</span></div>
                </div>
            """, unsafe_allow_html=True)

            fig_media_mes = px.bar(media_por_weekday_mes, x='dia_pt', y='processos', color_discrete_sequence=['#8B4513'])
            fig_media_mes.update_traces(texttemplate='%{y:.1f}', textposition='outside')
            max_chart_weekday = media_por_weekday_mes['processos'].max() if len(media_por_weekday_mes) > 0 else 1
            fig_media_mes.update_yaxes(range=[0, max_chart_weekday * 1.18], showticklabels=False)
            fig_media_mes.add_hline(y=media_weekday_val, line_color=line_rgba, line_width=2, line_dash="dash")
            fig_media_mes.update_layout(xaxis_title="", yaxis_title="", height=250, showlegend=False,
                                       margin=dict(t=40, b=20, l=20, r=20))
            st.plotly_chart(fig_media_mes, use_container_width=True, key='grafico_media_mes_corrente')

    # --- abaixo: manter os dois gráficos anteriores (Processos por mês e Média por dia da semana — 12 meses) ---
    col_graf1, col_graf2 = st.columns(2)

    # garantir média mensal antes de renderizar o bloco 1
    media_mensal_12m = processos_por_mes['quantidade'].mean() if len(processos_por_mes) > 0 else 0

    with col_graf1:
        st.markdown("**Processos por Mês (Últimos 12 meses)**")
        # mostrar média acima do gráfico com traço colorido à esquerda
        st.markdown(f"""
            <div style="display:flex;align-items:center;gap:6px;margin-bottom:2px;margin-top:4px;">
                <span style="display:inline-block;width:34px;height:6px;background:{label_rgba};border-radius:3px;"></span>
                <div style="font-size:13px;color:#7b6654;line-height:1;"><b>Média</b>: <span style="color:#d35400;font-weight:600;">{media_mensal_12m:.1f}</span></div>
            </div>
        """, unsafe_allow_html=True)

        fig_temporal = px.bar(
            processos_por_mes,
            x='mes_ano_str',
            y='quantidade',
            color_discrete_sequence=['steelblue']
        )
        fig_temporal.update_traces(texttemplate='%{y}', textposition='outside')
        # garantir espaço superior para labels "outside"
        max_chart = max_mes if (max_mes is not None and max_mes > 0) else processos_por_mes['quantidade'].max() if len(processos_por_mes)>0 else 1
        fig_temporal.update_yaxes(range=[0, max_chart * 1.18], showticklabels=False)
        # adicionar somente a linha de média (sem texto sobre a linha)
        fig_temporal.add_hline(y=media_mensal_12m, line_color=line_rgba, line_width=2, line_dash="dash")
        fig_temporal.update_layout(xaxis_title="", yaxis_title="", height=250, showlegend=False,
                                   margin=dict(t=40, b=20, l=20, r=20))
        st.plotly_chart(fig_temporal, use_container_width=True,
                        key='grafico_temporal')

    with col_graf2:
        st.markdown("**Média por Dia da Semana (Últimos 12 meses)**")

        # preparar dados de dia da semana antes de desenhar média/markup
        df_12_meses['dia_semana'] = df_12_meses['data_convertida'].dt.dayofweek
        df_12_meses['nome_dia'] = df_12_meses['data_convertida'].dt.day_name()
        df_dias_uteis = df_12_meses[df_12_meses['dia_semana'].between(0, 4)]

        if len(df_dias_uteis) > 0:
            mapa_dias = {
                'Monday': 'Segunda',
                'Tuesday': 'Terça',
                'Wednesday': 'Quarta',
                'Thursday': 'Quinta',
                'Friday': 'Sexta'
            }

            processos_por_dia_semana = df_dias_uteis.groupby(
                ['nome_dia', 'dia_semana']).size().reset_index(name='total_processos')
            weeks_count = df_dias_uteis['data_convertida'].dt.to_period(
                'W').nunique()
            media_por_dia = processos_por_dia_semana.groupby(['nome_dia', 'dia_semana'])[
                'total_processos'].sum().reset_index()
            media_por_dia['media'] = media_por_dia['total_processos'] / \
                max(weeks_count, 1)
            media_por_dia['dia_pt'] = media_por_dia['nome_dia'].map(mapa_dias)
            media_por_dia = media_por_dia.sort_values('dia_semana')
            media_geral_semana = media_por_dia['media'].mean()

            # mostrar média acima do gráfico with traço colorido à esquerda (somente quando houver dados)
            st.markdown(f"""
                <div style="display:flex;align-items:center;gap:6px;margin-bottom:2px;margin-top:4px;">
                    <span style="display:inline-block;width:34px;height:6px;background:{label_rgba};border-radius:3px;"></span>
                    <div style="font-size:13px;color:#7b6654;line-height:1;"><b>Média</b>: <span style="color:#d35400;font-weight:600;">{media_geral_semana:.1f}</span></div>
                </div>
            """, unsafe_allow_html=True)

            fig_dia_semana = px.bar(
                media_por_dia, x='dia_pt', y='media', color_discrete_sequence=['#8B4513'])
            fig_dia_semana.update_traces(
                texttemplate='%{y:.1f}', textposition='outside')
            # linha de média sem texto na linha; valor mostrado acima
            fig_dia_semana.add_hline(y=media_geral_semana, line_color=line_rgba, line_width=2, line_dash="dash")
            # garantir espaço superior para labels "outside"
            max_chart_dia = media_por_dia['media'].max() if ('media' in media_por_dia.columns and len(media_por_dia)>0) else 1
            fig_dia_semana.update_yaxes(range=[0, max_chart_dia * 1.18], showticklabels=False)
            fig_dia_semana.update_layout(xaxis_title="", yaxis_title="", height=250, showlegend=False,
                                         margin=dict(t=40, b=20, l=20, r=20))
            st.plotly_chart(
                 fig_dia_semana, use_container_width=True, key='grafico_dia_semana')
        else:
            st.warning("Nenhum processo em dias úteis encontrado")
