<?php

namespace ccxt;

// PLEASE DO NOT EDIT THIS FILE, IT IS GENERATED AND WILL BE OVERWRITTEN:
// https://github.com/ccxt/ccxt/blob/master/CONTRIBUTING.md#how-to-contribute-code

use Exception as Exception; // a common import

class exmo extends Exchange {

    public function describe () {
        return array_replace_recursive (parent::describe (), array (
            'id' => 'exmo',
            'name' => 'EXMO',
            'countries' => array ( 'ES', 'RU' ), // Spain, Russia
            'rateLimit' => 350, // once every 350 ms ≈ 180 requests per minute ≈ 3 requests per second
            'version' => 'v1',
            'has' => array (
                'CORS' => false,
                'fetchClosedOrders' => 'emulated',
                'fetchOpenOrders' => true,
                'fetchOrder' => 'emulated',
                'fetchOrders' => 'emulated',
                'fetchOrderTrades' => true,
                'fetchOrderBooks' => true,
                'fetchMyTrades' => true,
                'fetchTickers' => true,
                'withdraw' => true,
            ),
            'urls' => array (
                'logo' => 'https://user-images.githubusercontent.com/1294454/27766491-1b0ea956-5eda-11e7-9225-40d67b481b8d.jpg',
                'api' => 'https://api.exmo.com',
                'www' => 'https://exmo.me',
                'referral' => 'https://exmo.me/?ref=131685',
                'doc' => array (
                    'https://exmo.me/en/api_doc?ref=131685',
                    'https://github.com/exmo-dev/exmo_api_lib/tree/master/nodejs',
                ),
                'fees' => 'https://exmo.com/en/docs/fees',
            ),
            'api' => array (
                'public' => array (
                    'get' => array (
                        'currency',
                        'order_book',
                        'pair_settings',
                        'ticker',
                        'trades',
                    ),
                ),
                'private' => array (
                    'post' => array (
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
                    ),
                ),
            ),
            'fees' => array (
                'trading' => array (
                    'maker' => 0.2 / 100,
                    'taker' => 0.2 / 100,
                ),
                'funding' => array (
                    'withdraw' => array (
                        'BTC' => 0.001,
                        'LTC' => 0.01,
                        'DOGE' => 1,
                        'DASH' => 0.01,
                        'ETH' => 0.01,
                        'WAVES' => 0.001,
                        'ZEC' => 0.001,
                        'USDT' => 25,
                        'XMR' => 0.05,
                        'XRP' => 0.02,
                        'KICK' => 350,
                        'ETC' => 0.01,
                        'BCH' => 0.001,
                    ),
                    'deposit' => array (
                        'USDT' => 15,
                        'KICK' => 50,
                    ),
                ),
            ),
            'exceptions' => array (
                '40005' => '\\ccxt\\AuthenticationError', // Authorization error, incorrect signature
                '40009' => '\\ccxt\\InvalidNonce', //
                '40015' => '\\ccxt\\ExchangeError', // API function do not exist
                '40016' => '\\ccxt\\ExchangeNotAvailable', // Maintenance work in progress
                '40017' => '\\ccxt\\AuthenticationError', // Wrong API Key
                '50052' => '\\ccxt\\InsufficientFunds',
                '50054' => '\\ccxt\\InsufficientFunds',
                '50304' => '\\ccxt\\OrderNotFound', // "Order was not found '123456789'" (fetching order trades for an order that does not have trades yet)
                '50173' => '\\ccxt\\OrderNotFound', // "Order with id X was not found." (cancelling non-existent, closed and cancelled order)
                '50319' => '\\ccxt\\InvalidOrder', // Price by order is less than permissible minimum for this pair
                '50321' => '\\ccxt\\InvalidOrder', // Price by order is more than permissible maximum for this pair
            ),
        ));
    }

