# import map libraries here

class Mapper:
    def __init__(self):
        self.sensors = []
        self.gateways = []

        # create instance of the live map here

    def update(self, sensors, gateways):
        self.sensors = sensors
        self.gateways = gateways

        # Print status (optional)
        # for sensor in self.sensors:
            # print(f"Sensor: {sensor.get_sensor_id()} - {sensor.get_long_lat()}")
        # for gateway in self.gateways:
            # print(f"Gateway: {gateway.get_gateway_id()} - {gateway.get_long_lat()}")


        # Here we draw the live map



if __name__ == "__main__":
    # we already import this in main, so only when just running this file to we need to import
    from signals import Sensor, Gateway

    # Example data
    sensors = [
        Sensor("Sensor1", "EUI1", "Gateway1", 52.0, 4.0, 0.5),
        Sensor("Sensor2", "EUI2", "Gateway2", 52.1, 4.1, 0.6)
    ]
    gateways = [
        Gateway("Gateway1", "EUI1", 52.0, 4.0, 10),
        Gateway("Gateway2", "EUI2", 52.1, 4.1, 20)
    ]

    mapper = Mapper()
    mapper.update(sensors, gateways)  # Initial draw



