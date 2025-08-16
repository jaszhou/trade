import csv
import json
import os

import pandas as pd
from binance.client import Client
# import datetime
import time
from datetime import datetime, timedelta, timezone

# t1 = datetime.now(timezone.utc) # end time
# t0 = t1 - timedelta(10)         # start time

# # if you need UNIX time:
# start_ts, end_ts = t0.timestamp(), t1.timestamp()
# print(start_ts, end_ts)
# 1608972059.652785 1609836059.652785


# init
api_key = os.environ.get('binance_api')
api_secret = os.environ.get('binance_secret')

client = Client(api_key, api_secret)

def check(pair,interval):

	## main
	print("Trading pair:",pair)

	# interval = '1d'

	# valid intervals - 1m, 3m, 5m, 15m, 30m, 1h, 2h, 4h, 6h, 8h, 12h, 1d, 3d, 1w, 1M
	# get timestamp of earliest date data is available
	# timestamp = client._get_earliest_valid_timestamp('BTCUSDT', '1d')
	date=datetime.today()
	start_delta = timedelta(-date.weekday(), weeks=-1)
	print(date)
	last = date - timedelta(days=7)


	# using time module


	# ts stores the time in seconds
	# timestamp = time.time()
	timestamp = datetime.timestamp(last)
	# print the current timestamp
	# print(ts)


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

	# request historical candle (or klines) data
	bars = client.get_historical_klines(pair, interval, str(timestamp), limit=7)
	# print(bars)

	# option 1 - save to file using json method - this will retain Python format (list of lists)
	# with open('btc_bars.json', 'w') as e:
	# 	json.dump(bars, e)

	# option 2 - save as CSV file using the csv writer library
	# with open('btc_bars.csv', 'w', newline='') as f:
	# 	wr = csv.writer(f)
	# 	for line in bars:
	# 		wr.writerow(line)

	# option 3 - save as CSV file without using a library. Shorten to just date, open, high, low, close
	# with open('btc_bars2.csv', 'w') as d:
	# 	for line in bars:
	# 		d.write(f'{line[0]}, {line[1]}, {line[2]}, {line[3]}, {line[4]}, {line[5]}\n')

	# delete unwanted data - just keep date, open, high, low, close, volume
	for line in bars:
		del line[6:]

	# option 4 - create a Pandas DataFrame and export to CSV
	btc_df = pd.DataFrame(bars, columns=['date', 'open', 'high', 'low', 'close', 'volume'])
	# btc_df.set_index('date', inplace=True)
	# print(btc_df.head())
	# export DataFrame to csv
	# btc_df.to_csv('btc_bars3.csv')

	# load DataFrame
	# btc_df = pd.read_csv('btc_bars3.csv', index_col=0)
	btc_df.set_index('date', inplace=True)
	btc_df.index = pd.to_datetime(btc_df.index, unit='ms')
	# print(btc_df.head())

	# timestamp = 1545730073
	# dt_obj = datetime.fromtimestamp(1140825600)

	# print("date_time:",dt_obj)
	# print("type of dt:",type(dt_obj))

	df = btc_df

	# pd.to_datetime(df['I_DATE'])

	# df['dates'] = pd.to_datetime(btc_df['dates'])
	# df['date'] = datetime.fromtimestamp(df['date']).strftime('%d-%m-%y')


	# print (df.head())
	# print (df.dtypes)

	# Select last row of the dataframe as a dataframe object
	last_row_df = df.iloc[-1:]

	# print(last_row_df)

	last_two_df = df.iloc[-2:-1]

	# print(last_two_df)

	# last_row_df['date'] = datetime.fromtimestamp(last_row_df['date'])

	# ts = int(last_row_df['date'].iloc[0])
	# ts /= 1000
	# print(last_row_df['date'].iloc[0])

	# if you encounter a "year is out of range" error the timestamp
	# may be in milliseconds, try `ts /= 1000` in that case
	# print(datetime.utcfromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S'))

	# print("last row Of Dataframe: ")
	# print(last_row_df)

	last_volume=float(last_two_df['volume'].iloc[0])

	# candles = client.get_klines(symbol=pair, interval=Client.KLINE_INTERVAL_30MINUTE)
	# candles = client.get_klines(symbol=pair, interval=interval)
	# for line in candles:
	# 	del line[6:]
	# candles_df = pd.DataFrame(candles, columns=['date', 'open', 'high', 'low', 'close', 'volume'])
	# # candles_df.set_index('date', inplace=True)

	# candles_df.set_index('date', inplace=True)
	# candles_df.index = pd.to_datetime(candles_df.index, unit='ms')
	# print(candles_df.head())

	# last_row_df = candles_df.iloc[-1:]

	# print(last_row_df)
	# print (last_row_df.dtypes)

	# ts = int(last_row_df['date'].iloc[0])
	# ts /= 1000
	# print(last_row_df['date'].iloc[0])

	# if you encounter a "year is out of range" error the timestamp
	# may be in milliseconds, try `ts /= 1000` in that case
	# print(datetime.utcfromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S'))



	"""
	formula:   (close-low)/(high-open)*(today's volume - yesterday's volume)
	"""

	# close = float(last_row_df['close'])
	# low = float(last_row_df['low'])
	# high = float(last_row_df['high'])
	# open = float(last_row_df['open'])
	# today_volume = float(last_row_df['volume'])

	close = float(last_row_df['close'].iloc[0])
	low = float(last_row_df['low'].iloc[0])
	high = float(last_row_df['high'].iloc[0])
	open = float(last_row_df['open'].iloc[0])

	today_volume = float(last_row_df['volume'].iloc[0])

	head = abs(high-close)
	tail = abs(close-low)
	vol_ratio = today_volume / last_volume

	if head != 0 :
		v = tail / head 
	else:
		v = -1  # means lost


	# v = abs(close-low)/abs(high-open)*abs(today_volume - last_volume)
	# v2 = abs(close-low)/abs(high-open)

	print("The key index:",v)
	print("The volume ratio:", vol_ratio)

	if v > 2 and vol_ratio > 1 :
		print("***************************************")
		print("Alerting:",pair)
		

		
		print("***************************************")


	print("-------------------------------------")


# check('BTCUSDT','1d')
# check('BNBUSDT')

# # load DataFrame
while True:
	pair_df = pd.read_csv('trade_pair.csv', index_col=0)
	pair_df = pair_df.reset_index()  # make sure indexes pair with number of rows
	for index, row in pair_df.iterrows():
		#print(row[index-1])
		pair=row['Pair']
		check(pair,'1d')

	print("sleep for 10 minutes")
	time.sleep(600)

# print(pair_df.iloc(1))
# # btc_df.set_index('date', inplace=True)
# btc_df.index = pd.to_datetime(btc_df.index, unit='ms')

# print(btc_df.head())
