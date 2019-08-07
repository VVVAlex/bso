import tkinter as tk
application = tk.Tk()

import pui

# from . import pui

def main():
    # application = tk.Tk()
    application.withdraw()      # hide
    # application.title("БСО  (Блок сбора и обработки информации)")
    window = pui.App(application, 1100, 450, "ПУИ")
    application.protocol("WM_DELETE_WINDOW", window.exit_)
    application.minsize(900, 550)
    application.deiconify()     # show
    application.mainloop()

main()
