import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import pandas as pd
import plotly.express as px
import json
import os
from dash import callback_context

# Load data
with open('C:/ground1/karnataka.json', 'r') as f:
    geojson = json.load(f)
df = pd.read_csv('C:/ground1/water_data5.csv')

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, assets_folder=os.path.join(os.getcwd(), 'assets'), external_stylesheets=external_stylesheets, suppress_callback_exceptions=True)

# Define color options for the dropdown
color_options = ['cl', 'k', 'ph_gen', 'Level (m)']

# Define the starting page layout
start_page_layout = html.Div([
    html.H1("Welcome to Groundwater Analysis", style={'textAlign': 'center', 'color': 'blue'}),
    html.Button('Get Started', id='get-started-button', n_clicks=0, style={'margin': '20px'})
])

# Add a new layout for the district page
#district_page_layout = html.Div([
   # html.H1("District-Level Analysis", style={'textAlign': 'center', 'color': 'blue'}),
    #dcc.Dropdown(
        #id='district-dropdown',
        #options=[{'label': district, 'value': district} for district in df['District'].unique()],
        #value=df['District'].iloc[0],
        #style={'width': '50%', 'margin': '0 auto'}
   # ),
    #dcc.Graph(id='district-choropleth', style={'height': '70vh', 'width': '80vw', 'padding': '40px'}),
#])


# Define the main app layout
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])

## Modify the display_page callback to handle the new page
@app.callback(
    Output('page-content', 'children'),
    [Input('url', 'pathname')]
)
def display_page(pathname):
    if pathname == '/app':
        return main_app_layout
    elif pathname.startswith('/district/'):
        clicked_district = pathname.split('/')[2]
        return district_page_layout(clicked_district)

    else:
        return start_page_layout

# Main app layout
main_app_layout = html.Div([
    html.H1("Groundwater Analysis", style={'textAlign': 'center', 'color': 'blue'}),
    dcc.Dropdown(
        id='color-dropdown',
        options=[{'label': col, 'value': col} for col in color_options],
        value='cl',
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
    dcc.Graph(id='choropleth', clickData=None, style={'height': '70vh', 'width': '80vw', 'padding': '40px'}),
    html.Br(),
    dcc.Graph(id='scatter_geo', clickData=None, style={'height': '70vh', 'width': '80vw', 'padding': '40px'}),
    html.Br(),
    dcc.Markdown(id='click-data', children="Click on a point in the scatter plot to see more details.", style={'color': 'red'})
])

# Callback to handle button click and redirect to main app layout
@app.callback(
    Output('url', 'pathname'),
    [Input('get-started-button', 'n_clicks')],
    
)
def redirect_to_app(n_clicks):
    if n_clicks > 0:
        return '/app'
    else:
        return '/'
    
# Add a new callback to navigate to the district page when a district is clicked
@app.callback(
    Output('url', 'pathname',allow_duplicate=True),
    [Input('choropleth', 'clickData')],
    prevent_initial_call=True
)
def navigate_to_district_page(clickData):
    if clickData is not None:
        clicked_district = clickData['points'][0]['location']
        return f'/district/{clicked_district}'
    else:
        return '/app'

# Callbacks for the main app layout (similar to your existing callbacks)
@app.callback(
    [Output('choropleth', 'figure'),
     Output('scatter_geo', 'figure')],
    [Input('year-slider', 'value'),
     Input('color-dropdown', 'value')]
)
def update_visualizations(selected_year, selected_color):
    filtered_df = df[df['Date Collection'] == selected_year]
    app.selected_color = selected_color  # Store selected color in the app instance

    # Update choropleth map
    fig_choropleth = px.choropleth_mapbox(filtered_df,
                                          geojson=geojson,
                                          locations='District',
                                          color=selected_color,
                                          featureidkey="properties.district",
                                          center={"lat": filtered_df['Latitude'].mean(), "lon": filtered_df['Longitude'].mean()},
                                          mapbox_style="carto-positron",
                                          zoom=5,
                                          hover_data=['Station Name', 'Agency Name', 'District', selected_color])
    fig_choropleth.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})

    # Update scatter plot
    fig_scatter = px.scatter_geo(filtered_df,
                                 lat='Latitude',
                                 lon='Longitude',
                                 color=selected_color,
                                 hover_data=['Station Name', 'Agency Name', 'District', selected_color])
    fig_scatter.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})

    return fig_choropleth, fig_scatter

# Add a callback to update the district choropleth map
@app.callback(
    Output('district-choropleth', 'figure'),
    [Input('district-dropdown', 'value')]
)
def update_district_choropleth(selected_district):
    filtered_district_df = df[df['District'] == selected_district]

    # Create choropleth map for the selected district
    fig_district_choropleth = px.choropleth_mapbox(filtered_district_df,
                                                  geojson=geojson,
                                                  locations='District',
                                                  color=app.selected_color,  # Use the stored color
                                                  featureidkey="properties.district",
                                                  center={"lat": filtered_district_df['Latitude'].mean(), "lon": filtered_district_df['Longitude'].mean()},
                                                  mapbox_style="carto-positron",
                                                  zoom=9,  # Adjust the zoom level as needed
                                                  hover_data=['Station Name', 'Agency Name', 'District', app.selected_color])

    fig_district_choropleth.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})

    return fig_district_choropleth


@app.callback(
    Output('click-data', 'children'),
    [Input('scatter_geo', 'clickData'),
     Input('year-slider', 'value')]
)
def display_click_data(clickData, selected_year):
    if clickData is None:
        return "Click on a point in the scatter plot to see more details."
    else:
        # Get the index of the clicked point
        point_index = clickData['points'][0]['pointIndex']
        # Filter the dataframe for the selected year
        filtered_df = df[df['Date Collection'] == selected_year]
        # Get the data of the clicked point
        point_data = filtered_df.iloc[point_index]
        selected_color = app.selected_color  # Retrieve selected color from the app instance
        # Create a custom hover data message with NaN handling
        hover_data_message = "\n".join(
            [f"{property_name}: {point_data[property_name]}" if pd.notna(point_data[property_name]) else f"{property_name}: N/A"
             for property_name in ['Station Name', 'Agency Name', 'District', selected_color]]
        )
        return hover_data_message# Your existing callback logic here...
    
# Modify the district_page_layout to accept a district as a parameter
def district_page_layout(selected_district):
    filtered_district_df = df[df['District'] == selected_district]

    # Create choropleth map for the selected district
    fig_district_choropleth = px.choropleth_mapbox(filtered_district_df,
                                                  geojson=geojson,
                                                  locations='District',
                                                  color=app.selected_color,
                                                  featureidkey="properties.district",
                                                  center={"lat": filtered_district_df['Latitude'].mean(), "lon": filtered_district_df['Longitude'].mean()},
                                                  mapbox_style="carto-positron",
                                                  zoom=9,
                                                  hover_data=['Station Name', 'Agency Name', 'District', app.selected_color])

    fig_district_choropleth.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})

    return html.Div([
        html.H1(f"District-Level Analysis: {selected_district}", style={'textAlign': 'center', 'color': 'blue'}),
        dcc.Graph(id='district-choropleth', figure=fig_district_choropleth, style={'height': '70vh', 'width': '80vw', 'padding': '40px'}),
    ])

if __name__ == '__main__':
    app.run_server(debug=True)
