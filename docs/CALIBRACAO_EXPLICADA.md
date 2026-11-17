# A calibração, explicada

**Grupo 2 · SAD · Interrupções de negociação na Bolsa de Lisboa (ação do BCP)**

Este documento conta a calibração do modelo do princípio ao fim: o que queríamos atingir, o que mudámos em cada ronda e porquê, o que conseguimos e o que não conseguimos. Os números vêm do registo de calibração do João (Apêndice D do relatório e `data/processed/calibracao_log.xlsx`).

---

## 1. O que é calibrar e porque foi preciso

O modelo tem muitos números que não se conseguem observar na realidade: quantos investidores de cada tipo há, com que frequência decidem, quanto tempo uma ordem fica no livro antes de ser cancelada, com que frequência saem notícias. Não há dados públicos sobre isto para a Bolsa de Lisboa.

Calibrar é escolher esses números de forma a que o mercado artificial **se comporte como o BCP real**. Não tentamos copiar o preço do BCP dia a dia (isso seria impossível e não faria sentido). Tentamos que o modelo tenha as mesmas **características estatísticas** que os preços reais: a mesma agitação média, a mesma frequência de dias extremos, a mesma relação entre volume e agitação, e assim por diante. A estas características chama-se **factos estilizados**.

Se o modelo reproduz os factos estilizados, temos mais confiança de que os resultados das experiências (com e sem colares) dizem alguma coisa sobre o mercado real.

## 2. Os objetivos que traçámos

### 2.1 Os sete factos e os critérios

Escolhemos sete factos estilizados e medimo-los nos preços diários do BCP entre janeiro de 2023 e dezembro de 2024 (510 dias de negociação). Para cada um definimos um critério: uma faixa dentro da qual consideramos que o modelo "bate".

**Facto 1 – Volatilidade diária.** É o quanto o preço mexe por dia, em média (o desvio-padrão dos retornos diários). No BCP é **2,07%**. Critério: o modelo tem de ficar a menos de 25% deste valor, ou seja, entre 1,55% e 2,59%.

**Facto 2 – Caudas pesadas.** Nos preços reais, os dias de movimentos muito grandes são mais frequentes do que numa distribuição normal. Mede-se com a curtose em excesso, que vale 0 numa distribuição normal. No BCP é **2,41**. Critério: maior que 1 e a menos de 50% do valor do BCP, ou seja, entre 1,21 e 3,62.

**Facto 3 – Clustering da volatilidade.** Um dia agitado tende a ser seguido de outro dia agitado, e um dia calmo de outro calmo. Mede-se com a autocorrelação de um dia para o seguinte do tamanho dos movimentos (o valor absoluto dos retornos). No BCP é **0,080**. Critério: maior que 0,05.

**Facto 4 – Ausência de autocorrelação dos retornos.** Saber se o preço subiu hoje não ajuda a prever se sobe amanhã. Mede-se com a autocorrelação dos retornos de um dia para o seguinte. No BCP é **0,004**, praticamente zero. Critério: entre −0,1 e 0,1.

**Facto 5 – Frequência de movimentos grandes.** A percentagem de dias em que o preço mexe mais de 3%. No BCP é **12,9%**. Critério: a menos de 50% deste valor, ou seja, entre 6,5% e 19,4%.

**Facto 6 – Relação entre volume e volatilidade.** Nos dias agitados negoceia-se mais. Mede-se com a correlação entre o volume do dia e o tamanho do movimento do dia. No BCP é **0,636**. Critério: positiva.

**Facto 7 – Persistência do volume.** Um dia com muito volume tende a ser seguido de outro com muito volume. Mede-se com a autocorrelação do volume de um dia para o seguinte. No BCP é **0,470**. Critério: positiva.

### 2.2 Porque estes critérios e este período

Os critérios dos factos 1, 2 e 5 são faixas à volta do valor real, porque são medidas de "tamanho" e o modelo deve ter a mesma ordem de grandeza. Os critérios dos factos 3, 6 e 7 só exigem que o efeito exista (que seja positivo ou acima de um mínimo), porque são relações mais difíceis de reproduzir com exatidão. O critério do facto 4 é uma faixa à volta de zero, porque o que interessa é que não haja um padrão previsível.

