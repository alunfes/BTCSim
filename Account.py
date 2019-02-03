from MarketData import MarketData
from numba import jit

class Account:
    def __init__(self):
        #asset / performance
        self.total_asset = 0
        self.num_trade = 0
        self.total_pl = 0
        self.current_pl = 0

        #ordering data
        self.__initialize_order()

        #position data
        self.position_side = 'None'
        self.position_price = 0
        self.position_size = 0
        self.position_datetime = ''
        self.position_ind = ''

        #log
        self.log_total_asset = []
        self.log_pl = []
        self.log_holding_sec = []
        self.action_log = []
        self.num_win = 0
        self.win_ratio = 0

        #config
        self.force_lc = -0.2
        self.latency_sec = 1

    @jit
    def __initialize_order(self):
        self.ordering_side = 'None'
        self.ordering_price = 0
        self.ordering_size = 0
        self.ordering_datetime = ''
        self.ordering_ind = ''
        self.ordering_status = ''

    @jit
    def entry_order(self, side, price, size, ind):
        res = ''
        if self.ordering_status == '':
            self.ordering_status = 'Ordering'
            self.ordering_side = side
            self.ordering_price = price
            self.ordering_size = size
            self.ordering_ind = ind
            self.ordering_datetime = MarketData.datetime[ind]
            self.num_trade +=1
            res = 'OK'
        elif self.ordering_status == 'Ordering':
            self.ordering_status = 'Cancelling'
            res = 'Ordering status and order failed'
        elif self.ordering_status == 'Cancelling':
            res = 'Cancelling status and order failed'
        return res

    @jit
    def exit_order(self, ind, price):
        if self.position_side == 'Long':
            self.entry_order('Short', price, self.position_size, ind)
        elif self.position_side == 'Short':
            self.entry_order('Long', price, self.position_size, ind)
        else:
            print('exit_order should be called when holding position!')

    @jit
    def cancel_order(self, ind):
        self.ordering_status = 'Cancelling'
        self.ordering_datetime = MarketData.datetime[ind]
        self.ordering_ind = ind

    @jit
    def __check_cancel_order(self, ind):
        if self.ordering_status == 'Cancelling':
            if (MarketData.datetime[ind] - self.ordering_datetime).seconds >= self.latency_sec:
                self.__initialize_order()

    @jit
    def __check_and_execution(self, ind):
        if (MarketData.datetime[ind] - self.position_datetime).seconds >= self.latency_sec:
            if self.ordering_side == 'Long':
                if self.ordering_price <= MarketData.price[ind]:
                    self.update_position('Long',self.ordering_price,
                                         self.ordering_size if self.ordering_size <= MarketData.size[ind] else MarketData.size[ind], ind)
            elif self.ordering_side == 'Short':
                if self.ordering_price >= MarketData.price[ind]:
                    self.update_position('Short',self.ordering_price,
                                         self.ordering_size if self.ordering_size <= MarketData.size[ind] else MarketData.size[ind], ind)

    def __exit(self, ind, ex_p, ex_s):

        if self.position_side == 'Long':
            self.num_trade += 1
            p = += ex_s * (ex_p - self.position_price)
                self.total_pl
            self.log_holding_sec.append()
        elif self.position_side == 'Short':
            self.num_trade += 1
            self.total_pl += ex_s * (self.position_price - ex_p)
        else:
            print('position should be Long or Short when exit!')



    @jit
    def __update_position(self, side, price, size, ind):
        if self.position_side =='None':
            self.position_side = side
            self.position_price = price
            self.position_size = size
            self.position_datetime = MarketData.datetime[ind]
            self.position_ind = ind
        elif self.position_side == 'Long':
            if side == 'Long':
                self.position_price = (size * price + self.position_price *self.position_size) / (self.position_size + size)
                self.position_size += size
            elif side == 'Short':
                s = self.position_size - size
                if s == 0:
                    self.position_side = 'None'
                    self.ordering_price = 0
                    self.position_size = 0
                    self.position_datetime = ''
                    self.position_ind = 0
                elif s > 0:
                    self.position_size = s
                elif s < 0:
                    self.position_price = price
                    self.position_side = 'Short'
                    self.position_size = -s
                    self.position_datetime = MarketData.datetime[ind]
                    self.position_ind = ind
        elif self.position_side == 'Short':
            if side == 'Short':
                self.position_price = (size * price + self.position_price *self.position_size) / (self.position_size + size)
                self.position_size += size
            elif side == 'Long':
                s = self.position_size - size
                if s == 0:
                    self.position_side = 'None'
                    self.ordering_price = 0
                    self.position_size = 0
                    self.position_datetime = ''
                    self.position_ind = 0
                elif s > 0:
                    self.position_size = s
                elif s < 0:
                    self.position_price = price
                    self.position_side = 'Long'
                    self.position_size = -s
                    self.position_datetime = MarketData.datetime[ind]
                    self.position_ind = ind


    @jit
    def move_to_next(self, ind):
        #
        if self.position_side == 'Long':
        elif self.position_side == 'Short':

        self.__check_cancel_order(ind)
        self.__check_force_lc(ind)
        self.__calc_unrealized_pl(ind)

    @jit
    def __check_force_lc(self, ind):
        if self.position_side == 'Long':
            return  True if (self.position_price / MarketData.price[ind]) - 1.0 <= self.force_lc else False
        elif self.position_side == 'Short':
            return True if (MarketData.price[ind]/self.position_price) - 1.0 <= self.force_lc else False
        else:
            return False

    @jit
    def __calc_unrealized_pl(self, ind):
        if self.position_side == 'Long':
            self.current_pl = self.position_size * (MarketData.price[ind] - self.position_price)
        elif self.position_side == 'Short':
            self.current_pl = self.position_size * (self.position_price - MarketData.price[ind])
        else:
            self.current_pl = 0
