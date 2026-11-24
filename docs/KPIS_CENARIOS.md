# Indicadores dos cenários (fixados antes das corridas)

**Data:** 25/11/2026 · **Responsável:** João · Fixados **antes** de correr a Base, os Cenários 2–4, os Limiares e a sensibilidade, tal como os factos estilizados foram fixados antes da calibração. Não se mudam depois de ver os resultados.

Calculados por `scripts/kpis_choque.py`, para cada corrida, a partir de `precos.csv` (um registo por minuto) e `halts.csv` (reservas). O choque de informação é de **−10%** no minuto **30 600** (dia 60 da corrida = 5/09/2024). Um dia tem 510 minutos.

## 1. Crash (pergunta 1 da proposta)

Não existe uma definição regulamentar de crash (nem da ESMA nem da Euronext). Definimo-lo com os dados do BCP:

**Crash** = a queda máxima no dia do choque é maior do que **−10% (a notícia) mais a queda dentro do dia que o BCP real só ultrapassou em 1% dos dias de 2023–2024**.

- A queda dentro do dia é *mínimo do dia ÷ fecho do dia anterior − 1* (`scripts/limiar_crash.py`, `data/processed/limiar_crash.xlsx`).
- Ideia: o choque de −10% é informação; uma queda até aí é o mercado a ajustar-se. Um crash é cair **mais** do que a informação justifica, por um valor que um dia normal do BCP quase nunca produz.

| | Definição | Valor fixado |
|---|---|---|
| **Limiar principal** | −10% + percentil 99 da queda dentro do dia | **−17,44%** (`-0.1744`) |
| Intervalo de 95% do limiar principal | bootstrap em blocos de 10 dias, 3000 reamostragens | −19,60% a −15,21% |
| **Limiar de robustez** | −10% + percentil 95 | **−14,52%** (`-0.1452`) |

- **Probabilidade de crash** = % das corridas de um cenário com crash, com intervalo de confiança de Wilson a 95%. Calcula-se com os dois limiares (`prob_crash` e `prob_crash_alt`).
- **Queda a mais** em cada corrida (queda máxima − (−10%)): medida contínua que não depende de nenhum limiar.
- **Regra de leitura, fixada já:** uma conclusão sobre o efeito dos colares na probabilidade de crash só é dada como robusta se tiver o mesmo sentido com os dois limiares e com a queda a mais.
- Valores medidos em 511 dias de 2023–2024: percentil 99 da queda dentro do dia −7,44%; percentil 95 −4,52%; pior queda −10,46% a 15/03/2023 (crise do Credit Suisse).
- Comando para os KPIs: `python scripts\kpis_choque.py PASTA 30600 -0.1744 -0.1452`
- Limitações a reportar: o percentil 99 depende dos poucos piores dias (daí o intervalo); a queda dentro do dia inclui dias com notícias e a variação desde o fecho anterior; somar a notícia e a queda de um dia mau é uma convenção nossa.

## 2. Estabilidade

| Indicador | Definição |
|---|---|
| `queda_max_dia` | preço mínimo no dia do choque ÷ preço antes do choque − 1 |
| `queda_a_mais` | `queda_max_dia` − (−10%); negativo = caiu mais do que a notícia |
| `queda_30min` | queda máxima nos 30 minutos seguintes ao choque |
| `ret_fecho` | retorno do preço antes do choque até ao fecho do dia do choque |
| `ret_5d` | retorno até ao fim do 5.º dia depois do choque |
| `recupera_meia_min` | minutos desde o mínimo até o preço recuperar metade da queda (até 5 dias) |
| `vol_diaria` | desvio-padrão dos retornos diários da corrida |

## 3. Liquidez (pergunta 2 da proposta)

| Indicador | Definição |
|---|---|
| `spread_dia_choque` | spread relativo médio (ask − bid) ÷ preço médio, fora das reservas, no dia do choque |
| `spread_5d` | o mesmo nos 5 dias seguintes ao dia do choque |
| `volume_dia_choque` | ações negociadas no dia do choque |
| `volume_5d` | ações negociadas nos 5 dias seguintes |
| `min_reserva_dia_choque` | minutos em reserva (sem negociação contínua) no dia do choque |
| `n_reservas_dia_choque` | número de reservas no dia do choque |
| `pct_tempo_reserva` | % do tempo da corrida em reserva |

O spread mede-se só fora das reservas: durante a reserva não há negociação contínua e o livro pode ficar cruzado.

## 4. Comparações e testes

- Por cenário: média e intervalo de confiança de 95% (t-Student) de cada indicador.
- Com vs sem colares: diferença das médias e teste t de Welch (variâncias diferentes).
- Mesma semente por réplica (`new Random(1000 + getCurrentReplication())`): a réplica *k* de cada cenário vê o mesmo fundo de mercado; só mudam os colares.

## 5. Análise multicritério (pergunta 2)

1. Critérios: **estabilidade** (`queda_max_dia`, `prob_crash`, `recupera_meia_min`) e **liquidez** (`spread_dia_choque`, `volume_dia_choque`, `min_reserva_dia_choque`).
2. Cada indicador é normalizado entre 0 e 1 em todos os conjuntos de colares (1 = melhor).
3. Dentro de cada critério, média simples dos indicadores.
4. Pesos estabilidade/liquidez: **50/50**, com teste de robustez a **70/30** e **30/70**.
5. Ordenam-se os conjuntos de colares e durações da reserva. A recomendação só é dada como robusta se o primeiro lugar se mantiver nos três pesos.

## 6. Requisito para as experiências

O `label` de cada corrida tem de identificar **todos** os parâmetros que variam na experiência (colares, reserva, nº de chartists, `herdThreshold`, `customDyn`, `customStat` e o parâmetro da sensibilidade). Corridas com o mesmo `label` são agrupadas como se fossem do mesmo cenário.
