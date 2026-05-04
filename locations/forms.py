from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Location, Review

class UserSignupForm(UserCreationForm):
    email = forms.EmailField(required=True, help_text='Nhập email để nhận mã OTP xác thực.')

    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('email',)

# Giữ nguyên LocationForm và ReviewForm của bạn
class LocationForm(forms.ModelForm):
    class Meta:
        model = Location
        fields = ['name', 'description', 'address', 'image', 'open_time', 'close_time']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control fw-bold border-primary', 'placeholder': 'Tên địa điểm...'}),
            'address': forms.Textarea(attrs={'class': 'form-control small', 'rows': 2, 'placeholder': 'Địa chỉ...'}),
            'open_time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'close_time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
        }

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment', 'image']