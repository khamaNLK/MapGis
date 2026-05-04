import random
from django.db import models
from django.contrib.gis.db import models as gis_models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models import Avg

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='userprofile')
    avatar = models.ImageField(upload_to="avatars/", blank=True, null=True)
    bio = models.TextField(blank=True)
    last_location = gis_models.PointField(srid=4326, null=True, blank=True)
    status_message = models.CharField(max_length=255, blank=True)
    
    # --- XÁC THỰC OTP ---
    is_verified = models.BooleanField(default=False)
    otp_code = models.CharField(max_length=6, blank=True, null=True)
    
    # --- QUAN HỆ BẠN BÈ ---
    friends = models.ManyToManyField('self', symmetrical=True, blank=True)

    def __str__(self):
        return self.user.username

    def generate_otp(self):
        """Tạo mã 6 số ngẫu nhiên"""
        self.otp_code = str(random.randint(100000, 999999))
        self.save()

class Category(models.Model):
    name = models.CharField(max_length=100)
    icon_name = models.CharField(max_length=50, default='marker-icon.png')
    
    def __str__(self):
        return self.name

class Location(models.Model):
    name = models.CharField(max_length=200)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='locations')
    description = models.TextField(blank=True)
    address = models.CharField(max_length=255, blank=True)
    is_approved = models.BooleanField(default=False)
    image = models.ImageField(upload_to='location_images/', blank=True, null=True)
    geom = gis_models.PointField(srid=4326)
    creator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    open_time = models.TimeField(null=True, blank=True)
    close_time = models.TimeField(null=True, blank=True)

    def __str__(self):
        return self.name

    @property
    def avg_rating(self):
        """Tính điểm trung bình sao"""
        avg = self.reviews.aggregate(Avg('rating'))['rating__avg']
        return round(avg, 1) if avg else 0

class LocationImage(models.Model):
    location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='location_gallery/')
    created_at = models.DateTimeField(auto_now_add=True)

class Review(models.Model):
    location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField()
    image = models.ImageField(upload_to='review_images/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'location')

class FriendRequest(models.Model):
    from_user = models.ForeignKey(User, related_name="friend_requests_sent", on_delete=models.CASCADE)
    to_user = models.ForeignKey(User, related_name="friend_requests_received", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, default='pending') # pending, accepted, rejected

    def __str__(self):
        return f"{self.from_user} -> {self.to_user} ({self.status})"