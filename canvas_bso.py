#!/usr/bin/env python
# -*- coding:utf-8 -*-

import math
import tkinter as tk
from tkinter import ttk
from collections import deque

COLOR = ('#c40373', '#e32322', '#ea621f', '#f18e1c', '#fdc60b', '#f4e500',
         '#8cbb26', '#008e5b', '#0696bb', '#2a71b0', '#444e99', '#552f6f')
         
COLORMAX = 0xFF     # 0x600            # 65535  # TODO:

w = 12
color = 'blue'

#  система координат x0, y0 верхний левый  угол x1, y1 правый нижний угол

class CanvasT(ttk.Frame):
    """Поляна"""

    def __init__(self, root, sizeX, sizeY, bso_=False):
        super().__init__(root)
        self.root = root
        self.sizeX = sizeX
        self.sizeY = sizeY
        self.fil = 'orange3'
        self.hide_ = False
        self.bso_ = bso_
        self.y_top = 25
        # self.create_fild()

        colorbar = ttk.Frame(self, relief=tk.GROOVE, border=1)
        self.sclrbar = ttk.Frame(self, border=0)
        for i in COLOR:
            ttk.Label(colorbar, background=i, width=1).pack(fill=tk.Y, expand=True)
        colorbar.pack(side=tk.RIGHT, fill=tk.Y, expand=False)
        
        # self.scl_amp = tk.Canvas(self.sclrbar, width=w, bg="black",
        #                          height=300, bd=0, highlightthickness=0, relief=tk.RIDGE)
        # self.scl_amp.pack(side=tk.RIGHT, fill=tk.Y, expand=False, padx=0)
        
        canv = tk.Canvas(self, background='#383838', relief=tk.SUNKEN)
        canv.config(width=self.sizeX, height=self.sizeY)
        canv.config(highlightthickness=0)
        sbar = ttk.Scrollbar(self)
        sbar.config(command=self.myyview)     # canv.yview
        canv.config(yscrollcommand=sbar.set)
#        sbar.pack(side='left', fill='y')       # пакуем в bso
        self.sbar = sbar
#        canv.pack(side='left', fill='both', expand='yes') # пакуем в bso
        self.canv = canv
        self.colorbar = colorbar
        # self.skale = (1.0, 2.0, 5.0, 10.0, 20.0, 40.0, 50.0, 100.0, 200.0, 300.0, 400.0)
        self.skale = (1.0, 2.0, 5.0, 10.0, 20.0, 40.0, 50.0, 100.0, 200.0, 300.0, 400.0, 500.0, 600.0)
        self.scrol_ = 200000    # 125000
        self.n_ = 11            # 9
        if bso_:
            self.skale = (1.0, 2.0, 5.0, 10.0, 20.0, 40.0, 50.0, 100.0, 200.0, 300.0, 400.0)
            self.scrol_ = 125000
            self.n_ = 9
        self.k = 1.0
        self.i = 0
        self.value_ = ['']                        # список присутствующик портов
        self.oldglub = False
        self.error_pui = True
        # self.root.bind("<Configure>", self.conf)  # при изменении размеров окна
        
    # def vmeter(self, data):
        # """Рисование уровня амплитуды"""
        # high = self.scl_amp.winfo_height()
        # value = high / COLORMAX
        # mvalue = value * data
