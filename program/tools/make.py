#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jul 26 15:32:07 2022

@author: nick
"""

import os, sys
import netCDF4 as nc
import numpy as np

def rayleigh_file(lidar_info, channel_info, nc_path, meas_ID, sig, sig_d, shots, molecular_calc = [], P = [], T = [], rsonde = []):

    """Creates the rayleigh netcdf file according to the SCC format 
    https://docs.scc.imaa.cnr.it/en/latest/file_formats/netcdf_file.html
    and exports it to nc_path"""
        
    ds = nc.Dataset(nc_path,mode='w')
    
    n_time = sig.time.size
    n_channels = sig.channel.size
    n_points = sig.bins.size

    n_nb_of_time_scales = 1
    n_scan_angles = 1
    
    channel_label = channel_info.telescope_type.values + channel_info.channel_type.values + channel_info.acquisition_type.values + channel_info.channel_subtype.values
    
    Raw_Start_Time = np.nan * np.zeros([n_time,n_nb_of_time_scales])
    Raw_Stop_Time = np.nan * np.zeros([n_time,n_nb_of_time_scales])
    
    Raw_Start_Time[:,0] = np.arange(0,n_time,1) * lidar_info.temporal_resolution.seconds
    Raw_Stop_Time[:,0] = np.arange(1,n_time+1,1) * lidar_info.temporal_resolution.seconds
    
    if not isinstance(sig_d,list):
        n_time_bck = sig_d.time.size
        Bck_Start_Time = np.nan * np.zeros([n_time,n_nb_of_time_scales])
        Bck_Stop_Time = np.nan * np.zeros([n_time,n_nb_of_time_scales])
        Bck_Start_Time[:,0] = np.arange(0,n_time,1) * lidar_info.background_temporal_resolution.seconds
        Bck_Stop_Time[:,0] = np.arange(1,n_time+1,1) * lidar_info.background_temporal_resolution.seconds
    
    ds.createDimension('time', n_time)
    ds.createDimension('channels', n_channels)
    ds.createDimension('points', n_points)
    
    ds.createDimension('nb_of_time_scales', n_nb_of_time_scales)
    ds.createDimension('scan_angles', n_scan_angles)
    
    ds.createDimension('nchar',4)
    
    ds.Measurement_ID = meas_ID
    ds.RawData_Start_Date = lidar_info.start_time.strftime('%Y%m%d');
    ds.RawData_Start_Time_UT = lidar_info.start_time.strftime('%H%M%S');
    ds.RawData_Stop_Time_UT = lidar_info.end_time.strftime('%H%M%S');

    if not isinstance(sig_d,list):
        ds.createDimension('time_bck', n_time_bck)
        ds.RawBck_Start_Date = lidar_info.background_start_time.strftime('%Y%m%d');
        ds.RawBck_Start_Time_UT = lidar_info.background_start_time.strftime('%H%M%S');
        ds.RawBck_Stop_Time_UT = lidar_info.background_end_time.strftime('%H%M%S');
    
    make_nc_var(ds, name = 'Acquisition_Mode', value = channel_info.acquisition_mode.values, dtype = 'int', dims = ('channels',))

    make_nc_var(ds, name = 'Altitude', value = lidar_info.altitude, dtype = 'float')

    make_nc_var(ds, name = 'ADC_resolution', value = channel_info.analog_to_digital_resolution.values, dtype = 'float', dims = ('channels',))
    
    make_nc_var(ds, name = 'Background_Low', value = channel_info.background_low.values, dtype = 'float', dims = ('channels',))
    
    make_nc_var(ds, name = 'Background_High', value = channel_info.background_high.values, dtype = 'float', dims = ('channels',))
    
    if not isinstance(sig_d,list):
        make_nc_var(ds, name = 'Background_Profile', value = sig_d.values, dtype = 'float', dims = ('time_bck', 'channels', 'points',))

    make_nc_var(ds, name = 'channel_ID', value = channel_info.channel_id.values, dtype = 'int', dims = ('channels',))

    make_nc_str(ds, name = 'channel_label', value = channel_label, dims = ('channels','nchar'))    
    
    make_nc_var(ds, name = 'DAQ_Range', value = channel_info.data_acquisition_range.values, dtype = 'float', dims = ('channels',))
    
    make_nc_var(ds, name = 'Dead_Time', value = channel_info.dead_time.values, dtype = 'float', dims = ('channels',))

    make_nc_var(ds, name = 'Dead_Time_Correction_Type', value = channel_info.dead_time_correction_type.values, dtype = 'int', dims = ('channels',))
    
    make_nc_var(ds, name = 'Detected_Wavlength', value = channel_info.detected_wavelength.values, dtype = 'float', dims = ('channels',))
    
    make_nc_var(ds, name = 'Emitted_Wavlength', value = channel_info.emitted_wavelength.values, dtype = 'float', dims = ('channels',))
    
    make_nc_var(ds, name = 'First_Signal_Rangebin', value = channel_info.trigger_delay_bins.values, dtype = 'int', dims = ('channels',))
    
    make_nc_var(ds, name = 'Full_Overlap_Range', value = channel_info.full_overlap_distance.values, dtype = 'int', dims = ('channels',))
    
    make_nc_var(ds, name = 'id_timescale', value = np.zeros(n_channels), dtype = 'int', dims = ('channels',))

    make_nc_var(ds, name = 'Channel_Bandwidth', value = channel_info.channel_bandwidth.values, dtype = 'int', dims = ('channels',))
    
    make_nc_var(ds, name = 'Laser_Pointing_Angle', value = lidar_info.zenith_angle*np.ones(n_scan_angles), dtype = 'float', dims = ('scan_angles',))

    make_nc_var(ds, name = 'Laser_Pointing_Azimuth_Angle', value = lidar_info.azimuth_angle*np.ones(n_scan_angles), dtype = 'float', dims = ('scan_angles',))
    
    make_nc_var(ds, name = 'Laser_Pointing_Angle_of_Profiles', value = np.zeros([n_time, n_nb_of_time_scales]), dtype = 'int', dims = ('time', 'nb_of_time_scales',))

    make_nc_var(ds, name = 'Laser_Polarization',  value = channel_info.laser_polarization.values, dtype = 'int', dims = ('channels',))

    make_nc_var(ds, name = 'Laser_Repetition_Rate', value = channel_info.laser_repetition_rate.values, dtype = 'int', dims = ('channels',))
    
    make_nc_var(ds, name = 'Laser_Shots', value = shots.values, dtype = 'int', dims = ('time', 'channels',))

    make_nc_var(ds, name = 'Latitude', value = lidar_info.latitude, dtype = 'float')

    make_nc_var(ds, name = 'Longitude', value = lidar_info.longitude, dtype = 'float')

    make_nc_var(ds, name = 'PMT_High_Voltage', value = channel_info.pmt_high_voltage.values, dtype = 'float', dims = ('channels',))
    
    make_nc_var(ds, name = 'Raw_Lidar_Data', value = sig.values, dtype = 'float', dims = ('time', 'channels', 'points',))
    
    make_nc_var(ds, name = 'Raw_Data_Range_Resolution', value = channel_info.range_resolution.values, dtype = 'float', dims = ('channels',))
    
    make_nc_var(ds, name = 'Raw_Data_Start_Time', value = Raw_Start_Time, dtype = 'int', dims = ('time', 'nb_of_time_scales',))
    
    make_nc_var(ds, name = 'Raw_Data_Stop_Time', value = Raw_Stop_Time, dtype = 'int', dims = ('time', 'nb_of_time_scales',))
    
    if not isinstance(sig_d,list):
        make_nc_var(ds, name = 'Bck_Data_Start_Time', value = Bck_Start_Time, dtype = 'int', dims = ('time', 'nb_of_time_scales',))
    
        make_nc_var(ds, name = 'Bck_Data_Stop_Time', value = Bck_Stop_Time, dtype = 'int', dims = ('time', 'nb_of_time_scales',))
    
    if isinstance(molecular_calc, list) == False:
    
        make_nc_var(ds, name = 'Molecular_Calc', value = molecular_calc, dtype = 'int')
    
        if molecular_calc == 4:
            
            if isinstance(P,list):
                sys.exit('-- Error: The ground pressure must be provided in the make.file routine when molecular_calc = 4 (USSTD selected)')
       
            if isinstance(T,list):
                sys.exit('-- Error: The ground temperature must be provided in the make.file routine when molecular_calc = 4 (USSTD selected)')
       
            make_nc_var(ds, name = 'Pressure_at_Lidar_Station', value = P, dtype = 'float')
            
            make_nc_var(ds, name = 'Temperature_at_Lidar_Station', value = T, dtype = 'float')
            
        if molecular_calc == 1:
            
            if isinstance(rsonde,list):
                sys.exit('-- Error: The radiosonde filenmame must be provided in the make.file routine when molecular_calc = 1 (Radiosonde selected)')
       
            ds.Sounding_File_Name = rsonde;
    
    ds.close()
    
    return()

def telecover_file(lidar_info, channel_info, nc_path, meas_ID, sig, sig_d, shots, sector):

    """Creates the telecover netcdf file according to the SCC format 
    https://docs.scc.imaa.cnr.it/en/latest/file_formats/netcdf_file.html
    and exports it to nc_path"""
        
    ds = nc.Dataset(nc_path,mode='w')
    
    n_time = sig.time.size
    n_channels = sig.channel.size
    n_points = sig.bins.size
    
    n_nb_of_time_scales = 1
    n_scan_angles = 1
    
    channel_label = channel_info.telescope_type.values + channel_info.channel_type.values + channel_info.acquisition_type.values + channel_info.channel_subtype.values

    Raw_Start_Time = np.nan * np.zeros([n_time,n_nb_of_time_scales])
    Raw_Stop_Time = np.nan * np.zeros([n_time,n_nb_of_time_scales])
    
    Raw_Start_Time[:,0] = np.arange(0,n_time,1) * lidar_info.temporal_resolution.seconds
    Raw_Stop_Time[:,0] = np.arange(1,n_time+1,1) * lidar_info.temporal_resolution.seconds
    
    if not isinstance(sig_d,list):
        n_time_bck =sig_d.time.size
        Bck_Start_Time = np.nan * np.zeros([n_time,n_nb_of_time_scales])
        Bck_Stop_Time = np.nan * np.zeros([n_time,n_nb_of_time_scales])
        Bck_Start_Time[:,0] = np.arange(0,n_time,1) * lidar_info.background_temporal_resolution.seconds
        Bck_Stop_Time[:,0] = np.arange(1,n_time+1,1) * lidar_info.background_temporal_resolution.seconds
    
    ds.createDimension('time', n_time)
    ds.createDimension('channels', n_channels)
    ds.createDimension('points', n_points)
    
    ds.createDimension('nb_of_time_scales', n_nb_of_time_scales)
    ds.createDimension('scan_angles', n_scan_angles)

    ds.createDimension('nchar',4)
    
    ds.Measurement_ID = meas_ID
    ds.RawData_Start_Date = lidar_info.start_time.strftime('%Y%m%d');
    ds.RawData_Start_Time_UT = lidar_info.start_time.strftime('%H%M%S');
    ds.RawData_Stop_Time_UT = lidar_info.end_time.strftime('%H%M%S');

    if not isinstance(sig_d,list):
        ds.createDimension('time_bck', n_time_bck)
        ds.RawBck_Start_Date = lidar_info.background_start_time.strftime('%Y%m%d');
        ds.RawBck_Start_Time_UT = lidar_info.background_start_time.strftime('%H%M%S');
        ds.RawBck_Stop_Time_UT = lidar_info.background_end_time.strftime('%H%M%S');
    
    make_nc_var(ds, name = 'Acquisition_Mode', value = channel_info.acquisition_mode.values, dtype = 'int', dims = ('channels',))

    make_nc_var(ds, name = 'Altitude', value = lidar_info.altitude, dtype = 'float')

    make_nc_var(ds, name = 'ADC_resolution', value = channel_info.analog_to_digital_resolution.values, dtype = 'float', dims = ('channels',))
    
    make_nc_var(ds, name = 'Background_Low', value = channel_info.background_low.values, dtype = 'float', dims = ('channels',))
    
    make_nc_var(ds, name = 'Background_High', value = channel_info.background_high.values, dtype = 'float', dims = ('channels',))
    
    if not isinstance(sig_d,list):
        make_nc_var(ds, name = 'Background_Profile', value = sig_d.values, dtype = 'float', dims = ('time_bck', 'channels', 'points',))

    make_nc_var(ds, name = 'channel_ID', value = channel_info.channel_id.values, dtype = 'int', dims = ('channels',))

    make_nc_str(ds, name = 'channel_label', value = channel_label, dims = ('channels','nchar'))    
    
    make_nc_var(ds, name = 'DAQ_Range', value = channel_info.data_acquisition_range.values, dtype = 'float', dims = ('channels',))
    
    make_nc_var(ds, name = 'Dead_Time', value = channel_info.dead_time.values, dtype = 'float', dims = ('channels',))

    make_nc_var(ds, name = 'Dead_Time_Correction_Type', value = channel_info.dead_time_correction_type.values, dtype = 'int', dims = ('channels',))
    
    make_nc_var(ds, name = 'Detected_Wavlength', value = channel_info.detected_wavelength.values, dtype = 'float', dims = ('channels',))
    
    make_nc_var(ds, name = 'Emitted_Wavlength', value = channel_info.emitted_wavelength.values, dtype = 'float', dims = ('channels',))
    
    make_nc_var(ds, name = 'First_Signal_Rangebin', value = channel_info.trigger_delay_bins.values, dtype = 'int', dims = ('channels',))
    
    make_nc_var(ds, name = 'Full_Overlap_Range', value = channel_info.full_overlap_distance.values, dtype = 'int', dims = ('channels',))
    
    make_nc_var(ds, name = 'id_timescale', value = np.zeros(n_channels), dtype = 'int', dims = ('channels',))

    make_nc_var(ds, name = 'Channel_Bandwidth', value = channel_info.channel_bandwidth.values, dtype = 'int', dims = ('channels',))
    
    make_nc_var(ds, name = 'Laser_Pointing_Angle', value = lidar_info.zenith_angle*np.ones(n_scan_angles), dtype = 'float', dims = ('scan_angles',))

    make_nc_var(ds, name = 'Laser_Pointing_Azimuth_Angle', value = lidar_info.azimuth_angle*np.ones(n_scan_angles), dtype = 'float', dims = ('scan_angles',))
    
    make_nc_var(ds, name = 'Laser_Pointing_Angle_of_Profiles', value = np.zeros([n_time, n_nb_of_time_scales]), dtype = 'int', dims = ('time', 'nb_of_time_scales',))

    make_nc_var(ds, name = 'Laser_Polarization',  value = channel_info.laser_polarization.values, dtype = 'int', dims = ('channels',))

    make_nc_var(ds, name = 'Laser_Repetition_Rate', value = channel_info.laser_repetition_rate.values, dtype = 'int', dims = ('channels',))
    
    make_nc_var(ds, name = 'Laser_Shots', value = shots.values, dtype = 'int', dims = ('time', 'channels',))

    make_nc_var(ds, name = 'Latitude', value = lidar_info.latitude, dtype = 'float')

    make_nc_var(ds, name = 'Longitude', value = lidar_info.longitude, dtype = 'float')

    make_nc_var(ds, name = 'PMT_High_Voltage', value = channel_info.pmt_high_voltage.values, dtype = 'float', dims = ('channels',))
    
    make_nc_var(ds, name = 'Raw_Lidar_Data', value = sig.values, dtype = 'float', dims = ('time', 'channels', 'points',))
    
    make_nc_var(ds, name = 'Raw_Data_Range_Resolution', value = channel_info.range_resolution.values, dtype = 'float', dims = ('channels',))
    
    make_nc_var(ds, name = 'Raw_Data_Start_Time', value = Raw_Start_Time, dtype = 'int', dims = ('time', 'nb_of_time_scales',))
    
    make_nc_var(ds, name = 'Raw_Data_Stop_Time', value = Raw_Stop_Time, dtype = 'int', dims = ('time', 'nb_of_time_scales',))
    
    if not isinstance(sig_d,list):
        make_nc_var(ds, name = 'Bck_Data_Start_Time', value = Bck_Start_Time, dtype = 'int', dims = ('time', 'nb_of_time_scales',))
    
        make_nc_var(ds, name = 'Bck_Data_Stop_Time', value = Bck_Stop_Time, dtype = 'int', dims = ('time', 'nb_of_time_scales',))
    
    make_nc_var(ds, name = 'sector', value = sector.values, dtype = 'int', dims = ('time',))
    
    ds.close()
    
    return()

def calibration_file(lidar_info, channel_info, nc_path, meas_ID, sig, sig_d, shots, position, molecular_calc = [], P = [], T = [], rsonde = [], rayleigh = []):

    """Creates the polarization calibration netcdf file according to the SCC format 
    https://docs.scc.imaa.cnr.it/en/latest/file_formats/netcdf_file.html
    and exports it to nc_path"""
        
    ds = nc.Dataset(nc_path,mode='w')
    
    n_time = sig.time.size
    n_channels = sig.channel.size
    n_points = sig.bins.size
    
    n_nb_of_time_scales = 1
    n_scan_angles = 1

    channel_label = channel_info.telescope_type.values + channel_info.channel_type.values + channel_info.acquisition_type.values + channel_info.channel_subtype.values
    
    Raw_Start_Time = np.nan * np.zeros([n_time,n_nb_of_time_scales])
    Raw_Stop_Time = np.nan * np.zeros([n_time,n_nb_of_time_scales])
    
    Raw_Start_Time[:,0] = np.arange(0,n_time,1) * lidar_info.temporal_resolution.seconds
    Raw_Stop_Time[:,0] = np.arange(1,n_time+1,1) * lidar_info.temporal_resolution.seconds
    
    if not isinstance(sig_d,list):
        n_time_bck = sig_d.time.size
        Bck_Start_Time = np.nan * np.zeros([n_time,n_nb_of_time_scales])
        Bck_Stop_Time = np.nan * np.zeros([n_time,n_nb_of_time_scales])
        Bck_Start_Time[:,0] = np.arange(0,n_time,1) * lidar_info.background_temporal_resolution.seconds
        Bck_Stop_Time[:,0] = np.arange(1,n_time+1,1) * lidar_info.background_temporal_resolution.seconds
    
    ds.createDimension('time', n_time)
    ds.createDimension('channels', n_channels)
    ds.createDimension('points', n_points)
    
    ds.createDimension('nb_of_time_scales', n_nb_of_time_scales)
    ds.createDimension('scan_angles', n_scan_angles)
    
    ds.createDimension('nchar',4)
    
    ds.Measurement_ID = meas_ID
    ds.RawData_Start_Date = lidar_info.start_time.strftime('%Y%m%d');
    ds.RawData_Start_Time_UT = lidar_info.start_time.strftime('%H%M%S');
    ds.RawData_Stop_Time_UT = lidar_info.end_time.strftime('%H%M%S');

    if not isinstance(sig_d,list):
        ds.createDimension('time_bck', n_time_bck)
        ds.RawBck_Start_Date = lidar_info.background_start_time.strftime('%Y%m%d');
        ds.RawBck_Start_Time_UT = lidar_info.background_start_time.strftime('%H%M%S');
        ds.RawBck_Stop_Time_UT = lidar_info.background_end_time.strftime('%H%M%S');
        make_nc_var(ds, name = 'Acquisition_Mode', value = channel_info.acquisition_mode.values, dtype = 'int', dims = ('channels',))

    make_nc_var(ds, name = 'Altitude', value = lidar_info.altitude, dtype = 'float')

    make_nc_var(ds, name = 'ADC_resolution', value = channel_info.analog_to_digital_resolution.values, dtype = 'float', dims = ('channels',))
    
    make_nc_var(ds, name = 'Background_Low', value = channel_info.background_low.values, dtype = 'float', dims = ('channels',))
    
    make_nc_var(ds, name = 'Background_High', value = channel_info.background_high.values, dtype = 'float', dims = ('channels',))
    
    if not isinstance(sig_d,list):
        make_nc_var(ds, name = 'Background_Profile', value = sig_d.values, dtype = 'float', dims = ('time_bck', 'channels', 'points',))

    make_nc_var(ds, name = 'channel_ID', value = channel_info.channel_id.values, dtype = 'int', dims = ('channels',))

    make_nc_str(ds, name = 'channel_label', value = channel_label, dims = ('channels','nchar'))    
    
    make_nc_var(ds, name = 'DAQ_Range', value = channel_info.data_acquisition_range.values, dtype = 'float', dims = ('channels',))
    
    make_nc_var(ds, name = 'Dead_Time', value = channel_info.dead_time.values, dtype = 'float', dims = ('channels',))

    make_nc_var(ds, name = 'Dead_Time_Correction_Type', value = channel_info.dead_time_correction_type.values, dtype = 'int', dims = ('channels',))
    
    make_nc_var(ds, name = 'Detected_Wavlength', value = channel_info.detected_wavelength.values, dtype = 'float', dims = ('channels',))
    
    make_nc_var(ds, name = 'Emitted_Wavlength', value = channel_info.emitted_wavelength.values, dtype = 'float', dims = ('channels',))
    
    make_nc_var(ds, name = 'First_Signal_Rangebin', value = channel_info.trigger_delay_bins.values, dtype = 'int', dims = ('channels',))
    
    make_nc_var(ds, name = 'Full_Overlap_Range', value = channel_info.full_overlap_distance.values, dtype = 'int', dims = ('channels',))
    
    make_nc_var(ds, name = 'id_timescale', value = np.zeros(n_channels), dtype = 'int', dims = ('channels',))

    make_nc_var(ds, name = 'Channel_Bandwidth', value = channel_info.channel_bandwidth.values, dtype = 'int', dims = ('channels',))
    
    make_nc_var(ds, name = 'Laser_Pointing_Angle', value = lidar_info.zenith_angle*np.ones(n_scan_angles), dtype = 'float', dims = ('scan_angles',))

    make_nc_var(ds, name = 'Laser_Pointing_Azimuth_Angle', value = lidar_info.azimuth_angle*np.ones(n_scan_angles), dtype = 'float', dims = ('scan_angles',))
    
    make_nc_var(ds, name = 'Laser_Pointing_Angle_of_Profiles', value = np.zeros([n_time, n_nb_of_time_scales]), dtype = 'int', dims = ('time', 'nb_of_time_scales',))

    make_nc_var(ds, name = 'Laser_Polarization',  value = channel_info.laser_polarization.values, dtype = 'int', dims = ('channels',))

    make_nc_var(ds, name = 'Laser_Repetition_Rate', value = channel_info.laser_repetition_rate.values, dtype = 'int', dims = ('channels',))
    
    make_nc_var(ds, name = 'Laser_Shots', value = shots.values, dtype = 'int', dims = ('time', 'channels',))

    make_nc_var(ds, name = 'Latitude', value = lidar_info.latitude, dtype = 'float')

    make_nc_var(ds, name = 'Longitude', value = lidar_info.longitude, dtype = 'float')

    make_nc_var(ds, name = 'PMT_High_Voltage', value = channel_info.pmt_high_voltage.values, dtype = 'float', dims = ('channels',))
    
    make_nc_var(ds, name = 'Raw_Lidar_Data', value = sig.values, dtype = 'float', dims = ('time', 'channels', 'points',))
    
    make_nc_var(ds, name = 'Raw_Data_Range_Resolution', value = channel_info.range_resolution.values, dtype = 'float', dims = ('channels',))
    
    make_nc_var(ds, name = 'Raw_Data_Start_Time', value = Raw_Start_Time, dtype = 'int', dims = ('time', 'nb_of_time_scales',))
    
    make_nc_var(ds, name = 'Raw_Data_Stop_Time', value = Raw_Stop_Time, dtype = 'int', dims = ('time', 'nb_of_time_scales',))

    make_nc_var(ds, name = 'calibrator_position', value = position.values, dtype = 'int', dims = ('time',))
    
    if not isinstance(sig_d,list):
        make_nc_var(ds, name = 'Bck_Data_Start_Time', value = Bck_Start_Time, dtype = 'int', dims = ('time', 'nb_of_time_scales',))
    
        make_nc_var(ds, name = 'Bck_Data_Stop_Time', value = Bck_Stop_Time, dtype = 'int', dims = ('time', 'nb_of_time_scales',))
    
    if isinstance(molecular_calc, list) == False:
    
        make_nc_var(ds, name = 'Molecular_Calc', value = molecular_calc, dtype = 'int')
    
        if molecular_calc == 4 or molecular_calc == 0:
            
            if isinstance(P,list):
                sys.exit('-- Error: The ground pressure must be provided in the make.file routine when molecular_calc = 4 (USSTD selected) or 0 (automatic selected)')
       
            if isinstance(T,list):
                sys.exit('-- Error: The ground temperature must be provided in the make.file routine when molecular_calc = 4 (USSTD selected) or 0 (automatic selected)')
       
            make_nc_var(ds, name = 'Pressure_at_Lidar_Station', value = P, dtype = 'float')
            
            make_nc_var(ds, name = 'Temperature_at_Lidar_Station', value = T, dtype = 'float')
            
        if molecular_calc == 1:
            
            if isinstance(rsonde,list):
                sys.exit('-- Error: The radiosonde filenmame must be provided in the make.file routine when molecular_calc = 1 (Radiosonde selected)')
       
            ds.Sounding_File_Name = rsonde;

    if isinstance(rayleigh, list) == False:
        
        ds.Rayleigh_File_Name = rayleigh;
    
    ds.close()
    
    return()

def dark_file(lidar_info, channel_info, nc_path, meas_ID, sig_d, shots):

    """Creates a standalone dark netcdf file according to the SCC format 
    https://docs.scc.imaa.cnr.it/en/latest/file_formats/netcdf_file.html
    and exports it to nc_path"""
        
    ds = nc.Dataset(nc_path,mode='w')
    
    n_time = sig_d.time.size
    n_channels = sig_d.channel.size
    n_points = sig_d.bins.size
    
    n_time_bck = sig_d.time.size
    n_nb_of_time_scales = 1
    n_scan_angles = 1
    
    channel_label = channel_info.telescope_type.values + channel_info.channel_type.values + channel_info.acquisition_type.values + channel_info.channel_subtype.values
    
    Bck_Start_Time = np.nan * np.zeros([n_time,n_nb_of_time_scales])
    Bck_Stop_Time = np.nan * np.zeros([n_time,n_nb_of_time_scales])
        
    Bck_Start_Time[:,0] = np.arange(0,n_time,1) * lidar_info.background_temporal_resolution.seconds
    Bck_Stop_Time[:,0] = np.arange(1,n_time+1,1) * lidar_info.background_temporal_resolution.seconds
    
    ds.createDimension('time', n_time)
    ds.createDimension('channels', n_channels)
    ds.createDimension('points', n_points)
    
    ds.createDimension('time_bck', n_time_bck)
    ds.createDimension('nb_of_time_scales', n_nb_of_time_scales)
    ds.createDimension('scan_angles', n_scan_angles)
    
    ds.createDimension('nchar',4)
    
    ds.Measurement_ID = meas_ID
    ds.RawBck_Start_Date = lidar_info.background_start_time.strftime('%Y%m%d');
    ds.RawBck_Start_Time_UT = lidar_info.background_start_time.strftime('%H%M%S');
    ds.RawBck_Stop_Time_UT = lidar_info.background_end_time.strftime('%H%M%S');
    
    make_nc_var(ds, name = 'Acquisition_Mode', value = channel_info.acquisition_mode.values, dtype = 'int', dims = ('channels',))

    make_nc_var(ds, name = 'Altitude', value = lidar_info.altitude, dtype = 'float')

    make_nc_var(ds, name = 'ADC_resolution', value = channel_info.analog_to_digital_resolution.values, dtype = 'float', dims = ('channels',))
    
    make_nc_var(ds, name = 'Background_Low', value = channel_info.background_low.values, dtype = 'float', dims = ('channels',))
    
    make_nc_var(ds, name = 'Background_High', value = channel_info.background_high.values, dtype = 'float', dims = ('channels',))

    make_nc_var(ds, name = 'channel_ID', value = channel_info.channel_id.values, dtype = 'int', dims = ('channels',))

    make_nc_str(ds, name = 'channel_label', value = channel_label, dims = ('channels','nchar',))    
    
    make_nc_var(ds, name = 'DAQ_Range', value = channel_info.data_acquisition_range.values, dtype = 'float', dims = ('channels',))
    
    make_nc_var(ds, name = 'Dead_Time', value = channel_info.dead_time.values, dtype = 'float', dims = ('channels',))

    make_nc_var(ds, name = 'Dead_Time_Correction_Type', value = channel_info.dead_time_correction_type.values, dtype = 'int', dims = ('channels',))
    
    make_nc_var(ds, name = 'Detected_Wavlength', value = channel_info.detected_wavelength.values, dtype = 'float', dims = ('channels',))
    
    make_nc_var(ds, name = 'Emitted_Wavlength', value = channel_info.emitted_wavelength.values, dtype = 'float', dims = ('channels',))
    
    make_nc_var(ds, name = 'First_Signal_Rangebin', value = channel_info.trigger_delay_bins.values, dtype = 'int', dims = ('channels',))
    
    make_nc_var(ds, name = 'Full_Overlap_Range', value = channel_info.full_overlap_distance.values, dtype = 'int', dims = ('channels',))
    
    make_nc_var(ds, name = 'id_timescale', value = np.zeros(n_channels), dtype = 'int', dims = ('channels',))

    make_nc_var(ds, name = 'IFF_Central_Wavelength', value = channel_info.iff_central_wavelength.values, dtype = 'int', dims = ('channels',))

    make_nc_var(ds, name = 'IFF_bandwidth', value = channel_info.iff_bandwidth.values, dtype = 'int', dims = ('channels',))
    
    make_nc_var(ds, name = 'Laser_Pointing_Angle', value = lidar_info.zenith_angle*np.ones(n_scan_angles), dtype = 'float', dims = ('scan_angles',))
    
    make_nc_var(ds, name = 'Laser_Pointing_Azimuth_Angle', value = lidar_info.azimuth_angle*np.ones(n_scan_angles), dtype = 'float', dims = ('scan_angles',))

    make_nc_var(ds, name = 'Laser_Pointing_Angle_of_Profiles', value = np.zeros([n_time, n_nb_of_time_scales]), dtype = 'int', dims = ('time', 'nb_of_time_scales',))

    make_nc_var(ds, name = 'Laser_Polarization',  value = channel_info.laser_polarization.values, dtype = 'int', dims = ('channels',))

    make_nc_var(ds, name = 'Laser_Repetition_Rate', value = channel_info.laser_repetition_rate.values, dtype = 'int', dims = ('channels',))
    
    make_nc_var(ds, name = 'Laser_Shots', value = shots.values, dtype = 'int', dims = ('time', 'channels',))

    make_nc_var(ds, name = 'Latitude', value = lidar_info.latitude, dtype = 'float')

    make_nc_var(ds, name = 'Longitude', value = lidar_info.longitude, dtype = 'float')

    make_nc_var(ds, name = 'PMT_High_Voltage', value = channel_info.pmt_high_voltage.values, dtype = 'float', dims = ('channels',))
        
    make_nc_var(ds, name = 'Raw_Data_Range_Resolution', value = channel_info.range_resolution.values, dtype = 'float', dims = ('channels',))
            
    ds.close()
    
    return()

def meas_id(lr_id, sig):
    """Creates a sting variable with the measurement ID variable according to: 
    https://docs.scc.imaa.cnr.it/en/latest/file_formats/netcdf_file.html"""
    
    start_date = sig.time.dt.date.values[0].strftime('%Y%m%d')
    
    start_time = sig.time.dt.time.values[0].strftime('%H%M')
        
    meas_ID = f"{start_date}{lr_id}{start_time}"
    
    return(meas_ID)
        
