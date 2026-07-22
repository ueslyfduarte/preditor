import streamlit as st
import pandas as pd
import requests
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
                # 🛠️ CORREÇÃO DO ERRO 403: Simulando um navegador real (User-Agent)
                headers = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
                }
                
                # Baixa o conteúdo da página fingindo ser um humano no Chrome
                resposta = requests.get(LIGAS[liga_selecionada], headers=headers)
                
                if resposta.status_code == 200:
                    # Passamos o texto do HTML baixado para o Pandas, em vez da URL direta
                    tabelas = pd.read_html(resposta.text, match="Classificação")
                    
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
                        st.error("Tabela não encontrada na estrutura da página.")
                else:
                    st.error(f"O servidor do site recusou o acesso. Código de erro: {resposta.status_code}")
                    
            except Exception as e:
                st.error(f"Erro na raspagem: {e}")
