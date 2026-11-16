# Resumo do trabalho · Grupo 2 · Interrupções de negociação no BCP

Este resumo junta tudo o que está no modelo e as decisões que tomámos até 16/11/2026. Os valores vêm do `model/Euronext_Main/Euronext_Main.alp` (commit 91ec71c, modelo final da calibração) e dos documentos do repositório.

---

## 1. O que estamos a estudar

**Pergunta:** os colares de volatilidade da Euronext (interrupções de negociação) travam uma queda do preço, ou só adiam a descoberta do preço e tiram liquidez ao mercado?

**Como:** um mercado artificial no AnyLogic (PLE 8.9.10) com a ação do BCP. Investidores de vários tipos enviam ordens para um livro de ordens; o livro aplica os colares reais da Euronext (±3% / ±8%, reservas de 3 ou 10 min, leilão de reabertura). Depois lançamos choques de notícias (tipo BES) com e sem colares e comparamos a queda, a volatilidade, a liquidez e o tempo de recuperação.

**Âmbito:** só a **Fase 1** (uma ação, livro de ordens, colares), como pediram os professores no feedback à proposta. Alavancagem, brokers e contágio entre ações ficam como trabalho futuro.

**Equipa:**

| Pessoa | Papel |
|---|---|
| Miguel | Livro de ordens em Java (testado primeiro), colares, leilão, noise traders e integração de tudo no modelo principal |
| João | Fundamentalistas e chartists (manada), dados do BCP e scripts Python, factos estilizados, calibração, KPIs, pressupostos |
| Margarida | Instrumentação (CSV, KPIs), experiências dos cenários, corridas de calibração, ESMA |
| Matilde | NewsAgent, MarketMaker, ecrã inicial, dashboard, verificação |

**Tipo de modelo:** baseado em agentes (os investidores, com statecharts e mensagens). O livro de ordens é um sistema de filas (eventos discretos), mas implementado em Java em vez de blocos da Process Modeling Library.

---

## 2. Visão geral do modelo

```
                 ┌────────────── Main (o "mundo") ───────────────┐
                 │ parâmetros · KPIs · ficheiros CSV · broadcast │
                 └───────────────────────────────────────────────┘
   NewsAgent ──muda o valor fundamental──► Fundamentalistas (40)
       │                                   Chartists (13, em rede)
       │ "SHOCK"                           Noise traders (30)
       ▼                                   Market maker (1)
   todos os agentes                              │
                                   stock.order(quem, lado, preço, qtd)
                                                 ▼
                                  ┌──────── Stock (a bolsa) ────────┐
                                  │ livro: bids / asks / pending     │
                                  │ match → collarHit → execute      │
                                  │ statechart: Contínuo → Reserva   │
                                  │             → Leilão → Contínuo  │
                                  └──────────────────────────────────┘
                                    "HALT" / "REOPEN" (via broadcast)
```

- **Unidade de tempo:** minuto. Um dia de negociação = **510 min** (08:00–16:30, hora de Lisboa), seguidos, sem noite.
- **Ordens:** chegam ao Stock por **chamada de função** (`main.stock.order(...)`).
- **Avisos** (HALT, REOPEN, SHOCK, SELL_SIGNAL): por **mensagens** aos statecharts.
- **Tipos de agente:** 7 (Main, Stock, NoiseTrader, Fundamentalist, Chartist, MarketMaker, NewsAgent), mais a classe Java `Order`. Limite da PLE: 10 tipos de agente e 50 000 agentes dinâmicos; não criamos agentes durante a simulação.

---

## 3. Main

O agente de topo. Tem as populações, os parâmetros globais, os KPIs e os ficheiros de saída.

### 3.1 Populações

| Nome | Tipo | Quantidade |
|---|---|---|
| `stock` | Stock | 1 |
| `noiseTraders` | NoiseTrader | `nNoise` (30) |
| `fundamentalists` | Fundamentalist | `nFundamentalists` (40) |
| `chartists` | Chartist | `nChartists` (13) |
| `marketMaker` | MarketMaker | 1 |
| `news` | NewsAgent | 1 |

### 3.2 Parâmetros (todos)

**Mercado e livro de ordens**

| Parâmetro | Valor | O que faz | Origem / decisão |
|---|---|---|---|
| `initialPrice` | 0.50 € | preço inicial e valor fundamental inicial | ordem de grandeza do BCP |
| `tickSize` | 0.0001 € | arredondamento dos preços | simplificação (a Euronext usa uma tabela de ticks) |
| `orderLife` | 35 min | vida média de uma ordem; cada uma vive `orderLife × U(0.3, 1.7)` = 10–60 min | sem dados de Lisboa; calibrado |
| `maWindow` | 50 min | memória da média móvel `stock.ma` usada pelos chartists | horizonte intradiário intermédio |
| `runTests` | false | `true` corre os 6 testes do livro no arranque (com `nNoise` = 0) | verificação |

