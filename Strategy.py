from Account import Account
from MarketData import MarketData
from TradeDecisionData import TradeDecisionData

class Startegy:
    @classmethod
    def contrarian_kairi(cls, ind, ac, kairi_term, kairi_kijun, pt, lc):
        tdd = TradeDecisionData()

        if MarketData.ma_kairi[str(kairi_term)][ind] >= 1+kairi_kijun:
            sell
        elif MarketData.ma_kairi[str(kairi_term)][ind] <= 1 - kairi_kijun:
            buy


        return tdd
