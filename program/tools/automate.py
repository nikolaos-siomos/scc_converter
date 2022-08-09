"""
@author: Peristera
"""
import os, sys

def get_meas_type(path):

    """Identifies if the measurement being processed is a Rayleigh, 
    a Telecover, a Depolarization Calibration, or a standalone Dark."""
    
    meas_type = []

    list_dirs = [d for d in os.listdir(path) if os.path.isdir(os.path.join(path,d))]

    allowed_types = ['radiosonde', 'rayleigh', 'telecover', 'calibration', 'dark']

    if 'radiosonde' in list_dirs:
        meas_type.append('radiosonde')
        
    if 'rayleigh' in list_dirs: 
        meas_type.append('rayleigh')

    if 'telecover' in list_dirs:
        meas_type.append('telecover')

    if 'calibration' in list_dirs:
        meas_type.append('calibration')

    if 'dark' in list_dirs:
        meas_type.append('dark')
    
    if any(meas_type_i not in allowed_types for meas_type_i in meas_type):
        sys.exit('-- Error: None of the expected folders were detected in the parent folder. Please use at least one of the following: dark, rayleigh, telecover, calibration or calibration_plus and calibration_minus')
                
    return(meas_type)

def check_rayleigh(path):

    """Ensures that the rayleigh folder is properly set, otherwise it raises 
    an error """
        
    if os.path.exists(path):
        
        allowed_folders = ['dark', 'normal']
    
        list_dirs = [d for d in os.listdir(path) 
                     if os.path.isdir(os.path.join(path,d))]
    
        if 'normal' not in list_dirs:
            sys.exit('-- Error: The normal folder was not detected in the '+
                     'rayleigh folder. Please provide it!')
        
        if 'dark' not in list_dirs:
            print('-- Warning: No dark folder detected in the rayleigh folder. '+
                  'The generated rayleigh files will not be compatible with ATLAS!')
    
        if any(dir_i not in allowed_folders for dir_i in list_dirs):
            sys.exit(f'-- Error: The ./rayleigh folder contains at least one directory that is different from the expected ones ({allowed_folders}). Please make sure only the allowed directories exist there')
            
    return()

def check_telecover(path, files_per_sector):

    """Ensures that the telecover folder is properly set, otherwise it raises 
    an error """
        
    if os.path.exists(path):

        allowed_folders = ['dark', 'sectors']
    
        allowed_sfolders = ['north', 'east', 'south', 'west', 'inner', 'outer']
        
        list_dirs = [d for d in os.listdir(path) 
                     if os.path.isdir(os.path.join(path,d))]
    
        if 'sectors' not in list_dirs:
            sys.exit('-- Error: The sectors folder was not detected in the '+
                     'telecover folder. Please provide it!')
    
        if 'dark' not in list_dirs:
            print('-- Warning: No dark folder detected in the rayleigh folder. '+
                  'The generated telecover files will not be compatible with ATLAS!')
    
        if any(dir_i not in allowed_folders for dir_i in list_dirs):
            sys.exit(f'-- Error: The ./telecover folder contains at least one directory that is different from the expected ones ({allowed_folders}). Please make sure only the allowed directories exist there')
              
        if files_per_sector:
            
            if 'sectors' not in list_dirs:
                sys.exit('-- Error: The ./telecover/sectors folder was not detected '+
                         'in the telecover folder. All sector files must be '+
                         'provide in this folder when the files_per_sector '+
                         'argument is used!')
                
        else:
    
            path_sec = os.path.join(path,'sectors')
    
            
            list_sdirs = [d for d in os.listdir(path_sec) 
                         if os.path.isdir(os.path.join(path_sec,d))]
    
            if 'north' not in list_sdirs and 'east' not in list_sdirs and \
                'south' not in list_sdirs and 'west' not in list_sdirs and \
                    'inner' not in list_sdirs and 'outer' not in list_sdirs:
                    
                sys.exit('-- Error: No sector folders were detected in the ' +
                         './telecover/sectors folder. Please either provide ' +
                         'north east south west and/or inner outer folders ' +
                         'or provide the files_per_sector argument as: '+
                         '-n <number_of_files_per sector>')
    
            if ('north' not in list_sdirs or 'east' not in list_sdirs or \
                'south' not in list_sdirs or 'west' not in list_sdirs) and \
                    ('inner' not in list_sdirs or 'outer' in list_sdirs):
            
                sys.exit('-- Error: No complete set is provided in the ' +
                         'in ./telecover/sectors folder. Please provide either '+
                         'all of north east south west or both of '+
                         'inner outer folders') 
                
            if any(dir_i not in allowed_sfolders for dir_i in list_dirs):
                sys.exit(f'-- Error: The ./telecover/sectors folder contains at least one directory that is different from the expected ones ({allowed_folders}). Please make sure only the allowed directories exist there')
  
    return()

def check_calibration(path):

    """Ensures that the calibration folder is properly set, otherwise it raises 
    an error """
    
    if os.path.exists(path):
    
        allowed_folders = ['dark', 'static', '+45','-45']
        
        list_dirs = [d for d in os.listdir(path) 
                     if os.path.isdir(os.path.join(path,d))]
    
        if ('-45' not in list_dirs and '+45' not in list_dirs) \
            and 'static' not in list_dirs:
            sys.exit('-- Error: None of the expected folders were detected in the calibration folder. Please provide the -45 and +45 folders for a D90 calibration or the static folder for a calibration without rotation')
        
        if ('-45' not in list_dirs or '+45' not in list_dirs) \
            and 'static' not in list_dirs:
            sys.exit('-- Error: Only one of the -45 and +45 folders was provided for the D90 calibration. Please include both folders')
    
        if ('-45' in list_dirs or '+45' in list_dirs) \
            and 'static' in list_dirs:
            sys.exit('-- Error: Folders for more that one calibration technique were provided. Please keep either the -45 and +45 folders for a D90 calibration or the static folder for a calibration without rotation')
     
        if not 'dark' in list_dirs:
            print('-- Warning: No dark folder detected for the polarization calibration. The generated files will not be compatible with the ATLAS software!')
    
        if any(dir_i not in allowed_folders for dir_i in list_dirs):
            sys.exit(f'-- Error: The ./calibration folder contains at least one directory that is different from the expected ones ({allowed_folders}). Please make sure only the allowed directories exist there')

    return()