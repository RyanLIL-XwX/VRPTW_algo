# VRPTW
# Author: Hanzhen Qin
import json
from haversine import haversine, Unit # 用来计算两个经纬度之间的距离
from datetime import datetime, timedelta # 用来计算时间
import heapdict # dijkstra算法中使用的数据结构, 一种优先队列
import folium # 用于绘制地图
import numpy as np
from scipy.cluster.hierarchy import linkage, fcluster

class VRPTW_model(object):
    def __init__(self, file_path):
        self.file_path = file_path
        self.data = None # dictionary data type
        self.force_merge = None
        self.hand_over_time_by = None
        self.order_list = []
        self.parameters = None
        self.task_code = None
        self.vehicle_type = None
        self.warehouse = None
        
        self.load_data() # 函数用于读取txt文件中json格式的数据
        self.parse_data() # 函数用于解析json数据
        self.location_collect = [] # 使用list容器来储存经纬度信息
        self.distance_store = {} # 使用dictionary容器来储存两点之间的距离
        self.distance_store_update = {} # 使用dictionary容器来储存过滤后的两点之间的距离, 仅包含仓库的距离信息
        self.weight_collect = {} # 用于收集每个订单的重量信息的函数
        self.stay_period_info = {} # 用于收集每个订单的停留时间信息的函数
        self.first_order_address = None # 第一个订单的地址
        self.set_time = None # 设置时间
        self.set_delta_time = None # 设置时间间隔(分钟)
        self.set_mode = None # 设置时间计算模式
        self.check_weight = 0.0 # 检查车载重量是否可行
        self.check_volume = 0.0 # 检查车载空间是否可行
        self.arrive_time = None # 到达当前订单的时间(分钟)
        self.leave_time = None # 离开当前订单的时间(分钟)
        self.time_to_this_order = None # 到达当前订单的所需时间(分钟)
        self.single_stay_period = None # 单个订单的停留时间(分钟)
        self.set_receive_earliest_time = None # 设置最早收货时间
        self.set_receive_latest_time = None # 设置最晚收货时间
        
        # 给信息划分并分别处理, 全部都是和self.location_collect一样的结构
        self.location_collect_split_hierarchical = [] # 储存层次聚类分类器的地址信息
    
    # 函数用于读取txt文件中json格式的数据
    def load_data(self):
        try:
            # file = open(self.file_path, 'r', encoding='utf-8') # 打开文件, 读取模式使用仅读取, 编码格式为utf-8
            # 使用with来打开文件可以确保在文件使用完毕后自动关闭文件
            with open(self.file_path, 'r', encoding='utf-8') as file:
                file_content = file.read()  # 读取txt文件内容
                self.data = json.loads(file_content)  # 将json字符串解析为python字典
        # 如果读取txt文件时发生问题, 将会根据情况返回两个报错
        except FileNotFoundError:
            # 当你尝试打开一个不存在的文件时, python会抛出FileNotFoundError异常
            print(f"File {self.file_path} not found.")
        except json.JSONDecodeError:
            # 当尝试解码一个无效的json字符串时, python会抛出json.JSONDecodeError异常
            print("Error decoding JSON from the file.\n")
    
    # 函数用于解析json数据
    def parse_data(self):
        if (self.data == None):
            raise ValueError("Data is not loaded successfully.\n")
        # 从data属性中提取input部分的数据
        # 检查data的keys中是否有input, 如果有则提取input的值, 否则返回空字典
        if ("input" in self.data.keys()):
            input_data = self.data["input"]
        else:
            input_data = {}
        # 检查input_data的keys中是否有forceMerge, 如果有则提取forceMerge的值, 否则返回None
        if ("forceMerge" in input_data.keys()):
            self.force_merge = input_data["forceMerge"]
        else:
            self.force_merge = None
        # 检查input_data的keys中是否有handOverTimeBy, 如果有则提取handOverTimeBy的值, 否则返回None
        if ("handOverTimeBy" in input_data.keys()):
            self.hand_over_time_by = input_data["handOverTimeBy"]
        else:
            self.hand_over_time_by = None
        # 检查input_data的keys中是否有orderList, 如果有则提取orderList的值, 否则返回空列表
        if ("orderList" in input_data.keys()):
            self.order_list = input_data["orderList"]
        else:
            self.order_list = []
        # 检查input_data的keys中是否有parameter, 如果有则提取parameter的值, 否则返回空字典
        if ("parameter" in input_data.keys()):
            self.parameters = input_data["parameter"]
        else:
            self.parameters = {}
        # 检查input_data的keys中是否有taskCode, 如果有则提取taskCode的值, 否则返回None
        if ("taskCode" in input_data.keys()):
            self.task_code = input_data["taskCode"]
        else:
            self.task_code = None
        # 检查input_data的keys中是否有vehicleType, 如果有则提取vehicleType的值, 否则返回空字典
        if ("vehicleType" in input_data.keys()):
            self.vehicle_type = input_data["vehicleType"]
        else:
            self.vehicle_type = {}
        # 检查input_data的keys中是否有warehouse, 如果有则提取warehouse的值, 否则返回空字典
        if ("warehouse" in input_data.keys()):
            self.warehouse = input_data["warehouse"]
        else:
            self.warehouse = {}
    
    # 输出所有从txt文件中读取的数据
    def __str__(self):
        return "VRPTW_model:(\n force_merge={},\n hand_over_time_by={},\n order_list={},\n parameters={},\n task_code={},\n vehicle_type={},\n warehouse={}\n)".format(self.force_merge, self.hand_over_time_by, self.order_list, self.parameters, self.task_code, self.vehicle_type, self.warehouse)
        # or
        # python 3.6, f可以允许在字符串中直接嵌入表达式, 也称为格式化字符串字面值
        # return f"VRPTW_model:(\n force_merge={self.force_merge},\n hand_over_time_by={self.hand_over_time_by},\n order_list={self.order_list},\n parameters={self.parameters},\n task_code={self.task_code},\n vehicle_type={self.vehicle_type},\n warehouse={self.warehouse}\n)"
    
    # --------------------------------------------------------- #
    
    # 收集所有的经纬度信息和对应的地址, 包括order_list和warehouse
    def collect_location_info(self):
        location_collect = list() # 使用list容器来储存经纬度信息
        check_repreated = set() # 使用set容器来储存重复的地址
        count = 2
        # warehouse
        if ("address" in self.warehouse.keys() and "latitude" in self.warehouse.keys() and "longitude" in self.warehouse.keys() and self.warehouse["address"] != None and self.warehouse["latitude"] != None and self.warehouse["longitude"] != None):
            location_collect.append([self.warehouse["address"], float(self.warehouse["latitude"]), float(self.warehouse["longitude"]), "仓库"])
        else:
            print("No enough information for the warehouse.\n")
        # order_list
        # list中的每个index对应一个订单, 0为receivingAddress, 1为receivingLatitude, 2为receivingLongitude
        for i in range(len(self.order_list)):
            # 如果订单中有收货地址, 收货地址的经纬度和收货地址的区域信息, 并且这些信息不为空
            if ("receivingAddress" in self.order_list[i].keys() and "receivingLatitude" in self.order_list[i].keys() and "receivingLongitude" in self.order_list[i].keys() and self.order_list[i]["receivingLatitude"] != None and self.order_list[i]["receivingLongitude"] != None and self.order_list[i]["receivingAddress"] != None):
                # 如果有重复的地址, 则在地址后面加上一个数字
                if (self.order_list[i]["receivingAddress"] in check_repreated):
                    temp_list = list()
                    temp_list.append(self.order_list[i]["receivingAddress"] + "(" + str(count) + ")")
                    temp_list.append(float(self.order_list[i]["receivingLatitude"]))
                    temp_list.append(float(self.order_list[i]["receivingLongitude"]))
                    temp_list.append(self.order_list[i]["receivingDistrict"])
                    location_collect.append(temp_list)
                    count += 1
                else:
                    temp_list = list()
                    check_repreated.add(self.order_list[i]["receivingAddress"]) # 将当前地址加入到set容器中, 用于检查是否有重复的地址
                    temp_list.append(self.order_list[i]["receivingAddress"])
                    temp_list.append(float(self.order_list[i]["receivingLatitude"]))
                    temp_list.append(float(self.order_list[i]["receivingLongitude"]))
                    temp_list.append(self.order_list[i]["receivingDistrict"])
                    location_collect.append(temp_list)
            else:
                print("No enough information for the order list.\n")
        self.location_collect = location_collect # 更新self.location_collect属性
        return self.location_collect
    
    # 通过经纬度计算两点之间的距离
    def calculate_distance(self, location_collect):
        if (len(location_collect) < 2):
            raise ValueError("The number of locations is less than 2, please provide more locations.")
        distance_store = dict() # 使用字典来储存两点之间的距离
        pointer_a, pointer_b = 0, 1 # 用于指向当前订单的后一个订单
        while True:
            # 完成前指针所需计算的所有距离, 前指针开始更新, 后指针指向前指针的下一个订单
            if (pointer_b == len(location_collect)):
                pointer_a += 1
                pointer_b = pointer_a + 1
                # 如果后前针达到list的长度 - 1, 也就表示所有的地址之间的距离都被计算完毕
                if (pointer_a == len(location_collect) - 1):
                    break
            # distance = ((a_lat, a_lon), (b_lat, b_lon), unit = Unit.KILOMETERS)
            distance_km = haversine((location_collect[pointer_a][1], location_collect[pointer_a][2]), (location_collect[pointer_b][1], location_collect[pointer_b][2]), unit=Unit.KILOMETERS)
            # distance_store[distance_km] = (location_collect[pointer_a][0], location_collect[pointer_b][0])
            # 由于两个地址之间的距离可能会有重复, 所以需要将两个地址的名称组合成一个tuple, 作为key
            distance_store[(location_collect[pointer_a][0], location_collect[pointer_b][0])] = distance_km
            pointer_b += 1
        self.distance_store = distance_store # 更新self.distance_store属性
        return self.distance_store

    # --------------------------------------------------------- #
    
    # 过滤所有关于仓库的距离信息, 过滤self.distance_store
    def warehouse_leave_info(self, distance_store):
        distance_store_update = dict() # 用来过滤所有关于仓库的距离信息
        warehouse = self.warehouse["address"]
        for i in distance_store.keys():
            if (i[0] == warehouse):
                distance_store_update[i] = distance_store[i]
        self.distance_store_update = distance_store_update # 更新self.distance_store_update属性
        return self.distance_store_update
    
    # 计算仓库的出发时间, 这个时间取决于第一个订单的地址的最早收货时间来进行反推计算
    def time_warehouse_leave(self, first_order_address):
        temp_collect = {} # temp_collect: {"地址": [(订单号, 最早到达时间时间), (), ...]}
        for i in range(len(self.order_list)):
            if (self.order_list[i]["receivingAddress"] == first_order_address):
                # 出现一个地址多个订单的情况, 将这些订单的订单号和最早收货时间储存在temp_collect中
                if (self.order_list[i]["receivingAddress"] in temp_collect.keys()):
                    temp_collect[first_order_address].append((self.order_list[i]["orderCode"], self.order_list[i]["receivingEarliestTime"]))
                else:
                    temp_collect[first_order_address] = [(self.order_list[i]["orderCode"], self.order_list[i]["receivingEarliestTime"])]
        vehicle_speed = self.parameters["speed"] # 车辆的速度
        distance_between = 0 # 仓库于第一个订单之间的距离
        for i in self.distance_store_update.keys():
            if (i[1] == first_order_address):
                distance_between = self.distance_store_update[i]
                break
        # 计算仓库的出发时间
        delta_time = round((distance_between / vehicle_speed) * 60) # 将km/h转换为km/min, 并且保留整数部分
        # 经过对数据的查询发现, 当一个地址有多个订单时, 这些订单的最早收货时间是一样的
        self.set_time = temp_collect[first_order_address][0][1] # 仓库的出发时间
        self.set_delta_time = delta_time # 仓库的出发时间间隔
        self.set_mode = "-"
        return self.calculate_time(self.set_time, self.set_delta_time, self.set_mode)
    
    # --------------------------------------------------------- #
    
    # 计算每个订单的重量, helper function
    def calculate_weight(self, order_address):
        for i in range(len(self.order_list)):
            if (self.order_list[i]["receivingAddress"] == order_address):
                # 使用+=是因为可能会有多个订单在同一个地址
                self.check_weight = self.order_list[i]["weight"]
        return self.check_weight
    
    # 计算每个订单的体积, helper function
    def calculate_volume(self, order_address):
        for i in range(len(self.order_list)):
            if (self.order_list[i]["receivingAddress"] == order_address):
                # 使用+=是因为可能会有多个订单在同一个地址
                self.check_volume = self.order_list[i]["volume"]
        return self.check_volume
    
    # 计算每个订单的停留时间(单位: 分钟), helper function
    def calculate_stay_period(self, item_weight):
        stay_period = round(item_weight * self.parameters["handoverVariableTime"] + self.parameters["handoverFixedTime"]) # 四舍五入
        return stay_period
    
    # 设置最早收货时间, helper function
    def get_receive_earliest_time(self, order_address):
        for i in range(len(self.order_list)):
            if (self.order_list[i]["receivingAddress"] == order_address):
                self.set_receive_earliest_time = self.order_list[i]["receivingEarliestTime"]
        return self.set_receive_earliest_time
    
    # 设置最晚收货时间, helper function
    def get_receive_latest_time(self, order_address):
        for i in range(len(self.order_list)):
            if (self.order_list[i]["receivingAddress"] == order_address):
                self.set_receive_latest_time = self.order_list[i]["receivingLatestTime"]
        return self.set_receive_latest_time
    
    # 专门更新时间的函数, helper function
    def calculate_time(self, time: str, delta_time: int, mode: str) -> str:
        # 检查time是否为None
        if (not time):
            raise ValueError("The input time is empty. Please provide a valid time string.")
        
        # 将字符串类型的时间转换为datetime对象
        try:
            initial_time = datetime.strptime(time, "%Y-%m-%d %H:%M:%S")
        # 如果time的格式不符合"%Y-%m-%d %H:%M:%S", 则抛出ValueError异常
        except ValueError as e:
            raise ValueError(f"Time data '{time}' does not match format '%Y-%m-%d %H:%M:%S'.") from e
        
        # 将delta_time转换为timedelta对象, 单位为分钟
        delta = timedelta(minutes=delta_time)
        
        # 根据mode参数进行时间加减
        if (mode == "+"):
            new_time = initial_time + delta
        elif (mode == "-"):
            new_time = initial_time - delta
        else:
            raise ValueError("Mode should be '+' or '-'")
        
        # 将新的时间转换为字符串格式
        return new_time.strftime("%Y-%m-%d %H:%M:%S")
    
    # 判断车载重量是否可行, helper function
    def weight_availble(self, check_weight):
        if (check_weight > self.vehicle_type["loadableWeight"]):
            return False
        else:
            return True
    
    # 判断车载空间是否可行, helper function
    def volume_availble(self, check_volume):
        if (check_volume > self.vehicle_type["loadableVolume"]):
            return False
        else:
            return True
    
    # 只计算单个订单的到达时间, helper function
    def calculate_arrive_time(self, leave_time, time_to_this_order):
        # 到达时间 = 上一站点出发时间 + 到达本收货站点的路程耗时
        arrive_time = self.calculate_time(leave_time, time_to_this_order, "+")
        self.arrive_time = arrive_time
        return self.arrive_time
        
    # 只计算单个订单的离开时间, helper function
    def calculate_leave_time(self, single_stay_period, arrive_time):
        # 离开时间 = 到达时间 + 停留时间
        leave_time = self.calculate_time(arrive_time, single_stay_period, "+")
        self.leave_time = leave_time
        return self.leave_time
    
    # 判断时间是否可行, helper function
    def time_availble(self, receive_earliest_time, receive_latest_time, arrive_time):
        # 可以直接通过str来判断时间大小, 因为时间字符串是按照从小到大的顺序排列的
        # time1 > time2: 说明time1的时间晚于time2的时间
        # time1 < time2: 说明time1的时间早于time2的时间
        if ((arrive_time >= receive_earliest_time) and (arrive_time <= receive_latest_time)):
            return True
        else:
            return False
    
    # 判断到达时间是否可行, 当到达时间早于最早送货时间时, helper function
    def time_arrive_availble_earliest(self, receive_earliest_time, arrive_time):
        if (arrive_time >= receive_earliest_time):
            return True
        else:
            return False
    
    # 判断到达时间是否可行, 当到达时间超过最晚送货时间时, helper function
    def time_arrive_availble_last(self, receive_latest_time, arrive_time):
        if (arrive_time <= receive_latest_time):
            return True
        else:
            return False
    
    # 判断仓库的出发时间是否可行, helper function
    def time_warehouse_leave_availble(self, time_warehouse_leave):
        if (time_warehouse_leave >= self.warehouse["openTime"]):
            return True
        else:
            return False
    
    # --------------------------------------------------------- #

    # 使用层次聚类对订单进行聚类
    def cluster_location_hierarchical(self, location_collect, distance_threshold=1.0):
        """
        对订单进行层次聚类

        参数:
        - location_collect: 所有的订单信息
        - distance_threshold: 距离阈值，用于确定簇的数量

        返回:
        - clustered_list: 聚类后的订单列表，每个簇的第一个位置是仓库信息
        
        使用了linkage函数, 并选择了ward方法进行聚类. 
        - Ward方法是一种最小化总方差的聚类方法, 属于凝聚层次聚类的一种. 其主要特点是:
        - 凝聚层次聚类：从每个点自身作为一个簇开始, 不断合并最近的簇, 直到满足停止条件. 
        """
        # 提取经纬度信息
        coords = np.array([(order[1], order[2]) for order in location_collect], dtype=float)

        # 使用层次聚类中的Ward方法对坐标进行聚类, 返回一个层次聚类树的链表表示, 这个链表表示了在聚类过程中每一步合并的簇. 
        Z = linkage(coords, method='ward')

        # 根据距离阈值将层次聚类树截断, 生成平坦的簇标签
        labels = fcluster(Z, t=distance_threshold, criterion='distance')

        # 创建了一个字典, 字典的键是簇标签, 值是空列表, 用于存储每个簇中的数据点
        clustered_dict = {}
        for label in np.unique(labels):
            clustered_dict[label] = []

        # 将每个订单分配到相应的簇中
        for order, label in zip(location_collect, labels):
            clustered_dict[label].append(order)

        # 构建结果列表
        clustered_list = []
        warehouse_info = [self.warehouse["address"], float(self.warehouse["latitude"]), float(self.warehouse["longitude"]), "仓库"]
        
        for cluster in clustered_dict.values():
            # 确保仓库信息在每个簇的第一个位置
            if (warehouse_info not in cluster):
                cluster.insert(0, warehouse_info)
            clustered_list.append(cluster)

        self.location_collect_split_hierarchical = clustered_list
        return self.location_collect_split_hierarchical
    
    # --------------------------------------------------------- #
    
    # main part: finding path algorithm
    
    # 找到从仓库出发的第一个订单的地址
    def get_first_order_address(self, distance_store):
        check_weight = 0.0 # 用于检查车载重量是否可行
        check_volume = 0.0 # 用于检查车载空间是否可行
        path_record = [self.warehouse["address"]] # 用于储存warehouse和第一个订单的地址
        
        # 仅仅用于找到仓库和离仓库最近的收货地点
        distance_store_update_copy = self.warehouse_leave_info(distance_store).copy()
        # 对distance_store_update_copy进行排序, 以便找到离仓库最近的收货地点
        sorted_distance_store_update_copy = dict(sorted(distance_store_update_copy.items(), key=lambda item: item[1]))
        for i in (sorted_distance_store_update_copy.keys()):
            # 对基础的信息进行初始化并且检查weight, volume, time是否可行
            # 针对第一个订单的地址
            check_weight = self.calculate_weight(i[1]) # 计算车载重量
            check_volume = self.calculate_volume(i[1]) # 计算车载空间
            warehouse_leave_time = self.time_warehouse_leave(i[1]) # 计算仓库的离开时间
            if (self.time_warehouse_leave_availble(warehouse_leave_time) == True and self.weight_availble(check_weight) == True and self.volume_availble(check_volume) == True):
                path_record.append(i[1]) # 路径的第二个点: 离仓库最近的收货地点
                break # 已经找到了满足条件的, 并且离仓库最近的收货地点
            else:
                print("The warehouse's leave time is not available or the weight or volume is not available.\n")
        return path_record[1]
    
    # dijkstra算法, 用于计算最短路径
    def dijkstra(self, distance_store, start_address):
        # 开始创建图的邻接表表示法, 一个点到其他点的距离, 是一个dictionary容器: 
        # {address1: {address2: distance, address3: distance, ...}, ...}
        graph = {}
        for (address1, address2), distance in distance_store.items():
            if (address1 not in graph.keys()):
                graph[address1] = {}
            if (address2 not in graph.keys()):
                graph[address2] = {}
            graph[address1][address2] = distance
            graph[address2][address1] = distance
        # 初始化距离字典, 所有节点的初始距离为无穷大: float("inf")
        distances = {node: float("inf") for node in graph}
        distances[start_address] = 0  # 起点的距离为0
        # 初始化一个优先队列, 用于存储节点, 将起点加入队列
        priority_queue = heapdict.heapdict()
        priority_queue[start_address] = 0
        dijkstra_path = list() # 用于储存dijkstra算法的最短路径
        visited_order = list() # 用于储存已经访问过的订单地址
        # 接下来准备对剩下的订单地址进行处理, 不断的添加路径到dijkstra_path中
        while priority_queue:
            # 从优先队列中取出具有最小距离的节点
            current_node, current_distance = priority_queue.popitem()
            # 记录当前访问的节点
            visited_order.append((current_node, current_distance))
            # 遍历当前节点的所有邻居
            for neighbor, distance_weight in graph[current_node].items():
                distance = current_distance + distance_weight
                # 如果经当前节点到达邻居节点的距离小于目前记录的距离, 则更新距离和前驱节点
                if (distance < distances[neighbor]):
                    distances[neighbor] = distance
                    # heapdict结构会根据新的距离distance重新调整优先队列, 以确保队列中最小距离的节点在最前面
                    priority_queue[neighbor] = distance
        sorted_distances = sorted(distances.items(), key=lambda x: x[1])
        for i in sorted_distances:
            dijkstra_path.append((i[0], i[1]))
        return dijkstra_path
             
    def find_path(self, distance_store):
        dijkstra_path = list() # 用于储存dijkstra算法的最短路径
        first_order_address = self.get_first_order_address(distance_store) # 获取第一个订单的地址
        distance_store_copy = distance_store.copy() # 用于储存所有的距离信息
        # 删除所有和仓库有关的距离信息, 因为我们已经不再需要了
        for i in distance_store.keys():
            if (i[0] == self.warehouse["address"]):
                del distance_store_copy[i]
        # 开始进行dijkstra算法, 用于计算最短路径
        dijkstra_path = self.dijkstra(distance_store_copy, first_order_address)
        return dijkstra_path
               
    # 运行find_path()函数, 每次调用一个cluster的数据去进行最短路径的查找
    def run_find_path(self):
        all_path = list() # 用于储存所有的最短路径
        for i in range(len(self.location_collect_split_hierarchical)):
            if (len(self.location_collect_split_hierarchical[i]) >= 2):
                all_path.append(self.find_path(self.calculate_distance(self.location_collect_split_hierarchical[i])))
            elif (len(self.location_collect_split_hierarchical[i]) == 1):
                all_path.append(self.location_collect_split_hierarchical[i][0][0])
            else:
                continue
        return all_path
    
    # 处理dijkstra算法的路径, 用于检查车载重量, 车载空间和时间是否可行
    def process_dijkstra_path(self, all_path):
        final_path = list() # 用于储存最终的路径
        car_speed = self.parameters["speed"]
        visited_address = set() # 用于储存已经访问过的地址
        for order_path in all_path:
            check_weight = 0.0 # 用于检查车载重量是否可行
            check_volume = 0.0 # 用于检查车载空间是否可行
            arrive_time = self.get_receive_earliest_time(order_path[1][0]) # 到达当前订单的时间(分钟)
            leave_time = "" # 离开当前订单的时间(分钟)
            current_pointer = 0 # 访问当前订单的指针
            pointer = 0 # 如果当前订单不可行, 用来检查下一个可行订单
            temp_list = list() # 用于储存可以符合要求的订单地址
            while current_pointer < len(order_path):
                if (order_path[current_pointer] in visited_address):
                    current_pointer += 1
                    continue
                address, distance = order_path[current_pointer]
                check_weight += self.calculate_weight(address) # 计算车载重量
                check_volume += self.calculate_volume(address) # 计算车载空间
                leave_time = self.calculate_leave_time(self.calculate_stay_period(check_weight), arrive_time) # 离开当前订单的时间(分钟)
                # 每次新的一辆车的第一个订单, 都需要重新更新出发时间
                if (len(temp_list) == 0):
                    arrive_time = self.get_receive_earliest_time(address) # 到达当前订单的时间(分钟)
                else:
                    arrive_time = self.calculate_arrive_time(leave_time, distance / car_speed) # 到达当前订单的时间(分钟)
                # 如果车载重量和车载空间可行, 并且时间可行, 则将当前的订单地址加入到temp_list中
                if (self.weight_availble(check_weight) == True and self.volume_availble(check_volume) == True):
                    if (self.time_availble(self.get_receive_earliest_time(address), self.get_receive_latest_time(address), arrive_time) == True):
                        temp_list.append((address, distance))
                        visited_address.add((address, distance))
                        current_pointer += 1
                    # 当时间不可行时, 将会访问后面的所有可能满足要求的订单地址, 并且加入到temp_list中
                    else:
                        pointer = current_pointer + 1
                        while (pointer < len(order_path)):
                            check_weight += self.calculate_weight(order_path[pointer][0]) # 计算车载重量
                            check_volume += self.calculate_volume(order_path[pointer][0]) # 计算车载空间
                            leave_time = self.calculate_leave_time(self.calculate_stay_period(check_weight), arrive_time) # 离开当前订单的时间(分钟)
                            arrive_time = self.calculate_arrive_time(leave_time, order_path[pointer][1] / car_speed) # 到达当前订单的时间(分钟
                            if (self.weight_availble(check_weight) == True and self.volume_availble(check_volume) == True and self.time_availble(self.get_receive_earliest_time(order_path[pointer][0]), self.get_receive_latest_time(order_path[pointer][0]), arrive_time) == True):
                                temp_list.append(order_path[pointer])
                                visited_address.add(order_path[pointer])
                            pointer += 1
                # 如果车载重量或者车载空间不可行, 则将当前的订单地址加入到final_path中, 并且清空temp_list
                else:
                    if (len(temp_list) != 0):
                        final_path.append(temp_list[:]) # 这里需要使用temp_list[:]来进行深拷贝, 否则temp_list中的元素被清空时, final_path中的元素也会被清空
                    check_weight = 0.0
                    check_volume = 0.0
                    temp_list.clear()     
            # 如果一整条路线都可以用一辆车装完, 则直接加入到final_path中
            final_path.append(temp_list)
        processed_final_path = list() # 用于储存处理后的最终路径
        # 将final_path中的address元素提取出来, 并且将其转换为一个list
        for sublist in final_path:
            addresses = [address for address, _ in sublist]
            processed_final_path.append(addresses)
        return processed_final_path, final_path

    # --------------------------------------------------------- #

    # 计算车载重量和车载空间的利用率, 以及总距离
    def calculate_info(self, processed_final_path, final_path, file_name):
        weight_utilization = list() # 用于储存车载重量的利用率
        weight_record = 0.0 # 用于检查车载重量是否可行
        volume_utilization = list() # 用于储存车载空间的利用率
        volume_record = 0.0 # 用于检查车载空间是否可行
        max_weight = self.vehicle_type["loadableWeight"] # 车辆的最大载重量
        max_volume = self.vehicle_type["loadableVolume"] # 车辆的最大载重量
        order = 0 # 用于记录订单的数量
        # 计算车载重量和车载空间的利用率
        for i in processed_final_path:
            for j in i:
                weight_record += self.calculate_weight(j)
                volume_record += self.calculate_volume(j)
                order += 1
            weight_utilization.append((weight_record / max_weight) * 100)
            volume_utilization.append((volume_record / max_volume) * 100)
            weight_record = 0.0
            volume_record = 0.0
        # 打印车载重量和车载空间的利用率和订单的数量
        print("Total orders count: {}\n".format(order))
        if (len(weight_utilization) == len(volume_utilization)):
            length = len(weight_utilization)
            number = 0
            for i in range(length):
                number += 1
                print("Car {}: The weight utilization is {:.2f}% and the volume utilization is {:.2f}%".format(number, weight_utilization[i], volume_utilization[i]))
            print()
        else:
            raise ValueError("The length of weight utilization and volume utilization is not equal.")
        # 计算车载重量和车载空间的平均利用率
        average_weight_utilization = round(sum(weight_utilization) / len(weight_utilization))
        average_volume_utilization = round(sum(volume_utilization) / len(volume_utilization))
        print("The average weight utilization is {:.2f}% and the average volume utilization is {:.2f}%\n".format(average_weight_utilization, average_volume_utilization))
        # 计算总距离
        warehouse_info = self.warehouse["address"]
        total_distance = 0
        for i in final_path:
            for j in range(len(i)):
                if (j == 0):
                    if ((warehouse_info, i[j][0]) in self.distance_store_update.keys()):
                        total_distance += self.distance_store_update[(warehouse_info, i[j][0])]
                else:
                    total_distance += i[j][1]
        print("Total distance for the {}: {:.2f}km and Total number of cars using: [{}]".format(file_name, total_distance, len(processed_final_path)))

    # 将路径绘制到地图上
    def plot_route_on_map(self, location_collect, shortest_path):
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
        colors = ["blue", "green", "purple", "orange", "darkred", "lightred", "darkblue", "darkgreen", "cadetblue", "darkpurple", "pink", "lightblue", "lightgreen"]
        
        # 遍历shortest_path中的每个子列表
        for index, path in enumerate(shortest_path):
            # 存储路径的经纬度
            route_coords = []
            
            # 通过地址查找经纬度并添加到路径坐标列表中
            for address in path:
                if address in location_dict:
                    latitude, longitude, _ = location_dict[address]
                    route_coords.append([latitude, longitude])
            
            # 绘制路径
            if route_coords:
                # 添加路径线条到地图, 并设置颜色, 宽度和透明度
                folium.PolyLine(route_coords, color=colors[index % len(colors)], weight=5, opacity=0.8).add_to(route_map)
                
                # 为每个路径点添加小的彩色点
                for coord, address in zip(route_coords, path):
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
          
