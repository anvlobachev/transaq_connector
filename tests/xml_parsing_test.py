"""
Created on Wed Aug 05 17:09:45 2015

@author: Roma
"""

import unittest as ut
from structures import *
from datetime import datetime as dt


class TestClientOrders(ut.TestCase):
    """Проверяет клиентские ордера"""
    @classmethod
    def setUpClass(cls):
        with open('orders.xml') as xml:
            cls.obj = parse(xml.read())

    def test_packet(self):
        """Тест пакета"""
        self.assertIsInstance(self.obj, ClientOrderPacket)
        self.assertEqual(len(self.obj.items), 4)

    def test_order1(self):
        """Первый ордер"""
        obj = self.obj.items[0]
        self.assertIsInstance(obj, Order)
        self.assertEqual(obj.id, 4581)
        self.assertEqual(str(obj.order_no), '2693279377')
        self.assertEqual(obj.secid, 21)
        self.assertEqual(obj.board, 'TQBR')
        self.assertEqual(obj.seccode, 'MTSI')
        self.assertEqual(obj.value, 7539.3)
        self.assertEqual(obj.client, 'test/C282166')
        self.assertEqual(obj.status, 'matched')
        self.assertEqual(obj.buysell, 'B')
        self.assertEqual(obj.time, dt(2015, 8, 10, 16, 11, 30))
        self.assertEqual(obj.broker_ref, '')
        self.assertEqual(obj.accrued_int, 0.0)
        self.assertEqual(obj.settle_code, 'Y2')
        self.assertEqual(obj.balance, 0)
        self.assertEqual(obj.price, 0)
        self.assertEqual(obj.quantity, 3)
        self.assertEqual(obj.hidden, 0)
        self.assertEqual(obj.yld, 0)
        self.assertEqual(obj.withdraw_time, None)
        # self.assertEqual(obj.condition, None)
        self.assertEqual(obj.max_commission, 0)
        self.assertEqual(obj.result, '')

    def test_order2(self):
        """Второй ордер"""
        obj = self.obj.items[1]
        self.assertIsInstance(obj, Order)
        self.assertEqual(obj.id, 4531)
        self.assertEqual(str(obj.order_no), '2693271069')
        self.assertEqual(obj.secid, 21)
        self.assertEqual(obj.board, 'TQBR')
        self.assertEqual(obj.seccode, 'MTSI')
        self.assertEqual(obj.value, 7264.5)
        self.assertEqual(obj.client, 'test/C282166')
        self.assertEqual(obj.status, 'active')
        self.assertEqual(obj.buysell, 'S')
        self.assertEqual(obj.time, dt(2015, 8, 10, 16, 5, 20))
        self.assertEqual(obj.broker_ref, '')
        self.assertEqual(obj.accrued_int, 0.0)
        self.assertEqual(obj.settle_code, 'Y2')
        self.assertEqual(obj.balance, 3)
        self.assertEqual(obj.price, 242.15)
        self.assertEqual(obj.quantity, 3)
        self.assertEqual(obj.hidden, 0)
        self.assertEqual(obj.yld, 0)
        self.assertEqual(obj.withdraw_time, None)
        # self.assertEqual(obj.condition, None)
        self.assertEqual(obj.max_commission, 0)
        self.assertEqual(obj.result, '')

    def test_order3(self):
        """Третий ордер"""
        obj = self.obj.items[2]
        self.assertIsInstance(obj, TakeProfit)
        self.assertEqual(obj.id, 4571)
        self.assertEqual(str(obj.order_no), '2693279377')
        self.assertEqual(obj.secid, 21)
        self.assertEqual(obj.board, 'TQBR')
        self.assertEqual(obj.seccode, 'MTSI')
        self.assertEqual(obj.client, 'test/C282166')
        self.assertEqual(obj.status, 'tp_executed')
        self.assertEqual(obj.buysell, 'B')
        self.assertEqual(obj.canceller, '00000282166')
        self.assertEqual(str(obj.alltrade_no), '2693113024')
        self.assertEqual(obj.author, '00000282166')
        self.assertEqual(obj.valid_before, dt(2015, 8, 10, 16, 30))
        self.assertEqual(obj.accept_time, dt(2015, 8, 10, 16, 11, 26))
        self.assertEqual(obj.activation_price, 242.0)
        self.assertEqual(obj.quantity, 3)
        self.assertEqual(obj.extremum, 239.11)
        self.assertEqual(obj.level, 239.12)
        self.assertEqual(obj.correction, 0.01)
        self.assertEqual(obj.withdraw_time, None)
        self.assertEqual(obj.result, u"TP исполнен".encode(
            'utf8').decode('cp1251'))

    def test_order4(self):
        """Четвертый ордер"""
        obj = self.obj.items[3]
        self.assertIsInstance(obj, StopLoss)
        self.assertEqual(obj.id, 4561)
        self.assertEqual(obj.secid, 21)
        self.assertEqual(obj.board, 'TQBR')
        self.assertEqual(obj.seccode, 'MTSI')
        self.assertEqual(obj.client, 'test/C282166')
        self.assertEqual(obj.status, 'watching')
        self.assertEqual(obj.buysell, 'B')
        self.assertEqual(obj.canceller, '00000282166')
        self.assertEqual(obj.author, '00000282166')
        self.assertEqual(obj.valid_before, dt(2015, 8, 10, 16, 30))
        self.assertEqual(obj.accept_time, dt(2015, 8, 10, 16, 11, 26))
        self.assertEqual(obj.activation_price, 243.0)
        self.assertEqual(obj.quantity, 3)
        self.assertEqual(obj.use_credit, True)
        self.assertEqual(obj.withdraw_time, None)


