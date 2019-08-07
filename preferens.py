#!/usr/bin/env python
# -*- coding:utf-8 -*-

import tkinter as tk
from tkinter import ttk
from util import config, write_config


class Window(tk.Toplevel):
    """Форма ввода настроек"""
    
    def __init__(self, master):
        super().__init__(master)
        self.master = master
        self.withdraw()
        self.title("Настройки")
        self.T = config.getfloat('Preferens', 't')
        self.h = config.getfloat('Preferens', 'h')
        self.chosen = ('DBT', 'DBK', 'DBS')
        self.D = config.getint('Preferens', 'd')
        self.create_ui()
        self.reposition()
        self.resizable(False, False)
        self.deiconify()
        if self.winfo_viewable():
            self.transient(master)
        self.wait_visibility()      # подождать пока будек виден
        self.focus()
        
    def create_ui(self):
        """Создание формы"""
        padWE = dict(sticky=(tk.W, tk.E), padx=8, pady=4)       # "0.5m"
        ttk.Label(self, text="Формат").grid(column=0, row=0, padx=8, sticky=tk.E)
        format_chosen = ttk.Combobox(self, state='readonly')
        format_chosen['values'] = self.chosen
        format_chosen.grid(column=1, row=0, padx=8, pady=4, sticky=tk.W)
        format_chosen.bind('<FocusIn>', self.ch_format)
        format_chosen.current(self.D)   # int
        self.format_chosen = format_chosen
        
        ttk.Separator(self).grid(column=0, row=1, columnspan=2, **padWE)
        
        vcmdT = (self.master.register(self.is_okay1), '%P')         # , '%S'
        vcmdh = (self.master.register(self.is_okay2), '%P')
        #invcmd = (self.master.register(self.is_not_okay), '%S')
         
        ttk.Label(self, text="Параметры судна").grid(column=1, row=2)
        ttk.Label(self, text=' T, м').grid(column=0, row=3, sticky=tk.E, padx=8)
        self.in_T = ttk.Entry(self, validate='key',
                              validatecommand=vcmdT)       # , invalidcommand=invcmd
        self.in_T.grid(column=1, row=3, **padWE)
        ttk.Label(self, text=' h, м').grid(column=0, row=4, sticky=tk.E, padx=8)
        self.in_h = ttk.Entry(self, validate='key', 
                              validatecommand=vcmdh)       # , invalidcommand=invcmd
        self.in_h.grid(column=1, row=4, **padWE)
        
        ttk.Separator(self).grid(column=0, row=5, columnspan=2)
        ttk.Label(self, text=" Поправка").grid(column=1, row=6)
        ttk.Label(self, text='ΔZᵦ, м').grid(column=0, row=7, sticky=tk.E, padx=8)
        self.in_popr = ttk.Label(self, text='', background='white')
        self.in_popr.grid(column=1, row=7, **padWE)
        
        ttk.Separator(self).grid(column=0, row=8, columnspan=2, **padWE)
        f = ttk.Frame(self)
        f.grid(column=0, row=9, columnspan=2, sticky=(tk.W, tk.E))
        self.btn_ok = ttk.Button(f, text='Применить', command=self.ok)
        self.btn_close = ttk.Button(f, text='Отмена', command=self.close)
        self.btn_close.pack(side='right')
        self.btn_ok.pack(side='right')
        
        self.columnconfigure(0, weight=0)
        self.columnconfigure(1, weight=3)
    
        self.protocol("WM_DELETE_WINDOW", self.close)
        self.bind_()
        self.ch_format()

    def is_okay1(self, P):  # ,S
        """Если возвращает False то значение в поле не изменить (T)"""
        #print(f"{P}")
        if P:
            try:
                res = float(P)
                l = len(f"{res}".split('.')[-1]) > 1
                if res >= 50 or l:                      #
                    raise ValueError
            except Exception:
                self.bell()
                return False
        return True
        #return (S.isdigit() or S in ('.'))
        
    def is_okay2(self, P):
        """Если возвращает False то значение в поле не изменить (h)"""
        if P:
            try:
                res = float(P)
                l = (len(f"{res}".split('.')[-1]) > 1)
                if res >= 10 or l:                      #
                    raise ValueError
            except Exception:
                self.bell()
                return False
        return True
        
    def key_(self, event=None):
        self.master.after(100, self.calculate)
        
    def calculate(self):
        """Считаем заглубление"""
        T = self.in_T.get()
        h = self.in_h.get()
        try:
            Z = round(float(T) - float(h), 2)
            self.in_popr.config(text=f'{Z}')
        except:
            self.in_popr.config(text='')
   
    def ch_format(self, arg=None):
        """Обработка comboboxa формата"""
        format = self.format_chosen.get()       # text
        self.in_T.delete(0, tk.END)
        self.in_h.delete(0, tk.END)
        if format == 'DBT':
            self.in_T.insert(0, '0')
            self.in_h.insert(0, '0')
            self.in_T.config(state='disabled')
            self.in_h.config(state='disabled')
        elif format == 'DBK':
            self.in_h.config(state='normal')
            self.in_h.insert(0, f'{self.h}')
            self.in_T.insert(0, '0')
            self.in_T.config(state='disabled')
        elif format == 'DBS':
            self.in_T.config(state='normal')
            self.in_h.config(state='normal')
            self.in_T.insert(0, f'{self.T}')
            self.in_h.insert(0, f'{self.h}')
        self.calculate()

    def reposition(self, event=None):
        """Положение формы"""
        if self.master is not None:
            self.geometry("+{}+{}".format(self.master.winfo_rootx() + 250,      #
                self.master.winfo_rooty() + 250))                               #

    def close(self, arg=None):
        """Обработка кнопки отмена"""
        self.unbind_()
        self.withdraw()
        
    def ok(self, arg=None):
        """Обработка кнопки применить"""
        T = float(self.in_T.get())
        h = float(self.in_h.get())
        z = round(T - h, 2)
        DT = self.format_chosen.get()
        for i, j in enumerate(self.chosen):
            if DT == j:
                D = i 
        if (T, h, D) != (self.T, self.h, self.D):            
            self.save_(T, h, D)
            self.master.pref_form(DT, z)
        self.close()

    @staticmethod
    def save_(*arg):
        """Сохранить настройки в конфиге"""
        config.set('Preferens', 'T', f'{arg[0]}')
        config.set('Preferens', 'h', f'{arg[1]}')
        config.set('Preferens', 'D', f'{arg[2]}')
        write_config()
        
    def bind_(self):
        self.bind("<Escape>", self.close)
        self.bind("<Expose>", self.reposition)
        # self.in_h.bind('<FocusIn>', self.calculate)
        self.in_h.bind('<Key>', self.key_)
        self.in_T.bind('<Key>', self.key_)
        self.bind("<Return>", self.ok)
        self.bind("<Escape>", self.close)

    def unbind_(self):
        self.unbind("<Return>")
        self.unbind("<Escape>")

        
if __name__ == "__main__":
    application = tk.Tk()
    window = Window(application)
    application.bind("<Control-q>", lambda *args: application.quit())
    window.bind("<Control-q>", lambda *args: application.quit())
    application.mainloop()

