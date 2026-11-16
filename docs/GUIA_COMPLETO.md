# Guia completo do trabalho

**Grupo 2 · SAD · Interrupções de negociação na Bolsa de Lisboa (ação do BCP)**

Este guia explica, em texto e sem pressupor conhecimentos prévios, tudo o que está no modelo e porque é que as coisas são como são. Está escrito para ser lido do princípio ao fim: cada capítulo usa o que foi explicado nos anteriores. Os valores são os do modelo final (16 de novembro de 2026).

---

# Parte I · O problema

## 1. Como funciona uma bolsa, em poucas palavras

Uma bolsa é um sítio onde quem quer comprar ações encontra quem as quer vender. Hoje é tudo eletrónico: ninguém grita num pavilhão, há um computador da bolsa que recebe pedidos e junta compradores com vendedores.

Cada pedido chama-se uma **ordem**. Uma ordem diz quatro coisas: quem a envia, se quer comprar ou vender, a que preço, e quantas ações. Por exemplo: "quero comprar 500 ações do BCP e pago no máximo 0,50 € por cada uma". Esse preço máximo (ou, numa venda, o preço mínimo que o vendedor aceita) chama-se **preço-limite**.

As ordens que ainda não encontraram par ficam à espera numa lista. Essa lista chama-se **livro de ordens**. Tem dois lados: o lado das compras e o lado das vendas. Em cada lado as ordens estão arrumadas: nas compras, à frente fica quem paga mais; nas vendas, à frente fica quem pede menos. Se duas ordens têm o mesmo preço, passa à frente a que chegou primeiro. A esta regra chama-se **prioridade preço-tempo**.

Quando a melhor compra paga pelo menos o que a melhor venda pede, há **negócio**. O preço desse negócio passa a ser o **último preço** da ação, que é o preço que aparece nas notícias.

Há alguns nomes que vão aparecer muitas vezes:

- A **melhor compra** (o preço mais alto que alguém está disposto a pagar) chama-se **bid**.
- A **melhor venda** (o preço mais baixo que alguém aceita) chama-se **ask**.
- A diferença entre os dois chama-se **spread**. Um spread pequeno quer dizer que é fácil negociar sem perder dinheiro; um spread grande quer dizer que o mercado tem pouca **liquidez**.
- O ponto a meio entre o bid e o ask chama-se **mid** (preço médio).
- A **volatilidade** é o quanto o preço sobe e desce. Um dia com muita volatilidade é um dia agitado.
- O **volume** é o número de ações que mudaram de mãos.

## 2. O que são os colares e as reservas

Às vezes o preço de uma ação cai ou sobe muito em pouco tempo. Pode ser por uma notícia, por um erro de alguém que enviou uma ordem enorme por engano, ou por pânico. Para evitar que estes saltos se tornem descontrolados, a Euronext tem **travões automáticos**, a que chama **colares de volatilidade** (em inglês, *collars* ou *circuit breakers*).

Funcionam assim. A bolsa define uma faixa à volta de um preço de referência. Se um negócio fosse acontecer fora dessa faixa, o negócio **não acontece**. Em vez disso, a ação entra num período de **reserva**: durante uns minutos ninguém negoceia essa ação. As pessoas podem continuar a enviar ordens, mas elas ficam à espera. No fim da reserva há um **leilão de reabertura**: junta-se todas as ordens que estavam à espera e escolhe-se um só preço, aquele que permite negociar mais ações. Todos os que se cruzam a esse preço negoceiam, e depois a negociação normal recomeça.

Há dois colares, que funcionam ao mesmo tempo:

- O **colar dinâmico** compara o preço do próximo negócio com o **último negócio**. Para o BCP a faixa é de 3% para cima ou para baixo. Se o último negócio foi a 0,50 €, o seguinte tem de ficar entre 0,485 € e 0,515 €. Serve para travar saltos bruscos de um negócio para o outro.
- O **colar estático** compara com um **preço de referência do dia** (o preço de abertura ou o do último leilão). Para o BCP a faixa é de 8%. Serve para travar quedas lentas mas grandes: o preço pode ir descendo aos bocadinhos sem nunca disparar o colar de 3%, mas quando acumula 8% dispara este.

A reserva dura **3 minutos**. Se o colar estático disparar outra vez no mesmo sentido no mesmo dia, dura **10 minutos**.

O BCP tem estes valores (3% e 8%) porque é uma **blue chip**: uma das maiores e mais negociadas empresas do país, que faz parte do índice principal (o PSI). Ações pequenas têm faixas mais largas (5% e 10%), porque os preços delas saltam mais facilmente. Confirmámos os valores do BCP no anexo oficial da Euronext que está no repositório: grupo "P0 – Lisbon – Equities PSI", colar contínuo de 3%, colar estático de 8%, colar do leilão de 6% e reserva de 180 segundos.

## 3. A pergunta do trabalho

A pergunta é: **estes travões ajudam ou atrapalham?**

Há argumentos para os dois lados. A favor: dão tempo para as pessoas pensarem e podem cortar uma espiral de pânico (como na resolução do BES em 2014). Contra: enquanto a ação está parada ninguém consegue negociar, os investidores ficam sem saber o preço verdadeiro, e o problema pode simplesmente ficar adiado para depois da reserva.

Não dá para responder com dados reais, porque não conseguimos ver o que teria acontecido **sem** colares no mesmo dia. Por isso construímos um **mercado artificial** no computador: um modelo onde vários tipos de investidores negoceiam a ação do BCP, com os colares reais. Depois podemos fazer experiências que na realidade são impossíveis: lançar o mesmo choque com e sem colares, com colares mais apertados ou mais largos, com mais ou menos investidores em pânico, e comparar.

## 4. O âmbito

Na proposta havia três fases: (1) uma ação, o livro de ordens e os colares; (2) investidores com dinheiro emprestado (alavancagem) e corretoras; (3) várias ações e contágio entre elas. Os professores pediram para fazermos **só a Fase 1** e bem feita. As fases 2 e 3 aparecem no relatório apenas como trabalho futuro.

---

# Parte II · As ferramentas e a forma de modelar

## 5. AnyLogic e a versão PLE

O modelo é feito no **AnyLogic 8.9.10**, na versão gratuita para estudantes, chamada **PLE** (*Personal Learning Edition*). Esta versão tem limites: no máximo 10 tipos de agente diferentes e no máximo 50 000 agentes criados durante a simulação. Estes limites influenciaram várias decisões, como se verá.

O AnyLogic permite três formas de modelar:

- **Modelação baseada em agentes**: cada "pessoa" do modelo é um agente com o seu próprio comportamento, descrito por variáveis, funções e um diagrama de estados (statechart). É o que usamos para os investidores.
- **Eventos discretos**: entidades que passam por uma sequência de blocos (chegam, esperam numa fila, são atendidas, saem). No AnyLogic faz-se com a **Process Modeling Library** (PML), uma biblioteca de blocos que se ligam com setas, como `Source → Queue → Service → Sink`. O nosso livro de ordens é, no fundo, um sistema destes (ordens que chegam, esperam numa fila e saem), mas está escrito em código Java e não em blocos. O capítulo 9 explica porquê.
- **Dinâmica de sistemas**: stocks e fluxos agregados. Não usamos.

## 6. Agentes, parâmetros, variáveis, funções, eventos e statecharts

Estes são os "tijolos" do AnyLogic. Vale a pena perceber bem o que é cada um.

Um **tipo de agente** é como uma fôrma: define como é um investidor de um certo tipo. Cada investidor concreto que existe na simulação é um **agente** feito com essa fôrma. Um conjunto de agentes do mesmo tipo chama-se **população**. Por exemplo, o tipo `Fundamentalist` é a fôrma, e a população `fundamentalists` tem 40 agentes feitos com ela.

Um **parâmetro** é um valor de configuração que se escolhe antes de a simulação começar e que não muda durante ela. Serve para fazer experiências: mudando um parâmetro, muda-se o cenário sem mexer no código. Exemplo: o número de chartists.

Uma **variável** é um valor que muda durante a simulação. Exemplo: o último preço, ou o dinheiro de um investidor.

Uma **função** é um bocado de código com um nome, que se chama quando é preciso. Exemplo: a função `order` do Stock, que recebe uma ordem.

Um **evento** é código que corre num certo momento: uma vez, de x em x minutos, ou ao acaso com um certo ritmo. Exemplo: a cada minuto, apagar as ordens que já caducaram.

