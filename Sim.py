import Account
import Strategy
import MarketData

class Sim:
    def __init__(self):
        print()

    def startKairiSim(self, start_ind, end_ind, kairi_term, kairi_kijun, pt, lc):
        ac = Account.Account()
        for i in range(end_ind - start_ind):
            tdd = Strategy.Startegy.contrarian_kairi(i + start_ind, ac, kairi_term, kairi_kijun, pt, lc)

    def simple_sim(self, start_ind, end_ind, kairi_term, kairi_kijun, pt, lc, delay_sec):
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

        for i in range(end_ind - start_ind):
            ind = i + start_ind
            if entry_flg == '':
                if (MarketData.MarketData.ma_kairi[ind] -1.0) >= kairi_kijun: #entry sell
                    entry_flg = 'sell'
                    order_dt = MarketData.MarketData.datetime[ind]
                elif (1.0-MarketData.MarketData.ma_kairi[ind]) <= kairi_kijun: #entry buy
                    entry_flg = 'buy'
                    order_dt = MarketData.MarketData.datetime[ind]
            elif posi_side == '' and (entry_flg == 'buy' or entry_flg == 'sell'):
                if (MarketData.MarketData.datetime[ind] - order_dt).seconds >= delay_sec:
                    posi_price = MarketData.MarketData.price[ind]
                    posi_side = entry_flg
                    posi_size = 0.01
                    order_dt = MarketData.MarketData.datetime[ind]
            elif posi_side == 'buy' or posi_side == 'sell':
                if (MarketData.MarketData.datetime[ind] - order_dt).seconds >= delay_sec:












