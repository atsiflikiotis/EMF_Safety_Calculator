import tkinter as tk
import tkinter.ttk as ttk

class popupmessage(tk.Toplevel):
    def __init__(self, masterwindow, title, message, width, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.title = title
        self.iconbitmap('icon.ico')
        x = masterwindow.winfo_x()
        y = masterwindow.winfo_y()
        self.geometry("+%d+%d" % (x + 100, y + 200))
        messagelbl = tk.Message(self, text=message, width=width)
        messagelbl.grid(row=0, column=0, sticky='ns')
        btn = ttk.Button(self, text='OK', command=lambda: self.destroy())
        btn.grid(row=1, column=0)

