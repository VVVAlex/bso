#!/usr/bin/env python
# -*- coding:utf-8 -*-

import tkinter as tk
import math, os, time
from tkinter import ttk
from util import imgdir, rgb
from tooltip import ToolTip
from lupa import Lupa


class Fild(ttk.Frame):
    """Класс холста просмотра + информ.лабель"""

    def __init__(self, parent, bso_=False):
        super().__init__(parent)
        self.parent = parent
        # self.mult = (1, 2, 10, 20, 40, 100, 200, 300)                # see  _calk_scale and up(in canvas_show)
        self.mult = (1, 2, 5, 10, 20, 40, 50, 100, 200, 300, 400, 500)
        self.step = (0, 5, 10, 15, 20)
        self.W, self.H = 988, 400       # 868, 400
        self.m_top = 35
        self.m_right = 55
        self.m_bottom = 35 
        self.m_left =  20                           # margin
        self.font = ('tahoma', '10', 'bold')        # Helvetica bold italic
        self.ofsetd = 43
        self.n = 0
        self.n__ = 9 if bso_ else 11                # 9 for 6000
        self.scale = 0                              #scale 0,1,2,3,4,5,6,7 +4000, 6000
        self.screen = 1                             # текущий экран
        self.marker_on = 0
        self.fullscreen = 0
        self.id = None
        self.start = None
        (self.schirvalue, self.dolgvalue, self.timevar,
         self.tglub, self.ampvar, self.vsvar, self.kursvar) = (tk.StringVar() for i in range(7))

    def run_(self, frm, data=None):
        """Показ данных"""
        self.dataFull = data                            # all data
        self.frame_info = ttk.Frame(frm)
        self.frame_canv = ttk.Frame(frm)
        self.frame_info.pack(fill='x', expand='no')
        self.canvw = tk.Canvas(self.frame_canv, width=self.W + self.m_right + self.m_left,
                               height=self.H + self.m_top + self.m_bottom,
                               bg='#bbb', relief='ridge', bd=0)     # beige
        self.canvw.config(highlightthickness=0, takefocus=1)
        self.canvw.pack(fill='both', expand='yes')
        self.frame_canv.pack(fill='both', expand='yes')
        self.L = Lupa()
        self.L.withdraw()
        if self.dataFull:
            self.n_screen = self.get_maxscreen()   # число экранов
            self.data = self.dataFull[ : self.W]
            self._calk_scale()
            self.parent.numbersrc_.set(self.screen)
            self.k = self.mult[self.scale]
            self.flag_on_point = False              # показать все цели
            self.flag_on_lentht = True              # показать длительность цели
            self.dno_ = False                       # не подсвечивать рельеф при старте
            self.hide_ = True                       # показать метки при старте
            self.imgbufer = []			            # буфер для хранения изображений меток
            self.create_fild(self.canvw)
            self.text_axis(self.canvw)
            self.set_grid()
            self.label_()
        self.bind_()

    def create_fild(self, canv):
        """Рисуем поле с осями"""
        W, H, m_top, m_right, m_bottom, m_left = self.W, self.H, self.m_top, self.m_right, \
            self.m_bottom, self.m_left
        color1 = color2 = 'blue'
        color3 = color4 = 'brown'
        self.colorf = '#282828'
        line = canv.create_line
        canv.config(width=W + m_right + m_left, height=H + m_top + m_bottom)         
        canv.create_rectangle(m_left, m_top, m_left + W,
                              m_top + H, fill=self.colorf, tag='fild')
        line(m_left - 1, m_top, m_left - 1,                         # axis
             m_top + H, width="2", fill=color4, tag='fild')         # 4 left
        line(m_left + W + 2, m_top, m_left + W + 2,
             m_top + H, width="2", fill=color2, tag='fild')          # 2 right
        line(m_left - 1, m_top, m_left + W + 1,                      # 1 top
             m_top, width="2", fill=color1, tag='fild')
        line(m_left - 2, m_top + H,                                  # 3 bottom
             m_left + W + 2, m_top + H, width="2", fill=color3, tag='fild')
        for N in range(8):
            t = 10 if N % 2 == 0 else 7                            # len tick short ant long
            line(m_left + W + 2, m_top + N * H // 8, m_left + W + 2 + t, m_top + N * H // 8,  # tick_Y
                 width="2", fill=color1, tag='fild')
            line(m_left + N * W // 8 - 2, m_top + H, m_left + N * W // 8 - 2, m_top + H + t,  # tick_X
                 width="2", fill=color3, tag='fild')

    def set_grid(self):
        """Показать сетку"""
        self.GRID = 1                   # grin on
        for N in range(8):
            self.canvw.create_line(self.m_left, self.m_top + N * self.H // 8,
                                  self.m_left + self.W, self.m_top + N * self.H // 8,        # grid_X
                                  width="1", dash=(3, 5), fill='gray55', tag='grid')
            self.canvw.create_line(self.m_left + N * self.W // 8 - 2, self.m_top + self.H,
                                  self.m_left + N * self.W // 8 - 2, self.m_top,             # grid_Y
                                  width="1", dash=(3, 5), fill='gray55', tag='grid')

    def clr_grid(self):
        """Убрать сетку"""
        self.GRID = 0                   # grig off
        self.canvw.delete('grid')

    def text_axis(self, canv):
        """Наносим на оси время и дату по Y всё по X только в начале"""
        W, H, m_top, m_left = self.W, self.H, self.m_top, self.m_left
        ofsetX = 15
        ofsetY = 12         #  for text
        text = canv.create_text
        for i in range(5):
            txtY = self.step[i] * self.k
            text(m_left + W + ofsetX, m_top + i * H // 4, text=f'{txtY:2d}',        # text_Y
                 anchor='w', font=self.font, fill='darkblue', tag='text')
        txtX = time.strftime("%H:%M", self.data[0].timdata)
        self.day = txtXD = time.strftime("%d.%m", self.data[0].timdata)
        if txtX and txtXD:
            text(m_left + W - 16, m_top + H + ofsetY, text=f'{txtX}',               # text_X_time0
                 anchor='n', font= self.font, fill='brown', tag='text')
            text(m_left + W + 25, m_top + H + ofsetY, text=f'/{txtXD}',             # text_X_data0
                 anchor='n', font=self.font, fill='darkgreen', tag='text')
                            
