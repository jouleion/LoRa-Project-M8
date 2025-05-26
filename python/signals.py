# sensor class
#     eui_of_sensor
#     name_of_sensor
#     longitude
#     latitude
#     eui_of_gateway
#     time of flight
#     altitude
#     RSSI
from math import cos, radians
import numpy as np
from scipy.optimize import curve_fit
from geopy.distance import geodesic

#Global parameters used for rssi based distance calculation
#Should be global so all sensors can use the same information
transmition_power = 14
n = 3.0 #path loss exponent, tuneable range [2; 3.5]
true_distances = []
RSSIs = []


class Signal:
    def __init__(self,  eui_of_gateway, RSSI, lon, lat,):
        self.eui_of_gateway = eui_of_gateway


        self.RSSI = RSSI
        self.distance= self.distance_estimate()

        self.lon = lon  # longitude of gateway
        self.lat = lat  # lattitude of gateway



    def distance_estimate(self):
        # max is 14dB. recieved signal strength usually negative. look a the attenuation we can find the distance.
        return 10 ** ((transmition_power - self.RSSI) / (10 * n))

class Sensor:
    def __init__(self, name_of_sensor, known, eui_of_sensor, lon, lat):
        self.eui_of_sensor = eui_of_sensor
        self.known = known

        #if we know the sensor from the csv file
        #we also store the known lat and lon
        if known:
            self.known_lon = lon  # longitude of sensor
            self.known_lat = lat  # latitude of sensor

        self.name_of_sensor = name_of_sensor
        self.lon = lon  #estimated longitude of sensor
        self.lat = lat  #estimated latitude of sensor

        self.nr_of_packets = 0

        #Array with all signals recieved from sensor
        self.raw_signals = []

        #Array with average signal for each gateway from senor
        self.avg_signals = []

    def rssi_model(self, d, path_loss_exponent):
        """"
                    rssi_model calculates RSSI based
                    based on the true distance and n
                """
        return transmition_power - 10 * path_loss_exponent * np.log10(d)

    def get_lon(self):
        return self.lon
    def pos_is_estimated(self):
        return len(self.avg_signals) >= 3
    def get_lat(self):
        return self.lat

    def get_known_lon(self):
        if self.known:
            return self.known_lon
        return self.lon

    def get_known_lat(self):
        if self.known:
            return self.known_lat
        return self.lat


    def xy_to_latlon(self, x, y, lat0_deg, lon0_deg):
        """"
            Converts a local 2D X,Y coordinate to a true global lat, lon
        """
        R = 6371000  # Earth radius in meters
        lat = lat0_deg + (y / R) * (180 / np.pi)
        lon = lon0_deg + (x / (R * np.cos(np.radians(lat0_deg)))) * (180 / np.pi)
        return lat, lon

    def latlon_to_xy(self, lat_deg, lon_deg, lat0_deg, lon0_deg):
        """"
            Converts a  true global lat, lon to a local 2D X,Y coordinate
        """
        R = 6371000  # Earth radius in meters
        x = (np.radians(lon_deg - lon0_deg)) * R * np.cos(np.radians(lat0_deg))
        y = (np.radians(lat_deg - lat0_deg)) * R
        return x, y

    def get_sensor_id(self):
        return self.eui_of_sensor
    def has_sensor_name(self):
        return self.name_of_sensor != ""

    def add_signal(self, signal):
        """"
            Adds a signal to the raw signal array and updates average signal array
            and updates the parameters used in the distance calculation if the sensor is known
            and calculates estimated location if more than 3 gateways connected
        """


        #if we know the actual location
        if self.known:
            #update the global variables
            global n
            global RSSIs
            global true_distances

            #add the RSSI and True distance
            RSSIs.append(signal.RSSI)
            true_distances.append(geodesic((self.known_lat, self.known_lon), (signal.lat, signal.lon)).meters)
            print(f'true distances: {true_distances[:5]}')
            #Fit the RSSI_model to the true distance and RSSI
            params, _ = curve_fit(self.rssi_model, true_distances, RSSIs, p0=[3])

            #Update n
            n = params[0]
            print(f'updated n: {n}')

        # add signal to the raw signals
        self.raw_signals.append(signal)

        # use signal to update the avg_signal array
        self.average_distances_to_gateway(signal)

        print(f'Connected to {len(self.avg_signals)}, different gateways \n')

        #if signal recieved by 3 different gateways
        if len(self.avg_signals) >= 3:
            #estimate the lat and lon
            self.lat, self.lon = self.multilateration(self.avg_signals)
            print(f'estimated lat, lon: {self.lat}; {self.lon}')


    def average_distances_to_gateway(self, new_signal):
        # Check if this gateway already has an average signal
        for avg_signal in self.avg_signals:
            if avg_signal.eui_of_gateway == new_signal.eui_of_gateway:
                # Count how many previous raw signals came from this gateway
                count = sum(1 for s in self.raw_signals if s.eui_of_gateway == new_signal.eui_of_gateway)
                # Compute new average
                previous_avg_distance = avg_signal.distance
                new_avg_distance = (previous_avg_distance * count + new_signal.distance) / (count + 1)
                print(f'average distance distance to {avg_signal.eui_of_gateway}, is: {new_avg_distance}')
                avg_signal.distance = new_avg_distance
                return

        # If not found, add new signal to avg_signals
        self.avg_signals.append(Signal(new_signal.eui_of_gateway, new_signal.RSSI, new_signal.lon,new_signal.lat))

    def multilateration(self, gateways):
        """"
            Finds a location based on the distance from each gateway
            I dont fully understand how the calculation works
        """
        # gateways: list of signals with (lat, lon, distance)
        lat0 = sum(g.lat for g in gateways) / len(gateways)
        lon0 = sum(g.lon for g in gateways) / len(gateways)

        positions = [self.latlon_to_xy(g.lat, g.lon, lat0, lon0) for g in gateways]
        distances = [g.distance for g in gateways]

        # Set up equations using the first as a reference
        x1, y1 = positions[0]
        r1 = distances[0]
        A = []
        b = []

        for i in range(1, len(positions)):
            xi, yi = positions[i]
            ri = distances[i]
            A.append([2 * (xi - x1), 2 * (yi - y1)])
            b.append((r1 ** 2 - ri ** 2) - (x1 ** 2 - xi ** 2 + y1 ** 2 - yi ** 2))

        A = np.array(A)
        b = np.array(b)

        # Weight inversely proportional to distance squared (more trust in nearby gateways)
        weights = 1 / (np.array(distances[1:]) ** 2)
        W = np.diag(weights)

        # Solve weighted least squares
        AtW = A.T @ W
        result = np.linalg.inv(AtW @ A) @ AtW @ b

        x, y = result

        # Convert back to lat/lon using inverse of latlon_to_xy
        lat, lon = self.xy_to_latlon(x, y, lat0, lon0)

        return lat, lon


# gateway
    #     name_of_gateway
    #     eui_gateway
    #     lon
    #     lat
    #     altitude

class Gateway:
    def __init__(self, name_of_gateway, eui_gateway, lon, lat, altitude):
        self.name_of_gateway = name_of_gateway
        self.eui_gateway = eui_gateway
        self.lon = lon
        self.lat = lat
        self.altitude = altitude

    def get_lon(self):
        return self.lon

    def get_lat(self):
        return self.lat

    def get_gateway_id(self):
        return self.eui_gateway

    def get_gateway_name(self):
        return self.name_of_gateway

    def get_gateway_altitude(self):
        return self.altitude
