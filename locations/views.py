import json
import random
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.gis.geos import Point
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.db.models import Avg, Q
from django.http import JsonResponse, HttpResponse
from django.core.exceptions import PermissionDenied
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.conf import settings

from .models import Location, Review, UserProfile, Category, LocationImage, FriendRequest
from .forms import LocationForm, ReviewForm, UserSignupForm

# --- 1. TÀI KHOẢN & XÁC THỰC OTP ---
def signup(request):
    if request.method == 'POST':
        form = UserSignupForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            profile, _ = UserProfile.objects.get_or_create(user=user)
            profile.generate_otp()
            send_mail(
                'Mã xác thực MyMap GIS',
                f'Chào {user.username}, mã OTP của bạn là: {profile.otp_code}',
                settings.DEFAULT_FROM_EMAIL,
                [user.email]
            )
            request.session['otp_username'] = user.username
            messages.info(request, "Mã OTP đã được gửi đến email của bạn.")
            return redirect('verify_otp')
    else:
        form = UserSignupForm()
    return render(request, 'registration/signup.html', {'form': form})

def verify_otp(request):
    username = request.session.get('otp_username')
    if not username: return redirect('signup')
    if request.method == 'POST':
        otp_input = request.POST.get('otp')
        user = get_object_or_404(User, username=username)
        if user.userprofile.otp_code == otp_input:
            user.is_active = True
            user.save()
            user.userprofile.is_verified = True
            user.userprofile.otp_code = None
            user.userprofile.save()
            login(request, user)
            if 'otp_username' in request.session:
                del request.session['otp_username']
            messages.success(request, "Xác thực thành công! Chào mừng bạn.")
            return redirect('map_home')
        else:
            messages.error(request, "Mã OTP không chính xác.")
    return render(request, 'registration/verify_otp.html')

# --- 2. TRANG CHỦ & CHI TIẾT ---
def map_view(request):
    locations = Location.objects.filter(is_approved=True).annotate(
        avg_score=Avg('reviews__rating')
    ).select_related("category").prefetch_related("images")
    
    features = []
    for loc in locations:
        features.append({
            "type": "Feature",
            "geometry": json.loads(loc.geom.geojson) if loc.geom else None,
            "properties": {
                "pk": loc.pk,
                "name": loc.name,
                "avg_rating": float(loc.avg_score or 0),
                "open_time": loc.open_time.strftime('%H:%M') if loc.open_time else "N/A",
                "close_time": loc.close_time.strftime('%H:%M') if loc.close_time else "N/A",
                "category": loc.category.name if loc.category else "Khác",
                "address": loc.address,
                "image_url": loc.image.url if loc.image else None,
            }
        })
    return render(request, 'locations/index.html', {
        'locations_json': json.dumps({"type": "FeatureCollection", "features": features})
    })

def location_detail(request, pk):
    location = get_object_or_404(Location.objects.prefetch_related('images', 'reviews__user'), pk=pk)
    user_has_reviewed = Review.objects.filter(location=location, user=request.user).exists() if request.user.is_authenticated else False
    avg = location.reviews.aggregate(Avg('rating'))['rating__avg'] or 0
    return render(request, 'locations/location_detail.html', {
        'location': location,
        'avg_rating': round(avg, 1),
        'reviews': location.reviews.all().order_by('-created_at'),
        'user_has_reviewed': user_has_reviewed
    })

# --- 3. BẠN BÈ ---
@login_required
def find_friends(request):
    query = request.GET.get('q', '').strip()
    results = []
    if query:
        if query.isdigit():
            results = User.objects.filter(id=query).exclude(id=request.user.id)
        else:
            results = User.objects.filter(username__icontains=query).exclude(id=request.user.id)
            
    try:
        friend_ids = request.user.userprofile.friends.values_list('user_id', flat=True)
    except:
        friend_ids = []
        
    sent_requests_ids = FriendRequest.objects.filter(
        from_user=request.user, status='pending'
    ).values_list('to_user_id', flat=True)
    
    pending_to_me = FriendRequest.objects.filter(to_user=request.user, status='pending')
    
    return render(request, 'locations/find_friends.html', {
        'results': results,
        'query': query,
        'friend_ids': friend_ids,
        'sent_requests_ids': sent_requests_ids,
        'pending_requests': pending_to_me
    })

@login_required
def send_friend_request(request, user_id):
    to_user = get_object_or_404(User, id=user_id)
    if to_user != request.user:
        # Tối ưu: Lấy bản ghi cũ nếu có để cập nhật, tránh lỗi duplicate thay vì get_or_create mù quáng
        req, created = FriendRequest.objects.get_or_create(
            from_user=request.user, 
            to_user=to_user,
            defaults={'status': 'pending'}
        )
        if not created:
            req.status = 'pending'
            req.save()
        messages.success(request, f"Đã gửi lời mời đến {to_user.username}")
    return redirect('find_friends')

@login_required
def accept_friend_request(request, request_id):
    req = get_object_or_404(FriendRequest, id=request_id, to_user=request.user)
    request.user.userprofile.friends.add(req.from_user.userprofile)
    req.status = 'accepted'
    req.save()
    messages.success(request, f"Bạn và {req.from_user.username} đã là bạn bè.")
    return redirect('find_friends')

@login_required
def remove_friend(request, user_id):
    target = get_object_or_404(User, id=user_id)
    request.user.userprofile.friends.remove(target.userprofile)
    FriendRequest.objects.filter(
        Q(from_user=request.user, to_user=target) | Q(from_user=target, to_user=request.user)
    ).delete()
    messages.success(request, "Đã xóa bạn bè.")
    return redirect('custom_dashboard')

