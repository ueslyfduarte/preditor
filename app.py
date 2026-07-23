import import streamlit as st

# ==============================================================================
# CAMADA 1: INFRAESTRUTURA E CREDENCIAIS (SETUP)
# ==============================================================================
CHAVE_API_FOOTBALL = st.secrets["API_FOOTBALL_KEY"]
CHAVE_FOOTYSTATS   = st.secrets["FOOTYSTATS_KEY"]
CHAVE_THE_ODDS     = st.secrets["THE_ODDS_KEY"]

# ==============================================================================
# CAMADA 2: VARIÁVEIS DE ENTRADA (INPUTS)
# ==============================================================================
time_A = "Time A"
time_B = "Time B"
time_A_eh_mandante = True  # True se Time A for Mandante, False se for Visitante

# ==============================================================================
# CAMADA 3: INTERFACE - PAINEL DO JOGO
# ==============================================================================
st.header(f"{time_A} x {time_B}")

st.subheader("Classificação Atual")
# Espaço para os dados de classificação atual

st.subheader("Classificação de Momento (Últimos 5 jogos)")
# Espaço para os dados dos últimos 5 jogos

st.subheader("Classificação Projetada Antes do Início do Campeonato")
# Espaço para os dados de projeção inicial

# ==============================================================================
# CAMADA 4: ÍNDICE MOMENTO (ESTATÍSTICAS E RECORTE DE FORMA)
# ==============================================================================
st.header("Índice Momento")

# Mocks de sequências (V = Vitória, E = Empate, D = Derrota)
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

ultimos_5_h2h_A = ["V", "E", "D", "V", "E"]  # Desempenho do Time A contra o B nos últimos 5 jogos
ultimos_5_h2h_B = ["D", "E", "V", "D", "E"]  # Desempenho do Time B contra o A nos últimos 5 jogos

# Função auxiliar para calcular pontos
def calcular_pontos(lista_resultados):
    mapeamento = {"V": 3, "E": 1, "D": 0}
    return sum(mapeamento.get(res, 0) for res in lista_resultados)

# Cálculos de pontos para as fórmulas do Time A
pts_10_g_A  = calcular_pontos(ultimos_10_gerais_A)
pts_5_g_A   = calcular_pontos(ultimos_5_gerais_A)
pts_3_g_A   = calcular_pontos(ultimos_3_gerais_A)
pts_5_m_A   = calcular_pontos(ultimos_5_mando_A)
pts_3_m_A   = calcular_pontos(ultimos_3_mando_A)
pts_5_h2h_A = calcular_pontos(ultimos_5_h2h_A)

# Cálculos das fórmulas de indicadores do Time A
ind_I_A   = (pts_10_g_A / 30) * 100 * 0.10
ind_II_A  = (pts_5_g_A / 15) * 100 * 0.15
ind_III_A = (pts_3_g_A / 9) * 100 * 0.20
ind_IV_A  = (pts_5_m_A / 15) * 100 * 0.25
ind_V_A   = (pts_3_m_A / 9) * 100 * 0.20
ind_VI_A  = (pts_5_h2h_A / 15) * 100 * 0.10

im_final_A = ind_I_A + ind_II_A + ind_III_A + ind_IV_A + ind_V_A + ind_VI_A

# Cálculos de pontos para as fórmulas do Time B
pts_10_g_B  = calcular_pontos(ultimos_10_gerais_B)
pts_5_g_B   = calcular_pontos(ultimos_5_gerais_B)
pts_3_g_B   = calcular_pontos(ultimos_3_gerais_B)
pts_5_m_B   = calcular_pontos(ultimos_5_mando_B)
pts_3_m_B   = calcular_pontos(ultimos_3_mando_B)
pts_5_h2h_B = calcular_pontos(ultimos_5_h2h_B)

# Cálculos das fórmulas de indicadores do Time B
ind_I_B   = (pts_10_g_B / 30) * 100 * 0.10
ind_II_B  = (pts_5_g_B / 15) * 100 * 0.15
ind_III_B = (pts_3_g_B / 9) * 100 * 0.20
ind_IV_B  = (pts_5_m_B / 15) * 100 * 0.25
ind_V_B   = (pts_3_m_B / 9) * 100 * 0.20
ind_VI_B  = (pts_5_h2h_B / 15) * 100 * 0.10

im_final_B = ind_I_B + ind_II_B + ind_III_B + ind_IV_B + ind_V_B + ind_VI_B

