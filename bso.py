#!/usr/bin/env python
# -*- coding:utf-8 -*-

__version__ = "1.4"
__author__ = 'Veresov Alex'
__email__ = 'lexa1st@mail.ru'

import tkinter as tk
import tkinter.messagebox as box
from tkinter import ttk
from tkinter.filedialog import askdirectory
import os, time, shutil
import pathlib
import threading
import queue
import show_bso
import csv
import tempfile
import hashlib
import array
from tooltip import ToolTip
import dialog_ as dlg_
from util import imgdir, set_application_icons, create_img, cwddir
from util import config, write_config
from port import RS232, Gps, port_exc
from toolbar import Toolbar
from status_bar import Footer
from head import Head
from info_bar import InfoBar
from canvas_bso import CanvasT
from preferens import Window
import sqlite3
from db_api import LookupDict, update_table, request_data_coment, \
        request_data_all, del_table, create_table, insert_table
from db_show import ViewMetka

import help_

vesible = config.getboolean('Verbose', 'vesible')
trace = print if vesible else lambda *x: None

bso_ = True         # работет как БСО

req = LookupDict({})
        
#########################################################


class App(ttk.Frame):
    """Класс приложения"""

    def __init__(self, root, sizeX, sizeY, title):
        super().__init__(root)
        # self.pack(expand='no', fill='both')
        self.root = root
        self.state_ = False
        root.wm_title(title)
        root.focus_force()
        self.img_ = create_img()
        self.pack(expand=True, fill=tk.BOTH)
        set_application_icons(root, 'ico')          # imgdir
        self.path = pathlib.Path(cwddir)
        path_ = self.path.joinpath('Проекты')           # каталог для файлов конвертора  'project'
        if not path_.exists():
            os.mkdir(path_)
        self.b = {}                                     # контейнер для виджетов
        self.dir_cvt = path_
        self._zona = config.getfloat('System', 'vzona')
        self._opgl = 0
        self.mb = config.getboolean('Amplituda', 'mb')  # 1 - RGB
        # fxen = dict(fill=tk.X, expand=False)
        (self.glub_var, self.stop_var, self.time_var, self.numstr_var, self.ampl_var, self.skale_var,
            self.porog_var, self.frek_var) = (tk.StringVar() for _ in range(8))

        self.tol_bar = Toolbar(self, bso_)             # объект tolbar
        self.tol_bar.pack(fill=tk.X, expand=False)
        # ttk.Separator(self).pack(**fxen)

        self.head = Head(self)                         # объект этикетки head
        self.head.pack(fill=tk.X, expand=False)

        self.stbar = Footer(self, bso_)                # объект строки состояния
        self.stbar.pack(side=tk.BOTTOM, fill=tk.X)

        self.sep = ttk.Separator(self)
        self.sep.pack(side=tk.BOTTOM, fill=tk.X, pady=1)
        self.frame_upr = ttk.Frame(self)                # фрейм для управления
        self.frame_upr.pack(side=tk.BOTTOM, fill=tk.X)

        self.infobar = InfoBar(self)                    # объект Info
        self.infobar.pack(side=tk.BOTTOM, fill=tk.X)

        self.board = CanvasT(self, sizeX, sizeY, bso_)  # объект CanvasT
        self.board.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.ser = RS232(trace)                         # объект Serial
        self.gser = Gps(trace)                          # объект Gps
        self.gser.tty.baudrate = 4800
        self.gser.tty.timeout = 0.01
        self._zg = config.getfloat('System', 'zagl')
        self.head.set_z(self.zg)                    # zg - свойство
        self.d0 = {'L': 'МГ', 'M': 'СГ', 'H': 'БГ', 'C': 'B8', 'D': 'B10', 'B': 'Б6'}
        self.fil_ametka = 'DodgerBlue2'
        self.stringfile = 0                         # число строк записанных в файл
        self.txt_opmetka = 0                        # счётчик оперативных отметок ручн.
        self.y_g = 0
        # self.error = 0                              # занулить ошибки при старте проги
        self.file_gals = None                       # нет файла для записи галса
        self.man_metkawriteok = (False, False)
        self.avto_metkawriteok = False
        self.yold_ = 0.0                            # для перемещен текста врем. меток
        self.hide_metka = False                     # Показывать метки
        self.hide_grid = False                      # Показывать гор. линии
        self.gl_0 = 0
        self.d_gps = None
        self.last_d_gps = None
        self.tavto_ = None
        self.tbname = None
        self.view_db = None
        # self.count_gps = 0
        self.ida = None
        self.ida_ = True
        self.last_sec = -1
        self.count_tmetka = 1
        self.vz_last = self.rej_last = 0
        self.diap_last = self.old_depth = 'МГ'
        self.helpDialog = None
        self.color_ch = True
        self.t_pausa = 0
        self.y_metka = self.board.y_top
        if bso_:
            self.gui_main()
            self.sep.pack_forget()

    def gui_main(self):
        self.b.update(self.tol_bar.b)

        self.head.set_format(('DBT', 'DBK', 'DBS')[config.getint('Preferens', 'd')])
        self.numstr_var.set('')

        # scl = config.getboolean('Scale', 'amplscl')
        # if scl:
        #     self.board.sclrbar.pack(side=tk.RIGHT, fill=tk.Y, expand=False)  # показать шкалу
        yscroll = config.getboolean('Scale', 'yscroll')
        if yscroll:
            self.board.sbar.pack(side=tk.LEFT, fill=tk.Y)                    # показать полосу прокрутки
        self.board.canv.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)        # пакуем здесь
        self.open_port()
        self.init_board()
        path = pathlib.Path(config.get('Dir', 'dirprj'))
        # path = os.path.abspath(path)
        if path.exists():
            self.dbname = path.joinpath(path.name + '.db')                    # path + '.db'
            self.tol_bar.set_dir(str(path) + '   ...Галс не выбран')
        else:
            self.tol_bar.set_dir('Проект не выбран!')
            self.tol_bar.pr_name.set('  ?!  ')
            self.b['bgals'].config(state='disabled')
        
    def init_board(self):
        """Создание нового полотна и очередей"""
        self.visible = False                      # Показать все точки
        self.visible_len = False                  # Показать длительность
        self.board.create_fild()
        self.root.update_idletasks()
        maxlen = int(self.max_width_canv() - self.board.x_right - 2)
        self.board.create_list_deque(maxlen)
        self.bind_()
        
    def open_port(self):
        """Открытие портов"""
        port_pui = config.get('Port', 'port_pui')
        baudrate_pui = config.getint('Port', 'baudrate_pui')
        port_gps = config.get('Port', 'port_gps')
        baudrate_gps = config.getint('Port', 'baudrate_gps')
        try:
            self.ser.open_port(port_pui)
            self.ser.tty.baudrate = baudrate_pui
        except port_exc:
            self.stbar.set_device(f'Не открыть порт {port_pui}')
            self.stbar.set_icon(self.img_['networky'])
        if self.ser.is_open():
            self.stbar.set_device(self.ser.get_port_info())
            self.stbar.set_icon(self.img_['networkon'])
        try:
            self.gser.open_port(port_gps)
            self.gser.tty.baudrate = baudrate_gps
        except port_exc:
            self.stbar.set_gps(f'Не открыть порт {port_gps}')          
            self.stbar.set_icon_gps(self.img_['networky'])
        if self.gser.is_open():
            self.stbar.set_gps(self.gser.get_port_info('НАП СНС'))
            self.stbar.set_icon_gps(self.img_['networkon'])
            
    def runview_mem(self, arg=None):
        """Запуск просмотра Viewer"""
        bakfile = None
        if self.file_gals:
            fd, bakfile = tempfile.mkstemp()
            try:
                shutil.copyfile(self.file_gals, bakfile)
                os.close(fd)
            except IOError:
                bakfile = None
        top = tk.Toplevel()
        title = 'БСО просмотр логов' if bso_ else 'ПУИ просмотр логов'
        app_view = show_bso.App(top, title=title, filename=bakfile, galsname=self.file_gals)
        app_view.run()
        top.protocol("WM_DELETE_WINDOW", app_view.file_quit)
        top.iconbitmap(self.path.joinpath(imgdir, 'bookmark.ico'))
        top.focus_force()

    def clr_data(self):
        """Если ПУИ перейти в Ожидание"""
        self.init_board()
        if not bso_:
            # self.root.go_nel()
            pass
       
