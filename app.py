import streamlit as st
import pandas as pd
import numpy as np
from typing import Dict, Any, List

# =====================================================================
# DIVISÓRIA 1: CONFIGURAÇÃO DO DESIGN VISUAL DO APP (DARK MODE)
# =====================================================================

st.set_page_config(
    page_title="Método V2.8 - Painel de Previsões",
    page_icon="⚽",
    layout="wide"
)

st.markdown("""
    <style>
    .stApp { background-color: #0b0e14; color: #ffffff; }
    div[data-testid="stMetricValue"] { font-size: 24px; font-weight: bold; color: #00ffcc; }
    div[data-testid="stMetricLabel"] { font-size: 13px; color: #a3a8b4; }
    </style>
""", unsafe_allow_html=True)


# =====================================================================
# DIVISÓRIA 2: MOTOR ESTATÍSTICO PARTE A (PAINEL INICIAL)
# =====================================================================

class PainelInicialV28:
    """
    Módulo 1 do Método de Análise Esportiva V2.8.
    Gerencia o posicionamento, ancoragem pré-campeonato e classificação momentânea.
    """
    def __init__(self, rodada_atual: int, total_times: int = 20):
        self.rodada_atual = rodada_atual
        self.total_times = total_times

    def calcular_pontos_retro(self, resultado: str, mando: str, nivel_time: int, nivel_adversario: int) -> float:
        if resultado == 'V': return 3.0
        if resultado == 'D': return 0.0
        
        if mando == 'visitante':
            if nivel_time < nivel_adversario: return 2.0 
            return 3.0 
        else: 
            if nivel_time <= nivel_adversario: return 2.0 
            elif nivel_time == 1 and nivel_adversario == 4: return 0.0 
            else: return 1.0 

    def definir_nivel_posicao(self, posicao: int) -> int:
        if 1 <= posicao <= 5:   return 1  
        if 6 <= posicao <= 10:  return 2  
        if 11 <= posicao <= 15: return 3  
        return 4                          

        def calcular_nivel_dinamico(self, ranking_pre, posicao_atual):
        if self.rodada_atual <= 10:
            posicao_ponderada = (ranking_pre * 0.70) + (posicao_atual * 0.30)
        elif 11 <= self.rodada_atual <= 25:
            posicao_ponderada = (ranking_pre * 0.30) + (posicao_atual * 0.70)
        else:
            posicao_ponderada = posicao_atual
        return self.definir_nivel_posicao(int(np.round(posicao_ponderada)))


            # =====================================================================
# DIVISÓRIA 2: MOTOR ESTATÍSTICO PARTE B (MÁQUINA DE OVERALL - PARTE 1)
# =====================================================================

