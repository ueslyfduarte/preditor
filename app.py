import numpy as np
from typing import Dict, Any

class PainelInicialV28:
    """
    Módulo 1 do Método de Análise Esportiva V2.8.
    Gerencia e exibe estritamente: Posição Real, Posição Momentânea e Prospecção Teórica.
    """
    def __init__(self, total_times: int = 20):
        self.total_times = total_times

    def definir_nivel_posicao(self, posicao: int) -> str:
        """Define o nível/prateleira rigidamente a cada 5 posições (Regra das Prateleiras)"""
        if 1 <= posicao <= 5:   return "Elite"
        if 6 <= posicao <= 10:  return "Alto"
        if 11 <= posicao <= 15: return "Meio"
        return "Baixo"

    def processar_confronto(self, liga: Dict[str, Any], mandante: Dict[str, Any], visitante: Dict[str, Any]) -> Dict[str, Any]:
        """Consolida e formata os dados estruturais de posicionamento para o app"""
        
        # Puxando os níveis com base nas posições
        nivel_real_m = self.definir_nivel_posicao(mandante['posicao_real'])
        nivel_real_v = self.definir_nivel_posicao(visitante['posicao_real'])
        
        nivel_momentaneo_m = self.definir_nivel_posicao(mandante['posicao_momentanea'])
        nivel_momentaneo_v = self.definir_nivel_posicao(visitante['posicao_momentanea'])
        
        nivel_pre_m = self.definir_nivel_posicao(mandante['posicao_pre_campeonato'])
        nivel_pre_v = self.definir_nivel_posicao(visitante['posicao_pre_campeonato'])

        return {
            "liga": liga,
            "mandante": {
                "posicao_real": f"{mandante['posicao_real']}º ({nivel_real_m})",
                "posicao_momentanea": f"{mandante['posicao_momentanea']}º ({nivel_momentaneo_m})",
                "prospeccao_teorica": f"{mandante['posicao_pre_campeonato']}º ({nivel_pre_m})"
            },
            "visitante": {
                "posicao_real": f"{visitante['posicao_real']}º ({nivel_real_v})",
                "posicao_momentanea": f"{visitante['posicao_momentanea']}º ({nivel_momentaneo_v})",
                "prospeccao_teorica": f"{visitante['posicao_pre_campeonato']}º ({nivel_pre_v})"
            }
        }
import numpy as np
from typing import Dict, Any, List