#======= callback =============#
         
    def new_avtom__(self, arg=None):
        """Запуск автометок"""
        if arg is None:
            return
        if self.ida:
            self.root.after_cancel(self.ida)      # остановить цикл   
        if arg == 0.0:
            # self.odl_arg_time = arg
            self.b['btnmetka'].config(text='0.0 м')
            return
        else:
            # self.odl_arg_time = arg
            self.b['btnmetka'].config(text=f'{arg:0.1f} м')
            self.b['btnametka_on'].config(state='normal')
            self.count_tmetka = 1
            self.timeravto(arg)                   # запустить цикл
         
    def new_vzona__(self, arg=None):
        if arg is not None:
            self.zona = arg
        
#============== metki ==========================================
            
    def ch_state(self, dis=(), nor=()):
        """Изменение state кнопок (list 'disabled'), (list 'normal')"""
        for obj in dis:
            self.b[obj].state(['disabled', 'selected'])
        for obj in nor:
            self.b[obj].state(['!disabled', '!selected'])
                
    def opavto(self, arg=None):
        """Обработчик кнопки постановки авто. метки"""
        dlg_.get_float(self, 'Автоинтервал', 'Введите интервал в мин.', self.new_avtom__,
                       initial=0.0, minimum=0.5, maximum=100)
                                        
    def timeravto(self, t):
        """Тик для автометок 1 секунда"""
        # if t:
        sec = time.localtime(time.time())[5]
        if sec != self.last_sec:
            self.last_sec = sec             # 1 сек
            self.count_tmetka -= 1
            if self.count_tmetka == 0:
                if self.ida_:
                    self.draw_t()
                self.count_tmetka = t * 60
        self.ida = self.root.after(100, lambda: self.timeravto(t))
        # else:
        #     if self.ida:
        #         self.root.after_cancel(self.ida)
        
    def review_db(self, geom):
        """Обновить окно меток"""
        self.view_db.destroy()      # withdraw()
        self.opmetka_list(geom)
        
    def state_db_norm(self, arg=None):
        """Удалить окно просмотра меток и разблокировать кнопку db"""
        # self.b['b_db'].config(state='normal')         #
        self.view_db.destroy()      # withdraw()
        self.view_db = None         #
        
    def opmetka_list(self, geom=None):
        """"Обработчик кнопки просмотр BD"""
        try:
            result = request_data_all(self.dbname, self.tbname)
        except Exception:       # as er
            # print(er)
            return
        if self.view_db:
            self.view_db.destroy()
        self.view_db = ViewMetka(self, result, geom)
        self.view_db.show_tree()    #
        self.view_db.set_name_db(self.dbname)
        # self.b['b_db'].config(state='disabled')           #
        
    def data_coment(self, num):
        """Получить коментарий из базы"""
        return request_data_coment(self.dbname, self.tbname, num)
        
    def save_new_coment(self, num, txt):
        """Сохранить коментарий в базе"""
        update_table(self.dbname, self.tbname, num, txt)      
  
    def decorate_metka(*d_arg):
        """Декоратор функции"""
        def my_decorator(func):
            def wrapped(self, *f_arg):
                if self.hide_metka:
                    for tag in d_arg:
                        self.board.canv.move(tag, 0, 100)
                func(self, *f_arg)
                if self.hide_metka:
                    for tag in d_arg:
                        self.board.canv.move(tag, 0, -100)
            return wrapped
        return my_decorator

    @decorate_metka('', 'mman_td')
    def opmanual(self, arg=None):
        """Обработчик кнопки постановки ручной метки"""
        if not self.tol_bar.flag_gals and bso_:
            return                      # если галс не выбран то не ставим отметку
        color, tag = ("spring green", 'mman_td') if arg else ("red", 'mman_t')
        x = self.board.x0 - 3
        self.board.canv.create_line(x, self.board.y_top + 1, x,
                                    self.y_metka, fill=color, tag='mmetka')
        self.txt_opmetka += 1
        self.board.canv.create_text(x, self.board.y_top - 7 + self.yold_, text=self.txt_opmetka, anchor='center',
                                    font=('Helvetica', 8), fill=color, tag=tag)
        # Y = -100 if self.tol_bar.visible_time_metka_on else 0
        # self.board.canv.create_text(x+6, self.board.y_top+27+self.yold_+Y, text=self.gl_0, anchor=tk.CENTER,
        #                             angle=90, font=('Helvetica', 8), fill=self.fil_ametka, tag='mman_t_glub')
        self.man_metkawriteok = (True, False) if color == "red" else (True, True)
        req.num = self.txt_opmetka
        self.get_data_db()
        insert_table(self.dbname, self.tbname, req)
        if self.view_db:                                    #
            geom = self.view_db.geometry().split('+')
            self.review_db(geom)
        if self.hide_metka:
            self.board.canv.delete('mmetka')
        
    def del_metka_man(self):
        """Удаление ручных и авто отметок при смене галса"""
        for tag in ('mmetka', 'mman_t', 'mman_td', 'ametka', 'tametka', 'point', 'point_g', 'glub', 'timeametka'):     # 'mman_t_glub',
            self.board.canv.delete(tag)
        self.txt_opmetka = 0

    @decorate_metka('tametka', 'timeametka')
    def draw_t(self, arg=None):
        """Рисуем временные автоматич. метки"""
        x = self.board.x0 - 3
        if self.d_gps is None:
            text = time.strftime('%H:%M:%S')
        else:
            text = self.d_gps[0].split()[-1]
        self.txt_opmetka += 1
        Y = -100 if self.tol_bar.visible_time_metka_on else 0
        if not self.hide_metka:
            self.board.canv.create_line(x, self.board.y_top, x, self.y_metka, fill=self.fil_ametka,
                                        tag='ametka')
        self.board.canv.create_text(x, self.board.y_top - 7 + self.yold_, text=self.txt_opmetka, anchor=tk.CENTER,
                                    font=('Helvetica', 8), fill=self.fil_ametka, tag='tametka')
        self.board.canv.create_text(x - 6, self.board.y_top + 27 + self.yold_ + Y, text=text, anchor=tk.CENTER,
                                    angle=90, font=('Helvetica', 8), fill=self.fil_ametka, tag='timeametka')

        # self.board.canv.create_text(x+6, self.board.y_top+27+self.yold_+Y, text=self.gl_0, anchor=tk.CENTER,
        #                             angle=90, font=('Helvetica', 8), fill=self.fil_ametka, tag='timeametka')
        self.avto_metkawriteok = True
        self.get_data_db()
        req.num = self.txt_opmetka
        req.coment = 'A'
        insert_table(self.dbname, self.tbname, req)
        if self.view_db:
            geom = self.view_db.geometry().split('+')
            self.review_db(geom)

    def hide_metki(self):
        """Показать, скрыть метки"""
        if self.hide_metka:
            self.board.move_metkai_hide(hide=False)
            image = self.img_['geoon']
            ToolTip(self.b['btnmetki'], msg='Метки видны')
            if self.tol_bar.flag_gals:
                self.ch_state((), ('bmman', 'btnmetka'))
        else:
            self.board.move_metkai_hide(hide=True)
            image = self.img_['geooff']
            ToolTip(self.b['btnmetki'], msg='Метки скрыты')
            self.ch_state(('bmman', 'btnmetka'), ())
        self.b['btnmetki'].configure(image=image)
        self.hide_metka = not self.hide_metka
        
    def hide_hline(self, arg=None):
        """Показать, скрыть гор. линии поля"""
        if self.hide_grid:
            self.board.move_grid(2700, 0)
            image = self.img_['grid2']
            ToolTip(self.b['btnhidevline'], msg='Линии видны')
        else:
            self.board.move_grid(-2700, 0)
            image = self.img_['lauernogrid']
            ToolTip(self.b['btnhidevline'], msg='Линии скрыты')
        self.b['btnhidevline'].configure(image=image)
        self.hide_grid = not self.hide_grid
           
