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

    def __init_dll_method_types__(self):
        """
        Init types accordig to documentation.
        methods:
        int GetServiceInfo(const BYTE* request, BYTE** response);
        BYTE* Initialize(const BYTE* logPath, int logLevel);
        BYTE* InitializeEx(const BYTE* data);
        BYTE* SetLogLevel(int logLevel)
        BYTE* SendCommand(BYTE* pData);
        bool SetCallback(tcallback pCallback);
        bool SetCallbackEx(tcallbackEx pCallbackEx, void* userData);
        bool FreeMemory(BYTE* pData);
        BYTE* UnInitialize();

        """
        self.txml_dll.GetServiceInfo.argtypes = [ctypes.c_char_p, ctypes.c_char_p]
        self.txml_dll.GetServiceInfo.restype = ctypes.c_int

        self.txml_dll.Initialize.argtypes = [ctypes.c_char_p, ctypes.c_int]
        self.txml_dll.Initialize.restype = ctypes.c_char_p

        self.txml_dll.InitializeEx.argtypes = [ctypes.c_char_p]
        self.txml_dll.InitializeEx.restype = ctypes.c_char_p

        self.txml_dll.SetLogLevel.argtypes = [ctypes.c_int]
        self.txml_dll.SetLogLevel.restype = ctypes.c_char_p

        self.txml_dll.SendCommand.argtypes = [ctypes.c_char_p]
        self.txml_dll.SendCommand.restype = ctypes.c_char_p      

        # self.txml_dll.SetCallback.argtypes = []
        # self.txml_dll.SetCallback.restype = ctypes.c_bool

        # self.txml_dll.SetCallbackEx.argtypes = []
        # self.txml_dll.SetCallbackEx.restype = ctypes.c_bool

        self.txml_dll.FreeMemory.argtypes = [ctypes.c_char_p]
        self.txml_dll.FreeMemory.restype = ctypes.c_bool

        self.txml_dll.UnInitialize.argtypes = []
        self.txml_dll.UnInitialize.restype = ctypes.c_char_p


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

        self.__init_dll_method_types__()

        if not os.path.exists(logdir):
            os.mkdir(logdir)

        init = et.Element('init')
        init.set('log_path', str(logdir))
        init.set('log_level', str(loglevel))
        init.set('logfile_lifetime', str(logfile_lifetime))

        msg = self.txml_dll.InitializeEx(et.tostring(init))
        if msg:
            raise c.TransaqException(s.Error.parse(msg).text)
        if not self.txml_dll.SetCallback(c.callback):
            raise c.TransaqException('Callback has not been established')


    def __del__(self):
        """
        Closes Callback connections. Perform disconnect if neccecary.
        :return:
        """
        self.disconnect()
        msg = self.txml_dll.UnInitialize()
        if msg != 0:
            raise c.TransaqException(s.Error.parse(msg).text)


    def __send_command(self, element):
        # Send the message and check for errors
        cmd = et.tostring(element, encoding="utf-8")
        msg = self.txml_dll.SendCommand(cmd)
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
        command = et.Element("command", {"id": "connect"})
        et.SubElement(command, "login").text = login
        et.SubElement(command, "password").text = password
        et.SubElement(command, "host").text = host
        et.SubElement(command, "port").text = port
        et.SubElement(command, "rqdelay").text = str(min_delay)
        return self.__send_command(command)


    def disconnect(self):
        """
        Disconnect from server.
        """
        command = et.Element("command", {"id": "disconnect"})
        return self.__send_command(command)
