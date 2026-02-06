from django.db import models

# Create your models here.
from django.contrib.gis.db import models
from django.contrib.auth.models import User

# 1. Danh mục
class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name="Tên danh mục")
    icon_name = models.CharField(max_length=50, default='marker-icon.png')

    def __str__(self):
        return self.name

# 2. Địa điểm (Đây là class bị thiếu khiến lỗi xảy ra)
class Location(models.Model):
    name = models.CharField(max_length=200, verbose_name="Tên địa điểm")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name="Danh mục")
    description = models.TextField(blank=True, verbose_name="Mô tả")
    address = models.CharField(max_length=255, blank=True, verbose_name="Địa chỉ")
    
    # Tọa độ
    geom = models.PointField(srid=4326, verbose_name="Vị trí")
    
    creator = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

# 3. Đánh giá
class Review(models.Model):
    location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField(choices=[(i, str(i)) for i in range(1, 6)])
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)