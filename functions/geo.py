# gerar_mapas_municipios.py
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.colors import LinearSegmentedColormap, Normalize
import requests
import json
from unidecode import unidecode
from pathlib import Path
import numpy as np
import sys

# Adicionar path para importar a função geo
project_root = Path(__file__).parent
sys.path.append(str(project_root))

def baixar_municipios_sergipe():
    """
    Baixa shapefile dos municípios de Sergipe do IBGE
    Cópia da função original para evitar import circular
    """
    print("🗺️ Baixando municípios de Sergipe do IBGE...")
    
    # URL do shapefile de municípios do IBGE
    url = "https://geoftp.ibge.gov.br/organizacao_do_territorio/malhas_territoriais/malhas_municipais/municipio_2024/UFs/SE/SE_Municipios_2024.zip"
    
    # Diretório para salvar
    pasta_shapefiles = Path("temp_shapefiles")
    pasta_shapefiles.mkdir(exist_ok=True)
    
    arquivo_zip = pasta_shapefiles / "se_municipios.zip"
    
    try:
        # Baixar arquivo se não existir
        if not arquivo_zip.exists():
            print("📥 Baixando arquivo...")
            response = requests.get(url, timeout=60)
            response.raise_for_status()
            
            with open(arquivo_zip, 'wb') as f:
                f.write(response.content)
            print("✅ Arquivo baixado com sucesso")
        
        # Extrair ZIP
        pasta_extracao = pasta_shapefiles / "se_municipios"
        if not pasta_extracao.exists():
            print("📂 Extraindo arquivos...")
            with zipfile.ZipFile(arquivo_zip, 'r') as zip_ref:
                zip_ref.extractall(pasta_extracao)
            print("✅ Arquivos extraídos")
        
        # Procurar arquivo .shp
        arquivos_shp = list(pasta_extracao.glob("*.shp"))
        
        if not arquivos_shp:
            print("❌ Arquivo .shp não encontrado na pasta extraída")
            return None
        
        # Carregar shapefile
        arquivo_shp = arquivos_shp[0]
        print(f"📊 Carregando shapefile: {arquivo_shp.name}")
        
        gdf = gpd.read_file(arquivo_shp)
        
        print(f"✅ {len(gdf)} municípios carregados com sucesso")
        return gdf
        
    except Exception as e:
        print(f"❌ Erro ao baixar municípios: {e}")
        return None
    
def baixar_dados_api():
    """Baixa dados completos da API (sem filtros de status)"""
    print("📥 Baixando dados da API...")
    
    # URLs e token
    url_processos = "https://apisp.fabricadetempo.cloud/webhook/korbil/capistrano/processos?dataInicio=2010-01-01&dataFim=2025-12-31"
    url_clientes = "https://apisp.fabricadetempo.cloud/webhook/korbil/capistrano/clientes"
    token = "A92FD-7C4BAE1F3C9-82E"
    
    headers = {"token": token}
    
    try:
        # Baixar processos
        print("📊 Baixando processos...")
        response_proc = requests.get(url_processos, headers=headers, timeout=60)
        response_proc.raise_for_status()
        dados_proc = response_proc.json()
        
        if isinstance(dados_proc, list) and len(dados_proc) > 0 and 'processos' in dados_proc[0]:
            df_processos = pd.DataFrame(dados_proc[0]['processos'])
            print(f"✅ {len(df_processos)} processos baixados")
        else:
            print("❌ Erro na estrutura dos dados de processos")
            return None, None
        
        # Baixar clientes
        print("👥 Baixando clientes...")
        response_cli = requests.get(url_clientes, headers=headers, timeout=60)
        response_cli.raise_for_status()
        dados_cli = response_cli.json()
        
        if isinstance(dados_cli, list) and len(dados_cli) > 0 and 'clientes' in dados_cli[0]:
            df_clientes = pd.DataFrame(dados_cli[0]['clientes'])
            print(f"✅ {len(df_clientes)} clientes baixados")
        else:
            print("❌ Erro na estrutura dos dados de clientes")
            return None, None
        
        return df_processos, df_clientes
        
    except Exception as e:
        print(f"❌ Erro ao baixar dados: {e}")
        return None, None