# #        print(high, data, mvalue)
# #        mvalue = data
        # self.scl_amp.delete('sc_amp')
        # self.scl_amp.create_rectangle(0, 0, w, high, fill='#888', outline='#888', tag='sc_amp')
        # self.scl_amp.create_rectangle(w-2, high-2, 1, high-int(mvalue), 
            # fill='#666', outline='red', tag='sc_amp')
            
    # def conf(self, arg=None):
        # self.vmeter(0)
        
    def myyview(self, *arg):                         # e1=None, e2=None, e3=None, e4=None
        """Подмена yview, что бы надпись глубины оставалась на месте"""
        old_y = self.canv.canvasy(self.sizeY - 30)
        self.canv.yview(*arg)                        # e1, e2, e3, e4
        self.canv.move('glub', 0, self.canv.canvasy(self.sizeY - 30) - old_y)

    def create_error(self, text='Нет данных!'):
        """Выводим на канвас сообщение 'Нет связи с ППУ'"""
        font = ('Helvetica', 26)
        self.canv.delete('error')
        self.canv.delete('glub')
        self.error_pui = True
        self.canv.create_text(self.sizeX / 2, self.canv.canvasy(self.sizeY - 50), text=text,
                              font=font, anchor=tk.CENTER, fill='red', tag='error')

    def clr_error(self):
        """Убираем надпись 'Нет связи с ППУ' с холста"""
        self.canv.delete('error')
        self.error_pui = False

    def view_glub(self, glub_, opgl):
        """Отобразить глубину на холсте"""
        if self.bso_ and (not self.root.tol_bar.flag_gals or self.error_pui):   # !!
            return
        if glub_ <= 0:                        # if not glub:
            text = '-' * 5        # '-'*6
        # elif glub < 1000:
        #     text = f'{glub:5.1f} м'
        else:
            text = f'{glub_:5.1f} м'
        fill = 'orange2' if glub_ >= opgl else 'red'   # 'sienna3', 'tan1', orange2
        font = ('Arial', 42)                           # , 'bold'
        self.canv.delete('glub')
        self.canv.create_text(130, self.canv.canvasy(self.sizeY - 40), text=text,
                              font=font, anchor=tk.CENTER, fill=fill, tag='glub')
        self.oldglub = glub_

    def clr_glub(self):
        """Убираем показания глубины с холста"""
        self.canv.delete('glub')
        
    def create_list_deque(self, maxlen):
        """Создаём списки буфера для хранения экрана"""
        self.data_amplit = deque(maxlen=maxlen)
        self.data_lenth = deque(maxlen=maxlen)
        self.data_list = deque(maxlen=maxlen)
        self.metka_man_list = deque(maxlen=maxlen)
        self.metka_avto_list = deque(maxlen=maxlen)

    def create_fild(self):
        """Рисуем поле"""
        lincolor = 'gray50'
        fontcolor = self.fil
        x_right = 60       # 50
        y_top = self.y_top
        x0 = self.sizeX - x_right
        px = 20                                                  # число пикселов между штрихами
        scrollregY = self.scrol_ / self.k + y_top + 2            # 200000 для 10 000 м (125000 для 6 000 м)
        n_line = int(scrollregY / 20)
        canv = self.canv
        line = canv.create_line
        text = canv.create_text
        canv.config(scrollregion=(0, 0, self.sizeX, scrollregY))
        line(x0, y_top, x0, scrollregY + 10,
             width="3", fill='brown', stipple="gray75", tag='fild')     # y0
        line(x0, y_top, 0, y_top, width="3", fill='brown',
             stipple="gray75", tag='fild')                              # x0
        text(x0+10, y_top, text=0, anchor=tk.W,
             font='Helvetica,10', fill=fontcolor, tag='fild_t')
        self.x_start_fild = int(x0 - 2)
        for i in range(0, n_line):
            stepy = y_top + i * px
            line(x0 + 5, stepy, x0, stepy, fill=lincolor, tag='fild')          # штрих                
            if i % 5 == 0:
                line(x0, stepy, 0, stepy, fill=lincolor, tag='fild_l')          # yn                                      
                text(x0 + 10, stepy, text=f"{i * self.k}",
                     anchor=tk.W, font='Helvetica,10', fill=fontcolor, tag='fild_t')
        self.x_right = x_right
        # self.y_top = y_top
        self.x0 = x0
        self.px = px
        self.scrollregY = scrollregY
