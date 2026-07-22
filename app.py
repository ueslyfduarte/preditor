import streamlit as st
import pandas as pd
import time
import requests

# Configuração da página do Streamlit
st.set_page_config(page_title="Teste de Raspagem FBref", layout="centered")

st.title("⚽ Raspador Controlado - FBref")
st.markdown("Versão otimizada para rodar direto no celular.")

# Dicionário mapeando as URLs das ligas direto do FBref
LIGAS = {
    "Premier League (Inglaterra)": "https://fbref.com",
    "Brasileirão Série A": "https://fbref.com",
    "La Liga (Espanha)": "https://fbref.com",
    "Serie A (Itália)": "https://fbref.com"
}

# Interface: Seleção da liga
liga_selecionada = st.selectbox("Selecione a Liga para testar:", list(LIGAS.keys()))

if "ultimo_acesso" not in st.session_state:
    st.session_state.ultimo_acesso = 0

if st.button("Executar Raspagem Real"):
    tempo_atual = time.time()
    tempo_decorrido = tempo_atual - st.session_state.ultimo_acesso
    
    if tempo_decorrido < 4:
        tempo_restante = int(4 - tempo_decorrido)
        st.warning(f"⏳ Aguarde {tempo_restante} segundos antes de raspar novamente!")
    else:
        st.session_state.ultimo_acesso = tempo_atual
        url_alvo = LIGAS[liga_selecionada]
        
        with st.spinner("Conectando ao FBref..."):
            try:
                # 🛠️ MUDANÇA AQUI: Baixamos o HTML manualmente primeiro para evitar o erro do lxml
                headers = {"User-Agent": "Mozilla/5.0"}
                resposta = requests.get(url_alvo, headers=headers)
                
                # Forçamos o Pandas a usar o 'html5lib' ou o parser padrão que já existem no celular
                tabelas = pd.read_html(resposta.text, match="Classificação", flavor="html5lib")
                
                if tabelas:
                    df = tabelas[0]
                    
                    # Limpeza simples de colunas indesejadas se elas existirem
                    for col in ["Notas", "Últimos 5"]:
                        if col in df.columns:
                            df = df.drop(columns=[col])
                    
                    st.success(f"📊 Dados de {liga_selecionada} capturados!")
                    st.dataframe(df, use_container_width=True, hide_index=True)
                else:
                    st.error("A tabela não foi encontrada.")
                    
            except Exception as e:
                # Se ainda assim falhar por falta do html5lib, tentamos a última alternativa nativa
                try:
                    tabelas = pd.read_html(resposta.text, match="Classificação", flavor="bs4")
                    df = tabelas[0]
                    st.success(f"📊 Dados de {liga_selecionada} capturados (Modo de Segurança)!")
                    st.dataframe(df, use_container_width=True, hide_index=True)
                except Exception as erro_final:
                    st.error(f"Erro na raspagem pelo celular: {erro_final}")
