import numpy as np
from typing import Dict, Any, List

# =====================================================================
# DIVISÓRIA 1: MÓDULO DO PAINEL INICIAL (POSIÇÕES E RETROVENCEDOR)
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
        """
        Executa a regra do PASSO 3 (Retrovencedor de Empates) para o cálculo do Form Real.
        Filtra o momento traduzindo empates frustrantes em perdas reais de pontuação.
        """
        if resultado == 'V':
            return 3.0
        if resultado == 'D':
            return 0.0
        
        # Se for Empate ('E') - Aplicação da regra de prateleiras ajustada para o App
        if mando == 'visitante':
            if nivel_time < nivel_adversario: # Visitante era de prateleira superior
                return 2.0 # Vale 66.6% de uma vitória (2 pontos)
            return 3.0 # Igual ou inferior pontua cheio no empate fora (100% = 3 pontos)
            
        else: # Mandante
            if nivel_time == nivel_adversario or nivel_time < nivel_adversario:
                return 2.0 # Contra igual ou superior, vale 66.6% (2 pontos)
            elif nivel_time == 1 and nivel_adversario == 4:
                return 0.0 # Super favorito contra Z-4 empatando em casa = FIASCO (0 pontos)
            else:
                return 1.0 # Favorito contra meio de tabela = vale 33.3% (1 ponto)

    def definir_nivel_posicao(self, posicao: int) -> int:
        """Divide a tabela rigidamente a cada 5 posições (Regra dos 4 Quadrantes)"""
        if 1 <= posicao <= 5:   return 1  # Elite
        if 6 <= posicao <= 10:  return 2  # Alto
        if 11 <= posicao <= 15: return 3  # Meio
        return 4                          # Baixo / Zona de Perigo

    def calcular_nivel_dinamico(self, ranking_pre: int, posicao_atual: int) -> int:
        """Calcula o FMP Dinâmico ponderando a âncora pré-campeonato de acordo com a rodada"""
        if self.rodada_atual <= 10:
            posicao_ponderada = (ranking_pre * 0.70) + (posicao_atual * 0.30)
        elif 11 <= self.rodada_atual <= 25:
            posicao_ponderada = (ranking_pre * 0.30) + (posicao_atual * 0.70)
        else:
            posicao_ponderada = posicao_atual
            
        return self.definir_nivel_posicao(int(np.round(posicao_ponderada)))

    def processar_time(self, dados: Dict[str, Any], adversario_nivel_atual: int, mando: str) -> Dict[str, Any]:
        """Processa e consolida todas as métricas de um time para o Painel Inicial"""
        nivel_atual = self.definir_nivel_posicao(dados['posicao_atual'])
        nivel_dinamico = self.calcular_nivel_dinamico(dados['ranking_pre'], dados['posicao_atual'])
        
        # Processamento do Form Geral e de Campo utilizando o Retrovencedor de Empates
        pontos_f5 = sum([self.calcular_pontos_retro(r, 'geral', nivel_atual, adversario_nivel_atual) for r in dados['historico_5']])
        pontos_f10 = sum([self.calcular_pontos_retro(r, 'geral', nivel_atual, adversario_nivel_atual) for r in dados['historico_10']])
        pontos_mando = sum([self.calcular_pontos_retro(r, mando, nivel_atual, adversario_nivel_atual) for r in dados['historico_mando_5']])
        
        aproveitamento_f5 = pontos_f5 / 15.0
        aproveitamento_f10 = pontos_f10 / 30.0
        aproveitamento_mando = pontos_mando / 15.0
        
        return {
            "posicao_real": dados['posicao_atual'],
            "nivel_real": nivel_atual,
            "nivel_dinamico_fmp": nivel_dinamico,
            "aproveitamento_f5_retro": aproveitamento_f5,
            "aproveitamento_f10_retro": aproveitamento_f10,
            "aproveitamento_mando_retro": aproveitamento_mando
        }


# =====================================================================
# DIVISÓRIA 2: MÓDULO MÁQUINA DE OVERALL (FMP RODADA A RODADA E TRAVAS)
# =====================================================================

