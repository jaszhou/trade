import csv
import json
import os
import operator
import pandas as pd
from binance.client import Client
import requests.exceptions

from get_list import *
import sys
from wilders_rsi_pandas import pandas_rsi
# import logging
# import datetime
import time
from datetime import datetime, timedelta, timezone
from binance.exceptions import BinanceAPIException, BinanceOrderException
# from threading import Thread,threading
import threading
from time import sleep

from binance import ThreadedWebsocketManager
import random
from record import *
import math

current_thread_number = 0  #global variable
max_threads = 5
random.seed(10)
max_hold_minutes = 60*12   # max holding time in minutes
# init
api_key = os.environ.get('binance_api')
api_secret = os.environ.get('binance_secret')

profit=0.05

# set the amount by checking the current balance of FLOW
f_balance = retry(get_flow_balance, max_tries=10)

amount = 0
if f_balance:
    amount= f_balance * 10  # the amount for each order

winner=0

# set threshold for winner_score, the formula is:
# if v > 0 and v2 >0 and vol_ratio2 > 1 and check_day_price(pair):
WINNER_SCORE_THRESHOLD=0.5
winner_score=WINNER_SCORE_THRESHOLD

winner_pair=""
buy_price=0

client = Client(api_key, api_secret)

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
    close = float(last_row_df['close'])
    open = float(last_row_df['open'])
    
    
    return close > open 


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

    for line in candles:
        del line[6:]
    candles_df = pd.DataFrame(candles, columns=['date', 'open', 'high', 'low', 'close', 'volume'])
    # candles_df.set_index('date', inplace=True)

    candles_df.set_index('date', inplace=True)
    candles_df.index = pd.to_datetime(candles_df.index, unit='ms')
    # print(candles_df.head())
    return candles_df

def check_day_price(pair):
    ## main
    tries = 5
    for i in range(tries):
              try:
                 # do stuff
                 candles = client.get_klines(symbol=pair, interval=Client.KLINE_INTERVAL_1DAY)
              except:
                 #client = Client(api_key, api_secret)
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

    last_row_df = candles_df.iloc[-1:]
    close = float(last_row_df['close'])
    open = float(last_row_df['open'])
    
    
    return close > open 


def get_pair_balance(pair):
    # pair ='FTMUSDT'
    symbol = pair[:-4]
    # print(symbol)
    bnb_balance = client.get_asset_balance(asset=symbol)
    bnb_balance = float(bnb_balance['free'])
    # print(bnb_balance)
    return bnb_balance    

def get_balance():
    # pair ='FTMUSDT'
    symbol = 'USDT'
    # print(symbol)
    bnb_balance = client.get_asset_balance(asset=symbol)
    bnb_balance = float(bnb_balance['free'])
    # print(bnb_balance)
    return bnb_balance    



def convert_timestamp_to_datetime(timestamp):
    """
    Convert a timestamp to a datetime object.
    
    Args:
        timestamp (int): The timestamp to convert.
        
    Returns:
        datetime: The corresponding datetime object.
    """
    # Convert timestamp to seconds (if it's in milliseconds)
    timestamp_in_seconds = timestamp / 1000
    
    # Convert to datetime object
    return datetime.fromtimestamp(timestamp_in_seconds)

def check_expire(sell_by_time: datetime):
    current = time.time()
    return sell_by_time < current

# check price from time to time, if reach profit level, sell it
def sell(pair,open_price,profit,amount,sell_by_time):
    # print("Total score for {n} is {s}".format(n=name, s=score))
     print("Pair {p} open price {o} profit {e} amount {a} sell by {s}".format(p=pair, o=open_price, e=profit, a=amount, s=sell_by_time))

     while True:
         price = client.get_symbol_ticker(symbol=pair)
         close = float(price["price"])

         # print("{t} --- buying {p} at price {c} with target {tg}".format(t=datetime.today(),p=pair, c=open_price, tg=target))
     
         target = open_price * (1+profit)
         rsi = RSI(pair)
         trend = get_trend(pair)

         print("{d} -- {p} price {c} rsi {r} buy price {b} target {tg} trend {trend}".format(d=datetime.today(), p=pair, c=round(close,4), r=rsi, b=round(open_price,4), tg=round(target,4), trend=trend))

        #  print("current price {p}".format(p=close))
         balance = get_pair_balance(pair)
         if balance == 0:
             print("manual override, skipping...")
             break
         
         
         if ((close-open_price)/open_price > profit) or check_expire(sell_by_time):
        #  if (close-open_price)/open_price > profit and rsi > 80 :
         #if abs(close-open_price)/open_price > profit and trend == "down" :
        #  if (close-open_price)/open_price > profit and trend == "down" :
             #ready to sell

            
            #  print("selling pair {p} rsi {r}".format(p=pair, r=rsi))
             print("----------->  selling pair {p}".format(p=pair))
             print("balance to sell:",balance)
             
             order = client.order_market_sell(symbol=pair, quantity=balance)

            #  target = open_price * (1+profit)
            #  client.order_limit_sell(symbol=pair, quantity=get_pair_balance(pair),price=target)
             
             print("----------->  selling pair {p}".format(p=pair))

             break  # break of sell loop
         else:
            time.sleep(60*5)