O período 2023–2024 estava no plano do projeto desde o início. É recente (as regras e a forma de negociar são as de hoje) e não tem crises do BCP. Os alvos e os critérios foram **fixados antes de começar a calibrar** (a 25 de outubro, e o facto 7 a 31 de outubro, antes de qualquer afinação), para não haver a tentação de mudar os alvos para o modelo passar. O ano de 2025 ficou de fora: não estava no plano e tem o choque das tarifas de abril de 2025.

Mais tarde, o João fez um **teste de robustez**: calculou os mesmos factos para 2023, 2024 e 2025 separadamente. Os factos principais são parecidos em todos os anos. Os que mais variam de ano para ano são o clustering (de 0,06 a 0,18), a autocorrelação dos retornos (de −0,09 a 0,07) e a persistência do volume (de 0,16 a 0,49). Os alvos não foram mudados depois deste teste.

## 3. Como corria cada ronda

Cada ronda seguiu sempre o mesmo protocolo:

1. Escolher **uma só mudança**, a partir do diagnóstico da ronda anterior. Mudar uma coisa de cada vez permite saber o efeito de cada mudança.
2. Correr o cenário base (sem choque grande, com os colares reais) **10 vezes**, cada uma com **250 dias** de negociação (um ano) e uma semente aleatória diferente.
3. Calcular os sete factos para cada corrida com o script `compare_model.py`.
4. Comparar a **média** das 10 corridas com os critérios. Olhar também para a **mediana**, para detetar médias puxadas por uma ou duas corridas extremas.
5. Registar tudo no registo de calibração, com a decisão tomada.

---

## 4. As rondas, uma a uma

### Ronda 0 – o modelo tal como estava: 2 de 7

**O que tínhamos.** O primeiro modelo completo, com os valores iniciais: 30 noise traders, 40 fundamentalistas, 30 chartists, notícias a cada 5 dias com ±1%, e os fundamentalistas e chartists com 5000 € e 10 000 ações cada.

**O que vimos.** Só os dois factos de volume passavam, e o da persistência muito à justa (0,04). O mercado era cerca de **cinco vezes mais calmo** do que o BCP: volatilidade de 0,42% por dia contra 2,07%. Quase nenhum dia mexia mais de 3% (0,2% dos dias contra 12,9%). Os retornos tinham autocorrelação negativa (−0,14). A curtose média era 9,6, mas a mediana era só 0,2: a média era puxada por três corridas com reservas.

**Diagnóstico.** Os fundamentalistas prendiam o preço ao valor fundamental, e o valor fundamental quase não mexia. Com uma notícia a cada cinco dias e cada notícia a mexer 1%, as notícias sozinhas dão uma volatilidade de cerca de 0,44% por dia, que é exatamente o que o modelo mostrava. O problema era a falta de notícias.

### Ronda 1 – mais notícias: 4 de 7

**O que mudámos.** As notícias passaram de uma a cada cinco dias para cerca de **uma por dia** (`newsRate` de 0,0004 para 0,002 por minuto), e cada notícia passou de ±1% para **±2%**. As contas indicavam que, só com as notícias, isto daria uma volatilidade de 2,0%, uma curtose de 2,9 e 13,7% de dias acima de 3%, muito perto do BCP.

**O que vimos.** Passou para 4 de 7, mas a volatilidade só subiu para 0,87% e a curtose disparou para 75. Olhando para dentro de cada corrida, percebeu-se que **o mercado "morria" ao longo do ano**: a volatilidade era 1,22% nos primeiros 50 dias e só 0,38% depois do dia 150, e 26 das 35 reservas aconteciam nos primeiros 50 dias.

**Diagnóstico.** Os fundamentalistas e chartists **ficavam sem dinheiro ou sem ações**. A partir daí deixavam de negociar, o preço deixava de seguir o valor fundamental e só o apanhava aos saltos, de vez em quando (daí a curtose enorme).

### Ronda 2 – mais dinheiro: 4 de 7

**O que mudámos.** O dinheiro e as ações iniciais dos fundamentalistas e chartists foram multiplicados por 10 (50 000 € e 100 000 ações).

**O que vimos.** A volatilidade média saltou para 3,41%, mas isso era culpa de **uma só corrida**: sem ela, a média era 2,01%, quase igual ao BCP. Nessa corrida o preço caiu de **0,84 € para 0,02 € em dois dias**, através de uma sequência de leilões de reabertura, cada um a um preço muito mais baixo do que o anterior. Além disso, na maioria das corridas o mercado continuava a morrer, só que mais tarde (por volta do dia 100). Os primeiros meses, muito agitados, davam clustering a mais (0,45) e autocorrelação negativa dos retornos (−0,16).

