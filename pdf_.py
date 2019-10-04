#!/usr/bin/env python
# -*- coding:utf-8 -*-

import os.path, time, locale
import pathlib
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, landscape  #letter
from reportlab.pdfbase import pdfmetrics, ttfonts
from util import imgdir, rgb, bakdir

#  система координат x0, y0 левый нижний угол x1, y1 правый верхний угол

class Pdf:
    """Создание и печать pdf документа"""
    # w=768, data=None, src=None, scale = None, filename=None, verbose=None
    def __init__(self, master, verbose):
        # [Row(format_, glub, ampl, timdata, shir, dolg, vs, kurs, m_man, color_mm_, m_avto, all_data)...]
        self.master = master            # show_bso
        self.w, self.data, self.scr, self.scale, self.name = self.master.get_pdf_data()
        self.W = 768.0              # слева на право
        self.H = 450                # снизу вверх                   ## 400 !!!
        self.dx = 30                # слева
        self.dy = 90                # снизу
        self.stic = 7               # засечка на осях
        self.dl = 15                # удление надписий от осей
        self.k = self.W / self.w
        # self.list_scale = [(0, 2), (1, 1), (2, 0.2), (3, 0.1), (4, 0.05), (5, 0.02), (6, 0.01), (7, 4.0/600), (8, 0.005), (9, 0.004)]
        self.list_scale = [(0, 2.0), (1, 1.0), (2, 0.4), (3, 0.2), (4, 0.1), (5, 0.05),
                           (6, 0.04), (7, 0.02), (8, 0.01), (9, 4.0/600), (10, 0.005), (11, 0.004)]
        myFontObject = ttfonts.TTFont('Arial', 'arial.ttf')
        pdfmetrics.registerFont(myFontObject)
        self.dir = '.'
        cur_path = pathlib.Path('temp.pdf')
        self.tmp_name = cur_path.joinpath(bakdir, cur_path)
        if self.data:
            # name = os.path.join(bakdir, 'temp.pdf')
            # self.c = canvas.Canvas("temp.pdf", pagesize=landscape(A4))  # файл "temp.pdf"
                                                                          # в текущем каталоге
            self.c = canvas.Canvas(f"{self.tmp_name}", pagesize=landscape(A4))
            self.asix()
            self.grid()
            self.c.setFillColor('darkblue')
            self.c.drawString(self.dx + self.W + self.dl, self.dy + self.H - 5, "0")
            self.data_pdf()
            self.pasteimg()
            self.run()
            self.go(verbose)

    def pasteimg(self):
        """Рисуем кораблик и логотип"""
        file = os.path.join(imgdir, 'korabl.gif')
        self.c.drawInlineImage(file, self.W, self.dy // 2 - 20, 48, 24)    # 5

    def data_pdf(self):
        """Рисуем данные в масштабе, масштаб как и в просмоторщике
        'глубина','амплитуда','%d.%m.%y %H:%M:%S','широта','долгота',
        'метка ручн', 'метка txt(avto)', [all].
        """
        W, H, dx, dy = self.W, self.H, self.dx, self.dy
        y = 10  # смещение гор. надписи относит. верха оси X
        hide_met, view_len = self.master.gethide_metka()
        dat = [i.glub / 1.0 for i in self.data]           # глубина  [1]       .glub
#        glub = [i[2] for i in self.data]                 # амплитуда  [2]     .ampl
        dat_all = None
        try:
            dat_all = [g.all_data for g in self.data]     # [[(),(),...],[(), (),...],...]  .all_data [-1]
        except Exception:
            pass
        man_met = [i.m_man for i in self.data]            # ручн. метка           .m_man  [8]
        color_mm = [i.color_mm for i in self.data]        # цвет ручн. метки      .color_mm []
        avt_met = [i.m_avto for i in self.data]           # авт.. метка           .m_avto  [10]
        txt = [i.timdata for i in self.data]              # объект времени        .timdata  [3]
        # scal = ([5, 10, 15, 20], [10, 20, 30, 40], [50, 100, 150, 200], [100, 200, 300, 400],
        #         [200, 400, 600, 800], [500, 1000, 1500, 2000], [1000, 2000, 3000, 4000],
        #         [1500, 3000, 4500, 6000], [2000, 4000, 6000, 8000], [2500, 5000, 7500, 10000])
        scal = ([5, 10, 15, 20], [10, 20, 30, 40], [25, 50, 75, 100], [50, 100, 150, 200], [100, 200, 300, 400],
                [200, 400, 600, 800], [250, 500, 750, 1000], [500, 1000, 1500, 2000], [1000, 2000, 3000, 4000],
                [1500, 3000, 4500, 6000], [2000, 4000, 6000, 8000], [2500, 5000, 7500, 10000])
        j, n = self.list_scale[self.scale] if self.scale else self.list_scale[0]
        self.c.saveState()
        self.c.setDash([])
        self.c.setFont('Helvetica', 10)
        self.XY_dat(scal[j])
        self.c.restoreState()
        # self.k = self.k * 2     #
        for i in range(self.w):
            if i >= len(self.data):
                break  # если данных меньше чем w  то будет except
            if not self.master.can_show.flag_on_point:          # если показ всех целей
                if dat_all[i]:                                  # [(), (),...]
                    for gl in dat_all[i]:                       # проход по всем (глубинам, амплитудам) можно сменить цвет
                        if i != 0:
                            if gl[0] / 1.0 <= scal[j][-1] * 10: # 100000 подрезка выпадающих за низ холста
                                color = rgb(gl[1])
                                self.c.setFillColor(color)
                                # self.c.setStrokeColor(color)
                                if not view_len:
                                    self.c.circle(dx + W - i * self.k - 1, dy + H - round(gl[0] * n) * H / 400,
                                                0.8, stroke=0, fill=1)
                                else:
                                    ln = round(gl[-1] * 10 * n) * H / 400
                                    Yi = H - round(gl[0] * n * H / 400)
                                    lnn = Yi if ln > Yi else ln
                                    self.c.rect(dx + W - i * self.k - 1, dy + Yi,                      # 450/400 = 1.125
                                                1, 1 - lnn, stroke=0, fill=1)
            else:                             # показ одной цели
                if dat[i]:                    # 10km
                    if dat[i] <= 100000:      # выкидываю > 10км, чтобы не вылезало за ось снизу
                        #color1 = rgb(glub[i])
                        #color1 = rgb(dat_all[i][0][1])
                        color1 = '#444'                     #
                        self.c.setFillColor(color1)
                        # self.c.setStrokeColor(color1)
                        self.c.circle(dx + W - i * self.k - 1, dy + H - round(dat[i] * n) * H / 400,      #
                                      0.80, stroke=0, fill=1)
            self.c.saveState()
            self.c.setDash([])
            self.c.setFont('Helvetica', 10)
            if dat[i] != 0:
                Y = dy + H - round(dat[i] * n) * H / 400
                if Y < dy:
                    Y = dy
            else:
                #Y = dy
                Y = dy + H
            numa = avt_met[i].strip()
            if numa and hide_met:             # авто метка
                self.c.setFillColor('blue')
                self.c.setStrokeColor('blue')
                self.c.setLineWidth(0.25)
                self.c.line(dx + W - i * self.k, Y , dx + W - i * self.k, dy + H + 5)    # avto_metka
                self.c.translate(dx + W - i * self.k - 6, dy + y + H + 15)
                self.c.drawCentredString(5, -15, f'{numa}')
                self.c.setFillColor('blue')
                self.c.setStrokeColor('blue')
                self.c.drawCentredString(5, 0, self.txt_time(txt[i]))
            num = man_met[i].strip()
            if num and hide_met:              # ручная метка
                color_ = color_mm[i]                # "red" or "green"
                if color_ == 'spring green':        # 00ff7f
                    color_ = 'green'
                self.c.setFillColor(color_)
                self.c.setStrokeColor(color_)
                self.c.setLineWidth(0.5)
                self.c.line(dx + W - i * self.k, Y, dx + self.W - i * self.k, dy + H + 5)    # man_metka
                self.c.translate(dx + W - i * self.k - 6, dy + y + H)
                self.c.drawCentredString(5, 0, f'{num}')
            self.c.restoreState()
        self.c.setFillColor('#777')
        self.c.setFont('Arial', 11)
        self.c.drawString(dx * 1.2, dy // 2 - 12, self.info())    # 2

    @staticmethod
    def txt_time(t):
        """Возвращает отформатированное время"""
        return time.strftime('%H:%M', t)

    def XY_dat(self, y_scal):
        """Подпись по оси Y и X"""
        W, H, dx, dy, dl = self.W, self.H, self.dx, self.dy, self.dl
        x_string = []
        d_y = 3
        self.c.drawString(dx + W + dl, dy + H * 3 // 4 - d_y, str(y_scal[0]))         # Y
        self.c.drawString(dx + W + dl, dy + H // 2 - d_y, str(y_scal[1]))
        self.c.drawString(dx + W + dl, dy + H // 4 - d_y, str(y_scal[2]))
        self.c.drawString(dx + W + dl, dy - d_y, str(y_scal[3]))
        for i, j, x in ((0, 0, 0), (self.w // 4, 1, W // 4), (self.w // 2, 2, W // 2),
                        (self.w * 3 // 4, 3, W * 3 // 4), (self.w - 1, 4, W - 1)):
            try:
                s = time.strftime("%d.%m %H:%M", self.data[int(i)].timdata)     # .timdata [3]
                x_string.append(s)
            except IndexError:
                x_string.append('')
            self.c.drawCentredString(dx + W - x, dy - dl - 2, x_string[j])         # X

    def asix(self):
        """Рисуем оси"""
        W, H, dx, dy = self.W, self.H, self.dx, self.dy
        self.c.setLineWidth(2.0)
        self.c.line(dx + W, dy,dx + self.W, dy + H)                    # Y
        self.c.line(dx, dy + H, dx + self.W, dy + H)                   # X  с верху
        self.c.line(dx, dy, dx + self.W, dy)                           # X_ с низу
        for i in [0, H // 4, H // 2, H * 3 // 4, H]:
            self.c.line(dx + W, dy + i, dx + W + self.stic, dy + i)
        for i in [0, W // 4, W // 2, W * 3 // 4, W]:
            self.c.line(dx + i, dy, dx + i, dy - self.stic)

    def grid(self):
        """Рисуем сетку"""
        W, H, dx, dy = self.W, self.H, self.dx, self.dy
        self.c.setLineWidth(0.5)
        self.c.setDash([1, 2])
        self.c.grid([dx, W // 4 + dx, W // 2 + dx, W * 3 // 4 + dx,
                     W + dx], [dy, H // 4 + dy, H // 2 + dy, H * 3 // 4 + dy, H + dy])

    def info(self):
        """Формируем строку info"""
        if self.scr is None:
            self.scr = '*'
        # st = time.ctime(time.time())
        locale.setlocale(locale.LC_ALL, "Russian_Russia.1251")
        # s = "%A %d %B %Y %H:%M:%S"
        s = "%d %B %Y %H:%M:%S"
        st = time.strftime(s)
        istr = f"Файл = {self.name},  экран = {self.scr},  {st}"                                                            
        return istr

    def run(self):
        """Сохранить pdf файл на диск"""
        self.c.showPage()
        self.c.save()

    # @staticmethod
    # def go_(verbose):
    #     """FRportable.exe -filename то откывает документ,
    #     -/p -filename то сразу печать"""
    #     import subprocess
    #     #file = os.path.join(bundle_dir, 'frp.exe')  ## если frp.exe включать в сборку (смотри bso_5.spec)
    #     file = os.path.abspath(os.path.join('.', 'frp.exe'))  # иначе
    #     name = 'temp.pdf'
    #     subprocess.Popen(f'{file} {name}') if verbose \
    #         else subprocess.Popen(f'{file} /p {name}')
    # subprocess.run(['explorer', 'csyntax.pdf'])

    def go(self, verbose):
        command = 'open' if verbose else 'print'
        try:
            # os.startfile('temp.pdf', command)
            # cur_path = pathlib.Path('temp.pdf')
            # name = cur_path.joinpath(bakdir, cur_path)
            os.startfile(f'{self.tmp_name}', command)
        except:
            pass
