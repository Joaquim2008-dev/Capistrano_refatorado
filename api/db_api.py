import requests
import pandas as pd
import streamlit as st

def baixar_dados_clientes():
    """Baixa dados dos clientes da API usando secrets do Streamlit"""
    try:
        # Usar configurações do secrets
        url_clientes = st.secrets["api"]["url_clientes"]
        token = st.secrets["api"]["token"]
        
        headers = {
            "token": token
        }
        
        response = requests.get(url_clientes, headers=headers, timeout=30)
        
        if response.status_code == 200:
            dados = response.json()
            
            # Extrair a lista de clientes do primeiro item
            if isinstance(dados, list) and len(dados) > 0 and 'clientes' in dados[0]:
                lista_clientes = dados[0]['clientes']
                
                # Converter para DataFrame
                df = pd.DataFrame(lista_clientes)
                
                print(f"✅ Dados baixados com sucesso! {len(df)} clientes encontrados.")
                return df
            else:
                print("❌ Estrutura de dados inesperada")
                print(f"Dados recebidos: {dados}")
                return pd.DataFrame()
        
        else:
            print(f"❌ Erro na API: {response.status_code}")
            print(f"Resposta: {response.text}")
            return pd.DataFrame()
            
    except Exception as e:
        print(f"❌ Erro ao conectar com a API: {e}")
        return pd.DataFrame()

def baixar_dados_processos():
    """Baixa dados dos processos da API usando secrets do Streamlit"""
    try:
        # Usar configurações do secrets
        url_processos = st.secrets["api"]["url_processos"]
        token = st.secrets["api"]["token"]
        
        # Adicionar parâmetros de data
        url_completa = f"{url_processos}?dataInicio=2010-01-01&dataFim=2030-12-31"
        
        headers = {
            "token": token
        }
        
        response = requests.get(url_completa, headers=headers, timeout=30)
        
        if response.status_code == 200:
            dados = response.json()
            
            # Extrair a lista de processos do primeiro item
            if isinstance(dados, list) and len(dados) > 0 and 'processos' in dados[0]:
                lista_processos = dados[0]['processos']
                
                # Converter para DataFrame
                df = pd.DataFrame(lista_processos)
                
                print(f"✅ Dados baixados com sucesso! {len(df)} processos encontrados.")
                return df
            else:
                print("❌ Estrutura de dados inesperada")
                print(f"Dados recebidos: {dados}")
                return pd.DataFrame()
        
        else:
            print(f"❌ Erro na API: {response.status_code}")
            print(f"Resposta: {response.text}")
            return pd.DataFrame()
            
    except Exception as e:
        print(f"❌ Erro ao conectar com a API: {e}")
        return pd.DataFrame()

def baixar_dados_tarefas():
    """Baixa dados de tarefas da API usando secrets do Streamlit"""
    try:
        # Usar configurações do secrets
        url_tarefas = st.secrets["api"]["url_tarefas"]
        token = st.secrets["api"]["token"]
        
        headers = {
            "token": token
        }
        
        response = requests.get(url_tarefas, headers=headers, timeout=30)
        
        if response.status_code == 200:
            dados = response.json()
            
            # Extrair a lista de tarefas do primeiro item
            if isinstance(dados, list) and len(dados) > 0 and 'tarefas' in dados[0]:
                lista_tarefas = dados[0]['tarefas']
                
                # Converter para DataFrame
                df = pd.DataFrame(lista_tarefas)
                
                print(f"✅ Dados baixados com sucesso! {len(df)} tarefas encontrados.")
                return df
            else:
                print("❌ Estrutura de dados inesperada")
                print(f"Dados recebidos: {dados}")
                return pd.DataFrame()
        
        else:
            print(f"❌ Erro na API: {response.status_code}")
            print(f"Resposta: {response.text}")
            return pd.DataFrame()
            
    except Exception as e:
        print(f"❌ Erro ao conectar com a API: {e}")
        return pd.DataFrame()