**Diagnóstico.** Dois problemas. Primeiro, **o leilão não tinha limite de preço**: podia fixar qualquer preço, e esse preço passava a ser a referência do colar estático, por isso um leilão mau abria caminho ao seguinte. A Euronext limita o leilão das ações do PSI a ±6% (está no anexo oficial da Euronext), por isso esta regra tinha de entrar no modelo. Segundo, mesmo com 10 vezes mais, **os agentes continuavam a esgotar-se**.

### Ronda 3 – sem limite de orçamento: 4 de 7

**O que mudámos.** Os fundamentalistas e chartists passaram a ter dinheiro e ações praticamente ilimitados (1 000 milhões de euros e 1 000 milhões de ações), como os noise traders já tinham.

**O que vimos.** O mercado **deixou de morrer**: a volatilidade ficou entre 3,3% e 3,7% em todos os períodos de 50 dias, e as reservas espalharam-se pelo ano todo. A curtose (2,39) ficou igual à do BCP. Mas o mercado ficou **agitado demais**: 3,60% por dia, 30% dos dias acima de 3%, cerca de duas reservas por dia. E os retornos tinham autocorrelação muito negativa (−0,34): o preço passava do ponto num dia e corrigia no seguinte.

**Diagnóstico.** As notícias sozinhas davam cerca de 2% de volatilidade, por isso o excesso vinha dos **chartists**: seguiam a tendência, exageravam os movimentos, e depois os fundamentalistas corrigiam. Havia chartists a mais.

**Nota:** esta mudança resolveu o problema, mas criou uma limitação que ficou até ao fim: como os investidores nunca ficam sem dinheiro, nunca são obrigados a vender, e o modelo não reproduz as vendas forçadas que agravam os crashes reais.

### Ronda 4 – metade dos chartists e colar do leilão: 6 de 7

**O que mudámos.** Os chartists passaram de **30 para 15**. Ao mesmo tempo entrou o **colar do leilão de ±6%** (em rigor, duas mudanças na mesma ronda; o colar do leilão só teria afetado 2 dos 5074 leilões da ronda 3, por isso quase não mexe nos factos).

**O que vimos.** 6 de 7: volatilidade de 2,37%, curtose de 2,59, clustering de 0,10, 17% de dias acima de 3%, cerca de 38 reservas por ano espalhadas pelo ano todo, e nenhum leilão chegou ao limite de 6%. Só falhava a autocorrelação dos retornos, e por pouco (−0,105 contra o limite de −0,1; cinco das dez corridas já estavam dentro).

**Diagnóstico.** Reduzir os chartists para metade tinha levado a autocorrelação de −0,34 para −0,105. Bastava reduzir um pouco mais.

### Ronda 5 – 13 chartists: 7 de 7, mas à justa

**O que mudámos.** Os chartists passaram de **15 para 13**.

**O que vimos.** **Todos os sete critérios passavam**: volatilidade de 2,24% (BCP 2,07%), curtose de 2,22 (2,41), 16,6% de dias acima de 3% (12,9%), correlação volume–volatilidade de 0,58 (0,64), autocorrelação dos retornos de −0,07, e cerca de 17 reservas por ano.

**Mas três factos passavam só à justa:**
- O clustering era 0,053, mesmo em cima do limiar de 0,05.
- A autocorrelação dos retornos passava na média, mas só em 5 das 10 corridas.
- A persistência do volume era **0,001**. Passa o critério "positiva", mas o BCP tem 0,47. Na prática, **o modelo não reproduzia este facto**: passava só "no papel".

**Diagnóstico.** O volume diário vinha quase todo dos noise traders e do market maker, que negoceiam sempre ao mesmo ritmo e com as mesmas quantidades. Por isso o volume de um dia não tinha nada a ver com o do dia anterior.

**Decisão.** Os professores pediram, no feedback à proposta, para validar o preço **e o volume**. Um 7 de 7 com a persistência do volume só no papel seria difícil de defender. Por isso continuámos.

### Ronda 6 – atividade diária ao acaso: 6 de 7

**O que mudámos.** Criámos a **atividade diária dos noise traders**: um número que multiplica a quantidade das ordens deles e que muda uma vez por dia. Tem memória: o logaritmo da atividade de hoje é uma parte do de ontem (persistência de 0,7) mais uma parte ao acaso (desvio de 0,3). Assim, um dia de muita atividade tende a ser seguido de outro.

