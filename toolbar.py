#!/usr/bin/env python
# -*- coding:utf-8 -*-

import time
import os
import pathlib
import subprocess
import tkinter as tk
import tkinter.messagebox as box
import dialog_ as dlg_
from tkinter import ttk
from tkinter import StringVar
from tooltip import ToolTip
from util import config, write_config


class Toolbar(ttk.Frame):
    """Панель инструментов"""

    def __init__(self, master, bso_=False):
        super().__init__(master)
        self.master = master
        self.bso__ = False            # toolbar как в ПУИ
        self.img_ = master.img_
        self.f1 = ttk.Frame(master)
        self.f2 = ttk.Frame(master)
        self.f1.pack(fill=tk.X)
        ttk.Separator(master).pack(fill=tk.X, pady=1)
        self.f2.pack(fill=tk.X)
        ttk.Separator(master).pack(fill=tk.X, pady=1)
        self.b = {}                   # контейнер для хранения виджетов

        self.enable_skale = False     # нельзя менять шкалу автоматом
        self.visible_time_metka_on = True
        ttk.Separator(self.f1).pack(fill=tk.X, padx=1)
        sep = [ttk.Separator(self.f1, orient=tk.VERTICAL) for _ in range(8)]
        i = 0
        seppk = dict(side=tk.LEFT, fill=tk.Y, padx=2)
        (self.varcb, self.varcbgps , self.num_metka, self.dir_info) = (tk.StringVar() for _ in range(4))
           
        bt1 = ttk.Button(self.f1, text="Выход  ", image=master.img_['exit_'], compound=tk.RIGHT,
                         width='6', cursor="hand2", style='Toolbutton', command=master.exit_)
        bt1.pack(side=tk.LEFT)
        sep[i].pack(**seppk)
        i += 1
        ttk.Label(self.f1, text="Haстройки").pack(side=tk.LEFT, padx=3)
        bt2 = ttk.Button(self.f1, image=self.img_['osadka'],
                         cursor="hand2", width='7', style='Toolbutton', command=master.zaglub_)
        bt2.pack(side=tk.LEFT)
        bt3 = ttk.Button(self.f1, image=self.img_['clock'],
                         cursor="hand2", width='13', style='Toolbutton', command=master.vzonav_)
        bt3.pack(side=tk.LEFT)

        self.f_ = ttk.Frame(self.f1)
        self.f_.pack(side=tk.LEFT)
        btvzv = ttk.Button(self.f_, image=self.img_['spidveter'],
                         cursor="hand2", width='7', style='Toolbutton', command=self.spid_)
        btvzv.pack(side=tk.LEFT)
        btnvolume = ttk.Button(self.f_, image=self.img_['soundoff'],
                         cursor="hand2", width='13', style='Toolbutton', command=self.off_vol)
        btnvolume.pack(side=tk.LEFT)
        btopgl = ttk.Button(self.f_, image=self.img_['opgl'],
                         cursor="hand2", width='13', style='Toolbutton', command=self.opgl_)
        btopgl.pack(side=tk.LEFT)

        sep[i].pack(**seppk)
        i += 1
        ttk.Label(self.f1, text="Эхограмма").pack(side=tk.LEFT, padx=3)
        btnall = ttk.Button(self.f1, image=self.img_['sloion'], style='Toolbutton',
                            cursor="hand2", command=master.clr)
        btnlen = ttk.Button(self.f1, image=self.img_['candlestick'], style='Toolbutton',
                            cursor="hand2", command=master.len_view)                    
        btnhidevline = ttk.Button(self.f1, image=self.img_['grid2'], style='Toolbutton',        #
                                  cursor="hand2", command=master.hide_hline)                    #
        btnmetki = ttk.Button(self.f1, image=self.img_['geoon'], style='Toolbutton',
                              state='disabled', cursor="hand2", command=master.hide_metki)
        btnrgb = ttk.Button(self.f1, image=self.img_['off'], style='Toolbutton',
                            cursor="hand2", command=master.color_ch_)
        ToolTip(bt2, msg='Осадка')
        ToolTip(btvzv, msg='Скорость звука')
        ToolTip(bt3, msg='Часовой пояс')
        ToolTip(btnvolume, msg='Звук выключен')
        ToolTip(btopgl, msg='Опасная глубина')
        ToolTip(btnall, msg='Все эхо')
        ToolTip(btnlen, msg='Длительность видна')                                               #
        ToolTip(btnhidevline, msg='Линии видны')
        ToolTip(btnmetki, msg='Метки видны')
        ToolTip(btnrgb, msg='Фон')
        self.b['btnlen'] = btnlen                                                               #
        self.b['btnall'] = btnall
        self.b['btnhidevline'] = btnhidevline
        self.b['btnmetki'] = btnmetki
        self.b['btnrgb'] = btnrgb
        self.b['btnvolume'] = btnvolume
        
        btnall.pack(side=tk.LEFT)
        btnlen.pack(side=tk.LEFT)                                                                #
        btnhidevline.pack(side=tk.LEFT)
        btnmetki.pack(side=tk.LEFT)
        btnrgb.pack(side=tk.LEFT)
        sep[i].pack(**seppk)
        i += 1
        ttk.Label(self.f1, text="Масштаб").pack(side=tk.LEFT, padx=3)
        btnscale = ttk.Button(self.f1, image=self.img_['h1'], style='Toolbutton',
                              cursor="hand2", compound=tk.RIGHT, command=self.off_scale)
        ToolTip(btnscale, msg='Ручная шкала')
        self.b['btnscale'] = btnscale
        btnscale.pack(side=tk.LEFT)
        sep[i].pack(**seppk)
        i += 1
        ttk.Label(self.f1, text="Оперативные отметки").pack(side=tk.LEFT, padx=3)
        b_db = ttk.Button(self.f1, textvariable=self.num_metka, image=self.img_['list1'], style='Toolbutton',
                          state='normal', cursor="hand2", command=master.opmetka_list)
        self.b['b_db'] = b_db
        self.num_metka.set(' ')  #
        bmman = ttk.Button(self.f1, image=self.img_['h7'], style='Toolbutton',
                           cursor="hand2", state='disabled', command=master.opmanual)
        self.b['bmman'] = bmman
        btnmetka = ttk.Button(self.f1, text='0.0 м', image=self.img_['timer'], style='Toolbutton',
                              cursor="hand2", state='disabled', compound=tk.LEFT, command=master.opavto)
        self.b['btnmetka'] = btnmetka
        btnametka_on = ttk.Button(self.f1, image=self.img_['glasoff'], style='Toolbutton',
                                  state='disabled', cursor="hand2", command=self.time_metka_on)
        ToolTip(btnametka_on, msg='Время скрыто')
        self.b['btnametka_on'] = btnametka_on        
        bmman.pack(side=tk.LEFT)
        btnmetka.pack(side=tk.LEFT)
        btnametka_on.pack(side=tk.LEFT)
        b_db.pack(side=tk.LEFT)
        i += 1
        sep[i].pack(**seppk)
        ttk.Label(self.f1, text='Просмотр').pack(side=tk.LEFT, padx=3)
        ttk.Button(self.f1, image=self.img_['visible'], style='Toolbutton',
                   cursor="hand2", command=master.runview_mem).pack(side=tk.LEFT)
        i += 1
        sep[i].pack(**seppk)
        ttk.Label(self.f1, text='Конвертор').pack(side=tk.LEFT, padx=3)
        ttk.Button(self.f1, image=self.img_['conv'], style='Toolbutton',
                   cursor="hand2", command=master.convt).pack(side=tk.LEFT)
        i += 1
        sep[i].pack(**seppk)        
        ttk.Button(self.f1, text='Справка', image=self.img_['help'], style='Toolbutton',
                   compound=tk.RIGHT, cursor="hand2", command=master.help).pack(side=tk.RIGHT)   # help_
        ToolTip(bmman, msg='Оперативная отметка')
        ToolTip(btnmetka, msg='Автоматические отметки')
        