**Colares, reservas e leilão**

| Parâmetro | Valor | O que faz | Origem / decisão |
|---|---|---|---|
| `collarSet` | 2 | conjunto de colares: 0 = sem colares, 1 = 2%/5%, **2 = 3%/8% (real)**, 3 = 5%/10%, 4 = personalizado | cenários |
| `customDyn` / `customStat` | 0.03 / 0.08 | colares usados quando `collarSet` = 4 | limiares ótimos |
| `haltShort` | 3 min | duração da reserva normal | regra da Euronext |
| `haltLong` | 10 min | reserva quando o colar estático dispara de novo no mesmo sentido no mesmo dia | regra da Euronext |
| `auctionCollar` | 0.06 | o preço do leilão fica a ±6% do último preço antes da reserva | regra da Euronext para o PSI; introduzido a 04/11 |
| `tradeDuringHalt` | true | fundamentalistas e chartists continuam a enviar ordens durante a reserva (vão para o `pending`) | pressuposto relaxado na ronda 8b (Trading Manual: os membros podem pôr ordens durante a reserva) |

**Investidores**

| Parâmetro | Valor | O que faz | Origem / decisão |
|---|---|---|---|
| `nNoise` | 30 | número de noise traders | literatura; calibrado |
| `noiseRate` | 1 /min | ritmo de ordens de cada noise trader | dá liquidez de base |
| `noiseSigma` | 0.002 | dispersão (0,2%) dos preços dos noise traders à volta do mid | calibrado |
| `nFundamentalists` | 40 | número de fundamentalistas | literatura (Lux & Marchesi, 1999) |
| `fundRate` | 0.2 /min | ritmo de decisão do fundamentalista | literatura (Chiarella & Iori, 2002) |
| `fundBand` | 0.01 | só compra/vende se o preço se afastar mais de 1% do seu valor | literatura |
| `nChartists` | **13** | número de chartists | **calibrado: 30 → 15 → 13** (com 30 havia manada demais) |
| `chartRate` | 0.2 /min | ritmo de decisão base do chartist (× `attention`) | literatura |
| `trendThreshold` | 0.005 | o chartist só segue a tendência se o preço estiver mais de 0,5% acima/abaixo da média | literatura |
| `herdThreshold` | 2 | nº de avisos de vizinhos que põe um chartist em pânico | não observável |
| `panicDuration` | 10 min | duração do pânico | não observável |
| `mmSpread` | 0.004 | spread do market maker (0,4%) | sem dados; testado em extremos |
| `mmQty` | 2000 | quantidade de cada oferta do market maker | sem dados |

**Notícias e choque**

| Parâmetro | Valor | O que faz | Origem / decisão |
|---|---|---|---|
| `newsRate` | **0.002** /min | notícias pequenas (~1 por dia), cada uma muda o valor em ±2% | **calibrado na ronda 1** (era 0.0004 e ±1%) |
| `shockOn` | false | liga o choque grande | cenários |
| `shockTime` | 30600 min | instante do choque = dia 60 | cenários |
| `shockSize` | −0.10 | choque de −10% no valor fundamental | inspirado no BES, não é uma reprodução |
| `shockPanicProb` | 0.3 | probabilidade de cada chartist entrar logo em pânico com o choque | não observável |
| `scenario` | "baseline" | nome do cenário (vai para o `label` dos CSV) | instrumentação |

**Atividade e atenção (acrescentados na calibração)**

| Parâmetro | Valor | O que faz | Origem / decisão |
|---|---|---|---|
| `activityPersist` | 0.6 | persistência da atividade diária dos noise traders | rondas 6–7 (persistência do volume) |
| `activitySigma` | 0.05 | parte aleatória da atividade | rondas 6–7 |
| `activityNewsJump` | 0.4 | cada notícia aumenta a atividade | ronda 7 (liga volume às notícias) |
| `attPersist` | 0.7 | persistência da atenção dos chartists | ronda 8b, configuração A2 |
| `attWeight` | 0.6 | quanto um dia agitado aumenta a atenção | ronda 8b, A2 (Barber & Odean, 2008) |
| `useAttChart` | true | ritmo dos chartists = `chartRate × attention` | ronda 8b, A2 |
| `useAttNoise` | false | dispersão dos noise traders × `attention` (opção C, testada e não usada) | ronda 8b |

### 3.3 Variáveis

