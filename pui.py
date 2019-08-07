#!/usr/bin/env python
# -*- coding:utf-8 -*-

import bso
import functools
import operator
import threading
import queue
import tkinter as tk
from tkinter import ttk
import time
from tooltip import ToolTip
import dialog_ as dlg_
from util import config, write_config
from port import Rep, port_exc
from db_api import LookupDict
import alarm

vesible = bso.vesible
trace = bso.trace

bso.bso_ = False            # работает как ПУИ

req = bso.req
        
#########################################################


class App(bso.App):
    """Класс приложения"""

    def __init__(self, root, sizeX, sizeY, title):
        super().__init__(root, sizeX, sizeY, title)
        self.dict_depth = {'H': 3.2, 'B': 9.0, 'J': 7.5, 'E': 6.0,
                           'F': 4.7, 'M': 1.2, 'L': 1.1, 'C': 12.0, 'D': 15.0}      # 'L': 1
        self._vz = config.getfloat('System', 'vz')
        self._opgl = config.getfloat('System', 'opgl')

        # данные для передачи в ППУ
        # ($ 0x24 стартовый байт(start),work,rej,depth,b6,ku,sv1,sv2,sum1,sum2,0xA,0xD)
        # self.strdata = bytearray(b'$WSL05\x05\xdc94\r\n')
        recive_dict = dict(start='$', work='W', rej='S', depth='L',
            nused='0', ku='5', sv='\x05\xdc')
        look = LookupDict(recive_dict)
        self.send_data = look

        self.head.set_v(self.vz)        # vz - свойство скорость звука
        self.cvcreate = True            # для шума холст не создан
        self.delay = 1.0                # задержка для МГ и СГ 1с, БГ 3.2с B6 9с
        self.sboi = 0                   # число сбоев для ППУ Неисправен
        self.error = 0                  # занулить ошибки при старте проги
        self.flag_alarm = True
        self.off_volume = False         # звук выкл.
        self.oldsecs = 0
        self.count_g = 0
        self.gui_main()

    @staticmethod 
    def data_to_byte(kv):
        """Преобразуем словарь данных в данные для передачи в модуль с добавление ks"""
        data_str = ''.join(i for i in kv.__dict__.values())
        ks = functools.reduce(operator.xor, (ord(i) for i in data_str[1 : ]), 0)
        suml = chr(ks & 0x0F)
        sumh = chr((ks & 0xF0) >> 4)
        return data_str.encode('latin-1') + f"{sumh}{suml}".encode('latin-1') + b'\r\n' # + f"{sumh}{suml}".encode('latin-1')

    def gui_main(self):
        self.pser = Rep(trace)                          # объект Rep
        self.pser.tty.baudrate = 4800
        self.pser.tty.timeout = 0

        super().gui_main()

        ttk.Separator(self.frame_upr, orient="vertical").pack(side='right', fill='y', padx=4, pady=3)
        btn25 = ttk.Button(self.frame_upr, text='50кГц', image=self.img_['sinus'], cursor="hand2",
                           compound='left', width=7, command=self.b25)
        btn25.config(state='disabled')
        btn25.pack(side='right')
        btnavto = ttk.Button(self.frame_upr, text='Авто', image=self.img_['mashtabarrow'], cursor="hand2",
                             compound='left', width=7, command=self.btn_avto)
        btnavto.pack(side='right')
        self.b['btnavto'] = btnavto
        self.b['btn25'] = btn25

        s = ttk.Style()

        s.configure('TLabelframe.Label', foreground='black')
        self.infobar.diap_var.set('')
        self.frek_var.set('50кГц')
        self.infobar.rej_var.set('Авто')
        ttk.Separator(self.frame_upr, orient="vertical").pack(side='right', fill='y', padx=10, pady=3)
        self.cb = ttk.Combobox(self.frame_upr, values=('МГ', 'СГ', 'БГ'), width=7)        # radframe
        self.cb.pack(side='right')
        self.cb.set('')                      # in avto
        self.cb.focus()
        self.cb.state(['disabled','selected'])
        self.cb.bind('<FocusIn>', self.on_press_b)
        ToolTip(self.cb, msg='Выбор диапазона', delay_show=0.2, delay_hide=3.5)
        ttk. Label(self.frame_upr, text='Диапазоны   ').pack(side='right')
        ttk.Separator(self.frame_upr, orient="vertical").pack(side='right', fill='y', padx=10, pady=3)
        self.scl = tk.Scale(self.frame_upr, length=150, from_=1, to=15, showvalue=0,
            sliderlength=30, width=18, orient='horizontal', command=self.on_move)
        self.scl.set(9)
        self.porog_var.set('9')
        self.scl.pack(side='right', fill="x", expand=False)
        ttk. Label(self.frame_upr, text='Усиление   ').pack(side='right')
        ttk.Separator(self.frame_upr, orient="vertical").pack(side='right', fill='y', padx=10, pady=3)

        ttk.Separator(self.frame_upr, orient="vertical").pack(side='left', fill='y', padx=4, pady=3)
        bwait = ttk.Button(self.frame_upr, image=self.img_['nsignal'], text='Ожидание', compound="left",
                           cursor="hand2", width='16', command=self.go_nel)
        self.b['bwait'] = bwait
        bwait.pack(side='left')     #  ipady=2
        ttk.Separator(self.frame_upr, orient="vertical").pack(side='left', fill='y', padx=10, pady=3)
        btest = ttk.Button(self.frame_upr, image=self.img_['nastr_'], text='Тест', compound="left",
                           cursor="hand2", width='5', command=self.test_)
        bnoise = ttk.Button(self.frame_upr, image=self.img_['gaus2'], text='Шум', compound="left",
                            cursor="hand2", width='5', command=self.noise_)
        bversia = ttk.Button(self.frame_upr, image=self.img_['coment_'], text='Версия', compound="left",
                             cursor="hand2", width='8', command=self.ver_info)
        self.b['btest'] = btest
        self.b['bnoise'] = bnoise
        self.b['bversia'] = bversia
        btest.pack(side='left')
        bnoise.pack(side='left')
        bversia.pack(side='left')
        ttk.Separator(self.frame_upr, orient="vertical").pack(side='left', fill='y', padx=10, pady=3)
        
        if self.gser.is_open():
            self.que_gp = queue.Queue(1)
            thread_g = threading.Thread(target=self.getmsg_g, args=(self.que_gp,))
            thread_g.start()              # запуск потоковой функции нсп

        # self.set_local_time()                                                     ##
        # s.configure('H.TLabel', foreground='#2754aa')   # синий

        self.tick()

    def getmsg_g(self, que_gp):
        """Поточная функция чтения НСП"""
        while 1:                                 # self.tol_bar.flag_gals
            msg = self.gser.get_msg()       # str or None
            if msg:
                que_gp.put(msg)               # ждём пока очередь будет пуста

    def write_rep_thread(self):
        """Посылка в репитер"""
        if self.pser.is_open():
            self.thread_rep = threading.Thread(target=self.write_rep)
            self.thread_rep.start()

    def gps_thread(self):
        """Чтение НСП"""
        # s = ttk.Style()
        if self.gser.is_open():
            try:
                data_g = self.que_gp.get_nowait()
            except queue.Empty:
                # print('emptry')
                data_g = None
            if data_g:
                self.gps_data(data_g)
                self.count_g = 0
            else:
                self.count_g += 1
                if self.count_g >= 2:
                    self.count_g = 2
                    # s.configure('H.TLabel', foreground='#2754aa')   # синий
                    self.set_local_time()       # локальное время                   ##
                    self.d_gps = None
        else:
            # s.configure('H.TLabel', foreground='#2754aa')   # синий
            self.set_local_time()                                                   ##
        
    def tick(self):
        """Системный тик 100 млс."""
        if self.b['bwait'].cget('text') == 'Излучение':
            secs = time.time()
            if secs - self.oldsecs >= self.delay:    # delay = 1.2 сек
                self.oldsecs = secs
                self.gps_thread()                    # self.gps_data()
                self.write_rep_thread()              # write_rep()
                self.step_on()                       # work() self.head.set_t(t)
        else:
            self.oldsecs = 0
            self.board.clr_glub()                     # убрать '---' при изменении размера холста
        self.root.update()
        self.id = self.after(20, self.tick)

    def b25(self, *arg):
        """Обработчик кнопки 25 или 50 кГц"""
        if self.b['btn25'].cget('text') == '50кГц':
            self.send_data.start = '\x25'               # '%'  для 25 кГц
            self.send_data.work = '\xbb'                # '>>' 
            val = '25кГц' 
            self.b['btn25'].config(text='25кГц')
            # self.cb.config(values=('МГ', 'СГ', 'БГ', 'B6', 'B8', 'B10'))
            self.cb.config(values=('B6',))
        else:     
            self.send_data.start = '\x24'               # '$ '  для 50 кГц
            self.send_data.work = '\x57'                # 'W'
            val = '50кГц'
            self.b['btn25'].config(text='50кГц')
            self.cb.config(values=('МГ', 'СГ', 'БГ'))
        if self.b['btnavto'].cget('text') == 'Авто':
            self.cb.state(['disabled', 'selected'])
        self.frek_var.set(val)
        self.cb.current(0)
        self.on_press_b(event=None)

    def btn_avto(self, *arg):
        """Обработчик кнопки ручной/автомат режим"""
        if self.b['btnavto'].cget('text') == 'Авто':
            self.cb.state(['!disabled', '!selected'])
            try:
                self.cb.set(self.infobar.diap_var.get().split()[0])
            except IndexError: 
                self.cb.set('МГ')
                # self.infobar.diap_var.set('МГ')
            self.b['btnavto'].config(text='Ручной')
            self.send_data.rej = 'R'                      # '\x52'
            self.b['btn25'].state(['!disabled', '!selected'])
            self.infobar.rej_var.set('Ручной')
        else:
            self.cb.state(['disabled', 'selected'])
            self.cb.set('')                               #
            self.b['btnavto'].config(text='Авто')
            self.send_data.rej = 'S'                      # '\x53'
            self.b['btn25'].state(['disabled', 'selected'])
            self.infobar.rej_var.set('Авто')

    def on_press_func(self, arg):
        """dict_depth = {'H':3.2,'B':9.0,'M':1.0,'L':1.0,'C':12.0,'D':15.0}"""
        if arg in self.dict_depth:
            self.send_data.depth = arg
            self.delay = self.dict_depth[arg]

    def on_press_b(self, event):
        """Обработчик переключателей установки глубины  В6 В8 В10  БГ СГ МГ""" 
        val = self.cb.get()
        dic = {'МГ': 'L', 'СГ': 'M', 'БГ': 'H', 'B6': 'B', 'B8': 'C', 'B10': 'D'}
        if val in dic:
            self.on_press_func(dic[val])

    def on_move(self, value):
        """Обработчик шкалы усиления value = str('1.0'-'15.0') (value='5.67')"""
        if self.send_data.ku:
            self.send_data.ku = format(round(float(value)), 'X')    # '0', '1'...'F'
            self.porog_var.set(value.split('.')[0])               #          

    def go_nel(self, *arg):
        """Обработчик кнопки излучение/ожидание"""
        if not self.cvcreate:                           # если есть окно шума и т.д. то убрать
            self.windestroy()
        if self.ser.is_open():
            self.b['bwait'].state(['!disabled', '!selected'])
            if self.b['bwait'].cget('text') == 'Ожидание':
                self.b['bwait'].config(text='Излучение', image=self.img_['signal'])
                # self.veiwstate = 'disabled'
                enabl = ('bmman', 'btnmetka') if self.tbname and not self.hide_metka else ()
                self.ch_state(('bgals',), ('btnmetki',))
                self.ch_state(('btest', 'bnoise', 'bversia'), enabl)
                # self.new_avtom__(self.odl_arg_time)                  # ! start avtometka
                self.stbar.set_icon(self.img_['networkon'])
                self.root.update()
            else:
                self.b['bwait'].config(text='Ожидание', image=self.img_['nsignal'])
                self.ch_state(('bmman', 'btnmetki', 'btnmetka'), ('btest', 'bnoise', 'bversia', 'bgals'))
                self.new_avtom__(0)                                  # stop avtometka
                # self.veiwstate = 'normal'
                self.board.clr_error()                               # очистка лишнего
                self.board.clr_glub()                                #
                self.glub_var.set('')                                #
                self.stop_var.set('')                                #
                self.ampl_var.set('')
                self.infobar.diap_var.set('')
                self.porog_var.set('')
                # self.scl_amp.set(0)
                # self.vmeter(0)
                self.root.update()
        else:
            self.b['bwait'].state(['disabled', 'selected'])

    def control_(self, strdata, arg=None):
        """"""
        self.board.clr_error()
        if arg is None:
            t = 1.65;  z = 1                        # 0.9 ? надо подбирать т.к.
        else:                                       # в последних ХК не жду '#'
            t = 0.25; z = 402
        data = None
        if self.ser.is_open():
            self.ser.clear_port()
            self.ser.write(strdata)
            time.sleep(0.05)
            iW = self.ser.in_waiting()
            trace(iW)
            if iW == 1:
                xk_end = self.ser.read_()            # принемаем из ХК !(0x21) или ?(0x3F)
                trace(f'xk_end = {xk_end}')
                if xk_end == b'!':                   # если приняли ! (контр сумма совпала)
                    self.ser.clear_port()            # очистка порта
                    time.sleep(t)
                    #    self.ser.clear_port()       # очистка порта
                    if arg:
                        self.ser.write(b'#')         # запрос данных из ПУИ
                    time.sleep(0.1)
                    ans = self.ser.read_()
                    trace(f'ans = {ans}')
                    if ans == b'$':
                        trace('$$')
                        time.sleep(0.3)
                        data = self.ser.read_(z)
            else:
                self.ser.write(b'#')                  # чтобы не вис ХК посылаем (#)
                time.sleep(0.2)                       # пауза на прием данных
                self.board.create_error()             # Надпись Нет связи с ППУ на холст
        return data

    def ver_info(self, *arg):
        """Вывести версию проги при нажатии <Alt-v>"""
        # s = b'%VRL05\x05\xdc94\r\n' if self.kgz_25 else b'$VRL05\x05\xdc94\r\n'
        work = self.send_data.work
        self.send_data.work = 'V' 
        s = self.data_to_byte(self.send_data)
        self.send_data.work = work
        self.board.clr_error()
        if self.ser.is_open():
            self.ser.clear_port()
            self.ser.write(s)
            time.sleep(0.15)
            trace('>')
            if self.ser.in_waiting():
                xk_end = self.ser.read_()
                if xk_end == b'!':
                    time.sleep(0.2)
                    data = self.ser.read_(60)                    # строка с номером версии
                    data = data.decode('latin-1')                  # 'cp1251'
                    if data:
                        trace(f"--> {data}")                     # сливаем сообщение в консоль
                        text = f" {data}"
                        self.view_noise(title='Версия', data=None, text=text)
                    else:
                        trace("--> Old module version not defined!")
                else:
                    time.sleep(0.2)
                    self.board.create_error()
            else:
                time.sleep(0.2)
                self.board.create_error()

    def test_(self, *arg):
        """Обработчик кнопки тест"""
        # strdata = b'%\xb8RL05\x05\xdc7a\r\n' if self.kgz_25 else b'$TRL05\x05\xdc96\r\n'
        work = self.send_data.work
        self.send_data.work = 'T' if self.send_data.start == '\x24' else chr(0xb8)
        s = self.data_to_byte(self.send_data)
        self.send_data.work = work
        data = self.control_(s)
        if data != None:
            text = 'Эхолот исправен' if data == b'\x00' else 'Эхолот не исправен' 
            self.view_noise(title='Тест',data=None, text=text)

    def noise_(self, *arg):
        """Обработчик кнопки шум"""
    #    strdata = b'%\xb2RL05\x05\xdc70\r\n' if self.kgz_25 else b'$NRL05\x05\xdc8c\r\n'
        work = self.send_data.work
        self.send_data.work = 'N' if self.send_data.start == '\x24' else chr(0xb2)
        s = self.data_to_byte(self.send_data)
        self.send_data.work = work
        data = self.control_(s, 1)
        if data:
            if len(data) == 402:
                self.view_noise(title='Шум тракта', data=data,  text=None)

    def windestroy(self):
        """Закрытие окна"""
        self.cvcreate = True
        self.av_ = 0        # при закрытии окна убрать автомат для шума
        self.win.destroy()

    def view_noise(self, title, data, text):
        """Показать окно с шумами"""
        if self.cvcreate:
            self.cvcreate = False
            self.win = tk.Toplevel(self.root)
            self.win.title(title)
            self.win.protocol('WM_DELETE_WINDOW', self.windestroy)
            self.win.transient(self.root)                       # нет окна в трее
            self.win.focus()
            self.win.geometry('412x332+154+160')                # смещение от верха экрана
            f = ttk.Frame(self.win, borderwidth=4, relief='groove')
            f.pack(fill='both', expand="yes")
            self.cv = tk.Canvas(f, width=400, height=320, bg='white')
            self.cv.pack(fill='both', expand="yes")
        else:
            self.cv.delete('nois')
        if data:
            data = list(data)                                               # [int, int, ...]
            dat = [data[_] * 256 + data[_+1] for _ in range(0, len(data), 2)]
            for i in range(200):
                Y = 320 - int(round(dat[i] / 8))
                self.cv.create_line(i * 2, 320, i * 2, Y, width=2, fill='gray25', tag='nois')
            c = 320-int(round(dat[-1] / 8))                                   # среднее
            if c < 0:
                c = 0
            self.cv.create_line(0, c, 400, c, fill='red', tag='nois')
            l = ttk.Label(self.cv, text=f'{dat[-1]:04d}', width=5,
                      background='yellow', foreground='blue')
            l.pack()
            y = c - 11 if c > 100 else c + 11
            self.cv.create_window(360, y, window=l, tag='nois')
        if text:
            if title == 'Тест':
                self.cv.create_text(200, 250, text=text,
                                    font=("Times", 20, "bold"), fill='red', tag='nois')
            elif title == 'Версия':
                self.cv.create_text(210, 150, text=text,
                                    font=("Times", 14), fill='green', tag='nois')
        if config.getboolean('Amplituda', 'av'):                  # 1 - автошум 
            self.root.update()
            self.win.update_idletasks()
            if not self.cvcreate:   # иначе после перехода в ожидание появиться окно шума
                self.noise_()                 
        
    def open_port(self):
        """Открытие портов"""
        super().open_port()
        port_rep = config.get('Port', 'port_rep')
        baudrate_rep = config.getint('Port', 'baudrate_rep')
        try:
            self.pser.open_port(port_rep)
            self.pser.tty.baudrate = baudrate_rep
        except port_exc:
            self.stbar.set_rep(f'Не открыть порт {port_rep}')          
            self.stbar.set_icon_rep(self.img_['networky'])
        if self.pser.is_open():
            self.stbar.set_rep(self.pser.get_port_info('РЕПИТЕР'))
            self.stbar.set_icon_rep(self.img_['networkon'])

    def new_spid__(self, arg=None):
        if arg is not None:
            self.vz = arg

    def new_opgl__(self, arg=None):
        if arg is not None:
            self.opgl = arg             

    @property
    def vz(self):
        """"Скорость звука"""
        return self._vz

    @vz.setter
    def vz(self, value):
        """Изменение скорости звука"""
        self._vz = value                      # int
        self.head.set_v(value)
        config.set('System', 'vz', f'{value}') 
        write_config() 

    @property
    def opgl(self):
        """Опасная глубина"""
        return self._opgl

    @opgl.setter
    def opgl(self, value):
        self._opgl = value
        self.board.show_opgl()                           # вывести на холст оп. глуб.
        config.set('System', 'opgl', f'{value}') 
        write_config()

    def spid_(self):
        """Обработка кнопки скорость звука"""
        ini = config.getint('System', 'vz')
        dlg_.get_int(self.root, 'Скорость звука', 'Введите скорость звука', self.new_spid__,
                     initial=ini, minimum=1350, maximum=1600)

    def opgl_(self):
        """Обработка кнопки опасной глубины"""
        ini = config.getfloat('System', 'opgl')
        dlg_.get_float(self.root, 'Опасная глубина', 'Введите опасную глубину', self.new_opgl__,
                       initial=ini, minimum=0, maximum=14)

    def off_vol(self, *arg):
        """Отключить включить звук"""
        if not self.off_volume:
            image=self.img_['kmix']
            ToolTip(self.b['btnvolume'], msg='Звук включен')
        else:
            image=self.img_['kmixmute']
            ToolTip(self.b['btnvolume'], msg='Звук выключен')
        self.b['btnvolume'].configure(image=image)
        self.off_volume = not self.off_volume

