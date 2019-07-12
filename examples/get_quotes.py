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


def handle_txml_message(msg):
    print(msg)
    pass


if __name__ == '__main__':
    try:
        cmd.initialize("Logs", 3, handle_txml_message)
        login = os.environ['TRANSAQ_LOGIN']
        password = os.environ['TRANSAQ_PASS']
        con = cmd.connect(login, password, "tr1.finam.ru:3900")
        print(con)
        print(cmd.get_history('TQBR', 'GAZP', 2, count=10))
        time.sleep(3)
    finally:
        pass
        # print(disconnect())
        # uninitialize()
