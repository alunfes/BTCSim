from MarketData import MarketData
from numba import jit


class Account:
    def __init__(self):
        #asset / performance
        self.total_asset = 0
        self.num_trade = 0
        self.total_pl = 0
        self.current_pl = 0
        self.ave_pl = 0

        #ordering data
        self.__initialize_order()

        #position data
        self.__initialize_position()

        #log
        self.log_total_asset = {}
        self.log_total_pl = {}
        self.log_pl = {}
        self.action_log = {}
        self.num_win = 0
        self.win_ratio = 0

        #config
        self.force_lc = -0.2
        self.latency_sec = 1

        #flg
        self.cancelling_all_orders = False


    @jit
    def __initialize_order(self):
        self.ordering_side = [] #buy, sell
        self.ordering_price = []
        self.ordering_size = []
        self.ordering_datetime = []
        self.ordering_ind = [] #index in sim
        self.ordering_status = [] #bording, ordering, cancelling, executed

    @jit
    def __initialize_position(self):
        self.position_side = 'None'  # None, buy, sell
        self.position_price = 0
        self.position_size = 0
        self.position_datetime = ''
        self.position_ind = ''

    @jit
    def __remove_ordering(self,ordering_ind):
        self.ordering_ind.pop(ordering_ind)
        self.ordering_price.pop(ordering_ind)
        self.ordering_status.pop(ordering_ind)
        self.ordering_size.pop(ordering_ind)
        self.ordering_side.pop(ordering_ind)
        self.ordering_datetime.pop(ordering_ind)

    @jit
    def __update_total_pl(self, ind, ordering_ind, lot):
        pl =0
        if self.position_side == 'buy' and self.ordering_side[ordering_ind] == 'sell':
            pl = (self.ordering_price[ordering_ind] - self.position_price) * lot
        elif self.position_side == 'sell' and self.ordering_side[ordering_ind] == 'buy':
            pl = (self.position_price - self.ordering_price[ordering_ind]) * lot
        self.num_trade +=1
        self.num_win += 1 if pl >0 else 0
        self.total_pl +=pl
        self.current_pl = pl
        self.log_pl.append(ind, pl)
        self.log_total_pl.append(ind, self.total_pl)
        self.__remove_ordering(ordering_ind)

    def get_order(self, ind):
        print('side={},price={},size={},dt={},status={}'.format(self.ordering_side[ind], self.ordering_price[ind], self.ordering_size[ind]
                                                                , self.ordering_datetime[ind], self.ordering_status[ind]))
        return dict(side=self.ordering_side[ind], price=self.ordering_price[ind], size=self.ordering_size[ind], datetime=self.ordering_datetime[ind],
                    ind=self.ordering_ind[ind], status=self.ordering_status[ind])

    def get_all_orders(self):
        return {'side':self.ordering_side, 'price':self.ordering_price, 'size':self.ordering_size, 'datetime':self.ordering_datetime,
                'ind':self.ordering_ind, 'status':self.ordering_status}

    @jit
    def entry_order(self, side, price, size, ind):
        res = 'cancelling all orders!'
        if self.cancelling_all_orders == False:
            self.ordering_side.append(side)
            self.ordering_price.append(price)
            self.ordering_size.append(size)
            self.ordering_ind.append(ind)
            self.ordering_datetime.append(MarketData.datetime[ind])
            self.ordering_status.append('bording')
            res = 'oK'
        return res

    @jit
    def exit_all_orders(self, ind):
        if self.cancelling_all_orders == False:
            self.cancelling_all_orders = True
            map(lambda x: 'cancelling', self.ordering_status)

    @jit
    def cancel_order(self, ind):
        self.ordering_status[ind] = 'cancelling'

    @jit
    def __check_order_ordering(self, ind): #check if boarding order changed to ordering
        if self.cancelling_all_orders == False:
            for o in range(len(self.ordering_status)):
                if self.ordering_status[o] == 'boarding' and (MarketData.datetime[ind] - self.ordering_datetime).seconds >= self.latency_sec:
                    self.ordering_status = 'ordering'

    @jit
    def __check_order_execution(self, ind):
        for i, dt in enumerate(self.ordering_datetime):
            if (MarketData.datetime[ind] - dt).seconds >= self.latency_sec and self.ordering_status[i] == 'ordering':
                if self.ordering_side[i] == 'buy' and self.ordering_price[i] >= MarketData.price[ind]:
                    self.__execute(ind, i)
                elif self.ordering_side[i] == 'buy' and self.ordering_price[i] >= MarketData.price[ind]:
                    self.__execute(ind, i)


    @jit
    def __execute(self, ind, ordering_ind):
        lot = self.ordering_size[ordering_ind] if self.ordering_size[ordering_ind] <= MarketData.size[ind] else MarketData.size[ind]

        if self.position_side == 'None':
            self.position_side = self.ordering_side[ordering_ind]
            self.position_price = self.ordering_price[ordering_ind]
            self.position_size = self.ordering_size[ordering_ind]
            self.position_datetime = MarketData.datetime[ind]
            self.position_ind = ind
        elif self.position_side == 'buy':
            if self.ordering_side[ordering_ind] == 'buy':
                self.position_price = (self.ordering_size[ordering_ind] * self.ordering_price[ordering_ind] + self.position_price * self.position_size)/\
                                      (self.position_size + self.ordering_size[ordering_ind])
                self.position_size += self.ordering_size[ordering_ind]
                self.position_datetime = MarketData.datetime[ind]
                self.position_ind = ind
            elif self.ordering_side[ordering_ind] == 'sell':
                if lot < self.position_size:
                    self.position_size -= lot
                    self.__update_total_pl(ind,ordering_ind,lot)
                elif lot > self.position_size:
                    self.position_price = self.ordering_price[ordering_ind]
                    self.position_size = lot - self.position_size
                    self.position_side = 'sell'
                    self.position_ind = ind
                    self.position_datetime = MarketData.datetime[ind]
                    self.__update_total_pl(ind,ordering_ind,lot)
                elif lot == self.position_size:
                    self.__update_total_pl(ind,ordering_ind,lot)
                    self.__initialize_position()
        elif self.position_side == 'sell':
            if self.ordering_side[ordering_ind] == 'sell':
                self.position_price = (self.ordering_size[ordering_ind] * self.ordering_price[ordering_ind] + self.position_price * self.position_size)/\
                                      (self.position_size + self.ordering_size[ordering_ind])
                self.position_size += self.ordering_size[ordering_ind]
                self.position_datetime = MarketData.datetime[ind]
                self.position_ind = ind
            elif self.ordering_side[ordering_ind] == 'buy':
                if lot < self.position_size:
                    self.position_size -= lot
                    self.__update_total_pl(ind,ordering_ind,lot)
                elif lot > self.position_size:
                    self.position_price = self.ordering_price[ordering_ind]
                    self.position_size = lot - self.position_size
                    self.position_side = 'buy'
                    self.position_ind = ind
                    self.position_datetime = MarketData.datetime[ind]
                    self.__update_total_pl(ind,ordering_ind,lot)
                elif lot == self.position_size:
                    self.__update_total_pl(ind,ordering_ind,lot)
                    self.__initialize_position()

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
    def move_to_next(self, ind):
        self.__check_order_execution(ind)
        self.__check_cancel_order(ind)
        self.__check_force_lc(ind)
        self.total_asset = self.__calc_unrealized_pl(ind)
        self.log_total_asset.append(ind, self.total_asset)

    @jit
    def last_day_operation(self, ind):
        self.__check_order_execution(ind)
        self.__check_cancel_order(ind)
        self.__check_force_lc(ind)
        self.total_asset = self.__calc_unrealized_pl(ind)
        self.log_total_asset.append(ind, self.total_asset)
        self.win_ratio = float(self.num_win) / float(self.num_trade)
        self.ave_pl = float(self.total_asset) / float(self.num_trade)

    @jit
    def __check_force_lc(self, ind):
        if self.position_side == 'buy':
            return  True if (self.position_price / MarketData.price[ind]) - 1.0 <= self.force_lc else False
        elif self.position_side == 'sell':
            return True if (MarketData.price[ind]/self.position_price) - 1.0 <= self.force_lc else False
        else:
            return False

    @jit
    def __calc_unrealized_pl(self, ind):
        if self.position_side == 'buy':
            self.current_pl = self.position_size * (MarketData.price[ind] - self.position_price)
        elif self.position_side == 'sell':
            self.current_pl = self.position_size * (self.position_price - MarketData.price[ind])
        else:
            self.current_pl = 0
