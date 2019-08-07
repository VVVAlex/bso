# -*- coding:utf-8 -*-

import tkinter as tk
from time import time


class ToolTip(tk.Toplevel):
    """
    Предоставляет виджет всплывающей подсказки для Tkinter.
    """ 
    def __init__(self, wdgt, msg=None, msg_func=None, delay_show=0.5, delay_hide=2.5, follow=True):
        """
        Инициализация ToolTip
        Arguments:
          wdgt: Виджет этой подсказки назначен
          msg:  Статическое строковое сообщение, назначенное для ToolTip
          msg_func: Функция, которая извлекает строку для использования в качестве текста ToolTip
          delay:   Задержка в секундах перед всплывающей подсказкой(может быть float)
          follow:  Если True, ToolTip следует за движением, иначе скрывается
        """
        self.wdgt = wdgt
        self.parent = self.wdgt.master
        tk.Toplevel.__init__(self, self.parent, bg='black', padx=1, pady=1)
        self.withdraw()
        self.overrideredirect(True)
        self.msgVar = tk.StringVar()
        if msg is None:
            self.msgVar.set('No message provided')
        else:
            self.msgVar.set(msg)
        self.msg_func = msg_func
        self.delay_show = delay_show
        self.delay_hide = delay_hide
        self.follow = follow
        self.visible = 0
        self.lastMotion = 0
        tk.Message(self, textvariable=self.msgVar, bg='#FFFFDD',  aspect=1000).grid()
        self.wdgt.bind('<Enter>', self.spawn, '+')
        self.wdgt.bind('<Leave>', self.hide, '+')
        self.wdgt.bind('<Motion>', self.move, '+')

    def spawn(self, event=None):
        """
        Создет всплывающую подсказку.
        Arguments:
          event: Событие, вызвавшее эту функцию
        """
        self.visible = 1
        self.after(int(self.delay_show * 1000), self.show)

    def show(self):
        """
        Отображает подсказку, если время задержки достаточно продолжительное
        """
        if self.visible == 1 and time() - self.lastMotion > self.delay_show:
            self.visible = 2
        if self.visible == 2:
            self.deiconify()
        self.after(int(self.delay_hide * 1000), self.withdraw)         # скрыть tip

    def move(self, event):
        """
        Движение внутри виджета.
        Arguments:
          event: Событие, вызвавшее эту функцию
        """
        self.lastMotion = time()
        if self.follow is False:  # Если флаг ниже не установлен, движение внутри виджета приведет к тому, что ToolTip исчезнет
            self.withdraw()
            self.visible = 1
        self.geometry('+%i+%i' % (event.x_root + 10, event.y_root + 10)) # Смещение подсказки на 10x10 пикселей к юго-западу от указателя
        try:
            self.msgVar.set(self.msg_func())
        except:
            pass
        self.after(int(self.delay_show * 1000), self.show)

    def hide(self, event=None):
        """
        Скрывает всплывающую подсказку.
        Arguments:
          event: Событие, вызвавшее эту функцию
        """
        self.visible = 0
        self.withdraw()
