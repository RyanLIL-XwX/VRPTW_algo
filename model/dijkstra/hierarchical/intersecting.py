from shapely.geometry import LineString
from typing import List
import random
import math
from tqdm import tqdm


def distance(order1, order2):
    return math.sqrt((order1.receiving_latitude - order2.receiving_latitude) ** 2 +
                     (order1.receiving_longitude - order2.receiving_longitude) ** 2)


def calculate_total_distance(route):
    if len(route) < 2:
        return 0.0
    total_distance = 0.0
    for i in range(len(route) - 1):
        total_distance += distance(route[i], route[i + 1])
    return total_distance


def has_self_intersection(path):
    if len(path) < 2:
        return False
    line = LineString([(order.receiving_latitude, order.receiving_longitude) for order in path])
    return not line.is_simple


def crossover(parent1, parent2):
    size = len(parent1)
    start, end = sorted(random.sample(range(size), 2))
    child = [None] * size
    child[start:end] = parent1[start:end]

    for item in parent2:
        if item not in child:
            for i in range(size):
                if child[i] is None:
                    child[i] = item
                    break
    return child


def mutate(route, mutation_rate=0.01):
    for i in range(len(route)):
        if random.random() < mutation_rate:
            j = random.randint(0, len(route) - 1)
            route[i], route[j] = route[j], route[i]
    return route


def select(population, fitnesses, k=3):
    selected = random.choices(population, weights=fitnesses, k=k)
    return min(selected, key=lambda route: calculate_total_distance(route))


def two_opt(route):
    best = route
    improved = True
    while improved:
        improved = False
        for i in range(1, len(route) - 1):
            for j in range(i + 1, len(route)):
                if j - i == 1:
                    continue
                new_route = route[:i] + route[i:j][::-1] + route[j:]
                if calculate_total_distance(new_route) < calculate_total_distance(best):
                    best = new_route
                    improved = True
    return best


def genetic_algorithm(route, population_size=50, generations=100, mutation_rate=0.01):
    if len(route) < 2:
        return route
    population = [random.sample(route, len(route)) for _ in range(population_size)]
    with tqdm(total=generations, desc="Optimizing route", unit="gen") as pbar:
        for generation in range(generations):
            fitnesses = [1 / calculate_total_distance(ind) if calculate_total_distance(ind) > 0 else float('inf') for
                         ind in
                         population]
            new_population = []
            for _ in range(population_size):
                parent1 = select(population, fitnesses)
                parent2 = select(population, fitnesses)
                child = crossover(parent1, parent2)
                child = mutate(child, mutation_rate)
                new_population.append(two_opt(child))  # 使用2-opt优化
            population = new_population
            pbar.update(1)
    return min(population, key=lambda route: calculate_total_distance(route))


def optimize_vehicle_route(vehicle):
    if has_self_intersection(vehicle.path):
        vehicle.path = genetic_algorithm(vehicle.path, population_size=100, generations=200)  # 增加迭代次数和种群大小
    return vehicle


def optimize_vehicle_routes(vehicles: List) -> List:
    optimized_vehicles = []
    non_intersecting_vehicles = []

    for vehicle in vehicles:
        if has_self_intersection(vehicle.path):
            optimized_vehicles.append(optimize_vehicle_route(vehicle))
        else:
            non_intersecting_vehicles.append(vehicle)

    return non_intersecting_vehicles + optimized_vehicles
