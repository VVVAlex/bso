#!/usr/bin/env python
# -*- coding:utf-8 -*-

import tkinter as tk
from tkinter import ttk
import tkinter.messagebox as box
from tkinter.filedialog import askopenfilename  # asksaveasfilename
import os, time
import pathlib
import shutil
import csv
import hashlib
import io
from collections import namedtuple
from tooltip import ToolTip
import canvas_show, pdf_
from util import imgdir, create_img, set_application_icons
from util import config, bakdir
from db_api import request_data_coment, request_data_all
from db_show import ViewMetka

try:
    v_len = config.getboolean('Verbose', 'viewlen')
except:
    v_len = 0


class App(ttk.Frame):
    """Основной класс"""
    def __init__(self, parent, title, galsname=None):
        super().__init__(parent)

        self.can_show = canvas_show.Fild(self)          # bso_=True
        self.can_show.pack()
        self.state_ = True
        self.parent = parent
        self.filename = None
        self.galsname = galsname
        self.img_ = create_img()
        self.parent.withdraw()
        parent.wm_title(title)
        parent.focus_force()
        frame = ttk.Frame(parent, padding=0)
        frame.pack(fill='both', expand='yes')
        # frame.pack(fill='x', expand='no')
        # self.rev_flag = False                            # True реверс включен
        self.frame = frame
        self.tbname = self.dbname = None
        self.viewData = None
        self.avtoscale = 1
        self.dir = '.'
        self.path = pathlib.Path(os.path.abspath('.'))
        self.veiwstate = 'disabled'
        self.portstate = 'normal'
        self.readstate = 'disabled'
        (self.h_bar, self.m_grid, self.view_len,
         self.m_dno, self.m_avto, self.m_hide) = (tk.IntVar(self.parent, 1), tk.IntVar(self.parent, 1),
                                                  tk.IntVar(self.parent, 1), tk.IntVar(self.parent, 0),
                                                  tk.IntVar(self.parent, 1), tk.IntVar(self.parent, 1))
        self.get_tmp_file()

    def get_tmp_file(self):
        """Получить временный файл"""
        cur_path = pathlib.Path('tmp_file')                           # имя файл
        if self.galsname:
            self.filename = cur_path.joinpath(bakdir, cur_path)       # файл обьединить с врем дир
            try:
                shutil.copyfile(self.galsname, bakdir)
            except IOError:
               self.filename = None  
        
    def run(self):
        """Начало"""
        self.tol_bar = Toolbar(self)     # панель инструментов
        self.tol_bar.pack(side='top', fill='x', expand='no')
        self.status_bar()                # строка состояния pack('bottom')
        self.header()                    # нижний информ. лабель pack('bottom')
        self.content()                   # нотебук
        self.bind__()
        if self.filename:                # сразу открыть файл
            self.view_mem()
            self.get_db_tb_name(self.galsname)
        self.parent.deiconify()
        self.parent.wait_visibility()

    def get_geometry_root(self):
        return (self.parent.geometry(), self.parent.winfo_rootx(),  self.parent.winfo_rooty())

    # def remove_pdf(self):
    #     """Удаление временного pdf файла"""
    #     try:
    #         self.can_show.unbind_()
    #     except Exception:
    #         pass
    #     try:
    #         os.remove('temp.pdf')
    #     except Exception:
    #         pass
    #     try:
    #         os.unlink('db_op.pdf')
    #     except Exception:
    #         pass

    def file_quit(self, event=None):
        """Выход"""
        # if self.okay_to_exit():
        # self.remove_pdf()
        # self.remove_gals_dubl(self.dir)
        try:
            self.can_show.unbind_()
        except Exception:
            pass
        self.parent.destroy()

