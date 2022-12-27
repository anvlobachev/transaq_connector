"""
Пример использования коннектора - получение последних 10 столбцов
"""

import sys
import os
import time
from tabulate import tabulate

sys.path.append(os.path.join(sys.path[0], '../'))
import structures as ss
import commands as cmd


def custom_callback(obj):
    # в этом примере не обрабатываем большинство сообщений,
    # выдаваемых при инициализации
    if isinstance(obj, ss.SecurityPacket):
        print(f"SecurityPacket", [security.seccode for security in obj.items])
        pass
    elif isinstance(obj, ss.SecurityPitPacket):
        print(f"SecurityPitPacket", [pit.seccode for pit in obj.items])
        pass
    elif isinstance(obj, ss.SecInfoUpdate):
        print(f"SecInfoUpdate({obj.market}, {obj.seccode})")
        pass
    elif isinstance(obj, ss.BoardPacket):
        print("BoardPacket", [board.name for board in obj.items])
        pass
    elif isinstance(obj, ss.MarketPacket):
        print(f"MarketPacket({obj.items})")
        pass
    elif isinstance(obj, ss.CandleKindPacket):
        print("CandleKindPacket", [kind.name for kind in obj.items])
        pass
    elif isinstance(obj, ss.ClientTradePacket):
        print("ClientTradePacket", [trade.seccode for trade in obj.items])
        pass
    elif isinstance(obj, ss.ClientAccount):
        print(f"ClientAccount({obj.type}, {obj.currency}, {obj.market}")
        pass
    elif isinstance(obj, ss.CreditAbility):
        print(f"CreditAbility({obj.overnight}, {obj.intraday})")
        pass
    elif isinstance(obj, ss.ServerStatus):
        print(f"SERVER STATUS CONNECTED: {obj.connected}")
    elif isinstance(obj, ss.HistoryCandlePacket):
        print(list(i for i in obj.items))
        print(f"board: {obj.board}, seccode: {obj.seccode},\
                period: {obj.period}")
        ticks = []
        for i in obj.items:
            ticks.append([i.date, i.open, i.high, i.low, i.close, i.volume])
        print(tabulate(ticks,
                       headers=['date', 'open', 'high', 'low', 'close', 'volume']))
    else:
        # а все остальное на всякий случай печатаем
        print(f"CALLBACK {type(obj)}>\n{obj.__dict__}")


if __name__ == '__main__':
    try:
        cmd.initialize("Logs", 3, custom_callback)
        login = os.environ['TRANSAQ_LOGIN']
        password = os.environ['TRANSAQ_PASS']
        cmd.connect(login, password, "tr1.finam.ru:3900")
        # Тут должна быть асинхронная логика,
        # но для примера просто ждем ответ сервера
        # Если не успевает произойти соединение - увеличьте время
        time.sleep(30)
        cmd.get_history('TQBR', 'GAZP', 2, count=10)
        # Тут должна быть асинхронная логика,
        # но для примера просто ждем ответ сервера
        time.sleep(10)
    except Exception as exc:
        print(f"EXCEPTION:{exc}")
    finally:
        print(cmd.disconnect())
        cmd.uninitialize()
