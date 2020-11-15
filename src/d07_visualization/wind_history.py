#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct  5 21:16:29 2020

@author: benjaminfeciura
"""

import os, sys
import pandas as pd

root_dir = os.path.join(os.getcwd(), '..')
sys.path.append(root_dir)

import numpy as np
import math as m
import cartopy.crs as ccrs
import matplotlib.pyplot as plt
from src.d07_visualization import storm_tracks as trk


RADIUS = 3440.1

PROJECTION = ccrs.NearsidePerspective(central_longitude = -55, central_latitude = 30,  satellite_height = 10000000)

POSITIONS = pd.read_csv('data/02_intermediate/Atlantic_positions.csv')
STORMS = pd.read_csv('data/02_intermediate/Atlantic_storms.csv')

def wind_history(stormID, positions_df = POSITIONS):
    # Get the list of all of our coordinates, as well as the lists of wind extents
    storm_lats = trk.track_lat(stormID)
    storm_lons = trk.track_lon(stormID)
    storm_winds = trk.winds(stormID, positions_df)
    
    # Create empty matrix
    wind_history = np.zeros((180, 360))

    # Construct list of bearings
    ne_brngs = np.linspace(0, 90, 31)
    se_brngs = np.linspace(90, 180, 31)
    sw_brngs = np.linspace(180, 270, 31)
    nw_brngs = np.linspace(270, 360, 31)
    brngs = [ne_brngs, se_brngs, sw_brngs, nw_brngs]
    
    # For each pair of coordinates in the storm's history
    for x in range(len(storm_lats)):
        
        # Get and convert to radians from the center coordinates.
        lat = storm_lats[x]
        lon = storm_lons[x]
        rlat = lat*(m.pi/180)
        rlon = lon*(m.pi/180)
        # Pull out the correct wind values
        trext = [storm_winds[1][x], storm_winds[2][x], storm_winds[3][x], storm_winds[4][x]]
        huext = [storm_winds[5][x], storm_winds[6][x], storm_winds[7][x], storm_winds[8][x]]
        # If wind extents are missing for this row, skip to the next row.
        if -999 in trext:
            continue
        if -999 in huext:
            continue
        
        # If the storm is at least a tropical storm
        if storm_winds[0][x] in [' TS', ' HU']:
            # Implement the formula for the tropical storm wind extents
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
                            # ONLY if the cell was not previously set to 2
                            if (wind_history[y][180 + m.floor(dlon)] != 2):
                                wind_history[y][180 + m.floor(dlon)] = 1

                    elif quad in [1, 2]:
                        for y in range((90 + m.floor(dlat)), (90 + m.ceil(lat))):
                            # ONLY if the cell was not previously set to 2
                            if (wind_history[y][180 + m.floor(dlon)] != 2):
                                wind_history[y][180 + m.floor(dlon)] = 1
                            
        # If the storm is a hurricane
        if storm_winds[0][x] == ' HU':
            # Implement the formula again for the hurricane wind extents
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
                            wind_history[y][180 + m.floor(dlon)] = 2
                    
                    elif quad in [1, 2]:
                        for y in range((90 + m.floor(dlat)), (90 + m.ceil(lat))):
                            wind_history[y][180 + m.floor(dlon)] = 2

    # Mask the zero values            
    wind_history_transparent = np.ma.masked_equal(wind_history, 0)

    # And plot the result
    projection = ccrs.NearsidePerspective(central_longitude = -55, central_latitude = 30,  satellite_height = 10000000)
    lon = np.linspace(-180, 180, 361) # changed from 179
    lat = np.linspace(-90, 90, 181) # changed from 89
    Lon, Lat = np.meshgrid(lon, lat)

    fig = plt.figure(figsize=(10,10))
    ax = plt.axes(projection = projection)
    ax.set_global()
    ax.coastlines()
    ax.pcolormesh(Lon, Lat, wind_history_transparent, transform = ccrs.PlateCarree())

    # Note: Tropical Storm Winds in Purple, Hurricane in Yellow

def heatmap(freq_array, export = False, dest_fn = "wind_history_heatmap"):
    
    freq_array_transparent = np.ma.masked_equal(freq_array, 0)
    
    projection = ccrs.NearsidePerspective(central_longitude = -55, central_latitude = 30,  satellite_height = 10000000)
    lon = np.linspace(-180, 180, 361) # changed from 179
    lat = np.linspace(-90, 90, 181) # changed from 89
    Lon, Lat = np.meshgrid(lon, lat)

    fig = plt.figure(figsize=(10,10))
    ax = plt.axes(projection = projection)
    ax.set_global()
    ax.coastlines()
    mesh = ax.pcolormesh(Lon, Lat, freq_array_transparent, transform = ccrs.PlateCarree())
    plt.colorbar(mesh)
    
    if export:
        fig.savefig(f"../results/images/{dest_fn}.jpg")
    
    return
    