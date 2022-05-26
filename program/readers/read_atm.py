"""
@author: N.Siomos and P. Paschou

Functions for reading the temperature and pressure profiles from
- radiosonde
- NWP model (WRF)
"""
import numpy as np
import glob
import os
import datetime as dt

def rsonde(dir_path):  
    
    alt=[]
    prs=[]
    tem=[]
    hum=[]
    imol = 3
    #fname = glob.glob(os.path.join(dir_path, 'SO*'))
    fname = glob.glob(os.path.join(dir_path, '*.txt'))
    
    if len(fname) > 1:
        print('---- Warning! Too many radiosonde files found in folder --> \n'
              'Using U.S. standard atmosphere instead..')
        imol=1 # change the imol indicator for US standard
    
    if len(fname) == 0:
        print('---- Warning! No radiosonde file found --> \n'
              'Using U.S. standard atmosphere instead..')
        imol=1 # change the imol indicator for US standard
        
    if len(fname) == 1:
        data = np.loadtxt(fname[0],skiprows = 7, delimiter='~', dtype=str)
		
        prs = np.nan*np.zeros(len(data) + 1)
        alt = np.nan*np.zeros(len(data) + 1)
        tem = np.nan*np.zeros(len(data) + 1)
        hum = np.nan*np.zeros(len(data) + 1)
        
        for j in range(1,len(data) + 1):
            prs[j] = float(data[j-1][0:8])
            alt[j] = float(data[j-1][8:15])
            tem[j] = float(data[j-1][15:20]) + 273.15
            hum[j] = float(data[j-1][28:35])
        mask_empty = (prs == prs) & (alt == alt) & (tem == tem) & (hum == hum)
        
        prs = prs[mask_empty]
        alt = alt[mask_empty]
        tem = tem[mask_empty]
        hum = hum[mask_empty]
        
        prs[0] = prs[1]
        alt[0] = 0.
        tem[0] = tem[1]    
        hum[0] = hum[1]    
    
    return(alt,prs,tem,hum,imol)

def model(dir_path):
    
    alt=[]
    prs=[]
    tem=[]
    hum=[]
    imol = 2
    fname = glob.glob(os.path.join(dir_path, '*.txt'))
    
    if len(fname) > 1:
        print('---- Warning! Too many model files found in folder --> \n'
              'Using U.S. standard atmosphere instead..')
        imol=1 # change the imol indicator for US standard
    
    if len(fname) == 0:
        print('---- Warning! No model file found --> \n'
              'Using U.S. standard atmosphere instead..')
        imol=1 # change the imol indicator for US standard
        
    if len(fname) == 1:
        data = np.loadtxt(fname[0], skiprows = 0, delimiter='~', dtype=str)
		
        prs = np.nan*np.zeros(len(data) + 1)
        alt = np.nan*np.zeros(len(data) + 1)
        tem = np.nan*np.zeros(len(data) + 1)
        hum = np.nan*np.zeros(len(data) + 1)

        for j in range(1,len(data)):
            split_data = data[j].split(',')
            
            prs[j] = float(split_data[1].strip())
            alt[j] = float(split_data[5].strip())
            tem[j] = float(split_data[2].strip()) + 273.15
            hum[j] = float(split_data[4].strip())
            
        mask_empty = (prs == prs) & (alt == alt) & (tem == tem) & (hum == hum)
        
        prs = prs[mask_empty]
        alt = alt[mask_empty]
        tem = tem[mask_empty]
        hum = hum[mask_empty]

        prs[0] = prs[1]
        alt[0] = 0.
        tem[0] = tem[1]    
        hum[0] = hum[1]    
    
    
    return(alt,prs,tem,hum,imol)

def extract_rsonde_info(dir_path):
    fname = glob.glob(os.path.join(dir_path, '*.txt'))

    if len(fname) == 1:
        data = np.loadtxt(fname[0], max_rows=1, dtype=object)
        st_id = data[0]
        loc = data[2]
        t = f'{data[-4][:2]}UTC'
        m = str(dt.datetime.strptime(data[-2],'%b').month)
        date = f'{data[-3]}.{m}.{data[-1][-2:]}'
        info = ', '.join([loc,st_id,date,t])
    else:
        info = 'location, station_ID, dd.mm.yy, hhUTC'
        print('---- Warning! No or Too many radiosonde file(s) found in folder!\n'
              f'Returns no info about {info}')
        
    return(info)