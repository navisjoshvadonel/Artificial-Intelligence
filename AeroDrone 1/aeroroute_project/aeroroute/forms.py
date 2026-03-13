from django import forms
from .models import Location

class MissionForm(forms.Form):
    district = forms.ChoiceField(
        label="Select District",
        choices=[('', '--- Select District ---')],
        required=False
    )
    base_station = forms.ModelChoiceField(
        queryset=Location.objects.none(),  # will be updated dynamically
        label="Base Station (Blood Bank)",
        empty_label="--- Select Base ---"
    )
    destinations = forms.ModelMultipleChoiceField(
        queryset=Location.objects.none(),
        widget=forms.CheckboxSelectMultiple,
        label="Delivery Hospitals",
        required=False
    )
    map_style = forms.ChoiceField(
        choices=[('dark', 'Cyber Dark'), ('satellite', 'Satellite Real-World')],
        initial='dark',
        label="Map Style"
    )