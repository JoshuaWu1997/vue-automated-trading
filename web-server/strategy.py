import numpy as np
import time
from dealers.mysql_dealer import Dealer
from crawler import Crawler
import json


class BasicStrategy:
    def __init__(self, trade_id, socket=None):
        self.unit = 100
        self.scale = 1000000
        self.trade_id = str(trade_id)
        self.socket = socket

        self.crawler = Crawler()
        self.dealer = Dealer(self.trade_id, self.unit)

        self.n_time = None
        self.p_time = None
        self.tick = None
        self.order = [[], []]

        self.length = 0
        self.round = 0
        self.output_dims = len(self.dealer.stock_list) - 1
        self.replay_buffer = None
        self.model = None

    def process(self):
        if self.p_time is not None:
            if not self.p_time.date() == self.n_time.date():
                self.dealer.get_position()
        self.p_time = self.n_time
        print(self.n_time)
        start_time = time.time()
        s_id = np.asarray([tick[0] for tick in self.crawler.tick])
        curr = np.asarray([tick[2:5] for tick in self.crawler.tick], dtype=float)
        self.dealer.process_order(s_id, curr, self.order, self.n_time)
        self.order = self.get_order(s_id, curr)
        end_time = time.time()
        print('<<<<<<<<<< process_tick uses ' + str(end_time - start_time) + 's >>>>>>>>>>')

    async def run(self):
        while True:
            start_time = time.time()
            if self.crawler.get_info():
                end_time = time.time()
                self.n_time = self.crawler.timestamp
                print('<<<<<<<<<< get_tick uses ' + str(end_time - start_time) + 's >>>>>>>>>>')
                self.process()
                await self.send_socket()
            time.sleep(0.1)

    async def test(self):
        timestamps, ticks = self.dealer.get_test_ticks()
        for self.n_time in timestamps:
            self.crawler.tick = ticks[self.n_time]
            print('<<<<<<<<<< get_tick  >>>>>>>>>>')
            self.process()
            await self.send_socket()
            time.sleep(0.5)

    async def send_socket(self):
        s_id = np.asarray([tick[0] for tick in self.crawler.tick])
        curr = np.asarray([tick[2:4] for tick in self.crawler.tick], dtype=float)
        if self.round == 1:
            self.init = curr
        socket_msg = dict()
        socket_msg['curr_time'] = str(self.n_time)
        socket_msg['net_value'] = self.dealer.net_value
        socket_msg['sh50'] = curr[0, 0] / self.baseline * self.scale
        position = (self.dealer.position['total'] * self.dealer.position['curr_price']).values.ravel()
        s_list = self.dealer.position.index.values.ravel()[position > 0]
        position = position[position > 0].astype(np.int).astype(np.str)
        socket_msg['position'] = [{'Target': 'Cash', 'Volume': str(self.dealer.cash)}]
        socket_msg['position'].extend([{'Target': i, 'Volume': j} for i, j in zip(s_list, position)])
        curr = (curr - self.init) / self.init
        socket_msg['market_info'] = [{'stock_id': ID, 'buy': CURR[0], 'sell': CURR[1]} for ID, CURR in zip(s_id, curr)]
        await self.socket.send(json.dumps(socket_msg))

    def load_model(self):
        pass

    def get_pred(self):
        return []

    def pred2amount(self, y_pred, y_curr, position):
        return []

    def get_order(self, s_id, curr):
        print('round: ', self.round)
        ids, amount = [], []
        avail = self.dealer.position.loc[s_id, 'volume'].values[1:].ravel()
        if self.round < self.length - 1:
            print('get_data')
            self.replay_buffer[self.round] = curr[1:].T
        else:
            print('broking')
            self.replay_buffer[-1] = curr[1:].T
            y_pred = self.get_pred()
            amount = self.pred2amount(y_pred, curr[1:, 1].ravel(), avail)
            ids = np.asarray(s_id)[1:]
            ids = ids[amount != 0]
            amount = amount[amount != 0]
            self.replay_buffer[:-1] = self.replay_buffer[1:]
        if self.round == 0:
            self.baseline = curr[0, 0]
            print('baseline:\t', self.scale)
        else:
            print('baseline:\t', curr[0, 0] / self.baseline * self.scale)
        self.round += 1
        return ids, amount


if __name__ == '__main__':
    from modules.MLP import Strategy

    broker = Strategy(8)
    broker.test()
