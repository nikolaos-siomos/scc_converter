import os
import numpy as np
import pandas as pd
import glob
from datetime import datetime as dt
import xarray as xr

# Read measurement
def dtfs(cfg, dir_meas, ):
    
    """ Reads information from the raw licel files"""
    
    # Get raw lidar files code from the ini file
    if 'm_code' in cfg.lidar.index:  m_code = cfg.lidar.m_code
    else: m_code = ''

    # Setting sig, info, and time as empty lists in the beggining    
    sig_raw = []     
    shots = []
    folder = []
    start_time_arr = []
    end_time_arr = []
    
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
            cfg = read_lasers(cfg, buffer = buffer, sep = sep)
            cfg = read_header(cfg, buffer = buffer, sep = sep)
            
            channels = cfg.channels.index.values
            bins_arr = np.arange(1., cfg.channels.bins.max() + 1.)

            # Creating empty signal, shots, and time arrays
            start_time_arr = np.nan*np.zeros(len(mfiles), dtype = object)
            end_time_arr = np.nan*np.zeros(len(mfiles), dtype = object)

            shots_arr = np.nan*np.zeros((len(mfiles), len(channels)), dtype = object)
            sig_arr = np.nan*np.zeros((len(mfiles), len(channels), len(bins_arr)), dtype = float)

            folder = np.empty(len(mfiles), dtype = object)

            # Iterate over the files
            for k in range(len(mfiles)):

                buffer = read_buffer(mfiles[k])

                sep = find_sep(buffer)
                
                stime, etime = read_time(buffer = buffer, sep = sep)

                shots_arr[k,:] = read_shots(buffer = buffer, sep = sep)
                
                sig = read_body(cfg, buffer = buffer, sep = sep)

                # Store signal, start and end time
                sig_arr[k, :, :] = sig

                start_time_arr[k] = stime

                end_time_arr[k] = etime
                     
                if (mfiles[k]).split(os.sep)[-2] in ['north', 'east', 'south', 'west', 'inner', 'outer']:
                    folder[k] = (mfiles[k]).split(os.sep)[-2]
            
            sig_raw = xr.DataArray(sig_arr, 
                                   coords=[start_time_arr, channels, bins_arr],
                                   dims=['time', 'channel', 'bins']) 
            
            shots = xr.DataArray(shots_arr,  
                                 coords=[start_time_arr, channels],
                                 dims=['time', 'channel'])
            
            folder = xr.DataArray(folder,  
                                  coords=[start_time_arr],
                                  dims=['time'])            
                        
            # Sort by time
            sig_raw = sig_raw.sortby('time').copy()
            shots = shots.sortby('time').copy()
            folder = folder.sortby('time').copy()
            start_time_arr = np.sort(start_time_arr)
            end_time_arr = np.sort(end_time_arr)
            
        else:
            print('---- Warning! Folder empty \n'+\
                  f'---> !! Skip reading measurement files from folder {dir_meas}')  

    return(cfg, start_time_arr, end_time_arr, sig_raw, shots, folder)


def read_body(cfg, buffer, sep):
    
    """ Reads the information from the raw licel files below the header.
    Blocks are separated by #"""

    data = buffer[sep+4:]

    max_bins = int(cfg.channels.bins.max())

    n_channels = len(cfg.channels.index)
    
    # Parse data into dataframe    
    sig_raw_arr = []

    nbin_s = 0
    sig_raw_arr = np.nan*np.zeros((n_channels, max_bins))

    for j in range(n_channels):
        nbins = int(cfg.channels.bins.iloc[j])
        nbin_e = nbin_s + 4*nbins
        icount = 0
        for i in range(nbin_s, nbin_e, 4):
            sig_raw_arr[j,icount] = int.from_bytes(data[i:i+4], 
                                                   byteorder = 'little')
            icount = icount + 1

        nbin_s = nbin_e + 2
    
    return(sig_raw_arr)