class MaquinaOverallV28:
    """
    Módulo 2 do Método de Análise Esportiva V2.8.
    Calcula os blocos de força técnica aplicando o FMP rodada a rodada.
    """
    def __init__(self):
        self.base_score = 50.0

    def obter_multiplicadores_fmp(self, nivel_time: int, nivel_adversario_historico: int) -> Dict[str, float]:
        if nivel_time < nivel_adversario_historico:   
            return {"erro_defensivo": 1.40, "acerto_ofensivo": 0.60}
        elif nivel_time > nivel_adversario_historico: 
            return {"erro_defensivo": 0.70, "acerto_ofensivo": 1.30}
        else:                                         
            return {"erro_defensivo": 1.00, "acerto_ofensivo": 1.00}

    def modular_historico_ofensivo(self, jogos_time: List[Dict[str, float]], nivel_time: int) -> List[Dict[str, float]]:
        jogos_modulados = []
        for jogo in jogos_time:
            fmp = self.obter_multiplicadores_fmp(nivel_time, jogo['nivel_adversario_dia'])
            jogos_modulados.append({
                "ataques": jogo['ataques'] * fmp['acerto_ofensivo'],
                "ataques_perigosos": jogo['ataques_perigosos'] * fmp['acerto_ofensivo'],
                "chutes": jogo['chutes'] * fmp['acerto_ofensivo'],
                "chutes_gol": jogo['chutes_gol'] * fmp['acerto_ofensivo'],
                "gols": jogo['gols'] * fmp['acerto_ofensivo'],
                "xg": jogo['xg'] * fmp['acerto_ofensivo']
            })
        return jogos_modulados

    def modular_historico_defensivo(self, jogos_time: List[Dict[str, float]], nivel_time: int) -> List[Dict[str, float]]:
        jogos_modulados = []
        for jogo in jogos_time:
            fmp = self.obter_multiplicadores_fmp(nivel_time, jogo['nivel_adversario_dia'])
            jogos_modulados.append({
                "ataques_sofridos": jogo['ataques_sofridos'] * fmp['erro_defensivo'],
                "ataques_perigosos_sofridos": jogo['ataques_perigosos_sofridos'] * fmp['erro_defensivo'],
                "chutes_sofridos": jogo['chutes_sofridos'] * fmp['erro_defensivo'],
                "chutes_gol_sofridos": jogo['chutes_gol_sofridos'] * fmp['erro_defensivo'],
                "gols_sofridos": jogo['gols_sofridos'] * fmp['erro_defensivo'],
                "xg_cedido": jogo['xg_cedido'] * fmp['erro_defensivo']
            })
        return jogos_modulados
            def calcular_bloco_ataque(self, jogos_modulados: List[Dict[str, float]], liga: Dict[str, float]) -> Dict[str, float]:
        if not jogos_modulados: return {"FVO": self.base_score, "FCO": self.base_score, "Nota_Ataque": self.base_score}
        keys = ["ataques", "ataques_perigosos", "chutes", "chutes_gol", "gols", "xg"]
        med_time = {k: np.mean([j[k] for j in jogos_modulados]) for k in keys}
        proporcoes_fvo = [med_time[k] / max(0.0001, liga[k]) for k in keys]
        fvo = np.mean(proporcoes_fvo) * self.base_score
        chutes_por_gol_liga = liga['chutes_gol'] / max(0.0001, liga['gols'])
        chutes_por_gol_time = med_time['chutes_gol'] / max(0.0001, med_time['gols'])
        fco = (chutes_por_gol_liga / max(0.0001, chutes_por_gol_time)) * self.base_score
        return {"FVO": round(fvo, 2), "FCO": round(fco, 2), "Nota_Ataque": round(min(100.0, max(0.0, (fvo * 0.60) + (fco * 0.40))), 2)}

    def calcular_bloco_defesa(self, jogos_modulados: List[Dict[str, float]], liga: Dict[str, float]) -> Dict[str, float]:
        if not jogos_modulados: return {"FRD": self.base_score, "FCD": self.base_score, "Nota_Defesa": self.base_score}
        keys = ["ataques_sofridos", "ataques_perigosos_sofridos", "chutes_sofridos", "chutes_gol_sofridos", "gols_sofridos", "xg_cedido"]
        med_time = {k: np.mean([j[k] for j in jogos_modulados]) for k in keys}
        proporcoes_frd = [liga[k] / max(0.0001, med_time[k]) for k in keys]
        frd = np.mean(proporcoes_frd) * self.base_score
        chutes_sofridos_por_gol_time = med_time['chutes_gol_sofridos'] / max(0.0001, med_time['gols_sofridos'])
        chutes_sofridos_por_gol_liga = liga['chutes_gol_sofridos'] / max(0.0001, liga['gols_sofridos'])
        fcd = (chutes_sofridos_por_gol_time / max(0.0001, chutes_sofridos_por_gol_liga)) * self.base_score
        return {"FRD": round(frd, 2), "FCD": round(fcd, 2), "Nota_Defesa": round(min(100.0, max(0.0, (frd * 0.60) + (fcd * 0.40))), 2)}

    def calcular_bloco_consistencia(self, jogos_atq_mod: List[Dict[str, float]], jogos_def_mod: List[Dict[str, float]], im_max: float, im_min: float, liga: Dict[str, float]) -> Dict[str, float]:
        proporcoes_rodada = []
        for i in range(len(jogos_atq_mod)):
            ja, jd = jogos_atq_mod[i], jogos_def_mod[i]
            proporcoes_rodada.append(np.std([
                ja['ataques'] / max(0.0001, liga['ataques']),
                ja['chutes_gol'] / max(0.0001, liga['chutes_gol']),
                ja['gols'] / max(0.0001, liga['gols']),
                liga['gols_sofridos'] / max(0.0001, jd['gols_sofridos']),
                liga['xg_cedido'] / max(0.0001, jd['xg_cedido'])
            ]))
        fdm_std = np.mean(proporcoes_rodada) if proporcoes_rodada else 0.0
        fdm = max(0.0, min(100.0, 100.0 - (fdm_std * 100.0)))
        ier = max(0.0, min(100.0, 100.0 - (im_max - im_min)))
        return {"FDM": round(fdm, 2), "IER": round(ier, 2), "Nota_Consistencia": round((fdm * 0.60) + (ier * 0.40), 2)}

    def calcular_bloco_resistencia(self, time_pressao: Dict[str, float], liga_pressao: Dict[str, float], jogo_atual_time: Dict[str, Any]) -> Dict[str, float]:
        historico_def = jogo_atual_time.get('historico_defensivo_jogos', [])
        primeiro_jogo = historico_def[0] if isinstance(historico_def, list) and len(historico_def) > 0 else {}
        
        xg_cedido_time = primeiro_jogo.get('xg_cedido', 1.0)
        chutes_sofridos_time = primeiro_jogo.get('chutes_sofridos', 10.0)
        chutes_gol_sofridos_time = primeiro_jogo.get('chutes_gol_sofridos', 4.0)

        fcd_vol = (liga_pressao['xg_cedido'] / max(0.0001, xg_cedido_time)) * (liga_pressao['chutes_sofridos'] / max(0.0001, chutes_sofridos_time))
        fcd_nota = min(100.0, fcd_vol * self.base_score)

        time_chutes_por_gol = chutes_gol_sofridos_time / max(0.0001, time_pressao.get('gols_sofridos_fim', 1.0))
        liga_chutes_por_gol = liga_pressao['chutes_gol_sofridos'] / max(0.0001, liga_pressao['gols_sofridos'])
        egz_nota = min(100.0, (time_chutes_por_gol / max(0.0001, liga_chutes_por_gol)) * self.base_score)

        fri_nota = min(100.0, (time_pressao['pontos_recuperados'] / max(0.0001, time_pressao['pontos_disputados_atras'])) * 100.0)
        fzc_nota = min(100.0, max(0.0, 50.0 + ((time_pressao['gols_marcados_fim'] - time_pressao['gols_sofridos_fim']) * 10.0)))
        return {"Nota_Resistencia": round((fzc_nota * 0.30) + (egz_nota * 0.30) + (fri_nota * 0.20) + (fcd_nota * 0.20), 2)}
# =====================================================================
# DIVISÓRIA 2: MOTOR ESTATÍSTICO PARTE C (ÍNDICE DE MOMENTO)
# =====================================================================

class IndiceMomentoV28:
    def __init__(self, fac: float):
        self.fac = fac
        self.base_score = 50.0

    def converter_historico_nota(self, historico: List[str], mando: str, nivel_time: int, nivel_adversario: int) -> float:
        if not historico: return self.base_score
        pontos_acumulados = 0.0
        for r in historico:
            if r == 'V': pontos_acumulados += 3.0
            elif r == 'D': pontos_acumulados += 0.0
            elif r == 'E':
                if mando == 'visitante': pontos_acumulados += 2.0 if nivel_time < nivel_adversario else 3.0
                else: pontos_acumulados += 2.0 if nivel_time <= nivel_adversario else 0.0 if (nivel_time==1 and nivel_adversario==4) else 1.0
        return (pontos_acumulados / (len(historico) * 3.0)) * 100.0

    def calcular_bloco_tabela_dinamica(self, time: Dict[str, Any], nivel_adversario: int) -> float:
        multiplicador = 1.6 if nivel_adversario == 1 else 1.0 if nivel_adversario in [2, 3] else 0.0
        oscilacao_momentanea = (time['posicao_real'] - time['posicao_momentanea']) * multiplicador
        oscilacao_estrutural = (time['posicao_pre_campeonato'] - time['posicao_real']) * multiplicador
        return max(0.0, min(100.0, self.base_score + oscilacao_momentanea + oscilacao_estrutural))

    def calcular_im_final(self, dados_time: Dict[str, Any], adversario_nivel: int, mandante: bool) -> float:
        def obter_nivel(p): return 1 if p<=5 else 2 if p<=10 else 3 if p<=15 else 4
        nv_time = obter_nivel(dados_time['posicao_real'])
        mando_str = 'mandante' if mandante else 'visitante'
        bloco_campo = (self.converter_historico_nota(dados_time['historico_mando_3'], mando_str, nv_time, adversario_nivel) * 0.65) + (self.converter_historico_nota(dados_time['historico_mando_5'], mando_str, nv_time, adversario_nivel) * 0.35)
        bloco_geral = (self.converter_historico_nota(dados_time['historico_geral_3'], 'geral', nv_time, adversario_nivel) * 0.50) + (self.converter_historico_nota(dados_time['historico_geral_5'], 'geral', nv_time, adversario_nivel) * 0.35) + (self.converter_historico_nota(dados_time['historico_geral_10'], 'geral', nv_time, adversario_nivel) * 0.15)
        bloco_tabela = self.calcular_bloco_tabela_dinamica(dados_time, adversario_nivel)
        bonus_zebra = 15.0 * self.fac if (dados_time.get('venceu_ultimo_jogo_contra_elite', False) and obter_nivel(dados_time['posicao_pre_campeonato']) == 4) else 0.0
        return round(max(0.0, min(100.0, (bloco_campo * 0.45) + (bloco_geral * 0.35) + (bloco_tabela * 0.20) + bonus_zebra)), 2)
# =====================================================================
# DIVISÓRIA 3: MASSA DE DADOS DE ENTRADA SIMULADA (PADRÃO CONTRATO V2.8)
# =====================================================================

dados_partida_completa = {
    "contexto_confronto": {
        "tipo_de_confronto": "Campeonato Interligas",
        "rodada_atual": 14,
        "fac_rodada": 0.60
    },
    "odds_mercado_porcentagens": {
        "1X2": {"casa_pct": 50.0, "empate_pct": 25.0, "fora_pct": 25.0},
        "ambas_marcam_sim_pct": 58.0,
        "ambas_marcam_nao_pct": 42.0,
        "over_05_ht_pct": 65.0,
        "under_05_ht_pct": 35.0,
        "over_15_ht_pct": 30.0,
        "under_15_ht_pct": 70.0,
        "over_15_ft_pct": 75.0,
        "under_15_ft_pct": 25.0,
        "over_25_ft_pct": 52.0,
        "under_25_ft_pct": 48.0,
        "linha_escanteios_mercado": {"linha": 9.5, "over_pct": 55.0, "under_pct": 45.0}
    },
    "medias_liga_mandante_brutas": {
        "ataques": 100.0, "ataques_perigosos": 60.0, "chutes": 12.0, "chutes_gol": 4.5, "gols": 1.4, "xg": 1.5,
        "ataques_sofridos": 95.0, "ataques_perigosos_sofridos": 55.0, "chutes_sofridos": 11.0, "chutes_gol_sofridos": 4.0, "gols_sofridos": 1.2, "xg_cedido": 1.3
    },
    "medias_liga_visitante_brutas": {
        "ataques": 105.0, "ataques_perigosos": 65.0, "chutes": 13.0, "chutes_gol": 5.0, "gols": 1.5, "xg": 1.6,
        "ataques_sofridos": 100.0, "ataques_perigosos_sofridos": 58.0, "chutes_sofridos": 12.0, "chutes_gol_sofridos": 4.2, "gols_sofridos": 1.3, "xg_cedido": 1.4
    },
    "mandante": {
        "nome": "Time Mandante A", "liga_origem": "Liga Nacional 1",
        "posicao_real": 3, "posicao_momentanea": 1, "posicao_pre_campeonato": 2,
        "historico_ofensivo_jogos": [
            {"nivel_adversario_dia": 4, "ataques": 110, "ataques_perigosos": 70, "chutes": 15, "chutes_gol": 6, "gols": 3, "xg": 2.1},
            {"nivel_adversario_dia": 1, "ataques": 95, "ataques_perigosos": 50, "chutes": 10, "chutes_gol": 3, "gols": 1, "xg": 1.1}
        ],
        "historico_defensivo_jogos": [
            {"nivel_adversario_dia": 4, "ataques_sofridos": 80, "ataques_perigosos_sofridos": 40, "chutes_sofridos": 8, "chutes_gol_sofridos": 2, "gols_sofridos": 0, "xg_cedido": 0.6},
            {"nivel_adversario_dia": 1, "ataques_sofridos": 110, "ataques_perigosos_sofridos": 70, "chutes_sofridos": 14, "chutes_gol_sofridos": 6, "gols_sofridos": 2, "xg_cedido": 1.8}
        ],
        "dados_resistencia": {"pontos_recuperados": 40.0, "pontos_disputados_atras": 15.0, "gols_marcados_fim": 4, "gols_sofridos_fim": 1},
        "historico_mando_3": ['V', 'E', 'V'], "historico_mando_5": ['V', 'E', 'V', 'D', 'V'], "historico_5j_caracteres": ['V', 'V', 'E', 'D', 'V'],
        "historico_geral_3": ['V', 'V', 'E'], "historico_geral_5": ['V', 'V', 'E', 'D', 'V'], "historico_geral_10": ['V', 'V', 'E', 'D', 'V', 'E', 'V', 'D', 'V', 'V'],
        "venceu_ultimo_jogo_contra_elite": True,
        "urgencia_real": {"nota_posicao_atual": 85.0, "fpt_ajuste": 0},
        "orgulho_ferido": {"veio_de_goleada_humilhante": False, "veio_de_derrota_prateleira_inferior": False},
        "revanche": {"rival_goleou_ou_eliminou_recentemente": True},
        "observacoes_texto": "O time contratou um novo atacante titular que estreia hoje."
    },
    "visitante": {
        "nome": "Time Visitante B", "liga_origem": "Liga Nacional 2",
        "posicao_real": 16, "posicao_momentanea": 18, "posicao_pre_campeonato": 10,
        "historico_ofensivo_jogos": [
            {"nivel_adversario_dia": 2, "ataques": 85, "ataques_perigosos": 45, "chutes": 9, "chutes_gol": 2, "gols": 0, "xg": 0.7}
        ],
        "historico_defensivo_jogos": [
            {"nivel_adversario_dia": 2, "ataques_sofridos": 120, "ataques_perigosos_sofridos": 80, "chutes_sofridos": 16, "chutes_gol_sofridos": 7, "gols_sofridos": 3, "xg_cedido": 2.2}
        ],
        "dados_resistencia": {"pontos_recuperados": 10.0, "pontos_disputados_atras": 18.0, "gols_marcados_fim": 1, "gols_sofridos_fim": 5},
        "historico_mando_3": ['D', 'E', 'D'], "historico_mando_5": ['D', 'E', 'D', 'V', 'D'], "historico_5j_caracteres": ['D', 'D', 'E', 'D', 'V'],
        "historico_geral_3": ['D', 'D', 'E'], "historico_geral_5": ['D', 'D', 'E', 'D', 'V'], "historico_geral_10": ['D', 'D', 'E', 'D', 'V', 'E', 'D', 'D', 'V', 'D'],
        "venceu_ultimo_jogo_contra_elite": False,
        "urgencia_real": {"nota_posicao_atual": 90.0, "fpt_ajuste": 0},
        "orgulho_ferido": {"veio_de_goleada_humilhante": True, "veio_de_derrota_prateleira_inferior": True},
        "revanche": {"rival_goleou_ou_eliminou_recentemente": False},
        "observacoes_texto": "Três defensores titulares estão suspensos e desfalcam a equipe."
    }
}

# =====================================================================
# ADIÇÃO CRÍTICA: TRATAMENTO E INICIALIZAÇÃO DE VARIÁVEIS CONTEXTUAIS
# =====================================================================
ctx = dados_partida_completa["contexto_confronto"]
odds = dados_partida_completa["odds_mercado_porcentagens"]
mnd = dados_partida_completa["mandante"]
vis = dados_partida_completa["visitante"]

# Inicialização do Módulo 1 para descobrir os níveis reais dinâmicos
inicializador_p1 = PainelInicialV28(rodada_atual=ctx["rodada_atual"])
nv_real_m = inicializador_p1.calcular_nivel_dinamico(mnd["posicao_pre_campeonato"], mnd["posicao_real"])
nv_real_v = inicializador_p1.calcular_nivel_dinamico(vis["posicao_pre_campeonato"], vis["posicao_real"])
# ---------------------------------------------------------------------
# ETAPA 6: LEITURA AUTÔNOMA DE OBSERVAÇÕES E DESFALQUES
# ---------------------------------------------------------------------
st.header("📝 Etapa 6: Análise de Observações de Texto Extraídas")

col_obs1, col_obs2 = st.columns(2)
with col_obs1:
    st.markdown(f"**Bastidores ({mnd['nome']}):**")
    st.info(mnd["observacoes_texto"] if mnd["observacoes_texto"] else "Nenhuma observação descrita para este clube.")
with col_obs2:
    st.markdown(f"**Bastidores ({vis['nome']}):**")
    st.warning(vis["observacoes_texto"] if vis["observacoes_texto"] else "Nenhuma observação descrita para este clube.")


st.markdown("**📝 Resenha Estatística - Posicionamento:**")
if mnd["posicao_real"] < mnd["posicao_pre_campeonato"]:
    st.write(f"• O *{mnd['nome']}* está superando as expectativas iniciais do campeonato. Sua posição real está acima da prateleira projetada.")
else:
    st.write(f"• O *{mnd['nome']}* está entregando um desempenho dentro ou ligeiramente abaixo de sua prateleira estrutural histórica.")

if vis["posicao_real"] > 15:
    st.write(f"• Alerta crítico para o *{vis['nome']}*: O posicionamento real atual afunda a equipe na zona de perigo técnico de rebaixamento.")

st.write("---")

