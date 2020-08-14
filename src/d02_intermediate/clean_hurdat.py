#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Aug 13 18:59:47 2020

@author: benjaminfeciura
"""

import os, sys
import pandas as pd

root_dir = os.path.join(os.getcwd(), '..')
sys.path.append(root_dir)


"""
PARTITION_HURDAT
"""

# HURDAT files come with header and data rows mixed together.
# This function separates the raw HURDAT file {fn}.csv into two more workable
#   CSV files, {fn}_positions.csv and {fn}_storms.csv
def partition_hurdat(fn):
    
    import os, sys
    import pandas as pd

    root_dir = os.path.join(os.getcwd(), '..')
    sys.path.append(root_dir)
    
    """
    Import the HURDAT file and replace the column names for readability
    """
    
    fn_no_ext = os.path.splitext(fn)[0]

    # create a list to contain our new column names (provided by HURDAT
    #   documentation)
    header = ['date', 'time', 'recordID', 'status', 'lat', 'long', 'maxSustWind', 'minPressure', 'extNE34', 'extSE34', 'extSW34', 'extNW34', 'extNE50', 'extSE50', 'extSW50', 'extNW50', 'extNE64', 'extSE64', 'extSW64', 'extNW64']


    # import the HURDAT file from raw data folder using our column names
    hurdat = pd.read_csv(f'../data/01_raw/{fn}', names = header)
    
    
    # remove our temporary header from the download process and reset the index 
    hurdat.drop(index = 0, inplace = True)
    hurdat.reset_index(drop=True, inplace=True)

  
    """
    Determine which rows are Header rows
    """
    
    
    # create list to be used as new column hurdat['header']
    header = [] 


    # Flag header rows by exploiting the fact that all header rows,
    #   and only header rows, contain 'AL' or 'EP'/'CP', in the Atlantic
    #   and Eastern/Central Pacific datasets, respectively
    for entry in hurdat['date']:
        if entry.find('AL') != -1: 
            header.append(True)
        elif entry.find('EP') != -1: 
            header.append(True)
        elif entry.find('CP') != -1: 
            header.append(True)
        else:
            header.append(False)
 
    
    # add the list as a pandas series into a column of hurdat dataFrame
    hurdat['header'] = pd.Series(header) 


    """
    Create dataframes of only storm names and only position data
        so we can edit the columns and dtypes   
    """
    
    
    # all header columns of atl copied into new dataframe storms
    storms = hurdat[hurdat['header'] == True].copy() 
    
    
    # all data columns of atl copied into new dataframe positions
    positions = hurdat[hurdat['header'] == False].copy()
    
    
    """
    For the storms dataFrame, we need to remove unnecessary columns, 
        rename existing columns, create a new year column, and assign 
        the correct dtypes to all columns
    """


    # drop unnecessary columns, rename remaining columns, and clean up indices
    storms.drop(['status', 'lat', 'long', 'maxSustWind', 'minPressure', 'extNE34', 'extSE34', 'extSW34', 'extNW34', 'extNE50', 'extSE50', 'extSW50', 'extNW50', 'extNE64', 'extSE64', 'extSW64', 'extNW64', 'header'], axis = 1, inplace = True)
    storms.columns = ['stormID', 'name', 'numPositions']
    storms.reset_index(drop=True, inplace=True)


    # column names are as follows:
    #
    # 'stormID': an individual identifier for each storm in the form 
    #   ALXXYYYY or EPXXYYYY denoting the storm was the XXth storm
    #   of (A)t(L)antic or (E)astern (P)acific Hurricane Season YYYY. 
    #   Useful when storms in different years share the same name, and 
    #   for unnamed storms.
    # 'name': name of storm.
    # 'numPositions': the number of position entries in positions dataFrame 
    #   corresponding to this storm
    

    # create a new list to be used as a numeric years column
    stormYears = [] 


    # strip out the year from the stormID.
    # note that this year may not necessarily correspond to the calendar 
    #   dates during which the storm existed, but rather the Hurricane 
    #   Season to which it belonged.
    for stormID in storms['stormID']:
        stormYears.append(stormID[4:9]) 
    
    
    # assign new year column as integer dtype
    storms['year'] = pd.Series(stormYears).astype('int') 
    # reassign number of positions integer dtype
    storms['numPositions'] = storms['numPositions'].astype('int') 
    # reassign storm names string dtype and strip whitespace
    storms['name'] = storms['name'].astype('str').str.strip() 
    # reassign stormID string dtype and strip whitespace
    storms['stormID'] = storms['stormID'].astype('str').str.strip()
    
    
    """
    For the positions dataFrame we need to clean up the indices, reformat the 
        latitude and longitude columns to make them usable by matplotlib.pyplot, 
        create new columns for the storm name and stormId to make the 
        dataframe searchable by these criteria
    """


    # clean up the indices
    positions.reset_index(drop=True, inplace=True)

    # we can convert the latitude and longitude information into integers 
    #   by removing the cardinal direction.
    # we can instead write XX.XW as -XX.X and XX.XE as XX.X.
    # we can also write XX.XN as XX.X and XX.XS as -XX.X.


    # create lists to be used as new series for latitude and longitude
    intLat = []  
    intLong = []
        
    
    # iterate through each latitude in the existing cardinal direction format
    for cardLat in positions['lat']:
        # for latitudes of degrees north, strip the whitespace and N
        if cardLat.find('N') != -1: 
            intLat.append(cardLat.strip(" N"))
        # for latitudes of degrees south, strip the whitespace and S, 
        #   and add a negative to the front
        else: 
            intLat.append('-'+cardLat.strip(" S"))
    
    # iterate through each longitude in the existing cardinal direction format
    for cardLong in positions['long']:
        #for longitudes of degrees east, strip the whitespace and E
        if cardLong.find('E') != -1: 
            intLong.append(cardLong.strip(" E"))
        # for longitudes of degrees west, strip the whitespace and W, 
        #   and add a negative to the front
        else: 
            intLong.append('-'+cardLong.strip(" W"))

        
    # replace the existing longitude and latitude columns with the new ones
    positions['lat'] = pd.Series(intLat).astype('float')
    positions['long'] = pd.Series(intLong).astype('float')
    
    
    # use the provided number of position updates for each storm to create 
    #   a column for the positions dataframe containing the appropriate names
    #   (to make entries searchable by name)


    # create a list to be used as the names column for the positions dataFrame
    stormNames = [] 


    # for each storm in the storms dataFrame...
    for i in range(len(storms)): 
        # for the number of rows indicated, add the storm name to the list
        for j in range(storms['numPositions'][i]): 
            stormNames.append(storms['name'][i])
        
        
    # add the new list containing a name for every row of positions 
    #  into positions dataFrame  
    positions['name'] = pd.Series(stormNames)


    # repeat the process for storm IDs
    stormIDs = []

    for i in range(len(storms)):
        for j in range(storms['numPositions'][i]):
            stormIDs.append(storms['stormID'][i])
           
    positions['stormID'] = pd.Series(stormIDs)
    
    # remove the now unnecessary header column
    positions.drop(columns="header", inplace = True)
    
    # now we can save "storms" and "positions" to new csv files in data/02_intermediate

    positions_fn = ( fn_no_ext + "_positions.csv" )
    positions.to_csv(f"../data/02_intermediate/{positions_fn}")

    storms_fn = ( fn_no_ext + "_storms.csv" )
    storms.to_csv(f"../data/02_intermediate/{storms_fn}")

    print(f"Partitioned {fn} into:\n /data/02_intermediate/{positions_fn}\n /data/02_intermediate/{storms_fn}")
    
    return
