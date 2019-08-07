#!/usr/bin/env python
# -*- coding:utf-8 -*-

import tkinter as tk
import os.path
import pathlib
import sys
import configparser
import png
# import threading
import tkinter.messagebox as box

compiler = 'pyinstaller'
#compiler = 'cx_freeze'

COLOR = ('#c40373', '#e32322', '#ea621f', '#f18e1c', '#fdc60b', '#f4e500',
         '#8cbb26', '#008e5b', '#0696bb', '#2a71b0', '#444e99', '#552f6f')

cwddir = os.path.abspath('.')
path = pathlib.Path(cwddir)
         
config = configparser.ConfigParser()
file = path.joinpath('config.ini')

if not file.exists():
    box.showerror('Error!', 'Отсутствует или поврежден файл config.ini')
    sys.exit(0)
    
config.read(file, encoding='utf-8')


def write_config():
    """Сохранение файла сонфигурации"""
    with open(file, "w", encoding='utf-8') as config_file:
        config.write(config_file)


def rgb(arg):
    """Вернуть цвет по амплитуде как в ПУИ"""
    a = (0x14, 0x2C, 0x3E, 0x4E, 0x60, 0x72, 0x80, 0x90, 0xA0, 0xB6, 0xD0, 0xFF)   # темносиний ... темнокрасный
    for i,  j in enumerate(a):
        if arg <= j:
            return COLOR[11-i]      # COLOR[0..11] от т красного  до т синего
    return '#552f6f'

l = ['down_', 'up_', 'right', 'left', 'pui_', 'exit_','prompt', 'printer', 'pdf', 
     'visible', 'h1', 'h7', 'a_1', 'a', 'korabl1', 'pdf1', 'print1',
     'networkx', 'networkon', 'networkof', 'view', 'clock', 'opgl', 'png', 'networky',
     'network1', 'network3', 'folder', 'help', 'im16', 'stop2', 'start2',
     'gals', 'geooff', 'glason', 'glasoff', 'geoon', 'grid2', 'lauernogrid', 
     'mashtabarrow', 'off', 'on', 'osadka', 'new', 'open', 'sloion', 'timer',
     'book3', 'db', 'dbcopy', 'delete3', 'marker3', 'skrepka', 'saveas', 'sloi3',
     'com', 'list1', 'conv', 'spidveter', 'soundoff', 'soundon', 'coment_',
     'gaus2', 'nastr_', 'sinus', 'signal', 'nsignal', 'light_on', 'light_off',
     'linechart', 'candlestick']


def create_img():
    img_ = {}                                            # словарь для сохраненя изображении
    for im in l:
        img_[im] = tk.PhotoImage(data=eval('png.' + im))
    return img_  

if getattr(sys, 'frozen', False):
    if compiler == 'cx_freeze':
        bundle_dir = pathlib.Path(sys.executable).parent  # cx_Freese
    else:
        bundle_dir = sys._MEIPASS                         # PyInstaller
else:
    bundle_dir = path

imgdir = path.joinpath(bundle_dir, 'images')

def set_application_icons(application, ico):
    """Устанавливает значок приложения """
    icon32 = tk.PhotoImage(file=path.joinpath(imgdir, f"{ico}_32.png"))
    icon16 = tk.PhotoImage(file=path.joinpath(imgdir, f"{ico}_16.png"))
    application.tk.call("wm", "iconphoto", application, "-default", icon32,  icon16)


# def thread(func):
#     def execute(*args, **kwargs):
#         threading.Thread(target=func, args=args, kwargs=kwargs).start()
#     return execute
    