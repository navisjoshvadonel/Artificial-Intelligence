from django.core.management.base import BaseCommand
from aeroroute.models import Location

class Command(BaseCommand):
    help = 'Populate Location model with comprehensive hospital data'

    def handle(self, *args, **options):
        # Full district data from views.py
        NETWORK_DATA = {
            "Madurai": {
                "hospitals": {
                    "Government Rajaji Hospital (MAIN HUB)": (9.9195, 78.1148),
                    "Velammal Medical College Hospital": (9.8828, 78.0833),
                    "Apollo Speciality Hospitals": (9.9391, 78.1566),
                    "Meenakshi Mission Hospital & Research Centre": (9.9482, 78.1738),
                    "Vadamalayan Hospitals": (9.9328, 78.1362),
                    "Hannah Joseph Hospital": (9.9200, 78.1100),
                    "Devadoss Multispeciality Hospital": (9.9579, 78.1541)
                }
            },
            "Chennai": {
                "hospitals": {
                    "Rajiv Gandhi Government General Hospital (MAIN HUB)": (13.0814, 80.2772),
                    "Government Stanley Medical College Hospital": (13.1048, 80.2863),
                    "Government Kilpauk Medical College Hospital": (13.0784, 80.2438),
                    "Apollo Hospitals Greams Road": (13.0630, 80.2540),
                    "Fortis Malar Hospital": (13.0031, 80.2565),
                    "MIOT International Hospital": (13.0287, 80.1837),
                    "Sri Ramachandra Medical Centre": (13.0336, 80.1477)
                }
            },
            "Coimbatore": {
                "hospitals": {
                    "Coimbatore Medical College (MAIN HUB)": (11.0008, 76.9633),
                    "KMCH - Kovai Medical Center": (11.0560, 77.0260),
                    "GKNM Hospital": (11.0132, 76.9749),
                    "PSG Hospitals": (11.0252, 77.0084),
                    "Ganga Hospital": (11.0315, 76.9538),
                    "Royal Care Hospital": (11.0667, 77.0667)
                }
            },
            "Tiruchirappalli": {
                "hospitals": {
                    "Annal Gandhi Govt Hospital (MAIN HUB)": (10.8117, 78.6774),
                    "Apollo Speciality Trichy": (10.8100, 78.7100),
                    "Kauvery Hospital": (10.8050, 78.6850),
                    "Sundaram Hospital": (10.8100, 78.6800),
                    "Trichy SRM Medical College": (10.9500, 78.7500)
                }
            },
            "Salem": {
                "hospitals": {
                    "Mohan Kumaramangalam Govt (MAIN HUB)": (11.6643, 78.1610),
                    "Manipal Hospital Salem": (11.7088, 78.1256),
                    "Shanmuga Hospital": (11.6650, 78.1350),
                    "SKS Hospital": (11.6700, 78.1400)
                }
            },
            "Tirunelveli": {
                "hospitals": {
                    "Tirunelveli Medical College (MAIN HUB)": (8.7139, 77.7567),
                    "Galaxy Hospital": (8.7300, 77.7200),
                    "Shifa Hospital": (8.7300, 77.7100),
                    "Annai Velankanni Hospital": (8.7300, 77.7300)
                }
            }
        }

        created_count = 0
        for district, data in NETWORK_DATA.items():
            for hospital_name, (lat, lon) in data['hospitals'].items():
                is_hub = "MAIN HUB" in hospital_name
                category = "Blood Bank" if "Blood Bank" in hospital_name else "Hospital"
                Location.objects.update_or_create(
                    name=hospital_name,
                    defaults={
                        'latitude': lat,
                        'longitude': lon,
                        'district': district,
                        'category': category,
                        'is_blood_bank': (category == "Blood Bank")
                    }
                )
                created_count += 1

        self.stdout.write(self.style.SUCCESS(f"Successfully populated {created_count} locations across {len(NETWORK_DATA)} districts."))
