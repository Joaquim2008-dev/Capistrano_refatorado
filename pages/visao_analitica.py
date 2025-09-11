import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import sys
from pathlib import Path
from unidecode import unidecode
from datetime import datetime, timedelta

# Adicionar path do projeto
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from data.data_loader import carregar_e_processar_dados, filtrar_sergipe
from utils.text_processing import padronizar_reu, padronizar_competencia, categorizar_tipo_processo, normalizar_profissao
from utils.calculations import calcular_idade_processos, calcular_idade_clientes
from components.filters import aplicar_filtros_temporais

# =====================================
# CONFIGURAÇÃO DE FILTRO DE ANO
# =====================================
# Descomente UMA das opções abaixo:

# OPÇÃO 1: VERSÃO COMPLETA (todos os anos)
FILTRO_ANO_ATIVO = False
ANO_FILTRO = None

# OPÇÃO 2: VERSÃO APENAS 2025 
# FILTRO_ANO_ATIVO = True
# ANO_FILTRO = 2025

# =====================================

def aplicar_filtro_configurado(df):
    """Aplica filtro de ano baseado na configuração acima"""
    if not FILTRO_ANO_ATIVO or ANO_FILTRO is None:
        return df
    
    if 'data_convertida' in df.columns:
        df_filtrado = df[df['data_convertida'].dt.year == ANO_FILTRO].copy()
        return df_filtrado
    elif 'data' in df.columns:
        # Se ainda não converteu a data
        df['data_convertida'] = pd.to_datetime(df['data'], errors='coerce')
        df_filtrado = df[df['data_convertida'].dt.year == ANO_FILTRO].copy()
        return df_filtrado
    
    return df

def pagina_visao_analitica():
    """Página de análise detalhada dos processos"""
    
    # Título com indicação de filtro se ativo
    if FILTRO_ANO_ATIVO and ANO_FILTRO:
        st.title(f"📊 Visão Analítica dos Processos ({ANO_FILTRO})")
        st.markdown(f"### Análises detalhadas - Ano {ANO_FILTRO}")
    else:
        st.title("📊 Visão Analítica dos Processos")
        st.markdown("### Análises detalhadas sobre perfil, idade e características dos processos")
    
    # Carregar e preparar dados
    df = carregar_e_processar_dados()
    if df is None:
        st.error("❌ Erro ao carregar dados das APIs")
        st.stop()
    
    df_sergipe = filtrar_sergipe(df)
    if df_sergipe is None or len(df_sergipe) == 0:
        st.warning("⚠️ Nenhum processo encontrado em Sergipe")
        st.stop()
    
    # APLICAR FILTRO CONFIGURADO
    df_sergipe = aplicar_filtro_configurado(df_sergipe)
    
    if len(df_sergipe) == 0:
        st.warning(f"⚠️ Nenhum processo encontrado em Sergipe para {ANO_FILTRO}")
        st.stop()
    
    # Preparar dados para análise
    df_analise = preparar_dados_analise(df_sergipe)
    
    # FILTROS - OCULTAR SE FILTRO DE ANO ATIVO
    if FILTRO_ANO_ATIVO and ANO_FILTRO:
        # Não mostrar filtros, apenas informação
        df_filtrado = df_analise  # Usar dados sem filtros adicionais
    else:
        # Mostrar filtros normais
        df_filtrado = aplicar_filtros_temporais(df_analise)
    
    
    # KPIs
    mostrar_kpis_principais(df_filtrado)
    
    # Abas - VOLTAR PARA O PADRÃO SIMPLES
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "📊 Visão Geral",
        "📈 Análise Temporal", 
        "⚖️ Réus & Competênica", 
        "👥 Perfil dos Clientes", 
        "💼 Profissões",
        "🎯 Prospectores"
    ])

    with tab1:
        visao_geral(df_filtrado)
    
    with tab2:
        analise_temporal(df_filtrado)
    
    with tab3:
        analise_reus_procedencia(df_filtrado)
    
    with tab4:
        analise_perfil_clientes(df_filtrado)
    
    with tab5:
        analise_profissoes(df_filtrado)
    
    with tab6:
        analise_prospectors(df_filtrado)
    
    
