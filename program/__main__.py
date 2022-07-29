"""
@author: N. Siomos & P. Paschou

Main algorithm for pre-processing the raw signals and retrieve the optical products
"""
import warnings, os, sys
from readers.read_config import config
from readers.parse_config import parse_config
from readers import read_signals
from tools.automate import get_meas_type, check_all_dirs
from tools import trim, make
import matplotlib.pyplot as plt
import numpy as np


# Ignores all warnings --> they are not printed in terminal
warnings.filterwarnings('ignore')

# Get the full path of the config_file.ini
args = parse_config()

# Reading of the configuration file    
cfg = config(path = args['config_file'])

# Check all measurement folders for unnecessary subirectories
check_all_dirs(path = args['parent_folder'], files_per_sector = args['files_per_sector'])

# Identify the measurement type (rayleigh , telecover, or calibration)    
meas_type = get_meas_type(path = args['parent_folder'])
        
# In[1]
#------------------------------------------------------------
# A) Read and pre-process the signals
#------------------------------------------------------------
# A.1) Rayleigh measurement
if 'rayleigh' in meas_type:

    # Read the files in the dark folder
    cfg, sig_raw_d, shots_d  = read_signals.dark(cfg = cfg, finput = args['parent_folder'])

    # Read the files in the rayleigh folder
    cfg, sig_raw, shots = read_signals.rayleigh(cfg = cfg, finput = args['parent_folder'])
    
    # Remove channels that should be excluded according to the configuration file
    cfg, sig_raw, shots = trim.channels(cfg, sig_raw, shots)
    
    cfg, sig_raw_d, shots_d = trim.channels(cfg, sig_raw_d, shots_d) 
    
    # Creating the measurement ID
    meas_ID = make.meas_id(lr_id = cfg.lidar['lidar_id'], sig = sig_raw)
    
    # Creating the paths and folders
    nc_path = make.path(results_folder = args['results_folder'], meas_ID = meas_ID, meas_type = 'ray')
    
    # Making the raw SCC file
    make.rayleigh_file(cfg = cfg, nc_path = nc_path, meas_ID = meas_ID, 
                       molec_calc = args['molec_calc'], P = args['ground_pressure'], 
                       T = args['ground_temperature'], rsonde = args['radiosonde_file'], 
                       sig = sig_raw, sig_d = sig_raw_d, shots = shots)
    
    print('Succesfully generated a rayleigh QA file!')

# A.2) Telecover measurement
if 'telecover' in meas_type:
        
    # Read the files in the dark folder
    cfg, sig_raw_d, shots_d  = read_signals.dark(cfg = cfg, finput = args['parent_folder'])
    
    # Read the files in the telecover folder
    cfg, sig_raw, shots, sector = read_signals.telecover(cfg = cfg, finput = args['parent_folder'], files_per_sector = args['files_per_sector'])
    
    # Remove channels that should be excluded according to the configuration file
    cfg, sig_raw, shots = trim.channels(cfg, sig_raw, shots)
    
    cfg, sig_raw_d, shots_d = trim.channels(cfg, sig_raw_d, shots_d) 
    
    # Creating the measurement ID
    meas_ID = make.meas_id(lr_id = cfg.lidar['lidar_id'], sig = sig_raw)
    
    # Creating the paths and folders
    nc_path = make.path(results_folder = args['results_folder'], meas_ID = meas_ID, meas_type = 'tlc')
    
    # Making the raw SCC file
    make.telecover_file(cfg = cfg, nc_path = nc_path, meas_ID = meas_ID, 
                        molec_calc = args['molec_calc'], P = args['ground_pressure'], 
                        T = args['ground_temperature'], rsonde = args['radiosonde_file'], 
                        sig = sig_raw, sig_d = sig_raw_d, shots = shots, sector = sector)
    
    print('Succesfully generated a telecover QA file!')


# A.4) Standalone dark measurement
if 'dark' in meas_type and len(meas_type) == 1:
    
    # Read the files in the dark folder
    cfg, sig_raw_d, shots_d  = read_signals.dark(cfg = cfg, finput = args['parent_folder'])
    
    # Remove channels that should be excluded according to the configuration file
    cfg, sig_raw_d, shots_d = trim.channels(cfg, sig_raw_d, shots_d) 
    
    # Creating the measurement ID
    meas_ID = make.meas_id(lr_id = cfg.lidar['lidar_id'], sig = sig_raw_d)
    
    # Creating the paths and folders
    nc_path = make.path(results_folder = args['results_folder'], meas_ID = meas_ID, meas_type = 'drk')
    
    # Making the raw SCC file
    make.dark_file(cfg = cfg, nc_path = nc_path, meas_ID = meas_ID, 
                   molec_calc = args['molec_calc'], P = args['ground_pressure'], 
                   T = args['ground_temperature'], rsonde = args['radiosonde_file'], 
                   sig_d = sig_raw_d, shots = shots_d)
    
    print('Succesfully generated a dark QA file!')

sys.exit(0) 