#data = [(format, glub, amp, lehth, timdata, shir, dolg, vs, kurs,...
#         m_man, color_mm, m_avto, all_data)...] all_data = [(gl,amp,len),(gl1,amp1,len1)...]
    def set_data(self, canv):
        """Выводим данные и надписи на осях и метки"""
        W, H, m_top, m_left = self.W, self.H, self.m_top, self.m_left
        color_p = '#f59400';color_t = 'brown';color_d = 'darkgreen';font_t = self.font
        ofsetY = 12
        # y_len = 2
        line = canv.create_line
        text = canv.create_text
        for j in range(W):
            if j < len(self.data):
                # if 1:                      # глубина, в amp цвет        !!! self.data[j].glub
                    # all_data = self.data[j].all_data
                    # if self.data[j].all_data:             # бывает есть глубина а all_data=[] !!! [-1]
                    # if self.data[j].glub:                   # all_data
                Y = (self.data[j].glub / self.k * H / 200)
                    # else:
                    #     continue
                if Y < H and Y != 0:
                    line(m_left + W - j, m_top + Y,
                            m_left + W - j, H + m_top - 2,
                            fill=self.colorf, tag='dno')           # дно рисуем раньше точек (иначе затрём нижние цели)
                if not self.flag_on_point:
                    all_data = self.data[j].all_data   
                    for gl, amp, ln in all_data:
                        Y1 = (gl / self.k * H / 200)
                        L1 = (ln / self.k * H / 20) if self.flag_on_lentht else 2
                        color1 = rgb(amp)
                        if Y1 < H:
                            y_len = L1 if L1 > 2 else 2
                            if Y1 + y_len > H:
                                y_len = H - Y1
                            line(m_left + W - j, m_top + Y1,         # point_all
                                    m_left + W - j, m_top + Y1 + y_len,
                                    fill=color1, width='1', tag='point_all')
                else:
                    if Y < H and Y != 0:
                        line(m_left + W - j, m_top + Y,               # point one
                                m_left + W - j, m_top + Y + 2,
                                fill=color_p, width='1', tag='point')
                              
                if j == W // 4 - 1:
                    txtX = time.strftime("%H:%M", self.data[j].timdata)                  # [3]
                    text(m_left + W * 3 // 4,
                         m_top + H + ofsetY, text=f'{txtX}',         # text_X_time1
                         anchor='n', font=font_t, fill=color_t, tag='text')
                    if self.day != time.strftime("%d.%m", self.data[j].timdata):
                        txtXD = time.strftime("%d.%m", self.data[j].timdata)
                        text(m_left + W * 3 // 4 + self.ofsetd,
                             m_top + H + ofsetY, text=f'/{txtXD}',   # text_X_data1
                             anchor='n', font=font_t, fill=color_d, tag='text')
                        self.day = txtXD
                if j == W // 2 - 1:
                    txtX = time.strftime("%H:%M", self.data[j].timdata)
                    text(m_left + W // 2,
                         m_top + H + ofsetY, text=f'{txtX}',         # text_X_time2
                         anchor='n', font=font_t, fill=color_t, tag='text')
                    if self.day != time.strftime("%d.%m", self.data[j].timdata):
                        txtXD = time.strftime("%d.%m", self.data[j].timdata)
                        text(m_left + W // 2 + self.ofsetd,
                             m_top + H + ofsetY, text=f'/{txtXD}',   # text_X_data1
                             anchor='n', font=font_t, fill=color_d, tag='text')
                        self.day = txtXD
                if j == W * 3 // 4 - 1:
                    txtX = time.strftime("%H:%M", self.data[j].timdata)
                    text(m_left + W // 4,
                         m_top + H + ofsetY, text=f'{txtX}',         # text_X_time3
                         anchor='n', font=font_t, fill=color_t, tag='text')
                    if self.day != time.strftime("%d.%m", self.data[j].timdata):
                        txtXD = time.strftime("%d.%m", self.data[j].timdata)
                        text(m_left + W // 4 + self.ofsetd,
                             m_top + H + ofsetY, text=f'/{txtXD}',    # text_X_data1
                             anchor='n', font=font_t, fill=color_d, tag='text')
                        self.day = txtXD
                if j == W - 1:
                    txtX = time.strftime("%H:%M", self.data[j].timdata)
                    text(m_left, m_top + H + ofsetY,
                         text=f'{txtX}', anchor='n', font=font_t, fill=color_t, tag='text')
                    if self.day != time.strftime("%d.%m", self.data[j].timdata):
                        txtXD = time.strftime("%d.%m", self.data[j].timdata)
                        text(m_left + self.ofsetd,
                             m_top + H + ofsetY, text=f'/{txtXD}',  # text_X_data1
                             anchor='n', font=font_t, fill=color_d, tag='text')
                        self.day = txtXD
                
                Y = m_top + self.data[j].glub // self.k * H // 200          # int()
                if Y > m_top + H:
                    Y = m_top + H
                num = self.data[j].m_man.strip()        # [8]
                if num:                                 # мануал метка 8
                    color = self.data[j].color_mm       # [9]
                    self.create_manmetka(j, num, color, Y)
                numa = self.data[j].m_avto.strip()      # [10]
                if numa:                                # авто метка  10
                    self.create_avtometka(j, numa, Y)

    def create_avtometka(self, j, numa, Y):
        """Нарисовать автоматическую метку"""
        font = ("tahoma", "8")
        self.canvw.create_line(self.m_left + self.W - j, Y,
                              self.m_left + self.W - j, self.m_top - 1,
                              fill='DodgerBlue2', width='1', tag='avto_metka')
        txt = time.strftime('%H:%M', self.data[j].timdata)       # %d.%m.%y
        self.canvw.create_text(self.m_left + self.W - 16 - j, self.m_top - 25,
                              text=txt, anchor='w', font=font, fill='RoyalBlue4', tag='texta')
        self.canvw.create_text(self.m_left + self.W - j - 3, self.m_top - 10,
                              text=numa, anchor='w', font=font, fill='RoyalBlue4', tag='texta')

    def create_manmetka(self, j, num, color, Y):
        """Нарисовать ручную метку"""
        font = ("tahoma", "8")
        color_ = "red" if color == "red" else "spring green"
        self.canvw.create_line(self.m_left + self.W - j, Y,
                              self.m_left + self.W - j, self.m_top, fill=color_, width='1', tag='man_metka')
        self.canvw.create_text(self.m_left + self.W - j - 3, self.m_top - 10,
                              text=num, anchor='w', font=font, fill=color_, tag='man_img')

