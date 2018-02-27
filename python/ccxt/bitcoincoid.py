# -*- coding: utf-8 -*-

# PLEASE DO NOT EDIT THIS FILE, IT IS GENERATED AND WILL BE OVERWRITTEN:
# https://github.com/ccxt/ccxt/blob/master/CONTRIBUTING.md#how-to-contribute-code

from ccxt.base.exchange import Exchange
import hashlib
import json
from ccxt.base.errors import ExchangeError
from ccxt.base.errors import AuthenticationError
from ccxt.base.errors import InsufficientFunds
from ccxt.base.errors import InvalidOrder
from ccxt.base.errors import OrderNotFound


class bitcoincoid (Exchange):

    def describe(self):
        return self.deep_extend(super(bitcoincoid, self).describe(), {
            'id': 'bitcoincoid',
            'name': 'Bitcoin.co.id',
            'countries': 'ID',  # Indonesia
            'has': {
                'CORS': False,
                'createMarketOrder': False,
                'fetchTickers': False,
                'fetchOrder': True,
                'fetchOrders': False,
                'fetchClosedOrders': True,
                'fetchOpenOrders': True,
                'fetchMyTrades': False,
                'fetchCurrencies': False,
                'withdraw': False,
            },
            'version': '1.7',  # as of 6 November 2017
            'urls': {
                'logo': 'https://user-images.githubusercontent.com/1294454/27766138-043c7786-5ecf-11e7-882b-809c14f38b53.jpg',
                'api': {
                    'public': 'https://vip.bitcoin.co.id/api',
                    'private': 'https://vip.bitcoin.co.id/tapi',
                },
                'www': 'https://www.bitcoin.co.id',
                'doc': [
                    'https://vip.bitcoin.co.id/downloads/BITCOINCOID-API-DOCUMENTATION.pdf',
                ],
            },
            'api': {
                'public': {
                    'get': [
                        '{pair}/ticker',
                        '{pair}/trades',
                        '{pair}/depth',
                    ],
                },
                'private': {
                    'post': [
                        'getInfo',
                        'transHistory',
                        'trade',
                        'tradeHistory',
                        'getOrder',
                        'openOrders',
                        'cancelOrder',
                        'orderHistory',
                    ],
                },
            },
            'markets': {
                'BTC/IDR': {'id': 'btc_idr', 'symbol': 'BTC/IDR', 'base': 'BTC', 'quote': 'IDR', 'baseId': 'btc', 'quoteId': 'idr', 'limits': {'amount': {'min': 0.0001, 'max': None}}},
                'BCH/IDR': {'id': 'bch_idr', 'symbol': 'BCH/IDR', 'base': 'BCH', 'quote': 'IDR', 'baseId': 'bch', 'quoteId': 'idr', 'limits': {'amount': {'min': 0.001, 'max': None}}},
                'BTG/IDR': {'id': 'btg_idr', 'symbol': 'BTG/IDR', 'base': 'BTG', 'quote': 'IDR', 'baseId': 'btg', 'quoteId': 'idr', 'limits': {'amount': {'min': 0.01, 'max': None}}},
                'ETH/IDR': {'id': 'eth_idr', 'symbol': 'ETH/IDR', 'base': 'ETH', 'quote': 'IDR', 'baseId': 'eth', 'quoteId': 'idr', 'limits': {'amount': {'min': 0.01, 'max': None}}},
                'ETC/IDR': {'id': 'etc_idr', 'symbol': 'ETC/IDR', 'base': 'ETC', 'quote': 'IDR', 'baseId': 'etc', 'quoteId': 'idr', 'limits': {'amount': {'min': 0.1, 'max': None}}},
                'IGNIS/IDR': {'id': 'ignis_idr', 'symbol': 'IGNIS/IDR', 'base': 'IGNIS', 'quote': 'IDR', 'baseId': 'ignis', 'quoteId': 'idr', 'limits': {'amount': {'min': 1, 'max': None}}},
                'LTC/IDR': {'id': 'ltc_idr', 'symbol': 'LTC/IDR', 'base': 'LTC', 'quote': 'IDR', 'baseId': 'ltc', 'quoteId': 'idr', 'limits': {'amount': {'min': 0.01, 'max': None}}},
                'NXT/IDR': {'id': 'nxt_idr', 'symbol': 'NXT/IDR', 'base': 'NXT', 'quote': 'IDR', 'baseId': 'nxt', 'quoteId': 'idr', 'limits': {'amount': {'min': 5, 'max': None}}},
                'WAVES/IDR': {'id': 'waves_idr', 'symbol': 'WAVES/IDR', 'base': 'WAVES', 'quote': 'IDR', 'baseId': 'waves', 'quoteId': 'idr', 'limits': {'amount': {'min': 0.1, 'max': None}}},
                'XRP/IDR': {'id': 'xrp_idr', 'symbol': 'XRP/IDR', 'base': 'XRP', 'quote': 'IDR', 'baseId': 'xrp', 'quoteId': 'idr', 'limits': {'amount': {'min': 10, 'max': None}}},
                'XZC/IDR': {'id': 'xzc_idr', 'symbol': 'XZC/IDR', 'base': 'XZC', 'quote': 'IDR', 'baseId': 'xzc', 'quoteId': 'idr', 'limits': {'amount': {'min': 0.1, 'max': None}}},
                'XLM/IDR': {'id': 'str_idr', 'symbol': 'XLM/IDR', 'base': 'XLM', 'quote': 'IDR', 'baseId': 'str', 'quoteId': 'idr', 'limits': {'amount': {'min': 20, 'max': None}}},
                'BTS/BTC': {'id': 'bts_btc', 'symbol': 'BTS/BTC', 'base': 'BTS', 'quote': 'BTC', 'baseId': 'bts', 'quoteId': 'btc', 'limits': {'amount': {'min': 0.01, 'max': None}}},
                'DASH/BTC': {'id': 'drk_btc', 'symbol': 'DASH/BTC', 'base': 'DASH', 'quote': 'BTC', 'baseId': 'drk', 'quoteId': 'btc', 'limits': {'amount': {'min': 0.01, 'max': None}}},
                'DOGE/BTC': {'id': 'doge_btc', 'symbol': 'DOGE/BTC', 'base': 'DOGE', 'quote': 'BTC', 'baseId': 'doge', 'quoteId': 'btc', 'limits': {'amount': {'min': 1, 'max': None}}},
                'ETH/BTC': {'id': 'eth_btc', 'symbol': 'ETH/BTC', 'base': 'ETH', 'quote': 'BTC', 'baseId': 'eth', 'quoteId': 'btc', 'limits': {'amount': {'min': 0.001, 'max': None}}},
                'LTC/BTC': {'id': 'ltc_btc', 'symbol': 'LTC/BTC', 'base': 'LTC', 'quote': 'BTC', 'baseId': 'ltc', 'quoteId': 'btc', 'limits': {'amount': {'min': 0.01, 'max': None}}},
                'NXT/BTC': {'id': 'nxt_btc', 'symbol': 'NXT/BTC', 'base': 'NXT', 'quote': 'BTC', 'baseId': 'nxt', 'quoteId': 'btc', 'limits': {'amount': {'min': 0.01, 'max': None}}},
                'XLM/BTC': {'id': 'str_btc', 'symbol': 'XLM/BTC', 'base': 'XLM', 'quote': 'BTC', 'baseId': 'str', 'quoteId': 'btc', 'limits': {'amount': {'min': 0.01, 'max': None}}},
                'XEM/BTC': {'id': 'nem_btc', 'symbol': 'XEM/BTC', 'base': 'XEM', 'quote': 'BTC', 'baseId': 'nem', 'quoteId': 'btc', 'limits': {'amount': {'min': 1, 'max': None}}},
                'XRP/BTC': {'id': 'xrp_btc', 'symbol': 'XRP/BTC', 'base': 'XRP', 'quote': 'BTC', 'baseId': 'xrp', 'quoteId': 'btc', 'limits': {'amount': {'min': 0.01, 'max': None}}},
            },
            'fees': {
                'trading': {
                    'tierBased': False,
                    'percentage': True,
                    'maker': 0,
                    'taker': 0.3,
                },
            },
        })

    def fetch_balance(self, params={}):
        self.load_markets()
        response = self.privatePostGetInfo()
        balance = response['return']
        result = {'info': balance}
        codes = list(self.currencies.keys())
        for i in range(0, len(codes)):
            code = codes[i]
            currency = self.currencies[code]
            lowercase = currency['id']
            account = self.account()
            account['free'] = self.safe_float(balance['balance'], lowercase, 0.0)
            account['used'] = self.safe_float(balance['balance_hold'], lowercase, 0.0)
            account['total'] = self.sum(account['free'], account['used'])
            result[code] = account
        return self.parse_balance(result)

    def fetch_order_book(self, symbol, limit=None, params={}):
        self.load_markets()
        orderbook = self.publicGetPairDepth(self.extend({
            'pair': self.market_id(symbol),
        }, params))
        return self.parse_order_book(orderbook, None, 'buy', 'sell')

    def fetch_ticker(self, symbol, params={}):
        self.load_markets()
        market = self.market(symbol)
        response = self.publicGetPairTicker(self.extend({
            'pair': market['id'],
        }, params))
        ticker = response['ticker']
        timestamp = float(ticker['server_time']) * 1000
        baseVolume = 'vol_' + market['baseId'].lower()
        quoteVolume = 'vol_' + market['quoteId'].lower()
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
            'baseVolume': float(ticker[baseVolume]),
            'quoteVolume': float(ticker[quoteVolume]),
            'info': ticker,
        }

    def parse_trade(self, trade, market):
        timestamp = int(trade['date']) * 1000
        return {
            'id': trade['tid'],
            'info': trade,
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
            'symbol': market['symbol'],
            'type': None,
            'side': trade['type'],
            'price': float(trade['price']),
            'amount': float(trade['amount']),
        }

    def fetch_trades(self, symbol, since=None, limit=None, params={}):
        self.load_markets()
        market = self.market(symbol)
        response = self.publicGetPairTrades(self.extend({
            'pair': market['id'],
        }, params))
        return self.parse_trades(response, market, since, limit)

    def parse_order(self, order, market=None):
        side = None
        if 'type' in order:
            side = order['type']
        status = self.safe_string(order, 'status', 'open')
        if status == 'filled':
            status = 'closed'
        elif status == 'calcelled':
            status = 'canceled'
        symbol = None
        cost = None
        price = self.safe_float(order, 'price')
        amount = None
        remaining = None
        filled = None
        if market:
            symbol = market['symbol']
            quoteId = market['quoteId']
            baseId = market['baseId']
            if (market['quoteId'] == 'idr') and('order_rp' in list(order.keys())):
                quoteId = 'rp'
            if (market['baseId'] == 'idr') and('remain_rp' in list(order.keys())):
                baseId = 'rp'
            cost = self.safe_float(order, 'order_' + quoteId)
            if cost:
                amount = cost / price
                remainingCost = self.safe_float(order, 'remain_' + quoteId)
                if remainingCost is not None:
                    remaining = remainingCost / price
                    filled = amount - remaining
            else:
                amount = self.safe_float(order, 'order_' + baseId)
                cost = price * amount
                remaining = self.safe_float(order, 'remain_' + baseId)
                filled = amount - remaining
        average = None
        if filled:
            average = cost / filled
        timestamp = int(order['submit_time'])
        fee = None
        result = {
            'info': order,
            'id': order['order_id'],
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
            'symbol': symbol,
            'type': 'limit',
            'side': side,
            'price': price,
            'cost': cost,
            'average': average,
            'amount': amount,
            'filled': filled,
            'remaining': remaining,
            'status': status,
            'fee': fee,
        }
        return result

    def fetch_order(self, id, symbol=None, params={}):
        if not symbol:
            raise ExchangeError(self.id + ' fetchOrder requires a symbol')
        self.load_markets()
        market = self.market(symbol)
        response = self.privatePostGetOrder(self.extend({
            'pair': market['id'],
            'order_id': id,
        }, params))
        orders = response['return']
        order = self.parse_order(self.extend({'id': id}, orders['order']), market)
        return self.extend({'info': response}, order)

    def fetch_open_orders(self, symbol=None, since=None, limit=None, params={}):
        self.load_markets()
        market = None
        request = {}
        if symbol:
            market = self.market(symbol)
            request['pair'] = market['id']
        response = self.privatePostOpenOrders(self.extend(request, params))
        rawOrders = response['return']['orders']
        # {success: 1, return: {orders: null}} if no orders
        if not rawOrders:
            return []
        # {success: 1, return: {orders: [... objects]}} for orders fetched by symbol
        if symbol is not None:
            return self.parse_orders(rawOrders, market, since, limit)
        # {success: 1, return: {orders: {marketid: [... objects]}}} if all orders are fetched
        marketIds = list(rawOrders.keys())
        exchangeOrders = []
        for i in range(0, len(marketIds)):
            marketId = marketIds[i]
            marketOrders = rawOrders[marketId]
            market = self.markets_by_id[marketId]
            parsedOrders = self.parse_orders(marketOrders, market, since, limit)
            exchangeOrders = self.array_concat(exchangeOrders, parsedOrders)
        return exchangeOrders

    def fetch_closed_orders(self, symbol=None, since=None, limit=None, params={}):
        if not symbol:
            raise ExchangeError(self.id + ' fetchOrders requires a symbol')
        self.load_markets()
        request = {}
        market = None
        if symbol:
            market = self.market(symbol)
            request['pair'] = market['id']
        response = self.privatePostOrderHistory(self.extend(request, params))
        orders = self.parse_orders(response['return']['orders'], market, since, limit)
        orders = self.filter_by(orders, 'status', 'closed')
        if symbol:
            return self.filter_orders_by_symbol(orders, symbol)
        return orders

    def create_order(self, symbol, type, side, amount, price=None, params={}):
        if type != 'limit':
            raise ExchangeError(self.id + ' allows limit orders only')
        self.load_markets()
        market = self.market(symbol)
        order = {
            'pair': market['id'],
            'type': side,
            'price': price,
        }
        currency = market['baseId']
        if side == 'buy':
            order[market['quoteId']] = amount * price
        else:
            order[market['baseId']] = amount
        order[currency] = amount
        result = self.privatePostTrade(self.extend(order, params))
        return {
            'info': result,
            'id': str(result['return']['order_id']),
        }

    def cancel_order(self, id, symbol=None, params={}):
        if symbol is None:
            raise ExchangeError(self.id + ' cancelOrder requires a symbol argument')
        side = self.safe_value(params, 'side')
        if side is None:
            raise ExchangeError(self.id + ' cancelOrder requires an extra "side" param')
        self.load_markets()
        market = self.market(symbol)
        return self.privatePostCancelOrder(self.extend({
            'order_id': id,
            'pair': market['id'],
            'type': params['side'],
        }, params))

    def sign(self, path, api='public', method='GET', params={}, headers=None, body=None):
        url = self.urls['api'][api]
        if api == 'public':
            url += '/' + self.implode_params(path, params)
        else:
            self.check_required_credentials()
            body = self.urlencode(self.extend({
                'method': path,
                'nonce': self.nonce(),
            }, params))
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded',
                'Key': self.apiKey,
                'Sign': self.hmac(self.encode(body), self.encode(self.secret), hashlib.sha512),
            }
        return {'url': url, 'method': method, 'body': body, 'headers': headers}

    def handle_errors(self, code, reason, url, method, headers, body, response=None):
        # {success: 0, error: "invalid order."}
        if response is None:
            if body[0] == '{':
                response = json.loads(body)
        if not('success' in list(response.keys())):
            return  # no 'success' property on public responses
        if response['success'] == 1:
            # {success: 1, return: {orders: []}}
            if not('return' in list(response.keys())):
                raise ExchangeError(self.id + ': malformed response: ' + self.json(response))
            else:
                return
        message = response['error']
        feedback = self.id + ' ' + self.json(response)
        if message == 'Insufficient balance.':
            raise InsufficientFunds(feedback)
        elif message == 'invalid order.':
            raise OrderNotFound(feedback)  # cancelOrder(1)
        elif message.find('Minimum price ') >= 0:
            raise InvalidOrder(feedback)  # price < limits.price.min, on createLimitBuyOrder('ETH/BTC', 1, 0)
        elif message.find('Minimum order ') >= 0:
            raise InvalidOrder(feedback)  # cost < limits.cost.min on createLimitBuyOrder('ETH/BTC', 0, 1)
        elif message == 'Invalid credentials. API not found or session has expired.':
            raise AuthenticationError(feedback)  # on bad apiKey
        elif message == 'Invalid credentials. Bad sign.':
            raise AuthenticationError(feedback)  # on bad secret
        raise ExchangeError(self.id + ': unknown error: ' + self.json(response))
