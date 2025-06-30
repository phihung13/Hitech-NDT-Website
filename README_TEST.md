# 🧪 HƯỚNG DẪN KHỞI ĐỘNG TEST LOCAL

> Hướng dẫn setup nhanh website Hitech NDT trên máy local để test
README_TEST.md - Hướng dẫn chi tiết
test_start.sh - Script Linux/Mac
test_start.bat - Script Windows

## 📋 YÊU CẦU TỐI THIỂU
- Python 3.8+ 
- Git
- Internet connection

## ⚡ KHỞI ĐỘNG NHANH (3 PHÚT)

### 1️⃣ Clone project
```bash
git clone https://github.com/phihung13/Hitech-NDT-Website.git
cd Hitech-NDT-Website
```

### 2️⃣ Chạy script auto
```bash
chmod +x test_start.sh
./test_start.sh
```

**🎉 Xong! Website chạy tại http://127.0.0.1:8000**

---

## 🔧 SETUP THỦ CÔNG

### Bước 1: Virtual Environment
```bash
cd site_hitech
python3 -m venv venv

# Linux/Mac
source venv/bin/activate

# Windows
venv\Scripts\activate
```

### Bước 2: Cài Dependencies
```bash
pip install -r requirements.txt
```

### Bước 3: Setup Database (SQLite)
```bash
python manage.py migrate
```

### Bước 4: Tạo Admin User
```bash
python manage.py createsuperuser
# Hoặc dùng user test có sẵn (bước 5)
```

### Bước 5: Load Data Test (Optional)
```bash
python manage.py shell
```
```python
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@test.com', 'admin123')
    print("✅ Admin user created: admin/admin123")
exit()
```

### Bước 6: Chạy Server
```bash
python manage.py runserver
```

---

## 🌐 TRUY CẬP WEBSITE

- **Trang chủ:** http://127.0.0.1:8000/
- **Admin Panel:** http://127.0.0.1:8000/admin/
- **Login:** admin / admin123

---

## 🛠️ LỆNH THƯỜNG DÙNG

```bash
# Tạo migration khi thay đổi model
python manage.py makemigrations

# Apply migration
python manage.py migrate

# Reset database
rm db.sqlite3
python manage.py migrate

# Collect static files (nếu lỗi CSS)
python manage.py collectstatic

# Chạy shell Django để test code
python manage.py shell
```

---

## 📱 TEST TRÊN CÁC THIẾT BỊ

### Truy cập từ điện thoại/máy khác trong cùng mạng:
```bash
# Tìm IP máy tính
ipconfig      # Windows
ifconfig      # Linux/Mac

# Chạy server với IP cụ thể
python manage.py runserver 0.0.0.0:8000

# Truy cập từ thiết bị khác: http://IP_MÁY_TÍNH:8000
```

---

## 🔥 CÁC TÍNH NĂNG TEST

### ✅ Tính năng hoạt động:
- Trang chủ với hero section
- Blog system (tạo, sửa, xóa bài viết)
- Dịch vụ/khóa học
- Trang giới thiệu
- Liên hệ
- Admin panel đầy đủ
- Responsive design
- Multi-language (VI/EN)

### ✅ Admin features:
- Quản lý bài viết
- Quản lý dịch vụ
- Quản lý user
- Upload hình ảnh
- SEO settings

---

## 🚨 TROUBLESHOOTING

### Lỗi Python không tìm thấy:
```bash
# Kiểm tra Python
python3 --version
which python3

# Install Python (Ubuntu)
sudo apt install python3 python3-pip python3-venv
```

### Lỗi pip install:
```bash
# Upgrade pip
pip install --upgrade pip

# Install với user flag
pip install --user -r requirements.txt
```

### Lỗi port đã sử dụng:
```bash
# Chạy trên port khác
python manage.py runserver 8001
```

### Lỗi static files:
```bash
python manage.py collectstatic --clear
# Hoặc
rm -rf staticfiles/
```

### Reset hoàn toàn:
```bash
rm -rf venv/ db.sqlite3 staticfiles/
# Chạy lại từ đầu
```

---

## 📋 CHECKLIST TEST

- [ ] Clone project thành công
- [ ] Virtual environment hoạt động
- [ ] Dependencies cài đặt OK
- [ ] Database migrate thành công  
- [ ] Admin user tạo được
- [ ] Server chạy không lỗi
- [ ] Truy cập trang chủ OK
- [ ] Login admin panel OK
- [ ] Tạo bài viết test OK
- [ ] Upload hình ảnh OK
- [ ] Responsive trên mobile OK

---

## 💡 GHI CHÚ

- **Database:** SQLite (file db.sqlite3) - không cần cài PostgreSQL
- **Media files:** Lưu trong thư mục `media/`
- **Static files:** Auto collect khi chạy `collectstatic`
- **Debug:** Luôn bật cho môi trường test
- **Email:** Console backend (email hiển thị trong terminal)

**🎯 Mục tiêu:** Ai cũng có thể chạy website trong 3-5 phút! 