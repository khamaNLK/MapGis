from django.contrib import admin
from django.contrib.gis.admin import GISModelAdmin
from .models import Location, Category, Review, UserProfile, LocationImage


class LocationImageInline(admin.TabularInline):
    model = LocationImage
    extra = 3


@admin.register(Location)
class LocationAdmin(GISModelAdmin):

    list_display = (
        'name',
        'category',
        'is_approved',
        'creator',
        'open_time',
        'close_time'
    )

    list_filter = (
        'is_approved',
        'category',
        'created_at'
    )

    search_fields = (
        'name',
        'address'
    )

    inlines = [LocationImageInline]

    gis_widget_kwargs = {
        'attrs': {
            'default_zoom': 13,
            'default_lon': 106.660172,
            'default_lat': 10.762622,
        }
    }


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'icon_name')


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('user', 'location', 'rating', 'created_at')


admin.site.register(UserProfile)