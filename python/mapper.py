import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd
import numpy as np

class Mapper:
    def __init__(self):
        self.sensors = []
        self.gateways = []

        self.app = dash.Dash(__name__)
        self.location_center = (52.2313, 6.8686)  # abraham lebeboer park center
        self.initial_data = pd.DataFrame({"lat": [self.location_center[0]], "lon": [self.location_center[1]]})

        self.app.layout = html.Div([
            dcc.Graph(
                id='live-map',
                style={"width": "100vw", "height": "100vh"}
            ),
            dcc.Interval(
                id='interval-component',
                interval=1 * 1000,
                n_intervals=0
            )
        ], style={"margin": "0", "padding": "0"})

        # Register the callback using self.app.callback
        self.app.callback(
            Output('live-map', 'figure'),
            Input('interval-component', 'n_intervals')
        )(self.update_map)

    def update_map(self, n_intervals):
        # For demo: move the first sensor randomly
        if self.sensors:
            new_lat, new_lon = self.sensors[0].get_long_lat()
        else:
            new_lat, new_lon = self.location_center

        updated_data = pd.DataFrame({"lat": [new_lat], "lon": [new_lon]})

        # Use scatter_map and map_style!
        fig = px.scatter_map(
            updated_data,
            lat="lat",
            lon="lon",
            zoom=9,
            center={"lat": self.location_center[0], "lon": self.location_center[1]}
        )
        fig.update_layout(
            map_style="open-street-map",
            margin={"r": 0, "t": 0, "l": 0, "b": 0}
        )
        return fig

    def update(self, sensors, gateways):
        self.sensors = sensors
        self.gateways = gateways

    def run(self):
        self.app.run(debug=True, port=8050)  # Use .run() instead of .run_server()

if __name__ == "__main__":
    from signals import Sensor, Gateway


    # Example sensor and gateway data
    sensors = [
        Sensor("Sensor1", "EUI1", "Gateway1", 52.0, 4.0, 0.5),
        Sensor("Sensor2", "EUI2", "Gateway2", 52.1, 4.1, 0.6)
    ]
    gateways = [
        Gateway("Gateway1", "EUI1", 52.0, 4.0, 10),
        Gateway("Gateway2", "EUI2", 52.1, 4.1, 20)
    ]

    mapper = Mapper()
    mapper.update(sensors, gateways)
    mapper.run()
