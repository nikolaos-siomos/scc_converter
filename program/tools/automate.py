"""
@author: Peristera
"""
import os, sys
import numpy as np
import xarray as xr
import pandas as pd

def get_meas_type(path):

    """Identifies if the measurement being processed is a Rayleigh, 
    a Telecover, a Depolarization Calibration, or a standalone Dark."""
    
    meas_type = []

    list_dirs = [d for d in os.listdir(path) if os.path.isdir(os.path.join(path,d))]

    allowed_types = ['radiosonde', 'rayleigh', 'telecover', 'calibration', 'dark']

    if 'radiosonde' in list_dirs:
        meas_type.append('radiosonde')
        
    if 'rayleigh' in list_dirs: 
        meas_type.append('rayleigh')

    if 'telecover' in list_dirs:
        meas_type.append('telecover')

    if 'calibration' in list_dirs:
        meas_type.append('calibration')

    if 'dark' in list_dirs:
        meas_type.append('dark')
    
    if any(meas_type_i not in allowed_types for meas_type_i in meas_type):
        sys.exit('-- Error: None of the expected folders were detected in the parent folder. Please use at least one of the following: dark, rayleigh, telecover, calibration or calibration_plus and calibration_minus')
                
    return(meas_type)

def check_rayleigh(path):

    """Ensures that the rayleigh folder is properly set, otherwise it raises 
    an error """
        
    if os.path.exists(path):
        
        allowed_folders = ['dark', 'normal']
    
        list_dirs = [d for d in os.listdir(path) 
                     if os.path.isdir(os.path.join(path,d))]
    
        if 'normal' not in list_dirs:
            sys.exit('-- Error: The normal folder was not detected in the '+
                     'rayleigh folder. Please provide it!')
        
        if 'dark' not in list_dirs:
            print('-- Warning: No dark folder detected in the rayleigh folder. '+
                  'The generated rayleigh files will not be compatible with ATLAS!')
    
        if any(dir_i not in allowed_folders for dir_i in list_dirs):
            sys.exit(f'-- Error: The ./rayleigh folder contains at least one directory that is different from the expected ones ({allowed_folders}). Please make sure only the allowed directories exist there')
            
    return()

def check_telecover(path, files_per_sector):

    """Ensures that the telecover folder is properly set, otherwise it raises 
    an error """
        
    if os.path.exists(path):

        allowed_folders = ['dark', 'sectors']
    
        allowed_sfolders = ['north', 'east', 'south', 'west', 'inner', 'outer']
        
        list_dirs = [d for d in os.listdir(path) 
                     if os.path.isdir(os.path.join(path,d))]
    
        if 'sectors' not in list_dirs:
            sys.exit('-- Error: The sectors folder was not detected in the '+
                     'telecover folder. Please provide it!')
    
        if 'dark' not in list_dirs:
            print('-- Warning: No dark folder detected in the rayleigh folder. '+
                  'The generated telecover files will not be compatible with ATLAS!')
    
        if any(dir_i not in allowed_folders for dir_i in list_dirs):
            sys.exit(f'-- Error: The ./telecover folder contains at least one directory that is different from the expected ones ({allowed_folders}). Please make sure only the allowed directories exist there')
              
        if files_per_sector:
            
            if 'sectors' not in list_dirs:
                sys.exit('-- Error: The ./telecover/sectors folder was not detected '+
                         'in the telecover folder. All sector files must be '+
                         'provide in this folder when the files_per_sector '+
                         'argument is used!')
                
        else:
    
            path_sec = os.path.join(path,'sectors')
    
            
            list_sdirs = [d for d in os.listdir(path_sec) 
                         if os.path.isdir(os.path.join(path_sec,d))]
    
            if 'north' not in list_sdirs and 'east' not in list_sdirs and \
                'south' not in list_sdirs and 'west' not in list_sdirs and \
                    'inner' not in list_sdirs and 'outer' not in list_sdirs:
                    
                sys.exit('-- Error: No sector folders were detected in the ' +
                         './telecover/sectors folder. Please either provide ' +
                         'north east south west and/or inner outer folders ' +
                         'or provide the files_per_sector argument as: '+
                         '-n <number_of_files_per sector>')
    
            if ('north' not in list_sdirs or 'east' not in list_sdirs or \
                'south' not in list_sdirs or 'west' not in list_sdirs) and \
                    ('inner' not in list_sdirs or 'outer' in list_sdirs):
            
                sys.exit('-- Error: No complete set is provided in the ' +
                         'in ./telecover/sectors folder. Please provide either '+
                         'all of north east south west or both of '+
                         'inner outer folders') 
                
            if any(dir_i not in allowed_sfolders for dir_i in list_dirs):
                sys.exit(f'-- Error: The ./telecover/sectors folder contains at least one directory that is different from the expected ones ({allowed_folders}). Please make sure only the allowed directories exist there')
  
    return()

def check_calibration(path):

    """Ensures that the calibration folder is properly set, otherwise it raises 
    an error """
    
    if os.path.exists(path):
    
        allowed_folders = ['dark', 'static', '+45','-45']
        
        list_dirs = [d for d in os.listdir(path) 
                     if os.path.isdir(os.path.join(path,d))]
    
        if ('-45' not in list_dirs and '+45' not in list_dirs) \
            and 'static' not in list_dirs:
            sys.exit('-- Error: None of the expected folders were detected in the calibration folder. Please provide the -45 and +45 folders for a D90 calibration or the static folder for a calibration without rotation')
        
        if ('-45' not in list_dirs or '+45' not in list_dirs) \
            and 'static' not in list_dirs:
            sys.exit('-- Error: Only one of the -45 and +45 folders was provided for the D90 calibration. Please include both folders')
    
        if ('-45' in list_dirs or '+45' in list_dirs) \
            and 'static' in list_dirs:
            sys.exit('-- Error: Folders for more that one calibration technique were provided. Please keep either the -45 and +45 folders for a D90 calibration or the static folder for a calibration without rotation')
     
        if not 'dark' in list_dirs:
            print('-- Warning: No dark folder detected for the polarization calibration. The generated files will not be compatible with the ATLAS software!')
    
        if any(dir_i not in allowed_folders for dir_i in list_dirs):
            sys.exit(f'-- Error: The ./calibration folder contains at least one directory that is different from the expected ones ({allowed_folders}). Please make sure only the allowed directories exist there')

    return()

def detect_overflows(sig, shots, channel_info, time_info, method = 0):

    """
    General:
        Detects and removes lidar profiles with photon values above the
        maximum allowed countrate or analog values above the data 
        acquisition range
        
    Input:
        sig: 
            A 3D xarray with the lidar signals, it should include the 
            following dimensions: (time, channel, bins). 

        shots:
            A 2D xarray with the laser shots per timeframe and channel, 
            it should include the following dimensions: (time, channel).  
            
        channel_info:
            A pandas Dataframe with exactly one index entry per lidar channel.
            the following columns must be included:
                
            channel_id: 
                The channel_id per channel 
                
            acquisition_mode: 
                The acquision_mode values per channel 
                (0 for analog, 1 for photon)
                
            data_acquisition_range: 
                The data acquisition range of the analog channels.

        time_info: 
            A pandas dataframe with exactly one index entry per 
            lidar timeframe. The index should correspond to the time 
            dimension of sig. The following column must be included         
            
            filename: 
                The raw file filename. 
        
        method:
            An integer. If set to 0 only the check for overflows will be 
            performed and an error will be raised if a single value is 
            encountered. If set to 1 all files with overflows will be
            discarded. If set to 2 overflows will be removed and 
            interpolated instead
            
            
    Returns:
        
        sig, shots, time:
            If no overflows are detected then the 3 variables reuturn intact
            
            If overflows are detected:
                method = 0 : the code exits with a diagnostic error
            
                method = 1 : timeframes with at least one overflowed bin are
                             removed
                
                method = 2 : only sig changes, overflowed values are replaced
                             by interpolated values from the surrounding bins
            
    """
    
    print('-----------------------------------------')
    print('Handling overflow values...')
    print('-----------------------------------------')

    channel_id = channel_info.channel_id.values
    
    acquisition_mode = channel_info.acquisition_mode.values
    
    daq_range = channel_info.data_acquisition_range.values

    filename = time_info.filename
        
    daq_range = pd.Series(daq_range, index = channel_id)

    acquisition_mode = pd.Series(acquisition_mode, index = channel_id)
        
    # Get an overflow mask for each bin
    mask = get_overflow_mask(sig, acquisition_mode, daq_range)

    if method == 0 and mask.any(): # Detect the problematic profiles and raise error

        overflow_method_0(mask = mask, filename = filename)
            
    if method == 1 and mask.any(): # Remove the problematic profiles
    
        sig, shots, time_info = overflow_method_1(sig = sig.copy(), 
                                                  shots = shots.copy(),
                                                  time_info = time_info, 
                                                  mask = mask, 
                                                  filename = filename)
        print("Profiles with overflowed bin were succesfully removed!")
        
    if method == 2 and mask.any(): # Replace the overflowed values with interpolated ones from the nearby bins
        
        sig = overflow_method_2(sig = sig.copy(), 
                                mask = mask, 
                                filename = filename)
        print("Overflowed were succesfully replaced!")
    


    return(sig, shots, time_info)

