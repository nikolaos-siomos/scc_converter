#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Aug  4 23:30:39 2022

@author: nick
"""

from readers.read_config import config
import os
from readers import read_signals
from tools import modify, make

def rayleigh(args):
   
    path = os.path.join(args['parent_folder'],'rayleigh')
    path_d = os.path.join(args['parent_folder'],'rayleigh','dark')
    file_format = args['file_format']
    mcode = args['measurement_identifier']
    
    # Reading of the configuration file    
    cfg = config(path = args['config_file'])   
    licel_id_config = cfg.channels.licel_id.values

    # Read the files in the dark folder
    sig_raw_d, shots_d, lidar_info_d, channel_info_d  = \
        read_signals.dark(finput = path_d, file_format = file_format, mcode = mcode)

    # Read the files in the rayleigh folder
    sig_raw, shots, lidar_info, channel_info = \
        read_signals.rayleigh(path, file_format = file_format, mcode = mcode)

    # Remove channels that should be excluded according to the configuration file
    sig_raw_d, shots_d, channel_info_d = \
        modify.trim_channels(licel_id_config = licel_id_config, sig = sig_raw_d, shots = shots_d, channel_info = channel_info_d)
    
    sig_raw, shots, channel_info = \
        modify.trim_channels(licel_id_config = licel_id_config, sig = sig_raw, shots = shots, channel_info = channel_info)
        
    # Add the information from the raw files headers to the configuration object
    cfg = modify.merge_config(cfg = cfg, lidar_info = lidar_info, channel_info = channel_info)

    cfg = modify.merge_config(cfg = cfg, lidar_info = lidar_info_d, channel_info = channel_info_d)

    # Add dafault values to the configuration object when the respective variables are not provided in the configuration file
    cfg = modify.fill_defaults(cfg)

    # Convert analog channel units to mV (applicable mainly to licel)   
    sig_raw = modify.unit_conv_bits_to_mV(channel_info, signal = sig_raw.copy(), shots = shots)

    sig_raw_d = modify.unit_conv_bits_to_mV(channel_info_d, signal = sig_raw_d.copy(), shots = shots_d)
    
    # Creating the measurement ID
    meas_ID = make.meas_id(lr_id = cfg.lidar['lidar_id'], sig = sig_raw)
    
    # Creating the paths and folders
    nc_path = make.path(results_folder = args['results_folder'], meas_ID = meas_ID, meas_type = 'ray')
    
    # Making the raw SCC file
    make.rayleigh_file(lidar_info = cfg.lidar.copy(), 
                       channel_info = cfg.channels.copy(), 
                       nc_path = nc_path, meas_ID = meas_ID, 
                       molecular_calc = args['molecular_calc'], 
                       P = args['ground_pressure'], 
                       T = args['ground_temperature'], 
                       rsonde = args['radiosonde_filename'], 
                       sig = sig_raw, sig_d = sig_raw_d, shots = shots)
    
    print('Succesfully generated a rayleigh QA file!')
    
    return()

def telecover(args):
    
    path = os.path.join(args['parent_folder'],'telecover')
    path_d = os.path.join(args['parent_folder'],'telecover','dark')
    file_format = args['file_format']
    mcode = args['measurement_identifier']
    files_per_sector = args['files_per_sector']
    
    # Reading of the configuration file    
    cfg = config(path = args['config_file'])   
    licel_id_config = cfg.channels.licel_id.values

    # Read the files in the dark folder
    sig_raw_d, shots_d, lidar_info_d, channel_info_d  = \
        read_signals.dark(finput = path_d, file_format = file_format, mcode = mcode)
    
    # Read the files in the telecover folder
    sig_raw, shots, lidar_info, channel_info, sector = \
        read_signals.telecover(finput = path, file_format = file_format, mcode = mcode, files_per_sector = files_per_sector)

    # Remove channels that should be excluded according to the configuration file
    sig_raw_d, shots_d, channel_info_d = \
        modify.trim_channels(licel_id_config = licel_id_config, sig = sig_raw_d, shots = shots_d, channel_info = channel_info_d)
    
    sig_raw, shots, channel_info = \
        modify.trim_channels(licel_id_config = licel_id_config, sig = sig_raw, shots = shots, channel_info = channel_info)
        
    # Add the information from the raw files headers to the configuration object
    cfg = modify.merge_config(cfg = cfg, lidar_info = lidar_info, channel_info = channel_info)

    cfg = modify.merge_config(cfg = cfg, lidar_info = lidar_info_d, channel_info = channel_info_d)

    # Add dafault values to the configuration object when the respective variables are not provided in the configuration file
    cfg = modify.fill_defaults(cfg)

    # Convert analog channel units to mV (applicable mainly to licel)   
    sig_raw = modify.unit_conv_bits_to_mV(channel_info, signal = sig_raw.copy(), shots = shots)

    sig_raw_d = modify.unit_conv_bits_to_mV(channel_info_d, signal = sig_raw_d.copy(), shots = shots_d)
    
    # Creating the measurement ID
    meas_ID = make.meas_id(lr_id = cfg.lidar['lidar_id'], sig = sig_raw)
    
    # Creating the paths and folders
    nc_path = make.path(results_folder = args['results_folder'], meas_ID = meas_ID, meas_type = 'ray')
    
    # Making the raw SCC file
    make.telecover_file(cfg = cfg, nc_path = nc_path, meas_ID = meas_ID, 
                        sig = sig_raw, sig_d = sig_raw_d, shots = shots, 
                        sector = sector)
        # Making the raw SCC file
    make.rayleigh_file(lidar_info = cfg.lidar.copy(), 
                       channel_info = cfg.channels.copy(), 
                       nc_path = nc_path, meas_ID = meas_ID, 
                       sig = sig_raw, sig_d = sig_raw_d, shots = shots,
                       sector = sector)
    
    print('Succesfully generated a telecover QA file!')
    
    return()

def calibration(args):
    
    return()
