# EMF_Safety_Calculator

EMF Safety Calculator takes as input the technical specifications of a cellular mobile station (antennas type/height, frequency bands in which the antennas operate, power etc), and calculates the exposure level (normalized power density levels per reference levels).

# Usage
Run "main.py" to start the GUI and use the program. You need also all other helper .py files included in the repo to properly run it.

Antennas database is a pandas dataframe, that stores antennas names and supporting tilts and operating bands.

You can create (or insert new antennas into) a database, running "create_antennas_df.py' file, after ytou specify the location of .csv files that correspond to radiation pattern of each antenna).

Pattern files should be .csv files, with column 0 representing the horizontal and column 1 the vertical pattern.


A function in validuser.py is included if you want to define a user authentication process.

Propagation models that can be used to compute the power density at any point is free space loss, two-ray reflection model (assuming constructive interference and varyaing reflection factor), and COST-WI model (LOS condition, this is for reference only as it is valid for d>20m).

Image plot tab is for plotting the exposure levels over an image for a more friendly visualization. Base station position can be selected in any point over a selected image, and the exposure levels are plotted (you can select to colour only points with exposure level >threshold) around the BS.

Reference exposure levels that can be used are those adviced from ICNIRP with a editable reducing factor (some countries use lower reference levels for emf assessment)
 
