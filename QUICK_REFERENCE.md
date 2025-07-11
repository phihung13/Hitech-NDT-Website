# Quick Reference - Hitech NDT Website

## 🚀 Deployment Commands

### Lần đầu deploy
```bash
sudo bash deploy.sh
```

### Update code mới
```bash
sudo bash update.sh
```

### Rollback nếu có lỗi
```bash
sudo bash rollback.sh
```

## 🔧 Service Management

### Check status
```bash
sudo systemctl status hitech-ndt
sudo systemctl status nginx
sudo systemctl status postgresql
```

### Restart services
```bash
sudo systemctl restart hitech-ndt
sudo systemctl restart nginx
```

### Enable auto-start
```bash
sudo systemctl enable hitech-ndt
sudo systemctl enable nginx
sudo systemctl enable postgresql
```

## 📊 Logs & Monitoring

### Application logs
```bash
# Real-time logs
sudo journalctl -u hitech-ndt -f

# Last 50 lines
sudo journalctl -u hitech-ndt --no-pager -n 50

# Django logs
sudo tail -f /var/log/django.log
```

### Nginx logs
```bash
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

### System resources
```bash
# CPU, Memory usage
htop

# Disk usage
df -h
du -sh /var/www/hitech_ndt/

# Network connections
ss -tulpn | grep :80
ss -tulpn | grep :443
```

## 🗃️ Database Management

### Backup database
```bash
sudo -u postgres pg_dump hitech_ndt_db > backup_$(date +%Y%m%d_%H%M%S).sql
```

### Restore database
```bash
sudo -u postgres psql hitech_ndt_db < backup_file.sql
```

### Access database
```bash
sudo -u postgres psql hitech_ndt_db
```

### Database queries
```sql
-- List all tables
\dt

-- Check database size
SELECT pg_size_pretty(pg_database_size('hitech_ndt_db'));

-- Show active connections
SELECT * FROM pg_stat_activity WHERE datname = 'hitech_ndt_db';
```

## 🔒 SSL Certificate

### Check certificate status
```bash
sudo certbot certificates
```

### Renew certificate
```bash
sudo certbot renew
```

### Test auto-renewal
```bash
sudo certbot renew --dry-run
```

## 🐛 Troubleshooting

### Website không truy cập được
```bash
# 1. Check services
sudo systemctl status hitech-ndt nginx postgresql

# 2. Check logs
sudo journalctl -u hitech-ndt --no-pager -n 20
sudo tail -20 /var/log/nginx/error.log

# 3. Test local connection
curl -I http://localhost
curl -I https://hitechndt.vn

# 4. Check ports
ss -tulpn | grep -E ':(80|443|8000)'
```

### Database connection issues
```bash
# 1. Check PostgreSQL service
sudo systemctl status postgresql

# 2. Test connection
sudo -u postgres psql -c "\l"

# 3. Check Django database settings
cd /var/www/hitech_ndt/site_hitech
source ../venv/bin/activate
python manage.py check --deploy
```

### High memory usage
```bash
# Check memory usage
free -h

# Check processes
ps aux --sort=-%mem | head -10

# Restart services if needed
sudo systemctl restart hitech-ndt
```

### Disk space issues
```bash
# Check disk usage
df -h

# Find large files
sudo find /var/log -type f -size +100M
sudo find /var/www -type f -size +100M

# Clean old logs
sudo journalctl --vacuum-time=7d
sudo find /var/log -name "*.log.*" -mtime +7 -delete
```

## 📁 Important Paths

```
/var/www/hitech_ndt/                 # Project root
/var/www/hitech_ndt/site_hitech/     # Django application
/var/www/hitech_ndt/venv/            # Virtual environment
/var/www/hitech_ndt/backups/         # Backup directory
/etc/nginx/sites-available/hitechndt.vn  # Nginx config
/etc/systemd/system/hitech-ndt.service   # Systemd service
/var/log/nginx/                      # Nginx logs
/var/log/django.log                  # Django logs
```

## 🔑 Default Credentials

- **Database User**: hitech_ndt_user
- **Database Password**: hitech2024 (change in production!)
- **Database Name**: hitech_ndt_db
- **Django Admin**: Create with `python manage.py createsuperuser`

## 🌐 URLs

- **Website**: https://hitechndt.vn
- **Admin Panel**: https://hitechndt.vn/admin/
- **API**: https://hitechndt.vn/api/

## 📞 Emergency Commands

### Stop all services
```bash
sudo systemctl stop hitech-ndt
sudo systemctl stop nginx
```

### Start all services
```bash
sudo systemctl start postgresql
sudo systemctl start hitech-ndt
sudo systemctl start nginx
```

### Complete restart
```bash
sudo systemctl restart postgresql hitech-ndt nginx
```

### Check all services
```bash
sudo systemctl is-active postgresql hitech-ndt nginx
```

---

**💡 Tip**: Bookmark this file for quick access to common commands!