#----------------- view memory PUI ----------------------------------------

    @staticmethod
    def rev_file(file):
        """Реверс файла и слив его в файлоподобный объект"""
        out = io.StringIO()
        with open(file) as f:
            head = f.readline()
            s_list = f.readlines()
            s_list.reverse()
            out.write(head)
            out.writelines(s_list)
        out.seek(0)
        del s_list
        return out

    def open_file(self, dir_='.'):
        """Вернуть путь к файлу"""
        ftypes = [('CSV files', '.csv'), ('All files', '*')]
        oname = askopenfilename(initialdir=dir_, filetypes=ftypes)
        if oname:
            self.get_db_tb_name(oname)
            return oname

    def get_db_tb_name(self, oname):
        """Опредилить tbname и dbname"""
        path = pathlib.Path(oname).parent.parent       # без имени файла и папки Исходные
        fname = pathlib.Path(oname).stem
        md5 = hashlib.md5(fname.encode('utf-8')).hexdigest()
        self.tbname = f'tb_{md5}'
        self.dbname = path.joinpath(path.name + '.db')
        self.tol_bar.btn['Оперативные отметки'].config(state='normal')

    def read_csv(self):
        """Читаем csv файл direct=True если просмотр с галса"""
        if self.rev_flag:                       # если  True(не передали флаг) то реверс
            out = self.rev_file(self.filename)
        else:
            try:
                out = open(self.filename)
            except OSError:
                out = []
        f_csv = (filds for filds in csv.DictReader(out))
        self.dir = pathlib.Path(self.filename).parent   
        return f_csv, out
    
    def canvas_data(self, f_csv, out):
        """Формируем из файла gl_N.csv данные в виде
        data=[шапка,
        ('format_','glub','ampl','lenth',timdata','shir','dolg','vs','kurs','vz','zg','ku','depth','rej',
            'frek','cht','m','m_man','color_mm','m_avto','g0','a0','g1','a1', ...),
        ('format_','glub','ampl','dt','shir','dolg','vs','kurs','vz','zg','ku','depth','rej',
            'frek','cht','m','','','g0','a0','l0',g1','a1','l1'...),...
        ]
        для просмотра
        """   
        num_line = 0
        data = []
        Row = namedtuple('Row', 'format_ glub ampl lenth timdata shir dolg \
                         vs kurs vz zg ku depth rej frek cnt m m_man color_mm m_avto all_data')
        # if f_csv:
            # self.data_h = []
        for line_dict in f_csv:
            num_line += 1
            zg = line_dict.get('zg', '')                 # осадка
            # self.stbar_z.set(f'{zg} м')
            try:
                glub = int(line_dict['glub'])            # глубина * (1 or 10)
            except Exception:
                glub = 0
            try:
                lenth = float(line_dict['lenth'])         # длительность
            except Exception:
                lenth = 0
            try:
                cnt = int(line_dict['cnt'])              # число стопов
                cn = cnt
                if cnt > 20:
                    cn = cnt
            except Exception:
                cn = 0
            try:
                timdata = time.strptime(line_dict['timdata'], '%d.%m.%y %H:%M:%S')  # объект time
            except Exception:
                timdata = ''
            format_ = line_dict.get('format_', '')
            ampl = line_dict.get('ampl', '')             # амплитуда
            # lenth = line_dict.get('lenth', '')           # длительность
            shir = line_dict.get('shir', '')             # широта
            dolg = line_dict.get('dolg', '')             # долгота
            vs = line_dict.get('vs', '')                 # скорость судна
            kurs = line_dict.get('kurs', '')             # курс
            m_man = line_dict.get('m_man', '')           # ручн. метка
            color_mm = line_dict.get('color_mm', '')     # цвет ручн. метки
            m_avto = line_dict.get('m_avto', '')         # авто метка (авто. метка) 
            vz = line_dict.get('vz', '')                 # скорость звука
            m = line_dict.get('m', '')                   # число кор. стопов
            ku = line_dict.get('ku', '')                 # порог
            depth = line_dict.get('depth', '')           # диапазон глубин
            rej = line_dict.get('rej', '')               # режим
            frek = line_dict.get('frek', '')             # частота 
            try:
                if not v_len:
                    all_data = [(int(line_dict[f'g{i}']), int(line_dict[f'a{i}']), float(line_dict[f'l{i}'])) for i in range(cn)]
                else:
                    all_data = [(int(line_dict[f'g{i}']), int(line_dict[f'a{i}']), 0) for i in range(cn)]
            except Exception:
                # raise
                all_data = []
            tupl = Row(format_, glub, ampl, lenth, timdata, shir, dolg, vs, kurs, vz, zg, ku,
                        depth, rej, frek, cnt, m, m_man, color_mm, m_avto, all_data)
            data.append(tupl)                             # for canvas_show self.can_show.run_()
            if not num_line % 50 :
                self.notebook.update()

        if out:
            out.close()
        return data  

