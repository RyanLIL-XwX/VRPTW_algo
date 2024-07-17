from dijkstra_VRPTW_district import VRPTW_model

if __name__ == "__main__":
    # 创建一个VRPTW_model对象, 并将file作为参数传入
    # 函数: load_data(), parse_data(), __str__()
    file = input("Type the name of the file: ").strip() # strip()函数用于去除字符串两端的空格
    order_data = VRPTW_model(file)
    # print(order_data)
        
    # 测试所有class中的基础函数
    def testbasic():
        #*
            # order data: VRPTW_model对象
            # location_collect: list容器(lists of list): [[address, latitude, longitude, district], ...]
            # location_collect: 除了仓库的信息: [address, latitude, longitude, "仓库"]
            #
            # distance_store: dictionary容器储存两点之间的距离: {距离: (address1, address2), ...}
            # distance_store_update: dictionary容器储存过滤后的两点之间的距离, 仅包含仓库的距离信息: {距离: (address1, address2), ...}
            # time_warehouse_leave: 仓库对特定地址的出发时间
        #*#
        
        # 测试对于经纬度信息的收集
        # 函数: collect_location_info(), calculate_distance()
        location_collect = order_data.collect_location_info()
        # print(location_collect)
        distance_store = order_data.calculate_distance(location_collect)
        # print(distance_store)
        
        # 测试对于location_collect中的信息的划分, 通过区的名称分别加入不同的容器中
        # 函数: location_collect_split()
        location_collect_dongcheng = []
        location_collect_xiacheng = []
        location_collect_chaoyang = []
        location_collect_fengtai = []
        location_collect_shijingshan = []
        location_collect_haidian = []
        location_collect_mentougou = []
        location_collect_fangshan = []
        location_collect_tongzhou = []
        location_collect_shunyi = []
        location_collect_changping = []
        location_collect_daxing = []
        location_collect_huairou = []
        location_collect_pinggu = []
        location_collect_miyun = []
        location_collect_yanqing = []
        location_collect_dongcheng, location_collect_xiacheng, location_collect_chaoyang, location_collect_fengtai,\
            location_collect_shijingshan, location_collect_haidian, location_collect_mentougou, location_collect_fangshan,\
            location_collect_tongzhou, location_collect_shunyi, location_collect_changping, location_collect_daxing,\
            location_collect_huairou, location_collect_pinggu, location_collect_miyun, location_collect_yanqing\
            = order_data.location_collect_split(location_collect)
        # print(location_collect_dongcheng, "\n", location_collect_xiacheng, "\n", location_collect_chaoyang, "\n",\
        #     location_collect_fengtai, "\n", location_collect_shijingshan, "\n", location_collect_haidian, "\n",\
        #     location_collect_mentougou, "\n", location_collect_fangshan, "\n", location_collect_tongzhou, "\n",\
        #     location_collect_shunyi, "\n", location_collect_changping, "\n", location_collect_daxing, "\n",\
        #     location_collect_huairou, "\n", location_collect_pinggu, "\n", location_collect_miyun, "\n",\
        #     location_collect_yanqing)
        # print(order_data.location_collect_split_district)
        distance_store_dongcheng = order_data.calculate_distance(location_collect_dongcheng)
        # print(distance_store_dongcheng)
        
        # 测试对所有订单信息通过knn算法进行分类
        # 函数: knn_classification()
        
        # 测试对于仓库出发信息的收集
        # 函数: warehouse_leave_info()
        distance_store_update = order_data.warehouse_leave_info(distance_store)
        # print(distance_store_update)
        time_warehouse_leave = order_data.time_warehouse_leave("北京市昌平区南口镇陈庄村(京藏高速北侧)八达岭奥特莱斯F2")
        # print(time_warehouse_leave)
        
        # 测试单个计算重量, 体积和停留时间的函数
        # 函数: calculate_weight(), calculate_stay_period()
        item_weight = order_data.calculate_weight("北京市昌平区南口镇陈庄村(京藏高速北侧)八达岭奥特莱斯F2")
        # print(item_weight)
        single_stay_period = order_data.calculate_stay_period(item_weight)
        # print(single_stay_period)
        item_volume = order_data.calculate_volume("北京市昌平区南口镇陈庄村(京藏高速北侧)八达岭奥特莱斯F2")
        # print(item_volume)
        
        # 测试单个计算到达时间和离开时间的函数
        # 函数: get_receive_earliest_time(), get_receive_latest_time()
        single_receive_time = order_data.get_receive_earliest_time("北京市昌平区南口镇陈庄村(京藏高速北侧)八达岭奥特莱斯F2")
        # print(single_receive_time)
        single_receive_latest_time = order_data.get_receive_latest_time("北京市昌平区南口镇陈庄村(京藏高速北侧)八达岭奥特莱斯F2")
        # print(single_receive_latest_time)
    
    # 测试所有的helper function, 除了calculate_stay_period()
    # 函数: calculate_time(), weight_availble(), volume_availble(), calculate_arrive_time(), calculate_leave_time(), time_availble()
    def testcase1():
        # 测试weight_availble()
        if (order_data.weight_availble(2.5) == True):
            pass
        else:
            print("(1) weight_availble() failed.")
        if (order_data.weight_availble(2.51) == False):
            pass
        else:
            print("(2) weight_availble() failed.")
            
        # 测试volume_availble()
        if (order_data.volume_availble(11.0) == True):
            pass
        else:
            print("(1) volume_availble() failed.")
        if (order_data.volume_availble(11.1) == False):
            pass
        else:
            print("(2) volume_availble() failed.")
        
        # 测试time_availble()
        if (order_data.time_availble("2024-01-01 08:00:00", "2024-01-01 20:00:00", "2024-01-01 08:00:00") == True):
            pass
        else:
            print("(1) time_availble() failed.")
        if (order_data.time_availble("2024-01-01 08:00:00", "2024-01-01 20:00:00", "2024-01-01 20:00:00") == True):
            pass
        else:
            print("(2) time_availble() failed.")
        if (order_data.time_availble("2024-01-01 08:00:00", "2024-01-01 20:00:00", "2024-01-01 07:59:59") == False):
            pass
        else:
            print("(3) time_availble() failed.")
        if (order_data.time_availble("2024-01-01 08:00:00", "2024-01-01 20:00:00", "2024-01-01 20:00:01") == False):
            pass
        else:
            print("(4) time_availble() failed.")
        if (order_data.time_availble("2024-01-01 08:00:00", "2024-01-01 20:00:00", "2023-01-01 15:00:00") == False):
            pass
        else:
            print("(5) time_availble() failed.")
        if (order_data.time_availble("2024-01-01 08:00:00", "2024-01-01 20:00:00", "2024-05-02 15:00:00") == False):
            pass
        else:
            print("(6) time_availble() failed.")
        
        # 测试time_arrive_availble_earliest()
        if (order_data.time_arrive_availble_earliest("2024-01-01 08:00:00", "2024-01-01 08:00:00") == True):
            pass
        else:
            print("(1) time_arrive_availble_earliest() failed.")
        if (order_data.time_arrive_availble_earliest("2024-01-01 08:00:00", "2024-01-01 07:59:59") == False):
            pass
        else:
            print("(2) time_arrive_availble_earliest() failed.")
        
        # 测试time_arrive_availble_last()
        if (order_data.time_arrive_availble_last("2024-01-01 20:00:00", "2024-01-01 20:00:00") == True):
            pass
        else:
            print("(1) time_arrive_availble_last() failed.")
        if (order_data.time_arrive_availble_last("2024-01-01 20:00:00", "2024-01-01 20:00:01") == False):
            pass
        else:
            print("(2) time_arrive_availble_last() failed.")
        
        # 测试calculate_arrive_time()
        if (order_data.calculate_arrive_time("2024-01-01 21:00:00", 55) == "2024-01-01 21:55:00"):
            pass
        else:
            print("(1) calculate_arrive_time() failed.")
        if (order_data.calculate_arrive_time("2024-01-01 21:00:00", 65) == "2024-01-01 22:05:00"):
            pass
        else:
            print("(2) calculate_arrive_time() failed.")
        
        # 测试calculate_leave_time()
        if (order_data.calculate_leave_time(60, "2024-01-01 21:00:00") == "2024-01-01 22:00:00"):
            pass
        else:
            print("(1) calculate_leave_time() failed.")
        if (order_data.calculate_leave_time(500, "2024-01-01 21:00:00") == "2024-01-02 05:20:00"):
            pass
        else:
            print("(2) calculate_leave_time() failed.")
            
        # 测试time_warehouse_leave_availble()
        if (order_data.time_warehouse_leave_availble("2024-01-01 08:00:00") == True):
            pass
        else:
            print("(1) time_warehouse_leave_availble() failed.")
        if (order_data.time_warehouse_leave_availble("2023-12-31 00:00:00") == True):
            pass
        else:
            print("(2) time_warehouse_leave_availble() failed.")
        if (order_data.time_warehouse_leave_availble("2023-12-30 59:59:59") == False):
            pass
        else:
            print("(3) time_warehouse_leave_availble() failed.")
        
        # 测试get_distance_warehouse_order()
        if (order_data.get_distance_warehouse_order("北京市昌平区南口镇陈庄村(京藏高速北侧)八达岭奥特莱斯F2") == 38.93970268896342):
            pass
        else:
            print("(1) get_distance_warehouse_order() failed.")
            
    # run test cases
    def runtest():
        testbasic() # all pass
        testcase1() # all pass
    runtest()