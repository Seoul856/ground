import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output, State
import pandas as pd
import plotly.express as px
import json
import os

# Load data
with open('C:/ground1/karnataka.json', 'r') as f:
    geojson = json.load(f)
df = pd.read_csv('C:/ground1/water1.csv')
print(df.head(5))

app = dash.Dash(__name__,assets_folder=os.path.join(os.getcwd(), 'assets'))

app.layout = html.Div([
    html.H1("Groundwater Analysis", style={'textAlign': 'center', 'color': 'blue'}),
    dcc.Slider(
        id='year-slider',
        min=2015,
        max=2020,
        value=2015,
        marks={str(year): str(year) for year in range(2015, 2021)},
        step=None
    ),
    dcc.Graph(id='choropleth', clickData=None, style={'padding': '10px'}),
    html.Br(),
    dcc.Graph(id='scatter_geo', clickData=None, style={'padding': '10px'}),
    html.Br(),
    dcc.Markdown(id='click-data', children="Click on a point in the scatter plot to see more details.", style={'color': 'red'})
])

@app.callback(
    Output('choropleth', 'figure'),
    [Input('year-slider', 'value')]
)
def update_choropleth(selected_year):
    filtered_df = df[df['Date Collection'] == selected_year]

    fig = px.choropleth_mapbox(filtered_df, 
                                geojson=geojson, 
                                locations='district', 
                                color='cl',
                                featureidkey="properties.district",
                                center={"lat": filtered_df['Latitude'].mean(), "lon": filtered_df['Longitude'].mean()},
                                mapbox_style="carto-positron", 
                                zoom=5,
                                hover_data=['Station Name', 'Agency Name', 'district', 'ph_gen'])
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})

    return fig

@app.callback(
    Output('scatter_geo', 'figure'),
    [Input('year-slider', 'value')]
)
def update_scatter_geo(selected_year):
    filtered_df = df[df['Date Collection'] == selected_year]

    fig = px.scatter_geo(filtered_df, 
                         lat='Latitude', 
                         lon='Longitude', 
                         color='cl',
                         hover_data=['Station Name', 'Agency Name', 'district', 'ph_gen'])
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})

    return fig

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
        return f"""
        Station Name: {point_data['Station Name']}
        Agency Name: {point_data['Agency Name']}
        District: {point_data['district']}
        pH_gen: {point_data['ph_gen']}
        """

if __name__ == '__main__':
    app.run_server(debug=True)
#working little
#The choice of Mapbox style for a geo scatterplot can depend on the specific requirements of your visualization. However, if you're looking for a style that doesn't require a token, you can use one of the built-in styles provided by Plotly Express. Here are a few options:

#1. "open-street-map": This style provides a detailed view of streets and landmarks, making it suitable for visualizations that require a high level of detail at the street level.

#2. "carto-positron": This style provides a light-colored base map, which can help your data points stand out. It's a good choice for visualizations that need to highlight specific data points.

#3. "carto-darkmatter": This style provides a dark-colored base map, which can create a striking contrast with brightly colored data points. It's a good choice for visualizations that aim to create a strong visual impact.

#4. "stamen-terrain": This style emphasizes physical terrain features, making it suitable for visualizations that involve geographical or topographical data.

#5. "stamen-toner": This style provides a high-contrast, black and white base map. It's a good choice for visualizations that aim for a minimalist aesthetic.

#6. "stamen-watercolor": This style provides a base map with a watercolor effect, creating a visually pleasing aesthetic. It's a good choice for visualizations that aim to be visually appealing.

#Remember, the choice of style can greatly affect the readability and aesthetic appeal of your visualization, so it's worth trying out different styles to see which one works best for your specific needs. You can change the style by replacing "carto-positron" in your code with the name of the style you want to use. For example, to use the "open-street-map" style, you would change the `mapbox_style` parameter in the `px.scatter_geo` function to "open-street-map".
