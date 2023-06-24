import requests
import pandas as pd
import os
import glob
from settings import URL

def fetch_air_quality_data():
    """
    Fetches air quality data and returns a dataframe.
    """
    daily_data = requests.get(URL).json()
    times = [i['station']['time'] for i in daily_data['data']]
    station_names = [i['station']['name'] for i in daily_data['data']]

    df = pd.DataFrame(daily_data['data'], )
    df['time'] = times
    df['station_name'] = station_names

    df['lat'] = df['lat'].astype(float)
    df['lon'] = df['lon'].astype(float)
    df['aqi'] = df['aqi'].astype(float)
    df['time'] = pd.to_datetime(df['time'])

    return df

def load_csv_data(directory='data'):
    """
    Loads CSV files from the given directory, combines them,
    and assigns an additional field 'filename' extracted from the filename.
    Returns a single dataframe with all data.
    """
    # A one-liner to read, assign column name and concatenate the dataframes
    df = pd.concat([pd.read_csv(f, sep=',').assign(region=os.path.basename(f).split(',')[0]) for f in glob.glob(os.path.join(directory, '*.csv'))], ignore_index=True)
    
    return df

