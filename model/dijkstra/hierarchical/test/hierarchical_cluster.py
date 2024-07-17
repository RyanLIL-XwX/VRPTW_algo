import numpy as np
from scipy.cluster.hierarchy import linkage, fcluster

def cluster_location_hierarchical(location_collect, distance_threshold=1.0):
    """
    对订单进行层次聚类

    参数:
    - location_collect: 所有的订单信息
    - distance_threshold: 距离阈值，用于确定簇的数量

    返回:
    - clustered_list: 聚类后的订单列表，每个簇的第一个位置是仓库信息
    
    使用了linkage函数, 并选择了ward方法进行聚类. 
    - Ward方法是一种最小化总方差的聚类方法, 属于凝聚层次聚类的一种.
    - 凝聚层次聚类: 从每个点自身作为一个簇开始, 不断合并最近的簇, 直到满足停止条件. 
    """
    # 提取经纬度信息, 将每个订单的经纬度组成一个坐标数组
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

    # 构建结果列表, 确保每个簇的第一个位置是仓库信息
    clustered_list = []
    warehouse_info = ['北京市顺义区顺平路576号', 40.1196490409737, 116.60616697651679, '仓库']
    
    for cluster in clustered_dict.values():
        # 如果簇中没有仓库信息, 将其添加到第一个位置
        if warehouse_info not in cluster:
            cluster.insert(0, warehouse_info)
        clustered_list.append(cluster)

    return clustered_list

# 示例地址列表
location_collect = [
    ['北京市顺义区顺平路576号', 40.1196490409737, 116.60616697651679, '仓库'], 
    ['北京市密云县古北口镇司马台村国际休闲旅游度假区第一层101单元', 40.662436, 117.251497, '密云区'], 
    ['北京市大兴区区西红门宏福路鸿坤生活广场', 39.797382, 116.346796, '大兴区'], 
    ['北京市大兴区黄村东大街38号院2号楼1层（01）内1F-11', 39.73531, 116.349419, '大兴区'], 
    ['北京市大兴区金星西路3号', 39.770126, 116.340761, '大兴区'], 
    ['北京市大兴区西红门镇欣宁大街15号1层1-01-28-R号', 39.795298, 116.33387, '大兴区'], 
    ['北京市密云区密云镇鼓楼南大街1号1层的1129-F1A005、1129-F1-A004、1129-F1-B008店铺', 40.380933, 116.852228, '密云区'], 
    ['北京市密云区滨河路178号万象汇一层', 40.361323, 116.841688, '密云区'], 
    ['北京市东城区北京市东城区朝阳门北大街8号2号楼1层2-58', 39.936825, 116.442792, '东城区'], 
    ['北京市东城区广渠家园3号楼1层', 39.898703, 116.454626, '东城区'], 
    ['北京市东城区东直门南大街1号2层1-1202内P02-20商铺', 39.946079, 116.43794, '东城区'], 
    ['北京市大兴区旧宫镇旧宫西路3号(物美超市左侧)', 39.811108, 116.449658, '大兴区'], 
    ['北京市东城区光明路11号天玉大厦1层西侧', 39.890756, 116.443508, '东城区'], 
    ['北京市东城区新中街瑞士公寓1、2层L103&L202A', 39.938815, 116.443489, '东城区'], 
    ['北京市昌平区南口镇陈庄村(京藏高速北侧)八达岭奥特莱斯F2', 40.240958, 116.176189, '昌平区'], 
    ['北京市昌平区立汤路186号院1号楼02层(02)201内208单元', 40.104742, 116.419048, '昌平区'], 
    ['北京市昌平区立汤路186号院1号楼B1层B1041', 40.104742, 116.419048, '昌平区'], 
    ['北京市昌平区立汤路188号院1号万优汇商厦1层', 40.063747, 116.421787, '昌平区'], 
    ['北京市昌平区陈家营西路3号院23号楼 招商嘉铭珑原商业楼 1层101-2单元', 40.04709, 116.407605, '昌平区'], 
    ['北京市昌平区黄平路19号院1号楼B单元101-02室', 40.07174, 116.353812, '昌平区'], 
    ['北京市昌平区南口镇陈庄村(京藏高速北侧)八达岭奥特莱斯F2(2)', 40.240958, 116.176189, '昌平区']
]

clustered_locations = cluster_location_hierarchical(location_collect, distance_threshold=1.0)

# 打印聚类结果
for i, cluster in enumerate(clustered_locations):
    print(f"Cluster {i}:")
    for loc in cluster:
        print(loc)
