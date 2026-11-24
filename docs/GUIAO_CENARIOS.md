# Guião passo a passo até à entrega

**Grupo 2 · SAD · 24 de novembro de 2026 · entrega a 2 de dezembro**

Este guião diz, para cada passo, quem faz, o que fazer exatamente e como saber que ficou bem. Segue a ordem: cada passo precisa dos anteriores.

**Regras para todos**

- Antes de começar qualquer passo: `git pull`.
- O modelo principal é **um só**: `model/Euronext_Main/Euronext_Main.alp`. Ninguém o altera diretamente exceto o Miguel. Quem precisar de mudar o modelo faz uma cópia em `sandbox/<nome>/`, muda lá, faz commit da cópia e avisa o Miguel, que passa a mudança para o principal.
- Os ficheiros das corridas (`precos.csv`, `halts.csv`) são enormes e **não vão para o GitHub** (estão no `.gitignore`). Vão para o GitHub só os resultados já processados, em `data/processed/`.
- Os ficheiros de saída são escritos em modo **acrescentar** (`WRITE_APPEND`): se não forem apagados ou mudados de sítio entre experiências, as corridas de experiências diferentes ficam misturadas no mesmo ficheiro.

**Números que vão ser precisos**

- No ficheiro `data/processed/choques_reais.csv` os dias estão numerados de 0 a 508 (2/01/2023 a 30/12/2024).
- 13/06/2024 é o **dia 369**. 5/09/2024 é o **dia 429** (= 369 + 60). 27/11/2024 é o **dia 488** (= 369 + 119).
- Preço de fecho do BCP a 12/06/2024 (véspera do primeiro dia): **0,3494 €**.
- Um dia de negociação tem 510 minutos. 60 dias = **30 600 min**. 120 dias = **61 200 min**.

---

## Passo 1 · Miguel · Fechar o modelo final (hoje)

O modelo da ronda 11 já está no lugar do principal no computador do Miguel, mas ainda não foi para o GitHub.

1. No AnyLogic, se o `Euronext_Main` estiver aberto: na árvore **Projects**, botão direito em **Euronext_Main** → **Close**. Se perguntar se quer gravar, **No**.
2. **File → Open** → `C:\Users\ASUS\Desktop\MSc\SAD\sad-euronext-g2\model\Euronext_Main\Euronext_Main.alp`.
3. Em **Main → Parameters**, confirmar que existem `realShocks`, `shocksFile`, `useResid` e `residBlock` (é o modelo novo).
4. Clicar em `runTests` e marcar a caixa (**true**). Clicar em `nNoise` e pôr **0**.
5. Setinha ao lado do ▶ verde → **Simulation**. Na consola têm de aparecer **11 linhas PASS**. Se aparecer "Erro a ler os CSVs", tirar print e mandar ao Claude.
6. Parar a simulação (■). Pôr `runTests` = **false** e `nNoise` = **30**.
7. **Ctrl+S** e pedir ao Claude "commit". O Claude confirma os parâmetros no ficheiro antes de enviar.

**Está feito quando:** o commit do modelo final está no GitHub.

## Passo 2 · Grupo · Aprovar a data do choque (hoje)

Responder ao João no grupo:

> "Concordo com o choque a 5/09/2024, janela de 13/06/2024 a 27/11/2024 (dias 369 a 488 do ficheiro de choques), preço inicial 0,3494 €."

A regra que levou a esta data (nenhuma notícia 5 dias antes e 10 depois, menor volatilidade do BCP e do mercado à volta) tem de ficar escrita no relatório, secção 7, como foi escolhida **antes** de correr os cenários.

## Passo 3 · Matilde · Parâmetro `startDay` (amanhã)

**Objetivo:** o modelo poder começar num dia qualquer do ficheiro de choques, em vez de começar sempre a 2/01/2023.

