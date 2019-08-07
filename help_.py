#!/usr/bin/env python3

import tkinter as tk
import tkinter.ttk as ttk

PAD = "0.75m"

APPNAME_BCO = "БСО Версия 1.0"

_TEXT_BCO = """\

Программа предназначена для использования в качестве  промерного эхолота.
Позволяет сохранять промеры в фаиле для последующей обработки,
добавлять к промерам метки, как в ручном, так и автоматическом режимах.

Осушествлять просмотр записанной информации, а так же ее распечатку.!

"""

APPNAME = "ПУИ Версия 0.1"

_TEXT = """\

Программа предназначена для использования в качестве  ПУИ эхолота.
Позволяет управлять эхолотом, сохранять промеры в фаиле для
последующей обработки, добавлять к промерам метки, как в ручном,
так и автоматическом режимах.

Осушествлять просмотр записанной информации, а так же ее распечатку.!

"""

class Window(tk.Toplevel):

    def __init__(self, master, bso_=False):
        super().__init__(master)
        self.withdraw()
        if bso_:
            appname = APPNAME_BCO
            text = _TEXT_BCO
        else:
            appname = APPNAME
            text = _TEXT
        self.title(f"Справка \u2014 {appname}")
        self.create_ui(text)
        self.reposition()
        self.resizable(False, False)
        self.deiconify()
        if self.winfo_viewable():
            self.transient(master)
        self.wait_visibility()
        self.focus()

    def create_ui(self, text):
        self.helpLabel = ttk.Label(self, text=text, background="white")
        self.closeButton = ttk.Button(self, text="Закрыть", command=self.close)
        self.helpLabel.pack(anchor=tk.N, expand=True, fill=tk.BOTH,
                padx=PAD, pady=PAD)
        self.closeButton.pack(anchor=tk.S)
        self.protocol("WM_DELETE_WINDOW", self.close)
        self.bind("<Escape>", self.close)
        self.bind("<Expose>", self.reposition)


    def reposition(self, event=None):
        if self.master is not None:
            self.geometry(f"+{self.master.winfo_rootx() + 50}+{self.master.winfo_rooty() + 50}")


    def close(self, event=None):
        self.withdraw()


if __name__ == "__main__":
    application = tk.Tk()
    window = Window(application)
    application.bind("<Control-q>", lambda *args: application.quit())
    window.bind("<Control-q>", lambda *args: application.quit())
    application.mainloop()

