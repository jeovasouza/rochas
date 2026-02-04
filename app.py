import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import os
import glob

# Configuração da página (Deve ser o primeiro comando Streamlit)
st.set_page_config(page_title="Rochas Analytics Pro", layout="wide")

@st.cache_data
def load_data():
    # Lista de possíveis nomes para o arquivo
    arquivos_alvo = ['Dados brutos.xlsx - Plan1.csv', 'dados.csv']
    arquivo_final = None

    # Tenta encontrar o arquivo
    for nome in arquivos_alvo:
        if os.path.exists(nome):
            arquivo_final = nome
            break
    
    if not arquivo_final:
        lista_csvs = glob.glob("*.csv")
        if lista_csvs:
            arquivo_final = lista_csvs[0]

    if arquivo_final:
        try:
            # Carrega o CSV
            df = pd.read_csv(arquivo_final)
            # Limpa colunas financeiras
            cols = ['Consumo Total', 'Custo Direto Unit.', 'CIF', 'Custo Padrão']
            for col in cols:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
            # Cria métrica de eficiência
            if 'Custo Padrão' in df.columns and 'Consumo Total' in df.columns:
                df['R$/m2'] = (df['Custo Padrão'] / df['Consumo Total'].replace(0, 1)).fillna(0)
            return df
        except Exception as e:
            st.error(f"Erro ao processar arquivo: {e}")
            return None
    return None

# Execução do Dashboard
df = load_data()

if df is not None:
    st.title("💎 Dashboard Rochas Ornamentais")
    
    # --- SIDEBAR ---
    st.sidebar.header("Configurações")
    tema = st.sidebar.selectbox("Tema", ["plotly_dark", "plotly_white"])
    
    # --- KPIs ---
    c1, c2, c3 = st.columns(3)
    c1.metric("Custo Total", f"R$ {df['Custo Padrão'].sum():,.2f}")
    c2.metric("Média R$/m²", f"R$ {df['R$/m2'].mean():,.2f}")
    c3.metric("Volume Total", f"{df['Consumo Total'].sum():,.2f} m²")

    # --- GRÁFICO ---
    st.subheader("Análise por Processo")
    fig = px.bar(df, x="Complemento", y="Custo Padrão", color="Classificação Insumos", template=tema)
    st.plotly_chart(fig, use_container_width=True)
    
    # --- TABELA ---
    st.subheader("Dados brutos")
    st.dataframe(df, use_container_width=True)
else:
    st.error("Aguardando arquivo CSV no GitHub...")
