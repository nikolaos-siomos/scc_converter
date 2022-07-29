"""
@author: Peristera
"""
import os, sys
import numpy as np
from readers import read_licel, read_polly

def read_rayleigh(cfg, finput, cal_angle = 0, files_per_sector = None):
    
    """Extracts the raw signal, shots, and rest metadata information out of the 
    raw input files. The default format is currently licel. The signal units
    are always mV for analog and counts for photon channels"""
    
    #Define the format of the signal files - Defaults to licel
    if 'file_format' in cfg.lidar.index:
        file_format = cfg.lidar.file_format
    else:
        file_format = 'licel'
        sys.exit('-- Warning: The default file_format licel was assumed. Please make sure this is what you really want.')
    
    # Reading
    print('-----------------------------------------')
    print('Start reading Rayleigh signals...')
    print('-----------------------------------------')
    print('-- Reading measurement files!')
    
    path = os.path.join(finput, 'rayleigh')        

    # Select reader based on the file format
    if file_format == 'polly_xt':
     # In case of Polly define the cal_angle  
        sig_raw, sig_dev, info_val, info_dev, ground_alt, SZA, azimuth =\
            read_polly.dtfs(path, cfg, cal_angle)
            
    elif file_format == 'licel':
        cfg, start_time, end_time, sig, shots, folder =\
            read_licel.dtfs(cfg, dir_meas = path)
        
        cfg.lidar['start_time'] = start_time[0]
        cfg.lidar['end_time'] = end_time[-1]
        cfg.lidar['temporal_resolution'] = end_time[0] - start_time[0]
    
    else:
        sys.exit('-- Error: file_format field not recognized. Please revise the settings file and use one of: polly_xt, licel')

        
    print('Reading signals complete!')
    print('-----------------------------------------')
    print('')

    # Convert analog channel units to mV (applicable mainly to licel)   
    sig = unit_conv_bits_to_mV(cfg, signal = sig.copy(), shots = shots)
        
    return(cfg, sig, shots)

def unit_conv_bits_to_mV(cfg, signal, shots):

    """Converts analog signals from bits to mV"""
    
    if len(signal) > 0:
        for j in cfg.channels.index:
            ch = dict(channel = j)
            if cfg.channels.ch_mode[j] == 0 and cfg.channels.channel_id[j] != '_': 
                # analog conversion (to mV)
                signal.loc[ch] = signal.loc[ch]*cfg.channels.ADC_range[j]/(shots.loc[ch]*(np.power(2,cfg.channels.ADC_bit[j]) -1))
    
    return(signal) 