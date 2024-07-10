import os

import folium


def plot_all_routes(vehicles, output_file):
    # 创建输出文件夹
    output_dir = os.path.dirname(output_file)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # 创建地图对象，以第一个订单的地址为中心
    if not vehicles or not vehicles[0].path:
        print("No orders in vehicles.")
        return

    first_order = vehicles[0].path[0]
    m = folium.Map(location=[float(first_order.receiving_latitude), float(first_order.receiving_longitude)], zoom_start=12)

    # 添加高德地图图层
    folium.TileLayer(
        tiles='https://webrd0{s}.is.autonavi.com/appmaptile?lang=zh_cn&size=1&scl=1&style=8&x={x}&y={y}&z={z}',
        attr='高德地图',
        name='Amap',
        subdomains=['1', '2', '3', '4']
    ).add_to(m)

    # 添加每条路径上的每个节点和路径线
    colors = ['blue', 'green', 'red', 'purple', 'orange', 'darkred', 'lightred',
              'beige', 'darkblue', 'darkgreen', 'cadetblue', 'darkpurple',
              'white', 'pink', 'lightblue', 'lightgreen', 'gray', 'black', 'lightgray']
    for i, vehicle in enumerate(vehicles):
        color = colors[i % len(colors)]
        path_coordinates = [(float(order.receiving_latitude), float(order.receiving_longitude)) for order in vehicle.path]

        # 添加路径上的每个节点
        for order in vehicle.path:
            folium.CircleMarker(
                location=[float(order.receiving_latitude), float(order.receiving_longitude)],
                radius=3,  # 圆点的半径，可以调整
                color=color,
                fill=True,
                fill_color=color,
                fill_opacity=0.7,
                popup=order.receiving_address
            ).add_to(m)

        # 添加路径线
        folium.PolyLine(locations=path_coordinates, color=color).add_to(m)

    # 保存并展示地图
    folium.LayerControl().add_to(m)
    m.save(output_file)
    print(f"Map has been saved to {output_file}")

