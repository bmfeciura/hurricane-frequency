#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct  5 22:41:10 2020

@author: benjaminfeciura
"""

# Purpose of module: to produce numpy arrays containing frequencies with which
# 1x1 degree grid spaces experience storm conditions.

# Can be passed into the heatmap function in visualization or saved as a csv
# for use in modeling.

import os, sys
import pandas as pd

root_dir = os.path.join(os.getcwd(), '..')
sys.path.append(root_dir)

import numpy as np
import math as m
import cartopy.crs as ccrs
from src.d07_visualization import storm_tracks as trk


RADIUS = 3440.1

PROJECTION = ccrs.NearsidePerspective(central_longitude = -55, central_latitude = 30,  satellite_height = 10000000)

POSITIONS = pd.read_csv('../data/02_intermediate/Atlantic_positions.csv')
STORMS = pd.read_csv('../data/02_intermediate/Atlantic_storms.csv')

ne_brngs = np.linspace(0, 90, 31)
se_brngs = np.linspace(90, 180, 31)
sw_brngs = np.linspace(180, 270, 31)
nw_brngs = np.linspace(270, 360, 31)
brngs = [ne_brngs, se_brngs, sw_brngs, nw_brngs]


def wind_frequency(stormlist = STORMS['stormID'][STORMS['year'] >= 2004], positions_df = POSITIONS, hu_only = False):
    
    cumulative_winds = np.zeros((180, 360))

    for storm in stormlist:
        storm_lats = trk.track_lat(storm, positions_df = positions_df)
        storm_lons = trk.track_lon(storm, positions_df = positions_df)
        storm_winds = trk.winds(storm, positions_df = positions_df)

        storm_history = np.zeros((180, 360))

        for x in range(len(storm_lats)):
    
            lat = storm_lats[x]
            lon = storm_lons[x]
            rlat = lat*(m.pi/180)
            rlon = lon*(m.pi/180)

            trext = [storm_winds[1][x], storm_winds[2][x], storm_winds[3][x], storm_winds[4][x]]
            huext = [storm_winds[5][x], storm_winds[6][x], storm_winds[7][x], storm_winds[8][x]]
    
            if (-999) in trext:
                continue
            if (-999) in huext:
                continue

            if hu_only:

                if storm_winds[0][x] == ' HU':
    
                    for quad in range(4):
    
                        dist = huext[quad] / RADIUS
   
                        for i in brngs[quad]:
                            brng = i * (m.pi/180)
                            dlat = m.asin(m.sin(rlat)*m.cos(dist) + m.cos(rlat)*m.sin(dist)*m.cos(brng))
                            dlon = rlon + m.atan2(m.sin(brng)*m.sin(dist)*m.cos(rlat), m.cos(dist)-m.sin(rlat)*m.sin(dlat))
    
                            dlat *= (180/m.pi)
                            dlon *= (180/m.pi)
                            if dlon < -180:
                                dlon += 360
                            elif dlon > 180:
                                dlon -= 360
        
                            if quad  in [0, 3]:
                                for y in range((90 + m.floor(lat)), (90 + m.ceil(dlat))):
                                    storm_history[y][180 + m.floor(dlon)] = 2
                    
                            elif quad in [1, 2]:
                                for y in range((90 + m.floor(dlat)), (90 + m.ceil(lat))):
                                    storm_history[y][180 + m.floor(dlon)] = 2

            else:

                if storm_winds[0][x] in [' TS', ' HU']:
    
                    for quad in range(4):
    
                        dist = trext[quad] / RADIUS
   
                        for i in brngs[quad]:
                            brng = i * (m.pi/180)
                            dlat = m.asin(m.sin(rlat)*m.cos(dist) + m.cos(rlat)*m.sin(dist)*m.cos(brng))
                            dlon = rlon + m.atan2(m.sin(brng)*m.sin(dist)*m.cos(rlat), m.cos(dist)-m.sin(rlat)*m.sin(dlat))
    
                            dlat *= (180/m.pi)
                            dlon *= (180/m.pi)
                            if dlon < -180:
                                dlon += 360
                            elif dlon > 180:
                                dlon -= 360
            
                            if quad in [0, 3]:
                                for y in range((90 + m.floor(lat)), (90 + m.ceil(dlat))):
                                    if (storm_history[y][180 + m.floor(dlon)] != 2):
                                        storm_history[y][180 + m.floor(dlon)] = 1
                                
                            elif quad in [1, 2]:
                                for y in range((90 + m.floor(dlat)), (90 + m.ceil(lat))):
                                    if (storm_history[y][180 + m.floor(dlon)] != 2):
                                        storm_history[y][180 + m.floor(dlon)] = 1
                                            
        
        cumulative_winds += storm_history
        
    return(cumulative_winds)


