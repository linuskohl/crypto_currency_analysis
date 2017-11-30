#!/usr/bin/env python
'''
    Visualisation of Google Trends and Quandl data

    Author:         Linus Kohl <linus@munichresearch.com>
    Date created:   30.11.2017
    Python Version: 3.4
'''
import matplotlib.pyplot as plt
import pandas as pd
from pytrends.request import TrendReq
from dateutil.relativedelta import relativedelta
import datetime
import pickle
import quandl

search_term = 'buy bitcoin'
quandl_data_id = 'BCHARTS/COINBASEEUR-Bitcoin-Markets-coinbaseEUR'


def cached_fetch_quantl(quandl_id):
    '''Download and cache Quandl data'''
    now = datetime.datetime.now()
    cache_path = '{}.pkl'.format(quandl_id.replace('/', '-') + '_' + now.strftime("%Y-%m-%d"))
    try:
        f = open(cache_path, 'rb')
        df = pickle.load(f)
        print('Loaded {} from cache'.format(quandl_id))
    except (OSError, IOError) as e:
        print('Downloading {} from Quandl'.format(quandl_id))
        df = quandl.get(quandl_id, returns="pandas")
        df.to_pickle(cache_path)
        print('Cached {} at {}'.format(quandl_id, cache_path))
    return df


google_trends = TrendReq(hl='en-US', tz=360)
google_trends.build_payload(kw_list=[search_term], timeframe='today 3-m', )
df_interest = google_trends.interest_over_time()

df_price = cached_fetch_quantl(quandl_data_id)

'''Get start date and drop previous data'''
start = pd.to_datetime('today') - relativedelta(months=3)
start = start.date()
df_price = df_price.loc[start:]
df_interest = df_interest.loc[start:]

df = pd.concat([df_interest[search_term], df_price['Weighted Price'], df_price['Volume (BTC)']], axis=1)

'''Plot data'''
fig, ax1 = plt.subplots()
ax2 = ax1.twinx()

volume = ax2.bar(df.index.to_pydatetime(), df['Volume (BTC)'], 1,
                 alpha=0.08,
                 color='red',
                 label='Volume'
                 )

interest, = ax1.plot(df.index.to_pydatetime(), df[search_term], '--',
                     color='blue',
                     linewidth=1.0,
                     label='Interest (Google Trends)',
                     )

price, = ax2.plot(df.index.to_pydatetime(), df['Weighted Price'], '-',
                  color='red',
                  linewidth=1.0,
                  label='BTC/EUR (Coinbase)'
                  )

ax1.spines["top"].set_visible(False)
ax2.spines["top"].set_visible(False)
plt.legend(handles=[interest, price, volume])

print('Correlation')
print(df.pct_change().corr(method='pearson'))

plt.show()


