"""
@author: P. Paschou & N. Siomos
"""
import configparser
import re
import numpy as np
import pandas as pd
import sys

class config():
    
    def __init__(self, path):
        """Reads the config file at the given path"""
        
        parser = configparser.ConfigParser()
        parser.read(path)

# Lidar
        if parser.has_section('Lidar'):

            self.meas = read_section(parser['Lidar'], dtype = object, squeeze = True)

            if 'file_format' not in self.meas:
                self.meas['file_format'] = 'licel'

        else:
            
            sys.exit("-- Error: No lidar section is provided in the configuration files. Please include a section with at least the mandatory fields!")

# Channels
        if parser.has_section('Channels'):
            
            channel_section = read_section(parser['Channels'], dtype = object)
            
            channel_section[channel_section == '_'] = np.nan

            check_channels(channel_info = channel_section, 
                           file_format = self.meas['file_format'])
            
            channels = [f'{channel_section.channel_id[i]}_L{str(int(channel_section.laser[i]))}'
                        for i in range(channel_section.index.size)]
            
            channel_section.index = channels 
            
            self.channels = channel_section
            
        else:
            
            sys.exit("-- Error: No channel section is provided in the configuration files. Please include a section with at least the mandatory fields!")
            
# -------- END OF CLASS

def read_section(section, dtype=object, skip_vars=[], squeeze = False):
    # Reads the whole or part of the section and returns a Pandas Series
    first = True
    map_info = []

    for key in section:
        if key not in skip_vars:
            arr = [i.strip() for i in re.split(',', section[key]) if i !='']
            if len(arr) > 0:
                temp = pd.Series(arr, dtype = dtype, name = key)
                if first:
                    map_info = temp
                    first = False
                else:
                    check_len(map_info, temp, section)
                    map_info = pd.concat([map_info, temp], axis = 1)
    
    if len(map_info) > 0 and squeeze:
        map_info = map_info.squeeze()
    
    return(map_info)

def comma_split(var, dtype):
    
    if var != '':
        var = re.split(',', var)
    
        var = np.array([item.strip() for item in var], 
                       dtype = dtype) #trimming the spaces
    else:
        var=[]
    return(var)

def check_channels(channel_info, file_format):
    
    if file_format == 'licel':
            
        # Channel_id check
        for channel_id in channel_info.channel_id:
            
            if isinstance(channel_id,str):
                
                if not (channel_id[:2] == 'BT' or channel_id[:2] == 'BC'):
            
                    sys.exit("-- Error: Provided channel_id not recognized. The first two letters must be either BT or BC. Please do not provide S2A ot S2P channels (currently not supported)!")
        
            else:
                
                sys.exit("-- Error: The channel_id provided in the configuration file must be a string. Please correct!")
    
        # Laser number check
        for laser in channel_info.laser:
                            
            if int(laser) not in [1, 2, 3, 4]:
        
                sys.exit("-- Error: Provided laser number not recognized. Licel uses a laser number between 1 and 4!")
        
    return()
    
def check_len(reference_var, testing_var, section):
    if len(reference_var) != len(testing_var):
        raise ValueError(f'Length inconsistencies detected in {section}. All section variables must have the same length! Please revise the configuration file!')
    return()