# Registo de pressupostos

Os dados públicos sobre o livro de ordens e o comportamento dos investidores na Euronext Lisboa são escassos (comentário dos professores). Por isso, tudo o que não vem diretamente de dados fica registado aqui: o que assumimos, porquê e como o testamos. Esta tabela entra no relatório.

**Responsável:** João. Quem inventar um número acrescenta uma linha. Depois da calibração, atualiza-se a coluna *Valor*.

**Teste:** **C** = calibrado contra os factos estilizados · **S** = entra na análise de sensibilidade da Margarida · **V** = coberto pelos testes de verificação da Matilde · **—** = fixo (regra ou simplificação assumida).

| # | Pressuposto | Valor | Porquê / fonte | Teste |
|---|---|---|---|---|
| 1 | Uma só ação (BCP), sem contágio a outras | — | Âmbito da Fase 1, como os professores pediram | — |
| 2 | Regras dos colares: ±3% dinâmico, ±8% estático, reserva de 3 min (10 min se o estático se repetir), leilão de reabertura | regras reais | Euronext Trading Safeguards | — |
| 3 | O dia de negociação tem 510 min seguidos; não há noite nem leilões de abertura e fecho | 510 | Simplificação; o preço de referência estático muda a cada 510 min | — |
| 4 | Preço inicial e valor fundamental inicial | 0.50 € | Ordem de grandeza do BCP | — |
| 5 | Tick | 0.0001 € | Simplificação (a Euronext usa uma tabela de ticks) | — |
| 6 | As ordens são todas limitadas; uma ordem agressiva faz de ordem ao mercado | — | Simplificação do livro | — |
| 7 | Tempo de vida das ordens (`orderLife`) | 35 min | Não há dados de Lisboa sobre cancelamentos | C, S |
| 8 | Número de cada tipo de investidor (`nFundamentalists`, `nChartists`, `nNoise`) | 40 / 30 / 30 | Literatura de mercados baseados em agentes | C |
| 9 | Banda e ritmo do fundamentalista (`fundBand`, `fundRate`) | 0.01 / 0.2 | Literatura | C, S |
| 10 | Erro de avaliação de cada fundamentalista (`bias`) | Normal(0, 2%) | Heterogeneidade de opiniões | — |
| 11 | Ritmo e limiar de tendência do chartist (`chartRate`, `trendThreshold`) | 0.2 / 0.005 | Literatura | C, S |
| 12 | Memória da média móvel usada pelos chartists (`maWindow`) | 50 min | Horizonte intradiário intermédio: curto demais reage a ruído; longo demais não vê uma queda a meio da sessão | C, S |
| 13 | Rede de contactos dos chartists | small world, 6 vizinhos | Como no Market Model das aulas | — |
| 14 | Limiar de manada (`herdThreshold`) e duração do pânico (`panicDuration`) | 2 / 10 min | Não observável | C, S |
| 15 | Ruído: ritmo e dispersão de preços (`noiseRate`, `noiseSigma`) | 1 / 0.2% | Dá volume e liquidez de base | C, S |
| 16 | Criador de mercado: spread e quantidade (`mmSpread`, `mmQty`) | 0.4% / 2000 | Não há dados; testado em valores extremos | S, V |
| 17 | Choque de notícia estilizado (`shockSize`, `shockTime`) | −10%, dia 60 | Inspirado no BES; **não** é uma reprodução do crash | S |
| 18 | Probabilidade de pânico de um chartist com o choque (`shockPanicProb`) | 0.3 | Não observável | S |
| 19 | Pequenas notícias (`newsRate`) | ~1 a cada 5 dias | Simplificação | — |
