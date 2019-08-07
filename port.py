#!/usr/bin/env python
# -*- coding:utf-8 -*-

#import os.path, sys
import serial
import traceback
import time
import functools
# import configparser
# import tkinter.messagebox as box
#from util import bundle_dir

# config = configparser.ConfigParser()
# file = os.path.join('.', 'config.ini')
# #file = os.path.join(bundle_dir, 'config.ini')

# if not os.path.exists(file):
    # box.showerror('Error!', 'Отсутствует или поврежден файл config.ini')
    # sys.exit(0)

# config.read(file)

port_exc = serial.SerialException

# vesible = config.getboolean('Verbose', 'vesible')
# trace = print if vesible else lambda *x: None

class RS232:
    """Класс COM порта"""      
    def __init__(self, trace):
        self.tty = serial.Serial(timeout=0.2)   # 0.2
        self.trace = trace

    def scan(self):
        """ Сканируем порты и возврвщаем доступные в виде ['COM1', ...] """
        from serial.tools import list_ports
        available = []
        for _ in list_ports.comports():
            available.append(_[0])
        if available:
            return available

    def open_port(self, port):
        """Открывает выбранный порт ( port = int или str )"""
        self.tty.port = port
        self.tty.open()
        self.tty.reset_input_buffer()

    def is_open(self):
        """Tue если порт открыт и False если нет"""
        return self.tty.is_open

    def in_waiting(self):
        """Колличество байт в буфере приема"""
        return self.tty.in_waiting

    def close_port(self):
        """Закрываем порт"""
        self.tty.close()

    def get_port_info(self, name='ПУИ'):
        """Вернуть название порта и скорость передачи"""
        p = self.tty.port
        b = self.tty.baudrate
#        t = self.tty.timeout 
        return f"Порт {name} :: {p},  {b}"

    def clear_port(self):
        """Очистка порта"""
        self.tty.reset_input_buffer()

    def read_(self, n=1):
        """Прием из ХК 0х21{!} если если данные получены нормально
           или 0х3А{?} если не совпала КС
           Возможно ответа не будет если ХК не получил данные полностью
           тип возврата bytes"""
        time.sleep(0.05)
        return self.tty.read(n)     # type bytes

    def read(self):
        """Чтение данных из линии 91 байт ответа ХК"""
        if not self.tty.in_waiting:
            self.trace('inW = 0')
            return
        data = self.tty.readall()
        if len(data) != 91:
            self.trace(f'{len(data)} != 91')
            return
        if data[0:1] != b'$':
            self.trace('!= $')
            return
        return data[1:89]
        
    def read_all(self):
        """Чтение данных из линии 12bytes + !or? +# + 91bytes = 105"""
        if not self.tty.in_waiting:     # new!
            return
        data = self.tty.readall()
        #data = self.tty.read(105)
        #self.tty.reset_input_buffer()
        self.trace('>> ', len(data))
        if len(data) != 105:
            self.trace('!= 105')
            return
        if (data.startswith(b'$') and data.endswith(b'\r\n')) or (data.startswith(b'%') and data.endswith(b'\r\n')):
            # print(data)
            # return data[15 : -2]      # data
            return data                 # data
        self.trace('<>')
   
    def write(self, data):
        """Запись в порт bytearray """
        return self.tty.write(data)
        
class Gps(RS232):
    """Класс COM порта для GPS
    '$GPRMC,123519.xxx,A,4807.038x,N,01131.000x,E,x22.4,084.4,230394,003.1,W*6A\n'
    """      
    def __init__(self, trace):
        super().__init__(trace)
        self.trace = trace

    def get_msg(self):
        """Чтение порта GPS возвращает строку или None"""
        if not self.tty.in_waiting:
            return
        msg = self.tty.readall()
#        msgd = msg.decode('latin-1')
#        self.trace(f'>> {msgd}')
#        print(f'>> {msgd}')
        i1 = msg.rfind(b'*')
        if i1 != -1:
            msg = msg[ : i1]
            i2 = msg.rfind(b'RMC')      # !!! '$GNR'
            if i2 != -1:
                try:
                    msg_ = msg[i2 : ].decode('latin-1')
                    #print(msg_)
                except:
                    msg_ = None
                    traceback.print_exc(file=open('err.log', 'a'))
                    #print('Except...')
                return msg_
                

class Rep(RS232):
    """Класс COM порта для репитера"""      
    def __init__(self, trace):
        super().__init__(trace)
        self.trace = trace
    
    # def kssumm(self, ks):
    #     """Возврат к.с.(искл. или) два символа type bytes"""
    #     s = functools.reduce(lambda x1,x2:x1^x2, ks)
    #     x = divmod(s, 256)
    #     if x[0] > 255:
    #         x1 = divmod(x[0], 256)
    #         k = (x1[1], x[1])
    #     else:
    #         k = (x[0], x[1])
    #     return bytes(k)

    def ksum(self, msg):
        """Возврат к.с.(искл. или) два символа type bytes"""
        # msg = ms[1 : -4]
        s = functools.reduce(lambda x1, x2: x1 ^ x2, msg)
        sh = (s & 0xf0) >> 4
        sl = s & 0x0f
        if sh < 10:
            sh += 48
        else:
            sh += 55
        if sl < 10:
            sl += 48
        else:
            sl += 55
        # return b'$' + msg + chr(sh).encode('latin-1') + chr(sl).encode('latin-1') + b'\r\n'
        return bytes((sh, sl))

    def create_msg(self, gl, go):
        """Синтез сообщения
        '$SDDBT,,,xxxx.x,M,xx,M,A,*hh\r\n'
        gl = глубина в метрах, g_op = опасная глубина в метрах (0-99m) float
        """
        g0 = round(go)          # type int
        g = f'{gl:0=6}'.encode()
        g_op = f'{g0:0=2}'.encode()
        head = b'$SDDBT,,,'
        midle = b',M,A,'
        end_1 = b'*'
        ksl = head[1 : ] + g + b',M,' + g_op + midle
        # ks = self.kssumm(ksl)           # контрольная сумма
        ks = self.ksum(ksl)               # контрольная сумма
        end = b'\r\n'
        msg = head + g + b',M,' + g_op + midle + end_1 + ks + end
        return msg

    def write_msg(self, gl, go):
        """Записьсообщения в порт"""
        msg = self.create_msg(gl, go)
        if self.tty and msg:
            self.tty.write(msg)