Um **statechart** (diagrama de estados) descreve o comportamento de um agente como uma sequência de **estados** (o que o agente está a fazer) ligados por **transições** (o que o faz mudar). Uma transição pode disparar ao fim de um tempo, ao acaso com um certo ritmo, quando chega uma mensagem, ou quando uma condição é verdadeira. Um **ramo** (*branch*) é um ponto de decisão: o agente chega lá e segue por um caminho ou outro conforme uma condição.

Uma **mensagem** é um aviso que um agente manda ao statechart de outro (por exemplo, "HALT", que quer dizer "o mercado parou").

## 7. Unidade de tempo e o dia de negociação

No modelo, uma unidade de tempo é **um minuto**. Um dia de negociação tem **510 minutos**, que correspondem às 8 horas e meia de negociação contínua da Euronext em Lisboa (das 08:00 às 16:30). Não há noite: quando um dia acaba, o seguinte começa logo. Também não há pré-abertura nem leilões de abertura e de fecho (na realidade existem), porque o que nos interessa são as interrupções durante o dia.

Algumas contas úteis: 1 dia = 510 minutos; 60 dias = 30 600 minutos (é quando acontece o choque nos cenários); 120 dias = 61 200 minutos; 250 dias (um ano de bolsa) = 127 500 minutos.

---

# Parte III · O modelo, peça a peça

## 8. Visão geral

O modelo tem 7 tipos de agente e uma classe Java:

- **Main**: o "mundo". Tem todos os outros agentes, os parâmetros globais, os indicadores e os ficheiros de saída.
- **Stock**: a bolsa. Tem o livro de ordens, faz os negócios, aplica os colares e corre os leilões. Há só um.
- **NoiseTrader** (30): investidores que negoceiam ao acaso.
- **Fundamentalist** (40): investidores que negoceiam pelo valor da empresa.
- **Chartist** (13): investidores que seguem a tendência do preço e podem entrar em pânico em grupo.
- **MarketMaker** (1): um intermediário que está sempre disponível para comprar e vender.
- **NewsAgent** (1): gera as notícias que mudam o valor da empresa.
- **Order**: não é um agente, é uma classe Java que representa uma ordem.

A forma como as peças se ligam é esta. O NewsAgent muda o "valor verdadeiro" da empresa. Os investidores observam o preço e esse valor, e decidem comprar ou vender. Quando decidem, chamam a função `order` do Stock. O Stock põe a ordem no livro e tenta fazer negócio. Se um negócio fizesse o preço saltar demais, o Stock entra em reserva e avisa toda a gente com a mensagem "HALT". No fim da reserva faz o leilão e avisa com "REOPEN". Tudo o que acontece fica registado em dois ficheiros CSV, que depois são analisados em Python.

Há uma distinção importante: as **ordens** vão dos investidores para o Stock por **chamada de função** (o investidor diz diretamente ao Stock "quero comprar isto"). Os **avisos** vão do Stock (ou do NewsAgent) para os investidores por **mensagem**.

## 9. A classe Order: a ficha de uma ordem

A `Order` é a coisa mais simples do modelo. **Não faz nada**: é só uma ficha com sete campos. Pensa num impresso em branco dos correios com sete linhas para preencher. Cada vez que alguém envia uma ordem, o Stock tira uma cópia do impresso e preenche-a.

Os sete campos são:

- `id`: o número da ordem. É um contador que sobe sempre (0, 1, 2, …), por isso uma ordem com número mais baixo chegou primeiro. É assim que se desempata a prioridade de chegada.
- `side`: o lado. Vale 1 para uma compra e −1 para uma venda. Compras e vendas usam a mesma ficha; é este campo que as distingue.
- `price`: o preço-limite, já arredondado ao tick (0,0001 €).
- `qty`: a quantidade de ações que **ainda falta** negociar. Começa com a quantidade pedida e vai descendo à medida que a ordem é executada aos bocados.
- `tSubmit`: o minuto em que a ordem entrou.
- `expiry`: o minuto em que a ordem caduca se ninguém pegar nela.
- `trader`: quem a enviou (um noise trader concreto, um fundamentalista, etc.). Nos testes é `null`, porque as ordens de teste não pertencem a ninguém.

**Porque é que a ordem é uma classe Java e não um agente?** Por duas razões. Primeiro, uma corrida de um ano cria **milhões** de ordens, e a versão PLE só deixa criar 50 000 agentes. Segundo, um agente é pesado (tem posição no ecrã, statechart, animação…), e uma ficha Java é muito leve. Foi também por isto que o livro de ordens não foi feito com os blocos da Process Modeling Library: nesses blocos, cada ordem teria de ser um agente a "andar" pelos blocos.

## 10. O Stock: a bolsa e o livro de ordens

O Stock é o agente mais importante. Quando se diz que "o livro de ordens está no Stock", quer-se dizer que as listas de ordens e as funções que mexem nelas pertencem a este agente.

### 10.1 As três filas

No Stock há três listas de ordens. Estão escritas no "Additional class code" do agente (nas propriedades, em Advanced Java), porque são objetos Java e não aparecem no desenho.

A primeira chama-se `bids` e guarda as **compras**. É uma `PriorityQueue`, uma fila que se arruma sozinha: cada vez que entra uma ordem, a fila põe-na no sítio certo. A regra de arrumação é: quem paga **mais** fica à frente; se dois pagam o mesmo, fica à frente o que tem o `id` mais baixo (chegou primeiro).

A segunda chama-se `asks` e guarda as **vendas**, com a regra ao contrário: quem pede **menos** fica à frente; em empate, quem chegou primeiro.

A terceira chama-se `pending` e é uma lista simples. Guarda as ordens que chegam **durante uma reserva**. Essas ordens não entram no livro logo: ficam à espera do leilão.

As filas são criadas uma vez, quando o Stock nasce, e começam vazias. Durante a simulação as funções do Stock vão pondo e tirando ordens.

### 10.2 As variáveis do Stock

- `lastPrice` (último preço): começa em 0,50 €. É atualizado a cada negócio e é a referência do colar dinâmico.
- `refPrice` (preço de referência): começa em 0,50 €. É a referência do colar estático. No início de cada dia passa a ser o último preço do dia anterior, e depois de cada leilão passa a ser o preço do leilão.
- `ma` (média móvel): uma média do preço que "esquece" devagar o passado. Os chartists comparam o preço com esta média para saber se há tendência.
- `halted`: verdadeiro durante uma reserva, falso no resto do tempo.
- `volume`: o total de ações negociadas desde o início. É do tipo `long` (número inteiro grande). Começou por ser `int`, mas o João avisou que numa corrida de um ano o volume chegava a mil milhões e ia passar o limite do `int` (cerca de 2 147 milhões); quando isso acontece o número "dá a volta" e fica negativo sem dar erro. Por isso mudámos para `long` a 9 de novembro.
- `lastStaticDir`: lembra o sentido (subida +1 ou descida −1) do último colar estático do dia. Serve para saber se um novo colar estático é "repetido" e deve dar a reserva de 10 minutos.
- `haltStart` e `prePrice`: guardam o início da reserva e o preço antes dela, para escrever no ficheiro das interrupções.

### 10.3 O caminho de uma ordem, função a função

Vou seguir uma ordem do princípio ao fim.

**Passo 1: o investidor chama `order`.** Quando um investidor decide negociar, o código dele faz algo como `main.stock.order(this, 1, 0.50, 500)`, que quer dizer "eu, compra, 0,50 €, 500 ações". A função `order` cria a ficha (`new Order()`) e preenche-a: dá-lhe o próximo número, copia o lado e a quantidade, arredonda o preço ao tick, regista a hora, e calcula o prazo. O prazo é a hora atual mais `orderLife` (35 minutos) multiplicado por um número ao acaso entre 0,3 e 1,7; ou seja, cada ordem vive entre cerca de 10 e 60 minutos. Depois a função vê se o mercado está em reserva. Se estiver, a ordem vai para o `pending`. Se não estiver, chama `addToBook` e logo a seguir `match`.

**Passo 2: `addToBook` mete a ordem na fila certa.** É uma linha só: se o lado é 1, a ordem vai para `bids`; senão vai para `asks`. A fila arruma-a sozinha.

**Passo 3: `match` tenta fazer negócios.** Esta função é um ciclo que se repete enquanto o mercado não estiver em reserva e houver ordens dos dois lados. Em cada volta:

