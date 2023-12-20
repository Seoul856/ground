import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px
import json

# Load data
with open('C:/ground1/karnataka.json', 'r') as f:
    geojson = json.load(f)
df = pd.read_csv('C:/ground1/water_data5.csv')

app = dash.Dash(__name__)

# Get the unique districts and variables from the DataFrame
district_options = df['District'].unique()
variable_options = ['cl', 'k', 'ph_gen', 'Level (m)']

app.layout = html.Div([
    html.H1("District Page", style={'textAlign': 'center', 'color': 'blue'}),
    dcc.Dropdown(
        id='district-dropdown',
        options=[{'label': district, 'value': district} for district in district_options],
        value=district_options[0],  # Set a default district
        style={'width': '50%', 'margin': '0 auto'}
    ),
    dcc.Dropdown(
        id='variable-dropdown',
        options=[{'label': variable, 'value': variable} for variable in variable_options],
        value=variable_options[0],  # Set a default variable
        style={'width': '50%', 'margin': '0 auto'}
    ),
    dcc.Slider(
        id='year-slider',
        min=2018,
        max=2020,
        value=2018,
        marks={str(year): str(year) for year in range(2018, 2021)},
        step=None
    ),
    dcc.Graph(id='district-choropleth', style={'height': '70vh', 'width': '80vw', 'padding': '40px'})
])

@app.callback(
    Output('district-choropleth', 'figure'),
    [Input('district-dropdown', 'value'),
     Input('variable-dropdown', 'value'),
     Input('year-slider', 'value')]
)
def update_district_choropleth(selected_district, selected_variable, selected_year):
    filtered_df = df[(df['District'] == selected_district) & (df['Date Collection'] == selected_year)]

    # Update choropleth map for the specific district and variable
    fig_district_choropleth = px.choropleth_mapbox(filtered_df,
                                                  geojson=geojson,
                                                  locations='District',
                                                  color=selected_variable,
                                                  featureidkey="properties.district",
                                                  center={"lat": filtered_df['Latitude'].mean(), "lon": filtered_df['Longitude'].mean()},
                                                  mapbox_style="carto-positron",
                                                  zoom=5,
                                                  hover_data=['Station Name', 'Agency Name', 'District', selected_variable])
    fig_district_choropleth.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})

    return fig_district_choropleth

if __name__ == '__main__':
    app.run_server(debug=True)