class MaquinaOverallV28:
    """
    Módulo 2 do Método de Análise Esportiva V2.8.
    Calcula as notas de Ataque, Defesa, Consistência e Resistência à Pressão (0-100),
    aplicando o FMP rodada a rodada no histórico dos jogos passados.
    """
    def __init__(self):
        self.base_score = 50.0

    def obter_multiplicadores_fmp(self, nivel_time: int, nivel_adversario_historico: int) -> Dict[str, float]:
        """Retorna os pesos assimétricos do FMP com base nas 4 prateleiras interligadas"""
        if nivel_time < nivel_adversario_historico:   # Time era mais forte que o rival daquele dia
            return {"erro_defensivo": 1.40, "acerto_ofensivo": 0.60}
        elif nivel_time > nivel_adversario_historico: # Time era mais fraco que o rival daquele dia
            return {"erro_defensivo": 0.70, "acerto_ofensivo": 1.30}
        else:                                         # Prateleiras iguais
            return {"erro_defensivo": 1.00, "acerto_ofensivo": 1.00}

    def modular_historico_ofensivo(self, jogos_time: List[Dict[str, float]], nivel_time: int) -> List[Dict[str, float]]:
        """Aplica o FMP rodada a rodada em cada jogo passado para o bloco de ataque"""
        jogos_modulados = []
        for jogo in jogos_time:
            fmp = self.obter_multiplicadores_fmp(nivel_time, jogo['nivel_adversario_dia'])
            jogo_mod = {
                "ataques": jogo['ataques'] * fmp['acerto_ofensivo'],
                "ataques_perigosos": jogo['ataques_perigosos'] * fmp['acerto_ofensivo'],
                "chutes": jogo['chutes'] * fmp['acerto_ofensivo'],
                "chutes_gol": jogo['chutes_gol'] * fmp['acerto_ofensivo'],
                "gols": jogo['gols'] * fmp['acerto_ofensivo'],
                "xg": jogo['xg'] * fmp['acerto_ofensivo']
            }
            jogos_modulados.append(jogo_mod)
        return jogos_modulados

    def modular_historico_defensivo(self, jogos_time: List[Dict[str, float]], nivel_time: int) -> List[Dict[str, float]]:
        """Aplica o FMP rodada a rodada em cada jogo passado para o bloco de defesa"""
        jogos_modulados = []
        for jogo in jogos_time:
            fmp = self.obter_multiplicadores_fmp(nivel_time, jogo['nivel_adversario_dia'])
            jogo_mod = {
                "ataques_sofridos": jogo['ataques_sofridos'] * fmp['erro_defensivo'],
                "ataques_perigosos_sofridos": jogo['ataques_perigosos_sofridos'] * fmp['erro_defensivo'],
                "chutes_sofridos": jogo['chutes_sofridos'] * fmp['erro_defensivo'],
                "chutes_gol_sofridos": jogo['chutes_gol_sofridos'] * fmp['erro_defensivo'],
                "gols_sofridos": jogo['gols_sofridos'] * fmp['erro_defensivo'],
                "xg_cedido": jogo['xg_cedido'] * fmp['erro_defensivo']
            }
            jogos_modulados.append(jogo_mod)
        return jogos_modulados

    def calcular_bloco_ataque(self, jogos_modulados: List[Dict[str, float]], liga: Dict[str, float]) -> Dict[str, float]:
        """Executa o Passo 1-A com os dados históricos já limpos pelo FMP"""
        if not jogos_modulados:
            return {"FVO": self.base_score, "FCO": self.base_score, "Nota_Ataque": self.base_score}

        keys = ["ataques", "ataques_perigosos", "chutes", "chutes_gol", "gols", "xg"]
        med_time = {k: np.mean([j[k] for j in jogos_modulados]) for k in keys}

        proporcoes_fvo = [
            med_time['ataques'] / max(0.0001, liga['ataques']),
            med_time['ataques_perigosos'] / max(0.0001, liga['ataques_perigosos']),
            med_time['chutes'] / max(0.0001, liga['chutes']),
            med_time['chutes_gol'] / max(0.0001, liga['chutes_gol']),
            med_time['gols'] / max(0.0001, liga['gols']),
            med_time['xg'] / max(0.0001, liga['xg'])
        ]
        fvo = np.mean(proporcoes_fvo) * self.base_score

        chutes_por_gol_liga = liga['chutes_gol'] / max(0.0001, liga['gols'])
        chutes_por_gol_time = med_time['chutes_gol'] / max(0.0001, med_time['gols'])
        fco = (chutes_por_gol_liga / max(0.0001, chutes_por_gol_time)) * self.base_score

        nota_ataque = min(100.0, max(0.0, (fvo * 0.60) + (fco * 0.40)))
        return {"FVO": round(fvo, 2), "FCO": round(fco, 2), "Nota_Ataque": round(nota_ataque, 2)}

    def calcular_bloco_defesa(self, jogos_modulados: List[Dict[str, float]], liga: Dict[str, float]) -> Dict[str, float]:
        """Executa o Passo 1-B com os dados históricos já limpos pelo FMP"""
        if not jogos_modulados:
            return {"FRD": self.base_score, "FCD": self.base_score, "Nota_Defesa": self.base_score}

        keys = ["ataques_sofridos", "ataques_perigosos_sofridos", "chutes_sofridos", "chutes_gol_sofridos", "gols_sofridos", "xg_cedido"]
        med_time = {k: np.mean([j[k] for j in jogos_modulados]) for k in keys}

        proporcoes_frd = [
            liga['ataques_sofridos'] / max(0.0001, med_time['ataques_sofridos']),
            liga['ataques_perigosos_sofridos'] / max(0.0001, med_time['ataques_perigosos_sofridos']),
            liga['chutes_sofridos'] / max(0.0001, med_time['chutes_sofridos']),
            liga['chutes_gol_sofridos'] / max(0.0001, med_time['chutes_gol_sofridos']),
            liga['gols_sofridos'] / max(0.0001, med_time['gols_sofridos']),
            liga['xg_cedido'] / max(0.0001, med_time['xg_cedido'])
        ]
        frd = np.mean(proporcoes_frd) * self.base_score

        chutes_sofridos_por_gol_time = med_time['chutes_gol_sofridos'] / max(0.0001, med_time['gols_sofridos'])
