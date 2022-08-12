"""
@author: N. Siomos & P. Paschou

Main algorithm for pre-processing the raw signals and retrieve the optical products
"""
import warnings, os, sys
from readers.parse_config import parse_config
from tools import process, automate

# Ignores all warnings --> they are not printed in terminal
warnings.filterwarnings('ignore')

# Get the command line argument information
args = parse_config()

# Identify the measurement type (rayleigh , telecover, or calibration)    
meas_type = automate.get_meas_type(path = args['parent_folder'])
     
# In[1]
#------------------------------------------------------------
# A) Read and pre-process the signals
#------------------------------------------------------------
allowed_types = ['radiosonde', 'rayleigh', 'telecover', 'calibration', 'dark'] 
allowed_modes = ['S', 'R', 'T', 'C', 'D']
processors = {'radiosonde' : process.radiosonde,
              'rayleigh' : process.rayleigh,
              'telecover' : process.telecover,
              'calibration' : process.calibration,
              'dark' : process.dark}
modes = {'radiosonde' : 'S',
         'rayleigh' : 'R',
         'telecover' : 'T',
         'calibration' : 'C',
         'dark' : 'D'}

# Call all the processors sequentially
for mtype in allowed_types: 
    
    if mtype in meas_type and (args['mode'] == 'A' or args['mode'] == modes[mtype]):
    
        nc_fname = processors[mtype](args)
        
        if mtype == 'radiosonde' and not args['radiosonde_filename']:
            args['radiosonde_filename'] = os.path.basename(nc_fname)
        
        if mtype == 'rayleigh' and not args['rayleigh_filename'] and 'calibration' in meas_type:
            args['rayleigh_filename'] = os.path.basename(nc_fname)
    
    elif mtype not in meas_type and args['mode'] == 'A':
        print(f"--Warning: No {mtype} files were processed!")
        
    elif mtype not in meas_type and args['mode'] == modes[mtype]:
        sys.exit(f"--Error: No {mtype} folder was detected despite the provided mode ({modes[mtype]})!")
