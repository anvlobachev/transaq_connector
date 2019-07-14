"""
Пример использования коннектора.
Смена пароля при первом подключении.
"""
import sys
import os
sys.path.append(os.path.join(sys.path[0], '../'))
from commands import uninitialize, initialize, connect, disconnect, change_pass
import time
import structures as ss

CONNECTED = False


def custom_callback(obj):
    """
    Устанавливаем флаг соединения в True. Ошибки соединения никак не обрабатываются
    """
    if isinstance(obj, ss.ServerStatus):
        print(f"SERVER STATUS CONNECTED: {obj.connected}")
        global CONNECTED
        CONNECTED = obj.connected


def wait_connect():
    """
    Вместо асинхронной реализации - просто ждем, когда произойдет коннект
    """
    for _ in range(1, 50):
        if CONNECTED:
            return True
        time.sleep(3)
    return False


def main():
    """
    Пример использования - смена пароля
    """
    try:
        # Инициализация библиотеки.
        initialize("Logs", 3, custom_callback)

        # Соединение с сервером. Логин и пароль хранятся в переменных окружения.
        login = os.environ['TRANSAQ_LOGIN']
        password = os.environ['TRANSAQ_PASS']
        connect(login, password, "tr1.finam.ru:3900")

        # Когда коннект произойдет - меняем пароль на новый.
        if wait_connect():
            print(change_pass(password, "NEW_PASSWORD"))

    finally:
        print(disconnect())
        uninitialize()


if __name__ == '__main__':
    main()
