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
        self.location_center = (52.236, 6.86)  # abraham lebeboer park center
        self.initial_data = pd.DataFrame({"lat": [self.location_center[0]], "lon": [self.location_center[1]]})

        self.app.layout = html.Div([
            dcc.Graph(
                id='live-map',
                style={"width": "95vw", "height": "100vh"}
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


    def update(self, sensors, gateways):
        self.sensors = sensors
        self.gateways = gateways

    def update_map(self, n_intervals):

        # Collect all points
        data = []
        for s in self.sensors:
            lat = s.get_lat()
            lon = s.get_long()
            type = "Sensor"
            if not s.known:
                type = "Unknown Sensor"
            data.append({
                "lat": lat,
                "lon": lon,
                "type": type,
                "eui": s.get_sensor_id(),
                "name": s.name_of_sensor if s.has_sensor_name() else "Unknown",
            })
        for g in self.gateways:
            lat = g.get_lat()
            lon = g.get_long()
            data.append({
                "lat": lat,
                "lon": lon,
                "type": "Gateway",
                "eui": g.get_gateway_id(),
                "name": g.name_of_gateway,
                "altitude": g.altitude,
            })


        df = pd.DataFrame(data)


        # If no data, show center
        if df.empty:
            print("[Mapper]: no data to map")
            df = pd.DataFrame([{"lat": self.location_center[0], "lon": self.location_center[1], "type": "Center",
                                "name": "Center"}])

        fig = px.scatter_map(
            df,
            lat="lat",
            lon="lon",
            color="type",  # Color by type (Sensor/Gateway)
            hover_name="name",  # Show name on hover
            zoom=14,
            center={"lat": self.location_center[0], "lon": self.location_center[1]},
            map_style="open-street-map"
        )
        fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
        return fig

    def run(self):
        self.app.run(debug=True, port=8050)  # Use .run() instead of .run_server()

if __name__ == "__main__":
    from signals import Sensor, Gateway


    # Example sensor and gateway data
    sensors = [
        Sensor("Sensor1", "EUI1", "Gateway1", 52.233, 6.860, 0.5),
        Sensor("Sensor2", "EUI2", "Gateway2", 52.232, 6.868, 0.6)
    ]
    gateways = [
        Gateway("Gateway1", "EUI1", 52.236, 6.860, 10),
        Gateway("Gateway2", "EUI2", 52.231, 6.868, 20)
    ]

    mapper = Mapper()
    mapper.update(sensors, gateways)
    mapper.run()