| Variável | Valor inicial | O que é |
|---|---|---|
| `fundamentalValue` | `initialPrice` | o valor "verdadeiro" da ação; muda com as notícias |
| `nextOrderId` | 0 | contador para o `id` das ordens |
| `dynamicThreshold` / `staticThreshold` | 0.03 / 0.08 | colares em vigor, definidos no arranque a partir de `collarSet` |
| `collarsActive` | true | `false` se `collarSet` = 0 |
| `label` | — | `scenario + "_c" + collarSet + "_h" + haltShort + "_n" + nChartists` (identifica o cenário nos CSV) |
| `runId` | aleatório | identificador de 8 caracteres de cada corrida |
| `peakPrice`, `maxDrawdown` | — | máximo do preço e queda máxima (KPI) |
| `nHalts`, `timeHalted` | 0 | nº de reservas e tempo total em reserva (KPI) |
| `activity` | 1 | atividade do dia dos noise traders (multiplica a quantidade das ordens) |
| `attention` | 1 | atenção do dia dos chartists (multiplica o ritmo de decisão) |
| `dayOpen` | `initialPrice` | preço no início do dia, para medir o movimento diário |

### 3.4 Funções

| Função | O que faz |
|---|---|
| `roundTick(p)` | arredonda um preço ao tick (nunca abaixo de 1 tick) |
| `onFill(t, side, q, p)` | depois de um negócio, atualiza o `cash` e a `position` de quem negociou (`position += side·q`, `cash −= side·q·p`) |
| `broadcast(msg)` | escreve a mensagem na consola e entrega-a ao statechart de todos os fundamentalistas, chartists, market maker e NewsAgent (os noise traders não têm statechart) |

### 3.5 Eventos

| Evento | Quando | O que faz |
|---|---|---|
| `logEvent` | a cada minuto | atualiza `peakPrice` e `maxDrawdown`; escreve uma linha no `precos.csv` |
| `activityEvent` | a cada 510 min (uma vez por dia) | (1) atualiza a `activity`: `exp(activityPersist·log(activity) + N(0, activitySigma) − activityNewsJump·newsRate·510)`; (2) mede o movimento do dia `r = \|log(lastPrice/dayOpen)\|`; (3) atualiza a `attention`: `min(3, exp(attPersist·log(attention) + attWeight·(r/0.0165 − 1)))` |

O termo `− activityNewsJump·newsRate·510` desconta o aumento médio que as notícias dão num dia, para a atividade não crescer sem parar. O `0.0165` é o movimento diário "normal": acima disso a atenção sobe, abaixo desce.

### 3.6 Arranque e fim

**On startup:**
1. Se `runTests`, corre `stock.testBook()`.
2. `switch (collarSet)` define os colares.
3. `peakPrice = initialPrice` e constrói o `label`.
4. Constrói a **rede dos chartists** (small world): cada chartist liga-se aos 3 vizinhos seguintes num anel (6 vizinhos no total); com probabilidade 5% a ligação vai para um chartist ao acaso.

**On destroy:** fecha os dois CSV e escreve na consola `nHalts`, `timeHalted` e `maxDrawdown`.

### 3.7 Ficheiros de saída (`model/Euronext_Main/output/`)

| Ficheiro | Colunas (`;`) | Quando |
|---|---|---|
| `precos.csv` | `label;run;time;price;bid;ask;volume` | 1 linha por minuto |
| `halts.csv` | `label;run;start;end;prePrice;auctionPrice` | 1 linha por interrupção |

---

## 4. Order (classe Java)

Não é um agente: é só a **ficha** de uma ordem. Não tem lógica; quem a preenche e mexe nela é o Stock.

| Campo | Tipo | Significado |
|---|---|---|
| `id` | long | número único; cresce com o tempo, por isso desempata por ordem de chegada |
| `side` | int | 1 = compra, −1 = venda |
| `price` | double | preço-limite |
| `qty` | int | quantidade que falta executar (desce com as execuções parciais) |
| `tSubmit` | double | minuto em que entrou |
| `expiry` | double | minuto em que é cancelada se não for executada |
| `trader` | Agent | quem a enviou (`null` nos testes) |

**Porque é uma classe e não um agente:** cada corrida cria milhões de ordens; a PLE só permite 50 000 agentes dinâmicos, e um agente é muito mais pesado.

---

## 5. Stock (a bolsa e o livro de ordens)

### 5.1 As filas (Additional class code)