#----------------------------------------------------------------------------------------------#
        
    def ch_diap(self, *arg):
        """Вызов при смене диапазона"""
        t1 = time.time()
        if t1 - self.t_pausa > 5:                           # ставить отметку не чаще чем 5 сек.
            self.t_pausa = t1
            arg = self.infobar.diap_var.get()
            if arg != self.diap_last and arg:               # не ставить если не изменился диапазон
                if self.diap_last:
                    if self.tbname and self.txt_opmetka:    # не ставить если небыло меток
                        self.opmanual("green")
                        if self.tol_bar.id_rec:
                            txt = f"Диапазон {self.infobar.diap_var.get()}"
                            num = self.txt_opmetka
                            self.save_new_coment(num, txt)
                self.diap_last = arg       

    def pref_form(self, D, z):
        """Возврат результата из формы 'DBT.., z(заглубл.) если есть изменения'"""
        self.zg = z                                         # изменение заглубл.
        self.head.set_format(D)
    
    @property
    def zona(self):
        """Временная зона"""
        return self._zona

    @zona.setter
    def zona(self, value):
        self._zona = value
        self.head.set_utc(t=True)
        config.set('System', 'vzona', f'{value}')
        write_config()

    @property
    def zg(self):
        """Заглубление"""
        return self._zg

    @zg.setter
    def zg(self, value):
        """Изменение заглубления"""
        self._zg = value
        self.head.set_z(value)
        config.set('System', 'zagl', f'{value}')
        write_config()

    def gals(self, name):
        """Выбор галса"""
        path = pathlib.Path(config.get('Dir', 'dirprj'))
        dir_gals = path.joinpath('Исходные данные')           # каталог галсов 'base_data'
        # if name in (i.name for i in os.scandir(dir_gals)):
        if name in os.listdir(dir_gals):
            if not box.askyesno('!', 'Файл с таким именем уже существует!\n Переписать файл?'):
                return
        self.file_gals = path.joinpath('Исходные данные', name)      # имя файла данных 'base_data'
        self.tol_bar.set_dir(str(self.file_gals))
        head = ['format_', 'glub', 'ampl', 'lenth', 'timdata', 'shir', 'dolg', 'vs', 'kurs',
                'vz', 'zg', 'ku', 'depth', 'rej', 'frek', 'cnt', 'm', 'm_man', 'color_mm', 'm_avto']
        for i in range(20):
            head.append(f'g{i}')
            head.append(f'a{i}')
            head.append(f'l{i}')
        with open(self.file_gals, 'w', newline='') as f:  # пишем в файл шапку  a!
            f_csv = csv.writer(f)
            f_csv.writerow(head)

        fname = pathlib.Path(name).stem
        md5 = hashlib.md5(fname.encode('utf-8')).hexdigest()
        # md5 = hashlib.md5(os.path.splitext(name)[0].encode('utf-8')).hexdigest()
        self.tbname = f'tb_{md5}'   # "tb_" префикс т.к. имя не может начмнаться с цмфры
        try:
            create_table(self.dbname, self.tbname)   # создать таблицу и если надо базу
        except sqlite3.OperationalError as err:
            if str(err) == f'table {self.tbname} already exists':
                del_table(self.dbname, self.tbname)
            else:
                box.showerror('!', f'Ошидка базы данных!\n{str(err)}')
        req.num = 0
        self.del_metka_man()
        return True
        
    @staticmethod
    def get_prj_name():
        return pathlib.Path(config.get('Dir', 'dirprj')).name
        # return os.path.basename(config.get('Dir', 'dirprj'))
            
    def opendir_gals(self):
        """Открыть существующий проект"""
        path = pathlib.Path(config.get('Dir', 'dirprj')).parent
        # path = config.get('Dir', 'dirprj')
        # path = os.path.dirname(path)
        name = askdirectory(initialdir=path)
        if name:
            # dir_ = os.path.abspath(name)
            self.prepare_gals(name)
            self.tol_bar.set_dir(name + '   ...Галc не выбран')
            return name 

    def prepare_gals(self, dir):
        config.set('Dir', 'dirprj', dir)
        write_config()
        path = pathlib.Path(dir)
        self.dbname = path.joinpath(path.name + '.db')
        # self.dbname = os.path.join(dir, os.path.split(dir)[-1] + '.db')   # dir + '.db'
        # self.ch_state(('btn', 'b_db'), ())            #
        self.ch_state(('btn',), ())
        self.tol_bar.num_gals.set(f"{' ':^19}")
        self.tol_bar.flag_gals = False
        self.b['bgals'].config(state='normal')          
                
    def vzonav_(self):
        """Обработка кнопки врем. зона"""
        ini = config.getfloat('System', 'vzona')
        dlg_.get_float(self.root, 'Часовой пояс', 'Введите часовой пояс', self.new_vzona__,
                       initial=ini, minimum=-12, maximum=14)
            
    def zaglub_(self):
        """Обработка кнопки осадки"""
        Window(self)

