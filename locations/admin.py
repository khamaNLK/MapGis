from django.contrib import admin
from django.contrib.gis.admin import GISModelAdmin
from .models import Location, Category, Review

# Đăng ký Model Location để hiện bản đồ trong Admin
@admin.register(Location)
class LocationAdmin(GISModelAdmin):
    list_display = ('name', 'category', 'address', 'created_at')
    gis_widget_kwargs = {
        'attrs': {
            'default_zoom': 13,
            'default_lon': 106.660172,
            'default_lat': 10.762622,
        }
    }

# Đăng ký Model Category (Cái bạn đang thiếu)
admin.site.register(Category)

# Đăng ký Model Review
admin.site.register(Review)