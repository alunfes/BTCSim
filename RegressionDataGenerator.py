import pandas as pd
import numpy as np
from MarketDataOneMinute import MarketDataOneMinute as md
from SimpleSimOhlc import SimpleSimOhlc as sim

'''
1m dt, open, high, low, close, size, ma, ma_kairi, rsi, strategy-1 pl, strategy-1 sharp ratio,
strategy performance is result of sim started from the dt and when it continued for 4000 minutes 
'''
class RegressionDataGenerator:
    @classmethod
    def generate_data_contrarian_kairi(cls, start, end):
        df = pd.DataFrame()
        df = df.assign(dt=md.dt[start:end])
        df = df.assign(open=md.open[start:end])
        df = df.assign(high=md.high[start:end])
        df = df.assign(low=md.low[start:end])
        df = df.assign(close=md.close[start:end])
        for k in md.ma_kairi:
            col = 'kairi'+k
            df = df.assign(col=md.ma_kairi[k][start:end])
            df.rename(columns={'col' : col}, inplace=True)
        for k in md.rsi:
            col = 'rsi' + k
            df = df.assign(col=md.rsi[k][start:end])
            df.rename(columns={'col': col}, inplace=True)

        pl = []
        for i in range(end - start):
            s = sim()
            res = s.sim_contrarian_kairi(i+start, 1000+i+start, '50', 0.01, 1500, 500)
            pl.append(res[0])
            print(res[0])
        df = df.assign(strategy_1=pl)
        return df

    @classmethod
    def __generate_sim_paramter_combinations(self):
        print('')