######################## Work ############################

    def color_ch_(self, arg=None):
        """Обработчик ккнопки смены фона"""
        if self.color_ch:
            bg = 'beige'          # '#eee'
            fil = 'darkblue'
            image = self.img_['on']
        else:
            bg = 'gray22'         # '#444'
            fil = 'orange3'
            image = self.img_['off']
        self.b['btnrgb'].configure(image=image)
        self.color_ch = not self.color_ch
        self.board.reconfig()
        self.board.canv.config(background=bg)
        self.board.canv.itemconfigure('fild_t', fill=fil)
        self.board.canv.itemconfigure('ametka', fill=self.fil_ametka)
        self.board.canv.itemconfigure('tametka', fill=self.fil_ametka)

########################## Start Wait #########################

    def write_data(self, data):
        """
        Пишем данные в файл
        (b'${or %},work,rej,depth,notused,ku,vh,vl,ksh,ksl,\r\n')
        (b'! or ?, #')
        (b'$,depth,ku,m,cnt,gl_0h,gl_0l,am_0h,am_0l,glh,gll,amh,aml,...,\r\n')
        '$GPRMC,123519.xxx,A,4807.038x,N,01131.000x,E,022.4,084.4,230394,003.1,W*6A\n'
        '      ,    time  , , latitude, , logitude , ,spid ,track, data ,degrees,    '
        """
        if self.b["btn"].cget('text') == '.' and data:
            # self.b['bgals'].state(['disabled', 'selected'])         # откл кнопки галс
            if bso_:
                vz = int.from_bytes(data[6:8], 'big')               # скорость звука
                frek = '25' if data[0] == 0x25 else '50'            # частота
                rej = 'S' if data[2] == 0x53 else 'R'               # режим
                data = data[15:-2]
            else:
                vz = self.head.vz_var.get()[:-3]     ################ убрать м/с
                frek = '25' if self.frek_var.get() == '25кГц' else '50'
                rej = 'S' if self.infobar.rej_var.get() == 'Авто' else 'R'
            depth = chr(data[0])                                    # диапазон глубин
            ku = int(chr(data[1]), 16)                              # порог
            m = data[2]                                             # корелир. стопы
            glub = int.from_bytes(data[4:6], 'big')
            glub += self.zg * 10 if glub else 0                       # self.zg -> float
            glub = int(glub)
            #ampl = data[6] if self.mb else data[7]  # amplful = int.from_bytes(data[6:8], 'big')
            ampl = data[6]          # цвет
            # lenth = data[7]         # длительность импульса
            lenth = self.cal_len(data[7])
            # lenth = self.cal_len(data[7], self.d0[depth])
            # print(data[7], lenth)
            m_avto =  m_man = color_mm = ''   # авто метка, ручн.метка, цвет ручной метки
            format_ = self.head.format_var.get()                     # формат
            if self.d_gps is None:                # если нет GPS 
                gps1 = gps2 = gps3 = gps4 = ''
                gps0 = time.strftime('%d.%m.%y %H:%M:%S')
            else:
                # time, shir, dolg, speed, kurs
                gps0, gps1, gps2, gps3, gps4 = (self.d_gps[i] for i in range(5)) 
            if self.man_metkawriteok[0]:
                m_man = self.txt_opmetka
                color_mm = "spring green" if self.man_metkawriteok[1] else "red"
            if self.avto_metkawriteok:
                m_avto = self.txt_opmetka           # авто метка
            cnt = data[3]                           # стопы
            zg = self.zg                            # осадка
