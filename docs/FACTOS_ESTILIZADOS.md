# Factos estilizados a reproduzir

Os professores pediram para **definir os factos estilizados antes de calibrar**. Esta lista fica fixa antes da primeira calibração (semana 4). Mudá-la depois seria afinar a meta ao resultado.

- **Responsável:** João. Preenche a coluna *Valor BCP* com `python scripts/target_stats.py` (período calmo 2023–2024) e faz commit antes de a Margarida correr a calibração.
- **Como se mede no modelo:** `python scripts/compare_model.py baseline`, com 10 corridas do cenário baseline de 250 dias. O fecho de cada dia é o último preço de cada bloco de 510 minutos.
- **Dados:** valores calculados a 25/10/2026 com os preços diários do Yahoo Finance (BCP.LS, 2023-01-01 a 2024-12-31, 510 dias).

| # | Facto estilizado | Métrica (`target_stats` / `compare_model`) | Valor BCP 2023-24 | Critério para “bate” |
|---|---|---|---|---|
| 1 | Volatilidade de um dia normal | `volatilidade_diaria` | 0.0207 (2.1%) | modelo a ±25% |
| 2 | Caudas pesadas: dias extremos mais frequentes do que numa normal | `curtose_excesso` | 2.41 | modelo > 1 e a ±50% |
| 3 | Clustering de volatilidade: dias agitados vêm seguidos | `autocorr_abs_retornos_lag1` | 0.080 | modelo > 0.05 e do mesmo sinal |
| 4 | Ausência de autocorrelação nos retornos (o preço não é previsível) | `autocorr_retornos_lag1` | 0.004 | modelo entre −0.1 e 0.1 |
| 5 | Frequência de movimentos fortes (o que dispara os colares) | `pct_dias_var_maior_3pct` | 0.129 (12.9%) | modelo a ±50% |
| 6 | Volume e volatilidade andam juntos | `corr_volume_absret` | 0.636 | modelo > 0 |

## Validação (separada da calibração)

- **Efeito das interrupções (ESMA, 2020).** No cenário de choque com colares, a volatilidade depois da interrupção é menor do que antes e o spread alarga. A tabela com os valores da ESMA é feita pela Margarida.
- **Choques.** A queda máxima tem de ser plausível, da ordem de grandeza dos piores dias do BCP. **Não afirmamos que o modelo reproduz crashes reais** (BES 2014, março 2020): os choques são estilizados e servem para comparar regras.