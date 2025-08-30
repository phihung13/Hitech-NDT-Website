from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QDateEdit, QSpinBox, QTableWidget, QTableWidgetItem,
    QPushButton, QMessageBox, QComboBox, QDialog, QFormLayout, QLabel
)
from PyQt5.QtCore import QDate
from PyQt5.QtGui import QFont
from data_manager import DataManager
import json
import os

class ChucVuDialog(QDialog):
    def __init__(self, parent=None, current_chuc_vu=None):
        super().__init__(parent)
        self.setWindowTitle("Quản lý chức vụ")
        self.setModal(True)
        self.setFixedSize(400, 300)
        self.current_chuc_vu = current_chuc_vu or []
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Tiêu đề
        title = QLabel("Quản lý danh sách chức vụ:")
        title.setFont(QFont("Times New Roman", 12, QFont.Bold))
        layout.addWidget(title)
        
        # List chức vụ hiện có
        self.combo_chuc_vu = QComboBox()
        self.combo_chuc_vu.addItems(self.current_chuc_vu)
        layout.addWidget(self.combo_chuc_vu)
        
        # Input thêm chức vụ mới
        self.input_chuc_vu_moi = QLineEdit()
        self.input_chuc_vu_moi.setPlaceholderText("Nhập chức vụ mới...")
        layout.addWidget(self.input_chuc_vu_moi)
        
        # Buttons
        btn_layout = QHBoxLayout()
        
        self.btn_them = QPushButton("➕ Thêm")
        self.btn_them.clicked.connect(self.them_chuc_vu)
        
        self.btn_xoa = QPushButton("🗑️ Xóa")
        self.btn_xoa.clicked.connect(self.xoa_chuc_vu)
        
        self.btn_ok = QPushButton("OK")
        self.btn_ok.clicked.connect(self.accept)
        
        self.btn_cancel = QPushButton("Hủy")
        self.btn_cancel.clicked.connect(self.reject)
        
        btn_layout.addWidget(self.btn_them)
        btn_layout.addWidget(self.btn_xoa)
        btn_layout.addWidget(self.btn_ok)
        btn_layout.addWidget(self.btn_cancel)
        
        layout.addLayout(btn_layout)
        self.setLayout(layout)
    
    def them_chuc_vu(self):
        chuc_vu_moi = self.input_chuc_vu_moi.text().strip()
        if chuc_vu_moi and chuc_vu_moi not in self.current_chuc_vu:
            self.current_chuc_vu.append(chuc_vu_moi)
            self.combo_chuc_vu.addItem(chuc_vu_moi)
            self.input_chuc_vu_moi.clear()
    
    def xoa_chuc_vu(self):
        current_text = self.combo_chuc_vu.currentText()
        if current_text in self.current_chuc_vu:
            self.current_chuc_vu.remove(current_text)
            self.combo_chuc_vu.removeItem(self.combo_chuc_vu.currentIndex())
    
    def get_chuc_vu_list(self):
        return self.current_chuc_vu

