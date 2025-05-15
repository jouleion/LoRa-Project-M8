# Fetch LoRa Signals

# own script imports
from signals import Sensor, Gateway
from mapper import Mapper

# library imports
from websockets.sync.client import connect
import json
import pandas as pd
import threading



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

def websocket_handler(sensors, gateways, sensor_data, mapper):
    running = True
    num_of_packets = 0

    # make websocket connection
    with connect("ws://192.87.172.71:1337") as websocket:

        # keep on looping
        while running:
            msg = websocket.recv()
            try:
                # Decode the message
                msg = json.loads(msg)
                handle_message(sensors, gateways, msg, sensor_data)
                # show the sensors on a leaflet map
                print("just handled message")
                mapper.update(sensors, gateways)

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


def main():

    sensors = []
    gateways = []

    # init the mapper
    mapper = Mapper()

    sensor_data = pd.read_csv('data/sensor_locations.csv')
    sensor_data['Sensor_Eui'] = sensor_data['Sensor_Eui'].astype(str).str.replace(":", "")

    # start the websocket handler in a new thread
    websocket_thread = threading.Thread(
        target=websocket_handler,
        daemon=True,
        args=(sensors, gateways, sensor_data, mapper)
    )
    websocket_thread.start()

    # And start the server on port 8050. Do this in the main thread
    mapper.app.run(debug=True, port=8050)







if __name__ == "__main__":
    # start main loop
    main()