######################## Work ############################

    def blink_r(self):
        """Мигнуть телевизорами порта Rep"""
        self.stbar.lab_tel_rep.config(image=self.img_['network1'])
        self.root.after(200, lambda: self.stbar.lab_tel_rep.config(image=self.img_['network3']))

    def write_rep(self):                            # учесть заглубление self.zg
        """Посылка в репитер глубины и опасной глубины"""
        # if self.pser.is_open():
        if self.zg > 0:
            gl_0 = self.gl_0 - self.zg
        else:
            gl_0 = self.gl_0
        self.pser.write_msg(gl_0, self.opgl)
        self.blink_r()

    def check_opgl(self):
        """Аларм если превышена опасная глубина"""
        if not self.data_point:
            return
        x = self.data_point[0]
        if x:
            if self.opgl > x:
                if self.off_volume:
                    if self.flag_alarm:
                        self.p = alarm.AlarmProcess()
                        self.p.daemon = True
                        self.p.start()
                        self.flag_alarm = False
                else:
                    if not self.flag_alarm:
                        if self.p.is_alive():
                            self.p.terminate()
                            self.flag_alarm = True
            else:
                if not self.flag_alarm:
                    if self.p.is_alive():
                        self.p.terminate()
                        self.flag_alarm = True

    def work_(self, data):
        """data = bytes"""
        self.parse_data(data)
        super().work(data)
        self.board.clr_error()                 # убераем надпись Нет связи с ППУ с холста
        self.stbar.set_step(f'T = {self.delay} cек.')          # интервал опроса в статус
        # self.stbar.set_err(f'{self.error}')                    # и ошибки 

    def read_hach(self):
        """Приём ! or ? от ХК"""
        xk_end = self.ser.read_()            # принемаем из ХК !(0x21) или ?(0x3F)
        if xk_end == b'!':                   # если приняли ! (контр сумма совпала)
            trace(f'{xk_end}')
            self.ser.clear_port()            # очистка порта
            self.ser.write(b'#')             # запрос данных из ПУИ 
            self.after(120, self.read_data)
        else:
            self.error += 1
            self.sboi += 1
            trace(f'=! >{xk_end}')
            # self.jamp()
            self.ser.write(b'#')                  # чтобы не вис ХК

    def read_data(self):
        """Приём из ХК 91 bytes"""
        data = self.ser.read()              # приём данных из ХК может(None) 91 bytes   5 !!read_n()
        if data:                            # это start изл.
            self.work_(data)
            self.root.update()
            self.write_data(data)           # если надо то пишем в файл
            self.blink()                    # мигнуть телевизорами
            self.root.update()              # update_idletasks()
            self.sboi = 0

    def step_on(self):
        """Цикл работы с компортом"""
        if not self.ser.is_open():          # нет открытого порта
            self.go_nel()                   # обратно в ожидание
            return
        self.ser.clear_port()               # очистка порта                       1
        dat = self.data_to_byte(self.send_data)
        thread_ds = threading.Thread(target=self.ser.write, args=(dat,))
        thread_ds.start() 
        # self.ser.write(dat)                 # передаём в ХК info    12 bytes TODO:
        if self.sboi > 1:
            self.stbar.set_icon(self.img_['networky'])
            self.board.create_error(text='Нет связи с ППУ!')     # Надпись Нет связи с ППУ на холст
        self.after(1, self.read_hach)     

    def parse_data(self, data):
        super().parse_data(data)
        if self.b['btnavto'].cget('text') == 'Авто':
            self.send_data.ku = chr(data[1])
            self.send_data.depth = chr(data[0])
            self.scl.set(int(self.send_data.ku, 16))
            self.timing(data[0])

    def timing(self, arg):
        """Интервал запуска"""
        strd = chr(arg)
        if strd in self.dict_depth:
            self.delay = self.dict_depth[strd]
