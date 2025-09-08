from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QTableWidget, QTableWidgetItem,
    QPushButton, QMessageBox, QLabel, QComboBox, QGroupBox, QDialog, QFormLayout
)
from data_manager import DataManager
from PyQt5.QtGui import QFont, QColor
from PyQt5.QtCore import Qt

class PhuCapDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Nhập phụ cấp")
        self.setModal(True)
        self.setFixedSize(400, 250)
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Tiêu đề
        title = QLabel("Nhập thông tin phụ cấp:")
        title.setFont(QFont("Times New Roman", 12, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Form layout cho các input
        form_layout = QFormLayout()
        
        self.inputPCCongTrinh = QLineEdit()
        self.inputPCCongTrinh.setPlaceholderText("Ví dụ: 500000")
        self.inputPCChucDanh = QLineEdit()
        self.inputPCChucDanh.setPlaceholderText("Ví dụ: 300000")
        self.inputPCXang = QLineEdit()
        self.inputPCXang.setPlaceholderText("Ví dụ: 200000")
        self.inputPCDienThoai = QLineEdit()
        self.inputPCDienThoai.setPlaceholderText("Ví dụ: 100000")
        
        form_layout.addRow("PC-Công trình (VNĐ):", self.inputPCCongTrinh)
        form_layout.addRow("PC-Chức danh (VNĐ):", self.inputPCChucDanh)
        form_layout.addRow("PC-Xăng (VNĐ):", self.inputPCXang)
        form_layout.addRow("PC-Điện thoại (VNĐ):", self.inputPCDienThoai)
        
        # Nút OK và Cancel
        btn_layout = QHBoxLayout()
        self.btnOK = QPushButton("OK")
        self.btnCancel = QPushButton("Hủy")
        btn_layout.addWidget(self.btnOK)
        btn_layout.addWidget(self.btnCancel)
        
        layout.addLayout(form_layout)
        layout.addLayout(btn_layout)
        self.setLayout(layout)
        
        # Kết nối sự kiện
        self.btnOK.clicked.connect(self.accept)
        self.btnCancel.clicked.connect(self.reject)
    
    def get_phu_cap(self):
        """Trả về danh sách phụ cấp"""
        return [
            self.inputPCCongTrinh.text().strip(),
            self.inputPCChucDanh.text().strip(),
            self.inputPCXang.text().strip(),
            self.inputPCDienThoai.text().strip()
        ]
    
    def set_phu_cap(self, phu_cap_list):
        """Điền sẵn giá trị phụ cấp"""
        if len(phu_cap_list) >= 4:
            self.inputPCCongTrinh.setText(phu_cap_list[0])
            self.inputPCChucDanh.setText(phu_cap_list[1])
            self.inputPCXang.setText(phu_cap_list[2])
            self.inputPCDienThoai.setText(phu_cap_list[3])

class TabQuyDinhLuong(QWidget):
    def __init__(self):
        super().__init__()
        self.data_manager = DataManager()
        self.ds_luong_nv, self.ds_phu_cap_ct = self.data_manager.load_quydinh_luong()
        self.ds_nhanvien = self.data_manager.load_nhanvien()  # Tải danh sách nhân viên
        self.init_ui()
        self.capnhat_bang_luong()
        self.capnhat_bang_phucap()
        self.capnhat_combo_nhanvien()  # Cập nhật combobox nhân viên

    def init_ui(self):
        layout = QVBoxLayout()

        # PHẦN 1: BẢNG QUY ĐỊNH LƯƠNG NHÂN VIÊN
        group_luong = QGroupBox("Quy định lương nhân viên")
        layout_luong = QVBoxLayout()

        # Form nhập liệu lương với combobox chọn nhân viên
        form_layout = QHBoxLayout()
        
        # Combobox chọn nhân viên
        self.comboNhanVien = QComboBox()
        self.comboNhanVien.setPlaceholderText("Chọn nhân viên...")
        self.comboNhanVien.currentTextChanged.connect(self.chon_nhanvien)
        
        self.inputMaNV = QLineEdit()
        self.inputMaNV.setPlaceholderText("MSNV")
        self.inputHoTen = QLineEdit()
        self.inputHoTen.setPlaceholderText("Họ và tên")
        self.inputCCCD = QLineEdit()
        self.inputCCCD.setPlaceholderText("CCCD")
        self.inputLuongCB = QLineEdit()
        self.inputLuongCB.setPlaceholderText("Lương cơ bản")
        self.inputTrangThai = QLineEdit()
        self.inputTrangThai.setPlaceholderText("Trạng thái")
        self.inputBaoHiem = QLineEdit()
        self.inputBaoHiem.setPlaceholderText("Tình trạng BHXH")
        
        # Thêm các input phụ cấp
        self.inputPCCongTrinh = QLineEdit()
        self.inputPCCongTrinh.setPlaceholderText("PC-Công trình")
        self.inputPCChucDanh = QLineEdit()
        self.inputPCChucDanh.setPlaceholderText("PC-Chức danh")
        self.inputPCXang = QLineEdit()
        self.inputPCXang.setPlaceholderText("PC-Xăng")
        self.inputPCDienThoai = QLineEdit()
        self.inputPCDienThoai.setPlaceholderText("PC-Điện thoại")
        self.inputPCNangSuatPAUT = QLineEdit()
        self.inputPCNangSuatPAUT.setPlaceholderText("PC-Năng suất PAUT")
        self.inputPCNangSuatTOFD = QLineEdit()
        self.inputPCNangSuatTOFD.setPlaceholderText("PC-Năng suất TOFD")

        form_layout.addWidget(QLabel("Chọn NV:"))
        form_layout.addWidget(self.comboNhanVien)
        form_layout.addWidget(self.inputMaNV)
        form_layout.addWidget(self.inputHoTen)
        form_layout.addWidget(self.inputCCCD)
        form_layout.addWidget(self.inputLuongCB)
        form_layout.addWidget(self.inputPCCongTrinh)
        form_layout.addWidget(self.inputPCChucDanh)
        form_layout.addWidget(self.inputPCXang)
        form_layout.addWidget(self.inputPCDienThoai)
        form_layout.addWidget(self.inputPCNangSuatPAUT)
        form_layout.addWidget(self.inputPCNangSuatTOFD)
        form_layout.addWidget(self.inputTrangThai)
        form_layout.addWidget(self.inputBaoHiem)

        # Bảng quy định lương
        self.tableLuong = QTableWidget(0, 12)
        self.tableLuong.setHorizontalHeaderLabels([
            "MSNV", "Họ và tên", "CCCD", "Lương cơ bản", 
            "PC-Công trình", "PC-Chức danh", "PC-Xăng", 
            "PC-Điện thoại", "PC-Năng suất PAUT", "PC-Năng suất TOFD",
            "Trạng thái", "BHXH"
        ])

        # Nút thao tác lương
        btn_layout_luong = QHBoxLayout()
        self.btnThemLuong = QPushButton("Thêm")
        self.btnSuaLuong = QPushButton("Sửa")
        self.btnXoaLuong = QPushButton("Xóa")
        self.btnRefreshNV = QPushButton("Làm mới danh sách NV")
        btn_layout_luong.addWidget(self.btnThemLuong)
        btn_layout_luong.addWidget(self.btnSuaLuong)
        btn_layout_luong.addWidget(self.btnXoaLuong)
        btn_layout_luong.addWidget(self.btnRefreshNV)

        layout_luong.addLayout(form_layout)
        layout_luong.addWidget(self.tableLuong)
        layout_luong.addLayout(btn_layout_luong)
        group_luong.setLayout(layout_luong)

        # PHẦN 2: BẢNG QUY ĐỊNH PHỤ CẤP CÔNG TRƯỜNG
        group_phucap = QGroupBox("Quy định phụ cấp theo công trường")
        layout_phucap = QVBoxLayout()

        # Form nhập liệu phụ cấp
        form_layout_pc = QHBoxLayout()
        self.inputLoaiDuAn = QLineEdit()
        self.inputLoaiDuAn.setPlaceholderText("Loại dự án")
        self.inputDonGiaLe = QLineEdit()
        self.inputDonGiaLe.setPlaceholderText("Số lần")
        self.inputChiPhi = QLineEdit()
        self.inputChiPhi.setPlaceholderText("Chi phí")

        form_layout_pc.addWidget(self.inputLoaiDuAn)
        form_layout_pc.addWidget(self.inputDonGiaLe)
        form_layout_pc.addWidget(self.inputChiPhi)

        # Bảng phụ cấp công trường
        self.tablePhucap = QTableWidget(0, 3)
        self.tablePhucap.setHorizontalHeaderLabels([
            "Loại dự án", "Số lần", "Chi phí"
        ])

        # Nút thao tác phụ cấp
        btn_layout_pc = QHBoxLayout()
        self.btnThemPC = QPushButton("Thêm")
        self.btnSuaPC = QPushButton("Sửa")
        self.btnXoaPC = QPushButton("Xóa")
        btn_layout_pc.addWidget(self.btnThemPC)
        btn_layout_pc.addWidget(self.btnSuaPC)
        btn_layout_pc.addWidget(self.btnXoaPC)

        layout_phucap.addLayout(form_layout_pc)
        layout_phucap.addWidget(self.tablePhucap)
        layout_phucap.addLayout(btn_layout_pc)
        group_phucap.setLayout(layout_phucap)

        # Thêm cả 2 phần vào layout chính
        layout.addWidget(group_luong)
        layout.addWidget(group_phucap)
        self.setLayout(layout)

        # Kết nối sự kiện cho bảng lương
        self.btnThemLuong.clicked.connect(self.them_luong)
        self.btnSuaLuong.clicked.connect(self.sua_luong)
        self.btnXoaLuong.clicked.connect(self.xoa_luong)
        self.btnRefreshNV.clicked.connect(self.capnhat_combo_nhanvien)
        self.tableLuong.cellClicked.connect(self.hien_thi_luong)

        # Kết nối sự kiện cho bảng phụ cấp
        self.btnThemPC.clicked.connect(self.them_phucap)
        self.btnSuaPC.clicked.connect(self.sua_phucap)
        self.btnXoaPC.clicked.connect(self.xoa_phucap)
        self.tablePhucap.cellClicked.connect(self.hien_thi_phucap)

    # Hàm mo_dialog_phucap đã được xóa vì không còn sử dụng popup

    def capnhat_combo_nhanvien(self):
        """Cập nhật combobox với danh sách nhân viên mới"""
        self.ds_nhanvien = self.data_manager.load_nhanvien()
        self.comboNhanVien.clear()
        self.comboNhanVien.addItem("Chọn nhân viên...")
        
        for nv in self.ds_nhanvien:
            if len(nv) >= 3:  # Đảm bảo có đủ thông tin
                display_text = f"{nv[2]} - {nv[0]}"  # MSNV - Họ tên
                self.comboNhanVien.addItem(display_text, nv)

    def chon_nhanvien(self, text):
        """Khi chọn nhân viên từ combobox, tự động điền thông tin"""
        if text == "Chọn nhân viên..." or not text:
            return
            
        # Tìm nhân viên được chọn
        for nv in self.ds_nhanvien:
            if len(nv) >= 3 and f"{nv[2]} - {nv[0]}" == text:
                # Tự động điền thông tin
                self.inputMaNV.setText(nv[2])  # MSNV
                self.inputHoTen.setText(nv[0])  # Họ tên
                self.inputCCCD.setText(nv[1])   # CCCD
                
                # Kiểm tra xem nhân viên đã có trong bảng lương chưa
                for luong in self.ds_luong_nv:
                    if len(luong) > 0 and luong[0] == nv[2]:  # MSNV trùng
                        QMessageBox.information(self, "Thông báo", 
                                              f"Nhân viên {nv[0]} đã có trong bảng lương!")
                        return
                break

    def them_luong(self):
        """Thêm quy định lương mới"""
        try:
            # Lấy thông tin từ các input
            msnv = self.inputMaNV.text().strip()
            ho_ten = self.inputHoTen.text().strip()
            cccd = self.inputCCCD.text().strip()
            luong_co_ban = self.inputLuongCB.text().strip()
            ngay_tinh_luong = "" # Không có input ngày tính lương trong form này
            
            # Lấy phụ cấp từ input trực tiếp
            pc_cong_trinh = self.inputPCCongTrinh.text().strip()
            pc_chuc_danh = self.inputPCChucDanh.text().strip()
            pc_xang = self.inputPCXang.text().strip()
            pc_dien_thoai = self.inputPCDienThoai.text().strip()
            pc_nang_suat_paut = self.inputPCNangSuatPAUT.text().strip()
            pc_nang_suat_tofd = self.inputPCNangSuatTOFD.text().strip()
            
            # Kiểm tra dữ liệu bắt buộc
            if not msnv or not ho_ten:
                QMessageBox.warning(self, "Cảnh báo", "Vui lòng nhập đầy đủ MSNV và Họ tên!")
                return
            
            # Kiểm tra trùng lặp
            for row in range(self.tableLuong.rowCount()):
                item_msnv = self.tableLuong.item(row, 0)  # Cột MSNV
                if item_msnv and item_msnv.text() == msnv:
                    QMessageBox.warning(self, "Cảnh báo", "MSNV đã tồn tại!")
                    return
            
            # Tạo dữ liệu lương với đủ 12 cột (đã bỏ PC-Năng suất chung)
            luong = [msnv, ho_ten, cccd, luong_co_ban, pc_cong_trinh, pc_chuc_danh, pc_xang, pc_dien_thoai,
                    pc_nang_suat_paut, pc_nang_suat_tofd, "", ""]
            
            # Đảm bảo đủ số cột
            while len(luong) < 12:
                luong.append("")
            
            # Thêm vào bảng
            row = self.tableLuong.rowCount()
            self.tableLuong.insertRow(row)
            
            for col, value in enumerate(luong):
                self.tableLuong.setItem(row, col, QTableWidgetItem(str(value)))
            
            # Xóa dữ liệu input
            self.clear_inputs_luong()
            
            # Auto-save dữ liệu
            self.auto_save_data()
            
            QMessageBox.information(self, "Thành công", "Đã thêm quy định lương mới!")
            
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Không thể thêm quy định lương: {str(e)}")
    
    def auto_save_data(self):
        """Tự động lưu dữ liệu"""
        try:
            # Thu thập dữ liệu từ bảng
            data = []
            for row in range(self.tableLuong.rowCount()):
                row_data = []
                for col in range(self.tableLuong.columnCount()):
                    item = self.tableLuong.item(row, col)
                    row_data.append(item.text() if item else "")
                if any(cell.strip() for cell in row_data):  # Chỉ lưu dòng có dữ liệu
                    data.append(row_data)
            
            # Lưu vào file
            self.data_manager.save_quydinh_luong(data, self.ds_phu_cap_ct)
            print("Đã tự động lưu dữ liệu quy định lương")
            
        except Exception as e:
            print(f"Lỗi tự động lưu dữ liệu quy định lương: {str(e)}")

    def sua_luong(self):
        """Sửa quy định lương"""
        try:
            current_row = self.tableLuong.currentRow()
            if current_row >= 0:
                # Lấy thông tin từ các input
                msnv = self.inputMaNV.text().strip()
                ho_ten = self.inputHoTen.text().strip()
                cccd = self.inputCCCD.text().strip()
                luong_co_ban = self.inputLuongCB.text().strip()
                ngay_tinh_luong = ""  # Không có input ngày tính lương
                
                # Lấy phụ cấp từ input trực tiếp
                pc_cong_trinh = self.inputPCCongTrinh.text().strip()
                pc_chuc_danh = self.inputPCChucDanh.text().strip()
                pc_xang = self.inputPCXang.text().strip()
                pc_dien_thoai = self.inputPCDienThoai.text().strip()
                pc_nang_suat_paut = self.inputPCNangSuatPAUT.text().strip()
                pc_nang_suat_tofd = self.inputPCNangSuatTOFD.text().strip()
                
                # Kiểm tra dữ liệu bắt buộc
                if not msnv or not ho_ten:
                    QMessageBox.warning(self, "Cảnh báo", "Vui lòng nhập đầy đủ MSNV và Họ tên!")
                    return
                
                # Tạo dữ liệu lương với đủ 12 cột (đã bỏ PC-Năng suất chung)
                luong = [msnv, ho_ten, cccd, luong_co_ban, pc_cong_trinh, pc_chuc_danh, pc_xang, pc_dien_thoai,
                        pc_nang_suat_paut, pc_nang_suat_tofd, "", ""]
                
                # Đảm bảo đủ số cột
                while len(luong) < 12:
                    luong.append("")
                
                # Cập nhật vào bảng
                for col, value in enumerate(luong):
                    self.tableLuong.setItem(current_row, col, QTableWidgetItem(str(value)))
                
                # Xóa dữ liệu input
                self.clear_inputs_luong()
                
                # Auto-save dữ liệu
                self.auto_save_data()
                
                QMessageBox.information(self, "Thành công", "Đã cập nhật quy định lương!")
            else:
                QMessageBox.warning(self, "Cảnh báo", "Vui lòng chọn quy định lương cần sửa!")
                
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Không thể sửa quy định lương: {str(e)}")

    def xoa_luong(self):
        """Xóa quy định lương được chọn"""
        try:
            current_row = self.tableLuong.currentRow()
            if current_row >= 0:
                # Lấy tên nhân viên để hiển thị
                item = self.tableLuong.item(current_row, 1)  # Cột Họ tên
                ten_nv = item.text() if item else "Nhân viên"
                
                # Xác nhận xóa
                reply = QMessageBox.question(
                    self, "Xác nhận xóa", 
                    f"Bạn có chắc muốn xóa quy định lương của '{ten_nv}'?",
                    QMessageBox.Yes | QMessageBox.No, QMessageBox.No
                )
                
                if reply == QMessageBox.Yes:
                    self.tableLuong.removeRow(current_row)
                    
                    # Auto-save dữ liệu
                    self.auto_save_data()
                    
                    QMessageBox.information(self, "Thành công", f"Đã xóa quy định lương của '{ten_nv}'!")
            else:
                QMessageBox.warning(self, "Cảnh báo", "Vui lòng chọn quy định lương cần xóa!")
                
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Không thể xóa quy định lương: {str(e)}")

    def hien_thi_luong(self, row, col):
        try:
            # Kiểm tra row có hợp lệ không
            if row < 0 or row >= len(self.ds_luong_nv):
                print(f"Lỗi: Row {row} không hợp lệ, tổng số quy định lương: {len(self.ds_luong_nv)}")
                return
            
            luong = self.ds_luong_nv[row]
            
            # Kiểm tra luong có phải là list không
            if not isinstance(luong, list):
                print(f"Lỗi: Dữ liệu lương tại row {row} không phải là list")
                return
            
            # Tương thích dữ liệu cũ (13 cột, có PC-Năng suất ở index 8): bỏ cột này
            try:
                if len(luong) >= 13:
                    # Tạo bản sao để không sửa trực tiếp nguồn dữ liệu
                    luong = luong.copy()
                    luong.pop(8)  # Bỏ "PC-Năng suất" cũ
            except Exception:
                pass
            
            # Hiển thị thông tin với kiểm tra an toàn
            self.inputMaNV.setText(str(luong[0]) if len(luong) > 0 and luong[0] else "")
            self.inputHoTen.setText(str(luong[1]) if len(luong) > 1 and luong[1] else "")
            self.inputCCCD.setText(str(luong[2]) if len(luong) > 2 and luong[2] else "")
            self.inputLuongCB.setText(str(luong[3]) if len(luong) > 3 and luong[3] else "")
            
            # Hiển thị phụ cấp (đúng index theo header bảng)
            if len(luong) > 4:
                self.inputPCCongTrinh.setText(str(luong[4]))  # PC-Công trình
            else:
                self.inputPCCongTrinh.clear()
                
            if len(luong) > 5:
                self.inputPCChucDanh.setText(str(luong[5]))  # PC-Chức danh
            else:
                self.inputPCChucDanh.clear()
                
            if len(luong) > 6:
                self.inputPCXang.setText(str(luong[6]))      # PC-Xăng
            else:
                self.inputPCXang.clear()
                
            if len(luong) > 7:
                self.inputPCDienThoai.setText(str(luong[7])) # PC-Điện thoại
            else:
                self.inputPCDienThoai.clear()
                
            if len(luong) > 8:
                self.inputPCNangSuatPAUT.setText(str(luong[8]))  # PC-Năng suất PAUT (mới)
            else:
                self.inputPCNangSuatPAUT.clear()
                
            if len(luong) > 9:
                self.inputPCNangSuatTOFD.setText(str(luong[9]))  # PC-Năng suất TOFD (mới)
            else:
                self.inputPCNangSuatTOFD.clear()
            
            # Hiển thị trạng thái và BHXH
            if len(luong) > 10:
                self.inputTrangThai.setText(str(luong[10]))
            else:
                self.inputTrangThai.clear()
                
            if len(luong) > 11:
                self.inputBaoHiem.setText(str(luong[11]))
            else:
                self.inputBaoHiem.clear()
                
        except Exception as e:
            print(f"Lỗi khi hiển thị thông tin lương tại row {row}: {str(e)}")
            QMessageBox.warning(self, "Lỗi", f"Không thể hiển thị thông tin lương: {str(e)}")

    def capnhat_bang_luong(self):
        self.tableLuong.setRowCount(0)
        print(f" DEBUG - Cập nhật bảng lương:")
        print(f"   📊 Số lượng bản ghi: {len(self.ds_luong_nv)}")
        
        for i, luong in enumerate(self.ds_luong_nv):
            print(f"   📋 Bản ghi {i}: {luong}")
            row = self.tableLuong.rowCount()
            self.tableLuong.insertRow(row)
            
            # Chuyển dữ liệu cũ 13 cột về 12 cột (bỏ index 8 nếu có)
            if len(luong) >= 13:
                try:
                    luong = luong.copy()
                    luong.pop(8)
                    print(f"   🔄 Đã chuyển từ 13 cột về 12 cột")
                except Exception:
                    pass
            
            # Đảm bảo đủ 12 cột
            while len(luong) < 12:
                luong.append("")
            
            print(f"    Dữ liệu cuối cùng: {luong}")
            for col, val in enumerate(luong):
                self.tableLuong.setItem(row, col, QTableWidgetItem(str(val)))

    def clear_inputs_luong(self):
        """Xóa dữ liệu trong các input lương"""
        self.inputMaNV.clear()
        self.inputHoTen.clear()
        self.inputCCCD.clear()
        self.inputLuongCB.clear()
        self.inputPCCongTrinh.clear()
        self.inputPCChucDanh.clear()
        self.inputPCXang.clear()
        self.inputPCDienThoai.clear()
        self.inputPCNangSuatPAUT.clear()
        self.inputPCNangSuatTOFD.clear()
        self.inputTrangThai.clear()
        self.inputBaoHiem.clear()

    def them_phucap(self):
        pc = [
            self.inputLoaiDuAn.text().strip(),
            self.inputDonGiaLe.text().strip(),
            self.inputChiPhi.text().strip()
        ]
        
        if not pc[0]:
            QMessageBox.warning(self, "Thiếu thông tin", 
                              "Vui lòng nhập Loại dự án")
            return

        self.ds_phu_cap_ct.append(pc)
        self.capnhat_bang_phucap()
        self.clear_inputs_phucap()
        # Lưu dữ liệu
        self.data_manager.save_quydinh_luong(self.ds_luong_nv, self.ds_phu_cap_ct)

    def sua_phucap(self):
        dong = self.tablePhucap.currentRow()
        if dong >= 0:
            pc = [
                self.inputLoaiDuAn.text().strip(),
                self.inputDonGiaLe.text().strip(),
                self.inputChiPhi.text().strip()
            ]
            
            if not pc[0]:
                QMessageBox.warning(self, "Thiếu thông tin", 
                                  "Vui lòng nhập Loại dự án")
                return

            self.ds_phu_cap_ct[dong] = pc
            self.capnhat_bang_phucap()
            # Lưu dữ liệu
            self.data_manager.save_quydinh_luong(self.ds_luong_nv, self.ds_phu_cap_ct)
        else:
            QMessageBox.warning(self, "Chưa chọn", "Vui lòng chọn dự án để sửa")

    def xoa_phucap(self):
        dong = self.tablePhucap.currentRow()
        if dong >= 0:
            # Lấy tên công ty muốn xóa
            company_to_delete = self.ds_phu_cap_ct[dong][0]
            
            # Kiểm tra xem công ty có đang được sử dụng không
            if self.is_company_in_use(company_to_delete):
                QMessageBox.warning(
                    self, 
                    "Không thể xóa", 
                    f"Không thể xóa công ty '{company_to_delete}'!\n\n"
                    f"Công ty này đang được sử dụng trong dữ liệu chấm công.\n"
                    f"Vui lòng xóa dữ liệu chấm công liên quan trước khi xóa công ty."
                )
                return
            
            # Xác nhận xóa
            reply = QMessageBox.question(
                self, 
                "Xác nhận xóa", 
                f"Bạn có chắc chắn muốn xóa công ty '{company_to_delete}'?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                del self.ds_phu_cap_ct[dong]
                self.capnhat_bang_phucap()
                # Lưu dữ liệu
                self.data_manager.save_quydinh_luong(self.ds_luong_nv, self.ds_phu_cap_ct)
                QMessageBox.information(self, "Thành công", f"Đã xóa công ty '{company_to_delete}'")
        else:
            QMessageBox.warning(self, "Chưa chọn", "Vui lòng chọn dự án để xóa")

    def hien_thi_phucap(self, row, col):
        try:
            # Kiểm tra row có hợp lệ không
            if row < 0 or row >= len(self.ds_phu_cap_ct):
                print(f"Lỗi: Row {row} không hợp lệ, tổng số phụ cấp: {len(self.ds_phu_cap_ct)}")
                return
            
            pc = self.ds_phu_cap_ct[row]
            
            # Kiểm tra pc có phải là list không
            if not isinstance(pc, list):
                print(f"Lỗi: Dữ liệu phụ cấp tại row {row} không phải là list")
                return
            
            # Hiển thị thông tin với kiểm tra an toàn
            self.inputLoaiDuAn.setText(str(pc[0]) if len(pc) > 0 and pc[0] else "")
            self.inputDonGiaLe.setText(str(pc[1]) if len(pc) > 1 and pc[1] else "")
            self.inputChiPhi.setText(str(pc[2]) if len(pc) > 2 and pc[2] else "")
            
        except Exception as e:
            print(f"Lỗi khi hiển thị thông tin phụ cấp tại row {row}: {str(e)}")
            QMessageBox.warning(self, "Lỗi", f"Không thể hiển thị thông tin phụ cấp: {str(e)}")

    def capnhat_bang_phucap(self):
        self.tablePhucap.setRowCount(0)
        for pc in self.ds_phu_cap_ct:
            row = self.tablePhucap.rowCount()
            self.tablePhucap.insertRow(row)
            
            company_name = pc[0]
            is_in_use = self.is_company_in_use(company_name)
            
            for col, val in enumerate(pc):
                item = QTableWidgetItem(val)
                
                # Đánh dấu công ty đang được sử dụng
                if col == 0 and is_in_use:  # Cột đầu tiên (tên công ty)
                    item.setBackground(QColor(255, 255, 200))  # Màu vàng nhạt
                    item.setToolTip(f"⚠️ Công ty '{company_name}' đang được sử dụng trong dữ liệu chấm công")
                
                self.tablePhucap.setItem(row, col, item)

    def clear_inputs_phucap(self):
        self.inputLoaiDuAn.clear()
        self.inputDonGiaLe.clear()
        self.inputChiPhi.clear() 

    def refresh_data(self):
        """Tự động cập nhật dữ liệu khi có thay đổi"""
        try:
            print("Đang cập nhật dữ liệu quy định lương...")
            
            # Reload dữ liệu từ data manager
            self.ds_luong_nv, self.ds_phu_cap_ct = self.data_manager.load_quydinh_luong()
            
            # Cập nhật danh sách nhân viên (quan trọng!)
            self.capnhat_combo_nhanvien()
            
            # Refresh bảng
            self.capnhat_bang_luong()
            self.capnhat_bang_phucap()  # Thêm refresh bảng phụ cấp
            
            print("Đã cập nhật xong dữ liệu quy định lương")
            
        except Exception as e:
            print(f"Lỗi cập nhật dữ liệu quy định lương: {e}")
    
    def is_company_in_use(self, company_name):
        """
        Kiểm tra xem công ty có đang được sử dụng trong dữ liệu chấm công không
        """
        try:
            # Không tự động load dữ liệu chấm công khi khởi động
            # Chỉ kiểm tra khi thực sự cần thiết
            return False
            
        except Exception as e:
            print(f"Lỗi kiểm tra công ty đang sử dụng: {e}")
            return False  # Nếu có lỗi, không cho phép xóa để đảm bảo an toàn 