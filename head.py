#!/usr/bin/env python
# -*- coding:utf-8 -*-

import tkinter as tk
from tkinter import StringVar
from tkinter import ttk

s = ttk.Style()

class Head(ttk.Frame):
    """Информационный верхний лабель"""
    def __init__(self, master):
        super().__init__(master)
        # self.root = root
        self.master = master
        (self.t_var, self.vz_var, self.zg_var, self.sh_var, self.d_var,
         self.zona_var, self.skor_var, self.kurs_var, self.format_var) = (StringVar() for _ in range(9))
        self.viewlabel()

    def viewlabel(self):
        """{Время, Широта, Долгота, Путевой угол, Путевая скорость, Формат глубины, Скорость звука, Заглубление}"""
        font = ("Helvetica", 12)
        bg = 'gray85'           # 'gray25'
        # fg = 'black'            # 'green3'
        f = ttk.Frame(self.master, padding=2)
        f.pack(fill=tk.X, expand=False)          # False

        text = ('Широта', 'Долгота', 'Путевой угол', 'Путевая скорость',
                'Формат глубины', 'Скорость звука', 'Заглубление')
        t_var_ = (self.sh_var, self.d_var, self.kurs_var, self.skor_var, self.format_var,
                  self.vz_var, self.zg_var)
        w_ = (21, 21, 15, 16, 15, 11, 11)
        s.configure('H.TLabel', background=bg, anchor=tk.CENTER,
                    borderwidth=1, font=font, relief=tk.GROOVE)
        s.configure('HF.TLabel', background=bg, anchor=tk.CENTER,
                    borderwidth=1, font=font, relief=tk.GROOVE)
        f_v = ttk.Frame(f)
        f_v.pack(side=tk.LEFT, fill=tk.X, expand=False)
        ttk.Label(f_v, textvariable=self.zona_var, font='', anchor=tk.CENTER, padding=(0, 0, 0, 5)).pack(fill="x")
        self.labelTime = ttk.Label(f_v, textvariable=self.t_var, width=27, style='H.TLabel')
        ttk.Separator(f, orient=tk.VERTICAL,
                      style='Kim.TSeparator').pack(side=tk.LEFT, fill=tk.Y)
        self.labelTime.pack(ipady=2)
        i = 0
        for txt, w, tvar in zip(text, w_, t_var_):
            f_ = ttk.Frame(f)
            f_.pack(side=tk.LEFT, fill=tk.X, expand=True)       # False
            ttk.Label(f_, text=txt, font='', anchor=tk.CENTER, padding=(0, 0, 0, 4)).pack(fill="x", expand=True)
            ttk.Separator(f, orient=tk.VERTICAL,
                          style='Kim.TSeparator').pack(side=tk.LEFT, fill=tk.Y)
            styl_ = 'H.TLabel' if i <= 3 else 'HF.TLabel'
            ttk.Label(f_, textvariable=tvar, width=w, style=styl_).pack(side=tk.LEFT, ipady=2,
                                                                        fill="x", expand=True)
            i += 1
         
        ttk.Separator(self.master).pack(fill=tk.X, expand=False)
        self.set_utc()

    def set_utc(self, t=True):
        """Установка UTC, u = временной сдвиг"""
        if t and self.master.zona:    
            self.zona_var.set(f'Время  UTC ( {self.master.zona:+.1f} )')
        elif t:
            self.zona_var.set('Время  UTC ( 0.0 )')
        else:
            self.zona_var.set('Время  системное')

    def set_v(self, v):
        """Установка скорости звука"""
        self.vz_var.set(f'{v} м/с')

    def set_z(self, z):
        """Установка заглубления"""
        self.zg_var.set(f'{z:2.1f} м')

    @staticmethod
    def dop_gradus(st):
        """Вставляем знак градуса и минуту"""
        if st:
            d = st.split()
            d[0] = f'{d[0]}{0xB0:c} '
            d[1] = f'{d[1]}{0xB4:c} '
            st = ''.join(d)
        return st

    def set_sh(self, sh):
        """Установка широты"""
        sh = self.dop_gradus(sh)
        self.sh_var.set(f'{sh}')

    def set_d(self, d):
        """Установка долготы"""
        d = self.dop_gradus(d)
        self.d_var.set(f'{d}')

    def set_t(self, t):
         """Установка времени"""
         self.t_var.set(f'{t}')
         
    def set_vs(self, vs):
        """Установка путевой скорости"""
        self.skor_var.set(f'{vs} уз') if vs else self.skor_var.set('')
                
    def set_k(self, k):
        """Установка путевого угла"""
        self.kurs_var.set(f'{k}{0xB0:c}') if k else self.kurs_var.set('')
        
    def set_format(self, fm):
        """Установка формата"""
        self.format_var.set(f'{fm}')

    def set_(self, *arg):
        self.set_sh(arg[0])
        self.set_d(arg[1])
        self.set_vs(arg[2])
        self.set_k(arg[3])
        self.set_t(arg[4])
        self.set_utc(arg[5])
        