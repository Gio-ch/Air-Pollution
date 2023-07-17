import requests
import pandas as pd
import os
import glob
from settings import URL
from settings import DATASET_ID, TABLE_ID, PROJECT_ID, GOOGLE_APPLICATION_CREDENTIALS
from google.cloud import bigquery
from google.oauth2 import service_account
import time
import json

def load_daily_data(dataset_id='air_quality', table_id='quality_average_region', staging_table_id='staging_table') -> None:
    # Fetch the data from the API
    df = fetch_air_quality_data()

    # Create a unique ID for the temporary staging table
    temp_staging_table_id = f"{staging_table_id}_{int(time.time())}"

    # Store the data in the temporary staging table
    store_data_in_bigquery(df, dataset_id, temp_staging_table_id)

    # Merge the data from the temporary staging table into the main table
    merge_data(dataset_id, table_id, temp_staging_table_id)

    # Delete the temporary staging table
    delete_table(dataset_id, temp_staging_table_id)


def fetch_air_quality_data() -> pd.DataFrame:
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
    
    return df
    # Store data in BigQuery
    # store_data_in_bigquery(df, DATASET_ID, STAGING_TABLE_ID)

def create_table(project_id, dataset_id, staging_table_id):
    client = bigquery.Client()
    dataset_id = f"{project_id}.{dataset_id}"

    # Check if the table already exists
    tables = [table.table_id for table in client.list_tables(dataset_id)]
    if staging_table_id in tables:
        print(f"Table {staging_table_id} already exists.")
        return

    # Define your table schema
    # This should match the schema of your main table
    schema = [
        bigquery.SchemaField("station_name", "STRING"),
        bigquery.SchemaField("lat", "FLOAT"),
        bigquery.SchemaField("lon", "FLOAT"),
        bigquery.SchemaField("aqi", "FLOAT"),
        bigquery.SchemaField("time", "DATETIME"),
    ]

    # Create a new table with the defined schema
    table = bigquery.Table(f"{dataset_id}.{staging_table_id}", schema=schema)
    table = client.create_table(table)  # API request

    print(f"Created table {table.project}.{table.dataset_id}.{table.table_id}")
    
def store_data_in_bigquery(df, dataset_id, table_id) -> None:
    client = create_bigquery_client()

    # Convert the DataFrame to a BigQuery-compatible format
    df['time'] = df['time'].dt.tz_localize(None).astype(str)
    # df['time'] = df['time'].astype(str)
    records = df.to_dict('records')

    # Check if the table already exists else create it
    create_table(PROJECT_ID, dataset_id, table_id)
    
    # Get the table reference
    table_ref = client.dataset(dataset_id).table(table_id)
    table = client.get_table(table_ref)  # fetch the table schema
    
    
    # Insert data into the table
    errors = client.insert_rows_json(table, records)
    if errors:
        raise SystemExit(f'Encountered errors while inserting rows: {errors}')
    
def merge_data(dataset_id, table_id='quality_average_region', staging_table_id='staging_table'):
    client = create_bigquery_client()

    # Define the MERGE statement
    sql = f"""
    MERGE `{dataset_id}.{table_id}` T
    USING `{dataset_id}.{staging_table_id}` S
    ON T.time = S.time AND T.station_name = S.station_name
    WHEN NOT MATCHED THEN
      INSERT (station_name, lat, lon, aqi, time) 
      VALUES (station_name, lat, lon, aqi, time)
    """

    # Run the MERGE statement
    client.query(sql).result()

def clear_staging_table(dataset_id, staging_table_id='staging_table'):
    client = create_bigquery_client()

    # Define the DELETE statement
    sql = f"""
    DELETE FROM `{dataset_id}.{staging_table_id}` WHERE TRUE
    """

    # Run the DELETE statement
    client.query(sql).result()

def delete_table(dataset_id, table_id):
    client = create_bigquery_client()
    # client = bigquery.Client()

    # Construct a full BigQuery table identifier
    table_ref = client.dataset(dataset_id).table(table_id)

    # Delete the table
    client.delete_table(table_ref)

    print(f"Table {table_id} deleted.")
    
def fetch_air_quality_data_bigquery(dataset_id=DATASET_ID, table_id=TABLE_ID) -> pd.DataFrame:
    # client = bigquery.Client()
    client = create_bigquery_client()

    print(f"Fetching data from {dataset_id}.{table_id}")
    # Define the SQL query
    sql = f"""
    SELECT * FROM `{dataset_id}.{table_id}`
    """

    # Run the query and load the result into a pandas DataFrame
    df = client.query(sql).to_dataframe()

    return df



def create_bigquery_client():
    # Get the service account key JSON string from the environment variable
    service_account_info = json.loads(GOOGLE_APPLICATION_CREDENTIALS)

    # Create credentials from the service account info
    credentials = service_account.Credentials.from_service_account_info(service_account_info)

    # Create a BigQuery client with the credentials
    client = bigquery.Client(credentials=credentials, project=credentials.project_id)

    return client

def load_csv_data(directory='data') -> pd.DataFrame:
    """
    Loads CSV files from the given directory, combines them,
    and assigns an additional field 'filename' extracted from the filename.
    Returns a single dataframe with all data.
    """
    # A one-liner to read, assign column name and concatenate the dataframes
    df = pd.concat([pd.read_csv(f, sep=',').assign(region=os.path.basename(f).split(',')[0]) for f in glob.glob(os.path.join(directory, '*.csv'))], ignore_index=True)
    
    return df

