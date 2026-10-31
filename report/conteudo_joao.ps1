# João's sections. Edited directly since 31/10 (the old Joao_sections_DSS_report.docx and converter_joao.py are no longer used).
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
        @('2', 'Collar rules for PSI constituents: ±3% dynamic (last traded price), ±8% static (opening or previous reference price), 3-min reservation, 10 min for a consecutive static reservation in the same direction, reopening auction', 'real rules', 'Euronext Trading safeguards (consulted on 31/10/2026)', '—'),
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
        @('27', 'Dynamic collar measured against the last traded price', 'lastPrice', 'Euronext rule: the dynamic reference price is the last traded price', 'V'),
        @('28', 'Instantaneous reopening auction: maximum volume, ties broken by proximity to the last price', '—', 'Simplified auction rule', 'V'),
        @('29', 'During a reservation, fundamentalists and trend followers stop; noise trader orders wait for the auction', '—', 'Orders accumulate for the auction, as in the real market', '—'),
        @('30', 'BES stress period starts on 15 July 2014', '15/07–30/09/2014', 'Excludes the price jumps caused by the BCP capital increase', '—'),
        @('31', 'Source of real data: Yahoo Finance adjusted daily prices (BCP.LS)', '2010–2026', 'Free source with a long history', '—'),
        @('32', 'Reservations last exactly the Euronext minimum; in the real market they can be extended', '3 / 10 min', 'Simplification', 'S'),
        @('33', 'The static reference price is the last price of the previous day and is reset to the reopening auction price after each reservation; Euronext defines it as the opening price of the day or the previous reference price', '-', 'Simplification (no opening auction in the model)', 'V')
    ) @(0.8, 6.0, 2.6, 5.2, 1.4) 'assumptions'
}

$referencesJoao = @('Chiarella, C., & Iori, G. (2002). A simulation analysis of the microstructure of double auction markets. Quantitative Finance, 2(5), 346–353.', 'Lux, T., & Marchesi, M. (1999). Scaling and criticality in a stochastic multi-agent model of a financial market. Nature, 397, 498–500.')

$content['Trend Follower agent type and Herding'] = {
    Body 'Trend followers (chartists) ignore the value of the share and trade on the recent direction of the price. They buy when the price is above its moving average and sell when it is below. When they sell, they warn their neighbours in a social network, and an agent that receives enough warnings panics and sells a large quantity below the market. Trend following and herding amplify price movements, which is what drives the price towards the collars.'
    Body 'Each trend follower starts with 5000 € in cash and 10 000 shares and compares the last traded price with the moving average ma of the Stock agent, which is updated every minute with a memory of maWindow minutes. {T:chartParams} lists the parameters, variables, functions and events of this agent type.'
    Tbl 'Key parameters, variables, functions and events of the Trend Follower agent type' @('Name', 'Type', 'Value', 'Description') @(
        @('nChartists', 'Parameter (Main, int)', '30', 'Number of trend followers'),
        @('chartRate', 'Parameter (Main)', '0.2', 'Decisions per minute of each trend follower (one every 5 min on average)'),
        @('trendThreshold', 'Parameter (Main)', '0.005', 'Minimum gap between the last price and the moving average that triggers a trade'),
        @('herdThreshold', 'Parameter (Main, int)', '2', 'Number of sell signals from neighbours that triggers panic'),
        @('panicDuration', 'Parameter (Main)', '10', 'Duration of a panic episode (min)'),
        @('shockPanicProb', 'Parameter (Main)', '0.3', 'Probability of panic when a negative news shock arrives'),
        @('cash', 'Variable (double)', '5000', 'Available cash (EUR)'),
        @('position', 'Variable (int)', '10 000', 'Number of shares held'),
        @('sellSignals', 'Variable (int)', '0', 'Sell signals received from neighbours since the last reset'),
        @('signalNeighbours()', 'Function', '-', 'Delivers a SELL_SIGNAL message to the statechart of every trend follower neighbour'),
        @('forget', 'Event (every 30 min)', '-', 'Resets sellSignals, so that only recent warnings count')
    ) @(3.4, 3.6, 1.6, 7.4) 'chartParams'
    Body 'The trend followers are connected by a small-world network built in the start-up code of the Main agent, as in the Market Model used in class. The agents are placed on a ring and each one is linked to the next three, which gives about six neighbours per agent; with probability 5% a link goes to a random trend follower instead, creating shortcuts across the ring. The network only connects trend followers, so that the warnings are not lost on agents that do not react to them.'
    Body 'The behaviour is defined by the statechart in {F:chartChart} and {T:chartStates}. At random instants, with rate chartRate per minute, the agent leaves Neutral and compares the last price with the moving average. It buys up to 500 shares at 0.3% above the mid price if the price is more than trendThreshold above the average, and sells up to 500 shares at 0.3% below the mid price, warning its neighbours, if the price is more than trendThreshold below the average.'
    Fig (Join-Path $figDirJ 'chartist_statechart.png') 'Statechart of the Trend Follower agent type' 12.0 'chartChart'
    Tbl 'States and transitions of the Trend Follower agent type statechart' @('State', 'Meaning', 'Transitions') @(
        @('Neutral', 'Waiting for the next decision (initial state of Active)', 'To the branch decide at rate chartRate; to the branch herd on message SELL_SIGNAL (sellSignals + 1); to Panic on message SHOCK with probability shockPanicProb'),
        @('decide (branch)', 'Compares the last price with the moving average', 'To TrendBuy if the price is above the average and cash allows; to TrendSell if it is below and shares allow; otherwise (default) back to Neutral'),
        @('TrendBuy', 'Submits a buy order', 'Back to Neutral immediately (timeout 0)'),
        @('TrendSell', 'Submits a sell order and warns the neighbours', 'Back to Neutral immediately (timeout 0)'),
        @('herd (branch)', 'Counts the warnings received', 'To Panic if sellSignals reaches herdThreshold and the agent holds shares; otherwise (default) back to Neutral'),
        @('Panic', 'Sells up to 2000 shares at 1% below the mid price and warns the neighbours', 'Back to Neutral after panicDuration minutes, resetting sellSignals'),
        @('Halted', 'Trading suspended during a reservation', 'From Active on message HALT; back to Active (Neutral) on message REOPEN')
    ) @(3.0, 5.0, 8.0) 'chartStates'
    Body 'Herding spreads as a cascade: an agent in panic warns its neighbours, those that reach the threshold panic in turn and warn theirs, and the selling pressure grows faster than the fundamentalists can absorb it. The warnings are forgotten every 30 minutes, so panic only spreads when several neighbours sell at about the same time. Like the fundamentalists, trend followers stop trading during a reservation period, because the HALT and REOPEN messages are delivered to their statecharts.'
    Body 'Three tests confirmed this behaviour. Every trend follower had six neighbours in the network. With the default parameters, the collars were triggered in a normal market, which did not happen with fundamentalists and noise traders only. With 60 trend followers and a herding threshold of 1, the price rose by about 20% in two hours, triggering a 3-minute and a 10-minute reservation (the static collar breached twice in the same direction), and then stayed flat because the agents had run out of cash or shares; this limitation of the initial endowments is addressed in the calibration (Section 6.3).'
}

