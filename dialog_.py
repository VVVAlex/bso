#!/usr/bin/env python3

import sys
import tkinter as tk
import tkinter.ttk as ttk
#import tkinter.font as tkfont

OK_BUTTON =     0b0001
CANCEL_BUTTON = 0b0010
# YES_BUTTON =    0b0100
# NO_BUTTON =     0b1000

PAD = "0.75m"


class Dialog(tk.Toplevel):

    def __init__(self, master=None, title=None, buttons=OK_BUTTON, calback=None, default=OK_BUTTON):
        self.master = master or tk._default_root
        super().__init__(self.master)
        self.withdraw()   # скрыть
        self.resizable(True, False)    #
        if title is not None:
            self.title(title)
        self.buttons = buttons
        self.default = default
        self.calback = calback    #
        self.acceptButton = None
        self.__create_ui()
        self.__position()
        self.ok = None
        self.deiconify()    # показать
        if self.grid() is None:    # лудче minsize чем 1x1
            self.minsize(80, 40)
        else:
            self.minsize(10, 5)
        if self.winfo_viewable():
            self.transient(self.master)
        self.initialize()
        self.initialFocusWidget.focus()    # сосредоточиться на первом виджете
        self.wait_visibility()
        #self.grab_set()
        self.focus()
        if calback is None:
            self.wait_window(self)      # 

    def __create_ui(self):
        widget = self.body(self)
        if isinstance(widget, (tuple, list)):
            body, focusWidget = widget
        else:
            body = focusWidget = widget
        self.initialFocusWidget = focusWidget
        buttons = self.button_box(self)
        body.grid(row=0, column=0, sticky=(tk.N, tk.S, tk.W, tk.E))
        buttons.grid(row=1, column=0, sticky=tk.E)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

    def __position(self):
        self.protocol("WM_DELETE_WINDOW", self.__cancel)
        if self.master is not None:
            self.geometry(f"+{self.master.winfo_rootx() + 50}+{self.master.winfo_rooty() + 50}")

    def __ok(self, *arg):
        if not self.validate():
            self.initialFocusWidget.focus()
            return
        self.withdraw()
        self.update_idletasks()
        try:
            self.ok = True
            self.apply(self.calback)
        finally:
            self.__cancel()

    def __cancel(self, *arg):
        if self.ok is None:
            self.ok = False
        self.initialFocusWidget = None
        if self.master is not None:
            self.master.focus()
        self.destroy()

    def initialize(self):
        """Переопределите, чтобы выполнить все, что нужно сделать в конце"""
        pass

    @staticmethod
    def add_button(master, text, command, default=False):
        button = ttk.Button(master, text=text, command=command)
        if default:
            button.config(default=tk.ACTIVE)
        button.pack(side=tk.LEFT, padx=PAD, pady=PAD)
        return button

    def button_box(self, master):
        """Кнопки диалога"""
        frame = ttk.Frame(master)
        if self.buttons & OK_BUTTON:
            self.acceptButton = self.add_button(frame, "OK", self.__ok,
                                                self.default == OK_BUTTON)
        if self.buttons & CANCEL_BUTTON:
            self.add_button(frame, "Отмена", self.__cancel,
                            self.default == CANCEL_BUTTON)
        # if self.buttons & YES_BUTTON:
            # self.acceptButton = self.add_button(frame, "Yes", self.__ok,
                    # self.default == YES_BUTTON)
        # if self.buttons & NO_BUTTON:
            # self.add_button(frame, "No", self.__cancel,
                    # self.default == NO_BUTTON)
        self.bind("<Return>", self.__ok, "+")
        self.bind("<Escape>", self.__cancel, "+")
        return frame

    def body(self, master):
        """Переопределить, чтобы создать тело диалога"""
        label = ttk.Label(master, text="[Override Dialog.body()]")
        return label

    def validate(self):
        """Переопределить выполнение всей проверки диалога"""
        return True

    def apply(self, calback=None):
        """Переопределить выполнение действия OK"""
        pass


class Result:

    def __init__(self, value=None):
        self.value = value
        self.ok = False

    def __str__(self):
        return f"'{self.value}' {self.ok}"


class _StrDialog(Dialog):

    def __init__(self, master, title, prompt, result, calback):
        """Результатом должен быть объект Result,
           значение будет содержать str, 
           ok будет содержать True, если пользователь нажал OK или
           False если пользователь нажал Cancel."""
        self.prompt = prompt
        self.value = tk.StringVar()
        self.value.set(result.value)
        self.result = result
        super().__init__(master, title, OK_BUTTON|CANCEL_BUTTON, calback)

    def body(self, master):
        frame = ttk.Frame(master)
        label = ttk.Label(frame, text=self.prompt)
        label.pack(side=tk.LEFT, fill=tk.X, padx=PAD, pady=PAD)
        entry = ttk.Entry(frame, textvariable=self.value)
        entry.pack(side=tk.LEFT, fill=tk.X, expand=tk.YES, padx=PAD, pady=PAD)
        return frame, entry

    def apply(self, calback=None):
        self.result.value = self.value.get()
        self.result.ok = True
        if calback:
            calback(self.result.value)


