import os

from binance.client import Client
from binance.enums import *
from binance.exceptions import BinanceAPIException, BinanceOrderException

# init
api_key = os.environ.get('binance_api')
api_secret = os.environ.get('binance_secret')

client = Client(api_key, api_secret)

## main

# create order

# make a test order first. This will raise an exception if the order is incorrect.
# buy_order_limit = client.create_test_order(
# 	symbol='FLOWUSDT',
# 	side='BUY',
# 	type='LIMIT',
# 	timeInForce='GTC',
# 	quantity=1,
# 	price=7.6)

# buy_order = client.create_test_order(symbol='FLOWUSDT', side='BUY', type='MARKET', quantity=1)

# create a real order if the test orders did not raise an exception
try:
	# buy_limit = client.create_order(
	# 	symbol='FLOWUSDT',
	# 	side='BUY',
	# 	type='LIMIT',
	# 	timeInForce='GTC',
	# 	quantity=1,
	# 	price=7.6)

	# order = client.order_market_buy(symbol='FLOWUSDT', quantity=5, quoteOrderQty)
    order = client.order_market_buy(symbol='FLOWUSDT', quoteOrderQty=10.0)

	# order = client.order_market_sell(symbol='BNBUSDT', quantity=0.1)

	# same order but with helper function
	# buy_limit = client.order_limit_buy(symbol='FLOWUSDT', quantity=1, price=7.6)

	# market order using a helper function
	# market_order = client.order_market_sell(symbol='FLOWUSDT', quantity=1)

	# cancel previous orders
	# cancel = client.cancel_order(symbol='FLOWUSDT', orderId=buy_limit['orderId'])
except BinanceAPIException as e:
	# error handling goes here
	print(e)
except BinanceOrderException as e:
	# error handling goes here
	print(e)

# using binance constants - the library has hard coded commonly used strings
# https://python-binance.readthedocs.io/en/latest/constants.html#

# this order uses required strings such as 'BUY' and 'MARKET' which are prone to spelling errors
# buy_order = client.create_test_order(symbol='ETHUSDT', side='BUY', type='MARKET', quantity=100)

# binance constants can be used instead
# buy_order = client.create_test_order(symbol='ETHUSDT', side=SIDE_BUY, type=ORDER_TYPE_MARKET, quantity=100)