# s = ['300', '122', '20.05.14 11:55:05', '', '', '', '', '', '', ''..., []]
# ['формат','глубина','амплитуда','длительность','день.месяц.год ч:м:с',' шир.','долг.','скорость','курс',
# 'скорость звука', 'заглубление', 'порог','диапазон','режим','частота','число стопов',
# 'коррел. число стопов','man_metka','цвет man_metka','avto_metka',
# [()..]] если есть иначе '', ''
# time.strptime('24.06.14 12:34:11','%d.%m.%y %H:%M:%S')

#-----------------------------------------------------------------------------

    def view_mem(self, arg=None):
        """Просмотр данных arg=None если запуск из просмотра лога"""
        # direct = True
        # self.parent.focus_force()
        self.rev_flag = True
        if arg:
            self.filename = self.open_file(self.dir)
            # direct = False
            self.rev_flag = False
        if not self.filename:
            return
        self.parent.focus_force()
        # self.notebook.lift()
        self.notebook.config(cursor='watch')
        f_csv, out = self.read_csv()
        # start = time.time()
        data = self.canvas_data(f_csv, out)     # > 4.1 сек
        # if direct:
        if self.rev_flag:
            if out:
                out.close()
            # os.unlink(self.filename)                 # удаляем из tmp
            # shutil.rmtree(bakdir)                    # удаляем tmp каталог
            self.filename = ''
        # end = time.time()
        # print(end - start)
        if data:
            if self.viewData is None:
                self.lab_start.pack_forget()
                del self.lab_start
                self.veiwstate = 'normal'                 # надо вызывать меню для
                self.tol_bar.btn['Печать'].config(state='normal')
                self.tol_bar.btn['Просмотр PDF'].config(state='normal')
                self.tol_bar.bar_right.pack(side='left', padx=40)
                self.can_show.run_(self.mainFild, data)    # metr     # canvas_show
                self.viewData = True
                self.parent.update()
                # self.can_show.bindcanv()
                self.can_show.canvw.bind("<Configure>", self.can_show.resize)
                # self.src_.focus()            # фокус на поле ввода
                # self.can_show.canvw.focus_set()       # чтобы убрать фокус с вкладки 1 экрана
                s = self.parent.geometry()  # дёргаю геометрию иначе при разворачивании
                                            # окна и обратном сворачивание не сохраняется
                                            # предыдущий размер ???
                l = s.split('+')[0].split('x')
                l[0] = str(int(l[0]) + 1)
                l[1] = str(int(l[1]) + 1)
                self.parent.geometry('x'.join(l))
            else:
                self.can_show.reconfig(data)
            name = self.get_path()[0]              # filename
            if name:
                self.stbar_file.set(f'Файл = {name}')
#            n_scr = self.get_maxscreen()
            self.stbar_scr.set('Число экранов = {n_scr}')
            self.stbar_avto.set('Масштаб = Авто')
            self.can_show.resize()
            self.parent.focus_force()
        else:
            box.showerror('?', f'Не прочитать файл {self.filename}!')
            self.can_show.delete_data()
        self.notebook.config(cursor='')

    def get_path(self):
        """Вернуть путь и имя файла с данными или None"""
        return self.filename, self.dir

    def get_v(self):
        """Вернуть скорость звука"""
        return self.stbar_v.get()

    def get_z(self):
        """Вернуть осадку"""
        return self.stbar_z.get()

