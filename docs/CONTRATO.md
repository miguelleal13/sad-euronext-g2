# Contrato de nomes

Este documento junta os nomes que **todos** usam no AnyLogic. Quem precisar de um nome novo acrescenta-o aqui primeiro e avisa o grupo. Se os nomes baterem, as peças de cada um encaixam no modelo principal com copiar/colar, sem erros.

Unidade de tempo: **minuto**. Um dia de negociação corresponde a **510 min** (08:00–16:30).

Âmbito: **só a Fase 1** (uma ação, livro de ordens, colares), como pediram os professores. A Fase 2 e a Fase 3 ficam como extensões opcionais e não estão no plano.

## `Order` (classe Java, não é agente)

Os professores avisaram que o livro de ordens vai ser sobretudo código Java. Além disso, um modelo cria milhões de ordens, e se cada uma fosse um agente era provável ultrapassar os limites da versão PLE do AnyLogic.

| Campo | Tipo | Significado |
|---|---|---|
| `id` | `long` | identificador único; cresce com o tempo, por isso serve de desempate (quem chegou primeiro) |
| `side` | `int` | `1` = compra, `-1` = venda |
| `price` | `double` | preço-limite (€) |
| `qty` | `int` | quantidade por executar |
| `tSubmit` | `double` | instante de submissão |
| `expiry` | `double` | instante em que é cancelada se não for executada (desistência) |
| `trader` | `Agent` | quem enviou a ordem (`null` nos testes) |

## `Stock` (agente único no `Main`, nome `stock`)

O livro de ordens é um sistema de filas em Java: `bids` e `asks` são `PriorityQueue<Order>` (prioridade por preço e, no mesmo preço, por chegada), e `pending` é a fila de espera das ordens que chegam durante uma reserva.

| Nome | Tipo | Significado |
|---|---|---|
| `bids` / `asks` | `PriorityQueue<Order>` | os dois lados do livro |
| `pending` | `ArrayList<Order>` | ordens retidas até ao leilão de reabertura |
| `lastPrice` | `double` | último preço negociado |
| `refPrice` | `double` | preço de referência estático (o do último leilão) |
| `ma` | `double` | média móvel do preço (para os investidores de tendência) |
| `halted` | `boolean` | `true` durante uma reserva (interrupção) |
| `volume` | `int` | volume acumulado |
| `lastStaticDir` | `int` | sentido do último colar estático do dia (+1/−1) |
| `statechart` | Statechart | Continuous, ReservDynamic, ReservStatic, ReservStatic10, Auction |

Funções que **os outros chamam**:
- `main.stock.order(Agent trader, int side, double price, int qty)`: cria e envia uma ordem;
- `main.stock.cancelAll(Agent a)`: cancela todas as ordens de um agente;
- `main.stock.mid()`, `bestBid()`, `bestAsk()`, `spread()`.

Funções internas: `addToBook`, `match`, `execute`, `collarHit`, `runAuction`, `startHalt`, `endHalt` e os testes `testBook` e `check`.

## Populações no `Main`

| Nome | Tipo de agente | Quantidade | Responsável |
|---|---|---|---|
| `fundamentalists` | `Fundamentalist` | `nFundamentalists` | João |
| `chartists` | `Chartist` | `nChartists` | João |
| `noiseTraders` | `NoiseTrader` | `nNoise` | Miguel (1.ª versão) e depois João |
| `marketMaker` | `MarketMaker` | 1 | Matilde |
| `news` | `NewsAgent` | 1 | Matilde |

Todos os investidores têm as variáveis `double cash` e `int position` e um statechart chamado `statechart`.

## Mensagens (`String`)

