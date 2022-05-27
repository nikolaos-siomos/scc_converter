"""
@author: P. Paschou & N. Siomos
"""
import configparser
import re
import numpy as np
import pandas as pd


class config():
    
    def __init__(self, path):
        """Reads the config file at the given path"""
        
        parser = configparser.ConfigParser()
        parser.read(path)

# Lidar
        if parser.has_section('Lidar'):
            self.lidar = read_section(parser['Lidar'], dtype = object, squeeze = True)
        else:
            self.lidar = None

# Channels
        if parser.has_section('Channels'):
            self.channels = read_section(parser['Channels'], dtype = object)
        else:
            self.channels = None

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

def check_len(reference_var, testing_var, section):
    if len(reference_var) != len(testing_var):
        raise ValueError(f'Length inconsistencies detected in {section}. All section variables must have the same length! Please revise the configuration file!')
    return()