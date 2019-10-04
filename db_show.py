#!/usr/bin/env python
# -*- coding:utf-8 -*-

import tkinter as tk
import tkinter.ttk as ttk
import os.path
import pathlib
from tkinter.scrolledtext import ScrolledText
from util import imgdir, bakdir
from db_pdf import go_pdf


class Editor:

    def __init__(self, master=None, parent=None):
        self.parent = parent        # ViewMetka
        self.master = master        # Frame
        self.img_ = parent.img_
        font = ("Helvetica", 12)    # 24
        self.st = ScrolledText(master, height=12, width=40,                         # height=10
                               font=font, bg='#777', fg='yellow', wrap=tk.WORD)     # tk.NONE
        self.st.pack(fill=tk.BOTH, expand=True)
        # self.st.pack(fill=tk.Y, expand=False)
        self.st.focus()
        ttk.Separator(master).pack(fill=tk.X, expand=True)
        self.dirinfo = tk.StringVar()
        
        f = ttk.Frame(master)
        f.pack(fill=tk.X, expand=True)
        fdir = ttk.Frame(f, padding=1, relief=tk.SUNKEN)
        fdir.pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Label(fdir, image=self.img_['folder'], compound=tk.LEFT, textvariable=self.dirinfo,
                  width=55, padding=(2, 2)).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Separator(f, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y)
        ttk.Sizegrip(f).pack(side=tk.RIGHT, padx=3)
        
        fhelp = ttk.Frame(f, padding=1, relief=tk.SUNKEN)
        fhelp.pack(side=tk.RIGHT, fill=tk.X, expand=False)
        btn_cancel = ttk.Button(fhelp, text="Отмена", image=self.img_['delete3'],
                                cursor="hand2", compound=tk.LEFT, command=self.cancel_)
        self.btn_save = ttk.Button(fhelp, text="Сохранить", image=self.img_['saveas'],
                                   cursor="hand2", compound=tk.LEFT, command=self.save_)
        self.btn_save.pack(side=tk.RIGHT, fill=tk.X, expand=False)
        btn_cancel.pack(side=tk.RIGHT, fill=tk.X, expand=False)
        self.btn_db_show = ttk.Button(fhelp, text="Просмотр", image=self.img_['pdf1'],
                                      state='disabled', cursor="hand2",
                                      compound=tk.LEFT, command=lambda: self.db_show(1))
        self.btn_db_print = ttk.Button(fhelp, text="Печать", image=self.img_['print1'],
                                      state='disabled', cursor="hand2",
                                      compound=tk.LEFT, command=lambda: self.db_show(0))
        self.btn_db_show.pack(side=tk.RIGHT, fill=tk.X, expand=False)
        self.btn_db_print.pack(side=tk.RIGHT, fill=tk.X, expand=False)

    def db_show(self, verbose, arg=None):
        """Просмотр или печать базы отметок""" 
        data = self.parent.result
        command = 'open' if verbose else 'print'
        cur_path = pathlib.Path('db_op.pdf')
        tmp_name = cur_path.joinpath(bakdir, cur_path)
        go_pdf(data, tmp_name)
        try:
            os.startfile(f'{tmp_name}', command)
            # os.startfile('db_op.pdf', command)
        except:
            pass               
       
    def gettext(self):
        """Получить текст из редактора"""
        return self.st.get('1.0', tk.END+'-1c')

    def clrtext(self):
        """Очистить редактор"""
        self.st.delete('1.0', tk.END)

    def set_info(self, msg):
        """Вывести msg в правый лабель"""
        return self.dirinfo.set(msg)
        
    def cancel_(self, arg=None):
        """Скрыть редактор"""
        self.st.delete(1.0, tk.END)
        self.parent.ed_frame.grid_remove()
        geom = self.parent.geometry().split("+")
        self.parent.geometry(f"751x300+{geom[1]}+{geom[-1]}")
    
    def save_(self, arg=None):
        text = self.gettext()
        self.parent.save_coment(text)

class ViewMetka(tk.Toplevel):

    def __init__(self, parent, result, geom=None):
        super().__init__(parent)
        self.parent = parent                # bso
        self.result = result               
        self.img_ = parent.img_
        self.withdraw()
        self.title("Просмотр оперативных отметок")