def check(pair,interval):

    # check if bought twice
    if get_trade(pair) > 1:
        print(f"already bought twice {pair}, skipping ...")
        return 
    
    #skip existing pairs

    if get_pair_balance(pair) > 0 :
        return
        

    # date=datetime.today()
    # last = date - timedelta(days=1)

    # timestamp = datetime.timestamp(last)


    """
    [
    [
        1591258320000,          // Open time
        "9640.7",               // Open
        "9642.4",               // High
        "9640.6",               // Low
        "9642.0",               // Close (or latest price)
        "206",                  // Volume
        1591258379999,          // Close time
        "2.13660389",           // Base asset volume
        48,                     // Number of trades
        "119",                  // Taker buy volume
        "1.23424865",           // Taker buy base asset volume
        "0"                     // Ignore.
    ]
    ]
    """

    # klines = client.get_historical_klines(pair, 
    # Client.KLINE_INTERVAL_15MINUTE, "20 minute ago UTC")

    time_span="1 hour ago UTC"

    # request historical candle (or klines) data
    # bars = client.get_historical_klines(pair, interval, str(timestamp), limit=5)
    bars = client.get_historical_klines(pair, interval, time_span, limit=5)
    
    for line in bars:
        del line[6:]

    # option 4 - create a Pandas DataFrame and export to CSV
    df = pd.DataFrame(bars, columns=['date', 'open', 'high', 'low', 'close', 'volume'])
    
    df.set_index('date', inplace=True)
    df.index = pd.to_datetime(df.index, unit='ms')

    # df = btc_df

    # Select last row of the dataframe as a dataframe object
    last_row_df = df.iloc[-1:]

    # print(last_row_df)

    last_two_df = df.iloc[-2:-1]

    # print(last_two_df)

    # Select last row of the dataframe as a dataframe object
    last_three_df = df.iloc[-3:-2]
   

    close = float(last_row_df['close'])
    low = float(last_row_df['low'])
    high = float(last_row_df['high'])
    open_price = float(last_row_df['open'])

    close2 = float(last_two_df['close'])
    low2 = float(last_two_df['low'])
    high2 = float(last_two_df['high'])
    open_price2 = float(last_two_df['open'])

    close3 = float(last_three_df['close'])
    low3 = float(last_three_df['low'])
    high3 = float(last_three_df['high'])
    open_price3 = float(last_three_df['open'])

    # last_volume=float(last_row_df['volume'])
    last_two_volume=float(last_two_df['volume'])
    last_three_volume=float(last_three_df['volume'])
    today_volume = float(last_row_df['volume'])

    # head = abs(high-close)
    # tail = abs(close-low)
    if last_two_volume > 1000:
       vol_ratio = today_volume / last_two_volume
    else:
        vol_ratio = 0.1

    # last 2
    if last_three_volume > 1000:
       vol_ratio2 = last_two_volume / last_three_volume
    else:
        vol_ratio2 = 0.1

    v = (close - open_price) / open_price
    v2 = (close2 - open_price2) / open_price2  # last two
    v3 = (close3 - open_price3) / open_price3
    
    # score = v * vol_ratio + v2 * vol_ratio2
    # score = v2 * vol_ratio2
    score = v * vol_ratio * 100 + v2 * vol_ratio2 * 100

    trend = check_btc_price()
    print(f"Score:{score} v: {v} v2 {v2} vol_ratio: {vol_ratio} vol_ratio2: {vol_ratio2} check_day_price: {trend}")

    r = RSI(pair)

    ################################################################
    # buying condition here
    ################################################################

    # if v > 0 and v2 >0 and v3 > 0 and vol_ratio > 1 and vol_ratio2 > 1  and r < 90 :
    #if v > 0 and v2 >0 and v3 > 0 and vol_ratio > 2 and vol_ratio2 > 1 and check_day_price(pair) :
    if v > 0 and v2 >0 and vol_ratio2 > 1 and trend:
    # if v > 0 and v2 >0 and vol_ratio2 > 1 and check_day_price(pair) and r < 90:
        print("***************************************")
        # profit=0.05
        my_open_price=close
        # amount=20

        target=my_open_price*(1+profit)
        print(f"Alerting {pair} with score {score}")	
        print(f"v {v} vol_ratio {vol_ratio} v2 {v2} vol_ratio2 {vol_ratio2} score {score}")

        # print("{t} --- buying {p} at price {c} with target {tg}".format(t=datetime.today(),p=pair, c=open_price, tg=target))
        # order = client.order_market_buy(symbol=pair, quoteOrderQty=amount)

        # sell(pair,open_price,profit,amount)
        global winner_score
        global winner_pair
        global winner
        global buy_price
        global sell_by_time
        

        symbol = pair[:-4]
        if score > winner_score and get_balance_all(symbol) < 1:
            print("winning score: {w} winner: {win} winning pair:{p}".format(w=winner_score, win=winner,p=pair))

            winner_score = score
            buy_price = close
            winner_pair = pair
            winner = winner + 1
            # print("winner pair {p} length {l}".format(p=winner_pair, l=len(winner_pair)))

            # check_price(winner_pair)
        # print("***************************************")
        
        # exit

    # print("-------------------------------------")
    # time.sleep(1)

