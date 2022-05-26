"""
@author: N. Siomos & P. Paschou

Main algorithm for pre-processing the raw signals and retrieve the optical products
"""
import warnings, os,sys
from readers.read_config import config
from readers.parse_config import parse_config
from readers.read_signals import read_signals
from molecular.short_molec import short_molec
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

ds = nc.Dataset(r'./temp.nc',mode='w')
ds.createDimension('time', sig_raw.time.size)
ds.createDimension('channels', sig_raw.channel.size)
ds.createDimension('points', sig_raw.bins.size)  #16382
time_bck = ds.createDimension('time_bck', 1)
nb_of_time_scales = ds.createDimension('nb_of_time_scales', 1)
scan_angles = ds.createDimension('scan_angles', 1)
ds.Measurement_ID=year+month+day+'the' +hour+minute
ds.RawData_Start_Date = year+month+day;
ds.RawData_Start_Time_UT = hour+minute+second;
ds.RawData_Stop_Time_UT = hour_stop+minute_stop+second_stop;
ds.RawBck_Start_Date = year+month+day;
ds.RawBck_Start_Time_UT = hour_dr_start+minute_dr_start+second_dr_start;
ds.RawBck_Stop_Time_UT = hour_dr_stop+minute_dr_stop+second_dr_stop;
# ds.Measurement_ID='20220113th01'
# ds.RawData_Start_Date = "20220113";
# ds.RawData_Start_Time_UT = "163458";
# ds.RawData_Stop_Time_UT = "172629";
# ds.RawBck_Start_Date = "20220113";
# ds.RawBck_Start_Time_UT = "165259";
# ds.RawBck_Stop_Time_UT = "165455";
ds.Sounding_File_Name = "rs_20220411the02.nc";      

#02:day & 01:night20


Background_High = ds.createVariable('Background_High',np.double, ('channels',))
Background_Low = ds.createVariable('Background_Low',np.double, ('channels',))
Background_Profile = ds.createVariable('Background_Profile',np.double, ( 'time_bck','channels', 'points',))
channel_ID =ds.createVariable('channel_ID',np.int32, ('channels',))
DAQ_Range =ds.createVariable('DAQ_Range',np.double, ('channels',))
#First_Signal_Rangebin =ds.createVariable('First_Signal_Rangebin',np.int32, ('channels',))
id_timescale =ds.createVariable('id_timescale',np.int32, ('channels',))
Laser_Pointing_Angle=ds.createVariable('Laser_Pointing_Angle',np.double, ('scan_angles',))
Laser_Pointing_Angle_of_Profiles=ds.createVariable('Laser_Pointing_Angle_of_Profiles',np.int32, ('time', 'nb_of_time_scales',))
#aser_Shots=ds.createVariable('Laser_Shots',np.int32, ('channels',))
Laser_Shots=ds.createVariable('Laser_Shots',np.int32, ('time','channels',))
LR_Input=ds.createVariable('LR_Input',np.int32, ('channels',))
Molecular_Calc=ds.createVariable('Molecular_Calc',np.int32)
Pressure_at_Lidar_Station=ds.createVariable('Pressure_at_Lidar_Station',np.double)
Raw_Lidar_Data=ds.createVariable('Raw_Lidar_Data',np.double, ('time', 'channels', 'points',))
Raw_Bck_Start_Time=ds.createVariable('Raw_Bck_Start_Time',np.int32, ('time_bck','nb_of_time_scales',))
Raw_Bck_Stop_Time=ds.createVariable('Raw_Bck_Stop_Time',np.int32, ('time_bck','nb_of_time_scales',))
Raw_Data_Start_Time=ds.createVariable('Raw_Data_Start_Time',np.int32, ('time','nb_of_time_scales',))
Raw_Data_Stop_Time=ds.createVariable('Raw_Data_Stop_Time',np.int32, ('time','nb_of_time_scales',))
Temperature_at_Lidar_Station=ds.createVariable('Temperature_at_Lidar_Station',np.double)

d=np.mean(sig_raw_d[:,:,0:16380],axis=0)
a=len(sig_raw[:,0,0])
b=len(sig_raw[:,0,0])
Raw_Lidar_Data[:,:,:]=sig_raw[:,:,0:16380]
#Raw_Lidar_Data[:,:,:]=sig_raw[:,:,:]
Background_High[:]=30000
Background_Low[:]=28000
# #Background_Profile[:]=sig_raw_d[0,:,:].values
Background_Profile[:]=d.values

#====== Night Channels ======#
channel_ID[:]=[1721,1722,1723,1724,1698,1699,1700,1719,1717,1720,1718]

#====== Day Channels ========#
#channel_ID[:]=[1723,1724,1721,1722,1698,1699,1700]

DAQ_Range[:]=100
#First_Signal_Rangebin[:]=[1,4,1,4,-5,3,-6]
Laser_Pointing_Angle[:]=0.02
Laser_Pointing_Angle_of_Profiles[:]=0.0
Laser_Shots[:]= info_val.shots[0]                        #info_val.shots
LR_Input[:]=1
Molecular_Calc[:]=1
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
molec_map = read_maps.molecular(maps_dir, 'molecular.ini')
sig, molec_pack, molec_map = short_molec(sig_raw.copy(), cfg, molec_map) 


