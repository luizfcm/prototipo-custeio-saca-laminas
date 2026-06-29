# Protótipo de Custeio — Saca-Lâminas | LAB/UnB

Protótipo automatizado em Python com interface Streamlit para calcular e comparar os custos unitários de peças produzidas por Manufatura Aditiva FDM, aplicado ao dispositivo médico **Saca-Lâminas** do projeto **PROTeMA** (UnB / Laboratório Aberto de Brasília).

## Instalação

**Pré-requisito:** Python 3.9 ou superior instalado.

```bash
# 1. Clone ou extraia o projeto
cd prototipo-custeio-saca-laminas

# 2. (Recomendado) Crie um ambiente virtual
python -m venv .venv
# Windows:
.venv\Scripts\activate

# 3. Instale as dependências
pip install -r requirements.txt
```

## Execução

```bash
streamlit run app.py
```

O navegador abrirá automaticamente em `http://localhost:8501`.

## Estrutura do Projeto

```
prototipo-custeio-saca-laminas/
├── app.py                    Interface principal Streamlit
├── modulos/
│   ├── fabricacao.py         Módulo 1: custo de fabricação
│   ├── desenvolvimento.py    Módulo 2: custo de desenvolvimento
│   └── comparacao.py         Módulo 3: comparação entre versões
├── dados/
│   └── versoes.json          Versões salvas pelo usuário
├── requirements.txt
└── README.md
```

## Módulos

### 1. Custo de Fabricação
Calcula o custo unitário de produção física com rateio por lote. Inclui: material (filamento), depreciação da máquina, setup, pós-processamento, mão de obra e custos indiretos.

### 2. Custo de Desenvolvimento
Calcula o custo de projeto e desenvolvimento baseado no modelo de Lamei (2021): pré-processamento (CAD, DfAM, reuniões) e pós-processamento (validação, documentação).

### 3. Comparação entre Versões
Exibe gráficos comparativos entre todas as versões salvas: fabricação, desenvolvimento e custo total acumulado (barras empilhadas).

## Referências

- Lamei (2021) — modelo de custeio ABC para manufatura aditiva
- Concli (2023) — operador atua 10% do tempo de impressão
- Kelly Santana Silva (2025) — parâmetros reais do LAB/UnB
- Srikanth et al. (2025) — complexidade de forma e impacto no custo FDM

---

*Projeto de Iniciação Científica PIBIC/UnB — Laboratório Aberto de Brasília*
