# A nossa abordagem, explicada

**Grupo 2 · SAD · Interrupções de negociação na Bolsa de Lisboa (ação do BCP) · 24 de novembro de 2026**

Este documento responde a uma dúvida concreta: se usamos dados de 2023–2024, como é que o modelo serve para outros anos, e afinal qual é a nossa proposta? No fim está a lista do que falta fazer antes dos cenários.

---

## 1. A ideia numa frase

Construímos um **mercado artificial** que funciona como a Bolsa de Lisboa. Damos-lhe a **informação real** que chegou ao BCP num período (o que fizeram os bancos europeus, o mercado português, as notícias do banco), e ele **transforma essa informação em preços**, através de investidores artificiais que compram e vendem. Depois acrescentamos uma **má notícia falsa** de −10% e vemos o que acontece **com e sem colares**.

O objetivo não é prever o preço do BCP. É perceber como uma queda se propaga e se os colares ajudam.

## 2. O modelo tem duas partes

A chave para perceber tudo é separar o modelo em duas partes.

### 2.1 O mercado (fixo, igual para qualquer ano)

É a máquina: o livro de ordens, as regras da Euronext (colares de 3% e 8%, reservas, leilão de reabertura) e os investidores artificiais (30 noise traders, 40 fundamentalistas, 13 chartists, um market maker), cada um com a sua forma de decidir. Também faz parte da máquina a forma como o volume de negócios reage à informação.

Esta parte **não muda de ano para ano**. É ela que queremos estudar, porque é nela que estão os colares.

### 2.2 A informação que entra (muda com o período)

É o que chega ao mercado em cada dia:

- quanto se mexeram os **bancos europeus** nesse dia (é o que mais pesa no BCP);
- quanto se mexeu o **mercado português** (sem o BCP);
- se houve **notícias do próprio BCP** (resultados, comunicados) e de que tamanho;
- e um **resto que nada explica** (cerca de 42% da agitação do BCP), sorteado de exemplos reais.

Esta parte **muda com o período**: se quisermos simular 2025, damos-lhe a informação de 2025; se quisermos 2020, damos-lhe a de 2020. No modelo, é praticamente trocar um ficheiro (`shocksFile`) e o preço inicial.

### 2.3 Uma comparação

Pensa num **simulador de voo**. O avião (o mercado) é sempre o mesmo. O que muda de voo para voo é o tempo e a pista (a informação). Testar o simulador com o tempo de vários dias diferentes mostra que o avião está bem construído. E depois podemos usá-lo para testar uma coisa nova, por exemplo um travão diferente (os colares), em condições realistas.

## 3. Então para que servem os dados de 2023–2024?

Servem para **três coisas diferentes**, e é isso que causa confusão.

**Primeiro papel: medir as características do BCP atual.** Alguns números do modelo não se inventam, medem-se nos dados: quanto o BCP reage aos bancos europeus e ao mercado português, quanto o volume sobe com cada tipo de notícia, e de que tamanho é o "resto que nada explica". Foram medidos em 2023–2024. Assume-se que são características do BCP de hoje, que não mudam muito de ano para ano. O João verificou isto: o "resto" de 2023–2024 (1,24% por dia) está na média do BCP desde 2018 (1,28%).

**Segundo papel: ser o alvo da calibração.** Calculámos sete características estatísticas dos preços do BCP em 2023–2024 (os factos estilizados: agitação diária, dias extremos, dias agitados seguidos, etc.). Afinámos o modelo até ele reproduzir as sete. Este período foi escolhido no início do projeto porque é recente, não tem crises do BCP e estava no plano antes de corrermos o modelo.

**Terceiro papel: dar o "fundo" dos cenários.** Nos cenários dos colares, o mercado revive um pedaço real de 2024 (de 13 de junho a 27 de novembro), com a informação real desses dias, e a notícia falsa de −10% é posta num dia calmo (5 de setembro de 2024). Assim o choque acontece num mercado com um ambiente realista.

## 4. Porque é que o modelo serve para outros anos

