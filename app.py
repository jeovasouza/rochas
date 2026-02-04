@st.cache_data
def load_data():
    import os
    import glob
    
    # Lista de tentativas por ordem de prioridade
    arquivos_alvo = ['dados.csv', 'Dados brutos.xlsx - Plan1.csv']
    arquivo_final = None

    # 1. Tenta nomes específicos
    for nome in arquivos_alvo:
        if os.path.exists(nome):
            arquivo_final = nome
            break
    
    # 2. Se não achou, pega o primeiro arquivo CSV que existir na raiz
    if not arquivo_final:
        lista_csvs = glob.glob("*.csv")
        if lista_csvs:
            arquivo_final = lista_csvs[0]

    if arquivo_final:
        try:
            # Lendo o CSV (Tratando separador e encoding comum em arquivos brasileiros)
            df = pd.read_csv(arquivo_final, decimal=',', encoding='utf-8')
            
            # Padronização de Colunas
            colunas_financeiras = ['Consumo Total', 'Custo Direto Unit.', 'CIF', 'Custo Padrão']
            for col in colunas_financeiras:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
            
            # Cálculo de Eficiência
            if 'Custo Padrão' in df.columns and 'Consumo Total' in df.columns:
                df['R$/m2'] = (df['Custo Padrão'] / df['Consumo Total']).replace([np.inf, -np.inf], 0).fillna(0)
            
            return df
        except Exception as e:
            st.error(f"Erro ao processar o conteúdo de '{arquivo_final}': {e}")
            return None
    else:
        st.error("❌ Erro Crítico: Nenhum arquivo CSV encontrado no repositório GitHub!")
        return None