if __name__ == "__main__":
    # 创建一个VRPTW_model对象, 并将file作为参数传入
    # 函数: load_data(), parse_data(), __str__()
    file = input("Type the name of the file: ").strip() # strip()函数用于去除字符串两端的空格
    order_data = VRPTW_model(file)
    # print(order_data) 
    #*
        # order data: VRPTW_model对象
        # location_collect: list容器(lists of list): [[address, latitude, longitude, district], ...]
        # location_collect: 除了仓库的信息: [address, latitude, longitude, "仓库"]
        #
        # distance_store: dictionary容器储存两点之间的距离: {(address1, address2) : 距离, ...}
        # distance_store_update: dictionary容器储存过滤后的两点之间的距离, 仅包含仓库的距离信息: {(address1, address2) : 距离, ...}
        # time_warehouse_leave: 仓库对特定地址的出发时间
    #*#
    
    # 开始运行dijkstra算法, 并且找到最短路径, 再将路径绘制到地图上
    def start_find_path():
        # 设置基础数据
        location_collect = order_data.collect_location_info()
        # print(location_collect)
        distance_store = order_data.calculate_distance(location_collect)
        # print(distance_store)
        location_collect_split_hierarchical = order_data.cluster_location_hierarchical(location_collect)
        # print(location_collect_split_hierarchical)
        
        # 运行dijkstra算法, 并且找到最短路径, 再将路径绘制到地图上
        dijkstra_path_hierarchical = order_data.run_find_path()
        # print(dijkstra_path_hierarchical)
        processed_final_path, final_path = order_data.process_dijkstra_path(dijkstra_path_hierarchical)
        # print(processed_final_path)
        # 打印订单数量, 车载重量, 车载空间的利用率和总距离
        order_data.calculate_info(processed_final_path, final_path, file)
        # 将路径绘制到地图上
        order_data.plot_route_on_map(location_collect, processed_final_path)

    start_find_path()
    
    
    
    
    
    
    