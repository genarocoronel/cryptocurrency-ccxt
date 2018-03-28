# -*- coding: utf-8 -*-

# PLEASE DO NOT EDIT THIS FILE, IT IS GENERATED AND WILL BE OVERWRITTEN:
# https://github.com/ccxt/ccxt/blob/master/CONTRIBUTING.md#how-to-contribute-code

from ccxt.base.exchange import Exchange
from ccxt.base.errors import ExchangeError
from ccxt.base.errors import AuthenticationError
from ccxt.base.errors import InsufficientFunds
from ccxt.base.errors import InvalidOrder
from ccxt.base.errors import OrderNotFound


class coinex (Exchange):

    def describe(self):
        return self.deep_extend(super(coinex, self).describe(), {
            'id': 'coinex',
            'name': 'CoinEx',
            'version': 'v1',
            'countries': 'CN',
            'rateLimit': 1000,
            'has': {
                'fetchTickers': True,
                'fetchOHLCV': True,
                'fetchOpenOrders': True,
                'fetchClosedOrders': True,
                'fetchMyTrades': True,
            },
            'timeframes': {
                '1m': '1min',
                '3m': '3min',
                '5m': '5min',
                '15m': '15min',
                '30m': '30min',
                '1h': '1hour',
                '2h': '2hour',
                '4h': '4hour',
                '6h': '6hour',
                '12h': '12hour',
                '1d': '1day',
                '3d': '3day',
                '1w': '1week',
            },
            'urls': {
                'logo': 'https://user-images.githubusercontent.com/1294454/38046312-0b450aac-32c8-11e8-99ab-bc6b136b6cc7.jpg',
                'api': 'https://api.coinex.com/v1',
                'www': 'https://www.coinex.com',
                'doc': 'https://github.com/coinexcom/coinex_exchange_api/wiki',
                'fees': 'https://www.coinex.com/fees',
            },
            'api': {
                'public': {
                    'get': [
                        'market/list',
                        'market/ticker',
                        'market/ticker/all',
                        'market/depth',
                        'market/deals',
                        'market/kline',
                    ],
                },
                'private': {
                    'get': [
                        'balance',
                        'order',
                        'order/pending',
                        'order/finished',
                        'order/finished/{id}',
                        'order/user/deals',
                    ],
                    'post': [
                        'order/limit',
                        'order/market',
                    ],
                    'delete': [
                        'order/pending',
                    ],
                },
            },
            'fees': {
                'trading': {
                    'maker': 0.0,
                    'taker': 0.001,
                },
                'funding': {
                    'withdraw': {
                        'BCH': 0.0,
                        'BTC': 0.001,
                        'LTC': 0.001,
                        'ETH': 0.001,
                        'ZEC': 0.0001,
                        'DASH': 0.0001,
                    },
                },
            },
            'limits': {
                'amount': {
                    'min': 0.001,
                    'max': None,
                },
            },
            'precision': {
                'amount': 8,
                'price': 8,
            },
        })

    def fetch_markets(self):
        response = self.publicGetMarketList()
        markets = response['data']
        result = []
        for i in range(0, len(markets)):
            id = markets[i]
            base = id[-3:]
            quote = id[0:-3]
            base = self.common_currency_code(base)
            quote = self.common_currency_code(quote)
            symbol = base + '/' + quote
            result.append({
                'id': id,
                'symbol': symbol,
                'base': base,
                'quote': quote,
                'active': True,
                'lot': self.limits['amount']['min'],
                'info': id,
            })
        return result

    def parse_ticker(self, ticker, market=None):
        timestamp = ticker['date']
        symbol = market['symbol']
        ticker = ticker['ticker']
        return {
            'symbol': symbol,
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
            'high': float(ticker['high']),
            'low': float(ticker['low']),
            'bid': float(ticker['buy']),
            'ask': float(ticker['sell']),
            'vwap': None,
            'open': None,
            'close': None,
            'first': None,
            'last': float(ticker['last']),
            'change': None,
            'percentage': None,
            'average': None,
            'baseVolume': None,
            'quoteVolume': float(ticker['vol']),
            'info': ticker,
        }

    def fetch_ticker(self, symbol, params={}):
        self.load_markets()
        market = self.market(symbol)
        response = self.publicGetMarketTicker(self.extend({
            'market': market['id'],
        }, params))
        return self.parse_ticker(response['data'], market)

    def fetch_tickers(self, symbols=None, params={}):
        self.load_markets()
        response = self.publicGetMarketTickerAll(params)
        data = response['data']
        timestamp = data['date']
        tickers = data['ticker']
        ids = list(tickers.keys())
        result = {}
        for i in range(0, len(ids)):
            id = ids[i]
            market = self.markets_by_id[id]
            symbol = market['symbol']
            ticker = {
                'date': timestamp,
                'ticker': tickers[id],
            }
            result[symbol] = self.parse_ticker(ticker, market)
        return result

    def fetch_order_book(self, symbol, params={}):
        self.load_markets()
        response = self.publicGetMarketDepth(self.extend({
            'market': self.market_id(symbol),
            'merge': '0.00000001',
        }, params))
        return self.parse_order_book(response['data'])

    def parse_trade(self, trade, market=None):
        timestamp = self.safe_integer(trade, 'create_time')
        tradeId = self.safe_string(trade, 'id')
        orderId = self.safe_string(trade, 'id')
        if not timestamp:
            timestamp = trade['date']
            orderId = None
        else:
            tradeId = None
        timestamp *= 1000
        price = float(trade['price'])
        amount = float(trade['amount'])
        symbol = market['symbol']
        cost = self.safe_float(trade, 'deal_money')
        if not cost:
            cost = float(self.cost_to_precision(symbol, price * amount))
        fee = self.safe_float(trade, 'fee')
        return {
            'info': trade,
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
            'symbol': symbol,
            'id': tradeId,
            'order': orderId,
            'type': 'limit',
            'side': trade['type'],
            'price': price,
            'amount': amount,
            'cost': cost,
            'fee': fee,
        }

    def fetch_trades(self, symbol, since=None, limit=None, params={}):
        self.load_markets()
        market = self.market(symbol)
        response = self.publicGetMarketDeals(self.extend({
            'market': market['id'],
        }, params))
        return self.parse_trades(response['data'], market, since, limit)

    def parse_ohlcv(self, ohlcv, market=None, timeframe='5m', since=None, limit=None):
        return [
            ohlcv[0],
            float(ohlcv[1]),
            float(ohlcv[3]),
            float(ohlcv[4]),
            float(ohlcv[2]),
            float(ohlcv[5]),
        ]

    def fetch_ohlcv(self, symbol, timeframe='5m', since=None, limit=None, params={}):
        self.load_markets()
        market = self.market(symbol)
        response = self.publicGetMarketKline(self.extend({
            'market': market['id'],
            'type': self.timeframes[timeframe],
        }, params))
        return self.parse_ohlcvs(response['data'], market, timeframe, since, limit)

    def fetch_balance(self, params={}):
        self.load_markets()
        response = self.privateGetBalance(params)
        result = {'info': response}
        balances = response['data']
        currencies = list(balances.keys())
        for i in range(0, len(currencies)):
            id = currencies[i]
            balance = balances[id]
            currency = self.common_currency_code(id)
            account = {
                'free': float(balance['available']),
                'used': float(balance['frozen']),
                'total': 0.0,
            }
            account['total'] = self.sum(account['free'], account['used'])
            result[currency] = account
        return self.parse_balance(result)

    def parse_order(self, order, market=None):
        # TODO: check if it's actually milliseconds, since examples were in seconds
        timestamp = self.safe_integer(order, 'create_time') * 1000
        price = float(order['price'])
        cost = self.safe_float(order, 'deal_money')
        amount = self.safe_float(order, 'amount')
        filled = self.safe_float(order, 'deal_amount')
        symbol = market['symbol']
        remaining = self.amount_to_precision(symbol, amount - filled)
        status = order['status']
        if status == 'done':
            status = 'closed'
        else:
            # not_deal
            # part_deal
            status = 'open'
        return {
            'id': self.safe_string(order, 'id'),
            'datetime': self.iso8601(timestamp),
            'timestamp': timestamp,
            'status': status,
            'symbol': symbol,
            'type': order['order_type'],
            'side': order['type'],
            'price': price,
            'cost': cost,
            'amount': amount,
            'filled': filled,
            'remaining': remaining,
            'trades': None,
            'fee': {
                'currency': market['quote'],
                'cost': float(order['deal_fee']),
            },
            'info': order,
        }

    def create_order(self, symbol, type, side, amount, price=None, params={}):
        self.load_markets()
        method = 'privatePostOrder' + self.capitalize(type)
        market = self.market(symbol)
        amount = float(amount)
        request = {
            'market': market['id'],
            'amount': self.amount_to_precision(symbol, amount),
            'type': side,
        }
        if type == 'limit':
            price = float(price)
            request['price'] = self.price_to_precision(symbol, price)
        response = getattr(self, method)(self.extend(request, params))
        order = self.parse_order(response['data'], market)
        id = order['id']
        self.orders[id] = order
        return order

    def cancel_order(self, id, symbol=None, params={}):
        self.load_markets()
        market = self.market(symbol)
        response = self.privateDeleteOrderPending(self.extend({
            'id': id,
            'market': market['id'],
        }, params))
        return self.parse_order(response['data'], market)

    def fetch_order(self, id, symbol=None, params={}):
        self.load_markets()
        market = self.market(symbol)
        response = self.privateGetOrder(self.extend({
            'id': id,
            'market': market['id'],
        }, params))
        return self.parse_order(response['data'], market)

    def fetch_open_orders(self, symbol=None, since=None, limit=None, params={}):
        self.load_markets()
        market = self.market(symbol)
        request = {
            'market': market['id'],
        }
        if limit:
            request['limit'] = limit
        response = self.privateGetOrderPending(self.extend(request, params))
        return self.parse_orders(response['data']['data'], market)

    def fetch_closed_orders(self, symbol=None, since=None, limit=None, params={}):
        self.load_markets()
        market = self.market(symbol)
        request = {
            'market': market['id'],
        }
        if limit:
            request['limit'] = limit
        response = self.privateGetOrderFinished(self.extend(request, params))
        return self.parse_orders(response['data']['data'], market)

    def fetch_my_trades(self, symbol=None, since=None, limit=None, params={}):
        self.load_markets()
        market = self.market(symbol)
        response = self.privateGetOrderUserDeals(self.extend({
            'market': market['id'],
            'page': 1,
            'limit': 100,
        }, params))
        return self.parse_trades(response['data']['data'], market, since, limit)

    def nonce(self):
        return self.milliseconds()

    def sign(self, path, api='public', method='GET', params={}, headers=None, body=None):
        url = self.urls['api'] + '/' + self.version + '/' + self.implode_params(path, params)
        query = self.omit(params, self.extract_params(path))
        if api == 'public':
            if query:
                url += '?' + self.urlencode(query)
        else:
            self.check_required_credentials()
            nonce = self.nonce()
            query = self.extend({
                'access_id': self.apiKey,
                'tonce': str(nonce),
            }, query)
            query = self.keysort(query)
            urlencoded = self.urlencode(query)
            signature = self.hash(self.encode(urlencoded + '&secret_key=' + self.secret))
            headers = {
                'Authorization': signature.upper(),
                'Content-Type': 'application/json',
            }
            if method == 'GET':
                url += '?' + urlencoded
            else:
                body = self.json(query)
        return {'url': url, 'method': method, 'body': body, 'headers': headers}

    def request(self, path, api='public', method='GET', params={}, headers=None, body=None):
        response = self.fetch2(path, api, method, params, headers, body)
        code = self.safe_string(response, 'code')
        data = self.safe_value(response, 'data')
        if code != '0' or not data:
            responseCodes = {
                '24': AuthenticationError,
                '25': AuthenticationError,
                '107': InsufficientFunds,
                '600': OrderNotFound,
                '601': InvalidOrder,
                '602': InvalidOrder,
                '606': InvalidOrder,
            }
            ErrorClass = self.safe_value(responseCodes, code, ExchangeError)
            raise ErrorClass(response['message'])
        return response
