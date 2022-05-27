"""
@authors: Siomos and Paschou

================
Input:
    arg 1: full filename from current running directory, should be a string scalar
    arg 2: the code (first letters) of the measurements of the lidar 
Returns:
    arg 1-2: the signals if xarray format with dimensions (time, channel, bins)
    arg 3-4: info from header per channel (e.g. pmt type, laser polarization, bins, resolution, shots, channel type(p,s, total), ADC_range, ADC_bit, wavelength)
    arg 5-6: the ground altitude and the measurement angle(off-zenith)
"""
import os
import numpy as np
import pandas as pd
import glob
from datetime import datetime as dt
import xarray as xr

# Read measurement
def dtfs(cfg, dir_meas, meas_type):
    
    # Get raw lidar files code from the ini file
    if 'm_code' in cfg.lidar.index:  m_code = cfg.lidar.m_code
    else: m_code = ''

    # Setting sig, info, and time as empty lists in the beggining    
    sig_raw = []     
    info = []
    
    if not(os.path.exists(dir_meas)):
        print('---- Error : The folder for reading signals does not exist! \r\n' +\
              f'---- Check the input directory! \n Given folder: {dir_meas}')
    
    else:
        
        mfiles = glob.glob(os.path.join(dir_meas,m_code + '*'))
        
        # for existing directory and files inside it, starts the reading of files     
        if len(mfiles) > 0:
            print(f'-- Folder contains {len(mfiles)} file(s)!')
            
            buffer = read_buffer(mfiles[0])
            sep = find_sep(buffer)
            
            # Reading the licel file metadatas (header) - only for the first file
            cfg = read_geodata(cfg, buffer = buffer, sep = sep)
            info = read_header(buffer, sep)
            
            # Creating empty signal and time arrays
            start_time_arr = np.nan*np.zeros(len(mfiles), dtype = object)
            end_time_arr = np.nan*np.zeros(len(mfiles), dtype = object)
            sig_arr = np.nan*np.zeros((len(mfiles), info.shape[0], int(info.bins.max())), dtype = float)

            # Iterate over the files
            for k in range(len(mfiles)):

                buffer = read_buffer(mfiles[k])

                sep = find_sep(buffer)
                
                stime, etime = read_time(buffer = buffer, sep = sep, meas_type = meas_type)

                sig = read_body(buffer = buffer, info = info, sep = sep)

                # Store signal, start and end time
                sig_arr[k, :, :] = sig

                start_time_arr[k] = stime

                end_time_arr[k] = etime

            channels = info.index.values
            bins_arr = np.arange(1., info.bins.max() + 1.)
            
            sig_raw = xr.DataArray(sig_arr, 
                                   coords=[start_time_arr, channels, bins_arr], #range_sig
                                   dims=['time', 'channel', 'bins']) #'range' 
                        
            # Sort by time
            sig_raw = sig_raw.sortby('time')
            start_time_arr = np.sort(start_time_arr)
            end_time_arr = np.sort(end_time_arr)
            
            cfg.lidar[f'{meas_type}_start_time'] = start_time_arr[0]
            cfg.lidar[f'{meas_type}_end_time'] = end_time_arr[-1]
            cfg.lidar[f'{meas_type}_temporal_resolution'] = end_time_arr[0] - start_time_arr[0]
        else:
            print('---- Warning! Folder empty \n'+\
                  f'---> !! Skip reading measurement files from folder {dir_meas}')  

    return(cfg, info, sig_raw)


def read_body(buffer, info, sep):
    
    data = buffer[sep+4:]

    max_bins = int(info.bins.max())
    
    # Parse data into dataframe    
    sig_raw_arr = []

    nbin_s = 0
    sig_raw_arr = np.nan*np.zeros((info.shape[0], max_bins))

    for j in range(info.shape[0]):
        nbins = int(info.bins.iloc[j])
        nbin_e = nbin_s + 4*nbins
        icount = 0
        for i in range(nbin_s, nbin_e, 4):
            sig_raw_arr[j,icount] = int.from_bytes(data[i:i+4], 
                                                   byteorder = 'little')
            icount = icount + 1

        nbin_s = nbin_e + 2
    
    return(sig_raw_arr)

def find_sep(buffer):
    
    # We search the file for the \r\n\r\n sequence that separates the header from the data
    search_sequence = bytearray("\r\n\r\n", encoding="utf-8")
    i = 0
    while buffer[i:i+4] != search_sequence:
        i = i + 1
        if i >= len(buffer):
            raise Exception("Could not find header/data separator. Is this a licel file?")
    sep = i     
    
    return(sep)

def read_geodata(cfg, buffer, sep):

    # Now i points to the start of search_sequence, AKA end of header
    header_bytes = buffer[0:sep-1]
    
    # Convert header to text, parse metadata
    header = str(header_bytes, encoding="utf-8").split("\r\n")

    metadata = header[1].split()

    cfg.lidar['location'] = metadata[0]

    cfg.lidar['altitude'] = float(metadata[5])    
    cfg.lidar['latitude'] = float(metadata[6])
    cfg.lidar['longitude'] = float(metadata[7])
    
    if len(metadata) > 8:
        cfg.lidar['zenith'] = float(metadata[8])

    if len(metadata) > 9:
        cfg.lidar['azimuth'] = float(metadata[9])

    return(cfg)

def read_time(buffer, sep, meas_type):

    # Now i points to the start of search_sequence, AKA end of header
    header_bytes = buffer[0:sep-1]
    
    # Convert header to text, parse metadata
    header = str(header_bytes, encoding="utf-8").split("\r\n")

    metadata = header[1].split()

    start_date = metadata[1]
    start_time = metadata[2]
    end_date = metadata[3]
    end_time = metadata[4]

    stime = dt.strptime(start_date + ' ' + start_time, "%d/%m/%Y %H:%M:%S") # start meas
    etime = dt.strptime(end_date + ' ' + end_time, "%d/%m/%Y %H:%M:%S") # start meas
        
    return(stime, etime)

def read_header(buffer, sep):

    # Now i points to the start of search_sequence, AKA end of header
    header_bytes = buffer[0:sep-1]
    
    # Convert header to text, parse metadata
    header = str(header_bytes, encoding="utf-8").split("\r\n")

    # Header rows
    channel_ID = []
    header = np.array(list(np.char.split(header[3:])),dtype = object)

    for i in range(len(header[:,-1])):
        channel_ID.append(header[i, -1] + '_L' + str(header[i, 2]))   
    
    cols = ['active', 'ch_mode', 'laser', 'bins', 
            'laser_pol', 'voltage', 'resol', 'wave_pol', 
            'unk1', 'unk2', 'unk3', 'unk4', 'ADC_bit', 'shots', 
            'ADC_range', 'recorder']
    
    arr_head = pd.DataFrame(header, index = channel_ID, columns = cols, 
                            dtype = object)
    
    info_idx = ['ch_mode', 'bins', 'laser_pol', 'voltage', 'resol', 
                'shots', 'ADC_range', 'ADC_bit']
    
    info = arr_head.loc[:, info_idx].copy().astype(float)

    wave = np.array(list(np.char.split(arr_head.wave_pol.values.astype('str'),
                                       sep='.')))[:,0].astype(float)
    
    ch_pol = np.array(list(np.char.split(arr_head.wave_pol.values.astype('str'),
                                         sep='.')))[:,1].astype(str)
    info.loc[:,'wave'] = wave
    info.loc[:,'ch_pol'] = ch_pol
    
    return(info)

def read_buffer(fname):
    
    with open(fname, 'rb') as f:
        buffer = f.read()
        
    return(buffer)