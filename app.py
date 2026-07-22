import requests

# =========================================================================
# CONFIGURAÇÃO DE ACESSO (Substitua quando tiver sua chave real)
# =========================================================================
API_KEY = "SUA_CHAVE_AQUI"  # Cadastre-se grátis em api-sports.io para obter
USAR_MOCK_PARA_TESTE = True  # Mude para False para usar dados reais da internet

# ID 71 corresponde ao Campeonato Brasileiro Série A na API-Football
ID_CAMPEONATO = 71
ANO_TEMPORADA = 2026


# =========================================================================
# REGRAS DE NEGÓCIO DO SEU MÉTODO
# =========================================================================
def calcular_escalao(posicao, rodada):
    """Regra do Escalão: Oculta até a 3ª rodada, depois classifica."""
    if rodada < 4:
        return "Anulado (Apenas após a 3ª rodada)"

    if 1 <= posicao <= 3:
        return "Elite"
    elif 4 <= posicao <= 6:
        return "Alto"
    elif 7 <= posicao <= 12:
        return "Médio"
    elif 13 <= posicao <= 16:
        return "Baixo"
    elif posicao >= 17:
        return "Crítico"
    return "Indisponível"


# =========================================================================
# FUNÇÕES DE BUSCA DE DADOS (API OU SIMULADOR)
# =========================================================================
def buscar_dados_clube(nome_clube, rodada_atual):
    """Busca a classificação e as estatísticas do clube informando apenas o nome."""
    if USAR_MOCK_PARA_TESTE:
        return obter_dados_simulados(nome_clube, rodada_atual)

    # Configuração dos cabeçalhos da API real
    headers = {
        "x-rapidapi-host": "v3.football.api-sports.io",
        "x-rapidapi-key": API_KEY,
    }

    try:
        # --- 1. BUSCANDO CLASSIFICAÇÃO (TABELA ANALÍTICA) ---
        url_tabela = "https://api-sports.io"
        params_tabela = {"league": ID_CAMPEONATO, "season": ANO_TEMPORADA}
        res_tabela = requests.get(url_tabela, headers=headers, params=params_tabela)
        dados_tabela = res_tabela.json()

        tabela_times = dados_tabela["response"][0]["league"]["standings"][0]

        id_time = None
        dados_finais = {}

        for linha in tabela_times:
            if nome_clube.lower() in linha["team"]["name"].lower():
                id_time = linha["team"]["id"]
                dados_finais["Nome"] = linha["team"]["name"]
                dados_finais["P_Atual"] = linha["rank"]
                # P_Momento e P_P_I simulados por limitações de histórico em tempo real da API básica
                dados_finais["P_Momento"] = max(1, linha["rank"] - 1)
                dados_finais["P_P_I"] = 5
                break

        if not id_time:
            return f"Erro: Clube '{nome_clube}' não encontrado no campeonato."

        # --- 2. BUSCANDO MÉDIAS (PAINEL ESTATÍSTICO SIMPLES) ---
        # Define se busca temporada passada ou atual com base na rodada
        temporada_alvo = (
            ANO_TEMPORADA - 1 if rodada_atual < 3 else ANO_TEMPORADA
        )
        dados_finais["Fonte_Dados"] = (
            "Temporada Passada" if rodada_atual < 3 else "Campeonato Atual"
        )

        url_stats = "https://api-sports.io"
        params_stats = {
            "league": ID_CAMPEONATO,
            "season": temporada_alvo,
            "team": id_time,
        }
        res_stats = requests.get(url_stats, headers=headers, params=params_stats)
        dados_stats = res_stats.json()["response"]

        # Extração de gols e histórico recente
        gols_marcados = dados_stats["goals"]["for"]["total"]["total"]
        jogos_disputados = dados_stats["fixtures"]["played"]["total"]

        # Como a API gratuita agrupa os dados de gols e escanteios de forma geral,
        # calculamos a média por jogo para o seu painel simples:
        dados_finais["Media_Gols"] = (
            round(gols_marcados / jogos_disputados, 2)
            if jogos_disputados > 0
            else "Sem dados"
        )
        dados_finais["VED_10"] = dados_stats["form"][-10:] if dados_stats["form"] else "N/A"

        return dados_finais

    except Exception as e:
        return f"Erro na conexão com a API: {e}"


# =========================================================================
# INTERFACE DE EXIBIÇÃO NO TERMINAL
# =========================================================================
def executar_metodo(time_a, time_b, rodada_atual):
    print(f"\n" + "=" * 60)
    print(
        f" EXECUÇÃO DO MÉTODO: {time_a.upper()} x {time_b.upper()} (RODADA {rodada_atual})"
    )
    print("=" * 60)

    for time_nome, rotulo in [(time_a, "TIME A"), (time_b, "TIME B")]:
        resultado = buscar_dados_clube(time_nome, rodada_atual)

        if isinstance(resultado, str):
            print(f"\n[{rotulo}] {resultado}")
            continue

        escalao_calculado = calcular_escalao(resultado["P_Atual"], rodada_atual)

        print(f"\n▶ {rotulo}: {resultado['Nome']}")
        print(f"  [Tabela Analítica]")
        print(f"    - P. Atual: {resultado['P_Atual']}º")
        print(f"    - P. Momento: {resultado['P_Momento']}º")
        print(f"    - P.P.I: {resultado['P_P_I']}º")
        print(f"    - Escalão: {escalao_calculado}")

        print(f"  [Painel Estatístico Simples] (Fonte: {resultado['Fonte_Dados']})")
        print(f"    - Últimos Jogos (V.E.D): {resultado['VED_10']}")
        print(f"    - Média Gols/Jogo: {resultado['Media_Gols']}")
        # Caso algum dado venha vazio da API, tratamos como exceção (não exibe)
        if "Media_Escanteios" in resultado:
            print(f"    - Média Escanteios: {resultado['Media_Escanteios']}")


# =========================================================================
# SIMULADOR LOCAL (Para você testar agora mesmo sem a chave da API)
# =========================================================================
def obter_dados_simulados(nome_clube, rodada_atual):
    fonte = "Temporada Passada" if rodada_atual < 3 else "Campeonato Atual"
    if "palm" in nome_clube.lower():
        return {
            "Nome": "Palmeiras",
            "P_Atual": 2,
            "P_Momento": 1,
            "P_P_I": 2,
            "Fonte_Dados": fonte,
            "VED_10": "VVVEVVVDVV",
            "Media_Gols": 1.85,
            "Media_Escanteios": 10.4,
        }
    else:
        return {
            "Nome": "Flamengo",
            "P_Atual": 5,
            "P_Momento": 6,
            "P_P_I": 1,
            "Fonte_Dados": fonte,
            "VED_10": "VVEVDVVDEV",
            "Media_Gols": 1.60,
            "Media_Escanteios": 11.1,
        }


# =========================================================================
# TESTANDO O SEU MODELO
# =========================================================================
# Teste na Rodada 2: Deve anular o escalão e usar histórico da temporada passada
executar_metodo("Palmeiras", "Flamengo", rodada_atual=2)

# Teste na Rodada 5: Deve ativar o escalão e mudar a fonte para o campeonato atual
executar_metodo("Palmeiras", "Flamengo", rodada_atual=5)
