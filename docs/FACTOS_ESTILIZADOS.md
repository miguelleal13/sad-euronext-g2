# Factos estilizados a reproduzir

Os professores pediram para **definir os factos estilizados antes de calibrar**. Esta lista fica fixa antes da primeira calibração (semana 4). Mudá-la depois seria afinar a meta ao resultado.

- **Responsável:** João. Preenche a coluna *Valor BCP* com `python scripts/target_stats.py` (período calmo 2023–2024) e faz commit antes de a Margarida correr a calibração.
- **Como se mede no modelo:** `python scripts/compare_model.py baseline`, com 10 corridas do cenário baseline de 250 dias. O fecho de cada dia é o último preço de cada bloco de 510 minutos.
- **Porquê 2023–2024 e não 2025:** o período veio do plano do projeto (guião e `target_stats.py`), fixado antes de qualquer corrida do modelo, e não se mudou depois para não afinar as metas aos resultados. 2025 tem a queda de abril (−9.9% a 4/4/2025; volatilidade de 3.7%/dia em abril, contra 1.1%–2.7% nos outros meses).
- **Teste de robustez (09/11):** os mesmos factos em 2023, 2024 e 2025 dão valores da mesma ordem (volatilidade 1.9%–2.2%, curtose 2.0–3.0, 11%–15% de dias >3%, correlação volume–|r| 0.57–0.70). Variam mais o clustering (0.06–0.18), a autocorrelação (−0.09 a 0.07) e a persistência do volume (0.16–0.49). Tabela no relatório (secção 3.2). As metas não mudaram.
- **Facto 7** acrescentado a 31/10/2026, antes de qualquer afinação do modelo (a ronda 0 da calibração foi o modelo original), porque os professores pediram para validar preço **e volume** e o FEEDBACK_PROPOSTA já referia esta métrica.
- **Dados:** valores calculados a 25/10/2026 com os preços diários do Yahoo Finance (BCP.LS, 2023-01-01 a 2024-12-31, 510 dias).

| # | Facto estilizado | Métrica (`target_stats` / `compare_model`) | Valor BCP 2023-24 | Critério para “bate” |
|---|---|---|---|---|
| 1 | Volatilidade de um dia normal | `volatilidade_diaria` | 0.0207 (2.1%) | modelo a ±25% |
| 2 | Caudas pesadas: dias extremos mais frequentes do que numa normal | `curtose_excesso` | 2.41 | modelo > 1 e a ±50% |
| 3 | Clustering de volatilidade: dias agitados vêm seguidos | `autocorr_abs_retornos_lag1` | 0.080 | modelo > 0.05 e do mesmo sinal |
| 4 | Ausência de autocorrelação nos retornos (o preço não é previsível) | `autocorr_retornos_lag1` | 0.004 | modelo entre −0.1 e 0.1 |
| 5 | Frequência de movimentos fortes (o que dispara os colares) | `pct_dias_var_maior_3pct` | 0.129 (12.9%) | modelo a ±50% |
| 6 | Volume e volatilidade andam juntos | `corr_volume_absret` | 0.636 | modelo > 0 |
| 7 | Persistência do volume: dias de muito volume vêm seguidos | `autocorr_volume_lag1` | 0.470 | modelo > 0 |

## Validação (separada da calibração)

- **Efeito das interrupções (ESMA, 2020).** No cenário de choque com colares, a volatilidade depois da interrupção é menor do que antes e o spread alarga. A tabela com os valores da ESMA é feita pela Margarida.
- **Choques.** A queda máxima tem de ser plausível, da ordem de grandeza dos piores dias do BCP. **Não afirmamos que o modelo reproduz crashes reais** (BES 2014, março 2020): os choques são estilizados e servem para comparar regras.