import pandas as pd
import numpy as np
from sklearn import preprocessing
import copy
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
    def generate_lstm_ave_data(cls,start, end, length_of_sequence, test_size = 0.33):
        ave = []
        for i in range(start, end):
            ave.append((md.open[i]+md.high[i]+md.low[i]+md.close[i])/4.0)
        change = []
        for i in range(len(ave) - 1):
            change.append(ave[i+1]/ave[i])
        ca = np.array(change).reshape(-1, 1)
        scaler = preprocessing.MinMaxScaler()
        change = scaler.fit_transform(ca)
        change = np.array(change)
        yli = []
        xli = []
        x = np.empty((len(change) - length_of_sequence -1, length_of_sequence), np.float)
        y = np.empty((len(change) - length_of_sequence -1, 1), np.float)
        for i in range(len(change) - length_of_sequence -1):
            nx = change[i:i+length_of_sequence]
            ny = change[i+length_of_sequence:i+length_of_sequence+1]
            x = np.append(x, nx, axis = 0)
            y = np.append(y, ny, axis = 0)
            '''   
            xli = []
            for j in range(length_of_sequence):
                xli.append((float(change[i+j])))
            x = pd.concat([x, pd.Series(xli)], axis = 1, ignore_index=True)
            yli.append(float(change[i+length_of_sequence]))
        y = pd.Series(yli)
        x = copy.deepcopy(x.T).iloc[1:x.shape[1]+1]

        s = int(round(x.shape[0] * (1-test_size)))
            '''
        x_train =
        x_train = np.array(x.iloc[0:s]).reshape(s, length_of_sequence, 1)
        x_test = np.array(x.iloc[s:x.shape[0] + 1]).reshape(x.shape[0] - s, length_of_sequence, 1)
        y_train = np.array(y.iloc[0:s]).reshape(s, 1)
        y_test = np.array(y.iloc[s:x.shape[0]+1]).reshape(x.shape[0]-s,1)
        return x_train, y_train, x_test, y_test,ave,change

    #start should be > length_of_sequence
    @classmethod
    def generate_lstm_sim_data(cls, start, end, length_of_sequence, sim_period, kairi_term, kairi_kijun, pt, lc, test_size=0.33):
        x = []
        y = []
        for i in range(start,end):
            x.extend(x,md.close[i-length_of_sequence:i])
            s = sim()
            res = s.sim_contrarian_kairi(i,i+sim_period,kairi_term,kairi_kijun,pt,lc) #(self.pl, self.num_trade, self.win_rate, self.pl_log, self.pl_std, self.minus_sum)
            y.append(res[0])

        x_train = 

    @classmethod
    def __generate_sim_paramter_combinations(self):
        print('')




