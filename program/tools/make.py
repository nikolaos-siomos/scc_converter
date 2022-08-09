#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jul 26 15:32:07 2022

@author: nick
"""

import os, sys
import netCDF4 as nc
import numpy as np

def rayleigh_file(lidar_info, channel_info, nc_path, meas_ID, sig, sig_d, shots, P = None, T = None, rsonde = None):

    """Creates the rayleigh netcdf file according to the SCC format 
    https://docs.scc.imaa.cnr.it/en/latest/file_formats/netcdf_file.html
    and exports it to nc_path"""
            
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
    
    ds = nc.Dataset(nc_path,mode='w')

# Adding Dimensions    
    ds.createDimension('time', n_time)
    ds.createDimension('channels', n_channels)
    ds.createDimension('points', n_points)
    ds.createDimension('nb_of_time_scales', n_nb_of_time_scales)
    ds.createDimension('scan_angles', n_scan_angles)
    ds.createDimension('nchar',4)
    if not isinstance(sig_d,list):
        ds.createDimension('time_bck', n_time_bck)
    if radiosonde_file:
        ds.Sounding_File_Name = rsonde;
    
# Adding Global Parameters
    ds.Altitude_meter_asl = lidar_info.altitude;

    ds.Latitude_degrees_north = lidar_info.latitude;

    ds.Longitude_degrees_east = lidar_info.longitude;
  
    ds.Measurement_ID = meas_ID;
    
    if not isinstance(sig_d,list):

        ds.RawBck_Start_Date = lidar_info.background_start_time.strftime('%Y%m%d');

        ds.RawBck_Start_Time_UT = lidar_info.background_start_time.strftime('%H%M%S');

        ds.RawBck_Stop_Time_UT = lidar_info.background_end_time.strftime('%H%M%S');

    ds.RawData_Start_Date = lidar_info.start_time.strftime('%Y%m%d');
    
    ds.RawData_Start_Time_UT = lidar_info.start_time.strftime('%H%M%S');
    
    ds.RawData_Stop_Time_UT = lidar_info.end_time.strftime('%H%M%S');

# Adding Variables
    make_nc_var(ds, name = 'Acquisition_Mode', value = channel_info.acquisition_mode.values, dtype = 'int', dims = ('channels',))

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

    make_nc_var(ds, name = 'PMT_High_Voltage', value = channel_info.pmt_high_voltage.values, dtype = 'float', dims = ('channels',))
    
    make_nc_var(ds, name = 'Raw_Lidar_Data', value = sig.values, dtype = 'float', dims = ('time', 'channels', 'points',))
    
    make_nc_var(ds, name = 'Raw_Data_Range_Resolution', value = channel_info.range_resolution.values, dtype = 'float', dims = ('channels',))
    
    make_nc_var(ds, name = 'Raw_Data_Start_Time', value = Raw_Start_Time, dtype = 'int', dims = ('time', 'nb_of_time_scales',))
    
    make_nc_var(ds, name = 'Raw_Data_Stop_Time', value = Raw_Stop_Time, dtype = 'int', dims = ('time', 'nb_of_time_scales',))
    
    if not isinstance(sig_d,list):
        make_nc_var(ds, name = 'Bck_Data_Start_Time', value = Bck_Start_Time, dtype = 'int', dims = ('time', 'nb_of_time_scales',))
    
        make_nc_var(ds, name = 'Bck_Data_Stop_Time', value = Bck_Stop_Time, dtype = 'int', dims = ('time', 'nb_of_time_scales',))
    
    if radiosonde_file:
    
        make_nc_var(ds, name = 'Molecular_Calc', value = 1, dtype = 'int')
    
    else:
        
        make_nc_var(ds, name = 'Molecular_Calc', value = 0, dtype = 'int')
        
        make_nc_var(ds, name = 'Pressure_at_Lidar_Station', value = P, dtype = 'float')
        
        make_nc_var(ds, name = 'Temperature_at_Lidar_Station', value = T, dtype = 'float')

    ds.close()
    
    return()

def telecover_file(lidar_info, channel_info, nc_path, meas_ID, sig, sig_d, shots, sector):

    """Creates the telecover netcdf file according to the SCC format 
    https://docs.scc.imaa.cnr.it/en/latest/file_formats/netcdf_file.html
    and exports it to nc_path"""
            
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

    ds = nc.Dataset(nc_path,mode='w')

# Adding Dimensions    
    ds.createDimension('time', n_time)
    ds.createDimension('channels', n_channels)
    ds.createDimension('points', n_points)
    ds.createDimension('nb_of_time_scales', n_nb_of_time_scales)
    ds.createDimension('scan_angles', n_scan_angles)
    ds.createDimension('nchar',4)
    if not isinstance(sig_d,list):
        ds.createDimension('time_bck', n_time_bck)
    
# Adding Global Parameters
    ds.Altitude_meter_asl = lidar_info.altitude;

    ds.Latitude_degrees_north = lidar_info.latitude;

    ds.Longitude_degrees_east = lidar_info.longitude;
  
    ds.Measurement_ID = meas_ID;
    
    if not isinstance(sig_d,list):

        ds.RawBck_Start_Date = lidar_info.background_start_time.strftime('%Y%m%d');

        ds.RawBck_Start_Time_UT = lidar_info.background_start_time.strftime('%H%M%S');

        ds.RawBck_Stop_Time_UT = lidar_info.background_end_time.strftime('%H%M%S');

    ds.RawData_Start_Date = lidar_info.start_time.strftime('%Y%m%d');
    
    ds.RawData_Start_Time_UT = lidar_info.start_time.strftime('%H%M%S');
    
    ds.RawData_Stop_Time_UT = lidar_info.end_time.strftime('%H%M%S');

# Adding Variables
    make_nc_var(ds, name = 'Acquisition_Mode', value = channel_info.acquisition_mode.values, dtype = 'int', dims = ('channels',))

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
    
    ds = nc.Dataset(nc_path,mode='w')

# Adding Dimensions
    ds.createDimension('time', n_time)
    ds.createDimension('channels', n_channels)
    ds.createDimension('points', n_points)
    ds.createDimension('nb_of_time_scales', n_nb_of_time_scales)
    ds.createDimension('scan_angles', n_scan_angles)
    ds.createDimension('nchar',4)
    if not isinstance(sig_d,list):
        ds.createDimension('time_bck', n_time_bck)

# Adding Global Parameters
    ds.Altitude_meter_asl = lidar_info.altitude;

    ds.Latitude_degrees_north = lidar_info.latitude;

    ds.Longitude_degrees_east = lidar_info.longitude;
  
    ds.Measurement_ID = meas_ID;
    
    if not isinstance(sig_d,list):

        ds.RawBck_Start_Date = lidar_info.background_start_time.strftime('%Y%m%d');

        ds.RawBck_Start_Time_UT = lidar_info.background_start_time.strftime('%H%M%S');

        ds.RawBck_Stop_Time_UT = lidar_info.background_end_time.strftime('%H%M%S');

    ds.RawData_Start_Date = lidar_info.start_time.strftime('%Y%m%d');
    
    ds.RawData_Start_Time_UT = lidar_info.start_time.strftime('%H%M%S');
    
    ds.RawData_Stop_Time_UT = lidar_info.end_time.strftime('%H%M%S');

# Adding Variables
    make_nc_var(ds, name = 'Acquisition_Mode', value = channel_info.acquisition_mode.values, dtype = 'int', dims = ('channels',))

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

def dark_file(lidar_info, channel_info, nc_path, meas_ID, sig_d, shots_d):

    """Creates the rayleigh netcdf file according to the SCC format 
    https://docs.scc.imaa.cnr.it/en/latest/file_formats/netcdf_file.html
    and exports it to nc_path"""
            
    n_time = sig_d.time.size
    n_channels = sig_d.channel.size
    n_points = sig_d.bins.size

    n_nb_of_time_scales = 1
    n_scan_angles = 1
    
    channel_label = channel_info.telescope_type.values + channel_info.channel_type.values + channel_info.acquisition_type.values + channel_info.channel_subtype.values
    
    if not isinstance(sig_d,list):
        n_time_bck = sig_d.time.size
        Bck_Start_Time = np.nan * np.zeros([n_time,n_nb_of_time_scales])
        Bck_Stop_Time = np.nan * np.zeros([n_time,n_nb_of_time_scales])
        Bck_Start_Time[:,0] = np.arange(0,n_time,1) * lidar_info.background_temporal_resolution.seconds
        Bck_Stop_Time[:,0] = np.arange(1,n_time+1,1) * lidar_info.background_temporal_resolution.seconds

    ds = nc.Dataset(nc_path,mode='w')

# Adding Dimensions
    ds.createDimension('time', n_time)
    ds.createDimension('channels', n_channels)
    ds.createDimension('points', n_points)
    ds.createDimension('nb_of_time_scales', n_nb_of_time_scales)
    ds.createDimension('scan_angles', n_scan_angles)
    ds.createDimension('nchar',4)
    ds.createDimension('time_bck', n_time_bck)    

# Adding Global Parameters
    ds.Altitude_meter_asl = lidar_info.altitude;

    ds.Latitude_degrees_north = lidar_info.latitude;

    ds.Longitude_degrees_east = lidar_info.longitude;
  
    ds.Measurement_ID = meas_ID;
    
    ds.RawBck_Start_Date = lidar_info.background_start_time.strftime('%Y%m%d');

    ds.RawBck_Start_Time_UT = lidar_info.background_start_time.strftime('%H%M%S');

    ds.RawBck_Stop_Time_UT = lidar_info.background_end_time.strftime('%H%M%S');

# Adding Variables
    make_nc_var(ds, name = 'Acquisition_Mode', value = channel_info.acquisition_mode.values, dtype = 'int', dims = ('channels',))

    make_nc_var(ds, name = 'ADC_resolution', value = channel_info.analog_to_digital_resolution.values, dtype = 'float', dims = ('channels',))
    
    make_nc_var(ds, name = 'Background_Low', value = channel_info.background_low.values, dtype = 'float', dims = ('channels',))
    
    make_nc_var(ds, name = 'Background_High', value = channel_info.background_high.values, dtype = 'float', dims = ('channels',))
    
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
    
    make_nc_var(ds, name = 'Laser_Shots', value = shots_d.values, dtype = 'int', dims = ('time', 'channels',))

    make_nc_var(ds, name = 'PMT_High_Voltage', value = channel_info.pmt_high_voltage.values, dtype = 'float', dims = ('channels',))
        
    make_nc_var(ds, name = 'Raw_Data_Range_Resolution', value = channel_info.range_resolution.values, dtype = 'float', dims = ('channels',))
    
    make_nc_var(ds, name = 'Bck_Data_Start_Time_UT', value = Bck_Start_Time, dtype = 'int', dims = ('time', 'nb_of_time_scales',))
    
    make_nc_var(ds, name = 'Bck_Data_Stop_Time_UT', value = Bck_Stop_Time, dtype = 'int', dims = ('time', 'nb_of_time_scales',))
    
    ds.close()
    
    return()

def radiosonde_file(nc_path, date, time, geodata, atmo):

    """Creates the radiosonde netcdf file according to the SCC format 
    https://docs.scc.imaa.cnr.it/en/latest/file_formats/netcdf_file.html
    and exports it to nc_path"""
        
    ds = nc.Dataset(nc_path,mode='w')
    
    n_points = atmo.height.size
    
    ds.createDimension('points', n_points)
            
    ds.Altitude_meter_asl = geodata[2];

    ds.Latitude_degrees_north = geodata[0];

    ds.Longitude_degrees_east = geodata[1];

    ds.Sounding_Start_Date = date;

    ds.Sounding_Start_Time_UT = time;

    make_nc_var(ds, name = 'Altitude', value = atmo.height.values, dtype = 'float', dims = ('points',))

    make_nc_var(ds, name = 'Pressure', value = atmo.loc[dict(parameters = 'P')].values, dtype = 'float', dims = ('points',))

    make_nc_var(ds, name = 'Temperature', value = atmo.loc[dict(parameters = 'T')].values, dtype = 'float', dims = ('points',))

    if 'RH' in atmo.parameters.values:
        make_nc_var(ds, name = 'RelativeHumidity', value = atmo.loc[dict(parameters = 'RH')].values, dtype = 'float', dims = ('points',))

    ds.close()
    
    return()

def debug_file(path, data, meas_type, label, meas_ID, show_index = False, header = True):
    
    debug_folder = os.path.join(path, 'debug')
    
    fname = os.path.join(debug_folder,f'{meas_type}_{meas_ID}_{label}.txt')
    
    data.to_csv(fname, index = show_index, header = header)
    
    return()

def meas_id(lr_id, time):
    """Creates a sting variable with the measurement ID variable according to: 
    https://docs.scc.imaa.cnr.it/en/latest/file_formats/netcdf_file.html"""
    
    start_date = time.dt.date.values[0].strftime('%Y%m%d')
    
    start_time = time.dt.time.values[0].strftime('%H%M')
        
    meas_ID = f"{start_date}{lr_id}{start_time}"
    
    return(meas_ID)
        
def path(results_folder, meas_ID, meas_type):
    """Creates a sting variable with the full path to the output QA file: 
    https://docs.scc.imaa.cnr.it/en/latest/file_formats/netcdf_file.html"""
    
    nc_path = os.path.join(results_folder,f'{meas_type}_{meas_ID}.nc')
    
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
    
    