import streamlit as st
import pandas as pd
from datetime import datetime, timedelta


def visao_geral(df_filtrado, aplicar_filtro_configurado):
    """Visão geral com KPIs principais e últimos processos - COM FILTRO APLICADO"""
    # APLICAR FILTRO AQUI TAMBÉM
    df_filtrado = aplicar_filtro_configurado(df_filtrado)
        
    # KPIs de novos processos - AGORA COMO MARKDOWN
    st.markdown("#### Novos Processos")
    
    # CSS para os novos cards
    st.markdown("""
        <style>
        .processo-card {
            background-color: #062e6f;  /* Azul escuro */
            padding: 15px;
            border-radius: 10px;
            height: 200px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
        }
        .processo-titulo {
            color: #e0e0e0;
            font-size: 13px;
            font-weight: 500;
            margin-bottom: 6px;
            text-align: center;
        }
        .processo-valor {
            color: white;
            font-size: 26px;
            font-weight: 700;
            margin-bottom: 4px;
            line-height: 1;
            text-align: center;
        }
        .processo-media {
            font-size: 13px;
            line-height: 1.4;
            padding: 3px 8px;
            border-radius: 4px;
            display: inline-block;
            font-weight: 500;
            text-align: center;
        }
        .processo-media .media-label { color: #bdbdbd; margin-right:6px; }
        .processo-media .media-value { color: #ffffff; font-weight:700; }
        .media-verde {
            background-color: #4CAF50 !important;
        }
        .media-vermelha {
            background-color: #f44336 !important;
        }
        .media-amarela {
            background-color: #FFC107 !important;
        }
        .periodo-title {
            font-size: 16px;
            font-weight: 600;
            color: #333;
            text-align: center;
            margin-bottom: 10px;
        }
        .percentual-info {
            font-size: 14px;
            color: #666;
            text-align: center;
            margin-top: 10px;
        }
        </style>
    """, unsafe_allow_html=True)
    
    if 'data_convertida' in df_filtrado.columns:
        # Calcular datas
        hoje = pd.Timestamp.now().normalize()
        
        # 1. ÚLTIMO DIA ÚTIL
        ultimo_dia_util = hoje - pd.Timedelta(days=1)
        while ultimo_dia_util.weekday() > 4:
            ultimo_dia_util = ultimo_dia_util - pd.Timedelta(days=1)
        
        # 2. SEMANA PASSADA (segunda a sexta)
        dias_desde_segunda = hoje.weekday()
        inicio_semana = hoje - pd.Timedelta(days=dias_desde_segunda + 7)
        fim_semana = inicio_semana + pd.Timedelta(days=4)
        
        # 3. ESTE MÊS
        primeiro_dia_mes = hoje.replace(day=1)
        
        # CALCULAR MÉDIAS HISTÓRICAS
        seis_meses_atras = hoje - pd.DateOffset(months=6)
        doze_meses_atras = hoje - pd.DateOffset(months=12)
        
        # Dados dos últimos 6 meses para média diária
        df_6_meses = df_filtrado[df_filtrado['data_convertida'] >= seis_meses_atras]
        
        # Dados dos últimos 12 meses para média mensal
        df_12_meses = df_filtrado[df_filtrado['data_convertida'] >= doze_meses_atras]
        
        # MÉDIA DIÁRIA (últimos 6 meses) - apenas dias úteis
        df_6_meses_uteis = df_6_meses[df_6_meses['data_convertida'].dt.weekday < 5]  # 0-4 = segunda a sexta
        dias_uteis_6m = df_6_meses_uteis['data_convertida'].dt.date.nunique()
        
        if dias_uteis_6m > 0:
            media_diaria_geral = len(df_6_meses_uteis) / dias_uteis_6m
            if 'tipoPrincipal' in df_filtrado.columns:
                media_diaria_prev = len(df_6_meses_uteis[df_6_meses_uteis['tipoPrincipal'] == 'ACAO PREVIDENCIARIA']) / dias_uteis_6m
            else:
                media_diaria_prev = 0
        else:
            media_diaria_geral = 0
            media_diaria_prev = 0
        
        # MÉDIA SEMANAL (últimos 6 meses)
        df_6_meses_copia = df_6_meses.copy()  # Criar cópia para evitar warning
        df_6_meses_copia['semana'] = df_6_meses_copia['data_convertida'].dt.to_period('W')
        semanas_6m = df_6_meses_copia['semana'].nunique()
        
        if semanas_6m > 0:
            media_semanal_geral = len(df_6_meses) / semanas_6m
            if 'tipoPrincipal' in df_filtrado.columns:
                media_semanal_prev = len(df_6_meses[df_6_meses['tipoPrincipal'] == 'ACAO PREVIDENCIARIA']) / semanas_6m
            else:
                media_semanal_prev = 0
        else:
            media_semanal_geral = 0
            media_semanal_prev = 0
        
        # MÉDIA MENSAL (últimos 12 meses)
        df_12_meses_copia = df_12_meses.copy()  # Criar cópia para evitar warning
        df_12_meses_copia['mes'] = df_12_meses_copia['data_convertida'].dt.to_period('M')
        meses_12m = df_12_meses_copia['mes'].nunique()
        
        if meses_12m > 0:
            media_mensal_geral = len(df_12_meses) / meses_12m
            if 'tipoPrincipal' in df_filtrado.columns:
                media_mensal_prev = len(df_12_meses[df_12_meses['tipoPrincipal'] == 'ACAO PREVIDENCIARIA']) / meses_12m
            else:
                media_mensal_prev = 0
        else:
            media_mensal_geral = 0
            media_mensal_prev = 0
        
        # CALCULAR VALORES ATUAIS
        # Último dia útil
        processos_ultimo_dia = df_filtrado[df_filtrado['data_convertida'].dt.date == ultimo_dia_util.date()]
        processos_ultimo_dia_geral = len(processos_ultimo_dia)
        processos_ultimo_dia_prev = len(processos_ultimo_dia[processos_ultimo_dia['tipoPrincipal'] == 'ACAO PREVIDENCIARIA']) if 'tipoPrincipal' in df_filtrado.columns else 0
        
        # Semana passada
        processos_semana = df_filtrado[
            (df_filtrado['data_convertida'] >= inicio_semana) &
            (df_filtrado['data_convertida'] <= fim_semana)
        ]
        processos_semana_geral = len(processos_semana)
        processos_semana_prev = len(processos_semana[processos_semana['tipoPrincipal'] == 'ACAO PREVIDENCIARIA']) if 'tipoPrincipal' in df_filtrado.columns else 0
        
        # Este mês
        processos_mes = df_filtrado[df_filtrado['data_convertida'] >= primeiro_dia_mes]
        processos_mes_geral = len(processos_mes)
        processos_mes_prev = len(processos_mes[processos_mes['tipoPrincipal'] == 'ACAO PREVIDENCIARIA']) if 'tipoPrincipal' in df_filtrado.columns else 0
        
        # FUNÇÃO PARA DETERMINAR COR
        def get_cor_media(valor_atual, media_historica):
            if valor_atual > media_historica:
                return "media-verde"
            elif valor_atual < media_historica:
                return "media-vermelha"
            else:
                return "media-amarela"
        
        # Formatação das datas
        data_ultimo_dia = ultimo_dia_util.strftime('%d/%m/%Y')
        data_inicio_semana = inicio_semana.strftime('%d/%m')
        data_fim_semana = fim_semana.strftime('%d/%m')
        
        # Layout dos Cards - ÚNICA LINHA com 3 colunas (cada coluna = um período)
        # Usar HTML/CSS para garantir que cada análise fique em uma única linha horizontal
        st.markdown("""
            <style>
            .periodo-container {
                display: flex;
                flex-direction: column;
                align-items: center;
            }
            .processos-row {
                display: flex;
                gap: 8px;
                width: 100%;
                justify-content: center;
            }
            .processo-card-inline {
                background-color: #062e6f;
                padding: 10px;
                border-radius: 8px;
                width: 48%;
                box-shadow: 0 2px 4px rgba(0,0,0,0.08);
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
            }
            .processo-titulo { color: #e0e0e0; font-size:13px; font-weight:500; margin-bottom:6px; text-align:center; }
            .processo-valor { color: white; font-size:22px; font-weight:700; margin-bottom:4px; text-align:center; }
            .processo-media { font-size:12px; padding:3px 6px; border-radius:4px; color:#fff; font-weight:600; }
            .percentual-inline { font-size:13px; color:#444; margin-top:6px; text-align:center; }
            </style>
        """, unsafe_allow_html=True)

        periodos = [
            {
                "titulo": f"Último dia útil ({data_ultimo_dia})",
                "geral_val": processos_ultimo_dia_geral,
                "prev_val": processos_ultimo_dia_prev,
                "media_geral": media_diaria_geral,
                "media_prev": media_diaria_prev
            },
            {
                "titulo": f"Semana Passada ({data_inicio_semana} a {data_fim_semana})",
                "geral_val": processos_semana_geral,
                "prev_val": processos_semana_prev,
                "media_geral": media_semanal_geral,
                "media_prev": media_semanal_prev
            },
            {
                "titulo": "Este Mês",
                "geral_val": processos_mes_geral,
                "prev_val": processos_mes_prev,
                "media_geral": media_mensal_geral,
                "media_prev": media_mensal_prev
            }
        ]

        cols = st.columns(3)
        for i, periodo in enumerate(periodos):
            with cols[i]:
                # montar HTML inline para garantir única linha horizontal por análise
                geral = periodo["geral_val"]
                prev = periodo["prev_val"]
                perc = (prev / geral * 100) if geral > 0 else 0

                # determinar classes de cor para as médias (verde/vermelho/amarelo)
                cor_media_geral = get_cor_media(periodo["geral_val"], periodo["media_geral"])
                cor_media_prev = get_cor_media(periodo["prev_val"], periodo["media_prev"])

                html = f'''
                    <div class="periodo-container">
                        <div class="periodo-title">{periodo["titulo"]}</div>
                        <div class="processos-row">
                            <div class="processo-card-inline">
                                <div class="processo-titulo">Geral</div>
                                <div class="processo-valor">{periodo["geral_val"]}</div>
                                <div class="processo-media {cor_media_geral}">Média: {periodo["media_geral"]:.1f}</div>
                            </div>
                            <div class="processo-card-inline">
                                <div class="processo-titulo">Previdenciário</div>
                                <div class="processo-valor">{periodo["prev_val"]}</div>
                                <div class="processo-media {cor_media_prev}">Média: {periodo["media_prev"]:.1f}</div>
                            </div>
                        </div>
                        <div class="percentual-inline">🔍 {perc:.1f}% previdenciárias</div>
                    </div>
                '''
                st.markdown(html, unsafe_allow_html=True)
    
    else:
        st.warning("⚠️ Dados de data não disponíveis para cálculo de KPIs")

    
    # Tabela dos últimos 5 processos
    st.markdown("---")
    st.markdown("### 📋 Últimos 5 Processos")
    
    if len(df_filtrado) > 0:
        # Ordenar por data (mais recentes primeiro)
        if 'data_convertida' in df_filtrado.columns:
            df_recentes = df_filtrado.sort_values('data_convertida', ascending=False).head(5)
        else:
            df_recentes = df_filtrado.head(5)
        
        # Preparar dados para a tabela
        tabela_processos = []
        
        for _, row in df_recentes.iterrows():
            # Número do processo
            num_processo = row.get('numeroProcesso', row.get('numero', 'N/A'))
            
            # Data formatada
            if 'data_convertida' in row and pd.notna(row['data_convertida']):
                data_formatada = row['data_convertida'].strftime('%d/%m/%Y')
            else:
                data_formatada = 'N/A'
            
            # Nome do cliente
            nome_cliente = row.get('nome', row.get('nomeCliente', 'N/A'))
            if pd.notna(nome_cliente) and len(str(nome_cliente)) > 30:
                nome_cliente = str(nome_cliente)[:27] + "..."
            
            # MUDANÇA: usar tipoProcesso ao invés de tipoPrincipal
            tipo_processo = row.get('tipoProcesso', 'N/A')
            
            # Cidade
            cidade = row.get('cidade_upper', row.get('cidade', 'N/A'))
            if pd.notna(cidade) and len(str(cidade)) > 20:
                cidade = str(cidade)[:17] + "..."
            
            tabela_processos.append({
                'Nº Processo': num_processo,
                'Data': data_formatada,
                'Cliente': nome_cliente,
                'Tipo': tipo_processo,  # Agora usando tipoProcesso
                'Cidade': cidade
            })
        
        # Criar DataFrame
        df_tabela = pd.DataFrame(tabela_processos)
        
        # Exibir tabela
        st.dataframe(
            df_tabela,
            use_container_width=True,
            hide_index=True,
            height=220,
            column_config={
                "Nº Processo": st.column_config.TextColumn(
                    "Nº Processo",
                    help="Número do processo"
                ),
                "Data": st.column_config.TextColumn(
                    "Data",
                    help="Data de registro"
                ),
                "Cliente": st.column_config.TextColumn(
                    "Cliente",
                    help="Nome do cliente"
                ),
                "Tipo": st.column_config.TextColumn(
                    "Tipo do Processo",
                    help="Tipo original do processo"
                ),
                "Cidade": st.column_config.TextColumn(
                    "Cidade",
                    help="Cidade do cliente"
                )
            }
        )
                   
    else:
        st.warning("⚠️ Nenhum processo encontrado com os filtros aplicados")
