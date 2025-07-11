# Hướng Dẫn Triển Khai Hitech NDT Website

## Tổng Quan
Hướng dẫn này mô tả quy trình triển khai và cập nhật website Hitech NDT trên môi trường production Ubuntu/Debian.

## Yêu Cầu Hệ Thống
- Ubuntu 20.04+ hoặc Debian 11+
- Python 3.8+
- PostgreSQL 12+
- Nginx
- SSL Certificate (Let's Encrypt)
- Git
- Quyền root hoặc sudo

## Cấu Trúc Files
```
├── deploy.sh           # Script triển khai ban đầu
├── update.sh           # Script cập nhật
├── rollback.sh         # Script khôi phục
├── setup_git.sh        # Script cấu hình Git
├── README.md           # Tài liệu chính
├── QUICK_REFERENCE.md  # Tham chiếu nhanh
├── DEPLOYMENT_GUIDE.md # Hướng dẫn này
└── site_hitech/        # Mã nguồn Django
```

## Quy Trình Triển Khai

### 1. Triển Khai Lần Đầu
```bash
# Clone repository
git clone https://github.com/your-username/Hitech-NDT-Website.git
cd Hitech-NDT-Website

# Cấu hình Git (nếu cần)
sudo chmod +x setup_git.sh
sudo ./setup_git.sh

# Chạy triển khai
sudo chmod +x deploy.sh
sudo ./deploy.sh
```

### 2. Cập Nhật Code
```bash
# Chỉ cần chạy một lệnh
sudo ./update.sh
```

### 3. Khôi Phục (Nếu Có Lỗi)
```bash
sudo ./rollback.sh
```

## Cấu Hình Tự Động

### Deploy Script (deploy.sh)
- Cài đặt dependencies
- Cấu hình firewall
- Thiết lập PostgreSQL
- Tạo virtual environment
- Cấu hình Django settings
- Thiết lập Gunicorn service
- Cấu hình Nginx với SSL
- Tạo SSL certificate

### Update Script (update.sh)
- Sao lưu phiên bản hiện tại
- Pull code mới từ Git
- Cập nhật dependencies
- Chạy migrations
- Thu thập static files
- Khởi động lại services
- Kiểm tra health check
- Rollback tự động nếu có lỗi

### Rollback Script (rollback.sh)
- Liệt kê các backup có sẵn
- Khôi phục code và database
- Khởi động lại services
- Kiểm tra trạng thái

## Biến Cấu Hình

### Trong deploy.sh và update.sh:
```bash
DOMAIN="your-domain.com"           # Domain của bạn
PROJECT_NAME="hitech_ndt"          # Tên project
PROJECT_DIR="/var/www/hitech_ndt"  # Thư mục project
GITHUB_REPO="https://github.com/your-username/Hitech-NDT-Website.git"
BRANCH="main"                      # Nhánh Git
DB_NAME="hitech_ndt_db"            # Tên database
DB_USER="hitech_user"              # User database
DB_PASSWORD="your_secure_password" # Mật khẩu database
```

## Cấu Trúc Thư Mục Production
```
/var/www/hitech_ndt/               # Thư mục chính
├── site_hitech/                   # Code Django
├── venv/                          # Virtual environment
├── staticfiles/                   # Static files
├── media/                         # Media files
├── logs/                          # Log files
└── backups/                       # Backup files
```

## Services

### Gunicorn Service
- File: `/etc/systemd/system/hitech_ndt.service`
- Socket: `/var/www/hitech_ndt/gunicorn.sock`
- Workers: 3
- Timeout: 30s

### Nginx Configuration
- File: `/etc/nginx/sites-available/hitech_ndt`
- SSL: Let's Encrypt
- HTTP → HTTPS redirect
- Static/Media files serving

## Database
- PostgreSQL
- Database: `hitech_ndt_db`
- User: `hitech_user`
- Backup tự động khi update

## SSL Certificate
- Let's Encrypt
- Auto-renewal setup
- HTTPS redirect

## Monitoring

### Log Files
```bash
# Django logs
tail -f /var/www/hitech_ndt/logs/django.log

# Gunicorn logs
journalctl -u hitech_ndt -f

# Nginx logs
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log
```

### Service Status
```bash
# Kiểm tra services
sudo systemctl status hitech_ndt
sudo systemctl status nginx
sudo systemctl status postgresql

# Kiểm tra website
curl -I https://your-domain.com
```

## Troubleshooting

### Lỗi Thường Gặp

1. **Service không start**
   ```bash
   sudo journalctl -u hitech_ndt --no-pager
   sudo systemctl restart hitech_ndt
   ```

2. **Database connection error**
   ```bash
   sudo -u postgres psql
   \l  # List databases
   \du # List users
   ```

3. **SSL certificate error**
   ```bash
   sudo certbot renew --dry-run
   sudo certbot certificates
   ```

4. **Static files không load**
   ```bash
   cd /var/www/hitech_ndt/site_hitech
   source ../venv/bin/activate
   python manage.py collectstatic --noinput
   ```

### Emergency Commands
```bash
# Stop all services
sudo systemctl stop hitech_ndt nginx

# Start all services
sudo systemctl start postgresql nginx hitech_ndt

# Restart all services
sudo systemctl restart postgresql nginx hitech_ndt

# Check disk space
df -h

# Check memory
free -h

# Check processes
ps aux | grep gunicorn
ps aux | grep nginx
```

## Bảo Mật

### Firewall Rules
- Port 22 (SSH)
- Port 80 (HTTP - redirect to HTTPS)
- Port 443 (HTTPS)
- PostgreSQL chỉ local access

### File Permissions
- Project files: `www-data:www-data`
- Scripts: executable by root
- Database: postgres user only

### Backup Strategy
- Code backup trước mỗi update
- Database backup trước mỗi update
- Giữ 5 backup gần nhất
- Tự động cleanup backup cũ

## Performance

### Optimization
- Gunicorn workers: 3
- Nginx gzip compression
- Static files caching
- Database connection pooling

### Monitoring
- Django debug toolbar (development only)
- Nginx access logs
- System resource monitoring

## Maintenance

### Regular Tasks
```bash
# Update system packages
sudo apt update && sudo apt upgrade

# Renew SSL certificates
sudo certbot renew

# Clean old backups
find /var/www/hitech_ndt/backups -name "*.tar.gz" -mtime +30 -delete

# Rotate logs
sudo logrotate -f /etc/logrotate.conf
```

### Monthly Checklist
- [ ] Update system packages
- [ ] Check SSL certificate expiry
- [ ] Review log files
- [ ] Check disk space
- [ ] Test backup/restore process
- [ ] Update dependencies (if needed)

## Support

Nếu gặp vấn đề:
1. Kiểm tra logs
2. Xem QUICK_REFERENCE.md
3. Chạy health check
4. Liên hệ team development

---
*Cập nhật lần cuối: $(date)*