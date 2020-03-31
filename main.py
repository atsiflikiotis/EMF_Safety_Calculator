import json
import os
import tkinter as tk
import tkinter.filedialog
import tkinter.ttk as ttk

import matplotlib.pyplot as plt
import numpy as np
from matplotlib import gridspec
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from scipy.interpolate import InterpolatedUnivariateSpline
from scipy.interpolate import RectBivariateSpline

import Antennas_DB as AntDB
import SectorFrame as SecFrame
import plots
import toplevelwindow as tl
from validuser import validation


version = 'v2.0 2020'
bands = AntDB.bands
conn = AntDB.conn


def antennasbrowser():
    antennaswindow = tk.Toplevel()
    antennaswindow.title('Antennas Database')
    antennaswindow.iconbitmap('icon.ico')
    x = root.winfo_x()
    y = root.winfo_y()
    antennaswindow.geometry("+%d+%d" % (x+400, y+200))
    antennasframe = AntDB.AntennasDB(antennaswindow)
    antennasframe.grid(row=0, column=0)


class Main(ttk.Frame):

    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.master = master  # instance attribute
        master.title("EMF SAFETY CALCULATOR")
        master.geometry('1300x800')
        master.iconbitmap('icon.ico')

        menubar = tk.Menu(master)
        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label='Settings', command=self.opensettings)
        filemenu.add_command(label='Antennas DB', command=antennasbrowser)
        filemenu.add_command(label='About', command=about)
        filemenu.add_command(label='Exit', command=self.exit)
        menubar.add_cascade(label='File', menu=filemenu)
        master.config(menu=menubar)

        master.rowconfigure(0, weight=1)
        master.rowconfigure(1, weight=1)
        master.rowconfigure(2, weight=1)
        master.rowconfigure(3, weight=1)

        master.columnconfigure(0, weight=1)
        master.columnconfigure(1, weight=1)
        master.columnconfigure(2, weight=1)
        master.columnconfigure(3, weight=1)

        nb = ttk.Notebook(self.master)
        nb.grid(row=0, column=0, rowspan=11, columnspan=11, sticky='nsew')
        self.page1 = ttk.Frame(nb)
        self.page2 = ttk.Frame(nb)
        nb.add(self.page1, text='Main')
        nb.add(self.page2, text='Image plot')

        self.page1.rowconfigure(0, weight=0)
        self.page1.rowconfigure(1, weight=0)
        self.page1.rowconfigure(2, weight=0)
        self.page1.rowconfigure(3, weight=0)
        self.page1.rowconfigure(4, weight=0)
        self.page1.rowconfigure(5, weight=0)
        self.page1.rowconfigure(6, weight=0)
        self.page1.rowconfigure(7, weight=0)
        self.page1.rowconfigure(8, weight=0)
        self.page1.rowconfigure(9, weight=1)
        self.page1.rowconfigure(10, weight=20)
        self.page1.rowconfigure(11, weight=1)

        self.page1.columnconfigure(0, weight=0)
        self.page1.columnconfigure(1, weight=1)
        self.page2.rowconfigure(0, weight=1)
        self.page2.rowconfigure(1, weight=0)
        self.page2.columnconfigure(0, weight=1)
        self.page2.columnconfigure(1, weight=0)

        self.settingswindow = None
        self.reflbox = None
        self.modelvar = None
        self.limitfactorbox = None

        self.allsectorslist = None
        self.validhgeigh = None

        try:
            with open('settings.json', 'r') as fp:
                self.settings = json.load(fp)
        except FileNotFoundError:
            self.settings = {'model': 0, 'reflcoef': 0.4, 'limitfactor': 0.4}

        # get default settings:
        try:
            self.model = self.settings['model']
            self.reflcoef = self.settings['reflcoef']
            self.limitfactor = self.settings['limitfactor']
        except KeyError:
            self.model = 1
            self.reflcoef = 0.4
            self.limitfactor = 0.4

        # write values depending on preferences
        if self.model == 0:  # freespaceloss
            self.alpha = 1
            self.kappa = 4 * np.pi
            self.gamma = 2
        elif self.model == 1:  # two-ray model
            self.alpha = (1 + self.reflcoef) ** 2
            self.kappa = 4 * np.pi
            self.gamma = 2
        else:  # cost-wi los model
            self.alpha = 1
            self.kappa = 2.08
            self.gamma = 2.6

        self.reflevel = 0
        self.evallevel = 0

        reflevelframe = ttk.Frame(self.page1)
        reflevelframe.grid(row=0, column=0, padx=10, pady=5, sticky='nswe')
        refleveltext = ttk.Label(reflevelframe, text='Reference level (m):')
        refleveltext.grid(row=0, column=0, sticky='nsw', padx=(5, 3), pady=5)
        self.reflevelbox = ttk.Entry(reflevelframe, width=7, justify='center')
        self.reflevelbox.grid(row=0, column=1, padx=3, pady=5, sticky='nsw')
        self.reflevelbox.insert(0, 0)

        # print('default:')
        # print(self.alpha, self.kappa, self.gamma, self.limitfactor)

        self.sectorslist = []
        self.sectorslabels = []
        self.sectorsdeletebtn = []

        # frame1 - sector1
        self.sector1 = SecFrame.SectorFrame(self.page1, 1, self, relief='sunken')
        self.sector1.grid(row=1, column=0, sticky='nsew', padx=10, pady=0, rowspan=9)

        self.frame2 = ttk.LabelFrame(self.page1, text="More sectors", relief='groove')
        self.frame2.grid(row=10, column=0, padx=5, pady=(25, 0), sticky='nsew')

        self.frame3 = tk.Frame(self.frame2)
        self.frame3.grid(row=0, column=0, sticky='nsew')
        self.addsectorbtn = ttk.Button(self.frame3, text="Add sector", command=self.addsector, state='normal')
        self.addsectorbtn.grid(row=0, column=0, columnspan=1, padx=5, pady=5, sticky='ns')

        self.frame4 = tk.Frame(self.frame2)
        self.frame4.grid(row=1, column=0, sticky='nsew', rowspan=6)

        # userframe frame
        userframe = tk.Frame(self.page1)
        userframe.grid(row=11, column=0, sticky='w')
        signlabel = tk.Label(userframe, text='Developed by A. Tsiflikiotis', font=("Helvetica", 7))
        signlabel.grid(row=0, column=0, sticky='w', columnspan=1)

        userlabel = tk.Label(userframe, text='Logged in as: {}'.format(username), font=("Helvetica", 7))
        userlabel.grid(row=0, column=1, sticky='w', columnspan=1, padx=20)

        # calculate button frame
        calcframe = ttk.Frame(self.page1)
        calcframe.grid(row=0, column=1, sticky='nsew', padx=10, pady=5)
        calcframe.columnconfigure(0, weight=1)
        self.plotlinesbtn = ttk.Button(calcframe, text='Plot Lines', command=self.plotlines, width=10)
        self.plotlinesbtn.grid(row=0, column=0, sticky='ns', padx=5, pady=(5, 0))
        # lineplotsframe
        lineplotsframe = ttk.LabelFrame(self.page1, text='Line plots', relief='sunken')
        lineplotsframe.grid(row=1, column=1, sticky='nsew', padx=10, pady=(0, 5), rowspan=10)

        lineplotsframe.rowconfigure(0, weight=0)
        lineplotsframe.rowconfigure(1, weight=1)

        lineplotsframe.columnconfigure(0, weight=0)
        lineplotsframe.columnconfigure(1, weight=1)

        # subframe for direction label
        subframe = ttk.Frame(lineplotsframe)
        subframe.grid(row=0, column=0, sticky='nsew')
        self.directionbox = ttk.Entry(subframe, width=5, justify='center')
        self.directionlbl = ttk.Label(subframe, text='Direction (°):')
        self.directionlbl.grid(row=0, column=2, padx=(20, 4), pady=5, sticky='w')
        self.directionbox.grid(row=0, column=3, padx=(1, 4), pady=5, sticky='w')
        evalleveltext = ttk.Label(subframe, text='Evaluation level (m):')
        evalleveltext.grid(row=0, column=0, padx=(5, 3), pady=5, sticky='w')
        self.evallevelbox = ttk.Entry(subframe, width=7, justify='center')
        self.evallevelbox.grid(row=0, column=1, padx=1, pady=5, sticky='w')
        self.evallevelbox.insert(0, 0)
        subframe.columnconfigure(0, weight=0)
        subframe.columnconfigure(1, weight=0)
        subframe.columnconfigure(2, weight=0)
        subframe.columnconfigure(3, weight=0)

        # subframe for x1, x2 markers
        markersframe = ttk.Frame(lineplotsframe)
        markersframe.grid(row=0, column=2, sticky='nse', padx=5)

        x1markerlbl = ttk.Label(markersframe, text='x1 (m):')
        self.x1markerbox = ttk.Entry(markersframe, width=5, justify='center')
        x2markerlbl = ttk.Label(markersframe, text='x2 (m):')
        self.x2markerbox = ttk.Entry(markersframe, width=5, justify='center')

        x1markerlbl.grid(row=0, column=1, sticky='e', padx=(5, 2), pady=5)
        self.x1markerbox.grid(row=0, column=2, sticky='e', padx=0, pady=5)
        x2markerlbl.grid(row=0, column=3, sticky='e', padx=(10, 2), pady=5)
        self.x2markerbox.grid(row=0, column=4, sticky='e', padx=(0, 5), pady=5)

        # phi markers for horizontal plot
        phi1markerlbl = ttk.Label(markersframe, text='φ1 (°):')
        self.phi1markerbox = ttk.Entry(markersframe, width=4, justify='center')
        phi2markerlbl = ttk.Label(markersframe, text='φ2 (°):')
        self.phi2markerbox = ttk.Entry(markersframe, width=4, justify='center')

        phi1markerlbl.grid(row=0, column=5, sticky='e', padx=(5, 2), pady=5)
        self.phi1markerbox.grid(row=0, column=6, sticky='e', padx=0, pady=5)
        phi2markerlbl.grid(row=0, column=7, sticky='e', padx=(10, 2), pady=5)
        self.phi2markerbox.grid(row=0, column=8, sticky='e', padx=(0, 15), pady=5)

        markersframe.columnconfigure(0, weight=0)
        markersframe.columnconfigure(1, weight=0)
        markersframe.columnconfigure(2, weight=0)
        markersframe.columnconfigure(3, weight=0)
        markersframe.columnconfigure(4, weight=0)

        lineplotsframe.columnconfigure(0, weight=0)
        lineplotsframe.columnconfigure(1, weight=1)
        lineplotsframe.columnconfigure(2, weight=0)

        # plot frame
        plt.style.use('seaborn-darkgrid')
        self.lineplotsfig = plt.figure()
        gridspec.GridSpec(1, 2, width_ratios=[3, 1])
        self.verplotax = plt.subplot(211)
        self.horplotax = plt.subplot(212, projection='polar')
        # self.verplotax.set_title('Vtest')
        self.verplotax.set_title('Vertical plot exposure level vs distance at direction: 0°')
        self.verplotax.set_xlabel('Distance (m)')
        self.verplotax.set_ylabel('Exposure level')

        self.horplotax.set_title('Horizontal plot safety distance')
        #        self.horplotax.set_xlabel('Angle (°)')
        #        self.horplotax.set_ylabel('Rm (m)')
        self.horplotax.set_theta_zero_location("N")
        #        self.horplotax.set_xlim(-180, 180)
        #        self.horplotax.xaxis.set_major_locator(ticker.MultipleLocator(30))
        # verticalfigure.set_size_inches(10,7)
        #         self.verplotax.set_xlim(0, self.radius)
        # self.verplotax.plot(x, y)
        # self.lineplotsfig.tight_layout()
        self.lineplotsfig.subplots_adjust(bottom=0.05, right=0.98, top=0.95, left=0.07, hspace=0.4)
        self.lineplotscanvas = FigureCanvasTkAgg(self.lineplotsfig, lineplotsframe)
        self.lineplotscanvas.get_tk_widget().grid(row=1, column=0, columnspan=3, sticky='nsew')

        # contour-image plot frame
        contourplotframe = ttk.Frame(self.page2, relief='flat')
        contourplotframe.grid(row=0, column=0, sticky='nsew', padx=(10, 10), pady=(5, 5))

        contourplotframe.rowconfigure(0, weight=0)
        contourplotframe.rowconfigure(1, weight=0)
        contourplotframe.rowconfigure(2, weight=0)
        contourplotframe.rowconfigure(3, weight=0)
        contourplotframe.rowconfigure(4, weight=0)
        contourplotframe.rowconfigure(5, weight=50)
        contourplotframe.rowconfigure(6, weight=1)

        contourplotframe.columnconfigure(0, weight=0)
        contourplotframe.columnconfigure(1, weight=0)
        contourplotframe.columnconfigure(2, weight=1)
        contourplotframe.columnconfigure(3, weight=0)

        # add/clear/invert image frame
        addimageframe = tk.Frame(contourplotframe)
        addimageframe.grid(row=0, column=0, sticky='nsew')
        addimagebtn = ttk.Button(addimageframe, text='Add image layer', command=self.addimage, width=15)
        addimagebtn.grid(row=0, column=0, sticky='nw', padx=(5, 5), pady=(15, 5))
        self.clearimagebtn = ttk.Button(addimageframe, text='Clear all', command=self.clearimage, width=10,
                                        state='disabled')
        self.clearimagebtn.grid(row=0, column=1, sticky='nw', padx=(2, 0), pady=(15, 5))
        self.invertimagevar = tk.IntVar()
        self.invertimagevar.set(0)
        self.invertimagebox = ttk.Checkbutton(addimageframe, text='Plot with inverted colors', variable=self.invertimagevar)
        self.invertimagebox.grid(row=1, column=0, columnspan=2, padx=(5, 5), pady=3)

        progressframe = tk.Frame(contourplotframe, height=80, width=150)
        progressframe.grid(row=1, column=0, sticky='nsew', pady=(0, 5))
        progressframe.grid_propagate(0)
        self.progressvar = tk.StringVar()
        self.progressvar.set('Select image and scale to set calculation grid.')
        self.progress = tk.Message(progressframe, textvariable=self.progressvar, width=150)
        self.progress.grid(row=0, column=0, sticky='nsew', pady=(0, 5))

        # scale frame at row 2
        scaleframe = ttk.LabelFrame(contourplotframe, text='Scale image to real size', width=150, height=125)
        scaleframe.grid_propagate(0)
        scaleframe.grid(row=2, column=0, sticky='nsew', pady=(20, 15))

        point1label = ttk.Label(scaleframe, text='Point A:')
        point1label.grid(row=0, column=0, sticky='nsw', padx=(5, 0), pady=(3, 0))
        self.point1var = tk.StringVar()
        point1coord = tk.Label(scaleframe, textvariable=self.point1var)
        self.point1var.set('None')
        point1coord.grid(row=0, column=1, sticky='nsw', padx=1, pady=(3, 0))

        point2label = tk.Label(scaleframe, text='Point B:')
        point2label.grid(row=1, column=0, sticky='nsw', padx=(5, 0), pady=(3, 0))
        self.point2var = tk.StringVar()
        point2coord = tk.Label(scaleframe, textvariable=self.point2var)
        self.point2var.set('None')
        point2coord.grid(row=1, column=1, sticky='nsw', padx=1, pady=(3, 0))

        distlabel = tk.Label(scaleframe, text='d(A,B) (m):')
        distlabel.grid(row=2, column=0, sticky='nsw', padx=(5, 0), pady=(5, 0))
        self.distentry = ttk.Entry(scaleframe, width=5, justify='center', state='disabled')
        self.distentry.grid(row=2, column=1, padx=(5, 0), sticky='sw')
        self.scalebtn = ttk.Button(scaleframe, text='Scale image', command=self.scaleimagedistance, state='disabled')
        self.scalebtn.grid(row=3, column=0, padx=(5, 0), pady=(3, 3))
        self.resetbtn = ttk.Button(scaleframe, text='Reset points', command=self.resetpoints, state='disabled')
        self.resetbtn.grid(row=3, column=1, padx=(3, 0), pady=(3, 3))

        # set BS position frame row 3
        bspositionframe = tk.LabelFrame(contourplotframe, text='BS position at grid', width=150, height=80)
        bspositionframe.grid_propagate(0)
        bspositionframe.grid(row=3, column=0, rowspan=1, sticky='nsew', pady=(10, 0))

        bspositionlbl = tk.Label(bspositionframe, text='BS position: ')
        self.bspositionvar = tk.StringVar()
        self.bspositionlbl = tk.Label(bspositionframe, textvariable=self.bspositionvar)
        self.confirmbspositionbtn = ttk.Button(bspositionframe, text='Confirm', command=self.confirmbsposition,
                                               state='disabled', width=8)

        bspositionlbl.grid(row=0, column=0, sticky='nsw', padx=(5, 0), pady=(5, 0))
        self.bspositionlbl.grid(row=0, column=1, sticky='sw', padx=(5, 0), pady=(5, 0))
        self.confirmbspositionbtn.grid(row=2, column=0, padx=(3, 0), pady=(5, 3), sticky='nsew')

        # threshold level and button frame at row 4
        reflevelframe2 = tk.Frame(contourplotframe)
        reflevelframe2.grid(row=4, column=0, rowspan=1, sticky='nsew', pady=(20, 0))

        thresholdlbl = tk.Message(reflevelframe2, text='Highlite exposure values greater than:', width=150)
        thresholdlbl.grid(row=0, column=0, sticky='nsw', padx=(3, 3), pady=(3, 0))
        self.thresholdlevelbox = ttk.Spinbox(reflevelframe2, from_=0, to_=0.9, increment=0.1, width=6, justify='center')
        self.thresholdlevelbox.insert(0, 0.8)
        self.thresholdlevelbox.grid(row=0, column=1, sticky='w', padx=1, pady=(3, 0))
        self.lowlevelsplotvar = tk.IntVar(0)
        lowlevelsplotbtn = ttk.Checkbutton(reflevelframe2, text='Plot low exposure levels', onvalue=1, offvalue=0,
                                           variable=self.lowlevelsplotvar)
        lowlevelsplotbtn.grid(row=2, column=0, padx=(3, 3), pady=(3, 0), columnspan=2)

        evallevel2text = ttk.Label(reflevelframe2, text='Evaluation level (m):')
        evallevel2text.grid(row=3, column=0, padx=(5, 3), pady=(30, 0), sticky='nsw')
        self.evallevel2box = ttk.Entry(reflevelframe2, width=7, justify='center')
        self.evallevel2box.grid(row=3, column=1, padx=1, pady=(30, 0), sticky='nsw')
        self.evallevel2box.insert(0, 0)

        self.contourplotbtn = ttk.Button(reflevelframe2, text='Plot grid', command=lambda: plots.contourplot(self),
                                         width=15, state='disabled')
        self.contourplotbtn.grid(row=4, column=0, pady=(2, 5), padx=5, sticky='nw')

        self.contourplotfig, self.contourplotax = plt.subplots(1, 1)
        # self.contourplotfig.set_size_inches(7,7)
        self.contourplotax.grid(None)
        self.contourplotfig.set_facecolor('#f0f0f0')
        self.contourplotax.set_title('Exposure level contour plot in BS area')
        # self.contourplotax.set_xlabel('x (m)')
        # self.contourplotax.set_ylabel('y (m)')
        self.contourplotcanvas = FigureCanvasTkAgg(self.contourplotfig, contourplotframe)

        self.contourplotcanvas.get_tk_widget().grid(row=0, column=2, columnspan=2, rowspan=15, sticky='nsew')

        self.cb = None
        self.contourplotfig.subplots_adjust(bottom=0.05, right=0.95, top=0.95, left=0.05)
        # self.lineplotsfig.tight_layout()

        master.protocol("WM_DELETE_WINDOW", self.exit)

    # ###METHODS###################
    def writesectors(self):
        self.sectorslabels = []
        self.sectorsdeletebtn = []

        for i, sector in enumerate(self.sectorslist):
            sectorid = i + 2
            self.sectorslabels.append(ttk.Label(self.frame4,
                                                text='Sector {}: {}, Azim.={}, M.Tilt={}, Mid height={}'.format(
                                                    sectorid, sector.antennasel, sector.azimuth, sector.mechtilt,
                                                    sector.antheight)))
            self.sectorslabels[i].grid(row=i, column=0, padx=5, pady=5, sticky='w', columnspan=4)
            self.sectorsdeletebtn.append(
                ttk.Button(self.frame4, text='Delete Sector', command=lambda var=i: self.deletesector(var)))
            self.sectorsdeletebtn[i].grid(row=i, column=4, padx=5, pady=5)

    def deletesector(self, i):
        # delete all ui instances:
        # for i in range(len(self.sectorslabels)):
        #     self.sectorslabels[i].grid_forget()
        #     self.sectorsdeletebtn[i].grid_forget()

        self.frame4.grid_forget()

        self.frame4 = tk.Frame(self.frame2)
        self.frame4.grid(row=1, column=0, sticky='nsew', rowspan=6)

        self.sectorslabels = []
        self.sectorsdeletebtn = []

        self.sectorslist.pop(i)
        # self.sectorslist = list(filter(None, self.sectorslist))
        if len(self.sectorslist) > 0:
            self.writesectors()

    def addsector(self):
        self.getsector1()
        count = len(self.sectorslist)

        newwindow = tk.Toplevel()
        x = self.master.winfo_x()
        y = self.master.winfo_y()
        newwindow.geometry("+%d+%d" % (x+400, y+300))
        newwindow.title('Add new sector')
        newwindow.iconbitmap('icon.ico')
        sector = SecFrame.SectorFrame(newwindow, count + 2, self, parentsector=self.sector1)
        sector.grid(row=0, column=0, sticky='nsew', padx=10, pady=5, rowspan=5)

    def opensettings(self):
        self.settingswindow = tk.Toplevel()
        self.settingswindow.title('Settings')
        x = self.master.winfo_x()
        y = self.master.winfo_y()
        self.settingswindow.geometry("+%d+%d" % (x + 400, y + 300))

        self.settingswindow.iconbitmap('icon.ico')
        self.modelvar = tk.IntVar()
        modelframe = ttk.LabelFrame(self.settingswindow, text='Propagation model')
        modelframe.grid(row=0, column=0, padx=10, pady=10)
        model1rb = ttk.Radiobutton(modelframe, text='Free space loss', value=0, variable=self.modelvar)
        model2rb = ttk.Radiobutton(modelframe, text='Two-Ray model', value=1, variable=self.modelvar)
        model3rb = ttk.Radiobutton(modelframe, text='LOS COST-WI model (for reference only, d>20m)', value=2,
                                   variable=self.modelvar)
        self.modelvar.set(self.model)
        model1rb.grid(row=1, column=0, columnspan=1, padx=3, sticky='nsw')
        model2rb.grid(row=2, column=0, columnspan=1, padx=3, sticky='nsw')
        model3rb.grid(row=3, column=0, columnspan=1, padx=3, sticky='nsw')

        refllbl = tk.Label(modelframe, text='Reflection coef. |Γ|:')
        refllbl.grid(row=2, column=1, padx=7, sticky='nsw', columnspan=2)
        self.reflbox = tk.Spinbox(modelframe, from_=0, to=1, increment=0.1, width=5, readonlybackground='white',
                                  justify='center')
        self.reflbox.grid(row=2, column=3, padx=0, sticky='nsw', columnspan=1)
        self.reflbox.delete(0, tk.END)
        self.reflbox.insert(0, self.reflcoef)
        self.reflbox.config(state='readonly')
        # limit reduction factor
        limitframe = ttk.LabelFrame(self.settingswindow, text='ICNIRP Limits')
        limitframe.grid(row=1, column=0, padx=10, pady=10, sticky='nsew')
        text1 = ttk.Label(limitframe, text='Limit reduction factor (%):')
        self.limitfactorbox = ttk.Entry(limitframe, width=5, justify='center')
        text1.grid(row=0, column=0, sticky='nsw', padx=(5, 5), pady=(5, 5))
        self.limitfactorbox.grid(row=0, column=1, sticky='nsw', padx=(5, 5), pady=(5, 5))
        self.limitfactorbox.delete(0, tk.END)
        self.limitfactorbox.insert(0, self.limitfactor * 100)
        submitsettingsbtn = ttk.Button(self.settingswindow, text='Save', command=self.submitsettings)
        submitsettingsbtn.grid(row=3, column=0, pady=20)

        # incrementtext = ttk.Label(gridframe, text='Increment (m): ')
        # incrementtext.grid(row=0, column=2, sticky='nsw', padx=(35, 5), pady=(5, 5))
        # self.incrementbox = ttk.Entry(gridframe, width=5, justify='center')
        # self.incrementbox.grid(row=0, column=3, sticky='nsw', padx=(5, 5), pady=(5, 5))
        # self.incrementbox.delete(0, tk.END)
        # self.incrementbox.insert(0, 0.1)

    def limit(self, band):  # f is in MHz
        if band < 400:
            return (1 - self.limitfactor) * 2
        elif band < 2000:
            return (1 - self.limitfactor) * band / 200
        else:
            return (1 - self.limitfactor) * 10

    def submitsettings(self):
        self.model = self.modelvar.get()
        self.settings['model'] = self.model
        self.limitfactor = 0.01 * float(self.limitfactorbox.get())
        self.settings['limitfactor'] = self.limitfactor

        if self.model == 0:
            # freespace
            self.alpha = 1
            self.kappa = 4 * np.pi
            self.gamma = 2
            self.settingswindow.destroy()
        elif self.model == 1:
            # two-ray
            self.reflcoef = float(self.reflbox.get())
            self.settings['reflcoef'] = self.reflcoef
            self.alpha = (1 + self.reflcoef) ** 2
            self.kappa = 4 * np.pi
            self.gamma = 2
            self.settingswindow.destroy()
        else:
            # los cost-wi model
            self.alpha = 1
            self.kappa = 2.08
            self.gamma = 2.6
            self.settingswindow.destroy()

        with open('settings.json', 'w') as fp:
            json.dump(self.settings, fp)

    def exit(self):
        self.master.quit()
        self.master.destroy()

    def s(self, p, g, r):
        return self.alpha * p * 10 ** (0.1 * g) / (self.kappa * r ** self.gamma)

    def checkheight(self):
        self.allsectorslist = [self.sector1] + self.sectorslist
        # check min evaluation level:
        minheight = 1e10
        for sec in self.allsectorslist:
            if sec.antheight < minheight:
                minheight = sec.antheight
        
        threshold = 0.5
        maxevallevel = minheight + self.reflevel - 2 - threshold
        return maxevallevel

    def get_grid(self):
        # get levels from main tab buttons
        self.getsector1()
        
        try:
            self.reflevel = float(self.reflevelbox.get())
        except ValueError:
            tl.popupmessage(self.master, "Value error", "Invalid number for reference level, reverting to 0 value", 200)
            self.reflevel = 0
            self.reflevelbox.delete(0, tk.END)
            self.reflevelbox.insert(0, 0)
        
        # get all sectors and max valid eval height
        maxevallevel = self.checkheight()
        
        try:
            self.evallevel = float(self.evallevelbox.get())
            if self.evallevel > maxevallevel:
                tl.popupmessage(self.master, "Evaluation level error", 
                                f"Evaluation level is not low enough to perfmorm vertical pattern analysis, setting "
                                f"evaluation level to maximum valid value = {maxevallevel}m.", 200)
                self.evallevel = maxevallevel
                self.evallevelbox.delete(0, tk.END)
                self.evallevelbox.insert(0, maxevallevel)
        except ValueError:
            if self.reflevel <= maxevallevel:
                tl.popupmessage(self.master, "Value error", 
                                f"Invalid number for evaluation level, setting equal to reference level = "
                                f"{self.reflevel}m", 200)

                self.evallevel = self.reflevel
                self.evallevelbox.delete(0, tk.END)
                self.evallevelbox.insert(0, self.reflevel)
            else:
                tl.popupmessage(self.master, "Value error", 
                                f"Invalid number for evaluation level, setting equal to "
                                f"maximum valid evaluation level value: {maxevallevel}m", 200)
                self.evallevel = maxevallevel
                self.evallevelbox.delete(0, tk.END)
                self.evallevelbox.insert(0, maxevallevel)
        

        self.evallevel2box.delete(0, tk.END)
        self.evallevel2box.insert(0, self.evallevel)


    def reget_grid(self):
        # get levels from contourplot buttons
        
        self.getsector1()
        
        try:
            self.reflevel = float(self.reflevelbox.get())
        except ValueError:
            tl.popupmessage(self.master, "Value error", "Invalid number for reference level, reverting to 0 value", 200)
            self.reflevel = 0
            self.reflevelbox.delete(0, tk.END)
            self.reflevelbox.insert(0, 0)
            
        # get all sectors and max valid eval height
        maxevallevel = self.checkheight()
        
        
        # get evaluation level from box in image plot tab
        try:
            self.evallevel = float(self.evallevel2box.get())
            if self.evallevel > maxevallevel:
                tl.popupmessage(self.master, "Evaluation level error", f"Evaluation level is not low enough to perfmorm vertical pattern analysis, setting evaluation level to maximum valid value = {maxevallevel}m.", 200)
                self.evallevel = maxevallevel
                self.evallevel2box.delete(0, tk.END)
                self.evallevel2box.insert(0, maxevallevel)
        except ValueError:
            if self.reflevel <= maxevallevel:
                tl.popupmessage(self.master, "Value error", f"Invalid number for evaluation level, setting equal to reference level value = {self.reflevel}m", 200)
                self.evallevel = self.reflevel
                self.evallevel2box.delete(0, tk.END)
                self.evallevel2box.insert(0, self.reflevel)
            else:
                tl.popupmessage(self.master, "Value error", "Invalid number for evaluation level, setting equal to maximum valid evaluation level value = {maxevallevel}m", 200)
                self.evallevel = maxevallevel
                self.evallevel2box.delete(0, tk.END)
                self.evallevel2box.insert(0, maxevallevel)

        self.evallevelbox.delete(0, tk.END)
        self.evallevelbox.insert(0, self.evallevel)

        self.construct_grid_from_levels()

    def construct_grid_from_levels(self):
        h = self.sector1.antheight + self.reflevel - self.evallevel - 2

        # self.bsxposition = 0
        # self.bsyposition = 0
        thetaxstart = -np.arctan2(self.sidex / 2 + self.bsxposition, h) * 180 / np.pi  # must be negative
        thetaxend = np.arctan2(self.sidex / 2 - self.bsxposition, h) * 180 / np.pi  # must be positive
        thetaystart = -np.arctan2(self.sidey / 2 - self.bsyposition, h) * 180 / np.pi
        thetayend = np.arctan2(self.sidey / 2 + self.bsyposition, h) * 180 / np.pi

        self.x = h * np.tan(np.linspace(thetaxstart, thetaxend, int(np.ceil(thetaxend - thetaxstart))) * np.pi / 180)
        self.y = h * np.tan(np.linspace(thetaystart, thetayend, int(np.ceil(thetayend - thetaystart))) * np.pi / 180)

        self.xx, self.yy = np.meshgrid(self.x, -self.y, indexing='xy', sparse='false')
        self.size = (np.size(self.yy), np.size(self.xx))
        self.rho = np.sqrt(self.xx ** 2 + self.yy ** 2)
        self.phi = np.arctan2(self.xx, self.yy) * 180 / np.pi
        #get phi angles to 0.1degrees accuracy
        self.phi = np.round(self.phi, 1)

    def lineargrid(self):
        # make linear and finer grid
        f1 = RectBivariateSpline(self.y, self.x, self.totaldepps, kx=2, ky=2)

        # xcoord = np.linspace(-self.radius, self.radius, self.size2 + 1)
        # ycoord = xcoord
        # test with x0,y0
        self.xcoord = np.linspace(self.x[0], self.x[-1], 15 * np.size(self.x))
        self.ycoord = np.linspace(self.y[0], self.y[-1], 15 * np.size(self.y))

        self.xx2, self.yy2 = np.meshgrid(self.xcoord, -self.ycoord, indexing='xy', sparse='false')
        self.rho2 = np.sqrt(self.xx2 ** 2 + self.yy2 ** 2)
        self.phi2 = np.arctan2(self.xx2, self.yy2) * 180 / np.pi
        self.phi2[self.phi2 < 0] = self.phi2[self.phi2 < 0] + 360

        self.zvalues = f1(self.ycoord, self.xcoord).astype('float32')

    def totaldeppsgrid(self):
        self.totaldepps = np.full(self.size, 0.0)
        for sec in self.allsectorslist:
            self.sectordepps(sec)
            self.totaldepps = self.totaldepps + sec.depps

        self.lineargrid()

    def sectordepps(self, sector):
        # calculate depps per sector and return
        heightvalue = sector.antheight + self.reflevel - self.evallevel - 2

        sector.height = np.full(self.size, heightvalue)

        #        sector.rho[int(self.size / 2) + 1:, :] = -self.rho[int(self.size / 2) + 1:, :]

        sector.phi = self.phi - sector.azimuth

        sector.phi[sector.phi < 0] = sector.phi[sector.phi < 0] + 360
        sector.phi[(sector.phi > 359) & (sector.phi < 360)] = 0

        maskbehind = (sector.phi > 90) & (sector.phi < 270)  # behind antenna
        # maskfront = np.logical_not(maskbehind)    #in front of antenna

        # round to 1 decimal of phi and theta
        sector.phi = np.round(sector.phi, 1)
        sector.theta = np.round(np.arctan2(sector.height, self.rho) * 180 / np.pi, 1)

        sector.theta[maskbehind] = 180 - sector.theta[maskbehind]

        sector.theta = sector.theta - sector.mechtilt

        sector.theta[sector.theta < 0] = sector.theta[sector.theta < 0] + 360


        sector.R = np.sqrt(sector.height ** 2 + self.rho ** 2)
        sector.depps = np.full(self.size, 0.0)

        for band in bands:

            power = sector.totpower[band]
            if sector.totpower[band] > 0:
                # initialize with zeros
                sector.powerdensity[band] = np.full(self.size, 0.0)
                sector.banddepps[band] = np.full(self.size, 0.0)
                sector.gainatten[band] = np.full(self.size, 0.0)
                # interpolate patterns from 1degree step to 0.1degrees step
                # horizontal:
                f1 = InterpolatedUnivariateSpline(np.linspace(0, 360, 361), sector.horizontal[band], k=1)
                ihorizontal = f1(np.linspace(0, 360, 3601))
                # vertical
                f2 = InterpolatedUnivariateSpline(np.linspace(0, 360, 361), sector.vertical[band], k=1)
                ivertical = f2(np.linspace(0, 360, 3601))

                for i in range(self.size[0]):
                    for j in range(self.size[1]):
                        sector.gainatten[band][i, j] = sector.gain[band] - \
                                                       ihorizontal[int(10 * sector.phi[i, j])] - \
                                                       ivertical[int(10 * sector.theta[i, j])]

                        sector.powerdensity[band][i, j] = self.s(power, sector.gainatten[band][i, j],
                                                                 sector.R[i, j])

                sector.banddepps[band] = sector.powerdensity[band] / self.limit(band)
                sector.depps = sector.depps + sector.banddepps[band]
            else:
                sector.banddepps[band] = np.full(self.size, 0.0)

    def plotlines(self):
        self.plotlinesbtn.config(state='disabled', text='Progressing..')

        self.get_grid()

        if sum(self.sector1.totpower.values()):
            plots.horizontalplot(self)
            plots.verticalplot(self)
        else:
            tl.popupmessage(self.master, 'No power',
                            "Power error: Enter values for sector 1 that produce total power greater than 0.", 200)

        self.plotlinesbtn.config(state='normal', text='Plot Lines')

    def verticalvalues(self, angle, level):

        if angle < 0:
            angle += 360

        # get grid according to antenna with lowest height (more critical)
        # Ho = 1e5
        # for sector in self.allsectorslist:
        #     if Ho > sector.antheight:
        #         Ho = sector.antheight

        # correct height with reference level, evalluation level and 2m human height

        xinterp = np.arange(0, self.maxdistance + 0.05, 0.05)
        yinterp = np.zeros_like(xinterp)

        for sector in self.allsectorslist:
            Ho = sector.antheight + self.reflevel - level - 2
            thetaxend = np.arctan2(self.maxdistance, Ho) * 180 / np.pi
            thetaxmax = int(np.ceil(thetaxend))
            xvalues = (Ho * np.tan(np.arange(thetaxmax + 1) * np.pi / 180))
            H = np.full_like(xvalues, Ho)
            sectortheta = np.round(np.arctan2(H, xvalues) * 180 / np.pi).astype(int) - sector.mechtilt
            linedepps = np.zeros_like(xvalues)
            R = np.sqrt(H ** 2 + xvalues ** 2)
            for band in bands:

                power = sector.totpower[band]
                if sector.totpower[band] > 0:
                    # initialize with zeros
                    powerdensity = np.zeros_like(xvalues)
                    banddepps = np.zeros_like(xvalues)
                    gainatten = np.zeros_like(xvalues)
                    for i in range(len(sectortheta)):
                        gainatten[i] = sector.gain[band] - sector.horizontal[band][sector.azimuth - angle] - \
                                       sector.vertical[band][sectortheta[i]]

                        powerdensity[i] = self.s(power, gainatten[i], R[i])

                    banddepps = powerdensity / self.limit(band)
                    linedepps = linedepps + banddepps

            fvertical = InterpolatedUnivariateSpline(xvalues, linedepps, k=2)
            yinterp += fvertical(xinterp)

        return xinterp, yinterp

    def horizontalsafety(self, phi):
        sum_ = 0
        for band in bands:
            rmband = 0
            for sector in self.allsectorslist:
                if sector.totpower[band] > 0:
                    phisector = phi - sector.azimuth  # need to change variable not keep phi again. why?

                    if phisector < 0:
                        phisector += 360

                    gain = sector.gain[band] - sector.horizontal[band][phisector]
                    rmsectorband = self.alpha * sector.totpower[band] * 10 ** (0.1 * gain) / self.kappa
                else:
                    rmsectorband = 0.0
                rmband += rmsectorband

            rmband = rmband / self.limit(band)
            sum_ += rmband
        return sum_ ** (1 / self.gamma)


    def addimage(self):
        cwd = os.getcwd()
        filepath = tk.filedialog.askopenfilename(initialdir=cwd, title="Select file",
                                                 filetypes=[("Png image", "*.png"), ("JPEG image", "*.jpg")])

        self.img = plt.imread(filepath)
        
        if self.invertimagevar.get():
            self.img = plots.invertimage(self.img)
        
        self.invertimagebox.config(state='disabled')
            
        self.contourplotax.imshow(self.img, interpolation='bicubic')
        self.contourplotcanvas.draw()

        self.progressvar.set('Select points and distance to scale')
        tl.popupmessage(self.master, 'Next step:', 'Select points on image and enter distance to scale', 250)
        self.scaleimage()
        self.clearimagebtn.config(state='normal')

    def clearimage(self):
        self.contourplotax.cla()
        self.clearimagebtn.config(state='disabled')
        self.progressvar.set('Select image and scale to set calculation grid.')
        self.contourplotax.grid(None)
        self.contourplotfig.set_facecolor('#f0f0f0')
        self.resetpoints()
        self.clearimagebtn.config(state='disabled')
        self.distentry.config(state='disabled')
        self.bspositionvar.set('')
        self.confirmbspositionbtn.config(state='disabled')
        self.invertimagebox.config(state='normal')
        global cid2
        fig = self.contourplotfig
        fig.canvas.mpl_disconnect(cid2)

        if self.cb is not None:
            self.cb.remove()


        global bscoords
        if bscoords:
            self.bsmarker.remove()
            self.bsmarkertext.remove()

        self.contourplotcanvas.draw()

    def scaleimage(self):
        fig = self.contourplotfig
        canvas = self.contourplotcanvas
        global cid
        global coords
        coords = []
        cid = fig.canvas.mpl_connect('button_press_event', self.clicktoscale)

    def scaleimagedistance(self):
        distab = self.distentry.get()
        if len(distab) == 0 or float(distab) <= 0:
            tl.popupmessage(self.master, 'Error', 'You have to enter a valid distance for points A to B', 200)
        else:
            global coords
            pointsdistance = np.sqrt((coords[0][0] - coords[1][0]) ** 2 + (coords[0][1] - coords[1][1]) ** 2)
            self.scalefactor = float(distab) / pointsdistance
            imgy = np.shape(self.img)[0]
            imgx = np.shape(self.img)[1]
            self.xlimit = imgx * self.scalefactor / 2
            self.ylimit = imgy * self.scalefactor / 2
            self.sidex = 2 * self.xlimit
            self.sidey = 2 * self.ylimit
            self.contourplotax.set_xlabel('x (m)')
            self.contourplotax.set_ylabel('y (m)')
            self.contourplotax.set_xticks([0, imgx / 2, imgx])
            self.contourplotax.set_yticks([imgy, imgy / 2, 0])
            self.contourplotax.set_xticklabels(["{:.2f}".format(-self.xlimit), 0, "{:.2f}".format(self.xlimit)])
            self.contourplotax.set_yticklabels(["{:.2f}".format(-self.ylimit), 0, "{:.2f}".format(self.ylimit)])
            self.p1.remove()
            self.p2.remove()
            self.an1.remove()
            self.an2.remove()
            self.line1.pop(0).remove()
            coords = []
            self.scalebtn.config(state='disabled')
            self.contourplotcanvas.draw()
            self.resetbtn.config(state='disabled')
            self.progressvar.set('Select BS position on image')
            tl.popupmessage(self.master, 'Next step', 'Image scaled, now select BS position on image.', 250)
            self.setbsposition()

    def resetpoints(self):
        fig = self.contourplotfig
        canvas = self.contourplotcanvas
        global coords
        global cid

        self.point1var.set('None')
        self.point2var.set('None')
        
        if len(coords) > 0:
            self.p1.remove()
            self.an1.remove()
        
        if len(coords) > 1:
            self.p2.remove()
            self.an2.remove()
            self.line1.pop(0).remove()
        
        self.contourplotcanvas.draw()
        coords = []
        cid = fig.canvas.mpl_connect('button_press_event', self.clicktoscale)
        self.resetbtn.config(state='disabled')
        self.scalebtn.config(state='disabled')
        self.distentry.delete(0, tk.END)
        self.contourplotcanvas.draw()

    def clicktoscale(self, event):
        fig = self.contourplotfig
        # canvas = self.contourplotcanvas

        ix, iy = event.xdata, event.ydata

        global coords

        coords.append((ix, iy))

        if len(coords) == 1:
            self.resetbtn.config(state='normal')
            self.point1var.set('({:d}, {:d})'.format(int(coords[0][0]), int(coords[0][1])))
            self.p1 = self.contourplotax.scatter(ix, iy, c='blue', edgecolors='red')
            self.an1 = self.contourplotax.annotate('A', (ix, iy), xytext=(5 + ix, iy - 5))
            self.contourplotcanvas.draw()

        global cid
        if len(coords) == 2:
            self.point2var.set('({:d}, {:d})'.format(int(coords[1][0]), int(coords[1][1])))
            self.p2 = self.contourplotax.scatter(ix, iy, c='blue', edgecolors='red')
            self.an2 = self.contourplotax.annotate('B', (ix, iy), xytext=(5 + ix, iy - 5))
            self.line1 = self.contourplotax.plot([coords[0][0], coords[1][0]], [coords[0][1], coords[1][1]])
            fig.canvas.mpl_disconnect(cid)
            self.scalebtn.config(state='normal')
            self.distentry.config(state='normal')
            self.contourplotcanvas.draw()

    def setbsposition(self):
        fig = self.contourplotfig
        canvas = self.contourplotcanvas
        global cid2
        global bscoords
        bscoords = []
        cid2 = fig.canvas.mpl_connect('button_press_event', self.clickbsposition)

    def clickbsposition(self, event):
        fig = self.contourplotfig
        # canvas = self.contourplotcanvas

        ix2, iy2 = event.xdata, event.ydata

        global bscoords
        if bscoords:
            self.bsmarker.remove()
            self.bsmarkertext.remove()

        bscoords = []
        self.bsxposition = ix2 * self.scalefactor - self.xlimit
        self.bsyposition = -iy2 * self.scalefactor + self.ylimit
        # refine bsposition to grid for accuracy 0.05
        # xgrid = np.linspace(-self.xlimit, self.xlimit, 20 * self.sidex + 1)
        # ygrid = np.linspace(-self.ylimit, self.ylimit, 20 * self.sidex + 1)
        # self.bsxposition = xgrid[np.argmin(abs(self.bsxposition - xgrid))]
        # self.bsyposition = ygrid[np.argmin(abs(self.bsyposition - ygrid))]

        bscoords.append((self.bsxposition, self.bsyposition))

        self.confirmbspositionbtn.config(state='normal')
        self.bspositionvar.set('({:.2f}, {:.2f})'.format(bscoords[0][0], bscoords[0][1]))
        self.bsmarker = self.contourplotax.scatter(ix2, iy2, c='green', edgecolors='white')
        self.bsmarkertext = self.contourplotax.annotate('BS', (ix2, iy2), xytext=(5 + ix2, iy2 - 5), c='white')

        self.contourplotcanvas.draw()

    def confirmbsposition(self):
        global cid2
        fig = self.contourplotfig
        fig.canvas.mpl_disconnect(cid2)
        self.contourplotbtn.config(state='normal')
        self.progressvar.set('Insert desired evaluation height and plot grid.')
        self.confirmbspositionbtn.config(state='disabled')

    def getsector1(self):
        if len(self.sector1.azimtext.get()) == 0 or len(self.sector1.mechtilttext.get()) == 0 or len(
                self.sector1.midheighttext.get()) == 0:
            tl.popupmessage(self.master, 'Error', 'Please fill all required values then submit antenna.', 250)
        else:
            # final values
            self.sector1.azimuth = int(self.sector1.azimtext.get())
            if self.sector1.azimuth < 0:
                self.sector1.azimuth += 360
            self.sector1.mechtilt = int(self.sector1.mechtilttext.get())
            self.sector1.antheight = float(self.sector1.midheighttext.get())
            for i in range(len(bands)):
                self.sector1.totpower[bands[i]] = self.sector1.totpowervar[bands[i]].get()
                # split horizontal and vertical after roll to vertical
                if bands[i] in self.sector1.supbandslist:
                    self.sector1.gain[bands[i]] = float(self.sector1.gainsvar[bands[i]].get())
                    self.sector1.horizontal[bands[i]] = self.sector1.patterns[bands[i]][:, 0]
                    self.sector1.vertical[bands[i]] = self.sector1.patterns[bands[i]][:, 1]


