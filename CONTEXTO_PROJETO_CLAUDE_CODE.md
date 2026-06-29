# Contexto do Projeto — Protótipo de Custeio para Manufatura Aditiva
## Para uso inicial no Claude Code / VSCode

---

## 1. Identificação do Projeto

**Título:** Desenvolvimento de um Protótipo para Definição de Custos na Manufatura Aditiva

**Tipo:** Projeto de Iniciação Científica (PIBIC)

**Instituição:** Universidade de Brasília (UnB) — Laboratório Aberto de Brasília (LAB)

**Projeto maior:** PROTeMA — Inovações para Proteção em Segurança no Trabalho via Manufatura Aditiva

**Orientadora:** Profa. Dra. Andrea Cristina dos Santos

**Objetivo:** Desenvolver um protótipo automatizado em Python com interface Streamlit para calcular e comparar os custos unitários de peças produzidas por Manufatura Aditiva FDM, aplicado aos dispositivos médicos do projeto PROTeMA.

---

## 2. Contexto do Produto Analisado

O protótipo vai calcular e comparar os custos de produção do **Saca-Lâminas**, um dispositivo médico de proteção contra perfurocortantes desenvolvido pelo LAB para hospitais do Distrito Federal. O dispositivo passou por múltiplas versões (V1 a V19) e é produzido em duas partes (Parte A e Parte B) usando impressoras **Prusa MK3S** com filamento **PLA**.

---

## 3. Estrutura de Arquivos do Projeto

```
prototipo-custeio-saca-laminas/
├── app.py                        (interface principal Streamlit)
├── modulos/
│   ├── __init__.py
│   ├── fabricacao.py             (módulo 1: custo de fabricação)
│   ├── desenvolvimento.py        (módulo 2: custo de desenvolvimento)
│   └── comparacao.py             (módulo 3: comparação entre versões)
├── dados/
│   └── versoes.json              (armazena versões salvas pelo usuário)
├── requirements.txt
└── README.md
```

---

## 4. Parâmetros Fixos do Laboratório

Estes valores são baseados no trabalho de Kelly Santana Silva (2025) e nos dados reais do Laboratório Aberto de Brasília. Devem ser configuráveis pelo usuário na interface, mas possuem os seguintes valores padrão:

| Parâmetro | Valor Padrão | Fonte |
|---|---|---|
| Custo de aquisição da Prusa MK3 | R$ 5.500,00 | Kelly (2025) |
| Custo de manutenção da máquina | R$ 300,00 | Kelly (2025) |
| Valor residual da máquina | R$ 800,00 | Kelly (2025) |
| Vida útil da máquina (horas) | 14.112h | 7 anos × 12 meses × 21 dias × 8h |
| Custo do filamento PLA | R$ 0,14/g | LAB atual |
| Custo indireto (infraestrutura) | R$ 11,90/h | Kelly (2025) — R$ 2.000/mês ÷ 168h |
| Tempo de setup por rodada | 10 minutos | LAB |
| Tempo de pós-processamento | 5 minutos por peça | LAB |
| Dias úteis por mês | 21 dias | LAB |
| Horas por dia | 8 horas | LAB |

**Parâmetro variável (definido pelo usuário a cada cálculo):**
- Custo do operador (R$/h) — permite comparar diferentes perfis:
  - Consultor técnico / gestor: R$ 47,62/h (referência Cenário 1 de Kelly, 2025)
  - Operador graduando: R$ 23,21/h (referência Cenário 2 de Kelly, 2025)
  - Combinação dos dois: R$ 31,70/h (referência Cenário 3 de Kelly, 2025)

---

## 5. Módulo 1 — Custo de Fabricação

### Descrição
Calcula o custo unitário de produção física de uma versão do Saca-Lâminas, considerando produção em lote com rateio de custos fixos.

### Entradas do usuário
- Nome / versão do dispositivo (ex: "Saca-Lâminas V19")
- Quantidade de peças por lote
- Parte A: tempo de impressão (minutos) e massa de filamento (gramas)
- Parte B: tempo de impressão (minutos) e massa de filamento (gramas)
- Custo do operador R$/h (variável)

### Fórmulas de cálculo

```python
# Taxa de custo da máquina por hora
taxa_maquina = (custo_aquisicao + custo_manutencao - valor_residual) / vida_util_horas

# Custo da máquina por unidade
tempo_total_horas = (tempo_impressao_A + tempo_impressao_B) / 60
custo_maquina = (taxa_maquina * tempo_total_horas) / pecas_por_lote

# Custo de material por unidade
massa_total = massa_filamento_A + massa_filamento_B
custo_material = (massa_total / pecas_por_lote) * custo_filamento_grama

# Custo de setup por unidade (2 rodadas: uma para cada parte)
custo_setup = (2 * (tempo_setup_min / 60) * custo_operador) / pecas_por_lote

# Custo de pós-processamento por unidade
custo_pos = (tempo_pos_min / 60) * custo_operador

# Custo de mão de obra durante impressão (10% do tempo, baseado em Concli 2023)
custo_mao_obra = (tempo_total_horas * 0.10 / pecas_por_lote) * custo_operador

# Custo indireto por unidade
custo_indireto = (tempo_total_horas / pecas_por_lote) * custo_indireto_hora

# Custo total por unidade
custo_total = (custo_material + custo_maquina + custo_setup +
               custo_pos + custo_mao_obra + custo_indireto)
```

### Saídas
- Tabela detalhada com cada componente de custo e seu valor
- Métricas resumidas: custo total, custo de material, custo de máquina, custo de operação
- Gráfico de rosca (donut) mostrando a proporção de cada componente no custo total
- Botão para salvar a versão no arquivo versoes.json para comparação posterior

