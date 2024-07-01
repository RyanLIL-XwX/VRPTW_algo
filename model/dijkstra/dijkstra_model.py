import heapdict

def dijkstra(distance_store, start_address):
    """
    使用 Dijkstra 算法计算从起点到所有节点的最短路径，并返回访问所有节点的顺序列表。
    
    :param distance_store: 一个字典，键是距离，值是两个地址的元组
    :param start_address: 起始地址
    :return: 从起点访问所有其他节点的顺序列表
    """
    # 创建图的邻接表表示法
    graph = {}
    for distance, (address1, address2) in distance_store.items():
        if (address1 not in graph.keys()):
            graph[address1] = {}
        if (address2 not in graph.keys()):
            graph[address2] = {}
        graph[address1][address2] = distance
        graph[address2][address1] = distance
    
    # 初始化距离字典，所有节点的初始距离为无穷大（假设为 float('inf')）
    distances = {node: float('inf') for node in graph}
    distances[start_address] = 0  # 起点的距离为 0
    
    # 初始化前驱字典，用于重建最短路径
    predecessors = {node: None for node in graph}
    
    # 创建一个优先队列，并将起点加入其中
    priority_queue = heapdict.heapdict()
    priority_queue[start_address] = 0
    
    visited_order = []  # 记录访问顺序
    
    while priority_queue:
        # 从优先队列中取出具有最小距离的节点
        current_node, current_distance = priority_queue.popitem()
        
        # 记录当前访问的节点
        visited_order.append(current_node)
        
        # 遍历当前节点的所有邻居
        for neighbor, weight in graph[current_node].items():
            distance = current_distance + weight
            
            # 如果找到更短的路径，则更新距离和前驱节点
            if distance < distances[neighbor]:
                distances[neighbor] = distance
                predecessors[neighbor] = current_node
                priority_queue[neighbor] = distance

    return visited_order

# 示例 distance_store 数据
distance_store = {
    4.357465079709993: ('北京市东城区北京市东城区朝阳门北大街8号2号楼1层2-58', '北京市东城区广渠家园3号楼1层'),
    1.1090289763242347: ('北京市东城区北京市东城区朝阳门北大街8号2号楼1层2-58', '北京市东城区东直门南大街1号2层1-1202内P02-20商铺'),
    5.123010116782912: ('北京市东城区北京市东城区朝阳门北大街8号2号楼1层2-58', '北京市东城区光明路11号天玉大厦1层西侧'),
    0.22911863079497077: ('北京市东城区北京市东城区朝阳门北大街8号2号楼1层2-58', '北京市东城区新中街瑞士公寓1、2层L103&L202A'),
    5.456769547032478: ('北京市东城区广渠家园3号楼1层', '北京市东城区东直门南大街1号2层1-1202内P02-20商铺'),
    1.2963442589942702: ('北京市东城区广渠家园3号楼1层', '北京市东城区光明路11号天玉大厦1层西侧'),
    4.56026072793704: ('北京市东城区广渠家园3号楼1层', '北京市东城区新中街瑞士公寓1、2层L103&L202A'),
    6.1699452481750505: ('北京市东城区东直门南大街1号2层1-1202内P02-20商铺', '北京市东城区光明路11号天玉大厦1层西侧'),
    0.9360571067903632: ('北京市东城区东直门南大街1号2层1-1202内P02-20商铺', '北京市东城区新中街瑞士公寓1、2层L103&L202A'),
    5.343924606627421: ('北京市东城区光明路11号天玉大厦1层西侧', '北京市东城区新中街瑞士公寓1、2层L103&L202A')
}

# 设置起点
start_address = '北京市东城区东直门南大街1号2层1-1202内P02-20商铺'

# 运行 Dijkstra 算法
shortest_path = dijkstra(distance_store, start_address)

# print("从起点访问所有其他节点的顺序列表:")
print(shortest_path)