| Fila | Tipo | Regra |
|---|---|---|
| `bids` | `PriorityQueue<Order>` | compras: preço **mais alto** primeiro; empate → `id` mais baixo (chegou primeiro) |
| `asks` | `PriorityQueue<Order>` | vendas: preço **mais baixo** primeiro; empate → `id` mais baixo |
| `pending` | `ArrayList<Order>` | ordens que chegam durante uma reserva; entram no livro no leilão |

É a regra **preço-tempo** da Euronext. Em teoria das filas: chegadas = ordens; disciplina = prioridade; atendimento = negócio com uma ordem do outro lado; desistência = expiração; bloqueio = reserva.

### 5.2 Variáveis

| Variável | Inicial | O que é |
|---|---|---|
| `lastPrice` | `initialPrice` | último preço negociado (referência do colar dinâmico) |
| `refPrice` | `initialPrice` | referência do colar estático (último preço do dia anterior ou do último leilão) |
| `ma` | `initialPrice` | média móvel exponencial do preço (para os chartists) |
| `halted` | false | `true` durante uma reserva |
| `volume` | 0 | volume acumulado; **long** desde 09/11 (com int passava de 2 147 milhões e "dava a volta") |
| `lastStaticDir` | 0 | sentido do último colar estático do dia (+1/−1), para saber se é repetido |
| `haltStart`, `prePrice` | 0 | início da reserva e preço antes dela (para o `halts.csv`) |

### 5.3 Funções

| Função | O que faz |
|---|---|
| `order(trader, side, price, qty)` | **porta de entrada**: cria o `Order` (id, preço arredondado, hora, `expiry = agora + orderLife·U(0.3, 1.7)`). Se `halted` → vai para o `pending`; senão `addToBook` + `match` |
| `addToBook(o)` | põe a ordem em `bids` (side 1) ou `asks` (side −1) |
| `match()` | enquanto não está em reserva e há ordens dos dois lados: compara a melhor compra com a melhor venda; se não se cruzam, pára; se se cruzam, o preço é o da ordem **que já estava no livro** (id mais baixo); pergunta ao `collarHit`; se não dispara, `execute` com a quantidade menor; repete |
| `collarHit(p)` | se os colares estão ligados: dinâmico = `\|p/lastPrice − 1\| > 3%`; estático = `\|p/refPrice − 1\| > 8%`. Se disparar, manda ao statechart `"STATIC_REPEAT"` (estático no mesmo sentido do anterior), `"STATIC"` ou `"DYNAMIC"`, e devolve `true` (o negócio não acontece) |
| `execute(b, a, p, q)` | `lastPrice = p`, `volume += q`, tira `q` às duas ordens, `onFill` para comprador e vendedor; a ordem que fica a 0 sai da fila (a outra fica com o resto = execução parcial) |
| `cancelAll(a)` | apaga todas as ordens de um agente |
| `bestBid()`, `bestAsk()`, `mid()`, `spread()` | melhor compra, melhor venda, ponto médio (se faltar um lado usa `lastPrice`), diferença |
| `startHalt()` | `halted = true`, guarda `haltStart` e `prePrice`, `broadcast("HALT")`, `nHalts++` |
| `runAuction()` | ver 5.5 |
| `endHalt()` | soma o tempo a `timeHalted`, escreve no `halts.csv`, `broadcast("REOPEN")` |
| `testBook()`, `check()` | os 6 testes do livro (ver 5.6) |

### 5.4 Eventos e statechart

| Evento | Quando | O que faz |
|---|---|---|
| `purgeEvent` | a cada minuto | apaga as ordens com `expiry` vencido (desistência) |
| `dayEvent` | a cada 510 min | `refPrice = lastPrice` (nova referência do colar estático) e `lastStaticDir = 0` |
| `maEvent` | a cada minuto | `ma += (lastPrice − ma) / maWindow` |
| `matchEvent` | ao reabrir | corre `match()` uma vez para negociar o que ficou cruzado |

**Statechart do Stock:**

```
Continuous ──"DYNAMIC"───────► ReservDynamic ──3 min──┐
   ▲       ──"STATIC"────────► ReservStatic  ──3 min──┤
   │       ──"STATIC_REPEAT"─► ReservStatic10 ─10 min─┤
   │                                                  ▼
   └────────── 0.01 min: runAuction(); endHalt() ── Auction
```

- `Continuous` (entrada): `halted = false`; `matchEvent.restart(0)`.
- `Reserv…` (entrada): `startHalt()`.
- `Auction` (entrada): despeja o `pending` no livro; ao sair (0.01 min depois) corre o leilão e o `endHalt`. Por isso cada reserva aparece como 3.01 ou 10.01 min.

### 5.5 Leilão de reabertura (`runAuction`)

