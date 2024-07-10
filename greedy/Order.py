from datetime import datetime, timedelta


class Order:
    def __init__(self, order_code, receiving_address, receiving_latitude, receiving_longitude,
                 receiving_district, weight, volume, receiving_earliest_time, receiving_latest_time):
        self.order_code = order_code
        self.receiving_address = receiving_address
        self.receiving_latitude = receiving_latitude
        self.receiving_longitude = receiving_longitude
        self.receiving_district = receiving_district
        self.weight = weight
        self.volume = volume
        self.receiving_earliest_time = datetime.strptime(receiving_earliest_time, "%Y-%m-%d %H:%M:%S")
        self.receiving_latest_time = datetime.strptime(receiving_latest_time, "%Y-%m-%d %H:%M:%S")

    def print_all(self):
        print(f"Order Code: {self.order_code}")
        print(f"Receiving Address: {self.receiving_address}")
        print(f"Latitude: {self.receiving_latitude}")
        print(f"Longitude: {self.receiving_longitude}")
        print(f"District: {self.receiving_district}")
        print(f"Weight: {self.weight}")
        print(f"Volume: {self.volume}")
        print(f"Receiving Earliest Time: {self.receiving_earliest_time}")
        print(f"Receiving Latest Time: {self.receiving_latest_time}")

    def print_address(self):
        print(f"Receiving Address: {self.receiving_address}")
        print(f"Latitude: {self.receiving_latitude}")
        print(f"Longitude: {self.receiving_longitude}")
        print(f"District: {self.receiving_district}")
