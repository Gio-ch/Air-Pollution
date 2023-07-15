import requests
import pandas as pd
import os
import glob
from settings import URL
from settings import DATASET_ID, TABLE_ID
from google.cloud import bigquery

def load_daily_data() -> None:
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
    
    # remove all other fields except for the ones we need
    df = df[['station_name', 'lat', 'lon', 'aqi', 'time']]
    
    # Store data in BigQuery
    store_data_in_bigquery(df, DATASET_ID, TABLE_ID)

def store_data_in_bigquery(df, dataset_id, table_id) -> None:
    client = bigquery.Client()

    # Convert the DataFrame to a BigQuery-compatible format
    df['time'] = df['time'].dt.tz_localize(None).astype(str)
    # df['time'] = df['time'].astype(str)
    records = df.to_dict('records')

    # Get the table reference
    table_ref = client.dataset(dataset_id).table(table_id)
    table = client.get_table(table_ref)  # fetch the table schema
    
    
    # Insert data into the table
    errors = client.insert_rows_json(table, records)
    if errors:
        raise SystemExit(f'Encountered errors while inserting rows: {errors}')

def fetch_air_quality_data(dataset_id=DATASET_ID, table_id=TABLE_ID) -> pd.DataFrame:
    client = bigquery.Client()

    # Define the SQL query
    sql = f"""
    SELECT * FROM `{dataset_id}.{table_id}`
    """

    # Run the query and load the result into a pandas DataFrame
    df = client.query(sql).to_dataframe()

    return df

def load_csv_data(directory='data') -> pd.DataFrame:
    """
    Loads CSV files from the given directory, combines them,
    and assigns an additional field 'filename' extracted from the filename.
    Returns a single dataframe with all data.
    """
    # A one-liner to read, assign column name and concatenate the dataframes
    df = pd.concat([pd.read_csv(f, sep=',').assign(region=os.path.basename(f).split(',')[0]) for f in glob.glob(os.path.join(directory, '*.csv'))], ignore_index=True)
    
    return df

