# Miguel: Introduction, Problem Description and Modelling Approach.

$content['Introduction'] = {
    Body 'This chapter presents the context and motivation of the project, defines the objectives of the simulation model and outlines the structure of the report.'
}

$content['Context and Motivation'] = {
    Body 'Euronext Lisbon is the Portuguese stock exchange. Its main index, the PSI, is made up of 16 companies concentrated in a few sectors, namely energy, banking, retail, paper and infrastructure. It is a small market with limited liquidity and strong links between companies of the same sector, which makes it particularly exposed to sudden falls and to contagion.'
    Body 'Several stress episodes have hit this market: the sovereign debt crisis in 2011, the resolution of Banco Espirito Santo (BES) in 2014 and the crash of March 2020 at the start of the COVID-19 pandemic. In all of them, an initial fall amplified itself, often far beyond what the original news justified. Market crashes are not caused by bad news alone: participants react to each other, and the way the market is organised determines how far a fall can go.'
    Body 'To limit these dynamics, Euronext uses volatility interruptions: when the price moves too far in a short time, continuous trading stops for a few minutes and resumes through an auction. These mechanisms can stop a fall from accelerating, but while a stock is interrupted there is no trading and price discovery is delayed. The choice of the thresholds is therefore a trade-off between stability and liquidity, relevant for Euronext and for the Portuguese regulator (CMVM).'
    Body 'This trade-off cannot be studied by experimenting with the real market, and historical data offer only a few crashes and no counterfactual: it is impossible to observe the same fall with and without interruptions. Simulation addresses both limitations. An agent-based model reproduces a crash as the result of the interaction between heterogeneous investors and the order book, and allows the same shock to be replayed under different rules, with the same random numbers, to isolate the effect of the interruptions.'
}

$content["Simulation's Objectives"] = {
    Body 'The objective of this project is to build in AnyLogic an artificial market inspired by Euronext Lisbon, calibrated on the share of Banco Comercial Portugues (BCP), and to use it to understand how a fall propagates and to evaluate the effect of the volatility interruptions. The goal is not to predict prices nor to give investment advice. More specifically, the model aims to:'
    Bullets @(
        'reproduce the main statistical properties (stylised facts) of the BCP share in a calm period;',
        'represent the order book as a queueing system with price-time priority, together with the Euronext collars, reservation periods and reopening auctions;',
        'quantify how the share of trend followers and herding behaviour affect the probability and the size of crashes;',
        'compare collar thresholds and reservation durations in terms of the maximum fall and of the loss of liquidity;',
        'search for the thresholds that minimise the maximum fall for an acceptable loss of traded volume.'
    )
    Body 'Following the feedback received on the project proposal, the project is limited to a single stock (Phase 1). Leveraged investors, brokers and contagion between stocks are discussed as possible extensions in Chapter 10.'
}

$content['Report Structure'] = {
    Body 'Chapter 2 describes the problem: the Lisbon market, the mechanisms through which a fall propagates and the Euronext volatility interruptions, and states the research questions. Chapter 3 presents the data, the stylised facts the model must reproduce and the key assumptions. Chapter 4 describes the model and its implementation in AnyLogic, agent type by agent type, and Chapter 5 presents the simulation interface.'
    Body 'Chapter 6 covers the verification, calibration and validation of the model. Chapter 7 describes the experiments and scenarios and Chapter 8 presents their results, which are discussed in Chapter 9. Finally, Chapter 10 summarises the conclusions, the limitations of the model and possible directions for future work.'
}

$content['Problem Description'] = {
    Body 'This chapter describes the market under study, the mechanisms through which a fall propagates and the volatility interruption rules whose effect the model evaluates. It ends with the problem statement and the research questions.'
}

$content['Euronext Lisbon and the PSI'] = {
    Body 'Euronext Lisbon is part of the Euronext group, which operates the stock exchanges of several European countries under common trading rules. Its main index, the PSI, includes 16 companies and is dominated by a few large stocks and sectors, so a fall in one of them weighs heavily on the whole market.'
    Body 'The model focuses on a single stock, BCP, one of the most traded and most volatile constituents of the PSI. Its high trading activity provides enough data to calibrate the model, its volatility produces real interruption episodes, and, being a bank, it links the study to the BES resolution of 2014, which inspires the shock scenario.'
}

