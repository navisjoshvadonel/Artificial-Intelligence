from django.core.management.base import BaseCommand
from aeroroute.models import Location

class Command(BaseCommand):
    help = 'Set district for all existing hospitals'

    def handle(self, *args, **options):
        mapping = {
            "Blood Bank (Govt Hospital)": "Madurai",
            "Apollo Hospital": "Madurai",
            "Meenakshi Mission": "Madurai",
            "Velammal Medical College": "Madurai",
            "Vadamalayan Hospital": "Madurai",
            "Hannah Joseph Hospital": "Madurai",
        }

        updated = 0
        for loc in Location.objects.all():
            if loc.name in mapping:
                loc.district = mapping[loc.name]
            elif ', ' in loc.name:
                loc.district = loc.name.split(', ')[-1].strip()
            else:
                loc.district = "Unknown"
            loc.save()
            updated += 1

        self.stdout.write(self.style.SUCCESS(f"✅ Updated {updated} hospitals with district names!"))
        self.stdout.write(self.style.SUCCESS("Madurai now has all your original 6 hospitals."))