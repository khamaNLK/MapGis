from django import forms
from .models import Location, Review

# 1. Form thêm địa điểm
class LocationForm(forms.ModelForm):
    lat = forms.FloatField(widget=forms.HiddenInput())
    lon = forms.FloatField(widget=forms.HiddenInput())
    
    class Meta:
        model = Location
        # Các trường này PHẢI có trong model Location
        fields = ['name', 'category', 'description', 'address', 'image', 'lat', 'lon']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'address': forms.TextInput(attrs={'class': 'form-control'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }

# 2. Form đánh giá (Sửa lại class này)
class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        # Các trường này PHẢI có trong model Review
        fields = ['rating', 'comment', 'image'] 
        widgets = {
            'rating': forms.NumberInput(attrs={'min': 1, 'max': 5, 'class': 'form-control'}),
            'comment': forms.Textarea(attrs={'rows': 3, 'class': 'form-control', 'placeholder': 'Chia sẻ trải nghiệm của bạn...'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }