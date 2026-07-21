import streamlit as st
import numpy as np

# 1. MOTOR MATEMÁTICO CORE DO SEU MÉTODO
class SistemaUniversalRigidoV55:
    def __init__(self, media_liga=None):
        self.media_liga = media_liga if media_liga else {
            'gols': 1.45, 'xg': 1.50, 'chutes': 13.5, 'chutes_gol': 4.5,
            'ataques': 105.0, 'atq_perigosos': 65.0
        }

    def _normalizar_min_max(self, valores, minimo, maximo):
        if maximo == minimo: return 0.5
        return (valores - minimo) / (maximo - minimo)

    def processar_texto_celular(self, texto_bruto):
        dados = {}
        linhas = texto_bruto.strip().split('\n')
        for linha in linhas:
            if ':' in linha:
                chave, valor = linha.split(':', 1)
                chave = chave.strip().lower()
                valor = valor.strip()
                try:
                    if '[' in valor:
                        dados[chave] = [float(x) for x in valor.replace('[','').replace(']','').split(',')]
                    else:
                        dados[chave] = float(valor) if '.' in valor or valor.isdigit() else valor
                except ValueError:
                    dados[chave] = valor
        return dados

    def calcular_passo_1_overall(self, t, mando, prateleira_adversario):
        sufixo = "_casa" if mando == "mandante" else "_fora"
        prateleira_propria = t.get('prateleira', 'Meio')
        mult_def, mult_atq = 1.0, 1.0
        
        if prateleira_propria == "Baixo" and prateleira_adversario == "Elite":
            mult_def, mult_atq = 0.75, 1.25  
        elif prateleira_propria == "Elite" and prateleira_adversario == "Baixo":
            mult_def, mult_atq = 1.25, 0.75  

        v_atq = (t.get(f'ataques{sufixo}', 105.0) / self.media_liga['ataques'])
        v_atq_p = (t.get(f'atq_perigosos{sufixo}', 65.0) / self.media_liga['atq_perigosos'])
        v_chutes = (t.get(f'chutes{sufixo}', 13.5) / self.media_liga['chutes'])
        v_chutes_g = (t.get(f'chutes_gol{sufixo}', 4.5) / self.media_liga['chutes_gol'])
        v_gols = (t.get(f'gols_marcados{sufixo}', 1.45) / self.media_liga['gols'])
        v_xg = (t.get(f'xg_marcado{sufixo}', 1.50) / self.media_liga['xg'])
        
        fvo = np.mean([v_atq, v_atq_p, v_chutes, v_chutes_g, v_gols, v_xg]) * 50 * mult_atq
        c_gol_p_gol_liga = self.media_liga['chutes_gol'] / self.media_liga['gols']
        c_gol_p_gol_time = max(0.1, t.get(f'chutes_gol{sufixo}', 4.5)) / max(0.1, t.get(f'gols_marcados{sufixo}', 1.45))
        fco = (c_gol_p_gol_liga / c_gol_p_gol_time) * 50
        nota_ataque = min(100.0, max(0.0, (fvo * 0.60) + (fco * 0.40)))

        v_atq_s = (self.media_liga['ataques'] / max(0.1, t.get(f'ataques_sofridos{sufixo}', 105.0)))
        v_atq_ps = (self.media_liga['atq_perigosos'] / max(0.1, t.get(f'atq_perigosos_sofridos{sufixo}', 65.0)))
        v_chutes_s = (self.media_liga['chutes'] / max(0.1, t.get(f'chutes_sofridos{sufixo}', 13.5)))
        v_chutes_gs = (self.media_liga['chutes_gol'] / max(0.1, t.get(f'chutes_gol_sofridos{sufixo}', 4.5)))
        v_gols_s = (self.media_liga['gols'] / max(0.1, t.get(f'gols_sofridos{sufixo}', 1.45)))
        v_xg_s = (self.media_liga['xg'] / max(0.1, t.get(f'xg_cedido{sufixo}', 1.50)))
        
        frd = np.mean([v_atq_s, v_atq_ps, v_chutes_s, v_chutes_gs, v_gols_s, v_xg_s]) * 50 / mult_def
        c_gol_s_p_gol_time = max(0.1, t.get(f'chutes_gol_sofridos{sufixo}', 4.5)) / max(0.1, t.get(f'gols_sofridos{sufixo}', 1.45))
        fcd_def = (c_gol_s_p_gol_time / c_gol_p_gol_liga) * 50
        nota_defesa = min(100.0, max(0.0, (frd * 0.60) + (fcd_def * 0.40)))

        hist_atq = np.array(t.get('hist_nota_atq', [50.0]*5)) * mult_atq
        hist_def = np.array(t.get('hist_nota_def', [50.0]*5)) / mult_def
        bloco_unificado = np.concatenate([hist_atq, hist_def])
        bloco_normalizado = self._normalizar_min_max(bloco_unificado, 0, 150)
        fdm = 100 - (np.std(bloco_normalizado) * 100)
        
        im_max = max(t.get('hist_im_5_jogos', [50.0]*5))
        im_min = min(t.get('hist_im_5_jogos', [50.0]*5))
        ier = 100 - (im_max - im_min)
        nota_consistencia = min(100.0, max(0.0, (fdm * 0.60) + (ier * 0.40)))

        fcd_pressao = (v_chutes_s / max(0.1, v_xg_s)) * 50
        egz = (v_gols_s / max(0.1, v_chutes_gs)) * 50
        fri = t.get('pct_pontos_recuperados', 0.50) * 100
        fzc = t.get('saldo_minuto_75_90', 0.0) * 50
        nota_pressao = (fcd_pressao * 0.30) + (egz * 0.30) + (fri * 0.20) + (fzc * 0.20)
        nota_pressao = min(100.0, max(0.0, nota_pressao))

        overall = (nota_consistencia * 0.35) + (nota_ataque * 0.25) + (nota_defesa * 0.25) + (nota_pressao * 0.15)
        return round(overall, 2)

