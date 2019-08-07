#!/usr/bin/env python
# -*- coding:utf-8 -*-

import tkinter as tk
from tkinter import StringVar
from tkinter import ttk


class Footer(ttk.Frame):
    """Cтрока состояния"""

    def __init__(self, master, bso_=True):
        super().__init__(master)
        self.img_ = master.img_
        # sbar = ttk.Frame(master)
        fxey = dict(fill=tk.X, expand=True)
        fxen = dict(fill=tk.X, expand=False)
        # sbar.pack(**fxey)
        # self.dir_info = StringVar()
        (self.port_info, self.gps_info, self.rep_info, self.time_i,
         self.err) = (StringVar() for _ in range(5))
        rel = dict(padding=1, relief=tk.SUNKEN)
        info = ttk.Frame(self, **rel)          # Frame потр 485
        info_gps = ttk.Frame(self, **rel)      # Frame потр gps
        info_rep = ttk.Frame(self, **rel)      # Frame потр rep
        # info_dir = ttk.Frame(self, **rel)      # Frame рабочий каталог
        time_err = ttk.Frame(self, **rel)      # Frame сбои линии
        time_step = ttk.Frame(self, **rel)     # Frame период опроса
        info.pack(side=tk.LEFT, **fxey)
        ttk.Label(info, image=self.img_['com'], compound=tk.LEFT, textvariable=self.port_info,
                  width=25, padding=(2, 2)).pack(**fxey)   # side="left",
        ttk.Label(info_gps, image=self.img_['com'], compound=tk.LEFT, textvariable=self.gps_info,
                  width=24, padding=(2, 2)).pack(**fxey)   # side="left",
        ttk.Label(info_rep, image=self.img_['com'], compound=tk.LEFT, textvariable=self.rep_info,
                  width=24, padding=(2, 2)).pack(**fxey)
        tel = ttk.Frame(self, **rel)           # Frame индикотор сом
        tel.pack(side=tk.LEFT, **fxen)
        self.lab_tel = ttk.Label(tel, text='   ', compound=tk.LEFT, padding=(1, 0))
        self.lab_tel.pack(**fxey, ipady=2)   # side="left",
        ttk.Separator(self, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y)
        info_gps.pack(side=tk.LEFT, **fxey)
        tel_gps = ttk.Frame(self, **rel)       # Frame индикотор gps
        tel_gps.pack(side=tk.LEFT, **fxen)
        self.lab_tel_gps = ttk.Label(tel_gps, text='   ', compound=tk.LEFT, padding=(1, 0))
        self.lab_tel_gps.pack(**fxey, ipady=2)   # side="left",
        ttk.Separator(self, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y)
        
        tel_rep = ttk.Frame(self, **rel)        # Frame индикотор rep
        self.lab_tel_rep = ttk.Label(tel_rep, text='   ', compound='left', padding=(1, 0))
        if not bso_:
            info_rep.pack(side="left", **fxey)
            tel_rep.pack(side="left", **fxen)
            self.lab_tel_rep.pack(**fxey, ipady=2)
            ttk.Separator(self, orient="vertical").pack(side="left", fill="y")
        
        # info_dir.pack(side=tk.LEFT, **fxey)
        # ttk.Label(info_dir, image=self.img_['folder'], compound=tk.LEFT, textvariable=self.dir_info,
        #           width=40, padding=(2, 2)).pack(**fxey)   # side="left",

        ttk.Label(time_err, textvariable=self.err, width=11,
                  padding=(2, 2), anchor=tk.CENTER).pack(**fxey)   # side="left",
        time_err.pack(side=tk.LEFT, **fxen)

        ttk.Label(time_step, textvariable=self.time_i, width=11,
                  padding=(2, 2), anchor=tk.CENTER).pack(**fxey)
        if not bso_:
            time_step.pack(side=tk.LEFT, **fxen)
            self.set_icon_rep(self.img_['networkof'])
        ttk.Sizegrip(self).pack(side=tk.RIGHT, padx=3)
        # self.pack()
        self.set_icon(self.img_['networkof'])
        self.set_icon_gps(self.img_['networkof'])
        self.sboi = False                           # не показывать сбои линии

    def err_show(self, arg=None):
        """Скрыть сбои линии"""
        self.sboi = not self.sboi           

    def set_step(self, txt):
        """Период опроса линии"""
        self.time_i.set(txt)

    def set_err(self, txt):
        """Установка числа сбоев линии"""
        t = txt if self.sboi else ''
        self.err.set(t)

    # def set_dir(self, txt):
    #     """Установка пути к файлу"""
    #     self.dir_info.set(txt)
    #
    # def get_dir(self):                      # not used !
    #     """Получение пути к файлу"""
    #     return self.dir_info.get()
        
    def set_device(self, txt):
        """Информация о порте 485"""
        self.port_info.set(txt)

    def set_gps(self, txt):
        """Информация о порте gps"""
        self.gps_info.set(txt)

    def set_rep(self, txt):
        """Информация о порте репитера"""
        self.rep_info.set(txt)
        
    def set_icon(self, icon=None):
        im = icon if icon else self.img_['png']
        self.lab_tel.config(image=im)

    def set_icon_gps(self, icon=None):
        im = icon if icon else self.img_['png']
        self.lab_tel_gps.config(image=im)
        
    def set_icon_rep(self, icon=None):
        im = icon if icon else self.img_['png']
        self.lab_tel_rep.config(image=im)

    def config_tel_rep(self, st=1):
        im = self.img_['network1'] if st else self.img_['network3']
        self.lab_tel_rep.config(image=im)
