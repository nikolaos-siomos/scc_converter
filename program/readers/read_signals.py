"""
@author: Peristera
"""
import os, sys
import numpy as np
from readers import read_licel, read_polly
import xarray as xr

def rayleigh(cfg, finput, cal_angle = 0, files_per_sector = None):
    
    """Extracts the raw signal, shots, and rest metadata information out of the 
    raw input files. The default format is currently licel. The signal units
    are always mV for analog and counts for photon channels"""
    
    #Define the format of the signal files - Defaults to licel
    if 'file_format' in cfg.lidar.index:
        file_format = cfg.lidar.file_format
    else:
        file_format = 'licel'
        print('-- Warning: The default file_format licel was assumed. Please make sure this is what you really want.')

    if file_format not in ['licel', 'polly_xt']:
        sys.exit('-- Error: file_format field not recognized. Please revise the settings file and use one of: polly_xt, licel')

    # Reading
    print('-----------------------------------------')
    print('Start reading Rayleigh signals...')
    print('-----------------------------------------')
    print('-- Reading Rayleigh measurement files!')
    
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
        
    print('Reading Rayleigh signals complete!')
    print('-----------------------------------------')
    print('')

    # Convert analog channel units to mV (applicable mainly to licel)   
    sig = unit_conv_bits_to_mV(cfg, signal = sig.copy(), shots = shots)
        
    return(cfg, sig, shots)

def telecover(cfg, finput, cal_angle = 0, files_per_sector = None):
    
    """Extracts the raw signal, shots, and rest metadata information out of the 
    raw input files. The default format is currently licel. The signal units
    are always mV for analog and counts for photon channels"""
    
    #Define the format of the signal files - Defaults to licel
    if 'file_format' in cfg.lidar.index:
        file_format = cfg.lidar.file_format
    else:
        file_format = 'licel'
        print('-- Warning: The default file_format licel was assumed. Please make sure this is what you really want.')

    if file_format not in ['licel', 'polly_xt']:
        sys.exit('-- Error: file_format field not recognized. Please revise the settings file and use one of: polly_xt, licel')

    
    # Reading
    print('-----------------------------------------')
    print(f'Start reading telecover signals...')
    print('-----------------------------------------')
    print(f'-- Reading telecover measurement files!')
    
    sig_sec = []
    sector_sec = []
    shots_sec = []
    if not files_per_sector:
        for sector in ['north', 'east', 'south', 'west']:
            path = os.path.join(finput, 'telecover', sector)
            print(f'-- Reading {sector} sector..')           
            # Select reader based on the file format
            if file_format == 'polly_xt':
             # In case of Polly define the cal_angle  
                sig_raw, sig_dev, info_val, info_dev, ground_alt, SZA, azimuth =\
                    read_polly.dtfs(path, cfg, cal_angle)
                    
            if file_format == 'licel':
                cfg, start_time, end_time, sig, shots, folder =\
                    read_licel.dtfs(cfg, dir_meas = path)
                
                cfg.lidar['start_time'] = start_time[0]
                cfg.lidar['end_time'] = end_time[-1]
                cfg.lidar['temporal_resolution'] = end_time[0] - start_time[0]
                    
                sector = folder_to_sector(folder)
            sig_sec.append(sig)
            shots_sec.append(shots)
            sector_sec.append(sector)

        sig = xr.concat(sig_sec, dim = 'time').sortby('time')
        shots = xr.concat(shots_sec, dim = 'time').sortby('time')
        sector = xr.concat(sector_sec, dim = 'time').sortby('time')
        
    else:
        path = os.path.join(finput, 'telecover')        
        
        # Select reader based on the file format
        if file_format == 'polly_xt':
         # In case of Polly define the cal_angle  
            sig_raw, sig_dev, info_val, info_dev, ground_alt, SZA, azimuth =\
                read_polly.dtfs(path, cfg, cal_angle)
            
        if file_format == 'licel':
            cfg, start_time, end_time, sig, shots, folder =\
                read_licel.dtfs(cfg, dir_meas = path)
                
            cfg.lidar['start_time'] = start_time[0]
            cfg.lidar['end_time'] = end_time[-1]
            cfg.lidar['temporal_resolution'] = end_time[0] - start_time[0]
                
        sector = time_to_sector(folder, files_per_sector)

    print(f'Reading telecover signals complete!')
    print('-----------------------------------------')
    print('')

    # Convert analog channel units to mV (applicable mainly to licel)   
    sig = unit_conv_bits_to_mV(cfg, signal = sig.copy(), shots = shots)
        
    return(cfg, sig, shots, sector)

def dark(cfg, finput, cal_angle = 0, files_per_sector = None):
    
    """Extracts the raw signal, shots, and rest metadata information out of the 
    raw input files. The default format is currently licel. The signal units
    are always mV for analog and counts for photon channels"""
    
    #Define the format of the signal files - Defaults to licel
    if 'file_format' in cfg.lidar.index:
        file_format = cfg.lidar.file_format
    else:
        file_format = 'licel'
        print('-- Warning: The default file_format licel was assumed. Please make sure this is what you really want.')

    if file_format not in ['licel', 'polly_xt']:
        sys.exit('-- Error: file_format field not recognized. Please revise the settings file and use one of: polly_xt, licel')

    # Reading
    print('-----------------------------------------')
    print('Start reading dark signals...')
    print('-----------------------------------------')
    print('-- Reading dark measurement files!')
    
    path = os.path.join(finput, 'dark')        

    # Select reader based on the file format
    if file_format == 'polly_xt':
     # In case of Polly define the cal_angle  
        sig_raw, sig_dev, info_val, info_dev, ground_alt, SZA, azimuth =\
            read_polly.dtfs(path, cfg, cal_angle)
            
    elif file_format == 'licel':
        cfg, start_time, end_time, sig, shots, folder =\
            read_licel.dtfs(cfg, dir_meas = path)
        
        cfg.lidar['background_start_time'] = start_time[0]
        cfg.lidar['background_end_time'] = end_time[-1]
        cfg.lidar['background_temporal_resolution'] = end_time[0] - start_time[0]
        
    print('Reading dark signals complete!')
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

def folder_to_sector(folder):

    fld = ['north','east','south','west']
    sec = [1,2,3,4]
        
    folder_tmp = folder.values
    
    sector_tmp = np.nan * np.zeros(folder_tmp.shape)
    
    for i in range(len(fld)):
        sector_tmp[folder == fld[i]] = sec[i]
    
    sector = xr.DataArray(sector_tmp, coords = folder.coords, dims = folder.dims)
    
    return(sector)

def time_to_sector(folder, files_per_sector):
    
    blocks = folder.time.size / files_per_sector
    
    if blocks - np.floor(blocks) > 0.:
        sys.exit("-- Error: The files_per_sector argument was provided but " +
                 "the number of telecover files cannot be evenly divided by it! " +
                 "Please revise the files_per_sector value. If the number of " +
                 "files per sector was not constant during measurements then " +
                 "provide the telecover in individual folders per sector.")
    
    sec = [1, 2, 3, 4]
    
    sec_list = int(np.floor(blocks / 4.)) * sec
    sec_list.extend(sec[:np.int((blocks - np.floor(blocks / 4.)) * 4.)])
    
    sector = xr.DataArray(coords = folder.coords, dims = folder.dims)
        
    sector_tmp = np.nan * np.zeros(folder.shape)
    
    for i in range(len(sec_list)):
        sector_tmp[i*files_per_sector:(i+1)*files_per_sector] = sec_list[i]

    sector = xr.DataArray(sector_tmp, coords = folder.coords, dims = folder.dims)
    
    return(sector)