import tkinter as tk
import tkinter.ttk as ttk
from readdatabase import readdb
import pandas as pd

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
        #        self.master.configure(background='#D8D8D8')

        # logging.basicConfig(filename='antennas.log', filemode='a', level=logging.INFO,
        #                     format='%(asctime)s - %(message)s', )

        s = ttk.Style()
        s.configure('my.TButton', font=(None, 8))

        master.rowconfigure(0, weight=1)
        master.rowconfigure(1, weight=4)
        master.rowconfigure(2, weight=1)

        master.columnconfigure(0, weight=3)
        master.columnconfigure(1, weight=3)
        master.columnconfigure(2, weight=3)
        master.columnconfigure(3, weight=1)
        master.columnconfigure(4, weight=1)
        master.columnconfigure(5, weight=1)

        # DATABASE FRAME###########################################################
        databaseframe = ttk.LabelFrame(master, text="Browse Antennas")
        databaseframe.grid(row=0, column=0, columnspan=2, rowspan=1, sticky='nswe', padx=20)
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
        self.antlb.bind("<<ListboxSelect>>", self.filltilt)
        self.tiltlb.bind("<<ListboxSelect>>", self.getbands)

        # ANTENNA SPECS FRAME inside database frame###########################################################################
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

        # add update gains button
        # removed in v2.0
        # updatebtn = ttk.Button(self.specframe, text='Update gains', command=self.updategains, style='my.TButton', )
        # updatebtn.grid(row=1, column=2, sticky='nw', )

        # FRAME 'ADDBAND'#########################################################################
        # removed in v2.0
#        self.addbandfr = ttk.LabelFrame(master, text="Add band/tilt to: (select antenna)")
#        self.addbandfr.grid(row=1, column=0, columnspan=2, sticky='nswe', padx=20, pady=(10, 5))
#        self.addbandfr.grid_propagate(False)  # fixed size
#
#        # labels
#        bandlbl = ttk.Label(self.addbandfr, text='Band (MHz)')
#        tiltlbl = ttk.Label(self.addbandfr, text='Tilt (°)')
#        gainlbl = ttk.Label(self.addbandfr, text='Gain (dBi)')
#        patlbl = ttk.Label(self.addbandfr, text='Pattern file')
#        bandlbl.grid(row=0, column=0)
#        tiltlbl.grid(row=0, column=1, padx=10)
#        gainlbl.grid(row=0, column=2, padx=10)
#        patlbl.grid(row=0, column=3, padx=10)
#
#        # entries textboxes
#        self.bandtb = ttk.Entry(self.addbandfr, width=8, justify='center')
#        self.tilttb = ttk.Entry(self.addbandfr, width=4, justify='center')
#        self.gaintb = ttk.Entry(self.addbandfr, width=7, justify='center')
#        pattb = ttk.Button(self.addbandfr, width=12, text='Browse .xlsx', command=self.browsepattern)
#        self.bandtb.grid(row=1, column=0)
#        self.tilttb.grid(row=1, column=1, padx=10)
#        self.gaintb.grid(row=1, column=2, padx=10)
#        pattb.grid(row=1, column=3, padx=10)
#
#        editbtn = ttk.Button(self.addbandfr, text="Insert to DB", width=12, command=self.addexisting)
#        editbtn.grid(row=1, column=4, padx=15)
#
#        self.progress = tk.StringVar()
#        proglabel = ttk.Label(self.addbandfr, textvariable=self.progress)
#        proglabel.grid(row=2, column=0, pady=4, columnspan=5, sticky='nw')
#        self.progress.set('Insert antenna and values, then load pattern file.')

    # OTHER METHODS#################################################################################
    def fillantennas(self):
        # antlist = self.cursor.execute('SELECT DISTINCT name FROM antennas ORDER BY name')
        antlist = antennas.index.unique(level='Antenna').tolist()
        for name in antlist:
            self.antlb.insert(tk.END, name[0])

    def filltilt(self, event):
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
            for val in tiltlist:
                self.tiltlb.insert(tk.END, val[0])

            # removed in v2.0
            # self.addbandfr.configure(text="Add band/tilt to: " + self.antennasel)

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

#    def updategains(self):
#        removed in v2.0
#        if self.backupflag == 0:
#            backupname = 'backup_' + datetime.now().strftime('%Y-%m-%d_%H-%M-%S') + '.db'
#            backupconn = sqlite3.connect(backupname)
#            conn.backup(backupconn)
#            backupconn.close()
#            self.backupflag = 1
#            string = 'Antennas backup'
#            logging.info(string)
#
#        for i in self.gains:
#            # i is list of keys (aka bands)
#            if self.gains[i] != 'NA':
#                # get new value from textbox:
#                idx = bands.index(i)
#                newgain = self.tb[idx].get()
#
#                try:
#                    self.cursor.execute('UPDATE antennas SET gain=? WHERE name=? AND band=? AND tilt=?',
#                                        (newgain, self.antennasel, i, self.tiltsel))
#                except sqlite3.IntegrityError as e:
#                    conn.rollback()
#                    self.progress.set("Couldn't update database")
#                    logging.info('Error updating gain to band:' + str(i))
#                    break
#                else:
#                    conn.commit()
#                    string = 'Antenna {}.tilt={} updated gain from {} to {}'.format(self.antennasel, self.tiltsel,
#                                                                                    self.gains[i], newgain)
#                    logging.info(string)

#    def browsepattern(self):
#        msgwindow = tk.Toplevel()
#        msgwindow.configure(background='#D8D8D8')
#
#        if self.bandtb.get().isdigit() and self.tilttb.get().isdigit() and self.gaintb.get().isdigit() and self.antlb.curselection():
#            msg = 'File has to be xlsx with only 2 columns, "A" column with horizontal and "B" with vertical pattern.'
#            flag = True
#        else:
#            flag = False
#            msg = 'Please first select antenna and insert new band, tilt and gain. Then load again'
#
#        label = ttk.Label(msgwindow, text=msg, wraplength=300)
#        label.grid(row=0, column=0, columnspan=1, padx=(20, 20), pady=(10, 5))
#        okbutton = ttk.Button(msgwindow, text='OK', command=lambda: msgwindow.destroy(), width=7)
#        okbutton.grid(row=1, column=0)
#        self.wait_window(msgwindow)
#
#        if flag:
#            Desktop = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop')
#            while True:
#                self.filepath = tk.filedialog.askopenfilename(initialdir=Desktop, title="Select file",
#                                                              filetypes=[("Excel files", "*.xlsx")])
#                self.data = pd.read_excel(self.filepath, header=None)
#                # check if columns had headers
#                if str(self.data.iloc[0, 0]).isdigit() == False:
#                    self.data = self.data.drop(index=0)
#                if self.data.shape[0] >= 360 and self.data.shape[1] == 2:
#                    break
#                else:
#                    msgwindow2 = tk.Toplevel()
#                    msgwindow2.configure(background='#D8D8D8')
#                    label = ttk.Label(msgwindow2, text='Pattern file does not seem right, select another.',
#                                      wraplength=300)
#                    label.grid(row=0, column=0, columnspan=1, padx=(20, 20), pady=(10, 5))
#                    okbutton = ttk.Button(msgwindow2, text='OK', command=lambda: msgwindow2.destroy(), width=7)
#                    okbutton.grid(row=1, column=0)
#                    self.wait_window(msgwindow2)
#
#        self.progress.set('Pattern file loaded succesfully')

#    def addexisting(self):
#        ## removed in v2.0
#        band = self.bandtb.get()
#        tilt = self.tilttb.get()
#        gain = self.gaintb.get()
#        if band.isdigit() and tilt.isdigit() and gain.isdigit() and not self.data.empty and self.antlb.curselection():
#            namestring = (band, self.antennasel, tilt, gain)
#            namestring = '_'.join(namestring)
#            fname = namestring + '.csv'
#            self.data.to_csv(patternspath + fname, sep=',')
#
#            # execute sql command
#            if self.backupflag == 0:
#                backupname = 'backup_' + datetime.now().strftime('%Y-%m-%d_%H-%M-%S') + '.db'
#                backupconn = sqlite3.connect(backupname)
#                conn.backup(backupconn)
#                backupconn.close()
#                logging.info('Antenna backup')
#                self.backupflag = 1
#
#            try:
#                self.cursor.execute('INSERT INTO antennas (band, name, tilt, gain, pattern) VALUES (?,?,?,?,?)',
#                                    (band, self.antennasel, tilt, gain, fname))
#            except sqlite3.IntegrityError as e:
#                self.progress.set('Antenna-Band-Tilt combination already exists')
#                self.data = None
#                self.bandtb.delete(0, tk.END)
#                self.tilttb.delete(0, tk.END)
#                self.gaintb.delete(0, tk.END)
#                band = None
#                tilt = None
#                gain = None
#                conn.rollback()
#            else:
#                string = 'Added {}: band={}, tilt={}, gain={}, '.format(self.antennasel, band, tilt, gain)
#                conn.commit()
#                logging.info(string)
#                self.progress.set(string)
#                self.data = None

    # END OF CLASS###################################################