class TestClientTrades(ut.TestCase):
    @classmethod
    def setUpClass(cls):
        with open('trades.xml') as xml:
            cls.obj = parse(xml.read())

    def test_trade1(self):
        obj = self.obj.items[0]
        self.assertIsInstance(obj, ClientTrade)
        self.assertEqual(obj.secid, 21)
        self.assertEqual(str(obj.id), '2693113027')
        self.assertEqual(str(obj.order_no), '2693279377')
        self.assertEqual(obj.board, 'TQBR')
        self.assertEqual(obj.seccode, 'MTSI')
        self.assertEqual(obj.client, 'test/C282166')
        self.assertEqual(obj.buysell, 'B')
        self.assertEqual(obj.time, dt(2015, 8, 10, 16, 11, 30))
        self.assertEqual(obj.broker_ref, '')
        self.assertEqual(obj.value, 7180.5)
        self.assertEqual(obj.commission, 0)
        self.assertEqual(obj.price, 239.35)
        self.assertEqual(obj.quantity, 3)
        self.assertEqual(obj.items, 30)
        self.assertEqual(obj.current_position, 30)
        self.assertEqual(obj.accrued_int, 0)
        self.assertEqual(obj.trade_type, 'T')
        self.assertEqual(obj.settle_code, 'Y2')

    def test_trade2(self):
        obj = self.obj.items[1]
        self.assertIsInstance(obj, ClientTrade)
        self.assertEqual(obj.secid, 21)
        self.assertEqual(str(obj.id), '2692109248')
        self.assertEqual(str(obj.order_no), '2692232421')
        self.assertEqual(obj.board, 'TQBR')
        self.assertEqual(obj.seccode, 'MTSI')
        self.assertEqual(obj.client, 'test/C282166')
        self.assertEqual(obj.buysell, 'S')
        self.assertEqual(obj.time, dt(2015, 8, 9, 15, 32, 40))
        self.assertEqual(obj.broker_ref, '')
        self.assertEqual(obj.value, 2415.2)
        self.assertEqual(obj.commission, 0)
        self.assertEqual(obj.price, 241.52)
        self.assertEqual(obj.quantity, 1)
        self.assertEqual(obj.items, 10)
        self.assertEqual(obj.current_position, -10)
        self.assertEqual(obj.accrued_int, 0)
        self.assertEqual(obj.trade_type, 'T')
        self.assertEqual(obj.settle_code, 'Y2')

    def test_packet(self):
        self.assertIsInstance(self.obj, ClientTradePacket)
        self.assertEqual(len(self.obj.items), 2)