class TabNhanVien(QWidget):
    def __init__(self, on_nhanvien_changed=None):
        super().__init__()
        self.data_manager = DataManager()
        self.ds_nhanvien = self.data_manager.load_nhanvien()
        self.on_nhanvien_changed = on_nhanvien_changed  # Callback khi có thay đổi nhân viên
        
        # Danh sách chức vụ mặc định
        self.default_chuc_vu = [
            "Technical Manager",
            "Site Manager", 
            "NDT Team Leader",
            "Technician",
            "R&D Technician"
        ]
        
        # Danh sách tỉnh thành Việt Nam
        self.tinh_thanh_vn = [
            "An Giang", "Bà Rịa - Vũng Tàu", "Bắc Giang", "Bắc Kạn", "Bạc Liêu",
            "Bắc Ninh", "Bến Tre", "Bình Định", "Bình Dương", "Bình Phước",
            "Bình Thuận", "Cà Mau", "Cao Bằng", "Đắk Lắk", "Đắk Nông",
            "Điện Biên", "Đồng Nai", "Đồng Tháp", "Gia Lai", "Hà Giang",
            "Hà Nam", "Hà Tĩnh", "Hải Dương", "Hậu Giang", "Hòa Bình",
            "Hưng Yên", "Khánh Hòa", "Kiên Giang", "Kon Tum", "Lai Châu",
            "Lâm Đồng", "Lạng Sơn", "Lào Cai", "Long An", "Nam Định",
            "Nghệ An", "Ninh Bình", "Ninh Thuận", "Phú Thọ", "Quảng Bình",
            "Quảng Nam", "Quảng Ngãi", "Quảng Ninh", "Quảng Trị", "Sóc Trăng",
            "Sơn La", "Tây Ninh", "Thái Bình", "Thái Nguyên", "Thanh Hóa",
            "Thừa Thiên Huế", "Tiền Giang", "Trà Vinh", "Tuyên Quang", "Vĩnh Long",
            "Vĩnh Phúc", "Yên Bái", "Phú Yên", "Cần Thơ", "Đà Nẵng",
            "Hải Phòng", "Hà Nội", "TP Hồ Chí Minh"
        ]
        
        # Load danh sách chức vụ tùy chỉnh
        self.chuc_vu_list = self.load_chuc_vu_list()
        
        self.init_ui()
        self.capnhat_bang_nv()  # Cập nhật bảng sau khi tải dữ liệu

    def load_chuc_vu_list(self):
        """Load danh sách chức vụ từ file"""
        try:
            chuc_vu_file = "data/chuc_vu_list.json"
            if os.path.exists(chuc_vu_file):
                with open(chuc_vu_file, 'r', encoding='utf-8') as f:
                    custom_list = json.load(f)
                    return self.default_chuc_vu + custom_list
            return self.default_chuc_vu.copy()
        except:
            return self.default_chuc_vu.copy()
    
    def save_chuc_vu_list(self):
        """Save danh sách chức vụ tùy chỉnh"""
        try:
            custom_list = [cv for cv in self.chuc_vu_list if cv not in self.default_chuc_vu]
            chuc_vu_file = "data/chuc_vu_list.json"
            os.makedirs(os.path.dirname(chuc_vu_file), exist_ok=True)
            with open(chuc_vu_file, 'w', encoding='utf-8') as f:
                json.dump(custom_list, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Lỗi lưu danh sách chức vụ: {e}")

    def init_ui(self):
        layout = QVBoxLayout()
        # Các ô nhập liệu
        form_layout1 = QHBoxLayout()
        self.inputHoTen = QLineEdit(); self.inputHoTen.setPlaceholderText("Họ và tên")
        self.inputCCCD = QLineEdit(); self.inputCCCD.setPlaceholderText("CCCD")
        self.inputMSNV = QLineEdit(); self.inputMSNV.setPlaceholderText("MSNV")
        self.inputSDT = QLineEdit(); self.inputSDT.setPlaceholderText("Số điện thoại")
        self.inputNgaySinh = QDateEdit(); self.inputNgaySinh.setDisplayFormat("d/M/yyyy")
        self.inputQueQuan = QComboBox(); 
        self.inputQueQuan.addItem("Chọn tỉnh thành...")
        self.inputQueQuan.addItems(self.tinh_thanh_vn)
        self.inputQueQuan.setEditable(True)
        form_layout1.addWidget(self.inputHoTen)
        form_layout1.addWidget(self.inputCCCD)
        form_layout1.addWidget(self.inputMSNV)
        form_layout1.addWidget(self.inputSDT)
        form_layout1.addWidget(self.inputNgaySinh)
        form_layout1.addWidget(self.inputQueQuan)

        form_layout2 = QHBoxLayout()
        self.inputChucVu = QComboBox()
        self.inputChucVu.addItem("Chọn chức vụ...")
        self.inputChucVu.addItems(self.chuc_vu_list)
        self.inputChucVu.setEditable(True)
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
        self.btnQuanLyChucVu = QPushButton("🏷️ Quản lý chức vụ")
        btn_layout.addWidget(self.btnThemNV)
        btn_layout.addWidget(self.btnSuaNV)
        btn_layout.addWidget(self.btnXoaNV)
        btn_layout.addWidget(self.btnQuanLyChucVu)
        layout.addLayout(btn_layout)

        self.setLayout(layout)

        # Kết nối sự kiện
        self.btnThemNV.clicked.connect(self.them_nhanvien)
        self.btnXoaNV.clicked.connect(self.xoa_nhanvien)
        self.btnSuaNV.clicked.connect(self.sua_nhanvien)
        self.btnQuanLyChucVu.clicked.connect(self.quan_ly_chuc_vu)
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
            que_quan = self.inputQueQuan.currentText().strip()
            if que_quan == "Chọn tỉnh thành...":
                que_quan = ""
            chuc_vu = self.inputChucVu.currentText().strip()
            if chuc_vu == "Chọn chức vụ...":
                chuc_vu = ""
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
            
            # Thông báo cho các tab khác cập nhật (quan trọng!)
            if self.on_nhanvien_changed:
                self.on_nhanvien_changed()
                print("Đã thông báo cập nhật cho tab quy định lương")
            
        except Exception as e:
            print(f"Lỗi tự động lưu dữ liệu nhân viên: {str(e)}")

    def quan_ly_chuc_vu(self):
        """Mở dialog quản lý chức vụ"""
        dialog = ChucVuDialog(self, self.chuc_vu_list.copy())
        if dialog.exec_() == QDialog.Accepted:
            # Cập nhật danh sách chức vụ
            self.chuc_vu_list = dialog.get_chuc_vu_list()
            self.save_chuc_vu_list()
            
            # Cập nhật combo box
            current_text = self.inputChucVu.currentText()
            self.inputChucVu.clear()
            self.inputChucVu.addItem("Chọn chức vụ...")
            self.inputChucVu.addItems(self.chuc_vu_list)
            
            # Giữ lại lựa chọn hiện tại nếu có
            if current_text in self.chuc_vu_list:
                self.inputChucVu.setCurrentText(current_text)

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
                self.inputQueQuan.currentText().strip() if self.inputQueQuan.currentText() != "Chọn tỉnh thành..." else "",
                self.inputChucVu.currentText().strip() if self.inputChucVu.currentText() != "Chọn chức vụ..." else "",
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
            
            # Thông báo cho các tab khác cập nhật
            if self.on_nhanvien_changed:
                self.on_nhanvien_changed()
                print("Đã thông báo cập nhật cho tab quy định lương")
        else:
            QMessageBox.warning(self, "Chưa chọn", "Vui lòng chọn nhân viên để sửa.")

    def hien_thi_nhanvien(self, row, col):
        try:
            # Kiểm tra row có hợp lệ không
            if row < 0 or row >= len(self.ds_nhanvien):
                print(f"Lỗi: Row {row} không hợp lệ, tổng số nhân viên: {len(self.ds_nhanvien)}")
                return
            
            nv = self.ds_nhanvien[row]
            
            # Kiểm tra nv có đủ phần tử không
            if len(nv) < 13:
                print(f"Lỗi: Nhân viên tại row {row} không đủ thông tin, chỉ có {len(nv)} phần tử")
                return
            
            # Hiển thị thông tin nhân viên với kiểm tra an toàn
            self.inputHoTen.setText(str(nv[0]) if nv[0] else "")
            self.inputCCCD.setText(str(nv[1]) if nv[1] else "")
            self.inputMSNV.setText(str(nv[2]) if nv[2] else "")
            self.inputSDT.setText(str(nv[3]) if nv[3] else "")
            
            # Xử lý ngày sinh an toàn
            try:
                if nv[4]:
                    self.inputNgaySinh.setDate(QDate.fromString(str(nv[4]), "d/M/yyyy"))
                else:
                    self.inputNgaySinh.clear()
            except:
                self.inputNgaySinh.clear()
            
            # Set combo box cho quê quán
            que_quan = str(nv[5]) if nv[5] else ""
            if que_quan in self.tinh_thanh_vn:
                self.inputQueQuan.setCurrentText(que_quan)
            else:
                self.inputQueQuan.setEditText(que_quan)
            
            # Set combo box cho chức vụ
            chuc_vu = str(nv[6]) if nv[6] else ""
            if chuc_vu in self.chuc_vu_list:
                self.inputChucVu.setCurrentText(chuc_vu)
            else:
                self.inputChucVu.setEditText(chuc_vu)
            
            self.inputPhongBan.setText(str(nv[7]) if nv[7] else "")
            self.inputTrinhDo.setText(str(nv[8]) if nv[8] else "")
            self.inputChungNhan.setText(str(nv[9]) if nv[9] else "")
            
            # Xử lý số người phụ thuộc an toàn
            try:
                nguoi_phu_thuoc = int(nv[10]) if nv[10] else 0
                self.inputNguoiPhuThuoc.setValue(nguoi_phu_thuoc)
            except:
                self.inputNguoiPhuThuoc.setValue(0)
            
            self.inputSTK.setText(str(nv[11]) if nv[11] else "")
            self.inputNganHang.setText(str(nv[12]) if nv[12] else "")
            
        except Exception as e:
            print(f"Lỗi khi hiển thị thông tin nhân viên tại row {row}: {str(e)}")
            QMessageBox.warning(self, "Lỗi", f"Không thể hiển thị thông tin nhân viên: {str(e)}")

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
        self.inputQueQuan.setCurrentIndex(0)  # Reset về "Chọn tỉnh thành..."
        self.inputChucVu.setCurrentIndex(0)  # Reset về "Chọn chức vụ..."
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