#--------- print ----------------------------------------------------
    def print_pdf(self, event=None):
        self.get_pdf()

    def view_pdf(self, event=None):
        self.get_pdf(1)

    def get_pdf_data(self):
        """Получить данные для pdf"""
        src = self.can_show.get_src()                   # int номер экрана
        data = self.can_show.get_data()                 # данные или None  # canvas_show
        filename = self.get_path()[0]                   # имя файла с данными
        w = self.can_show.W                             # текущая ширина холста 768
        scale = self.can_show.get_scale()               # текущий масштаб
        return w, data, src, scale, filename

    def get_pdf(self, verbose=None):
        """Сразу печатаем (verbose=None) или запускаем Foxit (verbose=1)"""
        if self.viewData:
            pdf_.Pdf(self, verbose)

    def gethide_metka(self):
        """Вернуть нужно отображать метки и длительность в pdf или нет"""
        return (self.m_hide.get(), self.view_len.get())

#---------------hide------------------------------------------------
    def avto_on_off(self, arg=None):
        """Установиь сбросить автомасштаб"""
        if self.viewData:
            self.can_show._scal()
            if not self.avtoscale:
                self.m_avto.set(1)
                self.stbar_avto.set('Масштаб = Авто')
                self.tol_bar.btn['Автомасштаб'].config(image=self.img_['a'])
                ToolTip(self.tol_bar.btn['Автомасштаб'], msg='Автомасштаб')
            else:
                self.m_avto.set(0)
                self.stbar_avto.set('Масштаб = Ручной')
                self.tol_bar.btn['Автомасштаб'].config(image=self.img_['h1'])
                ToolTip(self.tol_bar.btn['Автомасштаб'], msg='Ручной масштаб')
            self.avtoscale = not self.avtoscale

    def op_db(self, arg=None):
        """Просмотр отметок в базе"""
        result = request_data_all(self.dbname, self.tbname)
        self.view_db = ViewMetka(self, result)
        self.view_db.show_tree()    # (№ int, timedata, shir, dolg, glub int, '"" or "A" or "coment" or "Диапазон..."')
        self.view_db.set_name_db(self.dbname)
        self.tol_bar.btn['Оперативные отметки'].config(state='disabled')
        
    def data_coment(self, num):
        """Получить коментарий из базы"""
        return request_data_coment(self.dbname, self.tbname, num)
        
    def state_db_norm(self, arg=None):
        """Удалить окно просмотра меток и разблокировать кнопку db"""
        self.tol_bar.btn['Оперативные отметки'].config(state='normal')
        self.view_db.destroy()
        

#--------------------------------- main fild -------------------------------------------

    def content(self):
        """Основное поле с вкладками"""
        logo_img = self.path.joinpath(imgdir, 'logo_navi.png')
        self.images = tk.PhotoImage(file=logo_img)
        widgetpanel = ttk.Notebook(self.frame, padding=1)   # panedzone
        widgetpanel.pack(side='left', fill='both', expand='yes')
        widgetpanel.enable_traversal()

        self.mainFild = ttk.Frame(widgetpanel)              # 1 panel
        self.mainFild.pack(padx=1, pady=1, )                  # expand = "yes", fill = "both"

        self.lab_start = tk.Label(self.mainFild, width=968, height=500,   # padding=(0,0),
                                  image=self.images)    # compound = "top",  anchor = "center    self.img_['korabl1']
        self.lab_start.pack()                                    # expand='yes', fill='both'

        widgetpanel.add(self.mainFild, text="Просмотр",
                        compound="left", padding=2, image=self.img_['prompt'])
        self.notebook = widgetpanel

