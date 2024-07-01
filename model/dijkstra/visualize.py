import folium

# 测试用的sudo data
location_data = {
    "warehouse": [39.9042, 116.4074],  # 北京的经纬度
    "order1_address": [39.9555, 116.3316],
    "order2_address": [39.9042, 116.4074],
    "order3_address": [39.8506, 116.3100]
}

# 测试
shortest_path = ["warehouse", "order1_address", "order2_address", "order3_address"]


# 绘制路径，保存为html
def plot_route(location_data, shortest_path, output_file='route_map.html'):
    # 创建地图对象
    m = folium.Map(location=location_data["warehouse"], zoom_start=12)

    # 添加路径上的每个节点
    for address in shortest_path:
        folium.Marker(location=location_data[address], popup=address).add_to(m)

    # 添加路径线
    path_coordinates = [location_data[address] for address in shortest_path]
    folium.PolyLine(locations=path_coordinates, color='blue').add_to(m)

    # 保存并展示地图
    m.save(output_file)
    print(f"Map has been saved to {output_file}")


if __name__ == "__main__":
    # test
    plot_route(location_data, shortest_path)