def quit_me():
    root.quit()
    root.destroy()

def about():
    aboutwindow = tk.Toplevel()
    aboutwindow.title('Licence')
    aboutwindow.iconbitmap('icon.ico')
    x = root.winfo_x()
    y = root.winfo_y()
    aboutwindow.geometry("+%d+%d" % (x+400, y+200))
    try:
        with open('LICENSE.md', 'r') as file:
            text = file.read()
    except FileNotFoundError:
        text = "License file cannot be found."
    else:
        pass

    tk.Message(aboutwindow, text=version, aspect=1000).grid(row=0, column=0, padx=5, pady=10, sticky='nw')
    tk.Message(aboutwindow, text=text, aspect=1000).grid(row=1, column=0, padx=5, pady=10, sticky='nw')


if __name__ == '__main__':
    answer, username = validation()
    if answer == 'pass':
        root = tk.Tk()
        root.protocol("WM_DELETE_WINDOW", quit_me)
        s = ttk.Style()
        s.theme_use('vista')
        mainapp = Main(root)
        root.mainloop()
    elif len(answer) > 1:
        loginwindow = tk.Tk()
        s1 = ttk.Style()
        s1.theme_use('vista')
        loginwindow.title("LOGIN")
        loginwindow.geometry('300x200')
        loginwindow.iconbitmap('icon.ico')
        loginwindow.rowconfigure(0, weight=1)
        loginwindow.columnconfigure(0, weight=1)
        tk.Message(loginwindow, text=answer, width=200, justify='center').grid(row=0, column=0,
                                                                                     padx=10, pady=10)
        loginwindow.mainloop()
    else:
        pass


