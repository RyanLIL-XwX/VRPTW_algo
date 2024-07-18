import numpy as np
from sklearn.cluster import KMeans
from sklearn.metrics import davies_bouldin_score

def determine_optimal_clusters_db_index(locations, max_clusters=15):
    """
    使用 Davies-Bouldin 指数确定 K-means 的最优簇数量

    参数:
    - locations: 地址的列表，每个地址包含名称、纬度、经度和描述信息
    - max_clusters: 最大簇数量

    返回:
    - optimal_k: 最优的簇数量
    """
    # 提取经纬度信息，排除仓库
    coords = np.array([[loc[1], loc[2]] for loc in locations if loc[3] != '仓库'], dtype=float)
    db_scores = []

    for k in range(2, max_clusters + 1):  # DB 指数在 k=1 时没有定义
        kmeans = KMeans(n_clusters=k, n_init=10, random_state=0).fit(coords)
        labels = kmeans.labels_
        db_index = davies_bouldin_score(coords, labels)
        db_scores.append(db_index)
    optimal_k = range(2, max_clusters + 1)[np.argmin(db_scores)]
    print(optimal_k)
    return optimal_k

def cluster_locations_kmeans(location_collect, n_clusters, n_init=10):
    """
    对地址进行 K-means 聚类

    参数:
    - location_collect: 地址的列表，每个地址包含名称、纬度、经度和描述信息
    - n_clusters: 聚类的簇数量
    - n_init: K-means 算法的初始运行次数

    返回:
    - clustered_location_collect: 聚类后的地址列表
    """
    warehouse_info = ['北京市顺义区顺平路576号', 40.1196490409737, 116.60616697651679, '仓库']
    # 提取经纬度信息，排除仓库
    coords = np.array([[loc[1], loc[2]] for loc in location_collect if loc[3] != '仓库'], dtype=float)

    # 使用 K-means 进行聚类
    kmeans = KMeans(n_clusters=n_clusters, n_init=n_init, random_state=0).fit(coords)
    labels = kmeans.labels_

    # 将地址按簇分类，初始每个簇包含仓库信息
    clustered_location_collect = [[warehouse_info] for _ in range(n_clusters)]
    non_warehouse_locations = [loc for loc in location_collect if loc[3] != '仓库']

    for label, loc in zip(labels, non_warehouse_locations):
        clustered_location_collect[label].append(loc)

    return clustered_location_collect

# 示例地址列表
location_collect = [['北京市顺义区顺平路576号', 40.1196490409737, 116.60616697651679, '仓库'], 
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
                    ['北京市昌平区南口镇陈庄村(京藏高速北侧)八达岭奥特莱斯F2(2)', 40.240958, 116.176189, '昌平区']]

# 确定最优簇数量
optimal_k = determine_optimal_clusters_db_index(location_collect, max_clusters=15)
print(f"Optimal number of clusters: {optimal_k}")

# 聚类地址
clustered_locations = cluster_locations_kmeans(location_collect, n_clusters=optimal_k)

# 打印聚类结果
for i, cluster in enumerate(clustered_locations):
    print(f"Cluster {i}:")
    for loc in cluster:
        print(loc)
