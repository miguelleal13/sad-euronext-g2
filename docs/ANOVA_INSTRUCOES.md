# ANOVA: instruções para correr no AnyLogic

**Objetivo:** ver que parâmetros *sem dados* mexem em cada um dos 7 factos estilizados, para escolher a mudança da ronda 10 com base em números.

## O que se varia
Os 6 parâmetros sem dados, cada um a −50% ou +50% do valor calibrado. São 32 combinações (desenho fatorial fracionado 2^(6-1)), listadas em `data/processed/anova_desenho.csv`:

| Parâmetro | −50% | Calibrado | +50% |
|---|---|---|---|
| nChartists | 6 | 13 | 20 |
| nFundamentalists | 20 | 40 | 60 |
| nNoise | 15 | 30 | 45 |
| noiseSigma | 0.001 | 0.002 | 0.003 |
| fundBand | 0.005 | 0.01 | 0.015 |
| trendThreshold | 0.0025 | 0.005 | 0.0075 |

(`nChartists` −50% = 6.5, arredondado para 6.)

## Modelo
`sandbox/matilde/Euronext_real.alp` (o modelo com os choques reais, o mesmo da ronda 9). Tudo o resto fica como está: `realShocks` = true, colares da Euronext, 509 dias.

## Passos no AnyLogic
1. Abrir `sandbox/matilde/Euronext_real.alp`.
2. Na árvore: botão direito no modelo → **New → Experiment → Parameters Variation**. Nome: `ANOVA`.
3. Em **Parameters**, escolher **Freeform** e definir **32 iterações**.
4. Em cada iteração, pôr os valores da linha correspondente do CSV:
   - `scenario` = coluna `scenario` (`"anova01"` … `"anova32"`, entre aspas, porque é String);
   - `nChartists`, `nFundamentalists`, `nNoise`, `noiseSigma`, `fundBand`, `trendThreshold` = colunas com o mesmo nome.
   - As colunas `x_...` são só a codificação (−1/+1) para o script e não se põem no AnyLogic.
5. **Replications:** 5 por iteração (fixas), com o mesmo gerador da Cenario1: `new Random(1000 + getCurrentReplication())`.
6. **Stop time:** 259 590 minutos (509 dias), igual à Cenario1.
7. Correr. São 160 simulações, cerca de 1h45.

## O que mandar
O `precos.csv` (e o `halts.csv`) num zip. O label das corridas tem de começar por `anova01`…`anova32`, porque é assim que o script as identifica.

## Análise (João)
```
python scripts\anova.py PASTA_COM_O_PRECOS_CSV
```
Escreve `data/processed/anova.xlsx`: para cada facto, a % da variação explicada por cada parâmetro e pelas interações de 2 parâmetros, com o valor p.
