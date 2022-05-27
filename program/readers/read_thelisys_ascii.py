
"""
@authors: Siomos and Paschou

================
Input:
    arg 1: full filename from current running directory, should be a string scalar

Returns:
    arg 1: list that contains [start date, start time, end date, end time] of the measurement
    arg 2: info from header per channel (bins, resolution, shots, ADC_range, ADC_bit, wavelength)
    arg 3: a list of arrays that conatains the raw summed signal profiles
"""
import os
import numpy as np
import pandas as pd
import glob
from datetime import datetime as dt
import xarray as xr


def dtfs(dir_meas, cfg):
    
    # Get raw lidar files code from the ini file
    m_code = cfg.lidar.m_code

    # Setting station metadata       
    ground_alt = 60.        
    SZA = 0.
    azimuth = 0.
    sig_raw, sig_dev, info, info_dev = [], [], [], []  

    # Reading Depol and Raman files
    sig_raw_dp, info_dp = dtfs_depol(os.path.join(dir_meas, 'depol'), m_code)
    sig_raw_ra, info_ra = dtfs_raman(os.path.join(dir_meas, 'raman'), m_code)
    
    # Merging the xarrays    
    if len(sig_raw_dp) == 0 and len(sig_raw_ra) > 0:
        sig_raw = sig_raw_ra
        info = info_ra
    
    if len(sig_raw_dp) > 0 and len(sig_raw_ra) == 0:
        sig_raw = sig_raw_dp
        info = info_dp
    
    if len(sig_raw_dp) > 0 and len(sig_raw_ra) > 0:
        sig_raw = xr.merge([sig_raw_dp, sig_raw_ra], join = 'outer').to_array()[0,:,:,:]
        info = info_dp.reset_index().merge(info_ra.reset_index(), how="outer").set_index('index')

    #Sort the final sig_raw and info and replace (or not) the channels ID    
    if len(sig_raw)>0 and len(info)>0:
        
        #Sorting
        sig_raw = sig_raw.sortby('time')    
        sig_raw = sig_raw.sortby('channel')
        info = info.sort_index()
    
        # Link channel ID from config file to the THELISYS IDs
        # Replace with the new index, if exists, the info (dataframe) and sig_raw (xarray)
        info.index = raw_to_config(info.index, cfg.ch_list)    
        sig_raw = signal.change_dim(sig_raw, 'channel', 'channel', info.index.values)
                
    return(sig_raw, sig_dev, info, info_dev, ground_alt, SZA, azimuth)

# Read measurement
def dtfs_depol(dir_meas, m_code):
    
    # Setting sig, info, and time as empty lists in the beggining    
    list_sig, list_info, list_time = [], [], []
    sig_raw = []     
    info = []
    
    # The output data xarray contains the pre-trigger region without any correction
    if not(os.path.exists(dir_meas)):
        print('---- Error : The folder for reading Depol signals does not exist! \r\n' +\
              f'---- Check the input directory! \r\n Given folder: {dir_meas}')
        # sys.exit(0)
    
    else:
        
        mfiles = glob.glob(os.path.join(dir_meas, m_code + '*'))

        # for existing directory and files inside it, starts the reading of files         
        if len(mfiles) > 0:
            print(f'-- Depol folder contains {len(mfiles)} file(s)!')
            for fname in mfiles: 
                temp_list_sig = []
                temp_list_info = []
                
                # Reading the raw thelisys files
                with open(fname, 'r') as f:
                    content = f.read()
                header = (content.split('#', 1)[0]).split('\n', 2)
                lines = header[2].split('\n')[:-1]

                for temp_info in lines:
                    temp_list_info.append(temp_info.split())

                date = header[1][0:6]
                time = header[1][7:13]
                body = content.replace('\n','').split('#')[1:-1]
    
                for sig in body:
                    temp_list_sig.append(sig.split('\t'))
                
                stime = dt.strptime(date + ' ' + time, "%d%m%y %H%M%S")
                list_time.append(stime)
                list_sig.append(temp_list_sig)
                list_info.append(temp_list_info)

    # Setting the raw channels ID for depol measurements
            channels = ['EL1_AN','EL1_PC','EL2_AN','EL2_PC','DP1_PC','EL3_AN','DP2_PC']
    # Setting info xarray            
            info = pd.DataFrame(index = channels,
                                columns = ['ch_mode', 'bins', 'laser_pol', 'resol',
                                           'shots', 'ADC_range', 'ADC_bit'], 
                                dtype = object)
            info.loc[:, 'laser_pol'] =  1
            info.loc[:, 'ch_mode'] = (np.array(list_info)[0, :, 1]).astype(float)
            info.loc[:, 'bins'] = (np.array(list_info)[0, :, 2]).astype(int)
            info.loc[:, 'wave'] = np.array([355., 355., 532., 532., 532., 1064., 532.])
            info.loc[:, 'resol'] = 1000.*np.array(list_info)[0, :, 4].astype(float)
            info.loc[:, 'ch_pol'] = np.array(['o', 'o', 'o', 'o', 'p', 'o', 's'])
            info.loc[:, 'ADC_range'] = 1000.*info.loc[:, 'ADC_range']
            info.loc[:, 'sampl_rate'] =  150./info.resol.values
            info.loc[:, 'shots'] = np.array(list_info)[0, :, 5].astype(int)
            
    
    # Setting sig_raw xarray                    
            temp_sig = np.array(list_sig).astype(float)
            bins_sig = 1. + np.arange(0, temp_sig.shape[-1])
            sig_raw = xr.DataArray(temp_sig, 
                                   coords=[list_time, info.index, bins_sig], 
                                   dims=['time', 'channel', 'bins'],
                                   name='signals') 
            sig_raw = sig_raw[:, :, :-2] #drop last 2 bins because a recorder bug causes a spik in the endo of the signals
            info.loc[:, 'bins'] = info.loc[:, 'bins'].values - 2
            
        else:
            print('---- Warning! Depol folder empty \n'+\
                  f'---> !! Skip reading measurement files from folder {dir_meas}')  
     
    return(sig_raw, info)