def find_sep(buffer):
    
    """ Identifies the location of the header separator field: \r\n\r\n"""
    
    search_sequence = bytearray("\r\n\r\n", encoding="utf-8")
    i = 0
    while buffer[i:i+4] != search_sequence:
        i = i + 1
        if i >= len(buffer):
            raise Exception("Could not find header/data separator. Is this a licel file?")
    sep = i     
    
    return(sep)

def read_geodata(cfg, buffer, sep):

    """ Retrieves location and geometry relevant information from 
    the licel header [altitude, latitude, longitude, 
    zenith angle, azimuth angle]"""

    # Now i points to the start of search_sequence, AKA end of header
    header_bytes = buffer[0:sep-1]
    
    # Convert header to text, parse metadata
    header = str(header_bytes, encoding="utf-8").split("\r\n")

    metadata = header[1].split()

    # cfg.lidar['location'] = metadata[0]

    cfg.lidar['altitude'] = float(metadata[5])    
    cfg.lidar['latitude'] = float(metadata[6])
    cfg.lidar['longitude'] = float(metadata[7])
    
    if len(metadata) > 8:
        cfg.lidar['zenith'] = float(metadata[8])

    if len(metadata) > 9:
        cfg.lidar['azimuth'] = float(metadata[9])

    return(cfg)

def read_lasers(cfg, buffer, sep):

    """ Retrieves laser relevant information from 
    the licel header [laser A repetion rate, laser B repetion rate if it exists
    laser C repetion rate if it exists]"""
    
    # Now i points to the start of search_sequence, AKA end of header
    header_bytes = buffer[0:sep-1]
    
    # Convert header to text, parse metadata
    header = str(header_bytes, encoding="utf-8").split("\r\n")

    metadata = header[2].split()

    cfg.lidar['laser_A_rep_rate'] = float(metadata[1])

    if len(metadata) > 2:
        cfg.lidar['laser_B_rep_rate'] = float(metadata[3])
        
    if len(metadata) > 5:
        cfg.lidar['laser_C_rep_rate'] = float(metadata[6])
    return(cfg)

def read_time(buffer, sep):
    
    """ Retrieves temporal information from 
    the licel header [start time, stop time]"""

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

def read_header(cfg, buffer, sep):
    
    """ Collects channel specific information from the licel header
    [analog/photon mode (0/1), laser number (A,B,C), number of range bins,
     laser polarization, high voltage, vertical resolution, 
     ADC range in mV (20,100,500), ADC bit used for the bit to mV conversion
     laser repetiotion rate, detected wavelength, channel polarization] """


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
    
    info_columns = ['ch_mode', 'laser', 'bins', 'laser_pol', 'voltage', 'resol', 
                    'ADC_range', 'ADC_bit']
    
    info = arr_head.loc[:, info_columns].copy().astype(float)

    wave = np.array(list(np.char.split(arr_head.wave_pol.values.astype('str'),
                                       sep='.')))[:,0].astype(float)
    
    ch_pol = np.array(list(np.char.split(arr_head.wave_pol.values.astype('str'),
                                         sep='.')))[:,1].astype(str)
    
    info.loc[:,'rep_rate'] = cfg.lidar['laser_A_rep_rate']
    if (info.loc[:,'laser'] == 2).any():
        info.loc[:,'rep_rate'][info.loc[:,'laser'] == 2] = cfg.lidar['laser_B_rep_rate']
    if (info.loc[:,'laser'] == 3).any():
        info.loc[:,'rep_rate'][info.loc[:,'laser'] == 3] = cfg.lidar['laser_C_rep_rate']
    
    info.loc[:,'wave'] = wave
    info.loc[:,'ch_pol'] = ch_pol
        
    for key in info.columns:
        if key not in cfg.channels.columns:
            cfg.channels.loc[:,key] = info.loc[:,key].values
    
    return(cfg)

def read_shots(buffer, sep):
    
    """ Gets the number of shots for each channel and file"""

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
    
    shots = arr_head.loc[:, 'shots'].copy().astype(int).values
    
    return(shots)

def read_buffer(fname):
       
    """ Reads the binary file as a single byte sequence (buffer)"""
    
    with open(fname, 'rb') as f:
        buffer = f.read()
        
    return(buffer)