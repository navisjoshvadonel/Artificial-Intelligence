<div align="center">
  <img src="https://raw.githubusercontent.com/navisjoshvadonel/Artificial-Intelligence/main/docs/assets/aeroroute_banner.png" alt="AeroRoute Banner" width="100%">
  
  # 🚁 AeroRoute Project Ecosystem
  
  [![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
  [![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=Streamlit&logoColor=white)](https://streamlit.io/)
  [![Django](https://img.shields.io/badge/Django-092E20?style=for-the-badge&logo=django&logoColor=white)](https://www.djangoproject.com/)
  [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](https://opensource.org/licenses/MIT)

  ### *Tactical Intelligence for Autonomous Drone Navigation & Asset Management*
</div>

---

## 🛰️ Project Overview

**AeroRoute** is a dual-component ecosystem designed for advanced drone pathfinding and logistical management. It combines a high-performance **Streamlit Tactical HUD** for real-time mission execution with a robust **Django Backend** for centralized resource tracking and location management.

Our core mission is to optimize medical supply deliveries (blood banks, hospitals) through informed search algorithms and interactive visualization.

---

## 🔥 Key Features

### 🖥️ AeroRoute Tactical HUD (Frontend)
- **A* Path Engine**: Implements Informed Search (Unit II) for optimal waypoint navigation.
- **Dynamic HUD Display**: Real-time metrics for Total Distance, Estimated Time, and Battery Status.
- **Interactive Mapping**: Powered by Folium with Dark Matter aesthetic for high-visibility tactical operations.
- **Mission Execution**: Multi-waypoint selection with path persistence and reactive state management.

### 🗄️ AeroRoute Backend (Management)
- **Centralized Registry**: Manage hospitals, blood banks, and launch points with precise geographic coordinates.
- **Category System**: Filter and organize locations by district and facility type.
- **Admin Dashboard**: Effortless CRUD operations for maintaining the mission network.

---

## 🛠️ Tech Stack

| Component | Technology |
| :--- | :--- |
| **Interface** | Streamlit, Folium |
| **Logic** | Python 3.x, A* Search Algorithm |
| **Backend** | Django, SQLite |
| **Styling** | Custom CSS (Glassmorphism & Neon Tech) |
| **Maps** | CartoDB Dark Matter |

---

## 🚀 Getting Started

### 1. Prerequisites
- Python 3.8 or higher
- `pip` package manager

### 2. Installation

Clone the repository and set up the environments:

#### Root & Frontend (`AeroRoute`)
```bash
cd AeroDrone
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install streamlit folium streamlit-folium
```

#### Backend (`AeroRoute 1`)
```bash
cd "AeroRoute 1/aeroroute_project"
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install django
python manage.py migrate
```

---

## 📖 Usage Guide

### Launching the Tactical HUD
1. Navigate to the `AeroDrone` directory.
2. Run the application:
   ```bash
   streamlit run app.py
   ```
3. Select your **Launch Point** and **Waypoints** in the Command Sidebar.
4. Press `🚀 EXECUTE MISSION` to visualize the optimized path.

### Accessing the Backend Central
1. Navigate to `AeroRoute 1/aeroroute_project`.
2. Start the development server:
   ```bash
   python manage.py runserver
   ```
3. Access the registry via `http://127.0.0.1:8000/admin` (requires superuser).

---

## 📐 Project Structure

```text
Artificial-Intelligence/
├── AeroDrone/              # Streamlit Application
│   ├── app.py              # Main Tactical HUD logic
│   └── aeroroute.py        # Pathfinding utilities
└── AeroRoute 1/            # Django Backend
    └── aeroroute_project/  # Central Management System
        ├── aeroroute/      # App modules (Models, Views)
        └── manage.py       # Django CLI
```

---

<div align="center">
  <p>Built with ❤️ for Autonomous Logistics & AI Research</p>
  <sub>&copy; 2026 AeroRoute Pro. All rights reserved.</sub>
</div>
