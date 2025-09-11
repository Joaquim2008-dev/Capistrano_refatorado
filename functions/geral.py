import streamlit as st
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import requests
import zipfile
import os
from pathlib import Path
from unidecode import unidecode

def aplicar_filtro_sergipe(df):
    """
    Filtra apenas processos de cidades de Sergipe
    """
    # Lista de municípios de Sergipe (você pode expandir essa lista)
    municipios_sergipe = [
        'ARACAJU', 'NOSSA SENHORA DO SOCORRO', 'LAGARTO', 'ITABAIANA', 
        'ESTANCIA', 'SIMAO DIAS', 'PROPRIÁ', 'TOBIAS BARRETO', 'CANINDE DE SAO FRANCISCO',
        'BARRA DOS COQUEIROS', 'SAO CRISTOVAO', 'CARMOPOLIS', 'SANTO AMARO DAS BROTAS',
        'FEIRA NOVA', 'RIBEIROPOLIS', 'POCO VERDE', 'CAMPO DO BRITO', 'ARAUA',
        'FREI PAULO', 'MACAMBIRA', 'SAO DOMINGOS', 'PEDRA MOLE', 'POCO REDONDO',
        'AQUIDABA', 'DIVINA PASTORA', 'GENERAL MAYNARD', 'ROSARIO DO CATETE',
        'MARUIM', 'RIACHUELO', 'LARANJEIRAS', 'CAPELA', 'SIRIRI', 'JAPARATUBA',
        'PIRAMBU', 'PACATUBA', 'SANTANA DO SAO FRANCISCO', 'NEOPOPOLIS', 'BREJO GRANDE',
        'ILHA DAS FLORES', 'CEDRO DE SAO JOAO', 'TELHA', 'MONTE ALEGRE DE SERGIPE',
        'NOSSA SENHORA DA GLORIA', 'GARARU', 'POCO REDONDO', 'AMPARO DE SAO FRANCISCO',
        'MURIBECA', 'SAO FRANCISCO', 'CUMBE', 'GRACCHO CARDOSO', 'NOSSA SENHORA APARECIDA',
        'ITABI', 'PEDRINHAS', 'PINHAO', 'CARIRA', 'FREI PAULO', 'NOSSA SENHORA DAS DORES',
        'CANHOBA', 'AREIA BRANCA', 'SIMAO DIAS', 'POCO VERDE'
    ]
    
    # Normalizar nomes (maiúsculo, sem acentos)
    df_filtrado = df.copy()
    df_filtrado['cidade_normalizada'] = df_filtrado['cidade'].str.upper().str.strip()
    
    # Filtrar apenas cidades de Sergipe
    df_sergipe = df_filtrado[df_filtrado['cidade_normalizada'].isin(municipios_sergipe)]
    
    return df_sergipe

def processar_dados_municipios(df_sergipe, gdf_municipios):
    """
    Processa dados de processos por município
    """
    # Limpar nomes
    df_sergipe['cidade_limpa'] = df_sergipe['cidade'].str.upper().str.strip()
    gdf_municipios['nome_limpo'] = gdf_municipios['NM_MUN'].str.upper().str.strip()
    
    # Contar processos por cidade
    contagem_processos = df_sergipe['cidade_limpa'].value_counts().reset_index()
    contagem_processos.columns = ['cidade_limpa', 'num_processos']
    
    # Merge com shapefile
    gdf_com_processos = gdf_municipios.merge(
        contagem_processos,
        left_on='nome_limpo',
        right_on='cidade_limpa',
        how='left'
    )
    
    gdf_com_processos['num_processos'] = gdf_com_processos['num_processos'].fillna(0)
    
    return gdf_com_processos, contagem_processos

def criar_mapa_plotly(gdf_com_processos):
    """
    Cria mapa interativo com Plotly
    """
    # Converter para formato adequado
    gdf_com_processos_wgs84 = gdf_com_processos.to_crs(epsg=4326)
    
    # Criar mapa choropleth
    fig = px.choropleth_mapbox(
        gdf_com_processos_wgs84,
        geojson=gdf_com_processos_wgs84.geometry.__geo_interface__,
        locations=gdf_com_processos_wgs84.index,
        color='num_processos',
        color_continuous_scale='Viridis',
        hover_name='NM_MUN',
        hover_data={'num_processos': True},
        mapbox_style="open-street-map",
        zoom=7,
        center={"lat": -10.5, "lon": -37.3},
        opacity=0.7,
        title="Número de Processos por Município - Sergipe"
    )
    
    fig.update_layout(
        height=600,
        margin=dict(l=0, r=0, t=50, b=0)
    )
    
    return fig

def exibir_kpis(df_sergipe, contagem_processos):
    """
    Exibe KPIs principais em destaque
    """
    total_processos = len(df_sergipe)
    total_municipios = len(contagem_processos)
    municipios_com_processos = len(contagem_processos[contagem_processos['num_processos'] > 0])
    media_processos = contagem_processos['num_processos'].mean()
    municipio_top = contagem_processos.iloc[0] if len(contagem_processos) > 0 else None
    
    # KPIs em colunas
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="📊 Total de Processos",
            value=f"{total_processos:,}",
            help="Total de processos em Sergipe"
        )
    
    with col2:
        st.metric(
            label="🏙️ Municípios Atendidos",
            value=f"{municipios_com_processos}/{total_municipios}",
            delta=f"{municipios_com_processos/total_municipios*100:.1f}%",
            help="Percentual de municípios com processos"
        )
    
    with col3:
        st.metric(
            label="📈 Média por Município",
            value=f"{media_processos:.1f}",
            help="Média de processos por município"
        )
    
    with col4:
        if municipio_top is not None:
            st.metric(
                label="🥇 Município Líder",
                value=municipio_top['cidade_limpa'],
                delta=f"{municipio_top['num_processos']} processos",
                help="Município com mais processos"
            )

