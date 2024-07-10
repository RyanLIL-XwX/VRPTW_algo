from datetime import datetime, timedelta

from model import Order


class Vehicle:
    def __init__(self, max_weight, max_volume, ):
        self.max_weight = max_weight
        self.max_volume = max_volume
        self.current_weight = 0.0
        self.current_volume = 0.0
        self.current_time = datetime.strptime("2024-01-01 00:00:00", "%Y-%m-%d %H:%M:%S")
        self.path = []

    def can_add_order(self, order_weight, order_volume, commute_time: timedelta,
                      earliest_time: datetime, latest_time: datetime):
        proposed_time = self.current_time + commute_time
        if (self.current_weight + order_weight <= self.max_weight and
                self.current_volume + order_volume <= self.max_volume and
                earliest_time <= proposed_time <= latest_time):
            return True
        return False

    def ability_check(self, order_weight, order_volume):
        if self.current_weight + order_weight <= self.max_weight and self.current_volume + order_volume <= self.max_volume:
            return True
        return False

    def time_check(self, commute_time: timedelta, earliest_time: datetime, latest_time: datetime):
        proposed_time = self.current_time + commute_time
        if earliest_time <= proposed_time <= latest_time:
            return True
        return False

    def add_order(self, order: Order, order_weight: float, order_volume: float,
                  stay_period: timedelta, commute_time: timedelta):
        self.path.append(order)
        self.current_weight += order_weight
        self.current_volume += order_volume
        self.current_time += commute_time + stay_period

    def get_current_order(self):
        if self.path:
            return self.path[-1]
        return None