1. Olha para a primeira ordem de cada fila: a melhor compra `b` e a melhor venda `a`.
2. Se a compra paga menos do que a venda pede (`b.price < a.price`), não há negócio possível e o ciclo pára.
3. Se os preços se cruzam, decide o preço do negócio. A regra é usar o preço da ordem **que já estava no livro**, ou seja, a que tem o `id` mais baixo. Isto é o que acontece na bolsa real: quem chega e aceita o preço de alguém que já estava à espera paga o preço desse alguém.
4. Antes de fazer o negócio, pergunta ao `collarHit` se esse preço dispara algum colar. Se disparar, a função termina sem negociar (o Stock vai entrar em reserva).
5. Se não disparar, chama `execute` com a quantidade menor das duas ordens.
6. Volta ao início. Isto é importante: uma ordem de compra grande pode "comer" várias ordens de venda seguidas, a preços cada vez piores. A isto chama-se "varrer" níveis do livro.

**Passo 4: `collarHit` verifica os colares.** Primeiro, se os colares estiverem desligados (cenário sem colares), responde logo "não". Senão calcula duas coisas: se o preço se afasta mais de 3% do último preço (colar dinâmico) e se se afasta mais de 8% do preço de referência (colar estático). Se nenhum dispara, responde "não". Se algum dispara, vê o sentido (subida ou descida) e manda uma mensagem ao statechart do próprio Stock. Se for o colar estático e no mesmo sentido do último colar estático do dia, manda "STATIC_REPEAT" (reserva de 10 minutos). Se for o colar estático noutro sentido ou pela primeira vez, guarda o sentido e manda "STATIC". Se só disparou o dinâmico, manda "DYNAMIC". Em qualquer destes casos responde "sim", e o negócio não acontece.

**Passo 5: `execute` faz o negócio.** Atualiza o último preço, soma a quantidade ao volume, tira essa quantidade às duas ordens, e chama `onFill` (uma função do Main) duas vezes, para atualizar o dinheiro e as ações do comprador e do vendedor. Por fim, a ordem que ficou com quantidade zero sai da fila (`poll`). A outra fica na fila com o que sobrou. Isto é a **execução parcial**: se alguém queria 500 ações e só havia 200 à venda, compra 200 e fica com uma ordem de 300 à espera.

**Passo 6: a ordem sai do livro.** Uma ordem só sai do livro de uma de três maneiras: (1) foi toda executada; (2) passou o prazo, e o evento `purgeEvent`, que corre a cada minuto, apaga-a; (3) o investidor cancelou as suas ordens com `cancelAll` (o market maker faz isto a cada minuto).

### 10.4 As outras funções do Stock

- `bestBid` e `bestAsk` devolvem o preço da primeira ordem de cada fila (ou "não há" se a fila estiver vazia).
- `mid` devolve o ponto médio entre os dois. Se faltar um dos lados, devolve o último preço, para os investidores terem sempre uma referência.
- `spread` devolve a diferença entre o ask e o bid.
- `cancelAll(a)` apaga todas as ordens de um agente, dos dois lados.
- `startHalt` é chamada quando começa uma reserva: põe `halted` a verdadeiro, guarda a hora e o preço, avisa toda a gente com "HALT" e soma 1 ao contador de interrupções.
- `endHalt` é chamada no fim: soma a duração ao tempo total em reserva, escreve uma linha no ficheiro `halts.csv` e avisa toda a gente com "REOPEN".
- `runAuction` faz o leilão (explicado em 10.6).
- `testBook` e `check` fazem os testes (explicados em 10.7).

### 10.5 O statechart do Stock

O Stock tem um statechart com cinco estados:

- **Continuous** (negociação contínua): o estado normal. Ao entrar, põe `halted` a falso e corre o `match` uma vez, para negociar o que tenha ficado cruzado.
- **ReservDynamic**: reserva causada pelo colar dinâmico. Entra-se com a mensagem "DYNAMIC". Ao entrar chama `startHalt`. Sai ao fim de `haltShort` (3 minutos).
- **ReservStatic**: reserva causada pelo colar estático. Entra-se com "STATIC". Também dura 3 minutos.
- **ReservStatic10**: reserva causada pelo colar estático repetido no mesmo sentido. Entra-se com "STATIC_REPEAT". Dura `haltLong` (10 minutos).
- **Auction** (leilão): depois de qualquer reserva. Ao entrar, despeja as ordens do `pending` no livro. Passado 0,01 minutos, corre `runAuction` e `endHalt` e volta a Continuous.

É por causa destes 0,01 minutos que, na consola, uma reserva aparece como 3,01 minutos (de "HALT" a "REOPEN") e não 3,00.

Há ainda três eventos no Stock:

- `purgeEvent`, a cada minuto: apaga as ordens com o prazo vencido.
- `dayEvent`, a cada 510 minutos (início de cada dia): o preço de referência passa a ser o último preço, e esquece-se o sentido do último colar estático.
- `maEvent`, a cada minuto: atualiza a média móvel com a fórmula `ma = ma + (lastPrice − ma) / maWindow`. Com `maWindow` = 50, a cada minuto a média anda 1/50 do caminho até ao preço atual. É uma média que dá mais peso ao passado recente.

### 10.6 O leilão de reabertura

O leilão escolhe **um só preço** para todas as ordens que estão no livro no fim da reserva. Funciona assim:

1. Faz a lista de todos os preços que aparecem nas ordens (são os preços candidatos).
2. Para cada preço candidato p, calcula a **procura** (quantas ações querem comprar os que aceitam pagar p ou mais) e a **oferta** (quantas ações querem vender os que aceitam receber p ou menos). O volume que se consegue negociar a esse preço é o menor dos dois.
3. Escolhe o preço que dá **mais volume**. Se houver empate, escolhe o mais perto do último preço.
4. **Colar do leilão**: o preço escolhido não pode ficar a mais de 6% do último preço antes da reserva. Se ficar, é empurrado para o limite (6% acima ou abaixo).
5. Executa todas as ordens que se cruzam a esse preço único.
6. **Caso especial**: se, mesmo assim, o leilão não conseguir negociar nada dentro do colar e o livro continuar cruzado (há compradores dispostos a pagar mais do que os vendedores pedem, mas fora da faixa de 6%), o último preço passa para o limite do colar. Isto faz com que a seguir haja nova reserva, e o preço aproxime-se 6% de cada vez do nível a que o mercado quer negociar.
7. O preço do leilão passa a ser a nova referência do colar estático.

Os pontos 4 e 6 foram acrescentados durante o trabalho, por causa de problemas encontrados na calibração (ver capítulo 18).

### 10.7 Os testes do livro de ordens

Os professores recomendaram construir e testar o livro de ordens **antes** de pôr investidores no modelo. Por isso há uma função `testBook` com 6 testes, que se corre pondo `runTests` a verdadeiro e `nNoise` a 0. Cada teste envia ordens "à mão" e verifica o resultado com a função `check`, que escreve PASS ou FAIL na consola. No total são 11 verificações:

1. **Sem cruzamento não há negócio.** Uma compra a 0,50 e uma venda a 0,51 ficam as duas no livro: o volume é 0 e o spread é 0,01.
2. **Um negócio simples.** Chega uma venda de 40 a 0,50: negoceia 40 a 0,50, e a compra fica com 60.
3. **Prioridade de chegada.** Chega outra compra de 10 a 0,50 (fica atrás da de 60, porque chegou depois) e uma venda de 65. A venda come primeiro as 60 da compra antiga e depois 5 da nova. O volume total é 105 e a segunda compra fica com 5.
4. **Varrer dois níveis.** Há uma venda de 100 a 0,52. Chega uma compra de 150 a 0,52. A compra come primeiro o que resta a 0,51 e depois parte da de 0,52. O volume passa a 255, o último preço é 0,52 e ficam 50 à venda a 0,52.
5. **O colar bloqueia.** Liga-se os colares e envia-se uma venda a 0,40 (−23%). O negócio não acontece: o volume continua 255.
6. **Cancelamento.** `cancelAll` esvazia o livro.

No modelo final, os 11 resultados dão PASS. Depois dos testes o modelo continua a correr; com `nNoise` = 0 não há noise traders a dar liquidez, por isso aparecem muitas reservas na consola, mas isso não interessa: só serve para testar.

## 11. O Main: o mundo

O Main é o agente de topo. Tem as populações, os parâmetros globais, os indicadores e os ficheiros.

### 11.1 Os parâmetros, um a um

**Parâmetros do mercado e do livro de ordens**

- `initialPrice` = 0,50 €. O preço inicial da ação e também o valor fundamental inicial. É a ordem de grandeza do BCP.
- `tickSize` = 0,0001 €. O tick é o menor passo de preço permitido; todos os preços são arredondados a este valor. Na Euronext o tick muda com o preço (há uma tabela); nós usamos um valor fixo por simplicidade.
- `orderLife` = 35 minutos. A vida média de uma ordem que não é executada. Cada ordem vive `orderLife` vezes um número ao acaso entre 0,3 e 1,7, ou seja, entre cerca de 10 e 60 minutos. Não há dados de Lisboa sobre cancelamentos, por isso é um pressuposto, ajustado na calibração.
- `maWindow` = 50 minutos. A memória da média móvel que os chartists usam. Curta demais e reagem a ruído; longa demais e não veem uma queda a meio da sessão.
- `runTests` = falso. Se for verdadeiro, os testes do livro correm no arranque.

