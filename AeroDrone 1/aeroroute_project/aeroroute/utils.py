import math
import itertools

def calculate_distance(coord1, coord2):
    R = 6371
    lat1, lon1 = coord1
    lat2, lon2 = coord2
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return round(R * c, 3)

def solve_tsp(base, destinations):
    # destinations = list of Location objects
    all_points = [base] + destinations
    n = len(all_points)
    
    shortest = float('inf')
    best_route = []

    for perm in itertools.permutations(range(1, n)):   # 0 is base
        route_idx = [0] + list(perm) + [0]
        dist = 0
        for i in range(len(route_idx)-1):
            p1 = (all_points[route_idx[i]].latitude, all_points[route_idx[i]].longitude)
            p2 = (all_points[route_idx[i+1]].latitude, all_points[route_idx[i+1]].longitude)
            dist += calculate_distance(p1, p2)
        
        if dist < shortest:
            shortest = dist
            best_route = [all_points[i] for i in route_idx]
    
    return best_route, round(shortest, 2)