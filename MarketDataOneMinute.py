import pandas as pd
import numpy as np
from SqliteDBAdmin import SqliteDBAdmin
from numba import jit
from datetime import datetime, timedelta

'''
confirmed ma and kairi are accurate
'''
class MarketDataOneMinute:

    @classmethod
    @jit
    def initialize(cls, year_s, month_s, day_s, year_e, month_e, day_e, period_sec=60):
        cls.dt = []
        cls.open = []
        cls.high = []
        cls.low = []
        cls.close = []
        cls.size = []
        cls.ma = {}
        cls.ma_kairi = {}
        

        SqliteDBAdmin.initialize()
        ticks = SqliteDBAdmin.read_from_sqlite(year_s, month_s, day_s, year_e, month_e, day_e)
        print('completed read data from DB')

        print('converting tick data to ' + str(period_sec) +' data')
        next_dt = None
        openp = 0
        high = 0
        low = 99999999
        close = 0
        size = 0
        num = 0
        for i,tick in enumerate(ticks):
            if next_dt == None:
                if tick.datetime.second == 0:
                    next_dt = tick.datetime + timedelta(seconds=period_sec)
                    #next_dt = next_dt - timedelta(microseconds=next_dt.microseconds)
            else:
                if tick.datetime < next_dt:
                    if size == 0:
                        openp = tick.price
                    size += tick.size
                    high = max(high, tick.price)
                    low = min(low, tick.price)
                elif tick.datetime >=  next_dt:
                    if size >= 1:
                        cls.dt.append(next_dt)
                        cls.open.append(openp)
                        cls.high.append(high)
                        cls.low.append(low)
                        cls.close.append(tick.price)
                        cls.size.append(size)
                    openp = 0
                    high = 0
                    low = 99999999
                    close = 0
                    size = 0
                    next_dt = next_dt + timedelta(seconds=period_sec)

        print('completed tick data conversion')
        print('calculating ma')
        cls.__calc_all_ma()
        cls.__calc_ma_kairi()
        print('completed ma calc')

    @classmethod
    @jit
    def __calc_ma(cls, term):
        sum = 0
        ma = []
        for i in range(term):
            ma.append(0)
            sum += cls.close[i]
        ma.pop(0)
        ma.append(float(sum) / float(term))
        for i in range(len(cls.close) - term):
            sum = sum + cls.close[i + term] - cls.close[i]
            ma.append(float(sum) / float(term))
        return ma

    @classmethod
    @jit
    def __calc_all_ma(cls):
        for i in range(10):
            term = (i + 1) * 10
            cls.ma[str(term)] = cls.__calc_ma(term)

    @classmethod
    @jit
    def __calc_ma_kairi(cls):
        for m in cls.ma:
            kairi = []
            num_v = int(m)
            for i in range(num_v - 1):
                kairi.append(0)
            for i in range(len(cls.ma[m]) - num_v + 1):
                kairi.append(cls.close[i + num_v - 1] / cls.ma[m][i + num_v - 1])
            cls.ma_kairi[m] = kairi


if __name__ == '__main__':
    MarketDataOneMinute.initialize(2019,1,1,2019,1,3)
    for i in range(1000):
        print('{},{},{},{},{}'.format(MarketDataOneMinute.dt[i],MarketDataOneMinute.open[i],MarketDataOneMinute.high[i],MarketDataOneMinute.low[i]
                                      ,MarketDataOneMinute.close[i],MarketDataOneMinute.size[i]))