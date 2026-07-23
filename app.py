import streamlit as st

# ==============================================================================
# CAMADA 1: INFRAESTRUTURA E CREDENCIAIS (SETUP)
# ==============================================================================
try:
    CHAVE_API_FOOTBALL = st.secrets["API_FOOTBALL_KEY"]
    CHAVE_FOOTYSTATS   = st.secrets["FOOTYSTATS_KEY"]
    CHAVE_THE_ODDS     = st.secrets["THE_ODDS_KEY"]
except Exception:
    CHAVE_API_FOOTBALL = "Chave Pendente"
    CHAVE_FOOTYSTATS   = "Chave Pendente"
    CHAVE_THE_ODDS     = "Chave Pendente"

# ==============================================================================
# CAMADA 2: VARIÁVEIS DE ENTRADA (INPUTS)
# ==============================================================================
time_A = "Flamengo"
time_B = "Palmeiras"
time_A_eh_mandante = True

posicao_atual_A = 3
posicao_projetada_A = 2
gols_sofridos_ultimo_jogo_A = 4
mediana_gols_sofridos_A = 1.0

posicao_atual_B = 5
posicao_projetada_B = 10
gols_sofridos_ultimo_jogo_B = 1
mediana_gols_sofridos_B = 1.2

total_times_campeonato = 20

# ==============================================================================
# CAMADA 2.5: FUNÇÕES AUXILIARES VISUAIS (DESIGN UTILS)
# ==============================================================================
def renderizar_badges_ved(lista_resultados):
    """Gera badges coloridas de forma limpa para exibição de sequências."""
    html_badges = []
    for r in lista_resultados:
        if r == "V":
            html_badges.append('<span style="background-color:#2ecc71; color:white; padding:3px 8px; border-radius:3px; margin-right:3px; font-weight:bold;">V</span>')
        elif r == "E":
            html_badges.append('<span style="background-color:#f1c40f; color:black; padding:3px 8px; border-radius:3px; margin-right:3px; font-weight:bold;">E</span>')
        else:
            html_badges.append('<span style="background-color:#e74c3c; color:white; padding:3px 8px; border-radius:3px; margin-right:3px; font-weight:bold;">D</span>')
    st.markdown(" ".join(html_badges), unsafe_allow_html=True)

# ==============================================================================
# CAMADA 3: INTERFACE - PAINEL DO JOGO
# ==============================================================================
st.title("📊 Preditor Esportivo Avançado")
st.markdown("---")

st.subheader(f"⚔️ Confronto: {time_A} (M) x {time_B} (V)")

col1, col2 = st.columns(2)
with col1:
    st.markdown(f"### 🏠 {time_A}")
    st.metric(label="Classificação Atual", value=f"{posicao_atual_A}º")
    st.metric(label="Projeção Pré-Campeonato", value=f"{posicao_projetada_A}º")

with col2:
    st.markdown(f"### 🚌 {time_B}")
    st.metric(label="Classificação Atual", value=f"{posicao_atual_B}º")
    st.metric(label="Projeção Pré-Campeonato", value=f"{posicao_projetada_B}º")

st.markdown("---")

# ==============================================================================
# CAMADA 4: ÍNDICE MOMENTO (ESTATÍSTICAS E RECORTE DE FORMA)
# ==============================================================================
# Mocks de sequências
ultimos_10_gerais_A = ["V", "E", "D", "V", "V", "E", "D", "V", "V", "E"]
ultimos_10_gerais_B = ["D", "V", "E", "D", "D", "V", "E", "D", "V", "D"]

ultimos_5_gerais_A = ultimos_10_gerais_A[:5]
ultimos_3_gerais_A = ultimos_10_gerais_A[:3]
ultimos_5_gerais_B = ultimos_10_gerais_B[:5]
ultimos_3_gerais_B = ultimos_10_gerais_B[:3]

ultimos_5_mando_A = ["V", "V", "E", "V", "D"] 
ultimos_3_mando_A = ultimos_5_mando_A[:3]
ultimos_5_mando_B = ["D", "E", "D", "V", "E"] 
ultimos_3_mando_B = ultimos_5_mando_B[:3]

ultimos_5_h2h_A = ["V", "E", "D", "V", "E"]
ultimos_5_h2h_B = ["D", "E", "V", "D", "E"]

def calcular_pontos(lista_resultados):
    mapeamento = {"V": 3, "E": 1, "D": 0}
    return sum(mapeamento.get(res, 0) for res in lista_resultados)