def preparar_dados_analise(df_sergipe):
    """Prepara dados específicos para análise"""
    df_analise = df_sergipe.copy()
    
    # 1. Calcular idades de forma mais robusta
    try:
        df_analise = calcular_idade_processos(df_analise)
    except Exception as e:
        print(f"Erro ao calcular idade dos processos: {e}")
        # Fallback manual
        if 'data' in df_analise.columns:
            try:
                df_analise['data_convertida'] = pd.to_datetime(df_analise['data'], errors='coerce')
                hoje = pd.Timestamp('now')
                df_analise['idade_processo_dias'] = (hoje - df_analise['data_convertida']).dt.days
                df_analise['idade_processo_anos'] = df_analise['idade_processo_dias'] / 365.25
            except:
                df_analise['idade_processo_anos'] = None
    
    try:
        df_analise = calcular_idade_clientes(df_analise)
    except Exception as e:
        print(f"Erro ao calcular idade dos clientes: {e}")
        df_analise['idade_cliente_anos'] = None
    
    # 2. Normalizar réus
    if 'reu' in df_analise.columns:
        try:
            df_analise['reu_ajustado'] = df_analise['reu'].apply(padronizar_reu)
        except:
            df_analise['reu_ajustado'] = df_analise['reu']
    
    # 3. Normalizar competência
    if 'competencia' in df_analise.columns:
        try:
            df_analise['competencia_ajustada'] = df_analise['competencia'].apply(padronizar_competencia)
        except:
            df_analise['competencia_ajustada'] = df_analise['competencia']
    
    # 4. Normalizar profissão com nova função robusta
    if 'profissaoTexto' in df_analise.columns:
        try:
            # Primeiro aplicar normalização básica
            df_analise['profissao_basica'] = df_analise['profissaoTexto'].apply(
                lambda x: unidecode(str(x).upper().strip()) if pd.notna(x) and str(x).strip() != '' else 'NÃO INFORMADO'
            )
            
            # Depois aplicar normalização avançada
            df_analise['profissao_normalizada'] = df_analise['profissao_basica'].apply(normalizar_profissao)
            
        except Exception as e:
            print(f"Erro ao normalizar profissões: {e}")
            df_analise['profissao_normalizada'] = df_analise['profissaoTexto']
    
    
    # 5. Categorizar tipos
    if 'tipoProcesso' in df_analise.columns:
        try:
            df_analise['tipoPrincipal'] = df_analise['tipoProcesso'].apply(categorizar_tipo_processo)
        except:
            df_analise['tipoPrincipal'] = 'OUTROS'
    
    return df_analise

def mostrar_kpis_principais(df_analise):
    """Mostra KPIs principais - COM FILTRO APLICADO"""
    # APLICAR FILTRO AQUI TAMBÉM
    df_analise = aplicar_filtro_configurado(df_analise)
    
    st.markdown("---")
    st.subheader("📈 Indicadores Básicos")

    col_kpi1, col_kpi2, col_kpi3, col_kpi4 = st.columns(4)
    
    with col_kpi1:
        if 'idade_processo_anos' in df_analise.columns:
            idade_media_processos = df_analise['idade_processo_anos'].mean()
            st.metric(
                "⏰ Idade Média Processos",
                f"{idade_media_processos:.1f} anos" if pd.notna(idade_media_processos) else "N/A"
            )
        else:
            st.metric("⏰ Idade Média Processos", "N/A")
    
    with col_kpi2:
        if 'idade_cliente_anos' in df_analise.columns:
            idade_media_clientes = df_analise['idade_cliente_anos'].mean()
            st.metric(
                "👥 Idade Média Clientes",
                f"{idade_media_clientes:.1f} anos" if pd.notna(idade_media_clientes) else "N/A"
            )
        else:
            st.metric("👥 Idade Média Clientes", "N/A")
    
    with col_kpi3:
        total_processos_periodo = len(df_analise)
        st.metric(
            "📊 Processos no Período",
            f"{total_processos_periodo:,}"
        )
    
    with col_kpi4:
        if 'prospector' in df_analise.columns:
            com_prospector = df_analise['prospector'].notna().sum()
            percentual_prospector = (com_prospector / len(df_analise) * 100) if len(df_analise) > 0 else 0
            st.metric(
                "🎯 % com Prospector",
                f"{percentual_prospector:.1f}%"
            )
        else:
            st.metric("🎯 % com Prospector", "N/A")

