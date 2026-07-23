import streamlit as st

# ==============================================================================
# CAMADA 1: INFRAESTRUTURA E CREDENCIAIS (SETUP)
# Este bloco lê as chaves em silêncio nos bastidores. Nada é exibido na tela.
# ==============================================================================
try:
    CHAVE_API_FOOTBALL = st.secrets["API_FOOTBALL_KEY"]
    CHAVE_FOOTYSTATS   = st.secrets["FOOTYSTATS_KEY"]
    CHAVE_THE_ODDS     = st.secrets["THE_ODDS_KEY"]
    st.success("✅ Chaves de API sincronizadas com sucesso!")
except Exception:
    st.warning("⚠️ Aguardando a sincronização das chaves do GitHub...")