Porque a parte que foi afinada (o mercado) não depende do ano, e porque o testámos com informação que nunca tinha visto.

**Teste de 2025–2026 (feito).** Deixámos o mercado exatamente como saiu da calibração e só lhe demos a informação real de janeiro de 2025 a outubro de 2026. O modelo reproduziu os sete factos do BCP desse período. Ou seja, funciona fora dos anos em que foi afinado.

**Teste de 2020–2021 (a fazer).** É o mesmo teste, mas num período com uma crise real (o crash da COVID). Interessa porque o tema do trabalho são as quedas.

**O limite.** O modelo representa o **BCP de hoje** (desde 2018). Não representa bem o BCP de 2011 a 2017, quando o banco esteve em crise (dívida soberana, ajuda do Estado, aumentos de capital): nessa altura o "resto que nada explica" era o **dobro**. Para uma crise bancária desse tipo, os nossos cenários são **conservadores**, ou seja, provavelmente subestimam a queda.

## 5. Como começámos e porque mudámos

**No início (rondas 0 a 8b)** as notícias eram **inventadas**: saíam ao acaso, cerca de uma por dia, com tamanho de ±2%. Era a forma clássica de fazer estes modelos (como nos artigos de Lux e Marchesi, e de Chiarella e Iori), era mais simples para começar a Fase 1, e o objetivo não era imitar o BCP dia a dia. Os dados de 2023–2024 serviam **só de alvo**. Afinámos muita coisa (número de notícias, dinheiro dos investidores, número de chartists, atividade) e chegámos a 6 de 7 factos. O que nunca conseguimos foi o clustering (dias agitados seguidos de dias agitados), porque notícias inventadas não vêm agrupadas como as reais.

**Depois (rondas 9 a 11)**, a seguir ao segundo feedback dos professores sobre o realismo do modelo, as notícias inventadas foram **substituídas pela informação real**. O clustering apareceu logo, porque as más notícias reais chegam em cadeia. Os investidores não mudaram desde a ronda 9, e os números do volume passaram a ser medidos nos dados em vez de afinados à mão. O modelo final (ronda 11) reproduz os 7 factos.

As rondas antigas continuam a contar no relatório: foi com elas que se percebeu porque é que o modelo precisa de investidores com muito dinheiro, do colar do leilão e da atividade dos noise traders.

**O que se ganhou e o que se perdeu.** Ganhou-se realismo. Mas ficou uma crítica possível: "se meteram a informação do BCP lá dentro, claro que saem os factos do BCP". A resposta é que a calibração prova uma coisa específica: que **os investidores artificiais transformam a informação real em preços sem estragar as suas propriedades**. E os colares, que são o que estudamos, atuam precisamente nessa transformação. Convém o relatório dizer isto explicitamente (secção 6.3).

## 6. O que prometemos na proposta e como respondemos

A proposta tem quatro perguntas. As duas primeiras são da Fase 1, que é a que fazemos.

**Pergunta 1: como é que a proporção de chartists e a manada afetam a probabilidade e o tamanho dos crashes?** Hoje variamos o número de chartists (Cenários 3 e 4), por isso o **tamanho** está coberto. Falta variar a **manada** (o número de avisos de vizinhos que põe um chartist em pânico, `herdThreshold`) e medir a **probabilidade** de crash (definir o que é um crash e contar em quantas corridas acontece).

**Pergunta 2: que colares e que durações reduzem mais a queda sem prejudicar demasiado a liquidez?** É a mais bem coberta: o Cenário 4 testa os colares (nenhuns, 2%/5%, 3%/8%, 5%/10%) e as durações (3 e 10 minutos). Falta procurar os **limiares ótimos** e fazer a **análise multicritério**, que junta a queda evitada e a perda de liquidez (spread, volume e tempo sem negociar) e ordena os colares.

**Perguntas 3 e 4 (alavancagem e contágio entre ações)** são das Fases 2 e 3, que ficaram fora do âmbito por indicação dos professores. O relatório tem de o dizer e ligá-las às limitações.

