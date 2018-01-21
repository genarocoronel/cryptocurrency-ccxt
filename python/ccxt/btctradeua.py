# -*- coding: utf-8 -*-

from ccxt.base.exchange import Exchange
from ccxt.base.errors import ExchangeError


class btctradeua (Exchange):

    def describe(self):
        return self.deep_extend(super(btctradeua, self).describe(), {
            'id': 'btctradeua',
            'name': 'BTC Trade UA',
            'countries': 'UA',  # Ukraine,
            'rateLimit': 3000,
            'has': {
                'CORS': True,
            },
            'urls': {
                'logo': 'https://user-images.githubusercontent.com/1294454/27941483-79fc7350-62d9-11e7-9f61-ac47f28fcd96.jpg',
                'api': 'https://btc-trade.com.ua/api',
                'www': 'https://btc-trade.com.ua',
                'doc': 'https://docs.google.com/document/d/1ocYA0yMy_RXd561sfG3qEPZ80kyll36HUxvCRe5GbhE/edit',
            },
            'api': {
                'public': {
                    'get': [
                        'deals/{symbol}',
                        'trades/sell/{symbol}',
                        'trades/buy/{symbol}',
                        'japan_stat/high/{symbol}',
                    ],
                },
                'private': {
                    'post': [
                        'auth',
                        'ask/{symbol}',
                        'balance',
                        'bid/{symbol}',
                        'buy/{symbol}',
                        'my_orders/{symbol}',
                        'order/status/{id}',
                        'remove/order/{id}',
                        'sell/{symbol}',
                    ],
                },
            },
            'markets': {
                'BCH/UAH': {'id': 'bch_uah', 'symbol': 'BCH/UAH', 'base': 'BCH', 'quote': 'UAH'},
                'BTC/UAH': {'id': 'btc_uah', 'symbol': 'BTC/UAH', 'base': 'BTC', 'quote': 'UAH', 'precision': {'price': 1}, 'limits': {'amount': {'min': 0.0000000001}}},
                'DASH/BTC': {'id': 'dash_btc', 'symbol': 'DASH/BTC', 'base': 'DASH', 'quote': 'BTC'},
                'DASH/UAH': {'id': 'dash_uah', 'symbol': 'DASH/UAH', 'base': 'DASH', 'quote': 'UAH'},
                'DOGE/BTC': {'id': 'doge_btc', 'symbol': 'DOGE/BTC', 'base': 'DOGE', 'quote': 'BTC'},
                'DOGE/UAH': {'id': 'doge_uah', 'symbol': 'DOGE/UAH', 'base': 'DOGE', 'quote': 'UAH'},
                'ETH/UAH': {'id': 'eth_uah', 'symbol': 'ETH/UAH', 'base': 'ETH', 'quote': 'UAH'},
                'ITI/UAH': {'id': 'iti_uah', 'symbol': 'ITI/UAH', 'base': 'ITI', 'quote': 'UAH'},
                'KRB/UAH': {'id': 'krb_uah', 'symbol': 'KRB/UAH', 'base': 'KRB', 'quote': 'UAH'},
                'LTC/BTC': {'id': 'ltc_btc', 'symbol': 'LTC/BTC', 'base': 'LTC', 'quote': 'BTC'},
                'LTC/UAH': {'id': 'ltc_uah', 'symbol': 'LTC/UAH', 'base': 'LTC', 'quote': 'UAH'},
                'NVC/BTC': {'id': 'nvc_btc', 'symbol': 'NVC/BTC', 'base': 'NVC', 'quote': 'BTC'},
                'NVC/UAH': {'id': 'nvc_uah', 'symbol': 'NVC/UAH', 'base': 'NVC', 'quote': 'UAH'},
                'PPC/BTC': {'id': 'ppc_btc', 'symbol': 'PPC/BTC', 'base': 'PPC', 'quote': 'BTC'},
                'SIB/UAH': {'id': 'sib_uah', 'symbol': 'SIB/UAH', 'base': 'SIB', 'quote': 'UAH'},
                'XMR/UAH': {'id': 'xmr_uah', 'symbol': 'XMR/UAH', 'base': 'XMR', 'quote': 'UAH'},
                'ZEC/UAH': {'id': 'zec_uah', 'symbol': 'ZEC/UAH', 'base': 'ZEC', 'quote': 'UAH'},
            },
            'fees': {
                'trading': {
                    'maker': 0.1 / 100,
                    'taker': 0.1 / 100,
                },
                'funding': {
                    'withdraw': {
                        'BTC': 0.0006,
                        'LTC': 0.01,
                        'NVC': 0.01,
                        'DOGE': 10,
                    },
                },
            },
        })

    def sign_in(self):
        return self.privatePostAuth()

    def fetch_balance(self, params={}):
        response = self.privatePostBalance()
        result = {'info': response}
        if 'accounts' in response:
            accounts = response['accounts']
            for b in range(0, len(accounts)):
                account = accounts[b]
                currency = account['currency']
                balance = float(account['balance'])
                result[currency] = {
                    'free': balance,
                    'used': 0.0,
                    'total': balance,
                }
        return self.parse_balance(result)

    def fetch_order_book(self, symbol, params={}):
        market = self.market(symbol)
        bids = self.publicGetTradesBuySymbol(self.extend({
            'symbol': market['id'],
        }, params))
        asks = self.publicGetTradesSellSymbol(self.extend({
            'symbol': market['id'],
        }, params))
        orderbook = {
            'bids': [],
            'asks': [],
        }
        if bids:
            if 'list' in bids:
                orderbook['bids'] = bids['list']
        if asks:
            if 'list' in asks:
                orderbook['asks'] = asks['list']
        return self.parse_order_book(orderbook, None, 'bids', 'asks', 'price', 'currency_trade')

    def fetch_ticker(self, symbol, params={}):
        response = self.publicGetJapanStatHighSymbol(self.extend({
            'symbol': self.market_id(symbol),
        }, params))
        orderbook = self.fetch_order_book(symbol)
        bid = None
        numBids = len(orderbook['bids'])
        if numBids > 0:
            bid = orderbook['bids'][0][0]
        ask = None
        numAsks = len(orderbook['asks'])
        if numAsks > 0:
            ask = orderbook['asks'][0][0]
        ticker = response['trades']
        timestamp = self.milliseconds()
        result = {
            'symbol': symbol,
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
            'high': None,
            'low': None,
            'bid': bid,
            'ask': ask,
            'vwap': None,
            'open': None,
            'close': None,
            'first': None,
            'last': None,
            'change': None,
            'percentage': None,
            'average': None,
            'baseVolume': None,
            'quoteVolume': None,
            'info': ticker,
        }
        tickerLength = len(ticker)
        if tickerLength > 0:
            start = max(tickerLength - 48, 0)
            for t in range(start, len(ticker)):
                candle = ticker[t]
                if result['open'] is None:
                    result['open'] = candle[1]
                if (result['high'] is None) or (result['high'] < candle[2]):
                    result['high'] = candle[2]
                if (result['low'] is None) or (result['low'] > candle[3]):
                    result['low'] = candle[3]
                if result['baseVolume'] is None:
                    result['baseVolume'] = -candle[5]
                else:
                    result['baseVolume'] -= candle[5]
            last = tickerLength - 1
            result['close'] = ticker[last][4]
            result['baseVolume'] = -1 * result['baseVolume']
        return result

    def convert_cyrillic_month_name_to_string(self, cyrillic):
        months = {
            u'января': '01',
            u'февраля': '02',
            u'марта': '03',
            u'апреля': '04',
            u'мая': '05',
            u'июня': '06',
            u'июля': '07',
            u'августа': '08',
            u'сентября': '09',
            u'октября': '10',
            u'ноября': '11',
            u'декабря': '12',
        }
        month = None
        if cyrillic in months:
            month = months[cyrillic]
        return month

    def parse_cyrillic_datetime(self, cyrillic):
        parts = cyrillic.split(' ')
        day = parts[0]
        month = self.convert_cyrillic_month_name_to_string(parts[1])
        if not month:
            raise ExchangeError(self.id + ' parseTrade() None month name: ' + cyrillic)
        year = parts[2]
        hms = parts[4]
        hmsLength = len(hms)
        if hmsLength == 7:
            hms = '0' + hms
        if len(day) == 1:
            day = '0' + day
        ymd = '-'.join([year, month, day])
        ymdhms = ymd + 'T' + hms
        timestamp = self.parse8601(ymdhms)
        # server reports local time, adjust to UTC
        md = ''.join([month, day])
        md = int(md)
        # a special case for DST
        # subtract 2 hours during winter
        if md < 325 or md > 1028:
            return timestamp - 7200000
        # subtract 3 hours during summer
        return timestamp - 10800000

    def parse_trade(self, trade, market):
        timestamp = self.parse_cyrillic_datetime(trade['pub_date'])
        return {
            'id': str(trade['id']),
            'info': trade,
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
            'symbol': market['symbol'],
            'type': 'limit',
            'side': trade['type'],
            'price': float(trade['price']),
            'amount': float(trade['amnt_trade']),
        }

    def fetch_trades(self, symbol, since=None, limit=None, params={}):
        market = self.market(symbol)
        response = self.publicGetDealsSymbol(self.extend({
            'symbol': market['id'],
        }, params))
        # they report each trade twice(once for both of the two sides of the fill)
        # deduplicate trades for that reason
        trades = []
        for i in range(0, len(response)):
            if response[i]['id'] % 2:
                trades.append(response[i])
        return self.parse_trades(trades, market, since, limit)

    def create_order(self, symbol, type, side, amount, price=None, params={}):
        if type == 'market':
            raise ExchangeError(self.id + ' allows limit orders only')
        market = self.market(symbol)
        method = 'privatePost' + self.capitalize(side) + 'Id'
        order = {
            'count': amount,
            'currency1': market['quote'],
            'currency': market['base'],
            'price': price,
        }
        return getattr(self, method)(self.extend(order, params))

    def cancel_order(self, id, symbol=None, params={}):
        return self.privatePostRemoveOrderId({'id': id})

    def parse_order(self, trade, market):
        timestamp = self.milliseconds
        return {
            'id': trade['id'],
            'timestamp': timestamp,  # until they fix their timestamp
            'datetime': self.iso8601(timestamp),
            'status': 'open',
            'symbol': market['symbol'],
            'type': None,
            'side': trade['type'],
            'price': trade['price'],
            'amount': trade['amnt_trade'],
            'filled': 0,
            'remaining': trade['amnt_trade'],
            'trades': None,
            'info': trade,
        }

    def fetch_open_orders(self, symbol=None, since=None, limit=None, params={}):
        if not symbol:
            raise ExchangeError(self.id + ' fetchOpenOrders requires a symbol param')
        market = self.market(symbol)
        response = self.privatePostMyOrdersSymbol(self.extend({
            'symbol': market['id'],
        }, params))
        orders = response['your_open_orders']
        return self.parse_orders(orders, market, since, limit)

    def nonce(self):
        return self.milliseconds()

    def sign(self, path, api='public', method='GET', params={}, headers=None, body=None):
        url = self.urls['api'] + '/' + self.implode_params(path, params)
        query = self.omit(params, self.extract_params(path))
        if api == 'public':
            if query:
                url += self.implode_params(path, query)
        else:
            self.check_required_credentials()
            nonce = self.nonce()
            body = self.urlencode(self.extend({
                'out_order_id': nonce,
                'nonce': nonce,
            }, query))
            auth = body + self.secret
            headers = {
                'public-key': self.apiKey,
                'api-sign': self.hash(self.encode(auth), 'sha256'),
                'Content-Type': 'application/x-www-form-urlencoded',
            }
        return {'url': url, 'method': method, 'body': body, 'headers': headers}
