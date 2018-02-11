import tkinter as tk
import time
master = tk.Tk()
whatever_you_do = "Whatever you do will be insignificant, but it is very important that you do it.\n(Mahatma Gandhi)"
var = tk.StringVar()
var.set(whatever_you_do);
msg = tk.Message(master, textvariable=var)
msg.config(bg='lightgreen', font=('times', 24, 'italic'))
msg.pack()
while True:
    var.set(whatever_you_do)   
    master.update_idletasks()
    master.update()
    time.sleep(5)
    var.set("Don't worry, Be happy");
    master.update_idletasks()
    master.update()
    time.sleep(5)