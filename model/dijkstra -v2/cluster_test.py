import os
from datetime import datetime, timedelta
from sklearn.cluster import DBSCAN
import matplotlib.pyplot as plt
import numpy as np
import folium
from Data_loader import load_data
from Order import cluster_orders_hierarchical


def visualize_clusters(orders, labels, header, file_name):
    """
    可视化聚类结果

    参数:
    - orders: Order对象的列表
    - labels: 聚类标签
    - header: 包含仓库信息的字典
    - file_name: 保存文件的名称
    """
    try:
        print("Initializing map...")
        # 初始化地图
        m = folium.Map(location=header['warehouse_coords'], zoom_start=12)

        print("Defining colors...")
        # 定义颜色
        colors = [
            'red', 'blue', 'green', 'purple', 'orange', 'darkred', 'lightred',
            'beige', 'darkblue', 'darkgreen', 'cadetblue', 'pink', 'lightblue',
            'lightgreen', 'gray', 'black', 'lightgray'
        ]

        print("Adding warehouse marker...")
        # 添加仓库标记，使用特殊图标
        folium.Marker(
            location=header['warehouse_coords'],
            popup="Warehouse",
            icon=folium.Icon(color='blue', icon='info-sign')
        ).add_to(m)

        print("Adding order markers...")
        # 添加订单标记，使用小圆点
        for order, label in zip(orders, labels):
            color = colors[label % len(colors)] if label != -1 else 'black'
            folium.CircleMarker(
                location=(order.receiving_latitude, order.receiving_longitude),
                radius=5,
                color=color,
                fill=True,
                fill_color=color,
                fill_opacity=0.6,
                popup=f"Order: {order.order_code}\nCluster: {label}"
            ).add_to(m)

        print(f"Saving map to {file_name}...")
        # 保存地图
        m.save(file_name)
        print(f"Map saved successfully to {file_name}.")
    except Exception as e:
        print(f"An error occurred while visualizing clusters: {e}")


if __name__ == "__main__":
    # 调用函数读取数据
    orders, header = load_data('北京712单.txt')

    if orders and header:
        # 进行层次聚类，尝试不同的距离阈值
        output_dir = os.path.dirname(os.path.abspath(__file__))
        for distance_threshold in [0.5, 1.0, 1.5, 2.0]:
            print(f"Trying distance_threshold={distance_threshold}")
            labels = cluster_orders_hierarchical(orders, distance_threshold=distance_threshold)

            # 统计每个簇的数量
            unique_labels, counts = np.unique(labels, return_counts=True)
            print("Cluster distribution:", dict(zip(unique_labels, counts)))

            # 可视化聚类结果
            file_name = os.path.join(output_dir, f'clusters_map_threshold_{distance_threshold}.html')
            visualize_clusters(orders, labels, header, file_name)
            print(f"Cluster visualization saved as {file_name}")
    else:
        print("Failed to load data.")
