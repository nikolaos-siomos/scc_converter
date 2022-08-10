"""
@author: Peristera
"""
import os, sys, glob
import numpy as np
from readers import read_licel, read_polly
import xarray as xr

def rayleigh(finput, mcode, file_format):
    
    """Extracts the raw signal, shots, and rest metadata information out of the 
    raw input files. The default format is currently licel. The signal units
    are always mV for analog and counts for photon channels"""
    
    # Reading
    print('-----------------------------------------')
    print('Start reading Rayleigh signals...')
    print('-----------------------------------------')
    print('-- Reading Rayleigh measurement files!')
    
    path = os.path.join(finput, 'normal')        

    # Select reader based on the file format
    if file_format == 'polly_xt':
        sys.exit('--Error: PollyXT reading routines are not yet ready!')
     # In case of Polly define the cal_angle  
        # sig_raw, sig_dev, info_val, info_dev, ground_alt, SZA, azimuth =\
        #     read_polly.dtfs(path, cfg, cal_angle)
            
    elif file_format == 'licel':
        lidar_info, channel_info, start_time, end_time, sig, shots, folder =\
            read_licel.dtfs(dir_meas = path, mcode = mcode)
        
        lidar_info['start_time'] = start_time[0]
        lidar_info['end_time'] = end_time[-1]
        lidar_info['temporal_resolution'] = end_time[0] - start_time[0]
        
    print('Reading Rayleigh signals complete!')
    print('-----------------------------------------')
    print('')

    return(sig, shots, lidar_info, channel_info)

def telecover(finput, mcode, file_format, files_per_sector = None):
    
    """Extracts the raw signal, shots, and rest metadata information out of the 
    raw input files. The default format is currently licel. The signal units
    are always mV for analog and counts for photon channels"""
    
    # Reading
    print('-----------------------------------------')
    print('Start reading telecover signals...')
    print('-----------------------------------------')
    print('-- Reading telecover measurement files!')
    
    sig_sec = []
    sector_sec = []
    shots_sec = []
    if not files_per_sector:
        for sector in ['north', 'east', 'south', 'west']:
            path = os.path.join(finput, 'sectors', sector)
            print(f'-- Reading {sector} sector..')           
            # Select reader based on the file format
            if file_format == 'polly_xt':
             # In case of Polly define the cal_angle  
                # sig_raw, sig_dev, info_val, info_dev, ground_alt, SZA, azimuth =\
                #     read_polly.dtfs(path, cfg, cal_angle)
                sys.exit('--Error: PollyXT reading routines are not yet ready!')
                    
            if file_format == 'licel':
                lidar_info, channel_info, start_time, end_time, sig, shots, folder =\
                    read_licel.dtfs(dir_meas = path, mcode = mcode)
                
                lidar_info['start_time'] = start_time[0]
                lidar_info['end_time'] = end_time[-1]
                lidar_info['temporal_resolution'] = end_time[0] - start_time[0]
                    
                sector = folder_to_sector(folder)
            sig_sec.append(sig)
            shots_sec.append(shots)
            sector_sec.append(sector)

        sig = xr.concat(sig_sec, dim = 'time').sortby('time')
        shots = xr.concat(shots_sec, dim = 'time').sortby('time')
        sector = xr.concat(sector_sec, dim = 'time').sortby('time')
        
    else:
        path = os.path.join(finput, 'sectors')        
        
        # Select reader based on the file format
        if file_format == 'polly_xt':
         # In case of Polly define the cal_angle  
            # sig_raw, sig_dev, info_val, info_dev, ground_alt, SZA, azimuth =\
            #     read_polly.dtfs(path, cfg, cal_angle)
            sys.exit('--Error: PollyXT reading routines are not yet ready!')
            
        if file_format == 'licel':
            lidar_info, channel_info, start_time, end_time, sig, shots, folder =\
                read_licel.dtfs(dir_meas = path, mcode = mcode)
                
            lidar_info['start_time'] = start_time[0]
            lidar_info['end_time'] = end_time[-1]
            lidar_info['temporal_resolution'] = end_time[0] - start_time[0]
                
        sector = time_to_sector(folder, files_per_sector)

    print('Reading telecover signals complete!')
    print('-----------------------------------------')
    print('')

    return(sig, shots, lidar_info, channel_info, sector)

def calibration(finput, mcode, file_format):
    
    """Extracts the raw signal, shots, and rest metadata information out of the 
    raw input files. The default format is currently licel. The signal units
    are always mV for analog and counts for photon channels"""
    
    # Reading
    print('-----------------------------------------')
    print('Start reading Polarization Calibration signals...')
    print('-----------------------------------------')
    print('-- Reading Polarization Calibration measurement files!')
    
    list_dirs = [d for d in os.listdir(finput)
                 if os.path.isdir(os.path.join(finput, d))]
            
    sig_pos = []
    shots_pos = []
    position_pos = []
   
    for folder in list_dirs:
        
        path = os.path.join(finput, folder)  
        
        print(f'-- Reading {folder} files..')      
        
        # Select reader based on the file format
        if file_format == 'polly_xt':
         # In case of Polly define the cal_angle  
            # sig_raw, sig_dev, info_val, info_dev, ground_alt, SZA, azimuth =\
            #     read_polly.dtfs(path, cfg, cal_angle)
            sys.exit('--Error: PollyXT reading routines are not yet ready!')

                
        if file_format == 'licel':
            lidar_info, channel_info, start_time, end_time, sig, shots, folder =\
                read_licel.dtfs(dir_meas = path, mcode = mcode)
            
            lidar_info['start_time'] = start_time[0]
            lidar_info['end_time'] = end_time[-1]
            lidar_info['temporal_resolution'] = end_time[0] - start_time[0]
                
            position = folder_to_position(folder)

        sig_pos.append(sig)
        shots_pos.append(shots)
        position_pos.append(position)

    sig = xr.concat(sig_pos, dim = 'time').sortby('time')
    shots = xr.concat(shots_pos, dim = 'time').sortby('time')
    position = xr.concat(position_pos, dim = 'time').sortby('time')
        
    print('Reading Polarization Calibration signals complete!')
    print('-----------------------------------------')
    print('')

    return(sig, shots, lidar_info, channel_info, position)


