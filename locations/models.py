from django.db import models
from django.contrib.gis.db import models as gis_models  # Đổi tên để không trùng với models thường
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator # Công cụ kiểm tra điểm số
from django.contrib.auth.models import User

# 1. Danh mục
class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name="Tên danh mục")
    icon_name = models.CharField(max_length=50, default='marker-icon.png')

    def __str__(self):
        return self.name

# 2. Địa điểm
class Location(models.Model):
    name = models.CharField(max_length=200, verbose_name="Tên địa điểm")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name="Danh mục")
    description = models.TextField(blank=True, verbose_name="Mô tả")
    address = models.CharField(max_length=255, blank=True, verbose_name="Địa chỉ")
    
    # --- MỚI THÊM: Ảnh đại diện cho địa điểm ---
    image = models.ImageField(upload_to='location_images/', blank=True, null=True, verbose_name="Ảnh địa điểm")
    
    # Sử dụng gis_models cho trường hình học
    geom = gis_models.PointField(srid=4326, verbose_name="Vị trí")
    
    # Nếu User bị xóa, địa điểm vẫn giữ lại (Set NULL) thay vì xóa theo
    creator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Người tạo")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

# 3. Đánh giá (Review)
class Review(models.Model):
    location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='reviews', verbose_name="Địa điểm")
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Người đánh giá")
    
    # Dùng Validator để giới hạn điểm từ 1 đến 5
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name="Điểm đánh giá (1-5)"
    )
    
    comment = models.TextField(verbose_name="Bình luận")
    
    # Ảnh đính kèm trong bài review (đã thêm ở bước trước)
    image = models.ImageField(upload_to='review_images/', blank=True, null=True, verbose_name="Ảnh đính kèm")
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} đánh giá {self.location.name}"
class UserProfile(models.Model):
    # Liên kết 1-1 với tài khoản User mặc định của Django
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    
    # Danh sách bạn bè (symmetrical=True nghĩa là A kết bạn B thì B cũng là bạn A)
    friends = models.ManyToManyField('self', blank=True, symmetrical=True)
    
    # Lưu tọa độ cuối cùng của người dùng
    last_lat = models.FloatField(null=True, blank=True)
    last_lon = models.FloatField(null=True, blank=True)
    
    # Trạng thái hiện tại
    battery_level = models.IntegerField(default=100)
    status_message = models.CharField(max_length=100, blank=True, null=True)
    
    # Thời gian cập nhật vị trí cuối cùng
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Profile của {self.user.username}"