### Dados de referência (Saca-Lâminas V19, lote de 20 unidades)
- Parte A: 521 minutos, 98,18g
- Parte B: 321 minutos, 70,38g
- Resultado esperado: aproximadamente R$ 8,00 por unidade

---

## 6. Módulo 2 — Custo de Desenvolvimento

### Descrição
Calcula o custo de projeto e desenvolvimento de uma versão do Saca-Lâminas, baseado no modelo de Lamei (2021) adaptado ao processo real do LAB. Segue a estrutura de pré-processamento e pós-processamento.

### Entradas do usuário
- Nome / versão do dispositivo
- Custo do operador R$/h (variável)
- Tempos estimados (em horas) para cada atividade:

**Pré-processamento:**
- Reuniões com equipe de saúde
- Levantamento de requisitos
- Modelagem CAD
- Fatiamento e configuração no PrusaSlicer
- Análise DfAM (Design for Additive Manufacturing)
- Retrabalho e ajustes de projeto

**Pós-processamento:**
- Validação no laboratório
- Validação com usuário / hospital
- Documentação da versão

### Fórmulas de cálculo

```python
# Para cada atividade:
custo_atividade = tempo_atividade_horas * (custo_operador + custo_indireto_hora)

# Totais
tempo_total = sum(todos_os_tempos)
custo_mao_obra_total = tempo_total * custo_operador
custo_indireto_total = tempo_total * custo_indireto_hora
custo_total_desenvolvimento = custo_mao_obra_total + custo_indireto_total
```

### Saídas
- Tabela com custo por atividade
- Métricas: custo total, tempo total, custo de mão de obra, custo indireto
- Gráfico de barras com custo por atividade
- Botão para salvar a versão no arquivo versoes.json

---

## 7. Módulo 3 — Comparação entre Versões

### Descrição
Exibe comparativos visuais entre todas as versões do Saca-Lâminas salvas pelo usuário, permitindo analisar a evolução dos custos ao longo das iterações de desenvolvimento.

### Funcionamento
- Lê o arquivo versoes.json com todas as versões salvas
- Gera três gráficos de barras comparativos:
  1. Custo de fabricação por versão
  2. Custo de desenvolvimento por versão
  3. Custo total acumulado por versão (barras empilhadas: fabricação + desenvolvimento)
- Exibe tabela resumo com todos os valores

### Estrutura do arquivo versoes.json

```json
{
  "versoes": [
    {
      "nome": "Saca-Lâminas V19",
      "data_registro": "2025-06-21",
      "fabricacao": {
        "custo_total": 8.00,
        "custo_material": 1.18,
        "custo_maquina": 0.24,
        "custo_setup": 1.00,
        "custo_pos_processamento": 5.00,
        "custo_mao_obra": 0.33,
        "custo_indireto": 0.25,
        "lote": 20,
        "custo_operador_hora": 47.62
      },
      "desenvolvimento": {
        "custo_total": 0,
        "custo_mao_obra": 0,
        "custo_indireto": 0,
        "tempo_total_horas": 0,
        "custo_operador_hora": 47.62,
        "atividades": {}
      }
    }
  ]
}
```

---

## 8. Interface Principal (app.py)

### Estrutura de navegação
A interface deve ter três abas principais:
1. **Custo de fabricação** — Módulo 1
2. **Custo de desenvolvimento** — Módulo 2
3. **Comparação entre versões** — Módulo 3

### Sidebar (painel lateral)
Contém os parâmetros fixos do laboratório, editáveis pelo usuário:
- Todos os parâmetros da seção 4 deste documento
- Um aviso indicando que alterações nos parâmetros fixos afetam todos os cálculos

### Estilo visual
- Interface limpa e profissional, adequada para uso acadêmico
- Cores principais: azul (#378ADD) para fabricação, verde (#1D9E75) para desenvolvimento
- Métricas em destaque usando st.metric do Streamlit
- Gráficos usando Plotly (mais interativo que matplotlib)

---

## 9. Dependências do Projeto (requirements.txt)

```
streamlit>=1.28.0
plotly>=5.18.0
pandas>=2.1.0
```

---

## 10. Referências Metodológicas

- **Lamei (2021):** modelo de custeio em três etapas (pré-processamento, processamento, pós-processamento) com custeio ABC
- **Concli (2023):** modelo focado em programação e fabricação, com operador atuando 10% do tempo de impressão
- **Kelly Santana Silva (2025):** aplicação dos modelos de Lamei e Concli no LAB/UnB, com os parâmetros reais do laboratório
- **Srikanth et al. (2025):** quantificação de complexidade de forma (FSC) e seu impacto no tempo e custo de impressão FDM

---

## 11. Instruções para o Claude Code

Ao receber este documento, o Claude Code deve:

1. Criar a estrutura de pastas descrita na seção 3
2. Implementar o arquivo `modulos/fabricacao.py` com as fórmulas da seção 5
3. Implementar o arquivo `modulos/desenvolvimento.py` com as fórmulas da seção 6
4. Implementar o arquivo `modulos/comparacao.py` com a lógica da seção 7
5. Implementar o arquivo `app.py` com a interface da seção 8
6. Criar o arquivo `requirements.txt` com as dependências da seção 9
7. Criar o arquivo `dados/versoes.json` com a estrutura da seção 7
8. Criar o arquivo `README.md` com instruções de instalação e uso
9. Garantir que todos os valores monetários sejam exibidos com duas casas decimais
10. Garantir que o custo do operador seja sempre um campo editável pelo usuário, nunca fixo

---

*Documento gerado em 21/06/2026 — Projeto de Iniciação Científica PIBIC/UnB*