# --- 4. DASHBOARD & ĐỊA ĐIỂM ---
@login_required
def custom_dashboard(request):
    locations = Location.objects.all() if request.user.is_superuser else Location.objects.filter(creator=request.user)
    locations = locations.annotate(avg_score=Avg('reviews__rating')).select_related('category').order_by('-id')
    for loc in locations:
        loc.dashboard_rating = loc.avg_score or 0
        
    pending_requests = FriendRequest.objects.filter(to_user=request.user, status='pending')

    # Lấy danh sách bạn bè
    try:
        friends = request.user.userprofile.friends.all()
    except:
        friends = []

    return render(request, 'locations/dashboard.html', {
        'locations': locations,
        'pending_requests': pending_requests,
        'friends': friends # Truyền biến ra giao diện
    })

@login_required
def add_location_dashboard(request):
    if request.method == 'POST':
        form = LocationForm(request.POST, request.FILES)
        lat, lon = request.POST.get('lat'), request.POST.get('lon')
        if form.is_valid() and lat and lon:
            loc = form.save(commit=False)
            loc.geom = Point(float(lon), float(lat), srid=4326)
            cat_name = request.POST.get('category_name')
            if cat_name:
                category_obj, _ = Category.objects.get_or_create(name=cat_name)
                loc.category = category_obj
            loc.description = request.POST.get('description')
            loc.open_time = request.POST.get('open_time')
            loc.close_time = request.POST.get('close_time')
            loc.creator = request.user
            loc.is_approved = request.user.is_staff
            loc.save()
            for img in request.FILES.getlist('extra_images'):
                LocationImage.objects.create(location=loc, image=img)
            messages.success(request, "✅ Thêm địa điểm thành công!")
            return redirect('custom_dashboard')
        else:
            messages.error(request, "Vui lòng chọn vị trí trên bản đồ!")
    else:
        form = LocationForm()
    return render(request, 'locations/add_location.html', {'form': form, 'is_edit': False})

@login_required
def edit_location(request, pk):
    location = get_object_or_404(Location, pk=pk)
    if not (request.user.is_superuser or location.creator == request.user):
        raise PermissionDenied
    if request.method == 'POST':
        form = LocationForm(request.POST, request.FILES, instance=location)
        lat, lon = request.POST.get('lat'), request.POST.get('lon')
        if form.is_valid():
            loc = form.save(commit=False)
            if lat and lon: loc.geom = Point(float(lon), float(lat), srid=4326)
            loc.description = request.POST.get('description')
            loc.open_time = request.POST.get('open_time')
            loc.close_time = request.POST.get('close_time')
            loc.save()
            for img in request.FILES.getlist('extra_images'):
                LocationImage.objects.create(location=loc, image=img)
            messages.success(request, "✅ Cập nhật thành công!")
            return redirect('custom_dashboard')
    else:
        form = LocationForm(instance=location)
    return render(request, 'locations/add_location.html', {'form': form, 'is_edit': True, 'location': location})

# --- 5. ADMIN ---
@login_required
def approve_location(request, pk):
    if not request.user.is_staff: raise PermissionDenied
    loc = get_object_or_404(Location, pk=pk)
    loc.is_approved = True
    loc.save()
    messages.success(request, f"✅ Đã duyệt: {loc.name}")
    return redirect('custom_dashboard')

@login_required
def manage_users(request):
    if not request.user.is_superuser: raise PermissionDenied
    return render(request, 'locations/manage_users.html', {'users': User.objects.all().order_by('-date_joined')})

@login_required
def toggle_user_status(request, user_id):
    if not request.user.is_superuser: raise PermissionDenied
    target_user = get_object_or_404(User, id=user_id)
    if target_user != request.user:
        target_user.is_active = not target_user.is_active
        target_user.save()
        status = "mở khóa" if target_user.is_active else "khóa"
        messages.success(request, f"Đã {status} tài khoản {target_user.username}")
    return redirect('manage_users')

# --- 6. API ---
@csrf_exempt
@login_required
def update_location(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            p, _ = UserProfile.objects.get_or_create(user=request.user)
            p.last_location = Point(float(data.get("lng")), float(data.get("lat")), srid=4326)
            p.save()
            return JsonResponse({"status": "success"})
        except: return JsonResponse({"status": "error"}, status=400)
    return JsonResponse({"status": "error"}, status=405)

@login_required
def get_friends_data(request):
    try:
        friend_profiles = request.user.userprofile.friends.filter(last_location__isnull=False)
    except:
        friend_profiles = []
    friends = [{
        "username": p.user.username,
        "lat": p.last_location.y,
        "lng": p.last_location.x,
        "avatar": p.avatar.url if p.avatar else f"https://ui-avatars.com/api/?name={p.user.username}",
        "status": p.status_message or "Đang hoạt động"
    } for p in friend_profiles]
    return JsonResponse({"status": "success", "friends": friends})

@login_required
@require_POST
def add_review(request, pk):
    location = get_object_or_404(Location, pk=pk)
    Review.objects.create(
        location=location, user=request.user,
        rating=int(request.POST.get('rating')),
        comment=request.POST.get('comment'),
        image=request.FILES.get('image')
    )
    return redirect('location_detail', pk=pk)

@login_required
def delete_location_dashboard(request, pk):
    loc = get_object_or_404(Location, pk=pk)
    if request.user.is_superuser or loc.creator == request.user: loc.delete()
    return redirect('custom_dashboard')

def search_nearby(request): return render(request, 'locations/index.html')
def error_404(request, exception): return render(request, '404.html', status=404)
def error_403(request, exception): return render(request, '403.html', status=403)
def about_view(request):
    return render(request, 'locations/about.html')