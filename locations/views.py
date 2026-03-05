from django.shortcuts import render, redirect, get_object_or_404
from django.core.serializers import serialize
import json
from django.contrib.gis.geos import Point
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.db.models import Avg
from django.http import HttpResponseForbidden # Import để báo lỗi cấm truy cập
from .models import Location, Review
from .forms import LocationForm, ReviewForm
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import UserProfile

# --- HÀM KIỂM TRA QUYỀN (Helper) ---
def check_permission(user, location):
    # Cho phép nếu: User là Admin (staff) HOẶC User là người tạo ra địa điểm đó
    if user.is_staff or location.creator == user:
        return True
    return False

# 1. Hàm hiển thị bản đồ trang chủ
def map_view(request):
    locations = Location.objects.all()
    
    # Tạo GeoJSON thủ công để dễ dàng chèn URL ảnh vào properties
    features = []
    for loc in locations:
        feature = {
            "type": "Feature",
            "geometry": json.loads(loc.geom.geojson),
            "properties": {
                "pk": loc.pk,
                "name": loc.name,
                "category": loc.category.name if loc.category else "Khác",
                "description": loc.description,
                "address": loc.address,
                # Lấy URL ảnh nếu có (để hiển thị trên popup)
                "image_url": loc.image.url if loc.image else None 
            }
        }
        features.append(feature)
    
    geojson_data = {
        "type": "FeatureCollection",
        "features": features
    }

    locations_json = json.dumps(geojson_data)
    
    return render(request, 'locations/index.html', {
        'locations_json': locations_json
    })

# 2. Hàm xem chi tiết và đánh giá địa điểm
def location_detail(request, pk):
    location = get_object_or_404(Location, pk=pk)
    reviews = location.reviews.all().order_by('-created_at')
    
    avg_rating = reviews.aggregate(Avg('rating'))['rating__avg']
    avg_rating = round(avg_rating, 1) if avg_rating else 0

    if request.method == 'POST':
        if not request.user.is_authenticated:
            return redirect('login')
            
        form = ReviewForm(request.POST, request.FILES)
        if form.is_valid():
            review = form.save(commit=False)
            review.location = location
            review.user = request.user
            review.save()
            return redirect('location_detail', pk=pk)
    else:
        form = ReviewForm()

    return render(request, 'locations/location_detail.html', {
        'location': location,
        'reviews': reviews,
        'avg_rating': avg_rating,
        'form': form
    })

# 3. Hàm thêm địa điểm
@login_required
def add_location(request):
    if request.method == 'POST':
        form = LocationForm(request.POST, request.FILES)
        if form.is_valid():
            new_location = form.save(commit=False)
            try:
                lat = form.cleaned_data['lat']
                lon = form.cleaned_data['lon']
                new_location.geom = Point(lon, lat, srid=4326)
            except (ValueError, TypeError):
                return render(request, 'locations/add_location.html', {
                    'form': form,
                    'error': 'Vui lòng chọn vị trí trên bản đồ!'
                })
            
            new_location.creator = request.user
            new_location.save()
            return redirect('map_home')
    else:
        form = LocationForm()

    return render(request, 'locations/add_location.html', {'form': form})

# 4. Hàm Đăng ký tài khoản
def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('map_home')
    else:
        form = UserCreationForm()
    
    return render(request, 'registration/signup.html', {'form': form})

# 5. Hàm Sửa địa điểm (MỚI - Có bảo mật)
@login_required
def edit_location(request, pk):
    location = get_object_or_404(Location, pk=pk)
    
    # KIỂM TRA QUYỀN
    if not check_permission(request.user, location):
        return HttpResponseForbidden("Bạn không có quyền sửa địa điểm này!")

    if request.method == 'POST':
        # instance=location để cập nhật bản ghi cũ thay vì tạo mới
        form = LocationForm(request.POST, request.FILES, instance=location)
        if form.is_valid():
            loc = form.save(commit=False)
            
            # Cập nhật tọa độ nếu người dùng chọn lại trên bản đồ
            try:
                lat = form.cleaned_data['lat']
                lon = form.cleaned_data['lon']
                if lat and lon: 
                    loc.geom = Point(lon, lat, srid=4326)
            except:
                pass # Giữ nguyên tọa độ cũ nếu không đổi
                
            loc.save()
            return redirect('location_detail', pk=pk)
    else:
        # Đổ dữ liệu cũ vào form, bao gồm cả tọa độ để hiện marker
        form = LocationForm(instance=location, initial={
            'lat': location.geom.y,
            'lon': location.geom.x
        })

    return render(request, 'locations/add_location.html', {
        'form': form, 
        'is_edit': True # Báo hiệu cho template biết đây là chế độ Sửa
    })

# 6. Hàm Xóa địa điểm (MỚI - Có bảo mật)
@login_required
def delete_location(request, pk):
    location = get_object_or_404(Location, pk=pk)
    
    # KIỂM TRA QUYỀN
    if not check_permission(request.user, location):
        return HttpResponseForbidden("Bạn không có quyền xóa địa điểm này!")
    
    if request.method == 'POST':
        location.delete()
        return redirect('map_home')
        
    return render(request, 'locations/confirm_delete.html', {'location': location})
@csrf_exempt # Tạm thời tắt check CSRF để API nhận dữ liệu dễ dàng hơn
def update_location(request):
    if request.method == 'POST' and request.user.is_authenticated:
        try:
            data = json.loads(request.body)
            # Tìm profile của user này, nếu chưa có thì tự động tạo mới
            profile, created = UserProfile.objects.get_or_create(user=request.user)
            
            # Cập nhật tọa độ và pin
            profile.last_lat = data.get('lat')
            profile.last_lon = data.get('lng')
            if 'battery' in data:
                profile.battery_level = data.get('battery')
                
            profile.save()
            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
            
    return JsonResponse({'status': 'fail', 'message': 'Chưa đăng nhập hoặc sai method'})
@login_required
def get_friends_data(request):
    try:
        # Lấy profile của người dùng hiện tại
        profile = UserProfile.objects.get(user=request.user)
        # Lấy danh sách những người bạn
        friends = profile.friends.all()
        
        friends_data = []
        for f in friends:
            # Bỏ qua những người bạn chưa từng bật GPS (chưa có tọa độ)
            if f.last_lat is not None and f.last_lon is not None:
                # Tự động tạo màu ngẫu nhiên cho avatar từng người
                avatar_url = f"https://ui-avatars.com/api/?name={f.user.username}&background=random&color=fff"
                
                friends_data.append({
                    'id': f.user.id,
                    'name': f.user.username,
                    'lat': f.last_lat,
                    'lng': f.last_lon,
                    'battery': f.battery_level,
                    'status': f.status_message or "",
                    'avatar': avatar_url
                })
                
        return JsonResponse({'status': 'success', 'friends': friends_data})
    except UserProfile.DoesNotExist:
        return JsonResponse({'status': 'success', 'friends': []})
@csrf_exempt
def update_status(request):
    if request.method == 'POST' and request.user.is_authenticated:
        try:
            data = json.loads(request.body)
            # Lấy profile và cập nhật dòng trạng thái mới
            profile, created = UserProfile.objects.get_or_create(user=request.user)
            profile.status_message = data.get('status', '')
            profile.save()
            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
            
    return JsonResponse({'status': 'fail', 'message': 'Chưa đăng nhập'})