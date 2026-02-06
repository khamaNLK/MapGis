from django import forms
from .models import Location

class LocationForm(forms.ModelForm):
    # Tạo 2 trường ẩn để chứa tọa độ khi user click trên map
    lat = forms.FloatField(widget=forms.HiddenInput())
    lon = forms.FloatField(widget=forms.HiddenInput())

    class Meta:
        model = Location
        fields = ['name', 'category', 'description', 'address'] # Không hiển thị field geom ở đây
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }