import heapq
from typing import List, Dict, Tuple
from collections.abc import Set
from datetime import datetime, timedelta
from haversine import haversine, Unit
import copy
from Order import Order, cluster_orders_hierarchical
from Vehicle import Vehicle
from Data_loader import group_orders_by_cluster, classify_orders_by_district


def calculate_time(current_time: str, minutes: int, mode: str) -> str:
    if not current_time:
        raise ValueError("The input time is empty. Please provide a valid time string.")

    try:
        initial_time = datetime.strptime(current_time, "%Y-%m-%d %H:%M:%S")
    except ValueError as e:
        raise ValueError(f"Time data '{current_time}' does not match format '%Y-%m-%d %H:%M:%S'.") from e

    delta = timedelta(minutes=minutes)

    if mode == "+":
        new_time = initial_time + delta
    elif mode == "-":
        new_time = initial_time - delta
    else:
        raise ValueError("Mode should be '+' or '-'")

    return new_time.strftime("%Y-%m-%d %H:%M:%S")


def calculate_distance(location1, location2):
    return haversine((location1[0], location1[1]), (location2[0], location2[1]), unit=Unit.KILOMETERS)


# 先计算每个点直接的距离，存在dict里，等等就不用再算了
def precompute_distances(orders, warehouse):
    distances = {}
    locations = [(order, float(order.receiving_latitude), float(order.receiving_longitude)) for order in orders]
    warehouse_location = (warehouse, float(warehouse.receiving_latitude), float(warehouse.receiving_longitude))
    locations.append(warehouse_location)

    for i, loc1 in enumerate(locations):
        for j, loc2 in enumerate(locations):
            if i != j:
                distance = calculate_distance((loc1[1], loc1[2]), (loc2[1], loc2[2]))
                distances[(loc1[0], loc2[0])] = distance

    return distances


def get_sorted_orders_by_distance(orders: List[Order], current_location: Order,
                                  distances: Dict[Tuple[Order, Order], float]) -> List[Tuple[float, Order]]:
    order_distances = []

    for order in orders:
        if (current_location, order) in distances:
            distance = distances[(current_location, order)]
        elif (order, current_location) in distances:
            distance = distances[(order, current_location)]
        else:
            continue

        order_distances.append((distance, order))

    # Sort by distance in ascending order
    order_distances.sort(key=lambda x: x[0])

    return order_distances


def dijkstra(distances: Dict[Tuple[Order, Order], float], current_location: Order) -> List[Tuple[float, Order]]:
    """
    使用 Dijkstra 算法计算从起点到所有节点的最短路径，并返回访问所有节点的顺序列表。

    :param distances: 一个字典，键是两个 Order 对象的元组，值是它们之间的距离
    :param current_location: 起始 Order 对象
    :return: 从起点访问所有其他节点的顺序列表，每个元素是一个元组，包含距离和 Order 对象
    """
    # 创建图的邻接表表示法
    graph = {}
    for (order1, order2), distance in distances.items():
        if order1 not in graph:
            graph[order1] = {}
        if order2 not in graph:
            graph[order2] = {}
        graph[order1][order2] = distance
        graph[order2][order1] = distance

    # 初始化距离字典，所有节点的初始距离为无穷大（假设为 float('inf')）
    distances_from_start = {order: float('inf') for order in graph}
    distances_from_start[current_location] = 0  # 起点的距离为 0

    # 初始化优先队列
    priority_queue = [(0, current_location)]  # (距离, Order对象)
    heapq.heapify(priority_queue)

    visited = set()
    order_of_visit = []

    while priority_queue:
        current_distance, current_order = heapq.heappop(priority_queue)

        if current_order in visited:
            continue

        visited.add(current_order)
        order_of_visit.append((current_distance, current_order))

        for neighbor, distance in graph[current_order].items():
            if neighbor in visited:
                continue
            new_distance = current_distance + distance
            if new_distance < distances_from_start[neighbor]:
                distances_from_start[neighbor] = new_distance
                heapq.heappush(priority_queue, (new_distance, neighbor))

    return order_of_visit