class IndiceMomentoV28:
    """
    Módulo 3 do Método de Análise Esportiva V2.8.
    Calcula o Índice de Momento (IM) de 0 a 100 com base no histórico retrovencedor,
    tabela dinâmica tripla e bônus de zebra automatizado.
    """
    def __init__(self, fac: float):
        self.fac = fac
        self.base_score = 50.0

    def converter_historico_nota(self, historico: List[str], mando: str, nivel_time: int, nivel_adversario: int) -> float:
        """
        Converte a lista de caracteres ['V', 'E', 'D'] em nota 0-100 
        utilizando as regras de peso do Retrovencedor de Empates (Passo 3).
        """
        if not historico:
            return self.base_score
            
        pontos_acumulados = 0.0
        for resultado in historico:
            if resultado == 'V':
                pontos_acumulados += 3.0
            elif resultado == 'D':
                pontos_acumulados += 0.0
            elif resultado == 'E':
                # Regra do Passo 3 de empates ponderados
                if mando == 'visitante':
                    pontos_acumulados += 2.0 if nivel_time < nivel_adversario else 3.0
                else: # Mandante ou Geral
                    if nivel_time <= nivel_adversario:
                        pontos_acumulados += 2.0
                    elif nivel_time == 1 and nivel_adversario == 4:
                        pontos_acumulados += 0.0
                    else:
                        pontos_acumulados += 1.0
                        
        total_pontos_disputados = len(historico) * 3.0
        return (pontos_acumulados / total_pontos_disputados) * 100.0

    def calcular_bloco_tabela_dinamica(self, time: Dict[str, Any], nivel_adversario: int) -> float:
        """
        Executa a fórmula expandida do Item 2, cruzando Posição Real, 
        Momentânea e Prospecção Pré-Campeonato com travas rígidas de segurança.
        """
        # Define o multiplicador com base na prateleira do adversário
        if nivel_adversario == 1:
            multiplicador = 1.6
        elif nivel_adversario == 2 or nivel_adversario == 3:
            multiplicador = 1.0
        else:
            multiplicador = 0.0  # Cenário de amplo favoritismo contra nível Baixo

        # Cálculo das forças de oscilação do Item 2
        oscilacao_momentanea = (time['posicao_real'] - time['posicao_momentanea']) * multiplicador
        oscilacao_estrutural = (time['posicao_pre_campeonato'] - time['posicao_real']) * multiplicador
        
        # Junta os três pilares na base original de 50 pontos
        nota_bruta = self.base_score + oscilacao_momentanea + oscilacao_estrutural
        
        # Trava rígida de segurança (Garante intervalo 0 a 100)
        return max(0.0, min(100.0, nota_bruta))

    def calcular_im_final(self, dados_time: Dict[str, Any], adversario_nivel: int, mandante: bool) -> float:
        """Calcula o IM final aplicando todos os pesos e o bônus de zebra automatizado"""
        
        # Identificação dos níveis numéricos (1 a 4) para o cálculo retrovencedor
        def obter_nivel(p): return 1 if p<=5 else 2 if p<=10 else 3 if p<=15 else 4
        nv_time = obter_nivel(dados_time['posicao_real'])
        nv_pre_time = obter_nivel(dados_time['posicao_pre_campeonato'])
        
        # Bloco 1: Condição de Campo (Peso 45%)
        mando_str = 'mandante' if mandante else 'visitante'
        nota_campo_3j = self.converter_historico_nota(dados_time['historico_mando_3'], mando_str, nv_time, adversario_nivel)
        nota_campo_5j = self.converter_historico_nota(dados_time['historico_mando_5'], mando_str, nv_time, adversario_nivel)
        bloco_campo = (nota_campo_3j * 0.65) + (nota_campo_5j * 0.35)
        
        # Bloco 2: Geral (Peso 35%)
        nota_geral_3j = self.converter_historico_nota(dados_time['historico_geral_3'], 'geral', nv_time, adversario_nivel)
        nota_geral_5j = self.converter_historico_nota(dados_time['historico_geral_5'], 'geral', nv_time, adversario_nivel)
        nota_geral_10j = self.converter_historico_nota(dados_time['historico_geral_10'], 'geral', nv_time, adversario_nivel)
        bloco_geral = (nota_geral_3j * 0.50) + (nota_geral_5j * 0.35) + (nota_geral_10j * 0.15)
        
        # Bloco 3: Tabela Dinâmica (Peso 20%)
        bloco_tabela = self.calcular_bloco_tabela_dinamica(dados_time, adversario_nivel)
        
        # Bloco 4: Bônus de Zebra Histórica Automatizado (Item 3)
        ganhou_zebra = dados_time.get('venceu_ultimo_jogo_contra_elite', False)
        # Só ativa se o time for estruturalmente do nível 4 (Baixo) e ganhou de um Elite
        if ganhou_zebra and nv_pre_time == 4:
            bonus_zebra = 15.0 * self.fac
        else:
            bonus_zebra = 0.0

        # Equação unificada do Índice de Momento original
        im_final = (bloco_campo * 0.45) + (bloco_geral * 0.35) + (bloco_tabela * 0.20) + bonus_zebra
        return round(max(0.0, min(100.0, im_final)), 2)
        import numpy as np
from typing import Dict, Any, List