def analise_temporal(df_analise):
    """Análise temporal com os 3 gráficos - COM FILTRO APLICADO"""
    # APLICAR FILTRO AQUI TAMBÉM
    df_analise = aplicar_filtro_configurado(df_analise)
    
    st.subheader("📈 Análise Temporal")

    if 'data_convertida' not in df_analise.columns:
        st.warning("Dados de data não disponíveis")
        return
    
    # SIMPLIFICAÇÃO: Usar apenas pd.Timestamp.now()
    hoje = pd.Timestamp.now()
    
    # Filtrar últimos 12 meses
    doze_meses_atras = hoje - pd.DateOffset(months=12)
    df_12_meses = df_analise[df_analise['data_convertida'] >= doze_meses_atras]
     
    if len(df_12_meses) > 0:
        # Layout com 3 colunas para os gráficos
        col_graf1, col_graf2, col_graf3 = st.columns(3)
        
        with col_graf1:
            st.markdown("**📊 Processos por Mês (Últimos 12 meses)**")
            
            # Agrupar por mês
            df_12_meses['mes_ano'] = df_12_meses['data_convertida'].dt.to_period('M')
            processos_por_mes = df_12_meses.groupby('mes_ano').size().reset_index(name='quantidade')
            processos_por_mes['mes_ano_str'] = processos_por_mes['mes_ano'].astype(str)
            
            # Calcular média mensal dos últimos 12 meses
            media_mensal_12m = processos_por_mes['quantidade'].mean()
            
            fig_temporal = px.bar(
                processos_por_mes,
                x='mes_ano_str',
                y='quantidade',
                color_discrete_sequence=['steelblue']
            )
            
            # Adicionar números no topo das barras
            fig_temporal.update_traces(
                texttemplate='%{y}',
                textposition='outside'
            )
            
            # Adicionar linha de média mensal
            fig_temporal.add_hline(
                y=media_mensal_12m,
                line_color="orange",
                line_width=2,
                line_dash="dash",
                annotation_text=f"Média: {media_mensal_12m:.1f}",
                annotation_position="top right"
            )
            
            fig_temporal.update_layout(
                xaxis_title="",
                yaxis_title="",
                height=400,
                showlegend=False,
                margin=dict(t=50, b=20, l=20, r=20)
            )
            st.plotly_chart(fig_temporal, use_container_width=True, key='grafico_temporal')
        
        with col_graf2:
            st.markdown("**📅 Média por Dia da Semana (Últimos 12 meses)**")
            
            # Adicionar dia da semana (0=Segunda, 6=Domingo)
            df_12_meses['dia_semana'] = df_12_meses['data_convertida'].dt.dayofweek
            df_12_meses['nome_dia'] = df_12_meses['data_convertida'].dt.day_name()
            
            # Filtrar apenas dias úteis (Segunda a Sexta: 0-4)
            df_dias_uteis = df_12_meses[df_12_meses['dia_semana'].between(0, 4)]
            
            # Mapear nomes dos dias em português
            mapa_dias = {
                'Monday': 'Segunda',
                'Tuesday': 'Terça',
                'Wednesday': 'Quarta',
                'Thursday': 'Quinta',
                'Friday': 'Sexta'
            }
            
            if len(df_dias_uteis) > 0:
                # Agrupar por dia da semana e calcular média
                processos_por_dia_semana = df_dias_uteis.groupby(['nome_dia', 'dia_semana']).size().reset_index(name='total_processos')
                
                # Calcular quantas semanas temos nos dados para fazer a média
                weeks_count = df_dias_uteis['data_convertida'].dt.to_period('W').nunique()
                
                media_por_dia = processos_por_dia_semana.groupby(['nome_dia', 'dia_semana'])['total_processos'].sum().reset_index()
                media_por_dia['media'] = media_por_dia['total_processos'] / max(weeks_count, 1)
                media_por_dia['dia_pt'] = media_por_dia['nome_dia'].map(mapa_dias)
                
                # Ordenar por dia da semana
                media_por_dia = media_por_dia.sort_values('dia_semana')
                
                # Calcular média geral da semana
                media_geral_semana = media_por_dia['media'].mean()
                
                fig_dia_semana = px.bar(
                    media_por_dia,
                    x='dia_pt',
                    y='media',
                    color_discrete_sequence=['#8B4513']  # Marrom escuro
                )
                
                # Adicionar números no topo
                fig_dia_semana.update_traces(
                    texttemplate='%{y:.1f}',
                    textposition='outside'
                )
                
                # Adicionar linha de média
                fig_dia_semana.add_hline(
                    y=media_geral_semana,
                    line_color="orange",
                    line_width=2,
                    line_dash="dash",
                    annotation_text=f"Média: {media_geral_semana:.1f}",
                    annotation_position="top right"
                )
                
                fig_dia_semana.update_layout(
                    xaxis_title="",
                    yaxis_title="",
                    height=400,
                    showlegend=False,
                    margin=dict(t=50, b=20, l=20, r=20)
                )
                st.plotly_chart(fig_dia_semana, use_container_width=True, key='grafico_dia_semana')
            else:
                st.warning("Nenhum processo em dias úteis encontrado")
        
        with col_graf3:
            st.markdown("**📆 Semana Corrente (Segunda a Sexta)**")
            
            # CORREÇÃO: Calcular início e fim da semana corrente de forma mais robusta
            try:
                hoje_simples = pd.Timestamp.now()
                dias_desde_segunda = hoje_simples.weekday()
                inicio_semana = hoje_simples - pd.Timedelta(days=dias_desde_segunda)
                fim_semana = inicio_semana + pd.Timedelta(days=4)
                                
            except Exception as e:
                st.warning(f"Erro ao calcular semana corrente: {e}")
                # Fallback: usar data atual
                hoje_sem_tz = pd.Timestamp.now().normalize()
                inicio_semana = hoje_sem_tz - pd.Timedelta(days=hoje_sem_tz.weekday())
                fim_semana = inicio_semana + pd.Timedelta(days=4)
            
            # Filtrar processos da semana corrente
            df_semana_corrente = df_analise[
                (df_analise['data_convertida'] >= inicio_semana) &
                (df_analise['data_convertida'] <= fim_semana)
            ]
            
            # Criar dados para todos os dias úteis da semana (mesmo se não houver processos)
            dias_semana_corrente = []
            nomes_dias = ['Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta']
            
            for i in range(5):  # Segunda a Sexta
                data_dia = inicio_semana + pd.Timedelta(days=i)
                processos_dia = len(df_semana_corrente[df_semana_corrente['data_convertida'].dt.date == data_dia.date()])
                
                dias_semana_corrente.append({
                    'dia': nomes_dias[i],
                    'data': data_dia.strftime('%d/%m'),
                    'processos': processos_dia,
                    'ordem': i
                })
            
            df_semana_atual = pd.DataFrame(dias_semana_corrente)
            
            # Calcular média da semana atual
            media_semana_atual = df_semana_atual['processos'].mean()
            
            fig_semana_atual = px.bar(
                df_semana_atual,
                x='dia',
                y='processos',
                color_discrete_sequence=['#006400'],  # Verde escuro
                hover_data=['data']
            )
            
            # Adicionar números no topo
            fig_semana_atual.update_traces(
                texttemplate='%{y}',
                textposition='outside'
            )
            
            # Adicionar linha de média
            fig_semana_atual.add_hline(
                y=media_semana_atual,
                line_color="orange",
                line_width=2,
                line_dash="dash",
                annotation_text=f"Média: {media_semana_atual:.1f}",
                annotation_position="top right"
            )
            
            fig_semana_atual.update_layout(
                xaxis_title="",
                yaxis_title="",
                height=400,
                showlegend=False,
                margin=dict(t=50, b=20, l=20, r=20)
            )
            st.plotly_chart(fig_semana_atual, use_container_width=True, key='grafico_semana_atual')
        
        # Estatísticas gerais do período
        st.markdown("---")
        st.markdown("**📈 Estatísticas do Período:**")
        
        col_stat1, col_stat2, col_stat3, col_stat4 = st.columns(4)
        
        with col_stat1:
            st.metric("Total 12 meses", f"{len(df_12_meses):,}")
        
        with col_stat2:
            media_mensal = len(df_12_meses) / 12
            st.metric("Média mensal", f"{media_mensal:.1f}")
        
        with col_stat3:
            if len(processos_por_mes) > 0:
                max_mes = processos_por_mes['quantidade'].max()
                mes_max = processos_por_mes.loc[processos_por_mes['quantidade'].idxmax(), 'mes_ano_str']
                st.metric("Pico mensal", f"{max_mes}", delta=f"em {mes_max}")
            else:
                st.metric("Pico mensal", "N/A")
        
        with col_stat4:
            if len(df_dias_uteis) > 0:
                weeks_count = df_dias_uteis['data_convertida'].dt.to_period('W').nunique()
                media_dia_util = len(df_dias_uteis) / max(weeks_count * 5, 1)
                st.metric("Média/dia útil", f"{media_dia_util:.1f}")
            else:
                st.metric("Média/dia útil", "N/A")
    
    else:
        st.warning("Nenhum processo nos últimos 12 meses")
      
