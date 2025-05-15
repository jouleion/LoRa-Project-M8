# Fetch LoRa Signals

# own script imports
from signals import Sensor, Gateway
from mapper import Mapper

# library imports
from websockets.sync.client import connect
import json
import pandas as pd

# def receive_data():
#     max_msg = 10  # Feel free to change this or just let it loop forever. Maybe best to keep it low while testing...
#     with connect("ws://192.87.172.71:1337") as websocket:
#         count = 0
#         while count < max_msg:
#             msg = websocket.recv()
#             try:
#                 msg = json.loads(msg)
#                 handle_message(msg)  # Call function to do the actual data handling
#             except json.JSONDecodeError:
#                 print("Failed to decode json, assuming next packet will be ok...")
#                 pass
#             except Exception as e:
#                 # Assume something went wrong and stop receiving
#                 print("Something went horribly wrong!")
#                 print("Error:", e)
#                 break
#
#             count += 1
#         print("Received %d messages!" % count)





# def cross_reference_with_csv(msg):
#     # Load data files
#     gate_way_locations = pd.read_csv('data/gateway_locations.csv')
#     sensor_locations = pd.read_csv('data/sensor_locations.csv')




    #
    # # Get sensor data
    # sensor = sensor_locations[sensor_locations['Sensor_Eui'] == msg['device_eui']].iloc[0]
    # gateway_row = gate_way_locations[gate_way_locations['eui'] == msg['gateway'].replace(":", "")]
    # if not gateway_row.empty:
    #     gateway = gateway_row.iloc[0]
    # else:
    #     print("No matching gateway found!")
    #     return
    #
    # # Extract coordinates
    # sensor_lat, sensor_lon = sensor['St_X'], sensor['St_Y']
    # gateway_lat, gateway_lon = gateway['latitude'], gateway['longitude']
    #
    # # Generate Leaflet map
    # html = f"""
    # <html>
    # <head>
    #     <title>LoRa Device Map</title>
    #     <link rel="stylesheet" href="https://unpkg.com/leaflet/dist/leaflet.css" />
    #     <script src="https://unpkg.com/leaflet/dist/leaflet.js"></script>
    # </head>
    # <body>
    #     <div id="map" style="height: 600px"></div>
    #     <script>
    #         var map = L.map('map').setView([{sensor_lat}, {sensor_lon}], 16);
    #         L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png').addTo(map);
    #
    #         L.marker([{sensor_lat}, {sensor_lon}])
    #             .bindPopup('Sensor: {msg['device_name']}')
    #             .addTo(map);
    #
    #         L.marker([{gateway_lat}, {gateway_lon}])
    #             .bindPopup('Gateway: {gateway['gateway_name']}')
    #             .addTo(map);
    #
    #         L.polyline([[{sensor_lat}, {sensor_lon}], [{gateway_lat}, {gateway_lon}]],
    #                   {{color: 'red'}}).addTo(map);
    #     </script>
    # </body>
    # </html>
    # """
    #
    # with open('output/map.html', 'w') as f:
    #     f.write(html)
    # print("Generated device map")


def handle_message(sensors, gateways, msg, sensor_data):
    print("Received packet with rssi: %d." % msg['rssi'])
    print(msg)
    if 'device_eui' in msg:
        print("This is a known device!")
        print("Device name: ", msg['device_name'])

        # check if device_euid is in the csv file


        if msg['device_eui'] in sensor_data['Sensor_Eui'].values:
            print("Device EUI found in CSV file!")

            # get sensor eui and gateway euid
            sensor_eui = msg['device_eui']
            gateway_eui = msg['gateway'].replace(":", "")

            # check if theres a sensor with the same eui and gatewate eui in the list
            sensor = next((s for s in sensors if s.get_sensor_id() == sensor_eui and s.get_gateway_id() == gateway_eui), None)

            # add a new sensor object to the list
            if sensor is None:
                sensor = Sensor(
                    msg['device_name'],
                    sensor_eui,
                    gateway_eui,
                    sensor_data["St_X"][sensor_data['Sensor_Eui'] == sensor_eui].values[0],
                    sensor_data["St_Y"][sensor_data['Sensor_Eui'] == sensor_eui].values[0],
                    0
                )
                sensors.append(sensor)
                # print in green
                print("\033[92mAdded new sensor to list\033[0m")
            else:
                sensor.nr_of_packets += 1
                print("Sensor already in list, incrementing packet count")
        else:
            print("Device EUI not found in CSV file!")
            # check if the sensor is in the list


    print()



def main():
    running = True
    num_of_packets = 0
    sensors = []
    gateways = []

    # init the mapper, and start the server on port 8050
    mapper = Mapper()
    mapper.app.run(debug=True, port=8050)

    sensor_data = pd.read_csv('data/sensor_locations.csv')
    sensor_data['Sensor_Eui'] = sensor_data['Sensor_Eui'].astype(str).str.replace(":", "")

    # make websocket connection
    with connect("ws://192.87.172.71:1337") as websocket:

        # keep on looping
        while running:
            msg = websocket.recv()
            try:
                # Decode the message
                msg = json.loads(msg)
                handle_message(sensors, gateways, msg, sensor_data)

            except json.JSONDecodeError:
                print("Failed to decode json, assuming next packet will be ok...")
                pass

            except Exception as e:
                # Assume something went wrong and stop receiving
                print("Could not parse the message")
                print("Error:", e)
                break

            # Increment the packet count
            num_of_packets += 1

            # show the sensors on a leaflet map
            mapper.update(sensors, gateways)



if __name__ == "__main__":
    # start main loop
    main()

