import os

from binance.client import Client
import pandas as pd


# import datetime
import time
from datetime import datetime, timedelta, timezone

# init
api_key = os.environ.get('binance_api')
api_secret = os.environ.get('binance_secret')

client = Client(api_key, api_secret)


# functions

def topup_bnb(min_balance: float, topup: float):
	''' Top up BNB balance if it drops below minimum specified balance '''
	bnb_balance = client.get_asset_balance(asset='BNB')
	bnb_balance = float(bnb_balance['free'])
	if bnb_balance < min_balance:
		qty = round(topup - bnb_balance, 5)
		print(qty)
		order = client.order_market_buy(symbol='BNBUSDT', quantity=qty)
		return order
	return False


# example
min_balance = 1.0
topup = 2.5
#order = topup_bnb(min_balance, topup)

def check_price(pair):
    ## main
    tries = 5
    for i in range(tries):
              try:
                 # do stuff
                 candles = client.get_klines(symbol=pair, interval=Client.KLINE_INTERVAL_15MINUTE)
              except:
                 time.sleep(3)
                 continue
              break

    # candles = client.get_klines(symbol=pair, interval=interval)
    for line in candles:
        del line[6:]
    candles_df = pd.DataFrame(candles, columns=['date', 'open', 'high', 'low', 'close', 'volume'])
    # candles_df.set_index('date', inplace=True)

    candles_df.set_index('date', inplace=True)
    candles_df.index = pd.to_datetime(candles_df.index, unit='ms')
    # print(candles_df.head())
    return candles_df

def check_btc_price():
    ## main
    
    candles = client.get_klines(symbol='BTCUSDT', interval=Client.KLINE_INTERVAL_1DAY)
    # candles = client.get_klines(symbol=pair, interval=interval)
    for line in candles:
    	del line[6:]
    candles_df = pd.DataFrame(candles, columns=['date', 'open', 'high', 'low', 'close', 'volume'])
    # candles_df.set_index('date', inplace=True)

    candles_df.set_index('date', inplace=True)
    candles_df.index = pd.to_datetime(candles_df.index, unit='ms')
    # print(candles_df.head())

    last_row_df = candles_df.iloc[-1:]
    close = float(last_row_df['close'].iloc[0])
    open = float(last_row_df['open'].iloc[0])
    
    
    return close > open 

# pair ='FTMUSDT'
# symbol = pair[:-4]
# print(symbol)
# bnb_balance = client.get_asset_balance(asset=symbol)
# bnb_balance = float(bnb_balance['free'])
# print(bnb_balance)

# print(check_btc_price())


check_price('FLOWUSDT')
# check_day_price('FLOWUSDT')