    public function fetch_markets () {
        $markets = $this->publicGetPairSettings ();
        $keys = is_array ($markets) ? array_keys ($markets) : array ();
        $result = array ();
        for ($p = 0; $p < count ($keys); $p++) {
            $id = $keys[$p];
            $market = $markets[$id];
            $symbol = str_replace ('_', '/', $id);
            list ($base, $quote) = explode ('/', $symbol);
            $result[] = array (
                'id' => $id,
                'symbol' => $symbol,
                'base' => $base,
                'quote' => $quote,
                'active' => true,
                'limits' => array (
                    'amount' => array (
                        'min' => $this->safe_float($market, 'min_quantity'),
                        'max' => $this->safe_float($market, 'max_quantity'),
                    ),
                    'price' => array (
                        'min' => $this->safe_float($market, 'min_price'),
                        'max' => $this->safe_float($market, 'max_price'),
                    ),
                    'cost' => array (
                        'min' => $this->safe_float($market, 'min_amount'),
                        'max' => $this->safe_float($market, 'max_amount'),
                    ),
                ),
                'precision' => array (
                    'amount' => 8,
                    'price' => 8,
                ),
                'info' => $market,
            );
        }
        return $result;
    }

    public function fetch_balance ($params = array ()) {
        $this->load_markets();
        $response = $this->privatePostUserInfo ();
        $result = array ( 'info' => $response );
        $currencies = is_array ($this->currencies) ? array_keys ($this->currencies) : array ();
        for ($i = 0; $i < count ($currencies); $i++) {
            $currency = $currencies[$i];
            $account = $this->account ();
            if (is_array ($response['balances']) && array_key_exists ($currency, $response['balances']))
                $account['free'] = floatval ($response['balances'][$currency]);
            if (is_array ($response['reserved']) && array_key_exists ($currency, $response['reserved']))
                $account['used'] = floatval ($response['reserved'][$currency]);
            $account['total'] = $this->sum ($account['free'], $account['used']);
            $result[$currency] = $account;
        }
        return $this->parse_balance($result);
    }

    public function fetch_order_book ($symbol, $limit = null, $params = array ()) {
        $this->load_markets();
        $market = $this->market ($symbol);
        $request = array_merge (array (
            'pair' => $market['id'],
        ), $params);
        if ($limit !== null)
            $request['limit'] = $limit;
        $response = $this->publicGetOrderBook ($request);
        $result = $response[$market['id']];
        return $this->parse_order_book($result, null, 'bid', 'ask');
    }

    public function fetch_order_books ($symbols = null, $params = array ()) {
        $this->load_markets();
        $ids = null;
        if (!$symbols) {
            $ids = implode (',', $this->ids);
            // max URL length is 2083 $symbols, including http schema, hostname, tld, etc...
            if (strlen ($ids) > 2048) {
                $numIds = is_array ($this->ids) ? count ($this->ids) : 0;
                throw new ExchangeError ($this->id . ' has ' . (string) $numIds . ' $symbols exceeding max URL length, you are required to specify a list of $symbols in the first argument to fetchOrderBooks');
            }
        } else {
            $ids = $this->market_ids($symbols);
            $ids = implode (',', $ids);
        }
        $response = $this->publicGetOrderBook (array_merge (array (
            'pair' => $ids,
        ), $params));
        $result = array ();
        $ids = is_array ($response) ? array_keys ($response) : array ();
        for ($i = 0; $i < count ($ids); $i++) {
            $id = $ids[$i];
            $symbol = $this->find_symbol($id);
            $result[$symbol] = $this->parse_order_book($response[$id], null, 'bid', 'ask');
        }
        return $result;
    }

    public function parse_ticker ($ticker, $market = null) {
        $timestamp = $ticker['updated'] * 1000;
        $symbol = null;
        if ($market)
            $symbol = $market['symbol'];
        $last = $this->safe_float($ticker, 'last_trade');
        return array (
            'symbol' => $symbol,
            'timestamp' => $timestamp,
            'datetime' => $this->iso8601 ($timestamp),
            'high' => $this->safe_float($ticker, 'high'),
            'low' => $this->safe_float($ticker, 'low'),
            'bid' => $this->safe_float($ticker, 'buy_price'),
            'bidVolume' => null,
            'ask' => $this->safe_float($ticker, 'sell_price'),
            'askVolume' => null,
            'vwap' => null,
            'open' => null,
            'close' => $last,
            'last' => $last,
            'previousClose' => null,
            'change' => null,
            'percentage' => null,
            'average' => $this->safe_float($ticker, 'avg'),
            'baseVolume' => $this->safe_float($ticker, 'vol'),
            'quoteVolume' => $this->safe_float($ticker, 'vol_curr'),
            'info' => $ticker,
        );
    }

