"""
@author: Voudouri Kelly

Main algorithm for preparing the SCC netcdf files 

"""
import warnings
import os,sys
from readers.read_config import config # -----> Read config file for ALOMAR
from readers.parse_config import parse_config # 
#from readers.handling_dirs isig_rawmport handling_dirs # ----> Hadling directories
from readers.read_signals import read_signals # 
import netCDF4 as nc
import numpy as np
import matplotlib.pyplot as plt


#Ignores all warnings --> they are not printed in terminal
warnings.filterwarnings('ignore')
#the full path of the config_file.ini
cfg_path = parse_config()
#Reading of the configuration file    
cfg = config(cfg_path)
dirs = cfg.directories


# In[1]
#------------------------------------------------------------
# A) Read and pre-pro2cess the signals
#------------------------------------------------------------
# A.1) Dark
meas_type='dark'
sig_raw_d, _, info_val, _, cfg = read_signals(meas_type, cfg, cfg_path)
           

# A.2)Normal
meas_type= 'normal4'#clb_mode'# 1
sig_raw, _, info_val, _, cfg = read_signals(meas_type, cfg, cfg_path)




for j in info_val.index:
        if info_val.ch_mode[j] == 1.0:
            ch = dict(channel = j)
            #photon counting conversion (MHz to counts)
            sig_raw.loc[ch] = sig_raw.loc[ch].values * \
                info_val.shots[j]/info_val.sampl_rate[j]


for j in info_val.index:
    if info_val.ch_mode[j] == 1.0:
        ch = dict(channel = j)
        #sig_raw.loc[ch] = numpy.rint(sig_raw.loc[ch])
       ## sig_raw.loc[ch] = numpy.round(sig_raw.loc[ch])
        sig_raw.loc[ch] = np.ceil(sig_raw.loc[ch])


#       
###############   write to SCC netcf ##############################################
import glob
dir_path_data='/media/DATA/Thelisys_recorder/04_2022/20220414/04_night/SCC_run/normal*'
dir_path_dark='/media/DATA/Thelisys_recorder/04_2022/20220414/04_night/SCC_run/dark'
#dir_path_rsonde='/media/DATA/Thelisys_record1er/02_2022/20222520221/01_day/SCC_run/atmosphere'
    
search_log= os.path.join(dir_path_data, 'OT22*.*')
file_path = glob.glob(search_log)
file_path.sort()
numfile = len(file_path)


search_log1= os.path.join(dir_path_dark, 'OT22*.*')
file_path1 = glob.glob(search_log1)
file_path1.sort()
numfile1 = len(file_path1)


# search_log2= os.path.join(dir_path_rsonde, 'rs*.nc')
# file_path2 = glob.glob(search_log2)
# file_path2.sort()
# numfile2 = len(file_path2)


day_start=file_path[0]
day_stop=file_path[-1]
day_start=day_start[55:68]
day_stop=day_stop[55:68]


date=file_path[0][(len(file_path[0])-14):(len(file_path[0])-9)]+file_path[0][(len(file_path[0])-8):(len(file_path[0])-10)]

hours=file_path[0][(len(file_path[0])-1):(len(file_path[0])-5)]+file_path[0][(len(file_path[0])-9):(len(file_path[0])-0)]

hours_stop=file_path[-1][(len(file_path[-1])-1):(len(file_path[-1])-5)]+file_path[-1][(len(file_path[-1])-9):(len(file_path[-1])-0)]

hours_start_dr=file_path1[0][(len(file_path1[0])-1):(len(file_path1[0])-5)]+file_path1[0][(len(file_path1[0])-9):(len(file_path1[0])-0)]

hours_stop_dr=file_path1[-1][(len(file_path1[-1])-1):(len(file_path1[-1])-1)]+file_path1[-1][(len(file_path1[-1])-9):(len(file_path1[-1])-0)]

#date_rs=file_path2[0][(len(file_path2[0])-16):(len(file_path2[0])-8)]+file_path2[0][(len(file_path2[0])-8):(len(file_path2[0])-10)]

set=file_path[0][(len(file_path[0])-18):(len(file_path[0])-17)]+file_path[0][(len(file_path[0])-7):(len(file_path[0])-10)]

year = date[0:2]
year = '20'+date[0:2]
day = date[3:5]
if date[2] == 'A':
    month = '10'
if date[2] == 'B':
    month = '11'
if date[2] == 'C':
    month = '12'

if date[2] != 'A' and date[2] != 'B' and date[2] != 'C':
    month = '0'+date[2]
    
#    hour = date[5:7]
#    minute = date[7:9]

hour = hours[0:2]
minute = hours[3:5]
second = hours[5:7]
msecond= hours[7:9]

hour_stop = hours_stop[0:2]
minute_stop = hours_stop[3:5]
second_stop = hours_stop[5:7]
msecond_stop = hours_stop[7:9]

hour_dr_start = hours_start_dr[0:2]
minute_dr_start = hours_start_dr[3:5]
second_dr_start = hours_start_dr[5:7]

hour_dr_stop = hours_stop_dr[0:2]
minute_dr_stop = hours_stop_dr[3:5]
second_dr_stop = hours_stop_dr[5:7]




set_file='0'+str(set)

ds = nc.Dataset(r'/media/DATA/Thelisys_recorder/04_2022/20220414/04_night/SCC_run/results/the'+str(set_file)+'_'+str(year)+str(month)+str(day)+'_'+str(hour)+str(minute)+str(second)+str(msecond)+'_'+str(hour_stop)+str(minute_stop)+str(second_stop)+str(msecond_stop)+'.nc',mode='w')
#ds = nc.Dataset(r'C:\\Users\\Admin\\Desktop\\SCC_converter_TH\\results\\the01_20220113_16345849_17262911.nc',mode='w')
time = ds.createDimension('time', len(sig_raw[:,0,0]))#54
numchannel= ds.createDimension('channels', len(sig_raw[0,:,0]))#11
bins = ds.createDimension('points', 16380)  #16382
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




print('')
print('-----------------------------------------')
print('End of programm!')
print('-----------------------------------------')
