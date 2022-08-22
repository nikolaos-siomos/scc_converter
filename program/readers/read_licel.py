import os
import numpy as np
import pandas as pd
import glob
from datetime import datetime as dt
import xarray as xr

# Read measurement
def dtfs(dir_meas, mcode):
    
    """ Reads information from the raw licel files"""
    
    # Setting sig, info, and time as empty lists in the beggining    
    sig_raw = []     
    shots = []
    folder = []
    start_time_arr = []
    end_time_arr = []
    filename = []
    
    if not(os.path.exists(dir_meas)):
        print('---- Error : The folder for reading signals does not exist! \r\n' +\
              f'---- Check the input directory! \n Given folder: {dir_meas}')
    
    else:
        
        mfiles = glob.glob(os.path.join(dir_meas,mcode + '*'))
        
        # for existing directory and files inside it, starts the reading of files     
        if len(mfiles) > 0:
            print(f'-- Folder contains {len(mfiles)} file(s)!')
            
            buffer = read_buffer(mfiles[0])
            sep = find_sep(buffer)
            
            # Reading the licel file metadatas (header) - only for the first file
            meas_info = pd.Series()
            channel_info = pd.DataFrame()
            meas_info = read_geodata(meas_info, buffer = buffer, sep = sep)
            meas_info = read_lasers(meas_info, buffer = buffer, sep = sep)
            channel_info = read_header(channel_info, buffer = buffer, sep = sep)
            
            channels = channel_info.index.values
            bins_arr = np.arange(1., channel_info.bins.max() + 1.)

            # Creating empty signal, shots, and time arrays
            start_time_arr = np.nan*np.zeros(len(mfiles), dtype = object)
            end_time_arr = np.nan*np.zeros(len(mfiles), dtype = object)

            shots_arr = np.nan*np.zeros((len(mfiles), len(channels)), dtype = object)
            sig_arr = np.nan*np.zeros((len(mfiles), len(channels), len(bins_arr)), dtype = float)

            filename = np.empty(len(mfiles), dtype = object)
            folder = np.empty(len(mfiles), dtype = object)

            # Iterate over the files
            for k in range(len(mfiles)):
                
                filename[k] = os.path.basename(mfiles[k])

                buffer = read_buffer(mfiles[k])

                sep = find_sep(buffer)
                
                stime, etime = read_time(buffer = buffer, sep = sep)

                shots_arr[k,:] = read_shots(buffer = buffer, sep = sep)
                
                sig = read_body(channel_info, buffer = buffer, sep = sep)

                # Store signal, start and end time
                sig_arr[k, :, :] = sig

                start_time_arr[k] = stime

                end_time_arr[k] = etime
                     
                if (mfiles[k]).split(os.sep)[-2] in ['north', 'east', 'south', 'west', 'inner', 'outer', '+45', '-45', 'static']:
                    folder[k] = (mfiles[k]).split(os.sep)[-2]
            
            sig_raw = xr.DataArray(sig_arr, 
                                   coords=[end_time_arr, channels, bins_arr],
                                   dims=['time', 'channel', 'bins']) 
            
            shots = xr.DataArray(shots_arr,  
                                 coords=[end_time_arr, channels],
                                 dims=['time', 'channel'])
            
            tdata = np.array([folder, filename, 
                              start_time_arr, end_time_arr], dtype = object)

            properties = ['folder', 'filename', 'start_time', 'end_time']
            
            time_info = pd.DataFrame(tdata.T,  
                                     index = end_time_arr,
                                     columns = properties)  
                        
            # Sort by time
            sig_raw = sig_raw.sortby('time').copy()
            shots = shots.sortby('time').copy()
            time_info = time_info.sort_index()
            
        else:
            print('---- Warning! Folder empty \n'+\
                  f'---> !! Skip reading measurement files from folder {dir_meas}')  

    return(meas_info, channel_info, time_info, sig_raw, shots)


def read_body(channel_info, buffer, sep):
    
    """ Reads the information from the raw licel files below the header.
    Blocks are separated by #"""

    data = buffer[sep+4:]

    max_bins = int(channel_info.bins.max())

    n_channels = len(channel_info.index)
    
    # Parse data into dataframe    
    sig_raw_arr = []

    nbin_s = 0
    sig_raw_arr = np.nan*np.zeros((n_channels, max_bins))

    for j in range(n_channels):
        nbins = int(channel_info.bins.iloc[j])
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

