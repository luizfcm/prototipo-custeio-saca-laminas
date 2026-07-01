ATIVIDADES_PRE = [
    ("reunioes_equipe_saude", "Reuniões com equipe de saúde"),
    ("analise_dfam",          "Análise de DfAM (Requisitos, Modelagem, Fatiamento)"),
]

ATIVIDADES_POS = [
    ("validacao_laboratorio", "Validação no laboratório"),
    ("validacao_usuario",     "Validação com usuário / hospital"),
    ("documentacao_versao",   "Documentação da versão"),
]


def calcular_custo_desenvolvimento(
    tempos_horas: dict,
    custo_operador_hora: float,
    custo_indireto_hora: float,
    considerar_indireto: bool = True,
) -> dict:
    taxa_indireto = custo_indireto_hora if considerar_indireto else 0.0

    atividades_resultado = {}
    tempo_total = 0.0

    for chave, label in ATIVIDADES_PRE + ATIVIDADES_POS:
        horas = tempos_horas.get(chave, 0.0)
        custo = horas * (custo_operador_hora + taxa_indireto)
        atividades_resultado[chave] = {
            "label": label,
            "horas": horas,
            "custo": round(custo, 2),
        }
        tempo_total += horas

    custo_mao_obra_total = tempo_total * custo_operador_hora
    custo_indireto_total = tempo_total * taxa_indireto
    custo_total = custo_mao_obra_total + custo_indireto_total

    return {
        "custo_total":        round(custo_total, 2),
        "custo_mao_obra":     round(custo_mao_obra_total, 2),
        "custo_indireto":     round(custo_indireto_total, 2),
        "tempo_total_horas":  round(tempo_total, 2),
        "custo_operador_hora": custo_operador_hora,
        "atividades":         atividades_resultado,
    }
