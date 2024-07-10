from shapely.geometry import LineString
from typing import List


def get_path_line(vehicle) -> LineString:
    coords = [(order.receiving_latitude, order.receiving_longitude) for order in vehicle.path]
    if len(coords) < 2:
        return None
    return LineString(coords)


def find_self_intersecting_vehicles(vehicles: List) -> List:
    self_intersecting_vehicles = []

    for vehicle in vehicles:
        path = get_path_line(vehicle)
        if path is None:
            continue
        # 检查路径是否自交叉
        if not path.is_simple:
            self_intersecting_vehicles.append(vehicle)

    return self_intersecting_vehicles