# ---------------------------------------------------------------------
# ETAPA 2: MÁQUINA DE OVERALL & FILTRO FMP RODADA A RODADA
# ---------------------------------------------------------------------
st.header("🛠️ Etapa 2: Resultados da Máquina de Overall")

motor_p2 = MaquinaOverallV28()

jogos_atq_m_mod = motor_p2.modular_historico_ofensivo(mnd["historico_ofensivo_jogos"], nv_real_m)
jogos_def_m_mod = motor_p2.modular_historico_defensivo(mnd["historico_defensivo_jogos"], nv_real_m)

jogos_atq_v_mod = motor_p2.modular_historico_ofensivo(vis["historico_ofensivo_jogos"], nv_real_v)
jogos_def_v_mod = motor_p2.modular_historico_defensivo(vis["historico_defensivo_jogos"], nv_real_v)

res_atq_m = motor_p2.calcular_bloco_ataque(jogos_atq_m_mod, dados_partida_completa["medias_liga_mandante_brutas"])
res_def_m = motor_p2.calcular_bloco_defesa(jogos_def_m_mod, dados_partida_completa["medias_liga_mandante_brutas"])
res_con_m = motor_p2.calcular_bloco_consistencia(jogos_atq_m_mod, jogos_def_m_mod, 85, 60, dados_partida_completa["medias_liga_mandante_brutas"])
res_res_m = motor_p2.calcular_bloco_resistencia(mnd["dados_resistencia"], dados_partida_completa["medias_liga_mandante_brutas"], mnd)

res_atq_v = motor_p2.calcular_bloco_ataque(jogos_atq_v_mod, dados_partida_completa["medias_liga_visitante_brutas"])
res_def_v = motor_p2.calcular_bloco_defesa(jogos_def_v_mod, dados_partida_completa["medias_liga_visitante_brutas"])
res_con_v = motor_p2.calcular_bloco_consistencia(jogos_atq_v_mod, jogos_def_v_mod, 70, 50, dados_partida_completa["medias_liga_visitante_brutas"])
res_res_v = motor_p2.calcular_bloco_resistencia(vis["dados_resistencia"], dados_partida_completa["medias_liga_visitante_brutas"], vis)

tabela_p2 = {
    "Blocos Técnicos do Overall": [mnd["nome"], vis["nome"]],
    "Nota Ataque (25%)": [res_atq_m["Nota_Ataque"], res_atq_v["Nota_Ataque"]],
    "Nota Defesa (25%)": [res_def_m["Nota_Defesa"], res_def_v["Nota_Defesa"]],
    "Nota Consistência (35%)": [res_con_m["Nota_Consistencia"], res_con_v["Nota_Consistencia"]],
    "Nota Resistência à Pressão (15%)": [res_res_m["Nota_Resistencia"], res_res_v["Nota_Resistencia"]]
}
df_p2 = pd.DataFrame(tabela_p2).set_index("Blocos Técnicos do Overall")
st.dataframe(df_p2)

st.markdown("**📝 Resenha Estatística - Força Estrutural:**")
st.write(f"• **Análise Ofensiva:** O power de fogo do mandante ({res_atq_m['Nota_Ataque']} pts) enfrenta uma linha defensiva vulnerável do visitante ({res_def_v['Nota_Defesa']} pts), criando um cenário técnico propício para gols do mandante.")
st.write(f"• **Análise de Inconstância:** A consistência tática do visitante está severamente comprometida de rodada em rodada, registrando apenas `{res_con_v['Nota_Consistencia']}` pontos.")

st.write("---")
# ---------------------------------------------------------------------
# ETAPA 3: ÍNDICE DE MOMENTO (IM) & RESPOSTA COMPETITIVA (IRC)
# ---------------------------------------------------------------------
st.header("📈 Etapa 3: Resultados de Momento (IM) e Fator Psicológico (IRC)")

motor_p3 = IndiceMomentoV28(fac=ctx["fac_rodada"])
im_final_m = motor_p3.calcular_im_final(mnd, nv_real_v, mandante=True)
im_final_v = motor_p3.calcular_im_final(vis, nv_real_m, mandante=False)

irc_m_bruto = 50.0 + ((mnd["urgencia_real"]["nota_posicao_atual"] + (20 if mnd["orgulho_ferido"]["veio_de_goleada_humilhante"] else 10 if mnd["orgulho_ferido"]["veio_de_derrota_prateleira_inferior"] else 0) + (10 if mnd["revanche"]["rival_goleou_ou_eliminou_recentemente"] else 0)) * ctx["fac_rodada"])
irc_v_bruto = 50.0 + ((vis["urgencia_real"]["nota_posicao_atual"] + (20 if vis["orgulho_ferido"]["veio_de_goleada_humilhante"] else 10 if vis["orgulho_ferido"]["veio_de_derrota_prateleira_inferior"] else 0) + (10 if vis["revanche"]["rival_goleou_ou_eliminou_recentemente"] else 0)) * ctx["fac_rodada"])

