import pandas as pd
import dash
import plotly.express as px
import plotly.graph_objects as go
from dash.dependencies import Input, Output
from data import fetch_air_quality_data_bigquery, load_csv_data
from layout import create_layout

# Initialize the Dash app
app = dash.Dash(__name__)

server = app.server

# Function to create map plot
def create_map_figure():
    air_quality_data = fetch_air_quality_data_bigquery()
    air_quality_data['scale'] = 6

    # make the points biggeor on map
    fig = px.scatter_mapbox(air_quality_data, lat='lat', lon='lon', color='aqi',size='scale',
                            hover_name='station_name', hover_data=['time'],
                            color_continuous_scale='teal',
                            zoom=10,  )
    fig.update_layout(mapbox_style='open-street-map', mapbox_zoom=10,
                      mapbox_center_lat=41.7151377, mapbox_center_lon=44.827096)
    return fig

def create_pollutants_line_figure(selected_region='alexander-kazbegi ave.', start_date='2021-01-01', end_date='2023-06-01'):
    data = load_csv_data()
    # Filter data for the selected region
    filtered_data = data[data['region'] == selected_region].copy()
    
    # Convert the date column to datetime
    filtered_data['date'] = pd.to_datetime(filtered_data['date'])
    
    # Set the date column as the index
    filtered_data.set_index('date', inplace=True)
    
    # drop values before start date and filter numeric columns
    numeric_columns = ['pm25', 'pm10', 'o3', 'no2', 'so2', 'co']
    filtered_data = filtered_data[numeric_columns][filtered_data.index >= start_date]
    filtered_data = filtered_data.applymap(lambda x: pd.to_numeric(x, errors='coerce'))

    # Resample data to monthly level and calculate mean
    monthly_avg = filtered_data.resample('M').mean()

    # Creating line chart
    fig = go.Figure()
    
    # Add lines for each pollutant
    for pollutant in ['pm25', 'pm10', 'o3', 'no2', 'so2', 'co']:
        fig.add_trace(go.Scatter(x=monthly_avg.index, y=monthly_avg[pollutant],
                                 mode='lines+markers', name=pollutant))
    
    # add line for average of all pollutants
    # fig.add_trace(go.Scatter(x=monthly_avg.index, y=monthly_avg.mean(axis=1),))
    
    # Add title and labelstitle='Monthly Average Pollutant Levels',title='Monthly Average Pollutant Levels',
    fig.update_layout(
                      xaxis_title='Month',
                      yaxis_title='Pollutant Levels',
                      margin=dict(l=100, r=100, t=100, b=100))
    
    return fig

# Create charts
map_figure = create_map_figure()

# Set the layout of the app
app.layout = create_layout(map_figure)

# Callback to update the heatmap figure based on the selected region
@app.callback(
    Output('heatmap-plot', 'figure'),
    [Input('region-dropdown', 'value',)]
)
def update_heatmap(selected_region):
    return create_pollutants_line_figure(selected_region)


# Run the Dash app
if __name__ == '__main__':
    app.run_server(debug=True)