**Parâmetros dos colares, reservas e leilão**

- `collarSet` = 2. Escolhe o conjunto de colares: 0 quer dizer sem colares; 1 quer dizer 2% e 5% (mais apertados); 2 quer dizer 3% e 8% (os reais); 3 quer dizer 5% e 10% (mais largos); 4 quer dizer valores personalizados. É assim que as experiências comparam colares diferentes.
- `customDyn` = 0,03 e `customStat` = 0,08. Os colares usados quando `collarSet` é 4. Servem para testar os "limiares ótimos".
- `haltShort` = 3 minutos e `haltLong` = 10 minutos. A duração das reservas.
- `auctionCollar` = 0,06. O colar do leilão: 6%. É o valor da Euronext para o PSI (coluna "Col U" do anexo).
- `tradeDuringHalt` = verdadeiro. Se for verdadeiro, os fundamentalistas e os chartists continuam a decidir e a enviar ordens durante as reservas (as ordens vão para o `pending`). Na primeira versão do modelo eles paravam; mudou na ronda 8b da calibração, porque o manual da Euronext diz que os membros podem pôr, alterar e cancelar ordens durante uma reserva.

**Parâmetros dos investidores**

- `nNoise` = 30. Número de noise traders.
- `noiseRate` = 1 por minuto. Cada noise trader envia em média uma ordem por minuto.
- `noiseSigma` = 0,002. A dispersão dos preços dos noise traders: põem as ordens tipicamente a 0,2% do mid.
- `nFundamentalists` = 40. Número de fundamentalistas.
- `fundRate` = 0,2 por minuto. Cada fundamentalista pensa em média uma vez a cada 5 minutos.
- `fundBand` = 0,01. Um fundamentalista só age se o preço estiver mais de 1% longe do valor que ele acha que a ação tem.
- `nChartists` = 13. Número de chartists. Começou em 30 e foi reduzido para 15 e depois 13 na calibração, porque com 30 havia demasiada manada e o mercado ficava volátil demais.
- `chartRate` = 0,2 por minuto. Ritmo de decisão base de cada chartist (multiplicado pela atenção, ver mais abaixo).
- `trendThreshold` = 0,005. O chartist só vê tendência se o preço estiver mais de 0,5% acima ou abaixo da média móvel.
- `herdThreshold` = 2. Um chartist entra em pânico se receber pelo menos 2 avisos de venda dos vizinhos.
- `panicDuration` = 10 minutos. Quanto tempo dura o pânico.
- `mmSpread` = 0,004. O spread do market maker: compra 0,2% abaixo do mid e vende 0,2% acima.
- `mmQty` = 2000. Quantas ações o market maker oferece de cada lado.

**Parâmetros das notícias e do choque**

- `newsRate` = 0,002 por minuto. O ritmo das notícias pequenas: 0,002 × 510 ≈ 1 notícia por dia. Cada notícia muda o valor da empresa em cerca de ±2%. Começou em 0,0004 (uma notícia a cada 5 dias, ±1%) e foi aumentado na ronda 1 da calibração, porque a volatilidade era muito baixa.
- `shockOn` = falso. Liga o choque grande. Nos cenários de choque passa a verdadeiro.
- `shockTime` = 30 600 minutos. O choque acontece no dia 60.
- `shockSize` = −0,10. O choque é uma queda de 10% no valor da empresa. É inspirado no caso BES, mas não é uma reprodução dele.
- `shockPanicProb` = 0,3. Quando o choque acontece, cada chartist tem 30% de probabilidade de entrar logo em pânico.
- `scenario` = "baseline". O nome do cenário, que vai para os ficheiros de saída.

**Parâmetros da atividade e da atenção** (acrescentados na calibração; explicados no capítulo 12)

- `activityPersist` = 0,6, `activitySigma` = 0,05 e `activityNewsJump` = 0,4: controlam a atividade diária dos noise traders.
- `attPersist` = 0,7 e `attWeight` = 0,6: controlam a atenção dos chartists.
- `useAttChart` = verdadeiro: liga a atenção nos chartists.
- `useAttNoise` = falso: ligaria a atenção nos noise traders (opção testada e não usada).

### 11.2 As variáveis do Main

- `fundamentalValue`: o valor "verdadeiro" da empresa. Começa em 0,50 € e muda com as notícias. Ninguém o vê exatamente: cada fundamentalista vê-o com um pequeno erro pessoal.
- `nextOrderId`: o contador que dá o número às ordens.
- `dynamicThreshold` e `staticThreshold`: os colares em vigor (por defeito 3% e 8%). São definidos no arranque a partir de `collarSet`.
- `collarsActive`: falso se `collarSet` for 0.
- `label`: um nome que identifica o cenário nos ficheiros. É construído juntando o cenário, o conjunto de colares, a duração da reserva e o número de chartists; por exemplo "shock_c2_h3.0_n13".
- `runId`: um código ao acaso de 8 caracteres que identifica cada corrida.
- `peakPrice` e `maxDrawdown`: o preço máximo até agora e a maior queda desde um máximo (um dos indicadores principais).
- `nHalts` e `timeHalted`: quantas reservas houve e quanto tempo o mercado esteve parado.
- `activity`: o nível de atividade do dia dos noise traders. Começa em 1.
- `attention`: o nível de atenção do dia dos chartists. Começa em 1.
- `dayOpen`: o preço no início do dia, para medir quanto o preço mexeu nesse dia.

### 11.3 As funções do Main

- `roundTick(p)`: arredonda um preço ao tick (e nunca deixa ficar abaixo de um tick, para o preço não chegar a zero).
- `onFill(t, side, q, p)`: chamada depois de cada negócio para cada um dos dois lados. Se foi uma compra, o investidor ganha q ações e perde q × p euros; se foi uma venda, perde as ações e ganha o dinheiro. Funciona para os quatro tipos de investidor.
- `broadcast(msg)`: escreve a mensagem na consola (é daí que vêm as linhas "t = … min HALT") e entrega-a ao statechart de todos os fundamentalistas, chartists, market maker e NewsAgent. Os noise traders não recebem, porque não têm statechart.

### 11.4 Os eventos do Main

- `logEvent`, a cada minuto: atualiza o preço máximo e a queda máxima, e escreve uma linha no ficheiro `precos.csv` com o cenário, a corrida, o minuto, o último preço, o bid, o ask e o volume acumulado.
- `activityEvent`, uma vez por dia (a cada 510 minutos): atualiza a atividade e a atenção (explicado no capítulo 12).

### 11.5 O arranque e o fim

Quando a simulação começa (*On startup*), o Main:

1. Corre os testes, se `runTests` for verdadeiro.
2. Define os colares conforme `collarSet`.
3. Inicia o preço máximo e constrói o `label`.
4. Constrói a **rede dos chartists**. Imagina os 13 chartists sentados numa roda. Cada um liga-se aos 3 seguintes na roda (e como as ligações são nos dois sentidos, cada um fica com cerca de 6 vizinhos). Mas, em 5% dos casos, em vez do vizinho da roda, liga-se a um chartist qualquer ao acaso. Esta mistura de vizinhos próximos com algumas ligações longas chama-se rede *small world* ("mundo pequeno"). É o tipo de rede usado no modelo de mercado das aulas e faz com que um pânico possa espalhar-se depressa.

Quando a simulação acaba (*On destroy*), fecha os dois ficheiros e escreve na consola o número de reservas, o tempo em reserva e a queda máxima.

### 11.6 Os ficheiros de saída

Os resultados ficam na pasta `model/Euronext_Main/output/`:

- `precos.csv` tem uma linha por minuto com: cenário, corrida, minuto, preço, bid, ask e volume. Numa corrida de um ano são 127 500 linhas.
- `halts.csv` tem uma linha por interrupção com: cenário, corrida, início, fim, preço antes e preço do leilão.

Os scripts Python do João leem estes ficheiros para calcular os indicadores.

## 12. A atividade e a atenção: a memória entre dias

Estes dois mecanismos foram acrescentados durante a calibração. Servem para dar ao mercado **memória de um dia para o outro**, que antes não existia.

### 12.1 A atividade dos noise traders

No mercado real, há dias com muito movimento e dias calmos, e os dias de muito movimento tendem a vir seguidos. Também há mais negócios nos dias em que saem notícias. No início, os noise traders negociavam sempre ao mesmo ritmo e com as mesmas quantidades, por isso o volume não tinha estas características.

