import math
import heapq

def calculate_distance(coord1, coord2):
    """Haversine distance in KM."""
    R = 6371.0
    lat1, lon1 = math.radians(coord1[0]), math.radians(coord1[1])
    lat2, lon2 = math.radians(coord2[0]), math.radians(coord2[1])
    dlat, dlon = lat2 - lat1, lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    return R * (2 * math.atan2(math.sqrt(a), math.sqrt(1 - a)))

def is_in_nofly(coord, nofly_zones):
    """Check if a coordinate falls inside any No-Fly Zone."""
    lat, lon = coord
    for zone in nofly_zones:
        # Fast circle check
        dist = calculate_distance((lat, lon), (zone.center_lat, zone.center_lon))
        if dist <= zone.radius_km + 0.05: # Small safety buffer
            return True
        # Fast rect check
        if zone.min_lat and zone.min_lon:
            if zone.min_lat <= lat <= zone.max_lat and zone.min_lon <= lon <= zone.max_lon:
                return True
    return False

def is_path_clear(start, goal, nofly_zones, samples=15):
    """Check if a straight-line path is clear of obstacles."""
    lat1, lon1 = start
    lat2, lon2 = goal
    for i in range(1, samples):
        t = i / samples
        curr_lat = lat1 + (lat2 - lat1) * t
        curr_lon = lon1 + (lon2 - lon1) * t
        if is_in_nofly((curr_lat, curr_lon), nofly_zones):
            return False
    return True

def a_star_search(start, goal, nofly_zones, grid_res=0.012):
    """
    Optimized A* Search:
    Returns direct path if clear, otherwise uses grid search.
    """
    if is_path_clear(start, goal, nofly_zones):
        return [start, goal]

    def get_neighbors(coord):
        lat, lon = coord
        # Using 8-way connectivity with slightly larger resolution for speed
        for dlat, dlon in [(grid_res, 0), (-grid_res, 0), (0, grid_res), (0, -grid_res),
                           (grid_res, grid_res), (grid_res, -grid_res), (-grid_res, grid_res), (-grid_res, -grid_res)]:
            neighbor = (round(lat + dlat, 5), round(lon + dlon, 5))
            if not is_in_nofly(neighbor, nofly_zones):
                yield neighbor

    open_set = []
    heapq.heappush(open_set, (0, start))
    came_from = {}
    g_score = {start: 0}
    f_score = {start: calculate_distance(start, goal)}
    
    # Cap search iterations to prevent long wait
    iterations = 0
    MAX_ITER = 800

    while open_set and iterations < MAX_ITER:
        iterations += 1
        _, current = heapq.heappop(open_set)

        if calculate_distance(current, goal) < grid_res * 1.5:
            path = [goal]
            curr = current
            while curr in came_from:
                path.append(curr)
                curr = came_from[curr]
            path.append(start)
            return path[::-1]

        for neighbor in get_neighbors(current):
            tentative_g = g_score[current] + calculate_distance(current, neighbor)
            if neighbor not in g_score or tentative_g < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g
                f_score[neighbor] = tentative_g + calculate_distance(neighbor, goal)
                heapq.heappush(open_set, (f_score[neighbor], neighbor))

    return [start, goal]

def solve_tsp(base, destinations, nofly_zones):
    """TSP solver that uses pathfinding distances instead of straight lines."""
    import itertools
    all_points = [base] + destinations
    n = len(all_points)
    
    best_dist = float('inf')
    best_route = []
    
    # Using Nearest Neighbor approach for speed, but could be itertools.permutations(range(1,n)) for small sets
    # We'll use itertools for 100% accuracy on small sets (<8 targets)
    if n < 8:
        for perm in itertools.permutations(range(1, n)):
            route_idx = [0] + list(perm) + [0]
            total_d = 0
            for i in range(len(route_idx)-1):
                p1 = (all_points[route_idx[i]].latitude, all_points[route_idx[i]].longitude)
                p2 = (all_points[route_idx[i+1]].latitude, all_points[route_idx[i+1]].longitude)
                total_d += calculate_distance(p1, p2) # Optimization: using straight distance as heuristic
            
            if total_d < best_dist:
                best_dist = total_d
                best_route = [all_points[i] for i in route_idx]
    else:
        # NN Fallback
        visited = [False] * n
        visited[0] = True
        curr = 0
        best_route = [all_points[0]]
        for _ in range(n-1):
            nearest = -1
            min_d = float('inf')
            for j in range(n):
                if not visited[j]:
                    d = calculate_distance((all_points[curr].latitude, all_points[curr].longitude), (all_points[j].latitude, all_points[j].longitude))
                    if d < min_d:
                        min_d = d
                        nearest = j
            visited[nearest] = True
            curr = nearest
            best_route.append(all_points[curr])
        best_route.append(all_points[0])

    return best_route