def dark(finput, mcode, file_format):
    
    """Extracts the raw signal, shots, and rest metadata information out of the 
    raw input files. The default format is currently licel. The signal units
    are always mV for analog and counts for photon channels"""
    
    # Reading
    print('-----------------------------------------')
    print('Start reading dark signals...')
    print('-----------------------------------------')
    print('-- Reading dark measurement files!')
    
    path = finput       

    # Select reader based on the file format
    if file_format == 'polly_xt':
     # In case of Polly define the cal_angle  
        # sig_raw, sig_dev, info_val, info_dev, ground_alt, SZA, azimuth =\
        #     read_polly.dtfs(path, cfg, cal_angle)
        sys.exit('--Error: PollyXT reading routines are not yet ready!')

    elif file_format == 'licel':
        lidar_info, channel_info, start_time, end_time, sig, shots, folder =\
            read_licel.dtfs(dir_meas = path, mcode = mcode)
        
        lidar_info['background_start_time'] = start_time[0]
        lidar_info['background_end_time'] = end_time[-1]
        lidar_info['background_temporal_resolution'] = end_time[0] - start_time[0]
        
    print('Reading dark signals complete!')
    print('-----------------------------------------')
    print('')
  
    return(sig, shots, lidar_info, channel_info)

    """Extracts the raw signal, shots, and rest metadata information out of the 
    raw input files. The default format is currently licel. The signal units
    are always mV for analog and counts for photon channels"""
    
    # Reading
    print('-----------------------------------------')
    print('Start reading dark signals...')
    print('-----------------------------------------')
    print('-- Reading dark measurement files!')
    
def radiosonde(finput, delimiter, skip_header, skip_footer, usecols):

    path = glob.glob(os.path.join(finput,'*'))
    
    lib_delimiter =  {"S": "",
                      "C": ",",
                      "T": "\t"}
    
    if len(path) > 1:
        sys.exit("--Error: More than one txt files provided in the radiosonde folder! Please provide a single file with the radiosonde data with the following filename: yyyymmddhh<any_text>.txt ")
    elif len(path) == 0 :
        sys.exit("--Error: No txt file provided in the radiosonde folder! Please provide a single file with the radiosonde data with the following filename: yyyymmddhh<any_text>.txt ")

    date, time = os.path.basename(path[0])[:15].split('_')

    if int(date[:4]) not in np.arange(1960,9999,1) or \
        int(date[4:6]) not in np.arange(1,13,1) \
            or int(date[6:8]) not in np.arange(1,31,1):
        sys.exit("--Error: The date provided in the radiosond filename is not correct. Please revise the filename format. It should start with 'yyyymmdd_hhmmss' and end with '.txt' ")

    if int(time[:2]) not in np.arange(0,24,1) or \
        int(time[2:4]) not in np.arange(0,60,1) \
            or int(date[4:6]) not in np.arange(0,60,1):
        sys.exit("--Error: The time provided in the radiosond filename is not correct. Please revise the filename format. It should start with 'yyyymmdd_hhmmss' and end with '.txt' ")
        
    data = np.genfromtxt(path[0],skip_header = skip_header, 
                         skip_footer = skip_footer,
                         delimiter = lib_delimiter[delimiter], 
                         autostrip = True,
                         usecols = np.array(usecols) - 1, dtype = float)

    if len(usecols) == 3:
        parameters = ['P', 'T']
    if len(usecols) == 4:
        parameters = ['P', 'T', 'RH']

    alt = data[:,0]
    atmo = xr.DataArray(data[:,1:], 
                        coords = [alt, parameters], 
                        dims = ['height', 'parameters'] )
    
    return(date, time, atmo)

def folder_to_sector(folder):

    fld = ['north','east','south','west']
    sec = [1,2,3,4]
        
    folder_tmp = folder.values
    
    sector_tmp = np.nan * np.zeros(folder_tmp.shape)
    
    for i in range(len(fld)):
        sector_tmp[folder == fld[i]] = sec[i]
    
    sector = xr.DataArray(sector_tmp, coords = folder.coords, dims = folder.dims)
    
    return(sector)

def folder_to_position(folder):

    fld = ['static', '-45', '+45']
    sec = [0, 1, 2]
        
    folder_tmp = folder.values
    
    position_tmp = np.nan * np.zeros(folder_tmp.shape)
    
    for i in range(len(fld)):
        position_tmp[folder == fld[i]] = sec[i]
    
    position = xr.DataArray(position_tmp, coords = folder.coords, dims = folder.dims)
    
    return(position)

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