irc_final_m = min(100.0, max(0.0, irc_m_bruto))
irc_final_v = min(100.0, max(0.0, irc_v_bruto))

c_im1, c_im2 = st.columns(2)
with c_im1:
    st.metric(label=f"Índice de Momento (IM): {mnd['nome']}", value=f"{im_final_m} Pts")
    st.metric(label=f"Resposta Competitiva (IRC): {mnd['nome']}", value=f"{irc_final_m} Pts")
with c_im2:
    st.metric(label=f"Índice de Momento (IM): {vis['nome']}", value=f"{im_final_v} Pts")
    st.metric(label=f"Resposta Competitiva (IRC): {vis['nome']}", value=f"{irc_final_v} Pts")

st.write("---")

# ---------------------------------------------------------------------
# ETAPA 4: VEREDITO FINAL, JUNÇÃO E DISPARIDADE CRÍTICA
# ---------------------------------------------------------------------
st.header("🎯 Etapa 4: Veredito Unificado e Disparidade Crítica (Passo 4)")

overall_m = (res_con_m["Nota_Consistencia"] * 0.35) + (res_atq_m["Nota_Ataque"] * 0.25) + (res_def_m["Nota_Defesa"] * 0.25) + (res_res_m["Nota_Resistencia"] * 0.15)
overall_v = (res_con_v["Nota_Consistencia"] * 0.35) + (res_atq_v["Nota_Ataque"] * 0.25) + (res_def_v["Nota_Defesa"] * 0.25) + (res_res_v["Nota_Resistencia"] * 0.15)

nota_juncao_m = round((overall_m + im_final_m + irc_final_m) / 3, 1)
nota_juncao_v = round((overall_v + im_final_v + irc_final_v) / 3, 1)
diferenca_critica = round(nota_juncao_m - nota_juncao_v, 1)

col_f1, col_f2, col_f3 = st.columns(3)
with col_f1:
    st.metric(label=f"Nota Junção Final ({mnd['nome']})", value=f"{nota_juncao_m} Pts")
with col_f2:
    st.metric(label=f"Nota Junção Final ({vis['nome']})", value=f"{nota_juncao_v} Pts")
with col_f3:
    st.metric(label="Diferença Crítica Final", value=f"{diferenca_critica} Pts", delta=f"{diferenca_critica}")

st.write("---")

# ---------------------------------------------------------------------
# ETAPA 5: PAINEL COMPARATIVO DE PROBABILIDADES INTEGRADO (PASSO 7)
# ---------------------------------------------------------------------
st.header("🎯 Etapa 5: Painel Comparativo de Probabilidades Integrado (Passo 7)")

linhas_mercados = []
pct_metodo_casa = min(95.0, max(5.0, 45.0 + (diferenca_critica * 1.2)))
pct_metodo_fora = min(95.0, max(5.0, 30.0 - (diferenca_critica * 1.2)))
pct_metodo_empate = max(5.0, 100.0 - pct_metodo_casa - pct_metodo_fora)

forca_gols_geral = (res_atq_m["Nota_Ataque"] + res_atq_v["Nota_Ataque"]) / 2
forca_intensity_ht = (im_final_m + im_final_v) / 2

if odds.get("1X2", {}).get("casa_pct") is not None:
    dif = pct_metodo_casa - odds["1X2"]["casa_pct"]
    linhas_mercados.append(["Vitória Mandante (1)", f"{odds['1X2']['casa_pct']}%", f"{pct_metodo_casa:.1f}%", f"{dif:+.1f}%", "🟢 VALOR" if dif>=5.0 else "🔴 EVITAR" if dif<=-5.0 else "🟡 Neutro"])

if odds.get("1X2", {}).get("fora_pct") is not None:
    dif = pct_metodo_fora - odds["1X2"]["fora_pct"]
    linhas_mercados.append(["Vitória Visitante (2)", f"{odds['1X2']['fora_pct']}%", f"{pct_metodo_fora:.1f}%", f"{dif:+.1f}%", "🟢 VALOR" if dif>=5.0 else "🔴 EVITAR" if dif<=-5.0 else "🟡 Neutro"])

