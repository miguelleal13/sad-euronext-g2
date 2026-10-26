# Generated from report/Joao_sections_DSS_report.docx (João). Do not edit by hand: edit João's file and convert again.
$figDirJ = Join-Path $PSScriptRoot 'figures'

$content['Data Sources'] = {
    Body 'The empirical reference for the model is the share of Banco Comercial Português (BCP), one of the most traded constituents of the PSI index. Daily adjusted closing prices and daily volumes (ticker BCP.LS) were downloaded from Yahoo Finance for January 2010 to October 2026 (4304 trading days), using the Python script download_daily.py. One-minute prices are also collected twice a week (archive_intraday.py), since Yahoo Finance only keeps the most recent days of intraday data.'
    Body 'The calibration targets were computed for 2023–2024 (510 trading days), a recent period without bank-specific crises. Two stress periods were used only as a reference for the plausibility of the shock scenarios: the resolution of Banco Espírito Santo (15 July to 30 September 2014) and the start of the COVID-19 pandemic (15 February to 30 April 2020).'
    Body 'The BES period starts on 15 July because the adjusted prices show artificial jumps of +12% and +24% at the end of June and the beginning of July 2014, caused by the BCP capital increase. All returns are logarithmic.'
}
$content['Stylised Facts of the BCP Stock'] = {
    Body 'Following the feedback on the project proposal, the stylised facts and their acceptance criteria were fixed before the calibration of the model, so that the targets could not be adjusted to the results. {T:facts} lists the six facts, the value measured for BCP and the criterion used to decide whether the model reproduces each one. The same statistics are computed for the model by the script compare_model.py, using the last price of each 510-minute block as the daily close.'
    Tbl 'Stylised facts of the BCP stock (2023–2024) and calibration criteria' @('#', 'Stylised fact', 'Metric', 'BCP', 'Model matches if') @(
        @('1', 'Daily volatility', 'Standard deviation of daily returns', '0.0207', 'within ±25%'),
        @('2', 'Heavy tails', 'Excess kurtosis', '2.41', '> 1 and within ±50%'),
        @('3', 'Volatility clustering', 'Lag-1 autocorrelation of absolute returns', '0.080', '> 0.05'),
        @('4', 'Absence of return autocorrelation', 'Lag-1 autocorrelation of returns', '0.004', 'between −0.1 and 0.1'),
        @('5', 'Frequency of large moves', 'Share of days with |r| > 3%', '12.9%', 'within ±50%'),
        @('6', 'Volume–volatility relation', 'Correlation between volume and |r|', '0.636', '> 0')
    ) @(0.8, 3.6, 5.2, 1.8, 4.6) 'facts'
    Body 'The BCP share shows the typical behaviour of financial returns: returns are not autocorrelated, the distribution has heavy tails, large moves tend to be followed by large moves, and trading volume is higher on volatile days. Volatility clustering is weak (0.080) and close to the acceptance threshold, so it is expected to be the hardest fact to reproduce.'
    Body '{T:stress} compares the calm period with the two stress periods. During a crisis the daily volatility roughly doubles and the share of days with moves above 3%, the range in which the collars act, roughly triples. The worst days reach −16%, so the stylised shock of the scenarios (−10%, Chapter 7) is of a plausible order of magnitude.'
    Tbl 'BCP statistics in the calm period and in two stress periods' @('Statistic', 'Calm 2023–24', 'BES 2014', 'COVID-19 2020') @(
        @('Trading days', '510', '55', '51'),
        @('Daily volatility', '2.1%', '4.0%', '4.4%'),
        @('Days with |r| > 3%', '13%', '36%', '41%'),
        @('Worst day', '−9.5%', '−16.3%', '−16.5%'),
        @('Best day', '+9.3%', '+8.4%', '+6.7%'),
        @('Maximum drawdown', '23%', '32%', '54%')
    ) @(4.6, 3.8, 3.8, 3.8) 'stress'
    Body 'The model is not meant to reproduce these historical crashes: the shocks are stylised and are used to compare interruption rules. Since each stress period has only about 50 trading days, higher-order statistics such as kurtosis and autocorrelations are unreliable there and are not used as targets.'
}
$content['Key Assumptions'] = {
    Body 'Public data on the order book and on investor behaviour in Euronext Lisbon is scarce. For this reason, every value that does not come directly from data is recorded in an assumptions register (Appendix E), with its justification and the way it is tested: calibrated against the stylised facts (C), included in the sensitivity analysis (S), covered by the extreme condition tests (V), or fixed as a rule or simplification (—). The most relevant assumptions are:'
    Bullets @('a single stock (BCP) is modelled, without contagion to other stocks;', 'the trading day is a continuous 510-minute session, without opening and closing auctions;', 'all orders are limit orders, and an aggressive limit order plays the role of a market order;', 'the number of agents of each type and their behavioural parameters are not observable; they are taken from the agent-based market literature and calibrated against the stylised facts;', 'the shocks are stylised news events inspired by the BES resolution, not reproductions of historical crashes.')
}
$content['Fundamentalist agent type'] = {
    Body 'Fundamentalists represent informed investors who trade on the gap between the market price and their own estimate of the value of the share. They buy when the share is cheap and sell when it is expensive, which pulls the price back towards its fundamental value and stabilises the market.'
    Body 'Each fundamentalist has its own estimate of the value, value() = fundamentalValue × (1 + bias), where bias is drawn once per agent from a normal distribution with mean 0 and standard deviation 2%. This heterogeneity of beliefs avoids all fundamentalists trading at the same time and in the same direction. Each agent starts with 5000 € in cash and 10 000 shares.'
    Tbl 'Key parameters, variables and functions of the Fundamentalist agent type' @('Name', 'Type', 'Value', 'Description') @(
        @('nFundamentalists', 'Parameter (Main, int)', '40', 'Number of fundamentalists'),
        @('fundRate', 'Parameter (Main)', '0.2', 'Decisions per minute of each fundamentalist (one every 5 min on average)'),
        @('fundBand', 'Parameter (Main)', '0.01', 'Minimum gap between price and value that triggers a trade'),
        @('cash', 'Variable (double)', '5000', 'Available cash (EUR)'),
        @('position', 'Variable (int)', '10 000', 'Number of shares held'),
        @('bias', 'Variable (double)', 'Normal(0, 2%)', 'Individual valuation error'),
        @('value()', 'Function (double)', '—', 'Value of the share estimated by the agent')
    ) @(3.2, 3.6, 2.6, 6.6) 'fundParams'
    Body 'The behaviour is defined by the statechart in {F:fundChart} and {T:fundStates}. The composite state Active contains the trading logic. At random instants, with rate fundRate per minute, the agent leaves Watching and compares the mid price with its estimate. It buys if the price is more than fundBand below value() and it can afford at least 100 shares, and sells if the price is more than fundBand above value() and it holds at least 100 shares.'
    Fig (Join-Path $figDirJ 'fundamentalist_statechart.png') 'Statechart of the Fundamentalist agent type' 12.0 'fundChart'
    Tbl 'States and transitions of the Fundamentalist agent type statechart' @('State', 'Meaning', 'Transitions') @(
        @('Watching', 'Waiting for the next decision (initial state of Active)', 'To the branch decide at rate fundRate'),
        @('decide (branch)', 'Compares the mid price with value()', 'To Buying if cheap and cash allows; to Selling if expensive and shares allow; to OutOfCash if no cash and no shares; otherwise (default) back to Watching'),
        @('Buying', 'Submits a buy order', 'Back to Watching immediately (timeout 0)'),
        @('Selling', 'Submits a sell order', 'Back to Watching immediately (timeout 0)'),
        @('OutOfCash', 'No cash and fewer than 100 shares', 'Back to Watching after 60 min'),
        @('Halted', 'Trading suspended during a reservation', 'From Active on message HALT; back to Active (Watching) on message REOPEN')
    ) @(3.0, 5.2, 7.8) 'fundStates'
    Body 'The size of each order grows with the mispricing: a buy order has 100 + 20 000 × (value/mid − 1) shares, limited by the available cash, and a sell order has 100 + 20 000 × (mid/value − 1) shares, limited by the shares held. The limit price never exceeds the agent''s own estimate and stays within 0.2% of the mid price, so fundamentalists rarely move the price by themselves. The cash and the position are updated by the function onFill of the Main agent every time one of their orders is executed.'
    Body 'During a reservation period the Stock agent broadcasts a HALT message, which is delivered directly to the statechart of every fundamentalist. Because the transition to Halted leaves the border of the composite state Active, the agent stops trading whatever its current state, and returns to Watching when the REOPEN message arrives after the reopening auction.'
    Body 'Two tests confirmed this behaviour. With noise traders only, the price follows a random walk with no anchor; with 40 fundamentalists it oscillates within about ±2% of the fundamental value of 0.50 €. In a deliberately volatile market (noiseSigma = 0.05), every HALT was followed by a REOPEN 3.01 minutes later and the fundamentalists stayed in Halted during each reservation.'
}
$content['APPENDIX E: Assumptions Register'] = {
    Body 'Test: C = calibrated against the stylised facts; S = sensitivity analysis; V = extreme condition tests; — = fixed rule or simplification. The Value column is updated with the calibrated values at the end of the project.'
    Tbl 'Assumptions register' @('#', 'Assumption', 'Value', 'Justification / source', 'Test') @(
        @('1', 'A single stock (BCP), without contagion', '—', 'Phase 1 scope, as recommended', '—'),
        @('2', 'Collar rules: ±3% dynamic, ±8% static, 3-min reservation (10 min if the static collar repeats), reopening auction', 'real rules', 'Euronext Trading Safeguards', '—'),
        @('3', 'Continuous 510-min trading day; no overnight, opening or closing auctions', '510 min', 'Simplification; the static reference changes every 510 min', '—'),
        @('4', 'Initial price and initial fundamental value', '0.50 €', 'Order of magnitude of BCP', '—'),
        @('5', 'Tick size', '0.0001 €', 'Simplification (Euronext uses a tick size table)', '—'),
        @('6', 'All orders are limit orders; an aggressive order acts as a market order', '—', 'Order book simplification', '—'),
        @('7', 'Mean order lifetime (orderLife), drawn as orderLife × U(0.3, 1.7)', '35 min', 'No data on cancellations in Lisbon', 'C, S'),
        @('8', 'Number of agents (nFundamentalists, nChartists, nNoise)', '40 / 30 / 30', 'Agent-based market literature (e.g. Lux & Marchesi, 1999)', 'C'),
        @('9', 'Fundamentalist band and decision rate (fundBand, fundRate)', '0.01 / 0.2 per min', 'Literature (e.g. Chiarella & Iori, 2002)', 'C, S'),
        @('10', 'Valuation error of each fundamentalist (bias)', 'Normal(0, 2%)', 'Heterogeneous beliefs', '—'),
        @('11', 'Trend follower decision rate and threshold (chartRate, trendThreshold)', '0.2 per min / 0.005', 'Literature (e.g. Lux & Marchesi, 1999)', 'C, S'),
        @('12', 'Memory of the moving average (maWindow)', '50 min', 'Intermediate intraday horizon', 'C, S'),
        @('13', 'Trend follower network; only trend follower neighbours receive the signal', 'small world, 6 links', 'As in the Market Model used in class', '—'),
        @('14', 'Herding threshold and panic duration (herdThreshold, panicDuration)', '2 / 10 min', 'Not observable', 'C, S'),
        @('15', 'Noise trader rate and price dispersion (noiseRate, noiseSigma)', '1 per min / 0.2%', 'Baseline volume and liquidity', 'C, S'),
        @('16', 'Market maker spread and quantity (mmSpread, mmQty)', '0.4% / 2000', 'No data; tested at extreme values', 'S, V'),
        @('17', 'Stylised news shock (shockSize, shockTime)', '−10%, day 60', 'Inspired by BES; not a reproduction', 'S'),
        @('18', 'Probability of panic of a trend follower after the shock (shockPanicProb)', '0.3', 'Not observable', 'S'),
        @('19', 'Small news events (newsRate)', '~1 every 5 days', 'Simplification', '—'),
        @('20', 'Initial endowment of fundamentalists and trend followers (cash, position)', '5000 € / 10 000 shares', 'All equal; half in cash, half in shares', 'S'),
        @('21', 'Fundamentalist orders: 100 + 20 000 × deviation from value; limit up to ±0.2% of the mid', '—', 'Larger orders for larger mispricing', 'C'),
        @('22', 'Fundamentalist without cash or shares waits before trying again', '60 min', 'Simplification', '—'),
        @('23', 'Trend follower orders: up to 500 shares at ±0.3% of the mid; panic up to 2000 shares at −1%', '—', 'Panic sells large quantities below the market', 'C'),
        @('24', 'Trend followers forget sell signals', '30 min', 'Not observable', '—'),
        @('25', 'Noise traders have no cash or short-selling constraints', '—', 'Source of baseline liquidity', '—'),
        @('26', 'Noise trader order quantity', 'U(100, 1000)', 'Simplification', '—'),
        @('27', 'Dynamic collar measured against the last traded price', 'lastPrice', 'Simplification of the Euronext dynamic reference', 'V'),
        @('28', 'Instantaneous reopening auction: maximum volume, ties broken by proximity to the last price', '—', 'Simplified auction rule', 'V'),
        @('29', 'During a reservation, fundamentalists and trend followers stop; noise trader orders wait for the auction', '—', 'Orders accumulate for the auction, as in the real market', '—'),
        @('30', 'BES stress period starts on 15 July 2014', '15/07–30/09/2014', 'Excludes the price jumps caused by the BCP capital increase', '—'),
        @('31', 'Source of real data: Yahoo Finance adjusted daily prices (BCP.LS)', '2010–2026', 'Free source with a long history', '—')
    ) @(0.8, 6.0, 2.6, 5.2, 1.4) 'assumptions'
}

$referencesJoao = @('Chiarella, C., & Iori, G. (2002). A simulation analysis of the microstructure of double auction markets. Quantitative Finance, 2(5), 346–353.', 'Lux, T., & Marchesi, M. (1999). Scaling and criticality in a stochastic multi-agent model of a financial market. Nature, 397, 498–500.')