def analise_reus_procedencia(df_analise):
    """Análise de réus e procedência"""
    df_analise = aplicar_filtro_configurado(df_analise)

    st.subheader("⚖️ Réus")

    col_reu1, col_reu2, col_competencia = st.columns(3)
    
    with col_reu1:
        st.markdown("**🏢 Top 10 Réus**")
        
        if 'reu' in df_analise.columns:
            # Aplicar padronização
            df_analise['reu_ajustado'] = df_analise['reu'].apply(padronizar_reu)
            
            # Contar réus padronizados
            top_reus = df_analise['reu_ajustado'].value_counts().head(10)

            # Estatísticas
            total_reus_unicos = df_analise['reu_ajustado'].nunique()
            reu_mais_comum = top_reus.index[0]
            processos_reu_top = top_reus.iloc[0]
            percentual_top = (processos_reu_top / len(df_analise) * 100)
                            
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
                    yaxis={'categoryorder':'total ascending'},
                    height=500,
                    margin=dict(l=100, r=50, t=20, b=20),
                    xaxis_title="",
                    yaxis_title="",
                    xaxis=dict(
                        range=[0, valor_max + padding],  # Estender range
                        automargin=True
                    )
                )
                
                # Adicionar números nas barras
                fig_reus.update_traces(
                    texttemplate='%{x}',
                    textposition='outside'
                )
                
                st.plotly_chart(fig_reus, use_container_width=True, key='grafico_reus')
    with col_reu2:
        col_reu11, col_reu12 = st.columns(2)
        with col_reu11:
            st.metric("Réus únicos", total_reus_unicos)
        with col_reu12:
            st.metric(f"% {reu_mais_comum}", f"{percentual_top:.1f}%")
        st.markdown("**⚖️ Top 5 Réus - Ação Cível:**")
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
        st.markdown("**🏛️ Top 10 Competências**") 
        if 'competencia' in df_analise.columns:
            # Aplicar padronização
            df_analise['competencia_ajustada'] = df_analise['competencia'].apply(padronizar_competencia)
            
            # Contar processos por competência
            competencia_counts = df_analise['competencia_ajustada'].value_counts()

            if len(competencia_counts) > 0:
                # Criar DataFrame para o gráfico - LIMITAR AO TOP 10
                df_competencia = competencia_counts.head(10).reset_index()  # Mudança aqui: head(10) em vez de head(15)
                df_competencia.columns = ['Competência', 'Número de Processos']
                
                # Gráfico de barras com MESMAS configurações do gráfico de réus
                if len(df_competencia) > 0:
                    # Calcular padding baseado no valor máximo (IGUAL aos réus)
                    valor_max = df_competencia['Número de Processos'].iloc[0]
                    padding = valor_max * 0.2  # 20% de padding
                    
                    fig_competencia = px.bar(
                        df_competencia,
                        x='Número de Processos',
                        y='Competência',
                        orientation='h',
                        color_discrete_sequence=['darkgreen']  # Manter cor diferente
                    )
                    
                    # MESMAS configurações de layout dos réus
                    fig_competencia.update_layout(
                        yaxis={'categoryorder':'total ascending'},
                        height=500,  # MESMA altura dos réus
                        margin=dict(l=100, r=50, t=20, b=20),  # MESMAS margens
                        xaxis_title="",
                        yaxis_title="",
                        xaxis=dict(
                            range=[0, valor_max + padding],  # MESMO padding
                            automargin=True
                        )
                    )
                    
                    # Adicionar números nas barras (IGUAL aos réus)
                    fig_competencia.update_traces(
                        texttemplate='%{x}',
                        textposition='outside'
                    )
                    
                    st.plotly_chart(fig_competencia, use_container_width=True, key='grafico_competencia')

