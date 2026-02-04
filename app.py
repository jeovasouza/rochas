import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
import os
import glob

# 1. Configuração Inicial
st.set_page_config(page_title="Analytics Rochas", layout="wide")

# 2. Carregamento Ultra-Robusto
@st.cache_data
def load_data():
    # Procura qualquer arquivo CSV na raiz
    arquivos = glob.glob("*.csv")
    if not arquivos:
        return None
    
    # Tenta o primeiro arquivo encontrado
    caminho = arquivos[0]
    
    try:
        # Tenta ler com diferentes configurações comuns no Brasil
        try:
            df = pd.read_csv(caminho, sep=',', encoding='utf-8')
            if len(df.columns) <= 1: raise Exception()
        except:
            df = pd.read_csv(caminho, sep=';', encoding='latin1')

        # Limpa nomes de colunas
        df.columns = [str(c).strip() for c in df.columns]

        # Converte colunas numéricas (limpa pontos e vírgulas de moeda)
        cols_financeiras = ['Consumo Total', 'Custo Direto Unit.', 'CIF', 'Custo Padrão']
        for col in cols_financeiras:
            if col in df.columns:
                df[col] = df[col].astype(str).str.replace('.', '', regex=False).str.replace(',', '.', regex=False)
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        
        return df
    except Exception as e:
        st.error(f"Erro na leitura: {e}")
        return None

# 3. Execução do Dashboard
df = load_data()

if df is not None:
    st.sidebar.title("🎨 Design & Filtros")
    tema = st.sidebar.selectbox("Tema", ["plotly_dark", "plotly_white"])
    
    # Filtro de Processo (Se a coluna existir)
    col_processo = 'Complemento' if 'Complemento' in df.columns else df.columns[0]
    processos = st.sidebar.multiselect("Filtrar Processo", df[col_processo].unique(), default=df[col_processo].unique())
    df_f = df[df[col_processo].isin(processos)]

    st.title("🏗️ Painel de Controle: Rochas Ornamentais")
    
    # KPIs principais
    c1, c2, c3 = st.columns(3)
    c1.metric("Custo Padrão Total", f"R$ {df_f['Custo Padrão'].sum():,.2f}")
    c2.metric("Consumo (m²)", f"{df_f['Consumo Total'].sum():,.2f}")
    c3.metric("Média Custo/Unid", f"R$ {df_f['Custo Direto Unit.'].mean():,.2f}")

    st.divider()

    # Gráfico de Barras Editável
    st.subheader("Análise de Custos por Categoria")
    col_insumo = 'Classificação Insumos' if 'Classificação Insumos' in df.columns else df.columns[1]
    
    fig = px.bar(df_f, x=col_processo, y="Custo Padrão", color=col_insumo, 
                 template=tema, barmode="group", height=500)
    st.plotly_chart(fig, use_container_width=True)

    # Tabela de Dados
    with st.expander("🔎 Visualizar Dados Brutos"):
        st.dataframe(df_f, use_container_width=True)
else:
    st.error("⚠️ O arquivo CSV foi encontrado, mas está vazio ou em formato inválido.")
    st.info("Dica: Abra o arquivo no seu computador e verifique se existem dados abaixo dos títulos das colunas.")