class TestClientPortfolio(ut.TestCase):
    @classmethod
    def setUpClass(cls):
        with open('portfolio.xml') as xml:
            cls.obj = parse(xml.read())

    def test_portfolio_tplus(self):
        obj = self.obj
        self.assertIsInstance(obj, ClientPortfolio)
        self.assertEqual(obj.client, 'test/C282166')
        self.assertEqual(obj.coverage_fact, 56325.08)
        self.assertEqual(obj.coverage_plan, 56325.08)
        self.assertEqual(obj.coverage_crit, 56325.08)
        self.assertEqual(obj.open_equity, 291368.30)
        self.assertEqual(obj.equity, 291076.74)
        self.assertEqual(obj.cover, 291076.74)
        self.assertEqual(obj.init_margin, 516.78)
        self.assertEqual(obj.pnl_income, 3.84)
        self.assertEqual(obj.pnl_intraday, -295.4)
        self.assertEqual(obj.leverage, 1)
        self.assertEqual(obj.margin_level, 516.78)
        self.assertTrue(obj.money)
        self.assertEqual(obj.money.open_balance, 290855.36)
        self.assertEqual(obj.money.bought, 106537.60)
        self.assertEqual(obj.money.sold, 106242.20)
        self.assertEqual(obj.money.balance, 290559.96)
        self.assertEqual(obj.money.settled, 0)
        self.assertEqual(obj.money.tax, 0)
        self.assertTrue(obj.money.value_parts and len(
            obj.money.value_parts) == 3)
        _o = obj.money.value_parts[0]
        self.assertEqual(_o.register, 'C')

        self.assertEqual(_o.open_balance, 190855.36)
        self.assertEqual(_o.balance, 190855.36)
        self.assertEqual(_o.bought, 0)
        self.assertEqual(_o.sold, 0)
        self.assertEqual(_o.settled, 0)
        _o = obj.money.value_parts[1]
        self.assertEqual(_o.register, 'T0')
        self.assertEqual(_o.open_balance, 100000.00)
        self.assertEqual(_o.balance, 100000.00)
        self.assertEqual(_o.bought, 0)
        self.assertEqual(_o.sold, 0)
        self.assertEqual(_o.settled, 0)
        _o = obj.money.value_parts[2]
        self.assertEqual(_o.register, 'Y2')
        self.assertEqual(_o.open_balance, 0)
        self.assertEqual(_o.balance, -295.4)
        self.assertEqual(_o.bought, 106537.60)
        self.assertEqual(_o.sold, 106242.20)
        self.assertEqual(_o.settled, 0)
        self.assertTrue(obj.securities and len(obj.securities) == 2)
        _o = obj.securities[0]
        self.assertEqual(_o.secid, 1)
        self.assertEqual(_o.market, 1)
        self.assertEqual(_o.seccode, 'GAZP')
        self.assertEqual(_o.price, 172.26)
        self.assertEqual(_o.open_balance, 3)
        self.assertEqual(_o.bought, 0)
        self.assertEqual(_o.sold, 0)
        self.assertEqual(_o.balance, 3)
        self.assertEqual(_o.buying, 0)
        self.assertEqual(_o.selling, 0)
        self.assertEqual(_o.cover, 516.78)
        self.assertEqual(_o.init_margin, 516.78)
        self.assertEqual(_o.riskrate_long, 100)
        self.assertEqual(_o.riskrate_short, 100)
        self.assertEqual(_o.pnl_income, 3.84)
        self.assertEqual(_o.pnl_intraday, 0)
        self.assertEqual(_o.max_buy, 1687)
        self.assertEqual(_o.max_sell, 1693)
        self.assertTrue(_o.value_parts and len(_o.value_parts) == 1)
        _o = _o.value_parts[0]
        self.assertEqual(_o.register, 'T0')
        self.assertEqual(_o.open_balance, 3)
        self.assertEqual(_o.balance, 3)
        self.assertEqual(_o.bought, 0)
        self.assertEqual(_o.sold, 0)
        self.assertEqual(_o.settled, 0)
        _o = obj.securities[1]
        self.assertEqual(_o.secid, 21)
        self.assertEqual(_o.market, 1)
        self.assertEqual(_o.seccode, 'MTSI')
        self.assertEqual(_o.price, 241.76)
        self.assertEqual(_o.open_balance, 0)
        self.assertEqual(_o.bought, 440)
        self.assertEqual(_o.sold, 440)
        self.assertEqual(_o.balance, 0)
        self.assertEqual(_o.buying, 0)
        self.assertEqual(_o.selling, 0)
        self.assertEqual(_o.cover, 0)
        self.assertEqual(_o.init_margin, 0)
        self.assertEqual(_o.riskrate_long, 100)
        self.assertEqual(_o.riskrate_short, 100)
        self.assertEqual(_o.pnl_income, 0)
        self.assertEqual(_o.pnl_intraday, -295.4)
        self.assertEqual(_o.max_buy, 120)
        self.assertEqual(_o.max_sell, 120)
        self.assertTrue(_o.value_parts and len(_o.value_parts) == 1)
        _o = _o.value_parts[0]
        self.assertEqual(_o.register, 'Y2')
        self.assertEqual(_o.open_balance, 0)
        self.assertEqual(_o.balance, 0)
        self.assertEqual(_o.bought, 440)
        self.assertEqual(_o.sold, 440)
        self.assertEqual(_o.settled, 0)


