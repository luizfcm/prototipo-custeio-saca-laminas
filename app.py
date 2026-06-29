import os

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from modulos.comparacao import (
    carregar_versoes,
    construir_dataframe,
    grafico_custo_por_versao,
    grafico_fab_por_versao,
    grafico_dev_por_versao,
)
from modulos.desenvolvimento import (
    ATIVIDADES_PRE,
    ATIVIDADES_POS,
    calcular_custo_desenvolvimento,
)
from modulos.fabricacao import calcular_custo_fabricacao, calcular_custo_unitario

CAMINHO_JSON = os.path.join(os.path.dirname(__file__), "dados", "versoes.json")

LAB = {
    "custo_aquisicao":      5500.00,
    "custo_manutencao":     300.00,
    "valor_residual":       800.00,
    "vida_util_horas":      14112.0,
    "custo_filamento_grama": 0.14,
    "custo_indireto_hora":  11.90,
    "tempo_setup_min":      10.0,
    "tempo_pos_min":        5.0,
}

PERFIS_OP = {
    "Consultor técnico / gestor — R$ 47,62/h (Cenário 1, Kelly 2025)": 47.62,
    "Operador graduando — R$ 23,21/h (Cenário 2, Kelly 2025)":         23.21,
    "Combinação dos dois — R$ 31,70/h (Cenário 3, Kelly 2025)":        31.70,
    "Personalizado": None,
}

PERFIS_NOME_CURTO = {
    "Consultor técnico / gestor — R$ 47,62/h (Cenário 1, Kelly 2025)": "Consultor (R$ 47,62/h)",
    "Operador graduando — R$ 23,21/h (Cenário 2, Kelly 2025)":         "Graduando (R$ 23,21/h)",
    "Combinação dos dois — R$ 31,70/h (Cenário 3, Kelly 2025)":        "Combinação (R$ 31,70/h)",
}

# ── Carregar versões ──────────────────────────────────────────────────────────
_versoes_json  = carregar_versoes(CAMINHO_JSON)
_nomes_versoes = [v["nome"] for v in _versoes_json]
_versoes_dict  = {v["nome"]: v for v in _versoes_json}

# ── Session state ─────────────────────────────────────────────────────────────
if "comparacoes" not in st.session_state:
    st.session_state["comparacoes"] = []

st.set_page_config(
    page_title="Custeio — Saca-Lâminas | LAB/UnB",
    page_icon="🔬",
    layout="wide",
)


# ══════════════════════════════════════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════════════════════════════════════

def _selecionar_operador(key_suffix: str) -> tuple[float, str]:
    perfil_key = st.selectbox(
        "Perfil do operador",
        options=list(PERFIS_OP.keys()),
        key=f"perfil_{key_suffix}",
    )
    if PERFIS_OP[perfil_key] is None:
        custo = st.number_input(
            "Custo do operador (R$/h)", value=47.62, min_value=0.0,
            step=0.01, format="%.2f", key=f"op_custom_{key_suffix}",
        )
        nome = f"Personalizado (R$ {custo:.2f}/h)"
    else:
        custo = PERFIS_OP[perfil_key]
        nome  = PERFIS_NOME_CURTO[perfil_key]
        st.metric("Custo do operador (R$/h)", f"R$ {custo:.2f}")
    return custo, nome


def _calcular_fab(v: dict, custo_op: float, modo: str) -> dict:
    dt = v["dados_tecnicos"]
    if modo == "Lote":
        if v["tipo"] == "duas_partes":
            return calcular_custo_fabricacao(
                tempo_impressao_A_min=dt["lote"]["parte_a"]["tempo_min"],
                tempo_impressao_B_min=dt["lote"]["parte_b"]["tempo_min"],
                massa_A_g=dt["lote"]["parte_a"]["massa_g"],
                massa_B_g=dt["lote"]["parte_b"]["massa_g"],
                pecas_por_lote=dt["lote"]["num_pecas"],
                custo_operador_hora=custo_op,
                rodadas_setup=2,
                **LAB,
            )
        else:
            return calcular_custo_fabricacao(
                tempo_impressao_A_min=dt["lote"]["tempo_total_min"],
                tempo_impressao_B_min=0.0,
                massa_A_g=dt["lote"]["massa_total_g"],
                massa_B_g=0.0,
                pecas_por_lote=dt["lote"]["num_pecas"],
                custo_operador_hora=custo_op,
                rodadas_setup=1,
                **LAB,
            )
    else:
        return calcular_custo_unitario(
            tempo_total_min=dt["unitario"]["tempo_min"],
            massa_total_g=dt["unitario"]["massa_g"],
            custo_operador_hora=custo_op,
            **LAB,
        )


