# Website Hitech NDT

## 📋 Tổng Quan
Website chính thức của công ty Hitech NDT - chuyên về kiểm tra không phá hủy (Non-Destructive Testing).

## 🏗️ Công Nghệ Sử Dụng
- **Backend**: Django 4.2.7 + PostgreSQL 14
- **Frontend**: HTML/CSS/JavaScript + Bootstrap
- **Web Server**: Nginx + Gunicorn
- **Domain**: hitechndt.vn, www.hitechndt.vn
- **Server**: Ubuntu 22.04 LTS

## 📁 Cấu Trúc Project
```
Hitech-NDT-Website/
├── README.md              # File này - hướng dẫn tổng quan
├── deploy.sh              # Script deploy tự động (lần đầu)
├── update.sh              # Script update code
└── site_hitech/           # Thư mục chứa source code Django
    ├── manage.py          # Django management
    ├── requirements.txt   # Python dependencies
    ├── api/              # App chính
    ├── blog/             # App blog
    ├── templates/        # HTML templates
    ├── static/           # CSS, JS, hình ảnh
    └── site_hitech/      # Django settings
```

## 🚀 Hướng Dẫn Deploy Lần Đầu

### 1. Chuẩn Bị Server
- Server Ubuntu 22.04 LTS
- Domain đã trỏ về IP server  
- Quyền root hoặc sudo

### 2. Chạy Script Deploy
```bash
# Upload code lên server và chạy
sudo bash deploy.sh
```

### 3. Tạo Superuser (Sau khi deploy)
```bash
cd /var/www/hitech_ndt
source venv/bin/activate
export DJANGO_SETTINGS_MODULE=site_hitech.settings_production
python manage.py createsuperuser
```

## 🔄 Hướng Dẫn Update Code

### Cách 1: Sử dụng Script (Khuyến Nghị)
```bash
# Chạy script update tự động
sudo bash update.sh
```

### Cách 2: Update Thủ Công
```bash
# 1. Backup code hiện tại
sudo cp -r /var/www/hitech_ndt /var/www/hitech_ndt_backup_$(date +%Y%m%d)

# 2. Copy code mới
sudo cp -r site_hitech/* /var/www/hitech_ndt/

# 3. Chạy migrations và collect static
cd /var/www/hitech_ndt
source venv/bin/activate
export DJANGO_SETTINGS_MODULE=site_hitech.settings_production
python manage.py migrate
python manage.py collectstatic --noinput

# 4. Restart services
sudo systemctl restart hitech-ndt
sudo systemctl restart nginx
```

## 📊 Quản Lý Services

### Kiểm Tra Trạng Thái
```bash
# Kiểm tra Django app
sudo systemctl status hitech-ndt

# Kiểm tra Nginx
sudo systemctl status nginx

# Kiểm tra database
sudo systemctl status postgresql@14-main
```

### Restart Services
```bash
# Restart Django app
sudo systemctl restart hitech-ndt

# Restart Nginx
sudo systemctl restart nginx
```

### Xem Logs
```bash
# Xem log Django
sudo journalctl -u hitech-ndt -f

# Xem log Nginx
sudo tail -f /var/log/nginx/error.log

# Xem log Django file
sudo tail -f /var/log/django.log
```

## 💾 Cấu Hình Database

### Thông Tin Database Hiện Tại
- **Engine**: PostgreSQL 14
- **Database**: hitech_ndt_db
- **User**: hitech_ndt_user
- **Password**: hitech2024
- **Host**: localhost
- **Port**: 5432

### Backup Database
```bash
# Backup database
sudo -u postgres pg_dump hitech_ndt_db > backup_$(date +%Y%m%d).sql

# Restore database
sudo -u postgres psql hitech_ndt_db < backup_file.sql
```

## 🔧 Troubleshooting

### Lỗi Thường Gặp

