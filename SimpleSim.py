import Account
import Strategy
import MarketData
from numba import jit

class SimpleSim:
    pl = 0
    pl_log = []
    num_trade = 0
    num_win = 0
    win_rate = 0
    entry_flg = ''
    posi_side = ''
    posi_price = 0
    posi_size = 0
    order_dt = None

    def initialize(self):
        self.pl = 0
        self.pl_log = []
        self.num_trade = 0
        self.num_win = 0
        self.win_rate = 0
        self.entry_flg = ''
        self.posi_side = ''
        self.posi_price = 0
        self.posi_size = 0
        self.order_dt = None

    @jit
    def execute(self, profit):
        self.pl += profit
        self.pl_log.append(self.pl)
        self.num_trade += 1
        if profit > 0:
            self.num_win += 1
        self.win_rate = float(self.num_win) / float(self.num_trade)
        self.posi_side = ''
        self.posi_price = 0
        self.posi_size = 0
        self.order_dt = None
        self.entry_flg = ''

    @jit
    def simple_sim(self, start_ind, end_ind, kairi_term, kairi_kijun, pt, lc, delay_sec):
        self.initialize()

        for i in range(end_ind - start_ind):
            ind = i + start_ind
            if self.entry_flg == '':
                if (MarketData.MarketData.ma_kairi[str(kairi_term)][ind] -1.0) >= kairi_kijun: #entry sell
                    self.entry_flg = 'sell'
                    self.order_dt = MarketData.MarketData.datetime[ind]
                elif (1.0-MarketData.MarketData.ma_kairi[str(kairi_term)][ind]) <= kairi_kijun: #entry buy
                    self.entry_flg = 'buy'
                    self.order_dt = MarketData.MarketData.datetime[ind]
            elif self.posi_side == '' and (self.entry_flg == 'buy' or self.entry_flg == 'sell'): #if ordering
                if (MarketData.MarketData.datetime[ind] - self.order_dt).seconds >= delay_sec: #if order was already boarded
                    self.posi_price = MarketData.MarketData.price[ind]
                    self.posi_side = self.entry_flg
                    self.posi_size = 0.01
                    self.order_dt = MarketData.MarketData.datetime[ind]
            elif self.posi_side == 'buy' or self.posi_side == 'sell': #if holding position
                if (MarketData.MarketData.datetime[ind] - self.order_dt).seconds >= delay_sec:
                    if (self.posi_side == 'buy' and MarketData.MarketData.price[ind] >= pt + self.posi_price) or \
                            (self.posi_side == 'sell' and MarketData.MarketData.price[ind] <= self.posi_price - pt):
                            self.execute(self.posi_size * pt)
                    if (self.posi_side == 'buy' and MarketData.MarketData.price[ind] <= self.posi_price - lc) or \
                            (self.posi_side == 'sell' and MarketData.MarketData.price[ind] >= self.posi_price + lc):
                        self.entry_flg = 'lc'
                        self.order_dt = MarketData.MarketData.datetime[ind]
                elif self.entry_flg =='lc' and (MarketData.MarketData.datetime[ind] - self.order_dt).seconds >= delay_sec:
                    p = MarketData.MarketData.price[ind] - self.posi_price if self.posi_side == 'buy' else self.posi_price - MarketData.MarketData.price[ind]
                    self.execute(self.posi_size * p)

        print('pl={}, num_trade={}, win_rate={}'.format(self.pl, self.num_trade, self.win_rate))

