$content['Calibration'] = {
    Body 'The behavioural parameters of the agents are not observable, so they were calibrated against the stylised facts of the BCP stock fixed in Section 3.2 ({T:facts}). The calibration followed an iterative protocol. In each round the baseline scenario (no news shock, collars as in the real market) was run with 10 replications of 250 trading days, the statistics of {T:facts} were computed by the script compare_model.py for every replication, and the mean over the replications was compared with the BCP values using the acceptance criteria of the table. The median over the replications was also reported, to detect means driven by one or two extreme replications.'
    Body 'Only one mechanism was changed per round, chosen from the diagnosis of the previous round, so that the effect of each change could be identified. Every round is recorded in the calibration log (Appendix D) with the parameter values, the resulting statistics and the decision taken.'
    Body 'The first run of the complete model (round 0, with the parameter values of Appendix E) reproduced only the volume-volatility relation. The market was about five times calmer than BCP (daily volatility of 0.42% against 2.07%), almost no day moved by more than 3%, and daily returns were negatively autocorrelated (-0.14). The diagnosis was that the price was anchored by the fundamentalists to a fundamental value that hardly moved: with one news item every five trading days and a standard deviation of 1% per item, news alone generate a daily volatility of about 0.44%, which matches the model. The mean excess kurtosis of 9.6 came from three replications with reservation periods, while the median was only 0.2.'
}

$content['APPENDIX D: Calibration Log'] = {
    Body 'Each round used 10 replications of 250 trading days of the baseline scenario. Statistics are means over the replications (median kurtosis in brackets); the targets are those of {T:facts}.'
    Tbl 'Calibration log' @('Round', 'Change', 'Daily vol.', 'Kurtosis', 'Autocorr. |r|', 'Autocorr. r', 'Days > 3%', 'Corr. vol.-|r|', 'Facts met') @(
        @('Target', '-', '0.0155-0.0259', '1.21-3.62', '> 0.05', '-0.1 to 0.1', '6.5%-19.4%', '> 0', '6 / 6'),
        @('0', 'Initial values (Appendix E)', '0.0042', '9.58 (0.20)', '0.040', '-0.139', '0.2%', '0.204', '1 / 6')
    ) @(1.3, 3.6, 1.6, 1.7, 1.6, 1.6, 1.5, 1.6, 1.5) 'calibLog'
}