def read_geodata(meas_info, buffer, sep):

    """ Retrieves location and geometry relevant information from 
    the licel header [altitude, latitude, longitude, 
    zenith angle, azimuth angle]"""

    # Now i points to the start of search_sequence, AKA end of header
    header_bytes = buffer[0:sep-1]
    
    # Convert header to text, parse metadata
    header = str(header_bytes, encoding="utf-8").split("\r\n")

    metadata = header[1].split()

    # cfg.lidar['location'] = metadata[0]

    meas_info['altitude'] = float(metadata[5])    
    meas_info['latitude'] = float(metadata[6])
    meas_info['longitude'] = float(metadata[7])
    
    if len(metadata) > 8:
        meas_info['zenith_angle'] = float(metadata[8])

    if len(metadata) > 9:
        meas_info['azimuth_angle'] = float(metadata[9])

    return(meas_info)

def read_lasers(meas_info, buffer, sep):

    """ Retrieves laser relevant information from 
    the licel header [laser A repetion rate, laser B repetion rate if it exists
    laser C repetion rate if it exists]"""
    
    # Now i points to the start of search_sequence, AKA end of header
    header_bytes = buffer[0:sep-1]
    
    # Convert header to text, parse metadata
    header = str(header_bytes, encoding="utf-8").split("\r\n")

    metadata = header[2].split()

    meas_info['laser_A_repetition_rate'] = float(metadata[1])

    if len(metadata) > 2:
        meas_info['laser_B_repetition_rate'] = float(metadata[3])
        
    if len(metadata) > 5:
        meas_info['laser_C_repetition_rate'] = float(metadata[6])
        
    return(meas_info)

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

def read_header(channel_info, buffer, sep):
    
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
        channel_ID.append(header[i, -1] + '_L' + str(int(header[i, 2])))   
    
    cols = ['active', 'acquisition_mode', 'laser', 'bins', 
            'laser_polarization', 'pmt_high_voltage', 'range_resolution', 
            'wave_pol', 'unk1', 'unk2', 'unk3', 'unk4', 
            'analog_to_digital_resolution', 'shots', 'data_acquisition_range',
            'channel_id']
    
    arr_head = pd.DataFrame(header, index = channel_ID, columns = cols, 
                            dtype = object)
    
    channel_info.index = channel_ID

    info_columns = ['acquisition_mode', 'laser', 'bins', 'laser_polarization', 
                    'pmt_high_voltage', 'range_resolution', 
                    'data_acquisition_range', 'analog_to_digital_resolution']
    
    channel_info.loc[:, 'channel_id'] = arr_head.loc[:, 'channel_id'].copy().values
    channel_info.loc[:, info_columns] = arr_head.loc[:, info_columns].copy().values.astype(float)

    mask_an = channel_info.loc[:,'acquisition_mode'].values == 0
    channel_info.loc[:,'data_acquisition_range'][mask_an] = 1000.*channel_info.loc[:,'data_acquisition_range'][mask_an]
    channel_info.loc[:,'data_acquisition_range'][~mask_an] = np.nan

    wave = np.array(list(np.char.split(arr_head.wave_pol.values.astype('str'),
                                       sep='.')))[:,0].astype(float)
    
    channel_info.loc[:,'detected_wavelength'] = wave

    return(channel_info)

def read_shots(buffer, sep):
    
    """ Gets the number of shots for each channel and file"""

    # Now i points to the start of search_sequence, AKA end of header
    header_bytes = buffer[0:sep-1]
    
    # Convert header to text, parse metadata
    header = str(header_bytes, encoding="utf-8").split("\r\n")

    # Header rows
    header = np.array(list(np.char.split(header[3:])),dtype = object)

    cols = ['active', 'acquisition_mode', 'laser', 'bins', 
            'laser_polarization', 'pmt_high_voltage', 'range_resolution', 
            'wave_pol', 'unk1', 'unk2', 'unk3', 'unk4', 
            'analog_to_digital_resolution', 'shots', 'data_acquisition_range',
            'channel_id']
    
    
    ind_shots = np.where(np.array(cols) == 'shots')[0][0]
    
    shots = header[:,ind_shots].astype(int)
    
    return(shots)

def read_buffer(fname):
       
    """ Reads the binary file as a single byte sequence (buffer)"""
    
    with open(fname, 'rb') as f:
        buffer = f.read()
        
    return(buffer)