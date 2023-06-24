import dash_html_components as html
import dash_core_components as dcc

def create_layout(map_figure):#, heatmap_figure):
    return html.Div([
        html.Div([
            dcc.Graph(id='map-plot', figure=map_figure, style={'height': '80vh'})
        ], style={'width': '50%', 'display': 'inline-block'}),
        
        html.Div([
            dcc.Dropdown(
                id='region-dropdown',
                options=[
                    {'label': 'Kazbegi', 'value': 'alexander-kazbegi ave.'},
                    {'label': 'David Agmashenebeli', 'value': 'david-agmashenebeli avenue 73a'},
                    {'label': 'Akaki Tsereteli', 'value': 'akaki-tsereteli ave. 105'},
                    {'label': 'Varketili', 'value': 'varketili'}
                ],
                value='alexander-kazbegi ave.',
                clearable=False
            ),
            dcc.Graph(id='heatmap-plot',style={'height': '80vh'})
        ], style={'width': '50%', 'display': 'inline-block'})
    ])
