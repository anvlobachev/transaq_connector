"""
Wrapper over Trasaq C# dll
"""
import os
import sys
import ctypes

import commands as c
import lxml.etree as et
import structures as s

SYS_ENCODING = sys.stdout.encoding


class TransaqConnection():
    """
    Transaq connection entity
    """

    def __init__(self, logdir, loglevel=2, logfile_lifetime=7):
        """
        :param logdir: log directory. ends with \\
        :param loglevel: level of logs from 1(minimum) to 3(maximum) 2 is default.
        :logfile_lifetime: days how long log files lives.
        """
        self.logdir = logdir
        self.loglevel = loglevel
        self.connected = False
        self.txml_dll = ctypes.WinDLL(os.path.join(
            os.path.dirname(__file__), "txmlconnector64.dll"))

        err = 0
        if not os.path.exists(logdir):
            os.mkdir(logdir)

        init = et.Element('init')
        init.set('log_path', str(logdir))
        init.set('log_level', str(loglevel))
        init.set('logfile_lifetime', str(logfile_lifetime))

        err = self.txml_dll.InitializeEx(et.tostring(init))
        if err != 0:
            msg = self.__get_message(err)
            raise c.TransaqException(s.Error.parse(msg).text)
        if not self.txml_dll.SetCallback(c.callback):
            raise c.TransaqException('Callback has not been established')


    def __del__(self):
        """
        Closes Callback connections. Perform disconnect if neccecary.
        :return:
        """
        self.disconnect()
        err = self.txml_dll.UnInitialize()
        if err != 0:
            msg = self.__get_message(err)
            raise c.TransaqException(s.Error.parse(msg).text)


    def __get_message(self, ptr):
        """
        Get message from native memory. Free memory from ptr.
        """
        msg = ctypes.string_at(ptr)
        self.txml_dll.FreeMemory(ptr)
        return msg


    def __send_command(self, element):
        # Send the message and check for errors
        cmd = et.tostring(element, encoding="utf-8")
        ptr = self.txml_dll.SendCommand(cmd)
        msg = self.__get_message(ptr)
        err = s.Error.parse(msg)
        if err.text:
            raise c.TransaqException(err.text.encode(SYS_ENCODING))
        else:
            return c.CmdResult.parse(msg)

    def connect(self, login, password, server, min_delay=100):
        """
        Connect to server.
        """
        host, port = server.split(':')
        root = et.Element("command", {"id": "connect"})
        et.SubElement(root, "login").text = login
        et.SubElement(root, "password").text = password
        et.SubElement(root, "host").text = host
        et.SubElement(root, "port").text = port
        et.SubElement(root, "rqdelay").text = str(min_delay)
        return self.__send_command(root)


    def disconnect(self):
        """
        Disconnect from server.
        """
        root = et.Element("command", {"id": "disconnect"})
        return self.__send_command(root)
