import numpy as np
import pandas as pd
import requests as rq
import datetime as dt
import yahoo_fin.stock_info as si
from PyInquirer import prompt, Separator
import csv
import math
import os.path

def printProgressBar (iteration, total, prefix = '', suffix = '', decimals = 1, length = 100, fill = '█', printEnd = '\r'):
    percent = ('{0:.' + str(decimals) + 'f}').format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print(f'\r{prefix} |{bar}| {percent}% {suffix}', end = printEnd)
    if iteration == total: 
        print()

stocks_q = [
    {
        'type': 'list',
        'message': 'Select stocks',
        'name': 'stocks',
        'choices': [
            'SP500',
            'Custom'
        ]
    }
]
outputs_q = [
    {
        'type': 'checkbox',
        'message': 'Select outputs',
        'name': 'outputs',
        'choices': [ 
            {
                'name': 'Overview',
				'checked': True
            },
            {
                'name': 'Change'
            },
            {
                'name': 'Ranking'
            }
        ]
    }
]
outputs_a = prompt(outputs_q)
get_stocks_q = [
    {
        'type': 'confirm',
        'message': 'Do you want to get the latest prices?',
        'name': 'fetch',
        'default': True
    }
]
get_stocks_a = prompt(get_stocks_q)
force_get_stocks_q = [
    {
        'type': 'confirm',
        'message': 'If data exists, would you like to overwrite?',
        'name': 'force_fetch',
        'default': True
    }
]
force_get_stocks_a = prompt(force_get_stocks_q)
if get_stocks_a['fetch']:
    stocks_a = prompt(stocks_q)
    if 'Custom' == stocks_a['stocks']:
        stocks = input('List stocks separated by comma: ').replace(' ', '').split(',')
    else:
        stocks = si.tickers_sp500()

today = dt.date.today() - dt.timedelta(days = 1)
dates_split = [1, 3, 6, 12]
dates_arr = [today]
failed_tickers, hqm_change, tickers_loss = [], [], []
data_header = ['Ticker', 'Recent', '1M', '3M', '6M', '12M']

for i in dates_split:
    date = today.replace(year = today.year if today.month - i > 0 else today.year - 1,
                         month = today.month - i if today.month - i > 0 else (12 + today.month - i),
                         day = 1)
    for e in range(7):
        if date.weekday() == 3:
            dates_arr.append(date)
            break
        date = date - dt.timedelta(days = 1)

if get_stocks_a['fetch']:
    if os.path.exists('overview.csv') == False or force_get_stocks_a['force_fetch']:
        with open('overview.csv', mode='w') as overview_file:
            overview_writer = csv.writer(overview_file, delimiter=',', quotechar='"')
            overview_writer.writerow(data_header)
    for i, ticker in enumerate(stocks):
        printProgressBar(i + 1, len(stocks), prefix = 'Progress:', suffix = ticker, length = 50)
        with open('overview.csv', 'r') as overview_read:
            for row in overview_read:
                if ticker in row:
                    force_get_data = False
        if force_get_data:
            price_builder = [ticker]
            try:
                for i in range(len(data_header) - 1):
                    stock_data = si.get_data(ticker,
                                            start_date=dates_arr[i] - dt.timedelta(days = 7),
                                            end_date=dates_arr[i])
                    stock_data.reset_index(inplace=True)
                    price_builder.append(round(float(stock_data['close'][-1:]), 4))
            except:
                failed_tickers.append(ticker)
            with open('overview.csv', mode='a') as overview_file:
                    overview_writer = csv.writer(overview_file, delimiter=',', quotechar='"')
                    overview_writer.writerow(price_builder)
        force_get_data = True
    print(f"\nFailed tickers: {', '.join(failed_tickers)}\n")
hqm_data = np.array(pd.read_csv('overview.csv'))

for ticker_idx, ticker_arr in enumerate(hqm_data):
    hqm_change.append([ticker_arr[0]])
    for price_idx in range(2, 6, 1):
        hqm_change[ticker_idx].append(round(100 * (ticker_arr[1] - ticker_arr[price_idx]) / ticker_arr[price_idx], 2))
if 'Change' in outputs_a['outputs']:
    change_df = pd.DataFrame(hqm_change, columns= data_header.remove('Recent'))
    change_df.to_csv('change.csv', index=False)
    print(change_df)
    print()

for ticker_arr in hqm_change:
    tickers_loss.append([ticker_arr[0], 0])

for column_idx in range(1, 5, 1):
    hqm_change = sorted(hqm_change, key = lambda x: x[column_idx], reverse=True)
    for loss, ticker_arr in enumerate(hqm_change):
        for ticker_loss_arr in tickers_loss:
            if ticker_loss_arr[0] == ticker_arr[0]:
                ticker_loss_arr[1] += loss
if 'Ranking' in outputs_a['outputs']:
    ranking_df = pd.DataFrame(tickers_loss, columns=['Ticker', 'Loss']).sort_values(by=['Loss'])
    ranking_df.to_csv('loss.csv', index=False)
    print(ranking_df)
    print()
