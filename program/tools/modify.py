#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jul 26 15:22:31 2022

@author: nick
"""

import numpy as np
import sys

def trim_channels(licel_id_config, sig, shots, channel_info):
    
    """Channels are selected based on the licel_id variable in the configuration
    file. All IDs in the config_file must be corresponendt to the Licel IDs in
    the raw files. If an unkown ID is included in the config_file then an error
    is raised"""
    
    licel_id_files = channel_info.licel_id.values
    
    if any(licel_id_config_i not in licel_id_files for licel_id_config_i in licel_id_config):
        sys.exit("--Error: The some of the licel IDs defined in the configuration file do not match with the licel IDs from the licel header. Please revise the configuration file! ")

    
    if licel_id_config.size > licel_id_files.size:
        sys.exit("--Error: The number of licel IDs provided in the configuration file exceed the number of IDs provided in the licel header. Please revise the configuration file! ")
    
    licel_id_com = np.intersect1d(licel_id_config, licel_id_files)
    
    mask_com = [licel_id_config_i in licel_id_files for licel_id_config_i in licel_id_config]
    
    licel_id_com = licel_id_config[mask_com]
    
    index_com = np.array(range(licel_id_config.size))[mask_com]

    sig = sig.loc[dict(channel = licel_id_com)]
    shots = shots.loc[dict(channel = licel_id_com)]
    channel_info = channel_info.iloc[index_com,:]
        
    return(sig, shots, channel_info)

def merge_config(cfg, meas_info, channel_info):

    for key in meas_info.index:
        if key not in cfg.lidar.index:
            cfg.lidar.loc[key] = meas_info.loc[key]    
    
    for key in channel_info.columns:
        if key not in cfg.channels.columns:
            cfg.channels.loc[:,key] = channel_info.loc[:,key].values    
    
    return(cfg)
    
def fill_defaults(cfg):
    
    if 'channel_bandwidth' not in cfg.channels:
        cfg.channels.loc[:,'channel_bandwidth'] = 1.  
    
    if 'zenith_angle' not in cfg.lidar:
        cfg.lidar['zenith_angle'] = 0.  
        
    if 'azimuth_angle' not in cfg.lidar:
        cfg.lidar['azimuth_angle'] = 0.  
        
    cfg.channels.loc[:,'laser_repetition_rate'] = cfg.lidar['laser_A_repetition_rate']
    if (cfg.channels.loc[:,'laser'] == 2).any():
        cfg.channels.loc[:,'laser_repetition_rate'][cfg.channels.loc[:,'laser'] == 2] = cfg.lidar['laser_B_repetition_rate']
    if (cfg.channels.loc[:,'laser'] == 3).any():
        cfg.channels.loc[:,'laser_repetition_rate'][cfg.channels.loc[:,'laser'] == 3] = cfg.lidar['laser_C_repetition_rate']
        
    acquisition_type = np.empty(cfg.channels.acquisition_mode.size,dtype=object)
    acquisition_type[cfg.channels.acquisition_mode.values == 0] = 'a'
    acquisition_type[cfg.channels.acquisition_mode.values == 1] = 'p' 
  
    cfg.channels.loc[:,'acquisition_type'] = acquisition_type    
        
    return(cfg)

def unit_conv_bits_to_mV(channel_info, signal, shots):

    """Converts analog signals from bits to mV"""
    
    if len(signal) > 0:
        
        mask_an = channel_info.acquisition_mode.values == 0
        
        licel_id_an = channel_info.licel_id[mask_an].values
        data_acquisition_range = channel_info.data_acquisition_range[mask_an].values
        analog_to_digital_resolution = channel_info.analog_to_digital_resolution[mask_an].values
        
        for i in range(licel_id_an.size):
            ch = dict(channel = licel_id_an[i])
            # analog conversion (to mV)
            signal.loc[ch] = signal.loc[ch]*data_acquisition_range[i]/(shots.loc[ch]*(np.power(2,analog_to_digital_resolution[i])-1.))
    
    return(signal) 