def corrigir_municipios(nome):
    """Corrige o nome dos municípios com base em regras específicas"""
    if pd.isna(nome):
        return ''
    
    nome_lower = unidecode(str(nome).lower())
    
    if 'socorro' in nome_lower or 'socoro' in nome_lower:
        return 'NOSSA SENHORA DO SOCORRO'
    elif 'itaporanga' in nome_lower:
        return "ITAPORANGA D'AJUDA"
    elif 'barra' in nome_lower and 'coqu' in nome_lower:
        return 'BARRA DOS COQUEIROS'
    elif 'japarat' in nome_lower:
        return 'JAPARATUBA'
    elif 'sao cristovao' in nome_lower or 'cristovao' in nome_lower or 'sao cris' in nome_lower:
        return 'SAO CRISTOVAO'
    elif 'neopolois' in nome_lower or 'neopolis' in nome_lower:
        return 'NEOPOLIS'
    elif 'maynard' in nome_lower:
        return 'GENERAL MAYNARD'
    elif 'santa rosa' in nome_lower:
        return 'SANTA ROSA DE LIMA'
    elif 'aracau' in nome_lower or 'aracaiu' in nome_lower:
        return 'ARACAJU'
    elif 'das flores' in nome_lower:
        return 'ILHA DAS FLORES'
    elif 'senhora apar' in nome_lower:
        return 'NOSSA SENHORA APARECIDA'
    elif 'aquibada' in nome_lower:
        return 'AQUIDABA'
    elif 'porto' in nome_lower and 'folha' in nome_lower:
        return 'PORTO DA FOLHA'
    elif 'propria' in nome_lower:
        return 'PROPRIA'
    elif 'tobias' in nome_lower:
        return 'TOBIAS BARRETO'
    elif 'estancia' in nome_lower:
        return 'ESTANCIA'
    elif 'lagarto' in nome_lower:
        return 'LAGARTO'
    elif 'itabaiana' in nome_lower and 'inha' not in nome_lower:
        return 'ITABAIANA'
    elif 'simao' in nome_lower:
        return 'SIMAO DIAS'
    
    return nome.upper()

def filtrar_sergipe(df_processos, df_clientes, apenas_ativos=True):
    """Filtra dados de Sergipe"""
    print(f"🔍 Filtrando dados de Sergipe (apenas_ativos={apenas_ativos})...")
    
    # Fazer merge
    df = df_processos.merge(df_clientes, on='idCliente', how='left', suffixes=('', '_cliente'))
    print(f"📊 Total após merge: {len(df)} registros")
    
    # Lista de cidades de Sergipe
    cidades_sergipe = [
        'AMPARO DE SAO FRANCISCO', 'AQUIDABA', 'ARACAJU', 'ARAUA',
        'AREIA BRANCA', 'BARRA DOS COQUEIROS', 'BOQUIM', 'BREJO GRANDE',
        'CAMPO DO BRITO', 'CANHOBA', 'CANINDE DE SAO FRANCISCO', 'CAPELA',
        'CARIRA', 'CARMOPOLIS', 'CEDRO DE SAO JOAO', 'CRISTINAPOLIS', 'CUMBE',
        'DIVINA PASTORA', 'ESTANCIA', 'FEIRA NOVA', 'FREI PAULO', 'GARARU',
        'GENERAL MAYNARD', 'GRACHO CARDOSO', 'ILHA DAS FLORES', 'INDIAROBA',
        'ITABAIANA', 'ITABAIANINHA', 'ITABI', "ITAPORANGA D'AJUDA", 'JAPARATUBA',
        'JAPOATA', 'LAGARTO', 'LARANJEIRAS', 'MACAMBIRA', 'MALHADA DOS BOIS',
        'MALHADOR', 'MARUIM', 'MOITA BONITA', 'MONTE ALEGRE DE SERGIPE',
        'MURIBECA', 'NEOPOLIS', 'NOSSA SENHORA APARECIDA', 'NOSSA SENHORA DA GLORIA',
        'NOSSA SENHORA DAS DORES', 'NOSSA SENHORA DE LOURDES', 'NOSSA SENHORA DO SOCORRO',
        'PACATUBA', 'PEDRA MOLE', 'PEDRINHAS', 'PINHAO',
        'PIRAMBU', 'POCO REDONDO', 'POCO VERDE', 'PORTO DA FOLHA',
        'PROPRIA', 'RIACHAO DO DANTAS', 'RIACHUELO', 'RIBEIROPOLIS',
        'ROSARIO DO CATETE', 'SALGADO', 'SANTA LUZIA DO ITANHY', 'SANTA ROSA DE LIMA',
        'SANTANA DO SAO FRANCISCO', 'SANTO AMARO DAS BROTAS', 'SAO CRISTOVAO',
        'SAO DOMINGOS', 'SAO FRANCISCO', 'SAO MIGUEL DO ALEIXO', 'SIMAO DIAS',
        'SIRIRI', 'TELHA', 'TOBIAS BARRETO', 'TOMAR DO GERU', 'UMBAUBA'
    ]
    
    # Filtrar dados válidos
    df_clean = df.dropna(subset=['cidade']).copy()
    df_clean['cidade_upper'] = df_clean['cidade'].str.upper().str.strip()
    
    # Aplicar correção de nomes
    df_clean['cidade_upper_corrigido'] = df_clean['cidade_upper'].apply(corrigir_municipios)
    
    # Filtrar apenas processos ativos se solicitado
    if apenas_ativos:
        df_clean = df_clean[df_clean['status'] == 'Ativo'].copy()
        print(f"📊 Após filtrar ativos: {len(df_clean)} registros")
    
    # Filtrar cidades de Sergipe
    df_sergipe = df_clean[df_clean['cidade_upper_corrigido'].isin(cidades_sergipe)]
    df_sergipe['cidade_upper'] = df_sergipe['cidade_upper_corrigido']
    
    print(f"✅ Sergipe filtrado: {len(df_sergipe)} registros")
    return df_sergipe

