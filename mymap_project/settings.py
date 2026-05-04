import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = "django-insecure-%vgxnlo4yb75vtus)-&67_*6z5&wcrhso4(n!@#^3xe9=l$mt^"
DEBUG = True
ALLOWED_HOSTS = ['127.0.0.1', 'localhost', '*']

# --- CẤU HÌNH ƯU TIÊN APP ---
INSTALLED_APPS = [
    'locations',            # 👈 Đưa app của bạn lên đầu để ưu tiên Template/Static
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    'django.contrib.gis',
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "mymap_project.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / 'templates'], # 👈 Đảm bảo có dòng này để nhận diện thư mục templates gốc
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "mymap_project.wsgi.application"

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': 'bando_db',
        'USER': 'MAC',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "Asia/Ho_Chi_Minh" # 👈 Đổi sang giờ VN cho đúng lịch sử trực ban/công việc
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"]

# --- GIS LIBRARY PATHS ---
GDAL_LIBRARY_PATH = '/Users/MAC/anaconda3/lib/libgdal.dylib'
GEOS_LIBRARY_PATH = '/Users/MAC/anaconda3/lib/libgeos_c.dylib'

# --- AUTH REDIRECTS ---
LOGIN_REDIRECT_URL = 'map_home'
LOGOUT_REDIRECT_URL = 'map_home'

# --- MEDIA CONFIG ---
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# --- EMAIL CONFIG (Dùng SMTP để gửi mã OTP thực tế) ---
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'khamnguyen147369@gmail.com' 
EMAIL_HOST_PASSWORD = 'ljtn yhkf dymp hnld'  # 👈 Dán mã 16 ký tự vào đây
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER