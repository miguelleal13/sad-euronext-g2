# Guião de tarefas · Grupo 2 · entrega a 2 de dezembro

Os passos concretos de cada pessoa, com o código para colar, estão nos PDFs em [guioes/](guioes/): `Guiao_Miguel.pdf`, `Guiao_Joao.pdf`, `Guiao_Margarida.pdf`, `Guiao_Matilde.pdf` e o resumo `Guiao_Geral.pdf`. Para os alterar, edita `guioes/gerar_guioes.py` e corre `python docs/guioes/gerar_guioes.py`.

**Âmbito: só a Fase 1.** Foi o que os professores pediram no feedback à proposta; vê [FEEDBACK_PROPOSTA.md](FEEDBACK_PROPOSTA.md). A alavancagem, os brokers e o contágio ficam como extensões opcionais e não estão no plano. O tempo que sobra vai para a qualidade da Fase 1: testes, verificação, pressupostos e sensibilidade.

## Papéis (cerca de 28–33 h por pessoa)

| Pessoa | Papel |
|---|---|
| Miguel | Livro de ordens em Java (testado primeiro), colares, leilão e integração |
| João | Investidores (fundamentalista, tendência/manada), dados/Python (BCP, calibração, KPIs), factos estilizados e pressupostos |
| Margarida | Experiências no AnyLogic (instrumentação, cenários, limiares ótimos, sensibilidade) e ESMA |
| Matilde | Notícias, criador de mercado, ecrã inicial, dashboard, verificação e gráficos finais |

## Por semana

| Semana | Miguel | João | Margarida | Matilde |
|---|---|---|---|---|
| 1 (17–24 out) | Livro de ordens em Java + **6 testes a passar**; depois os noise traders. **O preço mexe até quinta.** | Dados do BCP; **factos estilizados com os valores-alvo**; desenhar os statecharts | Aprender as experiências do AnyLogic; notas da ESMA | Tutorial de gráficos e controlos; esboços; começar o NewsAgent (plano B) |
| 2 (24–31 out) | Colares ±3%/±8%, reservas 3/10 min, leilão (com testes); integrar as peças | **Fundamentalist**; tabela de metas | **Instrumentar o modelo** (cenários, CSV, KPIs) | **NewsAgent e MarketMaker** |
| 3 (31 out–7 nov) | Integrar tudo: **Fase 1 a correr** | **Chartist com rede e manada**; testar o `kpis.py` | Montar as experiências dos cenários | Ecrã inicial; cores dos agentes |
| 4 (7–14 nov) | Velocidade; limites da PLE; apoio | **Calibração** (`compare_model.py`) e validação ESMA | Corridas de calibração | **Dashboard final** |
| 5 (14–21 nov) | Corrigir o que a verificação encontrar | KPIs dos cenários; fechar os **pressupostos** | Cenários (30 replicações); **análise de sensibilidade** | **Verificação**: 10 testes de condições extremas |
| 6 (21–28 nov) | Congelar o modelo; introdução, problema e livro de ordens | `kpis.xlsx` final; relatório: investidores, dados, factos, pressupostos e resultados | Corridas finais (grelha, limiares ótimos); relatório: experiências e sensibilidade | **Gráficos finais** e apresentação |

**Marcos:** domingo (reunião de 30 min) · 23 out (livro testado + preço a mexer) · 24 out (factos estilizados fixados) · 7 nov (Fase 1 a correr) · 14 nov (Fase 1 calibrada e validada) · 28 nov–2 dez (revisão e entrega).

## Para chegar ao 18–19 (comparação com o relatório do Grupo 21, que teve 18/20)

O Grupo 21 (logística da Super Bock) teve 18 com dados reais de empresa, decisões práticas (tirar um empilhador, payback) e animação 2D/3D com vídeo, mas sem verificação, calibração, intervalos de confiança nem sensibilidade. Nós temos o rigor; falta garantir o lado prático e visual.

| # | Tarefa | Quem | Quando |
|---|---|---|---|
| 1 | **Recomendação clara no fim dos resultados**: uma tabela final do tipo "colares 3%/8% reduzem a queda máxima em X% com Y% menos volume; 2%/5% reduzem Z% mas custam W% de liquidez; sem colares…", e uma frase de recomendação para a Euronext/CMVM. Vai para o fim do capítulo 8 e para as conclusões | João (números do `kpis.xlsx`) + Margarida | semana 6 |
| 2 | **Análise multicritério** (estabilidade vs. liquidez), prometida na proposta: normalizar a queda máxima, o tempo em interrupção, o volume e o spread por cenário, pesos (ex.: 50/50) e ranking dos colares; mostrar como muda o ranking com outros pesos | Margarida | semana 5–6 |
| 3 | **Dashboard bonito + vídeo curto (1–2 min)** do choque a acontecer: a queda, os HALT/REOPEN, o livro a esvaziar e os agentes a mudar de cor. Gravar o ecrã (Win+G) e pôr o link num apêndice, como o Grupo 21 fez | Matilde | semana 4–6 |
| 4 | **Calibração que bata com o BCP**, com a tabela "BCP real vs. modelo" no relatório. É a nossa resposta a não termos dados de uma empresa | João + Margarida | semana 4 |
| 5 | **Email aos professores** a confirmar que o livro de ordens em Java (sem blocos da Process Modeling Library) está bem | Miguel | já |
