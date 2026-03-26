from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.utils.safestring import mark_safe
from .models import Location, NoFlyZone
from .utils import a_star_search, calculate_distance, solve_tsp
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

# ====================== 2. LOGICAL MISSION TELEMETRY ======================
def calculate_mission_metrics(path_coords, num_destinations):
    """
    Calculates logical flight metrics:
    - Ground Distance: Raw horizontal path length.
    - Air Range: Ground Distance + Vertical Takeoff/Landing overhead.
    """
    ground_km = 0
    for i in range(len(path_coords) - 1):
        ground_km += calculate_distance(path_coords[i], path_coords[i+1])
    
    # Vertical Maneuvers: Each stop (dest + start/end) involves one landing and one takeoff.
    # Total stops in a tour = num_destinations + 1 (the hub)
    # Total Takeoff/Landing cycles = num_destinations + 1
    # Altitude = 0.12km (120m)
    vertical_overhead = (num_destinations + 1) * (0.12 * 2)
    
    total_air_km = ground_km + vertical_overhead
    return round(ground_km, 3), round(total_air_km, 3)

def estimate_battery(air_km, num_stops):
    """
    Professional Drone Consumption Model.
    """
    # 10% battery per 10km air distance + 2.5% per takeoff/landing cycle
    consumption = (air_km / 10.0) * 12.0
    consumption += (num_stops + 1) * 2.5 
    
    return min(round(consumption, 1), 100.0)

