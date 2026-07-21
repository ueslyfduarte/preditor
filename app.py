import streamlit as st
import numpy as np

class EcossistemaPreditivoCompletoV66:
    def __init__(self):
        # Médias padrão globais (âncora de segurança se os dados da liga sumirem)
        self.media_liga_padrao = {
            'gols': 1.45, 'xg': 1.50, 'chutes': 13.5, 'chutes_gol': 4.5,
            'ataques': 105.0, 'atq_perigosos': 65.0
        }

    def _normalizar_min_max(self, valores, minimo, maximo):
        if maximo == minimo: return 0.5
        return (valores - minimo) / (maximo - minimo)

    def processar_bloco_unico(self, texto_bruto):
        dados = {}
        linhas = texto_bruto.strip().split('\n')
        for linha in linhas:
            if ':' in linha and not linha.strip().startswith('---'):
                chave, valor = linha.split(':', 1)
                chave = chave.strip().lower()
                valor = valor.strip()
                if not valor:
                    continue
                try:
                    if '[' in valor:
                        elementos = valor.replace('[','').replace(']','').split(',')
                        elementos = [x.strip() for x in elementos if x.strip()]
                        try:
                            dados[chave] = [float(x) for x in elementos]
                        except ValueError:
                            dados[chave] = elementos
                    else:
                        dados[chave] = float(valor) if '.' in valor or valor.isdigit() else valor
                except ValueError:
                    dados[chave] = valor
        return dados

    def calcular_ajuste_empates(self, historico_pontos, prateleiras_adversarios, condicao, prateleira_propria):
        if not historico_pontos: return 0.0
        pontos_ajustados = []
        for i, p in enumerate(historico_pontos):
            prat_adv = prateleiras_adversarios[i] if i < len(prateleiras_adversarios) else "Meio"
            if p == 3:
                pontos_ajustados.append(3.0)
            elif p == 0:
                pontos_ajustados.append(0.0)
            elif p == 1:
                if condicao == "visitante":
                    if prateleira_propria == "Elite": pontos_ajustados.append(2.0)
                    else: pontos_ajustados.append(3.0)
                else:
                    if prat_adv in ["Elite", "Meio"] and prateleira_propria != "Elite": pontos_ajustados.append(2.0)
                    elif prat_adv == "Meio" and prateleira_propria == "Elite": pontos_ajustados.append(1.0)
                    else: pontos_ajustados.append(0.0)
        return np.sum(pontos_ajustados)

    def executar_calculo_completo(self, d):
        # --- AJUSTE DINÂMICO DA LIGA ---
        # Se as chaves existirem no texto colado, o sistema usa. Se não, herda o padrão global.
        media_liga = {
            'gols': d.get('gols_liga', self.media_liga_padrao['gols']),
            'xg': d.get('xg_liga', self.media_liga_padrao['xg']),
            'chutes': d.get('chutes_liga', self.media_liga_padrao['chutes']),
            'chutes_gol': d.get('chutes_gol_liga', self.media_liga_padrao['chutes_gol']),
            'ataques': d.get('ataques_liga', self.media_liga_padrao['ataques']),
            'atq_perigosos': d.get('atq_perigosos_liga', self.media_liga_padrao['atq_perigosos'])
        }
        
        usando_dados_reais_liga = 'gols_liga' in d

        rodada = d.get('rodada_atual', 20)
        fac = 0.30 if rodada <= 10 else (0.60 if rodada <= 25 else (0.85 if rodada <= 33 else 1.00))
        
        prat_m = d.get('prateleira_m', 'Meio')
        prat_v = d.get('prateleira_v', 'Meio')
        
        pm_atq, pm_def = 1.0, 1.0
        if prat_m == "Baixo" and prat_v == "Elite": pm_def, pm_atq = 0.75, 1.25
        elif prat_m == "Elite" and prat_v == "Baixo": pm_def, pm_atq = 1.25, 0.75

        pv_atq, pv_def = 1.0, 1.0
        if prat_v == "Baixo" and prat_m == "Elite": pv_def, pv_atq = 0.75, 1.25
        elif prat_v == "Elite" and prat_m == "Baixo": pv_def, pv_atq = 1.25, 0.75

        # --- MANDANTE: OVERALL (PASSO 1) ---
        fvo_m = np.mean([d.get('ataques_casa',105)/media_liga['ataques'], d.get('atq_perigosos_casa',65)/media_liga['atq_perigosos'],
                         d.get('chutes_casa',13.5)/media_liga['chutes'], d.get('chutes_gol_casa',4.5)/media_liga['chutes_gol'],
                         d.get('gols_marcados_casa',1.45)/media_liga['gols'], d.get('xg_marcado_casa',1.5)/media_liga['xg']]) * 50 * pm_atq
        c_gol_p_gol_liga = media_liga['chutes_gol'] / media_liga['gols']
        c_gol_p_gol_time = max(0.1, d.get('chutes_gol_casa',4.5))/max(0.1, d.get('gols_marcados_casa',1.45))
        fco_m = (c_gol_p_gol_liga / c_gol_p_gol_time) * 50
        nota_atq_m = min(100.0, max(0.0, (fvo_m * 0.60) + (fco_m * 0.40)))

        frd_m = np.mean([media_liga['ataques']/max(0.1, d.get('ataques_sofridos_casa',105)), media_liga['atq_perigosos']/max(0.1, d.get('atq_perigosos_sofridos_casa',65)),
                         media_liga['chutes']/max(0.1, d.get('chutes_sofridos_casa',13.5)), media_liga['chutes_gol']/max(0.1, d.get('chutes_gol_sofridos_casa',4.5)),
                         media_liga['gols']/max(0.1, d.get('gols_sofridos_casa',1.45)), media_liga['xg']/max(0.1, d.get('xg_cedido_casa',1.5))]) * 50 / pm_def
        c_gol_s_p_gol_time = max(0.1, d.get('chutes_gol_sofridos_casa',4.5))/max(0.1, d.get('gols_sofridos_casa',1.45))
        fcd_m = (c_gol_s_p_gol_time / c_gol_p_gol_liga) * 50
        nota_def_m = min(100.0, max(0.0, (frd_m * 0.60) + (fcd_m * 0.40)))

        b_unif_m = self._normalizar_min_max(np.concatenate([np.array(d.get('hist_nota_atq_m',[50.0]*5))*pm_atq, np.array(d.get('hist_nota_def_m',[50.0]*5))/pm_def]), 0, 150)
        fdm_m = 100 - (np.std(b_unif_m) * 100)
        ier_m = 100 - (max(d.get('hist_im_5_m',[50.0]*5)) - min(d.get('hist_im_5_m',[50.0]*5)))
        nota_cons_m = min(100.0, max(0.0, (fdm_m * 0.60) + (ier_m * 0.40)))
        nota_pres_m = min(100.0, max(0.0, ((d.get('chutes_sofridos_casa',13.5)/max(0.1, d.get('xg_cedido_casa',1.5)))*30 + (d.get('gols_sofridos_casa',1.45)/max(0.1, d.get('chutes_gol_sofridos_casa',4.5)))*30 + d.get('pct_pontos_recuperados_m',0.5)*20 + d.get('saldo_minuto_75_90_m',0)*10)))
        overall_m = (nota_cons_m * 0.35) + (nota_atq_m * 0.25) + (nota_def_m * 0.25) + (nota_pres_m * 0.15)

        # --- MANDANTE: MOMENTO (PASSO 2 & 3) ---
        prat_adv_m = d.get('prateleiras_adversarios_mando_m', ['Meio']*5)
        pts_cc_3_m = self.calcular_ajuste_empates(d.get('jogos_mando_3_m',), prat_adv_m[:3], "mandante", prat_m) / 9.0 * 100
        pts_cc_5_m = self.calcular_ajuste_empates(d.get('jogos_mando_5_m',), prat_adv_m, "mandante", prat_m) / 15.0 * 100
        cc_m = (pts_cc_3_m * 0.65) + (pts_cc_5_m * 0.35)
        geral_m = ((np.sum(d.get('jogos_gerais_3_m',))/9*100)*0.50 + (np.sum(d.get('jogos_gerais_5_m',))/15*100)*0.35 + (np.sum(d.get('jogos_gerais_10_m',*10))/30*100)*0.15)
        mult_prat_m = 1.6 if prat_v == "Elite" else (1.0 if prat_v == prat_m else 0.0)
        tab_m = 50 + ((d.get('posicao_real_m',10) - d.get('posicao_momentanea_m',10)) * mult_prat_m)
        im_m = min(100.0, max(0.0, (cc_m * 0.45) + (geral_m * 0.35) + (tab_m * 0.20)))

        # --- MANDANTE: IRC ---
        fpt_m = -10 if (prat_m == "Elite" and rodada <= 10) else 0
        irc_m = min(100.0, max(0.0, 50 + (d.get('urgencia_real_m',50) + fpt_m + d.get('orgulho_ferido_m',0) + d.get('revanche_m',0)) * fac))

        # --- VISITANTE: OVERALL (PASSO 1) ---
        fvo_v = np.mean([d.get('ataques_fora',105)/media_liga['ataques'], d.get('atq_perigosos_fora',65)/media_liga['atq_perigosos'],
                         d.get('chutes_fora',13.5)/media_liga['chutes'], d.get('chutes_gol_fora',4.5)/media_liga['chutes_gol'],
                         d.get('gols_marcados_fora',1.45)/media_liga['gols'], d.get('xg_marcado_fora',1.5)/media_liga['xg']]) * 50 * pv_atq
        fco_v = ((media_liga['chutes_gol']/media_liga['gols']) / (max(0.1, d.get('chutes_gol_fora',4.5))/max(0.1, d.get('gols_marcados_fora',1.45)))) * 50
        nota_atq_v = min(100.0, max(0.0, (fvo_v * 0.60) + (fco_v * 0.40)))

        frd_v = np.mean([media_liga['ataques']/max(0.1, d.get('ataques_sofridos_fora',105)), media_liga['atq_perigosos']/max(0.1, d.get('atq_perigosos_sofridos_fora',65)),
                         media_liga['chutes']/max(0.1, d.get('chutes_sofridos_fora',13.5)), media_liga['chutes_gol']/max(0.1, d.get('chutes_gol_sofridos_fora',4.5)),
                         media_liga['gols']/max(0.1, d.get('gols_sofridos_fora',1.45)), media_liga['xg']/max(0.1, d.get('xg_cedido_fora',1.5))]) * 50 / pv_def
        fcd_v = ((max(0.1, d.get('chutes_gol_sofridos_fora',4.5))/max(0.1, d.get('gols_sofridos_fora',1.45))) / (media_liga['chutes_gol']/media_liga['gols'])) * 50
        nota_def_v = min(100.0, max(0.0, (frd_v * 0.60) + (fcd_v * 0.40)))

        b_unif_v = self._normalizar_min_max(np.concatenate([np.array(d.get('hist_nota_atq_v',[50.0]*5))*pv_atq, np.array(d.get('hist_nota_def_v',[50.0]*5))/pv_def]), 0, 150)
        fdm_v = 100 - (np.std(b_unif_v) * 100)
        ier_v = 100 - (max(d.get('hist_im_5_v',[50.0]*5)) - min(d.get('hist_im_5_v',[50.0]*5)))
        nota_cons_v = min(100.0, max(0.0, (fdm_v * 0.60) + (ier_v * 0.40)))
        nota_pres_v = min(100.0, max(0.0, ((d.get('chutes_sofridos_fora',13.5)/max(0.1, d.get('xg_cedido_fora',1.5)))*30 + (d.get('gols_sofridos_fora',1.45)/max(0.1, d.get('chutes_gol_sofridos_fora',4.5)))*30 + d.get('pct_pontos_recuperados_v',0.5)*20 + d.get('saldo_minuto_75_90_v',0)*10)))
        overall_v = (nota_cons_v * 0.35) + (nota_atq_v * 0.25) + (nota_def_v * 0.25) + (nota_pres_v * 0.15)

        # --- VISITANTE: MOMENTO (PASSO 2 & 3) ---
        prat_adv_v = d.get('prateleiras_adversarios_mando_v', ['Meio']*5)
        pts_cc_3_v = self.calcular_ajuste_empates(d.get('jogos_mando_3_v',), prat_adv_v[:3], "visitante", prat_v) / 9.0 * 100pts_cc_5_v = self.calcular_ajuste_empates(d.get('jogos_mando_5_v',), prat_adv_v, "visitante", prat_v) / 15.0 * 100cc_v = (pts_cc_3_v * 0.65) + (pts_cc_5_v * 0.35)geral_v = ((np.sum(d.get('jogos_gerais_3_v',))/9*100)0.50 + (np.sum(d.get('jogos_gerais_5_v',))/15100)*0.35 + (np.sum(d.get('jogos_gerais_10_v',10))/30100)*0.15)mult_prat_v = 1.6 if prat_m == "Elite" else (1.0 if prat_m == prat_v else 0.0)tab_v = 50 + ((d.get('posicao_real_v',10) - d.get('posicao_momentanea_v',10)) * mult_prat_v)im_v = min(100.0, max(0.0, (cc_v * 0.45) + (geral_v * 0.35) + (tab_v * 0.20)))# --- VISITANTE: IRC ---fpt_v = -10 if (prat_v == "Elite" and rodada <= 10) else 0irc_v = min(100.0, max(0.0, 50 + (d.get('urgencia_real_v',50) + fpt_v + d.get('orgulho_ferido_v',0) + d.get('revanche_v',0)) * fac))# --- PASSO 4: UNIFICAÇÃO E DISPARIDADE ---juncao_m = (overall_m + im_m + irc_m) / 3juncao_v = (overall_v + im_v + irc_v) / 3return {'m_nome': d.get('nome_m', 'Mandante'), 'v_nome': d.get('nome_v', 'Visitante'),'m_pos': d.get('posicao_real_m', 10), 'v_pos': d.get('posicao_real_v', 10),'m_prat': prat_m, 'v_prat': prat_v,'overall_m': round(overall_m, 2), 'overall_v': round(overall_v, 2),'im_m': round(im_m, 2), 'im_v': round(im_v, 2),'irc_m': round(irc_m, 2), 'irc_v': round(irc_v, 2),'final_m': round(juncao_m, 2), 'final_v': round(juncao_v, 2),'disparidade': round(juncao_m - juncao_v, 2),'dados_reais_liga': usando_dados_reais_liga}==========================================INTERFACE VISUAL==========================================st.set_page_config(page_title="Preditor Rígido V6.6", layout="centered")st.title("🚀 Sistema Preditivo Unificado V6.6")st.caption("Detecção Dinâmica de Médias da Liga Ativada")app = EcossistemaPreditivoCompletoV66()texto_input = st.text_area("Cole as estatísticas da partida:", height=250, placeholder="gols_liga: 1.62\nxg_liga: 1.55\nnome_m: Flamengo...")if st.button("EXECUTAR ANÁLISE COMPLETA", use_container_width=True):if not texto_input.strip():st.error("Cole os dados estruturados do confronto antes de prosseguir.")else:try:dados_conferidos = app.processar_bloco_unico(texto_input)res = app.executar_calculo_completo(dados_conferidos)# Notificação visual do tipo de ancoragemif res['dados_reais_liga']:st.success("✅ Médias Reais da Liga detectadas e injetadas nas fórmulas com sucesso!")else:st.info("ℹ️ Médias da liga ausentes no texto. Aplicada a Âncora de Segurança Padrão Global.")# 1. PAINEL INICIALst.markdown("### 🏛️ PAINEL INICIAL: POSICIONAMENTO E PROSPECÇÃO")col_m, col_v = st.columns(2)with col_m:st.markdown(f"🏠 {res['m_nome']}")st.write(f"Posição Atual Real: {int(res['m_pos'])}º")st.write(f"Prospecção de Prateleira: {res['m_prat']}")with col_v:st.markdown(f"🚀 {res['v_nome']}")st.write(f"Posição Atual Real: {int(res['v_pos'])}º")st.write(f"Prospecção de Prateleira: {res['v_prat']}")# 2. DECOMPOSIÇÃO DE FORÇASst.markdown("---")st.markdown("### 📊 Decomposição de Forças (Escala 0 a 100)")c1, c2, c3 = st.columns(3)c1.metric(f"Overall {res['m_nome']}", f"{res['overall_m']} pts")c1.metric(f"Overall {res['v_nome']}", f"{res['overall_v']} pts")c2.metric(f"Momento (IM) {res['m_nome']}", f"{res['im_m']} pts")c2.metric(f"Momento (IM) {res['v_nome']}", f"{res['im_v']} pts")c3.metric(f"Psicológico (IRC) {res['m_nome']}", f"{res['irc_m']} pts")c3.metric(f"Psicológico (IRC) {res['v_nome']}", f"{res['irc_v']} pts")# 3. DISPARIDADEst.markdown("---")st.markdown("### 🎯 PASSO 4: TELA DE CONFRONTO DIRETO E DISPARIDADE")col_f1, col_f2 = st.columns(2)col_f1.metric(f"Nota Junção {res['m_nome']}", f"{res['final_m']} pts")col_f2.metric(f"Nota Junção {res['v_nome']}", f"{res['final_v']} pts")disp = res['disparidade']st.subheader(f"Diferença Crítica Final: {disp:+} pontos")except Exception as e:st.error(f"Erro nas equações: {str(e)}. Verifique as chaves do texto colado.")