**O que vimos.** A persistência do volume subiu de 0,001 para **0,66**. Mas a correlação entre volume e volatilidade caiu de 0,58 para **0,02**, e a autocorrelação dos retornos para −0,14 (fora da faixa). Ficou em 6 de 7, mas com outro facto a falhar.

**Diagnóstico.** A atividade mexia ao acaso, **sem ligação ao que fazia o preço mexer** (as notícias). Havia dias de muito volume sem agitação, e dias agitados sem volume.

**Problema encontrado nesta ronda.** Uma corrida (a 47d0b7e6) ficou **presa num ciclo de 1485 reservas** entre os dias 73 e 90, com o preço congelado em 0,5638 €. O leilão não conseguia negociar nada dentro do colar de 6% (o livro estava cruzado fora da faixa), o último preço nunca mudava, e ao reabrir o colar disparava logo outra vez. **Correção (8 de novembro):** quando o leilão não consegue negociar dentro do colar e o livro continua cruzado, o último preço passa para o limite do colar. Segue-se nova reserva, e o preço aproxima-se 6% de cada vez do nível a que o mercado quer negociar. O João confirmou depois no manual da Euronext (versão de 5 de julho de 2021, secção 4.2.4) que é isto que a Euronext faz. Nos indicadores, as reservas seguidas a menos de um minuto passaram a contar como uma só interrupção.

### Ronda 7 (7b) – atividade ligada às notícias: 6 de 7

**O que mudámos.** Cada notícia passou a **aumentar a atividade** desse dia (multiplica-a por cerca de 1,5), que depois vai baixando nos dias seguintes. Os valores finais da atividade ficaram: persistência de 0,6, parte ao acaso de 0,05 e salto por notícia de 0,4.

**O que vimos.** Os **dois factos de volume passaram a bater "a sério"**, pelo mecanismo e não só pelo critério: correlação volume–volatilidade de 0,25 e persistência do volume de 0,60 (BCP: 0,64 e 0,47). A autocorrelação dos retornos voltou à faixa (−0,07). Mas o **clustering caiu para 0,008**, praticamente zero. Ficou em 6 de 7.

**Diagnóstico.** No modelo, a agitação diária vem sobretudo das notícias, e as notícias chegam ao acaso. Por isso um dia agitado não diz nada sobre o dia seguinte. A atividade tem memória, mas mexe sobretudo no volume, não no preço. Uma simulação simplificada feita pelo João mostrou que, se as notícias chegassem mais vezes quando a atividade está alta ("notícias atraem notícias"), o clustering voltava.

Nesta altura a ronda 7 foi considerada o modelo final (11 de novembro) e os seus valores passaram para o modelo principal.

### Ronda 8 – notícias em ondas: 4 de 7 (descartada)

**O que mudámos.** O ritmo das notícias passou a ser multiplicado pela atividade (até 3 vezes), com um ritmo de base de 0,0026 por minuto e um salto de atividade de 0,3 por notícia.

**O que vimos.** O clustering voltou (**0,065**, acima do limiar). Mas as notícias passaram a vir em ondas **grandes demais**: volatilidade de 2,87%, 26% dos dias acima de 3%, curtose de 0,96 (abaixo do mínimo de 1,21) e correlação volume–volatilidade de 0,07. Só 4 de 7.

**Decisão.** Descartada. Ganhar o clustering à custa de três outros factos não compensava.

### Ronda 8b – três tentativas finais: 6 de 7 com a A2

**Contexto.** Depois do feedback do professor sobre o realismo dos pressupostos, decidimos fazer uma última ronda com duas coisas ao mesmo tempo: relaxar o pressuposto de que os fundamentalistas e chartists param durante as reservas, e tentar mais uma vez dar memória à volatilidade. Fez-se numa cópia do modelo, com uma mudança ativa de cada vez.

**R0 – só as ordens durante a reserva: 6 de 7.** Os fundamentalistas e chartists passaram a continuar a enviar ordens durante as reservas (como permite o manual da Euronext); as ordens ficam à espera do leilão. Manteve 6 de 7, o que mostrou que esta mudança não estraga a calibração. Mas a curtose caiu para 1,64 e a autocorrelação dos retornos ficou perto do limite (−0,093).