# формат, глубина, амплитуда, длительность, объект дата время, широта, долгота, скорость, курс, скорость звука, осадка, порог,
# диап. глубин, режим, частота, число стопов, число кор. стопов, ручн. метка, цвет ручн. метки , авто метка.
            file_list = [format_, glub, ampl, lenth, gps0, gps1, gps2, gps3, gps4,
                         vz, zg, ku, depth, rej, frek, cnt, m, m_man, color_mm, m_avto]
            if cnt:
                st_d = []
                data = data[8 : ]
                if cnt > 20:
                    cn = 20            # если > 20 то except т.к. матрица = 20
                else :
                    cn = cnt
                for i in range(0, cn*4, 4):
                    gd = int.from_bytes(data[i : i + 2], 'big')
                    gd += self.zg * 10 if gd else 0
                    gd = int(gd)
                    # ad = data[i+2] if self.mb else data[i+3]  # ad = int.from_bytes(data[i+2:i+4], 'big')
                    ad = data[i + 2]
                    # ld = data[i + 3]
                    # ld = self.cal_len(data[i + 3], self.d0[depth])
                    ld = self.cal_len(data[i + 3])
                    st_d.append(gd)
                    st_d.append(ad)
                    st_d.append(ld)
                file_list.extend(st_d)
            with open(self.file_gals, 'a', newline='') as f:
                f_csv = csv.writer(f)
                f_csv.writerow(file_list)   
            self.stringfile += 1
            self.numstr_var.set(f'{self.stringfile:=05d}')     # число строк зап. в файл
        self.man_metkawriteok = (False, False)
        self.avto_metkawriteok = False

    def bind_(self):
        """Привязки событий"""
        self.root.bind("<Up>", self.board.up)
        self.root.bind("<Down>", self.board.down)
        self.root.bind("<Home>", self.board.home)
        self.root.bind("<End>", self.board.en)
        self.root.bind("<Alt-F4>", self.exit_)
