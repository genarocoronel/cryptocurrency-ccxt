# -*- coding: utf-8 -*-

# PLEASE DO NOT EDIT THIS FILE, IT IS GENERATED AND WILL BE OVERWRITTEN:
# https://github.com/ccxt/ccxt/blob/master/CONTRIBUTING.md#how-to-contribute-code

from ccxt.base.exchange import Exchange

# -----------------------------------------------------------------------------

try:
    basestring  # Python 3
except NameError:
    basestring = str  # Python 2
import hashlib
import json
from ccxt.base.errors import ExchangeError
from ccxt.base.errors import AuthenticationError
from ccxt.base.errors import InsufficientFunds
from ccxt.base.errors import InvalidOrder
from ccxt.base.errors import OrderNotFound


class exmo (Exchange):

    def describe(self):
        return self.deep_extend(super(exmo, self).describe(), {
            'id': 'exmo',
            'name': 'EXMO',
            'countries': ['ES', 'RU'],  # Spain, Russia
            'rateLimit': 350,  # once every 350 ms ≈ 180 requests per minute ≈ 3 requests per second
            'version': 'v1',
            'has': {
                'CORS': False,
                'fetchClosedOrders': 'emulated',
                'fetchOpenOrders': True,
                'fetchOrder': 'emulated',
                'fetchOrders': 'emulated',
                'fetchOrderTrades': True,
                'fetchOrderBooks': True,
                'fetchMyTrades': True,
                'fetchTickers': True,
                'withdraw': True,
            },
            'urls': {
                'logo': 'https://user-images.githubusercontent.com/1294454/27766491-1b0ea956-5eda-11e7-9225-40d67b481b8d.jpg',
                'api': 'https://api.exmo.com',
                'www': 'https://exmo.me',
                'doc': [
                    'https://exmo.me/en/api_doc',
                    'https://github.com/exmo-dev/exmo_api_lib/tree/master/nodejs',
                ],
                'fees': 'https://exmo.com/en/docs/fees',
            },
            'api': {
                'public': {
                    'get': [
                        'currency',
                        'order_book',
                        'pair_settings',
                        'ticker',
                        'trades',
                    ],
                },
                'private': {
                    'post': [
                        'user_info',
                        'order_create',
                        'order_cancel',
                        'user_open_orders',
                        'user_trades',
                        'user_cancelled_orders',
                        'order_trades',
                        'required_amount',
                        'deposit_address',
                        'withdraw_crypt',
                        'withdraw_get_txid',
                        'excode_create',
                        'excode_load',
                        'wallet_history',
                    ],
                },
            },
            'fees': {
                'trading': {
                    'maker': 0.2 / 100,
                    'taker': 0.2 / 100,
                },
                'funding': {
                    'withdraw': {
                        'BTC': 0.001,
                        'LTC': 0.01,
                        'DOGE': 1,
                        'DASH': 0.01,
                        'ETH': 0.01,
                        'WAVES': 0.001,
                        'ZEC': 0.001,
                        'USDT': 25,
                        'XMR': 0.05,
                        'XRP': 0.02,
                        'KICK': 350,
                        'ETC': 0.01,
                        'BCH': 0.001,
                    },
                    'deposit': {
                        'USDT': 15,
                        'KICK': 50,
                    },
                },
            },
            'exceptions': {
                # '803': InvalidOrder,  # "Count could not be less than 0.001."(selling below minAmount)
                # '804': InvalidOrder,  # "Count could not be more than 10000."(buying above maxAmount)
                # '805': InvalidOrder,  # "price could not be less than X."(minPrice violation on buy & sell)
                # '806': InvalidOrder,  # "price could not be more than X."(maxPrice violation on buy & sell)
                # '807': InvalidOrder,  # "cost could not be less than X."(minCost violation on buy & sell)
                # '831': InsufficientFunds,  # "Not enougth X to create buy order."(buying with balance.quote < order.cost)
                # '832': InsufficientFunds,  # "Not enougth X to create sell order."(selling with balance.base < order.amount)
                '40005': AuthenticationError,  # Authorization error, incorrect signature
                '40015': ExchangeError,  # API function do not exist
                '40017': AuthenticationError,  # Wrong API Key
                '50052': InsufficientFunds,
                '50173': OrderNotFound,  # "Order with id X was not found."(cancelling non-existent, closed and cancelled order)
                '50319': InvalidOrder,  # Price by order is less than permissible minimum for self pair
                '50321': InvalidOrder,  # Price by order is more than permissible maximum for self pair
            },
        })

    def fetch_markets(self):
        markets = self.publicGetPairSettings()
        keys = list(markets.keys())
        result = []
        for p in range(0, len(keys)):
            id = keys[p]
            market = markets[id]
            symbol = id.replace('_', '/')
            base, quote = symbol.split('/')
            result.append({
                'id': id,
                'symbol': symbol,
                'base': base,
                'quote': quote,
                'limits': {
                    'amount': {
                        'min': self.safe_float(market, 'min_quantity'),
                        'max': self.safe_float(market, 'max_quantity'),
                    },
                    'price': {
                        'min': self.safe_float(market, 'min_price'),
                        'max': self.safe_float(market, 'max_price'),
                    },
                    'cost': {
                        'min': self.safe_float(market, 'min_amount'),
                        'max': self.safe_float(market, 'max_amount'),
                    },
                },
                'precision': {
                    'amount': 8,
                    'price': 8,
                },
                'info': market,
            })
        return result

    def fetch_balance(self, params={}):
        self.load_markets()
        response = self.privatePostUserInfo()
        result = {'info': response}
        currencies = list(self.currencies.keys())
        for i in range(0, len(currencies)):
            currency = currencies[i]
            account = self.account()
            if currency in response['balances']:
                account['free'] = float(response['balances'][currency])
            if currency in response['reserved']:
                account['used'] = float(response['reserved'][currency])
            account['total'] = self.sum(account['free'], account['used'])
            result[currency] = account
        return self.parse_balance(result)

    def fetch_order_book(self, symbol, limit=None, params={}):
        self.load_markets()
        market = self.market(symbol)
        request = self.extend({
            'pair': market['id'],
        }, params)
        if limit is not None:
            request['limit'] = limit
        response = self.publicGetOrderBook(request)
        result = response[market['id']]
        orderbook = self.parse_order_book(result, None, 'bid', 'ask')
        return self.extend(orderbook, {
            'bids': self.sort_by(orderbook['bids'], 0, True),
            'asks': self.sort_by(orderbook['asks'], 0),
        })

    def fetch_order_books(self, symbols=None, params={}):
        self.load_markets()
        ids = None
        if not symbols:
            ids = ','.join(self.ids)
            # max URL length is 2083 symbols, including http schema, hostname, tld, etc...
            if len(ids) > 2048:
                numIds = len(self.ids)
                raise ExchangeError(self.id + ' has ' + str(numIds) + ' symbols exceeding max URL length, you are required to specify a list of symbols in the first argument to fetchOrderBooks')
        else:
            ids = self.market_ids(symbols)
            ids = ','.join(ids)
        response = self.publicGetOrderBook(self.extend({
            'pair': ids,
        }, params))
        result = {}
        ids = list(response.keys())
        for i in range(0, len(ids)):
            id = ids[i]
            symbol = self.find_symbol(id)
            result[symbol] = self.parse_order_book(response[id], None, 'bid', 'ask')
        return result

    def parse_ticker(self, ticker, market=None):
        timestamp = ticker['updated'] * 1000
        symbol = None
        if market:
            symbol = market['symbol']
        last = float(ticker['last_trade'])
        return {
            'symbol': symbol,
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
            'high': float(ticker['high']),
            'low': float(ticker['low']),
            'bid': float(ticker['buy_price']),
            'ask': float(ticker['sell_price']),
            'vwap': None,
            'open': None,
            'close': last,
            'last': last,
            'previousClose': None,
            'change': None,
            'percentage': None,
            'average': float(ticker['avg']),
            'baseVolume': float(ticker['vol']),
            'quoteVolume': float(ticker['vol_curr']),
            'info': ticker,
        }

    def fetch_tickers(self, symbols=None, params={}):
        self.load_markets()
        response = self.publicGetTicker(params)
        result = {}
        ids = list(response.keys())
        for i in range(0, len(ids)):
            id = ids[i]
            market = self.markets_by_id[id]
            symbol = market['symbol']
            ticker = response[id]
            result[symbol] = self.parse_ticker(ticker, market)
        return result

    def fetch_ticker(self, symbol, params={}):
        self.load_markets()
        response = self.publicGetTicker(params)
        market = self.market(symbol)
        return self.parse_ticker(response[market['id']], market)

    def parse_trade(self, trade, market):
        timestamp = trade['date'] * 1000
        return {
            'id': str(trade['trade_id']),
            'info': trade,
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
            'symbol': market['symbol'],
            'order': self.safe_string(trade, 'order_id'),
            'type': None,
            'side': trade['type'],
            'price': float(trade['price']),
            'amount': float(trade['quantity']),
            'cost': self.safe_float(trade, 'amount'),
        }

    def fetch_trades(self, symbol, since=None, limit=None, params={}):
        self.load_markets()
        market = self.market(symbol)
        response = self.publicGetTrades(self.extend({
            'pair': market['id'],
        }, params))
        return self.parse_trades(response[market['id']], market, since, limit)

    def fetch_my_trades(self, symbol=None, since=None, limit=None, params={}):
        self.load_markets()
        request = {}
        market = None
        if symbol is not None:
            market = self.market(symbol)
            request['pair'] = market['id']
        response = self.privatePostUserTrades(self.extend(request, params))
        if market is not None:
            response = response[market['id']]
        return self.parse_trades(response, market, since, limit)

    def create_order(self, symbol, type, side, amount, price=None, params={}):
        self.load_markets()
        prefix = 'market_' if (type == 'market') else ''
        market = self.market(symbol)
        request = {
            'pair': market['id'],
            'quantity': self.amount_to_string(symbol, amount),
            'price': self.price_to_precision(symbol, price),
            'type': prefix + side,
        }
        response = self.privatePostOrderCreate(self.extend(request, params))
        id = self.safe_string(response, 'order_id')
        timestamp = self.milliseconds()
        price = float(price)
        amount = float(amount)
        status = 'open'
        order = {
            'id': id,
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
            'status': status,
            'symbol': symbol,
            'type': type,
            'side': side,
            'price': price,
            'cost': price * amount,
            'amount': amount,
            'remaining': amount,
            'filled': 0.0,
            'fee': None,
            'trades': None,
        }
        self.orders[id] = order
        return self.extend({'info': response}, order)

    def cancel_order(self, id, symbol=None, params={}):
        self.load_markets()
        response = self.privatePostOrderCancel({'order_id': id})
        if id in self.orders:
            self.orders[id]['status'] = 'canceled'
        return response

    def fetch_order(self, id, symbol=None, params={}):
        self.load_markets()
        self.fetch_orders(symbol, None, None, params)
        if id in self.orders:
            return self.orders[id]
        raise OrderNotFound(self.id + ' order id ' + str(id) + ' is not in "open" state and not found in cache')

    def fetch_order_trades(self, id, symbol=None, since=None, limit=None, params={}):
        order = self.fetch_order(id, symbol, params)
        # todo: filter by symbol, since and limit
        return order['trades']

    def update_cached_orders(self, openOrders, symbol):
        # update local cache with open orders
        for j in range(0, len(openOrders)):
            id = openOrders[j]['id']
            self.orders[id] = openOrders[j]
        openOrdersIndexedById = self.index_by(openOrders, 'id')
        cachedOrderIds = list(self.orders.keys())
        result = []
        for k in range(0, len(cachedOrderIds)):
            # match each cached order to an order in the open orders array
            # possible reasons why a cached order may be missing in the open orders array:
            # - order was closed or canceled -> update cache
            # - symbol mismatch(e.g. cached BTC/USDT, fetched ETH/USDT) -> skip
            id = cachedOrderIds[k]
            order = self.orders[id]
            result.append(order)
            if not(id in list(openOrdersIndexedById.keys())):
                # cached order is not in open orders array
                # if we fetched orders by symbol and it doesn't match the cached order -> won't update the cached order
                if symbol is not None and symbol != order['symbol']:
                    continue
                # order is cached but not present in the list of open orders -> mark the cached order as closed
                if order['status'] == 'open':
                    order = self.extend(order, {
                        'status': 'closed',  # likewise it might have been canceled externally(unnoticed by "us")
                        'cost': None,
                        'filled': order['amount'],
                        'remaining': 0.0,
                    })
                    if order['cost'] is None:
                        if order['filled'] is not None:
                            order['cost'] = order['filled'] * order['price']
                    self.orders[id] = order
        return result

    def fetch_orders(self, symbol=None, since=None, limit=None, params={}):
        self.load_markets()
        response = self.privatePostUserOpenOrders(params)
        marketIds = list(response.keys())
        orders = []
        for i in range(0, len(marketIds)):
            marketId = marketIds[i]
            market = None
            if marketId in self.markets_by_id:
                market = self.markets_by_id[marketId]
            parsedOrders = self.parse_orders(response[marketId], market)
            orders = self.array_concat(orders, parsedOrders)
        self.update_cached_orders(orders)
        return self.filter_by_symbol_since_limit(self.orders, symbol, since, limit)

    def fetch_open_orders(self, symbol=None, since=None, limit=None, params={}):
        self.fetch_orders(symbol, since, limit, params)
        orders = self.filter_by(self.orders, 'status', 'open')
        return self.filter_by_symbol_since_limit(orders, symbol, since, limit)

    def fetch_closed_orders(self, symbol=None, since=None, limit=None, params={}):
        self.fetch_orders(symbol, since, limit, params)
        orders = self.filter_by(self.orders, 'status', 'closed')
        return self.filter_by_symbol_since_limit(orders, symbol, since, limit)

    def parse_order(self, order, market=None):
        id = self.safe_string(order, 'order_id')
        timestamp = self.safe_integer(order, 'created')
        if timestamp is not None:
            timestamp *= 1000
        iso8601 = None
        symbol = None
        side = self.safe_string(order, 'type')
        if market is None:
            marketId = None
            if 'pair' in order:
                marketId = order['pair']
            elif ('in_currency' in list(order.keys())) and('out_currency' in list(order.keys())):
                if side == 'buy':
                    marketId = order['in_currency'] + '_' + order['out_currency']
                else:
                    marketId = order['out_currency'] + '_' + order['in_currency']
            if (marketId is not None) and(marketId in list(self.markets_by_id.keys())):
                market = self.markets_by_id[marketId]
        amount = self.safe_float(order, 'quantity')
        if amount is None:
            amountField = 'in_amount' if (side == 'buy') else 'out_amount'
            amount = self.safe_float(order, amountField)
        price = self.safe_float(order, 'price')
        cost = self.safe_float(order, 'amount')
        filled = 0.0
        trades = []
        transactions = self.safe_value(order, 'trades')
        feeCost = None
        if transactions is not None:
            if isinstance(transactions, list):
                for i in range(0, len(transactions)):
                    trade = self.parse_trade(transactions[i], market)
                    if id is None:
                        id = trade['order']
                    if timestamp is None:
                        timestamp = trade['timestamp']
                    if timestamp > trade['timestamp']:
                        timestamp = trade['timestamp']
                    filled += trade['amount']
                    if feeCost is None:
                        feeCost = 0.0
                    # feeCost += trade['fee']['cost']
                    if cost is None:
                        cost = 0.0
                    cost += trade['cost']
                    trades.append(trade)
        if timestamp is not None:
            iso8601 = self.iso8601(timestamp)
        remaining = None
        if amount is not None:
            remaining = amount - filled
        status = self.safe_string(order, 'status')  # in case we need to redefine it for canceled orders
        if filled >= amount:
            status = 'closed'
        else:
            status = 'open'
        if market is None:
            market = self.get_market_from_trades(trades)
        feeCurrency = None
        if market is not None:
            symbol = market['symbol']
            feeCurrency = market['quote']
        if cost is None:
            if price is not None:
                cost = price * filled
        elif price is None:
            if filled > 0:
                price = cost / filled
        fee = {
            'cost': feeCost,
            'currency': feeCurrency,
        }
        return {
            'id': id,
            'datetime': iso8601,
            'timestamp': timestamp,
            'status': status,
            'symbol': symbol,
            'type': 'limit',
            'side': side,
            'price': price,
            'cost': cost,
            'amount': amount,
            'filled': filled,
            'remaining': remaining,
            'trades': trades,
            'fee': fee,
            'info': order,
        }

    def get_market_from_trades(self, trades):
        tradesBySymbol = self.index_by(trades, 'pair')
        symbols = list(tradesBySymbol.keys())
        numSymbols = len(symbols)
        if numSymbols == 1:
            return self.markets[symbols[0]]
        return None

    def calculate_fee(self, symbol, type, side, amount, price, takerOrMaker='taker', params={}):
        market = self.markets[symbol]
        rate = market[takerOrMaker]
        cost = float(self.cost_to_precision(symbol, amount * rate))
        key = 'quote'
        if side == 'sell':
            cost *= price
        else:
            key = 'base'
        return {
            'type': takerOrMaker,
            'currency': market[key],
            'rate': rate,
            'cost': float(self.fee_to_precision(symbol, cost)),
        }

    def withdraw(self, currency, amount, address, tag=None, params={}):
        self.load_markets()
        request = {
            'amount': amount,
            'currency': currency,
            'address': address,
        }
        if tag is not None:
            request['invoice'] = tag
        result = self.privatePostWithdrawCrypt(self.extend(request, params))
        return {
            'info': result,
            'id': result['task_id'],
        }

    def sign(self, path, api='public', method='GET', params={}, headers=None, body=None):
        url = self.urls['api'] + '/' + self.version + '/' + path
        if api == 'public':
            if params:
                url += '?' + self.urlencode(params)
        else:
            self.check_required_credentials()
            nonce = self.nonce()
            body = self.urlencode(self.extend({'nonce': nonce}, params))
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded',
                'Key': self.apiKey,
                'Sign': self.hmac(self.encode(body), self.encode(self.secret), hashlib.sha512),
            }
        return {'url': url, 'method': method, 'body': body, 'headers': headers}

    def nonce(self):
        return self.milliseconds()

    def handle_errors(self, httpCode, reason, url, method, headers, body):
        if not isinstance(body, basestring):
            return  # fallback to default error handler
        if len(body) < 2:
            return  # fallback to default error handler
        if (body[0] == '{') or (body[0] == '['):
            response = json.loads(body)
            if 'result' in response:
                #
                #     {"result":false,"error":"Error 50052: Insufficient funds"}
                #
                success = self.safe_value(response, 'result', False)
                if isinstance(success, basestring):
                    if (success == 'true') or (success == '1'):
                        success = True
                    else:
                        success = False
                if not success:
                    code = None
                    message = self.safe_string(response, 'error')
                    errorParts = message.split(':')
                    numParts = len(errorParts)
                    if numParts > 1:
                        errorSubParts = errorParts[0].split(' ')
                        numSubParts = len(errorSubParts)
                        if numSubParts > 1:
                            code = errorSubParts[1]
                    feedback = self.id + ' ' + self.json(response)
                    exceptions = self.exceptions
                    if code in exceptions:
                        raise exceptions[code](feedback)
                    else:
                        raise ExchangeError(self.id + ' ' + self.json(response))
