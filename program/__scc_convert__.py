"""
@author: N. Siomos & P. Paschou

Main algorithm for pre-processing the raw signals and retrieve the optical products
"""
import warnings, os, sys
from readers.parse_config import parse_config
from tools import process, automate

# -f "/mnt/DATA/LRZ_Sync/CARS-LMU (Volker Freudenthaler)/data/EVE/20220617" -i EV -d --trim_overflows 3 -M R

# -f /home/nick/Downloads/Raw_LICEL -i OT -d --trim_overflows 0 -M A --rsonde_skip_header 6 --rsonde_skip_footer 0 --rsonde_delimiter S --rsonde_column_index 2 1 3 5 --rsonde_geodata 40.500 22.900 0 
# -f /mnt/DATA/Big_data/Databases/POLIS/data/181016 -n 20 -i m --rsonde_skip_header 35 --rsonde_skip_footer 8 --rsonde_delimiter S --rsonde_column_index 2 1 3 5 --rsonde_geodata 38.002 -1.171 61 -d --trim_overflows 2 -M C -l ray_20181016mun2024.nc

# -f /mnt/DATA/Big_data/Databases/POLIS/data/181016 -n 20 -i m --rsonde_skip_header 35 --rsonde_skip_footer 8 --rsonde_delimiter S --rsonde_column_index 2 1 3 5 --rsonde_column_units m hPa C percent --rsonde_geodata 38.002 -1.171 61 -d --trim_overflows 1 -M S -l ray_20181016mun2024.nc
# Ignores all warnings --> they are not printed in terminal
warnings.filterwarnings('ignore')

# def main(args):
args = parse_config()

# Identify the measurement type (rayleigh , telecover, or polarization_calibration)    
meas_type = automate.get_meas_type(args)
     
# In[1]
#------------------------------------------------------------
# A) Read and pre-process the signals
#------------------------------------------------------------
allowed_types = ['rayleigh', 'telecover', 
                 'polarization_calibration', 'standalone_dark'] 

processors = {'rayleigh' : process.rayleigh,
              'telecover' : process.telecover,
              'polarization_calibration' : process.polarization_calibration,
              'standalone_dark' : process.dark}

modes = {'rayleigh' : 'R',
         'telecover' : 'T',
         'polarization_calibration' : 'C',
         'standalone_dark' : 'D'}

fnames = dict()
# Call all the processors sequentially
for mtype in allowed_types: 
    
    if mtype in meas_type and (args['mode'] == 'A' or args['mode'] == modes[mtype]):
    
        nc_fname = processors[mtype](args)
        
        if mtype == 'rayleigh':
            args['rayleigh_filename'] = os.path.basename(nc_fname[0])
            args['radiosonde_filename'] = os.path.basename(nc_fname[1])
            fnames['rayleigh'] = nc_fname[0]
            fnames['radiosonde'] = nc_fname[0]
        else:
            fnames[mtype] = nc_fname
    
    elif mtype not in meas_type and args['mode'] == 'A':
        print(f"--Warning: No {mtype} files were processed!")
        print("")
        
    elif mtype not in meas_type and args['mode'] == modes[mtype]:
        raise Exception(f"--Error: No {mtype} folder was detected despite the provided mode ({modes[mtype]})!")

    # return(fnames)

# if __name__ == '__main__':
#     # Get the command line argument information
#     args = parse_config()
#     main(args)
