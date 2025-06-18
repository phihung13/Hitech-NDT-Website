# Hitech-NDT-Website

Website cho công ty Hitech NDT sử dụng Django framework.

## Cài đặt và Phát triển

### Yêu cầu

- Python 3.11+
- pip (Python package manager)

### Cài đặt môi trường phát triển

1. Clone repository:
   ```
   git clone <repository-url>
   cd Hitech-NDT-Website
   ```

2. Cài đặt các thư viện cần thiết:
   ```
   pip install -r requirements.txt
   ```

3. Tạo và áp dụng migrations:
   ```
   cd site_hitech
   python manage.py makemigrations
   python manage.py migrate
   ```

4. Tạo tài khoản admin:
   ```
   python manage.py createsuperuser
   ```

5. Chạy server phát triển:
   ```
   python manage.py runserver
   ```

## Triển khai lên Hosting

### Chuẩn bị triển khai

1. Cập nhật file `.env` với các thông tin cấu hình cho môi trường production:
   - Đặt `DEBUG=False`
   - Cập nhật `ALLOWED_HOSTS` với tên miền của bạn
   - Cấu hình thông tin database
   - Đảm bảo `SECRET_KEY` được thay đổi và giữ bí mật

2. Cài đặt các thư viện cần thiết cho production:
   ```
   pip install gunicorn whitenoise daphne
   ```

### Triển khai lên shared hosting (cPanel)

1. Tải mã nguồn lên hosting sử dụng FTP hoặc Git

2. Tạo môi trường ảo Python và cài đặt các thư viện:
   ```
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. Cấu hình database trên cPanel và cập nhật thông tin trong file `.env`

4. Chạy migrations và thu thập static files:
   ```
   python manage.py migrate
   python manage.py collectstatic
   ```

5. Cấu hình WSGI/ASGI trong cPanel để trỏ đến file wsgi.py/asgi.py của dự án

### Triển khai lên VPS/Cloud Server

1. Cài đặt Nginx làm reverse proxy:
   ```
   sudo apt update
   sudo apt install nginx
   ```

2. Cấu hình Nginx để phục vụ ứng dụng Django:
   ```
   # /etc/nginx/sites-available/hitech-ndt
   server {
       listen 80;
       server_name yourdomain.com www.yourdomain.com;

       location /static/ {
           alias /path/to/Hitech-NDT-Website/site_hitech/staticfiles/;
       }

       location /media/ {
           alias /path/to/Hitech-NDT-Website/site_hitech/media/;
       }

       location / {
           proxy_pass http://127.0.0.1:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```

3. Kích hoạt cấu hình Nginx:
   ```
   sudo ln -s /etc/nginx/sites-available/hitech-ndt /etc/nginx/sites-enabled/
   sudo nginx -t
   sudo systemctl restart nginx
   ```

4. Cài đặt và cấu hình Supervisor để quản lý quy trình Gunicorn:
   ```
   sudo apt install supervisor
   ```

5. Tạo file cấu hình Supervisor:
   ```
   # /etc/supervisor/conf.d/hitech-ndt.conf
   [program:hitech-ndt]
   command=/path/to/venv/bin/gunicorn site_hitech.wsgi:application --workers 3 --bind 127.0.0.1:8000
   directory=/path/to/Hitech-NDT-Website/site_hitech
   autostart=true
   autorestart=true
   stderr_logfile=/var/log/hitech-ndt.err.log
   stdout_logfile=/var/log/hitech-ndt.out.log
   user=your_user
   ```

6. Khởi động Supervisor:
   ```
   sudo supervisorctl reread
   sudo supervisorctl update
   sudo supervisorctl start hitech-ndt
   ```

## Cấu hình tên miền

1. Đăng ký tên miền với nhà cung cấp tên miền (VD: PA Việt Nam, Vietnix, VinaHost, Nhân Hòa)

2. Trỏ tên miền về hosting bằng cách cập nhật DNS:
   - Nếu sử dụng shared hosting: Cập nhật nameserver theo hướng dẫn của nhà cung cấp hosting
   - Nếu sử dụng VPS/Cloud Server: Tạo bản ghi A trỏ đến địa chỉ IP của server

3. Cấu hình SSL cho tên miền:
   - Với shared hosting: Sử dụng tính năng Let's Encrypt trong cPanel
   - Với VPS/Cloud Server: Sử dụng Certbot để cài đặt Let's Encrypt
     ```
     sudo apt install certbot python3-certbot-nginx
     sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
     ```

## Bảo trì và cập nhật

1. Cập nhật mã nguồn:
   ```
   git pull
   ```

2. Cập nhật dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Áp dụng migrations mới:
   ```
   python manage.py migrate
   ```

4. Thu thập static files mới:
   ```
   python manage.py collectstatic
   ```

5. Khởi động lại ứng dụng:
   - Shared hosting: Khởi động lại ứng dụng qua cPanel
   - VPS/Cloud Server: `sudo supervisorctl restart hitech-ndt`