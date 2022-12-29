"""
Wrapper over Trasaq C# dll
"""
import os
import commands as cmd
import structures as ss
import asyncio


class TransaqConnection():
    """
    Transaq connection entity
    """

    def __init__(self, logdir, loglevel=2):
        """
        :param logdir: log directory.
        :param loglevel: level of logs 1(min) to 3(max) 2 is default.
        :logfile_lifetime: days how long log files lives.
        """
        self.connected = False

        if not os.path.exists(logdir):
            os.mkdir(logdir)

        # словарь соответствий типов сообщений от сервера и функций, обрабатывающих эти сообщения
        self.__msg_handlers = {
            ss.BoardPacket.__name__: self.on_board_packet,
            ss.CandleKindPacket.__name__: self.on_candle_kind_packet,
            ss.ClientAccount.__name__: self.on_client_account,
            ss.CreditAbility.__name__: self.on_credit_ability,
            ss.ClientOrderPacket.__name__: self.on_client_order_packet,
            ss.HistoryCandlePacket.__name__: self.on_history_candle_packet,
            ss.HistoryTickPacket.__name__: self.on_history_tick_packet,
            ss.MarketPacket.__name__: self.on_market_packet,
            ss.PositionPacket.__name__: self.on_position_packet,
            ss.QuotationPacket.__name__: self.on_quotation_packet,
            ss.QuotePacket.__name__: self.on_quote_packet,
            ss.SecurityPacket.__name__: self.on_security_packet,
            ss.SecurityPitPacket.__name__: self.on_security_pit_packet,
            ss.SecInfoUpdate.__name__: self.on_sec_info_update,
            ss.ServerStatus.__name__: self.on_server_status,
            ss.TextMessagePacket.__name__: self.on_text_message_packet,
            ss.TradePacket.__name__: self.on_trade_packet,
        }

        cmd.initialize(logdir, loglevel, self.__msg_handler)

    def __del__(self):
        """
        Closes Callback connections. Perform disconnect if neccecary.
        :return:
        """
        if self.connected:
            cmd.disconnect()
        cmd.uninitialize()

    def __msg_handler(self, obj):
        # определяем, какой тип пакета пришёл от сервера
        packet_class_name = type(obj).__name__
        # определяем, какую функцию надо вызвать для обработки этого пакета
        fn = self.__msg_handlers.get(packet_class_name, self.on_unknown_packet)
        # асинхронно вызываем эту функцию и передаем пакет в качестве параметра
        asyncio.run(fn(obj))

    def connect(self, login, password, server, min_delay=100):
        """
        Connects to server
        """
        return cmd.connect(login, password, server, min_delay=min_delay)

    async def async_connect(self, login, password, server, min_delay=100):
        """
        Async connection to server.
        :param login:
        :param password:
        :param server:
        :param min_delay:
        :return: True if conneted, overwise, False
        """
        res = cmd.connect(login, password, server, min_delay=min_delay)
        if res.success:
            for _ in range(1, 50):
                await asyncio.sleep(3)
                if self.connected:
                    return True
        return self.connected

    # Функции-обработчики пакетов, отправленных с сервера.
    # При необходимости их нужно переопределить в классе-наследнике.

    async def on_board_packet(self, packet: ss.BoardPacket):
        ...

    async def on_candle_kind_packet(self, packet: ss.CandleKindPacket):
        ...

    async def on_client_account(self, packet: ss.ClientAccount):
        ...

    async def on_credit_ability(self, packet: ss.CreditAbility):
        ...

    async def on_client_order_packet(self, packet: ss.ClientOrderPacket):
        ...

    async def on_history_candle_packet(self, packet: ss.HistoryCandlePacket):
        ...

    async def on_history_tick_packet(self, packet: ss.HistoryTickPacket):
        ...

    async def on_market_packet(self, packet: ss.MarketPacket):
        ...

    async def on_position_packet(self, packet: ss.PositionPacket):
        ...

    async def on_quotation_packet(self, packet: ss.QuotationPacket):
        ...

    async def on_quote_packet(self, packet: ss.QuotePacket):
        ...

    async def on_security_packet(self, packet: ss.SecurityPacket):
        ...

    async def on_security_pit_packet(self, packet: ss.SecurityPitPacket):
        ...

    async def on_sec_info_update(self, packet: ss.SecInfoUpdate):
        ...

    async def on_server_status(self, packet: ss.ServerStatus):
        status = 'Connected' if packet.connected else 'Disconnected'
        print(f"SERVER STATUS CHANGED: {status}")
        self.connected = packet.connected

    async def on_text_message_packet(self, packet: ss.TextMessagePacket):
        ...

    async def on_trade_packet(self, packet: ss.TradePacket):
        ...

    async def on_unknown_packet(self, packet):
        """
        Функция обработки сообщений, не предусмотренных документацией.
        """
        print(packet)