A solução foi criar a variável `activity`, que multiplica a quantidade das ordens dos noise traders. Uma vez por dia, o `activityEvent` atualiza-a assim:

`activity = exp( activityPersist × log(activity) + N(0, activitySigma) − activityNewsJump × newsRate × 510 )`

Em palavras: o logaritmo da atividade de hoje é 60% (`activityPersist`) do de ontem, mais uma pequena parte ao acaso (`activitySigma` = 5%). Isto faz com que a atividade se lembre dos dias anteriores, mas vá voltando ao normal. Além disso, cada notícia multiplica a atividade por `exp(0,4)`, ou seja, aumenta-a cerca de 49% (isto está no NewsAgent). O último termo da fórmula desconta o aumento médio que as notícias dão num dia, para a atividade não crescer sem parar.

O resultado é que o volume passou a ser persistente (um dia com muito volume tende a ser seguido de outro) e mais alto nos dias de notícias, como no BCP real.

### 12.2 A atenção dos chartists

Mesmo com a atividade, faltava outra característica do mercado real: um dia **agitado** (com o preço a mexer muito) tende a ser seguido de outro dia agitado. A isto chama-se **clustering da volatilidade**. O nosso modelo quase não o tinha.

A solução final foi a **atenção**. A ideia vem de um estudo de Barber e Odean (2008): os investidores negoceiam mais nas ações que lhes chamam a atenção, por exemplo depois de movimentos fortes. No modelo, uma vez por dia, o `activityEvent` faz:

1. Mede quanto o preço mexeu nesse dia: `r = |log(último preço / preço no início do dia)|`.
2. Guarda o preço atual como início do dia seguinte.
3. Atualiza a atenção: `attention = min(3, exp( attPersist × log(attention) + attWeight × (r / 0,0165 − 1) ))`.

Em palavras: se o preço mexeu mais do que um dia normal (1,65%), a atenção sobe; se mexeu menos, desce. Tem memória (`attPersist` = 0,7), por isso vai baixando aos poucos depois de um dia agitado. O `min(3, …)` impede que passe de 3.

Depois, o ritmo de decisão dos chartists passa a ser `chartRate × attention`. Depois de um dia agitado os chartists decidem mais vezes durante alguns dias, o que tende a manter a agitação.

## 13. Os investidores

### 13.1 Noise traders: os aleatórios (30)

Os noise traders representam os pequenos investidores que negoceiam por razões que nada têm a ver com a empresa: precisam de dinheiro, ouviram um palpite, querem experimentar. O nome vem de *noise* (ruído).

Não têm statechart, só um evento chamado `trade`, que dispara ao acaso com um ritmo de uma vez por minuto (é um processo de Poisson: em média uma vez por minuto, mas os intervalos variam). De cada vez:

1. Decidem ao acaso, com 50% de probabilidade, se compram ou vendem.
2. Escolhem um preço perto do mid: `mid × (1 + N(0; 0,2%))`, ou seja, normalmente a menos de 0,2% do mid, umas vezes acima, outras abaixo.
3. Escolhem uma quantidade ao acaso entre 100 e 1000 ações, multiplicada pela atividade do dia.
4. Enviam a ordem ao Stock.

Têm 1 000 milhões de euros (`cash` = 1e9) e começam com zero ações (`position` = 0), e podem ficar com ações negativas (vender a descoberto). Ou seja, nunca ficam sem dinheiro nem sem ações.

**Para que servem:** dão **liquidez** (há sempre ordens perto do preço, por isso há sempre alguém para negociar) e o volume de base. Continuam a enviar ordens durante as reservas; essas ordens ficam à espera do leilão.

### 13.2 Fundamentalistas: os racionais (40)

Os fundamentalistas representam os analistas e os fundos que estudam as contas da empresa. Têm uma ideia de **quanto vale** a ação e compram quando está barata e vendem quando está cara.

Cada fundamentalista tem um erro pessoal, chamado `bias`, sorteado uma vez quando nasce, de uma distribuição normal com média 0 e desvio de 2%. O valor que ele acha que a ação tem é `value() = fundamentalValue × (1 + bias)`. Assim, nem todos pensam o mesmo: uns acham que vale um pouco mais, outros um pouco menos. Isto evita que os 40 comprem ou vendam todos ao mesmo tempo.

O statechart funciona assim. O fundamentalista está no estado **Watching** (a observar). Em média uma vez a cada 5 minutos (`fundRate`), passa ao ramo **decide**, onde compara o mid com o seu valor:

- Se o mid está mais de 1% **abaixo** do seu valor e ele tem dinheiro, vai para **Buying**: compra. A quantidade é `100 + 20 000 × (valor/mid − 1)`, ou seja, quanto mais barata está a ação, maior a ordem. O preço é o menor entre o seu valor e o mid mais 0,2% (não quer pagar mais do que acha que vale).
- Se o mid está mais de 1% **acima** do seu valor e ele tem ações, vai para **Selling**: vende, com a regra ao contrário.
- Se não tem dinheiro nem ações, vai para **OutOfCash** e espera 60 minutos. No modelo calibrado isto nunca acontece, porque têm dinheiro e ações praticamente ilimitados (1 000 milhões de cada).
- Caso contrário, volta a Watching.

Depois de comprar ou vender, volta logo a Watching.

Há ainda um estado **Halted**: quando chega a mensagem "HALT", o fundamentalista para até chegar "REOPEN". Mas esta transição tem uma condição: só acontece se `tradeDuringHalt` for falso. No modelo final é verdadeiro, por isso os fundamentalistas **não param** durante as reservas.

**Para que servem:** puxam o preço para o valor da empresa, ou seja, estabilizam o mercado.

### 13.3 Chartists: os seguidores de tendência e a manada (13)

Os chartists não querem saber do valor da empresa. Olham para o **gráfico** do preço (daí o nome, de *chart*) e seguem a tendência: se está a subir, compram; se está a descer, vendem. E falam uns com os outros.

Cada chartist está ligado aos vizinhos na rede *small world* construída no arranque. Tem uma variável `sellSignals`, que conta quantos avisos de venda recebeu. A cada 30 minutos um evento chamado `forget` põe-na a zero (os avisos antigos são esquecidos).

O statechart funciona assim. O chartist está no estado **Neutral**. Há três coisas que o podem tirar de lá:

1. **A sua própria decisão.** Ao ritmo `chartRate × attention` (em média uma vez a cada 5 minutos num dia normal), vai ao ramo **decide**, onde compara o último preço com a média móvel:
   - Se o preço está mais de 0,5% acima da média (tendência de subida) e tem dinheiro, vai para **TrendBuy**: compra até 500 ações a 0,3% acima do mid.
   - Se está mais de 0,5% abaixo (tendência de descida) e tem ações, vai para **TrendSell**: vende até 500 ações a 0,3% abaixo do mid e **avisa os vizinhos** com a mensagem "SELL_SIGNAL".
   - Senão, volta a Neutral.
2. **Um aviso de um vizinho.** Quando recebe "SELL_SIGNAL", soma 1 aos avisos e vai ao ramo **herd** (manada). Se já tem pelo menos 2 avisos (`herdThreshold`) e tem ações, entra em **Panic**. Senão volta a Neutral.
3. **O choque.** Quando recebe "SHOCK" e o choque é uma queda, com 30% de probabilidade entra diretamente em **Panic**.

No estado **Panic**, o chartist vende até 2000 ações a 1% abaixo do mid (quer sair a qualquer preço) e também avisa os vizinhos. Fica em pânico 10 minutos (`panicDuration`) e depois volta a Neutral com os avisos a zero.

É aqui que nasce a **cascata**: um chartist vende e avisa os vizinhos; os vizinhos, com avisos suficientes, entram em pânico e vendem muito e barato; isso faz o preço cair; a queda faz outros chartists verem uma tendência de descida e venderem também, e assim por diante. É exatamente este tipo de espiral que os colares podem cortar a meio.

Tal como os fundamentalistas, têm um estado **Halted** que só é usado se `tradeDuringHalt` for falso.

### 13.4 Market maker: o intermediário (1)

O market maker representa os bancos e corretoras contratados pela bolsa para dar liquidez. Está sempre disponível para comprar e vender.

No estado **Quoting**, a cada minuto chama a função `quote`: cancela as suas ordens antigas e põe duas novas, uma compra de 2000 ações a 0,2% abaixo do mid e uma venda de 2000 ações a 0,2% acima. Assim garante que há sempre um preço para comprar e um para vender.

