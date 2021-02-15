#!/usr/bin/env python
# coding: utf-8

# In[105]:


import numpy as np
import pandas as pd
import requests as rq
import datetime as dt
import yahoo_fin.stock_info as si
import math
from scipy import stats


# In[106]:


today = dt.date.today() - dt.timedelta(days = 1)
dates_split = [1, 3, 6, 12]
dates_arr = [today]
weekend_adj = 0

if dates_arr[0].weekday() == 6:
    weekend_adj = 1
elif dates_arr[0].weekday() == 5:
    weekend_adj = 1

for i in dates_split:
    date = today.replace(year = today.year if today.month - i > 0 else today.year - 1,
                         month = today.month - i if today.month - i > 0 else (12 + today.month - i),
                         day = 1)
    for e in range(7):
        if date.weekday() == 3:
            dates_arr.append(date)
            break
        date = date - dt.timedelta(days = 1)


# In[113]:


stocks = si.tickers_sp500()
# stocks = ['AAPL', 'IBM', 'FB', 'AMZN', 'UPWK', 'FVRR', 'DIS', 'TSLA', 'T', 'MSFT']


# In[114]:


hqm_data = []
for ticker in stocks:
    print('Getting', ticker, '...')
    price_builder = [ticker]
    try:
        for i in range(5):
            stock_data = si.get_data(ticker,
                                     start_date=dates_arr[i] - dt.timedelta(days = weekend_adj),
                                     end_date=dates_arr[i])
            stock_data.reset_index(inplace=True)
            price_builder.append(round(float(stock_data['close']), 4))
        hqm_data.append(price_builder)
        (pd.DataFrame(hqm_data, columns=['Ticker', 'Most recent', '1-Month', '3-Month', '6-Month', '12-Month'])).to_csv('overview.csv', index=False)
    except:
        print(ticker, 'not found')


# In[119]:


hqm_change = []
for ticker_idx, ticker_arr in enumerate(hqm_data):
    hqm_change.append([ticker_arr[0]])
    for price_idx in range(2, 6, 1):
        hqm_change[ticker_idx].append(round(ticker_arr[1] - ticker_arr[price_idx], 2))
(pd.DataFrame(hqm_change, columns=['Ticker', '1M', '3M', '6M', '12M'])).to_csv('change.csv', index=False)


# In[118]:


tickers_loss = []
for ticker_arr in hqm_change:
    tickers_loss.append([ticker_arr[0], 0])

for column_idx in range(1, 5, 1):
    hqm_change = sorted(hqm_change, key = lambda x: x[column_idx], reverse=True)
    for loss, ticker_arr in enumerate(hqm_change):
        for ticker_loss_arr in tickers_loss:
            if ticker_loss_arr[0] == ticker_arr[0]:
                ticker_loss_arr[1] += loss
(pd.DataFrame(tickers_loss, columns=['Ticker', 'Loss']).sort_values(by=['Loss'])).to_csv('loss.csv', index=False)


# In[ ]:




