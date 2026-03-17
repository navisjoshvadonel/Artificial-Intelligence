from django.db import models

class Location(models.Model):
    name         = models.CharField(max_length=200, unique=True)
    latitude     = models.FloatField()
    longitude    = models.FloatField()
    district     = models.CharField(max_length=100, default="Unknown")
    is_blood_bank = models.BooleanField(default=False)
    category     = models.CharField(max_length=50, default="Hospital")

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']

class NoFlyZone(models.Model):
    name      = models.CharField(max_length=200)
    center_lat = models.FloatField()
    center_lon = models.FloatField()
    radius_km = models.FloatField(default=0.5) # For circular zones
    
    # Alternatively for rectangular zones
    min_lat   = models.FloatField(null=True, blank=True)
    max_lat   = models.FloatField(null=True, blank=True)
    min_lon   = models.FloatField(null=True, blank=True)
    max_lon   = models.FloatField(null=True, blank=True)

    def __str__(self):
        return f"Zone: {self.name}"