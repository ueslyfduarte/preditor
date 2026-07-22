import streamlit as st
import pandas as pd
import yfinance as yf

st.set_page_config(page_title="Estatísticas de Futebol", layout="centered")
st.title("⚽ Estatísticas de Ligas - API de Teste")
st.markdown("Interface estável rodando via nuvem e otimizada para o celular.")

# Dicionários de Tickers de futebol disponíveis no Yahoo (ex: ^FTSE, etc para ligas ou dados de clubes públicos)
# Para fins de um teste de interface rápido e funcional no Streamlit, usaremos dados estruturados agregados
LIGAS = {
    "Manchester United (MUTD)": "MANU",
    "Juventus FC (JUVE)": "JUVE.MI",
    "Borussia Dortmund (BVB)": "BVB.DE",
    "Ajax Amsterdam (AJAX)": "AJAX.AS"
}

time_selecionado = st.selectbox("Escolha um clube para testar a captura de dados de mercado/desempenho:", list(LIGAS.keys()))

if st.button("Carregar Dados Históricos"):
    with st.spinner("Conectando ao provedor de dados abertos..."):
        try:
            ticker_simbolo = LIGAS[time_selecionado]
            clube = yf.Ticker(ticker_simbolo)
            
            # Captura dados históricos de desempenho institucional do clube
            df_historico = clube.history(period="1mo")
            
            if not df_historico.empty:
                st.success(f"📊 Dados de {time_selecionado} carregados com sucesso!")
                
                # Resumo das últimas métricas
                valores_recentes = df_historico.iloc[-1]
                
                col1, col2 = st.columns(2)
                col1.metric("Última Métrica Comercial", f"{valores_recentes['Close']:.2f}")
                col2.metric("Volume de Movimentação", f"{int(valores_recentes['Volume']):,}")
                
                st.markdown("### 📈 Tabela de Dados Recentes (Último Mês)")
                # Reseta o index para mostrar a data como coluna comum na tela do celular
                df_exibir = df_historico.reset_index()
                st.dataframe(df_exibir, use_container_width=True, hide_index=True)
            else:
                st.error("Nenhum dado disponível para este clube no momento.")
                
        except Exception as e:
            st.error(f"Erro ao conectar com a API: {e}")
