#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Aug  4 23:30:39 2022

@author: nick
"""

from readers.read_config import config
import os, sys
from readers import read_files
from tools import modify, make
from tools.automate import check_rayleigh, check_telecover, check_calibration

def rayleigh(args):
   
    path = os.path.join(args['parent_folder'],'rayleigh')
    path_d = os.path.join(args['parent_folder'],'rayleigh','dark')
    file_format = args['file_format']
    mcode = args['measurement_identifier']
    
    # Checking the rayleigh folder    
    check_rayleigh(path)

    # Reading of the configuration file    
    cfg = config(path = args['config_file']) 

    licel_id_config = cfg.channels.licel_id.values

    # Read the files in the dark folder
    sig_raw_d, shots_d, meas_info_d, channel_info_d, time_info_d  = \
        read_files.dark(finput = path_d, file_format = file_format, mcode = mcode)

    # Read the files in the rayleigh folder
    sig_raw, shots, meas_info, channel_info, time_info = \
        read_files.rayleigh(path, file_format = file_format, mcode = mcode)

    # Remove channels that should be excluded according to the configuration file
    sig_raw_d, shots_d, channel_info_d = \
        modify.trim_channels(licel_id_config = licel_id_config, sig = sig_raw_d, shots = shots_d, channel_info = channel_info_d)
    
    sig_raw, shots, channel_info = \
        modify.trim_channels(licel_id_config = licel_id_config, sig = sig_raw, shots = shots, channel_info = channel_info)

    # Creating the measurement ID
    meas_ID = make.meas_id(lr_id = cfg.lidar['lidar_id'], time = sig_raw.time)
            
    # Creating debugging files from the licel input
    if args['debug']:
        make.debug_file(path = args['results_folder'], data = meas_info, meas_type = 'ray', label = 'meas_info', meas_ID = meas_ID, show_index = True, header = False)
        make.debug_file(path = args['results_folder'], data = channel_info, meas_type = 'ray', label = 'channel_info', meas_ID = meas_ID)

    # Add the information from the raw file headers to the configuration object
    cfg = modify.merge_config(cfg = cfg, meas_info = meas_info, channel_info = channel_info)

    cfg = modify.merge_config(cfg = cfg, meas_info = meas_info_d, channel_info = channel_info_d)

    # Add default values to the configuration object when the respective variables are not provided in the configuration file
    cfg = modify.fill_defaults(cfg)

    # Creating debugging files from the configuration and licel input
    if args['debug']:
        make.debug_file(path = args['results_folder'], data = cfg.lidar, meas_type = 'ray', label = 'config_lidar', meas_ID = meas_ID, show_index = True, header = False)
        make.debug_file(path = args['results_folder'], data = cfg.channels, meas_type = 'ray', label = 'config_channels', meas_ID = meas_ID)
        make.debug_file(path = args['results_folder'], data = time_info, meas_type = 'ray', label = 'time_info', meas_ID = meas_ID)
        make.debug_file(path = args['results_folder'], data = time_info_d, meas_type = 'ray', label = 'time_info_d', meas_ID = meas_ID)

    # Convert analog channel units to mV (applicable mainly to licel)   
    sig_raw = modify.unit_conv_bits_to_mV(channel_info, signal = sig_raw.copy(), shots = shots)

    sig_raw_d = modify.unit_conv_bits_to_mV(channel_info_d, signal = sig_raw_d.copy(), shots = shots_d)
    
    # Creating the paths and folders
    nc_path = make.path(results_folder = args['results_folder'], meas_ID = meas_ID, meas_type = 'ray')
    
    # Making the raw SCC file
    make.rayleigh_file(meas_info = cfg.lidar.copy(), 
                       channel_info = cfg.channels.copy(), 
                       time_info = time_info, time_info_d = time_info_d,
                       nc_path = nc_path, meas_ID = meas_ID,  
                       P = args['ground_pressure'], 
                       T = args['ground_temperature'], 
                       rsonde = args['radiosonde_filename'], 
                       sig = sig_raw, sig_d = sig_raw_d,
                       shots = shots, shots_d = shots_d)
    
    print('Succesfully generated a rayleigh QA file!')
    print('')
    
    return(nc_path)

def telecover(args):
    
    path = os.path.join(args['parent_folder'],'telecover')
    path_d = os.path.join(args['parent_folder'],'telecover','dark')
    file_format = args['file_format']
    mcode = args['measurement_identifier']
    files_per_sector = args['files_per_sector']

    # Checking the telecover folder    
    check_telecover(path, files_per_sector = files_per_sector)
    
    # Reading of the configuration file    
    cfg = config(path = args['config_file'])   
    licel_id_config = cfg.channels.licel_id.values

    # Read the files in the dark folder
    sig_raw_d, shots_d, meas_info_d, channel_info_d, time_info_d  = \
        read_files.dark(finput = path_d, file_format = file_format, mcode = mcode)
    
    # Read the files in the telecover folder
    sig_raw, shots, meas_info, channel_info, time_info = \
        read_files.telecover(finput = path, file_format = file_format, mcode = mcode, files_per_sector = files_per_sector)

    # Remove channels that should be excluded according to the configuration file
    sig_raw_d, shots_d, channel_info_d = \
        modify.trim_channels(licel_id_config = licel_id_config, sig = sig_raw_d, shots = shots_d, channel_info = channel_info_d)
    
    sig_raw, shots, channel_info = \
        modify.trim_channels(licel_id_config = licel_id_config, sig = sig_raw, shots = shots, channel_info = channel_info)
        
    # Creating the measurement ID
    meas_ID = make.meas_id(lr_id = cfg.lidar['lidar_id'], time = sig_raw.time)
            
    # Add the information from the raw files headers to the configuration object
    cfg = modify.merge_config(cfg = cfg, meas_info = meas_info, channel_info = channel_info)

    cfg = modify.merge_config(cfg = cfg, meas_info = meas_info_d, channel_info = channel_info_d)

    # Add dafault values to the configuration object when the respective variables are not provided in the configuration file
    cfg = modify.fill_defaults(cfg)

    # Creating debugging files from the configuration and licel input
    if args['debug']:
        make.debug_file(path = args['results_folder'], data = cfg.lidar, meas_type = 'tlc', label = 'config_lidar', meas_ID = meas_ID, show_index = True, header = False)
        make.debug_file(path = args['results_folder'], data = cfg.channels, meas_type = 'tlc', label = 'config_channels', meas_ID = meas_ID)
        make.debug_file(path = args['results_folder'], data = time_info, meas_type = 'tlc', label = 'time_info', meas_ID = meas_ID)
        make.debug_file(path = args['results_folder'], data = time_info_d, meas_type = 'tlc', label = 'time_info_d', meas_ID = meas_ID)

    # Convert analog channel units to mV (applicable mainly to licel)   
    sig_raw = modify.unit_conv_bits_to_mV(channel_info, signal = sig_raw.copy(), shots = shots)

    sig_raw_d = modify.unit_conv_bits_to_mV(channel_info_d, signal = sig_raw_d.copy(), shots = shots_d)
    
    # Creating the paths and folders
    nc_path = make.path(results_folder = args['results_folder'], meas_ID = meas_ID, meas_type = 'tlc')
    
    # Making the raw SCC file
    make.telecover_file(meas_info = cfg.lidar.copy(), 
                        channel_info = cfg.channels.copy(),
                        time_info = time_info, time_info_d = time_info_d,
                        nc_path = nc_path, meas_ID = meas_ID, 
                        sig = sig_raw, sig_d = sig_raw_d,
                        shots = shots, shots_d = shots_d)
    
    print('Succesfully generated a telecover QA file!')
    print('')
    
    return(nc_path)

def calibration(args):
   
    path = os.path.join(args['parent_folder'],'calibration')
    path_d = os.path.join(args['parent_folder'],'calibration','dark')
    file_format = args['file_format']
    mcode = args['measurement_identifier']
    
    # Checking the calibration folder    
    check_calibration(path)
    
    # Reading of the configuration file    
    cfg = config(path = args['config_file'])   
    licel_id_config = cfg.channels.licel_id.values        

    # Check if the rayleigh filename was provided
    if not args['rayleigh_filename']:
        sys.exit("-- Error: A polarization calibration measurement is being processed but the rayleigh filename was not provided in the arguments! Please prepare the rayleigh file fist and included it with: -l <rayleigh_filename>'")
        
    # Read the files in the dark folder
    sig_raw_d, shots_d, meas_info_d, channel_info_d, time_info_d  = \
        read_files.dark(finput = path_d, file_format = file_format, mcode = mcode)

    # Read the files in the calibration folder
    sig_raw, shots, meas_info, channel_info, time_info = \
        read_files.calibration(path, file_format = file_format, mcode = mcode)

    # Remove channels that should be excluded according to the configuration file
    sig_raw_d, shots_d, channel_info_d = \
        modify.trim_channels(licel_id_config = licel_id_config, sig = sig_raw_d, shots = shots_d, channel_info = channel_info_d)
    
    sig_raw, shots, channel_info = \
        modify.trim_channels(licel_id_config = licel_id_config, sig = sig_raw, shots = shots, channel_info = channel_info)

    # Creating the measurement ID
    meas_ID = make.meas_id(lr_id = cfg.lidar['lidar_id'], time = sig_raw.time)
            
    # Add the information from the raw files headers to the configuration object
    cfg = modify.merge_config(cfg = cfg, meas_info = meas_info, channel_info = channel_info)

    cfg = modify.merge_config(cfg = cfg, meas_info = meas_info_d, channel_info = channel_info_d)

    # Add dafault values to the configuration object when the respective variables are not provided in the configuration file
    cfg = modify.fill_defaults(cfg)

    # Creating debugging files from the configuration and licel input
    if args['debug']:
        make.debug_file(path = args['results_folder'], data = cfg.lidar, meas_type = 'pcl', label = 'config_lidar', meas_ID = meas_ID, show_index = True, header = False)
        make.debug_file(path = args['results_folder'], data = cfg.channels, meas_type = 'pcl', label = 'config_channels', meas_ID = meas_ID)
        make.debug_file(path = args['results_folder'], data = time_info, meas_type = 'pcl', label = 'time_info', meas_ID = meas_ID)
        make.debug_file(path = args['results_folder'], data = time_info_d, meas_type = 'pcl', label = 'time_info_d', meas_ID = meas_ID)

    # Convert analog channel units to mV (applicable mainly to licel)   
    sig_raw = modify.unit_conv_bits_to_mV(channel_info, signal = sig_raw.copy(), shots = shots)

    sig_raw_d = modify.unit_conv_bits_to_mV(channel_info_d, signal = sig_raw_d.copy(), shots = shots_d)
    
    # Creating the paths and folders
    nc_path = make.path(results_folder = args['results_folder'], meas_ID = meas_ID, meas_type = 'pcl')
    
    # Making the raw SCC file
    make.calibration_file(meas_info = cfg.lidar.copy(), 
                          channel_info = cfg.channels.copy(), 
                          time_info = time_info, time_info_d = time_info_d,
                          nc_path = nc_path, meas_ID = meas_ID, 
                          P = args['ground_pressure'], 
                          T = args['ground_temperature'], 
                          rsonde = args['radiosonde_filename'],
                          rayleigh = args['rayleigh_filename'],  
                          sig = sig_raw, sig_d = sig_raw_d,
                          shots = shots, shots_d = shots_d)
    
    print('Succesfully generated a calibration QA file!')
    print('')
    
    return(nc_path)

def dark(args):
   
    path_d = os.path.join(args['parent_folder'],'dark')
    file_format = args['file_format']
    mcode = args['measurement_identifier']
    
    # Reading of the configuration file    
    cfg = config(path = args['config_file'])   
    licel_id_config = cfg.channels.licel_id.values

    # Read the files in the dark folder
    sig_raw_d, shots_d, meas_info_d, channel_info_d, time_info_d  = \
        read_files.dark(finput = path_d, file_format = file_format, mcode = mcode)

    # Remove channels that should be excluded according to the configuration file
    sig_raw_d, shots_d, channel_info_d = \
        modify.trim_channels(licel_id_config = licel_id_config, sig = sig_raw_d, shots = shots_d, channel_info = channel_info_d)
    
    # Creating the measurement ID
    meas_ID = make.meas_id(lr_id = cfg.lidar['lidar_id'], time = sig_raw_d.time)
            
    # Add the information from the raw files headers to the configuration object
    cfg = modify.merge_config(cfg = cfg, meas_info = meas_info_d, channel_info = channel_info_d)

    # Add dafault values to the configuration object when the respective variables are not provided in the configuration file
    cfg = modify.fill_defaults(cfg)

    # Creating debugging files from the configuration and licel input
    if args['debug']:
        make.debug_file(path = args['results_folder'], data = cfg.lidar, meas_type = 'drk', label = 'config_lidar', meas_ID = meas_ID, show_index = True, header = False)
        make.debug_file(path = args['results_folder'], data = cfg.channels, meas_type = 'drk', label = 'config_channels', meas_ID = meas_ID)
        make.debug_file(path = args['results_folder'], data = time_info_d, meas_type = 'drk', label = 'time_info', meas_ID = meas_ID)

    # Convert analog channel units to mV (applicable mainly to licel)   
    sig_raw_d = modify.unit_conv_bits_to_mV(channel_info_d, signal = sig_raw_d.copy(), shots = shots_d)
    
    # Creating the measurement ID
    meas_ID = make.meas_id(lr_id = cfg.lidar['lidar_id'], time = sig_raw_d.time)
    
    # Creating the paths and folders
    nc_path = make.path(results_folder = args['results_folder'], meas_ID = meas_ID, meas_type = 'drk')
    
    # Making the raw SCC file
    make.dark_file(meas_info = cfg.lidar.copy(), 
                   channel_info = cfg.channels.copy(),
                   time_info_d = time_info_d,
                   nc_path = nc_path, meas_ID = meas_ID, 
                   sig_d = sig_raw_d, shots_d = shots_d)
    
    print('Succesfully generated a dark QA file!')
    print('')
    
    return(nc_path)

def radiosonde(args):
   
    path = os.path.join(args['parent_folder'],'radiosonde')
    
    delimiter = args['rsonde_delimiter']
    skip_header = args['rsonde_skip_header']
    skip_footer = args['rsonde_skip_footer']
    usecols = args['rsonde_column_index']
    geodata = args['rsonde_geodata']
    
    date, time, atmo = read_files.radiosonde(path, delimiter = delimiter, 
                                             skip_header = skip_header, 
                                             skip_footer = skip_footer, 
                                             usecols = usecols)
    # Reading of the configuration file    
    cfg = config(path = args['config_file'])
    
    # Reading radiosonde geodata with the lidar station values if a geodata argument is not provided  
    if any([not geodata_i for geodata_i in geodata]):
        sys.exit("-- Error: The rsonde_geodata field is mandatory when processing a radiosonde file (mode = A and the radiosonde folder exists). Please provide 3 floats that correspond to the radiosonde station latitude, longitude, and altitude eg: --rsonde_geodata 40.5 22.9 60.0")

    # Creating the radiosonde ID
    rsonde_ID = f"{date}{cfg.lidar['lidar_id']}{time[:4]}"
    
    # Creating the paths and folders
    nc_path = make.path(results_folder = args['results_folder'], meas_ID = rsonde_ID, meas_type = 'rs')
    
    # Making the raw SCC file
    make.radiosonde_file(nc_path = nc_path, date = date, time = time, geodata = geodata, atmo = atmo)
    
    print('Succesfully generated a radiosonde file!')
    print('')
    
    return(nc_path)