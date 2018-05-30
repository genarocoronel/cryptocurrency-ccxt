# -*- coding: utf-8 -*-

# PLEASE DO NOT EDIT THIS FILE, IT IS GENERATED AND WILL BE OVERWRITTEN:
# https://github.com/ccxt/ccxt/blob/master/CONTRIBUTING.md#how-to-contribute-code

from ccxt.base.exchange import Exchange
from ccxt.base.errors import ExchangeError


class foxbit (Exchange):

    def describe(self):
        return self.deep_extend(super(foxbit, self).describe(), {
            'id': 'foxbit',
            'name': 'FoxBit',
            'countries': 'BR',
            'has': {
                'CORS': False,
                'createMarketOrder': False,
            },
            'rateLimit': 1000,
            'version': 'v1',
            'urls': {
                'logo': 'https://user-images.githubusercontent.com/1294454/27991413-11b40d42-647f-11e7-91ee-78ced874dd09.jpg',
                'api': {
                    'public': 'https://api.blinktrade.com/api',
                    'private': 'https://api.blinktrade.com/tapi',
                },
                'www': 'https://foxbit.exchange',
                'doc': 'https://blinktrade.com/docs',
            },
            'comment': 'Blinktrade API',
            'api': {
                'public': {
                    'get': [
                        '{currency}/ticker',    # ?crypto_currency=BTC
                        '{currency}/orderbook',  # ?crypto_currency=BTC
                        '{currency}/trades',    # ?crypto_currency=BTC&since=<TIMESTAMP>&limit=<NUMBER>
                    ],
                },
                'private': {
                    'post': [
                        'D',   # order
                        'F',   # cancel order
                        'U2',  # balance
                        'U4',  # my orders
                        'U6',  # withdraw
                        'U18',  # deposit
                        'U24',  # confirm withdrawal
                        'U26',  # list withdrawals
                        'U30',  # list deposits
                        'U34',  # ledger
                        'U70',  # cancel withdrawal
                    ],
                },
            },
            'markets': {
                'BTC/VEF': {'id': 'BTCVEF', 'symbol': 'BTC/VEF', 'base': 'BTC', 'quote': 'VEF', 'brokerId': 1, 'broker': 'SurBitcoin'},
                'BTC/VND': {'id': 'BTCVND', 'symbol': 'BTC/VND', 'base': 'BTC', 'quote': 'VND', 'brokerId': 3, 'broker': 'VBTC'},
                'BTC/BRL': {'id': 'BTCBRL', 'symbol': 'BTC/BRL', 'base': 'BTC', 'quote': 'BRL', 'brokerId': 4, 'broker': 'FoxBit'},
                'BTC/PKR': {'id': 'BTCPKR', 'symbol': 'BTC/PKR', 'base': 'BTC', 'quote': 'PKR', 'brokerId': 8, 'broker': 'UrduBit'},
                'BTC/CLP': {'id': 'BTCCLP', 'symbol': 'BTC/CLP', 'base': 'BTC', 'quote': 'CLP', 'brokerId': 9, 'broker': 'ChileBit'},
            },
            'options': {
                'brokerId': '4',  # https://blinktrade.com/docs/#brokers
            },
        })

    def fetch_balance(self, params={}):
        response = self.privatePostU2({
            'BalanceReqID': self.nonce(),
        })
        balances = self.safe_value(response['Responses'], self.options['brokerId'])
        result = {'info': response}
        if balances is not None:
            currencyIds = list(self.currencies_by_id.keys())
            for i in range(0, len(currencyIds)):
                currencyId = currencyIds[i]
                currency = self.currencies_by_id[currencyId]
                code = currency['code']
                # we only set the balance for the currency if that currency is present in response
                # otherwise we will lose the info if the currency balance has been funded or traded or not
                if currencyId in balances:
                    account = self.account()
                    account['used'] = float(balances[currencyId + '_locked']) * 1e-8
                    account['total'] = float(balances[currencyId]) * 1e-8
                    account['free'] = account['total'] - account['used']
                    result[code] = account
        return self.parse_balance(result)

    def fetch_order_book(self, symbol, limit=None, params={}):
        market = self.market(symbol)
        orderbook = self.publicGetCurrencyOrderbook(self.extend({
            'currency': market['quote'],
            'crypto_currency': market['base'],
        }, params))
        return self.parse_order_book(orderbook)

    def fetch_ticker(self, symbol, params={}):
        market = self.market(symbol)
        ticker = self.publicGetCurrencyTicker(self.extend({
            'currency': market['quote'],
            'crypto_currency': market['base'],
        }, params))
        timestamp = self.milliseconds()
        lowercaseQuote = market['quote'].lower()
        quoteVolume = 'vol_' + lowercaseQuote
        last = self.safe_float(ticker, 'last')
        return {
            'symbol': symbol,
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
            'high': self.safe_float(ticker, 'high'),
            'low': self.safe_float(ticker, 'low'),
            'bid': self.safe_float(ticker, 'buy'),
            'bidVolume': None,
            'ask': self.safe_float(ticker, 'sell'),
            'askVolume': None,
            'vwap': None,
            'open': None,
            'close': last,
            'last': last,
            'previousClose': None,
            'change': None,
            'percentage': None,
            'average': None,
            'baseVolume': self.safe_float(ticker, 'vol'),
            'quoteVolume': float(ticker[quoteVolume]),
            'info': ticker,
        }

    def parse_trade(self, trade, market):
        timestamp = trade['date'] * 1000
        return {
            'id': self.safe_string(trade, 'tid'),
            'info': trade,
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
            'symbol': market['symbol'],
            'type': None,
            'side': trade['side'],
            'price': trade['price'],
            'amount': trade['amount'],
        }

    def fetch_trades(self, symbol, since=None, limit=None, params={}):
        market = self.market(symbol)
        response = self.publicGetCurrencyTrades(self.extend({
            'currency': market['quote'],
            'crypto_currency': market['base'],
        }, params))
        return self.parse_trades(response, market, since, limit)

    def create_order(self, symbol, type, side, amount, price=None, params={}):
        if type == 'market':
            raise ExchangeError(self.id + ' allows limit orders only')
        market = self.market(symbol)
        orderSide = '1' if (side == 'buy') else '2'
        order = {
            'ClOrdID': self.nonce(),
            'Symbol': market['id'],
            'Side': orderSide,
            'OrdType': '2',
            'Price': price,
            'OrderQty': amount,
            'BrokerID': market['brokerId'],
        }
        response = self.privatePostD(self.extend(order, params))
        indexed = self.index_by(response['Responses'], 'MsgType')
        execution = indexed['8']
        return {
            'info': response,
            'id': execution['OrderID'],
        }

    def cancel_order(self, id, symbol=None, params={}):
        return self.privatePostF(self.extend({
            'ClOrdID': id,
        }, params))

    def sign(self, path, api='public', method='GET', params={}, headers=None, body=None):
        url = self.urls['api'][api] + '/' + self.version + '/' + self.implode_params(path, params)
        query = self.omit(params, self.extract_params(path))
        if api == 'public':
            if query:
                url += '?' + self.urlencode(query)
        else:
            self.check_required_credentials()
            nonce = str(self.nonce())
            request = self.extend({'MsgType': path}, query)
            body = self.json(request)
            headers = {
                'APIKey': self.apiKey,
                'Nonce': nonce,
                'Signature': self.hmac(self.encode(nonce), self.encode(self.secret)),
                'Content-Type': 'application/json',
            }
        return {'url': url, 'method': method, 'body': body, 'headers': headers}

    def request(self, path, api='public', method='GET', params={}, headers=None, body=None):
        response = self.fetch2(path, api, method, params, headers, body)
        if 'Status' in response:
            if response['Status'] != 200:
                raise ExchangeError(self.id + ' ' + self.json(response))
        return response
