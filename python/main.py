# Fetch LoRa Signals

from websockets.sync.client import connect
import json
import pandas as pd

def receive_data():
    max_msg = 10  # Feel free to change this or just let it loop forever. Maybe best to keep it low while testing...
    with connect("ws://192.87.172.71:1337") as websocket:
        count = 0
        while count < max_msg:
            msg = websocket.recv()
            try:
                msg = json.loads(msg)
                handle_message(msg)  # Call function to do the actual data handling
            except json.JSONDecodeError:
                print("Failed to decode json, assuming next packet will be ok...")
                pass
            except Exception as e:
                # Assume something went wrong and stop receiving
                print("Something went horribly wrong!")
                print("Error:", e)
                break

            count += 1
        print("Received %d messages!" % count)


def handle_message(msg):
    print("Received packet with rssi: %d." % msg['rssi'])
    print(msg)
    if 'device_eui' in msg:
        print("This is a known device!")
        print("Device name: ", msg['device_name'])
    print()

    cross_reference_with_csv(msg)


def cross_reference_with_csv(msg):
    # Load data files
    gate_way_locations = pd.read_csv('data/gateway_locations.csv')
    sensor_locations = pd.read_csv('data/sensor_locations.csv')


    # Get sensor data
    sensor = sensor_locations[sensor_locations['Sensor_Eui'] == msg['device_eui']].iloc[0]
    gateway_row = gate_way_locations[gate_way_locations['eui'] == msg['gateway'].replace(":", "")]
    if not gateway_row.empty:
        gateway = gateway_row.iloc[0]
    else:
        print("No matching gateway found!")
        return

    # Extract coordinates
    sensor_lat, sensor_lon = sensor['St_X'], sensor['St_Y']
    gateway_lat, gateway_lon = gateway['latitude'], gateway['longitude']

    # Generate Leaflet map
    html = f"""
    <html>
    <head>
        <title>LoRa Device Map</title>
        <link rel="stylesheet" href="https://unpkg.com/leaflet/dist/leaflet.css" />
        <script src="https://unpkg.com/leaflet/dist/leaflet.js"></script>
    </head>
    <body>
        <div id="map" style="height: 600px"></div>
        <script>
            var map = L.map('map').setView([{sensor_lat}, {sensor_lon}], 16);
            L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png').addTo(map);

            L.marker([{sensor_lat}, {sensor_lon}])
                .bindPopup('Sensor: {msg['device_name']}')
                .addTo(map);

            L.marker([{gateway_lat}, {gateway_lon}])
                .bindPopup('Gateway: {gateway['gateway_name']}')
                .addTo(map);

            L.polyline([[{sensor_lat}, {sensor_lon}], [{gateway_lat}, {gateway_lon}]], 
                      {{color: 'red'}}).addTo(map);
        </script>
    </body>
    </html>
    """

    with open('output/map.html', 'w') as f:
        f.write(html)
    print("Generated device map")


if __name__ == "__main__":
    # Call the function to start receiving data
    receive_data()