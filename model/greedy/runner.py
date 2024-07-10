
from Data_loader import load_data, classify_orders_by_district
from Greedy import greedy_algorithm
from visualize import plot_all_routes
from intersecting import find_self_intersecting_vehicles


def print_vehicle_paths(vehicles):
    total_orders_in_vehicles = 0
    count = 0
    for i, vehicle in enumerate(vehicles):
        print(f"Vehicle {i + 1}:")
        if(len(vehicle.path) == 1): count += 1
        for order in vehicle.path:

            print(f"  Receiving Address: {order.receiving_address}")
            print(f"  Receiving District: {order.receiving_district}")
            print(f"  Weight: {order.weight} kg")
            print(f"  Volume: {order.volume} m^3")
        weight_rate = vehicle.get_weight_rate()
        volume_rate = vehicle.get_volume_rate()

        print(f"Weight Rate: {weight_rate}")
        print(f"Volume Rate: {volume_rate}")
        total_orders_in_vehicles += len(vehicle.path)

    print(count)

    return total_orders_in_vehicles


def main():
    # 读取数据文件
    file_path = '北京712单.txt'  # 替换为你的数据文件路径
    orders, header = load_data(file_path)
    total_distance = 0.0

    if orders is None or header is None:
        print("Failed to load data.")
        return

    # 运行贪心算法
    vehicles = greedy_algorithm(orders, header)

    # vehicles = find_self_intersecting_vehicles(vehicles)



    # 打印路径并统计订单总数
    total_orders_in_vehicles = print_vehicle_paths(vehicles)

    for i, vehicle in enumerate(vehicles):
        total_distance += vehicle.total_distance
    # 检查所有车辆中的订单总数是否等于原始订单数量
    total_orders = len(orders)
    print(f"Total orders in vehicles: {total_orders_in_vehicles}")
    print(f"Total orders in input data: {total_orders}")
    print(f"Total number of vehicles: {len(vehicles)}")
    print(f"Total distance: {total_distance} km")

    # assert total_orders == total_orders_in_vehicles, "Mismatch in order counts!"

    plot_all_routes(vehicles, 'output/北京712单.html')


if __name__ == "__main__":
    main()
