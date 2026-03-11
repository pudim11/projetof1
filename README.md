# Previsão de Resultados de F1 com Machine Learning

Projeto de portfólio que usa dados de qualificação para prever a ordem de chegada em corridas de Fórmula 1. Construído com FastF1, LightGBM e Python.

---

## Como funciona

A ideia é simples: antes de cada corrida, o modelo recebe os dados da qualificação (posição no grid, gap para a pole, desempenho relativo dentro da equipe, tipo de circuito, fornecedor de motor) e devolve um ranking previsto dos 20 pilotos.

Depois que a corrida acontece, o sistema compara a previsão com o resultado real e calcula as métricas. Se um GP novo foi disputado, o modelo é retreinado com esses dados novos antes do próximo.

O modelo principal é um **LGBMRanker** — um algoritmo de *Learning to Rank* que aprende a ordenar pilotos dentro de cada corrida, em vez de prever um número absoluto de posição.

---

## Resultados

Testei o mesmo GP (Austrália) em quatro temporadas diferentes para ver como o modelo se comporta com o tempo:

| Temporada | Vencedor acertou | Acurácia top-3 | Correlação de ranking | Erro médio |
|-----------|-----------------|----------------|-----------------------|------------|
| 2023      | ✓               | 100%           | 0.896                 | 1.7 pos.   |
| 2024      | ✓               | 66.7%          | 0.896                 | 2.0 pos.   |
| 2025      | ✗               | 100%           | 0.786                 | 2.7 pos.   |
| 2026      | ✓               | 100%           | 0.981                 | 0.7 pos.   |

A queda em 2025 não é um bug — é *concept drift*. O modelo foi treinado principalmente com 2023/2024, quando Verstappen dominava. Em 2025 o McLaren deu um salto de performance que o modelo não havia visto antes, então ele continuou "achando" que VER ia ganhar mesmo com Norris na pole.

Em 2026 o novo regulamento zerou o grid. Os dados dessa temporada têm peso muito maior no treino (peso 1.0 contra 0.05 de 2025), então o modelo aprendeu rápido a hierarquia nova — daí a correlação de 0.981 e erro médio de 0.7 posições, quase acertando a ordem inteira da corrida.

---

## Estrutura

```
projeto_f1/
├── baixar_dados.py            
├── src/
│   ├── api/fetcher.py           
│   ├── model/
│   │   ├── trainer.py         
│   │   └── predictor.py         
│   └── preprocessing/
│       ├── features.py          
│       ├── circuit_metadata.py 
│       └── cleaner.py          
└── data/
    ├── fastf1_cache/            
    └── f1_master_dataset.csv    
```

---

## Instalação

```bash
git clone https://github.com/seu-usuario/projeto_f1
cd projeto_f1
python -m venv .venv
.venv\Scripts\activate        
pip install -r requirements.txt
```

---

## Como usar

**1. Baixar dados históricos**

```bash
python baixar_dados.py 2023
python baixar_dados.py 2024
python baixar_dados.py 2025
```

Se a conexão cair no meio, é só rodar novamente — os GPs já baixados são pulados automaticamente.

**2. Treinar o modelo**

```bash
python src/model/trainer.py
```

**3. Testar uma predição**

```python
import fastf1
from src.model.predictor import run_gp_cycle

session_q = fastf1.get_session(2026, "Australian Grand Prix", "Q")
session_r = fastf1.get_session(2026, "Australian Grand Prix", "R")
session_q.load()
session_r.load()

metrics = run_gp_cycle(session_q, session_r, 2026, "Australian Grand Prix")
```

**4. Atualizar após um GP novo (durante a temporada)**

```bash
python baixar_dados.py 2026   
python src/model/trainer.py  
```

---

## Features usadas

| Feature | Descrição |
|---------|-----------|
| `quali_position` | Posição no grid de largada |
| `quali_gap_to_pole` | Gap em segundos para o tempo da pole |
| `intra_team_rank` | Posição relativa dentro da equipe (isola habilidade do piloto) |
| `intra_team_gap` | Gap de tempo para o companheiro de equipe |
| `pu_manufacturer` | Fornecedor do motor |
| `is_street` | Circuito de rua ou não |
| `is_high_speed` | Circuito de alta velocidade |
| `is_sprint_weekend` | Fim de semana com Sprint |
| `is_new_circuit` | Circuito sem histórico na F1 |
| `mid_season_team_change` | Piloto trocou de equipe no meio da temporada |

A feature `intra_team_rank` merece destaque: em vez de usar o tempo absoluto de volta, ela mede o quão rápido o piloto foi **em relação ao companheiro de equipe**. Isso isola a habilidade do piloto da performance do carro — útil para anos de transição como 2026, onde não há histórico do carro novo mas o piloto é o mesmo.

---

## Decisões técnicas

**Por que LGBMRanker e não regressão?**
Prever a posição de chegada como número (1º, 2º, 3º...) cria um problema: o modelo pode prever dois pilotos em "2.3" sem saber que só um pode ser segundo. O LGBMRanker aprende diretamente a ordenar os pilotos dentro de cada corrida, que é exatamente o que queremos.

**Por que dados de 2023/2024 têm peso baixo?**
Em 2026 o regulamento mudou completamente — carros novos, nova unidade de potência. Os dados antigos ensinam comportamento de pilotos (quem é mais consistente, quem performa bem em circuitos de rua), mas não refletem a hierarquia atual de carros. O peso temporal equilibra isso.

**Por que não usar train_test_split aleatório?**
Dados de F1 têm ordem temporal — você nunca vai ter dados do futuro disponíveis quando fizer uma previsão. Usar split aleatório vazaria informação do futuro para o treino e inflaria artificialmente as métricas. O projeto usa TimeSeriesSplit (validação walk-forward).

---

## Tecnologias

- [FastF1](https://github.com/theOehrly/Fast-F1) — dados de sessões de F1
- [LightGBM](https://lightgbm.readthedocs.io/) — modelo de ranking
- [pandas](https://pandas.pydata.org/) / [numpy](https://numpy.org/) — manipulação de dados
- [scikit-learn](https://scikit-learn.org/) — pré-processamento e validação
- [scipy](https://scipy.org/) — correlação de Spearman
