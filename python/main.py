# Fetch LoRa Signals

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
        print(msg)


    if 'device_eui' in msg:
        if not muting:
            print("[Parser]: This is a known device!")
            print("[Parser]: Device name: ", msg['device_name'])

        # check if device_euid is in the csv file


        if msg['device_eui'] in sensor_data['Sensor_Eui'].values:
            if not muting:
                print("[Parser]: Device EUI found in CSV file!")

        # get sensor eui and gateway euid
        sensor_eui = msg['device_eui']
        gateway_eui = msg['gateway'].replace(":", "")

        lon, lat = 0, 0
        known = False

        # check if device_euid is in the csv file
        if msg['device_eui'] in sensor_data['Sensor_Eui'].values:
            known = True
            if not muting:
                print("[Parser]: Device EUI found in CSV file!")
            lon = sensor_data["St_X"][sensor_data['Sensor_Eui'] == sensor_eui].values[0]
            lat = sensor_data["St_Y"][sensor_data['Sensor_Eui'] == sensor_eui].values[0]

        # check if theres a sensor with the same eui and gatewate eui in the list
        sensor = next((s for s in sensors if s.get_sensor_id() == sensor_eui), None)
        incomming_signal = Signal(gateway_eui, msg['rssi'])

        # add a new sensor object to the list
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
            sensor.nr_of_packets += 1
            if not muting:
                print("[Parser]: Sensor already in list, incrementing packet count")

        # add the signal to the sensor
        sensor.add_signal(incomming_signal)
        if not muting:
            print("[Parser]: incoming distance ", incomming_signal.distance)

        # check if gateway is known
        if(gateway_eui in gateway_data['eui'].values):


            # add gateway to the list
            gateway = next((g for g in gateways if g.get_gateway_id() == gateway_eui), None)
            if gateway is None:
                lon_g = float(gateway_data['longitude'][gateway_data['eui'] == gateway_eui].values[0])
                lat_g = float(gateway_data['latitude'][gateway_data['eui'] == gateway_eui].values[0])
                altitude = float(gateway_data['altitude'][gateway_data['eui'] == gateway_eui].values[0])


                gateway = Gateway(
                    gateway_data['name'][gateway_data['eui'] == gateway_eui].values[0].strip(),
                    gateway_eui,
                    lon_g,
                    lat_g,
                    altitude,
                )

                gateways.append(gateway)
                print("[Parser]: \033[92mAdded new gateway to list\033[0m")

    else:
        if not muting:
            print("[Parser]: No device EUI found")
        # check if the sensor is in the list



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
                handle_message(sensors, gateways, msg, sensor_data, gateway_data, muting=True)

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