def analise_perfil_clientes(df_analise):
    """Análise do perfil dos clientes - COM FILTRO APLICADO"""
    # APLICAR FILTRO AQUI TAMBÉM
    df_analise = aplicar_filtro_configurado(df_analise)
    
    st.subheader("👥 Perfil dos Clientes")
    
    col_idade, col_sexo, col_stats = st.columns([2, 2, 1])
    
    with col_idade:
        st.markdown("**📊 Distribuição de Idades**")
        if 'idade_cliente_anos' in df_analise.columns:
            idades_validas = df_analise['idade_cliente_anos'].dropna()
            
            if len(idades_validas) > 0:
                # Criar histograma melhorado
                fig_idades = px.histogram(
                    x=idades_validas,
                    nbins=20,
                    color_discrete_sequence=['steelblue']
                )
                
                # Adicionar números no topo das barras
                fig_idades.update_traces(
                    texttemplate='%{y}',
                    textposition='outside'
                )
                
                # Ajustar layout para ficar mais limpo
                fig_idades.update_layout(
                    title="",  # Remover título
                    xaxis_title="",  # Remover título do eixo X
                    yaxis_title="",  # Remover título do eixo Y
                    height=400,
                    showlegend=False,
                    margin=dict(t=40, b=20, l=20, r=20),  # Margem superior para números
                    yaxis=dict(
                        showticklabels=False,  # Remover números do eixo Y
                        showgrid=False,        # Remover linhas horizontais
                        zeroline=False         # Remover linha do zero
                    ),
                    xaxis=dict(
                        showgrid=False,        # Remover linhas verticais também
                    ),
                    bargap=0.1  # Adicionar pequeno espaço entre barras (0.0 = grudadas, 0.2 = espaçadas)
                )
                
                st.plotly_chart(fig_idades, use_container_width=True, key="grafico_idades_clientes")
                
            else:
                st.warning("Nenhuma idade válida encontrada")
        else:
            st.warning("Dados de idade não disponíveis")
    
    with col_sexo:
        st.markdown("**⚧ Distribuição por Sexo**")
        if 'sexo' in df_analise.columns:
            # Filtrar apenas M e F
            sexo_valido = df_analise[df_analise['sexo'].isin(['M', 'F'])]
            
            if len(sexo_valido) > 0:
                sexo_counts = sexo_valido['sexo'].value_counts()
                
                fig_sexo = px.pie(
                    values=sexo_counts.values,
                    names=['Masculino' if x == 'M' else 'Feminino' for x in sexo_counts.index],
                    color_discrete_map={'Masculino': '#1f77b4', 'Feminino': '#ff7f0e'}
                )
                
                # Limpar layout do gráfico de pizza
                fig_sexo.update_layout(
                    title="",  # Remover título
                    height=400,
                    margin=dict(t=20, b=20, l=20, r=20)
                )
                
                st.plotly_chart(fig_sexo, use_container_width=True, key="grafico_sexo_clientes")
        
        with col_stats:
            st.markdown("**📈 Concentração Etária**")
            
            if 'idade_cliente_anos' in df_analise.columns:
                idades_validas = df_analise['idade_cliente_anos'].dropna()
                
                if len(idades_validas) > 0:
                    # Calcular percentis
                    p10 = idades_validas.quantile(0.10)
                    p25 = idades_validas.quantile(0.25)
                    p50 = idades_validas.quantile(0.50)  # Mediana
                    p75 = idades_validas.quantile(0.75)
                    p90 = idades_validas.quantile(0.90)
                    
                    # Calcular faixas de concentração
                    # 50% dos clientes estão entre P25 e P75 (quartis)
                    faixa_50_min = p25
                    faixa_50_max = p75
                    
                    # 80% dos clientes estão entre P10 e P90
                    faixa_80_min = p10
                    faixa_80_max = p90
                    
                    st.markdown(f"""
                    **50% dos clientes estão entre {faixa_50_min:.0f} e {faixa_50_max:.0f} anos**
                    
                    **80% dos clientes estão entre {faixa_80_min:.0f} e {faixa_80_max:.0f} anos**
                    """)
                    
                    st.markdown("---")
                    
                    # Estatísticas complementares
                    st.markdown("**📋 Resumo:**")
                    
                    st.metric(
                        label="Mediana",
                        value=f"{p50:.0f} anos",
                        help="Idade que divide os clientes ao meio"
                    )
                    
                    # Faixa etária mais comum (moda aproximada)
                    # Dividir em faixas de 5 anos
                    idades_faixas = pd.cut(idades_validas, bins=range(int(idades_validas.min()), int(idades_validas.max()) + 5, 5))
                    faixa_mais_comum = idades_faixas.mode()
                    
                    if len(faixa_mais_comum) > 0:
                        faixa_str = str(faixa_mais_comum[0])
                        # Extrair números da faixa (ex: (25, 30] -> 25-30)
                        if '(' in faixa_str and ']' in faixa_str:
                            faixa_limpa = faixa_str.replace('(', '').replace(']', '').replace(',', ' a')
                            st.metric(
                                label="Faixa mais comum",
                                value=f"{faixa_limpa} anos",
                                help="Faixa de 5 anos com mais clientes"
                            )
                                        
                else:
                    st.warning("Sem dados de idade válidos")
            else:
                st.warning("Dados de idade não disponíveis")