chutes_sofridos_por_gol_liga = liga['chutes_gol_sofridos'] / max(0.0001, liga['gols_sofridos'])
fcd = (chutes_sofridos_por_gol_time / max(0.0001, chutes_sofridos_por_gol_liga)) * self.base_score
nota_defesa = min(100.0, max(0.0, (frd * 0.60) + (fcd * 0.40)))
return {"FRD": round(frd, 2), "FCD": round(fcd, 2), "Nota_Defesa": round(nota_defesa, 2)}
    def calcular_bloco_consistencia(self, jogos_atq_mod: List[Dict[str, float]], jogos_def_mod: List[Dict[str, float]], im_max: float, im_min: float, liga: Dict[str, float]) -> Dict[str, float]:
        """Executa o Passo 1-C calculando a dispersão das proporções moduladas rodada a rodada"""
        proporcoes_rodada = []
        for i in range(len(jogos_atq_mod)):
            ja = jogos_atq_mod[i]
            jd = jogos_def_mod[i]
            vetor_rodada = [
                ja['ataques'] / max(0.0001, liga['ataques']),
                ja['chutes_gol'] / max(0.0001, liga['chutes_gol']),
                ja['gols'] / max(0.0001, liga['gols']),
                liga['gols_sofridos'] / max(0.0001, jd['gols_sofridos']),
                liga['xg_cedido'] / max(0.0001, jd['xg_cedido'])
            ]
            proporcoes_rodada.append(np.std(vetor_rodada))
            
        fdm_std = np.mean(proporcoes_rodada) if proporcoes_rodada else 0.0
        fdm = max(0.0, min(100.0, 100.0 - (fdm_std * 100.0)))
        ier = max(0.0, min(100.0, 100.0 - (im_max - im_min)))
        
        nota_consistencia = (fdm * 0.60) + (ier * 0.40)
        return {"FDM": round(fdm, 2), "IER": round(ier, 2), "Nota_Consistencia": round(nota_consistencia, 2)}

def calcular_bloco_resistencia(self, time_pressao: Dict[str, float], liga_pressao: Dict[str, float]) -> Dict[str, float]:
"""Executa o Passo 1-D: Bloco de Resistência à Pressão"""
fcd_vol = (liga_pressao['xg_cedido'] / max(0.0001, time_pressao['xg_cedido'])) * (liga_pressao['chutes_sofridos'] / max(0.0001, time_pressao['chutes_sofridos']))
fcd_nota = min(100.0, fcd_vol * self.base_score)
time_chutes_por_gol = time_pressao['chutes_gol_sofridos'] / max(0.0001, time_pressao['gols_sofridos'])
liga_chutes_por_gol = liga_pressao['chutes_gol_sofridos'] / max(0.0001, liga_pressao['gols_sofridos'])
egz_nota = min(100.0, (time_chutes_por_gol / max(0.0001, liga_chutes_por_gol)) * self.base_score)
fri_nota = min(100.0, (time_pressao['pontos_recuperados'] / max(0.0001, time_pressao['pontos_disputados_atras'])) * 100.0)
fzc_nota = min(100.0, max(0.0, 50.0 + ((time_pressao['gols_marcados_fim'] - time_pressao['gols_sofridos_fim']) * 10.0)))
nota_resistencia = (fzc_nota * 0.30) + (egz_nota * 0.30) + (fri_nota * 0.20) + (fcd_nota * 0.20)
return {"Nota_Resistencia": round(nota_resistencia, 2)}