| Mensagem | Quem envia | Quem recebe | Efeito |
|---|---|---|---|
| `"HALT"` | Stock, via `main.broadcast` | todos | início da reserva |
| `"REOPEN"` | Stock, via `main.broadcast` | todos | fim do leilão: volta a negociação contínua |
| `"SHOCK"` | NewsAgent, via `main.broadcast` | todos | o valor fundamental mudou |
| `"SELL_SIGNAL"` | Chartist | vizinhos na rede (`send`) | efeito manada |
| `"DYNAMIC"`, `"STATIC"`, `"STATIC_REPEAT"` | Stock para o próprio statechart | Stock | tipo de colar disparado |
| `"BIG_SHOCK"` | evento do NewsAgent | NewsAgent | dispara o choque do cenário |

## `Main`: parâmetros

| Nome | Tipo | Valor | Notas |
|---|---|---|---|
| `nFundamentalists` | int | 40 | calibrar |
| `nChartists` | int | 30 | calibrar / cenário 3 |
| `nNoise` | int | 30 | calibrar |
| `initialPrice` | double | 0.50 | aproximadamente o BCP (€) |
| `tickSize` | double | 0.0001 | |
| `orderLife` | double | 35 | minutos de vida média de uma ordem não executada |
| `maWindow` | double | 50 | memória da média móvel `stock.ma` (minutos); `ma += (lastPrice - ma) / maWindow` |
| `runTests` | boolean | false | `true` corre o `stock.testBook()` no arranque (com `nNoise = 0`) |
| `collarSet` | int | 2 | 0 = sem colares, 1 = 2%/5%, 2 = 3%/8% (atual), 3 = 5%/10%, 4 = personalizado |
| `customDyn` / `customStat` | double | 0.03 / 0.08 | usados quando `collarSet = 4` (limiares ótimos) |
| `haltShort` / `haltLong` | double | 3 / 10 | minutos |
| `shockOn` | boolean | false | |
| `shockTime` | double | 30600 | dia 60 |
| `shockSize` | double | -0.10 | |
| `shockPanicProb` | double | 0.3 | probabilidade de um chartist entrar em pânico com o choque |
| `scenario` | String | "baseline" | |
| `fundRate` / `fundBand` | double | 0.2 / 0.01 | decisões por minuto / banda de valor |
| `chartRate` / `trendThreshold` | double | 0.2 / 0.005 | |
| `herdThreshold` | int | 2 | número de vizinhos a vender que provoca pânico |
| `panicDuration` | double | 10 | minutos |
| `noiseRate` / `noiseSigma` | double | 1 / 0.002 | |
| `mmSpread` / `mmQty` | double / int | 0.004 / 2000 | |
| `newsRate` | double | 0.0004 | pequenas notícias por minuto (cerca de 1 a cada 5 dias) |

## `Main`: variáveis e funções (cenários, CSV e KPIs: Margarida; resto: Miguel)

| Nome | Tipo | Significado |
|---|---|---|
| `fundamentalValue` | double | valor "verdadeiro" (muda com as notícias) |
| `dynamicThreshold`, `staticThreshold` | double | definidos no arranque a partir de `collarSet` |
| `collarsActive` | boolean | `false` se `collarSet = 0` |
| `label` | String | nome do cenário mais os parâmetros principais (vai para os CSV) |
| `runId` | String | identificador aleatório da corrida |
| `nextOrderId` | long | |
| `peakPrice`, `maxDrawdown` | double | queda máxima (KPI) |
| `nHalts`, `timeHalted` | int, double | KPIs das interrupções |
| `broadcast(String msg)` | função | entrega `msg` ao statechart de todos os agentes |
| `onFill(Agent t, int side, int q, double p)` | função | atualiza o `cash` e a `position` de quem negociou |
| `roundTick(double p)` | função | arredonda ao tick |

## Ficheiros de saída (`model/Euronext_Main/output/`, lidos pelos scripts do João)

| Ficheiro | Colunas (separadas por `;`) |
|---|---|
| `precos.csv` | `label;run;time;price;bid;ask;volume` (1 linha por minuto) |
| `halts.csv` | `label;run;start;end;prePrice;auctionPrice` (1 linha por interrupção) |
