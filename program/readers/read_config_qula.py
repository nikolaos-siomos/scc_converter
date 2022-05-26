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
        self.lidar = read_section(parser['Lidar'], object)

# Angles        
        self.angles = read_section(parser['Angles'], object)
        
# Options    
        self.options = read_section(parser['Options'], object)
        
# Trimming
        self.ch_list = comma_split(parser['Channels']['ch_list'], object)
        
        self.ch_map = comma_split(parser['Channels']['ch_map'], object)
        
        self.timescale = parser['Trimming']['timescale']
        
        self.alt_lim = read_var(parser['Trimming']['alt_lim'], float)

# Channels
        self.channels = read_section(parser['Channels'], object)

# Molecular
        
        self.us = pd.Series([read_var(parser['Molecular']['g_temp'], float),
                             read_var(parser['Molecular']['g_pres'], float)], 
                            index = ['temp','pres'])
        
# -------- END OF CLASS

def read_section(section, dtype=object, skip_vars=[], return_empty=True):
    # Reads the whole or part of the section and returns a Pandas Series
    first = 1
    for key in section:
        if key not in skip_vars:
            temp = pd.Series([i.strip() for i in re.split(',', section[key]) if i !=''], 
                             dtype = dtype, name = key)
            if first == 1:
                map_info = temp
                first = 0
            else:
                check_len(map_info, temp, section)
                map_info = pd.concat([map_info, temp], axis = 1)
    
    if return_empty== True and map_info.isnull().values.any():
        map_info = []

    return(map_info)


def read_dictionary_with_dtype(d, keys, func):
    return {
        key: func(value)
        for key, value in d.items()
        if key in keys
    }

def read_var(var, func):
    #converts the var in a certain type (int, float, etc) unless it is ''
    if var != '':
        var = func(var)
    return(var)

def comma_split(var, func):
    
    if var != '':
        var = re.split(',', var)
    
        var = np.array([item.strip() for item in var], 
                       dtype = func) #trimming the spaces
    else:
        var=[]
    return(var)

def check_len(reference_var, testing_var, section):
    if len(reference_var) != len(testing_var):
        raise ValueError(f'Length inconsistencies detected in section {section}. All section variables must have the same length! Please revise the configuration file!')
    return()