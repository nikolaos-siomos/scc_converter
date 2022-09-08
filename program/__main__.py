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

# Get the command line argument information
args = parse_config()

# Identify the measurement type (rayleigh , telecover, or polarization_calibration)    
meas_type = automate.get_meas_type(path = args['parent_folder'])
     
# In[1]
#------------------------------------------------------------
# A) Read and pre-process the signals
#------------------------------------------------------------
allowed_types = ['radiosonde', 'rayleigh', 'telecover', 
                 'polarization_calibration', 'dark'] 
allowed_modes = ['S', 'R', 'T', 'C', 'D']
processors = {'radiosonde' : process.radiosonde,
              'rayleigh' : process.rayleigh,
              'telecover' : process.telecover,
              'polarization_calibration' : process.polarization_calibration,
              'dark' : process.dark}
modes = {'radiosonde' : 'S',
         'rayleigh' : 'R',
         'telecover' : 'T',
         'polarization_calibration' : 'C',
         'dark' : 'D'}

# Call all the processors sequentially
for mtype in allowed_types: 
    
    if mtype in meas_type and (args['mode'] == 'A' or args['mode'] == modes[mtype]):
    
        nc_fname = processors[mtype](args)
        
        if mtype == 'radiosonde' and not args['radiosonde_filename']:
            args['radiosonde_filename'] = os.path.basename(nc_fname)
        
        if mtype == 'rayleigh' and not args['rayleigh_filename'] and 'polarization_calibration' in meas_type:
            args['rayleigh_filename'] = os.path.basename(nc_fname)
    
    elif mtype not in meas_type and args['mode'] == 'A':
        print(f"--Warning: No {mtype} files were processed!")
        
    elif mtype not in meas_type and args['mode'] == modes[mtype]:
        sys.exit(f"--Error: No {mtype} folder was detected despite the provided mode ({modes[mtype]})!")
