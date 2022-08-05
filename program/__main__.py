"""
@author: N. Siomos & P. Paschou

Main algorithm for pre-processing the raw signals and retrieve the optical products
"""
import warnings, os, sys
from readers.read_config import config
from readers.parse_config import parse_config
from readers import read_signals
from tools import process, automate
import matplotlib.pyplot as plt
import numpy as np


# Ignores all warnings --> they are not printed in terminal
warnings.filterwarnings('ignore')

# Get the full path of the config_file.ini
args = parse_config()

# Check all measurement folders for unnecessary subirectories
automate.check_all_dirs(path = args['parent_folder'], files_per_sector = args['files_per_sector'])

# Identify the measurement type (rayleigh , telecover, or calibration)    
meas_type = automate.get_meas_type(path = args['parent_folder'])
     
# In[1]
#------------------------------------------------------------
# A) Read and pre-process the signals
#------------------------------------------------------------
# A.1) Rayleigh measurement
if 'rayleigh' in meas_type:
   
    process.rayleigh(args)

# A.2) Telecover measurement
if 'telecover' in meas_type:
     
    process.telecover(args)


# A.3) Polarization Calibration measurement
if 'calibration' in meas_type:
    
    # Check if the rayleigh filename was provided
    if not args['rayleigh_filename']:
        sys.exit("-- Error: A polarization calibration measurement is being processed but the rayleigh filename was not provided in the arguments! Please prepare the rayleigh file fist and included it with: -l <rayleigh_filename>'")
        
    # Read the files in the dark folder
    cfg, sig_raw_d, shots_d  = read_signals.dark(cfg = cfg, finput = os.path.join(args['parent_folder'],'calibration','dark'))
    
    # Read the files in the polarization calibration folder
    cfg, sig_raw, shots, position = read_signals.calibration(cfg = cfg, finput = os.path.join(args['parent_folder'],'calibration'))
    
    # Remove channels that should be excluded according to the configuration file
    cfg, sig_raw, shots = trim.channels(cfg, sig_raw, shots)
    
    cfg, sig_raw_d, shots_d = trim.channels(cfg, sig_raw_d, shots_d) 

    # Add dafault values to the configuration object when the respective variables are not provided in the configuration file
    cfg = trim.fill_defaults(cfg)
    
    # Creating the measurement ID
    meas_ID = make.meas_id(lr_id = cfg.lidar['lidar_id'], sig = sig_raw)
    
    # Creating the paths and folders
    nc_path = make.path(results_folder = args['results_folder'], meas_ID = meas_ID, meas_type = 'pcl')
    
    # Making the raw SCC file
    make.calibration_file(cfg = cfg, nc_path = nc_path, meas_ID = meas_ID, 
                          molecular_calc = args['molecular_calc'], 
                          P = args['ground_pressure'], 
                          T = args['ground_temperature'], 
                          rsonde = args['radiosonde_filename'],
                          rayleigh = args['rayleigh_filename'], 
                          sig = sig_raw, sig_d = sig_raw_d, shots = shots,
                          position = position)
    
    print('Succesfully generated a polarization calibration QA file!')


# A.4) Standalone dark measurement
if 'dark' in meas_type and len(meas_type) == 1:
    
    # Read the files in the dark folder
    cfg, sig_raw_d, shots_d  = read_signals.dark(cfg = cfg, finput = os.path.join(args['parent_folder'],'dark'))
    
    # Remove channels that should be excluded according to the configuration file
    cfg, sig_raw_d, shots_d = trim.channels(cfg, sig_raw_d, shots_d) 

    # Add dafault values to the configuration object when the respective variables are not provided in the configuration file
    cfg = trim.fill_defaults(cfg)
    
    # Creating the measurement ID
    meas_ID = make.meas_id(lr_id = cfg.lidar['lidar_id'], sig = sig_raw_d)
    
    # Creating the paths and folders
    nc_path = make.path(results_folder = args['results_folder'], meas_ID = meas_ID, meas_type = 'drk')
    
    # Making the raw SCC file
    make.dark_file(cfg = cfg, nc_path = nc_path, meas_ID = meas_ID,  
                   sig_d = sig_raw_d, shots = shots_d)
    
    print('Succesfully generated a dark QA file!')

sys.exit(0) 
