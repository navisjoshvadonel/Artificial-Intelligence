from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.utils.safestring import mark_safe
from .models import Location
import folium
import math
import datetime

# ====================== 1. AUTHENTICATION ======================
def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            return redirect('home')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('login')

# ====================== 2. BATTERY LOGIC ======================
def estimate_battery(total_km, num_stops, payload_kg=2.5):
    BATTERY_CAPACITY_WH  = 5500.0
    CRUISE_WH_PER_KM     = 45.0
    HOVER_POWER_W        = 450.0
    HOVER_SEC_PER_STOP   = 90.0
    SAFETY_MARGIN        = 0.20
    TECH_FACTOR          = 1.10

    cruise_energy = total_km * CRUISE_WH_PER_KM
    hover_energy  = num_stops * HOVER_POWER_W * (HOVER_SEC_PER_STOP / 3600)
    total_energy = (cruise_energy + hover_energy) * TECH_FACTOR
    payload_penalty = 1.0 + (max(0, payload_kg - 1.0) * 0.05)
    total_energy *= payload_penalty
    battery_used = (total_energy / BATTERY_CAPACITY_WH) * 100
    return min(round(battery_used * (1 + SAFETY_MARGIN), 1), 100.0)

def calculate_distance(coord1, coord2):
    R = 6371
    lat1, lon1 = coord1
    lat2, lon2 = coord2
    dlat, dlon = math.radians(lat2 - lat1), math.radians(lon2 - lon1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
    return round(R * (2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))), 3)

def solve_tsp(base_location, dest_locations):
    points = [base_location] + dest_locations
    n = len(points)
    route_indices = [0]
    visited = [False] * n
    visited[0] = True
    current = 0
    
    for _ in range(n - 1):
        min_dist = float('inf')
        next_idx = -1
        for i in range(n):
            if not visited[i]:
                d = calculate_distance((points[current].latitude, points[current].longitude), 
                                     (points[i].latitude, points[i].longitude))
                if d < min_dist:
                    min_dist = d
                    next_idx = i
        if next_idx != -1:
            route_indices.append(next_idx)
            visited[next_idx] = True
            current = next_idx
            
    # Return to base
    route_indices.append(0)
    
    route_points = [points[i] for i in route_indices]
    total_km = 0
    for i in range(len(route_points) - 1):
        total_km += calculate_distance((route_points[i].latitude, route_points[i].longitude),
                                     (route_points[i+1].latitude, route_points[i+1].longitude))
                                     
    return route_points, round(total_km, 2)

# ====================== 3. MAIN HOME VIEW ======================
@login_required(login_url='/login/')
def home(request):
    districts = Location.objects.values_list('district', flat=True).distinct().order_by('district')
    selected_district = request.POST.get('district') or request.GET.get('district')
    
    # Default to first district if none selected
    if not selected_district and districts.exists():
        selected_district = districts[0]

    locations = Location.objects.filter(district=selected_district) if selected_district else Location.objects.none()
    
    context = {
        'districts': districts,
        'selected_district': selected_district,
        'hospitals': locations,
        'show_result': False,
        'date': datetime.datetime.now().strftime("%d %B %Y, %H:%M")
    }

    if request.method == 'POST' and 'base_station' in request.POST:
        try:
            base_id = request.POST.get('base_station')
            dest_ids = request.POST.getlist('destinations')
            
            if base_id and dest_ids:
                base_loc = Location.objects.get(id=base_id)
                dest_locs = list(Location.objects.filter(id__in=dest_ids))
                
                route_locs, total_km = solve_tsp(base_loc, dest_locs)
                route_coords = [(loc.latitude, loc.longitude) for loc in route_locs]

                # --- HIGH ACCURACY MAP ---
                m = folium.Map(location=[base_loc.latitude, base_loc.longitude], zoom_start=12, tiles="OpenStreetMap")
                
                folium.TileLayer(
                    tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
                    attr="Esri", name="Satellite (High Res)", overlay=False
                ).add_to(m)

                # Draw Route (Solid Blue)
                folium.PolyLine(route_coords, color="#0d6efd", weight=5, opacity=0.8).add_to(m)

                # Markers
                for i, loc in enumerate(route_locs):
                    # Skip the last one as it's the base again
                    if i > 0 and i == len(route_locs) - 1: continue
                    
                    color = "green" if i == 0 else "blue"
                    icon = "home" if i == 0 else "info-sign"
                    label = "Base Station" if i == 0 else f"Stop {i}"
                    
                    folium.Marker(
                        [loc.latitude, loc.longitude], 
                        popup=f"<b>{loc.name}</b><br>{label}", 
                        icon=folium.Icon(color=color, icon=icon)
                    ).add_to(m)

                folium.LayerControl(position="topright").add_to(m)
                
                context.update({
                    'map_html': mark_safe(m._repr_html_()),
                    'total_km': total_km,
                    'est_time': int(total_km * 1.5), # Slightly more realistic flight time
                    'battery': estimate_battery(total_km, len(dest_locs)),
                    'show_result': True,
                    'route_locs': route_locs
                })
        except Exception as e:
            context['error'] = str(e)

    return render(request, 'index.html', context)