# canv.create_rectangle(100,100,101,101,outline='red')   # ,fill='red' квадрат 2x2 px
# canv.create_line(110,110,110,112,fill='blue')          # ,fill='red' линия 2x1 px

        
    def update_data_deque(self):
        self.data_list.appendleft([n / 10 for n in self.root.data_point])
        self.data_amplit.appendleft(self.root.data_ampl)
        self.data_lenth.appendleft([self.root.cal_len(n) for n in self.root.data_len])
        # self.data_lenth.appendleft(self.root.data_len)
        num = self.root.txt_opmetka if self.root.man_metkawriteok[0] else 0
        color_ = "spring green" if self.root.man_metkawriteok[1] else "red"
        num2 = self.root.txt_opmetka if self.root.avto_metkawriteok else 0
        self.metka_man_list.appendleft((num, color_))
        self.metka_avto_list.appendleft(num2)
            
    # def rgb(self, arg):
    #     if self.root.mb:
    #         return self.rgbc(arg)
    #     else:
    #         return self.rgba(arg)

    # @staticmethod        
    # def rgba(arg):                    # TODO:
    #     """Вернуть цвет по амплитуде"""
    #     step = math.ceil(COLORMAX / 12)
    #     for i, j in enumerate(range(step, COLORMAX + 12, step)):
    #         if arg <= j:
    #             return COLOR[11 - i]
    #     # return '#552f6f'                # т синий

    @staticmethod    
    def rgbc(arg):
        """Вернуть цвет по амплитуде как в ПУИ"""
        a = (0x14, 0x2C, 0x3E, 0x4E, 0x60, 0x72, 0x80, 0x90, 0xA0, 0xB6, 0xD0, 0xFF)   # темносиний ... темнокрасный
        for i, j in enumerate(a):
            if arg <= j:
                return COLOR[11 - i]      # COLOR[0..11] от т красного  до т синего
        # return '#552f6f'                  # т синий  

    def show_data_zip(self, on_eco=False):
        """Показ данных всего поля (перерисовка)"""
        # h1 = 2
        x = self.x0 - 1
        k = self.px / self.k
        y_top = self.y_top
        line = self.canv.create_line
        gen_data = zip(range(self.x_start_fild), self.data_list, self.data_amplit, self.data_lenth,
                       self.metka_man_list, self.metka_avto_list)
        # gen_data = zip(range(self.x_start_fild), self.data_list, self.data_amplit,
        #                self.metka_man_list, self.metka_avto_list)
        # for _, glub_, ampl_len_, mm_, ma_ in gen_data:
        for _, glub_, ampl_, len_, mm_, ma_ in gen_data:
            x -= 1
            if glub_:   # glub_ = [g0, g0, g1, ...g19]
                try:
                    y_g = y_top + glub_[0] * k + 1      # glub_[0] -> except 
                    if not self.root.visible:                           # показ всех точек с len
                        # if len(glub_) > 1:
                        #     glub_ = glub_[1 :]
                        #     ampl_len_ = ampl_len_[1 : ]
                        # gen_all_data = zip(glub_[1 : ], ampl_len_[1 : ])
                        gen_all_data = zip(glub_[1 : ], ampl_[1 : ], len_[1 : ])
                        # for gl, am_ln in gen_all_data:
                        for gl, am, ln in gen_all_data:
                            y = y_top + gl * k + 1
                            if gl > 0:
                                colorPoint = self.rgbc(am)
                                t = ln * k
                                # colorPoint = self.rgbc(am_ln[0])
                                # t = am_ln[1] * k
                                h = t if t > 2 else 2 
                                hl = h if not self.root.visible_len else 2
                                line(x, y, x, y + hl, fill=colorPoint, tag='point')
                    else:                                               # показ одной цели в 2px
                        if glub_[0] > 0: 
                            colorPoint = 'white' if self.root.color_ch else 'black'
                            line(x, y_g, x, y_g + 2, fill=colorPoint, tag='point_g')
                except IndexError:
                    y_g = 0
                    # print('ex')
                if not self.hide_ and not on_eco:
                    try:
                        y_g = y_g if glub_[0] else y_top
                        if mm_[0] != 0:         # перерисовка ручн меток
                            line(x - 2, y_top + 1, x - 2, y_g, fill=mm_[1], tag='mmetka')
                        if ma_ != 0:            # перерисовка авто меток
                            line(x - 2, y_top + 1, x - 2, y_g, fill='DodgerBlue2', tag='ametka')
                    except IndexError:
                        pass

    def show_opgl(self):
        """Показ линии опасной глубины"""
        if self.bso_:
            return
        k = self.px / self.k
        y_g = self.y_top + self.root.opgl * k + 1
        # text = f'{self.opgl:2.1f} м'
        text = f'{self.root.opgl} м'
        self.canv.delete('opgl')
        if self.root.opgl > 0:       # не рисуем линию если оп. глуб. равна нулю
            self.canv.create_line(self.x0 - 2, y_g, 0, y_g, fill='magenta', tag='opgl')
            self.canv.create_text(self.x0 - 40, y_g - 9, text=text, anchor='center',
                                  font=('Helvetica', 8), fill='magenta', tag='opgl')

    def move_metka(self, x=-1, y=0):
        """Переместить метки на x, y"""
        for i in ('ametka', 'tametka', 'mmetka', 'mman_t', 'mman_td', 'timeametka'):     # 'mman_t_glub',
            self.canv.move(i, x, y)
        
    def move_metkai_hide(self, hide):
        """Переместить техт меткок для скрытия и удалить линии"""
        self.hide_ = hide
        maxy = -100
        if hide:
            self.canv.move('mman_t', 0, maxy)       # текст на ручной метке
            self.canv.move('mman_td', 0, maxy)      # текст на ручной метке диапазона
            # self.canv.move('mman_t_glub', 0, maxy)  # глубина на ручной метке
            self.canv.move('timeametka', 0, maxy)   # время на авт. метке
            self.canv.move('tametka', 0, maxy)      # текст на авт. метке
            self.canv.delete('mmetka')              # ручная метка
            self.canv.delete('ametka')              # авт. метка
        else:
            self.canv.move('mman_t', 0, -maxy)       # текст на ручной метке
            self.canv.move('mman_td', 0, -maxy)      # текст на ручной метке диапазона
            # self.canv.move('mman_t_glub', 0, -maxy)  # глубина на ручной метке
            self.canv.move('timeametka', 0, -maxy)   # время на авт. метке
            self.canv.move('tametka', 0, -maxy)      # текст на авт. метке
            self.reconfig()
            
    def move_grid(self, x, y=0):
        """Переместить гор. разметку"""
        self.canv.move('fild_l', x, y)

    def del_widht_canvas(self):
        """Удалить всё за пределами холста"""
        y = self.scrollregY + 10
        x1 = 900 - self.root.winfo_screenwidth()
        x = x1 - 110
        for id_ in self.canv.find_enclosed(x, -110, x1, y):      # canv.find_overlapping
            if id_:
                self.canv.delete(id_)

    def show_point(self):
        """Показ очередных целей в начале"""
        # h1 = 2                            # при показе одной цели len = 2px
        self.canv.move('point_g', -1, 0)
        self.canv.move('point', -1, 0)
        self.move_metka()
        k = self.px / self.k
        y_top = self.y_top
        data_point = [n / 10 for n in self.root.data_point]     # список 1 + cnt глубин gl
        data_ampl = self.root.data_ampl                         # список 1 + cnt ampl
        # data_len = self.root.data_len       # список 1 + cnt lenth
        data_len = [self.root.cal_len(n) for n in self.root.data_len]       # список 1 + cnt lenth
        if data_point:
            x = self.x0 - 2
            y_g = y_top + data_point[0] * k + 1
            if data_point[0] > 0:           # есть глубина
                if self.root.visible:       # одна цель
                    color_point = 'white' if self.root.color_ch else 'black'
                    self.canv.create_line(x, y_g, x, y_g + 2, fill=color_point, tag='point_g') 
            if not self.root.visible:       # все цели
                # if len(data_point) > 1:
                #     data_point = data_point[1 : ]
                #     data_ampl = data_ampl[1 :]
                for point, ampl, len_ in zip(data_point[1 : ], data_ampl[1 : ], data_len[1 : ]):
                    y = y_top + point * k + 1
                    if point > 0:
                        color_point = self.rgbc(ampl)
                        t = len_ * k
                        h = t if t > 2 else 2
                        hl = h if not self.root.visible_len else 2
                        self.canv.create_line(x, y, x, y + hl, fill=color_point, tag='point')
            self.y_g = y_g            

    def reconfig2(self):
        """Тольо одна цель"""
        self.reconfig()
        if self.root.visible:
            self.canv.delete('point')

    def reconfig(self, arg=None):
        """Обновить холст"""
        for i in ('point', 'point_g', 'fild', 'fild_l', 'fild_t', 'mmetka', 'ametka'):
            self.canv.delete(i)
        self.create_fild()
        self.show_data_zip()
        self.show_opgl()
        if self.root.hide_grid:
            self.move_grid(-2700, 0)
        if self.bso_:
            self.root.opgl = 0
        self.view_glub(self.oldglub, self.root.opgl)

    def up(self, arg=None):
        """Увеличить масштад"""
        # self.n_ = 11
        if self.i < self.n_:
            self.i += 1
            self.k = self.skale[self.i]
            self.reconfig2()
        if self.i == self.n_:
            self.canv.yview(tk.MOVETO, 1.0)

    def down(self, arg=None):
        """Уменьшить масштад"""
        if self.i > 0:
            self.i -= 1
            self.k = self.skale[self.i]
            self.reconfig2()
        if self.i == 0:
            self.canv.yview(tk.MOVETO, 0.0)

    def home(self, arg=None):
        """На начало"""
        self.k = 1.0
        self.i = 0
        self.canv.yview(tk.MOVETO, 0.0)
        self.reconfig2()

    def en(self, arg=None):
        """В конец (6250м)"""
        self.k = self.skale[-2]     # 500
        self.i = self.n_            # 11
        self.canv.yview(tk.MOVETO, 1.0)
        self.reconfig2()

    def size_canv(self, arg=None):
        """Даёт текущую ширину и высоту холста"""
        oldX, oldY = self.sizeX, self.sizeY
        canvw, canvh = self.canv.winfo_width(), self.canv.winfo_height()
        self.sizeX, self.sizeY = canvw, canvh
        self.canv.move('glub', 0, self.sizeY-oldY)
        self.move_metka(self.sizeX-oldX, 0)
        self.reconfig(1)
        if self.root.visible:
            self.canv.delete('point')