# Exibição dos dados do Time A
st.subheader(f"Estatísticas de Momento: {time_A}")
st.write(f"Últimos 10 jogos gerais: {'-'.join(ultimos_10_gerais_A)}")
st.write(f"Últimos 5 jogos gerais: {'-'.join(ultimos_5_gerais_A)}")
st.write(f"Últimos 3 jogos gerais: {'-'.join(ultimos_3_gerais_A)}")

if time_A_eh_mandante:
    st.write(f"Últimos 5 jogos como Mandante: {'-'.join(ultimos_5_mando_A)}")
    st.write(f"Últimos 3 jogos como Mandante: {'-'.join(ultimos_3_mando_A)}")
    st.write(f"Resultados detalhados (Últimos 5 como Mandante): {ultimos_5_mando_A}")
else:
    st.write(f"Últimos 5 jogos como Visitante: {'-'.join(ultimos_5_mando_A)}")
    st.write(f"Últimos 3 jogos como Visitante: {'-'.join(ultimos_3_mando_A)}")
    st.write(f"Resultados detalhados (Últimos 5 como Visitante): {ultimos_5_mando_A}")

st.write(f"Últimos 5 Confrontos Diretos (H2H): {'-'.join(ultimos_5_h2h_A)}")
st.write(f"**Pontuação IM Final ({time_A}): {im_final_A:.2f}**")

# Exibição dos dados do Time B
st.subheader(f"Estatísticas de Momento: {time_B}")
st.write(f"Últimos 10 jogos gerais: {'-'.join(ultimos_10_gerais_B)}")
st.write(f"Últimos 5 jogos gerais: {'-'.join(ultimos_5_gerais_B)}")
st.write(f"Últimos 3 jogos gerais: {'-'.join(ultimos_3_gerais_B)}")

if not time_A_eh_mandante:
    st.write(f"Últimos 5 jogos como Mandante: {'-'.join(ultimos_5_mando_B)}")
    st.write(f"Últimos 3 jogos como Mandante: {'-'.join(ultimos_3_mando_B)}")
    st.write(f"Resultados detalhados (Últimos 5 como Mandante): {ultimos_5_mando_B}")
else:
    st.write(f"Últimos 5 jogos como Visitante: {'-'.join(ultimos_5_mando_B)}")
    st.write(f"Últimos 3 jogos como Visitante: {'-'.join(ultimos_3_mando_B)}")
    st.write(f"Resultados detalhados (Últimos 5 como Visitante): {ultimos_5_mando_B}")

st.write(f"Últimos 5 Confrontos Diretos (H2H): {'-'.join(ultimos_5_h2h_B)}")
st.write(f"**Pontuação IM Final ({time_B}): {im_final_B:.2f}**")
# ==============================================================================
# CAMADA 5: ÍNDICE DE OVERALL (IO)
# Cálculos de desempenho ofensivo, defensivo, consistência e eficiência.
# ==============================================================================
st.header("Índice de Overall (IO)")

# Mocks de dados estatísticos do campeonato e das equipes
# Substituir pelos dados reais das APIs futuramente
media_gols_campeonato = 2.5
media_chutes_campeonato = 12.0

# Dados do Time A
media_gols_A = 1.8
media_chutes_A = 14.2
pct_jogos_marcando_A = 80.0  # Em porcentagem (ex: 80% = 80.0)

media_gols_sofridos_A = 1.0
media_chutes_sofridos_A = 10.5
pct_clean_sheets_A = 40.0  # Em porcentagem

aproveitamento_geral_ajustado_A = 65.0  # Em porcentagem
aproveitamento_mando_ajustado_A = 75.0  # Em porcentagem

# Dados do Time B
media_gols_B = 1.2
media_chutes_B = 11.0
pct_jogos_marcando_B = 65.0

media_gols_sofridos_B = 1.5
media_chutes_sofridos_B = 13.8
pct_clean_sheets_B = 20.0

aproveitamento_geral_ajustado_B = 40.0
aproveitamento_mando_ajustado_B = 45.0


# --- CÁLCULOS DO TIME A ---
# Passo A (Ataque)
passo_A_A = ((media_gols_A / media_gols_campeonato * 50) + (media_chutes_A / media_chutes_campeonato * 50) + pct_jogos_marcando_A) / 3 * 0.25

# Passo B (Defesa)
passo_B_A = ((media_gols_campeonato / media_gols_sofridos_A * 50) + (media_chutes_campeonato / media_chutes_sofridos_A * 50) + pct_clean_sheets_A) / 3 * 0.25

