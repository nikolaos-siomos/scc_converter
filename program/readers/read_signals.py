"""
@author: Peristera
"""
import os,sys
import numpy as np
from readers import read_licel, read_polly

def read_signals(meas_type, cfg, finput, cal_angle = 0):
        
    #Define the format of the signal files
    if 'file_format' in cfg.lidar.index:
        file_format = cfg.lidar.file_format
    else:
        sys.exit('--Error: Mandatory field file_format is missing! Please provide it in the Lidar section of the setings file')
    
    # Reading
    print('-----------------------------------------')
    print(f'Start reading {meas_type} signals...')
    print('-----------------------------------------')
    print(f'-- Reading {meas_type} measurement files!')
    
    path = os.path.join(finput, meas_type)

    if file_format == 'polly_xt':
     # In case of Polly define the cal_angle  
        sig_raw, sig_dev, info_val, info_dev, ground_alt, SZA, azimuth =\
            read_polly.dtfs(path, cfg, cal_angle)
            
    elif file_format == 'licel':
        cfg, info, sig =\
            read_licel.dtfs(cfg, dir_meas = path, meas_type = meas_type)
    
    else:
        sys.exit('-- Error: file_format field not recognized. Please revise the settings file and use one of: polly_xt, licel')

        
    print(f'Reading {meas_type} signals complete!')
    print('-----------------------------------------')
    print('')

    # Overwrite the info parameters from the raw files with the optional fields
    # provided in the configuration file
    info = overwrite(info, cfg)
    
    # Remove channels that should be excluded according to the configuration file
    ch_list = info.index[cfg.channels.ch_id != '_'].values

    sig = sig.loc[dict(channel = ch_list)]  
    info = info.loc[ch_list,:]  

    # Convert analog channel units to mV (applicable mainly to licel)   
    sig = unit_conv_bits_to_mV(sig.copy(), info = info.copy())
        
    return(sig, info, cfg)

def overwrite(info, cfg):
    
    if len(info) > 0:
        # Overwrite in info dataframe the params reported in the input files with the user defined values given in config file
        keys = ['ch_mode', 'bins', 'laser_pol', 'shots', 'ADC_range', 'ADC_bit',
                'wave', 'ch_pol', 'resol', 'voltage']
        
        for key in keys:
            if key in cfg.channels.columns:
                info.loc[:,key] = cfg.channels.loc[:,key].values
         
    return(info)

def unit_conv_bits_to_mV(signal, info):

    if len(signal) > 0:
        for j in info.index:
            ch = dict(channel = j)
            if info.ch_mode[j] == 0.0: 
                # analog conversion (to mV)
                signal.loc[ch] = signal.loc[ch].values*info.ADC_range[j]/(info.shots[j]*(np.power(2,info.ADC_bit[j]) -1))
    
    return(signal) 