**A2 – R0 mais a atenção dos chartists: 6 de 7, a melhor.** Os chartists passaram a ter uma **atenção** que sobe depois de dias com movimentos grandes e vai baixando depois de dias calmos (com `attWeight` = 0,6). O ritmo a que decidem é multiplicado pela atenção. A ideia vem de Barber e Odean (2008): os investidores negoceiam mais depois de acontecimentos que lhes chamam a atenção. A A2 melhorou todos os factos em relação à R0: volatilidade de 2,17% (BCP 2,07%), curtose de 2,04, autocorrelação dos retornos de −0,052, 16,2% de dias acima de 3%, e um clustering **positivo de 0,026**. Ainda abaixo do limiar de 0,05.

**C1 – R0 mais nervosismo nos noise traders: 5 de 7 (descartada).** Em vez dos chartists, a atenção passou a aumentar a dispersão dos preços dos noise traders (com `attWeight` = 0,3). O clustering chegou a **0,049**, mesmo à beira do limiar. Mas a autocorrelação dos retornos saiu da faixa (−0,100). Além disso, este mecanismo parece-se mais com impor uma regra à volatilidade (um processo GARCH) do que com um comportamento de investidores, o que é mais difícil de defender num modelo baseado em agentes.

**Decisão final (14 de novembro).** O modelo final é a **A2**.

---

## 5. Onde ficámos: o modelo final em relação aos objetivos

**Facto 1 – Volatilidade diária: conseguido, muito perto.** Modelo 2,17%, BCP 2,07%: 5% acima, quando o critério aceitava 25%.

**Facto 2 – Caudas pesadas: conseguido, perto.** Modelo 2,04, BCP 2,41: 15% abaixo, quando o critério aceitava 50%. O modelo tem um pouco menos de dias extremos.

**Facto 3 – Clustering da volatilidade: não conseguido.** Modelo 0,026, BCP 0,080, limiar 0,05. O efeito existe mas é cerca de um terço do real.

**Facto 4 – Ausência de autocorrelação: conseguido.** Modelo −0,052, BCP 0,004, faixa de −0,1 a 0,1. Há uma ligeira tendência para corrigir no dia seguinte, mas pequena.

**Facto 5 – Movimentos maiores que 3%: conseguido, com algum excesso.** Modelo 16,2%, BCP 12,9%: 26% a mais, quando o critério aceitava 50%.

**Facto 6 – Volume e volatilidade: conseguido, mas mais fraco do que no real.** Modelo 0,26, BCP 0,64. A relação existe e tem o sentido certo, mas tem cerca de 40% da força real. O critério só exigia que fosse positiva.

**Facto 7 – Persistência do volume: conseguido, muito perto.** Modelo 0,60, BCP 0,47.

Em resumo: **6 de 7 factos**. Quatro estão muito perto do BCP (1, 2, 4 e 7), um com um ligeiro exagero (5), um passa o critério mas é mais fraco do que no real (6), e um falha (3).

Comparado com a ronda 5 (a única com 7 de 7), o modelo final troca um clustering à justa (0,053) por um clustering abaixo do limiar (0,026), mas ganha a persistência do volume a sério (0,60 em vez de 0,001) e relaxa um pressuposto irrealista (os investidores já não param durante as reservas).

## 6. Porque não conseguimos o clustering

Tentámos três mecanismos diferentes (rondas 8, 8b A2 e 8b C1). Há cinco razões para ser tão difícil:

1. **É preciso memória de vários dias, e os investidores do modelo pensam em minutos.** Os chartists lembram-se de 50 minutos de preços e o pânico dura 10 minutos. Nada no comportamento deles passa naturalmente de um dia para o outro. Qualquer memória entre dias tem de ser acrescentada de propósito, e cada acrescento mexe noutras coisas.

2. **É preciso prolongar o tamanho dos movimentos sem prolongar a direção.** O clustering diz que depois de um dia com um movimento grande vem outro dia com um movimento grande, **para cima ou para baixo**. Os mecanismos que prolongam a agitação tendem também a prolongar a direção, e isso estraga o facto 4. Foi o que aconteceu na C1: o clustering quase passou (0,049), mas a autocorrelação dos retornos falhou (−0,100).

3. **Amplificar demais estraga o resto.** Para haver clustering tem de haver reforço (agitação gera mais agitação). Se for fraco não se nota; se for forte, gera ondas enormes, com volatilidade a mais, dias de mais de 3% a mais e caudas erradas. Foi o que aconteceu na ronda 8 (4 de 7).