Quando chega "HALT" passa para **Paused** e cancela as suas ordens (não participa no leilão). Quando chega "REOPEN" volta a Quoting.

Uma limitação importante: o market maker **não tem limite de inventário** e nunca sai do mercado. Na realidade, numa crise, os market makers alargam o spread ou retiram-se. Isto torna o nosso mercado mais resistente do que o real (ver capítulo 21).

### 13.5 NewsAgent: as notícias (1)

O NewsAgent é quem faz mexer o valor da empresa. Tem três estados:

- **Calm** (calma): o estado normal. Ao ritmo `newsRate` (cerca de uma vez por dia) gera uma notícia pequena: o valor fundamental é multiplicado por `(1 + N(0; 2%))`, ou seja, muda tipicamente uns 2% para cima ou para baixo. Ao mesmo tempo a atividade dos noise traders aumenta.
- **BigShock** (choque grande): se `shockOn` for verdadeiro, um evento chamado `shockEvent` manda ao próprio NewsAgent a mensagem "BIG_SHOCK" no minuto 30 600 (dia 60). Ao entrar neste estado, o valor fundamental é multiplicado por `(1 + shockSize)`, ou seja, cai 10%, e toda a gente é avisada com "SHOCK".
- **Fading** (a desvanecer): 30 minutos depois do choque, o NewsAgent passa a este estado durante 120 minutos, em que há pequenas réplicas (notícias de cerca de −0,3% ± 0,5%), como acontece na realidade depois de uma má notícia. Depois volta a Calm.

## 14. As mensagens

Há seis mensagens no modelo:

- "DYNAMIC", "STATIC" e "STATIC_REPEAT" são enviadas pelo `collarHit` ao statechart do próprio Stock, para entrar no tipo de reserva certo.
- "HALT" é enviada pelo Stock a todos, através do `broadcast`, quando começa uma reserva. O market maker retira-se; os outros continuam (porque `tradeDuringHalt` é verdadeiro).
- "REOPEN" é enviada pelo Stock a todos quando o leilão acaba.
- "BIG_SHOCK" é enviada pelo evento do choque ao NewsAgent.
- "SHOCK" é enviada pelo NewsAgent a todos quando o choque acontece; alguns chartists entram em pânico.
- "SELL_SIGNAL" é enviada por um chartist que vende ou entra em pânico aos seus vizinhos na rede (efeito manada).

---

# Parte IV · Dados, calibração e experiências

## 15. Os dados reais

A referência do modelo é a ação do BCP. O João descarregou do Yahoo Finance (gratuito) os preços e volumes **diários** do BCP desde janeiro de 2010, com o script `download_daily.py`. Também está a guardar os preços **de minuto a minuto**, com o script `archive_intraday.py`; como o Yahoo só guarda cerca de uma semana de dados por minuto, o script tem de ser corrido duas vezes por semana.

Na proposta tinham sido prometidas mais fontes: estatísticas mensais da Euronext e da CMVM (número de negócios por mês, para saber quantas ordens chegam), dados tick a tick do Bloomberg da FEP ("só se houver acesso"), e amostras de livros de ordens de outros mercados (para o tempo de vida das ordens). Nenhuma destas foi usada: os valores correspondentes são pressupostos documentados e ajustados na calibração. A única fonte da proposta que usamos é o relatório da ESMA (2020), para validar o efeito das interrupções. Convém explicar isto numa frase na secção 3.1 do relatório.

## 16. Os factos estilizados

Um **facto estilizado** é uma característica que os preços das ações reais mostram quase sempre, em qualquer mercado. Para sabermos se o nosso mercado artificial se parece com o real, escolhemos sete factos e medimo-los no BCP real e no modelo. Os valores do BCP são do período 2023–2024 (510 dias de negociação).

1. **Volatilidade diária.** Quanto o preço mexe por dia, em média. No BCP é 2,07% (o desvio-padrão dos retornos diários é 0,0207). O modelo bate se ficar a menos de 25% deste valor.
2. **Caudas pesadas.** Os dias de movimentos muito grandes são mais frequentes do que numa distribuição normal. Mede-se com a curtose em excesso (0 numa normal). No BCP é 2,41. O modelo bate se for maior que 1 e estiver a menos de 50% do valor do BCP.
3. **Clustering da volatilidade.** Um dia agitado tende a ser seguido de outro dia agitado. Mede-se com a autocorrelação dos retornos em valor absoluto de um dia para o seguinte. No BCP é 0,080. O modelo bate se for maior que 0,05.
4. **Ausência de autocorrelação dos retornos.** Saber se hoje subiu não ajuda a prever se amanhã sobe (senão toda a gente ganhava dinheiro fácil). No BCP a autocorrelação é 0,004, praticamente zero. O modelo bate se ficar entre −0,1 e 0,1.
5. **Frequência de movimentos grandes.** A percentagem de dias em que o preço mexe mais de 3%. No BCP é 12,9%. O modelo bate se estiver a menos de 50% deste valor.
6. **Relação volume–volatilidade.** Nos dias agitados negoceia-se mais. No BCP a correlação entre o volume e o tamanho do movimento é 0,636. O modelo bate se for positiva.
7. **Persistência do volume.** Um dia de muito volume tende a ser seguido de outro. No BCP a autocorrelação do volume é 0,470. O modelo bate se for positiva.

Estes alvos e critérios foram **fixados antes** de ajustar o modelo, para não haver a tentação de mudar os alvos para o modelo passar.

**Porquê 2023–2024?** Porque estava no plano do projeto desde o início, é recente (as regras da Euronext e a forma de negociar são as de hoje) e não tem crises do BCP (a crise da dívida em 2011–2013, o BES em 2014 e a COVID em 2020 ficam de fora). O ano de 2025 não entrou: não estava no plano e tem o choque das tarifas americanas de abril de 2025 (o BCP caiu 9,9% a 4 de abril). O João fez um teste de robustez com 2023, 2024 e 2025 separados: os factos principais são parecidos em todos os anos, e os que variam mais (clustering, autocorrelação dos retornos e persistência do volume) são precisamente os mais difíceis de calibrar.

Também foram medidos dois períodos de stress, só como referência para ver se os choques simulados são plausíveis: o BES (15 de julho a 30 de setembro de 2014) e o início da COVID (15 de fevereiro a 30 de abril de 2020).

## 17. Os scripts Python

- `download_daily.py` descarrega os preços diários do BCP.
- `archive_intraday.py` guarda os preços de minuto a minuto.
- `target_stats.py` calcula os sete factos do BCP para um período.
- `make_metas.py` junta os alvos dos três períodos num Excel.
- `compare_model.py` lê o `precos.csv` do modelo, calcula os sete factos para cada corrida e compara-os com os alvos. É a ferramenta da calibração.
- `kpis.py` calcula os indicadores de cada interrupção (volatilidade e spread antes e depois, salto do leilão) e de cada corrida, e faz a validação da ESMA. Junta as reservas seguidas a menos de 1 minuto numa só interrupção.
- `kpis_choque.py` calcula os indicadores do choque (queda máxima, tempo de recuperação, etc.) para ficheiros muito grandes, lendo-os aos bocados.
- `recomendacao.py` faz a tabela de recomendação a partir do Cenário 4.

## 18. A calibração, ronda a ronda

**Calibrar** quer dizer ajustar os parâmetros que não conhecemos até o modelo reproduzir os factos estilizados. Cada ronda correu 10 réplicas de 250 dias (um ano) do cenário base e mediu os sete factos.

**Ronda 0 – valores iniciais.** Só 2 de 7 factos. O mercado era calmo demais: volatilidade de 0,42% por dia, cinco vezes menos do que o BCP.

**Ronda 1 – mais notícias.** As notícias passaram de uma a cada 5 dias para cerca de uma por dia, e de ±1% para ±2%. Passou a 4 de 7.

**Ronda 2 – mais dinheiro.** Os fundamentalistas e chartists começavam com pouco dinheiro (5000 €) e poucas ações (10 000) e esgotavam-se; multiplicou-se por 10. Continuou em 4 de 7. Nesta ronda uma corrida mostrou um problema grave: o preço caiu de 0,84 € para 0,02 € em dois dias, através de leilões sucessivos, cada um a um preço muito mais baixo do que o anterior. Isto levou ao colar do leilão (ronda 4).

**Ronda 3 – sem limite de orçamento.** Mesmo com 10 vezes mais, os agentes esgotavam-se e o mercado "morria" a meio do ano. Passaram a ter dinheiro e ações praticamente ilimitados (1 000 milhões). O mercado deixou de morrer, mas ficou agitado demais (3,6% por dia) e com autocorrelação negativa dos retornos (o preço passava do ponto num dia e corrigia no seguinte). Continuou em 4 de 7. Como as notícias sozinhas davam cerca de 2% de volatilidade, o excesso vinha dos chartists.