def RSI(pair):

    
    # print("pair {p} length {l}".format(p=pair, l=len(pair)))

    
    df = check_price(pair)
    df = df.astype({'close':'float'})

    rsi = pandas_rsi(df)

    
    return rsi.iloc[-1]['rsi']

def start(threadname):
        global current_thread_number,winner,winner_pair,winner_score,amount,max_threads

        current_thread_number+=1
        print(f"thread name is {threadname} current thread number is {current_thread_number}")
        # logging.info(f"thread name is {threadname} current thread number is {current_thread_number}")

        
        # if amount > 0 :
        # if check_btc_price() and amount > 0 and get_USDT_balance() > 2000 :
        if check_btc_price() and amount > 0 and get_balance() > 100 :

            #refresh list
            get_gainer()
            print('refresh list')

            pair_df = pd.read_csv('trade_pair.csv', index_col=0)
            pair_df = pair_df.reset_index()  # make sure indexes pair with number of rows
            n = 0
            total = len(pair_df)

            for index, row in pair_df.iterrows():
                pair=row['symbol']
                n = n + 1
                per = (n / total) * 100 
                my_formatter = "{0:.1f}"
                per = my_formatter.format(per)

                print("{t} -  checking pair {p} #{num} with {per}% completed".format(t=threadname,p=pair, num=n, per=per))

                tries = 5
                for i in range(tries):
                    try:
                        # do stuff
                        check(pair,'15m')
                    except:
                        time.sleep(1)
                        continue
                    break
               
                print("winning score: {w} winner: {win} winning pair:{p} btc: {b}".format(w=winner_score, win=winner,p=winner_pair,b=check_btc_price()))
            
            
            if winner > 0 and check_btc_price() :
                # symbol = winner_pair[:-4]
                # if get_balance_all(symbol) < 1  :
                    # print("winner pair {p} already bought, skipping ...".format(p=winner_pair))
                    # if winner > 0:
                    r = RSI(winner_pair)
                    # print("winner pair {p} rsi {r}".format(p=winner_pair, r=r))

                    if r < 200:
                        print("{t} --- buying {p} for amount {a}".format(t=datetime.today(),p=winner_pair,a=amount))
                        
                        # record active pairs, if it's the second times, then don't buy it again
                        add_trade(winner_pair)

                        winner = 0
                        # global winner_score
                        winner_score = WINNER_SCORE_THRESHOLD

                        order = client.order_market_buy(symbol=winner_pair, quoteOrderQty=amount)
                        

                        # end of holding period
                        sell_by_time = datetime.now() + timedelta(minutes=max_hold_minutes) 
                        
                        sell(winner_pair,buy_price,profit,amount,sell_by_time)
                        # client.order_limit_sell(symbol=symbol, quantity=get_pair_balance(winner_pair),price=target)
            else:
                winner = 0
                winner_score = WINNER_SCORE_THRESHOLD
                winner_pair = ""

                print("no winner and sleep for 1 min")
                time.sleep(60) 
            
        else:
            winner = 0
            winner_score = WINNER_SCORE_THRESHOLD
            winner_pair = ""

            st = math.ceil(100*random.random())
            print(f"Sleep for {st} seconds, BTC is down or FLOW balance is 0")
            # time.sleep(60)
            time.sleep(st)
    
        current_thread_number-=1


# main entry here
if __name__ == "__main__":
    # volume_dollar('BNBUSDT')

    while True:
            
            # threads = []
            # threading.active_count()
            # while current_thread_number < max_threads :
            flow_balance = retry(get_flow_balance)
            print(f'flow balance: {flow_balance}')

            amount = 0
            if flow_balance:
                amount= flow_balance * 10  # the amount for each order

            icp_balance = retry(get_icp_balance)
            print(f'icp balance: {icp_balance}')
            if icp_balance:
                max_threads = icp_balance
            

            winner=0
            winner_score=WINNER_SCORE_THRESHOLD
            winner_pair=""
            buy_price=0

            # refresh list every 10 minutes
            print('get gainer')
            get_gainer()
            # time.sleep(60)

            print(f'max threads: {max_threads}')
            while threading.active_count() < max_threads :
        
                thread = threading.Thread(target=start, args=("Thead-"+str(current_thread_number), ) )
                thread.start()
                print(f"active count is {threading.active_count()} max thread {max_threads}")
            
                st = math.ceil(50*random.random())
                print(f'sleep for {st} seconds')
                time.sleep(st)
                

            # time.sleep(60*10)
            # print(f"current thread number is {current_thread_number} and active count is {threading.active_count()}")
            