4. **Na realidade, o clustering tem muitas causas ao mesmo tempo.** Notícias em cadeia, investidores que entram e saem do mercado, investidores que mudam de estratégia, liquidez que demora a voltar, investidores endividados obrigados a vender. O modelo só tem algumas destas peças, e cada uma explica só uma parte do efeito.

5. **É a medida com mais ruído estatístico.** Com 250 dias por corrida, o erro de uma autocorrelação é cerca de 1/√250 ≈ 0,06, maior do que a diferença entre o nosso 0,026 e o limiar de 0,05. É por isso que no próprio BCP o valor salta entre 0,06 e 0,18 de ano para ano. Cada ronda de calibração dá uma resposta "tremida" neste facto, e é difícil saber se uma mudança o melhorou mesmo.

O mecanismo que a literatura usa mais para o clustering é os investidores **mudarem de estratégia** conforme o que está a dar lucro (passarem de fundamentalista a chartist e vice-versa), como no modelo de Lux e Marchesi (1999). Isso obrigaria a mexer a sério nos agentes e a recalibrar tudo, por isso ficou como trabalho futuro.

## 7. Porque a relação volume–volatilidade é mais fraca do que no real

O facto 6 passa o critério, mas com 0,26 em vez de 0,64. A razão é parecida com a do clustering: a maior parte do volume vem dos noise traders e do market maker, cuja atividade só sobe com as notícias. Os dias agitados por causa da manada dos chartists, sem notícia, não trazem muito volume extra. Na ronda 5 (antes da atividade) este valor era 0,58, mas aí o volume não tinha persistência nenhuma; ao dar persistência ao volume na ronda 6, a correlação caiu para 0,02, e ligar a atividade às notícias na ronda 7 só a recuperou até 0,25. Foi o equilíbrio possível entre os dois factos de volume.

## 8. O que isto quer dizer para as conclusões

Os colares atuam **dentro do dia**, e o que importa aí está bem calibrado: a volatilidade, as caudas pesadas e a frequência de dias com movimentos grandes. O que ficou mais fraco é a ligação **entre dias** (clustering) e a força da ligação entre volume e agitação.

A consequência prática é que, depois de um choque, a agitação no modelo passa mais depressa do que passaria na realidade. Por isso os **tempos de recuperação** depois do choque devem ser lidos como um limite inferior (otimistas). A **comparação entre cenários** (com e sem colares) é mais fiável do que os valores absolutos, porque todos os cenários têm a mesma limitação.

## 9. Mudanças ao modelo que vieram da calibração

A calibração não serviu só para escolher números. Também obrigou a mudar o modelo:

- **Notícias** mais frequentes e maiores (ronda 1).
- **Investidores sem limite de orçamento** (ronda 3). Ficou como limitação.
- **Menos chartists**: de 30 para 13 (rondas 4 e 5).
- **Colar do leilão de ±6%** (ronda 4), regra real da Euronext que faltava no modelo.
- **Regra do leilão sem execução** (ronda 6), confirmada no manual da Euronext.
- **Atividade diária dos noise traders**, ligada às notícias (rondas 6 e 7).
- **Ordens durante as reservas** para todos os investidores (ronda 8b), pressuposto relaxado.
- **Atenção dos chartists** (ronda 8b).
- **Volume guardado como `long`** em vez de `int` (antes da ronda 8), porque o volume acumulado de um ano ia passar o limite do `int`.

## 10. Como explicar isto ao professor

> "Fixámos sete factos estilizados do BCP (2023–2024) antes de calibrar. Fizemos dez rondas (da 0 à 8b), mudando uma coisa de cada vez, com 10 réplicas de um ano cada. A ronda 5 passava os sete, mas a persistência do volume só passava no papel (0,001 contra 0,47), e o feedback pedia para validar o volume. O modelo final reproduz seis: a volatilidade, as caudas, a autocorrelação e a persistência do volume estão muito perto do BCP; a relação volume–volatilidade existe mas é mais fraca (0,26 contra 0,64); e o clustering fica abaixo do limiar (0,026 contra 0,08), apesar de termos tentado três mecanismos. O clustering é o facto com mais ruído estatístico e o que mais varia no próprio BCP. Isto é um problema para as conclusões, ou basta apresentá-lo como limitação?"