class TestServerStatuses(ut.TestCase):
    @classmethod
    def setUpClass(cls):
        with open('server_statuses.xml') as xml:
            cls.statuses = list(map(parse, xml.readlines()))

    def test_server_status1(self):
        obj = self.statuses[0]
        self.assertEqual(obj.id, 0)
        self.assertEqual(obj.connected, "false")
        self.assertEqual(obj.text, None)
        self.assertEqual(obj.timezone, "Arab Standard Time")
        self.assertEqual(obj.text, None)
        self.assertEqual(obj.recover, False)

    def test_server_status2(self):
        obj = self.statuses[1]
        self.assertEqual(obj.id, 0)
        self.assertEqual(obj.connected, "true")
        self.assertEqual(obj.text, None)
        self.assertEqual(obj.timezone, "Arab Standard Time")
        self.assertEqual(obj.text, None)
        self.assertEqual(obj.recover, False)

    def test_server_status3(self):
        obj = self.statuses[2]
        self.assertEqual(obj.id, None)
        self.assertEqual(obj.connected, "error")
        expected_msg = u"Пользователь с таким идентификатором уже подключен к серверу"
        self.assertEqual(obj.text, expected_msg.encode(
            'utf8').decode('cp1251'))
        self.assertEqual(obj.timezone, None)
        self.assertEqual(obj.recover, False)


class TestHistoryCandles(ut.TestCase):
    @classmethod
    def setUpClass(cls):
        with open('candles.xml') as xml:
            cls.obj = parse(xml.read())

    def test_packet(self):
        obj = self.obj
        self.assertIsInstance(obj, HistoryCandlePacket)
        self.assertEqual(len(obj.items), 3)
        self.assertEqual(obj.board, 'TQBR')
        self.assertEqual(obj.seccode, 'VTBR')
        self.assertEqual(obj.period, 1)
        self.assertEqual(obj.status, 1)

    def test_candle1(self):
        obj = self.obj.items[1]
        self.assertEqual(obj.date, dt(2015, 8, 11, 23, 8))
        self.assertEqual(obj.open, 0.1037)
        self.assertEqual(obj.close, 0.1037)
        self.assertEqual(obj.high, 0.1037)
        self.assertEqual(obj.low, 0.1037)
        self.assertEqual(obj.volume, 257485)
        self.assertEqual(obj.open_interest, None)


class TestDateTimeMapper(ut.TestCase):
    def setUp(self):
        self.mapper = NullableDateTimeMapper(TIME_FORMAT)

    def test_null(self):
        self.assertEqual(self.mapper.to_python(None), None)
        self.assertEqual(self.mapper.to_python('0'), None)

    def test_norm(self):
        self.assertEqual(self.mapper.to_python(
            '11.08.2015 23:08:00.000'), dt(2015, 8, 11, 23, 8))