#
        self.time_gl, self.num_gals, self.pr_name = StringVar(), StringVar(), StringVar()
        self.id_g = None
        self.id_rec = None
        self.flag_rec = False
        self.oldsec = 0
        self.tgals_min = 0
        self.tgals_hour = 0
        self.flag_gals = False
        # bg = 'gray35'
        # fg = 'orange'
        fg = 'black'
        bg = 'gray85'
        font = ("Times", 12)
        font2 = ("Arial", 10, 'bold')
        s = ttk.Style()
        s.configure('P.TLabel', background=bg, foreground=fg, anchor='center',
                    font=font, relief='groove')
        pr = ttk.Label(self.f2, text="Проект", anchor=tk.CENTER, width='9', compound=tk.RIGHT)
        pr.pack(side=tk.LEFT)
        bnew = ttk.Button(self.f2, image=self.img_['new'], style='Toolbutton',
                          cursor="hand2", command=self.new_prj)
        bnew.pack(side=tk.LEFT)
        ToolTip(bnew,  msg='Новый')
        bopen = ttk.Button(self.f2, image=self.img_['open'], style='Toolbutton',
                           cursor="hand2", command=self.open_prj)
        bopen.pack(side=tk.LEFT)
        ToolTip(bopen,  msg='Открыть')
        prj_name = ttk.Label(self.f2, textvariable=self.pr_name, style='P.TLabel', padding=(2, 2))
        prj_name.pack(side=tk.LEFT, fill=tk.X, padx=2)
        
        ttk.Separator(self.f2, orient=tk.VERTICAL).pack(**seppk)
        bgals = ttk.Button(self.f2, text="Галс    ", image=self.img_['gals'], style='Toolbutton',
                           cursor="hand2", width='6', compound=tk.RIGHT, command=self.gals_log)
        bgals.pack(side=tk.LEFT)
        l_name = ttk.Label(self.f2, textvariable=self.num_gals, style='P.TLabel', padding=(2, 2))
        l_name.pack(side=tk.LEFT, fill=tk.X, padx=2)
        ToolTip(l_name,  msg='Имя галса')
        ttk.Separator(self.f2, orient=tk.VERTICAL).pack(**seppk)
        
        btn = ttk.Button(self.f2, text=" ", image=self.img_['start2'], style='Toolbutton',
                         cursor="hand2", state='disabled', command=self.action_log)        # padding=(11,6,16,11),
        btn.pack(side=tk.LEFT)
        
        lab_rec = ttk.Label(self.f2, text='Rec', anchor=tk.CENTER, padding=(1, 2), font=font2,  # image=img_['record'],
            width=5, relief='groove', compound=tk.RIGHT)
        lab_rec.configure(foreground='')      # image=img_['record'] gray95
        lab_rec.pack(side=tk.LEFT, padx=4)
        ToolTip(lab_rec, msg_func=lambda: self.msgfunc(master), delay_show=0.2, delay_hide=3.5)
        ToolTip(btn, msg='Пауза')
        ttk.Separator(self.f2, orient="vertical").pack(side=tk.LEFT, fill=tk.Y, padx=4)

        ttk.Label(self.f2, text='Время галса').pack(side=tk.LEFT, padx=4)
        l_time = ttk.Label(self.f2, textvariable=self.time_gl, width='10', style='P.TLabel',
                           padding=(0, 2))
        l_time.pack(side=tk.LEFT)
        ToolTip(l_time,  msg='Продолжительность галса')
        ttk.Separator(self.f2, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=4)

        ttk.Button(self.f2, image=self.img_['folder'], style='Toolbutton',
                   command=self.open_dir_prj).pack(side=tk.LEFT)
        ttk.Label(self.f2, textvariable=self.dir_info,
                  width=40, padding=(2, 2)).pack(side=tk.LEFT, fill=tk.X, expand=True)

        ttk.Label(self.f2, image=self.img_['korabl1'], text='  ', compound=tk.RIGHT,
                  padding=(1,0)).pack(side=tk.RIGHT)
        self.b['lab_rec'] = lab_rec
        self.b['btn'] = btn
        self.b['bgals'] = bgals
        name = master.get_prj_name()
        if name == '.':
            self.pr_name.set(f"{' ':^19}")
        else:
            self.pr_name.set(f'{name:^{len(name)+4}}')
        self.num_gals.set(f"{' ':^19}")
        if bso_:
            self.bso_()

    def open_dir_prj(self):
        """Открыть директорию проектов в проводнике"""
        name = os.path.join(os.path.abspath('.'), 'Проекты')
        # name = pathlib.Path().joinpath(os.path.abspath('.'), 'Проекты')
        subprocess.run(['explorer', name])                     # 

    def set_dir(self, txt):
        """Установка пути к файлу"""
        self.dir_info.set(txt)

    def new_prj__(self, arg=None):
        if arg:
            path = pathlib.Path(arg)
            prj_name = path.name
            prj_path = path.joinpath(os.path.abspath('.'), 'Проекты')
            path_prj = path.joinpath(prj_path, prj_name)
            # if prj_name in (i.name for i in os.scandir(prj_path)):
            if prj_name in os.listdir(prj_path):
                box.showwarning('!', 'Проект с таким именем уже существует!')
                return
            self.pr_name.set(f'{prj_name:^{len(prj_name)+4}}')
            config.set('Dir', 'dirprj', f'{path_prj}')
            write_config()
            self.master.prepare_gals(str(path_prj))
            try:
                os.mkdir(path_prj)
                os.mkdir(path.joinpath(path_prj, 'Исходные данные'))                  # 'base_data'
                os.mkdir(path.joinpath(path_prj, 'Обработанные данные'))              # 'processed_data'
                os.mkdir(path.joinpath(path_prj, 'Конвертированные данные'))          # 'converted_data'
                os.mkdir(path.joinpath(path_prj, 'Конвертированные данные NMEA'))     # 'converted_nmea_data'
            except Exception:
                box.showerror('?', 'Ошибка создания проекта!')
        
    def new_prj(self):
        """Создать новый проект"""
        dlg_.get_str(self.master, "Ввод имени проекта", "Введите имя проекта", '', self.new_prj__)
        
    def open_prj(self):
        """Открыть проект"""
        name = self.master.opendir_gals()
        if name:
            self.stop_write_file()
            name = pathlib.Path(name).name
            self.pr_name.set(f'{name:^{len(name)+4}}')
            self.num_gals.set(f"{' ':^19}")

    @staticmethod
    def msgfunc(master):
        """Вернуть число строк записанных в файл"""
        n = '0' if master.numstr_var.get() == '' else master.numstr_var.get()
        msg = f'Записано {n} строк'
        return msg

    def tick_gals(self):
        """Время записи галса"""
        secs = time.time()
        if secs - self.oldsec >= 60.0:                          # 1 мин
            self.oldsec = secs
            if self.tgals_min >= 60:
                self.tgals_min = 0
                self.tgals_hour += 1
            self.time_gl.set(f"{self.tgals_hour:02d} : {self.tgals_min:02d}")
            self.tgals_min += 1
        self.id_g = self.master.after(5000, self.tick_gals)
         
    def lab_rec_blink(self):
        """Мигнуть надписью REC"""
        if self.flag_rec:
            self.b["lab_rec"].config(foreground='red')
        else:
            self.b["lab_rec"].config(foreground='gray95')
        self.flag_rec = not self.flag_rec
        self.id_rec = self.master.after(500, self.lab_rec_blink)

    def time_metka_on(self):
        """Обработчик кнопки показа времени на автометке"""
        if self.visible_time_metka_on:
            im = self.img_['glason']
            self.master.board.canv.move('timeametka', 0, 100)     # время на авт. метке
            msg = 'Время видно '
        else:
            im = self.img_['glasoff']
            self.master.board.canv.move('timeametka', 0, -100)    # время на авт. метке
            msg = 'Время скрыто'
        self.visible_time_metka_on = not self.visible_time_metka_on
        self.b['btnametka_on'].config(image=im)
        ToolTip(self.b['btnametka_on'], msg=msg)
            
    def action_log(self):
        """Обработчик кнопки Запись/Пауза"""
        if self.master.file_gals:
            if self.b["btn"].cget('text') == '.':
                self.stop_write_file()
            else: 
                self.b["btn"].config(text='.', image=self.img_['stop2'])
                ToolTip(self.b["btn"], msg='Запись')
                # self.flag_rec = True
                if self.id_rec is None:
                    self.lab_rec_blink()
                self.tick_gals()                                # старт время записи

    def stop_write_file(self):
        """Остановить запись в файл"""
        self.b["btn"].config(text=' ', image=self.img_['start2'])
        self.master.stringfile = 0
        ToolTip(self.b["btn"], msg='Пауза')
        if self.id_rec:
            self.master.after_cancel(self.id_rec)
            self.b["lab_rec"].config(foreground='')    # стоп
            self.id_rec = None
        if self.id_g:
            self.master.after_cancel(self.id_g) 
                
    def new_gals__(self, arg=None):
        """Смена галса"""
        if arg:
            self.stop_write_file()
            name_ = f"{arg:^{len(arg)+4}}" if len(arg) > 15 else f"{arg:^{15-len(arg)+4}}"
            self.num_gals.set(name_)
            name = f'{arg}.csv'
            if self.master.gals(name):
                self.time_gl.set("00 : 00")
                self.master.ch_state(('btnmetka', 'btnametka_on'), ('btn',))
                self.tgals_min = 0
                self.tgals_hour = 0
                self.flag_gals = True                               # True цикл в run_loop Fale то break
                self.master.clr_data()                              # Очистка поля
                self.master.new_avtom__(0)                          # Остановить автометки
                # self.master.timeravto(0)                            # Остановить автометки
                # self.b['btnmetka'].config(text='0.0 м')
                self.master.odl_arg_time = 0
                if self.bso__:
                    self.master.ch_state((), ('btnmetki',))
                    if not self.master.hide_metka:
                        self.master.ch_state((), ('bmman', 'btnmetka'))
                    self.master.run_loop()
            else:
                self.master.ch_state(('bmman', 'btnmetka', 'btn', 'btnametka_on'), ())

    def bso_(self):
        """Скрыть лишние кнопки"""
        self.f_.pack_forget()
        self.bso__ = True           # toolbar как в БСО

    def off_scale(self):
        """Шкала авто или мануал"""
        if not self.enable_skale:
            image = self.img_['a']
            msg = 'Автоматическая шкала'
        else:
            image = self.img_['h1']
            msg = 'Ручная шкала'
        ToolTip(self.b['btnscale'], msg=msg)
        self.b['btnscale'].configure(image=image)
        self.enable_skale = not self.enable_skale 
    
    def gals_log(self):
        """"Выбор галса"""
        dlg_.get_str(self.master, "Выбор галса", "Введите имя галса", '', self.new_gals__)

    def opgl_(self, *arg):
        """Обработчик кнопки ввода опасной глубины"""
        self.master.opgl_()

    def spid_(self, *arg):
        """Обработчик кнопки ввода скорости звука"""
        self.master.spid_()

    def off_vol(self, *arg):
        """Обработка кнопки вкл./выкл. звука"""
        if not self.master.off_volume:
            image=self.img_['soundon']
            ToolTip(self.b['btnvolume'], msg='Звук включен')
        else:
            image=self.img_['soundoff']
            ToolTip(self.b['btnvolume'], msg='Звук выключен')
        self.b['btnvolume'].configure(image=image)
        self.master.off_volume = not self.master.off_volume   
