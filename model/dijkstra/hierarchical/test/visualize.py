import folium

 # 将路径绘制在地图上
def plot_route_on_map(location_collect, shortest_path):
    # 创建一个folium地图对象, 初始位置设为仓库的位置
    map_center = [location_collect[0][1], location_collect[0][2]]
    route_map = folium.Map(location=map_center, zoom_start=10, tiles=None)

    # 添加黑色背景
    folium.TileLayer(
        tiles='https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png',
        attr='Map tiles by Carto, under CC BY 3.0. Data by OpenStreetMap, under ODbL.',
        name='Dark Background',
        control=False,
        overlay=True
    ).add_to(route_map)
    
    # 创建一个字典, 方便通过地址快速查找经纬度和区域
    location_dict = {loc[0]: loc[1:] for loc in location_collect}
    
    # 为每条路径创建一个不同颜色的线条
    colors = ["cyan", "lime", "magenta", "yellow", "lightred", "lightblue", "lightgreen"]
    
    # 标记仓库位置
    warehouse = ["北京市顺义区顺平路576号", 40.1196490409737, 116.60616697651679, "仓库"]
    folium.CircleMarker(
        location=[warehouse[1], warehouse[2]],
        radius=15,  # 圆点半径
        color="red",  # 圆点颜色
        fill=True,
        fill_color="red",
        fill_opacity=0.9,
        popup=folium.Popup(f'<div style="white-space: nowrap;">{warehouse[0]}</div>', max_width=300)
    ).add_to(route_map)
    
    # 遍历shortest_path中的每个子列表
    for index, path in enumerate(shortest_path):
        # 存储路径的经纬度
        route_coords = []
        
        # 通过地址查找经纬度并添加到路径坐标列表中
        for address in path:
            if address in location_dict:
                latitude, longitude, _ = location_dict[address]
                route_coords.append([latitude, longitude])
        
        # 只有在路径坐标列表不为空时绘制路径
        if route_coords:
            # 添加路径线条到地图, 并设置颜色, 宽度和透明度
            folium.PolyLine(route_coords, color=colors[index % len(colors)], weight=5, opacity=0.8).add_to(route_map)
            
            # 为每个路径点添加小的彩色点
            for i, (coord, address) in enumerate(zip(route_coords, path)):
                if coord:
                    if i == 0:  # 路径的第一个点用正方形标记
                        folium.RegularPolygonMarker(
                            location=coord,
                            number_of_sides=4,
                            radius=8,  # 正方形边长
                            color=colors[index % len(colors)],  # 正方形颜色
                            fill=True,
                            fill_color=colors[index % len(colors)],
                            fill_opacity=0.8,
                            popup=folium.Popup(f'<div style="white-space: nowrap;">{address}</div>', max_width=300)
                        ).add_to(route_map)
                    else:  # 其他点用圆形标记
                        folium.CircleMarker(
                            location=coord,
                            radius=5,  # 圆点半径
                            color=colors[index % len(colors)],  # 圆点颜色
                            fill=True,
                            fill_color=colors[index % len(colors)],
                            fill_opacity=0.8,
                            popup=folium.Popup(f'<div style="white-space: nowrap;">{address}</div>', max_width=300)
                        ).add_to(route_map)
        
    # 保存地图到文件
    route_map.save("route_map.html")

# 示例数据
location_collect = [["北京市顺义区顺平路576号", 40.1196490409737, 116.60616697651679, "仓库"], 
                    ["北京市密云县古北口镇司马台村国际休闲旅游度假区第一层101单元", 40.662436, 117.251497, "密云区"],
                    ["北京市大兴区区西红门宏福路鸿坤生活广场", 39.797382, 116.346796, "大兴区"],
                    ["北京市大兴区黄村东大街38号院2号楼1层（01）内1F-11", 39.73531, 116.349419, "大兴区"],
                    ["北京市大兴区金星西路3号", 39.770126, 116.340761, "大兴区"],
                    ["北京市大兴区西红门镇欣宁大街15号1层1-01-28-R号", 39.795298, 116.33387, "大兴区"],
                    ["北京市密云区密云镇鼓楼南大街1号1层的1129-F1A005、1129-F1-A004、1129-F1-B008店铺", 40.380933, 116.852228, "密云区"],
                    ["北京市密云区滨河路178号万象汇一层", 40.361323, 116.841688, "密云区"],
                    ["北京市东城区北京市东城区朝阳门北大街8号2号楼1层2-58", 39.936825, 116.442792, "东城区"],
                    ["北京市东城区广渠家园3号楼1层", 39.898703, 116.454626, "东城区"],
                    ["北京市东城区东直门南大街1号2层1-1202内P02-20商铺", 39.946079, 116.43794, "东城区"],
                    ["北京市大兴区旧宫镇旧宫西路3号(物美超市左侧)", 39.811108, 116.449658, "大兴区"],
                    ["北京市东城区光明路11号天玉大厦1层西侧", 39.890756, 116.443508, "东城区"],
                    ["北京市东城区新中街瑞士公寓1、2层L103&L202A", 39.938815, 116.443489, "东城区"],
                    ["北京市昌平区南口镇陈庄村(京藏高速北侧)八达岭奥特莱斯F2", 40.240958, 116.176189, "昌平区"],
                    ["北京市昌平区立汤路186号院1号楼02层(02)201内208单元", 40.104742, 116.419048, "昌平区"],
                    ["北京市昌平区立汤路186号院1号楼B1层B1041", 40.104742, 116.419048, "昌平区"],
                    ["北京市昌平区立汤路188号院1号万优汇商厦1层", 40.063747, 116.421787, "昌平区"],
                    ["北京市昌平区陈家营西路3号院23号楼 招商嘉铭珑原商业楼 1层101-2单元", 40.04709, 116.407605, "昌平区"],
                    ["北京市昌平区黄平路19号院1号楼B单元101-02室", 40.07174, 116.353812, "昌平区"],
                    ["北京市昌平区南口镇陈庄村(京藏高速北侧)八达岭奥特莱斯F2", 40.240958, 116.176189, "昌平区"]]

shortest_path = [
    ["北京市东城区东直门南大街1号2层1-1202内P02-20商铺", "北京市东城区新中街瑞士公寓1、2层L103&L202A", "北京市东城区北京市东城区朝阳门北大街8号2号楼1层2-58", "北京市东城区广渠家园3号楼1层", "北京市东城区光明路11号天玉大厦1层西侧"],
    ["北京市昌平区立汤路186号院1号楼B1层B1041", "北京市昌平区立汤路186号院1号楼02层(02)201内208单元"],
    ["北京市大兴区旧宫镇旧宫西路3号(物美超市左侧)", "北京市大兴区黄村东大街38号院2号楼1层（01）内1F-11", "北京市大兴区金星西路3号", "北京市大兴区西红门镇欣宁大街15号1层1-01-28-R号"], 
    ["北京市密云区滨河路178号万象汇一层", "北京市密云县古北口镇司马台村国际休闲旅游度假区第一层101单元", "北京市密云区密云镇鼓楼南大街1号1层的1129-F1A005、1129-F1-A004、1129-F1-B008店铺"]
]

plot_route_on_map(location_collect, shortest_path)
