import numpy as np
from typing import Dict, Any

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
            if nivel_time < nivel_adversario: # Visitante era de prateleira superior (ex: Nível 1 vs Nível 3)
                return 2.0 # Vale 66.6% de uma vitória (2 pontos)
            return 3.0 # Igual ou inferior pontua cheio no empate fora (100% = 3 pontos)
            
        else: # Mandante
            if nivel_time == nivel_adversario or nivel_time < nivel_adversario:
                return 2.0 # Contra igual ou superior, vale 66.6% (2 pontos)
            elif nivel_time == 1 and nivel_adversario >= 4:
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
        
        # Aproveitamentos em formato decimal (0.0 a 1.0) para alimentar as notas do aplicativo
        aproveitamento_f5 = pontos_f5 / 15.0
        aproveitamento_f10 = pontos_f10 / 30.0
        aproveitamento_mando = pontos_mando / 15.0
        
        return {
            "posicao_real": dados['posicao_atual'],
            "nivel_real": nivel_atual,
            "nivel_dinamico_fmp": nivel_dinamico,
            "aproveitamento_f5_retro": round(aproveitamento_f5, 4),
            "aproveitamento_f10_retro": round(aproveitamento_f10, 4),
            "aproveitamento_mando_retro": round(aproveitamento_mando, 4)
        }
