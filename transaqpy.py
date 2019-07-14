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
        if isinstance(obj, ss.SecurityPacket):
            pass
        elif isinstance(obj, ss.SecurityPitPacket):
            pass
        elif isinstance(obj, ss.SecInfoUpdate):
            pass
        elif isinstance(obj, ss.BoardPacket):
            pass
        elif isinstance(obj, ss.MarketPacket):
            pass
        elif isinstance(obj, ss.CandleKindPacket):
            pass
        elif isinstance(obj, ss.ClientTradePacket):
            pass
        elif isinstance(obj, ss.ClientAccount):
            pass
        elif isinstance(obj, ss.CreditAbility):
            pass
        elif isinstance(obj, ss.ServerStatus):
            status = 'Connected' if obj.connected else 'Disconnected'
            print(
                f"SERVER STATUS CHANGED: {status}")
            self.connected = obj.connected
        else:
            print(obj)

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
