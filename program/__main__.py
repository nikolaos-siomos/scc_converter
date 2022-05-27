"""
@author: N. Siomos & P. Paschou

Main algorithm for pre-processing the raw signals and retrieve the optical products
"""
import warnings, os,sys
from readers.read_config import config
from readers.parse_config import parse_config
from readers.read_signals import read_signals
# from molecular.short_molec import short_molec
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import netCDF4 as nc

#Ignores all warnings --> they are not printed in terminal
warnings.filterwarnings('ignore')

#the full path of the config_file.ini
args = parse_config()

#Reading of the configuration file    
cfg = config(path = args['config_file'])

# In[1]
#------------------------------------------------------------
# A) Read and pre-process the signals
#------------------------------------------------------------
# A.1) Dark
sig_raw_d, info, cfg = read_signals(meas_type = 'dark', cfg = cfg, finput = args['parent_folder'])

# A.2)Normal
sig_raw, info, cfg = read_signals(meas_type = 'normal', cfg = cfg, finput = args['parent_folder'])

nc_path = os.path.join(args['results_folder'],'results')

start_date = sig_raw.time.dt.date.values[0].strftime('%Y%m%d')

stop_date = sig_raw.time.dt.date.values[0].strftime('%Y%m%d')

meas_ID = f"{start_date}{cfg.lidar['lr_id']}{args['dataset_number']}"

ds = nc.Dataset(os.path.join(f"{args['results_folder']}",f'{meas_ID}.nc'),mode='w')

ds.createDimension('time', sig_raw.time.size)
ds.createDimension('channels', sig_raw.channel.size)
ds.createDimension('points', sig_raw.bins.size)

time_bck = ds.createDimension('time_bck', 1)
nb_of_time_scales = ds.createDimension('nb_of_time_scales', 1)
scan_angles = ds.createDimension('scan_angles', 1)

ds.Measurement_ID = meas_ID
ds.RawData_Start_Date = cfg.lidar.normal_start_time.strftime('%Y%m%d');
ds.RawData_Start_Time_UT = cfg.lidar.normal_start_time.strftime('%H%M%S');
ds.RawData_Stop_Time_UT = cfg.lidar.normal_end_time.strftime('%H%M%S');
ds.RawBck_Start_Date = cfg.lidar.dark_start_time.strftime('%Y%m%d');
ds.RawBck_Start_Time_UT = cfg.lidar.dark_start_time.strftime('%H%M%S');
ds.RawBck_Stop_Time_UT = cfg.lidar.dark_end_time.strftime('%H%M%S');

# ds.Sounding_File_Name = "rs_20220411the02.nc";      

channel_ID = ds.createVariable('channel_ID', np.int32, ('channels',))
DAQ_Range = ds.createVariable('DAQ_Range', np.double, ('channels',))
id_timescale = ds.createVariable('id_timescale',np.int32, ('channels',))
Laser_Pointing_Angle = ds.createVariable('Laser_Pointing_Angle', np.double, ('scan_angles',))
Laser_Pointing_Angle_of_Profiles = ds.createVariable('Laser_Pointing_Angle_of_Profiles', np.int32, ('time', 'nb_of_time_scales',))
Laser_Shots=ds.createVariable('Laser_Shots',np.int32, ('time','channels',))
LR_Input=ds.createVariable('LR_Input',np.int32, ('channels',))

Background_High = ds.createVariable('Background_High', np.double, ('channels',))
Background_Low = ds.createVariable('Background_Low', np.double, ('channels',))
Background_Profile = ds.createVariable('Background_Profile', np.double, ('time_bck','channels', 'points',))


Molecular_Calc = ds.createVariable('Molecular_Calc',np.int32)

Molecular_Calc[:] = args['molec_calc']

if args['molec_calc'] == 4:
    Pressure_at_Lidar_Station = ds.createVariable('Pressure_at_Lidar_Station',np.double)
    Temperature_at_Lidar_Station = ds.createVariable('Temperature_at_Lidar_Station',np.double)

    Pressure_at_Lidar_Station[:] = args['ground_pressure']
    Temperature_at_Lidar_Station[:] = args['ground_temperature']
if args['molec_calc'] == 1:
    ds.Sounding_File_Name = args['radiosonde_file'];      

Raw_Lidar_Data = ds.createVariable('Raw_Lidar_Data', np.double, ('time', 'channels', 'points',))
Raw_Data_Start_Time = ds.createVariable('Raw_Data_Start_Time', np.int32, ('time', 'nb_of_time_scales',))
Raw_Data_Stop_Time = ds.createVariable('Raw_Data_Stop_Time', np.int32, ('time', 'nb_of_time_scales',))

Raw_Lidar_Data[:,:,:] = sig_raw.values
Raw_Bck_Start_Time = ds.createVariable('Raw_Bck_Start_Time', np.int32, ('time_bck','nb_of_time_scales',))
Raw_Bck_Stop_Time = ds.createVariable('Raw_Bck_Stop_Time', np.int32, ('time_bck','nb_of_time_scales',))

Background_High[:] = info.bgd_end.values
Background_Low[:] = info.bgd_start.values
Background_Profile[:] = sig_raw_d.values

channel_ID[:] = info.ch_id.values

DAQ_Range[:] = info.ADC_range
#First_Signal_Rangebin[:]=[1,4,1,4,-5,3,-6]
Laser_Pointing_Angle[:] = cfg.lidar.zenith
Laser_Pointing_Angle_of_Profiles[:] = 0
Laser_Shots[:]= info_val.shots[0]                        #info_val.shots

id_timescale[:]=0
Raw_Bck_Start_Time[:]=0.0
Raw_Data_Start_Time[:]=np.arange(0,29*a, 29)
Raw_Bck_Stop_Time[:]=29.0
Raw_Data_Stop_Time[:]=np.arange(28,29*b,29)
   

ds.close()




sys.exit(0)
    
# In[3]
#------------------------------------------------------------
# C) Calculation of the molecular profiles
#------------------------------------------------------------
# C.1) Molecular properties
# molec_map = read_maps.molecular(maps_dir, 'molecular.ini')
# sig, molec_pack, molec_map = short_molec(sig_raw.copy(), cfg, molec_map) 


