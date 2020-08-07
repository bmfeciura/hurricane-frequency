import pandas as pd

def download_atlantic_hurdat_raw(first_season = "1851", recent_season = "2019", update_date = "052520", dest_filename = "Atlantic"):
    
    url = f"https://www.nhc.noaa.gov/data/hurdat/hurdat2-{first_season}-{recent_season}-{update_date}.txt"

    download_dataset = pd.read_csv(url, header = None, names = list(range(0, 20)))

    download_dataset.to_csv(f"../data/01_raw/{dest_filename}.csv", index = False)

    return download_dataset.head()

def download_pacific_hurdat_raw(first_season = "1949", recent_season = "2019", update_date = "042320", dest_filename = "Pacific"):
    
    url = f"https://www.nhc.noaa.gov/data/hurdat/hurdat2-nepac-{first_season}-{recent_season}-{update_date}.txt"

    download_dataset = pd.read_csv(url, header = None, names = list(range(0, 20)))

    download_dataset.to_csv(f"../data/01_raw/{dest_filename}.csv", index = False)

    return download_dataset.head()