#        set_application_icons(self, 'icons')
        self.iconbitmap(os.path.join(imgdir, 'db.ico'))
        if geom:
            self.geometry(f"751x300+{geom[1]}+{geom[-1]}")
        else:
            self.geometry("751x300+100+100")
        self.deiconify()    #
        self.bind("<Escape>", self.parent.state_db_norm)
        #self.focus_force()
        if self.winfo_viewable():
            self.transient(parent)
        self.wait_visibility()      # подождать пока будек виден
        self.focus()
        self.resizable(0, 1)        # не менять размер
        #self.transient(self.parent)
        self.protocol("WM_DELETE_WINDOW", self.parent.state_db_norm)        
        
    def show_tree(self):
        style = ttk.Style()
        style.configure("Treeview", foreground='black')  # , rowheight=40
        style.configure("Treeview.Heading", font=('Helvetica', 14), foreground='brown')

        columns = ("#1", "#2", "#3", "#4")
        self.tree = ttk.Treeview(self, height=14, columns=columns, selectmode='browse')
        self.tree.heading("#0", text="", anchor=tk.W, image=self.img_['marker3'])
        self.tree.column("#1", width=160, anchor=tk.CENTER)
        self.tree.column("#2", width=160, anchor=tk.CENTER)
        self.tree.column("#3", width=160, anchor=tk.CENTER)
        self.tree.column("#4", width=160, anchor=tk.CENTER)
        self.tree.column("#0", width=70, anchor=tk.W)
        self.tree.heading("#1", text="Дата и время")
        self.tree.heading("#2", text="Широта")
        self.tree.heading("#3", text="Долгота")
        self.tree.heading("#4", text="Глубина")
        ysb = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=ysb.set)
        
        self.ed_frame = ttk.Frame(self)
        self.ed = Editor(self.ed_frame, self)
        tags = ("dbl-click",)   #
        for res in self.result:
            row = list(res)
            self.image_ = self.img_['im16']
            if row[5]:        # есть коментарий
                self.image_ = self.img_['book3']
                if row[5].startswith('Диапазон'):
                    self.image_ = self.img_['skrepka']
                elif row[5].startswith('A'):
                    self.image_ = self.img_['a_1']
            self.tree.insert("", tk.END, text=f"  {row[0]}", image=self.image_, values=tuple(row)[1 : -1], tags=tags)
#        self.tree.tag_bind("dbl-click", "<Double-Button-1>", self.edit_db)  #
        self.tree.bind("<<TreeviewSelect>>", self.coment_selection)

        self.tree.grid(row=0, column=0, sticky=tk.N+tk.W+tk.S+tk.E)
        ysb.grid(row=0, column=1, sticky=tk.N+tk.S)
        self.ed_frame.grid(row=1, column=0, columnspan=2, sticky=tk.N+tk.W+tk.S+tk.E)
        
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        self.columnconfigure(0, weight=1)
        self.ed_frame.grid_remove()
        
    def coment_selection(self, event):
        """Вывести коментарий в редактор"""
        self.item = self.tree.item(self.tree.selection())
        self.number = self.item["text"]       # type -> str
        data = self.parent.data_coment(self.number)[0]
        if data == 'A':
            self.ed.clrtext()
            self.ed.cancel_()
            return
        geom = self.geometry().split("+")
        self.geometry(f"751x554+{geom[1]}+{geom[-1]}")
        self.ed.st.config(state='normal')
        self.ed.st.delete(1.0, tk.END)
        self.ed.st.insert(tk.END, data)
        if self.parent.state_:        # False - bso, True - show
            self.ed.st.config(state='disabled')
            self.ed.btn_save.config(state='disabled')
            self.ed.btn_db_show.config(state='normal')
            self.ed.btn_db_print.config(state='normal')
        self.ed_frame.grid()
        
    def save_coment(self, coment):
        """Сохранить коментарий в базе"""
        self.parent.save_new_coment(self.number, coment)   #
        self.ed_frame.grid_remove()
        geom = self.geometry().split("+")
        self.parent.review_db(geom)      # сразу закрыть окно и вывести новое
        
    def set_name_db(self, msg):
        self.ed.set_info(msg)
