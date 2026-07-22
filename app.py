import streamlit as st

# ==============================================================================
# CAMADA 1: INFRAESTRUTURA E CREDENCIAIS (SETUP)
# Este bloco lê as chaves em silêncio nos bastidores. Nada é exibido na tela.
# ==============================================================================

# O código lê o arquivo secrets.toml e guarda as senhas na memória do servidor
CHAVE_API_FOOTBALL = st.secrets["API_FOOTBALL_KEY"]
CHAVE_FOOTYSTATS   = st.secrets["FOOTYSTATS_KEY"]
CHAVE_THE_ODDS     = st.secrets["THE_ODDS_KEY"]

