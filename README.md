# Protótipo de Custeio — Saca-Lâminas | LAB/UnB

Protótipo automatizado em Python com interface Streamlit para calcular e comparar os custos de fabricação e desenvolvimento do dispositivo médico **Saca-Lâminas**, desenvolvido no âmbito do projeto **PROTeMA** (Laboratório Aberto de Brasília — UnB), produzido por Manufatura Aditiva FDM.

🔗 **Acesso online:** [prototipo-custeio-saca-laminas.streamlit.app](https://prototipo-custeio-saca-laminas.streamlit.app)

---

## Sobre o Projeto

Este protótipo foi desenvolvido como parte de um Projeto de Iniciação Científica (PIBIC/UnB) e aplica o método de **Custeio Baseado em Atividades (ABC)** estruturado nas etapas de pré-processamento, processamento e pós-processamento, conforme o modelo de Lamei (2021).

O estudo de caso contempla **10 versões do Saca-Lâminas** (V1 a V8.1), com dados técnicos reais coletados do PrusaSlicer e estimativas de horas de desenvolvimento levantadas com a equipe do LAB/UnB.

---

## Funcionalidades

### 🏭 Custo de Fabricação
- Seleção da versão do dispositivo via dropdown
- Cálculo em dois modos: **Produção em Lote** e **Produção Unitária**
- Suporte a peças únicas (V1–V7.2) e peças com duas partes (V8 e V8.1)
- Perfil do operador variável (Consultor, Graduando, Combinação ou Personalizado)
- Decomposição do custo em: material, máquina, setup, pós-processamento, mão de obra e custos indiretos

### 📐 Custo de Desenvolvimento
- Cálculo baseado no modelo de Lamei (2021)
- Horas por atividade carregadas automaticamente do banco de dados
- Perfil do operador variável

### 📊 Comparação entre Versões
- Comparação de todos os cálculos realizados na sessão
- Suporte a múltiplos cenários simultâneos (diferentes versões, modos e perfis)
- Gráficos interativos com identificador único por cálculo
- Botão para calcular todas as versões automaticamente com um único perfil
- Botão para limpar os cálculos da sessão

---

## Parâmetros Fixos do Laboratório

| Parâmetro | Valor | Fonte |
|---|---|---|
| Custo de aquisição (Prusa MK3S) | R$ 5.500,00 | Kelly (2025) |
| Custo de manutenção | R$ 300,00 | Kelly (2025) |
| Valor residual | R$ 800,00 | Kelly (2025) |
| Vida útil | 14.112 h (7 anos) | Kelly (2025) |
| Custo do filamento PLA | R$ 0,14/g | LAB/UnB |
| Custo indireto (infraestrutura) | R$ 11,90/h | Kelly (2025) |
| Tempo de setup por rodada | 10 min | LAB/UnB |
| Tempo de pós-processamento | 5 min/peça | LAB/UnB |

---

## Estrutura do Projeto
prototipo-custeio-saca-laminas/

├── app.py                    Interface principal Streamlit

├── modulos/

│   ├── fabricacao.py         Cálculo do custo de fabricação

│   ├── desenvolvimento.py    Cálculo do custo de desenvolvimento

│   └── comparacao.py         Comparação entre versões e gráficos

├── dados/

│   └── versoes.json          Dados técnicos das 10 versões do Saca-Lâminas

├── requirements.txt

└── README.md

---

## Instalação Local

**Pré-requisito:** Python 3.13 instalado.

```bash
# 1. Clone o repositório
git clone https://github.com/luizfcm/prototipo-custeio-saca-laminas.git
cd prototipo-custeio-saca-laminas

# 2. Instale as dependências
pip install -r requirements.txt

# 3. Execute o protótipo
streamlit run app.py
```

O navegador abrirá automaticamente em `http://localhost:8501`.

---

## Referências Metodológicas

- **Lamei (2021)** — modelo de custeio ABC em três etapas para Manufatura Aditiva
- **Concli (2023)** — operador atua 10% do tempo de impressão (supervisão passiva)
- **Kelly Santana Silva (2025)** — parâmetros reais do Laboratório Aberto de Brasília/UnB
- **Srikanth et al. (2025)** — impacto da complexidade de forma (FSC) no custo FDM

---

*Projeto de Iniciação Científica PIBIC/UnB*
*Laboratório Aberto de Brasília — Faculdade de Tecnologia — Universidade de Brasília*
