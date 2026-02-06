from django.shortcuts import render, redirect
from django.core.serializers import serialize
from django.contrib.gis.geos import Point
from .models import Location
from .forms import LocationForm
def map_view(request):
    # 1. Lấy tất cả địa điểm từ Database
    locations = Location.objects.all()
    
    # 2. Chuyển dữ liệu sang dạng GeoJSON (để bản đồ hiểu được)
    # Chúng ta lấy thêm cả trường 'name', 'category', 'description' để hiện popup
    locations_geojson = serialize('geojson', locations, 
                                  geometry_field='geom', 
                                  fields=('name', 'category', 'description', 'address'))
    
    return render(request, 'locations/index.html', {
        'locations_json': locations_geojson
    })
def add_location(request):
    if request.method == 'POST':
        form = LocationForm(request.POST)
        if form.is_valid():
            new_location = form.save(commit=False)
            
            # Lấy tọa độ từ form ẩn và tạo dữ liệu hình học (Point)
            lat = form.cleaned_data['lat']
            lon = form.cleaned_data['lon']
            new_location.geom = Point(lon, lat, srid=4326) # Lưu ý: Point(kinh_độ, vĩ_độ)
            
            # Nếu user đã đăng nhập thì lưu người tạo (nếu chưa thì để null)
            if request.user.is_authenticated:
                new_location.creator = request.user
            
            new_location.save()
            return redirect('map_home') # Lưu xong quay về trang chủ
    else:
        form = LocationForm()

    return render(request, 'locations/add_location.html', {'form': form})