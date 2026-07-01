import json
import os

import pandas as pd
import plotly.graph_objects as go

_GRAPH_LAYOUT = dict(
    template="plotly_white",
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
)

_CORES = {
    "Fabricação — Lote":     "#378ADD",
    "Fabricação — Unitário": "#E07B39",
    "Desenvolvimento":       "#1D9E75",
}


def carregar_versoes(caminho_json: str) -> list:
    if not os.path.exists(caminho_json):
        return []
    with open(caminho_json, "r", encoding="utf-8") as f:
        dados = json.load(f)
    return dados.get("versoes", [])


def _build_label(c: dict) -> str:
    """Identificador único: 'V5 | Lote | Consultor (R$ 47,62/h)'."""
    versao = c["versao"].replace("Saca-Lâminas ", "")
    modo_display = c["modo"] if c["modo"] != "—" else "Dev"
    label = f"{versao} | {modo_display} | {c['perfil']}"
    if not c.get("considerar_indireto", True):
        label += " | s/ indiretos"
    return label


def construir_dataframe(comparacoes: list) -> pd.DataFrame:
    if not comparacoes:
        return pd.DataFrame(
            columns=["Versão", "Módulo", "Modo", "Perfil do Operador", "Custo (R$)", "Identificador"]
        )
    registros = [
        {
            "Versão":             c["versao"],
            "Módulo":             c["modulo"],
            "Modo":               c["modo"],
            "Perfil do Operador": c["perfil"],
            "Custo (R$)":        c["custo"],
            "Identificador":     _build_label(c),
        }
        for c in comparacoes
    ]
    return pd.DataFrame(registros)


def grafico_custo_por_versao(df: pd.DataFrame) -> go.Figure:
    df = df.copy()
    df["Categoria"] = df.apply(
        lambda r: f"Fabricação — {r['Modo']}" if r["Módulo"] == "Fabricação" else "Desenvolvimento",
        axis=1,
    )

    fig = go.Figure()
    for cat in df["Categoria"].unique():
        d = df[df["Categoria"] == cat]
        fig.add_trace(go.Bar(
            name=cat,
            x=d["Identificador"],
            y=d["Custo (R$)"],
            marker_color=_CORES.get(cat, "#888888"),
            text=d["Custo (R$)"].apply(lambda v: f"R$ {v:.2f}"),
            textposition="outside",
        ))

    fig.update_layout(
        barmode="group",
        title="Custo por Cálculo (Versão | Modo | Perfil)",
        xaxis_title="Cálculo",
        yaxis_title="Custo (R$)",
        xaxis_tickangle=-35,
        **_GRAPH_LAYOUT,
    )
    return fig


def grafico_fab_por_versao(df: pd.DataFrame) -> go.Figure:
    fab = df[df["Módulo"] == "Fabricação"].copy()
    fig = go.Figure()
    cores_modo = {"Lote": "#378ADD", "Unitário": "#E07B39"}
    for modo in (fab["Modo"].unique() if not fab.empty else []):
        d = fab[fab["Modo"] == modo]
        fig.add_trace(go.Bar(
            name=f"Fabricação — {modo}",
            x=d["Identificador"],
            y=d["Custo (R$)"],
            marker_color=cores_modo.get(modo, "#888"),
            text=d["Custo (R$)"].apply(lambda v: f"R$ {v:.2f}"),
            textposition="outside",
        ))
    fig.update_layout(
        barmode="group",
        title="Custo de Fabricação (Versão | Modo | Perfil)",
        xaxis_title="Cálculo",
        yaxis_title="Custo (R$)",
        xaxis_tickangle=-35,
        **_GRAPH_LAYOUT,
    )
    return fig


def grafico_dev_por_versao(df: pd.DataFrame) -> go.Figure:
    dev = df[df["Módulo"] == "Desenvolvimento"].copy()
    fig = go.Figure()
    if not dev.empty:
        fig.add_trace(go.Bar(
            name="Desenvolvimento",
            x=dev["Identificador"],
            y=dev["Custo (R$)"],
            marker_color="#1D9E75",
            text=dev["Custo (R$)"].apply(lambda v: f"R$ {v:.2f}"),
            textposition="outside",
        ))
    fig.update_layout(
        title="Custo de Desenvolvimento (Versão | Perfil)",
        xaxis_title="Cálculo",
        yaxis_title="Custo (R$)",
        xaxis_tickangle=-35,
        **_GRAPH_LAYOUT,
    )
    return fig
