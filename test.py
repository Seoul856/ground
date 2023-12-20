import streamlit as st
import pandas as pd
import plotly.express as px
import json

# Load data
with open('karnataka.json', 'r') as f:
    geojson = json.load(f)

df = pd.read_csv('water_data5.csv')

# Define color options for the dropdown
color_options = ['cl', 'k', 'ph_gen', 'Level (m)']
st.set_page_config(layout="wide")

# Define the starting page layout
if not st.session_state.get('started', False):
    st.title("Welcome to Groundwater Analysis")
    if st.button('Get Started'):
        st.session_state.started = True
else:
    st.title("Groundwater Analysis")

    # Hide the "Get Started" button on the next page
    st.session_state.started = True

    selected_color = st.selectbox("Select Color:", color_options, index=0)

    year_slider = st.slider("Select Year:", min_value=2018, max_value=2020, value=2018, step=1)

    # Filter data based on selected year
    filtered_df = df[df['Date Collection'] == year_slider]

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

    # Handle click events on the choropleth map
    click_data = fig_choropleth.to_dict()
    if click_data is not None and "clickData" in click_data:
        clicked_district = click_data["clickData"]["points"][0]["location"]
        st.experimental_set_query_params(selected_district=clicked_district)
        st.experimental_rerun()

    # Check if a district is selected in the URL parameters
    selected_district = st.experimental_get_query_params().get('selected_district', None)

    if selected_district:
        st.title(f"Analysis for {selected_district}")
        # Display content for the selected district (Page 2)
        st.write("You can add your analysis or content here for the selected district.")

    # Update scatter plot
    fig_scatter = px.scatter_geo(filtered_df,
                                 lat='Latitude',
                                 lon='Longitude',
                                 color=selected_color,
                                 hover_data=['Station Name', 'Agency Name', 'District', selected_color])
    fig_scatter.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})

    st.plotly_chart(fig_scatter)
