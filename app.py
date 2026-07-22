import streamlit as st
import pandas as pd
import time

st.set_page_config(page_title="Raspador FBref", layout="centered")
st.title("⚽ Estatísticas de Times - FBref")

LIGAS = {
    "Premier League (Inglaterra)": "https://fbref.com",
    "Brasileirão Série A": "https://fbref.com",
    "La Liga (Espanha)": "https://fbref.com",
    "Serie A (Itália)": "https://fbref.com"
}

liga_selecionada = st.selectbox("Selecione a Liga:", list(LIGAS.keys()))
nome_time = st.text_input("Digite o nome do time para filtrar (ex: Real Madrid, Flamengo):")

if "ultimo_acesso" not in st.session_state:
    st.session_state.ultimo_acesso = 0

if st.button("Buscar Estatísticas"):
    tempo_atual = time.time()
    if tempo_atual - st.session_state.ultimo_acesso < 4:
        st.warning("⏳ Aguarde 4 segundos antes de buscar novamente para respeitar o limite do site!")
    else:
        st.session_state.ultimo_acesso = tempo_atual
        
        with st.spinner("Raspando dados reais do FBref..."):
            try:
                # Agora com lxml no requirements.txt, esta linha funciona direto na nuvem
                tabelas = pd.read_html(LIGAS[liga_selecionada], match="Classificação")
                
                if tabelas:
                    df = tabelas[0]
                    
                    # Limpeza de colunas visuais do site
                    for col in ["Notas", "Últimos 5"]:
                        if col in df.columns:
                            df = df.drop(columns=[col])
                    
                    # Se o usuário digitou um time, filtra a tabela
                    if nome_time:
                        df = df[df['Equipe'].str.contains(nome_time, case=False, na=False)]
                    
                    if not df.empty:
                        st.success("Dados carregados com sucesso!")
                        st.dataframe(df, use_container_width=True, hide_index=True)
                    else:
                        st.warning("Nenhum time encontrado com esse nome na liga selecionada.")
                else:
                    st.error("Tabela não encontrada.")
            except Exception as e:
                st.error(f"Erro na raspagem: {e}")
