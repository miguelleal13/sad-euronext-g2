# Registo de pressupostos

Os dados públicos sobre o livro de ordens e o comportamento dos investidores na Euronext Lisboa são escassos (comentário dos professores). Por isso, tudo o que não vem diretamente de dados fica registado aqui: o que assumimos, porquê e como o testamos. Esta tabela entra no relatório.

**Responsável:** João. Quem inventar um número acrescenta uma linha. Depois da calibração, atualiza-se a coluna *Valor*.

**Teste:** **C** = calibrado contra os factos estilizados · **S** = entra na análise de sensibilidade da Margarida · **V** = coberto pelos testes de verificação da Matilde · **—** = fixo (regra ou simplificação assumida).

| # | Pressuposto | Valor | Porquê / fonte | Teste |
|---|---|---|---|---|
| 1 | Uma só ação (BCP), sem contágio a outras | — | Âmbito da Fase 1, como os professores pediram | — |
| 2 | Regras dos colares para o PSI: ±3% dinâmico (face ao último preço), ±8% estático (face ao preço de abertura ou à referência do dia anterior), reserva de 3 min, 10 min se houver uma reserva estática consecutiva no mesmo sentido, leilão de reabertura | regras reais | Euronext, *Trading safeguards* (consultado a 31/10/2026) | — |
| 3 | O dia de negociação tem 510 min seguidos; não há noite nem leilões de abertura e fecho | 510 | Simplificação; o preço de referência estático muda a cada 510 min | — |
| 4 | Preço inicial e valor fundamental inicial | 0.50 € | Ordem de grandeza do BCP | — |
| 5 | Tick | 0.0001 € | Simplificação (a Euronext usa uma tabela de ticks) | — |
| 6 | As ordens são todas limitadas; uma ordem agressiva faz de ordem ao mercado | — | Simplificação do livro | — |
| 7 | Tempo de vida das ordens (`orderLife`) | 35 min | Não há dados de Lisboa sobre cancelamentos | C, S |
| 8 | Número de cada tipo de investidor (`nFundamentalists`, `nChartists`, `nNoise`) | 40 / 30 / 30 | Literatura de mercados baseados em agentes (ex.: Lux & Marchesi, 1999) | C |
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
| 19 | Pequenas notícias (`newsRate`) | ~1 a cada 5 dias | Simplificação | — |
| 20 | Dotação inicial de fundamentalistas e chartists (`cash`, `position`) | 5000 € / 10 000 ações | Simplificação: todos iguais, metade em dinheiro e metade em ações (a 0.50 €) | S |
| 21 | Ordens do fundamentalista: quantidade 100 + 20 000 × desvio ao valor; preço até ±0.2% do mid | — | Quanto mais longe do valor, maior a ordem | C |
| 22 | Fundamentalista sem dinheiro nem ações espera antes de voltar a tentar | 60 min | Simplificação | — |
| 23 | Ordens do chartist: tendência até 500 ações a ±0.3% do mid; pânico até 2000 ações a −1% do mid | — | O pânico vende muito e abaixo do mercado | C |
| 24 | Os chartists esquecem os sinais de venda (`forget`) | 30 min | Não observável | — |
| 25 | Noise traders sem restrições de dinheiro nem de ações (podem vender a descoberto) | cash 1e9, position 0 | Fonte de liquidez de base | — |
| 26 | Quantidade das ordens dos noise traders | Uniforme(100, 1000) | Simplificação | — |
| 27 | Vida de cada ordem: `orderLife` × Uniforme(0.3; 1.7) | 10–60 min | Heterogeneidade nos cancelamentos | C, S |
| 28 | Colar dinâmico medido contra o último preço negociado | `lastPrice` | Regra da Euronext: o preço de referência dinâmico é o último preço negociado | V |
| 29 | Leilão de reabertura instantâneo: preço que maximiza o volume; em empate, o mais perto do último preço | — | Regra de leilão simplificada | V |
| 30 | Durante a reserva, fundamentalistas e chartists param; os noise traders continuam e as ordens ficam para o leilão | — | Como na realidade, as ordens acumulam-se para o leilão | — |
| 31 | Período de stress BES começa a 15/07/2014 (e não a 01/06) | 15/07–30/09/2014 | Os preços ajustados do Yahoo mostram subidas falsas (+12% e +24%) no fim de junho e início de julho, por causa do aumento de capital do BCP | — |
| 32 | Dados reais: preços diários ajustados do Yahoo Finance (BCP.LS) | 2010–2026 | Única fonte gratuita com histórico longo | — |
| 33 | As reservas duram exatamente o mínimo da Euronext; na realidade podem ser prolongadas | 3 / 10 min | Simplificação | S |
| 34 | O preço de referência estático é o último preço do dia anterior e passa a ser o preço do leilão de reabertura depois de cada reserva; a Euronext define-o como o preço de abertura do dia ou a referência do dia anterior | — | Simplificação (o modelo não tem leilão de abertura) | V |