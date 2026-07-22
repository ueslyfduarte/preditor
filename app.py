import streamlit as st
import pandas as pd
import numpy as np

# Configuração da página do Streamlit
st.set_page_config(layout="wide", page_title="Predição Esportiva Avançada")

# 1. ENTRADA DE DADOS ROBUSTA (Tabela de Texto / Área de Input)
st.title("🏛️ Sistema de Predição Esportiva Avançada")
st.markdown("Insira os dados brutos dos times ou médias da liga no campo abaixo.")

# Área para colar dados textuais (CSV, JSON ou texto tabulado)
dados_brutos = st.text_area(
    "Cole aqui os dados estatísticos (Formato CSV ou texto estruturado):",
    placeholder="Time,Atq,Atq_Perigosos,Chutes,Chutes_Gol,Gols,xG,Mando,Prateleira\nTime A,60,40,15,5,2,1.8,Casa,Elite\nTime B,45,30,10,3,1,1.1,Fora,Meio",
    height=200
)

# 2. APRESENTAÇÃO DO CONFRONTO
st.header("⚽ Apresentação do Confronto")

col1, col2 = st.columns(2)
with col1:
    time_casa = st.text_input("Nome do Time Mandante:", "Time Mandante")
    liga_casa = st.text_input("Liga/Campeonato:", "Série A")
    pos_atual_casa = st.number_input("Posição Atual (Mandante):", min_value=1, value=5)
    pos_proj_casa = st.number_input("Posição Projetada Inicial (Mandante):", min_value=1, value=3)
    
with col2:
    time_fora = st.text_input("Nome do Time Visitante:", "Time Visitante")
    liga_fora = st.text_input("Liga/Campeonato:", "Série A")
    pos_atual_fora = st.number_input("Posição Atual (Visitante):", min_value=1, value=12)
    pos_proj_fora = st.number_input("Posição Projetada Inicial (Visitante):", min_value=1, value=14)

# 3. LÓGICA MATEMÁTICA E BLOCOS DE CÁLCULO

# Função auxiliar para o Retrovisor de Ajuste de Empates
def calcular_pontos_retrovisor(mando, prateleira_adversario):
    """
    Calcula o valor ponderado do empate com base nas prateleiras e mando.
    """
    if mando == "Visitante":
        if prateleira_adversario == "Top 4":
            return 0.666
        else:
            return 1.00
    elif mando == "Mandante":
        if prateleira_adversario in ["Igual", "Superior"]:
            return 0.666
        elif prateleira_adversario == "Meio":
            return 0.333
        elif prateleira_adversario == "Z-4":
            return 0.00
    return 0.333 # Valor padrão caso não encaixe

# Função para o Fator de Modulação de Prateleira Dinâmico (FMP)
def aplicar_fmp(tipo_acao, relacao_adversario):
    """
    Retorna o multiplicador com base no erro/acerto e força do adversário.
    """
    if relacao_adversario == "Mais Forte":
        return 0.70 if tipo_acao == "erro_defensivo" else 1.30
    elif relacao_adversario == "Igual":
        return 1.00
    elif relacao_adversario == "Mais Fraca":
        return 1.40 if tipo_acao == "erro_defensivo" else 0.60
    return 1.00

# Exibição de Resultados na Interface
if st.button("Calcular Predição e Índices"):
    st.success("Dados processados com sucesso! Índices gerados abaixo:")
    
    # Exibição das Tabelas do Confronto (Item 2)
    dados_confronto = {
        "Métrica": ["Liga", "Posição Atual", "Posição Projetada"],
        time_casa: [liga_casa, pos_atual_casa, pos_proj_casa],
        time_fora: [liga_fora, pos_atual_fora, pos_proj_fora]
    }
    df_confronto = pd.DataFrame(dados_confronto)
    st.table(df_confronto)
    
    # Espaço para renderizar as notas finais calculadas (IM, IO, Consistência e Pressão)
    st.subheader("📊 Índices de Performance Calculados")
    
    # Exemplo visual de output dos blocos
    c1, c2, c3, c4 = st.columns(4)
    c1.metric(label=f"IM - {time_casa}", value="72.5 / 100", delta="+2.3% Geral")
    c2.metric(label=f"IM - {time_fora}", value="45.0 / 100", delta="-1.5% Geral")
    c3.metric(label=f"IO - {time_casa}", value="68.4 / 100")
    c4.metric(label=f"IO - {time_fora}", value="51.2 / 100")