pts_10_g_A  = calcular_pontos(ultimos_10_gerais_A)
pts_5_g_A   = calcular_pontos(ultimos_5_gerais_A)
pts_3_g_A   = calcular_pontos(ultimos_3_gerais_A)
pts_5_m_A   = calcular_pontos(ultimos_5_mando_A)
pts_3_m_A   = calcular_pontos(ultimos_3_mando_A)
pts_5_h2h_A = calcular_pontos(ultimos_5_h2h_A)

ind_I_A   = (pts_10_g_A / 30) * 100 * 0.10
ind_II_A  = (pts_5_g_A / 15) * 100 * 0.15
ind_III_A = (pts_3_g_A / 9) * 100 * 0.20
ind_IV_A  = (pts_5_m_A / 15) * 100 * 0.25
ind_V_A   = (pts_3_m_A / 9) * 100 * 0.20
ind_VI_A  = (pts_5_h2h_A / 15) * 100 * 0.10
im_final_A = ind_I_A + ind_II_A + ind_III_A + ind_IV_A + ind_V_A + ind_VI_A

pts_10_g_B  = calcular_pontos(ultimos_10_gerais_B)
pts_5_g_B   = calcular_pontos(ultimos_5_gerais_B)
pts_3_g_B   = calcular_pontos(ultimos_3_gerais_B)
pts_5_m_B   = calcular_pontos(ultimos_5_mando_B)
pts_3_m_B   = calcular_pontos(ultimos_3_mando_B)
pts_5_h2h_B = calcular_pontos(ultimos_5_h2h_B)

ind_I_B   = (pts_10_g_B / 30) * 100 * 0.10
ind_II_B  = (pts_5_g_B / 15) * 100 * 0.15
ind_III_B = (pts_3_g_B / 9) * 100 * 0.20
ind_IV_B  = (pts_5_m_B / 15) * 100 * 0.25
ind_V_B   = (pts_3_m_B / 9) * 100 * 0.20
ind_VI_B  = (pts_5_h2h_B / 15) * 100 * 0.10
im_final_B = ind_I_B + ind_II_B + ind_III_B + ind_IV_B + ind_V_B + ind_VI_B

st.header("📈 Análise de Forma Recente")
col_im_A, col_im_B = st.columns(2)

with col_im_A:
    st.markdown(f"#### Forma do {time_A}")
    st.write("Últimos 10 Gerais:")
    renderizar_badges_ved(ultimos_10_gerais_A)
    st.write("Últimos 5 Gerais:")
    renderizar_badges_ved(ultimos_5_gerais_A)
    st.write("Últimos 5 no Mando Atual:")
    renderizar_badges_ved(ultimos_5_mando_A)
    st.metric(label="Índice de Momento (IM)", value=f"{im_final_A:.1f} pts")

with col_im_B:
    st.markdown(f"#### Forma do {time_B}")
    st.write("Últimos 10 Gerais:")
    renderizar_badges_ved(ultimos_10_gerais_B)
    st.write("Últimos 5 Gerais:")
    renderizar_badges_ved(ultimos_5_gerais_B)
    st.write("Últimos 5 no Mando Atual:")
    renderizar_badges_ved(ultimos_5_mando_B)
    st.metric(label="Índice de Momento (IM)", value=f"{im_final_B:.1f} pts")

st.markdown("---")

# ==============================================================================
# CAMADA 5: ÍNDICE DE OVERALL (IO)
# ==============================================================================
media_gols_campeonato = 2.5
media_chutes_campeonato = 12.0

media_gols_A = 1.8
media_chutes_A = 14.2
pct_jogos_marcando_A = 80.0
media_gols_sofridos_A = 1.0
media_chutes_sofridos_A = 10.5
pct_clean_sheets_A = 40.0
aproveitamento_geral_ajustado_A = 65.0
aproveitamento_mando_ajustado_A = 75.0

media_gols_B = 1.2
media_chutes_B = 11.0
pct_jogos_marcando_B = 65.0
media_gols_sofridos_B = 1.5
media_chutes_sofridos_B = 13.8
pct_clean_sheets_B = 20.0
aproveitamento_geral_ajustado_B = 40.0
aproveitamento_mando_ajustado_B = 45.0

