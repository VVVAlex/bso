#!/usr/bin/env python
# -*- coding:utf-8 -*-

import sys
import os.path
import functools
#import time
import tkinter.messagebox as box
from tkinter.filedialog import askopenfilename  # , asksaveasfilename, askdirectory
#from util import bundle_dir

prefix_dbt = 'dbt_'
prefix_gga = 'gll_'
prefix = 'conv_'
prefix_dg = 'dbtgll_'
cat = 'Конвертированные данные'
cat_nmea = 'Конвертированные данные NMEA'

#strtime = time.strptime('14.12.09 3:2:10', '%d.%m.%y %H:%M:%S')  # объект time#
#t = time.strftime("%d.%m %H:%M:%S", strtime) -> '14.12 03:02:10'

def ksum(msg):
    """Возврат к.с.(искл. или) два символа"""
    s = functools.reduce(lambda x1, x2: x1 ^ x2, map(ord, msg))
    sh = (s & 0xf0) >> 4
    sl = s & 0x0f
    if sh < 10:
        sh += 48
    else:
        sh += 55
    if sl < 10:
        sl += 48
    else:
        sl += 55
    return f'${msg}*{chr(sh)}{chr(sl)}'

def parse(s):
    d = s.split(',')        # all type str
    frmt = d[0]
    d = d[1 : ]
    try:
        try:
            glub = int(d[0]) / 10      # + float(d[8])     # глубина (d[8] - заглубление)
        except:
            glub = 0
        try:
            HMS = d[2].split()[-1]                # '23:29:01'
            t = HMS.split(':')
            TIME = f"{t[0]}{t[1]}{t[2]}.00"
        except:
            TIME = ''
        sh_ = d[3]
        if sh_:                                    # широта '00 00.000 N'
            sh_h = int(sh_[ : 3])
            sh = sh_[3 : -2]                             
            NS = sh_[-2 : ]                        # 'N' or 'S'
            sh = sh_h + round(float(sh) / 60, 8)   # float
            latitude = sh_[ : 2] + sh_[3 : 8]      # 'xxxx.xx'
        else:
            sh = 0
            NS, latitude = '', ''
        dl_ = d[4]
        if dl_:                                     # долгота '000 00.000 E'
            dl_h = int(dl_[:4])
            dl = dl_[4 : -2]                              
            EW = dl_[-2 : ]                          # 'W' or 'E'
            dl = dl_h + round(float(dl) / 60, 8)
            longitude = dl_[ : 3] + dl_[4 : 9]       # 'xxxxx.xx'
        else:
            dl = 0
            EW, longitude = '', ''
        data = f'{dl:.8f} {sh:.8f} {glub:.3f}'
        data_dbt = ksum(f'SD{frmt},,f,{glub:.1f},M,,F')
        #data_gga = ksum(f'GPGGA,{TIME},{latitude},{NS},{longitude},{EW},,,,,M,,M,,')
        data_gll = ksum(f'GPGLL,{latitude},{NS},{longitude},{EW},{TIME},A')
    except:
        data = ''
        data_dbt = ''
       # data_gga = ''
        data_gll = ''
    return (data, data_dbt, data_gll)

def sel(dir_):
    name = askopenfilename(initialdir=dir_)
    if name:
        return os.path.abspath(name)

def convert(dir_ = '.'):
    file = sel(dir_)
    if file:
        name = os.path.split(file)              # (path, name.ext)
        dirout = os.path.join(os.path.dirname(name[0]), cat)
        dirout_nmea = os.path.join(os.path.dirname(name[0]), cat_nmea)        
        convname = prefix + name[-1].split('.')[0] + ".txt"
        convname_dbt = prefix_dbt + name[-1].split('.')[0] + ".txt"
        convname_gga = prefix_gga + name[-1].split('.')[0] + ".txt"
        convname_dg = prefix_dg + name[-1].split('.')[0] + ".txt"
        conv_file = os.path.join(dirout, convname)
        conv_file_dbt = os.path.join(dirout_nmea, convname_dbt)
        conv_file_gga = os.path.join(dirout_nmea, convname_gga)
        conv_file_dg = os.path.join(dirout_nmea, convname_dg)
        if not os.path.exists(dirout):
            os.mkdir(dirout)
        if not os.path.exists(dirout_nmea):
            os.mkdir(dirout_nmea)
        with open(file, 'r') as f:
            head = f.readline()
            if head[:6] != 'format':                 #
                box.showerror('Error!', f'Не тот формат файла {file}')
                sys.exit(0)
            with open(conv_file, 'w') as f_out, open(conv_file_dbt, 'w') as f_out_dbt, open(conv_file_gga, 'w') as f_out_nmea, open(conv_file_dg, 'w') as f_out_dg:
                for s in f:
                    if s:
                        data = parse(s)
                        if data[0]:                       
                            f_out.write(data[0])
                            f_out.write('\n')
                        else:
                            print('skeep')
                        if data[1]:                       
                            f_out_dbt.write(data[1])
                            f_out_dbt.write('\n')
                            f_out_dg.write(data[1])
                            f_out_dg.write('\n')    
                        else:
                            print('skeep_dbt')
                        if data[2]:                       
                            f_out_nmea.write(data[2])
                            f_out_nmea.write('\n')
                            f_out_dg.write(data[2])
                            f_out_dg.write('\n')
                        else:
                            print('skeep_nmea')
#            print('done!')
            box.showinfo('', f'Созданы файлы:\n{conv_file},\n{conv_file_dbt},\n{conv_file_gga}\n{conv_file_dg}')
            return name

if __name__ == "__main__":
    import tkinter as tk
    import os
    root = tk.Tk()
    convert(os.curdir)
    root.destroy()