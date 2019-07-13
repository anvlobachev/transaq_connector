# -*- coding: utf-8 -*-
"""
Пример использования коннектора.
"""
import sys
import os
import time
#import ctypes

sys.path.append(os.path.join(sys.path[0], '../'))
import commands as cmd
import structures as ss

def custom_callback(obj):
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
        pass
    else:
        print(f"CALLBACK {type(obj)}>\n{obj}")


if __name__ == '__main__':
    try:
        cmd.initialize("Logs", 3, custom_callback)
        login = os.environ['TRANSAQ_LOGIN']
        password = os.environ['TRANSAQ_PASS']
        cmd.connect(login, password, "tr1.finam.ru:3900")        
        history = cmd.get_history('TQBR', 'GAZP', 2, count=10)
        time.sleep(3)
    except Exception as exc:
        print(f"EXCEPTION:{exc}")
    finally:
        print(cmd.disconnect())
        cmd.uninitialize()

    input('Press Enter')