#        self.root.bind('<MouseWheel>', self.scroll)
        self.board.canv.bind("<Configure>", self.board.size_canv)
        self.root.bind("<Control-Alt-e>", self.stbar.err_show)
        self.root.bind("<Return>", lambda: None)

    def max_width_canv(self):
        """Возвращает максимально возможную ширину холста"""
        screen = self.root.winfo_screenwidth()
        labl = self.board.colorbar.winfo_width()
        sbar = self.board.sbar.winfo_width()
        return screen - labl - sbar

    def clr(self):
        """Тригер показ всех точек или одна цель""" 
        if self.visible:
            self.board.show_data_zip(on_eco=True)
            image = self.img_['sloion']
            ToolTip(self.b['btnall'], msg='Все эхо')
        else:
            self.board.canv.delete('point')
            image = self.img_['sloi3']
            ToolTip(self.b['btnall'], msg='Одно эхо')
            # self.board.canv.itemconfigure('point_g', fill='black')     # 'green3'
        self.b['btnall'].config(image=image)
        self.visible = not self.visible
        self.board.reconfig()

    def len_view(self):                                                         #
        """Тригер показ длительности целей"""
        if self.visible_len:
            self.board.show_data_zip(on_eco=True)
            image = self.img_['candlestick']
            ToolTip(self.b['btnlen'], msg='Длительность видна')
        else:
            self.board.canv.delete('point')
            image = self.img_['linechart']
            ToolTip(self.b['btnlen'], msg='Длительность  скрыта')
        self.b['btnlen'].config(image=image)
        self.visible_len = not self.visible_len
        self.board.reconfig()