Fazer numa **cópia**: `git pull`, copiar `model/Euronext_Main/Euronext_Main.alp` para `sandbox/matilde/Euronext_startDay.alp` e abrir a cópia.

### 3.1 Criar o parâmetro

1. Abrir o agente **Main**. Na **Palette** → **Agent** → arrastar um **Parameter** para fora do retângulo azul, junto aos outros parâmetros.
2. Nas Properties: **Name** = `startDay`, **Type** = `int`, **Default value** = `0`.

Com `0` o modelo começa a 2/01/2023 como até agora, por isso a calibração e os testes continuam a funcionar.

### 3.2 Somar o `startDay` nos três sítios onde o modelo calcula o dia

O modelo calcula "em que dia estou" com `time() / 510`. Esse cálculo aparece em três eventos. Em cada um, somar `startDay`:

**a) Main → evento `activityEvent`** (Action). Trocar a primeira linha:

```java
int d = (int) Math.floor(time() / 510 + 1e-9);
```

por:

```java
int d = startDay + (int) Math.floor(time() / 510 + 1e-9);
```

**b) NewsAgent → evento `sectorEvent`** (Action). Trocar:

```java
int d = (int) Math.floor(time() / 510);
```

por:

```java
int d = main.startDay + (int) Math.floor(time() / 510);
```

**c) NewsAgent → evento `newsEvent`** (Action). Trocar:

```java
int d = (int) Math.floor(time() / 510 + 1e-9);
```

por:

```java
int d = main.startDay + (int) Math.floor(time() / 510 + 1e-9);
```

Não mexer em mais nada nestes eventos.

### 3.3 Proteção contra dias em falta

No **Main → On startup**, **logo a seguir** ao bloco `try { ... } catch (Exception e) { ... }` que lê os CSV, acrescentar:

```java
double stopT = getEngine().getStopTime();
int needed = Double.isInfinite(stopT) ? 1 : (int) Math.ceil(stopT / 510);
if (startDay < 0 || startDay + needed > shockSector.length)
    error("startDay = " + startDay + " com " + needed + " dias passa o fim de " + shocksFile + " (" + shockSector.length + " dias)");
```

Assim, se alguém puser um `startDay` que, somado aos dias da corrida, passa do fim do ficheiro, o modelo para logo com uma mensagem clara em vez de correr com dias em falta.

### 3.4 Testar

1. Na experiência **Simulation**, mudar o Stop time para **61 200** (120 dias).
2. Pôr nos parâmetros do Main: `startDay` = **369**, `initialPrice` = **0.3494**, `shockOn` = **true** (o `shockTime` fica 30 600).
3. Correr. Verificar: o preço começa perto de 0,35 €; na consola aparece "BIG SHOCK" a t = 30 600; a simulação chega ao fim sem erros.
4. Pôr `startDay` = **500** e correr: tem de aparecer logo o erro do passo 3.3.
5. Repor tudo como estava: `startDay` = **0**, `initialPrice` = **0.1464**, `shockOn` = **false**, Stop time da Simulation como estava.
6. Gravar, fazer commit **só da cópia** (`sandbox/matilde/Euronext_startDay.alp`) e avisar o Miguel.

**Está feito quando:** a cópia com o `startDay` está no GitHub e os testes 3.4 correram bem.

## Passo 4 · Miguel · Integrar o `startDay` no modelo principal (amanhã)

1. `git pull` e pedir ao Claude: "a Matilde fez o startDay em `sandbox/matilde/Euronext_startDay.alp`, passa para o principal". O Claude compara os ficheiros, confirma que só mudou o que devia e faz a passagem.
2. Fechar o principal no AnyLogic sem gravar e voltar a abrir.
3. Correr os testes do livro (como no passo 1, pontos 4 a 6): 11 PASS.
4. Ctrl+S e pedir "commit".
5. Avisar o grupo: "o principal já tem o `startDay`; façam `git pull`".

**Regra a registar no CONTRATO (o Claude faz):** sempre que se muda o `startDay` ou o `shocksFile`, muda-se também o `initialPrice` para o fecho do BCP na véspera do primeiro dia.

## Passo 5 · João · Fixar os indicadores antes de correr (amanhã)

Tal como os factos estilizados foram fixados antes da calibração, os indicadores dos cenários têm de ser fixados **antes** de ver os resultados. Escrever num ficheiro (por exemplo `docs/KPIS_CENARIOS.md`) e fazer commit **antes** das corridas, com a data.

**5.1 O que é um crash** (para a probabilidade da pergunta 1 da proposta). Uma proposta, a decidir pelo João:

- Crash = queda máxima no dia do choque **superior a 15%** (o choque de informação é −10%, por isso um crash é uma queda pelo menos 5 pontos maior do que a notícia justifica).
- Probabilidade de crash = percentagem das 30 corridas de um cenário em que isso acontece.
- Opcional: medir também nos 5 dias seguintes ao choque.

**5.2 Liquidez** (para a pergunta 2):

- spread relativo médio fora das reservas, no dia do choque e nos 5 dias seguintes;
- volume no dia do choque e nos 5 dias seguintes;
- tempo total em reserva (minutos) no dia do choque.

**5.3 Estabilidade:**

- queda máxima no dia do choque;
- retorno no fecho do dia do choque e 5 dias depois;
- tempo até recuperar metade da queda.

**5.4 Análise multicritério** (prometida na proposta): normalizar cada indicador entre 0 e 1 em todos os cenários, dar um peso à estabilidade e outro à liquidez (por exemplo 50/50, e testar 70/30 e 30/70), e ordenar os conjuntos de colares.

**5.5** Acrescentar ao `scripts/kpis_choque.py` o que faltar (a probabilidade de crash, se ainda não estiver).

**Está feito quando:** as definições estão no GitHub com data anterior às corridas.

## Passo 6 · Margarida · Preparar as experiências (amanhã, depois do passo 4)

Fazer no **modelo principal** só depois de o Miguel confirmar o passo 4. Como mexe só nas experiências, fazer numa cópia (`sandbox/margarida/Euronext_cenarios.alp`) e o Miguel passa-as para o principal, ou combinar com o Miguel fazer diretamente no principal.

**6.1 Parâmetros comuns** a todas as experiências de cenários (em cada experiência, na tabela **Parameters**, tipo **Fixed** salvo indicação):

- `startDay` = **369**
- `initialPrice` = **0.3494**
- `shockTime` = **30600**
- **Model time → Stop**: **61 200**
- **Replications**: **30** por iteração
- **Randomness**: Custom generator `new Random(1000 + getCurrentReplication())` (já está assim)

**6.2 Base (experiência nova `Base`).** Botão direito em Euronext_Main → **New → Experiment → Parameter Variation**, Top-level agent **Main**, nome `Base`. Parâmetros: `scenario` = `"base"`, `shockOn` = **false**, `collarSet` Range **0 a 2, passo 2**, mais os comuns. Serve de referência sem choque.

**6.3 Cenário 2.** Já existe. Confirmar: `scenario` = `"shock"`, `shockOn` = **true**, `collarSet` Range **0 a 2, passo 2**, mais os comuns.

**6.4 Cenário 3 com a manada.** Já existe. Confirmar `scenario` = `"herd"`, `shockOn` = **true**, `nChartists` = **60**, `collarSet` Range **0 a 2, passo 2**, mais os comuns. **Acrescentar:** `herdThreshold` Range **1 a 4, passo 1** (1, 2, 3 e 4 avisos). Ficam 2 × 4 = 8 combinações × 30 = 240 corridas.

**6.5 Cenário 4 (grelha).** Já existe: `collarSet` 0 a 3, `haltShort` 3 e 10, `nChartists` 10 a 60. Só acrescentar os parâmetros comuns.

