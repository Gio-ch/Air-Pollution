import dash_html_components as html
import dash_core_components as dcc

def create_layout(map_figure):
    return html.Div([
        # Outer Div
        html.Div([
            # Left chart (Map)
            html.Div([
                # Title for Map
                html.H3("Air Quality Map", style={'textAlign': 'center','padding': '3px'} ),

                # Map
                dcc.Graph(
                    id='map-plot', 
                    figure=map_figure, 
                    config={'scrollZoom': False, 'displayModeBar': True},
                    style={'height': '75vh','margin-top': '50px',}
                )
            ], style={'flex': '1', 'padding': '10px',  }),
            
             # Right side with dropdown and heatmap/linechart
            html.Div([
                # Container for dropdown and chart
                html.Div([
                    # Title for Chart
                    html.H3("Pollutant Levels", style={'textAlign': 'center', 'padding': '3px'}),

                    dcc.Dropdown(
                        id='region-dropdown',
                        options=[
                            {'label': 'Kazbegi', 'value': 'alexander-kazbegi ave.'},
                            {'label': 'David Agmashenebeli', 'value': 'david-agmashenebeli avenue 73a'},
                            {'label': 'Akaki Tsereteli', 'value': 'akaki-tsereteli ave. 105'},
                            {'label': 'Varketili', 'value': 'varketili'}
                        ],
                        value='alexander-kazbegi ave.',
                        clearable=False,style={'margin-top': '50px'},
                    ),
                ], style={'marginBottom': '20px','z-index': '1000','position': 'relative',}),
              
                # Right Chart (Heatmap/Line chart)
                html.Div([
                        dcc.Graph(id='heatmap-plot',
                                  style={'height': '82vh','margin-top': '-98px','margin-right': '15px'},
                                  config={'displayModeBar': False}
                                )
                ],),
            ], style={'flex': '1', 'padding': '10px'})
        ], style={'display': 'flex'})
    ])