# ====================== 3. MAIN HOME VIEW ======================
@login_required(login_url='/login/')
def home(request):
    districts = Location.objects.values_list('district', flat=True).distinct().order_by('district')
    selected_district = request.POST.get('district') or request.GET.get('district')
    
    # Default to first district if none selected
    if not selected_district and districts.exists():
        selected_district = districts[0]

    locations = Location.objects.filter(district=selected_district) if selected_district else Location.objects.none()
    
    # --- PERSISTENT STATE LOGIC ---
    # Try to get drone's last location from session; otherwise default to identified Govt Hospital
    last_loc_id = request.session.get('drone_last_loc_id')
    last_loc = Location.objects.filter(id=last_loc_id).first() if last_loc_id else None
    
    govt_hospital = locations.filter(name__icontains="Govt").first() or \
                    locations.filter(name__icontains="GH").first() or \
                    locations.first()
    
    # Use drone's current (persistent) location if it belongs to the selected district
    drone_base = last_loc if last_loc and last_loc.district == selected_district else govt_hospital

    # --- MADURAI HUB IDENTIFICATION ---
    madurai_hub = Location.objects.filter(name__icontains="Government Rajaji Hospital").first() or \
                  Location.objects.filter(district="Madurai", is_blood_bank=True).first()

    context = {
        'districts': districts,
        'selected_district': selected_district,
        'hospitals': locations,
        'default_base': drone_base,
        'madurai_hub': madurai_hub,
        'show_result': False,
        'date': datetime.datetime.now().strftime("%d %B %Y, %H:%M")
    }

    if request.method == 'POST' and ('destinations' in request.POST or 'base_station' in request.POST):
        try:
            # --- EXACT ORDER LOGIC ---
            # Capture the specific order from the hidden 'ordered_destinations' field
            ordered_ids = request.POST.get('ordered_destinations', '').split(',')
            ordered_ids = [oid for oid in ordered_ids if oid.strip()]
            
            # --- BASE STATION IDENTIFICATION ---
            base_loc = drone_base
            
            if ordered_ids:
                # User specified exact order via clicks
                dest_locs = []
                for oid in ordered_ids:
                    loc = Location.objects.filter(id=oid).first()
                    if loc: dest_locs.append(loc)
                route_locs = [base_loc] + dest_locs
            else:
                # Fallback to TSP if order wasn't captured (standard checkbox submit)
                dest_ids = request.POST.getlist('destinations')
                dest_locs = list(Location.objects.filter(id__in=dest_ids))
                route_locs = solve_tsp(base_loc, dest_locs, list(NoFlyZone.objects.all()))
            
            nofly_zones = list(NoFlyZone.objects.all())
            
            if base_loc and dest_locs:
                # Build fine-grained A* path following the specified order
                full_path_coords = []
                for i in range(len(route_locs)-1):
                    p1 = (route_locs[i].latitude, route_locs[i].longitude)
                    p2 = (route_locs[i+1].latitude, route_locs[i+1].longitude)
                    seg_path = a_star_search(p1, p2, nofly_zones)
                    full_path_coords.extend(seg_path[:-1])
                full_path_coords.append((route_locs[-1].latitude, route_locs[-1].longitude))

                # Logic: Accurate Metrics (Ground vs Air)
                ground_km, total_air_km = calculate_mission_metrics(full_path_coords, len(dest_locs))
                
                # Efficiency: How much better is the AI path than the straight line tour?
                # Actually, efficiency should show optimization quality.
                # We'll compare AI Path (Ground) vs Straight Line Tour (Ground)
                straight_tour_km = 0
                for i in range(len(route_locs)-1):
                    straight_tour_km += calculate_distance((route_locs[i].latitude, route_locs[i].longitude), 
                                                         (route_locs[i+1].latitude, route_locs[i+1].longitude))
                
                # If they are equal, efficiency is 100% (ideal). 
                # If A* had to bend, Ground KM > Straight Tour KM, so efficiency drops slightly.
                efficiency = round((straight_tour_km / ground_km * 100), 1) if ground_km > 0 else 100

                # --- ADVANCED MAP VIZ ---
                m = folium.Map(location=[base_loc.latitude, base_loc.longitude], zoom_start=14, tiles="CartoDB Positron")
                
                # Draw No-Fly Zones
                for zone in nofly_zones:
                    folium.Circle(
                        location=[zone.center_lat, zone.center_lon],
                        radius=zone.radius_km * 1000,
                        color="#ff4d4d", fill=True, fill_opacity=0.4,
                        popup=f"DANGER: {zone.name}"
                    ).add_to(m)

                # Draw A* Intelligent Route
                if full_path_coords:
                    folium.PolyLine(full_path_coords, color="#0066FF", weight=5, opacity=0.8, 
                                  tooltip="AI Optimized Path").add_to(m)

                # Markers
                for i, loc in enumerate(route_locs):
                    # Label markers for clarity
                    if i == 0:
                        label = "START: " + loc.name
                        icon_color = "green"
                    elif i == len(route_locs) - 1:
                        label = "FINAL: " + loc.name
                        icon_color = "red"
                    else:
                        label = f"STOP {i}: {loc.name}"
                        icon_color = "blue"

                    folium.Marker(
                        [loc.latitude, loc.longitude], 
                        popup=label,
                        tooltip=label,
                        icon=folium.Icon(color=icon_color, icon="hospital-o", prefix="fa")
                    ).add_to(m)

                # --- HUB-RELATIVE VECTOR CALCULATIONS ---
                route_data = []
                if madurai_hub:
                    hub_coord = (madurai_hub.latitude, madurai_hub.longitude)
                    for i, loc in enumerate(route_locs):
                        target_coord = (loc.latitude, loc.longitude)
                        dist = calculate_distance(hub_coord, target_coord)
                        from .utils import calculate_bearing # local import for safety
                        bearing = calculate_bearing(hub_coord, target_coord)
                        
                        # Friendly navigation name (N, NE, E...)
                        directions = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]
                        dir_name = directions[int((bearing + 22.5) / 45) % 8]
                        
                        route_data.append({
                            'loc': loc,
                            'step': i,
                            'vec_dist': round(dist, 2),
                            'vec_bearing': round(bearing, 1),
                            'vec_dir': dir_name
                        })

                # --- UPDATE PERSISTENT STATE ---
                # The drone's new location is the last destination in this mission
                request.session['drone_last_loc_id'] = route_locs[-1].id

                # DEBUG: Check if path exists
                if not full_path_coords:
                    print("WARNING: full_path_coords is empty!")

                context.update({
                    'map_html': mark_safe(m._repr_html_()),
                    'ground_km': ground_km,
                    'total_km': total_air_km,
                    'est_time': int(total_air_km * (60/50)) + (len(dest_locs) * 2), 
                    'battery': estimate_battery(total_air_km, len(dest_locs)),
                    'efficiency': efficiency,
                    'route_data': route_data,
                    'show_result': True,
                })
        except Exception as e:
            import traceback
            print(traceback.format_exc()) # Debugging to terminal
            context['error'] = f"Mission Planning Error: {str(e)}"

    return render(request, 'index.html', context)