1. **Website không truy cập được**
   ```bash
   # Kiểm tra service
   sudo systemctl status nginx
   sudo systemctl status hitech-ndt
   
   # Restart services
   sudo systemctl restart nginx
   sudo systemctl restart hitech-ndt
   ```

2. **Lỗi database connection**
   ```bash
   # Kiểm tra PostgreSQL
   sudo systemctl status postgresql@14-main
   
   # Kiểm tra kết nối
   sudo -u postgres psql -c "SELECT version();"
   ```

3. **Lỗi static files**
   ```bash
   # Collect static lại
   cd /var/www/hitech_ndt
   source venv/bin/activate
   export DJANGO_SETTINGS_MODULE=site_hitech.settings_production
   python manage.py collectstatic --noinput
   ```

4. **Lỗi SSL certificate**
   ```bash
   # Renew SSL certificate
   sudo certbot renew
   
   # Test SSL config
   sudo nginx -t && sudo systemctl reload nginx
   ```

5. **Editor (CKEditor/Summernote) không hiển thị**
   ```bash
   # Check static files
   curl -I https://hitechndt.vn/static/ckeditor/ckeditor/ckeditor.js
   
   # If 404, check Nginx config
   grep "/static" /etc/nginx/sites-available/hitechndt
   
   # Should use 'alias' not 'root':
   # location /static/ {
   #     alias /var/www/hitech_ndt/staticfiles/;
   # }
   
   # Restart services if fixed
   sudo nginx -t && sudo systemctl reload nginx
   ```

## 📁 Đường Dẫn Quan Trọng

- **Project Directory**: `/var/www/hitech_ndt`
- **Virtual Environment**: `/var/www/hitech_ndt/venv`
- **Static Files**: `/var/www/hitech_ndt/staticfiles`
- **Media Files**: `/var/www/hitech_ndt/media`
- **Nginx Config**: `/etc/nginx/sites-available/hitechndt`
- **Service File**: `/etc/systemd/system/hitech-ndt.service`
- **SSL Certificates**: `/etc/letsencrypt/live/hitechndt.vn/`

## 📞 Liên Hệ
- **Website**: hitechndt.vn
- **Email**: info@hitechndt.vn
- **Admin Panel**: https://hitechndt.vn/admin/

## 📄 License
Proprietary - Hitech NDT Company
## 🛠️ CHẾ ĐỘ BẢO TRÌ

### Trên VPS
```bash
# Bật chế độ bảo trì
maintenance-mode on

# Tắt chế độ bảo trì  
maintenance-mode off

# Kiểm tra trạng thái
maintenance-mode status
```

### Từ máy Local

**Cách 1: SSH trực tiếp**
```bash
ssh root@103.90.224.176 "maintenance-mode on"
ssh root@103.90.224.176 "maintenance-mode off"
ssh root@103.90.224.176 "maintenance-mode status"
```

**Cách 2: Tạo script local (Windows)**
Tạo file `maintenance.bat`:
```batch
@echo off
if "%1"=="on" (
    ssh root@103.90.224.176 "maintenance-mode on"
) else if "%1"=="off" (
    ssh root@103.90.224.176 "maintenance-mode off"  
) else if "%1"=="status" (
    ssh root@103.90.224.176 "maintenance-mode status"
) else (
    echo Sử dụng: maintenance.bat [on/off/status]
)
```

Sử dụng: `maintenance.bat on`

**Cách 3: Tạo script local (Mac/Linux)**
Tạo file `maintenance.sh`:
```bash
#!/bin/bash
ssh root@103.90.224.176 "maintenance-mode $1"
chmod +x maintenance.sh
```

Sử dụng: `./maintenance.sh on`

### Tự động bảo trì
- Khi Django service down → Tự động hiển thị trang bảo trì
- Khi có lỗi 502, 503, 504 → Chuyển sang trang bảo trì
- Trang bảo trì: `/var/www/maintenance/index.html`

## 🚀 GIT WORKFLOW & DEPLOYMENT

### 💻 Setup Local Development

