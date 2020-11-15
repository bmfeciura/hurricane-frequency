#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

@author: benjaminfeciura
"""

# import data_download as ddln

import os
import pandas as pd

import requests
from bs4 import BeautifulSoup


# function to download atlantic hurdat data
def download_atlantic_hurdat_raw(dest_filename = "Atlantic"):
    
    URL = "https://www.nhc.noaa.gov/data/"
    r = requests.get(URL)

    soup = BeautifulSoup(r.content, 'html5lib')

    for element in soup.find_all('span'):
        if "Atlantic hurricane database (HURDAT2)" in element.text:
            target = element
    
    source = ("https://www.nhc.noaa.gov") + (target.next_sibling.next_sibling.attrs['href'])

    download_dataset = pd.read_csv(source, header = None, names = list(range(0, 20)))

    download_dataset.to_csv(f"../data/01_raw/{dest_filename}.csv", 
                            header = False, index = False)

    print(f"Downloaded data to /data/01_raw/{dest_filename}.csv")

    # Show the newly downloaded dataset
    return download_dataset.head()

# function to download pacific hurdat data
# default values download dataset current as of 2020.08.13
def download_pacific_hurdat_raw(dest_filename = "Pacific"):
    
    URL = "https://www.nhc.noaa.gov/data/"
    r = requests.get(URL)

    soup = BeautifulSoup(r.content, 'html5lib')

    for element in soup.find_all('span'):
        if "Northeast and North Central Pacific hurricane database (HURDAT2)" in element.text:
            target = element
    
    source = ("https://www.nhc.noaa.gov") + (target.next_sibling.next_sibling.attrs['href'])

    download_dataset = pd.read_csv(source, header = None, names = list(range(0, 20)))

    download_dataset.to_csv(f"../data/01_raw/{dest_filename}.csv",
                            header = False, index = False)

    print(f"Downloaded data to /data/01_raw/{dest_filename}.csv")

    return download_dataset.head()