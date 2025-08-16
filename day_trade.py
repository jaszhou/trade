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
import time
from datetime import datetime, timedelta, timezone
from binance.exceptions import BinanceAPIException, BinanceOrderException
import threading
from time import sleep
from binance import ThreadedWebsocketManager
import random
from record import *
import math
import asyncio

MAX_HOLD_MINUTES = 60 * 12
MIN_BALANCE = 100
SLEEP_TIME = 60

class TradeBot:
    def __init__(self):
        self.current_thread_number = 0
        self.max_threads = 5
        random.seed(10)
        self.profit = 0.05
        self.api_key = os.environ.get('binance_api')
        self.api_secret = os.environ.get('binance_secret')
        self.client = Client(self.api_key, self.api_secret)
        self.f_balance = retry(get_flow_balance, max_tries=10)
        self.amount = self.f_balance * 10 if self.f_balance else 0
        self.winner = 0
        self.winner_score = 0.5
        self.winner_pair = ""
        self.buy_price = 0

    def check_btc_price(self):
        ## main
        
        candles = self.client.get_klines(symbol='BTCUSDT', interval=Client.KLINE_INTERVAL_1DAY)
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


    def check_price(self, pair):
        ## main
        tries = 5
        for i in range(tries):
                try:
                    # do stuff
                    candles = self.client.get_klines(symbol=pair, interval=Client.KLINE_INTERVAL_15MINUTE)
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

    def check_day_price(self, pair):
        ## main
        tries = 5
        for i in range(tries):
                try:
                    # do stuff
                    candles = self.client.get_klines(symbol=pair, interval=Client.KLINE_INTERVAL_1DAY)
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
        close = float(last_row_df['close'].iloc[0])
        open = float(last_row_df['open'].iloc[0])
        
        
        return close > open 


    def get_pair_balance(self, pair):
        # pair ='FTMUSDT'
        symbol = pair[:-4]
        # print(symbol)
        bnb_balance = self.client.get_asset_balance(asset=symbol)
        bnb_balance = float(bnb_balance['free'])
        # print(bnb_balance)
        return bnb_balance    

    def get_balance(self):
        # pair ='FTMUSDT'
        symbol = 'USDT'
        # print(symbol)
        bnb_balance = self.client.get_asset_balance(asset=symbol)
        bnb_balance = float(bnb_balance['free'])
        # print(bnb_balance)
        return bnb_balance    



    def convert_timestamp_to_datetime(self, timestamp):
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

    def check_expire(self, sell_by_time: datetime):
        # current = time.time()
        return sell_by_time < datetime.now()

    # check price from time to time, if reach profit level, sell it


    async def sell(self, pair, open_price, profit, amount, sell_by_time):
        while True:
            price = self.client.get_symbol_ticker(symbol=pair)
            close = float(price["price"])

            target = open_price * (1 + profit)
            rsi = self.RSI(pair)
            trend = self.check_btc_price()

            print("{d} -- {p} price {c} rsi {r} buy price {b} target {tg} trend {trend}".format(
                d=datetime.today(), p=pair, c=round(close, 4), r=rsi, b=round(open_price, 4), tg=round(target, 4), trend=trend))
            print("Pair {p} open price {o} profit {e} amount {a} sell by {s}".format(
                p=pair, o=open_price, e=profit, a=amount, s=sell_by_time))

            balance = self.get_pair_balance(pair)
            if balance == 0:
                print("manual override, skipping...")
                break

            if ((close - open_price) / open_price > profit) or self.check_expire(sell_by_time):
                print("----------->  selling pair {p}".format(p=pair))
                print("balance to sell:", balance)

                order = self.client.order_market_sell(symbol=pair, quantity=balance)
                print("----------->  selling pair {p}".format(p=pair))

                break  # break of sell loop
            else:
                await asyncio.sleep(60 * 5)




    async def check(self, pair: str, interval: str, time_span: str, limit: int):
        # check if bought twice
        if get_trade(pair) > 1:
            print(f"already bought twice {pair}, skipping ...")
            return

        # skip existing pairs
        if self.get_pair_balance(pair) > 0:
            return

        bars = self.client.get_historical_klines(symbol=pair, interval=interval, start_str=time_span, limit=limit)
        for line in bars:
            del line[6:]

        df = pd.DataFrame(bars, columns=['date', 'open', 'high', 'low', 'close', 'volume'])
        df.set_index('date', inplace=True)
        df.index = pd.to_datetime(df.index, unit='ms')

        last_row_df = df.iloc[-1:]
        last_two_df = df.iloc[-2:-1]
        last_three_df = df.iloc[-3:-2]

        close = float(last_row_df['close'].iloc[0])
        low = float(last_row_df['low'].iloc[0])
        high = float(last_row_df['high'].iloc[0])
        open_price = float(last_row_df['open'].iloc[0])

        close2 = float(last_two_df['close'].iloc[0])
        low2 = float(last_two_df['low'].iloc[0])
        high2 = float(last_two_df['high'].iloc[0])
        open_price2 = float(last_two_df['open'].iloc[0])

        close3 = float(last_three_df['close'].iloc[0])
        low3 = float(last_three_df['low'].iloc[0])
        high3 = float(last_three_df['high'].iloc[0])
        open_price3 = float(last_three_df['open'].iloc[0])

        last_two_volume = float(last_two_df['volume'].iloc[0])
        last_three_volume = float(last_three_df['volume'].iloc[0])
        today_volume = float(last_row_df['volume'].iloc[0])

        vol_ratio = today_volume / last_two_volume if last_two_volume > 1000 else 0.1
        vol_ratio2 = last_two_volume / last_three_volume if last_three_volume > 1000 else 0.1

        v = (close - open_price) / open_price
        v2 = (close2 - open_price2) / open_price2
        v3 = (close3 - open_price3) / open_price3

        score = v * vol_ratio * 100 + v2 * vol_ratio2 * 100

        trend = self.check_btc_price()
        print(f"Score:{score} v: {v} v2 {v2} vol_ratio: {vol_ratio} vol_ratio2: {vol_ratio2} check_day_price: {trend}")

        r = self.RSI(pair)

        if v > 0 and v2 > 0 and vol_ratio2 > 1 and trend:
            print("***************************************")
            my_open_price = close

            target = my_open_price * (1 + self.profit)
            print(f"Alerting {pair} with score {score}")
            print(f"v {v} vol_ratio {vol_ratio} v2 {v2} vol_ratio2 {vol_ratio2} score {score}")

            symbol = pair[:-4]
            if score > self.winner_score and get_balance_all(symbol) < 1:
                print("winning score: {w} winner: {win} winning pair:{p}".format(w=self.winner_score, win=self.winner, p=pair))

                self.winner_score = score
                self.buy_price = close
                self.winner_pair = pair
                self.winner += 1



    def RSI(self,pair):

        
        # print("pair {p} length {l}".format(p=pair, l=len(pair)))

        
        df = self.check_price(pair)
        df = df.astype({'close':'float'})

        rsi = pandas_rsi(df)

        
        return rsi.iloc[-1]['rsi']

    def reset_winner(self):
        self.winner = 0
        self.winner_score = 0.5
        self.winner_pair = ""



    async def start(self, threadname):
        self.current_thread_number += 1
        print(f"thread name is {threadname} current thread number is {self.current_thread_number}")

        if self.check_btc_price() and self.amount > 0 and self.get_balance() > MIN_BALANCE:
            get_gainer()
            print('refresh list')

            pair_df = pd.read_csv('trade_pair.csv', index_col=0)
            pair_df = pair_df.reset_index()
            n = 0
            total = len(pair_df)

            for index, row in pair_df.iterrows():
                pair = row['symbol']
                n += 1
                per = (n / total) * 100
                print(f"{threadname} - checking pair {pair} #{n} with {per:.1f}% completed")

                tries = 5
                for _ in range(tries):
                    try:
                        interval = '1d'
                        time_span = '5 day ago UTC'
                        limit = 5
                        await self.check(pair=pair, interval=interval, time_span=time_span, limit=limit)
                    except Exception as e:
                        print(f"An error occurred: {e}")
                        time.sleep(1)
                        continue
                    break

                print(f"winning score: {self.winner_score} winner: {self.winner} winning pair: {self.winner_pair} btc: {self.check_btc_price()}")

            if self.winner > 0 and self.check_btc_price():
                r = self.RSI(self.winner_pair)
                if r < 200:
                    print(f"{datetime.today()} --- buying {self.winner_pair} for amount {self.amount}")
                    add_trade(self.winner_pair)
                    self.reset_winner()
                    order = self.client.order_market_buy(symbol=self.winner_pair, quoteOrderQty=self.amount)
                    sell_by_time = datetime.now() + timedelta(minutes=MAX_HOLD_MINUTES)
                    await self.sell(self.winner_pair, self.buy_price, self.profit, self.amount, sell_by_time)
            else:
                self.reset_winner()
                print("no winner and sleep for 1 min")
                await asyncio.sleep(SLEEP_TIME)
        else:
            self.reset_winner()
            st = math.ceil(100 * random.random())
            print(f"Sleep for {st} seconds, BTC is down or FLOW balance is 0")
            await asyncio.sleep(st)

        self.current_thread_number -= 1

async def main():
    bot = TradeBot()

    while True:
        print("********************************")
        print("version: 20250816")
        print("********************************")

        flow_balance = retry(get_flow_balance)
        print(f'flow balance: {flow_balance}')

        bot.amount = flow_balance * 10 if flow_balance else 0

        icp_balance = retry(get_icp_balance)
        print(f'icp balance: {icp_balance}')
        if icp_balance:
            bot.max_threads = round(icp_balance)

        bot.reset_winner()

        print('get gainer')
        get_gainer()

        print(f'max threads: {bot.max_threads}')
        tasks = []
        for i in range(bot.max_threads):
            task = asyncio.create_task(bot.start(f"Task-{i}"))
            tasks.append(task)

        await asyncio.gather(*tasks)

        # print("sleep for 10 minutes")
        # await asyncio.sleep(10 * 60)

if __name__ == "__main__":
    asyncio.run(main())
