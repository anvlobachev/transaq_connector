"""
Пример использования коннектора - получение последних 10 столбцов
"""
import sys
import os
import time
from tabulate import tabulate

sys.path.append(os.path.join(sys.path[0], '../'))
import commands as cmd
import structures as ss

def custom_callback(obj):
    # в этом примере не обрабатываем большинство сообщений, выдаваемых при инициализации
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
        print(f"SERVER STATUS CONNECTED: {obj.connected}")
    elif isinstance(obj, ss.HistoryCandlePacket):
        print(f"board: {obj.board}, seccode: {obj.seccode}, period: {obj.period}")
        ticks = []
        for i in obj.items:
            ticks.append([i.date, i.open, i.high, i.low, i.close])
        print(tabulate(ticks, headers=['date', 'open', 'high', 'low', 'close']))
    else:
        # а все остальное на всякий случай печатаем
        print(f"CALLBACK {type(obj)}>\n{obj}")


if __name__ == '__main__':
    try:
        cmd.initialize("Logs", 3, custom_callback)
        login = os.environ['TRANSAQ_LOGIN']
        password = os.environ['TRANSAQ_PASS']
        cmd.connect(login, password, "tr1.finam.ru:3900")
        # Тут должна быть асинхронная логика, но для примера просто ждем ответ сервера
        # Если не успевает произойти соединение - увеличьте время
        time.sleep(20)
        cmd.get_history('TQBR', 'GAZP', 2, count=10)
        # Тут должна быть асинхронная логика, но для примера просто ждем ответ сервера
        time.sleep(10)
    except Exception as exc:
        print(f"EXCEPTION:{exc}")
    finally:
        print(cmd.disconnect())
        cmd.uninitialize()