1. Candidatos = todos os preços-limite do livro.
2. Para cada preço p: procura = compras com preço ≥ p; oferta = vendas com preço ≤ p; volume executável = mínimo das duas.
3. Escolhe o preço com **mais volume**; em empate, o **mais perto do último preço**.
4. **Colar do leilão:** o preço fica entre `lastPrice × (1 ± 6%)` (desde 04/11).
5. Executa todas as ordens que se cruzam **a esse preço único**.
6. **Se o leilão não conseguir executar dentro do colar e o livro continuar cruzado**, o `lastPrice` passa para o limite do colar (desde 08/11). Segue-se nova reserva, e o preço aproxima-se 6% de cada vez do nível a que o mercado quer negociar.
7. `refPrice = lastPrice`.

### 5.6 Testes do livro (`testBook`, 11 verificações em 6 testes)

| Teste | Verifica |
|---|---|
| 1 | compra a 0.50 e venda a 0.51 não negociam; spread = 0.01 |
| 2 | venda de 40 a 0.50 executa 40 a 0.50; ficam 60 na compra |
| 3 | prioridade de chegada (FCFS): volume 105; a segunda compra fica com 5 |
| 4 | uma compra grande "varre" dois níveis de preço: volume 255, último preço 0.52, ficam 50 a 0.52 |
| 5 | uma venda a 0.40 (−23%) é bloqueada pelo colar |
| 6 | `cancelAll` esvazia o livro |

Resultado no modelo final: **11 PASS**.

---

## 6. NoiseTrader (30): os aleatórios

- **Sem statechart.** Um evento `trade` com ritmo `noiseRate` (1 por minuto, processo de Poisson).
- Cada ordem: compra ou venda com 50%; preço = `mid × (1 + N(0, noiseSigma))`; quantidade = `U(100, 1000) × activity`.
- `cash` = 1e9, `position` = 0 (podem vender a descoberto; nunca ficam sem dinheiro).
- Continuam a mandar ordens durante as reservas (vão para o `pending`).
- **Papel:** liquidez e volume de base. Com a `activity`, o volume fica persistente de um dia para o outro e sobe com as notícias.

---

## 7. Fundamentalist (40): os racionais

- `bias` = N(0, 2%) por agente; o seu valor é `value() = fundamentalValue × (1 + bias)` (opiniões diferentes).
- `cash` = 1e9, `position` = 1 000 000 000 (sem restrição de orçamento; calibração, rondas 2–3).

**Statechart** (dentro do estado composto `Active`):

| Estado / ramo | O que faz | Sai para |
|---|---|---|
| `Watching` | espera | `decide` ao ritmo `fundRate` |
| `decide` (ramo) | compara o mid com o seu valor | `Buying` se `mid < value·(1 − 1%)` e tem dinheiro; `Selling` se `mid > value·(1 + 1%)` e tem ações; `OutOfCash` se não tem nem um nem outro; senão `Watching` |
| `Buying` | compra `100 + 20 000 × (value/mid − 1)` ações a `min(value, mid × 1.002)` | `Watching` logo a seguir |
| `Selling` | vende `100 + 20 000 × (mid/value − 1)` ações a `max(value, mid × 0.998)` | `Watching` |
| `OutOfCash` | espera (nunca acontece no modelo calibrado) | `Watching` ao fim de 60 min |
| `Halted` | parado | `Active` com "REOPEN" |

`Active → Halted` com "HALT" só se `!tradeDuringHalt`. No modelo final `tradeDuringHalt = true`, por isso **não param** durante a reserva.

**Papel:** puxam o preço para o valor (estabilizam). Quanto mais longe do valor, maior a ordem.

---

## 8. Chartist (13): os seguidores de tendência e a manada

- `cash` = 1e9, `position` = 1 000 000 000; `sellSignals` conta os avisos recebidos (o evento `forget` põe-no a 0 a cada 30 min).
- Rede small world de 6 vizinhos (construída no Main).

**Statechart** (dentro de `Active`):

| Estado / ramo | O que faz | Sai para |
|---|---|---|
| `Neutral` | espera | `decide` ao ritmo `chartRate × attention`; `herd` com "SELL_SIGNAL" (`sellSignals++`); `Panic` com "SHOCK" se o choque é negativo e com probabilidade `shockPanicProb` |
| `decide` (ramo) | compara o último preço com a média móvel | `TrendBuy` se `lastPrice > ma·(1 + 0.5%)`; `TrendSell` se `lastPrice < ma·(1 − 0.5%)`; senão `Neutral` |
| `TrendBuy` | compra até 500 ações a `mid × 1.003` | `Neutral` |
| `TrendSell` | vende até 500 ações a `mid × 0.997` e **avisa os vizinhos** (`signalNeighbours`) | `Neutral` |
| `herd` (ramo) | conta os avisos | `Panic` se `sellSignals ≥ herdThreshold` (2) e tem ações; senão `Neutral` |
| `Panic` | vende até 2000 ações a `mid × 0.99` (1% abaixo) e avisa os vizinhos | `Neutral` ao fim de `panicDuration` (10 min) |
| `Halted` | parado (só se `!tradeDuringHalt`) | `Active` com "REOPEN" |