**6.6 Limiares ótimos (experiência nova `Limiares`).** `scenario` = `"limiares"`, `shockOn` = **true**, `collarSet` = **4**, `customDyn` Range **0.02 a 0.05, passo 0.01**, `customStat` Range **0.06 a 0.12, passo 0.02**, mais os comuns. São 4 × 4 = 16 combinações.

**6.7 Medir o tempo antes de lançar tudo.** Correr **uma** corrida do Cenário 2 (1 replicação) e cronometrar. Multiplicar pelo número de corridas de cada experiência. Se não couber no tempo, reduzir **primeiro** as replicações da experiência `Limiares` (por exemplo para 10) e **nunca** as do Cenário 2.

**6.8** Gravar, commit da cópia, avisar o Miguel.

## Passo 7 · João e Margarida · Teste fora da amostra 2020–2021 (já em curso)

Este teste já está a ser feito. Fica aqui o resumo do que tem de ser cumprido, igual ao teste de 2025–2026:

1. Experiência igual à `Teste`, com `shocksFile` = `"choques_reais_teste2020.csv"`, `startDay` = **0**, `initialPrice` = fecho do BCP na véspera do primeiro dia do ficheiro, Stop = número de dias do ficheiro × 510.
2. 10 replicações. Correr **uma vez**, sem mexer em nenhum parâmetro depois de ver o resultado.
3. Calcular os 7 factos com o `compare_model.py` e comparar com o BCP de 2020–2021.
4. O resultado entra na secção 6.4 do relatório, bata ou não bata. Se não bater, explicar porquê (por exemplo, o tamanho dos movimentos não explicados na COVID).

## Passo 8 · João · Verificação ao minuto

**Porquê:** a calibração é toda com dados diários, mas os colares atuam ao minuto.

**Dados reais:** `data/raw/bcp_1min.csv`, de 22/10/2026 até hoje (cerca de 7700 minutos, com falhas; continuar a correr o `archive_intraday.py` duas vezes por semana).

**Dados do modelo:** `precos.csv` da experiência `Base` com colares (`collarSet` = 2), 1 linha por minuto.

**Como comparar:**

1. Retornos de 1 minuto: `log(preço do minuto / preço do minuto anterior)`, **só dentro do mesmo dia** (no modelo, dentro de cada bloco de 510 minutos; no real, dentro de cada sessão).
2. Tirar os primeiros e os últimos 5 minutos de cada dia (o modelo não tem leilões de abertura e fecho, o real tem).
3. Tirar os minutos sem negócio do real (volume 0) ou tratá-los da mesma forma nos dois.
4. Comparar: desvio-padrão dos retornos de 1 minuto, curtose, percentagem de minutos com retorno zero, e a variância média por blocos de 30 minutos ao longo do dia.
5. Atenção ao nível de preço: o BCP está a cerca de 1,08 € em 2026 e o modelo a cerca de 0,35 €, por isso o tick (0,0001 €) pesa três vezes mais no modelo. Comparar em retornos e não em euros, e dizer isto no relatório.
6. Escrever o resultado na secção 6.3, mesmo que não bata perfeitamente (fica como limitação).

## Passos 9 a 11 · Margarida · As corridas

Para **cada** experiência (Base, Cenário 2, Cenário 3, Cenário 4, Limiares), por esta ordem:

1. Apagar (ou mudar de nome) `model/Euronext_Main/output/precos.csv` e `halts.csv`, para não misturar experiências.
2. Correr a experiência até ao fim.
3. Copiar a pasta `output` para uma pasta com o nome da experiência, fora do repositório ou em `sandbox/margarida/<experiência>/` (que não vai para o GitHub).
4. Correr `python scripts/kpis_choque.py <pasta>` (para a Base, que não tem choque, usar o mesmo instante 30 600 como referência).
5. Fazer commit do Excel que sai em `data/processed/` e avisar o João.

**Passo 11 · Análise de sensibilidade.** Repetir o **Cenário 2** mudando cada um dos 5 parâmetros que mais pesam, um de cada vez, para −50% e +50% do valor:

- `orderLife` (35 → 17.5 e 52.5)
- `noiseRate` (1 → 0.5 e 1.5)
- `nChartists` (13 → 7 e 20)
- `trendThreshold` (0.005 → 0.0025 e 0.0075)
- `nNoise` (30 → 15 e 45)

Para cada um: experiência com o parâmetro em Range com os dois valores, `collarSet` 0 e 2, e os comuns. Se o tempo for curto, usar 10 replicações. O que interessa é saber se **o efeito dos colares** (a diferença entre com e sem colares) muda de sinal ou de tamanho.

## Passo 12 · João · Resultados

1. Juntar os KPIs de todas as experiências.
2. Para cada cenário: média e intervalo de confiança de 95% de cada indicador, com e sem colares, e teste da diferença (t de Welch).
3. **Pergunta 1:** tamanho da queda e probabilidade de crash em função do número de chartists (Cenário 4) e da manada (Cenário 3).
4. **Pergunta 2:** queda evitada e perda de liquidez por conjunto de colares e duração (Cenário 4 e Limiares), análise multicritério e tabela de recomendação.
5. Sensibilidade: se a recomendação se mantém quando os 5 parâmetros mudam.

## Passo 13 · Miguel · Objetivos do relatório (secção 1.2)

Pedir ao Claude para aplicar estas mudanças em `report/conteudo_miguel_intro.ps1` e regenerar o relatório:

- Ponto 1: "reproduce the main statistical properties (stylised facts) of the BCP share in 2023–2024, driven by the real information that reached the market, and check them out of sample in other periods;"
- Ponto 5: "search for the thresholds that minimise the maximum fall for an acceptable loss of liquidity (traded volume, spread and time without trading)."
- Ponto 3 fica como está (é cumprido pelos passos 5 e 6.4).

## Passo 14 · João · Secção 6.3

Acrescentar um parágrafo que diga o que a calibração prova: o modelo recebe a informação real e os investidores artificiais transformam-na em preços sem distorcer as suas propriedades; os colares atuam precisamente nessa transformação. Juntar o resultado da verificação ao minuto (passo 8).

## Passo 15 · Grupo · Conclusões

1. Responder à **pergunta 1** da proposta com a mesma formulação: "How do the share of trend followers and herding affect the probability and size of crashes?"
2. Responder à **pergunta 2**: "Which collar thresholds and reservation durations reduce the maximum fall the most without excessively harming liquidity?"
3. Dizer que as perguntas 3 e 4 (alavancagem e contágio) ficaram fora do âmbito, por indicação dos professores, e ligá-las às limitações do capítulo 10.
4. Uma frase de recomendação clara, sem dar conselho de investimento.

## Passo 16 · Miguel · Congelar e rever (até 1 de dezembro)

1. Depois das últimas corridas, ninguém mexe mais no modelo principal. Commit final com a mensagem "modelo congelado".
2. Regenerar o relatório e ler tudo do princípio ao fim: números iguais entre o texto e as tabelas, referências a figuras e tabelas sem erros, todas as secções preenchidas.
3. Confirmar que o modelo do GitHub abre e corre num computador limpo (por exemplo o de outro elemento do grupo).

---

## Só se sobrar tempo

- **Regimes de mercado:** correr o Cenário 2 com os movimentos não explicados multiplicados por 0,7 (calmo), 1 (atual) e 2 (crise bancária). Precisa de um parâmetro novo no modelo (Miguel).
- **Cenário 2 numa janela calma de 2025–2026**, para mostrar que o resultado vale "hoje".
- **Comparar a informação que entra com o preço que sai**, para mostrar o que os investidores acrescentam (João).
- **Atualizar os resumos em PDF do Miguel**, que ainda falam do modelo antigo.

**Atenção:** os resultados antigos dos cenários foram feitos com o modelo antigo e já não valem.