# ==========================================
# 2. INTERFACE VISUAL DO SEU APLICATIVO
# ==========================================
st.set_page_config(page_title="Preditor Rígido V5.5", layout="centered")

st.title("🎯 Motor Preditivo Rígido V5.5")
st.caption("Interface de Usuário Ativada | Passo 1: Máquina de Overall")

motor = SistemaUniversalRigidoV55()

st.subheader("🏛️ Configuração do Cenário")
prateleira_m = st.selectbox("Prateleira do Mandante", ["Elite", "Meio", "Baixo"], index=1)
prateleira_v = st.selectbox("Prateleira do Visitante", ["Elite", "Meio", "Baixo"], index=1)

st.subheader("📋 Entrada de Dados por Texto")

exemplo_texto = (
    "ataques_casa: 95.0\n"
    "atq_perigosos_casa: 58.0\n"
    "chutes_casa: 11.0\n"
    "chutes_gol_casa: 3.2\n"
    "gols_marcados_casa: 1.2\n"
    "xg_marcado_casa: 1.05\n"
    "ataques_sofridos_casa: 112.0\n"
    "atq_perigosos_sofridos_casa: 72.0\n"
    "chutes_sofridos_casa: 15.0\n"
    "chutes_gol_sofridos_casa: 5.1\n"
    "gols_sofridos_casa: 1.8\n"
    "xg_cedido_casa: 1.65\n"
    "hist_nota_atq: [45.2, 50.1, 42.8, 60.2, 48.0]\n"
    "hist_nota_def: [38.5, 41.2, 55.0, 32.1, 44.5]\n"
    "hist_im_5_jogos: [42.0, 48.0, 39.0, 51.0, 45.0]\n"
    "pct_pontos_recuperados: 0.15\n"
    "saldo_minuto_75_90: -1.0"
)

texto_m = st.text_area("Cole as Estatísticas do MANDANTE:", value=exemplo_texto, height=150)
texto_v = st.text_area("Cole as Estatísticas do VISITANTE:", value=exemplo_texto, height=150)

if st.button("CALCULAR OVERALL RIGIDO", use_container_width=True):
    dados_m = motor.processar_texto_celular(texto_m)
    dados_v = motor.processar_texto_celular(texto_v)
    
    dados_m['prateleira'] = prateleira_m
    dados_v['prateleira'] = prateleira_v
    
    overall_m = motor.calcular_passo_1_overall(dados_m, "mandante", prateleira_v)
    overall_v = motor.calcular_passo_1_overall(dados_v, "visitante", prateleira_m)
    
    st.markdown("### 📊 Notas de Overall Finais")
    col1, col2 = st.columns(2)
    with col1: 
        st.metric("Overall Mandante", f"{overall_m} pts")
    with col2: 
        st.metric("Overall Visitante", f"{overall_v} pts")
