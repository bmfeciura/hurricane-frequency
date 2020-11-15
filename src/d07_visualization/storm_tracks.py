#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Sep 11 10:30:12 2020

@author: benjaminfeciura
"""

# import storm_tracks as trk #


import os, sys
import cartopy
import matplotlib.pyplot as plt

root_dir = os.path.join(os.getcwd(), "..")
sys.path.append(root_dir)

import pandas as pd

PROJECTION = cartopy.crs.NearsidePerspective(central_longitude = -55, central_latitude = 30,  satellite_height = 10000000)

POSITIONS = pd.read_csv('../data/02_intermediate/Atlantic_positions.csv')
STORMS = pd.read_csv('../data/02_intermediate/Atlantic_storms.csv')

def track_lat(stormID, positions_df = POSITIONS):
    return(positions_df['lat'][positions_df['stormID'] == stormID].tolist())

def track_lon(stormID, positions_df = POSITIONS):
    return(positions_df['lon'][positions_df['stormID'] == stormID].tolist())

def winds(stormID, positions_df = POSITIONS):
    ts_ne = positions_df['extNE34'][positions_df['stormID'] == stormID].tolist()
    ts_se = positions_df['extSE34'][positions_df['stormID'] == stormID].tolist()
    ts_sw = positions_df['extSW34'][positions_df['stormID'] == stormID].tolist()
    ts_nw = positions_df['extNW34'][positions_df['stormID'] == stormID].tolist()
    
    hu_ne = positions_df['extNE64'][positions_df['stormID'] == stormID].tolist()
    hu_se = positions_df['extSE64'][positions_df['stormID'] == stormID].tolist()
    hu_sw = positions_df['extSW64'][positions_df['stormID'] == stormID].tolist()
    hu_nw = positions_df['extNW64'][positions_df['stormID'] == stormID].tolist()
    
    status = positions_df['status'][positions_df['stormID'] == stormID].tolist()
    
    return([status, ts_ne, ts_se, ts_sw, ts_nw, hu_ne, hu_se, hu_sw, hu_nw])

def plot_season_summary(year, positions_df = POSITIONS, storms_df = STORMS, export = False, fullcolor = False):
    fig = plt.figure(figsize=(10,10))
    ax = plt.axes(projection = PROJECTION)
    ax.set_global()
    ax.coastlines(color = "black")
    if fullcolor:    
        ax.stock_img()
    plt.title(f"{year} Atlantic Hurricane Season Summary", fontsize = 20)

    for stormID in storms_df['stormID'][storms_df['year'] == year]:
        lat, lon = track_lat(stormID, positions_df), track_lon(stormID, positions_df)
        ax.plot(lon, lat, transform = cartopy.crs.PlateCarree(), c = "red")
        
    if export:
        fig.savefig(f"../results/images/{year}summary.jpg")
        
def plot_storm_track(stormID, positions_df = POSITIONS, storms_df = STORMS, global_view = False, export = False, fullcolor = False):
    if stormID == None:
        return
    
    storm = storms_df[storms_df['stormID']== stormID]
    name = storm['name'].to_string(index = False).strip()
    year = storm['year'].to_string(index = False).strip()
    
    fig = plt.figure(figsize=(10,10))
    ax = plt.axes(projection = PROJECTION)
    if global_view:
        ax.set_global()
    ax.coastlines()
    if fullcolor:
        ax.stock_img()
    plt.title(f"Track for {name} ({year})", fontsize = 20)
    
    ax.plot(track_lon(stormID, positions_df), track_lat(stormID, positions_df), transform = cartopy.crs.PlateCarree(), c = "red")
    
    if export:
        fig.savefig(f"../results/images/{name}{year}track.jpg")
        
        
def stormID(name, year, storms_df = STORMS):
    name = name.upper()
    match = storms_df[(storms_df['name'] == name) & (storms_df['year'] == year)]
    
    if len(match.index) == 0:
        print("Storm not found.")
        return None
    if len(match.index) > 1:
        print("Found multiple results.")
        print(match['stormID'])
        return None
    
    stormID = match['stormID'].to_string(index = False).strip()
    return stormID