#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jul 26 15:22:31 2022

@author: nick
"""

import numpy as np

def channels(cfg, sig, shots):
    
    """Removes channels that should be excluded according to the configuration 
    file (marked with _)"""
    
    if len(cfg.channels) > 0 and len(sig) > 0:
        ch_list = cfg.channels.index.values[np.where(cfg.channels.channel_id.values != '_')[0]]
    
        cfg.channels = cfg.channels.loc[ch_list,:]
        
        cfg.channels[cfg.channels == '_'] = np.nan
        
        sig = sig.loc[dict(channel = ch_list)] 
        shots = shots.loc[dict(channel = ch_list)] 
        
    return(cfg, sig, shots)