def analise_profissoes(df_analise):
    """Análise apenas de profissões - COM FILTRO APLICADO"""
    # APLICAR FILTRO AQUI TAMBÉM
    df_analise = aplicar_filtro_configurado(df_analise)
    
    st.subheader("💼 Análise de Profissões")

    # Layout principal
    col_prof_geral, col_masc, col_fem = st.columns([2, 1, 1])
    
    with col_prof_geral:
        st.markdown("**💼 Top 10 Profissões Gerais**")
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
                height=500,
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
            
            st.plotly_chart(fig_prof, use_container_width=True, key="grafico_profissoes_geral")
            
            st.write(f"**Total de profissões únicas:** {df_analise['profissao_normalizada'].nunique()}")
        else:
            st.warning("Dados de profissão não disponíveis")
    
    # TABELAS POR GÊNERO
    if 'profissao_normalizada' in df_analise.columns and 'sexo' in df_analise.columns:
        # Filtrar apenas M e F
        df_genero = df_analise[df_analise['sexo'].isin(['M', 'F'])]
        
        if len(df_genero) > 0:
            with col_masc:
                st.markdown("**👨 Top 5 - Masculino**")
                masculino = df_genero[df_genero['sexo'] == 'M']
                
                if len(masculino) > 0:
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
                    
                    st.metric("Total Masculino", f"{len(masculino):,}")
                    
                else:
                    st.warning("Nenhum dado masculino")
            
            with col_fem:
                st.markdown("**👩 Top 5 - Feminino**")
                feminino = df_genero[df_genero['sexo'] == 'F']
                
                if len(feminino) > 0:
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
                    
                    st.metric("Total Feminino", f"{len(feminino):,}")
                    
                else:
                    st.warning("Nenhum dado feminino")
        
        else:
            st.warning("Nenhum dado de gênero válido (M/F)")
    else:
        st.warning("Dados de profissão ou sexo não disponíveis")

