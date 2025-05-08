# sensor class
#     eui_of_sensor
#     name_of_sensor
#     longditude
#     latitude
#     eui_of_gateway
#     time of flight
#     altitude

class Sensor:
    def __init__(self, name_of_sensor, eui_of_sensor, eui_of_gateway, long, lat, time_of_flight):
        self.eui_of_sensor = eui_of_sensor
        self.name_of_sensor = name_of_sensor
        self.long = long
        self.lat = lat
        self.eui_of_gateway = eui_of_gateway
        self.time_of_flight = time_of_flight
        self.nr_of_packets = 0

    def get_long_lat(self):
        return self.long, self.lat

    def get_sensor_id(self):
        return self.eui_of_sensor

    def get_gateway_id(self):
        return self.eui_of_gateway

    def has_sensor_name(self):
        return self.name_of_sensor != ""



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

    def get_long_lat(self):
        return self.long, self.lat

    def get_gateway_id(self):
        return self.eui_gateway

    def get_gateway_name(self):
        return self.name_of_gateway

    def get_gateway_altitude(self):
        return self.altitude
