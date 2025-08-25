from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QDateEdit, QSpinBox, QTableWidget, QTableWidgetItem,
    QPushButton, QMessageBox
)
from PyQt5.QtCore import QDate
from data_manager import DataManager

class TabNhanVien(QWidget):
    def __init__(self):
        super().__init__()
        self.data_manager = DataManager()
        self.ds_nhanvien = self.data_manager.load_nhanvien()
        self.init_ui()
        self.capnhat_bang_nv()  # Cập nhật bảng sau khi tải dữ liệu

    def init_ui(self):
        layout = QVBoxLayout()
        # Các ô nhập liệu
        form_layout1 = QHBoxLayout()
        self.inputHoTen = QLineEdit(); self.inputHoTen.setPlaceholderText("Họ và tên")
        self.inputCCCD = QLineEdit(); self.inputCCCD.setPlaceholderText("CCCD")
        self.inputMSNV = QLineEdit(); self.inputMSNV.setPlaceholderText("MSNV")
        self.inputSDT = QLineEdit(); self.inputSDT.setPlaceholderText("Số điện thoại")
        self.inputNgaySinh = QDateEdit(); self.inputNgaySinh.setDisplayFormat("d/M/yyyy")
        self.inputQueQuan = QLineEdit(); self.inputQueQuan.setPlaceholderText("Quê quán")
        form_layout1.addWidget(self.inputHoTen)
        form_layout1.addWidget(self.inputCCCD)
        form_layout1.addWidget(self.inputMSNV)
        form_layout1.addWidget(self.inputSDT)
        form_layout1.addWidget(self.inputNgaySinh)
        form_layout1.addWidget(self.inputQueQuan)

        form_layout2 = QHBoxLayout()
        self.inputChucVu = QLineEdit(); self.inputChucVu.setPlaceholderText("Chức vụ")
        self.inputPhongBan = QLineEdit(); self.inputPhongBan.setPlaceholderText("Phòng ban")
        self.inputTrinhDo = QLineEdit(); self.inputTrinhDo.setPlaceholderText("Trình độ học vấn")
        self.inputChungNhan = QLineEdit(); self.inputChungNhan.setPlaceholderText("Chứng nhận có được")
        self.inputNguoiPhuThuoc = QSpinBox(); self.inputNguoiPhuThuoc.setRange(0, 20)
        self.inputNguoiPhuThuoc.setPrefix("Số người phụ thuộc: ")
        self.inputSTK = QLineEdit(); self.inputSTK.setPlaceholderText("STK ngân hàng")
        self.inputNganHang = QLineEdit(); self.inputNganHang.setPlaceholderText("Ngân hàng")
        form_layout2.addWidget(self.inputChucVu)
        form_layout2.addWidget(self.inputPhongBan)
        form_layout2.addWidget(self.inputTrinhDo)
        form_layout2.addWidget(self.inputChungNhan)
        form_layout2.addWidget(self.inputNguoiPhuThuoc)
        form_layout2.addWidget(self.inputSTK)
        form_layout2.addWidget(self.inputNganHang)

        layout.addLayout(form_layout1)
        layout.addLayout(form_layout2)

        # Bảng nhân viên
        self.tableNhanVien = QTableWidget(0, 13)
        self.tableNhanVien.setHorizontalHeaderLabels([
            "Họ và tên", "CCCD", "MSNV", "Số điện thoại", "Ngày sinh", "Quê quán",
            "Chức vụ", "Phòng ban", "Trình độ học vấn", "Chứng nhận có được", "Số người phụ thuộc",
            "STK ngân hàng", "Ngân hàng"
        ])
        layout.addWidget(self.tableNhanVien)

        # Các nút thao tác
        btn_layout = QHBoxLayout()
        self.btnThemNV = QPushButton("Thêm")
        self.btnSuaNV = QPushButton("Sửa")
        self.btnXoaNV = QPushButton("Xóa")
        btn_layout.addWidget(self.btnThemNV)
        btn_layout.addWidget(self.btnSuaNV)
        btn_layout.addWidget(self.btnXoaNV)
        layout.addLayout(btn_layout)

        self.setLayout(layout)

        # Kết nối sự kiện
        self.btnThemNV.clicked.connect(self.them_nhanvien)
        self.btnXoaNV.clicked.connect(self.xoa_nhanvien)
        self.btnSuaNV.clicked.connect(self.sua_nhanvien)
        self.tableNhanVien.cellClicked.connect(self.hien_thi_nhanvien)

    def them_nhanvien(self):
        """Thêm nhân viên mới"""
        try:
            # Lấy thông tin từ các input
            ho_ten = self.inputHoTen.text().strip()
            cccd = self.inputCCCD.text().strip()
            msnv = self.inputMSNV.text().strip()
            sdt = self.inputSDT.text().strip()
            ngay_sinh = self.inputNgaySinh.text().strip()
            que_quan = self.inputQueQuan.text().strip()
            chuc_vu = self.inputChucVu.text().strip()
            phong_ban = self.inputPhongBan.text().strip()
            trinh_do = self.inputTrinhDo.text().strip()
            chung_chi = self.inputChungNhan.text().strip()
            trang_thai = self.inputNguoiPhuThuoc.value() # Assuming inputNguoiPhuThuoc is the correct one for this
            stk = self.inputSTK.text().strip()
            ngan_hang = self.inputNganHang.text().strip()
            
            # Kiểm tra dữ liệu bắt buộc
            if not ho_ten or not cccd or not msnv:
                QMessageBox.warning(self, "Cảnh báo", "Vui lòng nhập đầy đủ thông tin bắt buộc!")
                return
            
            # Kiểm tra trùng lặp
            for row in range(self.tableNhanVien.rowCount()):
                item_msnv = self.tableNhanVien.item(row, 2)  # Cột MSNV
                if item_msnv and item_msnv.text() == msnv:
                    QMessageBox.warning(self, "Cảnh báo", "MSNV đã tồn tại!")
                    return
            
            # Thêm vào bảng
            row = self.tableNhanVien.rowCount()
            self.tableNhanVien.insertRow(row)
            
            self.tableNhanVien.setItem(row, 0, QTableWidgetItem(ho_ten))
            self.tableNhanVien.setItem(row, 1, QTableWidgetItem(cccd))
            self.tableNhanVien.setItem(row, 2, QTableWidgetItem(msnv))
            self.tableNhanVien.setItem(row, 3, QTableWidgetItem(sdt))
            self.tableNhanVien.setItem(row, 4, QTableWidgetItem(ngay_sinh))
            self.tableNhanVien.setItem(row, 5, QTableWidgetItem(que_quan))
            self.tableNhanVien.setItem(row, 6, QTableWidgetItem(chuc_vu))
            self.tableNhanVien.setItem(row, 7, QTableWidgetItem(phong_ban))
            self.tableNhanVien.setItem(row, 8, QTableWidgetItem(trinh_do))
            self.tableNhanVien.setItem(row, 9, QTableWidgetItem(chung_chi))
            self.tableNhanVien.setItem(row, 10, QTableWidgetItem(trang_thai))
            self.tableNhanVien.setItem(row, 11, QTableWidgetItem(stk))
            self.tableNhanVien.setItem(row, 12, QTableWidgetItem(ngan_hang))
            
            # Xóa dữ liệu input
            self.clear_inputs()
            
            # Auto-save dữ liệu
            self.auto_save_data()
            
            QMessageBox.information(self, "Thành công", "Đã thêm nhân viên mới!")
            
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Không thể thêm nhân viên: {str(e)}")
    
    def auto_save_data(self):
        """Tự động lưu dữ liệu"""
        try:
            # Thu thập dữ liệu từ bảng
            data = []
            for row in range(self.tableNhanVien.rowCount()):
                row_data = []
                for col in range(self.tableNhanVien.columnCount()):
                    item = self.tableNhanVien.item(row, col)
                    row_data.append(item.text() if item else "")
                if any(cell.strip() for cell in row_data):  # Chỉ lưu dòng có dữ liệu
                    data.append(row_data)
            
            # Lưu vào file
            self.data_manager.save_nhanvien(data)
            print("Đã tự động lưu dữ liệu nhân viên")
            
        except Exception as e:
            print(f"Lỗi tự động lưu dữ liệu nhân viên: {str(e)}")

    def xoa_nhanvien(self):
        """Xóa nhân viên được chọn"""
        try:
            current_row = self.tableNhanVien.currentRow()
            if current_row >= 0:
                # Lấy tên nhân viên để hiển thị
                item = self.tableNhanVien.item(current_row, 0)
                ten_nv = item.text() if item else "Nhân viên"
                
                # Xác nhận xóa
                reply = QMessageBox.question(
                    self, "Xác nhận xóa", 
                    f"Bạn có chắc muốn xóa nhân viên '{ten_nv}'?",
                    QMessageBox.Yes | QMessageBox.No, QMessageBox.No
                )
                
                if reply == QMessageBox.Yes:
                    self.tableNhanVien.removeRow(current_row)
                    
                    # Auto-save dữ liệu
                    self.auto_save_data()
                    
                    QMessageBox.information(self, "Thành công", f"Đã xóa nhân viên '{ten_nv}'!")
            else:
                QMessageBox.warning(self, "Cảnh báo", "Vui lòng chọn nhân viên cần xóa!")
                
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Không thể xóa nhân viên: {str(e)}")

    def sua_nhanvien(self):
        dong = self.tableNhanVien.currentRow()
        if dong >= 0:
            nv = [
                self.inputHoTen.text().strip(),
                self.inputCCCD.text().strip(),
                self.inputMSNV.text().strip(),
                self.inputSDT.text().strip(),
                self.inputNgaySinh.text(),
                self.inputQueQuan.text().strip(),
                self.inputChucVu.text().strip(),
                self.inputPhongBan.text().strip(),
                self.inputTrinhDo.text().strip(),
                self.inputChungNhan.text().strip(),
                str(self.inputNguoiPhuThuoc.value()),
                self.inputSTK.text().strip(),
                self.inputNganHang.text().strip()
            ]
            if not nv[0] or not nv[2]:
                QMessageBox.warning(self, "Thiếu thông tin", "Vui lòng nhập đầy đủ Họ tên và MSNV.")
                return
            self.ds_nhanvien[dong] = nv
            self.capnhat_bang_nv()
            # Lưu dữ liệu
            self.data_manager.save_nhanvien(self.ds_nhanvien)
        else:
            QMessageBox.warning(self, "Chưa chọn", "Vui lòng chọn nhân viên để sửa.")

    def hien_thi_nhanvien(self, row, col):
        nv = self.ds_nhanvien[row]
        self.inputHoTen.setText(nv[0])
        self.inputCCCD.setText(nv[1])
        self.inputMSNV.setText(nv[2])
        self.inputSDT.setText(nv[3])
        self.inputNgaySinh.setDate(QDate.fromString(nv[4], "d/M/yyyy"))
        self.inputQueQuan.setText(nv[5])
        self.inputChucVu.setText(nv[6])
        self.inputPhongBan.setText(nv[7])
        self.inputTrinhDo.setText(nv[8])
        self.inputChungNhan.setText(nv[9])
        self.inputNguoiPhuThuoc.setValue(int(nv[10]))
        self.inputSTK.setText(nv[11])
        self.inputNganHang.setText(nv[12])

    def capnhat_bang_nv(self):
        self.tableNhanVien.setRowCount(0)
        for nv in self.ds_nhanvien:
            row = self.tableNhanVien.rowCount()
            self.tableNhanVien.insertRow(row)
            for col, val in enumerate(nv):
                self.tableNhanVien.setItem(row, col, QTableWidgetItem(val))

    def clear_inputs(self):
        """Xóa dữ liệu trong các input"""
        self.inputHoTen.clear()
        self.inputCCCD.clear()
        self.inputMSNV.clear()
        self.inputSDT.clear()
        self.inputNgaySinh.clear()
        self.inputQueQuan.clear()
        self.inputChucVu.clear()
        self.inputPhongBan.clear()
        self.inputTrinhDo.clear()
        self.inputChungNhan.clear()
        self.inputNguoiPhuThuoc.setValue(0)
        self.inputSTK.clear()
        self.inputNganHang.clear()

    def refresh_data(self):
        """Tự động cập nhật dữ liệu khi có thay đổi"""
        try:
            print("Đang cập nhật dữ liệu nhân viên...")
            
            # Reload dữ liệu từ data manager
            self.ds_nhanvien = self.data_manager.load_nhanvien()
            
            # Refresh bảng
            self.capnhat_bang_nv()
            
            print("Đã cập nhật xong dữ liệu nhân viên")
            
        except Exception as e:
            print(f"Lỗi cập nhật dữ liệu nhân viên: {e}") 