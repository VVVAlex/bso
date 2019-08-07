import tkinter as tk
application = tk.Tk()

import bso

def main():
    # application = tk.Tk()
    application.withdraw()      # hide
    # application.title("БСО  (Блок сбора и обработки информации)")
    window = bso.App(application, 1100, 450, "БСО")
    application.protocol("WM_DELETE_WINDOW", window.exit_)
    application.minsize(900, 550)
    application.deiconify()     # show
    application.mainloop()

main()
