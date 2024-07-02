# VRPTW
# Author: Hanzhen Qin, Shenhan Xu
import json
from haversine import haversine, Unit # 用来计算两个经纬度之间的距离
from datetime import datetime, timedelta # 用来计算时间
import heapdict # dijkstra算法中使用的数据结构, 一种优先队列
import folium # 用于绘制地图

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
        
        # 给信息划分并分别处理, 全部都是和self.location_collect一样结构的数据
        self.dongcheng = [] # 储存东城区的地址信息
        self.xicheng = [] # 储存西城区的地址信息
        self.chaoyang = [] # 储存朝阳区的地址信息
        self.fengtai = [] # 储存丰台区的地址信息
        self.shijingshan = [] # 储存石景山区的地址信息
        self.haidian = [] # 储存海淀区的地址信息
        self.mentougou = [] # 储存门头沟区的地址信息
        self.fangshan = [] # 储存房山区的地址信息
        self.tongzhou = [] # 储存通州区的地址信息
        self.shunyi = [] # 储存顺义区的地址信息
        self.changping = [] # 储存昌平区的地址信息
        self.daxing = [] # 储存大兴区的地址信息
        self.huairou = [] # 储存怀柔区的地址信息
        self.pinggu = [] # 储存平谷区的地址信息
        self.miyun = [] # 储存密云区的地址信息
        self.yanqing = [] # 储存延庆区的地址信息
        self.location_collect_split_district = [] # 储存划分后的地址信息
    
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
        location_collect = list()
        # warehouse
        if ("address" in self.warehouse.keys() and "latitude" in self.warehouse.keys() and "longitude" in self.warehouse.keys() and self.warehouse["address"] != None and self.warehouse["latitude"] != None and self.warehouse["longitude"] != None):
            location_collect.append([self.warehouse["address"], float(self.warehouse["latitude"]), float(self.warehouse["longitude"]), "仓库"])
        else:
            print("No enough information for the warehouse.\n")
        # order_list
        # list中的每个index对应一个订单, 0为receivingAddress, 1为receivingLatitude, 2为receivingLongitude
        for i in range(len(self.order_list)):
            # 如果order_list中的当前index所在订单中包含receivingLatitude和receivingLongitude, 并且这两个值不为None, 则计算两点之间的距离
            if ("receivingAddress" in self.order_list[i].keys() and "receivingLatitude" in self.order_list[i].keys() and "receivingLongitude" in self.order_list[i].keys() and self.order_list[i]["receivingLatitude"] != None and self.order_list[i]["receivingLongitude"] != None and self.order_list[i]["receivingAddress"] != None):
                temp_list = list()
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
            # 如果两个订单的地址相同, 则后指针指向下一个订单, 跳过当前计算
            if (location_collect[pointer_a][0] == location_collect[pointer_b][0]):
                pointer_b += 1
                continue
            # distance = ((a_lat, a_lon), (b_lat, b_lon), unit = Unit.KILOMETERS)
            distance_km = haversine((location_collect[pointer_a][1], location_collect[pointer_a][2]), (location_collect[pointer_b][1], location_collect[pointer_b][2]), unit=Unit.KILOMETERS)
            distance_store[distance_km] = (location_collect[pointer_a][0], location_collect[pointer_b][0])
            pointer_b += 1
        self.distance_store = distance_store # 更新self.distance_store属性
        return self.distance_store

    # --------------------------------------------------------- #
    
    # 过滤所有关于仓库的距离信息, 过滤self.distance_store
    def warehouse_leave_info(self, distance_store):
        distance_store_update = dict() # 用来过滤所有关于仓库的距离信息
        warehouse = self.warehouse["address"]
        for i in distance_store.keys():
            if (distance_store[i][0] == warehouse):
                distance_store_update[i] = (distance_store[i][0], distance_store[i][1])
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
            if (self.distance_store_update[i][1] == first_order_address):
                distance_between = i
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
                self.check_weight += self.order_list[i]["weight"]
        return self.check_weight
    
    # 计算每个订单的体积, helper function
    def calculate_volume(self, order_address):
        for i in range(len(self.order_list)):
            if (self.order_list[i]["receivingAddress"] == order_address):
                # 使用+=是因为可能会有多个订单在同一个地址
                self.check_volume += self.order_list[i]["volume"]
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
    
    # 划分location_collect中的信息, 通过区的名称分别加入不同的容器中
    def location_collect_split(self, location_collect):
        for i in range(len(location_collect)):
            if (location_collect[i][3] == "东城区" or location_collect[i][3] == "仓库"):
                self.dongcheng.append(location_collect[i])
            if (location_collect[i][3] == "西城区" or location_collect[i][3] == "仓库"):
                self.xicheng.append(location_collect[i])
            if (location_collect[i][3] == "朝阳区" or location_collect[i][3] == "仓库"):
                self.chaoyang.append(location_collect[i])
            if (location_collect[i][3] == "丰台区" or location_collect[i][3] == "仓库"):
                self.fengtai.append(location_collect[i])
            if (location_collect[i][3] == "石景山区" or location_collect[i][3] == "仓库"):
                self.shijingshan.append(location_collect[i])
            if (location_collect[i][3] == "海淀区" or location_collect[i][3] == "仓库"):
                self.haidian.append(location_collect[i])
            if (location_collect[i][3] == "门头沟区" or location_collect[i][3] == "仓库"):
                self.mentougou.append(location_collect[i])
            if (location_collect[i][3] == "房山区" or location_collect[i][3] == "仓库"):
                self.fangshan.append(location_collect[i])
            if (location_collect[i][3] == "通州区" or location_collect[i][3] == "仓库"):
                self.tongzhou.append(location_collect[i])
            if (location_collect[i][3] == "顺义区" or location_collect[i][3] == "仓库"):
                self.shunyi.append(location_collect[i])
            if (location_collect[i][3] == "昌平区" or location_collect[i][3] == "仓库"):
                self.changping.append(location_collect[i])
            if (location_collect[i][3] == "大兴区" or location_collect[i][3] == "仓库"):
                self.daxing.append(location_collect[i])
            if (location_collect[i][3] == "怀柔区" or location_collect[i][3] == "仓库"):
                self.huairou.append(location_collect[i])
            if (location_collect[i][3] == "平谷区" or location_collect[i][3] == "仓库"):
                self.pinggu.append(location_collect[i])
            if (location_collect[i][3] == "密云区" or location_collect[i][3] == "仓库"):
                self.miyun.append(location_collect[i])
            if (location_collect[i][3] == "延庆区" or location_collect[i][3] == "仓库"):
                self.yanqing.append(location_collect[i])
        self.location_collect_split_district.append(self.dongcheng)
        self.location_collect_split_district.append(self.xicheng)
        self.location_collect_split_district.append(self.chaoyang)
        self.location_collect_split_district.append(self.fengtai)
        self.location_collect_split_district.append(self.shijingshan)
        self.location_collect_split_district.append(self.haidian)
        self.location_collect_split_district.append(self.mentougou)
        self.location_collect_split_district.append(self.fangshan)
        self.location_collect_split_district.append(self.tongzhou)
        self.location_collect_split_district.append(self.shunyi)
        self.location_collect_split_district.append(self.changping)
        self.location_collect_split_district.append(self.daxing)
        self.location_collect_split_district.append(self.huairou)
        self.location_collect_split_district.append(self.pinggu)
        self.location_collect_split_district.append(self.miyun)
        self.location_collect_split_district.append(self.yanqing)
        return self.dongcheng, self.xicheng, self.chaoyang, self.fengtai, self.shijingshan, self.haidian, self.mentougou, self.fangshan, self.tongzhou, self.shunyi, self.changping, self.daxing, self.huairou, self.pinggu, self.miyun, self.yanqing
    
    # main part: finding path algorithm
    
    # 找到从仓库出发的第一个订单的地址
    def get_first_order_address(self, distance_store):
        check_weight = 0.0 # 用于检查车载重量是否可行
        check_volume = 0.0 # 用于检查车载空间是否可行
        path_record = [self.warehouse["address"]] # 用于储存warehouse和第一个订单的地址
        
        # 仅仅用于找到仓库和离仓库最近的收货地点
        distance_store_update_copy = self.warehouse_leave_info(distance_store).copy()
        sorted_keys = sorted(distance_store_update_copy.keys())
        # 通过排序可以得到从warehouse出发到其他订单地址的距离
        sorted_distance_store_update_copy = {key: distance_store_update_copy[key] for key in sorted_keys}
        for i in (sorted_distance_store_update_copy.keys()):
            # 对基础的信息进行初始化并且检查weight, volume, time是否可行
            # 针对第一个订单的地址
            check_weight = self.calculate_weight(sorted_distance_store_update_copy[i][1]) # 计算车载重量
            check_volume = self.calculate_volume(sorted_distance_store_update_copy[i][1]) # 计算车载空间
            warehouse_leave_time = self.time_warehouse_leave(sorted_distance_store_update_copy[i][1]) # 计算仓库的离开时间
            if (self.time_warehouse_leave_availble(warehouse_leave_time) == True and self.weight_availble(check_weight) == True and self.volume_availble(check_volume) == True):
                path_record.append(sorted_distance_store_update_copy[i][1]) # 路径的第二个点: 离仓库最近的收货地点
                break # 已经找到了满足条件的, 并且离仓库最近的收货地点
            else:
                print("The warehouse's leave time is not available or the weight or volume is not available.\n")
        return path_record[1]
    
    # dijkstra算法, 用于计算最短路径
    def dijkstra(self, distance_store, start_address):
        check_weight = 0.0 # 用于检查车载重量是否可行
        check_volume = 0.0 # 用于检查车载空间是否可行
        arrive_time = self.get_receive_earliest_time(start_address) # 到达当前订单的时间(分钟)
        leave_time = "" # 离开当前订单的时间(分钟)
        car_speed = self.parameters["speed"]
        # 开始创建图的邻接表表示法, 一个点到其他点的距离, 是一个dictionary容器: 
        # {address1: {address2: distance, address3: distance, ...}, ...}
        graph = {}
        check_visited = set() # 用于检查是否访问过
        for distance, (address1, address2) in distance_store.items():
            if (address1 not in graph.keys()):
                graph[address1] = {}
            if (address2 not in graph.keys()):
                graph[address2] = {}
            check_visited.add(address1)
            check_visited.add(address2)
            graph[address1][address2] = distance
            graph[address2][address1] = distance
        # 初始化距离字典, 所有节点的初始距离为无穷大: float("inf")
        distances = {node: float("inf") for node in graph}
        distances[start_address] = 0  # 起点的距离为0
        # 初始化前驱节点字典, 所有节点的前驱节点为None, 用于重建最短路径, 通过前驱字典, 我们可以从目标节点出发, 一步步回到起点, 从而重建出完整的最短路径.
        previous_nodes = {node: None for node in graph}
        # 初始化一个优先队列, 用于存储节点, 将起点加入队列
        priority_queue = heapdict.heapdict()
        priority_queue[start_address] = 0
        dijkstra_path = list() # 用于储存dijkstra算法的最短路径
        unvisited_nodes = set() # 用于储存未访问过的节点
        # 接下来准备对剩下的订单地址进行处理, 不断的添加路径到dijkstra_path中, 并且保证时间, 重量, 体积可行
        while priority_queue:
            # 从优先队列中取出具有最小距离的节点
            current_node, current_distance = priority_queue.popitem()
            # 开始进行时间, 重量, 体积的检查
            check_weight += self.calculate_weight(current_node) # 计算车载重量
            check_volume += self.calculate_volume(current_node) # 计算车载空间
            leave_time = self.calculate_leave_time(self.calculate_stay_period(check_weight), arrive_time) # 计算离开时间
            arrive_time = self.calculate_arrive_time(leave_time, round(current_distance / car_speed)) # 计算到达时间
            if (self.weight_availble(check_weight) == True and self.volume_availble(check_volume) == True and self.time_arrive_availble_last(self.get_receive_latest_time(current_node), arrive_time) == True):
                pass
            else:
                temp_check_visited = set(dijkstra_path) # 用于储存已经访问过的节点
                unvisited_nodes = temp_check_visited.symmetric_difference(check_visited) # 用于储存未访问过的节点
                unvisited_nodes = list(unvisited_nodes)
                print("The weight or volume or is not available.\n")
                break
            # 当到达时间小于最早收货时间时, 车子会进行等待
            if (self.time_arrive_availble_earliest(self.get_receive_earliest_time(current_node), arrive_time) == False):
                arrive_time = self.get_receive_earliest_time(current_node)
            # 记录当前访问的节点
            dijkstra_path.append(current_node)
            # 遍历当前节点的所有邻居
            for neighbor, distance_weight in graph[current_node].items():
                distance = current_distance + distance_weight
                # 如果经当前节点到达邻居节点的距离小于目前记录的距离, 则更新距离和前驱节点
                if (distance < distances[neighbor]):
                    distances[neighbor] = distance
                    previous_nodes[neighbor] = current_node
                    # heapdict结构会根据新的距离distance重新调整优先队列, 以确保队列中最小距离的节点在最前面
                    priority_queue[neighbor] = distance
        return dijkstra_path, unvisited_nodes
             
    def find_path(self, distance_store):
        dijkstra_path = [self.warehouse["address"]] # 用于储存dijkstra算法的最短路径
        first_order_address = self.get_first_order_address(distance_store) # 获取第一个订单的地址
        distance_store_copy = distance_store.copy() # 用于储存所有的距离信息
        # 删除所有和仓库有关的距离信息, 因为我们已经不再需要了
        for i in distance_store.keys():
            if (distance_store[i][0] == self.warehouse["address"]):
                del distance_store_copy[i]
        # 开始进行dijkstra算法, 用于计算最短路径
        dijkstra_path, unvisited_nodes = self.dijkstra(distance_store_copy, first_order_address)
        # while (len(unvisited_nodes) != 0):
        #     # 创建一个新的字典, 用于存储满足条件的键值对
        #     remain_distance_store = {}

        #     # 遍历原始字典中的每一个键值对
        #     for key, value in distance_store_copy.items():
        #         # 检查路径中是否包含dijkstra_path的最后一位数据
        #         all_addresses_valid = True
        #         for address in value:
        #             if ((address != dijkstra_path[-1]) and (address not in unvisited_nodes)):
        #                 all_addresses_valid = False
        #                 break

        #         # 如果所有地址都满足条件, 则保留该键值对
        #         if (all_addresses_valid):
        #             remain_distance_store[key] = value
        #     distance_store_copy = remain_distance_store.copy() # 更新distance_store_copy
        #     current_path, unvisited_nodes = self.dijkstra(remain_distance_store, unvisited_nodes[0])
        #     dijkstra_path += current_path
            
        return dijkstra_path
               
    # 运行find_path()函数, 每次调用一个区的数据去进行最短路径的查找
    def run_find_path(self):
        all_path = list() # 用于储存所有的最短路径
        for i in range(len(self.location_collect_split_district)):
            # length为1说明没有别的任何地址, 只储存了最基础的仓库地址
            if (len(self.location_collect_split_district[i]) != 1):
                all_path.append(self.find_path(self.calculate_distance(self.location_collect_split_district[i])))
            else:
                continue
        return all_path
    
    # --------------------------------------------------------- #
    
    def plot_route_on_map(self, location_collect, shortest_path):
        # 创建一个folium地图对象, 初始位置设为仓库的位置
        map_center = [location_collect[0][1], location_collect[0][2]]
        route_map = folium.Map(location=map_center, zoom_start=10)
        
        # 创建一个字典, 方便通过地址快速查找经纬度和区域
        location_dict = {loc[0]: loc[1:] for loc in location_collect}
        # print(location_dict)  # 调试输出
        
        # 为每条路径创建一个不同颜色的线条
        colors = ["blue", "green", "purple", "orange", "darkred", "lightred", "beige", "darkblue", "darkgreen", "cadetblue", "darkpurple", "white", "pink", "lightblue", "lightgreen", "gray", "black"]
        
        # 遍历shortest_path中的每个子列表
        # enumerate函数用于在遍历列表时, 同时获得元素的索引和值.
        for index, path in enumerate(shortest_path):
            # 存储路径的经纬度
            route_coords = []
            
            # 通过地址查找经纬度并添加到路径坐标列表中
            for address in path:
                if (address in location_dict):
                    latitude, longitude, district = location_dict[address]
                    route_coords.append([latitude, longitude])
                    print(f"Address: {address}, Lat: {latitude}, Lon: {longitude}, District: {district}")  # 调试输出
                else:
                    print(f"Address not found: {address}")  # 调试输出
            
            # 绘制路径
            if (route_coords):
                # 添加路径线条到地图, 并设置颜色, 宽度和透明度
                folium.PolyLine(route_coords, color=colors[index % len(colors)], weight=5, opacity=0.8).add_to(route_map)
                
                # 为每个路径点添加标记
                for coord, address in zip(route_coords, path):
                    folium.Marker(location=coord, popup=address, icon=folium.Icon(color="red")).add_to(route_map)
        
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
        # distance_store: dictionary容器储存两点之间的距离: {距离: (address1, address2), ...}
        # distance_store_update: dictionary容器储存过滤后的两点之间的距离, 仅包含仓库的距离信息: {距离: (address1, address2), ...}
        # time_warehouse_leave: 仓库对特定地址的出发时间
    #*#
    
    # 开始运行dijkstra算法, 并且找到最短路径, 再将路径绘制到地图上
    def start_find_path():
        location_collect = order_data.collect_location_info()
        # print(location_collect)
        all_path = order_data.run_find_path()
        # print(all_path)
        order_data.plot_route_on_map(location_collect, all_path)

    start_find_path()
    
    
    
    
    
    
    