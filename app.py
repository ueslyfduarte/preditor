import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
import time

st.set_page_config(page_title="Raspador Nativo FBref", layout="centered")
st.title("⚽ Raspador Nativo - FBref")
st.markdown("Código adaptado para rodar em celulares sem precisar de pacotes extras.")

LIGAS = {
    "Premier League (Inglaterra)": "https://fbref.com",
    "Brasileirão Série A": "https://fbref.com",
    "La Liga (Espanha)": "https://fbref.com",
    "Serie A (Itália)": "https://fbref.com"
}

liga_selecionada = st.selectbox("Selecione a Liga para testar:", list(LIGAS.keys()))

if "ultimo_acesso" not in st.session_state:
    st.session_state.ultimo_acesso = 0

if st.button("Executar Raspagem Real"):
    tempo_atual = time.time()
    if tempo_atual - st.session_state.ultimo_acesso < 4:
        st.warning("⏳ Aguarde alguns segundos antes de raspar novamente!")
    else:
        st.session_state.ultimo_acesso = tempo_atual
        url_alvo = LIGAS[liga_selecionada]
        
        with st.spinner("Extraindo dados com o leitor padrão do celular..."):
            try:
                headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
                resposta = requests.get(url_alvo, headers=headers)
                
                # Usa o 'html.parser' que é nativo do Python e funciona em qualquer celular
                soup = BeautifulSoup(resposta.text, "html.parser")
                
                # Encontra a tabela de classificação pela estrutura do FBref
                tabela = soup.find("table", {"id": lambda x: x and "results" in x and "overall" in x})
                
                if not tabela:
                    # Segunda tentativa se o ID mudar
                    tabela = soup.find("table")
                
                if tabela:
                    # Captura os cabeçalhos das colunas
                    cabecalho = [th.text.strip() for th in tabela.find("thead").find_all("th")]
                    # O FBref costuma colocar uma coluna vazia ou rank no início, ajustamos os nomes
                    if cabecalho and cabecalho[0] == "":
                        cabecalho[0] = "Pos"
                        
                    # Limita às colunas principais para não quebrar o layout do celular
                    colunas_principais = ["Pos", "Equipe", "MP", "V", "E", "D", "GM", "GS", "GD", "PTS"]
                    
                    linhas_dados = []
                    # Varre as linhas da tabela
                    for linha in tabela.find("tbody").find_all("tr"):
                        # Ignora linhas de divisão intermediárias que o FBref usa
                        if "thead" in linha.get("class", []):
                            continue
                            
                        # Captura o texto de cada célula (th e td)
                        celulas = [linha.find("th")] + linha.find_all("td")
                        valores = [c.text.strip() for c in celulas if c is not None]
                        
                        if valores:
                            linhas_dados.append(valores)
                    
                    # Cria o DataFrame mapeando os dados extraídos
                    df_bruto = pd.DataFrame(linhas_dados)
                    
                    # Ajusta as colunas dinamicamente baseado no tamanho extraído
                    df_bruto.columns = cabecalho[:len(df_bruto.columns)]
                    
                    # Filtra apenas o básico para ficar bonito na tela do celular
                    colunas_finais = [col for col in colunas_principais if col in df_bruto.columns]
                    df_exibir = df_bruto[colunas_finais]
                    
                    st.success(f"📊 Dados de {liga_selecionada} carregados!")
                    st.dataframe(df_exibir, use_container_width=True, hide_index=True)
                else:
                    st.error("Não foi possível encontrar a tabela na página.")
                    
            except Exception as e:
                st.error(f"Erro na raspagem manual: {e}")