def create_new_vehicle(visited: Set[Order], orders: List[Order], warehouse: Order, header: dict,
                       distances: Dict[Tuple[Order, Order], float]) -> Vehicle:
    vehicle = Vehicle(
        max_weight=header['max_weight'],
        max_volume=header['max_volume']
    )
    sorted_from_warehouse = dijkstra(distances, warehouse)

    for distance, order in sorted_from_warehouse:
        if order not in visited:
            vehicle.path.append(order)
            vehicle.current_weight += order.weight
            vehicle.current_volume += order.volume
            vehicle.current_time = order.receiving_earliest_time
            visited.add(order)
            vehicle.total_distance += distance
            break

    return vehicle


def find_paths(orders: List[Order], header: dict):
    vehicles = []

    warehouse = Order(
        order_code="warehouse",
        receiving_address=header["warehouse_address"],
        receiving_latitude=header["warehouse_coords"][0],
        receiving_longitude=header["warehouse_coords"][1],
        receiving_district="warehouse",
        weight=0,
        volume=0,
        receiving_earliest_time="2024-01-01 00:00:00",
        receiving_latest_time="2024-01-01 00:00:00"
    )

    # district_orders = classify_orders_by_district(orders)
    labels = cluster_orders_hierarchical(orders, 0.5)
    clusters = group_orders_by_cluster(orders, labels)

    list_of_list = classify_orders_by_district(orders)

    for district, orders in list_of_list.items():
        if not orders:
            continue
        distances = precompute_distances(orders, warehouse)

        # Print distances for debugging
        # print(f"Distances for district {district}:")
        # for (order1, order2), distance in distances.items():
        #     print(f"  {order1.order_code} to {order2.order_code}: {distance} km")

        visited = set()

        current_vehicle = create_new_vehicle(visited, orders, warehouse, header, distances)

        current_order = current_vehicle.get_current_order()
        while len(orders) != len(visited):  # 还有没送完的订单
            sorted_orders = dijkstra(distances, current_order)
            for distance, order in sorted_orders:
                commute_time = timedelta(minutes=(distance / 40 * 60))
                if order not in visited and current_vehicle.time_check(commute_time,
                                                                       order.receiving_earliest_time,
                                                                       order.receiving_latest_time):
                    if current_vehicle.ability_check(order.weight, order.volume):
                        stay_period = timedelta(minutes=calculate_stay_period(order.weight, header))
                        current_vehicle.add_order(order, order.weight, order.volume,
                                                  stay_period, commute_time)
                        current_vehicle.total_distance += distance
                        visited.add(order)
                        current_order = order
                    else:
                        vehicles.append(copy.deepcopy(current_vehicle))
                        # print_vehicle(current_vehicle)  # 打印车辆信息
                        current_vehicle = create_new_vehicle(visited, orders, warehouse, header, distances)
                    break
                else:
                    continue
        vehicles.append(copy.deepcopy(current_vehicle))
        # print_vehicle(current_vehicle)  # 打印车辆信息
    return vehicles


def print_vehicle(vehicle):
    print("New Vehicle:")
    for order in vehicle.path:
        print(f"  Order Code: {order.order_code}")
        print(f"  Receiving Address: {order.receiving_address}")
        print(f"  Receiving District: {order.receiving_district}")
        print(f"  Weight: {order.weight} kg")
        print(f"  Volume: {order.volume} m^3")
        print(f"  Receiving Earliest Time: {order.receiving_earliest_time}")
        print(f"  Receiving Latest Time: {order.receiving_latest_time}")
    print()


def calculate_stay_period(weight, vehicle_info):
    return round(weight * vehicle_info['handoverVariableTime'] + vehicle_info['handoverFixedTime'])
