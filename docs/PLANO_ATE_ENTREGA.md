# Plano até à entrega (2 de dezembro)

**Grupo 2 · SAD · 24 de novembro de 2026** · Por ordem. Cada passo diz quem faz.

---

## Hoje

1. **Miguel:** abrir o modelo final no AnyLogic (fechar sem gravar se estiver aberto e voltar a abrir), correr os testes com `runTests` = true e `nNoise` = 0 (têm de dar 11 PASS), repor `runTests` = false e `nNoise` = 30, gravar (Ctrl+S) e pedir o commit. Sem isto ninguém pode começar.
2. **Grupo:** responder ao João a aprovar a data do choque: 5/09/2024, numa janela de 13/06/2024 a 27/11/2024.

## Amanhã

3. **Matilde:** criar o parâmetro `startDay`, para o modelo começar a 13/06/2024 (preço inicial 0,3494 €).
4. **Miguel:** integrar o `startDay` no modelo principal e fazer o commit.
5. **João:** fixar, antes de correr, a definição de crash (para medir a probabilidade) e os indicadores de liquidez (spread, volume e tempo sem negociar).
6. **Margarida:** atualizar as experiências dos Cenários 2, 3 e 4 com o `startDay` e o choque no dia 60. Acrescentar ao Cenário 3 a manada (`herdThreshold` com 1, 2 e 4). Preparar a grelha dos limiares ótimos.

## A seguir: as corridas

7. **João e Margarida:** teste fora da amostra de 2020–2021 (crise da COVID).
8. **João:** verificação ao minuto. A calibração é toda com dados diários, mas os colares atuam ao minuto. Com os dados de minuto a minuto do BCP que o João tem guardado, comparar o BCP com o modelo nos retornos de 1 minuto: a agitação (volatilidade), os saltos grandes (curtose) e como a agitação se distribui ao longo do dia. Se não bater perfeitamente, entra no relatório como limitação, mas mostra que olhámos para a escala em que os colares atuam.
9. **Margarida:** Cenário 2, choque com e sem colares (o principal).
10. **Margarida:** Cenários 3 e 4 e os limiares ótimos.
11. **Margarida:** análise de sensibilidade aos 5 parâmetros que mais pesam.

## No fim: resultados e relatório

12. **João:** KPIs, probabilidade de crash, análise multicritério e tabela de recomendação.
13. **Miguel:** atualizar os objetivos do relatório (secção 1.2).
14. **João:** parágrafo na secção 6.3 sobre o que a calibração prova (os investidores transformam a informação real em preços) e o resultado da verificação ao minuto.
15. **Grupo:** conclusões a responder às perguntas 1 e 2 da proposta, uma a uma, e a dizer que as perguntas 3 e 4 ficaram fora do âmbito.
16. **Miguel:** congelar o modelo e rever o relatório final antes de 2 de dezembro.

---

## Só se sobrar tempo

- Correr os cenários em três regimes de mercado (calmo, atual e crise bancária).
- Correr o Cenário 2 numa janela calma de 2025–2026.
- Comparar a informação que entra no modelo com o preço que sai, para mostrar o que os investidores acrescentam.
- Atualizar os resumos em PDF do Miguel (ainda falam do modelo antigo).

**Atenção:** os resultados antigos dos cenários foram feitos com o modelo antigo e têm de ser corridos de novo.