**Papel:** amplificam os movimentos. Uma queda faz uns venderem, avisam os vizinhos, e a manada transforma-a numa cascata. É isto que os colares podem cortar.

**Atenção (ronda 8b):** depois de dias com movimentos grandes, a `attention` sobe e os chartists decidem mais vezes durante alguns dias (Barber & Odean, 2008). Foi o que deu algum clustering (0.026).

---

## 9. MarketMaker (1): o intermediário

- Estado `Quoting`: a cada minuto cancela as suas ordens e põe uma compra a `mid × (1 − 0.2%)` e uma venda a `mid × (1 + 0.2%)`, de 2000 ações cada (spread 0,4%).
- "HALT" → `Paused` (cancela as ofertas); "REOPEN" → `Quoting`.
- `cash` = 0, `position` = 0, **sem limite de inventário** e nunca sai do mercado (limitação).

---

## 10. NewsAgent (1): as notícias

| Estado | O que faz |
|---|---|
| `Calm` | ao ritmo `newsRate` (~1 por dia): `fundamentalValue *= (1 + N(0, 2%))` e `activity *= exp(activityNewsJump)` |
| `BigShock` | (com a mensagem interna "BIG_SHOCK", enviada pelo evento `shockEvent` no instante `shockTime` se `shockOn`) `fundamentalValue *= (1 + shockSize)`, `broadcast("SHOCK")` |
| `Fading` | 30 min depois do choque, durante 120 min: pequenas réplicas de `N(−0.3%, 0.5%)` ao ritmo 0.05/min; depois volta a `Calm` |

---

## 11. Mensagens

| Mensagem | Quem envia | Quem recebe | Efeito |
|---|---|---|---|
| `"DYNAMIC"`, `"STATIC"`, `"STATIC_REPEAT"` | `collarHit` | statechart do Stock | início da reserva de 3 ou 10 min |
| `"HALT"` | Stock (`startHalt`) via `broadcast` | todos | MM retira-se; os outros continuam (`tradeDuringHalt`) |
| `"REOPEN"` | Stock (`endHalt`) via `broadcast` | todos | volta a negociação contínua |
| `"BIG_SHOCK"` | `shockEvent` | NewsAgent | choque do cenário |
| `"SHOCK"` | NewsAgent via `broadcast` | todos | chartists podem entrar em pânico |
| `"SELL_SIGNAL"` | Chartist (`signalNeighbours`) | vizinhos na rede | manada |

---

## 12. Experiências

Todas com sementes fixas por replicação (`new Random(1000 + replicação)`), para serem reproduzíveis e comparáveis entre cenários.

| Experiência | O que varia | Replicações | Objetivo |
|---|---|---|---|
| `Simulation` | — (parâmetros por defeito) | 1 | correr e ver o modelo; testes |
| `Cenario1` | baseline, `nChartists` = 13 | 10 | calibração / mercado calmo |
| `Cenario2` | `collarSet` 0 vs 2, choque −10% | 30 | **choque com e sem colares** |
| `Cenario3` | `collarSet` 0 vs 2, `nChartists` = 60, choque | 30 | choque num mercado com muita manada |
| `Cenario4` | grelha: `collarSet` 0–3 × `haltShort` 3/10 × `nChartists` 10–60, choque | 30 | limiares e duração ótimos (48 combinações) |

Na calibração cada corrida tem 250 dias (127 500 min).

---

## 13. Dados e scripts Python (João)

| Script | O que faz |
|---|---|
| `download_daily.py` | preços diários do BCP (Yahoo, BCP.LS) desde 2010 |
| `archive_intraday.py` | guarda os dados de 1 minuto (o Yahoo só dá ~7 dias; corre 2× por semana) |
| `target_stats.py` | calcula os 7 factos estilizados do BCP num período |
| `make_metas.py` | junta as metas de 3 períodos (calmo 2023–24, BES 2014, COVID 2020) |
| `compare_model.py` | compara as corridas do modelo com os factos (calibração) |
| `kpis.py` | KPIs por interrupção e por corrida, validação ESMA (junta reservas a menos de 1 min) |
| `kpis_choque.py` | KPIs do choque para ficheiros grandes (Cenários 2–4) |
| `recomendacao.py` | tabela de recomendação a partir da grelha do Cenário 4 |