class MaquinaOverallV28:
    """
    Módulo 2 do Método de Análise Esportiva V2.8.
    Calcula as notas de Ataque, Defesa, Consistência e Resistência à Pressão (0-100).
    """
    def __init__(self):
        self.base_score = 50.0

    def calcular_fmp(self, nivel_time: int, nivel_adversario: int) -> Dict[str, float]:
        """Aplica o Fator de Modulação de Prateleira Dinâmico baseado em 4 Níveis"""
        if nivel_time < nivel_adversario:   # Mais Forte (ex: Nível 1 vs Nível 3)
            return {"erro_defensivo": 1.40, "acerto_ofensivo": 0.60}
        elif nivel_time > nivel_adversario: # Mais Fraco (ex: Nível 3 vs Nível 1)
            return {"erro_defensivo": 0.70, "acerto_ofensivo": 1.30}
        else:                               # Prateleira Igual
            return {"erro_defensivo": 1.00, "acerto_ofensivo": 1.00}

    def calcular_bloco_ataque(self, time: Dict[str, float], liga: Dict[str, float], fmp: Dict[str, float]) -> Dict[str, float]:
        """Executa o Passo 1-A: Bloco de Ataque"""
        # 1. FVO (Força de Volume Ofensivo)
        proporcoes_fvo = [
            time['ataques'] / max(0.0001, liga['ataques']),
            time['ataques_perigosos'] / max(0.0001, liga['ataques_perigosos']),
            time['chutes'] / max(0.0001, liga['chutes']),
            time['chutes_gol'] / max(0.0001, liga['chutes_gol']),
            time['gols'] / max(0.0001, liga['gols']),
            time['xg'] / max(0.0001, liga['xg'])
        ]
        fvo = np.mean(proporcoes_fvo) * self.base_score * fmp['acerto_ofensivo']

        # 2. FCO (Fator de Conversão) com trava de divisão por zero
        chutes_por_gol_liga = liga['chutes_gol'] / max(0.0001, liga['gols'])
        chutes_por_gol_time = time['chutes_gol'] / max(0.0001, time['gols'])
        fco = (chutes_por_gol_liga / max(0.0001, chutes_por_gol_time)) * self.base_score * fmp['acerto_ofensivo']

        nota_ataque = min(100.0, max(0.0, (fvo * 0.60) + (fco * 0.40)))
        return {"FVO": round(fvo, 2), "FCO": round(fco, 2), "Nota_Ataque": round(nota_ataque, 2)}

    def calcular_bloco_defesa(self, time: Dict[str, float], liga: Dict[str, float], fmp: Dict[str, float]) -> Dict[str, float]:
        """Executa o Passo 1-B: Bloco de Defesa"""
        # 1. FRD (Força de Resiliência Defensiva)
        proporcoes_frd = [
            liga['ataques_sofridos'] / max(0.0001, time['ataques_sofridos']),
            liga['ataques_perigosos_sofridos'] / max(0.0001, time['ataques_perigosos_sofridos']),
            liga['chutes_sofridos'] / max(0.0001, time['chutes_sofridos']),
            liga['chutes_gol_sofridos'] / max(0.0001, time['chutes_gol_sofridos']),
            liga['gols_sofridos'] / max(0.0001, time['gols_sofridos']),
            liga['xg_cedido'] / max(0.0001, time['xg_cedido'])
        ]
        frd = (np.mean(proporcoes_frd) * self.base_score) / fmp['erro_defensivo']

        # 2. FCD (Fator de Conversão Defensiva)
        chutes_sofridos_por_gol_time = time['chutes_gol_sofridos'] / max(0.0001, time['gols_sofridos'])
        chutes_sofridos_por_gol_liga = liga['chutes_gol_sofridos'] / max(0.0001, liga['gols_sofridos'])
        fcd = ((chutes_sofridos_por_gol_time / max(0.0001, chutes_sofridos_por_gol_liga)) * self.base_score) / fmp['erro_defensivo']

        nota_defesa = min(100.0, max(0.0, (frd * 0.60) + (fcd * 0.40)))
        return {"FRD": round(frd, 2), "FCD": round(fcd, 2), "Nota_Defesa": round(nota_defesa, 2)}

    def calcular_bloco_consistencia(self, historico_jogos_proporcoes: List[List[float]], im_max: float, im_min: float) -> Dict[str, float]:
        """Executa o Passo 1-C: Bloco de Consistência normalizado"""
        # historico_jogos_proporcoes: lista contendo a proporção de cada variável em relação à liga jogo a jogo
        desvios_por_variavel = [np.std(jogo) for jogo in historico_jogos_proporcoes]
        std_medio = np.mean(desvios_por_variavel)
        
        # Multiplicador 100 escalona o desvio proporcional para a perda de pontos de 0 a 100
        fdm = max(0.0, min(100.0, 100.0 - (std_medio * 100.0)))
        ier = max(0.0, min(100.0, 100.0 - (im_max - im_min)))
        
        nota_consistencia = (fdm * 0.60) + (ier * 0.40)
        return {"FDM": round(fdm, 2), "IER": round(ier, 2), "Nota_Consistencia": round(nota_consistencia, 2)}

    def calcular_bloco_resistencia(self, time_pressao: Dict[str, float], liga_pressao: Dict[str, float]) -> Dict[str, float]:
        """Executa o Passo 1-D: Bloco de Resistência à Pressão com as novas fórmulas"""
        # 1. FCD Volume vs xG Cedido
        fcd_vol = (liga_pressao['xg_cedido'] / max(0.0001, time_pressao['xg_cedido']))
        fcd_chu = (liga_pressao['chutes_sofridos'] / max(0.0001, time_pressao['chutes_sofridos']))
        fcd_nota = min(100.0, (fcd_vol * fcd_chu) * self.base_score)

        # 2. EGZ Taxa de Conversão Defensiva Cedida
        time_chutes_por_gol = time_pressao['chutes_gol_sofridos'] / max(0.0001, time_pressao['gols_sofridos'])
        liga_chutes_por_gol = liga_pressao['chutes_gol_sofridos'] / max(0.0001, liga_pressao['gols_sofridos'])
        egz_nota = min(100.0, (time_chutes_por_gol / max(0.0001, liga_chutes_por_gol)) * self.base_score)

        # 3. FRI % Pontos Recuperados após sair perdendo
        fri_nota = (time_pressao['pontos_recuperados'] / max(0.0001, time_pressao['pontos_disputados_atras'])) * 100.0
        fri_nota = min(100.0, fri_nota)

        # 4. FZC Saldo de Gols no Crunch Time (75' a 90'+)
        saldo_final_jogo = time_pressao['gols_marcados_fim'] - time_pressao['gols_sofridos_fim']
        fzc_nota = min(100.0, max(0.0, 50.0 + (saldo_final_jogo * 10.0)))

        nota_resistencia = (fzc_nota * 0.30) + (egz_nota * 0.30) + (fri_nota * 0.20) + (fcd_nota * 0.20)
        return {"Nota_Resistencia": round(nota_resistencia, 2)}

    def calcular_overall_final(self, n_atq: float, n_def: float, n_con: float, n_res: float) -> float:
        """Entrega a Nota Final Unificada do Overall Geral (Escala 0-100)"""
        overall = (n_con * 0.35) + (n_atq * 0.25) + (n_def * 0.25) + (n_res * 0.15)
        return round(overall, 2)
        import numpy as np