#-----------------footer--------------------------------------- 

    def set_head(self, head_data):
        """Установка данных"""
        try:
            format_, ku, depth, rej, frek, cnt, m, v, zg = head_data
            # print(index, self.data_h[index])
            # print(ku, depth, rej, cnt)
        except IndexError:
            return
        d0 = {'L': 'МГ', 'M': 'СГ', 'H': 'БГ', 'B': 'Б6'}
        self.ku_var.set(ku)
        self.depth_var.set(d0.get(depth, ''))
        rj = 'Авто' if rej == 'S' else 'Ручной'
        self.format_var.set(format_)
        self.rej_var.set(rj)
        self.frek_var.set(f"{frek}кГц")
        self.stop_var.set(f"{m} / {cnt}")
        self.v_var.set(f'{v} м/с')
        self.stbar_z.set(f'{zg} м')
        
    def clr_var_h(self):
        """Очищаем данне"""
        self.format_var.set('')
        self.ku_var.set('')
        self.depth_var.set('')
        self.rej_var.set('')
        self.frek_var.set('')
        self.stop_var.set('')
        self.v_var.set('')
        self.stbar_z.set('')
    
    def header(self):
        """Поле с данными"""
        s = ttk.Style()
        (self.ku_var, self.depth_var, self.rej_var, self.frek_var,
         self.format_var, self.stop_var, self.v_var) = (tk.StringVar() for _ in range(7))
        fxen = dict(fill='x', expand='no')
        self.head = ttk.Frame(self.frame)
        self.head.pack(side='bottom', **fxen)
        font = ("Times", 12)
        # font = ("7 Segment", 12)
        # font = ("Digital-7 Mono", 18)
        bg = 'gray85'
        # foreground = 'black'                                #darkblue'
        fbey = dict(fill="both", expand="yes")
        s.configure('MH.TLabel', background=bg, anchor='center',
                    font=font, borderwidth=2, width='10', relief='groove')
        txt = ('Уровень / Длительность', 'Эхо', 'Усиление', 'Диапазон', 'Режим', 'Частота')   # Длительность
        t_vr_ = (self.can_show.ampvar, self.stop_var, self.ku_var, self.depth_var,
                 self.rej_var, self.frek_var)
        w_ = ('23', '7,', '10', '9', '7', '9')      # 23 to 9
        f = ttk.Frame(self.head)
        ttk.Label(f, text='Формуляр\n эхолота', width=10, font = ("Times", 11, 'bold')).pack()
        f.pack(side='left', fill='x', expand='yes')
        for text, w, t_vr in zip(txt, w_, t_vr_):
            f = ttk.Frame(self.head)
            f.pack(side='left', fill='x', expand='yes')
            ttk.Label(f, text=text, width=w).pack()
            ttk.Label(f, textvariable=t_vr, style='MH.TLabel').pack(**fbey)


#-------------------------statusbar----------------------------
    def status_bar(self):
        """Cтрока состояния"""
        self.numbersrc_ = tk.IntVar()
        fxen = dict(fill='x', expand='no')
        fxey = dict(fill='x', expand='yes')
        ttk.Separator(self.frame).pack(**fxen)
        sbar = ttk.Frame(self.frame)                    
        sbar.pack(side='bottom', **fxen)
        (self.stbar_scr, self.stbar_file, self.stbar_avto,
         self.stbar_v, self.stbar_z) = (tk.StringVar() for _ in range(5))
        rel = dict(padding=1, relief='sunken')
        infofile = ttk.Frame(sbar, **rel)
        infoscr = ttk.Frame(sbar, **rel)
        infoavto = ttk.Frame(sbar, **rel)        
        infofile.pack(side="left", **fxey)
        infoscr.pack(side="left", **fxen)
        infoavto.pack(side="left", **fxen)
        ttk.Sizegrip(sbar).pack(side='right', padx=3)
        ttk.Label(infofile, textvariable=self.stbar_file, width=20,
                  padding=(2, 0)).pack(side="left", **fxey)          # файл
        ttk.Label(infoscr, textvariable=self.stbar_scr, width=20,
                  padding=(2, 0)).pack(side="left", **fxey)          # число экран.

        ttk.Label(infoavto, text='Экран', width='8', anchor='center').pack(side='left')
        self.src_ = ttk.Entry(infoavto, textvariable=self.numbersrc_, width='8', font = ('tachoma','8'),
                             takefocus=1, justify='center')
        self.src_.bind("<Return>", self.can_show._enter)
        self.src_.pack(side='right')

    def bind__(self, arg=None):
        self.parent.bind("<Alt-F4>", self.file_quit)

