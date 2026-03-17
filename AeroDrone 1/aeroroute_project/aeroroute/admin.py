from django.contrib import admin
from .models import Location, NoFlyZone

admin.site.register(Location)
admin.site.register(NoFlyZone)
class LocationAdmin(admin.ModelAdmin):
    list_display = ('name', 'latitude', 'longitude', 'is_blood_bank')
    search_fields = ('name',)