# Text of Miguel's sections, inserted by gerar_relatorio.ps1 under the matching heading.
# Helpers available: Body, Tbl, Fig.

$figDir = Join-Path $PSScriptRoot 'figures'

$content = @{}

$content['Main agent'] = {
    Body 'The Main agent is the top-level agent of the model. It holds every agent population and the global parameters, so that scenarios can be changed without modifying the model logic, together with three utility functions shared by all agents. The model time unit is the minute, and one trading day corresponds to 510 minutes, the length of the continuous trading session of Euronext Lisbon (08:00-16:30).'
    Body '{T:mainParams} lists the parameters and variables of the market core. The parameters that define the scenarios and the output files are presented in Chapter 7.'
    Tbl 'Key parameters and variables present in the Main agent' @('Name', 'Type', 'Value', 'Description') @(
        @('nNoise', 'Parameter (int)', '30', 'Number of noise traders'),
        @('initialPrice', 'Parameter', '0.50', 'Initial price and fundamental value of the stock (EUR), of the order of magnitude of BCP'),
        @('tickSize', 'Parameter', '0.0001', 'Minimum price increment (EUR)'),
        @('haltShort', 'Parameter', '3', 'Duration of a reservation period (min)'),
        @('haltLong', 'Parameter', '10', 'Duration of a repeated static reservation (min)'),
        @('noiseRate', 'Parameter', '1', 'Orders submitted per minute by each noise trader'),
        @('noiseSigma', 'Parameter', '0.002', 'Dispersion of the noise traders limit prices around the mid price'),
        @('orderLife', 'Parameter', '35', 'Mean lifetime of an order that is not executed (min)'),
        @('maWindow', 'Parameter', '50', 'Memory of the moving average used by trend followers (min)'),
        @('runTests', 'Parameter (boolean)', 'false', 'Runs the order book tests at start-up'),
        @('fundamentalValue', 'Variable', 'initialPrice', 'Fundamental value of the stock, changed by news'),
        @('dynamicThreshold', 'Variable', '0.03', 'Dynamic collar, relative to the last traded price'),
        @('staticThreshold', 'Variable', '0.08', 'Static collar, relative to the reference price'),
        @('collarsActive', 'Variable (boolean)', 'true', 'Switches the volatility interruptions on or off')
    ) @(3.2, 3.2, 2.3, 7.3) 'mainParams'
    Tbl 'Key functions present in the Main agent' @('Function', 'Description') @(
        @('roundTick(p)', 'Rounds a price to the tick size'),
        @('onFill(t, side, q, p)', 'Updates the cash and the position of a trader after one of its orders is executed'),
        @('broadcast(msg)', 'Delivers a message (HALT, REOPEN or SHOCK) to the statecharts of all agents')
    ) @(4.5, 11.5)
}

