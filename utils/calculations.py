# utils/calculations.py
import pandas as pd
from datetime import datetime

def calcular_idade_processos(df):
    """Calcula idade dos processos em dias e anos"""
    if 'data' not in df.columns:
        return df
    
    df = df.copy()
    try:
        df['data_convertida'] = pd.to_datetime(df['data'], errors='coerce')
        
        # CORREÇÃO: Usar apenas pd.Timestamp.now() sem timezone
        hoje = pd.Timestamp.now()
        
        # Garantir que ambas as datas não tenham timezone
        df['data_convertida'] = pd.to_datetime(df['data_convertida']).dt.tz_localize(None)
        
        df['idade_processo_dias'] = (hoje - df['data_convertida']).dt.days
        df['idade_processo_anos'] = df['idade_processo_dias'] / 365.25
        
    except Exception as e:
        print(f"Erro ao calcular idade dos processos: {e}")
        df['idade_processo_anos'] = None
    
    return df

def calcular_idade_clientes(df):
    """Calcula idade dos clientes baseado em dia/mês/ano nascimento"""
    if not all(col in df.columns for col in ['diaNascimento', 'mesNascimento', 'anoNascimento']):
        return df
    
    df = df.copy()
    try:
        # CORREÇÃO: Usar apenas pd.Timestamp.now() sem timezone
        hoje = pd.Timestamp.now()
        
        # Filtrar dados válidos
        dados_nascimento = df[['anoNascimento', 'mesNascimento', 'diaNascimento']].copy()
        dados_nascimento = dados_nascimento.dropna()
        dados_nascimento = dados_nascimento[
            (dados_nascimento['anoNascimento'] > 1900) &
            (dados_nascimento['anoNascimento'] <= hoje.year) &
            (dados_nascimento['mesNascimento'] >= 1) &
            (dados_nascimento['mesNascimento'] <= 12) &
            (dados_nascimento['diaNascimento'] >= 1) &
            (dados_nascimento['diaNascimento'] <= 31)
        ]
        
        if len(dados_nascimento) > 0:
            df['dataNascimento'] = pd.to_datetime(
                dados_nascimento.rename(
                    columns={'anoNascimento': 'year', 'mesNascimento': 'month', 'diaNascimento': 'day'}
                ), errors='coerce'
            )
            
            df['idade_cliente_anos'] = ((hoje - df['dataNascimento']).dt.days / 365.25)
            
            # Filtrar idades razoáveis
            df.loc[
                (df['idade_cliente_anos'] < 0) | 
                (df['idade_cliente_anos'] > 120), 
                'idade_cliente_anos'
            ] = None
        else:
            df['idade_cliente_anos'] = None
            
    except Exception as e:
        print(f"Erro ao calcular idade dos clientes: {e}")
        df['idade_cliente_anos'] = None
    
    return df