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