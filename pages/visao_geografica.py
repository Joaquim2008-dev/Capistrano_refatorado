import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import geopandas as gpd
from shapely.geometry import mapping
import json
import folium
from folium import plugins
from unidecode import unidecode
import pickle
import os
from datetime import datetime
from pathlib import Path
import sys

# Adicionar path do projeto
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from data.data_loader import carregar_e_processar_dados, filtrar_sergipe
from utils.text_processing import categorizar_tipo_processo

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

def pagina_visao_geografica():
    """Página original com mapas geográficos"""
    
    # Título com indicação de filtro se ativo
    if FILTRO_ANO_ATIVO and ANO_FILTRO:
        st.title(f"🗺️ Visão Geográfica dos Processos ({ANO_FILTRO})")
        st.markdown(f"### Distribuição de processos por município e bairro - Ano {ANO_FILTRO}")
    else:
        st.title("🗺️ Visão Geográfica dos Processos")
        st.markdown("### Distribuição de processos por município e bairro")
    
    # Carregar dados
    df = carregar_e_processar_dados()
    
    if df is None:
        st.error("❌ Erro ao carregar dados das APIs")
        st.stop()
    
    # Filtrar Sergipe
    df_sergipe = filtrar_sergipe(df)
    
    if df_sergipe is None or len(df_sergipe) == 0:
        st.warning("⚠️ Nenhum processo encontrado em Sergipe")
        st.stop()
    
    # APLICAR FILTRO CONFIGURADO
    df_sergipe = aplicar_filtro_configurado(df_sergipe)
    
    if len(df_sergipe) == 0:
        st.warning(f"⚠️ Nenhum processo encontrado em Sergipe para {ANO_FILTRO}")
        st.stop()
    
    # PREPARAR DADOS PARA FILTROS
    # 1. Preparar coluna de ano (apenas se filtro não ativo)
    if not (FILTRO_ANO_ATIVO and ANO_FILTRO):
        if 'data' in df_sergipe.columns:
            try:
                df_sergipe['data_convertida'] = pd.to_datetime(df_sergipe['data'], errors='coerce')
                df_sergipe['ano'] = df_sergipe['data_convertida'].dt.year
                anos_validos = df_sergipe['ano'].dropna().astype(int)
                
                if len(anos_validos) > 0:
                    min_ano = int(anos_validos.min())
                    max_ano = int(anos_validos.max())
                    tem_filtro_ano = True
                else:
                    tem_filtro_ano = False
            except:
                tem_filtro_ano = False
        else:
            tem_filtro_ano = False
    else:
        # Se filtro ativo, não preparar controles de ano
        tem_filtro_ano = False
    
    # 2. Preparar coluna de tipo principal
    if 'tipoProcesso' in df_sergipe.columns:
        df_sergipe['tipoPrincipal'] = df_sergipe['tipoProcesso'].apply(categorizar_tipo_processo)
        tipos_unicos = ['ACAO CIVEL', 'ACAO PREVIDENCIARIA', 'ACAO TRABALHISTA', 'OUTROS']
        tem_filtro_tipo = True
    else:
        tem_filtro_tipo = False
    
    # CRIAR FILTROS - OCULTAR SE FILTRO DE ANO ATIVO
    if FILTRO_ANO_ATIVO and ANO_FILTRO:
        # Não mostrar seção de filtros
        # Aplicar apenas filtro de tipo se disponível
        if tem_filtro_tipo:
            col_filtro_unico = st.columns(1)[0]
            with col_filtro_unico:
                st.markdown("**⚖️ Filtro por Tipo (opcional):**")
                
                tipos_disponiveis = ["Todos"] + tipos_unicos
                tipo_selecionado = st.selectbox(
                    "Selecione o tipo:",
                    tipos_disponiveis,
                    index=0,
                    key="tipo_geografica"
                )
        else:
            tipo_selecionado = "Todos"
        
        anos_selecionados = (None, None)
        periodo_texto = f"Ano {ANO_FILTRO}"
        
    else:
        st.subheader("🔍 Filtros")
        
        if tem_filtro_ano or tem_filtro_tipo:
            col_filtro1, col_filtro2 = st.columns(2)
            
            # Filtro de Ano com SLIDER
            with col_filtro1:
                if tem_filtro_ano:
                    st.markdown("**📅 Filtro por Ano:**")
                    
                    # Slider de range para anos
                    anos_selecionados = st.slider(
                        "Selecione o período:",
                        min_value=min_ano,
                        max_value=max_ano,
                        value=(min_ano, max_ano),  # Valor inicial (todos os anos)
                        step=1,
                        format="%d"
                    )
                    
                    # Mostrar informações do período selecionado
                    ano_inicio, ano_fim = anos_selecionados
                    
                    if ano_inicio == min_ano and ano_fim == max_ano:
                        periodo_texto = "Todos os anos"
                    elif ano_inicio == ano_fim:
                        periodo_texto = f"Apenas {ano_inicio}"
                    else:
                        periodo_texto = f"{ano_inicio} - {ano_fim}"
                    
                else:
                    anos_selecionados = (None, None)
                    periodo_texto = "Todos"
                    st.warning("⚠️ Coluna 'data' não encontrada")
            
            # Filtro de Tipo Principal
            with col_filtro2:
                if tem_filtro_tipo:
                    st.markdown("**⚖️ Filtro por Tipo:**")
                    
                    tipos_disponiveis = ["Todos"] + tipos_unicos
                    tipo_selecionado = st.selectbox(
                        "Selecione o tipo:",
                        tipos_disponiveis,
                        index=0
                    )
                    
                    # Mostrar distribuição das 4 categorias
                    distribuicao_tipos = df_sergipe['tipoPrincipal'].value_counts()
                                            
                else:
                    tipo_selecionado = "Todos"
                    st.warning("⚠️ Coluna 'tipoProcesso' não encontrada")
        else:
            anos_selecionados = (None, None)
            tipo_selecionado = "Todos"
            periodo_texto = "Todos"
            st.warning("⚠️ Colunas para filtros não encontradas")
    
    # APLICAR FILTROS
    df_sergipe_filtrado = df_sergipe.copy()
    
    # Filtro por período de anos
    if tem_filtro_ano and anos_selecionados[0] is not None:
        ano_inicio, ano_fim = anos_selecionados
        df_sergipe_filtrado = df_sergipe_filtrado[
            (df_sergipe_filtrado['ano'] >= ano_inicio) & 
            (df_sergipe_filtrado['ano'] <= ano_fim)
        ]
    
    # Filtro por tipo
    if tem_filtro_tipo and tipo_selecionado != "Todos":
        df_sergipe_filtrado = df_sergipe_filtrado[df_sergipe_filtrado['tipoPrincipal'] == tipo_selecionado]
    
    # Verificar se ainda há dados após filtros
    if len(df_sergipe_filtrado) == 0:
        st.warning(f"⚠️ Nenhum processo encontrado para os filtros: Período={periodo_texto}, Tipo={tipo_selecionado}")
        st.info("💡 Tente alterar os filtros")
        df_sergipe_filtrado = df_sergipe  # Usar dados sem filtro como fallback
        anos_selecionados = (min_ano, max_ano) if tem_filtro_ano else (None, None)
        tipo_selecionado = "Todos"
        periodo_texto = "Todos"
    
    # INFORMAÇÕES DOS FILTROS
    col_info1, col_info2, col_info3, col_info4 = st.columns(4)
    
    # MAPAS + KPIs (usando dados filtrados)
    st.markdown("---")
    
    # Criar títulos dinâmicos
    filtros_texto = []
    if tem_filtro_ano and anos_selecionados[0] is not None:
        if anos_selecionados[0] == anos_selecionados[1]:
            filtros_texto.append(str(anos_selecionados[0]))
        else:
            filtros_texto.append(f"{anos_selecionados[0]}-{anos_selecionados[1]}")
    
    if tipo_selecionado != "Todos":
        tipo_abrev = tipo_selecionado[:15] + "..." if len(tipo_selecionado) > 15 else tipo_selecionado
        filtros_texto.append(tipo_abrev)
    
    filtros_str = " | ".join(filtros_texto) if filtros_texto else "Todos os dados"
    
    # Layout com 3 colunas: Mapa Sergipe | Mapa Aracaju | KPIs
    col_sergipe, col_aracaju, col_kpis = st.columns([2, 2, 1])
    
    with col_sergipe:
        st.markdown(f"#### 🗺️ Sergipe por Município")
        st.caption(f"Filtros: {filtros_str}")
        
        with st.spinner("Gerando mapa de Sergipe..."):
            mapa_sergipe = criar_mapa_folium_sergipe(df_sergipe_filtrado)
            
            if mapa_sergipe is not None:
                from streamlit_folium import st_folium
                try:
                    st_folium(mapa_sergipe, width=500, height=450)
                except ImportError:
                    from streamlit_folium import folium_static
                    folium_static(mapa_sergipe, width=500, height=450)
            else:
                st.error("❌ Erro no mapa de Sergipe")
    
    with col_aracaju:
        st.markdown(f"#### 🏙️ Aracaju por Bairro")
        st.caption(f"Filtros: {filtros_str}")
        
        with st.spinner("Gerando mapa de Aracaju..."):
            mapa_aracaju = criar_mapa_aracaju_bairros(df_sergipe_filtrado)
            
            if mapa_aracaju is not None:
                try:
                    st_folium(mapa_aracaju, width=500, height=450)
                except ImportError:
                    folium_static(mapa_aracaju, width=500, height=450)
            else:
                st.error("❌ Erro no mapa de Aracaju")
    
    with col_kpis:
        st.markdown("#### 📊 Indicadores Básicos")
        
        # Calcular KPIs adicionais baseados nos dados originais (sem filtro)
        total_processos_original = len(df)
        total_processos_ativos = len(df[df['status'] == 'Ativo']) if 'status' in df.columns else len(df)
        total_processos_fora_sergipe = total_processos_original - len(df_sergipe)
        
        # KPIs da coluna atual (dados filtrados)
        total_processos_filtrados = len(df_sergipe_filtrado)
        total_cidades = df_sergipe_filtrado['cidade_upper'].nunique()
        
        # Percentual de Aracaju nos dados filtrados
        aracaju_processos = len(df_sergipe_filtrado[df_sergipe_filtrado['cidade_upper'] == 'ARACAJU'])
        percentual_aracaju = (aracaju_processos / total_processos_filtrados * 100) if total_processos_filtrados > 0 else 0
        
        # Cidade líder
        if len(df_sergipe_filtrado) > 0:
            cidade_top = df_sergipe_filtrado['cidade_upper'].mode().iloc[0]
            processos_top = df_sergipe_filtrado['cidade_upper'].value_counts().iloc[0]
        else:
            cidade_top = "N/A"
            processos_top = 0
        
        # Exibir KPIs
        st.metric(
            label="🗂️ Processos Filtrados",
            value=f"{total_processos_filtrados:,}",
            help=f"Processos com filtros aplicados: {filtros_str}"
        )
        
        st.metric(
            label="📂 Total Geral",
            value=f"{total_processos_original:,}",
            help="Número total de processos (todos os estados e status)"
        )
        
        st.metric(
            label="🏙️ Cidades Atendidas (SE)",
            value=total_cidades,
            help="Municípios de Sergipe com processo nos filtros aplicados"
        )
        
        st.metric(
            label="🌍 Fora de Sergipe",
            value=f"{total_processos_fora_sergipe:,}",
            help="Processos fora do estado de Sergipe"
        )
        
        st.metric(
            label="🥇 Cidade Líder",
            value=cidade_top,
            delta=f"{processos_top} processos",
            help="Município com maior número de processos (dados filtrados)"
        )
        
        st.metric(
            label="📊 % Aracaju",
            value=f"{percentual_aracaju:.1f}%",
            help="Percentual de processos em Aracaju (dados filtrados)"
        )
        
        # Separador visual
        st.markdown("---")
        
        # KPIs adicionais sobre os filtros
        if filtros_str != "Todos os dados":
            st.markdown("**🔍 Impacto dos Filtros:**")
            
            reducao_percent = ((len(df_sergipe) - total_processos_filtrados) / len(df_sergipe) * 100) if len(df_sergipe) > 0 else 0
            
            st.metric(
                label="Redução",
                value=f"{reducao_percent:.1f}%",
                help="Percentual de processos removidos pelos filtros"
            )
            
            # Se filtro de tipo aplicado, mostrar participação
            if tipo_selecionado != "Todos":
                participacao_tipo = (total_processos_filtrados / len(df_sergipe) * 100) if len(df_sergipe) > 0 else 0
                st.metric(
                    label="Participação Tipo",
                    value=f"{participacao_tipo:.1f}%",
                    help=f"Participação de '{tipo_selecionado}' no total"
                )

# As funções de criação de mapas precisam ser implementadas
# Você pode mover elas do seu dash.py original ou implementar aqui

@st.cache_data(ttl=3600)
def carregar_shapefile_sergipe():
    """Carrega o shapefile de Sergipe"""
    try:
        from functions.geo import baixar_municipios_sergipe
        gdf_municipios = baixar_municipios_sergipe()
        return gdf_municipios
    except Exception as e:
        st.error(f"Erro ao carregar shapefile: {e}")
        return None

def criar_mapa_folium_sergipe(df_sergipe):
    """
    Cria mapa interativo de Sergipe usando Folium
    """
    
    # Contar processos por cidade
    contagem_cidades = df_sergipe['cidade_upper'].value_counts().reset_index()
    contagem_cidades.columns = ['cidade', 'num_processos']
    
    # Carregar shapefile
    gdf_municipios = carregar_shapefile_sergipe()
    
    if gdf_municipios is None:
        st.error("❌ Não foi possível carregar o shapefile de Sergipe")
        return None
    
    # CORRIGIR: Preparar dados para merge aplicando unidecode
    gdf_municipios['nome_upper'] = gdf_municipios['NM_MUN'].apply(
        lambda x: unidecode(str(x).upper().strip()) if pd.notna(x) else ''
    )    
    # Merge
    gdf_com_processos = gdf_municipios.merge(
        contagem_cidades,
        left_on='nome_upper',
        right_on='cidade',
        how='left'
    )
        
    gdf_com_processos['num_processos'] = gdf_com_processos['num_processos'].fillna(0)
    
    def obter_cor_municipio(row):
        num_proc = row['num_processos']
        nome = row['nome_upper']
        
        # Identificar top 5 municípios
        top_5_nomes = gdf_com_processos.nlargest(5, 'num_processos')['nome_upper'].tolist()
        
        if nome in top_5_nomes:
            # Top 5 com tons de azul escuro
            if nome == 'ARACAJU':
                return '#000080'  # Navy (azul muito escuro)
            elif nome == 'NOSSA SENHORA DO SOCORRO':
                return '#191970'  # MidnightBlue (azul escuro)
            elif nome == 'SAO CRISTOVAO':
                return '#483D8B'  # DarkSlateBlue (azul escuro mais claro)
            else:
                # Para o 4º e 5º colocados
                posicao = top_5_nomes.index(nome)
                if posicao == 3:
                    return '#4169E1'  # RoyalBlue
                else:  # posicao == 4
                    return '#6495ED'  # CornflowerBlue
        elif num_proc == 0:
            return '#D3D3D3'  # Cinza claro para zero
        else:
            # Degradê verde para outros municípios (fora do top 5)
            outros_municipios = gdf_com_processos[
                (~gdf_com_processos['nome_upper'].isin(top_5_nomes)) &
                (gdf_com_processos['num_processos'] > 0)
            ]
            
            if len(outros_municipios) > 0:
                max_outros = outros_municipios['num_processos'].max()
                if max_outros > 0:
                    intensidade = num_proc / max_outros
                    if intensidade <= 0.2:
                        return '#E6FFE6'  # Verde muito claro
                    elif intensidade <= 0.4:
                        return '#B3FFB3'  # Verde claro
                    elif intensidade <= 0.6:
                        return '#80FF80'  # Verde médio claro
                    elif intensidade <= 0.8:
                        return '#4DFF4D'  # Verde médio
                    else:
                        return '#00CC00'  # Verde escuro
                else:
                    return '#E6FFE6'
            else:
                return '#E6FFE6'
    
    # Aplicar as cores
    gdf_com_processos['color'] = gdf_com_processos.apply(obter_cor_municipio, axis=1)
    
    # Modificar para pegar TODOS os municípios com processos > 0
    municipios_com_processos = gdf_com_processos[gdf_com_processos['num_processos'] > 0]
    
    # Calcular bounds de Sergipe para limitar o mapa
    bounds = gdf_com_processos.total_bounds  # [minx, miny, maxx, maxy]
    
    # Criar o mapa base com configurações restritivas
    m = folium.Map(
        location=[-10.5, -37.4], 
        tiles='CartoDB positron',
        zoom_start=8,
        min_zoom=8,
        max_zoom=8,
        max_bounds=True,
        zoom_control=False,
        scrollWheelZoom=False,
        doubleClickZoom=False,
        touchZoom=False,
        dragging=True,
        keyboard=False
    )
    
    # Coordenadas aproximadas de Sergipe (mais precisas)
    sergipe_bounds = [
        [-11.6, -38.3],  # Southwest [lat_min, lon_min]
        [-9.4, -36.8]    # Northeast [lat_max, lon_max]
    ]
    
    # Aplicar os bounds ao mapa
    m.fit_bounds(sergipe_bounds)
    
    # Converter para GeoJSON
    geojson_str = gdf_com_processos.to_json()
    geojson_data = json.loads(geojson_str)
    
    # Função de estilo CORRIGIDA
    def style_function(feature):
        nome_mun = feature['properties'].get('NM_MUN', '')
        cor = feature['properties'].get('color', '#CCCCCC')  # Usar a cor calculada
        
        return {
            'fillColor': cor,
            'color': 'gray',  # Borda branca
            'weight': 0.5,
            'fillOpacity': 0.8
        }
    
    # Adicionar camada de municípios
    folium.GeoJson(
        geojson_data,
        name="Municípios de Sergipe",
        tooltip=folium.GeoJsonTooltip(
            fields=['NM_MUN', 'num_processos'],
            aliases=['Município:', 'Processos:'],
            labels=True,
            style=("background-color: white; color: #333333; font-family: arial; font-size: 12px; padding: 10px;")
        ),
        popup=folium.GeoJsonPopup(
            fields=['NM_MUN', 'num_processos'],
            aliases=['Município:', 'Número de Processos:']
        ),
        style_function=style_function,
        highlight_function=lambda x: {'weight': 3, 'color': 'black'}
    ).add_to(m)
    
    # Adicionar números para TODOS os municípios com processos > 0
    for _, row in municipios_com_processos.iterrows():
        if row['geometry'] is not None:
            centroid = row['geometry'].centroid
            
            # Identificar top 5 para cor do texto
            top_5_nomes = gdf_com_processos.nlargest(5, 'num_processos')['nome_upper'].tolist()
            
            if row['nome_upper'] in top_5_nomes:
                cor_texto = 'white'  # Texto branco para top 5
                if row['nome_upper'] == 'ARACAJU':
                    tamanho_fonte = 16
                    peso_fonte = 'bold'
                elif row['nome_upper'] == 'NOSSA SENHORA DO SOCORRO':
                    tamanho_fonte = 14
                    peso_fonte = 'bold'
                else:
                    tamanho_fonte = 12
                    peso_fonte = 'bold'
            else:
                cor_texto = 'black'  # Texto preto para os outros
                tamanho_fonte = 10
                peso_fonte = 'bold'
            
            folium.Marker(
                [centroid.y, centroid.x],
                icon=folium.DivIcon(
                    html=f"""
                    <div style="
                        font-size: {tamanho_fonte}px; 
                        color: {cor_texto}; 
                        text-align: center; 
                        font-weight: {peso_fonte};
                        font-family: Arial;
                        text-shadow: 1px 1px 2px rgba(0,0,0,0.7);
                        pointer-events: none;
                    ">
                        {int(row['num_processos'])}
                    </div>
                    """,
                    icon_size=(25, 25),
                    icon_anchor=(12, 12)
                )
            ).add_to(m)
    
    # Atualizar legenda
    top_5_municipios = gdf_com_processos.nlargest(5, 'num_processos')
    top_5_processos = top_5_municipios['num_processos'].sum()
    percentual_top5 = (top_5_processos / df_sergipe.shape[0] * 100) if df_sergipe.shape[0] > 0 else 0
    
    # Criar texto do top 5
    top5_texto = ""
    for i, (_, row) in enumerate(top_5_municipios.iterrows()):
        nome_curto = row['NM_MUN'].replace('NOSSA SENHORA DO SOCORRO', 'N.S. do Socorro')
        nome_curto = nome_curto.replace('SAO CRISTOVAO', 'São Cristóvão')
        top5_texto += f"<p style='margin: 1px 0; font-size: 10px;'>{nome_curto}: {int(row['num_processos'])}</p>"
    
    legenda_html = f'''
    <div style="position: fixed; 
                top: 10px; left: 10px; width: 180px; height: 165px; 
                background-color: rgba(255, 255, 255, 0.6); border:2px solid grey; z-index:9999; 
                font-size:11px; padding: 8px; border-radius: 5px;">
    <h6 style="margin-top:0;">Top 5 Municípios</h6>
    {top5_texto}
    <p style="margin: 3px 0; font-weight: bold; font-size: 11px;">Top 5: {percentual_top5:.1f}% dos processos</p>
    <p style="margin: 1px 0; font-size: 9px;">🔵 Top 5: azul</p>
    <p style="margin: 1px 0; font-size: 9px;">🟢 Demais: verde</p>
    </div>
    '''
    m.get_root().html.add_child(folium.Element(legenda_html))
    

    # JavaScript para restringir ainda mais e ajustar tamanho
    restrict_js = f"""
    <script>
    setTimeout(function(){{
        var mapContainer = document.querySelector('.folium-map');
        if (mapContainer) {{
            // Ajustar tamanho do container para formato retrato
            mapContainer.style.width = '500px';   // Largura reduzida
            mapContainer.style.height = '600px';  // Altura mantida
            mapContainer.style.margin = '0 auto'; // Centralizar
        }}
        
        var map = window[Object.keys(window).find(key => key.startsWith('map_'))];
        if (map) {{
            // Bounds específicos de Sergipe
            var southWest = L.latLng(-11.6, -38.3);
            var northEast = L.latLng(-9.4, -36.8);
            var bounds = L.latLngBounds(southWest, northEast);
            
            // Aplicar restrições rígidas
            map.setMaxBounds(bounds);
            map.fitBounds(bounds);
            map.options.minZoom = 8;
            map.options.maxZoom = 8;
            
            // Invalidar tamanho para ajustar
            setTimeout(function() {{
                map.invalidateSize();
            }}, 100);
        }}
    }}, 1000);
    </script>
    """
    m.get_root().html.add_child(folium.Element(restrict_js))
    
    return m

@st.cache_data(persist=True, ttl=86400)  # Cache por 24 horas
def criar_mapa_aracaju_bairros(df_sergipe):
    """
    Versão original que funcionava: top 20 com bolhas, demais com losangos pequenos
    """
    
    # Filtrar apenas processos de Aracaju
    df_aracaju = df_sergipe[df_sergipe['cidade_upper'] == 'ARACAJU'].copy()
    
    if len(df_aracaju) == 0:
        st.warning("❌ Nenhum processo encontrado em Aracaju")
        return None
    
    if 'bairro' not in df_aracaju.columns:
        st.warning("❌ Coluna 'bairro' não encontrada")
        return None
    
    # Contar processos diretamente por bairro
    contagem_bairros = df_aracaju.groupby('bairro').agg({
        'idCliente': 'count',
        'cep': 'first'
    }).reset_index()
    contagem_bairros.columns = ['bairro', 'num_processos', 'cep_ref']
    contagem_bairros = contagem_bairros[contagem_bairros['cep_ref'].notna()]
    
    # Pegar apenas os top 20 bairros para otimizar
    contagem_bairros = contagem_bairros.nlargest(50, 'num_processos')  # Top 50 total
    
    # Separar top 10 e demais
    top_10 = contagem_bairros.nlargest(10, 'num_processos')
    demais_bairros = contagem_bairros[~contagem_bairros['bairro'].isin(top_10['bairro'])]
    
    
    # Geocodificar bairros (versão original)
    from geopy.geocoders import Nominatim
    import time
    
    geolocator = Nominatim(user_agent="aracaju_bairros")
    coordenadas_top10 = []
    coordenadas_demais = []
    
    # Processar top 10
    with st.spinner(f"Geocodificando top 10 bairros..."):
        for _, row in top_10.iterrows():
            try:
                endereco = f"{row['bairro']}, Aracaju, Sergipe, Brasil"
                location = geolocator.geocode(endereco, timeout=5)
                
                if location:
                    coordenadas_top10.append({
                        'bairro': row['bairro'],
                        'num_processos': row['num_processos'],
                        'lat': location.latitude,
                        'lon': location.longitude
                    })
                time.sleep(0.5)
                
            except Exception as e:
                continue
    
    # Processar demais bairros
    with st.spinner(f"Geocodificando demais bairros..."):
        for _, row in demais_bairros.iterrows():
            try:
                endereco = f"{row['bairro']}, Aracaju, Sergipe, Brasil"
                location = geolocator.geocode(endereco, timeout=5)
                
                if location:
                    coordenadas_demais.append({
                        'bairro': row['bairro'],
                        'num_processos': row['num_processos'],
                        'lat': location.latitude,
                        'lon': location.longitude
                    })
                time.sleep(0.5)
                
            except Exception as e:
                continue
    
    # Combinar todas as coordenadas
    todas_coordenadas = coordenadas_top10 + coordenadas_demais
    
    if not todas_coordenadas:
        st.warning("❌ Nenhum bairro geocodificado")
        return None
    
    # Criar DataFrame para o mapa
    df_bairros_geo = pd.DataFrame(todas_coordenadas)
    
    # Criar mapa base focado em Aracaju
    centro_lat = df_bairros_geo['lat'].mean() - 0.01  # Ajuste para subir
    centro_lon = df_bairros_geo['lon'].mean() - 0.01
    
    m = folium.Map(
        location=[centro_lat, centro_lon],
        tiles='CartoDB positron',
        zoom_start=12,
        min_zoom=11,
        max_zoom=14,
        zoom_control=False,
        scrollWheelZoom=False,
        doubleClickZoom=False,
        touchZoom=False,
        dragging=True,
        keyboard=False
    )
    
    # Função de cores para top 10
    def obter_cor_bairro(num_proc, max_proc):
        intensidade = num_proc / max_proc if max_proc > 0 else 0
        if intensidade <= 0.2:
            return '#e6f3ff'
        elif intensidade <= 0.4:
            return '#99d6ff'
        elif intensidade <= 0.6:
            return '#3399ff'
        elif intensidade <= 0.8:
            return '#0066cc'
        else:
            return '#003366'
    
    max_processos_top10 = max([coord['num_processos'] for coord in coordenadas_top10]) if coordenadas_top10 else 1
    
    # Adicionar marcadores para TOP 10 (bolhas grandes com números)
    for coord in coordenadas_top10:
        # Tamanho proporcional
        raio = max(10, min(30, coord['num_processos'] * 0.3))
        cor = obter_cor_bairro(coord['num_processos'], max_processos_top10)
        
        # Bolha colorida
        folium.CircleMarker(
            location=[coord['lat'], coord['lon']],
            radius=raio,
            popup=f"""
            <b>{coord['bairro']}</b><br>
            Processos: {coord['num_processos']}<br>
            Ranking: Top 10
            """,
            tooltip=f"{coord['bairro']}: {coord['num_processos']} processos",
            color='white',
            weight=2,
            fill=True,
            fillColor=cor,
            fillOpacity=0.8
        ).add_to(m)
        
        # Número no centro da bolha
        folium.Marker(
            [coord['lat'], coord['lon']],
            icon=folium.DivIcon(
                html=f"""
                <div style="
                    font-size: 11px; 
                    color: white; 
                    text-align: center; 
                    font-weight: bold;
                    font-family: Arial;
                    text-shadow: 1px 1px 1px rgba(0,0,0,0.8);
                    pointer-events: none;
                ">
                    {int(coord['num_processos'])}
                </div>
                """,
                icon_size=(25, 25),
                icon_anchor=(12, 12)
            )
        ).add_to(m)
    
    # Adicionar marcadores para DEMAIS bairros (losangos pequenos)
    for coord in coordenadas_demais:
        folium.RegularPolygonMarker(
            location=[coord['lat'], coord['lon']],
            number_of_sides=4,  # Losango
            radius=4,
            popup=f"""
            <b>{coord['bairro']}</b><br>
            Processos: {coord['num_processos']}<br>
            """,
            tooltip=f"{coord['bairro']}: {coord['num_processos']} processos",
            color='#8B0000',
            weight=1,
            fill=True,
            fillColor='#CD5C5C',
            fillOpacity=0.8
        ).add_to(m)
    
    # Legenda
    total_processos_top10 = sum([coord['num_processos'] for coord in coordenadas_top10])
    total_processos_demais = sum([coord['num_processos'] for coord in coordenadas_demais])
    total_geral = total_processos_top10 + total_processos_demais
    
    percentual_top10 = (total_processos_top10 / total_geral * 100) if total_geral > 0 else 0
    
    bairro_top = max(coordenadas_top10, key=lambda x: x['num_processos'])['bairro'] if coordenadas_top10 else "N/A"
    processos_top = max(coordenadas_top10, key=lambda x: x['num_processos'])['num_processos'] if coordenadas_top10 else 0
    
    legenda_html = f'''
    <div style="position: fixed; 
                top: 10px; left: 10px; width: 180px; height: 140px; 
                background-color: rgba(255, 255, 255, 0.9); border:2px solid grey; z-index:9999; 
                font-size:10px; padding: 6px; border-radius: 5px;">
    <h6 style="margin-top:0;">Aracaju por Bairro</h6>
    <p style="margin: 1px 0;">🏆 {bairro_top}: {int(processos_top)}</p>
    <p style="margin: 1px 0;">📊 Top 10: {int(total_processos_top10)} ({percentual_top10:.1f}%)</p>
    <p style="margin: 1px 0;">📊 Demais: {int(total_processos_demais)}</p>
    <p style="margin: 1px 0;">🗺️ {len(coordenadas_top10)} bolhas + {len(coordenadas_demais)} losangos</p>
    <p style="margin: 1px 0; font-size: 8px;">🔵 Top 10: bolhas + números</p>
    <p style="margin: 1px 0; font-size: 8px;">🔺 Demais: losangos pequenos</p>
    </div>
    '''
    m.get_root().html.add_child(folium.Element(legenda_html))
    
    return m