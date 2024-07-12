import time
from Data_loader import load_data, classify_orders_by_district
from Greedy import greedy_algorithm
from visualize import plot_all_routes
from intersecting import optimize_vehicle_routes, has_self_intersection


def print_vehicle_paths(vehicles):
    total_orders_in_vehicles = 0
    count = 0
    weight_full_rate_80 = 0
    volume_full_rate_80 = 0
    weight_full_rate_60 = 0
    volume_full_rate_60 = 0
    total_weight_rate = 0
    total_volume_rate = 0

    for i, vehicle in enumerate(vehicles):
        print(f"Vehicle {i + 1}:")
        if len(vehicle.path) == 1:
            count += 1
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

        total_weight_rate += weight_rate
        total_volume_rate += volume_rate

        if weight_rate >= 0.8:
            weight_full_rate_80 += 1
        if volume_rate >= 0.8:
            volume_full_rate_80 += 1
        if weight_rate <= 0.6:
            weight_full_rate_60 += 1
        if volume_rate <= 0.6:
            volume_full_rate_60 += 1

    num_vehicles = len(vehicles)
    avg_weight_rate = total_weight_rate / num_vehicles
    avg_volume_rate = total_volume_rate / num_vehicles

    print(f"孤点数量: {count}")
    print(f"重量满载率大于等于80%的占比: {weight_full_rate_80 / num_vehicles * 100:.2f}%")
    print(f"体积满载率大于等于80%的占比: {volume_full_rate_80 / num_vehicles * 100:.2f}%")
    print(f"重量满载率小于等于60%的占比: {weight_full_rate_60 / num_vehicles * 100:.2f}%")
    print(f"体积满载率小于等于60%的占比: {volume_full_rate_60 / num_vehicles * 100:.2f}%")
    print(f"平均重量满载率: {avg_weight_rate:.2f}")
    print(f"平均体积满载率: {avg_volume_rate:.2f}")

    return total_orders_in_vehicles


def main():
    start_time = time.time()  # 记录开始时间

    # 读取数据文件
    file_path = '北京712单.txt'  # 替换为你的数据文件路径
    orders, header = load_data(file_path)
    total_distance = 0.0

    if orders is None or header is None:
        print("Failed to load data.")
        return

    # 运行贪心算法
    vehicles = greedy_algorithm(orders, header)
    vehicles = optimize_vehicle_routes(vehicles)

    # 打印路径并统计订单总数
    total_orders_in_vehicles = print_vehicle_paths(vehicles)

    for i, vehicle in enumerate(vehicles):
        total_distance += vehicle.total_distance

    # 检查所有车辆中的订单总数是否等于原始订单数量
    total_orders = len(orders)
    print(f"输入订单总数: {total_orders}")
    print(f"输出订单总数: {total_orders_in_vehicles}")

    print(f"用车总数: {len(vehicles)}")
    print(f"总距离: {total_distance} km")

    # 统计有自交叉的路线数量
    intersecting_count = sum(has_self_intersection(vehicle.path) for vehicle in vehicles)
    print(f"Number of routes with self-intersection: {intersecting_count}")

    # assert total_orders == total_orders_in_vehicles, "Mismatch in order counts!"

    plot_all_routes(vehicles, 'output/北京712单.html')

    end_time = time.time()  # 记录结束时间
    elapsed_time = end_time - start_time  # 计算运行时间
    minutes = int(elapsed_time // 60)
    seconds = elapsed_time % 60
    print(f"跑跑竟然花了: {minutes} 分钟 {seconds:.2f} 秒！")


if __name__ == "__main__":
    main()
