# Limites da AnyLogic PLE e o nosso modelo

Os professores pediram para verificar os limites da versão PLE. Fonte: a ajuda oficial da AnyLogic 8.9.9 instalada (*AnyLogic Help → AnyLogic editions comparison → Limitations in AnyLogic PLE*), consultada a 23/10/2026.

## Limites e onde estamos

| Limite da PLE | O nosso modelo | Problema? |
|---|---|---|
| Máximo **10 tipos de agente** num modelo | Main, Stock, NoiseTrader, Fundamentalist, Chartist, MarketMaker, NewsAgent = **7** (`Order` é uma classe Java, não conta) | ✅ Não, mas sobram só 3: não criar tipos de agente desnecessários |
| **Tempo de modelação limitado a 5 horas** em todas as bibliotecas exceto a Process Modeling Library | Não usamos as bibliotecas limitadas (Material Handling, Pedestrian, Rail, Road Traffic, Fluid). **Testado:** uma corrida de 120 dias (61 200 min ≈ 1020 h de tempo de modelo) correu até ao fim, a 23/10. Alguns resumos na internet dizem que *todas* as corridas da PLE param às 5 h; o teste mostra que no nosso modelo isso não acontece | ✅ Não |
| Máximo **50 000 agentes criados dinamicamente** | Criamos milhões de **ordens**, mas são objetos Java e não agentes. Os ~100 investidores são criados no arranque | ✅ Não. Foi por isto que o livro de ordens passou para Java |
| Máximo **200 populações e blocos de fluxograma** por tipo de agente | Poucas populações e nenhum bloco | ✅ Não |
| Máximo 200 variáveis de System Dynamics por tipo de agente | Não usamos System Dynamics | ✅ Não |
| OptQuest: **500 iterações** e **7 parâmetros** por experiência | Limiares ótimos: 2 parâmetros (`customDyn`, `customStat`), 200 iterações | ✅ Não |

## Experiências disponíveis na PLE

| Experiência | PLE | Uso no projeto |
|---|---|---|
| Simulation | ✅ | correr e ver o modelo |
| Parameter Variation | ✅ | cenários, grelha de colares, sensibilidade (Margarida) |
| Monte Carlo | ✅ | replicações |
| Sensitivity Analysis | ✅ | alternativa pronta para a análise de sensibilidade |
| Calibration | ✅ | possível ajuda na calibração (opcional) |
| Compare Runs | ✅ | — |
| Optimization (motor genético) | ✅ | limiares ótimos |
| Optimization (OptQuest) | Limitado (500 iterações, 7 parâmetros) | chega para o nosso caso |
| Custom experiment | ❌ | não precisamos |

## Outras coisas que a PLE não tem (e que não nos afetam)
- **Integração Git dentro do AnyLogic:** usamos o Git por fora (GitHub), e funciona.
- Debugging profissional (breakpoints, ver variáveis Java): usamos `traceln` e o `testBook`.
- Aplicação standalone e snapshots do modelo: não precisamos.

## Regras para o grupo
1. **Não criar novos tipos de agente** sem combinar (máximo 10; vamos em 7).
2. **Nada de criar agentes durante a simulação** (ex.: um agente por ordem ou por notícia). Usar classes Java ou variáveis.
3. A licença PLE é só para ensino e aprendizagem pessoal, o que é o nosso caso.
