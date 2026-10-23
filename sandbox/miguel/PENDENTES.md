# Pendentes do Miguel

Coisas do modelo que ficaram "provisórias" e que tenho de mudar mais tarde. Risco quando fizer.

## Semana 2: colares, reservas e leilão
- [x] **`collarHit`** (Stock): trocar `return false;` pelo código dos colares (guião, secção 6).
- [x] **Statechart do Stock**: Continuous → ReservDynamic / ReservStatic / ReservStatic10 → Auction → Continuous (guião, secção 6).
- [x] Funções **`startHalt`**, **`endHalt`** e **`runAuction`** no Stock (guião, secção 6).
- [x] Correr os testes (`runTests = true`, `nNoise = 0`): o **teste 5** tem de passar a **OK**.

## Quando a Margarida entregar a instrumentação (semana 2)
- [ ] Copiar do Main dela: os parâmetros `collarSet`, `customDyn`, `customStat` e `scenario`, as variáveis `label`, `runId`, `peakPrice`, `maxDrawdown`, `nHalts` e `timeHalted`, os 2 Text File (`pricesFile`, `haltsFile`) e o `logEvent`.
- [ ] **On startup** do Main: juntar o código dela (o `switch (collarSet)` e o `label`) ao meu `if (runTests) stock.testBook();`.
- [ ] **On destroy** do Main: `pricesFile.close(); haltsFile.close();`
- [ ] **`startHalt`** (Stock): por agora tem só 4 linhas. Acrescentar antes do `main.broadcast("HALT");`:
  ```java
  main.nHalts++;
  ```
- [ ] **`endHalt`** (Stock): por agora tem só o `broadcast`. Acrescentar antes do `main.broadcast("REOPEN");`:
  ```java
  main.haltsFile.println(main.label + ";" + main.runId + ";" + haltStart + ";" + time() + ";"
                         + prePrice + ";" + lastPrice);
  main.timeHalted += time() - haltStart;
  ```

## Sempre que entrar um agente novo (semanas 2–3)
Tirar as `//` da linha desse agente em:
- [ ] **`onFill`** (Main): Fundamentalist · Chartist · MarketMaker
- [ ] **`broadcast`** (Main): fundamentalists · chartists · marketMaker · news
- [ ] Criar a população com o nome do CONTRATO e **Initial number of agents** = parâmetro (`nFundamentalists`, `nChartists`, …), nunca um número fixo.
- [ ] Copiar os parâmetros novos que a pessoa criou no Main dela.
- [ ] Quando entrar o Chartist: acrescentar `+ "_n" + nChartists` ao `label` (On startup).
- [ ] Depois de cada integração: Build → `testBook` (tudo OK) → Run → pedir ao Claude para fazer commit.

## Aspeto visual (semana 3, com a Matilde)
- [ ] **Localização das populações**: `noiseTraders` (e as próximas) estão fora do retângulo azul, por isso os bonecos não aparecem na simulação. A Matilde define o layout; mover para onde ela disser.
- [ ] **Time Plot provisório** do preço: a Matilde substitui pelo dashboard final. Apagar o meu quando o dela entrar.
- [ ] Parâmetros, variáveis e funções ficam **fora** do retângulo azul (o retângulo é o ecrã da simulação).

## Configuração
- [ ] `runTests`: tem de ficar **false** no modelo do GitHub (só passa a true quando corro os testes).
- [ ] Simulation: Stop time **61200** (120 dias). A Margarida usa 127500 (250 dias) no baseline, nas experiências dela.
- [ ] Semana 4: confirmar no site da AnyLogic os **limites da PLE** (duração das corridas, número de agentes, experiências disponíveis) e avisar a Margarida.

## Para outros confirmarem (não é código meu)
- [ ] João: confirmar no documento *Trading safeguards* da Euronext os valores dos colares para o BCP (±3% / ±8%, 3 / 10 min) e citar com data.
- [ ] João: pressuposto nº 3 (só negociação contínua 08:00–16:30; sem pré-abertura nem leilões de abertura e fecho).
