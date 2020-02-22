import sqlite3
import os


currentdir = os.getcwd()
patternfold = currentdir+'\patterns'

conn = sqlite3.connect('antennas.sql')
cursor = conn.cursor()

cursor.execute('CREATE TABLE IF NOT EXISTS antennas (band INTEGER NOT NULL,' 
                                               'name TEXT NOT NULL,' 
                                               'tilt REAL NOT NULL,' 
                                               'gain REAL NOT NULL,'
                                               'pattern TEXT NOT NULL,'
                                               'PRIMARY KEY (band, name, tilt))')

conn.commit()

for r, d, f in os.walk(patternfold):
    for file in f:
        if '.csv' in file:
            split = file.split('_')
            bandval = int(split[0])
            nameval = split[1]
            tiltval = float(split[2])
            gainval = float(split[3][:-4])
            try:
                cursor.execute('INSERT INTO antennas VALUES (?, ?, ?, ?, ?)',(bandval , nameval, tiltval, gainval, file))
            except:
                pass
            else:
                conn.commit()

