import pandas as pd
import numpy as np
from SqliteDBAdmin import SqliteDBAdmin
from numba import jit
from datetime import datetime, timedelta

'''
confirmed ma and kairi are accurate
'''
class MarketData:
    @classmethod
    def initialize(cls, year_s, month_s, day_s, year_e, month_e, day_e):
        cls.datetime = []
        cls.id = []
        cls.price = []
        cls.size = []
        cls.ma = {}
        cls.ma_kairi = {}
        cls.minutes_data = pd.DataFrame()

        SqliteDBAdmin.initialize()
        ticks = SqliteDBAdmin.read_from_sqlite(year_s, month_s, day_s, year_e, month_e, day_e)
        print('completed read data from DB')
        for tick in ticks:
            #cls.datetime.append(dt.strptime(tick.datetime, '%Y-%m-%d %H:%M:%S'))
            cls.datetime.append(tick.datetime)
            cls.id.append(tick.id)
            cls.price.append(tick.price)
            cls.size.append(tick.size)
        print('completed appended data to list')
        cls.__calc_ma_kairi()
        cls.__calc_all_ma()

    @classmethod
    @jit
    def convert_tick_to_minutes(cls):
        next_dt = None
        openp=0
        high = 0
        low = 99999999
        close = 0
        size = 0
        dohlcs = []
        flg = False
        for i,p in enumerate(cls.price):
            if next_dt == None:
                if cls.datetime[i].second ==0:
                    next_dt = cls.datetime[i] +timedelta(minutes=1)
                    print('next dt defined'+str(next_dt))
                    flg = True
            else:
                if flg:
                    if next_dt <= cls.datetime[i]:
                        close = cls.price[i]
                        dohlcs.append([next_dt, openp, high, low, close, size])
                        next_dt = next_dt + timedelta(minutes=1)
                        openp = 0
                        high = 0
                        low = 9999999
                        close = 0
                        size = 0
                    else:
                        if size ==0:
                            openp = cls.price[i]
                        high = max(high, cls.price[i])
                        low = min(low, cls.price[i])
                        size += cls.size[i]
        cls.minutes_data = pd.DataFrame(np.array(dohlcs))
        cls.minutes_data.columns = ['dt','open','high','low','close','size']

    @classmethod
    @jit
    def __calc_ma(cls, term):
        print('calculating ma, term='+str(term))
        sum = 0
        ma = []
        for i in range(term):
            ma.append(0)
            sum += cls.price[i]
        ma.pop(0)
        ma.append(float(sum) / float(term))
        for i in range(len(cls.price) - term):
            sum = sum + cls.price[i + term] - cls.price[i]
            ma.append(float(sum) / float(term))
        print('completed ma calc')
        return ma

    @classmethod
    @jit
    def __calc_ma2(cls, term):
        print('calculating ma, term=' + str(term))
        ma = []
        for i in range(len(cls.price) - term):
            ma.append(cls.price[i:i+term].sum() / float(term))
        print('completed ma calc')
        return ma

    @classmethod
    @jit
    def __calc_all_ma(cls):
        for i in range(10):
            term = (i+1) * 1000
            cls.ma[str(term)] = cls.__calc_ma(term)
            #cls.ma[str(term)] = cls.__calc_ma2(term)

    @classmethod
    @jit
    def __calc_ma_kairi(cls):
        for m in cls.ma:
            kairi = []
            num_v = int(m)
            for i in range(num_v-1):
                kairi.append(0)
            for i in range(len(cls.ma[m]) - num_v+1):
                kairi.append(cls.price[i + num_v-1] / cls.ma[m][i + num_v-1])
            cls.ma_kairi[m] = kairi


if __name__ == '__main__':
    MarketData.initialize(2019,1,1,2019,1,2)
    MarketData.ma['500']
