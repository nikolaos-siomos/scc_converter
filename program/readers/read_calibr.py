"""
@author: P. Paschou
"""
import configparser
import numpy as np
import pandas as pd
from .read_config import comma_split, read_var

class config_calibr():
    
    def __init__(self, path):
        """Reads the calibration.ini file at the given path"""
        
        parser = configparser.ConfigParser()
        parser.read(path)
        
#D90    
        if parser.has_section('D90'):        
    
            self.range_d90 = comma_split(parser['D90']['range_d90'], float)
    
            self.ch_r_d90 = comma_split(parser['D90']['ch_r_d90'], str)
    
            self.ch_t_d90 = comma_split(parser['D90']['ch_t_d90'], str)
            
            self.rt_id_d90 = comma_split(parser['D90']['rt_id_d90'], str)
            
            self.nd_pos = pd.Series(data=comma_split(parser['D90']['nd_pos'], str),
                                    index = self.rt_id_d90, dtype = str)
            
            self.nd_val = pd.Series(data=comma_split(parser['D90']['nd_val'], float),
                                    index = self.rt_id_d90, dtype = float)

#Export
        if parser.has_section('Export'): 
    
            self.cfg_path_nrm = read_var(parser['Export']['cfg_path_nrm'], str)
            
            rt_id = comma_split(parser['Export']['rt_id'], str)
            G_R = comma_split(parser['Export']['G_R'], float)
            G_T = comma_split(parser['Export']['G_T'], float)
            H_R = comma_split(parser['Export']['H_R'], float)
            H_T = comma_split(parser['Export']['H_T'], float)
            K = comma_split(parser['Export']['K'], float)
            l_rot = comma_split(parser['Export']['l_rot'], float)
            y = comma_split(parser['Export']['y'], float)
    
            self.GHKprms = pd.DataFrame(data=np.vstack((G_R, G_T, H_R, H_T, K, l_rot, y)).T,
                                        index = rt_id,
                                        columns=['GR','GT','HR','HT','K','l_rot','y'],
                                        dtype=object)
        
#Ratios
        if parser.has_section('Ratios'):        
            self.range_rt = comma_split(parser['Ratios']['range'], float)

            self.ch_r_rt = comma_split(parser['Ratios']['ch_r'], str)
    
            self.ch_t_rt = comma_split(parser['Ratios']['ch_t'], str)
            
            self.rt_id_rt = comma_split(parser['Ratios']['rt_id'], str)
    
            self.cal_fact_rt = comma_split(parser['Ratios']['cal_fact'], float)

            self.nd_val_rt = pd.Series(data=comma_split(parser['Ratios']['nd_val'], float),
                                       index = self.rt_id_rt, dtype = float)

            self.nd_pos_rt = pd.Series(data=comma_split(parser['Ratios']['nd_pos'], str),
                                       index = self.rt_id_rt, dtype = str)
#Stokes
        if parser.has_section('Stokes'):        
            self.range_st = comma_split(parser['Stokes']['range'], float)

            self.ch_r_st = comma_split(parser['Stokes']['ch_r'], str)
    
            self.ch_t_st = comma_split(parser['Stokes']['ch_t'], str)
            
            self.rt_id_st = comma_split(parser['Stokes']['rt_id'], str)
    
            self.cal_fact_st = comma_split(parser['Stokes']['cal_fact'], float)

            # self.nd_val_st = comma_split(parser['Stokes']['nd_val'], float)
            self.nd_val_st = pd.Series(data=comma_split(parser['Stokes']['nd_val'], float),
                                       index = self.rt_id_st, dtype = float)

            # self.nd_pos_st = comma_split(parser['Stokes']['nd_pos'], str)
            self.nd_pos_st = pd.Series(data=comma_split(parser['Stokes']['nd_pos'], str),
                                       index = self.rt_id_st, dtype = str)

            self.DR_st = comma_split(parser['Stokes']['DR'], float)

            self.DT_st = comma_split(parser['Stokes']['DT'], float)
            
#Mueller
        if parser.has_section('Mueller'):        
            self.range_ml = comma_split(parser['Mueller']['range'], float)

            self.range_aux_ml = comma_split(parser['Mueller']['range_aux'], float)

            self.ch_r_ml = comma_split(parser['Mueller']['ch_r'], str)
    
            self.ch_t_ml = comma_split(parser['Mueller']['ch_t'], str)
            
            self.rt_id_ml = comma_split(parser['Mueller']['rt_id'], str)
    
            self.cal_fact_ml = comma_split(parser['Mueller']['cal_fact'], float)

            # self.nd_val_ml = comma_split(parser['Mueller']['nd_val'], float)
            self.nd_val_ml = pd.Series(data=comma_split(parser['Mueller']['nd_val'], float),
                                       index = self.rt_id_ml, dtype = float)

            # self.nd_val_aux_ml = comma_split(parser['Mueller']['nd_val_aux'], float)
            self.nd_val_aux_ml = pd.Series(data=comma_split(parser['Mueller']['nd_val_aux'], float),
                                       index = self.rt_id_ml, dtype = float)

            # self.nd_pos_ml = comma_split(parser['Mueller']['nd_pos'], str)
            self.nd_pos_ml = pd.Series(data=comma_split(parser['Mueller']['nd_pos'], str),
                                       index = self.rt_id_ml, dtype = str)            

            self.DR_ml = comma_split(parser['Mueller']['DR'], float)

            self.DT_ml = comma_split(parser['Mueller']['DT'], float)

            self.alpha_ml = comma_split(parser['Mueller']['alpha'], float)

            self.alpha_aux_ml = comma_split(parser['Mueller']['alpha_aux'], float)

            self.Q_ml = comma_split(parser['Mueller']['Q'], float)

            self.U_ml = comma_split(parser['Mueller']['U'], float)

            self.V_ml = comma_split(parser['Mueller']['V'], float)

            self.ems_rot_ml = comma_split(parser['Mueller']['ems_rot'], float)

            self.opt_ems_typ_ml = comma_split(parser['Mueller']['opt_ems_typ'], str)

            self.opt_ems_cor_ml = comma_split(parser['Mueller']['opt_ems_cor'], float)

# -------- END OF CLASS