**Factos estilizados (alvos fixados antes da calibração, BCP 2023–2024):**

| # | Facto | BCP | Critério |
|---|---|---|---|
| 1 | Volatilidade diária | 0.0207 | ±25% |
| 2 | Curtose em excesso | 2.41 | > 1 e ±50% |
| 3 | Clustering da volatilidade (autocorr. de \|r\|) | 0.080 | > 0.05 |
| 4 | Ausência de autocorrelação dos retornos | 0.004 | entre −0.1 e 0.1 |
| 5 | Dias com \|r\| > 3% | 12.9% | ±50% |
| 6 | Correlação volume–\|r\| | 0.636 | > 0 |
| 7 | Persistência do volume | 0.470 | > 0 |

**Porquê 2023–2024:** vinha do plano do projeto e foi fixado antes de correr o modelo; é recente e sem crises do BCP. 2025 ficou de fora (e tem o choque das tarifas de abril de 2025: −9,9% a 4/4). Teste de robustez com 2023, 2024 e 2025 na secção 3.2: os factos principais são estáveis; os que variam mais (clustering, autocorrelação, persistência do volume) são os que custaram a calibrar.

---

## 14. Calibração (10 replicações × 250 dias por ronda)

| Ronda | Mudança | Factos | Nota |
|---|---|---|---|
| 0 | valores iniciais | 2/7 | volatilidade muito baixa (0.42%) |
| 1 | notícias 0.0004 → 0.002/min, ±1% → ±2% | 4/7 | |
| 2 | orçamentos × 10 | 4/7 | uma corrida caiu de 0.84 € para 0.02 € em leilões sucessivos → colar do leilão |
| 3 | sem restrição de orçamento (fundamentalistas e chartists) | 4/7 | o mercado deixou de "morrer"; volátil demais |
| 4 | chartists 30 → 15; colar do leilão ±6% | 6/7 | |
| 5 | chartists 15 → 13 | 7/7 | mas a persistência do volume era 0.001 (só passava "no papel") |
| 6 | atividade diária aleatória dos noise traders | 6/7 | volume persistente, mas a correlação volume–volatilidade caiu; uma corrida ficou presa em 1485 reservas → correção do leilão |
| 7 (7b) | atividade sobe com as notícias | 6/7 | os dois factos de volume batem a sério; clustering 0.008 |
| 8 | ritmo das notícias × atividade | 4/7 | clustering voltou (0.065) mas estragou o resto → descartada |
| **8b A2** | **+ atenção dos chartists (`attWeight` 0.6) + ordens durante a reserva** | **6/7** | **modelo final**: vol 0.0217, curtose 2.04, autocorr −0.05, dias > 3% 16.2%, clustering 0.026 |
| 8b C1 | nervosismo nos noise traders | 5/7 | clustering 0.049, mas a autocorrelação falhou (−0.1001) |

**O que falha:** o clustering (0.026 contra 0.05). Com ~250 dias por corrida, o erro de uma autocorrelação é ~0.06, por isso é o facto com mais ruído. Preferimos 6/7 honestos (os dois factos de volume a sério) a 7/7 com a persistência do volume só "no papel" (ronda 5).

---

## 15. Resultados até agora

**Cenário 2** (choque −10%, 30 + 30 replicações):
- Os colares disparam sempre: 2,6 reservas no dia do choque (~15 min).
- Não mudam significativamente a crise: queda máxima −16,6% sem colares contra −17,2% com colares (p = 0,29); fecho −11,2% contra −11,8%; recuperação de metade da queda 539 contra 741 min (p = 0,18).
- ESMA (janela de 5 min): a volatilidade desce em 44% das interrupções e o spread alarga em 52%; sem efeito sistemático.
- O choque é plausível: −17% no dia, perto dos piores dias do BCP.
- **Leitura:** os colares adiam a descoberta do preço mas não travam uma queda causada por informação nova. Atenção: o mercado do modelo é mais resistente do que o real (sem vendas forçadas, MM sempre presente), o que pode esconder parte do efeito.

**Cenários 3 e 4:** KPIs e tabela de recomendação já calculados pelo João (`data/processed/kpis_choque_*.xlsx`, `recomendacao.xlsx`).

---

## 16. Decisões tomadas (e porquê)

