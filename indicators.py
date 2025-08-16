

import pandas as pd
import time
import os

from binance.client import Client
from wilders_rsi_pandas import pandas_rsi

import requests.exceptions

API_KEY = os.environ.get("API_KEY")
API_SECRET = os.environ.get("API_SECRET")
client = Client(API_KEY, API_SECRET, tld='us')

def RSI(pair):

    # load DataFrame
    # btc_df = pd.read_csv('btc_bars3.csv', index_col=0)
    # # btc_df.set_index('date', inplace=True)
    # btc_df.index = pd.to_datetime(btc_df.index, unit='ms')
    print("pair {p} length {l}".format(p=pair, l=len(pair)))

    
    candles = client.get_klines(symbol=pair, interval=Client.KLINE_INTERVAL_15MINUTE, limit=20)
    # candles = client.get_klines(symbol=pair, interval=Client.KLINE_INTERVAL_15MINUTE)
    

    # candles = client.get_klines(symbol=pair, interval=interval)
    for line in candles:
        del line[6:]
    candles_df = pd.DataFrame(candles, columns=['date', 'open', 'high', 'low', 'close', 'volume'])
    # candles_df.set_index('date', inplace=True)

    candles_df.set_index('date', inplace=True)
    candles_df.index = pd.to_datetime(candles_df.index, unit='ms')


    # btc_df.close = btc_df.close.astype(float)
    candles_df = candles_df.astype({'close':'float'})

    rsi = pandas_rsi(candles_df)

    
    return rsi.iloc[-1]['rsi']

# r = RSI('FLOWUSDT')
# print(r)

def volume_dollar(pair):

    # load DataFrame
    # btc_df = pd.read_csv('btc_bars3.csv', index_col=0)
    # # btc_df.set_index('date', inplace=True)
    # btc_df.index = pd.to_datetime(btc_df.index, unit='ms')
    print("pair {p} length {l}".format(p=pair, l=len(pair)))

    
    candles = client.get_klines(symbol=pair, interval=Client.KLINE_INTERVAL_1DAY, limit=2)
    # candles = client.get_klines(symbol=pair, interval=Client.KLINE_INTERVAL_15MINUTE)
    


    # candles = client.get_klines(symbol=pair, interval=interval)
    for line in candles:
        del line[6:]
    candles_df = pd.DataFrame(candles, columns=['date', 'open', 'high', 'low', 'close', 'volume'])
    # candles_df.set_index('date', inplace=True)

    candles_df.set_index('date', inplace=True)
    candles_df.index = pd.to_datetime(candles_df.index, unit='ms')



    # btc_df.close = btc_df.close.astype(float)
    candles_df = candles_df.astype({'close':'float'})

    print(candles_df)
    # rsi.iloc[-1]['rsi']
    # print(type(candles_df.iloc[-1]['close']))
    v=float(candles_df.iloc[-1]['volume'])
    # print(type(int(candles_df.iloc[-1]['volume'])))

    # v = candles_df.iloc[-1]['volume']
    c = float(candles_df.iloc[-1]['close'])
    a = v * c 

    print(f'close {c} volume {v}')

    print(f'amount: {a}')

def get_metrics():
#    client.get
   print("hello")


if __name__ == "__main__":
    volume_dollar('BNBUSDT')