**Ronda 4 – menos chartists e colar do leilão.** Os chartists passaram de 30 para 15, e o leilão passou a ter o colar de ±6% da Euronext. Passou a 6 de 7.

**Ronda 5 – 13 chartists.** Passou 7 de 7. Mas à justa: a persistência do volume era 0,001 (passa o critério "positiva", mas o BCP tem 0,47, ou seja, na prática o modelo não reproduzia este facto), o clustering estava mesmo em cima do limiar (0,053), e a autocorrelação dos retornos só passava em 5 das 10 corridas. Como os professores pediram para validar o volume, decidiu-se continuar.

**Ronda 6 – atividade diária.** Criou-se a atividade dos noise traders (capítulo 12), ao acaso. A persistência do volume subiu para 0,66, mas a correlação volume–volatilidade caiu para 0,02 (a atividade não tinha nada a ver com o que fazia o preço mexer). Ficou em 6 de 7. Nesta ronda apareceu outro problema: uma corrida (a 47d0b7e6) ficou presa num ciclo de 1485 reservas, com o preço congelado em 0,5638 €. O leilão não conseguia negociar nada dentro do colar de 6%, o último preço nunca mudava, e ao reabrir o colar disparava logo outra vez. A correção foi a regra do caso especial do leilão (10.6, ponto 6): o último preço passa para o limite do colar. O João confirmou depois no manual da Euronext (versão de 5 de julho de 2021, secção 4.2.4) que é isto que a Euronext faz: muda os limites e o limite superior ou inferior passa a ser o novo preço de referência.

**Ronda 7 (7b) – atividade ligada às notícias.** Cada notícia passou a aumentar a atividade. Os dois factos de volume passaram a bater "a sério" (correlação volume–volatilidade 0,25 e persistência 0,60). Ficou em 6 de 7: falhava o clustering, que caiu para 0,008.

**Ronda 8 – notícias em ondas.** Tentou-se fazer com que as notícias chegassem mais vezes quando a atividade estava alta ("notícias atraem notícias"). O clustering voltou (0,065), mas as ondas eram grandes demais: volatilidade de 2,87%, 26% de dias acima de 3%, curtose de 0,96. Só 4 de 7. Foi descartada.

**Ronda 8b – três tentativas.** Testaram-se três formas de dar memória à volatilidade, e ao mesmo tempo o relaxamento das ordens durante as reservas:
- **R0** (só as ordens durante a reserva): 6 de 7. Mostrou que esta mudança não estraga a calibração.
- **A2** (atenção dos chartists, `attWeight` = 0,6): 6 de 7, e a melhor em quase tudo: volatilidade 2,17% (BCP 2,07%), curtose 2,04, autocorrelação −0,05, 16,2% de dias acima de 3%. O clustering subiu para 0,026: positivo, mas ainda abaixo de 0,05.
- **C1** (nervosismo nos noise traders: a dispersão dos preços aumenta depois de dias agitados): 5 de 7. O clustering quase passou (0,049), mas a autocorrelação dos retornos falhou por pouco (−0,1001). Além disso era a opção mais difícil de defender, porque se parece com uma regra imposta ao preço.

**O modelo final é a A2.** Reproduz 6 dos 7 factos, com os dois de volume a sério. Preferiu-se a 6 de 7 "honestos" a 7 de 7 com a persistência do volume só "no papel" (ronda 5).

**Porque é tão difícil o clustering?** Por cinco razões. (1) É preciso memória de dias, e os agentes pensam em minutos. (2) É preciso prolongar o **tamanho** dos movimentos sem prolongar a **direção** (senão estraga-se o facto 4, como aconteceu na C1). (3) Amplificar demais estraga a volatilidade e as caudas (ronda 8). (4) Na realidade o clustering tem muitas causas ao mesmo tempo (notícias em cadeia, investidores que entram e saem, vendas forçadas, liquidez que demora a voltar), e o modelo só tem algumas. (5) É uma medida com muito ruído: com 250 dias por corrida, o erro de uma autocorrelação é cerca de 1/√250 ≈ 0,06, maior do que a diferença entre o nosso 0,026 e o limiar de 0,05. É por isso que no próprio BCP o valor salta entre 0,06 e 0,18 de ano para ano.

## 19. As experiências

Todas as experiências usam sementes fixas para os números ao acaso: a réplica número k usa a semente 1000 + k. Isto tem duas vantagens: os resultados podem ser repetidos exatamente, e a réplica k do cenário com colares e a réplica k do cenário sem colares começam com a mesma "sorte", o que torna a comparação mais justa.

- **Simulation**: uma corrida com os valores por defeito. Serve para ver o modelo a funcionar e para correr os testes.
- **Cenario1** (baseline): o mercado calmo, sem choque, com 13 chartists, 10 réplicas. É o que serve à calibração.
- **Cenario2** (choque com e sem colares): choque de −10% ao dia 60, com `collarSet` 0 (sem colares) e 2 (colares reais), 30 réplicas cada. É a experiência central do trabalho.
- **Cenario3** (manada): o mesmo choque, mas com 60 chartists em vez de 13, com e sem colares, 30 réplicas. Pergunta se os colares ajudam mais quando há muita manada.
- **Cenario4** (grelha): o choque com todas as combinações de colares (0, 1, 2, 3), duração da reserva (3 ou 10 minutos) e número de chartists (de 10 a 60), 30 réplicas cada. São 48 combinações. Serve para procurar os limiares e a duração ótimos.

## 20. Os resultados até agora

**Cenário 2** (30 + 30 réplicas, choque de −10%):

- Os colares disparam sempre: em média 2,6 reservas no dia do choque, cerca de 15 minutos parado.
- Não mudam significativamente a crise. A queda máxima foi de −16,6% sem colares e −17,2% com colares; a diferença não é estatisticamente significativa (p = 0,29, ou seja, pode bem ser acaso). O fecho do dia foi −11,2% contra −11,8%. O tempo até recuperar metade da queda foi de 539 minutos sem colares e 741 com colares (p = 0,18, também não significativo).
- Validação com a ESMA (janela de 5 minutos antes e depois de cada interrupção): a volatilidade desce em 44% das interrupções e o spread alarga em 52%. Não há um efeito sistemático.
- O choque é plausível: a queda de −17% no dia está perto dos piores dias reais do BCP.

**Leitura:** os colares adiam a descoberta do preço, mas não travam uma queda causada por informação nova. Faz sentido: se a empresa vale de facto 10% menos, uma pausa de 3 minutos não muda isso. Mas é preciso ter cuidado, porque o nosso mercado é mais resistente do que o real (sem vendas forçadas e com o market maker sempre presente), e isso pode esconder parte do efeito dos colares numa espiral de pânico.

Os Cenários 3 e 4 já foram corridos e o João calculou os indicadores e a tabela de recomendação (`data/processed/`). A recomendação final e a análise multicritério (estabilidade contra liquidez) ainda vão ser escritas.

---

# Parte V · Decisões, limitações e defesa

## 21. As decisões tomadas, e porquê

Esta é a lista das decisões importantes, pela ordem em que foram tomadas.

**Fazer só a Fase 1.** Foi o que os professores pediram no feedback à proposta.

**Fazer o livro de ordens em Java e testá-lo antes de tudo.** Os professores escreveram no feedback que o livro de ordens ia ser sobretudo código Java e que o devíamos construir e testar primeiro. Além disso, com os blocos da Process Modeling Library cada ordem seria um agente, e a PLE só permite 50 000; a execução dos negócios, as execuções parciais e o leilão teriam sempre de ser programados em Java. Ficou a dúvida se os professores querem ver a PML nalguma parte; o Miguel vai perguntar presencialmente.

**A ordem é uma classe Java e não um agente.** Por causa dos milhões de ordens por corrida.

**Prioridade preço-tempo, e o negócio ao preço da ordem que já estava no livro.** São as regras da Euronext.

**Só ordens limitadas.** Na bolsa também há ordens "ao mercado" (compra ao preço que for). No modelo, uma ordem com um preço muito agressivo faz esse papel. É uma simplificação.

**As ordens caducam ao fim de 10 a 60 minutos.** Não há dados sobre cancelamentos em Lisboa; é um pressuposto, com alguma variedade entre ordens.

**Um dia contínuo de 510 minutos, sem leilões de abertura e de fecho.** Simplificação; o foco são as interrupções durante o dia. Consequência: a referência do colar estático é o último preço do dia anterior em vez do preço de abertura.