=====================================================================

DIVISÓRIA 3: MÓDULO ÍNDICE DE MOMENTO (IM COMPLETO COM TRAVAS)

=====================================================================
class IndiceMomentoV28:
"""
Módulo 3 do Método de Análise Esportiva V2.8.
Calcula o Índice de Momento (IM) de 0 a 100.
"""
def init(self, fac: float):
self.fac = fac
self.base_score = 50.0
def converter_historico_nota(self, historico: List[str], mando: str, nivel_time: int, nivel_adversario: int) -> float:
if not historico:
return self.base_score
pontos_acumulados = 0.0
for resultado in historico:
if resultado == 'V':
pontos_acumulados += 3.0
elif resultado == 'D':
pontos_acumulados += 0.0
elif resultado == 'E':
if mando == 'visitante':
pontos_acumulados += 2.0 if nivel_time < nivel_adversario else 3.0
else:
if nivel_time <= nivel_adversario:
pontos_acumulados += 2.0
elif nivel_time == 1 and nivel_adversario == 4:
pontos_acumulados += 0.0
else:
pontos_acumulados += 1.0
total_pontos_disputados = len(historico) * 3.0
return (pontos_acumulados / total_pontos_disputados) * 100.0
def calcular_bloco_tabela_dinamica(self, time: Dict[str, Any], nivel_adversario: int) -> float:
if nivel_adversario == 1:
multiplicador = 1.6
elif nivel_adversario == 2 or nivel_adversario == 3:
multiplicador = 1.0
else:
multiplicador = 0.0
oscilacao_momentanea = (time['posicao_real'] - time['posicao_momentanea']) * multiplicador
oscilacao_estrutural = (time['posicao_pre_campeonato'] - time['posicao_real']) * multiplicador
nota_bruta = self.base_score + oscilacao_momentanea + oscilacao_estrutural
return max(0.0, min(100.0, nota_bruta))
def calcular_im_final(self, dados_time: Dict[str, Any], adversario_nivel: int, mandante: bool) -> float:
def obter_nivel(p): return 1 if p<=5 else 2 if p<=10 else 3 if p<=15 else 4
nv_time = obter_nivel(dados_time['posicao_real'])
nv_pre_time = obter_nivel(dados_time['posicao_pre_campeonato'])
mando_str = 'mandante' if mandante else 'visitante'
nota_campo_3j = self.converter_historico_nota(dados_time['historico_mando_3'], mando_str, nv_time, adversario_nivel)
nota_campo_5j = self.converter_historico_nota(dados_time['historico_mando_5'], mando_str, nv_time, adversario_nivel)
bloco_campo = (nota_campo_3j * 0.65) + (nota_campo_5j * 0.35)
nota_geral_3j = self.converter_historico_nota(dados_time['historico_geral_3'], 'geral', nv_time, adversario_nivel)
nota_geral_5j = self.converter_historico_nota(dados_time['historico_geral_5'], 'geral', nv_time, adversario_nivel)
nota_geral_10j = self.converter_historico_nota(dados_time['historico_geral_10'], 'geral', nv_time, adversario_nivel)
bloco_geral = (nota_geral_3j * 0.50) + (nota_geral_5j * 0.35) + (nota_geral_10j * 0.15)
bloco_tabela = self.calcular_bloco_tabela_dinamica(dados_time, adversario_nivel)
ganhou_zebra = dados_time.get('venceu_ultimo_jogo_contra_elite', False)
bonus_zebra = 15.0 * self.fac if (ganhou_zebra and nv_pre_time == 4) else 0.0
im_final = (bloco_campo * 0.45) + (bloco_geral * 0.35) + (bloco_tabela * 0.20) + bonus_zebra
return round(max(0.0, min(100.0, im_final)), 2)
