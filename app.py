import streamlit as st
import pandas as pd
import time

# Configuração da página do Streamlit
st.set_page_config(page_title="Teste de Raspagem FBref", layout="centered")

st.title("⚽ Raspador Controlado - FBref")
st.markdown("Interface simples para testar a captura de dados respeitando o limite de requisições.")

# Dicionário mapeando os IDs e nomes das ligas direto do FBref
# IDs fixos do site para o ano corrente (2025-2026 / 2026)
LIGAS = {
    "Premier League (Inglaterra)": "https://fbref.com",
    "Brasileirão Série A": "https://fbref.com",
    "La Liga (Espanha)": "https://fbref.com",
    "Serie A (Itália)": "https://fbref.com"
}

# Interface: Seleção da liga
liga_selecionada = st.selectbox("Selecione a Liga para testar:", list(LIGAS.keys()))

# Inicializa um indicador de controle de tempo no Streamlit (Session State)
if "ultimo_acesso" not in st.session_state:
    st.session_state.ultimo_acesso = 0

if st.button("Executar Raspagem Real"):
    tempo_atual = time.time()
    tempo_decorrido = tempo_atual - st.session_state.ultimo_acesso
    
    # 🚨 CONTROLE DE SEGURANÇA: Garante um intervalo mínimo de 4 segundos entre cliques
    # (4 segundos por clique garante no máximo 15 requisições por minuto, abaixo do limite de 20)
    if tempo_decorrido < 4:
        tempo_restante = int(4 - tempo_decorrido)
        st.warning(f"⏳ Aguarde {tempo_restante} segundos antes de raspar novamente para evitar bloqueios!")
    else:
        # Atualiza o cronômetro do último acesso
        st.session_state.ultimo_acesso = tempo_atual
        
        url_alvo = LIGAS[liga_selecionada]
        
        with st.spinner("Conectando ao FBref e interpretando a tabela HTML..."):
            try:
                # O Pandas localiza a tabela que contém o texto "Classificação"
                tabelas = pd.read_html(url_alvo, match="Classificação")
                
                if tabelas:
                    df = tabelas[0]
                    
                    # Limpeza das colunas indesejadas que o site gera
                    colunas_remover = ["Notas", "Últimos 5"]
                    for col in colunas_remover:
                        if col in df.columns:
                            df = df.drop(columns=[col])
                    
                    st.success(f"📊 Dados de {liga_selecionada} capturados com sucesso!")
                    
                    # Exibe a tabela final limpa
                    st.dataframe(df, use_container_width=True, hide_index=True)
                else:
                    st.error("A tabela não pôde ser encontrada na estrutura da página.")
                    
            except Exception as e:
                st.error(f"Erro na raspagem: {e}")
                st.info("Se o site retornar erro 429, significa que o limite de requisições por IP foi excedido. Aguarde 1 minuto.")
pip install lxml
