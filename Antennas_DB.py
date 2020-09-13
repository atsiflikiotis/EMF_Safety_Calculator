import tkinter as tk
import tkinter.ttk as ttk
from readdatabase import readdb
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import tkinter.filedialog
from pathlib import Path

antennas = readdb()
bands = [700, 800, 900, 1800, 2100, 2600, 3500]

class AntennasDB(tk.Frame):
    backupflag = 0

    def __init__(self, master, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        # self.cursor = conn.cursor()
        self.master = master
        self.master.title('Antennas Database')
        self.master.geometry('650x450')
        # self.master.configure(background='#D8D8D8')

        # logging.basicConfig(filename='antennas.log', filemode='a', level=logging.INFO,
        #                     format='%(asctime)s - %(message)s', )

        s = ttk.Style()
        s.configure('my.TButton', font=(None, 8))

        master.rowconfigure(0, weight=0)
        master.rowconfigure(1, weight=1)
        master.rowconfigure(2, weight=1)
        master.rowconfigure(3, weight=10)

        master.columnconfigure(0, weight=0)
        master.columnconfigure(1, weight=1)
        master.columnconfigure(2, weight=10)

        # DATABASE FRAME##########
        databaseframe = ttk.LabelFrame(master, text="Browse Antennas")
        databaseframe.grid(row=1, column=1, columnspan=1, rowspan=1, sticky='nswe', padx=20)
        databaseframe.rowconfigure(0, weight=0)
        databaseframe.rowconfigure(1, weight=1)
        databaseframe.rowconfigure(2, weight=1)
        databaseframe.rowconfigure(3, weight=1)
        databaseframe.rowconfigure(4, weight=1)
        databaseframe.columnconfigure(0, weight=10)
        databaseframe.columnconfigure(1, weight=0)
        databaseframe.columnconfigure(2, weight=1)
        databaseframe.columnconfigure(3, weight=0)

        # labels
        lab1 = ttk.Label(databaseframe, text='Antennas')
        lab1.grid(row=0, column=0, sticky='nw')
        lab2 = ttk.Label(databaseframe, text='Tilts')
        lab2.grid(row=0, column=2, sticky='nw', padx=10)

        # set antenna listbox and scrollbar
        antlbscrollbar = ttk.Scrollbar(databaseframe)
        self.antlb = tk.Listbox(databaseframe, yscrollcommand=antlbscrollbar.set, exportselection=False)
        antlbscrollbar.config(command=self.antlb.yview)
        self.antlb.grid(row=1, column=0, rowspan=5, sticky='nsew')
        antlbscrollbar.grid(row=1, column=1, sticky='nsw', rowspan=4)
        # fill antennas
        self.fillantennas()

        # set tilt listbox and scrollbar
        tiltlbscrollbar = ttk.Scrollbar(databaseframe)
        self.tiltlb = tk.Listbox(databaseframe, yscrollcommand=tiltlbscrollbar.set, exportselection=False, width=3,
                                 height=4)
        tiltlbscrollbar.config(command=self.tiltlb.yview)
        self.tiltlb.grid(row=1, column=2, sticky='nswe', padx=(5, 0))
        tiltlbscrollbar.grid(row=1, column=3, sticky='nsw')

        # bindings
        self.antlb.bind("<<ListboxSelect>>", self.antselected)
        self.tiltlb.bind("<<ListboxSelect>>", self.getbands)

        # ANTENNA SPECS FRAME inside database frame
        self.specframe = ttk.Frame(databaseframe)
        self.specframe.grid(row=0, column=4, rowspan=len(bands) + 1, padx=(10, 0), sticky='nswe')
        lb1 = [None] * len(bands)
        self.tb = [None] * len(bands)

        # write bands rows
        label1 = ttk.Label(self.specframe, text='Band (MHz)')
        label1.grid(row=0, column=0, pady=(1, 5))
        label2 = ttk.Label(self.specframe, text='Gain(dBi)')
        label2.grid(row=0, column=1, pady=(1, 5), padx=5)

        for r in range(len(bands)):
            lb1[r] = ttk.Label(self.specframe, text=str(bands[r]) + ':')
            lb1[r].grid(row=r + 1, column=0, sticky='ne', pady=5)
            # self.gainvar[r] = tk.StringVar()
            # lb2[r] = ttk.Text(self.specframe, textvariable=self.gainvar[r])
            # lb2[r].grid(row=r+1, column=1, sticky='nw', pady=0, padx=5)
            self.tb[r] = ttk.Entry(self.specframe, width=5, justify='center')
            self.tb[r].grid(row=r + 1, column=1, sticky='nw', pady=0, padx=5)

        # Plot frame
        plotframe = ttk.LabelFrame(master, text='Export radiation plots')
        plotframe.grid(row=2, column=1, padx=20, pady=30, sticky='nsew')

        # labels in plot frame
        text1 = tk.Label(plotframe, text='Export vertical and horizontal plots for Band:')
        text1.grid(row=0, column=0, padx=5, pady=5, sticky='nsw')
        self.freqbox = ttk.Combobox(plotframe, values=[], width=6)
        self.freqbox.grid(row=0, column=1, padx=2, pady=5, sticky='nsew')
        self.freqbox.bind("<<ComboboxSelected>>", self.filltiltbox)

        text2 = tk.Label(plotframe, text='and tilt:')
        text2.grid(row=0, column=2, padx=1, pady=5, sticky='nsw')
        self.tiltbox = ttk.Combobox(plotframe, values=[], width=4)
        self.tiltbox.grid(row=0, column=3, padx=2, pady=5, sticky='nsew')

        plotbtn = ttk.Button(plotframe, text='Export plots', command=self.plotpatterns)
        plotbtn.grid(row=0, column=4, sticky='nsw', padx=10, pady=5)

    def fillantennas(self):
        # antlist = self.cursor.execute('SELECT DISTINCT name FROM antennas ORDER BY name')
        antlist = antennas.index.unique(level='Antenna').tolist()
        for name in antlist:
            self.antlb.insert(tk.END, name)
        self.antlb.insert(tk.END, *antlist)

    def antselected(self, event):
        if self.antlb.curselection():
            self.tiltlb.delete(0, tk.END)

            for i in range(len(bands)):
                # self.gainvar[i].set(' ')
                self.tb[i].delete(0, tk.END)

            antidx = self.antlb.curselection()[0]
            self.antennasel = self.antlb.get(antidx)
            # tiltlist = self.cursor.execute('SELECT DISTINCT tilt FROM antennas WHERE name = ? ORDER BY tilt',
            #                                (self.antennasel,))
            tiltlist = antennas.loc[self.antennasel].index.unique(level='Tilt').tolist()

            # for val in tiltlist:
            #     self.tiltlb.insert(tk.END, val)
            # one-line fill listbox
            self.tiltlb.insert(tk.END, *tiltlist)

            # reset freqbox and tiltbox in plot frame:
            self.freqbox.delete(0, tk.END)
            self.tiltbox.delete(0, tk.END)

            # fill supported bands in plot frame freqbox
            supbandslist = antennas.loc[pd.IndexSlice[self.antennasel, :, :]].index.unique(level='Band').tolist()
            self.freqbox.config(values=supbandslist)
            self.freqbox.current(0)
            self.filltiltbox(event)

    def getbands(self, event):
        if self.tiltlb.curselection():
            tiltidx = self.tiltlb.curselection()[0]
            self.tiltsel = self.tiltlb.get(tiltidx)

            # supbandstemp = self.cursor.execute(
            #     'SELECT DISTINCT band FROM antennas WHERE name=? AND tilt=? ORDER BY band',
            #     (self.antennasel, self.tiltsel)).fetchall()
            supbandslist = antennas.loc[pd.IndexSlice[self.antennasel, :, self.tiltsel]].index.unique(level='Band').tolist()
            # supbandslist = [] * len(supbandstemp)
            # for val in supbandstemp:
            #     supbandslist.append(val[0])

            self.gains = dict.fromkeys(supbandslist)  # dictionary with bands as keys and gains as values

            for i in range(len(bands)):
                self.tb[i].delete(0, tk.END)
                if bands[i] in supbandslist:
                    gain = antennas.loc[(self.antennasel, bands[i], self.tiltsel)]['Gain']
                    # gain = self.cursor.execute('SELECT gain FROM antennas WHERE name=? AND tilt=? AND band=?',
                    #                            (self.antennasel, self.tiltsel, bands[i])).fetchone()[0]
                    self.gains[bands[i]] = gain
                else:
                    self.gains[bands[i]] = 'NA'
                self.tb[i].insert(0, self.gains[bands[i]])

    def filltiltbox(self, event):
        # get selected band
        bandsel = float(self.freqbox.get())
        # get supported tilts, xs usage instead of pd indexslide
        suptilts = antennas.xs((self.antennasel, bandsel)).index.unique(level='Tilt').tolist()
        self.tiltbox.config(values=suptilts)
        self.tiltbox.current(0)

    def plotpatterns(self):
        antenna = self.antennasel
        band = float(self.freqbox.get())
        tilt = float(self.tiltbox.get())
        defname = f"{band}_{antenna}_{tilt}"
        fpath = tkinter.filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG image", '*.png')],
                                                initialdir=Path.cwd(), title="Save as file", initialfile=defname)

        fig = plt.Figure(figsize=(12, 8))
        horax = fig.add_subplot(121, polar=True)
        verax = fig.add_subplot(122, polar=True)

        row = antennas.loc[(antenna, band, tilt)]
        horizontal = row['Pattern'][:, 0]
        vertical = row['Pattern'][:, 1]
        gain = row['Gain']
        vernorm = -vertical
        hornorm = -horizontal
        horax.plot(np.linspace(0, 2 * np.pi, 361), hornorm)
        verax.plot(np.linspace(0, 2 * np.pi, 361), vernorm)
        verax.set_theta_direction(-1)
        horax.set_theta_direction(-1)
        horax.set_theta_offset(np.pi/2)
        fig.suptitle(f"{defname}, Gain={gain:.2f}dBi")
        fig.savefig(fpath)








