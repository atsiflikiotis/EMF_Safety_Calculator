import pandas as pd
from pathlib import Path
import numpy as np
import scipy.signal as signal

# define folder containg csv files.
# Each csv file contains horizontal and vertical radiation pattern in columns (0, 1) respectively, and follow the
# filename format "BAND_ANTENNANAME_ELTILT_MAXGAIN.csv"
# example file patterns are located in '\pattern' folder
folder = Path.joinpath(Path.cwd(), "patterns")
files = folder.glob("*.csv")

# check if antennas df already exists:
file = 'antennas_df.hdf'
fpath = Path.joinpath(Path.cwd(), file)

if fpath.is_file():
    antennas = pd.read_hdf('antennas_df.hdf', key='antennasdb')
else:
    # create new dataframe:
    antennas = pd.DataFrame(columns=['Antenna', 'Band', 'Tilt', 'Gain', 'HorBW', 'VerBW',
                                     'sidelobe', 'theta_s', 'phi10', 'phi20', 'Pattern'])
    antennas.set_index(['Antenna', 'Band', 'Tilt'], inplace=True)


for file in files:
    fnamesplit = file.stem.split('_')
    band = float(fnamesplit[0])
    antenna = fnamesplit[1]
    tiltval = float(fnamesplit[2])
    gainval = float(fnamesplit[3])
    pattern = np.genfromtxt(file, 'float32', delimiter=';')
    horbw = float(np.sum((pattern[:, 0] < 3)))
    verbw = float(np.sum((pattern[:, 1] < 3)))
    phi10 = float(np.sum((pattern[:, 0] < 10)))
    phi20 = float(np.sum((pattern[:, 0] < 20)))
    try:
        verticalnorm = gainval - pattern[:, 1]
        peaks, _ = signal.find_peaks(verticalnorm, [None, gainval - 3.1], prominence=1)
        sidelobe = np.max(verticalnorm[peaks])
        theta_s = float(np.sum((verticalnorm >= sidelobe)))
    except:
        sidelobe = np.nan
        theta_s = np.nan
    temp_series = pd.Series({'Gain': gainval, 'HorBW': horbw, 'VerBW': verbw, 'sidelobe': sidelobe,
                             'theta_s': theta_s, 'phi10': phi10, 'phi20': phi20, 'Pattern': pattern})
    
    antennas.loc[antenna, band, tiltval] = temp_series
    

# set multindex to select antenna using name and electrical tilt:
antennas.sort_index(inplace=True)

# filter only unique set of (antenna, band, eltilt)
antennas = antennas.loc[~antennas.index.duplicated(keep='last')]

# convert datatypes to float32:
antennas = antennas.astype({'Gain': 'float32', 'HorBW': 'float32', 'VerBW': 'float32', 'sidelobe': 'float32',
                            'theta_s': 'float32', 'phi10': 'float32', 'phi20': 'float32'})

# store dataframe:
antennas.to_hdf('antennas_df.hdf', key='antennasdb')

# to extract antenna pattern and specs:
# antennas = pd.read_hdf('antennas_df.hdf', key='antennasdb')
# row = antennas.loc[(antenna, band, eltilt)]
# maxgain = row['Gain']
# horizontal = row['Pattern'][:, 0]
# vertical = row['Pattern'][:, 1]

