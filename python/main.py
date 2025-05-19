# Fetch LoRa Signals
import math
import random

# own script imports
from signals import Signal, Sensor, Gateway
from mapper import Mapper

# library imports
from websockets.sync.client import connect
import json
import pandas as pd
import threading



def handle_message(sensors, gateways, msg, sensor_data, gateway_data, muting=False):
    if not muting:
        print("[Parser]: Received packet with rssi: %d." % msg['rssi'])
    if not muting:
        print("[Parser]: Received message (rssi): %d." % msg['rssi'])
        print(msg)

    # check if the message has a device eui
    if 'device_eui' not in msg:
        if not muting:
            print("[Parser]: No device EUI found")
        return

    # init variables for new sensor
    lat, lon = 52.2394, 6.8566
    known = False

    # check if device_euid is in the csv file
    if msg['device_eui'] not in sensor_data['Sensor_Eui'].values:
        if not muting:
            print("[Parser]: Unknown device EUI", msg['device_eui'])


    if not muting:
        print("[Parser]: Device found in csv (name): ", msg['device_name'])

    # get sensor eui and gateway euid
    sensor_eui = msg['device_eui']
    gateway_eui = msg['gateway'].replace(":", "")



    lon = 0
    lat = 0
    known = False

    # check if device_euid is in the csv file
    if msg['device_eui'] in sensor_data['Sensor_Eui'].values:
        temp_lon = sensor_data["St_X"][sensor_data['Sensor_Eui'] == sensor_eui].values[0],
        temp_lat = sensor_data["St_Y"][sensor_data['Sensor_Eui'] == sensor_eui].values[0],
        print(f'Lon: {temp_lon[0]}')
        print(f'Lat: {temp_lat[0]}')
        if (not math.isnan(temp_lon[0])) and (not math.isnan(temp_lon[0])) :
            known = True
            lon = temp_lon[0]
            lat = temp_lat[0]
        print("Device EUI found in CSV file!")





    # check if theres a sensor with the same eui and gatewate eui in the list
    sensor = next((s for s in sensors if s.get_sensor_id() == sensor_eui), None)


    # if this is a new sensor, add it to the list
    if sensor is None:
        sensor = Sensor(
            msg['device_name'],
            known,
            sensor_eui,
            lon,
            lat,
            0,
        )
        sensors.append(sensor)
        # print in green
        print("[Parser]: \033[92mAdded new sensor to list\033[0m")

    else:
        # if we already found this sensor, increment its packet count
        sensor.nr_of_packets += 1
        if not muting:
            print("[Parser]: Sensor already in list, incrementing packet count")

    # create a new signal for this sensor and add it to the sensor
    gate_lat = gateway_data["latitude"][gateway_data['eui'] == gateway_eui].values[0],
    gate_lon = gateway_data["longitude"][gateway_data['eui'] == gateway_eui].values[0],

    incomming_signal = Signal(gateway_eui, msg['rssi'], float(gate_lon[0]), float(gate_lat[0]))
    sensor.add_signal(incomming_signal)

    if not muting:
        print("[Parser]: incoming distance ", incomming_signal.distance)

    # check if gateway_eui is known (in csv)
    if gateway_eui in gateway_data['eui'].values:

        # add gateway to the list if its not already found
        gateway = next((g for g in gateways if g.get_gateway_id() == gateway_eui), None)
        if gateway is None:
            lon_g = float(gateway_data['longitude'][gateway_data['eui'] == gateway_eui].values[0])
            lat_g = float(gateway_data['latitude'][gateway_data['eui'] == gateway_eui].values[0])
            altitude = float(gateway_data['altitude'][gateway_data['eui'] == gateway_eui].values[0])

            # create a new gateway
            gateway = Gateway(
                gateway_data['name'][gateway_data['eui'] == gateway_eui].values[0].strip(),
                gateway_eui,
                lon_g,
                lat_g,
                altitude,
            )

            gateways.append(gateway)
            print("[Parser]: \033[92mAdded new gateway to list\033[0m")
    print()




def websocket_handler(sensors, gateways, sensor_data, gateway_data, mapper):
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
                handle_message(sensors, gateways, msg, sensor_data,gateway_data, muting=False)

                # show the sensors on a leaflet map
                mapper.update(sensors, gateways)

            except json.JSONDecodeError:
                print("[Parser]: Failed to decode json, assuming next packet will be ok...")
                pass

            except Exception as e:
                # Assume something went wrong and stop receiving
                print("[Parser]: Could not parse the message")
                print("[Parser]: Error:", e)
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

    gateway_data = pd.read_csv('data/gateway_locations.csv')


    # start the websocket handler in a new thread
    websocket_thread = threading.Thread(
        target=websocket_handler,
        daemon=True,
        args=(sensors, gateways, sensor_data, gateway_data, mapper)
    )
    websocket_thread.start()
    print("[Main]: Websocket thread started")

    # And start the server on port 8050. Do this in the main thread
    print("[Main]: Starting mapper server on port 8050")
    mapper.app.run(debug=True, port=8050)







if __name__ == "__main__":
    # start main loop
    main()