def criar_graficos_analise(contagem_processos):
    """
    Cria gráficos de análise
    """
    # Top 10 municípios
    top_10 = contagem_processos.head(10)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🏆 Top 10 Municípios")
        
        fig_bar = px.bar(
            top_10,
            x='num_processos',
            y='cidade_limpa',
            orientation='h',
            color='num_processos',
            color_continuous_scale='Viridis',
            title="Municípios com Mais Processos"
        )
        fig_bar.update_layout(
            height=400,
            yaxis={'categoryorder': 'total ascending'}
        )
        st.plotly_chart(fig_bar, use_container_width=True)
    
    with col2:
        st.subheader("📊 Distribuição de Processos")
        
        # Histograma da distribuição
        fig_hist = px.histogram(
            contagem_processos,
            x='num_processos',
            nbins=20,
            title="Distribuição do Número de Processos",
            color_discrete_sequence=['skyblue']
        )
        fig_hist.update_layout(height=400)
        st.plotly_chart(fig_hist, use_container_width=True)

def padronizar_reu(reu_text):
    """
    Padroniza nomes de réus, especialmente bancos e instituições
    """
    if pd.isna(reu_text) or str(reu_text).strip() == '':
        return 'NÃO INFORMADO'
    
    # Normalizar: maiúsculo e sem acentos
    texto = unidecode(str(reu_text).upper().strip())
    
    # INSS - qualquer texto que contenha INSS
    if 'INSS' in texto:
        return 'INSS'
    
    # CAIXA ECONÔMICA FEDERAL - diversas variações
    if any(palavra in texto for palavra in ['CAIXA ECONOMICA', 'CEF', 'CAIXA FEDERAL']):
        return 'CAIXA'
    elif 'CAIXA' in texto and ('BANCO' in texto or 'FEDERAL' in texto or len(texto.split()) == 1):
        return 'CAIXA'
    
    # BANCO DO BRASIL
    if any(variacao in texto for variacao in ['BANCO DO BRASIL', 'BANCO BRASIL']):
        return 'BANCO DO BRASIL'
    elif texto in ['BB', 'B.B.'] or (len(texto) <= 5 and 'BB' in texto):
        return 'BANCO DO BRASIL'
    
    # BRADESCO
    if 'BRADESCO' in texto:
        return 'BRADESCO'
    
    # ITAÚ
    if any(variacao in texto for variacao in ['ITAU', 'ITAÚ', 'BANCO ITAU']):
        return 'ITAU'
    
    # SANTANDER
    if 'SANTANDER' in texto:
        return 'SANTANDER'
    
    # CREFISA
    if 'CREFISA' in texto:
        return 'CREFISA'
    
    # BMG
    if 'BMG' in texto or 'BANCO BMG' in texto:
        return 'BMG'
    
    # PAN
    if 'BANCO PAN' in texto or (len(texto) <= 10 and 'PAN' in texto):
        return 'BANCO PAN'
    
    # INTER
    if 'BANCO INTER' in texto or 'INTER' in texto:
        return 'BANCO INTER'
    
    # SAFRA
    if 'SAFRA' in texto:
        return 'BANCO SAFRA'
    
    # ORIGINAL
    if 'ORIGINAL' in texto:
        return 'BANCO ORIGINAL'
    
    # C6 BANK
    if 'C6' in texto or 'C6 BANK' in texto:
        return 'C6 BANK'
    
    # NUBANK
    if 'NUBANK' in texto or 'NU BANK' in texto:
        return 'NUBANK'
    
    # VOTORANTIM
    if 'VOTORANTIM' in texto:
        return 'BANCO VOTORANTIM'
    
    # BV (antigo Votorantim)
    if texto == 'BV' or 'BANCO BV' in texto:
        return 'BANCO BV'
    
    # BANRISUL
    if 'BANRISUL' in texto:
        return 'BANRISUL'
    
    # SICOOB
    if 'SICOOB' in texto:
        return 'SICOOB'
    
    # SICREDI
    if 'SICREDI' in texto:
        return 'SICREDI'
    
    # MERCADO PAGO/MERCADO LIVRE
    if 'MERCADO PAGO' in texto or 'MERCADOPAGO' in texto:
        return 'MERCADO PAGO'
    elif 'MERCADO LIVRE' in texto or 'MERCADOLIVRE' in texto:
        return 'MERCADO LIVRE'
    
    # LOSANGO
    if 'LOSANGO' in texto:
        return 'LOSANGO'
    
    # AYMORÉ
    if 'AYMO' in texto or 'AYMORE' in texto:
        return 'AYMORE'
    
    # BANCO CETELEM
    if 'CETELEM' in texto:
        return 'CETELEM'
    
    # EMPRÉSTIMOS/FINANCEIRAS comuns
    if 'CREDITAS' in texto:
        return 'CREDITAS'
    elif 'OLE' in texto and 'CONSIG' in texto:
        return 'OLE CONSIGNADO'
    elif 'CREDSYSTEM' in texto:
        return 'CREDSYSTEM'
    
    # Se não encontrou padrão específico, retorna o texto limpo
    return texto