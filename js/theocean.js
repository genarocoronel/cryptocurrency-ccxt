'use strict';

const Exchange = require ('./base/Exchange');
const { ExchangeError, ExchangeNotAvailable, InsufficientFunds, OrderNotFound, DDoSProtection, InvalidOrder, AuthenticationError } = require ('./base/errors');

module.exports = class theocean extends Exchange {
    describe () {
        return this.deepExtend (super.describe (), {
            'id': 'theocean',
            'name': 'TheOcean',
            'countries': [ 'US' ],
            'rateLimit': 3000,
            'version': 'v0',
            'userAgent': this.userAgents['chrome'],
            'has': {
                'CORS': false, // ?
                'fetchTickers': true,
            },
            'urls': {
                'logo': 'https://user-images.githubusercontent.com/1294454/27982022-75aea828-63a0-11e7-9511-ca584a8edd74.jpg',
                'api': 'https://api.staging.theocean.trade/api',
                'www': 'https://theocean.trade',
                'doc': 'https://docs.theocean.trade',
                'fees': 'https://theocean.trade/fees',
            },
            'api': {
                'public': {
                    'get': [
                        'token_pairs',
                        'ticker',
                        'tickers',
                        'candlesticks',
                        'candlesticks/intervals',
                        'trade_history',
                        'order_book',
                        'order/{orderHash}',
                        'available_balance',
                    ],
                },
                'private': {
                    'get': [
                        'user_history',
                    ],
                    'post': [
                        'limit_order/reserve',
                        'limit_order/place',
                        'market_order/reserve',
                        'market_order/place',
                    ],
                    'delete': [
                        'order/{orderHash}',
                    ],
                },
            },
            'exceptions': {
                '803': InvalidOrder, // "Count could not be less than 0.001." (selling below minAmount)
                '804': InvalidOrder, // "Count could not be more than 10000." (buying above maxAmount)
                '805': InvalidOrder, // "price could not be less than X." (minPrice violation on buy & sell)
                '806': InvalidOrder, // "price could not be more than X." (maxPrice violation on buy & sell)
                '807': InvalidOrder, // "cost could not be less than X." (minCost violation on buy & sell)
                '831': InsufficientFunds, // "Not enougth X to create buy order." (buying with balance.quote < order.cost)
                '832': InsufficientFunds, // "Not enougth X to create sell order." (selling with balance.base < order.amount)
                '833': OrderNotFound, // "Order with id X was not found." (cancelling non-existent, closed and cancelled order)
            },
        });
    }

    calculateFee (symbol, type, side, amount, price, takerOrMaker = 'taker', params = {}) {
        let market = this.markets[symbol];
        let key = 'quote';
        let rate = market[takerOrMaker];
        let cost = parseFloat (this.costToPrecision (symbol, amount * rate));
        if (side === 'sell') {
            cost *= price;
        } else {
            key = 'base';
        }
        return {
            'type': takerOrMaker,
            'currency': market[key],
            'rate': rate,
            'cost': cost,
        };
    }

    async fetchMarkets () {
        let markets = await this.publicGetTokenPairs ();
        //
        //     [
        //       {
        //         "baseToken": {
        //           "address": "0xa8e9fa8f91e5ae138c74648c9c304f1c75003a8d",
        //           "symbol": "ZRX",
        //           "decimals": "18",
        //           "minAmount": "1000000000000000000",
        //           "maxAmount": "100000000000000000000000",
        //           "precision": "18"
        //         },
        //         "quoteToken": {
        //           "address": "0xc00fd9820cd2898cc4c054b7bf142de637ad129a",
        //           "symbol": "WETH",
        //           "decimals": "18",
        //           "minAmount": "5000000000000000",
        //           "maxAmount": "100000000000000000000",
        //           "precision": "18"
        //         }
        //       }
        //     ]
        //
        let result = [];
        for (let i = 0; i < markets.length; i++) {
            let market = markets[i];
            let baseToken = market['baseToken'];
            let quoteToken = market['quoteToken'];
            let baseId = baseToken['address'];
            let quoteId = quoteToken['address'];
            let base = baseToken['symbol'];
            let quote = quoteToken['symbol'];
            base = this.commonCurrencyCode (base);
            quote = this.commonCurrencyCode (quote);
            let symbol = base + '/' + quote;
            let id = baseId + '/' + quoteId;
            let precision = {
                'amount': this.safeInteger (baseToken, 'precision'),
                'price': this.safeInteger (quoteToken, 'precision'),
            };
            let amountLimits = {
                'min': this.safeFloat (baseToken, 'minAmount'),
                'max': this.safeFloat (baseToken, 'maxAmount'),
            };
            let priceLimits = {
                'min': undefined,
                'max': undefined,
            };
            let costLimits = {
                'min': this.safeFloat (quoteToken, 'minAmount'),
                'max': this.safeFloat (quoteToken, 'maxAmount'),
            };
            let limits = {
                'amount': amountLimits,
                'price': priceLimits,
                'cost': costLimits,
            };
            let active = true;
            result.push ({
                'id': id,
                'symbol': symbol,
                'base': base,
                'quote': quote,
                'baseId': baseId,
                'quoteId': quoteId,
                'active': active,
                'taker': undefined,
                'maker': undefined,
                'precision': precision,
                'limits': limits,
                'info': market,
            });
        }
        return result;
    }

    async fetchBalance (params = {}) {
        await this.loadMarkets ();
        let response = await this.privatePostGetInfo ();
        let balances = response['return'];
        let result = { 'info': balances };
        let funds = balances['funds'];
        let currencies = Object.keys (funds);
        for (let c = 0; c < currencies.length; c++) {
            let currency = currencies[c];
            let uppercase = currency.toUpperCase ();
            uppercase = this.commonCurrencyCode (uppercase);
            let total = undefined;
            let used = undefined;
            if (balances['open_orders'] === 0) {
                total = funds[currency];
                used = 0.0;
            }
            let account = {
                'free': funds[currency],
                'used': used,
                'total': total,
            };
            result[uppercase] = account;
        }
        return this.parseBalance (result);
    }

    async fetchOrderBook (symbol, limit = undefined, params = {}) {
        await this.loadMarkets ();
        let market = this.market (symbol);
        let request = {
            'pair': market['id'],
        };
        if (typeof limit !== 'undefined')
            request['limit'] = limit; // default = 150, max = 2000
        let response = await this.publicGetDepthPair (this.extend (request, params));
        let market_id_in_reponse = (market['id'] in response);
        if (!market_id_in_reponse)
            throw new ExchangeError (this.id + ' ' + market['symbol'] + ' order book is empty or not available');
        let orderbook = response[market['id']];
        return this.parseOrderBook (orderbook);
    }

    async fetchOrderBooks (symbols = undefined, params = {}) {
        await this.loadMarkets ();
        let ids = undefined;
        if (typeof symbols === 'undefined') {
            ids = this.ids.join ('-');
            // max URL length is 2083 symbols, including http schema, hostname, tld, etc...
            if (ids.length > 2048) {
                let numIds = this.ids.length;
                throw new ExchangeError (this.id + ' has ' + numIds.toString () + ' symbols exceeding max URL length, you are required to specify a list of symbols in the first argument to fetchOrderBooks');
            }
        } else {
            ids = this.marketIds (symbols);
            ids = ids.join ('-');
        }
        let response = await this.publicGetDepthPair (this.extend ({
            'pair': ids,
        }, params));
        let result = {};
        ids = Object.keys (response);
        for (let i = 0; i < ids.length; i++) {
            let id = ids[i];
            let symbol = id;
            if (id in this.markets_by_id) {
                let market = this.markets_by_id[id];
                symbol = market['symbol'];
            }
            result[symbol] = this.parseOrderBook (response[id]);
        }
        return result;
    }

    parseTicker (ticker, market = undefined) {
        //
        //     {
        //         "bid": "0.00050915",
        //         "ask": "0.00054134",
        //         "last": "0.00052718",
        //         "volume": "3000000000000000000",
        //         "timestamp": "1512929327792"
        //     }
        //
        let timestamp = parseInt (ticker['timestamp'] / 1000);
        let symbol = undefined;
        if (market)
            symbol = market['symbol'];
        let last = this.safeFloat (ticker, 'last');
        return {
            'symbol': symbol,
            'timestamp': timestamp,
            'datetime': this.iso8601 (timestamp),
            'high': undefined,
            'low': undefined,
            'bid': this.safeFloat (ticker, 'bid'),
            'bidVolume': undefined,
            'ask': this.safeFloat (ticker, 'ask'),
            'askVolume': undefined,
            'vwap': undefined,
            'open': undefined,
            'close': last,
            'last': last,
            'previousClose': undefined,
            'change': this.safeFloat (ticker, 'priceChange'),
            'percentage': undefined,
            'average': undefined,
            'baseVolume': this.safeString (ticker, 'volume'),
            'quoteVolume': undefined,
            'info': ticker,
        };
    }

    async fetchTickers (symbols = undefined, params = {}) {
        await this.loadMarkets ();
        let ids = undefined;
        if (typeof symbols === 'undefined') {
            ids = this.ids.join ('-');
            // max URL length is 2083 symbols, including http schema, hostname, tld, etc...
            if (ids.length > 2048) {
                let numIds = this.ids.length;
                throw new ExchangeError (this.id + ' has ' + numIds.toString () + ' symbols exceeding max URL length, you are required to specify a list of symbols in the first argument to fetchTickers');
            }
        } else {
            ids = this.marketIds (symbols);
            ids = ids.join ('-');
        }
        let tickers = await this.publicGetTickerPair (this.extend ({
            'pair': ids,
        }, params));
        let result = {};
        let keys = Object.keys (tickers);
        for (let k = 0; k < keys.length; k++) {
            let id = keys[k];
            let ticker = tickers[id];
            let symbol = id;
            let market = undefined;
            if (id in this.markets_by_id) {
                market = this.markets_by_id[id];
                symbol = market['symbol'];
            }
            result[symbol] = this.parseTicker (ticker, market);
        }
        return result;
    }

    async fetchTicker (symbol, params = {}) {
        await this.loadMarkets ();
        let market = this.market (symbol);
        let request = {
            'baseTokenAddress': market['baseId'],
            'quoteTokenAddress': market['quoteId'],
        };
        let response = await this.publicGetTicker (this.extend (request, params));
        return this.parseTicker (response, market);
    }

    parseTrade (trade, market = undefined) {
        let timestamp = parseInt (trade['timestamp']) * 1000;
        let side = trade['type'];
        if (side === 'ask')
            side = 'sell';
        if (side === 'bid')
            side = 'buy';
        let price = this.safeFloat (trade, 'price');
        if ('rate' in trade)
            price = this.safeFloat (trade, 'rate');
        let id = this.safeString (trade, 'tid');
        if ('trade_id' in trade)
            id = this.safeString (trade, 'trade_id');
        let order = this.safeString (trade, this.getOrderIdKey ());
        if ('pair' in trade) {
            let marketId = trade['pair'];
            market = this.markets_by_id[marketId];
        }
        let symbol = undefined;
        if (market)
            symbol = market['symbol'];
        let amount = trade['amount'];
        let type = 'limit'; // all trades are still limit trades
        let isYourOrder = this.safeValue (trade, 'is_your_order');
        let takerOrMaker = 'taker';
        if (typeof isYourOrder !== 'undefined')
            if (isYourOrder)
                takerOrMaker = 'maker';
        let fee = this.calculateFee (symbol, type, side, amount, price, takerOrMaker);
        return {
            'id': id,
            'order': order,
            'timestamp': timestamp,
            'datetime': this.iso8601 (timestamp),
            'symbol': symbol,
            'type': type,
            'side': side,
            'price': price,
            'amount': amount,
            'fee': fee,
            'info': trade,
        };
    }

    async fetchTrades (symbol, since = undefined, limit = undefined, params = {}) {
        await this.loadMarkets ();
        let market = this.market (symbol);
        let request = {
            'pair': market['id'],
        };
        if (typeof limit !== 'undefined')
            request['limit'] = limit;
        let response = await this.publicGetTradesPair (this.extend (request, params));
        return this.parseTrades (response[market['id']], market, since, limit);
    }

    async createOrder (symbol, type, side, amount, price = undefined, params = {}) {
        if (type === 'market')
            throw new ExchangeError (this.id + ' allows limit orders only');
        await this.loadMarkets ();
        let market = this.market (symbol);
        let request = {
            'pair': market['id'],
            'type': side,
            'amount': this.amountToPrecision (symbol, amount),
            'rate': this.priceToPrecision (symbol, price),
        };
        price = parseFloat (price);
        amount = parseFloat (amount);
        let response = await this.privatePostTrade (this.extend (request, params));
        let id = undefined;
        let status = 'open';
        let filled = 0.0;
        let remaining = amount;
        if ('return' in response) {
            id = this.safeString (response['return'], this.getOrderIdKey ());
            if (id === '0') {
                id = this.safeString (response['return'], 'init_order_id');
                status = 'closed';
            }
            filled = this.safeFloat (response['return'], 'received', 0.0);
            remaining = this.safeFloat (response['return'], 'remains', amount);
        }
        let timestamp = this.milliseconds ();
        let order = {
            'id': id,
            'timestamp': timestamp,
            'datetime': this.iso8601 (timestamp),
            'lastTradeTimestamp': undefined,
            'status': status,
            'symbol': symbol,
            'type': type,
            'side': side,
            'price': price,
            'cost': price * filled,
            'amount': amount,
            'remaining': remaining,
            'filled': filled,
            'fee': undefined,
            // 'trades': this.parseTrades (order['trades'], market),
        };
        this.orders[id] = order;
        return this.extend ({ 'info': response }, order);
    }

    getOrderIdKey () {
        return 'order_id';
    }

    async cancelOrder (id, symbol = undefined, params = {}) {
        await this.loadMarkets ();
        let response = undefined;
        let request = {};
        let idKey = this.getOrderIdKey ();
        request[idKey] = id;
        response = await this.privatePostCancelOrder (this.extend (request, params));
        if (id in this.orders)
            this.orders[id]['status'] = 'canceled';
        return response;
    }

    parseOrderStatus (status) {
        let statuses = {
            '0': 'open',
            '1': 'closed',
            '2': 'canceled',
            '3': 'canceled', // or partially-filled and still open? https://github.com/ccxt/ccxt/issues/1594
        };
        if (status in statuses)
            return statuses[status];
        return status;
    }

    parseOrder (order, market = undefined) {
        let id = order['id'].toString ();
        let status = this.safeString (order, 'status');
        if (status !== 'undefined')
            status = this.parseOrderStatus (status);
        let timestamp = parseInt (order['timestamp_created']) * 1000;
        let symbol = undefined;
        if (!market)
            market = this.markets_by_id[order['pair']];
        if (market)
            symbol = market['symbol'];
        let remaining = undefined;
        let amount = undefined;
        let price = this.safeFloat (order, 'rate');
        let filled = undefined;
        let cost = undefined;
        if ('start_amount' in order) {
            amount = this.safeFloat (order, 'start_amount');
            remaining = this.safeFloat (order, 'amount');
        } else {
            remaining = this.safeFloat (order, 'amount');
            if (id in this.orders)
                amount = this.orders[id]['amount'];
        }
        if (typeof amount !== 'undefined') {
            if (typeof remaining !== 'undefined') {
                filled = amount - remaining;
                cost = price * filled;
            }
        }
        let fee = undefined;
        let result = {
            'info': order,
            'id': id,
            'symbol': symbol,
            'timestamp': timestamp,
            'datetime': this.iso8601 (timestamp),
            'lastTradeTimestamp': undefined,
            'type': 'limit',
            'side': order['type'],
            'price': price,
            'cost': cost,
            'amount': amount,
            'remaining': remaining,
            'filled': filled,
            'status': status,
            'fee': fee,
        };
        return result;
    }

    parseOrders (orders, market = undefined, since = undefined, limit = undefined) {
        let ids = Object.keys (orders);
        let result = [];
        for (let i = 0; i < ids.length; i++) {
            let id = ids[i];
            let order = orders[id];
            let extended = this.extend (order, { 'id': id });
            result.push (this.parseOrder (extended, market));
        }
        return this.filterBySinceLimit (result, since, limit);
    }

    async fetchOrder (id, symbol = undefined, params = {}) {
        await this.loadMarkets ();
        let response = await this.privatePostOrderInfo (this.extend ({
            'order_id': parseInt (id),
        }, params));
        id = id.toString ();
        let newOrder = this.parseOrder (this.extend ({ 'id': id }, response['return'][id]));
        let oldOrder = (id in this.orders) ? this.orders[id] : {};
        this.orders[id] = this.extend (oldOrder, newOrder);
        return this.orders[id];
    }

    updateCachedOrders (openOrders, symbol) {
        // update local cache with open orders
        // this will add unseen orders and overwrite existing ones
        for (let j = 0; j < openOrders.length; j++) {
            const id = openOrders[j]['id'];
            this.orders[id] = openOrders[j];
        }
        let openOrdersIndexedById = this.indexBy (openOrders, 'id');
        let cachedOrderIds = Object.keys (this.orders);
        for (let k = 0; k < cachedOrderIds.length; k++) {
            // match each cached order to an order in the open orders array
            // possible reasons why a cached order may be missing in the open orders array:
            // - order was closed or canceled -> update cache
            // - symbol mismatch (e.g. cached BTC/USDT, fetched ETH/USDT) -> skip
            let cachedOrderId = cachedOrderIds[k];
            let cachedOrder = this.orders[cachedOrderId];
            if (!(cachedOrderId in openOrdersIndexedById)) {
                // cached order is not in open orders array
                // if we fetched orders by symbol and it doesn't match the cached order -> won't update the cached order
                if (typeof symbol !== 'undefined' && symbol !== cachedOrder['symbol'])
                    continue;
                // cached order is absent from the list of open orders -> mark the cached order as closed
                if (cachedOrder['status'] === 'open') {
                    cachedOrder = this.extend (cachedOrder, {
                        'status': 'closed', // likewise it might have been canceled externally (unnoticed by "us")
                        'cost': undefined,
                        'filled': cachedOrder['amount'],
                        'remaining': 0.0,
                    });
                    if (typeof cachedOrder['cost'] === 'undefined') {
                        if (typeof cachedOrder['filled'] !== 'undefined')
                            cachedOrder['cost'] = cachedOrder['filled'] * cachedOrder['price'];
                    }
                    this.orders[cachedOrderId] = cachedOrder;
                }
            }
        }
        return this.toArray (this.orders);
    }

    async fetchOrders (symbol = undefined, since = undefined, limit = undefined, params = {}) {
        if ('fetchOrdersRequiresSymbol' in this.options)
            if (this.options['fetchOrdersRequiresSymbol'])
                if (typeof symbol === 'undefined')
                    throw new ExchangeError (this.id + ' fetchOrders requires a symbol argument');
        await this.loadMarkets ();
        let request = {};
        let market = undefined;
        if (typeof symbol !== 'undefined') {
            let market = this.market (symbol);
            request['pair'] = market['id'];
        }
        let response = await this.privatePostActiveOrders (this.extend (request, params));
        // liqui etc can only return 'open' orders (i.e. no way to fetch 'closed' orders)
        let openOrders = [];
        if ('return' in response)
            openOrders = this.parseOrders (response['return'], market);
        let allOrders = this.updateCachedOrders (openOrders, symbol);
        let result = this.filterBySymbol (allOrders, symbol);
        return this.filterBySinceLimit (result, since, limit);
    }

    async fetchOpenOrders (symbol = undefined, since = undefined, limit = undefined, params = {}) {
        let orders = await this.fetchOrders (symbol, since, limit, params);
        return this.filterBy (orders, 'status', 'open');
    }

    async fetchClosedOrders (symbol = undefined, since = undefined, limit = undefined, params = {}) {
        let orders = await this.fetchOrders (symbol, since, limit, params);
        return this.filterBy (orders, 'status', 'closed');
    }

    async fetchMyTrades (symbol = undefined, since = undefined, limit = undefined, params = {}) {
        await this.loadMarkets ();
        let market = undefined;
        let request = {
            // 'from': 123456789, // trade ID, from which the display starts numerical 0 (test result: liqui ignores this field)
            // 'count': 1000, // the number of trades for display numerical, default = 1000
            // 'from_id': trade ID, from which the display starts numerical 0
            // 'end_id': trade ID on which the display ends numerical ∞
            // 'order': 'ASC', // sorting, default = DESC (test result: liqui ignores this field, most recent trade always goes last)
            // 'since': 1234567890, // UTC start time, default = 0 (test result: liqui ignores this field)
            // 'end': 1234567890, // UTC end time, default = ∞ (test result: liqui ignores this field)
            // 'pair': 'eth_btc', // default = all markets
        };
        if (typeof symbol !== 'undefined') {
            market = this.market (symbol);
            request['pair'] = market['id'];
        }
        if (typeof limit !== 'undefined')
            request['count'] = parseInt (limit);
        if (typeof since !== 'undefined')
            request['since'] = parseInt (since / 1000);
        let response = await this.privatePostTradeHistory (this.extend (request, params));
        let trades = [];
        if ('return' in response)
            trades = response['return'];
        return this.parseTrades (trades, market, since, limit);
    }

    async withdraw (currency, amount, address, tag = undefined, params = {}) {
        this.checkAddress (address);
        await this.loadMarkets ();
        let response = await this.privatePostWithdrawCoin (this.extend ({
            'coinName': currency,
            'amount': parseFloat (amount),
            'address': address,
        }, params));
        return {
            'info': response,
            'id': response['return']['tId'],
        };
    }

    signBodyWithSecret (body) {
        return this.hmac (this.encode (body), this.encode (this.secret), 'sha512');
    }

    sign (path, api = 'public', method = 'GET', params = {}, headers = undefined, body = undefined) {
        let url = this.urls['api'] + '/' + this.version + '/' + this.implodeParams (path, params);
        let query = this.omit (params, this.extractParams (path));
        if (api === 'private') {
            this.checkRequiredCredentials ();
            let nonce = this.nonce ();
            body = this.urlencode (this.extend ({
                'nonce': nonce,
                'method': path,
            }, query));
            let signature = this.signBodyWithSecret (body);
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded',
                'Key': this.apiKey,
                'Sign': signature,
            };
        } else if (api === 'public') {
            if (Object.keys (query).length) {
                url += '?' + this.urlencode (query);
            }
        }
        return { 'url': url, 'method': method, 'body': body, 'headers': headers };
    }

    handleErrors (httpCode, reason, url, method, headers, body) {
        if (typeof body !== 'string')
            return; // fallback to default error handler
        if (body.length < 2)
            return; // fallback to default error handler
        if ((body[0] === '{') || (body[0] === '[')) {
            let response = JSON.parse (body);
            if ('success' in response) {
                //
                // 1 - Liqui only returns the integer 'success' key from their private API
                //
                //     { "success": 1, ... } httpCode === 200
                //     { "success": 0, ... } httpCode === 200
                //
                // 2 - However, exchanges derived from Liqui, can return non-integers
                //
                //     It can be a numeric string
                //     { "sucesss": "1", ... }
                //     { "sucesss": "0", ... }, httpCode >= 200 (can be 403, 502, etc)
                //
                //     Or just a string
                //     { "success": "true", ... }
                //     { "success": "false", ... }, httpCode >= 200
                //
                //     Or a boolean
                //     { "success": true, ... }
                //     { "success": false, ... }, httpCode >= 200
                //
                // 3 - Oversimplified, Python PEP8 forbids comparison operator (===) of different types
                //
                // 4 - We do not want to copy-paste and duplicate the code of this handler to other exchanges derived from Liqui
                //
                // To cover points 1, 2, 3 and 4 combined this handler should work like this:
                //
                let success = this.safeValue (response, 'success', false);
                if (typeof success === 'string') {
                    if ((success === 'true') || (success === '1'))
                        success = true;
                    else
                        success = false;
                }
                if (!success) {
                    const code = this.safeString (response, 'code');
                    const message = this.safeString (response, 'error');
                    const feedback = this.id + ' ' + this.json (response);
                    const exceptions = this.exceptions;
                    if (code in exceptions) {
                        throw new exceptions[code] (feedback);
                    }
                    // need a second error map for these messages, apparently...
                    // in fact, we can use the same .exceptions with string-keys to save some loc here
                    if (message === 'invalid api key') {
                        throw new AuthenticationError (feedback);
                    } else if (message === 'invalid sign') {
                        throw new AuthenticationError (feedback);
                    } else if (message === 'api key dont have trade permission') {
                        throw new AuthenticationError (feedback);
                    } else if (message.indexOf ('invalid parameter') >= 0) { // errorCode 0, returned on buy(symbol, 0, 0)
                        throw new InvalidOrder (feedback);
                    } else if (message === 'invalid order') {
                        throw new InvalidOrder (feedback);
                    } else if (message === 'Requests too often') {
                        throw new DDoSProtection (feedback);
                    } else if (message === 'not available') {
                        throw new ExchangeNotAvailable (feedback);
                    } else if (message === 'data unavailable') {
                        throw new ExchangeNotAvailable (feedback);
                    } else if (message === 'external service unavailable') {
                        throw new ExchangeNotAvailable (feedback);
                    } else {
                        throw new ExchangeError (this.id + ' unknown "error" value: ' + this.json (response));
                    }
                }
            }
        }
    }
};
