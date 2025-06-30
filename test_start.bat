@echo off
REM ========================================
REM HITECH NDT - TEST LOCAL START (Windows)
REM Script khởi động tự động cho Windows
REM ========================================

title HITECH NDT - Test Local Setup
color 0A

echo.
echo =========================================
echo 🧪 HITECH NDT - TEST LOCAL SETUP
echo =========================================
echo.

REM Check if we're in the right directory
if not exist "site_hitech" (
    echo [ERROR] Không tìm thấy thư mục site_hitech!
    echo Hãy chạy script từ thư mục gốc của project
    echo Example: cd Hitech-NDT-Website ^&^& test_start.bat
    pause
    exit /b 1
)

REM Check Python
echo [INFO] Kiểm tra Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python không được cài đặt!
    echo Tải và cài Python từ https://python.org
    pause
    exit /b 1
)
echo [OK] Python detected

REM Navigate to Django project
cd site_hitech

echo [INFO] 1. Tạo virtual environment...
if exist "venv" (
    echo [WARNING] Virtual environment đã tồn tại, sử dụng lại...
) else (
    python -m venv venv
    echo [OK] Virtual environment đã tạo
)

echo [INFO] 2. Kích hoạt virtual environment...
call venv\Scripts\activate.bat
echo [OK] Virtual environment đã kích hoạt

echo [INFO] 3. Upgrade pip...
python -m pip install --upgrade pip >nul 2>&1

echo [INFO] 4. Cài đặt dependencies...
pip install -r requirements.txt >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Lỗi cài đặt dependencies!
    echo Thử chạy: pip install --user -r requirements.txt
    pause
    exit /b 1
)
echo [OK] Dependencies đã cài đặt

echo [INFO] 5. Setup database...
if exist "db.sqlite3" (
    echo [WARNING] Database đã tồn tại, skip migration...
) else (
    python manage.py migrate
    if %errorlevel% neq 0 (
        echo [ERROR] Migration thất bại!
        pause
        exit /b 1
    )
    echo [OK] Database migration thành công
)

echo [INFO] 6. Tạo superuser test...
echo from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.create_superuser('admin', 'admin@test.com', 'admin123') if not User.objects.filter(username='admin').exists() else print('Admin already exists') | python manage.py shell

echo [INFO] 7. Collect static files...
python manage.py collectstatic --noinput >nul 2>&1
echo [OK] Static files processed

echo [INFO] 8. Tạo test settings...
if not exist "site_hitech\settings_test.py" (
    (
        echo from .settings import *
        echo.
        echo # Test environment settings
        echo DEBUG = True
        echo ALLOWED_HOSTS = ['*']
        echo.
        echo # Use SQLite for testing
        echo DATABASES = {
        echo     'default': {
        echo         'ENGINE': 'django.db.backends.sqlite3',
        echo         'NAME': BASE_DIR / 'db.sqlite3',
        echo     }
        echo }
        echo.
        echo # Console email backend
        echo EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
        echo.
        echo # Disable security for local testing
        echo SECURE_SSL_REDIRECT = False
        echo SESSION_COOKIE_SECURE = False
        echo CSRF_COOKIE_SECURE = False
    ) > site_hitech\settings_test.py
    echo [OK] Test settings created
)

REM Get local IP
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /C:"IPv4"') do set LOCAL_IP=%%a
set LOCAL_IP=%LOCAL_IP: =%

echo.
echo =========================================
echo 🎉 SETUP HOÀN THÀNH!
echo =========================================
echo.
echo 📋 THÔNG TIN TRUY CẬP:
echo 🌐 Local:    http://127.0.0.1:8000
echo 🌐 Network:  http://%LOCAL_IP%:8000
echo 👤 Admin:    http://127.0.0.1:8000/admin
echo 📧 Username: admin
echo 🔑 Password: admin123
echo.
echo 📱 TEST TRÊN ĐIỆN THOẠI:
echo Kết nối cùng WiFi và truy cập: http://%LOCAL_IP%:8000
echo.
echo [WARNING] Nhấn Ctrl+C để dừng server
echo =========================================
echo.

REM Start Django server
echo [INFO] 🚀 Khởi động Django server...
set DJANGO_SETTINGS_MODULE=site_hitech.settings_test
python manage.py runserver 0.0.0.0:8000

pause 