## 7. Os cenários

Todos usam o mesmo fundo (13 de junho a 27 de novembro de 2024, informação real), a notícia falsa de −10% a 5 de setembro de 2024, e 30 corridas por combinação.

- **Base:** o fundo sem a notícia falsa. Serve de referência.
- **Cenário 2 (o principal):** a notícia falsa, sem colares e com os colares reais (3%/8%). A diferença é o efeito dos colares.
- **Cenário 3 (manada):** o mesmo, mas com 60 chartists em vez de 13 (e, se aprovado, com vários níveis de manada).
- **Cenário 4 (grelha):** todas as combinações de colares, durações e número de chartists. Daqui sai a tabela de recomendação.
- **Limiares ótimos:** colares intermédios, para encontrar o melhor equilíbrio entre travar a queda e manter a liquidez.
- **Sensibilidade:** repetir com os 5 parâmetros que mais pesam a −50% e +50%, para ver se a recomendação muda.

**Atenção:** os resultados antigos dos cenários (feitos com o modelo de notícias inventadas) já não valem e têm de ser corridos de novo.

## 8. O que falta fazer antes de começar os cenários

**Obrigatório**

1. **Miguel:** abrir o modelo final no AnyLogic, correr os testes do livro (11 PASS), repor os parâmetros, gravar e fazer commit. Sem isto ninguém pode começar.
2. **Grupo:** aprovar a data do choque (5/09/2024).
3. **Matilde:** o parâmetro `startDay`, para o modelo começar a 13/06/2024 (preço inicial 0,3494 €). O Miguel integra-o no modelo principal.
4. **João e Margarida:** o teste fora da amostra de 2020–2021.
5. **Margarida:** atualizar as experiências dos Cenários 2, 3 e 4 com o `startDay` e o choque no dia 60.
6. **Pergunta 1:** acrescentar ao Cenário 3 a variação da manada (1, 2 e 4 avisos) e definir **antes de correr** o que é um crash, para medir a probabilidade (João no script de KPIs).
7. **Pergunta 2:** fixar **antes de correr** os indicadores de liquidez; preparar a grelha dos limiares ótimos e a análise multicritério.
8. **Margarida:** a análise de sensibilidade aos 5 parâmetros.

**Relatório (em paralelo)**

9. **Miguel:** atualizar os objetivos (secção 1.2) com o modelo conduzido pela informação real e a liquidez medida por volume, spread e tempo sem negociar.
10. **João:** um parágrafo na secção 6.3 a explicar o que a calibração prova (os agentes transformam a informação real em preços).
11. **Conclusões:** responder às perguntas 1 e 2 uma a uma, e dizer que as 3 e 4 ficaram fora do âmbito.

**Opcional, se houver tempo**

- Correr os cenários em **três regimes** (calmo como 2025–26, normal como 2023–24, crise bancária como 2011–17), multiplicando o "resto que nada explica" por 0,7, 1 e 2. Mostra que a recomendação vale para lá de 2023–2024.
- Correr o Cenário 2 numa janela calma de 2025–2026.
- Comparar os factos da informação que entra com os do preço que sai, para mostrar o que os investidores acrescentam.
- Verificação com os dados de minuto a minuto do BCP.

## 9. Como explicar isto a um professor

> "O modelo tem duas partes: o mercado, com as regras da Euronext e os investidores artificiais, que é fixo; e a informação que chega ao BCP em cada dia, que vem dos dados reais. Medimos as características do BCP atual em 2023–2024 e afinámos o mercado até reproduzir os sete factos estilizados desse período. Depois demos-lhe a informação de 2025–2026, sem mexer em nada, e reproduziu os factos desse período também. Nos cenários, o mercado revive um período real de 2024 e acrescentamos uma má notícia de −10% num dia calmo, com e sem colares. Assim isolamos o efeito dos colares num ambiente realista. O modelo representa o BCP atual; numa crise bancária como a de 2011–2017 a informação seria o dobro, por isso os resultados são conservadores."
