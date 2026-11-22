# Triagem dos outros parâmetros sem dados: instruções

**Objetivo:** ver se algum dos parâmetros sem dados que **não** entraram na ANOVA mexe nos 7 factos estilizados tanto como os 3 principais da ANOVA (nº de trend followers, `trendThreshold`, nº de noise traders). Se mexer, entra na calibração.

## O que se varia
10 parâmetros, cada um a −50% ou +50% do valor do modelo final, num desenho de **Plackett–Burman com 12 combinações** (`data/processed/triagem_desenho.csv`). Os 6 parâmetros da ANOVA ficam nos valores calibrados.

| Parâmetro | O que é | −50% | Modelo | +50% |
|---|---|---|---|---|
| chartRate | decisões/min de cada trend follower | 0.1 | 0.2 | 0.3 |
| fundRate | decisões/min de cada fundamentalista | 0.1 | 0.2 | 0.3 |
| herdThreshold | avisos que põem um trend follower em pânico | 1 | 2 | 3 |
| panicDuration | minutos de pânico | 5 | 10 | 15 |
| maWindow | memória da média móvel (min) | 25 | 50 | 75 |
| orderLife | vida média de uma ordem (min) | 17.5 | 35 | 52.5 |
| mmSpread | spread do criador de mercado | 0.002 | 0.004 | 0.006 |
| mmQty | quantidade cotada pelo criador de mercado | 1000 | 2000 | 3000 |
| activitySigma | parte aleatória da atividade diária | 0.025 | 0.05 | 0.075 |
| noiseRate | ordens/min de cada noise trader | 0.5 | 1 | 1.5 |

Há também uma coluna `x_fantasma`, que não corresponde a nenhum parâmetro e não se põe no AnyLogic: o script usa-a para medir o tamanho de um efeito que é só ruído.

## Modelo e passos no AnyLogic
Igual à ANOVA:
1. Abrir `sandbox/matilde/Euronext_real.alp`.
2. Nova experiência **Parameters Variation** (ex.: `Triagem`), em **Freeform**, com **12 iterações**.
3. Em cada iteração:
   - `scenario` = `"triagem01"` … `"triagem12"` (entre aspas);
   - os 10 parâmetros com os valores da linha correspondente do CSV;
   - tudo o resto fica igual (`realShocks` = true e os 6 da ANOVA nos valores calibrados).
4. **5 réplicas** por iteração, gerador `new Random(1000 + getCurrentReplication())`, stop time **259 590** minutos (509 dias).
5. São 60 simulações, cerca de 40 minutos.

## O que mandar
O `precos.csv` (e o `halts.csv`) num zip.

## Análise (João)
```
python scripts\triagem.py PASTA_COM_O_PRECOS_CSV
```
Escreve `data/processed/triagem.xlsx`.