def _calcular_dev(v: dict, custo_op: float) -> dict:
    atividades_json = v["desenvolvimento"]["atividades"]
    tempos = {k: a["horas"] for k, a in atividades_json.items()}
    return calcular_custo_desenvolvimento(
        tempos_horas=tempos,
        custo_operador_hora=custo_op,
        custo_indireto_hora=LAB["custo_indireto_hora"],
    )


def _hex_lighter(hex_color: str, factor: float) -> str:
    hex_color = hex_color.lstrip("#")
    r, g, b = (int(hex_color[i:i + 2], 16) for i in (0, 2, 4))
    return f"#{int(r+(255-r)*factor):02X}{int(g+(255-g)*factor):02X}{int(b+(255-b)*factor):02X}"


def _donut(r: dict, titulo: str, cor: str) -> go.Figure:
    comp = {
        "Material":    r["custo_material"],
        "Máquina":     r["custo_maquina"],
        "Setup":       r["custo_setup"],
        "Pós-proc.":   r["custo_pos_processamento"],
        "Mão de obra": r["custo_mao_obra"],
        "Indireto":    r["custo_indireto"],
    }
    shades = [cor] + [_hex_lighter(cor, f) for f in (0.3, 0.5, 0.65, 0.75, 0.85)]
    fig = go.Figure(go.Pie(
        labels=list(comp.keys()), values=list(comp.values()),
        hole=0.45, marker_colors=shades, textinfo="percent+label",
    ))
    fig.update_layout(
        title=titulo, showlegend=False,
        margin=dict(t=40, b=0, l=0, r=0),
        template="plotly_white",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )
    return fig


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.caption("Laboratório Aberto de Brasília — UnB")
    with st.expander("Parâmetros do laboratório (LAB/UnB)", expanded=False):
        st.caption("Fonte: Kelly (2025) / LAB/UnB.")
        st.subheader("Máquina (Prusa MK3S)")
        st.metric("Custo de aquisição",  "R$ 5.500,00")
        st.metric("Custo de manutenção", "R$ 300,00")
        st.metric("Valor residual",      "R$ 800,00")
        st.metric("Vida útil",           "14.112 h  (7 anos)")
        st.subheader("Material")
        st.metric("Custo do filamento PLA", "R$ 0,14/g")
        st.subheader("Operação")
        st.metric("Custo indireto (infraestrutura)", "R$ 11,90/h")
        st.metric("Tempo de setup por rodada",       "10 min")
        st.metric("Tempo de pós-processamento / peça", "5 min")


# ══════════════════════════════════════════════════════════════════════════════
# ABAS
# ══════════════════════════════════════════════════════════════════════════════
aba_fab, aba_dev, aba_comp = st.tabs(
    ["🏭 Custo de Fabricação", "📐 Custo de Desenvolvimento", "📊 Comparação entre Versões"]
)


