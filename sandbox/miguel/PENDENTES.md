# Pendentes do Miguel

Coisas do modelo que ficaram "provisórias" e que tenho de mudar mais tarde. Risco quando fizer.

## Semana 2: colares, reservas e leilão
- [x] **`collarHit`** (Stock): trocar `return false;` pelo código dos colares (guião, secção 6).
- [x] **Statechart do Stock**: Continuous → ReservDynamic / ReservStatic / ReservStatic10 → Auction → Continuous (guião, secção 6).
- [x] Funções **`startHalt`**, **`endHalt`** e **`runAuction`** no Stock (guião, secção 6).
- [x] Correr os testes (`runTests = true`, `nNoise = 0`): o **teste 5** tem de passar a **OK**.

## Quando a Margarida entregar a instrumentação (semana 2) ✅ feito a 27/10
- [x] Copiar do Main dela: os parâmetros `collarSet`, `customDyn`, `customStat` e `scenario`, as variáveis `label`, `runId`, `peakPrice`, `maxDrawdown`, `nHalts` e `timeHalted`, os 2 Text File (`pricesFile`, `haltsFile`) e o `logEvent`.
- [x] **On startup** do Main: juntar o código dela (o `switch (collarSet)` e o `label`) ao meu `if (runTests) stock.testBook();`.
- [x] **On destroy** do Main: `pricesFile.close(); haltsFile.close();`
- [x] **`startHalt`** (Stock): por agora tem só 4 linhas. Acrescentar antes do `main.broadcast("HALT");`:
  ```java
  main.nHalts++;
  ```
- [x] **`endHalt`** (Stock): por agora tem só o `broadcast`. Acrescentar antes do `main.broadcast("REOPEN");`:
  ```java
  main.haltsFile.println(main.label + ";" + main.runId + ";" + haltStart + ";" + time() + ";"
                         + prePrice + ";" + lastPrice);
  main.timeHalted += time() - haltStart;
  ```

## Experiências da Margarida (quando entrar a Matilde)
- [x] (27/10) Copiar do modelo `sandbox/margarida/margarida.alp` as experiências **Cenario1, Cenario2 e Cenario4** (Projects → Ctrl+C → Ctrl+V no `Euronext_Main`). Só depois de existirem os parâmetros da Matilde (`shockOn`, `shockTime`, `shockSize`…), senão não compilam.

## Relatório
- [x] Secções do João juntas ao relatório principal (26/10).
- [x] Escritas: 1 Introduction, 2 Problem Description, 4.1 Modelling Approach (26/10).

## Sempre que entrar um agente novo (semanas 2–3)
Integrados a 27/10: Fundamentalist e Chartist (João), com a rede dos chartists no On startup. NewsAgent e MarketMaker (Matilde) e experiências Cenario1/2/4 (Margarida) também integrados a 27/10. Falta: dashboard e ecrã inicial (Matilde) e Cenario3 (Margarida).

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
- [x] Tempo de uma corrida de 120 dias (só 30 noise traders, sem log): **< 5 s** em virtual time (23/10).
- [ ] **Voltar a cronometrar depois da integração** (semana 3): com ~100 agentes e o log da Margarida a cada minuto vai ser mais lento. Passar o tempo à Margarida para ela planear as replicações.
- [x] Limites da PLE confirmados (23/10): ver `docs/LIMITES_PLE.md`. Nenhum limite nos afeta; regra: máximo 10 tipos de agente (vamos em 7) e não criar agentes durante a simulação.

## Para a calibração (passar ao João e à Margarida) — 1.ª corrida do modelo completo, 27/10
Corrida: nNoise 30, nFundamentalists 40, nChartists 30, choque de −10% ao minuto 600. O mecanismo funciona (queda em cascata de 0.50 para ~0.41, colares de 3 e 10 min, estabilização), mas:
- [ ] Há reservas antes do choque (min 33, 70, 198, 244); a primeira dura 10 min. Num mercado calmo deviam ser raras → pouca liquidez perto do preço? (`nNoise`, `mmQty`, `orderLife`).
- [ ] Depois da queda o preço anda "aos degraus" (poucos negócios) → ver `cash`/`position` dos fundamentalistas e chartists depois do choque (sem dinheiro / sem ações?).
- [ ] O preço estabiliza em ~0.43, abaixo do novo valor fundamental (~0.44–0.45).

## Para outros confirmarem (não é código meu)
- [ ] João: confirmar no documento *Trading safeguards* da Euronext os valores dos colares para o BCP (±3% / ±8%, 3 / 10 min) e citar com data.
- [ ] João: pressuposto nº 3 (só negociação contínua 08:00–16:30; sem pré-abertura nem leilões de abertura e fecho).