class TestGlobalParse(ut.TestCase):
    def test_candles(self):
        with open('candles.xml') as xml:
            obj = parse(xml.read())
        self.assertTrue(obj and isinstance(obj, HistoryCandlePacket))

    def test_portfolio(self):
        with open('portfolio.xml') as xml:
            obj = parse(xml.read())
        self.assertTrue(obj and isinstance(obj, ClientPortfolio))

    def test_orders(self):
        with open('orders.xml') as xml:
            obj = parse(xml.read())
        self.assertTrue(obj and isinstance(obj, ClientOrderPacket))

    def test_trades(self):
        with open('trades.xml') as xml:
            obj = parse(xml.read())
        self.assertTrue(obj and isinstance(obj, ClientTradePacket))


class TestEntity(ut.TestCase):
    def test_some(self):
        xml = "<NoneClass id=\"1\"/>"
        obj = parse(xml)
        self.assertIsNone(obj)


class TestError(ut.TestCase):
    def test_some(self):
        xml = "<error>This babe is too hot</error>"
        obj = parse(xml)
        self.assertEqual(obj.text, "This babe is too hot")


class TestCmdResults(ut.TestCase):
    def test_success(self):
        xml = "<result success=\"true\"/>"
        obj = parse(xml)
        self.assertEqual(obj.success, True)

    def test_fail(self):
        xml = u"<result success=\"false\">\
                <message>Соединение не установлено...</message>\
                </result>"
        obj = parse(xml)
        self.assertEqual(obj.success, False)
        self.assertEqual(obj.text, u"Соединение не установлено...")


class TestClientAccount(ut.TestCase):
    @classmethod
    def setUpClass(cls):
        with open('account.xml') as xml:
            cls.obj = parse(xml.read())

    def test_account(self):
        obj = self.obj
        self.assertEqual(obj.id, "test/C282166")
        self.assertEqual(obj.active, True)
        self.assertEqual(obj.currency, "RUR")
        self.assertEqual(obj.type, "leverage")
#        self.assertEqual(obj.ml_intraday, 1)
#        self.assertEqual(obj.ml_overnight, 1)


class TestMarkets(ut.TestCase):
    def test_some(self):
        xml = "<market id=\"1\">ММВБ</market>"
        obj = parse(xml)
        self.assertEqual(obj.id, 1)
        self.assertEqual(obj.name, u"ММВБ")


class TestSecurity(ut.TestCase):
    @classmethod
    def setUpClass(cls):
        with open('securities.xml') as xml:
            cls.obj = parse(xml.read())

    def test_packet(self):
        self.assertIsInstance(self.obj, SecurityPacket)
        self.assertEqual(len(self.obj.items), 3)

    def test_sec1(self):
        obj = self.obj.items[1]
        self.assertEqual(obj.id, 1)
        self.assertEqual(obj.active, True)
        self.assertEqual(obj.seccode, 'GAZP')
        self.assertEqual(obj.sectype, 'SHARE')
        self.assertEqual(obj.board, 'TQBR')
        self.assertEqual(obj.market, 1)
        self.assertEqual(obj.name, u"Газпром ао".encode(
            'utf8').decode('cp1251'))
        self.assertEqual(obj.decimals, 2)
        self.assertEqual(obj.minstep, .01)
        self.assertEqual(obj.lotsize, 1)
        self.assertEqual(obj.point_cost, 1)
        self.assertEqual(obj.timezone.strip(), "Arab Standard Time")
        self.assertEqual(obj.credit_allowed, True)
        self.assertEqual(obj.bymarket_allowed, True)
        self.assertEqual(obj.nosplit_allowed, True)
        self.assertEqual(obj.immediate_allowed, True)
        self.assertEqual(obj.cancelbalance_allowed, True)


class TestQuotations(ut.TestCase):
    pass