def path(results_folder, meas_ID, meas_type):
    """Creates a sting variable with the full path to the output QA file: 
    https://docs.scc.imaa.cnr.it/en/latest/file_formats/netcdf_file.html"""
    
    nc_path = os.path.join(results_folder,f'{meas_ID}{meas_type}.nc')
    
    if os.path.exists(results_folder) == False:
        os.makedirs(nc_path)
        
    if os.path.exists(nc_path):
        os.unlink(nc_path)
        
    return(nc_path)

def make_nc_var(ds, name, value, dtype, dims = []):  
    """Function called by the *_file functions in order to fascilitate variable
    creation in the netcdf"""
    
    if dtype == 'int':
        func = np.int32
        default_val = nc.default_fillvals['i8']
        
    if dtype == 'float':
        func = np.double
        default_val = nc.default_fillvals['f8']
      
    if len(dims) == 0:
        value = func(value)
    else:
        value[value != value] = default_val
        value = value.astype(dtype)

    var = ds.createVariable(name, func, dims)
    
    if len(dims) == 0:
        var[:] = value

    elif len(dims) == 1:
        var[:] = value

    elif len(dims) == 2:
        var[:,:] = value
        
    elif len(dims) == 3:
        var[:,:,:] = value
        
    else:
        sys.exit('-- Error: 4 or higher dimensional arrays not supported in function make_nc_var')
        
    return()

def make_nc_str(ds, name, value, dims):  
    """Function called by the *_file functions in order to fascilitate variable
    creation in the netcdf"""

    value_char = nc.stringtochar(value.astype('S4'))

    var = ds.createVariable(name, 'S1', dims)
    

    if len(dims) == 1:
        var[:] = value_char

    elif len(dims) == 2:
        var[:,:] = value_char
        
    elif len(dims) == 3:
        var[:,:,:] = value_char
        
    else:
        sys.exit('-- Error: 4 or higher dimensional arrays and scalars not supported in function make_nc_str')
        
    return()
    
    