def dtfs_raman(dir_meas, m_code):
    
    # Setting sig, info, and time as empty lists in the beggining    
    list_sig, list_info, list_time = [], [], []
    sig_raw = []     
    info = []
    
    # The output data xarray contains the pre-trigger region without any correction
    if not(os.path.exists(dir_meas)):
        print('---- Error : The folder for reading Raman signals does not exist! \r\n' +\
              f'---- Check the input directory! \r\n Given folder: {dir_meas}')
        # sys.exit(0)
    
    else:    
        mfiles = glob.glob(os.path.join(dir_meas, m_code + '*'))
    
    # Setting sig, info, and time lists
        list_sig = []
        list_info = []
        list_time = []
    
        if len(mfiles) > 0:
            print(f'-- Raman folder contains {len(mfiles)} file(s)!')
            for fname in mfiles: 
                temp_list_sig = []
                temp_list_info = []
                # Reading the raw thelisys files
                with open(fname, 'r') as f:
                    content = f.read()
                header = (content.split('#', 1)[0]).split('\n', 2)
                lines = header[2].split('\n')[:-1]
                for temp_info in lines:
                    temp_list_info.append(temp_info.split())
                date = header[1][0:6]
                time = header[1][7:13]
                body = content.replace('\n','').split('#')[1:-1]
                for sig in body:
                    temp_list_sig.append(sig.split('\t'))
                
    
                stime = dt.strptime(date + ' ' + time, "%d%m%y %H%M%S")
                list_time.append(stime)
                list_sig.append(temp_list_sig)
                list_info.append(temp_list_info)
    
    # Setting the raw channels ID for raman measurements
                channels = ['EL1_AN','EL1_PC','EL2_AN','EL2_PC','RA1_PC','EL3_AN','RA2_PC']
    
    # Setting info Dataframe            
            info = pd.DataFrame(index = channels,
                                columns = ['ch_mode', 'bins', 'laser_pol', 'resol',
                                           'shots', 'ADC_range', 'ADC_bit'], 
                                dtype = object)
            
            info.loc[:, 'laser_pol'] =  1
            info.loc[:, 'ch_mode'] = (np.array(list_info)[0, :, 1]).astype(float)
            info.loc[:, 'bins'] = (np.array(list_info)[0, :, 2]).astype(int)
            info.loc[:, 'wave'] = np.array([355., 355., 532., 532., 387., 1064., 607.])
            info.loc[:, 'resol'] = 1000.*np.array(list_info)[0, :, 4].astype(float)
            info.loc[:, 'ch_pol'] = np.array(['o', 'o', 'o', 'o', 'o', 'o', 'o'])
            info.loc[:, 'ADC_range'] = 1000.*info.loc[:, 'ADC_range']
            info.loc[:, 'sampl_rate'] =  150./info.resol.values
            info.loc[:, 'shots'] = np.array(list_info)[0, :, 5].astype(int)

    
    # Setting sig_raw xarray                    
            temp_sig = np.array(list_sig).astype(float)
            bins_sig = 1. + np.arange(0, temp_sig.shape[-1])
            sig_raw = xr.DataArray(temp_sig, 
                                   coords=[list_time, info.index, bins_sig], 
                                   dims=['time', 'channel', 'bins'],
                                   name='signals') 
            sig_raw = sig_raw[:, :, :-2] #drop last 2 bins because a recorder bug causes a spik in the endo of the signals
            info.loc[:, 'bins'] = info.loc[:, 'bins'].values - 2
            
        else:
            print('---- Warning! Raman folder empty \n'+\
                  f'---> !! Skip reading measurement files from folder {dir_meas}')  
     
    return(sig_raw, info)

def raw_to_config(raw_channels, config_channels):
    
    if len(config_channels)>0:
        
        if len(config_channels) != len(raw_channels):
            raise ValueError('config_file channels ID and raw channels ID '+\
                             'have not the same length! Please revise the config_file.ini!')
        
        #Replace the raw channels ID with the IDs given by the user in config_file
        raw_channels = config_channels
    
    return(raw_channels)