
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd
import numpy as np

app = dash.Dash(__name__)

# Initialize with a starting position
initial_data = pd.DataFrame({"lat": [53], "lon": [7]})

app.layout = html.Div([
    dcc.Graph(id='live-map'),
    dcc.Interval(
        id='interval-component',
        interval=1 * 1000,  # Update every 1 second
        n_intervals=0
    )
])


@app.callback(
    Output('live-map', 'figure'),
    Input('interval-component', 'n_intervals')
)
def update_map(n):
    # Simulate new GPS coordinates (replace with real data)
    new_lat = initial_data["lat"].iloc[-1] + np.random.uniform(-0.1, 0.1)
    new_lon = initial_data["lon"].iloc[-1] + np.random.uniform(-0.1, 0.1)

    # Update DataFrame with new position
    updated_data = pd.DataFrame({"lat": [new_lat], "lon": [new_lon]})

    # Create Plotly Express map figure
    fig = px.scatter_mapbox(
        updated_data,
        lat="lat",
        lon="lon",
        zoom=8,
        height=500,
        width=800
    )
    fig.update_layout(
        mapbox_style="open-street-map",
        margin={"r": 0, "t": 0, "l": 0, "b": 0}
    )
    return fig


if __name__ == '__main__':
    app.run(debug=True, port=8050)