class _NumberDialogBase(Dialog):    # Abstract base class

    def __init__(self, master, title, prompt, result, calback=None, minimum=None,
                 maximum=None, format=None):
        """Результатом должен быть объект Result,
           значение будет содержать int или float,
           ok будет содержать True, если пользователь нажал OK или
           False если пользователь нажал Cancel."""
        self.prompt = prompt
        self.minimum = minimum
        self.maximum = maximum
        self.format = format
        self.value = tk.StringVar()
        self.value.set(result.value)
        self.result = result
        super().__init__(master, title, OK_BUTTON | CANCEL_BUTTON, calback)


class _IntDialog(_NumberDialogBase):

    def body(self, master):
        frame = ttk.Frame(master)
        label = ttk.Label(frame, text=self.prompt)
        label.pack(side=tk.LEFT, fill=tk.X, padx=PAD, pady=PAD)
        self.spinbox = ttk.Spinbox(frame, from_=self.minimum, to=self.maximum,
                textvariable=self.value, validate="all")
        self.spinbox.config(validatecommand=(
            self.spinbox.register(self.validate), "%P"))
        self.spinbox.pack(side=tk.LEFT, padx=PAD, pady=PAD)
        return frame, self.spinbox
        
    def validate_spinbox_int(self, spinbox, number=None):
        if number is None:
            number = spinbox.get()
        if number == "":
            return True
        try:
            x = int(number)
            if int(spinbox.cget("from")) <= x <= int(spinbox.cget("to")):
                return True
        except ValueError:
            pass
        return False

    def validate(self, number=None):
        return self.validate_spinbox_int(self.spinbox, number)

    def apply(self, calback=None):
        self.result.value = int(self.value.get())
        self.result.ok = True
        if calback:
            calback(self.result.value)


class _FloatDialog(_NumberDialogBase):

    def body(self, master):
        frame = ttk.Frame(master)
        label = ttk.Label(frame, text=self.prompt)
        label.pack(side=tk.LEFT, fill=tk.X, padx=PAD, pady=PAD)
        self.spinbox = ttk.Spinbox(frame, from_=self.minimum, to=self.maximum,
                                  increment=0.5,
                                  textvariable=self.value, validate="all",
                                  format=self.format)
        self.spinbox.config(validatecommand=(
                                             self.spinbox.register(self.validate), "%P"))
        self.spinbox.pack(side=tk.LEFT, padx=PAD, pady=PAD)
        return frame, self.spinbox

    @staticmethod
    def validate_spinbox_float(spinbox, number=None):
        # if number is None:
            # number = spinbox.get()
        # if number == "":
            # return True
        if number == 0:     # для остановки автометок
            return True
        if number:
            try:
                x_ = float(number)
                if float(spinbox.cget("from")) <= x_ <= float(spinbox.cget("to")):
                    return True
            except ValueError:
                pass
            return False
        return True

    def validate(self, number=None):
        return self.validate_spinbox_float(self.spinbox, number)

    def apply(self, calback=None):
        self.result.value = float(self.value.get())
        self.result.ok = True
        if calback:
            calback(self.result.value)


def get_str(master, title, prompt, initial="", calback=None):
    """Возвращает None, если отмена или строку"""
    result = Result(initial)
    _StrDialog(master, title, prompt, result, calback)
    return result.value if result.ok else None

def get_int(master, title, prompt, calback=None, initial=0, minimum=None,
            maximum=None):
    """Возвращает None если отмена или int в заданном диапазоне"""
    assert minimum is not None and maximum is not None
    result = Result(initial)
    _IntDialog(master, title, prompt, result, calback, minimum, maximum)
    return result.value if result.ok else None

def get_float(master, title, prompt, calback=None, initial=0.0, minimum=None,
              maximum=None, format="%0.1f"):
    """Возвращает None если отмена или float в заданном диапазоне"""
    assert minimum is not None and maximum is not None
    result = Result(initial)
    _FloatDialog(master, title, prompt, result, calback, minimum, maximum, format)
    return result.value if result.ok else None


if __name__ == "__main__":
    if sys.stdout.isatty():
        application = tk.Tk()
        Dialog(application, "Dialog")
        x = get_str(application, "Get Str", "Name", "test")
        print("str", x)
        x = get_int(application, "Get Int", "Percent", None, 5, 0, 100)
        print("int", x)
        x = get_float(application, "Get Float", "Angle", None, 90, 0, 90)
        print("float", x)
        application.bind("<Escape>", lambda *args: application.quit())
        application.mainloop()
    else:
        print("Loaded OK")