    public function fetch_tickers ($symbols = null, $params = array ()) {
        $this->load_markets();
        $response = $this->publicGetTicker ($params);
        $result = array ();
        $ids = is_array ($response) ? array_keys ($response) : array ();
        for ($i = 0; $i < count ($ids); $i++) {
            $id = $ids[$i];
            $market = $this->markets_by_id[$id];
            $symbol = $market['symbol'];
            $ticker = $response[$id];
            $result[$symbol] = $this->parse_ticker($ticker, $market);
        }
        return $result;
    }

    public function fetch_ticker ($symbol, $params = array ()) {
        $this->load_markets();
        $response = $this->publicGetTicker ($params);
        $market = $this->market ($symbol);
        return $this->parse_ticker($response[$market['id']], $market);
    }

    public function parse_trade ($trade, $market) {
        $timestamp = $trade['date'] * 1000;
        return array (
            'id' => (string) $trade['trade_id'],
            'info' => $trade,
            'timestamp' => $timestamp,
            'datetime' => $this->iso8601 ($timestamp),
            'symbol' => $market['symbol'],
            'order' => $this->safe_string($trade, 'order_id'),
            'type' => null,
            'side' => $trade['type'],
            'price' => $this->safe_float($trade, 'price'),
            'amount' => $this->safe_float($trade, 'quantity'),
            'cost' => $this->safe_float($trade, 'amount'),
        );
    }

    public function fetch_trades ($symbol, $since = null, $limit = null, $params = array ()) {
        $this->load_markets();
        $market = $this->market ($symbol);
        $response = $this->publicGetTrades (array_merge (array (
            'pair' => $market['id'],
        ), $params));
        return $this->parse_trades($response[$market['id']], $market, $since, $limit);
    }

    public function fetch_my_trades ($symbol = null, $since = null, $limit = null, $params = array ()) {
        $this->load_markets();
        $request = array ();
        $market = null;
        if ($symbol !== null) {
            $market = $this->market ($symbol);
            $request['pair'] = $market['id'];
        }
        $response = $this->privatePostUserTrades (array_merge ($request, $params));
        if ($market !== null)
            $response = $response[$market['id']];
        return $this->parse_trades($response, $market, $since, $limit);
    }

    public function create_order ($symbol, $type, $side, $amount, $price = null, $params = array ()) {
        $this->load_markets();
        $prefix = ($type === 'market') ? ($type . '_') : '';
        $market = $this->market ($symbol);
        if (($type === 'market') && ($price === null)) {
            $price = 0;
        }
        $request = array (
            'pair' => $market['id'],
            'quantity' => $this->amount_to_string($symbol, $amount),
            'type' => $prefix . $side,
            'price' => $this->price_to_precision($symbol, $price),
        );
        $response = $this->privatePostOrderCreate (array_merge ($request, $params));
        $id = $this->safe_string($response, 'order_id');
        $timestamp = $this->milliseconds ();
        $amount = floatval ($amount);
        $price = floatval ($price);
        $status = 'open';
        $order = array (
            'id' => $id,
            'timestamp' => $timestamp,
            'datetime' => $this->iso8601 ($timestamp),
            'lastTradeTimestamp' => null,
            'status' => $status,
            'symbol' => $symbol,
            'type' => $type,
            'side' => $side,
            'price' => $price,
            'cost' => $price * $amount,
            'amount' => $amount,
            'remaining' => $amount,
            'filled' => 0.0,
            'fee' => null,
            'trades' => null,
        );
        $this->orders[$id] = $order;
        return array_merge (array ( 'info' => $response ), $order);
    }

