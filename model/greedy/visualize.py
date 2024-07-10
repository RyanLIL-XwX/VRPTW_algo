import os
import folium
from jinja2 import Template

def plot_all_routes(vehicles, output_file):
    access_token = 'pk.eyJ1IjoiaGFycmlzb25zeHUiLCJhIjoiY2xlcm0yZm5hMHUxbDN5cXJtNzdleGtpYSJ9.l6B08dUynQ89RYGkAn2qJg'

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

    # 使用Mapbox黑色背景图层
    tiles = f'https://api.mapbox.com/styles/v1/mapbox/dark-v10/tiles/{{z}}/{{x}}/{{y}}?access_token={access_token}'
    attr = 'Mapbox - 黑色'

    folium.TileLayer(
        tiles=tiles,
        attr=attr,
        name='Mapbox Dark',
    ).add_to(m)

    # 定义一些鲜艳的颜色
    colors = ['cyan', 'magenta', 'yellow', 'lime', 'orange', 'red', 'green', 'blue', 'purple', 'pink', 'lightblue',
              'lightgreen', 'gold', 'silver', 'crimson', 'violet']

    # 添加每条路径上的每个节点和路径线
    for i, vehicle in enumerate(vehicles):
        color = colors[i % len(colors)]
        path_coordinates = [(float(order.receiving_latitude), float(order.receiving_longitude)) for order in
                            vehicle.path]

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

    # 保存地图
    map_file = 'map.html'
    map_path = os.path.join(os.getcwd(), map_file)
    m.save(map_path)

    # 生成车辆信息表格
    table_rows = ""
    for i, vehicle in enumerate(vehicles):
        weight_rate = vehicle.get_weight_rate()
        volume_rate = vehicle.get_volume_rate()
        color = "red" if weight_rate < 0.8 or volume_rate < 0.8 else "black"
        table_rows += f"""
        <tr onclick="showVehicleDetails({i})" style="color: {color}; cursor: pointer;">
            <td>Vehicle {i + 1}</td>
            <td>{weight_rate:.2%}</td>
            <td>{volume_rate:.2%}</td>
        </tr>
        """

    vehicle_details = ""
    for i, vehicle in enumerate(vehicles):
        details = "<br>".join([f"{order.receiving_address}" for order in vehicle.path])
        weight_rate = vehicle.get_weight_rate()
        volume_rate = vehicle.get_volume_rate()
        vehicle_details += f"""
        <div id="vehicle{i}" class="vehicle-details" style="display: none;">
            <h3>Vehicle {i + 1} Details</h3>
            <p>Weight Rate: {weight_rate:.2%}</p>
            <p>Volume Rate: {volume_rate:.2%}</p>
            <p>Path:</p>
            <p>{details}</p>
        </div>
        """

    # 将地图和表格嵌入到HTML中
    html_template = Template("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Vehicle Routes</title>
        <style>
            body, html { margin: 0; padding: 0; width: 100%; height: 100%; }
            .vehicle-details { display: none; }
            #vehicleList { display: none; position: absolute; top: 10px; left: 10px; background: white; padding: 10px; border: 1px solid black; z-index: 1000; max-height: 90%; overflow-y: auto; }
            #map { height: 100%; }
            button { position: absolute; top: 10px; left: 10px; z-index: 1001; }
        </style>
        <script>
            function showVehicleDetails(vehicleIndex) {
                var details = document.getElementsByClassName('vehicle-details');
                for (var i = 0; i < details.length; i++) {
                    details[i].style.display = 'none';
                }
                document.getElementById('vehicle' + vehicleIndex).style.display = 'block';
            }

            function toggleVehicleList() {
                var vehicleList = document.getElementById('vehicleList');
                if (vehicleList.style.display === 'none') {
                    vehicleList.style.display = 'block';
                } else {
                    vehicleList.style.display = 'none';
                }
            }
        </script>
    </head>
    <body>
        <div id="map">
            <iframe src="{{ map_path }}" width="100%" height="100%" frameborder="0"></iframe>
        </div>
        <button onclick="toggleVehicleList()">Toggle Vehicle List</button>
        <div id="vehicleList">
            <h2>Vehicle List</h2>
            <table border="1">
                <tr>
                    <th>Vehicle</th>
                    <th>Weight Rate</th>
                    <th>Volume Rate</th>
                </tr>
                {{ table_rows }}
            </table>
            {{ vehicle_details }}
        </div>
    </body>
    </html>
    """)
    html_content = html_template.render(map_path=map_path, table_rows=table_rows, vehicle_details=vehicle_details)

    # 保存HTML文件
    with open(output_file, 'w') as f:
        f.write(html_content)

    print(f"HTML file has been saved to {output_file}")