if odds.get("over_05_ht_pct") is not None:
    pct_metodo_o05ht = min(95.0, max(5.0, forca_intensity_ht - 10.0))
    dif = pct_metodo_o05ht - odds["over_05_ht_pct"]
    linhas_mercados.append(["Gols: Over 0.5 HT (Gol no 1º Tempo)", f"{odds['over_05_ht_pct']}%", f"{pct_metodo_o05ht:.1f}%", f"{dif:+.1f}%", "🟢 VALOR OVER HT" if dif>=5.0 else "🔴 EVITAR OVER HT" if dif<=-5.0 else "🟡 Neutro"])

if odds.get("over_15_ht_pct") is not None:
    pct_metodo_o15ht = min(90.0, max(5.0, forca_intensity_ht - 35.0))
    dif = pct_metodo_o15ht - odds["over_15_ht_pct"]
    linhas_mercados.append(["Gols: Over 1.5 HT", f"{odds['over_15_ht_pct']}%", f"{pct_metodo_o15ht:.1f}%", f"{dif:+.1f}%", "🟢 VALOR OVER 1.5 HT" if dif>=5.0 else "🔴 EVITAR OVER 1.5 HT" if dif<=-5.0 else "🟡 Neutro"])

if odds.get("over_15_ft_pct") is not None:
    pct_metodo_o15ft = min(98.0, max(5.0, forca_gols_geral - 5.0))
    dif = pct_metodo_o15ft - odds["over_15_ft_pct"]
    linhas_mercados.append(["Gols: Over 1.5 FT", f"{odds['over_15_ft_pct']}%", f"{pct_metodo_o15ft:.1f}%", f"{dif:+.1f}%", "🟢 VALOR OVER 1.5" if dif >= 5.0 else "🔴 EVITAR" if dif <= -5.0 else "🟡 Neutro"])

if odds.get("over_25_ft_pct") is not None:
    dif = (forca_gols_geral - 15.0) - odds["over_25_ft_pct"]
    linhas_mercados.append(["Gols: Over 2.5 FT", f"{odds['over_25_ft_pct']}%", f"{(forca_gols_geral - 15.0):.1f}%", f"{dif:+.1f}%", "🟢 VALOR OVER 2.5" if dif >= 5.0 else "🔴 EVITAR / IR NO UNDER" if dif <= -5.0 else "🟡 Neutro"])

if odds.get("ambas_marcam_sim_pct") is not None:
    dif = (forca_gols_geral - 12.0) - odds["ambas_marcam_sim_pct"]
    linhas_mercados.append(["Ambas Marcam: SIM", f"{odds['ambas_marcam_sim_pct']}%", f"{(forca_gols_geral - 12.0):.1f}%", f"{dif:+.1f}%", "🟢 VALOR AMBAS" if dif >= 5.0 else "🔴 EVITAR" if dif <= -5.0 else "🟡 Neutro"])

if odds.get("linha_escanteios_mercado", {}).get("over_pct") is not None:
    volume_chutes_combinado = (res_atq_m["FVO"] + res_atq_v["FVO"]) / 2
    pct_metodo_cantos = min(95.0, max(5.0, volume_chutes_combinado + 2.0))
    dif = pct_metodo_cantos - odds["linha_escanteios_mercado"]["over_pct"]
    linhas_mercados.append([f"Escanteios: Over {odds['linha_escanteios_mercado']['linha']}", f"{odds['linha_escanteios_mercado']['over_pct']}%", f"{pct_metodo_cantos:.1f}%", f"{dif:+.1f}%", "🟢 VALOR CANTOS" if dif >= 5.0 else "🔴 EVITAR CANTOS" if dif <= -5.0 else "🟡 Neutro"])

if pct_metodo_casa > 60.0 and diferenca_critica >= 10.0:
    linhas_mercados.append(["[Sugestão App] Empate Anula (DNB Casa)", "Proteção Ativa", "Alta Probabilidade", "FMP Favorável", "💎 ENTRADA RECOMENDADA"])
elif pct_metodo_fora > 45.0 and diferenca_critica <= -10.0:
    linhas_mercados.append(["[Sugestão App] Empate Anula (DNB Fora)", "Proteção Ativa", "Alta Probabilidade", "FMP Favorável", "💎 ENTRADA RECOMENDADA"])

df_probabilidades = pd.DataFrame(linhas_mercados, columns=["Mercado Operacional", "% Mercado", "% Método", "Variação Líquida", "Alerta Técnico"])
st.table(df_probabilidades)

st.info("💡 Observação: Caso os mercados de Cantos ou Gols HT não possuam dados preenchidos na estrutura de entrada, eles são omitidos automaticamente deste painel.")
st.write("---")


