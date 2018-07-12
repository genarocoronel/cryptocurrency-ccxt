# -*- coding: utf-8 -*-

# PLEASE DO NOT EDIT THIS FILE, IT IS GENERATED AND WILL BE OVERWRITTEN:
# https://github.com/ccxt/ccxt/blob/master/CONTRIBUTING.md#how-to-contribute-code

from ccxt.async_support.base.exchange import Exchange

# -----------------------------------------------------------------------------

try:
    basestring  # Python 3
except NameError:
    basestring = str  # Python 2
import math
import json
from ccxt.base.errors import ExchangeError
from ccxt.base.errors import AuthenticationError
from ccxt.base.errors import PermissionDenied
from ccxt.base.errors import NotSupported


class bitstamp (Exchange):

    def describe(self):
        return self.deep_extend(super(bitstamp, self).describe(), {
            'id': 'bitstamp',
            'name': 'Bitstamp',
            'countries': ['GB'],
            'rateLimit': 1000,
            'version': 'v2',
            'has': {
                'CORS': True,
                'fetchDepositAddress': True,
                'fetchOrder': True,
                'fetchOpenOrders': True,
                'fetchMyTrades': True,
                'withdraw': True,
            },
            'urls': {
                'logo': 'https://user-images.githubusercontent.com/1294454/27786377-8c8ab57e-5fe9-11e7-8ea4-2b05b6bcceec.jpg',
                'api': 'https://www.bitstamp.net/api',
                'www': 'https://www.bitstamp.net',
                'doc': 'https://www.bitstamp.net/api',
            },
            'requiredCredentials': {
                'apiKey': True,
                'secret': True,
                'uid': True,
            },
            'api': {
                'public': {
                    'get': [
                        'order_book/{pair}/',
                        'ticker_hour/{pair}/',
                        'ticker/{pair}/',
                        'transactions/{pair}/',
                        'trading-pairs-info/',
                    ],
                },
                'private': {
                    'post': [
                        'balance/',
                        'balance/{pair}/',
                        'bch_withdrawal/',
                        'bch_address/',
                        'user_transactions/',
                        'user_transactions/{pair}/',
                        'open_orders/all/',
                        'open_orders/{pair}/',
                        'order_status/',
                        'cancel_order/',
                        'buy/{pair}/',
                        'buy/market/{pair}/',
                        'sell/{pair}/',
                        'sell/market/{pair}/',
                        'ltc_withdrawal/',
                        'ltc_address/',
                        'eth_withdrawal/',
                        'eth_address/',
                        'xrp_withdrawal/',
                        'xrp_address/',
                        'transfer-to-main/',
                        'transfer-from-main/',
                        'withdrawal-requests/',
                        'withdrawal/open/',
                        'withdrawal/status/',
                        'withdrawal/cancel/',
                        'liquidation_address/new/',
                        'liquidation_address/info/',
                    ],
                },
                'v1': {
                    'post': [
                        'bitcoin_deposit_address/',
                        'unconfirmed_btc/',
                        'bitcoin_withdrawal/',
                        'ripple_withdrawal/',
                        'ripple_address/',
                    ],
                },
            },
            'fees': {
                'trading': {
                    'tierBased': True,
                    'percentage': True,
                    'taker': 0.25 / 100,
                    'maker': 0.25 / 100,
                    'tiers': {
                        'taker': [
                            [0, 0.25 / 100],
                            [20000, 0.24 / 100],
                            [100000, 0.22 / 100],
                            [400000, 0.20 / 100],
                            [600000, 0.15 / 100],
                            [1000000, 0.14 / 100],
                            [2000000, 0.13 / 100],
                            [4000000, 0.12 / 100],
                            [20000000, 0.11 / 100],
                            [20000001, 0.10 / 100],
                        ],
                        'maker': [
                            [0, 0.25 / 100],
                            [20000, 0.24 / 100],
                            [100000, 0.22 / 100],
                            [400000, 0.20 / 100],
                            [600000, 0.15 / 100],
                            [1000000, 0.14 / 100],
                            [2000000, 0.13 / 100],
                            [4000000, 0.12 / 100],
                            [20000000, 0.11 / 100],
                            [20000001, 0.10 / 100],
                        ],
                    },
                },
                'funding': {
                    'tierBased': False,
                    'percentage': False,
                    'withdraw': {
                        'BTC': 0,
                        'BCH': 0,
                        'LTC': 0,
                        'ETH': 0,
                        'XRP': 0,
                        'USD': 25,
                        'EUR': 0.90,
                    },
                    'deposit': {
                        'BTC': 0,
                        'BCH': 0,
                        'LTC': 0,
                        'ETH': 0,
                        'XRP': 0,
                        'USD': 25,
                        'EUR': 0,
                    },
                },
            },
            'exceptions': {
                'No permission found': PermissionDenied,
            },
        })

    async def fetch_markets(self):
        markets = await self.publicGetTradingPairsInfo()
        result = []
        for i in range(0, len(markets)):
            market = markets[i]
            symbol = market['name']
            base, quote = symbol.split('/')
            baseId = base.lower()
            quoteId = quote.lower()
            symbolId = baseId + '_' + quoteId
            id = market['url_symbol']
            precision = {
                'amount': market['base_decimals'],
                'price': market['counter_decimals'],
            }
            parts = market['minimum_order'].split(' ')
            cost = parts[0]
            # cost, currency = market['minimum_order'].split(' ')
            active = (market['trading'] == 'Enabled')
            lot = math.pow(10, -precision['amount'])
            result.append({
                'id': id,
                'symbol': symbol,
                'base': base,
                'quote': quote,
                'baseId': baseId,
                'quoteId': quoteId,
                'symbolId': symbolId,
                'info': market,
                'lot': lot,
                'active': active,
                'precision': precision,
                'limits': {
                    'amount': {
                        'min': lot,
                        'max': None,
                    },
                    'price': {
                        'min': math.pow(10, -precision['price']),
                        'max': None,
                    },
                    'cost': {
                        'min': float(cost),
                        'max': None,
                    },
                },
            })
        return result

    async def fetch_order_book(self, symbol, limit=None, params={}):
        await self.load_markets()
        orderbook = await self.publicGetOrderBookPair(self.extend({
            'pair': self.market_id(symbol),
        }, params))
        timestamp = int(orderbook['timestamp']) * 1000
        return self.parse_order_book(orderbook, timestamp)

    async def fetch_ticker(self, symbol, params={}):
        await self.load_markets()
        ticker = await self.publicGetTickerPair(self.extend({
            'pair': self.market_id(symbol),
        }, params))
        timestamp = int(ticker['timestamp']) * 1000
        vwap = self.safe_float(ticker, 'vwap')
        baseVolume = self.safe_float(ticker, 'volume')
        quoteVolume = baseVolume * vwap
        last = self.safe_float(ticker, 'last')
        return {
            'symbol': symbol,
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
            'high': self.safe_float(ticker, 'high'),
            'low': self.safe_float(ticker, 'low'),
            'bid': self.safe_float(ticker, 'bid'),
            'bidVolume': None,
            'ask': self.safe_float(ticker, 'ask'),
            'askVolume': None,
            'vwap': vwap,
            'open': self.safe_float(ticker, 'open'),
            'close': last,
            'last': last,
            'previousClose': None,
            'change': None,
            'percentage': None,
            'average': None,
            'baseVolume': baseVolume,
            'quoteVolume': quoteVolume,
            'info': ticker,
        }

    def get_market_from_trade(self, trade):
        trade = self.omit(trade, [
            'fee',
            'price',
            'datetime',
            'tid',
            'type',
            'order_id',
            'side',
        ])
        currencyIds = list(trade.keys())
        numCurrencyIds = len(currencyIds)
        if numCurrencyIds > 2:
            raise ExchangeError(self.id + ' getMarketFromTrade too many keys: ' + self.json(currencyIds) + ' in the trade: ' + self.json(trade))
        if numCurrencyIds == 2:
            marketId = currencyIds[0] + currencyIds[1]
            if marketId in self.markets_by_id:
                return self.markets_by_id[marketId]
            marketId = currencyIds[1] + currencyIds[0]
            if marketId in self.markets_by_id:
                return self.markets_by_id[marketId]
        return None

    def get_market_from_trades(self, trades):
        tradesBySymbol = self.index_by(trades, 'symbol')
        symbols = list(tradesBySymbol.keys())
        numSymbols = len(symbols)
        if numSymbols == 1:
            return self.markets[symbols[0]]
        return None

    def parse_trade(self, trade, market=None):
        timestamp = None
        symbol = None
        if 'date' in trade:
            timestamp = int(trade['date']) * 1000
        elif 'datetime' in trade:
            timestamp = self.parse8601(trade['datetime'])
        # only if overrided externally
        side = self.safe_string(trade, 'side')
        orderId = self.safe_string(trade, 'order_id')
        if orderId is None:
            if side is None:
                side = self.safe_integer(trade, 'type')
                if side == 0:
                    side = 'buy'
                else:
                    side = 'sell'
        price = self.safe_float(trade, 'price')
        amount = self.safe_float(trade, 'amount')
        id = self.safe_string(trade, 'tid')
        id = self.safe_string(trade, 'id', id)
        if market is None:
            keys = list(trade.keys())
            for i in range(0, len(keys)):
                if keys[i].find('_') >= 0:
                    marketId = keys[i].replace('_', '')
                    if marketId in self.markets_by_id:
                        market = self.markets_by_id[marketId]
            # if the market is still not defined
            # try to deduce it from used keys
            if market is None:
                market = self.get_market_from_trade(trade)
        feeCost = self.safe_float(trade, 'fee')
        feeCurrency = None
        if market is not None:
            price = self.safe_float(trade, market['symbolId'], price)
            amount = self.safe_float(trade, market['baseId'], amount)
            feeCurrency = market['quote']
            symbol = market['symbol']
        cost = None
        if price is not None:
            if amount is not None:
                cost = price * amount
        return {
            'id': id,
            'info': trade,
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
            'symbol': symbol,
            'order': orderId,
            'type': None,
            'side': side,
            'price': price,
            'amount': amount,
            'cost': cost,
            'fee': {
                'cost': feeCost,
                'currency': feeCurrency,
            },
        }

    async def fetch_trades(self, symbol, since=None, limit=None, params={}):
        await self.load_markets()
        market = self.market(symbol)
        response = await self.publicGetTransactionsPair(self.extend({
            'pair': market['id'],
            'time': 'hour',
        }, params))
        return self.parse_trades(response, market, since, limit)

    async def fetch_balance(self, params={}):
        await self.load_markets()
        balance = await self.privatePostBalance()
        result = {'info': balance}
        currencies = list(self.currencies.keys())
        for i in range(0, len(currencies)):
            currency = currencies[i]
            lowercase = currency.lower()
            total = lowercase + '_balance'
            free = lowercase + '_available'
            used = lowercase + '_reserved'
            account = self.account()
            if free in balance:
                account['free'] = float(balance[free])
            if used in balance:
                account['used'] = float(balance[used])
            if total in balance:
                account['total'] = float(balance[total])
            result[currency] = account
        return self.parse_balance(result)

    async def create_order(self, symbol, type, side, amount, price=None, params={}):
        await self.load_markets()
        method = 'privatePost' + self.capitalize(side)
        order = {
            'pair': self.market_id(symbol),
            'amount': self.amount_to_precision(symbol, amount),
        }
        if type == 'market':
            method += 'Market'
        else:
            order['price'] = self.price_to_precision(symbol, price)
        method += 'Pair'
        response = await getattr(self, method)(self.extend(order, params))
        return {
            'info': response,
            'id': response['id'],
        }

    async def cancel_order(self, id, symbol=None, params={}):
        await self.load_markets()
        return await self.privatePostCancelOrder({'id': id})

    def parse_order_status(self, order):
        if (order['status'] == 'Queue') or (order['status'] == 'Open'):
            return 'open'
        if order['status'] == 'Finished':
            return 'closed'
        return order['status']

    async def fetch_order_status(self, id, symbol=None, params={}):
        await self.load_markets()
        response = await self.privatePostOrderStatus(self.extend({'id': id}, params))
        return self.parse_order_status(response)

    async def fetch_order(self, id, symbol=None, params={}):
        await self.load_markets()
        market = None
        if symbol is not None:
            market = self.market(symbol)
        response = await self.privatePostOrderStatus(self.extend({'id': id}, params))
        return self.parse_order(response, market)

    async def fetch_my_trades(self, symbol=None, since=None, limit=None, params={}):
        await self.load_markets()
        request = {}
        method = 'privatePostUserTransactions'
        market = None
        if symbol is not None:
            market = self.market(symbol)
            request['pair'] = market['id']
            method += 'Pair'
        if limit is not None:
            request['limit'] = limit
        response = await getattr(self, method)(self.extend(request, params))
        return self.parse_trades(response, market, since, limit)

    def parse_order(self, order, market=None):
        id = self.safe_string(order, 'id')
        timestamp = None
        iso8601 = None
        side = self.safe_string(order, 'type')
        if side is not None:
            side = 'sell' if (side == '1') else 'buy'
        datetimeString = self.safe_string(order, 'datetime')
        if datetimeString is not None:
            timestamp = self.parse8601(datetimeString)
            iso8601 = self.iso8601(timestamp)
        symbol = None
        if market is None:
            if 'currency_pair' in order:
                marketId = order['currency_pair']
                if marketId in self.markets_by_id:
                    market = self.markets_by_id[marketId]
        amount = self.safe_float(order, 'amount')
        filled = 0.0
        trades = []
        transactions = self.safe_value(order, 'transactions')
        feeCost = None
        cost = None
        if transactions is not None:
            if isinstance(transactions, list):
                for i in range(0, len(transactions)):
                    trade = self.parse_trade(self.extend({
                        'order_id': id,
                        'side': side,
                    }, transactions[i]), market)
                    filled += trade['amount']
                    if feeCost is None:
                        feeCost = 0.0
                    feeCost += trade['fee']['cost']
                    if cost is None:
                        cost = 0.0
                    cost += trade['cost']
                    trades.append(trade)
        status = self.safe_string(order, 'status')
        if (status == 'In Queue') or (status == 'Open'):
            status = 'open'
        elif status == 'Finished':
            status = 'closed'
            if amount is None:
                amount = filled
        remaining = None
        if amount is not None:
            remaining = amount - filled
        price = self.safe_float(order, 'price')
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
            'lastTradeTimestamp': None,
            'status': status,
            'symbol': symbol,
            'type': None,
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

    async def fetch_open_orders(self, symbol=None, since=None, limit=None, params={}):
        market = None
        await self.load_markets()
        if symbol is not None:
            market = self.market(symbol)
        orders = await self.privatePostOpenOrdersAll()
        return self.parse_orders(orders, market, since, limit)

    def get_currency_name(self, code):
        if code == 'BTC':
            return 'bitcoin'
        return code.lower()

    def is_fiat(self, code):
        if code == 'USD':
            return True
        if code == 'EUR':
            return True
        return False

    async def fetch_deposit_address(self, code, params={}):
        if self.is_fiat(code):
            raise NotSupported(self.id + ' fiat fetchDepositAddress() for ' + code + ' is not implemented yet')
        name = self.get_currency_name(code)
        v1 = (code == 'BTC')
        method = 'v1' if v1 else 'private'  # v1 or v2
        method += 'Post' + self.capitalize(name)
        method += 'Deposit' if v1 else ''
        method += 'Address'
        response = await getattr(self, method)(params)
        address = response if v1 else self.safe_string(response, 'address')
        tag = None if v1 else self.safe_string(response, 'destination_tag')
        self.check_address(address)
        return {
            'currency': code,
            'address': address,
            'tag': tag,
            'info': response,
        }

    async def withdraw(self, code, amount, address, tag=None, params={}):
        self.check_address(address)
        if self.is_fiat(code):
            raise NotSupported(self.id + ' fiat withdraw() for ' + code + ' is not implemented yet')
        name = self.get_currency_name(code)
        request = {
            'amount': amount,
            'address': address,
        }
        v1 = (code == 'BTC')
        method = 'v1' if v1 else 'private'  # v1 or v2
        method += 'Post' + self.capitalize(name) + 'Withdrawal'
        query = params
        if code == 'XRP':
            if tag is not None:
                request['destination_tag'] = tag
                query = self.omit(params, 'destination_tag')
            else:
                raise ExchangeError(self.id + ' withdraw() requires a destination_tag param for ' + code)
        response = await getattr(self, method)(self.extend(request, query))
        return {
            'info': response,
            'id': response['id'],
        }

    def sign(self, path, api='public', method='GET', params={}, headers=None, body=None):
        url = self.urls['api'] + '/'
        if api != 'v1':
            url += self.version + '/'
        url += self.implode_params(path, params)
        query = self.omit(params, self.extract_params(path))
        if api == 'public':
            if query:
                url += '?' + self.urlencode(query)
        else:
            self.check_required_credentials()
            nonce = str(self.nonce())
            auth = nonce + self.uid + self.apiKey
            signature = self.encode(self.hmac(self.encode(auth), self.encode(self.secret)))
            query = self.extend({
                'key': self.apiKey,
                'signature': signature.upper(),
                'nonce': nonce,
            }, query)
            body = self.urlencode(query)
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded',
            }
        return {'url': url, 'method': method, 'body': body, 'headers': headers}

    def handle_errors(self, httpCode, reason, url, method, headers, body):
        if not isinstance(body, basestring):
            return  # fallback to default error handler
        if len(body) < 2:
            return  # fallback to default error handler
        if (body[0] == '{') or (body[0] == '['):
            response = json.loads(body)
            # fetchDepositAddress returns {"error": "No permission found"} on apiKeys that don't have the permission required
            error = self.safe_string(response, 'error')
            exceptions = self.exceptions
            if error in exceptions:
                raise exceptions[error](self.id + ' ' + body)
            status = self.safe_string(response, 'status')
            if status == 'error':
                code = self.safe_string(response, 'code')
                if code is not None:
                    if code == 'API0005':
                        raise AuthenticationError(self.id + ' invalid signature, use the uid for the main account if you have subaccounts')
                raise ExchangeError(self.id + ' ' + body)