def analise_prospectors(df_analise):
    """Análise específica de prospectores - COM FILTRO APLICADO"""
    # APLICAR FILTRO AQUI TAMBÉM
    df_analise = aplicar_filtro_configurado(df_analise)
    
    st.subheader("🎯 Análise de Prospectores")
    
    if 'prospector' not in df_analise.columns:
        st.warning("Coluna 'prospector' não encontrada")
        return
    
    if 'data_convertida' not in df_analise.columns:
        st.warning("Dados de data não disponíveis para análise temporal")
        return
    
    col_grafico, col_ranking = st.columns(2)
    
    with col_grafico:
        st.markdown("**📊 Proporção de Ações por Mês (Últimos 12 meses)**")
        
        # Filtrar últimos 12 meses
        hoje = pd.Timestamp.now()
        doze_meses_atras = hoje - pd.DateOffset(months=12)
        df_12_meses = df_analise[df_analise['data_convertida'] >= doze_meses_atras]
        
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
            
            # Criar gráfico de barras empilhadas normalizado (CORREÇÃO)
            fig_prospector = px.bar(
                agrupado,
                x='mes_ano_str',
                y='percentual',  # Usar percentual já calculado
                color='prospector_categoria',
                color_discrete_map={
                    'Com Prospector': '#2E8B57',    # Verde escuro
                    'Sem Prospector': '#CD5C5C'      # Vermelho claro
                }
                # REMOVER barnorm que não existe
            )
            
            fig_prospector.update_layout(
                title="",
                xaxis_title="",
                yaxis_title="Percentual (%)",
                height=400,
                margin=dict(t=20, b=20, l=20, r=20),
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1
                ),
                yaxis=dict(range=[0, 100])  # Fixar em 0-100%
            )
            
            # Adicionar percentuais nas barras
            fig_prospector.update_traces(
                texttemplate='%{y:.1f}%',
                textposition='inside'
            )
            
            st.plotly_chart(fig_prospector, use_container_width=True, key="grafico_prospectors_temporal")
            
            # Estatísticas do período
            total_12_meses = len(df_12_meses)
            com_prospector_12m = df_12_meses['tem_prospector'].sum()
            percentual_prospector_12m = (com_prospector_12m / total_12_meses * 100) if total_12_meses > 0 else 0
            
            col_stat1, col_stat2, col_stat3 = st.columns(3)
            with col_stat1:
                st.metric("Total 12 meses", f"{total_12_meses:,}")
            with col_stat2:
                st.metric("Com prospector", f"{com_prospector_12m:,}")
            with col_stat3:
                st.metric("% com prospector", f"{percentual_prospector_12m:.1f}%")
        
        else:
            st.warning("Nenhum processo nos últimos 12 meses")
    
    with col_ranking:
        st.markdown("**🏆 Top 5 Prospectors**")
        
        # Filtros com radio buttons
        periodo_filtro = st.radio(
            "Período de análise:",
            ["Geral", "Ano atual", "Mês atual"],
            index=0,
            help="Selecione o período para o ranking",
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
            
            st.markdown(f"**📊 Ranking ({periodo_texto}):**")

            st.markdown("""
            <style>
            .prospector-item {
                display: flex;
                justify-content: space-between;
                align-items: center;
                padding: 8px 0;
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

def visao_geral(df_filtrado):
    """Visão geral com KPIs principais e últimos processos - COM FILTRO APLICADO"""
    # APLICAR FILTRO AQUI TAMBÉM
    df_filtrado = aplicar_filtro_configurado(df_filtrado)
    
    st.subheader("📊 Visão Geral")
    
    # KPIs de novos processos
    st.markdown("### 📈 Novos Processos")
    
    if 'data_convertida' in df_filtrado.columns:
        import pandas as pd
        from datetime import datetime, timedelta
        
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
        df_6_meses['semana'] = df_6_meses['data_convertida'].dt.to_period('W')
        semanas_6m = df_6_meses['semana'].nunique()
        
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
        df_12_meses['mes'] = df_12_meses['data_convertida'].dt.to_period('M')
        meses_12m = df_12_meses['mes'].nunique()
        
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
        
        # FUNÇÃO PARA DETERMINAR SETA E COR
        def get_seta_cor(valor_atual, media_historica):
            if valor_atual > media_historica:
                return "🟢 ↗️", "normal"
            elif valor_atual < media_historica:
                return "🔴 ↘️", "inverse"
            else:
                return "🟡 →", "off"
        
        # Formatação das datas
        data_ultimo_dia = ultimo_dia_util.strftime('%d/%m/%Y')
        data_inicio_semana = inicio_semana.strftime('%d/%m')
        data_fim_semana = fim_semana.strftime('%d/%m')
        
        # Layout dos KPIs - 3 COLUNAS
        col_kpi1, col_kpi2, col_kpi3 = st.columns(3)
        
        with col_kpi1:
            st.markdown(f"#### 📅 Último dia útil ({data_ultimo_dia})")
            
            col_sub1, col_sub2 = st.columns(2)
            
            # GERAL com comparação
            with col_sub1:
                seta_geral, delta_color_geral = get_seta_cor(processos_ultimo_dia_geral, media_diaria_geral)
                st.metric(
                    label="Geral",
                    value=f"{processos_ultimo_dia_geral:,}",
                    delta=f"Média: {media_diaria_geral:.1f} {seta_geral}",
                    delta_color=delta_color_geral,
                    help=f"Comparação com média diária dos últimos 6 meses ({media_diaria_geral:.1f})"
                )
            
            # PREVIDENCIÁRIO com comparação
            with col_sub2:
                seta_prev, delta_color_prev = get_seta_cor(processos_ultimo_dia_prev, media_diaria_prev)
                st.metric(
                    label="Previdenciário",
                    value=f"{processos_ultimo_dia_prev:,}",
                    delta=f"Média: {media_diaria_prev:.1f} {seta_prev}",
                    delta_color=delta_color_prev,
                    help=f"Comparação com média diária previdenciária dos últimos 6 meses ({media_diaria_prev:.1f})"
                )
            
            # Percentual
            if processos_ultimo_dia_geral > 0:
                perc_prev_dia = (processos_ultimo_dia_prev / processos_ultimo_dia_geral * 100)
                st.caption(f"🔍 {perc_prev_dia:.1f}% previdenciárias")
            else:
                st.caption("🔍 Nenhum processo")
        
        with col_kpi2:
            st.markdown(f"#### 📅 Semana Passada ({data_inicio_semana} a {data_fim_semana})")
            
            col_sub3, col_sub4 = st.columns(2)
            
            # GERAL com comparação semanal
            with col_sub3:
                seta_sem_geral, delta_color_sem_geral = get_seta_cor(processos_semana_geral, media_semanal_geral)
                st.metric(
                    label="Geral",
                    value=f"{processos_semana_geral:,}",
                    delta=f"Média: {media_semanal_geral:.1f} {seta_sem_geral}",
                    delta_color=delta_color_sem_geral,
                    help=f"Comparação com média semanal dos últimos 6 meses ({media_semanal_geral:.1f})"
                )
            
            # PREVIDENCIÁRIO com comparação semanal
            with col_sub4:
                seta_sem_prev, delta_color_sem_prev = get_seta_cor(processos_semana_prev, media_semanal_prev)
                st.metric(
                    label="Previdenciário",
                    value=f"{processos_semana_prev:,}",
                    delta=f"Média: {media_semanal_prev:.1f} {seta_sem_prev}",
                    delta_color=delta_color_sem_prev,
                    help=f"Comparação com média semanal previdenciária dos últimos 6 meses ({media_semanal_prev:.1f})"
                )
            
            # Percentual
            if processos_semana_geral > 0:
                perc_prev_semana = (processos_semana_prev / processos_semana_geral * 100)
                st.caption(f"🔍 {perc_prev_semana:.1f}% previdenciárias")
            else:
                st.caption("🔍 Nenhum processo")
        
        with col_kpi3:
            st.markdown(f"#### 📅 Este Mês")
            
            col_sub5, col_sub6 = st.columns(2)
            
            # GERAL com comparação mensal
            with col_sub5:
                seta_mes_geral, delta_color_mes_geral = get_seta_cor(processos_mes_geral, media_mensal_geral)
                st.metric(
                    label="Geral",
                    value=f"{processos_mes_geral:,}",
                    delta=f"Média: {media_mensal_geral:.1f} {seta_mes_geral}",
                    delta_color=delta_color_mes_geral,
                    help=f"Comparação com média mensal dos últimos 12 meses ({media_mensal_geral:.1f})"
                )
            
            # PREVIDENCIÁRIO com comparação mensal
            with col_sub6:
                seta_mes_prev, delta_color_mes_prev = get_seta_cor(processos_mes_prev, media_mensal_prev)
                st.metric(
                    label="Previdenciário",
                    value=f"{processos_mes_prev:,}",
                    delta=f"Média: {media_mensal_prev:.1f} {seta_mes_prev}",
                    delta_color=delta_color_mes_prev,
                    help=f"Comparação com média mensal previdenciária dos últimos 12 meses ({media_mensal_prev:.1f})"
                )
            
            # Percentual
            if processos_mes_geral > 0:
                perc_prev_mes = (processos_mes_prev / processos_mes_geral * 100)
                st.caption(f"🔍 {perc_prev_mes:.1f}% previdenciárias")
            else:
                st.caption("🔍 Nenhum processo")
    
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
            # if pd.notna(tipo_processo) and len(str(tipo_processo)) > 30:
            #     tipo_processo = str(tipo_processo)[:27] + "..."
            
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
    
   