    public function cancel_order ($id, $symbol = null, $params = array ()) {
        $this->load_markets();
        $response = $this->privatePostOrderCancel (array ( 'order_id' => $id ));
        if (is_array ($this->orders) && array_key_exists ($id, $this->orders))
            $this->orders[$id]['status'] = 'canceled';
        return $response;
    }

    public function fetch_order ($id, $symbol = null, $params = array ()) {
        $this->load_markets();
        try {
            $response = $this->privatePostOrderTrades (array (
                'order_id' => (string) $id,
            ));
            return $this->parse_order($response);
        } catch (Exception $e) {
            if ($e instanceof OrderNotFound) {
                if (is_array ($this->orders) && array_key_exists ($id, $this->orders))
                    return $this->orders[$id];
            }
        }
        throw new OrderNotFound ($this->id . ' fetchOrder order $id ' . (string) $id . ' not found in cache.');
    }

    public function fetch_order_trades ($id, $symbol = null, $since = null, $limit = null, $params = array ()) {
        $market = null;
        if ($symbol !== null)
            $market = $this->market ($symbol);
        $response = $this->privatePostOrderTrades (array (
            'order_id' => (string) $id,
        ));
        return $this->parse_trades($response, $market, $since, $limit);
    }

    public function update_cached_orders ($openOrders, $symbol) {
        // update local cache with open orders
        for ($j = 0; $j < count ($openOrders); $j++) {
            $id = $openOrders[$j]['id'];
            $this->orders[$id] = $openOrders[$j];
        }
        $openOrdersIndexedById = $this->index_by($openOrders, 'id');
        $cachedOrderIds = is_array ($this->orders) ? array_keys ($this->orders) : array ();
        for ($k = 0; $k < count ($cachedOrderIds); $k++) {
            // match each cached $order to an $order in the open orders array
            // possible reasons why a cached $order may be missing in the open orders array:
            // - $order was closed or canceled -> update cache
            // - $symbol mismatch (e.g. cached BTC/USDT, fetched ETH/USDT) -> skip
            $id = $cachedOrderIds[$k];
            $order = $this->orders[$id];
            if (!(is_array ($openOrdersIndexedById) && array_key_exists ($id, $openOrdersIndexedById))) {
                // cached $order is not in open orders array
                // if we fetched orders by $symbol and it doesn't match the cached $order -> won't update the cached $order
                if ($symbol !== null && $symbol !== $order['symbol'])
                    continue;
                // $order is cached but not present in the list of open orders -> mark the cached $order as closed
                if ($order['status'] === 'open') {
                    $order = array_merge ($order, array (
                        'status' => 'closed', // likewise it might have been canceled externally (unnoticed by "us")
                        'cost' => null,
                        'filled' => $order['amount'],
                        'remaining' => 0.0,
                    ));
                    if ($order['cost'] == null) {
                        if ($order['filled'] != null)
                            $order['cost'] = $order['filled'] * $order['price'];
                    }
                    $this->orders[$id] = $order;
                }
            }
        }
        return $this->to_array($this->orders);
    }

    public function fetch_orders ($symbol = null, $since = null, $limit = null, $params = array ()) {
        $this->load_markets();
        $response = $this->privatePostUserOpenOrders ($params);
        $marketIds = is_array ($response) ? array_keys ($response) : array ();
        $orders = array ();
        for ($i = 0; $i < count ($marketIds); $i++) {
            $marketId = $marketIds[$i];
            $market = null;
            if (is_array ($this->markets_by_id) && array_key_exists ($marketId, $this->markets_by_id))
                $market = $this->markets_by_id[$marketId];
            $parsedOrders = $this->parse_orders($response[$marketId], $market);
            $orders = $this->array_concat($orders, $parsedOrders);
        }
        $this->update_cached_orders ($orders, $symbol);
        return $this->filter_by_symbol_since_limit($this->to_array($this->orders), $symbol, $since, $limit);
    }

    public function fetch_open_orders ($symbol = null, $since = null, $limit = null, $params = array ()) {
        $this->fetch_orders($symbol, $since, $limit, $params);
        $orders = $this->filter_by($this->orders, 'status', 'open');
        return $this->filter_by_symbol_since_limit($orders, $symbol, $since, $limit);
    }

    public function fetch_closed_orders ($symbol = null, $since = null, $limit = null, $params = array ()) {
        $this->fetch_orders($symbol, $since, $limit, $params);
        $orders = $this->filter_by($this->orders, 'status', 'closed');
        return $this->filter_by_symbol_since_limit($orders, $symbol, $since, $limit);
    }

    public function parse_order ($order, $market = null) {
        $id = $this->safe_string($order, 'order_id');
        $timestamp = $this->safe_integer($order, 'created');
        if ($timestamp !== null)
            $timestamp *= 1000;
        $iso8601 = null;
        $symbol = null;
        $side = $this->safe_string($order, 'type');
        if ($market === null) {
            $marketId = null;
            if (is_array ($order) && array_key_exists ('pair', $order)) {
                $marketId = $order['pair'];
            } else if ((is_array ($order) && array_key_exists ('in_currency', $order)) && (is_array ($order) && array_key_exists ('out_currency', $order))) {
                if ($side === 'buy')
                    $marketId = $order['in_currency'] . '_' . $order['out_currency'];
                else
                    $marketId = $order['out_currency'] . '_' . $order['in_currency'];
            }
            if (($marketId !== null) && (is_array ($this->markets_by_id) && array_key_exists ($marketId, $this->markets_by_id)))
                $market = $this->markets_by_id[$marketId];
        }
        $amount = $this->safe_float($order, 'quantity');
        if ($amount === null) {
            $amountField = ($side === 'buy') ? 'in_amount' : 'out_amount';
            $amount = $this->safe_float($order, $amountField);
        }
        $price = $this->safe_float($order, 'price');
        $cost = $this->safe_float($order, 'amount');
        $filled = 0.0;
        $trades = array ();
        $transactions = $this->safe_value($order, 'trades');
        $feeCost = null;
        if ($transactions !== null) {
            if (gettype ($transactions) === 'array' && count (array_filter (array_keys ($transactions), 'is_string')) == 0) {
                for ($i = 0; $i < count ($transactions); $i++) {
                    $trade = $this->parse_trade($transactions[$i], $market);
                    if ($id === null)
                        $id = $trade['order'];
                    if ($timestamp === null)
                        $timestamp = $trade['timestamp'];
                    if ($timestamp > $trade['timestamp'])
                        $timestamp = $trade['timestamp'];
                    $filled .= $trade['amount'];
                    if ($feeCost === null)
                        $feeCost = 0.0;
                    // $feeCost .= $trade['fee']['cost'];
                    if ($cost === null)
                        $cost = 0.0;
                    $cost .= $trade['cost'];
                    $trades[] = $trade;
                }
            }
        }
        if ($timestamp !== null)
            $iso8601 = $this->iso8601 ($timestamp);
        $remaining = null;
        if ($amount !== null)
            $remaining = $amount - $filled;
        $status = $this->safe_string($order, 'status'); // in case we need to redefine it for canceled orders
        if ($filled >= $amount)
            $status = 'closed';
        else
            $status = 'open';
        if ($market === null)
            $market = $this->get_market_from_trades ($trades);
        $feeCurrency = null;
        if ($market !== null) {
            $symbol = $market['symbol'];
            $feeCurrency = $market['quote'];
        }
        if ($cost === null) {
            if ($price !== null)
                $cost = $price * $filled;
        } else if ($price === null) {
            if ($filled > 0)
                $price = $cost / $filled;
        }
        $fee = array (
            'cost' => $feeCost,
            'currency' => $feeCurrency,
        );
        return array (
            'id' => $id,
            'datetime' => $iso8601,
            'timestamp' => $timestamp,
            'lastTradeTimestamp' => null,
            'status' => $status,
            'symbol' => $symbol,
            'type' => 'limit',
            'side' => $side,
            'price' => $price,
            'cost' => $cost,
            'amount' => $amount,
            'filled' => $filled,
            'remaining' => $remaining,
            'trades' => $trades,
            'fee' => $fee,
            'info' => $order,
        );
    }