#### 1. Clone repository về máy local
```bash
git clone https://github.com/phihung13/Hitech-NDT-Website.git
cd Hitech-NDT-Website
```

#### 2. Tạo môi trường ảo Python
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Mac/Linux  
python3 -m venv venv
source venv/bin/activate
```

#### 3. Cài đặt dependencies
```bash
cd site_hitech
pip install -r requirements.txt
```

#### 4. Cấu hình môi trường development
```bash
# Copy file env
cp .env.example .env

# Sửa file .env với thông tin local:
DEBUG=True
DATABASE_URL=sqlite:///db.sqlite3
SECRET_KEY=your-secret-key-here
```

#### 5. Setup database local
```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py collectstatic
python manage.py runserver
```

Truy cập: http://localhost:8000

### 🔄 Quy Trình Development

#### 1. Sửa code trên máy local
- Edit files trong project
- Test trên localhost:8000
- Kiểm tra admin tại localhost:8000/admin

#### 2. Commit và push changes
```bash
git add .
git commit -m "Mô tả thay đổi cụ thể"
git push origin main
```

#### 3. Deploy lên production server
```bash
# Từ local SSH vào server
ssh root@103.90.224.176 "git-deploy"

# Hoặc tạo script local
```

### 🛠️ Script Tiện Ích Local

#### Tạo file deploy.bat (Windows)
```batch
@echo off
echo 🚀 Deploying to production...
ssh root@103.90.224.176 "git-deploy"
echo ✅ Deploy complete!
pause
```

#### Tạo file deploy.sh (Mac/Linux)
```bash
#!/bin/bash
echo "🚀 Deploying to production..."
ssh root@103.90.224.176 "git-deploy"
echo "✅ Deploy complete!"
chmod +x deploy.sh
```

#### Tạo file maintenance.bat (Windows)
```batch
@echo off
if "%1"=="on" (
    echo 🔧 Bật chế độ bảo trì...
    ssh root@103.90.224.176 "maintenance-mode on"
) else if "%1"=="off" (
    echo ✅ Tắt chế độ bảo trì...
    ssh root@103.90.224.176 "maintenance-mode off"
) else if "%1"=="status" (
    ssh root@103.90.224.176 "maintenance-mode status"
) else (
    echo Sử dụng: maintenance.bat [on/off/status]
)
```

### 🔧 Lệnh Quan Trọng

#### Trên Server (VPS)
```bash
# Deploy code mới từ Git
git-deploy

# Bảo trì website
maintenance-mode on     # Bật bảo trì
maintenance-mode off    # Tắt bảo trì
maintenance-mode status # Kiểm tra trạng thái

# Kiểm tra logs
sudo journalctl -u hitech-ndt -f

# Restart services
sudo systemctl restart hitech-ndt nginx
```

#### Từ Local
```bash
# Deploy nhanh
ssh root@103.90.224.176 "git-deploy"

# Bảo trì từ xa
ssh root@103.90.224.176 "maintenance-mode on"
ssh root@103.90.224.176 "maintenance-mode off"

# Xem logs từ xa
ssh root@103.90.224.176 "journalctl -u hitech-ndt -f"
```

### 🎯 Workflow Hoàn Chỉnh

1. **Development:** Code trên local → Test localhost
2. **Commit:** `git add . && git commit -m "message" && git push`
3. **Deploy:** `ssh root@103.90.224.176 "git-deploy"` hoặc chạy script
4. **Monitor:** Kiểm tra website hoạt động
5. **Rollback:** Nếu lỗi, dùng `maintenance-mode on` và fix

### 📝 Tính Năng Mới

- ✅ **CKEditor 5** (thay thế CKEditor 4 có lỗ hổng bảo mật)
- ✅ **Maintenance mode** tự động khi service down
- ✅ **Git workflow** hoàn chỉnh với auto-deploy
- ✅ **SEO optimization** và multi-language support
- ✅ **Responsive design** và admin dashboard

**🚀 Chúc bạn phát triển website thành công!**

