# Registo de pressupostos

Os dados públicos sobre o livro de ordens e o comportamento dos investidores na Euronext Lisboa são escassos (comentário dos professores). Por isso, tudo o que não vem diretamente de dados fica registado aqui: o que assumimos, porquê e como o testamos. Esta tabela entra no relatório.

**Responsável:** João. Quem inventar um número acrescenta uma linha. Depois da calibração, atualiza-se a coluna *Valor*.

**Teste:** **C** = calibrado contra os factos estilizados · **S** = entra na análise de sensibilidade da Margarida · **V** = coberto pelos testes de verificação da Matilde · **—** = fixo (regra ou simplificação assumida).

| # | Pressuposto | Valor | Porquê / fonte | Teste |
|---|---|---|---|---|
| 1 | Uma só ação (BCP), sem contágio a outras | — | Âmbito da Fase 1, como os professores pediram | — |
| 2 | Regras dos colares para o PSI: ±3% dinâmico (face ao último preço), ±8% estático (face ao preço de abertura ou à referência do dia anterior), reserva de 3 min, 10 min se houver uma reserva estática consecutiva no mesmo sentido, leilão de reabertura | regras reais | Euronext, *Trading safeguards* (consultado a 31/10/2026) e anexo aos Trading Manuals 4-01 (2025), grupo P0 Equities PSI | — |
| 3 | O dia de negociação tem 510 min seguidos (negociação contínua das 08:00 às 16:30 em Lisboa = 09:00–17:30 CET); não há noite, pré-abertura, leilão de abertura nem leilão de fecho (na realidade há pré-abertura desde as 06:30 e leilão de fecho às 16:35, hora de Lisboa) | 510 | Horário confirmado no anexo aos Trading Manuals da Euronext (2025); o preço de referência estático muda a cada 510 min | — |
| 4 | Preço inicial e valor fundamental inicial | 0.50 € | Ordem de grandeza do BCP | — |
| 5 | Tick | 0.0001 € | Simplificação (a Euronext usa uma tabela de ticks) | — |
| 6 | As ordens são todas limitadas; uma ordem agressiva faz de ordem ao mercado | — | Simplificação do livro | — |
| 7 | Tempo de vida das ordens (`orderLife`) | 35 min | Não há dados de Lisboa sobre cancelamentos | C, S |
| 8 | Número de cada tipo de investidor (`nFundamentalists`, `nChartists`, `nNoise`) | 40 / **13** / 30 | Literatura de mercados baseados em agentes (ex.: Lux & Marchesi, 1999); chartists reduzidos de 30 para 13 na calibração (rondas 4 e 5) | C |
| 9 | Banda e ritmo do fundamentalista (`fundBand`, `fundRate`) | 0.01 / 0.2 | Literatura (ex.: Chiarella & Iori, 2002) | C, S |
| 10 | Erro de avaliação de cada fundamentalista (`bias`) | Normal(0, 2%) | Heterogeneidade de opiniões | — |
| 11 | Ritmo e limiar de tendência do chartist (`chartRate`, `trendThreshold`) | 0.2 / 0.005 | Literatura (ex.: Lux & Marchesi, 1999) | C, S |
| 12 | Memória da média móvel usada pelos chartists (`maWindow`) | 50 min | Horizonte intradiário intermédio: curto demais reage a ruído; longo demais não vê uma queda a meio da sessão | C, S |
| 13 | Rede de contactos dos chartists | small world, 6 vizinhos | Como no Market Model das aulas; só os vizinhos que são `Chartist` recebem o sinal | — |
| 14 | Limiar de manada (`herdThreshold`) e duração do pânico (`panicDuration`) | 2 / 10 min | Não observável | C, S |
| 15 | Ruído: ritmo e dispersão de preços (`noiseRate`, `noiseSigma`) | 1 / 0.2% | Dá volume e liquidez de base | C, S |
| 16 | Criador de mercado: spread e quantidade (`mmSpread`, `mmQty`) | 0.4% / 2000 | Não há dados; testado em valores extremos | S, V |
| 17 | Choque de notícia estilizado (`shockSize`, `shockTime`) | −10%, dia 60 | Inspirado no BES; **não** é uma reprodução do crash | S |
| 18 | Probabilidade de pânico de um chartist com o choque (`shockPanicProb`) | 0.3 | Não observável | S |
| 19 | Notícias (`newsRate`) e o seu tamanho | **~1 por dia (0.002/min), ±2%** | Calibrado na ronda 1 (era ~1 a cada 5 dias, ±1%) | C |
| 20 | Fundamentalistas e chartists sem restrição de orçamento (`cash`, `position`) | **1e9 € / 1 000 000 000 ações** | Calibrado nas rondas 2 e 3: com 5000 € / 10 000 ações (e mesmo 10×) os agentes esgotavam-se e o mercado "morria" a meio do ano | C |
| 21 | Ordens do fundamentalista: quantidade 100 + 20 000 × desvio ao valor; preço até ±0.2% do mid | — | Quanto mais longe do valor, maior a ordem | C |
| 22 | Fundamentalista sem dinheiro nem ações espera antes de voltar a tentar | 60 min | Simplificação; deixou de acontecer no modelo calibrado | — |
| 23 | Ordens do chartist: tendência até 500 ações a ±0.3% do mid; pânico até 2000 ações a −1% do mid | — | O pânico vende muito e abaixo do mercado | C |
| 24 | Os chartists esquecem os sinais de venda (`forget`) | 30 min | Não observável | — |
| 25 | Noise traders sem restrições de dinheiro nem de ações (podem vender a descoberto) | cash 1e9, position 0 | Fonte de liquidez de base | — |
| 26 | Quantidade das ordens dos noise traders | Uniforme(100, 1000) **× atividade do dia** | Calibrado (ronda 7): dá persistência ao volume e liga-o às notícias | C |
| 27 | Vida de cada ordem: `orderLife` × Uniforme(0.3; 1.7) | 10–60 min | Heterogeneidade nos cancelamentos | C, S |
| 28 | Colar dinâmico medido contra o último preço negociado | `lastPrice` | Regra da Euronext: o preço de referência dinâmico é o último preço negociado | V |
| 29 | Leilão de reabertura instantâneo: preço que maximiza o volume; em empate, o mais perto do último preço | — | Regra de leilão simplificada | V |
| 30 | Durante a reserva, todos os agentes continuam a pôr ordens, que ficam na fila `pending` para o leilão de reabertura. **Relaxado na ronda 8b** (antes os fundamentalistas e os chartists paravam) | `tradeDuringHalt` = true | Euronext Trading Manual §4.2.3: durante a reserva os membros podem introduzir, modificar e cancelar ordens. Pressuposto crítico identificado após o feedback do professor | C |
| 31 | Período de stress BES começa a 15/07/2014 (e não a 01/06) | 15/07–30/09/2014 | Os preços ajustados do Yahoo mostram subidas falsas (+12% e +24%) no fim de junho e início de julho, por causa do aumento de capital do BCP | — |
| 32 | Dados reais: preços diários ajustados do Yahoo Finance (BCP.LS) | 2010–2026 | Única fonte gratuita com histórico longo | — |
| 33 | As reservas duram exatamente o mínimo da Euronext; na realidade podem ser prolongadas | 3 / 10 min | Simplificação | S |
| 34 | O preço de referência estático é o último preço do dia anterior e passa a ser o preço do leilão de reabertura depois de cada reserva; a Euronext define-o como o preço de abertura do dia ou a referência do dia anterior | — | Simplificação (o modelo não tem leilão de abertura) | V |
| 35 | Colar do leilão de reabertura (`auctionCollar`): o preço do leilão fica a ±6% do último preço antes da reserva | ±6% | Regra da Euronext para os títulos do PSI (anexo aos Trading Manuals, coluna Col U). Introduzido a 04/11: sem ele, leilões sucessivos levavam o preço de 0,84 € a 0,02 € | V |
| 36 | Se o leilão de reabertura não conseguir executar dentro do colar de ±6% (o livro continua cruzado fora do intervalo), o último preço passa para o limite do colar e segue-se nova reserva. Assim a referência aproxima-se 6% em cada leilão do preço a que o mercado quer negociar | limite do colar | Aproxima a extensão da reserva da Euronext (reserva prolongada com limites ajustados). Introduzido a 08/11: sem isto, a corrida 47d0b7e6 da ronda 6 ficou presa em 1485 reservas com o preço congelado em 0,5638 €. **Confirmado (João, 09/11) no Trading Manual da Euronext (versão de 05/07/2021), secção 4.2.4:** *"Euronext will modify the thresholds and, depending on the direction of the market, either the upper or lower thresholds will become the new reference price"*; e *"Euronext may in certain market conditions modify the length of the reservation period and may accept fluctuation ranges broader than those stipulated"*. Consequência para os KPIs: reservas seguidas (menos de 1 min entre elas) contam como uma só interrupção no `kpis.py` | V |
| 37 | Nível de atividade diário dos noise traders (`activity`): cada dia, log(activity) fica a `activityPersist` do dia anterior, com uma parte aleatória `activitySigma`, e sobe `activityNewsJump` a cada notícia | 0.6 / 0.05 / 0.4 | Calibrado nas rondas 6 e 7: não há dados sobre a intensidade de negociação; liga o volume às notícias e torna-o persistente | C |
| 38 | Modelo final da calibração | **ronda 8b, configuração A2** (6 de 7 factos) | Melhora todos os factos face à R0 (7b + pressuposto 30 relaxado): vol 0.0217, curtose 2.04, autocorr r −0.05, dias >3% 16.2%, clustering 0.026 (positivo mas abaixo de 0.05; erro de uma autocorrelação com 250 dias ≈ 0.06). A C1 (nervosismo dos noise traders) deu 5 de 7 e foi descartada. A ronda 7b foi o modelo final até 14/11 | C |
| 39 | Atenção dos chartists (`attention`): no fim de cada dia, log(attention) = `attPersist` × log(attention) + `attWeight` × (\|r\|/0.0165 − 1), com máximo 3; o ritmo de decisão dos chartists é `chartRate` × attention (`useAttChart` = true). 0.0165 é a média de \|r\| diário do BCP (≈ 0.8 × 0.0207) | 0.7 / 0.6 | Barber & Odean (2008): os investidores negoceiam mais depois de movimentos fortes. Relaxa o pressuposto de ritmo de negociação constante. Calibrado na ronda 8b | C |
