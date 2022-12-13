from binance.client import Client
import pandas as pd
import os
import csv

from binance.enums import *
from binance.exceptions import BinanceAPIException, BinanceOrderException

from threading import Thread
import time

import random



api_key = os.environ.get('binance_api')
api_secret = os.environ.get('binance_secret')


client = Client(api_key, api_secret)

current_thread_number = 0  #global variable
max_threads = 5


random.seed(10)


def get_usdt_pairs(num=30):


    symbols = client.get_ticker()
    df = pd.DataFrame(symbols)
    df = df[df.symbol.str.contains('USDT')]
    
    df = df.astype({'priceChangePercent':'float'})


    df = df.sort_values(by="priceChangePercent", ascending=False)
 
    df = df['symbol']
    df.head(num).to_csv('trade_pair.csv', index=False)


def get_gainer():

    get_usdt_pairs(num=100)


def get_flow_balance():
    balance = client.get_asset_balance(asset="FLOW")
    balance = float(balance['free'])
    # print(bnb_balance)
    return balance

def get_flow_balance_thread(threadname):
    global current_thread_number
    current_thread_number+=1
    print(f"thread name is {threadname} current thread number is {current_thread_number}")

    
    print(random.random())

    balance = client.get_asset_balance(asset="FLOW")
    balance = float(balance['free'])
    print(balance)

    # time.sleep(10*random.random())

    current_thread_number-=1

    return balance
# get_gainer()    

def get_icp_balance_thread(threadname):
    global current_thread_number
    current_thread_number+=1
    print(f"thread name is {threadname} current thread number is {current_thread_number}")

    
    print(random.random())

    balance = client.get_asset_balance(asset="FLOW")
    balance = float(balance['free'])
    print(balance)

    # time.sleep(10*random.random())

    current_thread_number-=1

    return balance

#get_usdt_pairs()
#print("flow balance is: {b}".format(b=get_flow_balance()))

while True:

        # threads = []
        while current_thread_number < max_threads :
            thread = Thread( target=get_flow_balance_thread, args=("Thread-1", ) )
            thread.start()
            # threads.append(thread)
            
        # for thread in threads:
        #     thread.join()

        time.sleep(5)
        print(f"current thread number is {current_thread_number}")
        
        
        

# thread1 = Thread( target=get_flow_balance_thread, args=("Thread-1", ) )
# thread2 = Thread( target=get_flow_balance_thread, args=("Thread-2", ) )

# thread1.start()
# thread2.start()

# thread.join()
# thread2.join()
