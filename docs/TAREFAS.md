# Guião de tarefas · Grupo 2 · entrega a 2 de dezembro

Os passos concretos de cada pessoa, com o código para colar, estão nos PDFs em [guioes/](guioes/): `Guiao_Miguel.pdf`, `Guiao_Joao.pdf`, `Guiao_Margarida.pdf`, `Guiao_Matilde.pdf` e o resumo `Guiao_Geral.pdf`. Para os alterar, edita `guioes/gerar_guioes.py` e corre `python docs/guioes/gerar_guioes.py`.

## Papéis (cerca de 28–33 h por pessoa)

| Pessoa | Papel |
|---|---|
| Miguel | Motor do mercado (livro de ordens, colares, leilão) e integração |
| João | Investidores (fundamentalista, tendência/manada, criador de mercado em stress) e dados/Python (BCP, calibração, KPIs) |
| Margarida | Experiências no AnyLogic (instrumentação, cenários, otimização), ESMA e investidor alavancado |
| Matilde | Notícias, criador de mercado, broker, ecrã inicial, dashboard e gráficos finais |

## Por semana

| Semana | Miguel | João | Margarida | Matilde |
|---|---|---|---|---|
| 1 (17–24 out) | Modelo base: Order, Stock com filas, matching e noise traders. **O preço mexe até quinta.** | Dados do BCP (Python), estatísticas-alvo, arquivo intradiário; desenhar os statecharts | Aprender as experiências do AnyLogic; notas da ESMA | Tutorial de gráficos e controlos; esboços; começar o NewsAgent (plano B) |
| 2 (24–31 out) | Colares ±3%/±8%, reservas 3/10 min, leilão; integrar as peças | **Fundamentalist**; tabela de metas | **Instrumentar o modelo** (cenários, CSV, KPIs) | **NewsAgent e MarketMaker** |
| 3 (31 out–7 nov) | Integrar tudo: **Fase 1 a correr** | **Chartist com rede e manada**; testar o `kpis.py` | Montar as experiências dos cenários | Ecrã inicial; cores dos agentes |
| 4 (7–14 nov) | Velocidade; apoio | **Calibração** (`compare_model.py`) e validação | Corridas de calibração no AnyLogic | **Dashboard final** |
| 5 (14–21 nov) | Integrar a Fase 2 | KPIs dos cenários; MarketMaker em stress | Cenários da Fase 1 (30 replicações); **LeveragedTrader** | **Broker completo** (fila e statecharts) |
| 6 (21–28 nov) | Congelar o modelo; introdução e problema | `kpis.xlsx` final; relatório: investidores, dados, resultados | Corridas finais (grelha, otimização); relatório: experiências | **Gráficos finais** e apresentação |

**Marcos:** domingo (reunião de 30 min) · 23 out (modelo base) · 7 nov (Fase 1 a correr) · 14 nov (decisão sobre a Fase 2) · 28 nov–2 dez (revisão e entrega).
