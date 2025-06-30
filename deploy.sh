#!/bin/bash

# ========================================
# HITECH NDT - DEPLOY SCRIPT
# Script deploy hoàn chỉnh cho website Hitech NDT
# Domain: hitechndt.vn và www.hitechndt.vn
# ========================================

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuration
DOMAIN="hitechndt.vn"
WWW_DOMAIN="www.hitechndt.vn"
PROJECT_NAME="hitech_ndt"
PROJECT_DIR="/var/www/$PROJECT_NAME"
SERVICE_NAME="hitech-ndt"
ADMIN_EMAIL="admin@hitechndt.vn"
DB_PASSWORD="hitech2024"
GITHUB_REPO="https://github.com/phihung13/Hitech-NDT-Website.git"  # Thay đổi URL này

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

install_dependencies() {
    print_status "Cài đặt dependencies..."
    
    apt update && apt upgrade -y
    
    apt install -y \
        python3 \
        python3-pip \
        python3-venv \
        nginx \
        postgresql \
        postgresql-contrib \
        git \
        ufw \
        curl \
        wget \
        certbot \
        python3-certbot-nginx \
        fail2ban
    
    print_success "Dependencies đã được cài đặt"
}

setup_firewall() {
    print_status "Cấu hình firewall..."
    
    ufw --force reset
    ufw default deny incoming
    ufw default allow outgoing
    ufw allow 22/tcp
    ufw allow 80/tcp
    ufw allow 443/tcp
    ufw --force enable
    
    print_success "Firewall đã được cấu hình"
}

setup_database() {
    print_status "Cài đặt PostgreSQL database..."
    
    systemctl start postgresql
    systemctl enable postgresql
    
    # Save database info
    echo "Database password: $DB_PASSWORD" > /root/db_password.txt
    chmod 600 /root/db_password.txt
    
    # Create database and user
    sudo -u postgres psql << EOF
DROP DATABASE IF EXISTS ${PROJECT_NAME}_db;
DROP USER IF EXISTS ${PROJECT_NAME}_user;
CREATE DATABASE ${PROJECT_NAME}_db;
CREATE USER ${PROJECT_NAME}_user WITH PASSWORD '$DB_PASSWORD';
ALTER ROLE ${PROJECT_NAME}_user SET client_encoding TO 'utf8';
ALTER ROLE ${PROJECT_NAME}_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE ${PROJECT_NAME}_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE ${PROJECT_NAME}_db TO ${PROJECT_NAME}_user;
\q
EOF
    
    print_success "Database đã được tạo"
}

check_git_access() {
    print_status "Kiểm tra Git access..."
    
    # Check if git credentials are configured
    if [ ! -f "/root/.git-credentials" ] && [ ! -f "/root/.ssh/config" ]; then
        print_error "Git credentials chưa được cấu hình!"
        print_status "Chạy: sudo bash setup_git.sh"
        exit 1
    fi
    
    # Test access to repository
    if ! git ls-remote $GITHUB_REPO >/dev/null 2>&1; then
        print_error "Không thể truy cập repository: $GITHUB_REPO"
        print_status "Kiểm tra lại Git credentials hoặc chạy: sudo bash setup_git.sh"
        exit 1
    fi
    
    print_success "✓ Git access OK"
}

deploy_application() {
    print_status "Deploy ứng dụng Django từ Git..."
    
    # Check Git access first
    check_git_access
    
    # Backup current version if exists
    if [ -d "$PROJECT_DIR" ]; then
        print_status "Backup version hiện tại..."
        mv $PROJECT_DIR $PROJECT_DIR.backup.$(date +%Y%m%d_%H%M%S)
    fi
    
    # Create new project directory
    mkdir -p $PROJECT_DIR
    cd $PROJECT_DIR
    
    # Clone latest code from Git
    print_status "Pulling code mới nhất từ Git..."
    if git clone $GITHUB_REPO .; then
        print_success "✓ Git clone thành công"
        
        # Pull latest changes
        git pull origin main
        
        # Navigate to Django project if in subfolder
        if [ -d "site_hitech" ]; then
            cd site_hitech
        fi
    else
        print_error "Git clone thất bại!"
        print_warning "Fallback: copy từ thư mục local..."
        rm -rf $PROJECT_DIR/*
        cp -r "$(dirname "$0")/site_hitech"/* .
    fi
    
    # Create virtual environment
    python3 -m venv venv
    source venv/bin/activate
    
    # Install dependencies
    pip install --upgrade pip
    pip install -r requirements.txt
    
    # Create production settings
    cat > site_hitech/settings_production.py << EOF
from .settings import *

DEBUG = False
ALLOWED_HOSTS = ['$DOMAIN', '$WWW_DOMAIN', 'localhost', '127.0.0.1']

SECRET_KEY = '$(openssl rand -base64 50)'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': '${PROJECT_NAME}_db',
        'USER': '${PROJECT_NAME}_user',
        'PASSWORD': '$DB_PASSWORD',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

STATIC_ROOT = '$PROJECT_DIR/staticfiles'
MEDIA_ROOT = '$PROJECT_DIR/media'

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

    # Ensure log file exists
    touch /var/log/django.log
    chown www-data:www-data /var/log/django.log
    
    # Set environment
    export DJANGO_SETTINGS_MODULE=site_hitech.settings_production
    
    # Run Django setup
    python manage.py migrate
    python manage.py collectstatic --noinput
    
    # Create homepage settings if script exists
    [ -f "create_homepage_settings.py" ] && python create_homepage_settings.py 2>/dev/null
    
    print_success "Django application deployed với code mới nhất"
}

create_gunicorn_service() {
    print_status "Tạo Gunicorn service..."
    
    cat > /etc/systemd/system/$SERVICE_NAME.service << EOF
[Unit]
Description=Hitech NDT Django Application
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=$PROJECT_DIR
Environment="DJANGO_SETTINGS_MODULE=site_hitech.settings_production"
ExecStart=$PROJECT_DIR/venv/bin/gunicorn --workers 3 --bind unix:$PROJECT_DIR/gunicorn.sock site_hitech.wsgi:application
Restart=always

[Install]
WantedBy=multi-user.target
EOF
    
    systemctl daemon-reload
    systemctl enable $SERVICE_NAME
    systemctl start $SERVICE_NAME
    
    print_success "Gunicorn service đã được tạo"
}

configure_nginx() {
    print_status "Cấu hình Nginx..."
    
    cat > /etc/nginx/sites-available/hitechndt << EOF
server {
    listen 80;
    server_name $DOMAIN $WWW_DOMAIN;
    return 301 https://\$host\$request_uri;
}

server {
    listen 443 ssl;
    server_name $DOMAIN $WWW_DOMAIN;
    
    # SSL configuration sẽ được thêm bởi certbot
    
    client_max_body_size 100M;
    
    location = /favicon.ico { access_log off; log_not_found off; }
    
    location /static/ {
        alias $PROJECT_DIR/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
    
    location /media/ {
        alias $PROJECT_DIR/media/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
    
    location / {
        include proxy_params;
        proxy_pass http://unix:$PROJECT_DIR/gunicorn.sock;
    }
    
    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
    add_header X-XSS-Protection "1; mode=block" always;
}
EOF
    
    ln -sf /etc/nginx/sites-available/hitechndt /etc/nginx/sites-enabled/
    rm -f /etc/nginx/sites-enabled/default
    
    nginx -t && systemctl restart nginx
    
    print_success "Nginx đã được cấu hình"
}

setup_ssl() {
    print_status "Cài đặt SSL certificate..."
    
    certbot --nginx -d $DOMAIN -d $WWW_DOMAIN --non-interactive --agree-tos --email $ADMIN_EMAIL
    
    if [ $? -eq 0 ]; then
        print_success "SSL certificate đã được cài đặt"
        
        # Auto-renewal
        (crontab -l 2>/dev/null; echo "0 12 * * * /usr/bin/certbot renew --quiet") | crontab -
    else
        print_warning "SSL setup failed - website vẫn hoạt động với HTTP"
    fi
}

set_permissions() {
    print_status "Thiết lập permissions..."
    
    chown -R www-data:www-data $PROJECT_DIR
    chmod -R 755 $PROJECT_DIR
    
    print_success "Permissions đã được thiết lập"
}

run_health_check() {
    print_status "Kiểm tra hệ thống..."
    
    sleep 5
    
    # Check services
    if systemctl is-active --quiet $SERVICE_NAME; then
        print_success "✓ Django service đang chạy"
    else
        print_error "✗ Django service lỗi"
    fi
    
    if systemctl is-active --quiet nginx; then
        print_success "✓ Nginx đang chạy"
    else
        print_error "✗ Nginx lỗi"
    fi
    
    if systemctl is-active --quiet postgresql; then
        print_success "✓ PostgreSQL đang chạy"
    else
        print_error "✗ PostgreSQL lỗi"
    fi
    
    # Check website
    if curl -s -o /dev/null -w "%{http_code}" http://localhost | grep -q "200\|301\|302"; then
        print_success "✓ Website đang hoạt động"
    else
        print_warning "⚠ Website có thể cần kiểm tra"
    fi
}

main() {
    print_status "========================================="
    print_status "HITECH NDT - DEPLOY SCRIPT"
    print_status "========================================="
    echo
    
    check_root
    install_dependencies
    setup_firewall
    setup_database
    deploy_application
    create_gunicorn_service
    configure_nginx
    setup_ssl
    set_permissions
    run_health_check
    
    echo
    print_success "========================================="
    print_success "DEPLOY HOÀN THÀNH!"
    print_success "========================================="
    print_success "Website: https://$DOMAIN"
    print_success "WWW: https://$WWW_DOMAIN"
    print_success "Admin: https://$DOMAIN/admin/"
    print_success "Database: PostgreSQL"
    print_success "User: ${PROJECT_NAME}_user"
    print_success "Password: $DB_PASSWORD"
    echo
    print_status "Để update code: sudo bash update.sh"
    print_status "Để xem logs: sudo journalctl -u $SERVICE_NAME -f"
}

# Run main function
main "$@" 