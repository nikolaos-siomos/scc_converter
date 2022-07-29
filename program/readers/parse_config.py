"""
Created on Sun May 17 21:06:52 2020

@author: nick
"""

import argparse
import os
import sys

def parse_config():
        
    """Collects the information included as commandline arguments. 
    Current mandatory arguments: --parent_folder [-f]"""
    
    parser = argparse.ArgumentParser(
    	description='arguments ')
    
    parser.add_argument('-f', '--parent_folder', metavar='parent_folder', 
                        type=str, nargs='+', 
                        help='The path to the parent folder that contains the normal folder and all other optional input folders (dark, atmosphere, overlap). If no results and/or plots folders are provided, everything will be exported here by default')

    parser.add_argument('-r', '--results_folder', metavar='results_folder', 
                        type=str, nargs='+', 
                        help='The path to the results folder. This optional argument can be used if the results folder must be placed out of the parent_folder (default)')

    parser.add_argument('-p', '--plots_folder', metavar='plots_folder', 
                        type=str, nargs='+', 
                        help='The path to the plots folder. This optional argument can be used if the results folder must be placed out of the parent_folder (default)')
        
    parser.add_argument('-c', '--config_file', metavar='config_file', 
                        type=str, nargs='+', 
                        help='The path to the configuration file that contains the necessary metadata. This optional argument can be used if the settings folder must be placed out of the parent_folder (default)')            

    parser.add_argument('-m', '--molec_calc', metavar='molec_calc', 
                        type=str, nargs='+', 
                        help='Calculation method of the molecular atmosphere. Use 4 to use the US Standard Atmosphere 1976 or 1 if a radiosonde or model file is provided. Defaults to 4')            

    parser.add_argument('-s', '--radiosonde_file', metavar='radiosonde_file', 
                        type=str, nargs='+', 
                        help='Path to the radiosonde file. Has to be provided if molec_calc is set to 1 or 2')            

    parser.add_argument('-P', '--ground_pressure', metavar='ground_pressure', 
                        type=str, nargs='+', 
                        help='The atmospheric pressure in the lidar station in hPa. Defaults to 1013hPa')            

    parser.add_argument('-T', '--ground_temperature', metavar='ground_temperature', 
                        type=str, nargs='+', 
                        help='The atmospheric temperature in the lidar station in K. Defaults to 293.15 K')            

    parser.add_argument('-n', '--files_per_sector', metavar='files_per_sector', 
                        type=int, nargs='+', 
                        help='The number of telecover files per sector. If this values is provided for a telecover measurement all telecover measurements must be placed into the telecover folder inside the parent folder')            


    args = vars(parser.parse_args())
    
    mandatory_args = ['parent_folder']

    scalar_args = ['parent_folder','results_folder','plots_folder','config_file', 'molec_calc', 'ground_pressure', 'ground_temperature', 'files_per_sector']
    
    mandatory_args_abr = ['-f']
    
    for i in range(len(mandatory_args)):
        if not args[mandatory_args[i]]:
            print(f'-- Error: The mandatory argument {mandatory_args[i]} is not provided! Please provide it with: {mandatory_args_abr[i]} <path>')
            sys.exit('-- Program stopped')            

    for i in range(len(scalar_args)):
        if isinstance(args[scalar_args[i]],list):
            if len(args[scalar_args[i]]) > 1:
                print(f'-- Error: More than one objects provided for argument {scalar_args[i]}!')
                sys.exit('-- Program stopped')
            if len(args[scalar_args[i]]) == 1:
                args[scalar_args[i]] = args[scalar_args[i]][0]    

    optional_args = ['results_folder','plots_folder','config_file',
                     'molec_calc', 'ground_pressure', 'ground_temperature',
                     'files_per_sector']
    default_values = [os.path.join(args['parent_folder'],'results'), 
                      os.path.join(args['parent_folder'],'plots'),
                      os.path.join(args['parent_folder'],'config_file.ini'),
                      4, 1013., 293.15, None]
    
    print("-------------------------------------------------------------------")
    print("-- Warning: The following default values have been used!")
    print("-------------------------------------------------------------------")
    for i in range(len(optional_args)):
        if not args[optional_args[i]]:
            args[optional_args[i]] = default_values[i]
            print(f"{optional_args[i]} = {args[optional_args[i]]}")
    print("-------------------------------------------------------------------")

    
    if not args['radiosonde_file'] and args['molec_calc'] == 1:
        print("-- Error: molec_calc is set to 1 (indicating a radiosonde file) but the radiosonde filename is not provided! Please provide it with: -s <radiosonde_filename>'")               
        sys.exit('-- Program stopped')  
    if not os.path.exists(args['config_file']):
        print(f"-- Error: Path to the configuration file does not exists (defaults to <parent_folder>/config_file.ini). Path: {args['config_file']}!")
        sys.exit('-- Program stopped')  
    if not (args['molec_calc'] == 1 or args['molec_calc'] == 4):
        print("-- Error: molec_calc can be only 1 or 4, please provide a correct value with: -m <molec_calc>!")
        sys.exit('-- Program stopped')  

    
    return(args)