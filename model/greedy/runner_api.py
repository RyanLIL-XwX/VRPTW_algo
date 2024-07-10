from flask import Flask, jsonify, request
from Data_loader import load_data, classify_orders_by_district
from Greedy import greedy_algorithm
from visualize import plot_all_routes
import os
import json

app = Flask(__name__)


def print_vehicle_paths(vehicles):
    total_orders_in_vehicles = 0
    vehicle_paths = []

    for i, vehicle in enumerate(vehicles):
        vehicle_info = {
            'vehicle_number': i + 1,
            'path': []
        }
        for order in vehicle.path:
            vehicle_info['path'].append({
                'receiving_address': order.receiving_address,
                'receiving_district': order.receiving_district,
                'weight': order.weight,
                'volume': order.volume
            })
        vehicle_paths.append(vehicle_info)
        total_orders_in_vehicles += len(vehicle.path)

    return total_orders_in_vehicles, vehicle_paths


@app.route('/run-greedy', methods=['POST'])
def run_greedy():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    if file:
        file_content = file.read().decode('utf-8')
        data = json.loads(file_content)
        orders, header = load_data(data)
        total_distance = 0.0

        if orders is None or header is None:
            return jsonify({"error": "Failed to load data."}), 400

        # 运行贪心算法
        vehicles = greedy_algorithm(orders, header)

        # 打印路径并统计订单总数
        total_orders_in_vehicles, vehicle_paths = print_vehicle_paths(vehicles)

        for vehicle in vehicles:
            total_distance += vehicle.total_distance

        # 检查所有车辆中的订单总数是否等于原始订单数量
        total_orders = len(orders)
        assert total_orders == total_orders_in_vehicles, "Mismatch in order counts!"

        output_path = 'output/sample.html'
        plot_all_routes(vehicles, output_path)

        result = {
            "total_orders_in_vehicles": total_orders_in_vehicles,
            "total_orders": total_orders,
            "total_vehicles": len(vehicles),
            "total_distance": total_distance,
            "vehicle_paths": vehicle_paths,
            "output_map": os.path.abspath(output_path)
        }

        return jsonify(result)


if __name__ == "__main__":
    app.run(debug=True)