# ═══════════════════════════════════════════════════════════════════════════════
# ABA 1 — CUSTO DE FABRICAÇÃO
# ═══════════════════════════════════════════════════════════════════════════════
with aba_fab:
    st.header("Custo de Fabricação")

    if not _versoes_json:
        st.warning("Nenhuma versão encontrada em dados/versoes.json.")
        st.stop()

    col_esq, col_dir = st.columns([1, 2])

    with col_esq:
        versao_fab = st.selectbox(
            "Versão do dispositivo",
            options=_nomes_versoes,
            key="fab_versao_sel",
        )
        v_fab  = _versoes_dict[versao_fab]
        dt_fab = v_fab["dados_tecnicos"]

        modo_fab = st.radio(
            "Modo de produção",
            ["Lote", "Unitário"],
            horizontal=True,
            key="fab_modo",
        )

        st.subheader("Perfil do operador")
        custo_op_fab, perfil_fab = _selecionar_operador("fab")

        st.divider()
        tipo_label = "Peça única" if v_fab["tipo"] == "peca_unica" else "Duas partes (A+B)"
        st.caption(f"**Configuração:** {tipo_label}")
        st.caption(f"**Data de desenvolvimento:** {v_fab['info'].get('data_versao', '—')}")

        st.subheader("Dados técnicos")
        if modo_fab == "Lote":
            if v_fab["tipo"] == "duas_partes":
                lc1, lc2 = st.columns(2)
                lc1.metric("Parte A — Tempo", f"{dt_fab['lote']['parte_a']['tempo_min']:.0f} min")
                lc1.metric("Parte A — Massa", f"{dt_fab['lote']['parte_a']['massa_g']:.2f} g")
                lc2.metric("Parte B — Tempo", f"{dt_fab['lote']['parte_b']['tempo_min']:.0f} min")
                lc2.metric("Parte B — Massa", f"{dt_fab['lote']['parte_b']['massa_g']:.2f} g")
                st.metric("Peças por lote", str(dt_fab["lote"]["num_pecas"]))
            else:
                pu1, pu2 = st.columns(2)
                pu1.metric("Tempo total", f"{dt_fab['lote']['tempo_total_min']:.0f} min")
                pu1.metric("Massa total", f"{dt_fab['lote']['massa_total_g']:.2f} g")
                pu2.metric("Peças por lote", str(dt_fab["lote"]["num_pecas"]))
        else:
            uc1, uc2 = st.columns(2)
            if v_fab["tipo"] == "peca_unica":
                uc1.metric("Tempo de impressão", f"{dt_fab['unitario']['tempo_min']:.0f} min")
                uc2.metric("Massa de filamento", f"{dt_fab['unitario']['massa_g']:.2f} g")
            else:
                uc1.metric("Tempo A+B", f"{dt_fab['unitario']['tempo_min']:.0f} min")
                uc2.metric("Massa A+B", f"{dt_fab['unitario']['massa_g']:.2f} g")

    with col_dir:
        # Invalidar resultado se os inputs mudaram desde o último cálculo
        _cache_fab = (versao_fab, modo_fab, custo_op_fab)
        if st.session_state.get("_fab_cache") != _cache_fab:
            st.session_state.pop("fab_resultado", None)

        if st.button("Calcular custo de fabricação", type="primary", use_container_width=True):
            r_fab = _calcular_fab(v_fab, custo_op_fab, modo_fab)
            st.session_state["fab_resultado"] = r_fab
            st.session_state["_fab_cache"]    = _cache_fab

        if "fab_resultado" in st.session_state:
            r    = st.session_state["fab_resultado"]
            cor  = "#378ADD" if modo_fab == "Lote" else "#E07B39"
            lote = f"{r['lote']} un." if modo_fab == "Lote" else "1 un."

            st.divider()
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Custo / unidade", f"R$ {r['custo_total']:.2f}")
            m2.metric("Material",        f"R$ {r['custo_material']:.2f}")
            m3.metric("Máquina",         f"R$ {r['custo_maquina']:.2f}")
            m4.metric("Lote",            lote)

            col_tab, col_graf = st.columns(2)
            with col_tab:
                comp = {
                    "Material (filamento)":    r["custo_material"],
                    "Máquina (depreciação)":   r["custo_maquina"],
                    "Setup":                   r["custo_setup"],
                    "Pós-processamento":       r["custo_pos_processamento"],
                    "Mão de obra (supervisão)":r["custo_mao_obra"],
                    "Custo indireto":          r["custo_indireto"],
                }
                rows = [
                    {
                        "Componente": k,
                        "Valor (R$)": f"R$ {v:.2f}",
                        "% do Total": f"{v / r['custo_total'] * 100:.1f}%",
                    }
                    for k, v in comp.items()
                ]
                rows.append({"Componente": "TOTAL",
                              "Valor (R$)": f"R$ {r['custo_total']:.2f}", "% do Total": "100%"})
                st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

            with col_graf:
                st.plotly_chart(
                    _donut(r, f"Composição — {modo_fab}", cor),
                    use_container_width=True,
                )

            st.divider()
            if st.button("➕ Adicionar à comparação", key="add_fab", type="secondary"):
                st.session_state["comparacoes"].append({
                    "versao":             versao_fab,
                    "modulo":             "Fabricação",
                    "modo":               modo_fab,
                    "perfil":             perfil_fab,
                    "custo_operador_hora": r["custo_operador_hora"],
                    "custo":              r["custo_total"],
                    "resultado_completo": r,
                })
                st.success(f"'{versao_fab} — Fabricação {modo_fab}' adicionado à comparação!")


