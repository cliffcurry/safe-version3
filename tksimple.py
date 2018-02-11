from tkinter import *
from builtins import str
import string
master = Tk()
tt=str("Access Denied")
master.wm_overrideredirect(True) 
w = Label(master, text=tt, font=("Helvetica", 56))
w.pack()

mainloop()