#=================================================================

    def blink(self):
        """Мигнуть телевизорами порта"""
        self.stbar.lab_tel.config(image=self.img_['network1'])
        self.root.after(200, lambda: self.stbar.lab_tel.config(image=self.img_['network3']))
        
    def blink_g(self):
        """Мигнуть телевизорами порта"""
        self.stbar.lab_tel_gps.config(image=self.img_['network1'])
        self.root.after(200, lambda: self.stbar.lab_tel_gps.config(image=self.img_['network3']))

    def set_local_time(self):
        """Установка машинного времени"""
        s = ttk.Style()
        s.configure('H.TLabel', foreground='#2754aa')   # синий
        t = time.strftime('%d.%m.%y %H:%M:%S')
        self.head.set_utc(False)
        self.head.set_t(t)

    def gps_data(self, data):
        """Получение данных из GPS
        '$GPRMC,123519.xxx,A,4807.038x,N,01131.000x,E,022.4,084.4,230394,003.1,W*6A\n'"""
        s = ttk.Style()
        self.d_gps = None
        data = data.split(',')          # type list
        self.blink_g()
        try:
            s_ = data[3].split('.')
            d_ = data[5].split('.')
            sh = f"{s_[0][:-2]} {s_[0][-2:]}.{s_[1][:3]} {data[4]}"     # {0xB0:c} °
            d = f"{d_[0][:-2]} {d_[0][-2:]}.{d_[1][:3]} {data[6]}"
        except Exception:
            sh = f"xx xx.xxx x"
            d = f"xxx xx.xxx x"
        try:
            str_struct = time.strptime(data[1].split('.')[0] + data[9], "%H%M%S%d%m%y")
            tsek = time.mktime(str_struct)
            tsek += self.zona*3600
            str_struct = time.localtime(tsek)
            t = time.strftime("%d.%m.%y %H:%M:%S", str_struct)
        except Exception:
            t = "xx.xx.xx xx:xx:xx"
        try:
            vs = f"{float(data[7]):=04.1f}"         # ! 05.1f
            k = f"{float(data[8]):=05.1f}"
        except Exception:
            vs = k = ''
        s.configure('H.TLabel', foreground='black')
        self.head.set_(sh, d, vs, k, t, True)
        # self.head.labelTime.config(foreground='green3')
        self.d_gps = (t, sh, d, vs, k)
                      
    def get_data_db(self):
        """Получить данные для базы"""
        if self.d_gps is None:
            t, sh_, d_ = time.strftime('%d.%m.%y %H:%M:%S'), '', ''
        else:
            t, sh, d = self.d_gps[0], self.d_gps[1], self.d_gps[2]
            sh__ = sh.split()
            d__ = d.split()
            sh_ = f"{sh__[0]}{0xB0:c} {sh__[1]}{0xB4:c} {sh__[2]}"
            d_ = f"{d__[0]}{0xB0:c} {d__[1]}{0xB4:c} {d__[2]}"
        req.timedata, req.shirota,  req.dolgota = t, sh_, d_
        req.glubina = f'{self.gl_0} м'
        req.coment = ''

    def update_scale(self):
        """Установка шкалы по глубине"""
        if not self.data_point:
            return
        # x = self.data_point[0]
        x = self.data_point[0] / 10
        up = (20, 40, 100, 200, 400, 800, 1000, 2000, 4000, 4500)
        down = (0, 16, 35, 75, 190, 350, 750, 950, 1900, 3900)
        if x > up[self.board.i]:
            self.board.up()
        elif x < down[self.board.i]:
            self.board.down()

    def work(self, data):
        """data = bytes"""
        # len(data)=105
        if bso_:
            vz = int.from_bytes(data[6 : 8], 'big')            # скорость звука
            self.infobar.vz_var.set(vz)                        # for trace
            self.head.set_v(vz)
            rej = 'Авто' if data[2] == 0x53 else 'Ручной'      # режим
            self.infobar.rej_var.set(f"{rej}")
            frek = '25 кГц' if data[0] == 0x25 else '50 кГц'   # частота
            self.frek_var.set(f"{frek}")
            self.parse_data(data[15 : -2])

        if self.data_point[0] > 0:
            # self.y_metka = self.board.y_top + self.data_point[0] * self.board.px / self.board.k + 1
            self.y_metka = self.board.y_top + self.data_point[0] / 10 * self.board.px / self.board.k + 1
        else:
            self.y_metka = self.board.y_top
        self.board.update_data_deque()
        if self.tol_bar.enable_skale:
            self.update_scale()                # изменить шкалу !
        self.board.show_point()                # в canvast
        self.board.del_widht_canvas()          # удалить всё за холстом

    def getmsg(self, que):
        """Поточная функция чтения ППУ"""
        while self.tol_bar.flag_gals:
            msg = self.ser.read_all()       # byte or None
            if msg:
                que.put(msg)                # ждём пока очередь будет пуста

    def getmsg_g(self, que_gp):
        """Поточная функция чтения НСП"""
        while self.tol_bar.flag_gals:
            msg = self.gser.get_msg()       # str or None
            if msg:
                que_gp.put(msg)               # ждём пока очередь будет пуста
      
    def run_loop(self):
        """
        Работа в режиме просмотра и возможной записи в лог.
        (b'${or%},work,rej,depth,notused,ku,vh,vl,ksh,ksl,\r\n')
        (b'! or ?, #')
        (b'$,depth,ku,m,cnt,gl_0h,gl_0l,am_0h,am_0l,glh,gll,amh,aml,...,\r\n')
        """
        # Вызов при выборе галса (start)
        # s = ttk.Style()
        self.init_board()    # очистить все очереди, иначе при reconfig() появяться цели от старого галса
        if not self.ser.is_open():          # нет открытого порта
            self.b["btn"].state(['disabled', 'selected'])
            return
        self.ser.clear_port()                   # очистка порта
        que = queue.Queue(1)
        if self.gser.is_open():
            que_g = queue.Queue(1)
            thread_g = threading.Thread(target=self.getmsg_g, args=(que_g,))       # daemon=True
            thread_g.start()
        thread_d = threading.Thread(target=self.getmsg, args=(que,))
        thread_d.start()
        self.timer = True
        self.local = False
        # self.timer_g = True
        self.not_data_g()
        while 1:
            if not self.tol_bar.flag_gals:      # exit loop
                break
            if self.gser.is_open():
                try:
                    data_g = que_g.get_nowait()
                except queue.Empty:
                    data_g = None
                    if self.timer_g:
                        self.timer_g = False
                        tg = threading.Timer(3.0, self.not_data_g)
                        tg.start() 
                if data_g:
                    if not self.timer_g:
                        tg.cancel()
                        self.timer_g = True
                        self.local = True
                    self.gps_data(data_g)
                if not self.local:
                    self.set_local_time()       # локальное время
                    self.d_gps = None
            else:
                # s.configure('H.TLabel', foreground='#2754aa')   # синий
                self.set_local_time()
            self.root.update()
            try:
                data = que.get_nowait()          # не ждём
            except queue.Empty:
                data = None
                if self.timer:
                    self.timer = False
                    t = threading.Timer(9.5, self.not_data)
                    t.start()       
            if data:
                if not self.timer:
                    t.cancel()
                    self.timer = True
                self.work(data)
                self.write_data(data)           # если надо то пишем в файл
                self.board.clr_error()          # убераем надпись Нет данных!
                self.ch_state((), ('bmman', 'btnmetka', 'btnametka_on'))
                self.blink()
                self.root.update()
                self.ida_ = True
        if self.gser.is_open():
            thread_g.join()         #
        thread_d.join()             #

    def not_data(self):
        """Вызов при отсутствии данных в линии"""
        self.timer = True
        self.stbar.set_icon(self.img_['networkx'])
        self.board.create_error()        # Выводим на холст Нет данных
        self.ch_state(('bmman', 'btnmetka', 'btnametka_on'), ())
        self.ida_ = False

    def not_data_g(self):
        """Вызов при отсутствии данных в линии GPS"""
        # s = ttk.Style()
        self.timer_g = True
        self.local = False
        # s.configure('H.TLabel', foreground='#2754aa')   # синий
        self.set_local_time()

    def parse_data(self, data):
        """
        Разбор данных глубин и амплитуд
        (b'depth,ku,m,cnt,gl_0h,gl_0l,am_0h,am_0l,glh,gll,amh,aml,...glh,gll,amh,aml')
        """
        # data_point = []
        # data_ampl = []                                    # 1+cnt глубин и 1+cnt (амплитуд, длительностей)
        # data_len = []
        data_point = array.array('H')                       # float 'f' 4 bytes 'B' 1 bytes
        data_ampl = array.array('B')                        # 1 + cnt глубин, амплттуд, длительностей
        data_len = array.array('B')
        if data:
            cnt = data[3]                                   # число принятых стопов
            m = data[2]                                     # число коррелир. стопов
            ku = int(chr(data[1]), 16)                      # порог
            depth = self.d0[chr(data[0])]                   # диапазон глубин
            self.depth = depth
            if depth != self.old_depth or not self.infobar.diap_var.get():
                self.infobar.diap_var.set(f"{depth}")
                self.old_depth = depth 
            self.porog_var.set(f"{ku}")
            self.stop_var.set(f" {m}  из  {cnt} ")
            glub = int.from_bytes(data[4:6], 'big')
            if glub:
                gl_0 = glub / 10 + self.zg
                data_point.append(glub + int(self.zg * 10))     # в дециметрах
            else:
                gl_0 = 0
                data_point.append(0)
            self.glub_var.set(f'{glub / 10:5.1f} м') if glub > 0 else self.glub_var.set('')
            self.board.view_glub(gl_0, self._opgl)            # вывод лгубины на холст
            # data_point.append(gl_0)                         # основной стоп
            # ampl = data[6] if self.mb else data[7]  amplful = int.from_bytes(data[6:8], 'big')
            ampl = data[6] 
            lenth = data[7]
            bg = self.board.rgbc(ampl * 7)  if ampl else 'gray85'        ## ~
            self.infobar.lab_a_l.config(background=bg)
            # lenth = self.cal_len(data[7], depth)
            # lenth = lenth if lenth else '  -'
            # lenth = data[7]
            # data_ampl.append((ampl, lenth))                 # основной стоп
            data_ampl.append(ampl)                 # основной стоп
            data_len.append(lenth)                 # основной стоп
            a = ampl if ampl else ''
            l = str(self.cal_len(lenth)) + ' м' if lenth else ''    #
            self.ampl_var.set(f'{a:3} \\ {l:5}')             # вывод амплитуды и длит. в лабель 
            foreground='black' if m else '#2754aa'           # синий
            self.infobar.lab_am_ln[1].config(foreground=foreground)