**Os colares reais do BCP: 3% e 8%, reservas de 3 e 10 minutos.** Confirmado no anexo da Euronext e nas regras de *Trading safeguards*.

**Leilão instantâneo, que escolhe o preço com mais volume.** Simplificação das regras de leilão.

**Fixar os alvos do BCP (2023–2024) antes de calibrar.** Para os alvos não poderem ser ajustados aos resultados.

**Colar do leilão de ±6% (4 de novembro).** Sem ele, leilões sucessivos levaram o preço de 0,84 € a 0,02 €. O valor é o da Euronext para o PSI.

**Quando o leilão não consegue negociar dentro do colar, o último preço passa para o limite (8 de novembro).** Sem isto, uma corrida ficou presa em 1485 reservas. Confirmado no manual da Euronext.

**O volume passa a `long` (9 de novembro).** Com `int` passava do limite numa corrida de um ano.

**Reservas seguidas a menos de 1 minuto contam como uma só interrupção nos indicadores.** É consequência da regra anterior: várias reservas seguidas ao mesmo nível são, na prática, uma interrupção prolongada.

**Os valores calibrados passam a ser os do modelo principal (11 de novembro).** 13 chartists, notícias de 0,002 por minuto e ±2%, orçamento ilimitado, atividade diária, e o Cenario3.

**O modelo final é a configuração A2 da ronda 8b (14 de novembro).** Atenção dos chartists e ordens durante as reservas. Seis de sete factos, a melhor nos restantes, e mais fácil de defender do que o nervosismo.

**Quatro pressupostos foram relaxados (14 de novembro).** Um professor pediu para rever os pressupostos irrealistas e críticos. Foram relaxados: (1) os fundamentalistas e chartists já não param durante a reserva; (2) o ritmo dos chartists já não é constante (atenção); (3) o volume já não é constante de dia para dia (atividade); (4) o leilão segue as regras da Euronext (colar de 6% e nova reserva no limite).

**Dois pressupostos críticos ficam como limitações.** Os investidores sem limite de orçamento e o market maker sem limite de inventário.

## 22. As limitações

Há duas limitações críticas para a pergunta do trabalho:

1. **Os fundamentalistas e chartists têm dinheiro e ações praticamente ilimitados.** Nunca são obrigados a vender. No mundo real, numa queda, há investidores que pediram dinheiro emprestado e recebem *margin calls* (são obrigados a vender para cobrir as perdas), o que acelera a queda.
2. **O market maker nunca se retira.** No mundo real, numa crise, os market makers alargam o spread ou saem do mercado, e a liquidez desaparece.

As duas tornam o mercado simulado **mais resistente** do que o real durante um crash. Por isso as quedas e a perda de liquidez do modelo são estimativas **conservadoras** (por baixo), e pode haver efeitos dos colares que o modelo não apanha.

A terceira limitação é o **clustering**, que só é reproduzido em parte (0,026 contra 0,080 no BCP). Dentro do dia, onde os colares atuam, o modelo tem a dinâmica certa (manada, liquidez, saltos). Mas de um dia para o outro a agitação depois do choque passa mais depressa do que na realidade. Por isso os tempos de recuperação são um limite inferior. A comparação entre cenários (com e sem colares) é mais fiável do que os valores absolutos, porque todos os cenários têm a mesma limitação.

Há ainda simplificações menos críticas: só há uma ação, sem contágio a outras; não há leilões de abertura e de fecho; os choques são estilizados, não reproduções de crises reais; e os parâmetros do comportamento dos investidores não se observam, por isso vêm da literatura e da calibração.

**Trabalho futuro:** orçamento com alavancagem e *margin calls*; um market maker que se retira quando perde demasiado; investidores que mudam de estratégia conforme o que está a dar lucro (como em Lux e Marchesi, 1999), que é o mecanismo clássico para o clustering; várias ações do PSI e contágio entre elas; leilões de abertura e de fecho; e calibração com os dados de minuto a minuto.

## 23. Perguntas que os professores podem fazer

**"Porque não usaram a Process Modeling Library?"**
Porque cada ordem teria de ser um agente, e a PLE só permite 50 000; nós criamos milhões. E o negócio entre uma compra e uma venda, as execuções parciais e o leilão teriam de ser programados em Java na mesma. O livro continua a ser um sistema de filas: duas filas com prioridade, desistências pelo prazo e bloqueio durante as reservas.

**"O que é o Order?"**
É só a ficha de uma ordem, com sete campos: número, lado, preço, quantidade, hora, prazo e quem a enviou. Não tem lógica; a lógica está toda no Stock.

**"Como sabem que o livro de ordens está certo?"**
Seis testes antes de pôr os investidores, com 11 verificações: sem cruzamento não há negócio, um negócio simples, prioridade de chegada, uma ordem que varre dois níveis de preço, o colar a bloquear, e o cancelamento. Passam todos.

**"Porque é que os colares são 3% e 8%?"**
Porque o BCP é uma blue chip do PSI, e são esses os valores da Euronext para esse grupo. Está confirmado no anexo oficial da Euronext.

**"Porque 2023–2024?"**
Estava no plano desde o início, é recente e não tem crises do BCP. Fixámos os alvos antes de calibrar. Fizemos um teste de robustez com 2023, 2024 e 2025.

**"Porque não passa os sete factos?"**
Passava na ronda 5, mas a persistência do volume só passava no papel (0,001 contra 0,47). Preferimos um modelo que reproduz o volume a sério, como pediram no feedback. O clustering fica abaixo do limiar, mas é o facto com mais ruído (erro de cerca de 0,06 com 250 dias) e o que mais varia no próprio BCP.

**"Então os colares não servem para nada?"**
No nosso modelo, perante uma queda causada por informação nova, os colares adiam a descoberta do preço mas não mudam significativamente a queda. Mas o modelo não tem vendas forçadas e o market maker nunca sai, que são precisamente as coisas que tornam os crashes reais piores. Os colares podem ser mais úteis numa espiral de pânico do que numa notícia, e é isso que os Cenários 3 e 4 ajudam a ver.

**"O que é um chartist e porque são só 13?"**
Um investidor que segue a tendência do gráfico e que pode entrar em pânico com os vizinhos. Começámos com 30, mas o mercado ficava agitado demais; com 13 os factos estilizados batem. No Cenário 3 testamos 60 para ver o efeito de muita manada.

**"Onde está a ligação à matéria de filas?"**
As chegadas são as ordens dos investidores; a disciplina é por prioridade (preço e depois chegada); há desistência pelo prazo e bloqueio durante as reservas. O atendimento é diferente de um balcão, porque uma compra só sai quando aparece uma venda compatível: as duas filas atendem-se uma à outra.

## 24. Pequeno glossário

- **Ask**: o preço mais baixo a que alguém está disposto a vender.
- **Bid**: o preço mais alto que alguém está disposto a pagar.
- **Blue chip**: ação de uma empresa grande e muito negociada, que faz parte do índice principal.
- **Calibrar**: ajustar os parâmetros desconhecidos até o modelo reproduzir os dados reais.
- **Chartist**: investidor que segue a tendência do preço.
- **Clustering da volatilidade**: dias agitados vêm seguidos.
- **Colar**: faixa de preço fora da qual a negociação é interrompida.
- **Curtose**: medida de quantos movimentos extremos há; acima de 0 quer dizer caudas pesadas.
- **Execução parcial**: uma ordem negociada só em parte; o resto fica no livro.
- **Facto estilizado**: característica que os preços reais mostram quase sempre.
- **Fundamentalista**: investidor que negoceia pelo valor da empresa.
- **KPI**: indicador de desempenho (queda máxima, tempo de recuperação, etc.).
- **Leilão de reabertura**: fim de uma reserva; um só preço para todas as ordens.
- **Liquidez**: facilidade em negociar sem mexer muito o preço.
- **Livro de ordens**: a lista das ordens à espera, de compra e de venda.
- **Market maker**: intermediário que está sempre disponível para comprar e vender.
- **Mid**: o ponto médio entre o bid e o ask.
- **Noise trader**: investidor que negoceia ao acaso.
- **Ordem limitada**: ordem com um preço máximo (compra) ou mínimo (venda).
- **Prioridade preço-tempo**: primeiro o melhor preço, depois quem chegou primeiro.
- **Réplica**: uma corrida do modelo com uma semente aleatória diferente.
- **Reserva**: período em que a negociação de uma ação está parada.
- **Spread**: a diferença entre o ask e o bid.
- **Statechart**: diagrama de estados que descreve o comportamento de um agente.
- **Tick**: o menor passo de preço permitido.
- **Volatilidade**: o quanto o preço sobe e desce.
- **Volume**: o número de ações negociadas.
