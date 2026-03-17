from django.core.management.base import BaseCommand
from aeroroute.models import NoFlyZone

class Command(BaseCommand):
    help = 'Populate restricted no-fly zones (Danger Zones)'

    def handle(self, *args, **options):
        # Sample No-Fly Zones for better visual and pathfinding testing
        zones = [
            # High Risk Area 1
            {
                "name": "Industrial Hazard Zone",
                "center_lat": 12.9716,
                "center_lon": 77.5946,
                "radius_km": 0.8,
                "min_lat": 12.965, "max_lat": 12.975,
                "min_lon": 77.585, "max_lon": 77.595
            },
            # High Risk Area 2
            {
                "name": "Restricted Airspace A",
                "center_lat": 12.9500,
                "center_lon": 77.6000,
                "radius_km": 1.2,
                "min_lat": 12.940, "max_lat": 12.955,
                "min_lon": 77.595, "max_lon": 77.610
            }
        ]

        for z in zones:
            NoFlyZone.objects.update_or_create(name=z["name"], defaults=z)
        
        self.stdout.write(self.style.SUCCESS('Successfully populated no-fly zones'))