#---------------- info ---------------------------------------------------
    def label_(self):
        """Фрейм для вывода всех данных"""
        font = ('tachoma','10')
        bg = 'gray85'
        s = ttk.Style()
        s.configure('V.TLabel', font=font, height=1,
                    anchor='center')
        s.configure('V2.TLabel', background=bg, font=font, height=1,
                    anchor='center')
        list_ = [('Время', self.timevar, '14'), ('Широта', self.schirvalue, '14'),
                 ('Долгота', self.dolgvalue, '14'), ('Путевой угол', self.kursvar, '9'),
                 ('Путевая скорость', self.vsvar, '12'), ('Формат', self.parent.format_var, '4'),
                #  ('Глубина', self.parent.can_show.tglub, 9),
                 ('Глубина', self.tglub, 9),
                 ('Скорость звука', self.parent.v_var, '9'), ('Заглубление', self.parent.stbar_z, '6')]
        for text, var, w in list_:
            f = ttk.Frame(self.frame_info, style='M.TFrame')
            ttk.Label(f, text=text, style="V.TLabel", relief='flat', width=w).pack(fill='x', expand='yes', ipady=2)
            l = ttk.Label(f, textvariable=var, style="V2.TLabel", relief='groove',
                          borderwidth=2, width=w)
            l.pack(fill='x', expand='yes', ipady=2)
            f.pack(side='left', fill='x', expand='yes') 


    def info(self, event):
        """Инициализация переменных по данным"""
        index = self.index_(event)
        if index is not None:
            head_data = (self.data[index].format_, self.data[index].ku, self.data[index].depth,
                         self.data[index].rej, self.data[index].frek, self.data[index].cnt, 
                         self.data[index].m, self.data[index].vz, self.data[index].zg)
            # index_ = index + self.W * (self.screen - 1)
            self.parent.set_head(head_data)               # вывод в нижний лабель (из show_bso) !!abc
            # format_ = self.data[index][0]               # format
            glub = self.data[index].glub / 10.            # glubina
            glub_ = f'{glub} м'
            if int(self.data[index].m): 
                ampl = self.data[index].ampl              # амплитуда
                lenth = self.data[index].lenth             # длительность 
            else:
                ampl = ''
                lenth = ''
            t = time.strftime("%d.%m %H:%M:%S", self.data[index].timdata)
            sh = self.data[index].shir.split()            # schirota
            dol = self.data[index].dolg.split()           # dolgota
            vs = self.data[index].vs                      # скорость судна
            vs_ = f'{vs} уз'
            kurs = self.data[index].kurs                  # курс
            kurs_ = f'{kurs}{0xB0:c}'
            try:
                sh = f"{sh[0]}{0xB0:c} {sh[1]}{0xB4:c} {sh[2]}"
                dol = f"{dol[0]}{0xB0:c} {dol[1]}{0xB4:c} {dol[2]}"
            except Exception:
                sh = dol = ''
            # maxg = 100000.0 if self.metr_ else 6553.5
            if glub < 6000:                          # maxg
                self.tglub.set(glub_)
                self.timevar.set(t)
                self.schirvalue.set(sh)
                self.dolgvalue.set(dol)
                self.ampvar.set(f"{ampl} / {lenth} м")       # 
                self.vsvar.set(vs_)
                self.kursvar.set(kurs_)
                if glub <= 0:                         # если <=0 то не отображаем
                    self.tglub.set('')
                if not ampl:
                    self.ampvar.set('')
                if not sh:
                    self.schirvalue.set('')
                if not dol:
                    self.dolgvalue.set('')
                if not vs:
                    self.vsvar.set('')
                if not kurs:
                    self.kursvar.set('')
                return
        self.clr_var()

    def clr_var(self):
        """Очистка полей данных"""
        self.tglub.set('')
        self.timevar.set('')
        self.schirvalue.set('')
        self.dolgvalue.set('')
        self.ampvar.set('')
        self.vsvar.set('')
        self.kursvar.set('')
        self.parent.clr_var_h()        # очищаем нижний лабель (из show_bso)   !!! abc

    def index_(self, event):
        """Позиция в данных"""
        index = (self.W + self.m_left) - event.x if event \
            else (self.W + self.m_left) - self.start.x
        if index < len(self.data):                    # self.W
            return index

    def dno(self, arg=None):
        """Cкрыть показать профиль"""
        color_d = self.colorf if self.dno_ else '#505050'
        im = self.parent.img_['light_off'] if self.dno_ else self.parent.img_['light_on']
        self.parent.tol_bar.btn['Подсветка дна'].config(image=im)
        self.dno_ = not self.dno_
        self.canvw.itemconfigure('dno', fill=color_d)
        if self.GRID: self.set_grid()
        self.parent.m_dno.set(1) if self.dno_ else self.parent.m_dno.set(0)

    def one_ceil(self, arg=None):
        """Cкрыть показать все цели или одна цель"""
        (im, tip) = (self.parent.img_['sloion'], 'Все цели') if self.flag_on_point \
                     else (self.parent.img_['sloi3'], 'Одна цель')
        self.parent.tol_bar.btn['Все цели'].config(image=im)
        ToolTip(self.parent.tol_bar.btn['Все цели'], msg=tip)
        self.flag_on_point = not self.flag_on_point
        self.update_data()

    def len_view(self, arg=None):
        """Cкрыть показать протяженность цели"""
        (im, tip) = (self.parent.img_['linechart'], 'Длительность  скрыта') if self.flag_on_lentht \
                     else (self.parent.img_['candlestick'], 'Длительность видна')
        self.parent.tol_bar.btn['Длительность видна'].config(image=im)
        ToolTip(self.parent.tol_bar.btn['Длительность видна'], msg=tip)
        self.flag_on_lentht = not self.flag_on_lentht
        self.update_data()
        self.parent.view_len.set(1) if self.flag_on_lentht else self.parent.view_len.set(0)

    def metka(self, arg=None):
        """Cкрыть показать все метки"""
        (im, tip) = (self.parent.img_['geooff'], 'Показать метки') if self.hide_ \
                     else (self.parent.img_['geoon'], 'Скрыть метки')
        self.parent.tol_bar.btn['Скрыть метки'].config(image=im)
        ToolTip(self.parent.tol_bar.btn['Скрыть метки'], msg=tip)
        self.hide_ = not self.hide_
        self.update_data()
        self.parent.m_hide.set(1) if self.hide_ else self.parent.m_hide.set(0)

    def grid(self, arg=None):
        """Cкрыть показать сетку"""
        (im, tip) = (self.parent.img_['lauernogrid'], 'Сетка выкл.') if self.GRID \
                     else (self.parent.img_['grid2'], 'Сетка вкл.')
        self.parent.tol_bar.btn['Сетка вкл.'].config(image=im)
        ToolTip(self.parent.tol_bar.btn['Сетка вкл.'], msg=tip)
        self.clr_grid() if self.GRID else self.set_grid()
        self.parent.m_grid.set(1) if self.GRID else self.parent.m_grid.set(0)

    def next(self, arg=None):
        """На следующий экран"""
        if self.screen < self.n_screen:
            self.screen += 1
            self.datascreen()

    def prev(self, arg=None):
        """На предыдущий экран"""
        if self.screen > 1:
            self.screen -= 1
            self.datascreen()

    def up(self, arg=None):
        """Увеличить масштаб"""
        if self.scale < self.n__:       # 9 for 10000м
            self.scale += 1
            self.update_data()

    def down(self, arg=None):
        """Уменьшить масштаб"""
        if self.scale > 0:
            self.scale -= 1
            self.update_data()

    def full(self, arg=None):
        """Полный экран"""
        if self.parent.viewData:
            self._enter() if self.fullscreen else \
                self._dataFullscreen()
            for v in ('avto_metka', 'texta', 'man_metka', 'man_img'):
                self.canvw.delete(v)
            self.parent.tol_bar.config_btn()

    def calk_data_lupa(self, event):
        """Подготовить данные для лупы"""
        """[Row(format_='DBK', glub=1477, ampl='0', lenth=0.48,
            timdata=time.struct_time(tm_year=2019, tm_mon=6, tm_mday=17, tm_hour=12, tm_min=5, tm_sec=19,
            tm_wday=0, tm_yday=168, tm_isdst=-1),
            shir='', dolg='', vs='', kurs='', vz='1500', zg='0.0', ku='15', depth='M', rej='R', frek='50',
            cnt=2, m='2', m_man='', color_mm='', m_avto='', all_data=[(1477, 20, 0.48), (1500, 62, 2.88)]), ...]"""
        x0 = self.W + self.m_left - event.x
        y0 = event.y - self.m_top
        n = 40
        if x0 < 0 or y0 < 0:
            return
        data = self.data[x0 : x0 + n] if len(self.data) > n else self.data[x0 : ]
        return data

    def _view_lupa(self, event):
        """Показать окно лупы"""
        data = self.calk_data_lupa(event)
        if data:
            self.L.lenth = True if self.flag_on_lentht else False
            geom = self.parent.get_geometry_root()
            self.L.focus_force()
            self.L.geometry(f"+{5 + geom[1] + event.x - 200}+{110 + geom[2] + event.y}")      # от экрана 15 143
            self.L.deiconify()
            y0 = event.y - self.m_top
            self.L.draw(self.k, self.H, y0, data)

    def _move_lupa(self, event):
        """Переместить окно лупы"""
        self._view_lupa(event)

    # def _lupa_color(self, event):
    #     self.canvw.focus_force()
    #     self.L.destroy()
    #     self.L = Lupa(color='gray22')
    #     self.L.withdraw()

    def next_one(self, event):
        """Переместить маркер влево на 1px"""
        if self.start is not None:
            if self.W + self.m_left + 1 > self.start.x > self.m_left:
                # self.canvw.move('marker', -1.0, 0)
                self.canvw.delete('marker')
                self.start.x -= 1
                self._marker(self.canvw, self.start)
                # self.info(self.start)

    def prev_one(self, event):
        """Переместить маркер вправо на 1px"""
        if self.start is not None:
            if self.W + self.m_left > self.start.x > self.m_left - 1:
                    # self.canvw.move('marker', 1.0, 0)
                    self.canvw.delete('marker')
                    self.start.x += 1
                    self._marker(self.canvw, self.start)
                    # self.info(self.start)

    def bind_(self, arg=None):
        # self.canv.bind_all("<a>", self._scal)
        self.canvw.bind("<ButtonPress-1>", self._on_marker)
        self.canvw.bind("<ButtonRelease-1>", self._release)
        self.canvw.bind("<B1-Motion>", self._move_marker)
        self.canvw.bind("<Double-1>", self._enter)
        self.canvw.bind_all("<Escape>", self._clear_marker)
        self.canvw.bind("<Control-ButtonPress-1>", self._view_lupa)
        self.canvw.bind("<Control-B1-Motion>", self._move_lupa)
        # self.canvw.bind("<Alt-B1-Motion>", self._move_lupa)
        # self.canvw.bind("<Double-2>", self._lupa_color)
        self.bind_2()
        # self.canv.bind("<ButtonPress-2>", self._dataFullscreen)

    def bind_2(self, arg=None):
        self.canvw.bind_all("<Home>", self._home)
        self.canvw.bind_all("<End>", self._end)
        self.canvw.bind_all("<Up>", self.up)
        self.canvw.bind_all("<Down>", self.down)
        self.canvw.bind_all("<Left>", self.next)
        self.canvw.bind_all("<Right>", self.prev)
        self.canvw.bind_all("<Control-Left>", self.next_one)
        self.canvw.bind_all("<Control-Right>", self.prev_one)

    def unbind_(self, arg=None):
        self.canvw.unbind("<ButtonPress-1>")
        self.canvw.unbind("<ButtonRelease-1>")
        self.canvw.unbind("<B1-Motion>")
        self.canvw.unbind("<Double-1>")
        self.canvw.unbind("<Double-2>")
        self.canvw.unbind_all("<Escape>")
        self.unbind_2()

    def unbind_2(self, arg=None):
        self.canvw.unbind_all("<Home>")
        self.canvw.unbind_all("<End>")
        self.canvw.unbind_all("<Up>")
        self.canvw.unbind_all("<Down>")
        self.canvw.unbind_all("<Left>")
        self.canvw.unbind_all("<Right>")
        self.canvw.unbind_all("<Control-Left>")
        self.canvw.unbind_all("<Control-Right>")

    def moveMetka(self, d):
        """Переместить метки на d"""
        for v in ("avto_metka", "texta", "man_metka", "man_img"):
            self.canvw.move(v, d, 0)

    def resize(self, event=None):
        """Изменение размера холста при измкнении размера окна"""
        if self.canvw.winfo_geometry() != '1x1+0+0':
            canvw, canvh = self.canvw.winfo_width(), self.canvw.winfo_height()
            self.W, self.H = canvw - self.m_left - self.m_right,\
                canvh - self.m_bottom - self.m_top
        self.reconfig()

    def _enter(self, event=None):
        """Обработка поля ввода номера экрана"""
        self.parent.tol_bar.config_btn(state='normal')
        try:
            self.screen = int(self.parent.src_.get())
            if self.screen > self.n_screen:
                self.screen = self.n_screen
            if self.screen < 1:
                self.screen = 1
            self.canvw.focus_set()
            self.datascreen()
        except ValueError:
            self.parent.src_.delete(0,tk.END)

