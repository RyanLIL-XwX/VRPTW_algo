# VRPTW
# Author: Hanzhen Qin, Shenhan Xu
import json
from haversine import haversine, Unit # 用来计算两个经纬度之间的距离
from datetime import datetime, timedelta # 用来计算时间

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
        self.item_weight = 0.0 # 单个订单的重量
        self.weight_collect = {} # 用于收集每个订单的重量信息的函数
        self.stay_period_info = {} # 用于收集每个订单的停留时间信息的函数
        self.first_order_address = None # 第一个订单的地址
        self.set_time = None # 设置时间
        self.set_delta_time = None # 设置时间间隔(分钟)
        self.set_mode = None # 设置时间计算模式
        self.check_weight = None # 检查车载重量是否可行
        self.check_volume = None # 检查车载空间是否可行
        self.arrive_time = None # 到达当前订单的时间(分钟)
        self.leave_time = None # 离开当前订单的时间(分钟)
        self.time_to_this_order = None # 到达当前订单的所需时间(分钟)
        self.single_stay_period = None # 单个订单的停留时间(分钟)
        self.set_receive_earliest_time = None # 设置最早收货时间
        self.set_receive_latest_time = None # 设置最晚收货时间
    
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
            location_collect.append([self.warehouse["address"], float(self.warehouse["latitude"]), float(self.warehouse["longitude"])])
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
    
    # 过滤所有关于仓库的距离信息
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
        # print(temp_collect)
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
    
    # 收集每个订单的重量信息, 储存在字典中, keys为订单号, value为(重量, 收货地址)
    def collect_weight_info(self):
        weight_collect = dict() # 用来收集每个订单的重量信息
        for i in range(len(self.order_list)):
            if ("orderCode" in self.order_list[i].keys() and "weight" in self.order_list[i].keys() and "receivingAddress" in self.order_list[i].keys() and self.order_list[i]["orderCode"] != None and self.order_list[i]["weight"] != None and self.order_list[i]["receivingAddress"] != None):
                weight_collect[self.order_list[i]["orderCode"]] = [self.order_list[i]["weight"], self.order_list[i]["receivingAddress"]]
            else:
                print("No enough information for the weight info.\n")
        self.weight_collect = weight_collect # 更新self.weight_collect属性
        return self.weight_collect
    
    # 计算每个订单的停留时间(单位: 分钟), helper function
    def calculate_stay_period(self, item_weight):
        stay_period = item_weight * self.parameters["handoverVariableTime"] + self.parameters["handoverFixedTime"]
        return stay_period

    # 收集每个订单的停留时间信息, 储存在字典中
    def collect_stay_period_info(self, weight_collect):
        stay_period_info = dict() # 用于存储每个订单的停留时间
        for i in weight_collect.keys():
            self.item_weight = weight_collect[i][0]
            # 如果当前订单的收货地址不在stay_period_info中, 则将当前订单的停留时间和订单号添加到stay_period_info中
            if (weight_collect[i][1] not in stay_period_info.keys()):
                stay_period_info[weight_collect[i][1]] = [self.calculate_stay_period(self.item_weight), [i]]
            # 如果当前订单的收货地址在stay_period_info中, 则将当前订单的停留时间和订单号添加到stay_period_info对应的keys中
            else:
                stay_period_info[weight_collect[i][1]][1].append(i)
                # 更新当前订单的停留时间(单位: 分钟)
                stay_period_info[weight_collect[i][1]][0] += self.calculate_stay_period(self.item_weight)
        return stay_period_info
    
    # --------------------------------------------------------- #
    
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
        
        # 将delta_time转换为timedelta对象，单位为分钟
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

if __name__ == "__main__":
    '''
    order data: VRPTW_model对象
    location_collect: list容器(lists of list): [[address, latitude, longitude], ...]
    distance_store: dictionary容器储存两点之间的距离: {距离: (address1, address2), ...}
    distance_store_update: dictionary容器储存过滤后的两点之间的距离, 仅包含仓库的距离信息: {距离: (address1, address2), ...}
    time_warehouse_leave: 仓库对特定地址的出发时间
    weight_collect: dictionary容器: {订单号: [重量, 收货地址]}
    order_stay_period_info: dictionary容器储存每个订单的停留时间: {收货地址: [停留时间(单位: 分钟), [订单号1, 订单号2, ...]]}
    '''
    # 创建一个VRPTW_model对象, 并将file作为参数传入
    # 函数: load_data(), parse_data(), __str__()
    file = input("Type the name of the file: ").strip() # strip()函数用于去除字符串两端的空格
    order_data = VRPTW_model(file)
    # print(order_data)
        
    # 测试所有class中的基础函数
    def testbasic():
        # 测试对于经纬度信息的收集
        # 函数: collect_location_info(), calculate_distance()
        location_collect = order_data.collect_location_info()
        # print(location_collect)
        distance_store = order_data.calculate_distance(location_collect)
        # print(distance_store)
        
        # 测试对于仓库出发信息的收集
        # 函数: warehouse_leave_info()
        distance_store_update = order_data.warehouse_leave_info(distance_store)
        # print(distance_store_update)
        time_warehouse_leave = order_data.time_warehouse_leave("北京市昌平区南口镇陈庄村(京藏高速北侧)八达岭奥特莱斯F2")
        # print(time_warehouse_leave)
        
        # 测试对于订单停留数间数据的收集
        # 函数: collect_weight_info(), collect_stay_period_info(), calculate_stay_period()
        weight_collect = order_data.collect_weight_info()
        # print(weight_collect)
        order_stay_period_info = order_data.collect_stay_period_info(weight_collect)
        # print(order_stay_period_info)
    
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

    # run test cases
    def runtest():
        testbasic() # all pass
        testcase1() # all pass
    
    runtest()
    
    
    
    
    
    
    