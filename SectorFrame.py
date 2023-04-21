import tkinter as tk
import tkinter.ttk as ttk
import math as math
import numpy as np
import Antennas_DB as AntDB
import pandas as pd

bands = AntDB.bands
lenbands = len(bands)
antennas = AntDB.antennas


class SectorFrame(ttk.Labelframe):
    def __init__(self, master, sector, mainclass, parentsector=None, **kwargs):
        super().__init__(master, text='Sector {0}'.format(sector), **kwargs)
        self.master = master
        self.parentsector = parentsector
        self.sector = sector    #sector id (unique integer)
        self.mainclass = mainclass  # for access inside other methods

        # Antenna ComboBox, azimuth, tilt and height frame
        frame1 = ttk.Frame(self)
        frame1.grid(row=0, column=0, columnspan=9)

        # antenna combobox
        # get list of antennas
        antlist = antennas.index.unique(level='Antenna').tolist()

        self.antcombobox = ttk.Combobox(frame1, values=antlist, width=30, state='readonly')
        self.antcombobox.grid(row=1, column=0, sticky='nw', columnspan=5, padx=5)

        self.antcombobox.bind("<<ComboboxSelected>>", self.antennaselected)

        self.patterns = dict.fromkeys(bands)
        self.horizontal = dict.fromkeys(bands)
        self.vertical = dict.fromkeys(bands)

        self.powerdensity = dict.fromkeys(bands)
        self.banddepps = dict.fromkeys(bands)
        self.gainatten = dict.fromkeys(bands)
        self.rmcoefficient = dict.fromkeys(bands)

        lbl1 = ttk.Label(frame1, text='Antenna')
        lbl2 = ttk.Label(frame1, text='Azimuth (°)')
        lbl3 = tk.Message(frame1, text='Mech. Tilt (°)', aspect=200, justify='center')
        lbl4 = tk.Message(frame1, text='MoA height from ref. level (m)', aspect=200, justify='center')
        lbl1.grid(row=0, column=0, columnspan=5, sticky='ns', padx=5)
        lbl2.grid(row=0, column=5, sticky='ns', padx=5, columnspan=2)
        lbl3.grid(row=0, column=7, sticky='nsew', padx=5, columnspan=2)
        lbl4.grid(row=0, column=9, sticky='s', padx=5)

        self.azimtext = ttk.Entry(frame1, width=6, justify='center')
        self.azimtext.grid(row=1, column=5, sticky='ns', padx=8, columnspan=2)
        self.mechtilttext = ttk.Entry(frame1, width=4, justify='center')
        self.mechtilttext.grid(row=1, column=7, sticky='ns', padx=8, columnspan=2)
        self.midheighttext = ttk.Entry(frame1, width=5, justify='center')
        self.midheighttext.grid(row=1, column=9, sticky='ns', padx=4)

        # set power unit selection
        powerunitframe = ttk.LabelFrame(self, text="Power unit")
        powerunitframe.grid(row=2, column=0, columnspan=9, padx=10, sticky='nws', pady=(5, 5))
        # powerunitlabel = ttk.Label(powerunitframe, text="Power unit:")
        # powerunitlabel.grid(row=0, column=0, sticky='nsw', columnspan=1, padx=2)
        self.powerunitvar = tk.StringVar()

        powerunitrb1 = ttk.Radiobutton(powerunitframe, text="dBm", variable=self.powerunitvar, value='Power (dBm):',
                                       command=self.updatetotpowers)
        powerunitrb2 = ttk.Radiobutton(powerunitframe, text="Watt", variable=self.powerunitvar, value='Power (Watt):',
                                       command=self.updatetotpowers)
        if self.parentsector is None:
            self.powerunitvar.set('Power (Watt):')
        else:
            self.powerunitvar.set(mainclass.sector1.powerunitvar.get())

        powerunitrb1.grid(row=0, column=1, sticky='nsw', columnspan=1, padx=6)
        powerunitrb2.grid(row=0, column=2, sticky='nsw', columnspan=1, padx=1)

        # initialize tiltsbox to fill after default antenna selected
        # tilts boxes
        # initialize dictionary with list of tilts for each band
        self.tiltslist = dict.fromkeys(bands)
        self.tiltsbox = dict.fromkeys(bands)
        for i in range(lenbands):
            self.tiltsbox[bands[i]] = ttk.Combobox(self, values=self.tiltslist[bands[i]], width=2, state='readonly',
                                                   justify='center', )
            self.tiltsbox[bands[i]].bind("<<ComboboxSelected>>", self.tiltschanged)
            self.tiltsbox[bands[i]].grid(row=6, column=i + 1, sticky='we', padx=(7, 7))

        # write rows labels
        lbl5 = ttk.Label(self, text="Band (MHz):").grid(row=3, column=0, sticky='nw', padx=(5, 5), pady=(8, 8))
        lbl6 = ttk.Label(self, text='El. tilt (°):').grid(row=6, column=0, sticky='nw', padx=(5, 5), pady=(0, 0))
        lbl12 = ttk.Label(self, text='TRXs/Carriers:').grid(row=7, column=0, sticky='nw', padx=(5, 5), pady=(0, 0))
        lbl7 = ttk.Label(self, textvariable=self.powerunitvar).grid(row=8, column=0, sticky='nw', padx=(5, 5),
                                                                    pady=(0, 0))
        lbl8 = ttk.Label(self, text='Losses (dB):').grid(row=9, column=0, sticky='nw', padx=(5, 5), pady=(0, 0))
        lbl9 = ttk.Label(self, text='Utilizaton (%):').grid(row=10, column=0, sticky='nw', padx=(5, 5), pady=(0, 0))
        # separator2 row 11
        lbl10 = ttk.Label(self, text='Tot. Power (W):').grid(row=12, column=0, sticky='nw', padx=(5, 5), pady=(0, 0))
        lbl11 = ttk.Label(self, text='Gain (dBi):').grid(row=13, column=0, sticky='nw', padx=(5, 5), pady=(0, 0))
        lbl13 = ttk.Label(self, text='Total EIRP (W):').grid(row=14, column=0, sticky='nw', padx=(5, 5), pady=(0, 0))

        # write all bands in column titles
        labelband = [None] * lenbands
        for i in range(lenbands):
            labelband[i] = ttk.Label(self, text=bands[i], width=5)
            labelband[i].grid(row=3, column=i + 1, padx=5, sticky='ns', pady=(8, 5))

        # seperator1
        sep = ttk.Separator(self)
        sep.grid(row=4, column=1, columnspan=9, sticky='ew', pady=(0, 4))

        # other entries boxes
        # carriers
        self.carrierbox = dict.fromkeys(bands)
        for i in range(lenbands):
            self.carrierbox[bands[i]] = tk.Spinbox(self, from_=0, to=10, width=5, justify='center', state='normal',
                                                   command=self.updatetotpowers)
            # self.carrierbox[bands[i]] = tk.Entry(self,  justify='center', width=6)
            self.carrierbox[bands[i]].grid(row=7, column=i + 1, padx=(7, 7))
            self.carrierbox[bands[i]].bind("<KeyRelease>", lambda evnt: self.updatetotpowers())
            self.carrierbox[bands[i]].delete(0, tk.END)
            if self.parentsector is None:
                self.carrierbox[bands[i]].insert(0, 2)
            else:
                self.carrierbox[bands[i]].insert(0, mainclass.sector1.carrierbox[bands[i]].get())

        # powers
        self.powerbox = dict.fromkeys(bands)
        for i in range(lenbands):
            self.powerbox[bands[i]] = tk.Spinbox(self, from_=0, to=1000, width=5, justify='center', state='normal',
                                                 command=self.updatetotpowers)
            # self.powerbox[bands[i]] = tk.Entry(self,  justify='center', width=6)
            self.powerbox[bands[i]].grid(row=8, column=i + 1, padx=(7, 7))
            self.powerbox[bands[i]].bind("<KeyRelease>", lambda evnt: self.updatetotpowers())
            self.powerbox[bands[i]].delete(0, tk.END)
            if self.parentsector is None:
                self.powerbox[bands[i]].insert(0, 40)
            else:
                self.powerbox[bands[i]].insert(0, mainclass.sector1.powerbox[bands[i]].get())

        # loses
        self.losesbox = dict.fromkeys(bands)
        for i in range(lenbands):
            self.losesbox[bands[i]] = tk.Spinbox(self, from_=0, to=1000, width=5, justify='center', state='normal',
                                                 command=self.updatetotpowers)
            # self.losesbox[bands[i]] = tk.Entry(self,  justify='center', width=6)
            self.losesbox[bands[i]].grid(row=9, column=i + 1, padx=(7, 7))
            self.losesbox[bands[i]].bind("<KeyRelease>", lambda evnt: self.updatetotpowers())
            self.losesbox[bands[i]].delete(0, tk.END)
            if self.parentsector is None:
                self.losesbox[bands[i]].insert(0, 1)
            else:
                self.losesbox[bands[i]].insert(0, mainclass.sector1.losesbox[bands[i]].get())

        # utilization(%)
        self.utilbox = dict.fromkeys(bands)
        for i in range(lenbands):
            self.utilbox[bands[i]] = tk.Spinbox(self, from_=0, to=100, width=5, justify='center', state='normal',
                                                command=self.updatetotpowers)
            # self.utilbox[bands[i]] = tk.Entry(self,  justify='center', width=6)
            self.utilbox[bands[i]].grid(row=10, column=i + 1, padx=(7, 7))
            self.utilbox[bands[i]].bind("<KeyRelease>", lambda evnt: self.updatetotpowers())
            self.utilbox[bands[i]].delete(0, tk.END)
            if self.parentsector is None:
                self.utilbox[bands[i]].insert(0, 80)
            else:
                self.utilbox[bands[i]].insert(0, mainclass.sector1.utilbox[bands[i]].get())

        # separator2
        sep2 = ttk.Separator(self)
        sep2.grid(row=11, column=1, columnspan=11, sticky='ew', pady=(4, 4))

        # labels
        # total power input
        # dependent from power, loses and utilization
        self.totpowerlabel = dict.fromkeys(bands)
        self.totpowervar = dict.fromkeys(bands)
        self.totpower = dict.fromkeys(bands)  # final values of class
        # construct first time then in method only update variable
        for i in range(lenbands):
            self.totpowervar[bands[i]] = tk.DoubleVar()
            self.totpowerlabel[bands[i]] = ttk.Label(self, textvariable=self.totpowervar[bands[i]])
            self.totpowerlabel[bands[i]].grid(row=12, column=i + 1, padx=(7, 7))

        # gains labels
        self.gainslabel = dict.fromkeys(bands)
        self.gainsvar = dict.fromkeys(bands)
        self.gain = dict.fromkeys(bands)  # final values of class
        # construct first time then in method only update variable
        for i in range(lenbands):
            self.gainsvar[bands[i]] = tk.DoubleVar()
            self.gainslabel[bands[i]] = ttk.Label(self, textvariable=self.gainsvar[bands[i]])
            self.gainslabel[bands[i]].grid(row=13, column=i + 1, padx=(7, 7))

        # total EIRP
        self.totaleirpvar = tk.DoubleVar()
        self.totaleirplabel = ttk.Label(self, textvariable=self.totaleirpvar)
        self.totaleirplabel.grid(row=14, column=1, columnspan=lenbands - 1, padx=(7, 7))

        # frame 2 to submit antenna
        if self.sector != 1:
            frame2 = ttk.Frame(self)
            frame2.grid(row=14, column=0, columnspan=9, pady=(7, 7), padx=5)
            submit = ttk.Button(frame2, text='Submit sector {}'.format(self.sector), command=self.submitantenna)
            submit.grid(row=0, column=0, sticky='ns')

        self.filldefaultvalues(parentsector, mainclass)

    # METHODS###################################################

    def filldefaultvalues(self, parentsector, mainclass):
        # fill default values
        if parentsector is None:
            self.antcombobox.current(0)
            self.azimtext.insert(0, 0)
            self.mechtilttext.insert(0, 0)
            self.midheighttext.insert(0, 5)
            self.antcombobox.event_generate("<<ComboboxSelected>>", when='tail')
        else:
            self.antcombobox.current(mainclass.sector1.antcombobox.current())
            # self.azimtext.insert(0, parentsector.azimtext.get())
            self.mechtilttext.insert(0, mainclass.sector1.mechtilttext.get())
            self.midheighttext.insert(0, mainclass.sector1.midheighttext.get())
            self.antcombobox.event_generate("<<ComboboxSelected>>", when='tail')

    def antennaselected(self, event):
        # when antenna selected, fill tilts
        self.antennasel = self.antcombobox.get()
        # get antenna supporting bands and fill textboxes with tilts
        # cursor = self.cursor.execute('SELECT DISTINCT band FROM antennas WHERE name=? ORDER BY band',
        #                              (self.antennasel,))
        self.supbandslist = antennas.loc[self.antennasel].index.unique(level='Band').tolist()

        # get supported tilts for each band or fill with 'NA' label in frame row 4
        for i in range(lenbands):
            if bands[i] in self.supbandslist:
                # self.tiltslist[bands[i]] = []
                # cursor = self.cursor.execute('SELECT DISTINCT tilt FROM antennas WHERE name=? AND band=? ORDER BY tilt',
                #                              (self.antennasel, bands[i]))

                # for val in cursor:
                #     self.tiltslist[bands[i]].append(val[0])

                # get tilts values
                self.tiltslist[bands[i]] = antennas.loc[pd.IndexSlice[self.antennasel, bands[i], :]].index.unique(level='Tilt').tolist()
                # put a spinbox with list of supporting tilts
                self.tiltsbox[bands[i]].config(values=self.tiltslist[bands[i]], state='readonly')

                # self.tiltsbox[bands[i]].bind('<Button-1>', lambda evnt, var=i: self.tiltchanged(var)) when
                # binding events in lambda, evnt keyword is used only in lambda line and no in function args

                # self.tiltsbox[bands[i]].event_generate('<<Button-1>>')  #not working why?
                if self.parentsector is None:
                    self.tiltsbox[bands[i]].current(0)
                else:
                    if self.antennasel == self.mainclass.sector1.antcombobox.get():
                        self.tiltsbox[bands[i]].current(self.mainclass.sector1.tiltsbox[bands[i]].current())
                    else:
                        self.tiltsbox[bands[i]].current(0)
            else:
                self.tiltsbox[bands[i]].config(values=['NA'], state='disabled')

        self.updatecarriers()
        self.updatepowers()
        self.updateloses()
        self.updateutils()
        self.updategains()
        self.updatetotpowers()
        self.updatetotaleirp()
        self.getpatterns()

    def tiltschanged(self, event):
        self.updategains()
        self.getpatterns()

    def updatepowers(self):
        for i in range(lenbands):
            if bands[i] in self.supbandslist:
                self.powerbox[bands[i]].config(state='normal')
            else:
                self.powerbox[bands[i]].config(state='disabled')

    def updateloses(self):
        for i in range(lenbands):
            if bands[i] in self.supbandslist:
                self.losesbox[bands[i]].config(state='normal')
            else:
                self.losesbox[bands[i]].config(state='disabled')

    def updateutils(self):
        for i in range(lenbands):
            if bands[i] in self.supbandslist:
                self.utilbox[bands[i]].config(state='normal')
            else:
                self.utilbox[bands[i]].config(state='disabled')

    def updatecarriers(self):
        for i in range(lenbands):
            if bands[i] in self.supbandslist:
                self.carrierbox[bands[i]].config(state='normal')
            else:
                self.carrierbox[bands[i]].config(state='disabled')

    def updatetotpowers(self):
        for i in range(lenbands):
            if (bands[i] in self.supbandslist) and self.powerbox[bands[i]].get() and self.carrierbox[
                bands[i]].get() and int(self.carrierbox[bands[i]].get()) > 0 and float(
                    self.powerbox[bands[i]].get()) > 0:
                carriers = int(self.carrierbox[bands[i]].get())
                if self.powerunitvar.get() == 'Power (Watt):':
                    dBm = 10 * math.log10(carriers * float(self.powerbox[bands[i]].get())) + 30
                else:
                    dBm = 10 * math.log10(carriers * 10 ** (0.1 * float(self.powerbox[bands[i]].get())))

                var1 = (dBm - float(self.losesbox[bands[i]].get()))
                var2 = 0.00001 * (math.pow(10, 0.1 * var1) * float(self.utilbox[bands[i]].get()))
                self.totpowervar[bands[i]].set("{0:.3f}".format(var2))
            else:
                self.totpowervar[bands[i]].set(0)
        self.updatetotaleirp()

    def updategains(self):
        for i in range(lenbands):
            if bands[i] in self.supbandslist:
                tilt = float(self.tiltsbox[bands[i]].get())
                # get gain from antennasel and tilt

                # cursor = self.cursor.execute('SELECT gain FROM antennas WHERE name=? AND band=? AND tilt=?',
                #                              (self.antennasel, bands[i], tilt)).fetchone()
                # gain = cursor[0]

                gain = antennas.loc[self.antennasel, bands[i], tilt]['Gain']
                self.gainsvar[bands[i]].set("{0:.2f}".format(gain))
            else:
                self.gainsvar[bands[i]].set('NA')
        self.updatetotpowers()

    def updatetotaleirp(self):
        sum = 0
        for i in range(lenbands):
            if self.totpowervar[bands[i]].get() > 0:
                sum += self.totpowervar[bands[i]].get() * 10 ** (0.1 * self.gainsvar[bands[i]].get())
        self.totaleirpvar.set("{0:.2f}".format(sum))

    def getpatterns(self):
        for i in range(lenbands):
            if bands[i] in self.supbandslist:
                tilt = float(self.tiltsbox[bands[i]].get())
                # cursor = self.cursor.execute('SELECT pattern FROM antennas WHERE name=? AND band=? AND tilt=?',
                #                              (self.antennasel, bands[i], tilt)).fetchone()
                # file = patternspath + str(cursor[0])

                ####decimal separator warning!!
                # self.patterns[bands[i]] = np.asarray(pd.read_csv(file, delimiter=';', decimal=',', header=None))
                # if decimal is '.' (true in version when all attoll patterns are extracted) then no pandas is needed:
                # self.patterns[bands[i]] = np.genfromtxt(file, delimiter=';')
                self.patterns[bands[i]] = antennas.loc[(self.antennasel, bands[i], tilt)]['Pattern']
            else:
                self.patterns[bands[i]] = None

    def submitantenna(self):

        if len(self.azimtext.get()) == 0 or len(self.mechtilttext.get()) == 0 or len(self.midheighttext.get()) == 0:
            newwindow = tk.Toplevel()
            newwindow.iconbitmap('icon.ico')
            newwindow.grab_set()
            message = 'Please fill all required values then submit antenna.'
            messagelbl = tk.Message(newwindow, text=message, width=400)
            messagelbl.grid(row=0, column=0, sticky='ns')
            btn = ttk.Button(newwindow, text='OK', command=lambda: newwindow.destroy())
            btn.grid(row=1, column=0)
        else:
            # final values
            self.azimuth = int(self.azimtext.get())
            if self.azimuth < 0:
                self.azimuth += 360
            self.mechtilt = int(self.mechtilttext.get())
            self.antheight = float(self.midheighttext.get())
            for i in range(lenbands):
                self.totpower[bands[i]] = float(self.totpowervar[bands[i]].get())
                # split horizontal and vertical after roll to vertical
                if bands[i] in self.supbandslist:
                    self.gain[bands[i]] = float(self.gainsvar[bands[i]].get())
                    # instead of rolling array, sector.phi matrix is going to rotate
                    self.horizontal[bands[i]] = self.patterns[bands[i]][:, 0]
                    # self.vertical[bands[i]] = np.roll(self.patterns[bands[i]][:,1], self.mechtilt)
                    self.vertical[bands[i]] = self.patterns[bands[i]][:, 1]

            # add sector to list of Main class in frame2
            if self not in self.mainclass.sectorslist:
                self.mainclass.sectorslist.append(self)
                self.mainclass.writesectors()

            self.master.destroy()

