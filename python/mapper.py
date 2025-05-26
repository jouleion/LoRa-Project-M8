import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objects as go

import plotly.express as px
import pandas as pd
import numpy as np

class Mapper:
    def __init__(self):
        # create object lists for the sensors and gateways (optimization possible, just use a pointer instead of a copy)
        self.sensors = []
        self.gateways = []

        # create a dash app
        self.app = dash.Dash(__name__)
        self.location_center = (52.2394, 6.8566)  # campus
        self.initial_data = pd.DataFrame({"lat": [self.location_center[0]], "lon": [self.location_center[1]]})

        # Set up the layout of the app
        self.app.layout = html.Div([
            dcc.Graph(
                id='live-map',
                style={"width": "95vw", "height": "100vh"},
                config = {
                    "displayModeBar": False  # This hides the toolbar!
                }
            ),
            # Add an interval component to update the map every 2 seconds
            dcc.Interval(
                id='interval-component',
                interval=2 * 1000,
                n_intervals=0
            )
        ], style={"margin": "0", "padding": "0"})

        # Register the callback using self.app.callback.
        # This sets the function that is run when the interval is triggered
        self.app.callback(
            Output('live-map', 'figure'),
            Input('interval-component', 'n_intervals')
        )(self.update_map)





    def update(self, sensors, gateways):
        # in this function we update the sensors and gateways
        # (optimization possible, just use a pointer instead of a copy)
        self.sensors = sensors
        self.gateways = gateways

    def update_map(self, n_intervals):
        # Get the sensor and gateway data (these are points were gonna plot later
        data = []
        for s in self.sensors:
            # determine position of the sensor and determine the type
            lat = s.get_lat()
            lon = s.get_lon()
            type = "Sensor"
            if not s.known:
                type = "Unknown Sensor"
            data.append({
                "lat": lat,
                "lon": lon,
                "known_lat": s.get_known_lat(),
                "known_lon": s.get_known_lon(),
                "type": type,
                "eui": s.get_sensor_id(),
                "name": s.name_of_sensor if s.has_sensor_name() else "Unknown",
            })
        for g in self.gateways:
            lat = g.get_lat()
            lon = g.get_lon()
            data.append({
                "lat": lat,
                "lon": lon,
                "type": "Gateway",
                "eui": g.get_gateway_id(),
                "name": g.name_of_gateway,
                "altitude": g.altitude,
            })
        df = pd.DataFrame(data)

        # use a center point as a fallback
        if df.empty:
            df = pd.DataFrame(
                [{"lat": self.location_center[0], "lon": self.location_center[1], "type": "Center", "name": "Center"}])

        # Create a scatter mapbox figure
        fig = go.Figure()
        fig.update_layout(
            mapbox=dict(
                style="carto-darkmatter",
                center={"lat": self.location_center[0], "lon": self.location_center[1]},
                zoom=14

            )
        )

        # add extra tranparent circles
        fig.add_trace(
            dict(
                type="scattermapbox",
                lat=df["lat"],
                lon=df["lon"],
                mode="markers",
                marker=dict(
                    size=6,
                    color="white",
                    opacity=0.15,
                    allowoverlap=True,
                ),
                hoverinfo="skip",  # <--- This disables hover for this trace!
                showlegend=False,
            )
        )

        # add extra transpartent circles
        fig.add_trace(
            dict(
                type="scattermapbox",
                lat=df["lat"],
                lon=df["lon"],
                mode="markers",
                marker=dict(
                    size=10,
                    color="white",
                    opacity=0.05,
                    allowoverlap=True,
                ),
                hoverinfo="skip",  # <--- This disables hover for this trace!
                showlegend=False,
            )
        )

        # Add a layer for the points
        for point_type in {"Sensor", "Gateway", "Unknown Sensor"}:
            subdf = df[df["type"] == point_type]
            size = 3
            if point_type == "Sensor":
                color = "pink"
                actual_pos_df = df[df["known_lat"].notnull() & df["known_lon"].notnull()]
                name = df["name"]


                fig.add_trace(
                    dict(
                        type="scattermapbox",
                        lat=actual_pos_df["known_lat"],
                        lon=actual_pos_df["known_lon"],
                        mode="markers",
                        marker=dict(
                            size=3,
                            color="pink",
                            opacity=0.9,
                            allowoverlap=True,
                        ),
                        name="Actual Position Sensors",
                        text=name,
                        hoverinfo="text",

                    )
                )

                color = "lime"
            elif point_type == "Gateway":
                color = "aqua"
                size = 5
            elif point_type == "Unknown Sensor":
                color = "orange"

            fig.add_trace(
                dict(
                    type="scattermapbox",
                    lat=subdf["lat"],
                    lon=subdf["lon"],
                    mode="markers",
                    marker=dict(
                        size=size,
                        color=color,
                        opacity=0.9,
                        allowoverlap=True,
                    ),
                    name=point_type,
                    text=subdf["name"],
                    hoverinfo="text",
                )
            )

        # loop through all sensors
        for sensor in self.sensors:
            if sensor.known:

                # loop through all signals of the sensor
                for signal in sensor.avg_signals:

                    # get the gateway eui > get the gateway position
                    gateway = signal.eui_of_gateway
                    gateway_pos = next((g for g in self.gateways if g.get_gateway_id() == gateway), None)
                    if gateway_pos:
                        # store all the coordinates of the line (2 points, 4 values)
                        line_coordinates = {
                            "lat": [sensor.get_lat(), gateway_pos.get_lat()],
                            "lon": [sensor.get_lon(), gateway_pos.get_lon()]
                        }

                        # Add a line between the sensor and the gateway
                        fig.add_trace(
                            dict(
                                type="scattermapbox",
                                lat=line_coordinates["lat"],
                                lon=line_coordinates["lon"],
                                mode="lines",
                                line=dict(
                                    width=1.5,  # Line width
                                    color="rgba(0, 255, 0, 0.2)",  # Line color
                                ),
                                name=f"Signal to {gateway_pos.name_of_gateway}",
                                showlegend=True,
                            )
                        )

                #if there is a estimated position
                if sensor.pos_is_estimated():
                    line_coordinates = {
                        "lat": [sensor.get_lat(), sensor.get_known_lat()],
                        "lon": [sensor.get_lon(), sensor.get_known_lon()]
                    }

                    # Add a pink line between the actual sensor and the estimated sensor position
                    fig.add_trace(
                        dict(
                            type="scattermapbox",
                            lat=line_coordinates["lat"],
                            lon=line_coordinates["lon"],
                            mode="lines",
                            line=dict(
                                width=1.5,  # Line width
                                color="rgba(255, 198, 208, 0.2)",  # Line color
                            ),
                            name="Actual Position Sensors",
                            showlegend=True,  # Hide legend for these lines
                        )
                    )



            # unkown sensors, draw with orange lines
            else:
                # loop through all signals of the sensor
                for signal in sensor.avg_signals:

                    # get the gateway eui > get the gateway position
                    gateway = signal.eui_of_gateway
                    gateway_pos = next((g for g in self.gateways if g.get_gateway_id() == gateway), None)
                    if gateway_pos:
                        # store all the coordinates of the line (2 points, 4 values)
                        line_coordinates = {
                            "lat": [sensor.get_lat(), gateway_pos.get_lat()],
                            "lon": [sensor.get_lon(), gateway_pos.get_lon()]
                        }

                        # Add a line between the sensor and the gateway
                        fig.add_trace(
                            dict(
                                type="scattermapbox",
                                lat=line_coordinates["lat"],
                                lon=line_coordinates["lon"],
                                mode="lines",
                                line=dict(
                                    width=1.5,  # Line width
                                    color="rgba(255, 200, 0, 0.15)",  # Line color
                                ),
                                name=f"Signal to {gateway_pos.name_of_gateway}",
                                showlegend=True,  # Hide legend for these lines
                            )
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
