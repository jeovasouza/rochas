import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import os
import glob

# 1. CONFIGURAÇÃO DA PÁGINA
st.set_page_config(page_title="Gestão Rochas Pro", layout="wide", initial_sidebar_state="expanded")

# 2. FUNÇÃO DE CARREGAMENTO INTELIGENTE
@st.cache_data
def load_data():
    # Procura por qualquer arquivo CSV na pasta raiz
    arquivos_csv = glob.glob("*.csv")
    if not arquivos_csv:
        return None
    
    # Prioriza o nome original ou pega o primeiro que encontrar
    arquivo_alvo = 'Dados brutos.xlsx - Plan1.csv' if 'Dados brutos.xlsx - Plan1.csv' in arquivos_csv else arquivos_csv[0]
    
    try:
        # Tenta ler com separadores comuns
        df = pd.read_csv(arquivo_alvo, sep=',', encoding='utf-8')
        if len(df.columns) <= 1:
            df = pd.read_csv(arquivo_alvo, sep=';', encoding='latin1')

        # Limpeza de nomes de colunas (importante para o seu arquivo)
        df.columns = [c.strip() for c in df.columns]

        # Conversão de colunas numéricas (limpando o formato brasileiro se necessário)
        cols_financeiras = ['Consumo Total', 'Custo Direto Unit.', 'CIF', 'Custo Padrão']
        for col in cols_financeiras:
            if col in df.columns:
                if df[col].dtype == object:
                    df[col] = df[col].astype(str).str.replace('.', '', regex=False).str.replace(',', '.', regex=False)
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        
        # Métrica de eficiência (R$ por unidade de medida)
        if 'Custo Padrão' in df.columns and 'Consumo Total' in df.columns:
            df['Eficiencia_R$'] = (df['Custo Padrão'] / df['Consumo Total'].replace(0, 1)).fillna(0)
        
        return df
    except Exception as e:
        st.error(f"Erro ao processar arquivo: {e}")
        return None

# 3. INTERFACE DO DASHBOARD
df = load_data()

if df is not None:
    # --- SIDEBAR: DESIGN E CONTROLE ---
    st.sidebar.title("💎 Painel Industrial")
    
    with st.sidebar.expander("🎨 Personalizar Design", expanded=True):
        tema_viz = st.selectbox("Estilo dos Gráficos", ["plotly_dark", "plotly_white", "ggplot2"])
        paleta = st.selectbox("Paleta de Cores", ["Viridis", "Prism", "Set1"])
        tipo_grafico = st.radio("Modelo de Análise", ["Barras", "Treemap", "Linhas"])

    with st.sidebar.expander("🔮 Simulação de Custos", expanded=False):
        ajuste_custo = st.slider("Aumento Insumos (%)", 0, 50, 0)
    
    # Filtros de Processo
    if 'Complemento' in df.columns:
        linhas = st.sidebar.multiselect("Linhas de Produção", df['Complemento'].unique(), default=df['Complemento'].unique())
        df_f = df[df['Complemento'].isin(linhas)]
    else:
        df_f = df

    # --- CORPO PRINCIPAL ---
    st.title("📊 Analytics: Indústria de Rochas")
    st.caption(f"Analisando dados do arquivo: {glob.glob('*.csv')[0]}")

    # KPIs
    c1, c2, c3, c4 = st.columns(4)
    custo_total = df_f['Custo Padrão'].sum() * (1 + ajuste_custo/100)
    
    c1.metric("Custo Total", f"R$ {custo_total:,.2f}")
    c2.metric("Consumo Metragem", f"{df_f['Consumo Total'].sum():,.2f}")
    c3.metric("Média Custo/Unit", f"R$ {df_f['Custo Direto Unit.'].mean():,.2f}")
    c4.metric("Itens Processados", len(df_f))

    st.divider()

    # --- GRÁFICOS DINÂMICOS ---
    col_dir, col_esq = st.columns([6, 4])

    with col_dir:
        st.subheader("Distribuição de Custo por Processo/Insumo")
        if tipo_grafico == "Barras":
            fig = px.bar(df_f, x="Complemento", y="Custo Padrão", color="Classificação Insumos", 
                         template=tema_viz, barmode="group", color_discrete_sequence=getattr(px.colors.qualitative, paleta))
        elif tipo_grafico == "Treemap":
            fig = px.treemap(df_f, path=['Complemento', 'Classificação Insumos'], values='Custo Padrão', 
                             template=tema_viz, color_discrete_sequence=getattr(px.colors.qualitative, paleta))
        else:
            fig = px.line(df_f.groupby('Complemento')['Custo Padrão'].sum().reset_index(), 
                          x='Complemento', y='Custo Padrão', template=tema_viz)
        
        st.plotly_chart(fig, use_container_width=True)

    with col_esq:
        st.subheader("Participação por Classe")
        fig_pie = px.pie(df_f, values='Custo Padrão', names='Classificação Insumos', 
                         hole=0.5, template=tema_viz, color_discrete_sequence=getattr(px.colors.qualitative, paleta))
        st.plotly_chart(fig_pie, use_container_width=True)

    # --- AUDITORIA DE IA ---
    st.divider()
    st.subheader("🚨 Auditoria de Desvios (IA)")
    # Identifica itens onde o custo unitário está acima da média
    media_custo = df_f['Eficiencia_R$'].mean()
    df_critico = df_f[df_f['Eficiencia_R$'] > (media_custo * 1.5)]
    
    if not df_critico.empty:
        st.warning(f"Foram detectados {len(df_critico)} lançamentos com custo 50% acima da média.")
        st.dataframe(df_critico[['Código+Derivação', 'Processo', 'Complemento', 'Custo Padrão', 'Eficiencia_R$']], use_container_width=True)
    else:
        st.success("Operação dentro dos padrões de custo.")

else:
    st.error("❌ ERRO: Arquivo CSV não encontrado ou está vazio no GitHub.")
    st.info("Certifique-se de que o arquivo 'Dados brutos.xlsx - Plan1.csv' está na raiz do repositório.")