#------------------------------------scroll------------------------------
    def _end(self, event=None):
        """На последний экран"""
        self.screen = self.n_screen
        self.datascreen()

    def _home(self, event=None):
        """На первый экран"""
        self.screen = 1
        self.datascreen()

    def _next(self, event=None):
        if self.screen < self.n_screen:
            self.screen+=1
            self.datascreen()

    def _prev(self, event=None):
        if self.screen > 1:
            self.screen -= 1
            self.datascreen()

    def _dataFullscreen(self, event=None):
        """Полный экран"""
        k = self.n_screen
        data = self.dataFull[0 : self.W * k : k]
        self.fullscreen = 1
        self.parent.src_["foreground"] = 'red'
        if data:
            self.reload_fild(data)
        if self.start:                             # not None (=event) когда есть маркер
            self.canvw.delete("marker")

    def update_scr(self):
        """Обновить номер экрана при полном экране"""
        x = self.start.x                            # координата маркера
        scr_w = int(self.n_screen * (x - 20) / self.W)
        scr = self.n_screen - scr_w
        self.screen = scr
        self.parent.numbersrc_.set(scr)

    def datascreen(self):
        """Новый срез данных"""
        self.fullscreen = 0
        if self.screen > self.n_screen:
            self.screen = self.n_screen
        data = self.dataFull[self.W * (self.screen - 1) : self.W * self.screen]
        self.parent.src_["foreground"] = 'blue'
        if data:
            self.reload_fild(data)

    def reload_fild(self, data):
        """Подготовка для перирисовки поля"""
        self.data = data
        self.parent.numbersrc_.set(self.screen)
        if self.parent.avtoscale:
            self._calk_scale()
        self.update_data()

    def update_data(self):
        """Перерисовать поле и оси"""
        for v in ('text', 'point', 'point_all', 'dno', 'marker', 'grid', 'man_metka', 'man_img',
                  'avto_metka', 'texta'):
            try:
                self.canvw.delete(v)
            except:
                # print('canvw.delete Exept')
                pass
        self.k = self.mult[self.scale]
        self.text_axis(self.canvw) 
        self.set_data(self.canvw)
        if not self.hide_:
            self.moveMetka(self.W + self.m_right)
        if self.dno_:
            self.canvw.itemconfigure('dno', fill='#505050')
        if self.GRID:
            self.set_grid()
        if self.marker_on:
            self._marker(self.canvw)

    def reconfig(self, data=None):
        """Перерисовка всего холста при изменении его размера"""
        if data:
            self.dataFull = data
        self.canvw.delete('fild')
        self.create_fild(self.canvw)
        self.canvw.delete('marker')   # иначе будет на другой позиции
        scr = self.get_maxscreen()
        self.parent.stbar_scr.set(f'Число экранов = {scr}')
        self.datascreen()            # вместо update_data()иначе не полностью перерисовываются данные

#-----------------------------------------------------------------------

    def delete_data(self):
        """Очищаем поле"""
        for v in ('text', 'point', 'point_all', 'dno', 'marker', 'grid', 'man_metka', 'man_img',
                  'avto_metka', 'texta'):
            try:
                self.canvw.delete(v)
            except:
                pass

    def _marker(self, canv, event=None):
        """Рисуем маркер"""
        color_m = 'green'
        color_t = 'magenta'       #red'
        X = event.x if event else self.start.x
        Y = self.m_top
        H = self.H
        line = canv.create_line
        line(X, Y, X, Y + H, width="1", fill=color_m, tag='marker')
        line(X + 1, Y, X + 1, Y + 5, width="1", fill=color_t, tag='marker')
        line(X + 2, Y, X + 2, Y + 3, width="1", fill=color_t, tag='marker')
        line(X - 1, Y, X - 1, Y + 5, width="1", fill=color_t, tag='marker')
        line(X - 2, Y, X - 2, Y + 3, width="1", fill=color_t, tag='marker')
        line(X + 1, Y + H, X + 1, Y + H - 5, width="1", fill=color_m, tag='marker')
        line(X + 2, Y + H, X + 2, Y + H - 3, width="1", fill=color_m, tag='marker')
        line(X - 1, Y + H, X - 1, Y + H - 5, width="1", fill=color_m, tag='marker')
        line(X - 2, Y + H, X - 2, Y + H - 3, width="1", fill=color_m, tag='marker')
        index = self.index_(event)          # light marker
        if index is not None:
            try:
                dat = self.data[index].glub / self.k * H / 200              # [1]
                if dat > H - 5:
                    dat = H - 5
                line(X, Y + 5, X, Y + dat, fill=color_t, tag='marker')
            except Exception:
                pass
        self.info(event)

    def update_screen(self, event):
        """Перейти на следующий или предыдущий экран"""
        if event.x <= self.m_left and self.m_top + self.H > event.y > self.m_top:
            self._next()
        if event.x >= self.W + self.m_left and self.m_top + self.H > event.y > self.m_top:
            self._prev()

    def a_cancel(self):
        """Отвязать пролистывание экранов после repid()"""
        if self.id:
            self.canvw.after_cancel(self.id)
            self.id = None

    def _release(self, event=None):     # отпускание кнопки 1 мыши
        self.canvw.configure(cursor='')
        self.a_cancel()

    def notfild(self):
        """Пролистываем экраны когда курсор не в поле"""
        if self.fullscreen == 0:
            self.marker_on = 0
            if self.id is None:
                self.repid()

    def _on_marker(self, event):
        """Показать маркер"""
        self.canvw.delete('marker')
        self.start = event                                       # запомнить позицию маркера
        if self.W + self.m_left + 1 > event.x > self.m_left - 1 and \
           self.m_top + self.H > event.y > self.m_top:
                self.canvw.configure(cursor='cross')             # cross, sb_h_double_arrow
                self.marker_on = 1
                self._marker(self.canvw, event)                  # нарисовать маркер
                self.a_cancel()
                if self.fullscreen:
                    self.update_scr()
        else:
            self.notfild()
        self.L.destroy_()                                        # убрать лупу

    def _move_marker(self, event):
        """Переместить маркер"""
        if self.W + self.m_left + 1 > event.x > self.m_left - 1 and \
           self.m_top + self.H > event.y > self.m_top:
            self.canvw.delete('marker')
            self.marker_on = 1
            self.start = event                                  # запомнить позицию маркера
            self._marker(self.canvw, event)                     # нарисовать маркер
            self.a_cancel()
            if self.fullscreen:
                self.update_scr()
        else:
            self.notfild()

    def _clear_marker(self, event=None):
        """Погасить маркер"""
        self.canvw.delete('marker')
        self.marker_on = 0
        self.clr_var()

    def repid(self):
        """Если надо то сменить экран через 0.6 сек на след./предыд."""
        self.update_screen(self.start)
        self.id = self.canvw.after(800, self.repid)      # возвращает целый id для after_cancel

    def _calk_scale(self):
        """Вычислить масштаб"""
        M = [i.glub + i.lenth * 10 for i in self.data]                # !!!  int() + float()
        m = max(M) / 10
        # for i, j in ((1, 0), (2, 1), (10, 2), (20, 3), (40, 4), (100, 5), (200, 6), (300, 7)):    # (400, 8), (500, 9), (1000, 9)):
        for i, j in ((1, 0), (2, 1), (5, 2), (10, 3), (20, 4), (40, 5), (50, 6), (100, 7), (200, 8), (300, 9), (400, 10), (500, 11)):
            if m / i < 20:
                self.scale = j
                break

    def _scal(self, event=None):
        """Изменить масштаб экрана"""
        self._calk_scale()
        self.update_data()

    def get_scale(self):
        """Вернуть масштаб 0-7"""
        return self.scale

    def get_src(self):
        """Вернуть номер экрана"""
        return self.screen

    def get_data(self):
        """Вернуть текущие данные"""
        return self.data

    def get_maxscreen(self):
        """Вернуть число экранов"""
        n_screen = int(math.ceil(len(self.dataFull) * 1.0 / self.W))
        self.n_screen = n_screen
        return n_screen

    def get_filename(self):
        """Вернуть путь[1] с именем файла[0] данных"""
        path = self.parent.get_path()
        return path

    # def save_ps(self, *arg):
    #     print('PS')
    #     self.canvw.postscript(file='can_ps.ps')
