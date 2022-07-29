"""
@author: Peristera
"""
import os, sys

def get_meas_type(path):

    """Identifies if the measurement being processed is a Rayleigh, 
    a Telecover, a Depolarization Calibration, or a standalone Dark."""
    
    meas_type = []

    list_dirs = [d for d in os.listdir(path) if os.path.isdir(os.path.join(path,d))]

    if 'rayleigh' in list_dirs: 
        meas_type.append('rayleigh')
    if 'telecover' in list_dirs:
        meas_type.append('telecover')
    if ('calibration_plus' and 'calibration_minus' in list_dirs) or 'calibration' in list_dirs:
        meas_type.append('calibration')
    if 'dark' in list_dirs:
        meas_type.append('dark')
    else:
        print('-- Warning: No dark folder detected. The generated files will be compatible with the QA software!')
    if len(meas_type) == 0:
        sys.exit('-- Error: None of the expected folders were detected in the parent folder. Please use at least one of the following: dark, rayleigh, telecover, calibration or calibration_plus and calibration_minus')
                
    return(meas_type)

def check_all_dirs(path, files_per_sector):

    print('-----------------------------------------')
    print('Checking folder structure...')
    print('-----------------------------------------')
    
    check_rayleigh(path)
    check_telecover(path, files_per_sector)
    check_calibration(path)
    check_dark(path)
    
    print('-- No problems detected!')

    return()

def check_rayleigh(path):

    """Ensures that the rayleigh folder is properly set, otherwise it raises 
    an error """
    
    path_ray = os.path.join(path,'rayleigh')
    
    if os.path.exists(path_ray):
        list_dirs = [d for d in os.listdir(path_ray) if os.path.isdir(os.path.join(path_ray,d))]

        if len(list_dirs) > 0:
            sys.exit('-- Error: At least one folder was detected inside the ' +
                     'rayleigh directory. Please ensure that only raw files '+
                     'are included inside')
            
    return()

def check_telecover(path, files_per_sector):

    """Ensures that the telecover folder is properly set, otherwise it raises 
    an error """
    
    path_tlc = os.path.join(path,'telecover')
    
    if os.path.exists(path_tlc):
        list_dirs = [d for d in os.listdir(path_tlc) if os.path.isdir(os.path.join(path_tlc,d))]

        if files_per_sector:
            if len(list_dirs) > 0:
                sys.exit('-- Error: At least one folder was detected inside the ' +
                         'telecover directory. Please ensure that only raw files '+
                         'are included inside')
        else:
            if len(list_dirs) != 2 and len(list_dirs) != 4 and len(list_dirs) != 6:
                sys.exit('-- Error: The number of folders does not correspond to '+
                         'one of the following: (2) inner/outer ring telecover, '+
                         '(4): 4 sector telecover, (6) combination of the former')
            elif len(list_dirs) == 2:
                if 'inner' not in list_dirs or 'outer' not in list_dirs:
                    sys.exit('-- Error: The 2 folder structure inside the '+
                             'telecover folder is not correct. Please ensure '+
                             'that the following folders are provided: '+
                             'inner, outer')                       
            elif len(list_dirs) == 4:
                if 'north' not in list_dirs or 'east' not in list_dirs or \
                    'south' not in list_dirs or 'west' not in list_dirs:
                        sys.exit('-- Error: The 4 folder structure inside the '+
                                 'telecover folder is not correct. Please ensure '+
                                 'that the following folders are provided: '+
                                 'north, east, south, west')                    

            elif len(list_dirs) == 6:
                if 'north' not in list_dirs or 'east' not in list_dirs or \
                    'south' not in list_dirs or 'west' not in list_dirs or \
                        'inner' not in list_dirs or 'outer' not in list_dirs:
                        sys.exit('-- Error: The 6 folder structure inside the '+
                                 'telecover folder is not correct. Please ensure '+
                                 'that the following folders are provided: '+
                                 'north, east, south, west, inner, outer')              
    return()

def check_calibration(path):

    """Ensures that the telecover folder is properly set, otherwise it raises 
    an error """
    
    folders = ['calibration', 'calibration_minus', 'calibration_plus']
    
    for folder in folders:
        path_clb = os.path.join(path, folder)
    
        if os.path.exists(path_clb):
            list_dirs = [d for d in os.listdir(path_clb) if os.path.isdir(os.path.join(path_clb,d))]
    
            if len(list_dirs) > 0:
                sys.exit('-- Error: At least one folder was detected inside the ' +
                         f'{folder} directory. Please ensure that only raw files '+
                         'are included inside')

    return()

def check_dark(path):

    """Ensures that the dark folder is properly set, otherwise it raises 
    an error """
    
    path_drk = os.path.join(path,'dark')
    
    if os.path.exists(path_drk):
        list_dirs = [d for d in os.listdir(path_drk) if os.path.isdir(os.path.join(path_drk,d))]

        if os.path.exists(path_drk) and len(list_dirs) > 0:
            sys.exit('-- Error: At least one folder was detected inside the ' +
                     'dark directory. Please ensure that only raw files '+
                     'are included inside')

    return()