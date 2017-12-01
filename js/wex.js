"use strict";

// ---------------------------------------------------------------------------

const liqui = require ('./liqui.js')
const { ExchangeError, InsufficientFunds, OrderNotFound, DDoSProtection } = require ('./base/errors')

// ---------------------------------------------------------------------------

module.exports = class wex extends liqui {

    describe () {
        return this.deepExtend (super.describe (), {
            'id': 'wex',
            'name': 'WEX',
            'countries': 'NZ', // New Zealand
            'version': '3',
            'hasFetchTickers': true,
            'hasCORS': false,
            'urls': {
                'logo': 'https://user-images.githubusercontent.com/1294454/30652751-d74ec8f8-9e31-11e7-98c5-71469fcef03e.jpg',
                'api': {
                    'public': 'https://wex.nz/api',
                    'private': 'https://wex.nz/tapi',
                },
                'www': 'https://wex.nz',
                'doc': [
                    'https://wex.nz/api/3/docs',
                    'https://wex.nz/tapi/docs',
                ],
            },
            'api': {
                'public': {
                    'get': [
                        'info',
                        'ticker/{pair}',
                        'depth/{pair}',
                        'trades/{pair}',
                    ],
                },
                'private': {
                    'post': [
                        'getInfo',
                        'Trade',
                        'ActiveOrders',
                        'OrderInfo',
                        'CancelOrder',
                        'TradeHistory',
                        'TransHistory',
                        'CoinDepositAddress',
                        'WithdrawCoin',
                        'CreateCoupon',
                        'RedeemCoupon',
                    ],
                },
            },
            'fees': {
                'trading': {
                    'maker': 0.2 / 100,
                    'taker': 0.2 / 100,
                },
            },
        });
    }

    parseTicker (ticker, market = undefined) {
        let timestamp = ticker['updated'] * 1000;
        let symbol = undefined;
        if (market)
            symbol = market['symbol'];
        return {
            'symbol': symbol,
            'timestamp': timestamp,
            'datetime': this.iso8601 (timestamp),
            'high': this.safeFloat (ticker, 'high'),
            'low': this.safeFloat (ticker, 'low'),
            'bid': this.safeFloat (ticker, 'sell'),
            'ask': this.safeFloat (ticker, 'buy'),
            'vwap': undefined,
            'open': undefined,
            'close': undefined,
            'first': undefined,
            'last': this.safeFloat (ticker, 'last'),
            'change': undefined,
            'percentage': undefined,
            'average': this.safeFloat (ticker, 'avg'),
            'baseVolume': this.safeFloat (ticker, 'vol_cur'),
            'quoteVolume': this.safeFloat (ticker, 'vol'),
            'info': ticker,
        };
    }

    handleErrors (code, reason, url, method, headers, body) {
        if (code != 200) {
            // resort to defaultErrorHandler
            return;
        }
        if (body[0] != "{") {
            // response is not JSON
            throw new ExchangeError (this.id + ': JSON expected but received: ' + body);
        }
        let response = JSON.parse (body);
        let success = response['success'];
        if (success == undefined || success > 0) {
            // no errors
            return;
        }
        let error = response['error'];
        if (!error) {
            throw new ExchangeError (this.id + ': malformed response: ' + body);
        }
        if (error == 'no orders') {
            // that's what fetchOpenOrders return if no open orders (fix for #489)
            return;
        }
        if (error == 'bad status') {
            throw new OrderNotFound (this.id + ' ' + error);
        }
        if (error.indexOf ('It is not enough') >= 0) {
            throw new InsufficientFunds (this.id + ' ' + error);
        }
        if (['Requests too often', 'not available', 'external service unavailable'].indexOf(error)) {
            throw new DDoSProtection (this.id + ' ' + body);
        }
        throw new ExchangeError (this.id + ' ' + body);
    }

    request (path, api = 'public', method = 'GET', params = {}, headers = undefined, body = undefined) {
        return this.fetch2 (path, api, method, params, headers, body);
    }

}
