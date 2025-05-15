# sensor class
#     eui_of_sensor
#     name_of_sensor
#     longditude
#     latitude
#     eui_of_gateway
#     time of flight
#     altitude
#     RSSI

#Parameters used for rssi based distance calculation
transmition_power = 14
n = 3.0 #path loss exponent, tuneable range [2; 3.5]
class Signal:
    def __init__(self,  eui_of_gateway, RSSI):
        self.eui_of_gateway = eui_of_gateway
        self.RSSI = RSSI
        self.distance= self.distance_estimate()

    def distance_estimate(self):
        return 10 ** ((transmition_power - self.RSSI) / (10 * n))

class Sensor:
    def __init__(self, name_of_sensor, known, eui_of_sensor, long, lat, time_of_flight):
        self.eui_of_sensor = eui_of_sensor
        self.known = known
        self.name_of_sensor = name_of_sensor
        self.long = long
        self.lat = lat
        self.time_of_flight = time_of_flight
        self.nr_of_packets = 0
        self.raw_signals = []
        self.avg_signals = []

    def get_long(self):
        return self.long

    def get_lat(self):
        return self.lat

    def get_sensor_id(self):
        return self.eui_of_sensor
    def has_sensor_name(self):
        return self.name_of_sensor != ""

    def add_signal(self, signal):
        self.raw_signals.append(signal)

    # def average_distances_to_gateway(self):
    #     for s in self.raw_singals:
    #         if s.gateway_eui in self.avg_signals.gateway_eui:
    #             number_of_signal_at_gateway = len(self.raw_singals[i for i in self.raw_signals if i == s.gateway_eui])
    #             previous_avg_distance = self.avg_signal[i for i in self.avg_signals if i == s.gateway_eui].distance
    #



# gateway
    #     name_of_gateway
    #     eui_gateway
    #     long
    #     lat
    #     altitude

class Gateway:
    def __init__(self, name_of_gateway, eui_gateway, long, lat, altitude):
        self.name_of_gateway = name_of_gateway
        self.eui_gateway = eui_gateway
        self.long = long
        self.lat = lat
        self.altitude = altitude

    def get_long(self):
        return self.long

    def get_lat(self):
        return self.lat

    def get_gateway_id(self):
        return self.eui_gateway

    def get_gateway_name(self):
        return self.name_of_gateway

    def get_gateway_altitude(self):
        return self.altitude
