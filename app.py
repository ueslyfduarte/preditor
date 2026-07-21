import streamlit as st
import numpy as np

class EcossistemaPreditivoCompletoV75:
    def __init__(self):
        # Âncora Global - Médias padrões
        self.media_liga_padrao = {
            'gols': 1.45, 'xg': 1.50, 'chutes': 13.5, 'chutes_gol': 4.5,
            'atq_perigosos': 65.0
        }

    def _normalizar_min_max(self, valores, minimo, maximo):
        arr = np.array(valores)
        # Lógica de normalização
        return (arr - min_val) / (max_val - min_val) if max_val != min_val else np.zeros_like(arr) + 0.5

    def processar_bloco_unico(self, texto_bruto):
        # Lógica para processar texto bruto e converter para dicionário
        dados = {}
        # ... processamento
        return dados

    def calcular_ajuste_empates(self, historico_pontos, prateleiras_adversarios, condicao, prateleira_propria):
        # Lógica de ajuste de pontos baseada na condição e prateleira
        # ... cálculo
        return np.sum(pontos_ajustados)
    def gerar_insights_jogo(self, d, res):
        """Gera leituras descritivas e sugestões automáticas baseadas nos cálculos."""
        insights = []
        
        # 1. Análise de Ritmo / Tendência de Gols
        atq_total = d.get('atq_perigosos_casa', 65) + d.get('atq_perigosos_fora', 65)
        if atq_total > (self.media_liga_padrao['atq_perigosos'] * 2 * 1.15):
            insights.append("🔥 **Tendência de Ritmo Alto:** Ambas as equipes produzem volume ofensivo acima da média.")
        elif atq_total < (self.media_liga_padrao['atq_perigosos'] * 2 * 0.85):
            insights.append("🚧 **Tendência de Jogo Truncado:** Volume ofensivo projetado abaixo da média da liga.")
        else:
            insights.append("📊 **Ritmo Equilibrado:** O volume ofensivo projetado orbita a média padrão da competição.")

        # 2. Análise da Disparidade e Prateleiras
        if abs(res['disparidade']) >= 20:
            favorito = res['m_nome'] if res['disparidade'] > 0 else res['v_nome']
            insights.append(f"🎯 **Dominância Estatística:** Alta disparidade favorável ao **{favorito}**.")
        elif abs(res['disparidade']) <= 5:
            insights.append("⚖️ **Equilíbrio Extremo:** Margem de disparidade quase nula.")

        # 3. Análise dos 15 Minutos Finais
        if d.get('saldo_minuto_75_90_m', 0) > 0 and d.get('saldo_minuto_75_90_v', 0) < 0:
            insights.append(f"⏱️ **Pressão Final:** {res['m_nome']} costuma crescer no fim, {res['v_nome']} cede gols.")
        elif d.get('saldo_minuto_75_90_v', 0) > 0 and d.get('saldo_minuto_75_90_m', 0) < 0:
            insights.append(f"⏱️ **Pressão Final:** {res['v_nome']} costuma crescer no fim, {res['m_nome']} cede gols.")

        return insights

    def executar_calculo_completo(self, d):
        # [Cálculos de força e métricas consolidadas, omitidos para brevidade]
        # ... (processamento de força ofensiva/defensiva, consistência e momentum)
        
        # Simulação dos cálculos para preencher 'retorno_base'
        overall_m = 70.0; im_m = 65.0; irc_m = 60.0
        overall_v = 50.0; im_v = 55.0; irc_v = 50.0
        juncao_m = (overall_m + im_m + irc_m) / 3
        juncao_v = (overall_v + im_v + irc_v) / 3

        retorno_base = {
            'm_nome': d.get('nome_m', 'Mandante'), 'v_nome': d.get('nome_v', 'Visitante'),
            'disparidade': round(juncao_m - juncao_v, 2),
            # ... outros campos resumidos
        }
        
        # Injeta os insights antes de retornar
        retorno_base['insights'] = self.gerar_insights_jogo(d, retorno_base)
        return retorno_base
        # --- INICIALIZAÇÃO DA INTERFACE STREAMLIT ---
st.set_page_config(page_title="Preditor Rígido V6.7", layout="centered")

st.title("🚀 Sistema Preditivo Unificado V6.7")
st.caption("Fórmulas Inteiras com Inteligência de Insights Textuais")

# Instancia a classe principal
app = EcossistemaPreditivoCompletoV75()

# Caixa de texto para o usuário colar as estatísticas
texto_input = st.text_area("Cole as estatísticas da partida:", height=250)

if st.button("EXECUTAR ANÁLISE COMPLETA", use_container_width=True):
    if not texto_input.strip():
        st.error("Cole os dados estruturados do confronto antes de prosseguir.")
    else:
        try:
            # Processa e executa os cálculos
            dados_conferidos = app.processar_bloco_unico(texto_input)
            res = app.executar_calculo_completo(dados_conferidos)
            
            # --- NOVO BLOCO: ANÁLISE DESCRITIVA E SUGESTÕES ---
            st.markdown("### 🧠 INSIGHTS E LEITURA DE JOGO")
            if "insights" in res and res["insights"]:
                for insight in res["insights"]:
                    st.info(insight)
            else:
                st.warning("Dados insuficientes para gerar leituras avançadas de jogo.")
            
            st.markdown("---")
            
            # --- PAINEL INICIAL: POSICIONAMENTO ---
            st.markdown("### 🏛 *PAINEL INICIAL: POSICIONAMENTO E PROSPECÇÃO*")
            col_m, col_v = st.columns(2)
            with col_m: 
                st.markdown(f"**🏠 {res['m_nome']}**\n🏆 Prospecção do Mandante ativada.")
            with col_v: 
                st.markdown(f"**🚀 {res['v_nome']}**\n🏆 Prospecção do Visitante ativada.")
            
            st.markdown("---")
            
            # --- PASSO 4: CONFRONTO DIRETO E DISPARIDADE ---
            st.markdown("### 🎯 TELA DE CONFRONTO DIRETO E DISPARIDADE")
            
            disp = res['disparidade']
            if disp > 0:
                st.subheader(f"Diferença Crítica Final: +{disp} pontos a favor de {res['m_nome']}")
            else:
                st.subheader(f"Diferença Crítica Final: {disp} pontos a favor de {res['v_nome']}")
                
        except Exception as e: 
            st.error(f"Erro nas equações: {str(e)}. Verifique a formatação dos dados colados.")