passo_A_A = ((media_gols_A / media_gols_campeonato * 50) + (media_chutes_A / media_chutes_campeonato * 50) + pct_jogos_marcando_A) / 3 * 0.25
passo_B_A = ((media_gols_campeonato / media_gols_sofridos_A * 50) + (media_chutes_campeonato / media_chutes_sofridos_A * 50) + pct_clean_sheets_A) / 3 * 0.25
passo_C_A = (aproveitamento_geral_ajustado_A + aproveitamento_mando_ajustado_A) / 2 * 0.50
calc_iec_A = (media_chutes_sofridos_A / media_gols_sofridos_A) / (media_chutes_A / media_gols_A)
passo_D_A = min(calc_iec_A * 5, 20.0)
io_final_A = passo_A_A + passo_B_A + passo_C_A + passo_D_A

passo_A_B = ((media_gols_B / media_gols_campeonato * 50) + (media_chutes_B / media_chutes_campeonato * 50) + pct_jogos_marcando_B) / 3 * 0.25
passo_B_B = ((media_gols_campeonato / media_gols_sofridos_B * 50) + (media_chutes_campeonato / media_chutes_sofridos_B * 50) + pct_clean_sheets_B) / 3 * 0.25
passo_C_B = (aproveitamento_geral_ajustado_B + aproveitamento_mando_ajustado_B) / 2 * 0.50
calc_iec_B = (media_chutes_sofridos_B / media_gols_sofridos_B) / (media_chutes_B / media_gols_B)
passo_D_B = min(calc_iec_B * 5, 20.0)
io_final_B = passo_A_B + passo_B_B + passo_C_B + passo_D_B

st.header("📊 Força Consistente (Índice Overall)")
col_io_A, col_io_B = st.columns(2)

with col_io_A:
    st.metric(label=f"Índice Overall ({time_A})", value=f"{io_final_A:.1f} pts")

with col_io_B:
    st.metric(label=f"Índice Overall ({time_B})", value=f"{io_final_B:.1f} pts")

st.markdown("---")

# ==============================================================================
# CAMADA 6: ÍNDICE DE FATORES PSICOLÓGICOS (IFP)
# ==============================================================================
fator_posicao_A = (total_times_campeonato + 1 - posicao_atual_A) / total_times_campeonato
ruptura_A = (gols_sofridos_ultimo_jogo_A / max(mediana_gols_sofridos_A, 0.1)) * fator_posicao_A
comp_1_A = min((ruptura_A * (io_final_A / 100)) * 25, 100.0)
desvio_expectativa_A = posicao_atual_A - posicao_projetada_A
comp_3_A = min((desvio_expectativa_A / total_times_campeonato) * 100, 100.0) if desvio_expectativa_A > 0 else 0.0
ifp_final_A = (comp_1_A + comp_3_A) / 2

fator_posicao_B = (total_times_campeonato + 1 - posicao_atual_B) / total_times_campeonato
ruptura_B = (gols_sofridos_ultimo_jogo_B / max(mediana_gols_sofridos_B, 0.1)) * fator_posicao_B
comp_1_B = min((ruptura_B * (io_final_B / 100)) * 25, 100.0)
desvio_expectativa_B = posicao_atual_B - posicao_projetada_B
comp_3_B = min((desvio_expectativa_B / total_times_campeonato) * 100, 100.0) if desvio_expectativa_B > 0 else 0.0
ifp_final_B = (comp_1_B + comp_3_B) / 2

st.header("🧠 Índice de Fatores Psicológicos (IFP)")
col_ifp_A, col_ifp_B = st.columns(2)

with col_ifp_A:
    st.metric(label=f"Fator Psicológico ({time_A})", value=f"{ifp_final_A:.1f} / 100")

with col_ifp_B:
    st.metric(label=f"Fator Psicológico ({time_B})", value=f"{ifp_final_B:.1f} / 100")

st.markdown("---")

# ==============================================================================
# CAMADA 7: PONTUAÇÃO CONSOLIDADA E PRECIFICAÇÃO FINAL
# ==============================================================================
st.header("🏆 Pontuação Consolidada Final")

peso_im = 0.40
peso_io = 0.40
peso_ifp = 0.20
pontuacao_final_A = (im_final_A * peso_im) + (io_final_A * peso_io) + (ifp_final_A * peso_ifp)pontuacao_final_B = (im_final_B * peso_im) + (io_final_B * peso_io) + (ifp_final_B * peso_ifp)col_res_A, col_res_B = st.columns(2)with col_res_A:st.subheader(f"{time_A}")st.metric(label="Nota Final Ponderada", value=f"{pontuacao_final_A:.1f}")with col_res_B:st.subheader(f"{time_B}")st.metric(label="Nota Final Ponderada", value=f"{pontuacao_final_B:.1f}")