# Passo C (Consistência)
passo_C_A = (aproveitamento_geral_ajustado_A + aproveitamento_mando_ajustado_A) / 2 * 0.50

# Passo D (IEC)
calc_iec_A = (media_chutes_sofridos_A / media_gols_sofridos_A) / (media_chutes_A / media_gols_A)
passo_D_A = min(calc_iec_A * 5, 20.0)

# IO Final Time A
io_final_A = passo_A_A + passo_B_A + passo_C_A + passo_D_A


# --- CÁLCULOS DO TIME B ---
# Passo A (Ataque)
passo_A_B = ((media_gols_B / media_gols_campeonato * 50) + (media_chutes_B / media_chutes_campeonato * 50) + pct_jogos_marcando_B) / 3 * 0.25

# Passo B (Defesa)
passo_B_B = ((media_gols_campeonato / media_gols_sofridos_B * 50) + (media_chutes_campeonato / media_chutes_sofridos_B * 50) + pct_clean_sheets_B) / 3 * 0.25

# Passo C (Consistência)
passo_C_B = (aproveitamento_geral_ajustado_B + aproveitamento_mando_ajustado_B) / 2 * 0.50

# Passo D (IEC)
calc_iec_B = (media_chutes_sofridos_B / media_gols_sofridos_B) / (media_chutes_B / media_gols_B)
passo_D_B = min(calc_iec_B * 5, 20.0)

# IO Final Time B
io_final_B = passo_A_B + passo_B_B + passo_C_B + passo_D_B


# --- EXIBIÇÃO DA INTERFACE ---
st.subheader(f"Métricas IO: {time_A}")
st.write(f"Passo A (Ataque): {passo_A_A:.2f}")
st.write(f"Passo B (Defesa): {passo_B_A:.2f}")
st.write(f"Passo C (Consistência): {passo_C_A:.2f}")
st.write(f"Passo D (IEC): {passo_D_A:.2f}")
st.write(f"**Índice de Overall Final ({time_A}): {io_final_A:.2f}**")

st.subheader(f"Métricas IO: {time_B}")
st.write(f"Passo A (Ataque): {passo_A_B:.2f}")
st.write(f"Passo B (Defesa): {passo_B_B:.2f}")
st.write(f"Passo C (Consistência): {passo_C_B:.2f}")
st.write(f"Passo D (IEC): {passo_D_B:.2f}")
st.write(f"**Índice de Overall Final ({time_B}): {io_final_B:.2f}**")
# ==============================================================================
# CAMADA 6: ÍNDICE DE FATORES PSICOLÓGICOS (IFP)
# Cálculos de impacto, reação e cobrança por expectativa de tabela.
# ==============================================================================
st.header("Índice de Fatores Psicológicos (IFP)")

# Mocks de dados adicionais necessários para o IFP
# Substituir pelos dados reais do Painel do Jogo (Camada 3) e IO (Camada 5) futuramente
posicao_atual_A = 3
posicao_projetada_A = 2
gols_sofridos_ultimo_jogo_A = 4
mediana_gols_sofridos_A = 1.0

posicao_atual_B = 15
posicao_projetada_B = 10
gols_sofridos_ultimo_jogo_B = 4
mediana_gols_sofridos_B = 1.6

# Posição Máxima do Campeonato para normalização (Geralmente 20 times)
total_times_campeonato = 20


# --- CÁLCULOS DO TIME A ---
# Componente 1: Impacto e Reação (IIR)
fator_posicao_A = (total_times_campeonato + 1 - posicao_atual_A) / total_times_campeonato
ruptura_A = (gols_sofridos_ultimo_jogo_A / max(mediana_gols_sofridos_A, 0.1)) * fator_posicao_A

# A Balança: Se o IO (já calculado na Camada 5) for alto, vira Reação. Se for baixo, vira Abalo.
# Multiplicamos a ruptura pelo IO ponderado para gerar uma nota de 0 a 100
# Nota alta = Alta capacidade de reação / Nota baixa = Time abalado e frágil
comp_1_A = min((ruptura_A * (io_final_A / 100)) * 25, 100.0)

# Componente 3: Cobrança e Fracasso (ICF) - Escala de 0 a 100 de pressão
desvio_expectativa_A = posicao_atual_A - posicao_projetada_A
# Se o desvio for positivo (está pior que o projetado), gera pressão. Se negativo (está melhor), gera leveza.
if desvio_expectativa_A > 0:
    comp_3_A = min((desvio_expectativa_A / total_times_campeonato) * 100, 100.0)
