"""
Created on Sun May 17 21:06:52 2020

@author: nick
"""

import argparse
import os
import sys

def parse_config():
        
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

    args = vars(parser.parse_args())
    
    mandatory_args = ['parent_folder']

    scalar_args = ['parent_folder','results_folder','plots_folder','config_file']
    
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

    if not args['results_folder']:
        args['results_folder'] = os.path.join(args['parent_folder'],'results')
    if not args['plots_folder']:
        args['plots_folder'] = os.path.join(args['parent_folder'],'plots')
    if not args['config_file']:
        args['config_file'] = os.path.join(args['parent_folder'],'config_file.ini')
        
    if not os.path.exists(args['config_file']):
        print(f"-- Error: Path to the configuration file does not exists (defaults to <parent_folder>/config_file.ini). Path: {args['config_file']}!")
        sys.exit('-- Program stopped')        
    
    return(args)