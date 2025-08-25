# PHẦN MỀM QUẢN LÝ NỘI BỘ CHẤM CÔNG

## 1. Giới thiệu
Phần mềm này giúp quản lý nhân sự, chấm công, tính lương, xuất phiếu lương và tổng hợp chi phí cho công ty. Giao diện thân thiện, dễ sử dụng, phù hợp cho kế toán, nhân sự nội bộ.

---

## 2. Yêu cầu hệ thống
- Windows 10/11 (khuyến nghị)
- Python 3.8 – 3.12
- Đã cài đặt [PyQt5](https://pypi.org/project/PyQt5/), [matplotlib](https://pypi.org/project/matplotlib/), [pyinstaller](https://pypi.org/project/pyinstaller/)

---

## 3. Cài đặt & chạy phần mềm
### a. Nếu chạy bằng mã nguồn Python:
1. **Cài Python** (nếu chưa có): [Tải tại đây](https://www.python.org/downloads/)
2. **Cài thư viện cần thiết:**
   ```
   pip install pyqt5 matplotlib
   ```
3. **Chạy phần mềm:**
   ```
   python main.py
   ```

### b. Nếu chạy file .exe đã đóng gói:
- Chỉ cần **mở file `main.exe`** trong thư mục `dist/` (sau khi đóng gói).
- Không cần cài Python hay thư viện gì thêm.

---

## 4. Đóng gói thành file .exe (tạo file chạy độc lập)
1. **Cài PyInstaller:**
   ```
   pip install pyinstaller
   ```
2. **Chạy lệnh đóng gói:**
   ```
   pyinstaller --onefile --windowed --icon=logo_hitech.ico main.py
   ```
   - File chạy sẽ nằm trong thư mục `dist/`.
   - Đổi `logo_hitech.ico` thành icon của bạn nếu muốn.
3. **Copy các file dữ liệu cần thiết** (logo, file mẫu, v.v.) vào cùng thư mục với file `.exe` nếu cần.

---

## 5. Tạo shortcut ngoài desktop (không hiện .exe)
1. **Chuột phải vào file `main.exe` → Send to → Desktop (create shortcut) / Gửi tới → Màn hình (tạo lối tắt)**
2. **Đổi tên shortcut** thành tên bạn muốn (ví dụ: "Chấm công Hitech").
3. **Đổi icon shortcut** (chuột phải → Properties → Change Icon... → chọn icon).
4. **Shortcut sẽ không hiện đuôi .exe**.

---

## 6. Hướng dẫn sử dụng nhanh
- **Tab Quản lý con người:** Thêm/xóa/sửa nhân viên, nhập đủ thông tin.
- **Tab Quy định lương:** Thiết lập lương, phụ cấp, chức danh cho từng nhân viên.
- **Tab Bảng công tổng hợp:** Import file chấm công (CSV/JSON), xem tổng hợp ngày công, chi tiết từng ngày.
- **Tab Phiếu lương:** Chọn nhân viên, tháng, năm → Xem phiếu lương → In phiếu lương ra PNG hoặc copy hình.
- **Tab Tổng lương:** Xem tổng hợp lương, chi phí, biểu đồ lương, biểu đồ chi phí.

---

## 7. Một số lưu ý
- **Không xóa file dữ liệu mẫu** (logo, file mẫu chấm công) nếu phần mềm cần dùng.
- **Không đổi tên file .exe** nếu đã tạo shortcut, tránh lỗi shortcut.
- **Nếu không chạy được, kiểm tra lại phiên bản Python và thư viện.**
- **Nếu muốn ẩn đuôi .exe:**
  - Vào Explorer → View → Options → View → Bỏ chọn "Hiện phần mở rộng cho các loại tệp đã biết".
  - Hoặc chỉ dùng shortcut ngoài desktop.

---

## 8. Liên hệ hỗ trợ
- Nếu gặp lỗi hoặc cần hỗ trợ, liên hệ IT hoặc người phát triển phần mềm. 