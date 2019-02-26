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