def get_overflow_mask(sig, acquisition_mode, daq_range):

    channels = sig.channel.values
    
    time = sig.time.values

    bins = sig.bins.values
    
    mask = xr.DataArray(np.zeros([time.size, channels.size, bins.size], 
                                 dtype = bool),
                        dims = ['time','channel', 'bins'],
                        coords = [time, channels, bins])
    
    for ch in channels:

        ch_d = dict(channel = ch)

        if acquisition_mode.loc[ch] == 1: #3rd digit of channel name is the acquisition mode (a or p)
        
            max_count = np.power(2.,15)

            crit = (sig.loc[ch_d] >= max_count)
            
            if crit.any():
                print(f"-- Warning: Channel {ch} - Photon signal count values above the maximum allowed summed counts were detected! ")

                mask.loc[ch_d] = crit.values                                           

        if acquisition_mode.loc[ch] == 0: #3rd digit of channel name is the acquisition mode (a or p)

            max_mV = daq_range.loc[ch]
        
            crit = (sig.loc[ch_d] >= max_mV) | (sig.loc[ch_d] <= 0.)
            
            if crit.any():
                print(f"-- Warning: Channel {ch} - Analog signal mV values above the data acqusition range or below 0. were detected! ")

                mask.loc[ch_d] = crit.values
    
    return(mask)

def overflow_method_0(mask, filename):
    
    time = mask.time.values
    
    channels = mask.channel.values
    
    bins = mask.bins.values
    
    # use the index and not the time....
    if mask.any():
        
        print("-- Error at least one bin with an overflow was detected. ")
        print("-- Please revise the following bins: ")
        
        mask_t = mask.any(dim = 'bins').any(dim = 'channel').values
                    
        time_ovf = time[mask_t]
                    
        for t in time_ovf:
            filename_ovf = filename[t]
            
            t_d = dict(time = t)
                            
            ch_ovf = channels[mask.any(dim = 'bins').loc[t_d].values]
            
            for ch in ch_ovf:
            
                ch_d = dict(channel = ch)
                
                bins_ovf = bins[mask.loc[t_d].loc[ch_d].values].astype(int)
                
                print(f"    file: {filename_ovf} | ch: {ch} | bins: {bins_ovf}")
        
        print("-- In order to continue with an automated overflow removal use the trim_overflow argument with value 1 or 2 (default is 0) ")

        sys.exit("-- Aborting!")
        
    return()

def overflow_method_1(sig, shots, time_info, mask, filename):

    time = mask.time.values
    
    mask_t = mask.any(dim = 'bins').any(dim = 'channel').values

    print(f"-- Warning: {np.sum(mask_t)} profiles with at least one overflowed bin have been detected ")
    print("-- Warning: trim_overflows = 1: The following profiles have been removed ")
                
    time_ovf = time[mask_t]

    time_cor = time[~mask_t]
                
    for t in time_ovf:
        filename_ovf = filename[t]
        
        print(f"    {filename_ovf} ")

    time_d = dict(time = time_cor)
    
    sig_out = sig.copy().loc[time_d] 

    shots_out = shots.copy().loc[time_d] 
    
    time_info = time_info.loc[time_cor,:]
    
    return(sig_out, shots_out, time_info)

def overflow_method_2(sig, mask, filename):

    mask_t = mask.any(dim = 'bins').any(dim = 'channel').values

    ovfs = mask.sum(dim = 'bins')

    print(f"-- Warning: {np.sum(mask_t)} profiles with at least one overflowed bin have been detected ")
    print("-- Warning: trim_overflows = 2: Will attempt to replace the overflows ")
          
    if (ovfs > 100).any():
        print("-- Warning: More that 100 overflowed bins encountered in single profiles... Interpolation is too risky, please revise the input files or consider switching to --trim_overflows 2 ")
    
    sig = sig.copy().where(~mask)
    
    sig_out = sig.copy().interpolate_na(dim = "bins", method = "linear", 
                                        fill_value = "extrapolate")

    print(f"-- Warning: {np.sum(mask).values} overflows have been replaced by interpolating across the bins ")
    
    return(sig_out)
  