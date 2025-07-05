# 🔧 Hướng dẫn sử dụng SiteSettings (Cấu hình chung website)

## 📝 Mô tả
SiteSettings giờ đây chỉ quản lý các thông tin chung của website như navbar, footer, logo công ty, màu sắc cơ bản và thông tin liên hệ. Các trang riêng biệt như trang chủ, giới thiệu sẽ có model cấu hình riêng.

## 🏗️ Cấu trúc mới

### 🏢 Thông tin công ty & Logo
- **Logo công ty**: Hiển thị trên navbar
- **Tên công ty**: Hitech NDT
- **Slogan**: Câu slogan chính
- **Mô tả**: Giới thiệu ngắn về công ty

### 🧭 Navbar (Menu điều hướng)
- Màu nền, màu chữ
- Kích thước font
- Tùy chọn sticky navbar

### 🦶 Footer (Chân trang)
- Màu nền, màu chữ, màu liên kết
- Bản quyền footer
- Thông tin liên hệ (địa chỉ, phone, email)

### 🌐 Mạng xã hội
- Facebook, LinkedIn, YouTube, Twitter
- Số Zalo

### 🎨 Màu sắc chung
- Primary, Secondary, Success, Warning, Danger
- Áp dụng cho các trang chưa có cấu hình riêng

### 🔍 SEO chung
- Meta title, description, keywords mặc định
- Các trang riêng có thể ghi đè

### 📞 Liên hệ nhanh (Floating)
- Nút floating ở góc màn hình
- Phone và Zalo liên hệ nhanh

## 🚀 Cách sử dụng

1. **Truy cập admin**: `/admin/api/sitesettings/`
2. **Chỉnh sửa**: Chỉ có 1 bản ghi duy nhất
3. **Cập nhật**: Lưu để áp dụng toàn website

## 🗂️ Phân biệt với các model khác

- **SiteSettings**: Cấu hình chung (navbar, footer, colors, logo)
- **HomePageSettings**: Cấu hình riêng cho trang chủ
- **AboutPage**: Cấu hình riêng cho trang giới thiệu
- **ContactSettings**: Cấu hình riêng cho trang liên hệ

## 🔄 Migration đã thực hiện

Đã xóa các field không cần thiết:
- Hero section (chuyển về HomePageSettings)
- Services section (chuyển về HomePageSettings)
- About section (chuyển về AboutPage)
- Projects section (chuyển về HomePageSettings)
- Testimonials section (chuyển về HomePageSettings)
- Client logos (chuyển về HomePageSettings)

Thêm các field mới:
- Màu sắc chung website
- Typography settings
- SEO chung
- Floating contact
- Navbar sticky option

## ✅ Lợi ích của cấu trúc mới

1. **Tách biệt rõ ràng**: Mỗi model có trách nhiệm riêng
2. **Dễ quản lý**: Admin interface gọn gàng, tập trung
3. **Linh hoạt**: Các trang có thể tùy chỉnh riêng
4. **SEO tốt**: Meta tags riêng cho từng trang
5. **Maintainable**: Code dễ bảo trì và mở rộng 