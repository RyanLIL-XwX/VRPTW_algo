from datetime import datetime, timedelta
from sklearn.cluster import DBSCAN
import matplotlib.pyplot as plt
import numpy as np
from scipy.cluster.hierarchy import linkage, fcluster



class Order:
    def __init__(self, order_code, receiving_address, receiving_latitude, receiving_longitude,
                 receiving_district, weight, volume, receiving_earliest_time, receiving_latest_time):
        self.order_code = order_code
        self.receiving_address = receiving_address
        self.receiving_latitude = float(receiving_latitude)
        self.receiving_longitude = float(receiving_longitude)
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


def cluster_orders_hierarchical(orders, distance_threshold=1.0):
    """
    对订单进行层次聚类

    参数:
    - orders: Order对象的列表
    - distance_threshold: 距离阈值，用于确定簇的数量

    返回:
    - labels: 每个订单的聚类标签
    """
    # 提取经纬度信息
    coords = np.array([(order.receiving_latitude, order.receiving_longitude) for order in orders], dtype=float)

    # 使用层次聚类进行聚类
    Z = linkage(coords, method='ward')  # 采用Ward方法进行层次聚类
    labels = fcluster(Z, t=distance_threshold, criterion='distance')

    return labels

