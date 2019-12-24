# import tkinter as tk
from ttkthemes import ThemedTk
from util import config

theme = config.get('Theme', 'theme')

application = ThemedTk(theme=theme)

# application = ThemedTk(theme="radiance")     # plastik clearlooks elegance radiance   
                                             # arc black blue equilux itft1 keramik kroc  
# application.set_theme('arc')

# application = tk.Tk()

import bso

def main():
    # application = tk.Tk()
    application.withdraw()      # hide
    # application.title("БСО  (Блок сбора и обработки информации)")
    window = bso.App(application, 1100, 450, "БСО")
    application.protocol("WM_DELETE_WINDOW", window.exit_)
    application.minsize(900, 550)
    # application.wm_state('zoomed')
    application.deiconify()     # show
    application.mainloop()

main()
