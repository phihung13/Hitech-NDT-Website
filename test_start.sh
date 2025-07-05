#!/bin/bash

# ========================================
# HITECH NDT - TEST LOCAL START
# Script khởi động tự động cho test local
# ========================================

set -e  # Exit on any error

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m'

# Functions
print_status() { echo -e "${BLUE}[INFO]${NC} $1"; }
print_success() { echo -e "${GREEN}[✓]${NC} $1"; }
print_warning() { echo -e "${YELLOW}[!]${NC} $1"; }
print_error() { echo -e "${RED}[✗]${NC} $1"; }
print_header() { echo -e "${PURPLE}$1${NC}"; }

clear
print_header "========================================="
print_header "🧪 HITECH NDT - TEST LOCAL SETUP"
print_header "========================================="
echo

# Check if we're in the right directory
if [ ! -d "site_hitech" ]; then
    print_error "Không tìm thấy thư mục site_hitech!"
    print_status "Hãy chạy script từ thư mục gốc của project"
    print_status "Example: cd Hitech-NDT-Website && ./test_start.sh"
    exit 1
fi

# Check Python
print_status "Kiểm tra Python..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version | grep -oE '[0-9]+\.[0-9]+')
    print_success "Python $PYTHON_VERSION detected"
else
    print_error "Python3 không được cài đặt!"
    print_status "Cài đặt Python3 trước khi tiếp tục"
    exit 1
fi

# Navigate to Django project
cd site_hitech

print_status "1. Tạo virtual environment..."
if [ -d "venv" ]; then
    print_warning "Virtual environment đã tồn tại, sử dụng lại..."
else
    python3 -m venv venv
    print_success "Virtual environment đã tạo"
fi

print_status "2. Kích hoạt virtual environment..."
source venv/bin/activate
print_success "Virtual environment đã kích hoạt"

print_status "3. Upgrade pip..."
pip install --upgrade pip -q

print_status "4. Cài đặt dependencies..."
if pip install -r requirements.txt -q; then
    print_success "Dependencies đã cài đặt"
else
    print_error "Lỗi cài đặt dependencies!"
    print_status "Thử: pip install --user -r requirements.txt"
    exit 1
fi

print_status "5. Kiểm tra và setup database..."
if [ -f "db.sqlite3" ]; then
    print_warning "Database đã tồn tại, skip migration..."
else
    if python manage.py migrate; then
        print_success "Database migration thành công"
    else
        print_error "Migration thất bại!"
        exit 1
    fi
fi

print_status "6. Tạo superuser test..."
python manage.py shell << EOF
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@test.com', 'admin123')
    print("✅ Admin user created: admin/admin123")
else:
    print("ℹ️  Admin user already exists")
EOF

print_status "7. Collect static files..."
if python manage.py collectstatic --noinput > /dev/null 2>&1; then
    print_success "Static files collected"
else
    print_warning "Static files có vấn đề (không ảnh hưởng test)"
fi

print_status "8. Kiểm tra cấu hình..."
# Create local test settings if not exists
if [ ! -f "site_hitech/settings_test.py" ]; then
    cat > site_hitech/settings_test.py << 'EOF'
from .settings import *

# Test environment settings
DEBUG = True
ALLOWED_HOSTS = ['*']

# Use SQLite for testing
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Console email backend for testing
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Disable security for local testing
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False

# Static files
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']

print("🧪 Test environment loaded")
EOF
    print_success "Test settings created"
fi

# Get local IP for network access
LOCAL_IP=$(hostname -I | awk '{print $1}' 2>/dev/null || echo "127.0.0.1")

print_success "========================================="
print_success "🎉 SETUP HOÀN THÀNH!"
print_success "========================================="
echo
print_header "📋 THÔNG TIN TRUY CẬP:"
echo "🌐 Local:    http://127.0.0.1:8000"
echo "🌐 Network:  http://$LOCAL_IP:8000"
echo "👤 Admin:    http://127.0.0.1:8000/admin"
echo "📧 Username: admin"
echo "🔑 Password: admin123"
echo
print_header "📱 TEST TRÊN ĐIỆN THOẠI:"
echo "Kết nối cùng WiFi và truy cập: http://$LOCAL_IP:8000"
echo
print_warning "Nhấn Ctrl+C để dừng server"
print_status "========================================="

# Start Django server
echo
print_status "🚀 Khởi động Django server..."
export DJANGO_SETTINGS_MODULE=site_hitech.settings_test
python manage.py runserver 0.0.0.0:8000 