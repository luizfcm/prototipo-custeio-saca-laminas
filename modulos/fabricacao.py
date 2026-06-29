

def calcular_custo_fabricacao(
    tempo_impressao_A_min: float,
    tempo_impressao_B_min: float,
    massa_A_g: float,
    massa_B_g: float,
    pecas_por_lote: int,
    custo_operador_hora: float,
    custo_aquisicao: float,
    custo_manutencao: float,
    valor_residual: float,
    vida_util_horas: float,
    custo_filamento_grama: float,
    custo_indireto_hora: float,
    tempo_setup_min: float,
    tempo_pos_min: float,
    rodadas_setup: int = 2,
) -> dict:
    taxa_maquina = (custo_aquisicao + custo_manutencao - valor_residual) / vida_util_horas

    tempo_total_horas = (tempo_impressao_A_min + tempo_impressao_B_min) / 60
    custo_maquina = (taxa_maquina * tempo_total_horas) / pecas_por_lote

    massa_total = massa_A_g + massa_B_g
    custo_material = (massa_total / pecas_por_lote) * custo_filamento_grama

    taxa_combinada = custo_operador_hora + custo_indireto_hora
    custo_setup = (rodadas_setup * (tempo_setup_min / 60) * taxa_combinada) / pecas_por_lote
    custo_pos = (tempo_pos_min / 60) * taxa_combinada

    # Operador supervisiona 10% do tempo de impressão; taxa efetiva = custo_operador/10
    # pois a supervisão é passiva (Concli, 2023 / Kelly, 2025)
    custo_mao_obra = (tempo_total_horas * 0.10 / pecas_por_lote) * (custo_operador_hora / 10)

    custo_indireto = (custo_indireto_hora * tempo_total_horas) / pecas_por_lote

    custo_total = (
        custo_material
        + custo_maquina
        + custo_setup
        + custo_pos
        + custo_mao_obra
        + custo_indireto
    )

    return {
        "custo_total": round(custo_total, 2),
        "custo_material": round(custo_material, 2),
        "custo_maquina": round(custo_maquina, 2),
        "custo_setup": round(custo_setup, 2),
        "custo_pos_processamento": round(custo_pos, 2),
        "custo_mao_obra": round(custo_mao_obra, 2),
        "custo_indireto": round(custo_indireto, 2),
        "lote": pecas_por_lote,
        "custo_operador_hora": custo_operador_hora,
    }


def calcular_custo_unitario(
    tempo_total_min: float,
    massa_total_g: float,
    custo_operador_hora: float,
    custo_aquisicao: float,
    custo_manutencao: float,
    valor_residual: float,
    vida_util_horas: float,
    custo_filamento_grama: float,
    custo_indireto_hora: float,
    tempo_setup_min: float,
    tempo_pos_min: float,
) -> dict:
    """A e B impressos juntos na mesma bandeja — 1 peça, 1 setup, sem rateio de lote."""
    taxa_maquina = (custo_aquisicao + custo_manutencao - valor_residual) / vida_util_horas
    tempo_total_horas = tempo_total_min / 60

    custo_maquina = taxa_maquina * tempo_total_horas
    custo_material = massa_total_g * custo_filamento_grama

    taxa_combinada = custo_operador_hora + custo_indireto_hora
    custo_setup = (tempo_setup_min / 60) * taxa_combinada  # 1 rodada, sem rateio
    custo_pos = (tempo_pos_min / 60) * taxa_combinada

    custo_mao_obra = (tempo_total_horas * 0.10) * (custo_operador_hora / 10)
    custo_indireto = custo_indireto_hora * tempo_total_horas

    custo_total = (
        custo_material
        + custo_maquina
        + custo_setup
        + custo_pos
        + custo_mao_obra
        + custo_indireto
    )

    return {
        "custo_total": round(custo_total, 2),
        "custo_material": round(custo_material, 2),
        "custo_maquina": round(custo_maquina, 2),
        "custo_setup": round(custo_setup, 2),
        "custo_pos_processamento": round(custo_pos, 2),
        "custo_mao_obra": round(custo_mao_obra, 2),
        "custo_indireto": round(custo_indireto, 2),
        "lote": 1,
        "custo_operador_hora": custo_operador_hora,
    }
