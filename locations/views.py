import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.gis.geos import Point
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.db.models import Avg
from django.http import HttpResponseForbidden, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.contrib.auth.models import User
from .models import Location, Review, UserProfile, Category, FriendRequest
from .forms import LocationForm, ReviewForm

# 1. TÀI KHOẢN (Signup)
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

# 2. TRANG CHỦ & CHI TIẾT
def map_view(request):
    locations = Location.objects.filter(is_approved=True) 
    features = []
    for loc in locations:
        features.append({
            "type": "Feature", "geometry": json.loads(loc.geom.geojson),
            "properties": {
                "pk": loc.pk, "name": loc.name, "category": loc.category.name if loc.category else "Khác",
                "address": loc.address, "image_url": loc.image.url if loc.image else None 
            }
        })
    return render(request, 'locations/index.html', {'locations_json': json.dumps({"type": "FeatureCollection", "features": features})})

def location_detail(request, pk):
    location = get_object_or_404(Location, pk=pk)
    if request.method == 'POST' and request.user.is_authenticated:
        Review.objects.create(
            location=location, user=request.user, 
            rating=int(request.POST.get('rating')), 
            comment=request.POST.get('comment'), 
            image=request.FILES.get('image')
        )
        messages.success(request, "✅ Cảm ơn bạn đã đánh giá!")
        return redirect('location_detail', pk=pk)
    return render(request, 'locations/location_detail.html', {
        'location': location, 'reviews': location.reviews.all().order_by('-created_at'),
        'avg_rating': round(location.reviews.aggregate(Avg('rating'))['rating__avg'] or 0, 1),
        'form': ReviewForm()
    })

# 3. DASHBOARD & KẾT BẠN (ĐỒNG Ý)
@login_required
def custom_dashboard(request):
    locations = Location.objects.all() if request.user.is_superuser else Location.objects.filter(creator=request.user)
    cat_name = request.GET.get('category')
    if cat_name: locations = locations.filter(category__name=cat_name)
    pending_requests = FriendRequest.objects.filter(to_user=request.user, is_active=True)
    return render(request, 'locations/dashboard.html', {
        'locations': locations.order_by('-id'), 'categories': Category.objects.all(),
        'current_category': cat_name, 'pending_requests': pending_requests
    })

@login_required
def find_friends(request):
    query = request.GET.get('q')
    results = User.objects.filter(username__icontains=query).exclude(id=request.user.id) if query else []
    return render(request, 'locations/find_friends.html', {'results': results})

@login_required
def send_friend_request(request, user_id):
    to_user = get_object_or_404(User, id=user_id)
    if not FriendRequest.objects.filter(from_user=request.user, to_user=to_user, is_active=True).exists():
        FriendRequest.objects.create(from_user=request.user, to_user=to_user)
        messages.success(request, f"Đã gửi lời mời tới {to_user.username}")
    return redirect('find_friends')

@login_required
def accept_friend_request(request, request_id):
    fr = get_object_or_404(FriendRequest, id=request_id, to_user=request.user)
    my_p, _ = UserProfile.objects.get_or_create(user=request.user)
    sender_p, _ = UserProfile.objects.get_or_create(user=fr.from_user)
    my_p.friends.add(sender_p)
    fr.delete()
    messages.success(request, f"Bạn và {fr.from_user.username} đã là bạn bè!")
    return redirect('custom_dashboard')

@login_required
def reject_friend_request(request, request_id):
    get_object_or_404(FriendRequest, id=request_id, to_user=request.user).delete()
    return redirect('custom_dashboard')

# 4. QUẢN LÝ NGƯỜI DÙNG & GIS API
@staff_member_required
def manage_users(request):
    return render(request, 'locations/manage_users.html', {'users': User.objects.all().order_by('-date_joined')})

@staff_member_required
def toggle_user_status(request, user_id):
    u = get_object_or_404(User, id=user_id)
    if not u.is_superuser:
        u.is_active = not u.is_active
        u.save()
    return redirect('manage_users')

@csrf_exempt
def update_location(request):
    if request.method == 'POST' and request.user.is_authenticated:
        data = json.loads(request.body)
        p, _ = UserProfile.objects.get_or_create(user=request.user)
        p.last_lat, p.last_lon = data.get('lat'), data.get('lng')
        p.save()
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'fail'})

@csrf_exempt
def update_status(request):
    if request.method == 'POST' and request.user.is_authenticated:
        data = json.loads(request.body)
        p, _ = UserProfile.objects.get_or_create(user=request.user)
        p.status_message = data.get('status', '')
        p.save()
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'fail'})

def get_friends_data(request):
    if not request.user.is_authenticated: return JsonResponse({'friends': []})
    p, _ = UserProfile.objects.get_or_create(user=request.user)
    data = [{'id': f.user.id, 'name': f.user.username, 'lat': f.last_lat, 'lng': f.last_lon, 'battery': f.battery_level, 'status': f.status_message, 'avatar': f"https://ui-avatars.com/api/?name={f.user.username}"} for f in p.friends.all() if f.last_lat]
    return JsonResponse({'status': 'success', 'friends': data})

@login_required
def add_location_dashboard(request):
    if request.method == 'POST':
        data = request.POST.copy()
        cat_name = request.POST.get('category_name')
        if cat_name:
            category_obj, _ = Category.objects.get_or_create(name=cat_name)
            data['category'] = category_obj.pk
        form = LocationForm(data, request.FILES)
        if form.is_valid():
            loc = form.save(commit=False)
            lat, lon = request.POST.get('lat'), request.POST.get('lon')
            if lat and lon: loc.geom = Point(float(lon), float(lat), srid=4326)
            loc.creator = request.user
            loc.is_approved = request.user.is_superuser
            loc.save()
            return redirect('custom_dashboard')
    return render(request, 'locations/add_location.html', {'form': LocationForm(), 'is_edit': False})

@login_required
def edit_location(request, pk):
    location = get_object_or_404(Location, pk=pk)
    if not (request.user.is_superuser or location.creator == request.user):
        return HttpResponseForbidden()
    if request.method == 'POST':
        data = request.POST.copy()
        cat_name = request.POST.get('category_name')
        if cat_name:
            category_obj, _ = Category.objects.get_or_create(name=cat_name)
            data['category'] = category_obj.pk
        form = LocationForm(data, request.FILES, instance=location)
        if form.is_valid():
            loc = form.save(commit=False)
            lat, lon = request.POST.get('lat'), request.POST.get('lon')
            if lat and lon: loc.geom = Point(float(lon), float(lat), srid=4326)
            loc.save()
            return redirect('custom_dashboard')
    form = LocationForm(instance=location)
    return render(request, 'locations/add_location.html', {'form': form, 'is_edit': True, 'location': location})

@login_required
def delete_location_dashboard(request, pk):
    loc = get_object_or_404(Location, pk=pk)
    if request.user.is_superuser or loc.creator == request.user:
        loc.delete()
    return redirect('custom_dashboard')

@staff_member_required
def approve_location(request, pk):
    loc = get_object_or_404(Location, pk=pk)
    loc.is_approved = True
    loc.save()
    return redirect('custom_dashboard')