from MarketDataOneMinute import MarketDataOneMinute
from numba import jit
import numpy as np
import OptunaSim


class SimpleSimOhlc:
    @jit
    def __initialize(cls):
        cls.pl = 0
        cls.pl_log =[]
        cls.num_trade = 0
        cls.num_win = 0
        cls.win_rate = 0
        cls.entry_flg = ''
        cls.posi_side = ''
        cls.posi_price = 0
        cls.posi_size = 0
        cls.order_dt = None
        cls.order_price = 0

    @jit
    def __execute(cls, profit):
        cls.pl += profit
        cls.pl_log.append(cls.pl)
        cls.num_trade +=1
        if profit > 0:
            cls.num_win +=1
        cls.win_rate = float(cls.num_win) / float(cls.num_trade)
        cls.posi_side = ''
        cls.posi_price = 0
        cls.posi_size = 0
        cls.order_dt = None
        cls.entry_flg = ''
        cls.order_price = 0

    @jit
    def check_execution(cls, ind, side, order_price):
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
    def sim_contrarian_kairi(cls, start_ind, end_ind, kairi_term, kairi_kijun, pt, lc):
        cls.__initialize()
        for i in range(end_ind - start_ind):
            ind = i + start_ind
            if cls.entry_flg == '':
                if (MarketDataOneMinute.ma_kairi[kairi_term][ind] - 1.0) >= kairi_kijun: #entry sell
                    cls.entry_flg = 'sell'
                    cls.order_dt = MarketDataOneMinute.close[ind]
                    cls.order_price = MarketDataOneMinute.close[ind]
                elif (1.0 - MarketDataOneMinute.ma_kairi[kairi_term][ind]) <= kairi_kijun: #entyr buy
                    cls.entry_flg ='buy'
                    cls.order_dt = MarketDataOneMinute.close[ind]
                    cls.order_price = MarketDataOneMinute.close[ind]
            elif cls.posi_side == '' and (cls.entry_flg =='buy' or cls.entry_flg=='sell'): #check and do process entry
                exe_p = cls.check_execution(ind, cls.entry_flg, cls.order_price)
                if exe_p > 0:
                    cls.posi_price = exe_p
                    cls.posi_side = cls.entry_flg
                    cls.posi_size = 0.11
                    cls.order_dt = MarketDataOneMinute.dt[ind]
                    cls.order_price = 0
                    cls.entry_flg = ''
            elif cls.posi_side == 'buy' or cls.posi_side == 'sell': #if holidng position
                if (cls.posi_side == 'buy' and MarketDataOneMinute.high[ind] >= pt + cls.posi_price) or\
                    (cls.posi_side == 'sell' and MarketDataOneMinute.low[ind] <= cls.posi_price - pt): #if pt can be executed
                    price = pt + cls.posi_price if cls.posi_side =='buy' else cls.posi_price - pt
                    cls.__execute(cls.posi_size * pt)
                if cls.entry_flg == 'lc':
                    exe_p = cls.check_execution(ind, cls.posi_side, cls.order_price)
                    if exe_p > 0:
                        p = cls.order_price - cls.posi_price if cls.posi_side == 'buy' else cls.posi_price - cls.order_price
                        cls.__execute(cls.posi_size * p)
                if (cls.posi_side == 'buy' and MarketDataOneMinute.low[ind] <= cls.posi_price - lc) or\
                    (cls.posi_side =='sell' and MarketDataOneMinute.high[ind] >= cls.posi_price + lc): #entry lc order
                    cls.entry_flg = 'lc'
                    cls.order_dt = MarketDataOneMinute.dt[ind]
                    cls.order_price = MarketDataOneMinute.low[ind] if cls.posi_side == 'buy' else MarketDataOneMinute.high[ind]
        #print('pl={}, num_trade={}, win_rate={}'.format(cls.pl, cls.num_trade, cls.win_rate))
        return (cls.pl, cls.num_trade, cls.win_rate, cls.pl_log)

    @jit
    def sim_contrarian_kairi_conti_optuna(cls, start_ind, end_ind):
        cls.__initialize()
        kairi_term = ''
        kairi_kijun = 0
        pt = 0
        lc = 0
        opsim_num = 10000
        for i in range(end_ind - start_ind):
            ind = i + start_ind
            if opsim_num >= 1000:
                ops = OptunaSim.OptunaSim()
                params = ops.get_opt_param_for_simplesimohlc(ind - 1001, ind - 1)
                kairi_term = str(params['kairi_term'])
                kairi_kijun = params['kairi_kijun']
                pt = params['pt']
                lc = params['lc']
                opsim_num = 0
            if cls.entry_flg == '':
                if (MarketDataOneMinute.ma_kairi[kairi_term][ind] - 1.0) >= kairi_kijun:  # entry sell
                    cls.entry_flg = 'sell'
                    cls.order_dt = MarketDataOneMinute.close[ind]
                    cls.order_price = MarketDataOneMinute.close[ind]
                elif (1.0 - MarketDataOneMinute.ma_kairi[kairi_term][ind]) <= kairi_kijun:  # entyr buy
                    cls.entry_flg = 'buy'
                    cls.order_dt = MarketDataOneMinute.close[ind]
                    cls.order_price = MarketDataOneMinute.close[ind]
            elif cls.posi_side == '' and (
                    cls.entry_flg == 'buy' or cls.entry_flg == 'sell'):  # check and do process entry
                exe_p = cls.check_execution(ind, cls.entry_flg, cls.order_price)
                if exe_p > 0:
                    cls.posi_price = exe_p
                    cls.posi_side = cls.entry_flg
                    cls.posi_size = 0.11
                    cls.order_dt = MarketDataOneMinute.dt[ind]
                    cls.order_price = 0
                    cls.entry_flg = ''
            elif cls.posi_side == 'buy' or cls.posi_side == 'sell':  # if holidng position
                if (cls.posi_side == 'buy' and MarketDataOneMinute.high[ind] >= pt + cls.posi_price) or \
                        (cls.posi_side == 'sell' and MarketDataOneMinute.low[
                            ind] <= cls.posi_price - pt):  # if pt can be executed
                    price = pt + cls.posi_price if cls.posi_side == 'buy' else cls.posi_price - pt
                    cls.__execute(cls.posi_size * pt)
                if cls.entry_flg == 'lc':
                    exe_p = cls.check_execution(ind, cls.posi_side, cls.order_price)
                    if exe_p > 0:
                        p = cls.order_price - cls.posi_price if cls.posi_side == 'buy' else cls.posi_price - cls.order_price
                        cls.__execute(cls.posi_size * p)
                if (cls.posi_side == 'buy' and MarketDataOneMinute.low[ind] <= cls.posi_price - lc) or \
                        (cls.posi_side == 'sell' and MarketDataOneMinute.high[
                            ind] >= cls.posi_price + lc):  # entry lc order
                    cls.entry_flg = 'lc'
                    cls.order_dt = MarketDataOneMinute.dt[ind]
                    cls.order_price = MarketDataOneMinute.low[ind] if cls.posi_side == 'buy' else \
                    MarketDataOneMinute.high[ind]
            opsim_num +=1
        print('pl={}, num_trade={}, win_rate={}'.format(cls.pl, cls.num_trade, cls.win_rate))
        return (cls.pl, cls.num_trade, cls.win_rate, cls.pl_log)


if __name__ == '__main__':
    MarketDataOneMinute.initialize(2019,1,1,2019,1,30)
    sim = SimpleSimOhlc()
    sim.sim_contrarian_kairi_conti_optuna(5000, 10000)
    #sim.sim_contrarian_kairi(100,len(MarketDataOneMinute.dt), '50', 0.01, 1500, 500)