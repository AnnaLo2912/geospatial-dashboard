import geopandas as gpd
from shapely.geometry import Point
import dash
from dash import dcc, html
import plotly.express as px
import pandas as pd

# --- Load & preprocess data ---
df = pd.read_csv("data/yellow_tripdata_2015-01.csv", nrows=10000)

# Remove invalid coordinates
df = df[
    (df.pickup_longitude != 0) &
    (df.pickup_latitude != 0) &
    (df.pickup_longitude > -80) & (df.pickup_longitude < -70) &
    (df.pickup_latitude > 35) & (df.pickup_latitude < 45)
]

# Convert to GeoDataFrame
gdf = gpd.GeoDataFrame(
    df,
    geometry=[Point(xy) for xy in zip(df.pickup_longitude, df.pickup_latitude)],
    crs="EPSG:4326"
)

# Create an interactive Plotly map
fig = px.scatter_map(
    gdf,
    lat=gdf.geometry.y,
    lon=gdf.geometry.x,
    zoom=10,
    title="NYC Taxi Pickups (Sample)",
    height=600
)
fig.update_layout(map_style="open-street-map")

# --- Build Dash app layout ---
app = dash.Dash(__name__)

app.layout = html.Div([
    html.H1("NYC Taxi Pickup Map", style={'textAlign': 'center'}),
    dcc.Graph(figure=fig)
])

if __name__ == "__main__":
    app.run(debug=True)
