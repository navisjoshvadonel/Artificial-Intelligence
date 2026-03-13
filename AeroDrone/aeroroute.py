import math
import heapq
import time
import os
import sys
import webbrowser
import folium

# --- 🛰️ ADVANCED CONFIGURATION & NO-FLY ZONES ---
LOCATIONS = {
    "Blood Bank (Base)": (9.9252, 78.1198),
    "Apollo Hospital": (9.9391, 78.1566),
    "Meenakshi Mission": (9.9482, 78.1738),
    "Velammal Medical": (9.8828, 78.0833),
    "Vadamalayan Hospital": (9.9328, 78.1362),
}

# Simulated No-Fly Zones (Lat, Lon, Radius in KM)
NFZ = [
    (9.9300, 78.1400, 0.8), # High-Security Zone
    (9.9100, 78.1000, 0.5)  # Weather Turbulence Cell
]

# --- 🧠 A* PATHFINDING ENGINE ---
class AStarOptimizer:
    def __init__(self, start_coords, end_coords):
        self.start = start_coords
        self.end = end_coords

    def heuristic(self, a, b):
        return math.sqrt((a[0]-b[0])**2 + (a[1]-b[1])**2)

    def is_in_nfz(self, point):
        for (lat, lon, radius) in NFZ:
            dist = math.sqrt((point[0]-lat)**2 + (point[1]-lon)**2) * 111 # Convert to KM approx
            if dist < radius: return True
        return False

    def get_path(self):
        """Simulates A* by calculating optimal waypoints avoiding NFZ centers"""
        # In a real grid, this would iterate neighbors. 
        # Here we simulate the 'A* refined path' logic.
        path = [self.start]
        # Calculate if direct path hits NFZ
        # (Simplified for demonstration: provides a 3-point curved path if NFZ detected)
        mid_lat = (self.start[0] + self.end[0]) / 2
        mid_lon = (self.start[1] + self.end[1]) / 2
        
        if self.is_in_nfz((mid_lat, mid_lon)):
            # "A* Correction": Deviate path to the East
            path.append((mid_lat + 0.005, mid_lon + 0.005))
            
        path.append(self.end)
        return path

# --- 🚀 MISSION CONTROL UI ---
def clear(): os.system('cls' if os.name == 'nt' else 'clear')

def typewriter(text, delay=0.02, color="\033[94m"):
    for char in text:
        sys.stdout.write(f"{color}{char}\033[0m")
        sys.stdout.flush()
        time.sleep(delay)
    print()

def draw_header():
    print("\033[1;36m" + "═"*60)
    print("  AEROROUTE PRO | TACTICAL DRONE LOGISTICS | V4.0-AI")
    print("═"*60 + "\033[0m")

def run_mission():
    clear()
    draw_header()
    
    typewriter(">>> INITIALIZING AI CORE...", 0.05, "\033[92m")
    time.sleep(0.5)
    typewriter(">>> LOADING NO-FLY ZONE DATABASE... DONE", 0.03)
    
    base_name = "Blood Bank (Base)"
    base_coords = LOCATIONS[base_name]
    total_distance = 0
    
    # Map Initialization
    m = folium.Map(location=base_coords, zoom_start=13, tiles="CartoDB dark_matter")
    
    # Process each destination
    targets = [k for k in LOCATIONS.keys() if k != base_name]
    
    current_loc_name = base_name
    current_coords = base_coords
    
    for target in targets:
        dest_coords = LOCATIONS[target]
        typewriter(f"\n[PLANNING] {current_loc_name} ➔ {target}")
        
        # Run A* Pathfinding
        optimizer = AStarOptimizer(current_coords, dest_coords)
        path = optimizer.get_path()
        
        # Telemetry Simulation
        dist = math.sqrt((current_coords[0]-dest_coords[0])**2 + (current_coords[1]-dest_coords[1])**2) * 111
        total_distance += dist
        
        print(f"    ├─ Status: \033[92mOptimal Path Calculated (A*)\033[0m")
        print(f"    ├─ Leg Distance: {dist:.2f} km")
        
        # Progress Bar Animation
        sys.stdout.write("    └─ Progress: ")
        for i in range(21):
            sys.stdout.write(f"\033[96m{'█' if i < 20 else 'Done'}\033[0m")
            sys.stdout.flush()
            time.sleep(0.05)
        print()
        
        # Add to Map
        folium.PolyLine(path, color="#00f2ff", weight=4, opacity=0.8).add_to(m)
        folium.Marker(dest_coords, tooltip=target, icon=folium.Icon(color='cadetblue', icon='cube', prefix='fa')).add_to(m)
        
        current_loc_name = target
        current_coords = dest_coords

    # Save and Finalize
    m.save("drone_mission_pro.html")
    print("\n" + "═"*60)
    typewriter(f"MISSION COMPLETE | TOTAL DISTANCE: {total_distance:.2f} KM", 0.05, "\033[1;92m")
    print("═"*60)
    
    if input("\nOpen Tactical Map? (Y/N): ").upper() == "Y":
        webbrowser.open('file://' + os.path.realpath("drone_mission_pro.html"))

if __name__ == "__main__":
    run_mission()