# ═══════════════════════════════════════════════════════════════════════════════
# ABA 2 — CUSTO DE DESENVOLVIMENTO
# ═══════════════════════════════════════════════════════════════════════════════
with aba_dev:
    st.header("Custo de Desenvolvimento")
    st.caption("Horas por atividade carregadas do JSON conforme a versão selecionada. "
               "Baseado no modelo de Lamei (2021).")

    if not _versoes_json:
        st.warning("Nenhuma versão encontrada em dados/versoes.json.")
        st.stop()

    col_dev1, col_dev2 = st.columns([1, 2])

    with col_dev1:
        versao_dev = st.selectbox(
            "Versão do dispositivo",
            options=_nomes_versoes,
            key="dev_versao_sel",
        )
        v_dev = _versoes_dict[versao_dev]

        st.subheader("Perfil do operador")
        custo_op_dev, perfil_dev = _selecionar_operador("dev")

        st.divider()
        st.subheader("Horas por atividade")
        ativs_json = v_dev["desenvolvimento"]["atividades"]
        total_h_json = v_dev["desenvolvimento"]["tempo_total_horas"]

        rows_h = [
            {"Atividade": a["label"], "Horas": a["horas"]}
            for a in ativs_json.values()
        ]
        rows_h.append({"Atividade": "TOTAL", "Horas": total_h_json})
        st.dataframe(pd.DataFrame(rows_h), use_container_width=True, hide_index=True)

    with col_dev2:
        _cache_dev = (versao_dev, custo_op_dev)
        if st.session_state.get("_dev_cache") != _cache_dev:
            st.session_state.pop("dev_resultado", None)

        if st.button("Calcular custo de desenvolvimento", type="primary", use_container_width=True):
            r_dev = _calcular_dev(v_dev, custo_op_dev)
            st.session_state["dev_resultado"] = r_dev
            st.session_state["_dev_cache"]    = _cache_dev

        if "dev_resultado" in st.session_state:
            r_d = st.session_state["dev_resultado"]
            st.divider()
            md1, md2, md3, md4 = st.columns(4)
            md1.metric("Custo Total",     f"R$ {r_d['custo_total']:.2f}")
            md2.metric("Tempo Total",     f"{r_d['tempo_total_horas']:.1f} h")
            md3.metric("Mão de Obra",     f"R$ {r_d['custo_mao_obra']:.2f}")
            md4.metric("Custo Indireto",  f"R$ {r_d['custo_indireto']:.2f}")

            ativs_res = r_d["atividades"]
            labels_d  = [a["label"] for a in ativs_res.values() if a["horas"] > 0]
            custos_d  = [a["custo"] for a in ativs_res.values() if a["horas"] > 0]

            col_td, col_gd = st.columns(2)
            with col_td:
                rows_dev = [
                    {"Atividade": a["label"], "Horas": f"{a['horas']:.1f}h",
                     "Custo (R$)": f"R$ {a['custo']:.2f}"}
                    for a in ativs_res.values()
                ]
                rows_dev.append({"Atividade": "TOTAL",
                                  "Horas": f"{r_d['tempo_total_horas']:.1f}h",
                                  "Custo (R$)": f"R$ {r_d['custo_total']:.2f}"})
                st.dataframe(pd.DataFrame(rows_dev), use_container_width=True, hide_index=True)

            with col_gd:
                if labels_d:
                    fig_bar = go.Figure(go.Bar(
                        x=custos_d, y=labels_d, orientation="h",
                        marker_color="#1D9E75",
                        text=[f"R$ {c:.2f}" for c in custos_d],
                        textposition="outside",
                    ))
                    fig_bar.update_layout(
                        title="Custo por Atividade",
                        xaxis_title="Custo (R$)",
                        template="plotly_white",
                        paper_bgcolor="rgba(0,0,0,0)",
                        plot_bgcolor="rgba(0,0,0,0)",
                        margin=dict(l=220),
                    )
                    st.plotly_chart(fig_bar, use_container_width=True)

            st.divider()
            if st.button("➕ Adicionar à comparação", key="add_dev", type="secondary"):
                st.session_state["comparacoes"].append({
                    "versao":             versao_dev,
                    "modulo":             "Desenvolvimento",
                    "modo":               "—",
                    "perfil":             perfil_dev,
                    "custo_operador_hora": r_d["custo_operador_hora"],
                    "custo":              r_d["custo_total"],
                    "resultado_completo": r_d,
                })
                st.success(f"'{versao_dev} — Desenvolvimento' adicionado à comparação!")


