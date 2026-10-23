# SAD · Grupo 2 · Simulador Euronext Lisboa (BCP)

Mercado artificial baseado em agentes (AnyLogic) para estudar as **interrupções de negociação** (circuit breakers) da Euronext Lisboa, calibrado com dados reais do **BCP (BCP.LS)**.

Entrega final: **2 de dezembro**.

## Equipa e papéis

| Pessoa | Papel |
|---|---|
| Miguel | Livro de ordens em Java (testado primeiro), colares, leilão e integração |
| João | Investidores (fundamentalista, tendência e manada), dados/Python (BCP, calibração, KPIs), factos estilizados e pressupostos |
| Margarida | Experiências no AnyLogic (instrumentação, cenários, limiares ótimos, sensibilidade) e ESMA |
| Matilde | Notícias, criador de mercado, interface, dashboard, verificação e gráficos finais |

O plano completo, com as tarefas por semana, está em [docs/TAREFAS.md](docs/TAREFAS.md). **Âmbito: só a Fase 1** (ver [docs/FEEDBACK_PROPOSTA.md](docs/FEEDBACK_PROPOSTA.md)). Antes de calibrar: [docs/FACTOS_ESTILIZADOS.md](docs/FACTOS_ESTILIZADOS.md). Tudo o que é assumido: [docs/PRESSUPOSTOS.md](docs/PRESSUPOSTOS.md). Limites da versão PLE: [docs/LIMITES_PLE.md](docs/LIMITES_PLE.md).

## Estrutura

```
model/      modelo principal Euronext_Main/Euronext_Main.alp (só o Miguel faz commit aqui)
sandbox/    uma pasta por pessoa para modelos de teste
docs/       CONTRATO, TAREFAS, FACTOS_ESTILIZADOS, PRESSUPOSTOS, FEEDBACK_PROPOSTA e guioes/ (PDF por pessoa)
scripts/    Python para descarregar dados e calcular as estatísticas-alvo
data/raw/        CSV descarregados
data/processed/  estatísticas (Excel/CSV)
report/     figuras e versões do relatório
```

## Regras do grupo

1. **O `model/` é só do Miguel.** Os outros trabalham na sua pasta `sandbox/<nome>/` e, quando a peça estiver pronta, avisam o grupo para ela ser integrada.
2. **Os nomes vêm do [CONTRATO](docs/CONTRATO.md).** Se precisares de um nome novo, acrescenta-o lá primeiro e avisa o grupo.
3. **Faz pull antes de começar e commit + push quando acabas.** Escreve mensagens de commit claras, ex.: `João: fundamentalista com statechart`.
4. **Os ficheiros `.alp` não se fundem.** Duas pessoas não podem editar o mesmo `.alp` ao mesmo tempo.

## Como usar (GitHub Desktop)

1. Instalar o [GitHub Desktop](https://desktop.github.com/) e iniciar sessão.
2. `File → Clone repository` e escolher `sad-euronext-g2`.
3. Antes de trabalhar: **Fetch origin → Pull**.
4. Depois de trabalhar: escrever a mensagem em baixo à esquerda, **Commit to main** e depois **Push origin**.

## Scripts (João)

```bash
pip install -r scripts/requirements.txt
python scripts/download_daily.py      # preços diários do BCP desde 2010
python scripts/archive_intraday.py    # dados de 1 minuto; correr 2x/semana até dezembro
python scripts/target_stats.py        # estatísticas reais que o modelo tem de reproduzir
```