$content['Order Book (Stock agent type)'] = {
    Body 'The Stock agent type represents the BCP share and its limit order book. Following the recommendation received on the project proposal, the order book was implemented in Java and was built and tested before any trading agent was added to the model. Each order is a lightweight Java object (class Order) holding an identifier, the side (buy or sell), the limit price, the quantity left to execute, the submission time, the expiry time and a reference to the submitting agent. Representing orders as plain objects rather than as agents also keeps the model within the limits of AnyLogic PLE, which allows at most 50 000 dynamically created agents, since a single run generates millions of orders.'
    Body 'The order book is modelled as a queueing system with two priority queues. The bid queue is ordered by decreasing price and the ask queue by increasing price; orders with the same price are served by order of arrival, which is the price-time priority rule used by Euronext (first come, first served within each price level). Orders that are not executed within their lifetime leave the book, which represents order cancellations (reneging); the lifetime of each order is drawn uniformly between 0.3 and 1.7 times orderLife. A third queue, pending, holds the orders received during a reservation period until the reopening auction.'
    Body 'Matching is triggered every time an order arrives. While the best bid price is greater than or equal to the best ask price, a trade is executed at the price of the order that was already resting in the book, for the smallest of the two quantities, and fully executed orders leave their queue. An aggressive order can therefore sweep several price levels, which reproduces the behaviour of a market order. Before each trade, the function collarHit checks whether the trade price would breach a volatility collar; if it does, the trade is not executed and a reservation period starts (Section 4.2.3).'
    Tbl 'Key variables present in the Stock agent type' @('Name', 'Type', 'Description') @(
        @('bids, asks', 'PriorityQueue<Order>', 'The two sides of the order book, with price-time priority'),
        @('pending', 'ArrayList<Order>', 'Orders received during a reservation, waiting for the reopening auction'),
        @('lastPrice', 'double', 'Last traded price'),
        @('refPrice', 'double', 'Reference price of the static collar (opening or last auction price)'),
        @('ma', 'double', 'Moving average of the price, used by the trend followers'),
        @('halted', 'boolean', 'True during a reservation period'),
        @('volume', 'int', 'Cumulative traded volume'),
        @('lastStaticDir', 'int', 'Direction of the last static collar of the day (+1 or -1)')
    ) @(3.0, 4.2, 8.8)
    Tbl 'Key functions present in the Stock agent type' @('Function', 'Description') @(
        @('order(trader, side, price, qty)', 'Entry point used by all agents: creates an order and adds it to the book, or to the pending queue during a reservation'),
        @('match()', 'Executes trades while the best bid and the best ask cross'),
        @('execute(b, a, p, q)', 'Executes one trade: updates the last price, the volume and the traders, and removes filled orders'),
        @('bestBid(), bestAsk(), mid(), spread()', 'Best prices, mid price and bid-ask spread of the book'),
        @('cancelAll(a)', 'Cancels every order of a given agent'),
        @('collarHit(p)', 'Checks the dynamic and static collars before a trade and starts a reservation when one is breached'),
        @('runAuction()', 'Reopening auction (Section 4.2.3)'),
        @('testBook(), check(name, ok)', 'Order book tests (Section 6.1)')
    ) @(5.5, 10.5)
    Tbl 'Key events present in the Stock agent type' @('Event', 'Trigger', 'Description') @(
        @('matchEvent', 'Called by the model', 'Restarts matching after a reopening auction'),
        @('purgeEvent', 'Every minute', 'Removes the orders whose lifetime has expired'),
        @('dayEvent', 'Every 510 minutes', 'Starts a new trading day: the last price becomes the reference of the static collar'),
        @('maEvent', 'Every minute', 'Updates the moving average: ma = ma + (lastPrice - ma) / maWindow')
    ) @(3.0, 3.5, 9.5)
}

$content['Volatility Interruptions and Reopening Auction'] = {
    Body 'The volatility interruptions follow the Euronext trading safeguards for the constituents of its main indices, including the PSI. A reservation period starts when a trade would occur more than 3% away from the last traded price (dynamic collar) or more than 8% away from the reference price, which is the opening price or the price of the last auction (static collar). The reservation lasts 3 minutes and is extended to 10 minutes when the static collar is triggered again in the same direction on the same day. Trading then resumes through a reopening auction.'
    Body 'This mechanism is implemented with a statechart in the Stock agent type, shown in {F:stockChart} and described in {T:stockStates}. When a reservation starts, every agent receives a HALT message and new orders are kept in the pending queue; at the end of the auction, a REOPEN message is sent and continuous trading resumes.'
    Fig (Join-Path $figDir 'stock_statechart.png') 'Statechart defining the trading phases of the Stock agent type' 9.5 'stockChart'
    Tbl 'States and transitions of the Stock agent type statechart' @('State', 'Meaning', 'Transitions') @(
        @('Continuous', 'Continuous trading (initial state)', 'To ReservDynamic on message DYNAMIC; to ReservStatic on STATIC; to ReservStatic10 on STATIC_REPEAT'),
        @('ReservDynamic', 'Reservation after a breach of the dynamic collar', 'To Auction after haltShort (3 min)'),
        @('ReservStatic', 'Reservation after a breach of the static collar', 'To Auction after haltShort (3 min)'),
        @('ReservStatic10', 'Static collar breached again in the same direction', 'To Auction after haltLong (10 min)'),
        @('Auction', 'Reopening auction: the pending orders enter the book', 'To Continuous after 0.01 min, executing runAuction() and endHalt()')
    ) @(3.2, 5.5, 7.3) 'stockStates'
    Body 'The reopening auction sets a single uncrossing price. For every candidate price p (the limit prices present in the book), the demand is the quantity of bids with a price greater than or equal to p and the supply is the quantity of asks with a price lower than or equal to p; the executable volume is the minimum of the two. The auction selects the price with the largest executable volume and, in case of a tie, the one closest to the last traded price. All crossing orders are executed at that single price, which becomes the new reference price of the static collar.'
    Body '{F:halts} shows the mechanism at work in a deliberately volatile market (noise traders with a price dispersion of 5%): every HALT is followed by a REOPEN 3.01 minutes later, that is, the 3-minute reservation plus the auction.'
    Fig (Join-Path $figDir 'reservations_demo.png') 'Reservation periods in a volatile market: every HALT is followed by a REOPEN 3.01 minutes later' 6.0 'halts'
}

