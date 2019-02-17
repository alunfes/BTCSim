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

        if ac.position_side == 'None': #before entry
            if ac.ordering_side == 'None':
                if MarketData.ma_kairi[str(kairi_term)][ind] >= 1+kairi_kijun:
                    tdd.side = 'sell'
                elif MarketData.ma_kairi[str(kairi_term)][ind] <= 1 - kairi_kijun:
                    tdd.side = 'buy'
            elif ac.ordering_side == 'buy':
                if MarketData.ma_kairi[str(kairi_term)][ind] >= 1+kairi_kijun:
                    tdd.side = 'cancel'
                elif MarketData.ma_kairi[str(kairi_term)][ind] <= 1 - kairi_kijun:
                    tdd.side = 'None'
            elif ac.ordering_side == 'sell':
                if MarketData.ma_kairi[str(kairi_term)][ind] >= 1+kairi_kijun:
                    tdd.side = 'None'
                elif MarketData.ma_kairi[str(kairi_term)][ind] <= 1 - kairi_kijun:
                    tdd.side = 'cancel'
        else: #after entry
            orders = Account .get_all_orders()
            if ac.position_side == 'buy':
                orders['price']
                #pt order
                #lc order
                #wait for execution of pt / lc
            elif ac.position_side == 'sell':
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
