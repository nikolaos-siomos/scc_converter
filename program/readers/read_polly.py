"""
@author: Peristera

Read the raw PollyXT data
"""
import glob
import pandas as pd
import numpy as np
import os
import xarray as xr
from lidar_processing import signal
from readers.read_thelisys_ascii import raw_to_config


def dtfs(dir_meas, cfg, cal_angle=0.):
    
    # Get raw lidar files code from the ini file
    m_code = cfg.lidar.m_code
        
    sig_raw, sig_raw_dev = [], []     
    info, info_dev = [], []
    ground_alt, SZA, azimuth = [], [], []
    
    if not(os.path.exists(dir_meas)):
        print('---- Error : The folder for reading signals does not exist! \r\n' +\
              f'---- Check the input directory! \n Given folder: {dir_meas}')
        #sys.exit(0)
    
    else:
        
        mfiles = glob.glob(os.path.join(dir_meas,'*'+m_code + '*.nc'))
        
        if len(mfiles)>0:
            print(f'-- Folder contains {len(mfiles)} file(s)!')
            
            list_sig = []
            
            for fname in mfiles: 
            
                raw_polly = xr.open_dataset(fname)

                # Mask normal measurements from routine calibration measurements (True:norm / False:clb)
                # Mask measurements (normal, +45, -45) according to cal_angle (True:norm or +45 or -45 / False:other)                
                mask_nrm = (raw_polly.depol_cal_angle.values == cal_angle)
                # xarray with dims [time, bins, channel]
                raw_signal = raw_polly.raw_signal[mask_nrm,:,:].values.astype(float)
                
                # convert the time to npdatetime format and mask them
                meas_time = meas_time_to_npdatetime(raw_polly.measurement_time)                
                meas_time= np.array(meas_time)[mask_nrm]

                # Convert the signal from counts to MHz                
                # rep = raw_polly.laser_rep_rate.values
                # shots = raw_polly.measurement_shots[mask_nrm,:].values.astype(float)

                # for k in range(raw_signal.shape[0]):
                    # for j in range(raw_signal.shape[2]):
                        # raw_signal[k,:,j] = raw_signal[k,:,j]*rep/shots[k,j]

                # Define temporal xarray
                arr = xr.DataArray(data = raw_signal, 
                                   dims=['time','height','channel'],
                                   coords=[meas_time, raw_polly.height.values, raw_polly.channel.values],
                                   name='signals')
                # append the xarray to a list
                list_sig.append(arr)
            
            # Append in the time dimension all the time frames
            sig_raw = xr.concat(list_sig, dim='time')
            
            # Transpose the dims in [time, channel, bins]            
            sig_raw = sig_raw.transpose('time','channel','height')
            
            # channels IDs
            raw_channels = ['355_total','355_cross','387','407','532_total','532_cross',
                            '607','1064','532_NR','607_NR','355_NR','387_NR']
            
            channels = raw_to_config(raw_channels, cfg.ch_list)
            sig_raw = signal.change_dim(sig_raw.copy(), 'channel', 'channel', channels)

            # Bins
            bins = raw_polly.raw_signal.height.values + 1            
            sig_raw = signal.change_dim(sig_raw.copy(), 'height', 'bins', bins)            

            
            # Create the info dataframe from the last file            
            # Setting info Dataframe            
            info = pd.DataFrame(index = channels,
                                columns = ['ch_mode', 'bins', 'laser_pol', 'resol',
                                           'shots', 'ADC_range', 'ADC_bit'], 
                                dtype = object)
            
            info.loc[:, 'laser_pol'] =  1
            info.loc[:, 'ch_mode'] = 1.
            info.loc[:, 'shots'] = raw_polly.measurement_shots.values[-1,:] 
            info.loc[:, 'bins'] = bins[-1]
            info.loc[:, 'wave'] = raw_polly.if_center.values
            info.loc[:, 'resol'] = 7.5
            info.loc[:, 'ch_pol'] = np.array(['o', 's', 'o', 'o', 'o', 's', 'o', 'o', 'o', 'o', 'o','o'])
            info.loc[:, 'ADC_range'] = 0.
            info.loc[:, 'sampl_rate'] =  raw_polly.laser_rep_rate.values
            
            # Sort by time
            sig_raw = sig_raw.sortby('time')
            
            # Analog units conversion from bits to mV for analog 
            # and summed counts to MHz for photon
            sig_raw = signal.unit_conv(sig_raw, info)
                
            # Sort by channel
            #sig_raw = sig_raw.sortby('channel')
            #info = info.sort_index()
            
            SZA = raw_polly.zenithangle.values
            ground_alt = raw_polly.location_height.values
            azimuth = 0.

    return(sig_raw, sig_raw_dev, info, info_dev, ground_alt, SZA, azimuth)

def meas_time_to_npdatetime(meas_time):
    # meas_time: 2d array : [times, 2], 2: [yyyymmdd, second of day]
    t_dims = np.shape(meas_time)
    npdatetime = []
    
    for i in range(t_dims[0]): 
        temp_str = str(meas_time.values[i][0])
        hr = np.divide(meas_time.values[i][1],(60*60)); minute = (hr - np.fix(hr))*60; sec = (minute - np.fix(minute))*60
        date = temp_str[0:4]+'-'+temp_str[4:6]+'-'+temp_str[6:8]+'T'+"%02d" %np.fix(hr)+':'+"%02d" %np.fix(minute)+':'+"%02d" %np.fix(sec)
        npdatetime.append(np.datetime64(date))
    
    return(npdatetime)

