#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Aug 13 18:59:47 2020

@author: benjaminfeciura
"""

# import clean_hurdat as clh


# HURDAT files come with header and data rows mixed together.
# This function separates the raw HURDAT file {fn}.csv into two more workable
#   CSV files, {fn}_positions.csv and {fn}_storms.csv
def partition_hurdat(fn):
    
    import os
    import pandas as pd

    # These steps will apply both to Atlantic and Pacific datasets, so when
    # we ultimately convert these steps into a function we'll allow the
    # user to provide a filename. The function will always search in the
    # raw data directory, so the filename alone will differentiate between
    # the raw datasets.
    
    # We're going to save the two new datasets that result from splitting
    # the HURDAT file as separate files, so we'll use os.path.splitext to 
    # separate the filename and extension for the raw data, then store the
    # filename to use in appropriately naming the resulting files.
    fn_no_ext = os.path.splitext(fn)[0]

    # This list of column names applies to the position data rows.
    header = ['date', 'time', 'recordID', 'status', 'lat', 'lon', 'maxSustWind', 'minPressure', 'extNE34', 'extSE34', 'extSW34', 'extNW34', 'extNE50', 'extSE50', 'extSW50', 'extNW50', 'extNE64', 'extSE64', 'extSW64', 'extNW64']

    # Import data from raw data folder using our column names.
    hurdat = pd.read_csv(f'../data/01_raw/{fn}', names = header)
        

    # We need to determine which rows go in which new DataFrame, so create
    # a list that can be turned into a series and added as a new column.
    header = []
   
    # If there are only numeric characters in the date column, this is
    # a position row. Otherwise, flag the row as being a header row.
    for entry in hurdat['date']:
        if entry.isnumeric():
            header.append(False)
        else:
            header.append(True)
   
    # Cast the list as a pandas series and add it as a column of DataFrame.
    hurdat['header'] = pd.Series(header) 
    
    # Create DataFrames of only header rows and only position data so we 
    # can prepare each appropriately.
    storms = hurdat[hurdat['header'] == True].copy() # All header columns of atl copied into new dataframe storms.
    positions = hurdat[hurdat['header'] == False].copy() # All data columns of atl copied into new dataframe positions.
    

    # Storms DataFrame:
    # Drop unnecessary columns, including the column indicating header rows.
    storms.drop(['status', 'lat', 'lon', 'maxSustWind', 'minPressure', 'extNE34', 'extSE34', 'extSW34', 'extNW34', 'extNE50', 'extSE50', 'extSW50', 'extNW50', 'extNE64', 'extSE64', 'extSW64', 'extNW64', 'header'], axis = 1, inplace = True)
    # Rename remaining columns.
    storms.columns = ['stormID', 'name', 'numPositions']
    # Reset indices to fill in gaps from position rows.
    storms.reset_index(drop=True, inplace=True)

    # We're going to want storms to easily be subsettable by years, so we'll
    # create a new numeric column for it and fill the entries by parsing 
    # the entries of the stormID column.
    stormYears = []
    
    # We can pull out the year easily since all the stormIDs share the same
    # format. Note that this year corresponds to the storm season, but
    # that it is possible under rare circumstances for storms to
    # persist into the following year so the dates on position entries may
    # not always show the year presented here.
    for stormID in storms['stormID']:
        stormYears.append(stormID[4:9]) 
        
    # Assign new year column integer dtype.
    storms['year'] = pd.Series(stormYears).astype('int') 
    # Reassign number of positions integer dtype.
    storms['numPositions'] = storms['numPositions'].astype('int')
    # Strip whitespace from name and stormID values.
    storms['name'] = storms['name'].astype('str').str.strip() 
    storms['stormID'] = storms['stormID'].astype('str').str.strip()


    # Positions DataFrame:
    # Reset the index.
    positions.reset_index(drop=True, inplace=True)
    
    # Create lists to be used as new series for latitude and longitude. 
    numLat = [] 
    numLon = []
    
    for cardLat in positions['lat']:
        if cardLat.find('N') != -1: 
            # For latitudes of degrees North, strip the whitespace and N.
            numLat.append(cardLat.strip(" N"))
        else: 
            # For latitudes of degrees South, strip the whitespace and S 
            # and make the value negative.
            numLat.append('-'+cardLat.strip(" S"))
    
    for cardLon in positions['lon']:
        if cardLon.find('E') != -1: 
            # For longitudes of degrees East, strip the whitespace and E.
            numLon.append(cardLon.strip(" E"))
        else: 
            # For longitudes of degrees West, strip the whitespace and W 
            # and make the value negative.
            numLon.append('-'+cardLon.strip(" W"))
     
    # Replace the existing longitude and latitude columns with the new ones.
    positions['lat'] = pd.Series(numLat).astype('float')
    positions['lon'] = pd.Series(numLon).astype('float')
    
    
    # Add storm names and stormIDs to positions DataFrame:
    # Create a list to be used as the names column in this DataFrame
    stormNames = [] 
        
    # For each storm in the storms DataFrame...
    for i in range(len(storms)): 
        # For the number of rows indicated, add the storm name to the list.
        for j in range(storms['numPositions'][i]): 
            stormNames.append(storms['name'][i])
               
    # And create the new column using the list.      
    positions['name'] = pd.Series(stormNames)
                
    # Repeat the process for storm IDs
    stormIDs = []
                
    for i in range(len(storms)):
        for j in range(storms['numPositions'][i]):
            stormIDs.append(storms['stormID'][i])
              
    positions['stormID'] = pd.Series(stormIDs)

    # Remove the unnecessary header indicator column.
    positions.drop(columns="header", inplace = True)
    
    # Create a column in the storms dataset with the month formed
    month_formed = []

    positions["date"] = pd.to_datetime(positions["date"], format = "%Y%m%d")

    for stormID in storms["stormID"]:
        
        months = positions[positions["stormID"] == stormID]["date"].dt.month
        monthslist = months.tolist()
        month_formed.append(monthslist[0])

    storms["month_formed"] = pd.Series(month_formed)
    

    # Export to files and notify the user:
    # We'll use the filename we stored after removing the extension earlier
    # to create the child files in the new directory.
    positions_fn = ( fn_no_ext + "_positions.csv" )
    positions.to_csv(f"../data/02_intermediate/{positions_fn}", index = False)

    storms_fn = ( fn_no_ext + "_storms.csv" )
    storms.to_csv(f"../data/02_intermediate/{storms_fn}", index = False)

    # Verify for the user which files were created.
    print(f"Partitioned {fn} into:\n /data/02_intermediate/{positions_fn}\n /data/02_intermediate/{storms_fn}")
    
    return