else:
    comp_3_A = 0.0  # Sem pressão por expectativa de tabela

# IFP Final Time A (Média geométrica ou ponderada dos componentes existentes)
# Para manter isolado, calculamos a média simples dos dois componentes estruturados até aqui
ifp_final_A = (comp_1_A + comp_3_A) / 2


# --- CÁLCULOS DO TIME B ---
# Componente 1: Impacto e Reação (IIR)
fator_posicao_B = (total_times_campeonato + 1 - posicao_atual_B) / total_times_campeonato
ruptura_B = (gols_sofridos_ultimo_jogo_B / max(mediana_gols_sofridos_B, 0.1)) * fator_posicao_B

# A Balança para o Time B
comp_1_B = min((ruptura_B * (io_final_B / 100)) * 25, 100.0)

# Componente 3: Cobrança e Fracasso (ICF)
desvio_expectativa_B = posicao_atual_B - posicao_projetada_B
if desvio_expectativa_B > 0:
    comp_3_B = min((desvio_expectativa_B / total_times_campeonato) * 100, 100.0)
else:
    comp_3_B = 0.0

# IFP Final Time B
ifp_final_B = (comp_1_B + comp_3_B) / 2


# --- EXIBIÇÃO DA INTERFACE ---
st.subheader(f"Métricas Psicologia (IFP): {time_A}")
st.write(f"Fator Posição (Peso do Vexame): {fator_posicao_A:.2f}")
st.write(f"Capacidade de Reação (Comp 1): {comp_1_A:.2f} (Nota alta = Boa resposta / Baixa = Pane)")
st.write(f"Pressão por Expectativa (Comp 3): {comp_3_A:.2f} (Nota alta = Cobrança interna)")
st.write(f"**Índice de Fatores Psicológicos Final ({time_A}): {ifp_final_A:.2f}**")

st.subheader(f"Métricas Psicologia (IFP): {time_B}")
st.write(f"Fator Posição (Peso do Vexame): {fator_posicao_B:.2f}")
st.write(f"Capacidade de Reação (Comp 1): {comp_1_B:.2f} (Nota alta = Boa resposta / Baixa = Pane)")
st.write(f"Pressão por Expectativa (Comp 3): {comp_3_B:.2f} (Nota alta = Cobrança interna)")
st.write(f"**Índice de Fatores Psicológicos Final ({time_B}): {ifp_final_B:.2f}**")
# ==============================================================================
# CAMADA 7: PONTUAÇÃO CONSOLIDADA E PRECIFICAÇÃO FINAL
# Consolidação dos três índices (IM, IO, IFP) para gerar a nota final do confronto.
# ==============================================================================
st.header("Pontuação Consolidada Final")

# Definição de pesos para a consolidação (ajustáveis conforme sua estratégia)
peso_im = 0.40   # 40% de importância para o Momento Recente
peso_io = 0.40   # 40% de importância para a Consistência (Overall)
peso_ifp = 0.20  # 20% de importância para o Fator Psicológico

# Cálculo da Pontuação Consolidada para o Time A
pontuacao_final_A = (im_final_A * peso_im) + (io_final_A * peso_io) + (ifp_final_A * peso_ifp)

# Cálculo da Pontuação Consolidada para o Time B
pontuacao_final_B = (im_final_B * peso_im) + (io_final_B * peso_io) + (ifp_final_B * peso_ifp)

# --- EXIBIÇÃO DA INTERFACE ---
col_res_A, col_res_B = st.columns(2)

with col_res_A:
    st.subheader(f"Resultado Final: {time_A}")
    st.write(f"Índice de Momento (IM): {im_final_A:.2f}")
    st.write(f"Índice de Overall (IO): {io_final_A:.2f}")
    st.write(f"Fatores Psicológicos (IFP): {ifp_final_A:.2f}")
    st.write(f"**Nota Consolidada ({time_A}): {pontuacao_final_A:.2f}**")

with col_res_B:
    st.subheader(f"Resultado Final: {time_B}")
    st.write(f"Índice de Momento (IM): {im_final_B:.2f}")
    st.write(f"Índice de Overall (IO): {io_final_B:.2f}")
    st.write(f"Fatores Psicológicos (IFP): {ifp_final_B:.2f}")
    st.write(f"**Nota Consolidada ({time_B}): {pontuacao_final_B:.2f}**")
