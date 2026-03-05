from django.contrib import admin
from django.contrib.gis.admin import GISModelAdmin
from .models import Location, Category, Review, UserProfile

# 1. Quản lý Địa điểm (Có bản đồ)
@admin.register(Location)
class LocationAdmin(GISModelAdmin):
    list_display = ('name', 'category', 'address', 'creator', 'created_at') # Các cột hiển thị
    search_fields = ('name', 'address') # Thanh tìm kiếm
    list_filter = ('category', 'created_at') # Bộ lọc bên phải
    
    # Cấu hình bản đồ trong Admin
    gis_widget_kwargs = {
        'attrs': {
            'default_zoom': 13,
            'default_lon': 106.660172,
            'default_lat': 10.762622,
        }
    }

# 2. Quản lý Danh mục
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'icon_name')

# 3. Quản lý Đánh giá
@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('user', 'location', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
admin.site.register(UserProfile)