class TestSubscribedTicks(ut.TestCase):
    @classmethod
    def setUpClass(cls):
        with open('alltrades.xml') as xml:
            cls.obj = parse(xml.read())

    def test_packet(self):
        self.assertIsInstance(self.obj, TradePacket)
        self.assertEqual(len(self.obj.items), 3)

    def test_tik1(self):
        obj = self.obj.items[1]
        self.assertEqual(str(obj.id), '2691161113')
        self.assertEqual(obj.secid, 14)
        self.assertEqual(obj.seccode, 'SBER03')
        self.assertEqual(obj.board, 'TQBR')
        self.assertEqual(obj.time, dt(2015, 8, 8, 23, 6, 36))
        self.assertEqual(obj.price, 102.5)
        self.assertEqual(obj.quantity, 118)
        self.assertEqual(obj.buysell, 'B')
        self.assertEqual(obj.trade_period, 'N')
        self.assertEqual(obj.open_interest, None)


class TestSubscribedBidAsks(ut.TestCase):
    @classmethod
    def setUpClass(cls):
        with open('quotes.xml') as xml:
            cls.obj = parse(xml.read())

    def test_packet(self):
        self.assertIsInstance(self.obj, QuotePacket)
        self.assertEqual(len(self.obj.items), 3)

    def test_quote1(self):
        obj = self.obj.items[1]
        self.assertEqual(obj.secid, 3)
        self.assertEqual(obj.board, 'TQBR')
        self.assertEqual(obj.seccode, 'LKOH')
        self.assertEqual(obj.price, 1750.29)
        self.assertEqual(obj.buy, None)
        self.assertEqual(obj.sell, -1)
        self.assertEqual(obj.yld, 0)

    def test_quote2(self):
        obj = self.obj.items[0]
        self.assertEqual(obj.secid, 1)
        self.assertEqual(obj.board, 'TQBR')
        self.assertEqual(obj.seccode, 'GAZP')
        self.assertEqual(obj.price, 169.7)
        self.assertEqual(obj.buy, 1)
        self.assertEqual(obj.sell, None)
        self.assertEqual(obj.yld, 0)


class TestClientPositions(ut.TestCase):
    @classmethod
    def setUpClass(cls):
        with open('positions.xml') as xml:
            cls.obj = parse(xml.read())

    def test_packet(self):
        self.assertIsInstance(self.obj, PositionPacket)
        self.assertEqual(len(self.obj.items), 3)

    def test_pos1(self):
        obj = self.obj.items[0]
        self.assertIsInstance(obj, SecurityPosition)
        self.assertEqual(obj.secid, 1)
        self.assertEqual(obj.market, 1)
        self.assertEqual(obj.client, 'test/C282166')
        self.assertEqual(obj.seccode, 'GAZP')
        self.assertEqual(obj.name, u"Газпром ао".encode(
            'utf8').decode('cp1251'))
        self.assertEqual(obj.saldo_in, 3)
        self.assertEqual(obj.saldo_min, 0)
        self.assertEqual(obj.bought, 0)
        self.assertEqual(obj.sold, 0)
        self.assertEqual(obj.saldo, 3)
        self.assertEqual(obj.order_buy, 0)
        self.assertEqual(obj.order_sell, 0)

    def test_pos2(self):
        obj = self.obj.items[1]
        self.assertIsInstance(obj, SecurityPosition)
        self.assertEqual(obj.secid, 21)
        self.assertEqual(obj.market, 1)
        self.assertEqual(obj.client, 'test/C282166')
        self.assertEqual(obj.seccode, 'MTSI')
        self.assertEqual(obj.name, u"МТС-ао".encode('utf8').decode('cp1251'))
        self.assertEqual(obj.saldo_in, 0)
        self.assertEqual(obj.saldo_min, 0)
        self.assertEqual(obj.bought, 0)
        self.assertEqual(obj.sold, 0)
        self.assertEqual(obj.saldo, 0)
        self.assertEqual(obj.order_buy, 0)
        self.assertEqual(obj.order_sell, 0)

    def test_pos3(self):
        obj = self.obj.items[2]
        self.assertIsInstance(obj, MoneyPosition)
        self.assertEqual(obj.market, [1])
        self.assertEqual(obj.client, 'test/C282166')
        self.assertEqual(obj.asset, 'FOND_MICEX')
        self.assertEqual(obj.name, u"Рубли РФ КЦБ ММВБ".encode(
            'utf8').decode('cp1251'))
        self.assertEqual(obj.saldo_in, 290855.36)
        self.assertEqual(obj.saldo, 290855.36)
        self.assertEqual(obj.bought, 0)
        self.assertEqual(obj.sold, 0)
        self.assertEqual(obj.order_buy, 0)
        self.assertEqual(obj.order_buy_cond, 0)
        self.assertEqual(obj.commission, 0)


class TestLimitsTPlus(ut.TestCase):
    @classmethod
    def setUpClass(cls):
        with open('limits_t+.xml') as xml:
            cls.obj = parse(xml.read())

    def test_limits(self):
        obj = self.obj
        self.assertIsInstance(obj, ClientLimitsTPlus)
        self.assertEqual(obj.client, 'test/C282166')
        self.assertEqual(len(obj.securities), 2)
        _o = obj.securities[0]
        self.assertEqual(_o.secid, 21)
        self.assertEqual(_o.market, 1)
        self.assertEqual(_o.seccode, 'MTSI')
        self.assertEqual(_o.max_buy, 136)
        self.assertEqual(_o.max_sell, 100)
        _o = obj.securities[1]
        self.assertEqual(_o.secid, 1)
        self.assertEqual(_o.market, 1)
        self.assertEqual(_o.seccode, 'GAZP')
        self.assertEqual(_o.max_buy, 1432)
        self.assertEqual(_o.max_sell, 1438)


class TestPits(ut.TestCase):
    @classmethod
    def setUpClass(cls):
        with open('pits.xml') as xml:
            cls.obj = parse(xml.read())

    def test_packet(self):
        self.assertIsInstance(self.obj, SecurityPitPacket)
        self.assertEqual(len(self.obj.items), 3)

    def test_pit1(self):
        obj = self.obj.items[1]
        self.assertEqual(obj.seccode, 'GAZP')
        self.assertEqual(obj.board, 'TQBR')
        self.assertEqual(obj.market, 1)
        self.assertEqual(obj.decimals, 2)
        self.assertEqual(obj.minstep, .01)
        self.assertEqual(obj.lotsize, 1)
        self.assertEqual(obj.point_cost, 1)


class TestBoards(ut.TestCase):
    @classmethod
    def setUpClass(cls):
        with open('boards.xml') as xml:
            cls.obj = parse(xml.read())

    def test_packet(self):
        self.assertIsInstance(self.obj, BoardPacket)
        self.assertEqual(len(self.obj.items), 3)

    def test_board1(self):
        obj = self.obj.items[1]
        self.assertEqual(obj.id, 'TQBR')
        self.assertEqual(obj.market, 1)
        self.assertEqual(obj.type, 1)


class TestMarketOrderAbility(ut.TestCase):
    def test_some(self):
        xml = '<marketord secid="1" seccode="GAZP" permit="yes" />'
        obj = parse(xml)
        self.assertEqual(obj.secid, 1)
        self.assertEqual(obj.seccode, 'GAZP')
        self.assertEqual(obj.permitted, True)


class TestCreditAbility(ut.TestCase):
    def test_some(self):
        xml = '<overnight status="true"/>'
        obj = parse(xml)
        self.assertEqual(obj.overnight, True)
        self.assertEqual(obj.intraday, False)


@ut.skip('No data for sec_info')
class TestSecInfo(ut.TestCase):
    @classmethod
    def setUpClass(cls):
        xml = open('secinfo.xml').read()
        cls.obj = parse(xml)

    def test_secinfo(self):
        obj = self.obj
        self.assertEqual(obj.secname, '')


class TestSecInfoUpd(ut.TestCase):
    @classmethod
    def setUpClass(cls):
        xml = open('secinfoupd.xml').read()
        cls.obj = parse(xml)

    def test_secinfo_upd(self):
        obj = self.obj
        self.assertIsInstance(obj, SecInfoUpdate)
        self.assertEqual(obj.seccode, 'Eu86250BC0')
        self.assertEqual(obj.bgo_c, 5454.72)


@ut.skip('No data for mct portfolio')
class TestPortfolioMCT(ut.TestCase):
    @classmethod
    def setUpClass(cls):
        xml = open('portfolio_mct.xml').read()
        cls.obj = parse(xml)

    def test(self):
        obj = self.obj
        self.assertEqual(obj.secname, '')


if __name__ == '__main__':
    ut.main()