# ═══════════════════════════════════════════════════════════════════════════════
# ABA 3 — COMPARAÇÃO ENTRE VERSÕES
# ═══════════════════════════════════════════════════════════════════════════════
with aba_comp:
    st.header("Comparação entre Versões")
    st.caption("Exibe apenas os cálculos realizados nesta sessão.")

    comparacoes = st.session_state["comparacoes"]

    if comparacoes:
        df_comp = construir_dataframe(comparacoes)

        st.subheader("Resultados da sessão")
        st.dataframe(df_comp, use_container_width=True, hide_index=True)

        st.subheader("Gráficos")
        st.plotly_chart(grafico_custo_por_versao(df_comp), use_container_width=True)

        col_g1, col_g2 = st.columns(2)
        with col_g1:
            st.plotly_chart(grafico_fab_por_versao(df_comp), use_container_width=True)
        with col_g2:
            st.plotly_chart(grafico_dev_por_versao(df_comp), use_container_width=True)
    else:
        st.info(
            "Nenhum cálculo realizado nesta sessão. "
            "Calcule e adicione resultados nas abas de Fabricação e Desenvolvimento, "
            "ou use o botão abaixo para calcular todas as versões de uma vez."
        )

    st.divider()
    col_lim, col_all = st.columns([1, 2])

    with col_lim:
        if st.button("🗑️ Limpar todos os cálculos", type="secondary"):
            st.session_state["comparacoes"] = []
            st.rerun()

    with col_all:
        with st.expander("🚀 Calcular todas as versões automaticamente"):
            st.caption(
                "Calcula fabricação (lote e unitário) e desenvolvimento para todas as "
                f"{len(_versoes_json)} versões com o perfil selecionado e adiciona à tabela."
            )
            custo_op_all, perfil_all = _selecionar_operador("all")

            n_total = len(_versoes_json) * 3
            if st.button(
                f"▶ Calcular {len(_versoes_json)} versões × 3 = {n_total} resultados",
                type="primary",
                key="calc_all",
            ):
                for v_all in _versoes_json:
                    for modo_all in ["Lote", "Unitário"]:
                        r_all = _calcular_fab(v_all, custo_op_all, modo_all)
                        st.session_state["comparacoes"].append({
                            "versao":             v_all["nome"],
                            "modulo":             "Fabricação",
                            "modo":               modo_all,
                            "perfil":             perfil_all,
                            "custo_operador_hora": custo_op_all,
                            "custo":              r_all["custo_total"],
                            "resultado_completo": r_all,
                        })
                    r_dev_all = _calcular_dev(v_all, custo_op_all)
                    st.session_state["comparacoes"].append({
                        "versao":             v_all["nome"],
                        "modulo":             "Desenvolvimento",
                        "modo":               "—",
                        "perfil":             perfil_all,
                        "custo_operador_hora": custo_op_all,
                        "custo":              r_dev_all["custo_total"],
                        "resultado_completo": r_dev_all,
                    })
                st.rerun()
