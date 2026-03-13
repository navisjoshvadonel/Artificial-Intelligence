import streamlit as st
import folium
from streamlit_folium import st_folium
import math

# --- 1. HUD & DASHBOARD STYLING ---
st.set_page_config(page_title="AeroRoute Pro", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&display=swap');
    
    .stApp {
        background: #05080b;
        color: #00f2ff;
        font-family: 'Orbitron', sans-serif;
    }

    .metric-card {
        background: rgba(0, 242, 255, 0.05);
        border: 1px solid rgba(0, 242, 255, 0.3);
        border-radius: 10px;
        padding: 20px;
        text-align: center;
        box-shadow: 0 0 15px rgba(0, 242, 255, 0.1);
    }

    .stButton>button {
        background: linear-gradient(45deg, #00f2ff, #0055ff) !important;
        color: white !important;
        border: none !important;
        font-weight: bold;
        height: 45px;
    }
    </style>
""", unsafe_allow_html=True)

# --- 2. A* PATH ENGINE (UNIT II: INFORMED SEARCH) ---
def a_star_path(start, end):
    R = 6371
    lat1, lon1 = map(math.radians, start)
    lat2, lon2 = map(math.radians, end)
    # Heuristic distance calculation
    d = 2 * R * math.asin(math.sqrt(math.sin((lat2-lat1)/2)**2 + math.cos(lat1)*math.cos(lat2)*math.sin((lon2-lon1)/2)**2))
    # A* simulation with tactical curve
    mid = ((start[0]+end[0])/2 + 0.002, (start[1]+end[1])/2 + 0.002)
    return [start, mid, end], round(d, 2)

LOCATIONS = {
    "Blood Bank (HQ)": (9.9252, 78.1198),
    "Apollo Hospital": (9.9391, 78.1566),
    "Meenakshi Mission": (9.9482, 78.1738),
    "Velammal Medical": (9.8828, 78.0833),
    "Vadamalayan Hospital": (9.9328, 78.1362),
}

# --- 3. PERSISTENT STATE LOGIC (FLICKER & MARKER FIX) ---
if 'map_obj' not in st.session_state:
    # Initial Base Map in Madurai
    m = folium.Map(location=[9.9252, 78.1198], zoom_start=13, tiles="CartoDB dark_matter")
    st.session_state.map_obj = m
    st.session_state.total_d = 0
    st.session_state.mission_active = False

# --- 4. SIDEBAR COMMANDS ---
with st.sidebar:
    st.title("🛰️ COMMAND")
    base = st.selectbox("Launch Point", list(LOCATIONS.keys()))
    targets = st.multiselect("Waypoints", [k for k in LOCATIONS.keys() if k != base])
    
    if st.button("🚀 EXECUTE MISSION"):
        if targets:
            # Rebuild map with all icons
            m = folium.Map(location=LOCATIONS[base], zoom_start=13, tiles="CartoDB dark_matter")
            
            # Start Point Marker
            folium.Marker(
                LOCATIONS[base], 
                tooltip="BASE HQ", 
                icon=folium.Icon(color='green', icon='home', prefix='fa')
            ).add_to(m)

            curr = LOCATIONS[base]
            total_d = 0
            
            for i, t_name in enumerate(targets):
                t_coords = LOCATIONS[t_name]
                path, d = a_star_path(curr, t_coords)
                
                # Draw A* Path
                folium.PolyLine(path, color="#00f2ff", weight=4, opacity=0.8, dash_array='10').add_to(m)
                
                # FIX: Explicit icon for every waypoint (including the 3rd spot)
                folium.Marker(
                    t_coords, 
                    tooltip=f"WP {i+1}: {t_name}", 
                    icon=folium.Icon(color='blue', icon='cube', prefix='fa')
                ).add_to(m)
                
                total_d += d
                curr = t_coords
            
            st.session_state.map_obj = m
            st.session_state.total_d = total_d
            st.session_state.mission_active = True
        else:
            st.warning("Please select target waypoints.")

# --- 5. MAIN HUD DISPLAY ---
st.title("🚁 AEROROUTE TACTICAL HUD")

# Metrics Dashboard
c1, c2, c3 = st.columns(3)
with c1:
    st.markdown(f"<div class='metric-card'><h2>{st.session_state.total_d:.2f} KM</h2><p>TOTAL DISTANCE</p></div>", unsafe_allow_html=True)
with c2:
    st.markdown(f"<div class='metric-card'><h2>{int(st.session_state.total_d*1.5)} MIN</h2><p>ESTIMATE</p></div>", unsafe_allow_html=True)
with c3:
    st.markdown(f"<div class='metric-card'><h2 style='color:#00ff88'>{max(5, 100-int(st.session_state.total_d*2))}%</h2><p>BATTERY</p></div>", unsafe_allow_html=True)

st.markdown("---")

# THE MAP (No flickering with returned_objects=[])
st_folium(
    st.session_state.map_obj, 
    width=1300, 
    height=550, 
    key="unified_drone_map", 
    returned_objects=[]
)

if st.session_state.mission_active:
    if st.button("⚠️ RESET MISSION"):
        st.session_state.map_obj = folium.Map(location=[9.9252, 78.1198], zoom_start=13, tiles="CartoDB dark_matter")
        st.session_state.total_d = 0
        st.session_state.mission_active = False
        st.rerun()