$content['Noise Trader agent type'] = {
    Body 'Noise traders represent uninformed participants and provide the baseline trading volume and liquidity of the market. They have no statechart: each noise trader submits orders at random instants, according to a Poisson process with rate noiseRate per minute. Each order is a buy or a sell with equal probability, has a limit price drawn from a normal distribution centred on the mid price with relative standard deviation noiseSigma, and a quantity drawn uniformly between 100 and 1000 shares. Noise traders keep submitting orders during reservation periods; these orders wait in the pending queue and take part in the reopening auction, as in the real market.'
    Tbl 'Key variables and events present in the Noise Trader agent type' @('Name', 'Type', 'Description') @(
        @('cash', 'Variable (double)', 'Available cash; set to a very large value so that noise traders are never constrained'),
        @('position', 'Variable (int)', 'Number of shares held (may become negative)'),
        @('trade', 'Event (rate noiseRate)', 'Submits a random buy or sell order around the mid price')
    ) @(3.0, 4.2, 8.8)
}

$content['Order Book Tests'] = {
    Body 'Before any trading agent was added, the order book was verified with six scripted tests (function testBook), run with no agents in the model. Each test submits known orders and checks that the resulting state of the book is the expected one. The tests are run again after every change to the Stock agent type. {T:tests} describes them and {F:tests} shows the output of the last run, in which all checks passed.'
    Tbl 'Order book tests' @('#', 'Situation', 'Expected behaviour', 'Result') @(
        @('1', 'Buy 100 at 0.50 and sell 100 at 0.51', 'No trade, since the prices do not cross; spread of 0.01', 'Pass'),
        @('2', 'Sell 40 at 0.50', '40 shares traded at 0.50, the price of the resting bid; 60 shares remain on the bid', 'Pass'),
        @('3', 'Buy 10 at 0.50 after the first bid, then sell 65 at 0.50', 'The first bid is filled before the second (first come, first served within the price level); the second bid keeps 5', 'Pass'),
        @('4', 'Sell 100 at 0.52, then buy 150 at 0.52', 'The buy order sweeps two levels: 100 at 0.51 and 50 at 0.52; last price of 0.52', 'Pass'),
        @('5', 'Sell at 0.40 against the bid at 0.50, with collars active', 'The trade (-3.8% from the last price) is blocked and a reservation starts: HALT at t = 0 and REOPEN at t = 3.01 min', 'Pass'),
        @('6', 'Cancel all orders', 'The order book is empty', 'Pass')
    ) @(0.8, 4.7, 8.8, 1.7) 'tests'
    Fig (Join-Path $figDir 'order_book_tests.png') 'Output of the order book tests' 9.0 'tests'
}
