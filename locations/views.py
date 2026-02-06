from django.shortcuts import render, redirect
from django.core.serializers import serialize
from django.contrib.gis.geos import Point
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from .models import Location
from .forms import LocationForm

# 1. Hàm hiển thị bản đồ trang chủ
def map_view(request):
    # Lấy tất cả địa điểm từ Database
    locations = Location.objects.all()
    
    # Chuyển dữ liệu sang dạng GeoJSON để bản đồ Leaflet hiểu được
    locations_geojson = serialize('geojson', locations, 
                                  geometry_field='geom', 
                                  fields=('name', 'category', 'description', 'address'))
    
    return render(request, 'locations/index.html', {
        'locations_json': locations_geojson
    })

# 2. Hàm thêm địa điểm (Bắt buộc phải đăng nhập mới được vào)
@login_required
def add_location(request):
    if request.method == 'POST':
        form = LocationForm(request.POST)
        if form.is_valid():
            new_location = form.save(commit=False)
            
            # Lấy tọa độ từ form ẩn (do JS điền vào) và tạo đối tượng Point
            try:
                lat = form.cleaned_data['lat']
                lon = form.cleaned_data['lon']
                new_location.geom = Point(lon, lat, srid=4326) # Lưu ý thứ tự: (lon, lat)
            except (ValueError, TypeError):
                # Trường hợp lỗi không có tọa độ (dù đã validate ở frontend)
                return render(request, 'locations/add_location.html', {
                    'form': form,
                    'error': 'Vui lòng chọn vị trí trên bản đồ!'
                })
            
            # Gán người tạo là user đang đăng nhập
            new_location.creator = request.user
            
            new_location.save()
            return redirect('map_home') # Lưu xong quay về trang chủ
    else:
        form = LocationForm()

    return render(request, 'locations/add_location.html', {'form': form})

# 3. Hàm Đăng ký tài khoản (Bổ sung thêm)
def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Đăng ký xong thì tự động đăng nhập luôn cho tiện
            login(request, user)
            return redirect('map_home')
    else:
        form = UserCreationForm()
    
    return render(request, 'registration/signup.html', {'form': form})