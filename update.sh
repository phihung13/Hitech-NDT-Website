#!/bin/bash

# ========================================
# HITECH NDT - UPDATE SCRIPT
# Script update code nhanh cho website hiện có
# ========================================

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuration - Cập nhật theo thực tế hiện tại
PROJECT_DIR="/var/www/hitech_ndt"
SERVICE_NAME="hitech-ndt"
BACKUP_DIR="/backup/update_$(date +%Y%m%d_%H%M%S)"

# Functions
print_status() { echo -e "${BLUE}[INFO]${NC} $1"; }
print_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
print_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
print_error() { echo -e "${RED}[ERROR]${NC} $1"; }

check_root() {
    if [[ $EUID -ne 0 ]]; then
        print_error "Script cần chạy với quyền root: sudo $0"
        exit 1
    fi
}

check_source() {
    if [ ! -d "site_hitech" ]; then
        print_error "Không tìm thấy thư mục site_hitech"
        print_error "Hãy chạy script từ thư mục chứa source code mới"
        exit 1
    fi
    
    if [ ! -f "site_hitech/manage.py" ]; then
        print_error "Không tìm thấy manage.py trong site_hitech"
        exit 1
    fi
}

check_production() {
    if [ ! -d "$PROJECT_DIR" ]; then
        print_error "Không tìm thấy website production tại $PROJECT_DIR"
        print_error "Sử dụng deploy.sh để deploy lần đầu"
        exit 1
    fi
}

create_backup() {
    print_status "Tạo backup..."
    
    mkdir -p "$BACKUP_DIR"
    cp -r "$PROJECT_DIR" "$BACKUP_DIR/site_backup"
    
    print_success "Backup tại: $BACKUP_DIR"
}

stop_services() {
    print_status "Dừng services..."
    
    systemctl stop "$SERVICE_NAME" 2>/dev/null || print_warning "Django service không chạy"
    
    print_success "Services đã dừng"
}

update_code() {
    print_status "Update source code..."
    
    # Backup old code
    if [ -d "$PROJECT_DIR.old" ]; then
        rm -rf "$PROJECT_DIR.old"
    fi
    
    cp -r "$PROJECT_DIR" "$PROJECT_DIR.old"
    
    # Copy new code (preserve venv, staticfiles, media, logs)
    rsync -av --exclude 'venv' --exclude 'staticfiles' --exclude 'media' --exclude '*.log' \
          --exclude '__pycache__' --exclude '*.pyc' \
          site_hitech/ "$PROJECT_DIR/"
    
    print_success "Code đã được update"
}

restore_production_settings() {
    print_status "Khôi phục production settings..."
    
    if [ -f "$PROJECT_DIR.old/site_hitech/settings_production.py" ]; then
        cp "$PROJECT_DIR.old/site_hitech/settings_production.py" "$PROJECT_DIR/site_hitech/"
        print_success "Production settings đã được khôi phục"
    else
        print_warning "Không tìm thấy settings_production.py cũ"
        # Tạo settings_production.py mới nếu không có
        create_production_settings
    fi
}

create_production_settings() {
    print_status "Tạo production settings mới..."
    
    cat > "$PROJECT_DIR/site_hitech/settings_production.py" << 'EOF'
from .settings import *

DEBUG = False
ALLOWED_HOSTS = ['hitechndt.vn', 'www.hitechndt.vn', 'localhost', '127.0.0.1']

SECRET_KEY = 'TYEwHbr9Vhm2zXlk2zX4VhfY7LCf0MmK2zX5d8w7RoNJPzWVKJwQ3zN4mK9CrL'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'hitech_ndt_db',
        'USER': 'hitech_ndt_user',
        'PASSWORD': 'hitech2024',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

STATIC_ROOT = '/var/www/hitech_ndt/staticfiles'
MEDIA_ROOT = '/var/www/hitech_ndt/media'

# Security settings
SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': '/var/log/django.log',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}

# CKEditor settings
CKEDITOR_UPLOAD_PATH = "uploads/"
CKEDITOR_IMAGE_BACKEND = "pillow"
CKEDITOR_BROWSE_SHOW_DIRS = True
CKEDITOR_RESTRICT_BY_USER = True

CKEDITOR_CONFIGS = {
    'default': {
        'toolbar': 'full',
        'height': 300,
        'width': '100%',
    },
}

# Summernote settings
SUMMERNOTE_CONFIG = {
    'summernote': {
        'width': '100%',
        'height': '400',
    },
}
EOF
    
    print_success "Production settings đã được tạo"
}

run_django_tasks() {
    print_status "Chạy Django tasks..."
    
    cd "$PROJECT_DIR"
    source venv/bin/activate
    
    export DJANGO_SETTINGS_MODULE=site_hitech.settings_production
    
    # Install any new dependencies
    pip install -r requirements.txt
    
    # Run migrations
    python manage.py migrate
    
    # Collect static files
    python manage.py collectstatic --noinput
    
    # Update homepage settings if script exists
    [ -f "create_homepage_settings.py" ] && python create_homepage_settings.py 2>/dev/null || true
    
    print_success "Django tasks hoàn thành"
}

set_permissions() {
    print_status "Thiết lập permissions..."
    
    chown -R www-data:www-data "$PROJECT_DIR"
    chmod -R 755 "$PROJECT_DIR"
    
    print_success "Permissions đã được thiết lập"
}

start_services() {
    print_status "Khởi động services..."
    
    systemctl start "$SERVICE_NAME"
    systemctl restart nginx
    
    print_success "Services đã khởi động"
}

run_health_check() {
    print_status "Kiểm tra website..."
    
    sleep 5
    
    # Check services
    if systemctl is-active --quiet "$SERVICE_NAME"; then
        print_success "✓ Django service đang chạy"
    else
        print_error "✗ Django service lỗi"
        print_error "Rollback bằng cách: mv $PROJECT_DIR.old $PROJECT_DIR && systemctl restart $SERVICE_NAME"
        return 1
    fi
    
    if systemctl is-active --quiet nginx; then
        print_success "✓ Nginx đang chạy"
    else
        print_error "✗ Nginx lỗi"
    fi
    
    # Check website response
    if curl -s -o /dev/null -w "%{http_code}" http://localhost | grep -q "200\|301\|302"; then
        print_success "✓ Website đang hoạt động"
    else
        print_warning "⚠ Website có thể cần kiểm tra"
    fi
}

main() {
    print_status "========================================="
    print_status "HITECH NDT - UPDATE CODE"
    print_status "========================================="
    print_status "Thư mục hiện tại: $(pwd)"
    print_status "Target: $PROJECT_DIR"
    print_status "Service: $SERVICE_NAME"
    echo
    
    # Confirmations and checks
    print_warning "⚠️  Website sẽ tạm dừng 2-3 phút trong quá trình update"
    print_warning "Tiếp tục? (y/N)"
    read -r CONFIRM
    if [[ ! $CONFIRM =~ ^[Yy]$ ]]; then
        print_status "Update đã hủy"
        exit 0
    fi
    
    check_root
    check_source
    check_production
    
    # Main update process
    create_backup
    stop_services
    update_code
    restore_production_settings
    run_django_tasks
    set_permissions
    start_services
    
    # Health check
    if run_health_check; then
        echo
        print_success "========================================="
        print_success "UPDATE HOÀN THÀNH!"
        print_success "========================================="
        print_success "Website: https://hitechndt.vn"
        print_success "Backup: $BACKUP_DIR"
        echo
        print_status "Để xem logs: sudo journalctl -u $SERVICE_NAME -f"
        print_status "Để rollback: mv $PROJECT_DIR.old $PROJECT_DIR && sudo systemctl restart $SERVICE_NAME"
    else
        print_error "========================================="
        print_error "UPDATE CÓ LỖI!"
        print_error "========================================="
        print_error "Kiểm tra logs: sudo journalctl -u $SERVICE_NAME -f"
        print_error "Rollback: mv $PROJECT_DIR.old $PROJECT_DIR && sudo systemctl restart $SERVICE_NAME"
    fi
}

# Run main function
main "$@" 