$content['How a Market Fall Propagates'] = {
    Body 'Trading takes place in a limit order book, where investors post buy and sell orders at the prices they are willing to accept. The order book is a queueing system: each price level is a queue of orders served first come, first served, aggressive orders consume these queues and cancelled orders leave them. When liquidity disappears, the queues near the best price empty and the next trade happens at a much worse price, so the price jumps.'
    Body 'A fall propagates through the reactions of the market participants to each other:'
    Bullets @(
        'trend followers sell because the price is falling, and herding spreads the selling from one investor to the next;',
        'investors in panic sell large quantities below the market price, consuming the buy side of the order book;',
        'market makers, who normally provide liquidity, withdraw their quotes when uncertainty rises, removing liquidity exactly when it is most needed.'
    )
    Body 'In this way, a moderate piece of bad news can turn into a crash that goes far beyond its original cause.'
}

$content['Volatility Interruptions at Euronext'] = {
    Body 'For the constituents of its main indices, including the PSI, Euronext applies volatility interruptions (collars). A price move beyond 3% from the last traded price (dynamic collar) or beyond 8% from the reference price, which is the opening or the last auction price (static collar), puts the stock in a reservation period of 3 minutes, extended to 10 minutes if the static collar is triggered again in the same direction. Trading then resumes through a reopening auction, in which the accumulated orders are executed at a single price.'
    Body 'These mechanisms give investors time to react and stop a fall from accelerating, but while a stock is halted there is no continuous trading, liquidity is lost and price discovery is delayed. The European Securities and Markets Authority analysed the effects of circuit breakers in European trading venues (ESMA, 2020); its findings are used in Chapter 6 to validate the behaviour of the model.'
}

$content['Problem Statement and Research Questions'] = {
    Body 'The problem addressed is how to set the volatility interruptions of Euronext Lisbon so that they limit crashes without excessively harming liquidity. Because this question cannot be answered by experimenting with the real market, it is studied with an agent-based simulation of the BCP order book. Every question is answered by comparison with a calm baseline that reproduces the statistics of the real stock, rather than by forecasting. The research questions are:'
    Bullets @(
        'RQ1: How do the share of trend followers and herding affect the probability and the size of crashes?',
        'RQ2: Which collar thresholds and reservation durations reduce the maximum fall the most without excessively harming liquidity?',
        'RQ3: Which thresholds minimise the maximum fall for an acceptable loss of traded volume?'
    )
    Body 'The interruptions are evaluated with three groups of indicators, measured in windows of 2, 5 and 10 minutes around each interruption and over the whole session: volatility (standard deviation of returns before and after the interruption, maximum drawdown and kurtosis of returns), liquidity (bid-ask spread, traded volume and time without continuous trading) and price recovery (time to recover half of the fall, gap between the reopening auction price and the pre-halt price, and number of repeated interruptions).'
}

$content['Modelling Approach'] = {
    Body 'The model is an agent-based simulation built in AnyLogic, with a discrete-event core: the order book is a queueing system in which orders arrive, wait, are executed or abandon the queue. Following the feedback on the proposal, the order book was implemented in Java inside the Stock agent type, instead of with Process Modeling Library blocks; orders are plain Java objects rather than agents, which also keeps the model within the limits of AnyLogic PLE. The time unit is the minute and one trading day lasts 510 minutes.'
    Body 'The model contains the following agent types:'
    Bullets @(
        'Stock: the BCP share, its order book, the volatility interruptions and the reopening auction;',
        'Fundamentalist: informed investors who buy below and sell above their estimate of the value of the share;',
        'Trend Follower: investors who follow the price trend and spread panic to their neighbours in a network (herding);',
        'Noise Trader: uninformed investors who provide the baseline volume and liquidity;',
        'Market Maker: a liquidity provider that quotes buy and sell prices around the mid price;',
        'News: the source of small news events and of the large stylised shock of the scenarios.'
    )
    Body 'All investors trade only by submitting orders to the Stock agent. The Stock agent informs every agent of the start and end of a reservation period with the messages HALT and REOPEN, the News agent announces shocks with the message SHOCK, and trend followers warn their neighbours with SELL_SIGNAL. Each simulation run records the price, the best prices and the volume every minute, and every interruption, in CSV files; Python scripts then compute the stylised facts and the indicators used in Chapters 6 to 8.'
}

$content['References'] = {
    $refs = @(
        'Chiarella, C., & Iori, G. (2002). A simulation analysis of the microstructure of double auction markets. Quantitative Finance, 2(5), 346-353.',
        'ESMA (2020). Market impacts of circuit breakers: Evidence from EU trading venues. ESMA Economic Report.',
        'Euronext. Trading safeguards. Euronext Rule Book and trading procedures.',
        'Lux, T., & Marchesi, M. (1999). Scaling and criticality in a stochastic multi-agent model of a financial market. Nature, 397, 498-500.'
    )
    foreach ($r in $refs) { Body $r }
}
