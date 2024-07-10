import json
from Order import Order


def load_data(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
    except FileNotFoundError:
        print(f"File {file_path} not found.")
        return None, None
    except json.JSONDecodeError:
        print("Error decoding JSON from the file.")
        return None, None

    orders = []

    input_data = data.get("input", {})

    for order_data in input_data.get("orderList", []):
        order = Order(
            order_code=order_data.get("orderCode"),
            receiving_address=order_data.get("receivingAddress"),
            receiving_latitude=order_data.get("receivingLatitude"),
            receiving_longitude=order_data.get("receivingLongitude"),
            receiving_district=order_data.get("receivingDistrict"),
            weight=order_data.get("weight"),
            volume=order_data.get("volume"),
            receiving_earliest_time=order_data.get("receivingEarliestTime"),
            receiving_latest_time=order_data.get("receivingLatestTime")
        )
        orders.append(order)

    vehicle_data = input_data.get("vehicleType", {})
    warehouse = input_data.get("warehouse", {})
    if vehicle_data and warehouse:
        header = {
            "max_weight": vehicle_data.get("loadableWeight"),
            "max_volume": vehicle_data.get("loadableVolume"),
            "speed": input_data.get("parameter", {}).get("speed", 0),
            "warehouse_address": warehouse.get("address", ""),
            "handoverVariableTime": input_data.get("parameter", {}).get("handoverVariableTime", 0),
            "handoverFixedTime": input_data.get("parameter", {}).get("handoverFixedTime", 0),
            "warehouse_coords": (warehouse.get("latitude", 0), warehouse.get("longitude", 0))
        }

    return orders, header


def classify_orders_by_district(orders):
    districts = {
        "东城区": [],
        "西城区": [],
        "朝阳区": [],
        "丰台区": [],
        "石景山区": [],
        "海淀区": [],
        "门头沟区": [],
        "房山区": [],
        "通州区": [],
        "顺义区": [],
        "昌平区": [],
        "大兴区": [],
        "怀柔区": [],
        "平谷区": [],
        "密云区": [],
        "延庆区": []
    }

    for order in orders:
        if order.receiving_district in districts:
            districts[order.receiving_district].append(order)

    return districts


def group_orders_by_cluster(orders, labels):
    """
    将订单按聚类标签分组

    参数:
    - orders: Order对象的列表
    - labels: 聚类标签的列表

    返回:
    - grouped_orders: 一个字典，键是聚类标签，值是属于该簇的订单列表
    """
    grouped_orders = {}
    for order, label in zip(orders, labels):
        if label not in grouped_orders:
            grouped_orders[label] = []
        grouped_orders[label].append(order)
    return grouped_orders