    public function get_market_from_trades ($trades) {
        $tradesBySymbol = $this->index_by($trades, 'pair');
        $symbols = is_array ($tradesBySymbol) ? array_keys ($tradesBySymbol) : array ();
        $numSymbols = is_array ($symbols) ? count ($symbols) : 0;
        if ($numSymbols === 1)
            return $this->markets[$symbols[0]];
        return null;
    }

    public function calculate_fee ($symbol, $type, $side, $amount, $price, $takerOrMaker = 'taker', $params = array ()) {
        $market = $this->markets[$symbol];
        $rate = $market[$takerOrMaker];
        $cost = floatval ($this->cost_to_precision($symbol, $amount * $rate));
        $key = 'quote';
        if ($side === 'sell') {
            $cost *= $price;
        } else {
            $key = 'base';
        }
        return array (
            'type' => $takerOrMaker,
            'currency' => $market[$key],
            'rate' => $rate,
            'cost' => floatval ($this->fee_to_precision($symbol, $cost)),
        );
    }

    public function withdraw ($currency, $amount, $address, $tag = null, $params = array ()) {
        $this->load_markets();
        $request = array (
            'amount' => $amount,
            'currency' => $currency,
            'address' => $address,
        );
        if ($tag !== null)
            $request['invoice'] = $tag;
        $result = $this->privatePostWithdrawCrypt (array_merge ($request, $params));
        return array (
            'info' => $result,
            'id' => $result['task_id'],
        );
    }

    public function sign ($path, $api = 'public', $method = 'GET', $params = array (), $headers = null, $body = null) {
        $url = $this->urls['api'] . '/' . $this->version . '/' . $path;
        if ($api === 'public') {
            if ($params)
                $url .= '?' . $this->urlencode ($params);
        } else {
            $this->check_required_credentials();
            $nonce = $this->nonce ();
            $body = $this->urlencode (array_merge (array ( 'nonce' => $nonce ), $params));
            $headers = array (
                'Content-Type' => 'application/x-www-form-urlencoded',
                'Key' => $this->apiKey,
                'Sign' => $this->hmac ($this->encode ($body), $this->encode ($this->secret), 'sha512'),
            );
        }
        return array ( 'url' => $url, 'method' => $method, 'body' => $body, 'headers' => $headers );
    }

    public function nonce () {
        return $this->milliseconds ();
    }

    public function handle_errors ($httpCode, $reason, $url, $method, $headers, $body) {
        if (gettype ($body) != 'string')
            return; // fallback to default error handler
        if (strlen ($body) < 2)
            return; // fallback to default error handler
        if (($body[0] === '{') || ($body[0] === '[')) {
            $response = json_decode ($body, $as_associative_array = true);
            if (is_array ($response) && array_key_exists ('result', $response)) {
                //
                //     array ("result":false,"error":"Error 50052 => Insufficient funds")
                //
                $success = $this->safe_value($response, 'result', false);
                if (gettype ($success) == 'string') {
                    if (($success === 'true') || ($success === '1'))
                        $success = true;
                    else
                        $success = false;
                }
                if (!$success) {
                    $code = null;
                    $message = $this->safe_string($response, 'error');
                    $errorParts = explode (':', $message);
                    $numParts = is_array ($errorParts) ? count ($errorParts) : 0;
                    if ($numParts > 1) {
                        $errorSubParts = explode (' ', $errorParts[0]);
                        $numSubParts = is_array ($errorSubParts) ? count ($errorSubParts) : 0;
                        $code = ($numSubParts > 1) ? $errorSubParts[1] : $errorSubParts[0];
                    }
                    $feedback = $this->id . ' ' . $this->json ($response);
                    $exceptions = $this->exceptions;
                    if (is_array ($exceptions) && array_key_exists ($code, $exceptions)) {
                        throw new $exceptions[$code] ($feedback);
                    } else {
                        throw new ExchangeError ($feedback);
                    }
                }
            }
        }
    }
}
