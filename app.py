import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

# Configuração de alta performance
st.set_page_config(page_title="Rochas Analytics Pro", layout="wide", initial_sidebar_state="expanded")

# Carregamento e Tratamento Sênior
@st.cache_data
def load_data():
    try:
        df = pd.read_csv('Dados brutos.xlsx - Plan1.csv')
        cols_financeiras = ['Consumo Total', 'Custo Direto Unit.', 'CIF', 'Custo Padrão']
        for col in cols_financeiras:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        
        # Engenharia de Atributos: Eficiência por m2
        df['R$/m2'] = (df['Custo Padrão'] / df['Consumo Total']).replace([np.inf, -np.inf], 0).fillna(0)
        return df
    except Exception as e:
        st.error(f"Erro ao carregar arquivo: {e}")
        return None

df = load_data()

if df is not None:
    # --- SIDEBAR ESTRATÉGICA ---
    st.sidebar.title("🎮 Controle de Gestão")
    
    with st.sidebar.expander("🎨 Aparência", expanded=False):
        tema = st.selectbox("Tema Visual", ["plotly_dark", "plotly_white", "ggplot2"])
        cor_foco = st.color_picker("Cor de Destaque", "#00e5ff")

    with st.sidebar.expander("🔮 Simulador de Mercado", expanded=True):
        inflacao = st.slider("Aumento Insumos (%)", 0, 50, 0)
        vol_proj = st.slider("Aumento Produção (%)", 0, 100, 0)
    
    # Filtro Dinâmico
    processos = st.sidebar.multiselect("Filtrar Processos", df['Complemento'].unique(), default=df['Complemento'].unique())
    df_f = df[df['Complemento'].isin(processos)].copy()

    # --- LÓGICA DE AUDITORIA IA ---
    media = df_f['R$/m2'].mean()
    desvio = df_f['R$/m2'].std()
    df_f['Alerta'] = df_f['R$/m2'] > (media + (1.5 * desvio)) # Sensibilidade de 1.5 desvios

    # --- TELA PRINCIPAL ---
    st.title("💎 Inteligência de Dados: Rochas Ornamentais")
    
    # KPIs com Projeção
    c1, c2, c3, c4 = st.columns(4)
    custo_atual = df_f['Custo Padrão'].sum()
    custo_previsto = custo_atual * (1 + inflacao/100) * (1 + vol_proj/100)
    
    c1.metric("Custo Atual Total", f"R$ {custo_atual:,.2f}")
    c2.metric("Projeção Cenário", f"R$ {custo_previsto:,.2f}", f"{((custo_previsto/custo_atual)-1)*100:.1f}%" if custo_atual > 0 else 0)
    c3.metric("Média R$/m²", f"R$ {df_f['R$/m2'].mean():,.2f}")
    c4.metric("Itens Críticos", len(df_f[df_f['Alerta']]))

    st.divider()

    # --- GRÁFICOS ---
    g1, g2 = st.columns([6, 4])

    with g1:
        st.subheader("Distribuição de Custos por Linha")
        fig_bar = px.bar(df_f, x="Complemento", y="Custo Padrão", color="Classificação Insumos", 
                         template=tema, barmode="group", color_discrete_sequence=px.colors.qualitative.Prism)
        st.plotly_chart(fig_bar, use_container_width=True)

    with g2:
        st.subheader("Pareto de Insumos")
        fig_pie = px.pie(df_f, values='Custo Padrão', names='Classificação Insumos', hole=0.5, template=tema)
        st.plotly_chart(fig_pie, use_container_width=True)

    # --- AUDITORIA DE PRODUTOS ---
    st.subheader("🚨 Auditoria de Produtos Fora do Padrão")
    df_criticos = df_f[df_f['Alerta']].sort_values('R$/m2', ascending=False)
    
    st.dataframe(
        df_criticos[['Código+Derivação', 'Processo', 'Complemento', 'Consumo Total', 'R$/m2']],
        column_config={
            "R$/m2": st.column_config.NumberColumn("Custo por m²", format="R$ %.2f"),
            "Consumo Total": st.column_config.NumberColumn("Metragem", format="%.2f m²")
        },
        use_container_width=True,
        hide_index=True
    )