class Toolbar(ttk.Frame):
    """Панель инструментов"""

    def __init__(self, master):
        super().__init__(master)
        self.master = master
        self.btn = {}
        self.toolbar = ttk.Frame(master.frame, padding='0')
        ttk.Separator(master.frame).pack(fill="x", expand="no")
        bar_left = ttk.Frame(self.toolbar, padding='0')
        self.bar_right = ttk.Frame(self.toolbar, padding='0')
        j = 0
        padding = (2, 2)
        img_ = master.img_
        for image_, tip, command in (
                (img_['exit_'], 'Выход', master.file_quit),
                (None, None, None),
                (img_['printer'], 'Печать', master.print_pdf),
                (img_['pdf'], 'Просмотр PDF', master.view_pdf),
                (None, None, None),
                (img_['open'], 'Просмотр памяти', lambda: master.view_mem(True)),
                (None, None, None)):
            j += 1
            try:
                if image_ is None:
                    ttk.Separator(bar_left, orien="vertical").grid(row=0, column=j,
                                                                   sticky="ns", padx=2, pady=2)
                else:
                    bt = ttk.Button(bar_left, style="TLabel", image=image_, compound="left",
                                    cursor="hand2", padding=padding,        # TLabel TButton Toolbutton
                                    width=0, command=command)
                    bt.grid(row=0, column=j, padx=0)
                    self.btn[tip] = bt
                    ToolTip(self.btn[tip], msg=tip)
            except tk.TclError as err:
                # print(f"e > {err}")
                pass
        self.btn['Печать'].config(state='disabled')
        self.btn['Просмотр PDF'].config(state='disabled')
        j = 0
        for image, tip_, command in (
                (None, None, None),
                (img_['sloion'], 'Все цели', master.can_show.one_ceil),
                (img_['candlestick'], 'Длительность видна', master.can_show.len_view),
                (img_['grid2'], 'Сетка вкл.', master.can_show.grid),
                (img_['light_off'], 'Подсветка дна', master.can_show.dno),
                (img_['geoon'], 'Скрыть метки', master.can_show.metka),
                (img_['a'], 'Автомасштаб', master.avto_on_off),
                (None, None, None),
                (img_['left'], 'Следующий экран', master.can_show.next),
                (img_['right'], 'Предыдущий экран', master.can_show.prev),
                (None, None, None),
                (img_['up_'], 'Увеличить масштаб', master.can_show.up),
                (img_['down_'], 'Уменьшить масштаб', master.can_show.down),
                (None, None, None),
                (img_['visible'], 'Вся память', master.can_show.full),
                (None, None, None),
                (img_['db'], 'Оперативные отметки', master.op_db),
                (None, None, None)):
            try:
                if image is None:
                    ttk.Separator(self.bar_right, orient="vertical").grid(row=0, column=j,
                                                                          sticky="ns", padx=2, pady=2)
                else:
                    bt2 = ttk.Button(self.bar_right, style="TLabel", image=image,     # Toolbutton
                                     compound="left", cursor="hand2", padding=padding,
                                     width=0, command=command)        # space=1,
                    bt2.grid(row=0, column=j)
                    self.btn[tip_] = bt2
                    ToolTip(self.btn[tip_], msg=tip_)
            except tk.TclError:
                # print(err)
                pass
            j += 1
        self.btn['Оперативные отметки'].config(state='disabled')
        bar_left.pack(side='left', fill='x', expand='no')
        self.bar_right.pack(side='left')

        imgname = master.path.joinpath(imgdir, 'korabl.gif')
        self.img_k = tk.PhotoImage(file=imgname)
        lab_k = ttk.Label(self.toolbar, image=self.img_k)  
        lab_k.pack(side='right', padx=6)
        self.bar_right.pack_forget()

        self.toolbar.pack(side='top', fill='x', expand='no')

    def config_btn(self, state='disabled'):
        """Запретить все кнопки в меню"""
        for i in self.btn:
            self.btn[i].config(state=state)
        if state == 'disabled':
            self.master.can_show.unbind_2()
            self.master.parent.resizable(False, False) 
        else: 
            self.master.can_show.bind_2()
            self.master.parent.resizable(True, True)
              

def main():
    import sys
    root = tk.Tk()
    file = sys.argv[1] if len(sys.argv) > 1 else None
    app = App(root, "Viewer", file)     # запуск просмотра из PUI
    app.run()
    root.protocol("WM_DELETE_WINDOW", app.file_quit)
    root.focus_force()
    set_application_icons(root, 'icon')     # imgdir
    root.mainloop()


if __name__ == "__main__":
    main()
