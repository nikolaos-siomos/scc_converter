"""
@authors: Nikolaos Siomos (nikolaos.siomos@lmu.de)

================
General:
    Parses the command line arguments provided when calling __main_ 
    The information is stored in a python dictionary
    
Returns:
    
    args:
        A dictionary with all the information provided as command line arguments
        
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
                        help='The path to the parent folder that contains the normal folder and all other optional input folders (dark, atmosphere, overlap). If no results folder is provided, it will be exported here by default')

    parser.add_argument('-r', '--results_folder', metavar='results_folder', 
                        type=str, nargs='+', 
                        help='The path to the results folder. This optional argument can be used if the results folder must be placed out of the parent_folder (default)')

    parser.add_argument('-d', '--debug', metavar='debug', 
                        type=bool, nargs='+', 
                        help='If set to True then debugging files will be generated in ./results/debug folder. These included the metadata gathered from the configuration file, the licel header, and the combination of the two. Default to False ')
        
    parser.add_argument('-c', '--config_file', metavar='config_file', 
                        type=str, nargs='+', 
                        help='The path to the configuration file that contains the necessary metadata. This optional argument can be used if the settings folder must be placed out of the parent_folder (default)')            

    parser.add_argument('-s', '--radiosonde_filename', metavar='radiosonde_filename', 
                        type=str, nargs='+', 
                        help='Corresponding radiosonde filename. Use mode A in order to automatically include it by processing both rayleigh and radiosonde folders. Providing it as an argument will override the automatic detection with mode A')            

    parser.add_argument('-l', '--rayleigh_filename', metavar='rayleigh_filename', 
                        type=str, nargs='+', 
                        help='Corresponding rayleigh filename. Mandatory to provid when processing a depolarization calibration measurement. Use mode A in order to automatically include it by processing both rayleigh and calibration folders. Providing it as an argument will override the automatic detection with mode A')          

    parser.add_argument('-P', '--ground_pressure', metavar='ground_pressure', 
                        type=str, nargs='+', 
                        help='The atmospheric pressure in the lidar station in hPa. Defaults to 1013hPa')            

    parser.add_argument('-T', '--ground_temperature', metavar='ground_temperature', 
                        type=str, nargs='+', 
                        help='The atmospheric temperature in the lidar station in K. Defaults to 293.15 K')            

    parser.add_argument('-n', '--files_per_sector', metavar='files_per_sector', 
                        type=int, nargs='+', 
                        help='The number of telecover files per sector. If this values is provided for a telecover measurement all telecover measurements must be placed into the telecover folder inside the parent folder')            
    
    parser.add_argument('-i', '--measurement_identifier', metavar='measurement_identifier', 
                        type=str, nargs='+', 
                        help="Licel files usually start with a 1 or 2 character long pattern. Set the measurement_code to match this patern in order to read only files starting with it. Defaults to an empty string.")   

    parser.add_argument('-F', '--file_format', metavar='file_format', 
                        type=str, nargs='+', 
                        help="Raw file format.  Currently only licel is supported and polly_xt is being prepared. Defaults to 'licel'.")   
         
    parser.add_argument('-M', '--mode', metavar='mode', 
                        type=str, nargs='+', 
                        help="The processing mode. Select between A: Automated, R: Rayleigh, T: Telecover, C: Polarization Calibration, D: Standalone Dark, S: Radiosond. Defaults to A. By using A the algorithm will process all available measurements. Use an option other than A to process only measurements of the specific type!")   

    parser.add_argument('--rsonde_skip_header', metavar='rsonde_skip_header', 
                        type=int, nargs='+', 
                        help="Number of lines to skip at the beginning of the radiosonde file. Defaults to 1 (1 line reserved for header info)")   
                  
    parser.add_argument('--rsonde_skip_footer', metavar='rsonde_skip_footer', 
                        type=int, nargs='+', 
                        help="Number of lines to skip at the end of the radiosonde file. Defaults to 0 (no footer assumed)")   

    parser.add_argument('--rsonde_delimiter', metavar='rsonde_delimiter', 
                        type=str, nargs='+', 
                        help="The dilimiter that separates columns in the radiosonde file choose one of S: space, C: comma. Defaults to S!")   
    
    parser.add_argument('--rsonde_column_index', metavar='rsonde_delimiter', 
                        type=int, nargs='+', 
                        help="The column number of Height, Pressure, Temperature, and Relative Humidity (optional) columns in the radiosonde file. For example: --rsonde_columns 1 3 2 6 means height: 1st column, temperature: 3rd column, pressure: 2nd column, relative humidity: 6th column. The relative humidity column is OPTIONAL and can be omitted! Defaults to 1 2 3")   
                                                              
    parser.add_argument('--rsonde_geodata', metavar='rsonde_geodata', 
                        type=float, nargs='+', 
                        help="The radiosonde station latitude, longitude, and altitude. Mandatory if the mode is set to S. For example: --rsonde_geodata 40.5 22.9 60.0 ")   


    args = vars(parser.parse_args())
    
    mandatory_args = ['parent_folder']

    scalar_args = ['parent_folder','results_folder', 'debug', 'config_file',
                   'radiosonde_filename', 'rayleigh_filename', 
                   'ground_pressure', 'ground_temperature', 'files_per_sector',
                   'measurement_identifier', 'file_format', 'mode',
                   'rsonde_skip_header', 'rsonde_skip_footer', 'rsonde_delimiter']
    
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

    optional_args = ['results_folder', 'debug', 'config_file',
                     'radiosonde_filename', 'rayleigh_filename', 
                     'ground_pressure', 'ground_temperature',
                     'files_per_sector', 'measurement_identifier', 'file_format',
                     'mode', 'rsonde_skip_header', 'rsonde_skip_footer', 
                     'rsonde_delimiter', 'rsonde_column_index', 'rsonde_geodata']
    
    default_values = [os.path.join(args['parent_folder'],'results'), False,
                      os.path.join(args['parent_folder'],'config_file.ini'),
                      None, None, 1013., 293.15, None, '', 'licel', 'A',
                      1, 0, 'S', [1, 2, 3, None], [None, None, None]]
    
    print("-------------------------------------------------------------------")
    print("-- Warning: The following default values have been used!")
    print("-------------------------------------------------------------------")
    for i in range(len(optional_args)):
        if not args[optional_args[i]]:
            args[optional_args[i]] = default_values[i]
            print(f"{optional_args[i]} = {args[optional_args[i]]}")
    print("-------------------------------------------------------------------")
            
    if not os.path.exists(args['config_file']):
        sys.exit(f"-- Error: Path to the configuration file does not exists (defaults to <parent_folder>/config_file.ini). Path: {args['config_file']}!")  

    if not os.path.exists(args['results_folder']):
        os.makedirs(args['results_folder'])

    if args['debug'] not in [True, False]:
        sys.exit(f"-- Error: debug field should be boolean. Please use one of {[True, False]} with: -d <debug>")
        
    if not os.path.exists(os.path.join(args['results_folder'],'debug')) and args['debug']:
        os.makedirs(os.path.join(args['results_folder'],'debug'))

    if args['file_format'] not in ['licel', 'polly_xt']:
        sys.exit(f"-- Error: file_format field not recognized. Please use one of {['licel', 'polly_xt']} with: -F <file_format>")
    
    if args['mode'] not in ['A', 'R', 'T', 'C', 'D', 'S']:
        sys.exit(f"-- Error: mode field not recognized. Please revise the settings file and use one of {['A', 'R', 'T', 'C', 'D', 'S']} with: -M <mode>")

    if len(args['rsonde_column_index']) not in [3, 4]:
        sys.exit("-- Error: rsonde_column_index field has less or more elements than expected. Please provide 3 or 4 integer eg: --rsonde_column_index 1 2 3")

    if len(args['rsonde_geodata']) != 3:
        sys.exit("-- Error: rsonde_geodata field has less or more elements than expected. Please provide 3 floats that correspond to the radiosonde station latitude, longitude, and altitude eg: --rsonde_geodata 40.5 22.9 60.0")
            
    if any([not geodata_i for geodata_i in args['rsonde_geodata']]) and args['mode'] == 'S':
        sys.exit("-- Error: The rsonde_geodata field is mandatory when processing a radiosonde file (mode = S). Please provide 3 floats that correspond to the radiosonde station latitude, longitude, and altitude eg: --rsonde_geodata 40.5 22.9 60.0")
            
    return(args)
