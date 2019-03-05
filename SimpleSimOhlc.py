from MarketDataOneMinute import MarketDataOneMinute
from numba import jit
import numpy as np
import OptunaSim


class SimpleSimOhlc:
    @jit
    def __initialize(self):
        self.pl = 0
        self.pl_log =[]
        self.pl_std = 0
        self.minus_sum = 0
        self.num_trade = 0
        self.num_win = 0
        self.win_rate = 0
        self.entry_flg = ''
        self.posi_side = ''
        self.posi_price = 0
        self.posi_size = 0
        self.order_dt = None
        self.order_price = 0

    @jit
    def __execute(self, profit):
        self.pl += profit
        self.pl_log.append(self.pl)
        self.num_trade +=1
        if profit > 0:
            self.num_win +=1
        self.win_rate = float(self.num_win) / float(self.num_trade)
        self.posi_side = ''
        self.posi_price = 0
        self.posi_size = 0
        self.order_dt = None
        self.entry_flg = ''
        self.order_price = 0

    @jit
    def __check_execution(self, ind, side, order_price):
        if side =='buy':
            if MarketDataOneMinute.low[ind] <= order_price:
                return order_price
            else:
                return 0
        elif side == 'sell':
            if MarketDataOneMinute.high[ind] >= order_price:
                return order_price
            else:
                return 0

    @jit
    def __last_ind_operation(self, ind):
        if self.posi_side == 'buy':
            self.__execute( (MarketDataOneMinute.close[ind] - self.posi_price) * self.posi_size)
        elif self.posi_side == 'sell':
            self.__execute( (self.posi_price - MarketDataOneMinute.close[ind]) * self.posi_size)
        self.pl_std = np.array(self.pl_log).std()
        for i,p in enumerate(self.pl_log):
            if i >0:
                if p - self.pl_log[i-1] <0:
                    self.minus_sum +=p - self.pl_log[i-1]

    @jit
    def __next_ind_operation(self, ind, start_ind):
        if self.posi_side == 'buy':
            self.pl_log.append((MarketDataOneMinute.close[ind] - self.posi_price) * self.posi_size)
        elif self.posi_side == 'sell':
            self.pl_log.append((self.posi_price - MarketDataOneMinute.close[ind]) * self.posi_size)
        else:
            if ind > start_ind:
                self.pl_log.append(self.pl_log[len(self.pl_log) - 1])
            else:
                self.pl_log.append(0)

    @jit
    def sim_contrarian_kairi(self, start_ind, end_ind, kairi_term, kairi_kijun, pt, lc):
        self.__initialize()
        for i in range(end_ind - start_ind):
            ind = i + start_ind
            if self.entry_flg == '':
                if (MarketDataOneMinute.ma_kairi[kairi_term][ind] - 1.0) >= kairi_kijun: #entry sell
                    self.entry_flg = 'sell'
                    self.order_dt = MarketDataOneMinute.close[ind]
                    self.order_price = MarketDataOneMinute.close[ind]
                elif (1.0 - MarketDataOneMinute.ma_kairi[kairi_term][ind]) <= kairi_kijun: #entyr buy
                    self.entry_flg ='buy'
                    self.order_dt = MarketDataOneMinute.close[ind]
                    self.order_price = MarketDataOneMinute.close[ind]
            elif self.posi_side == '' and (self.entry_flg =='buy' or self.entry_flg=='sell'): #check and do process entry
                exe_p = self.__check_execution(ind, self.entry_flg, self.order_price)
                if exe_p > 0:
                    self.posi_price = exe_p
                    self.posi_side = self.entry_flg
                    self.posi_size = 0.11
                    self.order_dt = MarketDataOneMinute.dt[ind]
                    self.order_price = 0
                    self.entry_flg = ''
            elif self.posi_side == 'buy' or self.posi_side == 'sell': #if holidng position
                if (self.posi_side == 'buy' and MarketDataOneMinute.high[ind] >= pt + self.posi_price) or\
                    (self.posi_side == 'sell' and MarketDataOneMinute.low[ind] <= self.posi_price - pt): #if pt can be executed
                    price = pt + self.posi_price if self.posi_side =='buy' else self.posi_price - pt
                    self.__execute(self.posi_size * pt)
                if self.entry_flg == 'lc':
                    exe_p = self.__check_execution(ind, self.posi_side, self.order_price)
                    if exe_p > 0:
                        p = self.order_price - self.posi_price if self.posi_side == 'buy' else self.posi_price - self.order_price
                        self.__execute(self.posi_size * p)
                if (self.posi_side == 'buy' and MarketDataOneMinute.low[ind] <= self.posi_price - lc) or\
                    (self.posi_side =='sell' and MarketDataOneMinute.high[ind] >= self.posi_price + lc): #entry lc order
                    self.entry_flg = 'lc'
                    self.order_dt = MarketDataOneMinute.dt[ind]
                    self.order_price = MarketDataOneMinute.low[ind] if self.posi_side == 'buy' else MarketDataOneMinute.high[ind]
            self.__next_ind_operation(ind, start_ind)
        self.__last_ind_operation(end_ind - start_ind - 1)
        return (self.pl, self.num_trade, self.win_rate, self.pl_log, self.pl_std, self.minus_sum)

    @jit
    def sim_contrarian_kairi_conti_optuna(self, start_ind, end_ind):
        self.__initialize()
        kairi_term = ''
        kairi_kijun = 0
        pt = 0
        lc = 0
        opsim_num = 10000
        for i in range(end_ind - start_ind):
            ind = i + start_ind
            if opsim_num >= 3000:
                ops = OptunaSim.OptunaSim()
                params = ops.get_opt_param_for_simplesimohlc(ind - 4001, ind - 1)
                kairi_term = str(params['kairi_term'])
                kairi_kijun = params['kairi_kijun']
                pt = params['pt']
                lc = params['lc']
                opsim_num = 0
            if self.entry_flg == '':
                if (MarketDataOneMinute.ma_kairi[kairi_term][ind] - 1.0) >= kairi_kijun:  # entry sell
                    self.entry_flg = 'sell'
                    self.order_dt = MarketDataOneMinute.close[ind]
                    self.order_price = MarketDataOneMinute.close[ind]
                elif (1.0 - MarketDataOneMinute.ma_kairi[kairi_term][ind]) <= kairi_kijun:  # entyr buy
                    self.entry_flg = 'buy'
                    self.order_dt = MarketDataOneMinute.close[ind]
                    self.order_price = MarketDataOneMinute.close[ind]
            elif self.posi_side == '' and (
                    self.entry_flg == 'buy' or self.entry_flg == 'sell'):  # check and do process entry
                exe_p = self.__check_execution(ind, self.entry_flg, self.order_price)
                if exe_p > 0:
                    self.posi_price = exe_p
                    self.posi_side = self.entry_flg
                    self.posi_size = 0.11
                    self.order_dt = MarketDataOneMinute.dt[ind]
                    self.order_price = 0
                    self.entry_flg = ''
            elif self.posi_side == 'buy' or self.posi_side == 'sell':  # if holidng position
                if (self.posi_side == 'buy' and MarketDataOneMinute.high[ind] >= pt + self.posi_price) or \
                        (self.posi_side == 'sell' and MarketDataOneMinute.low[
                            ind] <= self.posi_price - pt):  # if pt can be executed
                    price = pt + self.posi_price if self.posi_side == 'buy' else self.posi_price - pt
                    self.__execute(self.posi_size * pt)
                if self.entry_flg == 'lc':
                    exe_p = self.__check_execution(ind, self.posi_side, self.order_price)
                    if exe_p > 0:
                        p = self.order_price - self.posi_price if self.posi_side == 'buy' else self.posi_price - self.order_price
                        self.__execute(self.posi_size * p)
                if (self.posi_side == 'buy' and MarketDataOneMinute.low[ind] <= self.posi_price - lc) or \
                        (self.posi_side == 'sell' and MarketDataOneMinute.high[
                            ind] >= self.posi_price + lc):  # entry lc order
                    self.entry_flg = 'lc'
                    self.order_dt = MarketDataOneMinute.dt[ind]
                    self.order_price = MarketDataOneMinute.low[ind] if self.posi_side == 'buy' else \
                    MarketDataOneMinute.high[ind]
            opsim_num +=1
        print('pl={}, num_trade={}, win_rate={}'.format(self.pl, self.num_trade, self.win_rate))
        return (self.pl, self.num_trade, self.win_rate, self.pl_log, self.pl_std, self.minus_sum)

    @jit
    def sim_trendfollow_ma_kairi(self, start_ind, end_ind, ma_term, pt, lc, no_ptlc = False):
        self.__initialize()
        for i in range(end_ind - start_ind):
            ind = i + start_ind
            if self.entry_flg == '':
                if (MarketDataOneMinute.close[ind] - MarketDataOneMinute.ma[ma_term][ind]) >0 :  # entry buy
                    self.entry_flg = 'buy'
                    self.order_dt = MarketDataOneMinute.close[ind]
                    self.order_price = MarketDataOneMinute.close[ind]
                elif (MarketDataOneMinute.close[ind] - MarketDataOneMinute.ma[ma_term][ind]) < 0:  # entyr sell
                    self.entry_flg = 'sell'
                    self.order_dt = MarketDataOneMinute.close[ind]
                    self.order_price = MarketDataOneMinute.close[ind]
            elif self.posi_side == '' and (
                    self.entry_flg == 'buy' or self.entry_flg == 'sell'):  # check and do process entry
                exe_p = self.__check_execution(ind, self.entry_flg, self.order_price)
                if exe_p > 0:
                    self.posi_price = exe_p
                    self.posi_side = self.entry_flg
                    self.posi_size = 0.11
                    self.order_dt = MarketDataOneMinute.dt[ind]
                    self.order_price = 0
                    self.entry_flg = ''
            elif self.posi_side == 'buy' or self.posi_side == 'sell':  # if holidng position
                if (self.posi_side == 'buy' and MarketDataOneMinute.high[ind] >= pt + self.posi_price) or \
                        (self.posi_side == 'sell' and MarketDataOneMinute.low[
                            ind] <= self.posi_price - pt):  # if pt can be executed
                    price = pt + self.posi_price if self.posi_side == 'buy' else self.posi_price - pt
                    self.__execute(self.posi_size * pt)
                if self.entry_flg == 'lc':
                    exe_p = self.__check_execution(ind, self.posi_side, self.order_price)
                    if exe_p > 0:
                        p = self.order_price - self.posi_price if self.posi_side == 'buy' else self.posi_price - self.order_price
                        self.__execute(self.posi_size * p)
                if (self.posi_side == 'buy' and MarketDataOneMinute.low[ind] <= self.posi_price - lc) or \
                        (self.posi_side == 'sell' and MarketDataOneMinute.high[
                            ind] >= self.posi_price + lc):  # entry lc order
                    self.entry_flg = 'lc'
                    self.order_dt = MarketDataOneMinute.dt[ind]
                    self.order_price = MarketDataOneMinute.low[ind] if self.posi_side == 'buy' else \
                    MarketDataOneMinute.high[ind]
            self.__next_ind_operation(ind, start_ind)
        self.__last_ind_operation(end_ind - start_ind - 1)
        return (self.pl, self.num_trade, self.win_rate, self.pl_log, self.pl_std, self.minus_sum)


if __name__ == '__main__':
    MarketDataOneMinute.initialize(2019,1,1,2019,1,30)
    sim = SimpleSimOhlc()
    #sim.sim_contrarian_kairi_conti_optuna(5000, 10000)
    sim.sim_contrarian_kairi(100,len(MarketDataOneMinute.dt), '50', 0.01, 1500, 500)