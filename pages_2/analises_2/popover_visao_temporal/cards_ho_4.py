import streamlit as st
import pandas as pd
import plotly.express as px

def render_4_cards_temporal(df_analise):
    """
    Renderiza 4 KPIs horizontais (azul-escuro) calculando tudo internamente a partir de df_analise.
    """
    if df_analise is None:
        st.warning("Dados não disponíveis para os KPIs temporais")
        return

    df = df_analise.copy()

    # garantir coluna de data
    if 'data_convertida' not in df.columns and 'data' in df.columns:
        df['data_convertida'] = pd.to_datetime(df['data'], errors='coerce')
    else:
        df['data_convertida'] = pd.to_datetime(df.get('data_convertida'), errors='coerce')

    df = df.dropna(subset=['data_convertida'])
    if df.empty:
        st.warning("Sem datas válidas para calcular KPIs temporais")
        return

    hoje = pd.Timestamp.now()
    doze_meses_atras = hoje - pd.DateOffset(months=12)
    df_12_meses = df[df['data_convertida'] >= doze_meses_atras].copy()

    if df_12_meses.empty:
        st.warning("Nenhum processo nos últimos 12 meses")
        return

    # métricas principais
    total_12_meses = len(df_12_meses)
    df_12_meses['mes_ano'] = df_12_meses['data_convertida'].dt.to_period('M')
    processos_por_mes = df_12_meses.groupby('mes_ano').size().reset_index(name='quantidade')
    processos_por_mes['mes_ano_str'] = processos_por_mes['mes_ano'].astype(str)
    media_mensal_12m = processos_por_mes['quantidade'].mean() if len(processos_por_mes) > 0 else 0

    if len(processos_por_mes) > 0:
        max_mes = int(processos_por_mes['quantidade'].max())
        mes_max = processos_por_mes.loc[processos_por_mes['quantidade'].idxmax(), 'mes_ano_str']
    else:
        max_mes = None
        mes_max = None

    # dias úteis nos últimos 12 meses -> média por dia útil
    df_12_meses['dia_semana'] = df_12_meses['data_convertida'].dt.dayofweek
    df_dias_uteis = df_12_meses[df_12_meses['dia_semana'].between(0, 4)]
    if len(df_dias_uteis) > 0:
        weeks_count = df_dias_uteis['data_convertida'].dt.to_period('W').nunique()
        media_dia_util = len(df_dias_uteis) / max(weeks_count * 5, 1)
    else:
        media_dia_util = None

    # classes para delta
    if max_mes is not None:
        pico_class = "delta-green-temporal" if max_mes >= media_mensal_12m else "delta-red-temporal"
    else:
        pico_class = "delta-neutral-temporal"

    kpi_pico_extra = f"<span class='kpi-delta-temporal {pico_class}'> em {mes_max}</span>" if mes_max else ""

    # estilo dos 4 cards (pequenos)
    st.markdown("""
        <style>
        .kpis-row-temporal { display: flex; gap: 6px; align-items: stretch; margin-bottom: 8px; }
        .kpi-card-temporal {
            background: #062e6f;
            padding: 4px 6px;
            border-radius: 6px;
            min-width: 70px;
            max-width: 110px;
            flex: 1;
            text-align: center;
            color: #ffffff;
            box-shadow: 0 1px 3px rgba(6,46,111,0.08);
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            font-family: inherit;
            font-size: 10px;
            height: 48px;
            line-height:1;
        }
        .kpi-title-temporal { color: rgba(255,255,255,0.9); font-size: 9px; margin-bottom: 1px; font-weight:600; }
        .kpi-value-temporal { color: #ffffff; font-size: 12px; font-weight: 700; line-height: 1; }
        .kpi-delta-temporal { display: inline-block; margin-left: 4px; font-size: 9px; vertical-align: middle; }
        .delta-green-temporal { color: #4CAF50; font-weight:600; }
        .delta-red-temporal { color: #f44336; font-weight:600; }
        .delta-neutral-temporal { color: #fff200; font-weight:600; }
        </style>
    """, unsafe_allow_html=True)

    # render dos 4 cards
    return      st.markdown(f"""
                    <div class="kpis-row-temporal">
                        <div class="kpi-card-temporal">
                            <div class="kpi-title-temporal">Total 12 meses</div>
                            <div class="kpi-value-temporal">{total_12_meses:,}</div>
                        </div>
                        <div class="kpi-card-temporal">
                            <div class="kpi-title-temporal">Média mensal</div>
                            <div class="kpi-value-temporal">{media_mensal_12m:.1f}</div>
                        </div>
                        <div class="kpi-card-temporal">
                            <div class="kpi-title-temporal">Pico mensal</div>
                            <div class="kpi-value-temporal">{max_mes if max_mes is not None else 'N/A'}{kpi_pico_extra}</div>
                        </div>
                        <div class="kpi-card-temporal">
                            <div class="kpi-title-temporal">Média / dia útil</div>
                            <div class="kpi-value-temporal">{f"{media_dia_util:.1f}" if media_dia_util is not None else 'N/A'}</div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)


def render_graficos_temporal(df):
    """
    Renderiza os dois gráficos (um abaixo do outro) usando df com 'data_convertida' datetime.
    Recebe df já validado/normalizado.
    """
    if df is None:
        st.warning("Dados não fornecidos para os gráficos temporais.")
        return

    hoje = pd.Timestamp.now()
    # preparar métricas de 12 meses necessárias para o gráfico mensal
    doze_meses_atras = hoje - pd.DateOffset(months=12)
    df_12_meses = df[df['data_convertida'] >= doze_meses_atras].copy()
    df_12_meses['mes_ano'] = df_12_meses['data_convertida'].dt.to_period('M')
    processos_por_mes = df_12_meses.groupby('mes_ano').size().reset_index(name='quantidade')
    processos_por_mes['mes_ano_str'] = processos_por_mes['mes_ano'].astype(str)
    media_mensal_12m = processos_por_mes['quantidade'].mean() if len(processos_por_mes) > 0 else 0
    max_mes = int(processos_por_mes['quantidade'].max()) if len(processos_por_mes) > 0 else None

    
    tipo_analise = st.selectbox('Escolha o tipo de análise', ['Nº de processos', 'Nº médio de processos'], key='rg_tipo_analise')

    if tipo_analise == 'Nº de processos':
            # um abaixo do outro (sem duplicações)
            # --- Nº de processos por dia no mês corrente (somente dias úteis) ---
            mes_atual = hoje.month
            ano_atual = hoje.year
            df_mes_corrente = df[
                (df['data_convertida'].dt.month == mes_atual) &
                (df['data_convertida'].dt.year == ano_atual)
            ].copy()

            df_mes_corrente['dia_semana'] = df_mes_corrente['data_convertida'].dt.dayofweek
            df_mes_corrente_uteis = df_mes_corrente[df_mes_corrente['dia_semana'].between(0, 4)]

            render_4_cards_temporal(df)
            tab1, tab2 = st.tabs(['último mes', 'últimos 12 meses'])


            with tab1:
                    st.markdown("**Nº de processos por dia no mês corrente (somente dias úteis)**")
                    if df_mes_corrente_uteis.empty:
                        st.info("Nenhum processo no mês corrente (dias úteis).")
                    else:
                        df_mes_corrente_uteis['data_only'] = df_mes_corrente_uteis['data_convertida'].dt.date
                        processos_por_dia_mes = df_mes_corrente_uteis.groupby('data_only').size().reset_index(name='processos')
                        processos_por_dia_mes = processos_por_dia_mes.sort_values('data_only')
                        processos_por_dia_mes['dia_label'] = processos_por_dia_mes['data_only'].apply(lambda d: pd.Timestamp(d).strftime('%d/%m'))
                        media_mes_corrente = processos_por_dia_mes['processos'].mean() if len(processos_por_dia_mes) > 0 else 0

                        st.markdown(f"""
                            <div style="display:flex;align-items:center;gap:6px;margin-bottom:6px;margin-top:4px;">
                                <span style="display:inline-block;width:34px;height:6px;background:rgba(123,102,84,0.95);border-radius:3px;"></span>
                                <div style="font-size:11px;color:#7b6654;line-height:1;"><b>Média</b>: <span style="color:#d35400;font-weight:600;">{media_mes_corrente:.1f}</span></div>
                            </div>
                        """, unsafe_allow_html=True)

                        fig_dia_mes = px.bar(processos_por_dia_mes, x='dia_label', y='processos', color_discrete_sequence=['#5B9BD5'])
                        fig_dia_mes.update_traces(texttemplate='%{y}', textposition='outside')
                        max_chart_day = processos_por_dia_mes['processos'].max() if len(processos_por_dia_mes) > 0 else 1
                        fig_dia_mes.update_yaxes(range=[0, max_chart_day * 1.18], showticklabels=False)
                        fig_dia_mes.add_hline(y=media_mes_corrente, line_color="rgba(211,84,0,0.6)", line_width=2, line_dash="dash")
                        fig_dia_mes.update_layout(xaxis_title="", yaxis_title="", height=220, showlegend=False, margin=dict(t=30, b=20, l=20, r=20))
                        st.plotly_chart(fig_dia_mes, use_container_width=True, key='grafico_dia_mes_corrente')

            with tab2:
                    # --- Processos por Mês (Últimos 12 meses) ---
                    st.markdown("**Processos por Mês (Últimos 12 meses)**")
                    if processos_por_mes.empty:
                        st.info("Nenhum processo nos últimos 12 meses.")
                    else:
                        media_mensal = media_mensal_12m
                        st.markdown(f"""
                            <div style="display:flex;align-items:center;gap:6px;margin-bottom:6px;margin-top:4px;">
                                <span style="display:inline-block;width:34px;height:6px;background:rgba(123,102,84,0.95);border-radius:3px;"></span>
                                <div style="font-size:11px;color:#7b6654;line-height:1;"><b>Média</b>: <span style="color:#d35400;font-weight:600;">{media_mensal:.1f}</span></div>
                            </div>
                        """, unsafe_allow_html=True)

                        fig_temporal = px.bar(
                            processos_por_mes,
                            x='mes_ano_str',
                            y='quantidade',
                            color_discrete_sequence=['steelblue']
                        )
                        fig_temporal.update_traces(texttemplate='%{y}', textposition='outside')
                        max_chart = max_mes if (max_mes is not None and max_mes > 0) else (processos_por_mes['quantidade'].max() if len(processos_por_mes) > 0 else 1)
                        fig_temporal.update_yaxes(range=[0, max_chart * 1.18], showticklabels=False)
                        fig_temporal.add_hline(y=media_mensal, line_color="rgba(211,84,0,0.6)", line_width=2, line_dash="dash")
                        fig_temporal.update_layout(xaxis_title="", yaxis_title="", height=220, showlegend=False, margin=dict(t=30, b=20, l=20, r=20))
                        st.plotly_chart(fig_temporal, use_container_width=True, key='grafico_temporal')

    if tipo_analise == 'Nº médio de processos':
         # Média por dia da semana - Mês corrente (somente dias úteis)
         render_4_cards_temporal(df)

         tab1, tab2 = st.tabs(['último mes', 'últimos 12 meses'])

         with tab1:
             st.markdown("**Número médio de processos por dia da semana — mês corrente (somente dias úteis)**")
             mes_atual = hoje.month
             ano_atual = hoje.year
             df_mes_corrente = df[
                 (df['data_convertida'].dt.month == mes_atual) &
                 (df['data_convertida'].dt.year == ano_atual)
             ].copy()

             df_mes_corrente['dia_semana'] = df_mes_corrente['data_convertida'].dt.dayofweek
             df_mes_corrente_uteis = df_mes_corrente[df_mes_corrente['dia_semana'].between(0, 4)]

             if df_mes_corrente_uteis.empty:
                 st.info("Nenhum processo no mês corrente (dias úteis).")
             else:
                 # contar por data, depois agregar por dia da semana e tirar média
                 df_mes_corrente_uteis['data_only'] = df_mes_corrente_uteis['data_convertida'].dt.date
                 processos_por_dia = df_mes_corrente_uteis.groupby('data_only').size().reset_index(name='processos')
                 processos_por_dia['dia_semana'] = pd.to_datetime(processos_por_dia['data_only']).dt.dayofweek
                 weekday_means = processos_por_dia.groupby('dia_semana')['processos'].mean().reindex([0,1,2,3,4], fill_value=0)
                 labels = ['Seg', 'Ter', 'Qua', 'Qui', 'Sex']
                 values = [weekday_means.get(i, 0) for i in range(5)]
                 overall_mean = sum(values) / len([v for v in values if v is not None]) if len(values) > 0 else 0

                 st.markdown(f"""
                     <div style="display:flex;align-items:center;gap:6px;margin-bottom:6px;margin-top:4px;">
                         <span style="display:inline-block;width:34px;height:6px;background:rgba(123,102,84,0.95);border-radius:3px;"></span>
                         <div style="font-size:11px;color:#7b6654;line-height:1;"><b>Média</b>: <span style="color:#d35400;font-weight:600;">{overall_mean:.2f}</span></div>
                     </div>
                 """, unsafe_allow_html=True)

                 df_plot = pd.DataFrame({'dia': labels, 'media': values})
                 fig_avg_weekday = px.bar(df_plot, x='dia', y='media', color_discrete_sequence=['#5B9BD5'])
                 fig_avg_weekday.update_traces(texttemplate='%{y:.2f}', textposition='outside')
                 max_chart = max(values) if len(values) > 0 else 1
                 fig_avg_weekday.update_yaxes(range=[0, max_chart * 1.18], showticklabels=False)
                 fig_avg_weekday.add_hline(y=overall_mean, line_color="rgba(211,84,0,0.6)", line_width=2, line_dash="dash")
                 fig_avg_weekday.update_layout(xaxis_title="", yaxis_title="", height=220, showlegend=False, margin=dict(t=30, b=20, l=20, r=20))
                 st.plotly_chart(fig_avg_weekday, use_container_width=True, key='grafico_media_dia_semana_mes_corrente')

         with tab2:
             st.markdown("**Média por Dia da Semana (Últimos 12 meses)**")
             # usar df_12_meses já preparado mais acima
             df_12_uteis = df_12_meses.copy()
             df_12_uteis['dia_semana'] = df_12_uteis['data_convertida'].dt.dayofweek
             df_12_uteis = df_12_uteis[df_12_uteis['dia_semana'].between(0,4)]

             if df_12_uteis.empty:
                 st.info("Nenhum processo nos últimos 12 meses (dias úteis).")
             else:
                 df_12_uteis['data_only'] = df_12_uteis['data_convertida'].dt.date
                 processos_por_dia_12m = df_12_uteis.groupby('data_only').size().reset_index(name='processos')
                 processos_por_dia_12m['dia_semana'] = pd.to_datetime(processos_por_dia_12m['data_only']).dt.dayofweek
                 weekday_means_12m = processos_por_dia_12m.groupby('dia_semana')['processos'].mean().reindex([0,1,2,3,4], fill_value=0)
                 labels = ['Seg', 'Ter', 'Qua', 'Qui', 'Sex']
                 values_12m = [weekday_means_12m.get(i, 0) for i in range(5)]
                 overall_mean_12m = sum(values_12m) / len([v for v in values_12m if v is not None]) if len(values_12m) > 0 else 0

                 st.markdown(f"""
                     <div style="display:flex;align-items:center;gap:6px;margin-bottom:6px;margin-top:4px;">
                         <span style="display:inline-block;width:34px;height:6px;background:rgba(123,102,84,0.95);border-radius:3px;"></span>
                         <div style="font-size:11px;color:#7b6654;line-height:1;"><b>Média</b>: <span style="color:#d35400;font-weight:600;">{overall_mean_12m:.2f}</span></div>
                     </div>
                 """, unsafe_allow_html=True)

                 df_plot_12m = pd.DataFrame({'dia': labels, 'media': values_12m})
                 fig_avg_weekday_12m = px.bar(df_plot_12m, x='dia', y='media', color_discrete_sequence=['steelblue'])
                 fig_avg_weekday_12m.update_traces(texttemplate='%{y:.2f}', textposition='outside')
                 max_chart = max(values_12m) if len(values_12m) > 0 else 1
                 fig_avg_weekday_12m.update_yaxes(range=[0, max_chart * 1.18], showticklabels=False)
                 fig_avg_weekday_12m.add_hline(y=overall_mean_12m, line_color="rgba(211,84,0,0.6)", line_width=2, line_dash="dash")
                 fig_avg_weekday_12m.update_layout(xaxis_title="", yaxis_title="", height=220, showlegend=False, margin=dict(t=30, b=20, l=20, r=20))
                 st.plotly_chart(fig_avg_weekday_12m, use_container_width=True, key='grafico_media_dia_semana_12m')