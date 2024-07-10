from VRPTW import VRPTW_model

dijkstra = [[('北京市东城区东直门南大街1号2层1-1202内P02-20商铺', 0),
             ('北京市东城区新中街瑞士公寓1、2层L103&L202A', 0.9360571067903632),
             ('北京市东城区北京市东城区朝阳门北大街8号2号楼1层2-58', 1.1090289763242347),
             ('北京市东城区广渠家园3号楼1层', 5.456769547032478),
             ('北京市东城区光明路11号天玉大厦1层西侧', 6.1699452481750505)],
            [('北京市昌平区立汤路186号院1号楼02层(02)201内208单元', 0),
             ('北京市昌平区立汤路186号院1号楼B1层B1041', 0.0), ('北京市昌平区立汤路188号院1号万优汇商厦1层', 4.564394273478249),
             ('北京市昌平区陈家营西路3号院23号楼 招商嘉铭珑原商业楼 1层101-2单元', 6.484134235838884), ('北京市昌平区黄平路19号院1号楼B单元101-02室', 6.653186899464086),
             ('北京市昌平区南口镇陈庄村(京藏高速北侧)八达岭奥特莱斯F2(2)', 25.596754723689617), ('北京市昌平区南口镇陈庄村(京藏高速北侧)八达岭奥特莱斯F2', 25.596754723689617)],
            [('北京市大兴区旧宫镇旧宫西路3号(物美超市左侧)', 0), ('北京市大兴区区西红门宏福路鸿坤生活广场', 8.918459901215831),
             ('北京市大兴区西红门镇欣宁大街15号1层1-01-28-R号', 10.046243614793198),
             ('北京市大兴区金星西路3号', 10.360290427546989),
             ('北京市大兴区黄村东大街38号院2号楼1层（01）内1F-11', 12.017713069471931)],
            [('北京市密云区滨河路178号万象汇一层', 0),
             ('北京市密云区密云镇鼓楼南大街1号1层的1129-F1A005、1129-F1-A004、1129-F1-B008店铺', 2.356270405702512),
             ('北京市密云县古北口镇司马台村国际休闲旅游度假区第一层101单元', 48.179884605153944)]]
vrpt = VRPTW_model("/Users/shenhanxu/Desktop/凯捷实习/VRPTW_algo/model/dijkstra/sample.txt")


# 处理dijkstra算法的路径, 用于检查车载重量, 车载空间和时间是否可行
def process_dijkstra_path(all_path):
    final_path = list()  # 用于储存最终的路径
    check_weight = 0.0  # 用于检查车载重量是否可行
    check_volume = 0.0  # 用于检查车载空间是否可行
    arrive_time = ""  # 到达当前订单的时间(分钟)
    leave_time = ""  # 离开当前订单的时间(分钟)
    car_speed = vrpt.parameters["speed"]
    for order_path in all_path:
        pointer = 0  # 用改指针来获取需要分离的路径
        arrive_time = vrpt.get_receive_earliest_time(order_path[0][0])  # 到达当前订单的时间(分钟)
        for j in range(len(order_path)):
            check_weight += vrpt.calculate_weight(order_path[j][0])  # 计算车载重量
            check_volume += vrpt.calculate_volume(order_path[j][0])  # 计算车载空间
            leave_time = vrpt.calculate_leave_time(vrpt.calculate_stay_period(check_weight),
                                                   arrive_time)  # 离开当前订单的时间(分钟)
            arrive_time = vrpt.calculate_arrive_time(leave_time, order_path[j][1] / car_speed)  # 到达当前订单的时间(分钟
            if (vrpt.weight_availble(check_weight) == True and vrpt.volume_availble(
                    check_volume) == True and vrpt.time_arrive_availble_last(
                vrpt.get_receive_latest_time(order_path[j][0]), arrive_time) == True):
                pass
            else:
                final_path.append(order_path[pointer:j])
                pointer = j
                check_weight = 0.0
                check_volume = 0.0
            if (vrpt.time_arrive_availble_earliest(vrpt.get_receive_earliest_time(order_path[j][0]),
                                                   arrive_time) == False):
                arrive_time = vrpt.get_receive_earliest_time(order_path[j][0])
        if pointer < len(order_path):
            final_path.append(order_path[pointer:])
        # Append the remaining path segment after the loop

    processed_final_path = list()  # 用于储存处理后的最终路径
    for sublist in final_path:
        addresses = [address for address, _ in sublist]
        processed_final_path.append(addresses)
    return processed_final_path


if __name__ == "__main__":
    print(process_dijkstra_path(dijkstra))
