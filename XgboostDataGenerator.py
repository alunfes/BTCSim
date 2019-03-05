import pandas as pd
import numpy as np
from MarketDataOneMinute import MarketDataOneMinute as md

'''
1m dt, open, high, low, close, size, ma, ma_kairi, rsi, strategy-1 pl, strategy-1 sharp ratio,
strategy performance is result of sim started from the dt and when it continued for 4000 minutes 
'''
class XgboostDataGenerator:
    @classmethod
    def generate_data_contrarian_kairi(cls, start, end):
        df = pd.DataFrame()
        df = df.assign(dt=md.dt)
        df = df.assign(open=md.open)
        df = df.assign(high=md.high)
        df = df.assign(low=md.low)
        df = df.assign(close=md.close)
        for k in md.ma_kairi:
            col = 'kairi'+k
            df = df.assign(col=md.ma_kairi[k])
        for k in md.rsi:
            col = 'rsi' + k
            df = df.assign(col=md.rsi[k])




    @classmthod
    def __generate_sim_paramter_combinations(self):
        print('')


