#!/usr/bin/env python
# -*- coding:utf-8 -*-

import tkinter as tk
from tkinter import ttk

s = ttk.Style()

# i16 = \
# 'iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAABHNCSVQICAgIfAhkiAAAAAlwSFlz\nAAAN1wAADdcBQiibeAAAABl0RVh0'\
# 'U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAACXSURB\nVDiN7ZLBCcJQFATnxXQgdiFpQHIXlIANKFhG8JwuhGABHoRfQbCBJO34'\
# '15MXzZOIN3HOy7ALazhs\nDmGNpUcQdmN/rpZhKJd6ApjUWTafItF2XQ3MPhIIJVJEEsjMy7kCI27btj+ZmSyy85t+yUu1ogwa\nCl6q1e'\
# 'AMd1tRBuX5AoCmubqCZFTPN/wFPyEY/cQHz4e6A/kULFtBjk6OAAAAAElFTkSuQmCC\n'


# img = tk.PhotoImage(data=i16)


class InfoBar(ttk.Frame):

    def __init__(self, master):
        super().__init__(master)
        self.diap_var, self.rej_var, self.vz_var = (tk.StringVar() for _ in range(3))
        self.diap_var.trace('w', master.ch_diap)

        fxen = dict(fill=tk.X, expand=False)
        info = ttk.Frame(self, borderwidth=3, relief=tk.GROOVE)     # фрейм для label
        fr_format = ttk.Frame(info)
        fr_format.pack(side=tk.LEFT)

        bg = 'gray85'                        # 'gray25'
        font = ("Times", 14)
        foreground = 'black'                 # 'orange'
        fbey = dict(fill=tk.BOTH, expand=True)
        s.configure('M.TLabel', background=bg, anchor=tk.CENTER,
                    font=font, borderwidth=2, width='1', relief=tk.GROOVE)        # relief=tk.RAISED

        ttk.Label(fr_format, text='Формуляр\n эхолота', image='', font=("Times", 12), foreground='black',
                  compound='left', anchor=tk.CENTER).pack(side=tk.LEFT, ipadx=10)  # format relief=tk.GROOVE

        txt = ('Глубина', 'Уровень \ Длительность', 'Эхо', 'Усиление', 'Диапазон', 'Режим', 'Частота')
        t_v = (master.glub_var, master.ampl_var, master.stop_var, master.porog_var,
               self.diap_var, self.rej_var, master.frek_var)
        self.lab_am_ln = []
        for text, t_var in zip(txt, t_v):
            fr = ttk.Frame(info)
            fr.pack(side=tk.LEFT, fill=tk.X, expand=True)
            ttk.Label(fr, text=text, padding=(0, 0, 0, 4)).pack()
            la = ttk.Label(fr, textvariable=t_var, foreground=foreground, style='M.TLabel')
            la.pack(**fbey)
            self.lab_am_ln.append(la)     #
        info.pack(**fxen)
        self.lab_a_l = ttk.Label(self.lab_am_ln[1], width=1, background=bg, style='M.TLabel')
        self.lab_a_l.pack(side='left') 