def carregar_municipios_sergipe():
    """Carrega municípios de Sergipe usando a função do geo.py"""
    print("🗺️ Baixando/carregando municípios de Sergipe...")
    
    try:
        # Usar a função existente do geo.py
        gdf_municipios = baixar_municipios_sergipe()
        
        if gdf_municipios is not None and len(gdf_municipios) > 0:
            print(f"✅ {len(gdf_municipios)} municípios carregados com sucesso")
            
            # Verificar se tem a coluna de nome
            if 'NM_MUN' not in gdf_municipios.columns:
                # Tentar encontrar coluna de nome do município
                colunas_nome = [col for col in gdf_municipios.columns if 'nome' in col.lower() or 'mun' in col.lower()]
                if colunas_nome:
                    gdf_municipios['NM_MUN'] = gdf_municipios[colunas_nome[0]]
                    print(f"📝 Usando coluna '{colunas_nome[0]}' como nome do município")
                else:
                    print("❌ Coluna de nome do município não encontrada")
                    return None
            
            return gdf_municipios
        else:
            print("❌ Falha ao carregar municípios de Sergipe")
            return None
            
    except Exception as e:
        print(f"❌ Erro ao carregar municípios: {e}")
        return None

def gerar_mapa_municipios(df_sergipe, gdf_municipios, titulo, nome_arquivo):
    """Gera mapa de municípios com contagem de processos"""
    print(f"🎨 Gerando mapa: {titulo}")
    
    # Contar processos por município
    contagem_municipios = df_sergipe['cidade_upper'].value_counts().reset_index()
    contagem_municipios.columns = ['cidade', 'num_processos']
    
    # Preparar shapefile
    gdf_municipios = gdf_municipios.copy()
    gdf_municipios['nome_upper'] = gdf_municipios['NM_MUN'].apply(
        lambda x: unidecode(str(x).upper().strip()) if pd.notna(x) else ''
    )
    
    # Merge com contagem
    gdf_com_processos = gdf_municipios.merge(
        contagem_municipios,
        left_on='nome_upper',
        right_on='cidade',
        how='left'
    )
    gdf_com_processos['num_processos'] = gdf_com_processos['num_processos'].fillna(0)
    
    # Estatísticas
    total_processos = gdf_com_processos['num_processos'].sum()
    municipios_com_processos = (gdf_com_processos['num_processos'] > 0).sum()
    total_municipios = len(gdf_com_processos)
    
    print(f"📊 {total_processos} processos em {municipios_com_processos}/{total_municipios} municípios")
    
    # Criar figura
    fig, ax = plt.subplots(1, 1, figsize=(16, 12))
    
    # Definir cores
    max_processos = gdf_com_processos['num_processos'].max()
    
    # Cores para diferentes faixas
    cores = []
    for _, row in gdf_com_processos.iterrows():
        num_proc = row['num_processos']
        if num_proc == 0:
            cores.append('#E8E8E8')  # Cinza claro para zero
        elif num_proc <= 10:
            cores.append('#FFF7BC')  # Amarelo claro
        elif num_proc <= 50:
            cores.append('#FEC44F')  # Amarelo
        elif num_proc <= 100:
            cores.append('#FE9929')  # Laranja
        elif num_proc <= 500:
            cores.append('#EC7014')  # Laranja escuro
        elif num_proc <= 1000:
            cores.append('#CC4C02')  # Vermelho escuro
        else:
            cores.append('#8C2D04')  # Marrom escuro
    
    # Plotar mapa
    gdf_com_processos.plot(
        ax=ax,
        color=cores,
        edgecolor='white',
        linewidth=0.8
    )
    
    # Adicionar números nos municípios
    for idx, row in gdf_com_processos.iterrows():
        if row['num_processos'] > 0:
            # Calcular centroide
            centroid = row['geometry'].centroid
            
            # Tamanho da fonte baseado no número de processos
            if row['num_processos'] >= 1000:
                fontsize = 14
                fontweight = 'bold'
            elif row['num_processos'] >= 100:
                fontsize = 12
                fontweight = 'bold'
            elif row['num_processos'] >= 10:
                fontsize = 10
                fontweight = 'normal'
            else:
                fontsize = 8
                fontweight = 'normal'
            
            # Cor do texto
            if row['num_processos'] >= 100:
                color = 'white'
            else:
                color = 'black'
            
            ax.text(
                centroid.x, centroid.y,
                str(int(row['num_processos'])),
                ha='center', va='center',
                fontsize=fontsize,
                fontweight=fontweight,
                color=color,
                bbox=dict(boxstyle="round,pad=0.2", facecolor='white', alpha=0.7, edgecolor='none')
            )
    
    # Configurar plot
    ax.set_xlim(gdf_com_processos.total_bounds[0] - 0.1, gdf_com_processos.total_bounds[2] + 0.1)
    ax.set_ylim(gdf_com_processos.total_bounds[1] - 0.1, gdf_com_processos.total_bounds[3] + 0.1)
    ax.set_aspect('equal')
    ax.axis('off')
    
    # Título e informações
    plt.suptitle(titulo, fontsize=20, fontweight='bold', y=0.95)
    
    # Subtítulo com estatísticas
    subtitulo = f"Total: {total_processos:,} processos em {municipios_com_processos} de {total_municipios} municípios"
    plt.figtext(0.5, 0.92, subtitulo, ha='center', fontsize=14, style='italic')
    
    # Top 5 municípios
    top_5 = gdf_com_processos.nlargest(5, 'num_processos')[['NM_MUN', 'num_processos']]
    top_5_texto = "Top 5: " + " | ".join([f"{row['NM_MUN']}: {int(row['num_processos'])}" for _, row in top_5.iterrows()])
    plt.figtext(0.5, 0.89, top_5_texto, ha='center', fontsize=12)
    
    # Legenda
    legend_elements = [
        mpatches.Patch(color='#E8E8E8', label='0 processos'),
        mpatches.Patch(color='#FFF7BC', label='1-10 processos'),
        mpatches.Patch(color='#FEC44F', label='11-50 processos'),
        mpatches.Patch(color='#FE9929', label='51-100 processos'),
        mpatches.Patch(color='#EC7014', label='101-500 processos'),
        mpatches.Patch(color='#CC4C02', label='501-1000 processos'),
        mpatches.Patch(color='#8C2D04', label='>1000 processos')
    ]
    
    ax.legend(handles=legend_elements, loc='lower left', bbox_to_anchor=(0, 0), fontsize=10)
    
    # Data de geração
    from datetime import datetime
    data_geracao = datetime.now().strftime("%d/%m/%Y %H:%M")
    plt.figtext(0.99, 0.01, f"Gerado em: {data_geracao}", ha='right', fontsize=8, alpha=0.7)
    
    # Salvar
    plt.tight_layout()
    plt.savefig(nome_arquivo, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    
    print(f"💾 Mapa salvo: {nome_arquivo}")

def main():
    """Função principal"""
    print("🗺️ GERADOR DE MAPAS - PROCESSOS POR MUNICÍPIO")
    print("="*50)
    
    # 1. Baixar dados
    df_processos, df_clientes = baixar_dados_api()
    if df_processos is None or df_clientes is None:
        print("❌ Falha ao baixar dados")
        return
    
    # 2. Carregar municípios de Sergipe usando função do geo.py
    gdf_municipios = carregar_municipios_sergipe()
    if gdf_municipios is None:
        print("❌ Falha ao carregar municípios de Sergipe")
        return
    
    # 3. Gerar mapas
    print("\n🎨 GERANDO MAPAS...")
    
    # MAPA 1: Todos os processos (ativos + inativos)
    print("\n1️⃣ MAPA 1: TODOS OS PROCESSOS")
    df_sergipe_todos = filtrar_sergipe(df_processos, df_clientes, apenas_ativos=False)
    gerar_mapa_municipios(
        df_sergipe_todos,
        gdf_municipios,
        "Capistrano Advogados - Todos os Processos por Município",
        "mapa_todos_processos.jpg"
    )
    
    # MAPA 2: Apenas processos ativos
    print("\n2️⃣ MAPA 2: APENAS PROCESSOS ATIVOS")
    df_sergipe_ativos = filtrar_sergipe(df_processos, df_clientes, apenas_ativos=True)
    gerar_mapa_municipios(
        df_sergipe_ativos,
        gdf_municipios,
        "Capistrano Advogados - Processos Ativos por Município",
        "mapa_processos_ativos.jpg"
    )
    
    print("\n✅ MAPAS GERADOS COM SUCESSO!")
    print("📁 Arquivos criados:")
    print("   - mapa_todos_processos.jpg")
    print("   - mapa_processos_ativos.jpg")
    print("\n🖨️ Pronto para impressão (300 DPI)")

if __name__ == "__main__":
    main()