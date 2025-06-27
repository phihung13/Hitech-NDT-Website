# HITECH NDT - QUICK REFERENCE

## 🚀 Commands Thường Dùng

### Deploy/Update
```bash
# Deploy lần đầu
sudo bash deploy.sh

# Update code
sudo bash update.sh
```

### Services Management
```bash
# Check status
sudo systemctl status hitech-ndt
sudo systemctl status nginx
sudo systemctl status postgresql@14-main

# Restart services
sudo systemctl restart hitech-ndt
sudo systemctl restart nginx
```

### Logs
```bash
# Django logs
sudo journalctl -u hitech-ndt -f
sudo tail -f /var/log/django.log

# Nginx logs
sudo tail -f /var/log/nginx/error.log
sudo tail -f /var/log/nginx/access.log
```

### Django Commands
```bash
cd /var/www/hitech_ndt
source venv/bin/activate
export DJANGO_SETTINGS_MODULE=site_hitech.settings_production

# Migrations
python manage.py migrate

# Collect static
python manage.py collectstatic --noinput

# Create superuser
python manage.py createsuperuser

# Django shell
python manage.py shell
```

### Database
```bash
# Connect to database
sudo -u postgres psql hitech_ndt_db

# Backup database
sudo -u postgres pg_dump hitech_ndt_db > backup_$(date +%Y%m%d).sql

# Restore database
sudo -u postgres psql hitech_ndt_db < backup_file.sql
```

### SSL/Certificates
```bash
# Renew SSL
sudo certbot renew

# Test SSL
sudo certbot certificates

# Nginx config test
sudo nginx -t
```

### Editor Issues
```bash
# Test CKEditor static files
curl -I https://hitechndt.vn/static/ckeditor/ckeditor/ckeditor.js

# Test Summernote static files  
curl -I https://hitechndt.vn/static/summernote/summernote.min.js

# Fix Nginx static path (if needed)
sed -i 's|root /var/www/hitech_ndt;|alias /var/www/hitech_ndt/staticfiles/;|' /etc/nginx/sites-available/hitechndt
sudo nginx -t && sudo systemctl reload nginx
```

## 📁 Important Paths
- **Project**: `/var/www/hitech_ndt`
- **Venv**: `/var/www/hitech_ndt/venv`
- **Static**: `/var/www/hitech_ndt/staticfiles`
- **Media**: `/var/www/hitech_ndt/media`
- **Nginx**: `/etc/nginx/sites-available/hitechndt`
- **Service**: `/etc/systemd/system/hitech-ndt.service`

## 💾 Database Info
- **Name**: hitech_ndt_db
- **User**: hitech_ndt_user
- **Password**: hitech2024
- **Port**: 5432

## 🌐 URLs
- **Website**: https://hitechndt.vn
- **Admin**: https://hitechndt.vn/admin/ 