#            self.vmeter(ampl)
            datas = data[8 : ]                               # данные с матрицы
            if cnt > 20:
                 cnt = 20
            for i in range(0, cnt * 4, 4):
                glubs = int.from_bytes(datas[i : i + 2], 'big')
                if glubs:
                    # gl = glubs / 10.0 + self.zg 
                    data_point.append(glubs + int(self.zg * 10))
                else:
                    data_point.append(0)
                # data_point.append(gl)
                ampl2 = datas[i + 2]
                # lenth2 = self.cal_len(datas[i + 3], depth)    # в метрах
                lenth2 = datas[i + 3]                        # в дециметрах
                data_ampl.append(ampl2)
                data_len.append(lenth2)
            self.gl_0 = round(gl_0, 1)                       # глубина глобально
        self.data_point = data_point
        self.data_ampl = data_ampl
        self.data_len = data_len

    def cal_len(self, cod):
        cod = cod * 1.5 / 100
        # print(depth, type(depth))
        if self.depth == 'МГ': n = 4
        elif self.depth == 'СГ': n = 32
        elif self.depth == 'БГ': n = 256
        elif self.depth == 'Б6': n = 256     # !
        else:
            n = 0    
        return cod * n

#========================================================

    def convt(self, arg=None):
        """Конвертировать в формат ..."""
        import conv_csv
        dir__ = conv_csv.convert(self.dir_cvt)
        self.dir_cvt = dir__

    def help(self, event=None):
        """Окно справки"""
        if self.helpDialog is None:
            self.helpDialog = help_.Window(self, bso_)
        else:
            self.helpDialog.deiconify()
            
    def quitter(self):
        """Закрыть сокеты и убить окно"""
        if self.ser.is_open():
            self.ser.close_port()
        if self.gser.is_open():
            self.gser.close_port()
        main_thread = threading.main_thread()
        for t in threading.enumerate():
            if t is main_thread:
                continue
            t.join()
        try:
            self.root.destroy()
        except Exception:
            pass

    def exit_(self, arg=None):
        """Обработчик меню Exit"""
        if self.okay_to_exit():
            # sys.stderr = open('err.log', 'a')   #
            self.root.withdraw()
            self.tol_bar.t = 0
            self.tol_bar.flag_gals = False
            self.after(500, self.quitter)

    def okay_to_exit(self):
        """Подтверждение выхода"""
        reply = box.askokcancel("Выход", "Закончить работу программы?", parent=self.root)
        if reply is False:
            return False
        return True

# import logging
# logging.basicConfig(
        # filename = "bso.log",
        # format = "%(asctime)s %(message)s", # %(levelname)-10s 
        # #level = logging.DEBUG
        # level = logging.ERROR
# )
# logging.debug('start app')