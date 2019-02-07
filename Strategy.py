from Account import Account
from MarketData import MarketData
import TradeDecisionData

class Startegy:
    @classmethod
    def contrarian_kairi(cls, ind, ac: Account, kairi_term, kairi_kijun, pt, lc):
        tdd = TradeDecisionData.TradeDecisionData()
        tdd.side = 'None'

        tdd.price = MarketData.price[ind]
        tdd.size = 0.5

        # none position & order & kairi
        if ac.ordering_side == 'None' and ac.position_side == 'None':
            if MarketData.ma_kairi[str(kairi_term)][ind] >= 1+kairi_kijun:
                tdd.side = 'sell'
            elif MarketData.ma_kairi[str(kairi_term)][ind] <= 1 - kairi_kijun:
                tdd.side = 'buy'
        elif ac.ordering_side == 'buy' and ac.position_side == 'None':
            if MarketData.ma_kairi[str(kairi_term)][ind] >= 1+kairi_kijun:
                tdd.side = 'cancel'
            elif MarketData.ma_kairi[str(kairi_term)][ind] <= 1 - kairi_kijun:
                tdd.side = 'None'
        elif ac.ordering_side == 'sell' and ac.position_side == 'None':
            if MarketData.ma_kairi[str(kairi_term)][ind] >= 1+kairi_kijun:
                tdd.side = 'None'
            elif MarketData.ma_kairi[str(kairi_term)][ind] <= 1 - kairi_kijun:
                tdd.side = 'cancel'
        elif ac.ordering_side == 'None' and ac.position_side == 'buy':
            tdd.side = 'sell'
            tdd.size = ac.position_size
            tdd.price = ac.position_price + pt



        # none position & none order & buy/sell kairi -> buy or sell
        # none position & buy order & plus kairi -> cancel order
        # none position & buy order & minus kairi -> do nothing
        # none position & sell order & plus kairi -> do nothing
        # none position & sell order & minus kairi -> cancel order
        # buy/sell position & order & kairi ->pt lc order, other than do nothing




        return tdd
