import pandas as pd

def readdb():
    # load database from file:
    antennas = pd.read_hdf('antennas_df.hdf', key='antennasdb')
    return antennas