from typing import Dict, Any, List

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

    def modular_historico_ofensivo(self, jogos_time: List[Dict[str, float]], medias_liga: Dict[str, float], nivel_time: int) -> List[Dict[str, float]]:
        """Aplica o FMP rodada a rodada em cada jogo passado para o bloco de ataque"""
        jogos_modulados = []
        for jogo in jogos_time:
            fmp = self.obter_multiplicadores_fmp(nivel_time, jogo['nivel_adversario_dia'])
            # Modula os acertos ofensivos do dia
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

    def modular_historico_defensivo(self, jogos_time: List[Dict[str, float]], medias_liga: Dict[str, float], nivel_time: int) -> List[Dict[str, float]]:
        """Aplica o FMP rodada a rodada em cada jogo passado para o bloco de defesa"""
        jogos_modulados = []
        for jogo in jogos_time:
            fmp = self.obter_multiplicadores_fmp(nivel_time, jogo['nivel_adversario_dia'])
            # O erro defensivo divide a nota (ou seja, se o multiplicador for 1.40, a resiliência cai)
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

        # Extrai as médias já corrigidas do período
        med_time = {k: np.mean([j[k] for j in jogos_modulados]) for k in jogos_modulados[0].keys()}

        # 1. FVO (Força de Volume Ofensivo)
        proporcoes_fvo = [
            med_time['ataques'] / max(0.0001, liga['ataques']),
            med_time['ataques_perigosos'] / max(0.0001, liga['ataques_perigosos']),
            med_time['chutes'] / max(0.0001, liga['chutes']),
            med_time['chutes_gol'] / max(0.0001, liga['chutes_gol']),
            med_time['gols'] / max(0.0001, liga['gols']),
            med_time['xg'] / max(0.0001, liga['xg'])
        ]
        fvo = np.mean(proporcoes_fvo) * self.base_score

        # 2. FCO (Fator de Conversão) com trava de segurança contra divisão por zero
        chutes_por_gol_liga = liga['chutes_gol'] / max(0.0001, liga['gols'])
        chutes_por_gol_time = med_time['chutes_gol'] / max(0.0001, med_time['gols'])
        fco = (chutes_por_gol_liga / max(0.0001, chutes_por_gol_time)) * self.base_score

        nota_ataque = min(100.0, max(0.0, (fvo * 0.60) + (fco * 0.40)))
        return {"FVO": round(fvo, 2), "FCO": round(fco, 2), "Nota_Ataque": round(nota_ataque, 2)}

    def calcular_bloco_defesa(self, jogos_modulados: List[Dict[str, float]], liga: Dict[str, float]) -> Dict[str, float]:
        """Executa o Passo 1-B com os dados históricos já limpos pelo FMP"""
        if not jogos_modulados:
            return {"FRD": self.base_score, "FCD": self.base_score, "Nota_Defesa": self.base_score}

        med_time = {k: np.mean([j[k] for j in jogos_modulados]) for k in jogos_modulados[0].keys()}

        # 1. FRD (Força de Resiliência Defensiva) com inversão contra a liga
        proporcoes_frd = [
            liga['ataques_sofridos'] / max(0.0001, med_time['ataques_sofridos']),
            liga['ataques_perigosos_sofridos'] / max(0.0001, med_time['ataques_perigosos_sofridos']),
            liga['chutes_sofridos'] / max(0.0001, med_time['chutes_sofridos']),
            liga['chutes_gol_sofridos'] / max(0.0001, med_time['chutes_gol_sofridos']),
            liga['gols_sofridos'] / max(0.0001, med_time['gols_sofridos']),
            liga['xg_cedido'] / max(0.0001, med_time['xg_cedido'])
        ]
        frd = np.mean(proporcoes_frd) * self.base_score

        # 2. FCD (Fator de Conversão Defensiva)
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
            # Consolida o ecossistema de proporções daquela rodada específica em relação à liga
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


