import pandas as pd
import numpy as np
from SqliteDBAdmin import SqliteDBAdmin
from numba import jit
import datetime


class MarketData:
    @classmethod
    def initialize(cls, year_s, month_s, day_s, year_e, month_e, day_e):
        cls.datetime = []
        cls.id = []
        cls.price = []
        cls.size = []
        cls.ma = {}
        cls.ma_kairi = {}

        SqliteDBAdmin.initialize()
        ticks = SqliteDBAdmin.read_from_sqlite(year_s, month_s, day_s, year_e, month_e, day_e)
        print('completed read data from DB')
        for tick in ticks:
            #cls.datetime.append(datetime.datetime.strptime(tick.datetime, '%Y-%m-%d %H:%M:%S'))
            cls.datetime.append(tick.datetime)
            cls.id.append(tick.id)
            cls.price.append(tick.price)
            cls.size.append(tick.size)
        print('completed appended data to list')
        cls.__calc_all_ma()
        cls.__calc_ma_kairi()


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
        for i in range(len(cls.price) - term - 1):
            sum = sum + cls.price[i + term] - cls.price[i]
            ma.append(float(sum) / float(term))
        print('completed ma calc')
        return ma

    @classmethod
    @jit
    def __calc_all_ma(cls):
        for i in range(10):
            term = (i+1) * 100
            cls.ma[str(term)] = cls.__calc_ma(term)

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
    MarketData.initialize(2018,10,1,2018,10,2)