| Data | Decisão | Porquê |
|---|---|---|
| out | Só a Fase 1 | pedido dos professores no feedback à proposta |
| out | Livro de ordens em **Java**, testado antes de qualquer agente | feedback ("vai ser sobretudo código Java: construam-no e testem-no primeiro"); limite de 50 000 agentes da PLE |
| out | `Order` como classe Java, não agente | milhões de ordens por corrida |
| out | Prioridade preço-tempo; negócio ao preço da ordem que já estava no livro | regra da Euronext |
| out | Só ordens limitadas; uma ordem agressiva faz de ordem ao mercado | simplificação |
| out | Ordens expiram em 10–60 min | não há dados de cancelamentos; heterogeneidade |
| out | Dia contínuo de 510 min, sem leilões de abertura e fecho | simplificação; foco nas interrupções intradiárias |
| out | Colares ±3% (último preço) / ±8% (referência), 3/10 min | regras reais da Euronext para o PSI (Trading safeguards) |
| out | Leilão instantâneo que maximiza o volume; empate → mais perto do último preço | regra de leilão simplificada |
| 25/10 | Alvos do BCP 2023–24 fixados antes da calibração | evitar ajustar os alvos aos resultados |
| 27/10 | Integração de todos os agentes e das experiências 1, 2 e 4 | Fase 1 a correr |
| 04/11 | Colar do leilão ±6% (`auctionCollar`) | sem ele, leilões sucessivos levaram o preço de 0,84 € a 0,02 € |
| 08/11 | Se o leilão não executa dentro do colar, o último preço vai para o limite | uma corrida ficou presa em 1485 reservas; confirmado no Trading Manual da Euronext (2021), secção 4.2.4 |
| 09/11 | `volume` passa a long | com int passava de 2 147 milhões numa corrida de 250 dias |
| 09/11 | Reservas seguidas a menos de 1 min contam como uma só interrupção nos KPIs | consequência da regra de 08/11 |
| 11/11 | Defaults calibrados no Main (13 chartists, notícias 0.002/±2%, orçamento ilimitado, atividade) e Cenario3 | calibração fechada na ronda 7b |
| 14/11 | Modelo final = ronda 8b A2 (atenção dos chartists + ordens durante a reserva) | 6/7, melhor nos outros factos; mais defensável do que o nervosismo (C1) |
| 14/11 | 4 pressupostos relaxados: ordens durante a reserva, atenção dos chartists, atividade diária, colar do leilão | feedback do professor: rever pressupostos irrealistas e críticos |
| 14/11 | 2 pressupostos ficam como limitações: orçamento ilimitado e MM sem limite de inventário | tornam o mercado mais resistente num crash; no capítulo 10 |
| nov | Pergunta aos professores (presencial) sobre Java vs Process Modeling Library | a PML é matéria da cadeira e não a usamos |

---

## 17. Limitações (capítulo 10)

1. **Orçamento ilimitado** dos fundamentalistas e chartists: não há vendas forçadas nem margin calls.
2. **Market maker sem limite de inventário**, que nunca se retira (na realidade alargam o spread ou saem em stress).
3. **Clustering só parcial** (0.026 contra 0.080): a agitação depois do choque dissipa-se mais depressa do que na realidade; os tempos de recuperação são um limite inferior.
4. Uma só ação, sem contágio; sem leilões de abertura e fecho; choques estilizados; parâmetros comportamentais não observáveis.

As limitações 1 e 2 tornam o mercado mais resistente: as quedas e a perda de liquidez são estimativas conservadoras. Comparar cenários entre si é mais fiável do que os valores absolutos.

**Trabalho futuro:** alavancagem e margin calls; MM que se retira; mudança de estratégia (Lux & Marchesi, 1999) para o clustering; várias ações do PSI; leilões de abertura e fecho; calibração com dados intradiários.

---

## 18. Onde está cada coisa

| Ficheiro | Conteúdo |
|---|---|
| `model/Euronext_Main/Euronext_Main.alp` | modelo principal (o único a usar) |
| `docs/CONTRATO.md` | nomes de tudo (parâmetros, variáveis, mensagens, ficheiros) |
| `docs/PRESSUPOSTOS.md` | registo de pressupostos (Apêndice E) |
| `docs/FACTOS_ESTILIZADOS.md` | os 7 factos e os critérios |
| `docs/FEEDBACK_PROPOSTA.md` | feedback dos professores e o que fizemos |
| `docs/LIMITES_PLE.md` | limites da versão PLE |
| `docs/TAREFAS.md` | papéis, semanas, o que falta para o 18–19 |
| `data/processed/` | `calibracao_log.xlsx`, `kpis*.xlsx`, `recomendacao.xlsx`, metas |
| `report/` | relatório (`DSS_Report_Group2_Euronext.docx`) e os scripts que o geram |
| `sandbox/` | cópias de trabalho de cada um (histórico; não usar) |
