from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QMessageBox, QLabel, QComboBox, QGroupBox, QFormLayout,
    QHeaderView, QFrame, QSpacerItem, QSizePolicy, QScrollArea, QDialog,
    QFileDialog, QSpinBox, QLineEdit, QTextEdit, QCheckBox, QScrollArea
)
from PyQt5.QtCore import Qt, QDate, QSize, QPoint
from PyQt5.QtGui import QFont, QColor, QIcon, QPixmap, QPainter
import json
import csv
import calendar
from datetime import datetime
from data_manager import DataManager
from company_matcher import CompanyMatcher
from new_company_dialog import NewCompanyDialog
from employee_mapper import EmployeeMapper
import os

class EmployeeSelectionDialog(QDialog):
    """Dialog để chọn nhân viên hiển thị trong bảng công"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.data_manager = DataManager()
        self.selected_employees = set()  # Set lưu tên nhân viên được chọn
        self.load_selected_employees()  # Tải danh sách đã chọn trước đó
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle("Chọn nhân viên hiển thị")
        self.setModal(True)
        self.setFixedSize(500, 400)
        
        layout = QVBoxLayout(self)
        
        # Tiêu đề
        title = QLabel("Chọn nhân viên để hiển thị trong bảng công:")
        title.setFont(QFont("Times New Roman", 12, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Scroll area cho danh sách nhân viên
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        # Widget chứa danh sách checkbox
        self.checkbox_widget = QWidget()
        self.checkbox_layout = QVBoxLayout(self.checkbox_widget)
        
        # Tải danh sách nhân viên từ 2 tab
        self.load_employees_from_tabs()
        
        scroll_area.setWidget(self.checkbox_widget)
        layout.addWidget(scroll_area)
        
        # Nút thao tác
        btn_layout = QHBoxLayout()
        
        self.btnSelectAll = QPushButton("Chọn tất cả")
        self.btnSelectAll.clicked.connect(self.select_all)
        
        self.btnDeselectAll = QPushButton("Bỏ chọn tất cả")
        self.btnDeselectAll.clicked.connect(self.deselect_all)
        
        self.btnOK = QPushButton("OK")
        self.btnOK.clicked.connect(self.accept)
        
        self.btnCancel = QPushButton("Hủy")
        self.btnCancel.clicked.connect(self.reject)
        
        btn_layout.addWidget(self.btnSelectAll)
        btn_layout.addWidget(self.btnDeselectAll)
        btn_layout.addStretch()
        btn_layout.addWidget(self.btnOK)
        btn_layout.addWidget(self.btnCancel)
        
        layout.addLayout(btn_layout)
        
    def load_employees_from_tabs(self):
        """Tải nhân viên từ 2 tab: Quản lý con người và Quy định lương"""
        employees = set()
        
        # Tải từ tab Quản lý con người
        try:
            ds_nhanvien = self.data_manager.load_nhanvien()
            for nv in ds_nhanvien:
                if len(nv) >= 3:  # Đảm bảo có đủ thông tin
                    employees.add(nv[0])  # Họ tên
        except Exception as e:
            print(f"Lỗi tải nhân viên từ tab Quản lý con người: {e}")
            
        # Tải từ tab Quy định lương
        try:
            ds_luong_nv, _ = self.data_manager.load_quydinh_luong()
            for luong in ds_luong_nv:
                if len(luong) >= 2:
                    employees.add(luong[1])  # Họ tên
        except Exception as e:
            print(f"Lỗi tải nhân viên từ tab Quy định lương: {e}")
        
        # Tạo checkbox cho từng nhân viên
        self.checkboxes = {}
        for employee in sorted(employees):
            if employee and employee.strip():  # Kiểm tra tên không rỗng
                checkbox = QCheckBox(employee)
                checkbox.setChecked(employee in self.selected_employees)
                checkbox.stateChanged.connect(self.on_checkbox_changed)
                self.checkbox_layout.addWidget(checkbox)
                self.checkboxes[employee] = checkbox
            
        # Thêm spacer để đẩy các checkbox lên trên
        self.checkbox_layout.addStretch()
        
    def on_checkbox_changed(self):
        """Khi checkbox thay đổi, cập nhật danh sách được chọn"""
        try:
            self.selected_employees.clear()
            for employee, checkbox in self.checkboxes.items():
                if checkbox.isChecked():
                    self.selected_employees.add(employee)
            self.save_selected_employees()
        except Exception as e:
            print(f"Lỗi khi cập nhật checkbox: {e}")
        
    def select_all(self):
        """Chọn tất cả nhân viên"""
        try:
            for checkbox in self.checkboxes.values():
                checkbox.setChecked(True)
        except Exception as e:
            print(f"Lỗi khi chọn tất cả: {e}")
            
    def deselect_all(self):
        """Bỏ chọn tất cả nhân viên"""
        try:
            for checkbox in self.checkboxes.values():
                checkbox.setChecked(False)
        except Exception as e:
            print(f"Lỗi khi bỏ chọn tất cả: {e}")
            
    def get_selected_employees(self):
        """Trả về danh sách nhân viên được chọn"""
        try:
            return list(self.selected_employees)
        except Exception as e:
            print(f"Lỗi khi lấy danh sách nhân viên được chọn: {e}")
            return []
        
    def load_selected_employees(self):
        """Tải danh sách nhân viên đã chọn từ file"""
        try:
            import os
            if os.path.exists('data/selected_employees.json'):
                with open('data/selected_employees.json', 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.selected_employees = set(data.get('employees', []))
            else:
                self.selected_employees = set()
        except Exception as e:
            print(f"Lỗi tải danh sách nhân viên: {e}")
            self.selected_employees = set()
    
    def save_selected_employees(self):
        """Lưu danh sách nhân viên được chọn vào file"""
        try:
            import os
            if not os.path.exists('data'):
                os.makedirs('data')
                
            data = {
                'employees': list(self.selected_employees),
                'timestamp': datetime.now().isoformat()
            }
            
            with open('data/selected_employees.json', 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Lỗi lưu danh sách nhân viên: {e}")

class BangCongDialog(QDialog):
    """Dialog để xem chi tiết bảng công của 1 nhân viên"""
    def __init__(self, employee_name, month_data, parent=None):
        super().__init__(parent)
        self.employee_name = employee_name
        self.month_data = month_data
        self.data_manager = DataManager()
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle(f"Chi tiết bảng công - {self.employee_name}")
        self.setModal(True)
        self.resize(1000, 600)
        
        layout = QVBoxLayout(self)
        
        # Tiêu đề
        title = QLabel(f"Chi tiết bảng công - {self.employee_name}")
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont("Times New Roman", 14, QFont.Bold))
        layout.addWidget(title)
        
        # Bảng chi tiết từng ngày với nhiều cột thông tin
        table = QTableWidget()
        
        # Tìm số ngày có dữ liệu
        max_day = 0
        for day_key in self.month_data.keys():
            if day_key.startswith('day_'):
                day_num = int(day_key.split('_')[1])
                max_day = max(max_day, day_num)
        
        if max_day == 0:
            max_day = 31
            
        table.setRowCount(max_day)
        table.setColumnCount(17)
        table.setHorizontalHeaderLabels([
            "Ngày", "Loại", "Địa điểm", "Phương\npháp", 
            "Ca\nngày", "Ca\nđêm", "Tăng ca\nngày", "Tăng ca\nđêm", 
            "Giờ tăng\nca", "Chi phí\n(VNĐ)", "Khách sạn\n(VNĐ)", "Mua sắm\n(VNĐ)", "Điện thoại\n(VNĐ)", "Xăng xe\n(VNĐ)", "Khác\n(VNĐ)",
            "Tạo lúc", "Cập nhật", "Ghi chú"
        ])
        
        # Điền dữ liệu
        for day in range(1, max_day + 1):
            # Thử cả 2 format: day_01 và day_1
            day_data = self.month_data.get(f"day_{day:02d}", self.month_data.get(f"day_{day}", {}))
            
            if isinstance(day_data, dict):
                # Dữ liệu JSON chi tiết từ website
                table.setItem(day-1, 0, QTableWidgetItem(str(day)))
                table.setItem(day-1, 1, QTableWidgetItem(day_data.get('type', '')))
                table.setItem(day-1, 2, QTableWidgetItem(day_data.get('location', '')))
                table.setItem(day-1, 3, QTableWidgetItem(day_data.get('method', '')))
                
                # Thông tin ca làm việc
                day_shift = day_data.get('day_shift', False)
                night_shift = day_data.get('night_shift', False)
                table.setItem(day-1, 4, QTableWidgetItem("✓" if day_shift else ""))
                table.setItem(day-1, 5, QTableWidgetItem("✓" if night_shift else ""))
                
                # Thông tin tăng ca
                day_overtime = day_data.get('day_overtime_end', '')
                night_overtime = day_data.get('night_overtime_end', '')
                table.setItem(day-1, 6, QTableWidgetItem(day_overtime))
                table.setItem(day-1, 7, QTableWidgetItem(night_overtime))
                
                # Giờ tăng ca
                overtime_hours = day_data.get('overtime_hours', 0)
                table.setItem(day-1, 8, QTableWidgetItem(f"{overtime_hours}" if overtime_hours > 0 else ""))
                
                # Chi phí = tổng các khoản: KS + MS + ĐT + Xăng xe + Khác
                location = day_data.get('location', '')
                
                # Tính tiền khách sạn từ dữ liệu JSON
                hotel = day_data.get('hotel_expense', 0)
                hotel_amount = float(hotel) if hotel else 0
                
                shopping = day_data.get('shopping_expense', 0)
                shopping_amount = float(shopping) if shopping else 0
                
                phone = day_data.get('phone_expense', 0)
                phone_amount = float(phone) if phone else 0
                
                # Xăng xe - tính theo địa điểm công trường
                gas_amount = 0
                day_type = day_data.get('type', '')
                location = day_data.get('location', '')
                if day_type == 'W' and location:  # Chỉ tính cho ngày công trường có địa điểm
                    try:
                        ds_luong, ds_phu_cap = self.data_manager.load_quydinh_luong()
                        if ds_phu_cap:
                            # Tìm địa điểm trong quy định phụ cấp công trường
                            for phu_cap in ds_phu_cap:
                                if isinstance(phu_cap, list) and len(phu_cap) >= 3:
                                    dia_diem = phu_cap[0] if phu_cap[0] else ""
                                    if dia_diem == location:
                                        gas_amount = float(str(phu_cap[2]).replace(',', '')) if phu_cap[2] else 0
                                        break
                    except Exception as e:
                        print(f"Lỗi tính tiền xăng xe: {e}")
                        gas_amount = 0
                
                other = day_data.get('other_expense', 0)
                other_amount = float(other) if other else 0
                
                total_expenses = hotel_amount + shopping_amount + phone_amount + gas_amount + other_amount
                table.setItem(day-1, 9, QTableWidgetItem(f"{total_expenses:,}" if total_expenses > 0 else ""))
                
                # Khách sạn - lấy từ dữ liệu JSON
                hotel = day_data.get('hotel_expense', 0)
                hotel_amount = float(hotel) if hotel else 0
                table.setItem(day-1, 10, QTableWidgetItem(f"{hotel_amount:,}" if hotel_amount > 0 else ""))
                
                # Mua sắm
                shopping = day_data.get('shopping_expense', 0)
                shopping_amount = float(shopping) if shopping else 0
                table.setItem(day-1, 11, QTableWidgetItem(f"{shopping_amount:,}" if shopping_amount > 0 else ""))
                
                # Điện thoại
                phone = day_data.get('phone_expense', 0)
                phone_amount = float(phone) if phone else 0
                table.setItem(day-1, 12, QTableWidgetItem(f"{phone_amount:,}" if phone_amount > 0 else ""))
                
                table.setItem(day-1, 13, QTableWidgetItem(f"{gas_amount:,}" if gas_amount > 0 else ""))
                
                # Khác
                other = day_data.get('other_expense', 0)
                other_desc = day_data.get('other_expense_desc', '')
                other_amount = float(other) if other else 0
                
                if other_amount > 0:
                    if other_desc:
                        other_text = f"{other_amount:,} ({other_desc})"
                    else:
                        other_text = f"{other_amount:,}"
                else:
                    other_text = ""
                table.setItem(day-1, 14, QTableWidgetItem(other_text))
                
                # Thời gian tạo
                created_at = day_data.get('created_at', '')
                if created_at:
                    # Format thời gian ngắn gọn hơn
                    try:
                        dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                        created_time = dt.strftime('%H:%M')
                    except:
                        created_time = created_at[:5] if len(created_at) >= 5 else created_at
                else:
                    created_time = ""
                table.setItem(day-1, 15, QTableWidgetItem(created_time))
                
                # Thời gian cập nhật
                updated_at = day_data.get('updated_at', '')
                if updated_at:
                    try:
                        dt = datetime.fromisoformat(updated_at.replace('Z', '+00:00'))
                        updated_time = dt.strftime('%H:%M')
                    except:
                        updated_time = updated_at[:5] if len(updated_at) >= 5 else updated_at
                else:
                    updated_time = ""
                table.setItem(day-1, 16, QTableWidgetItem(updated_time))
                
                # Ghi chú
                note = day_data.get('note', '')
                table.setItem(day-1, 17, QTableWidgetItem(note))
                
                # Thêm tooltip với thông tin chi tiết
                tooltip_parts = []
                
                # Thêm thông tin chi phí vào tooltip
                if hotel_amount > 0:
                    tooltip_parts.append(f"Khách sạn: {hotel_amount:,} VNĐ")
                if shopping_amount > 0:
                    tooltip_parts.append(f"Mua sắm: {shopping_amount:,} VNĐ")
                if phone_amount > 0:
                    tooltip_parts.append(f"Điện thoại: {phone_amount:,} VNĐ")
                if gas_amount > 0:
                    tooltip_parts.append(f"Xăng xe: {gas_amount:,} VNĐ")
                if other_amount > 0:
                    if other_desc:
                        tooltip_parts.append(f"Khác: {other_amount:,} VNĐ ({other_desc})")
                    else:
                        tooltip_parts.append(f"Khác: {other_amount:,} VNĐ")
                
                if tooltip_parts:
                    tooltip = "Chi phí: " + " | ".join(tooltip_parts)
                    for col in range(18):
                        item = table.item(day-1, col)
                        if item:
                            item.setToolTip(tooltip)
            else:
                # Dữ liệu CSV đơn giản (fallback)
                table.setItem(day-1, 0, QTableWidgetItem(str(day)))
                table.setItem(day-1, 1, QTableWidgetItem(str(day_data)))
                # Các cột khác để trống cho dữ liệu CSV đơn giản
        
        # Style cho table
        table.setStyleSheet("""
            QTableWidget {
                gridline-color: #e9ecef;
                font-family: "Times New Roman";
                font-size: 10pt;
                background-color: white;
                alternate-background-color: #fafbfc;
                border: 1px solid #e9ecef;
            }
            QHeaderView::section {
                background-color: #f8f9fa;
                padding: 8px 4px;
                border: none;
                border-right: 1px solid #e9ecef;
                border-bottom: 1px solid #e9ecef;
                font-weight: normal;
                font-family: "Times New Roman";
                font-size: 9pt;
                color: #495057;
                min-height: 40px;
            }
            QTableWidget::item {
                padding: 6px 4px;
                border: none;
                border-right: 1px solid #f1f3f4;
                border-bottom: 1px solid #f1f3f4;
                font-family: "Times New Roman";
            }
            QTableWidget::item:selected {
                border: 1px solid #ced4da;
            }
        """)
        
        table.resizeColumnsToContents()
        table.setAlternatingRowColors(True)
        layout.addWidget(table)
        
        # Nút đóng
        close_btn = QPushButton("Đóng")
        close_btn.setFont(QFont("Times New Roman", 10))
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #495057;
                color: white;
                border: none;
                border-radius: 2px;
                padding: 8px 16px;
                font-family: "Times New Roman";
            }
            QPushButton:hover {
                background-color: #343a40;
            }
        """)
        close_btn.clicked.connect(self.close)
        layout.addWidget(close_btn)

class TabBangCong(QWidget):
    def __init__(self, on_data_changed=None, on_quydinh_changed=None):
        super().__init__()
        self.data_manager = DataManager()
        self.employee_mapper = EmployeeMapper()
        
        # Lưu trữ dữ liệu theo tháng: { "MM/YYYY": { data_chamcong: {}, file_path: "" } }
        self.monthly_data = {}
        # Khởi tạo data_chamcong để tương thích với code cũ
        self.data_chamcong = {}
        # Danh sách các tháng có dữ liệu
        self.available_months = []
        self.current_month = datetime.now().month
        self.current_year = datetime.now().year
        self.current_period = f"{self.current_month:02d}/{self.current_year}"
        
        self.on_data_changed = on_data_changed
        self.on_quydinh_changed = on_quydinh_changed
        self.selected_employees = set()
        self.sunday_columns = []
        
        self.load_selected_employees()
        self.load_employee_mapping()
        self.scan_available_files()  # Quét các file có sẵn
        self.auto_load_imported_file()  # Tự động load file đã import
        self.init_ui()
        self.auto_load_current_month()  # Tự động load tháng hiện tại
    
    def scan_available_files(self):
        """Quét các file chấm công có sẵn trong thư mục data"""
        try:
            import glob
            import os
            
            # Tìm tất cả file chấm công
            json_files = glob.glob(os.path.join(self.data_manager.data_dir, "*.json"))
            chamcong_files = [f for f in json_files if "chamcong" in os.path.basename(f).lower()]
            
            print(f"🔍 Quét thấy {len(chamcong_files)} file chấm công:")
            
            for file_path in chamcong_files:
                try:
                    # Đọc file để lấy thông tin period
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    # Lấy period từ export_info
                    if isinstance(data, dict) and "export_info" in data:
                        period = data.get("export_info", {}).get("period", "")
                        if period and "/" in period:
                            print(f"    {period}: {os.path.basename(file_path)}")
                            # Lưu thông tin file
                            if period not in self.monthly_data:
                                self.monthly_data[period] = {
                                    'file_path': file_path,
                                    'data_chamcong': {},
                                    'is_loaded': False
                                }
                    
                except Exception as e:
                    print(f"   ❌ Lỗi đọc file {file_path}: {e}")
                    
        except Exception as e:
            print(f"❌ Lỗi quét file: {e}")
    
    def auto_load_current_month(self):
        """Tự động load dữ liệu tháng hiện tại"""
        try:
            print(f" Tự động load dữ liệu tháng {self.current_period}...")
            
            # Kiểm tra xem tháng hiện tại đã có dữ liệu chưa
            if self.current_period in self.monthly_data:
                if not self.monthly_data[self.current_period]['is_loaded']:
                    self.load_month_data(self.current_period)
            else:
                # Tìm file phù hợp cho tháng hiện tại
                self.find_and_load_month_file(self.current_period)
                
        except Exception as e:
            print(f"❌ Lỗi auto load tháng hiện tại: {e}")
    
    def find_and_load_month_file(self, period):
        """Tìm và load file cho tháng cụ thể"""
        try:
            import glob
            import os
            
            month_str = period.split('/')[0]
            year_str = period.split('/')[1]
            
            # Tìm file phù hợp
            patterns = [
                f"chamcong_{month_str}_{year_str}.json",
                f"chamcong_{int(month_str):02d}_{year_str}.json",
                f"chamcong_3_nhanvien_{month_str}_{year_str}.json",
                f"chamcong_3_nhanvien.json"
            ]
            
            for pattern in patterns:
                file_path = os.path.join(self.data_manager.data_dir, pattern)
                if os.path.exists(file_path):
                    print(f"📂 Tìm thấy file: {file_path}")
                    self.monthly_data[period] = {
                        'file_path': file_path,
                        'data_chamcong': {},
                        'is_loaded': False
                    }
                    self.load_month_data(period)
                    return True
            
            print(f"⚠️ Không tìm thấy file cho tháng {period}")
            return False
            
        except Exception as e:
            print(f"❌ Lỗi tìm file tháng {period}: {e}")
            return False
    
    def load_month_data(self, period):
        """Load dữ liệu cho tháng cụ thể"""
        try:
            if period not in self.monthly_data:
                print(f"❌ Không có thông tin file cho tháng {period}")
                return False
            
            file_path = self.monthly_data[period]['file_path']
            print(f" Load dữ liệu từ: {file_path}")
            
            # Cập nhật đường dẫn file trong data manager
            self.data_manager.chamcong_file = file_path
            
            # Load dữ liệu
            data_chamcong = self.data_manager.load_chamcong()
            
            # Lưu vào monthly_data
            self.monthly_data[period]['data_chamcong'] = data_chamcong
            self.monthly_data[period]['is_loaded'] = True
            
            print(f"✅ Đã load {len(data_chamcong)} nhân viên cho tháng {period}")
            
            # Nếu là tháng hiện tại, cập nhật UI
            if period == self.current_period:
                self.update_ui_with_data()
                if self.on_data_changed:
                    # Truyền đúng format cho callback
                    data_with_period = {
                        'data_chamcong': data_chamcong,
                        'period': period
                    }
                    self.on_data_changed(data_with_period)
            
            return True
            
        except Exception as e:
            print(f"❌ Lỗi load dữ liệu tháng {period}: {e}")
            return False
    
    def unload_month_data(self, period):
        """Gỡ dữ liệu tháng cụ thể"""
        try:
            if period in self.monthly_data:
                # Lưu lại data trước khi xóa để truyền cho callback
                old_data = self.monthly_data[period].get('data_chamcong', {})
                
                # Xóa dữ liệu
                self.monthly_data[period]['data_chamcong'] = {}
                self.monthly_data[period]['is_loaded'] = False
                print(f"🗑️ Đã gỡ dữ liệu tháng {period}")
                
                # Nếu là tháng hiện tại, cập nhật UI
                if period == self.current_period:
                    self.update_ui_with_data()
                    if self.on_data_changed:
                        # Truyền đúng format cho callback
                        data_with_period = {
                            'data_chamcong': {},  # Dữ liệu rỗng vì đã gỡ
                            'period': period
                        }
                        self.on_data_changed(data_with_period)
                
                return True
            return False
            
        except Exception as e:
            print(f"❌ Lỗi gỡ dữ liệu tháng {period}: {e}")
            return False
    
    def get_current_data(self):
        """Lấy dữ liệu tháng hiện tại"""
        if self.current_period in self.monthly_data:
            return self.monthly_data[self.current_period]['data_chamcong']
        return {}
    
    def get_chamcong_data(self):
        """Trả về dữ liệu chấm công cho các tab khác sử dụng (alias cho get_current_data)"""
        return self.get_current_data()
    
    def get_employees_list(self):
        """Trả về danh sách nhân viên có dữ liệu chấm công tháng hiện tại"""
        employees = []
        try:
            data_chamcong = self.get_current_data()
            
            for key, employee_data in data_chamcong.items():
                if isinstance(employee_data, dict):
                    # Tìm period keys (MM/YYYY format)
                    period_keys = [k for k in employee_data.keys() if '/' in str(k)]
                    if period_keys:
                        # Kiểm tra xem key có phải là MSNV không
                        if key.startswith('HTNV-'):
                            # Đây là MSNV, cần tìm tên tương ứng
                            msnv = key
                            name = self.get_name_by_msnv(msnv)
                            if name:
                                employees.append({
                                    'msnv': msnv,
                                    'name': name
                                })
                        else:
                            # Đây có thể là tên nhân viên
                            name = key
                            msnv = self.get_msnv_by_name(name)
                            if msnv:
                                employees.append({
                                    'msnv': msnv,
                                    'name': name
                                })
        except Exception as e:
            print(f"❌ Lỗi get_employees_list: {e}")
        
        return employees
    
    def get_name_by_msnv(self, msnv):
        """Lấy tên nhân viên theo MSNV từ file nhanvien.json"""
        try:
            employees = self.data_manager.load_nhanvien()
            for emp in employees:
                if len(emp) >= 3 and str(emp[2]).strip() == msnv:
                    return str(emp[0]).strip()
        except Exception as e:
            print(f"❌ Lỗi get_name_by_msnv: {e}")
        return None
    
    def get_msnv_by_name(self, name):
        """Lấy MSNV theo tên nhân viên từ file nhanvien.json"""
        try:
            employees = self.data_manager.load_nhanvien()
            for emp in employees:
                if len(emp) >= 3 and str(emp[0]).strip().lower() == name.lower():
                    return str(emp[2]).strip()
        except Exception as e:
            print(f"❌ Lỗi get_msnv_by_name: {e}")
        return None
    
    def load_selected_employees(self):
        """Tải danh sách nhân viên đã chọn từ file"""
        try:
            import os
            if os.path.exists('data/selected_employees.json'):
                with open('data/selected_employees.json', 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.selected_employees = set(data.get('employees', []))
            else:
                self.selected_employees = set()
        except Exception as e:
            print(f"Lỗi tải danh sách nhân viên: {e}")
            self.selected_employees = set()
    
    def save_selected_employees(self):
        """Lưu danh sách nhân viên được chọn vào file"""
        try:
            import os
            if not os.path.exists('data'):
                os.makedirs('data')
                
            data = {
                'employees': list(self.selected_employees),
                'timestamp': datetime.now().isoformat()
            }
            
            with open('data/selected_employees.json', 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Lỗi lưu danh sách nhân viên: {e}")
    
    def load_employee_mapping(self):
        """Load mapping nhân viên từ dữ liệu nhân viên"""
        try:
            # Load mapping từ file nếu có
            self.employee_mapper.load_mapping()
            
            # Cập nhật mapping từ dữ liệu nhân viên hiện tại
            nhanvien_data = self.data_manager.load_nhanvien()
            self.employee_mapper.load_from_nhanvien_data(nhanvien_data)
            
            # Lưu mapping mới
            self.employee_mapper.save_mapping()
            
            # print(f"Đã load mapping cho {len(self.employee_mapper.get_all_msnv())} nhân viên")
        except Exception as e:
            print(f"Lỗi load employee mapping: {e}")
    
    def refresh_employee_mapping(self):
        """Refresh mapping nhân viên khi có thay đổi"""
        try:
            self.load_employee_mapping()
            print("Đã refresh employee mapping")
        except Exception as e:
            print(f"Lỗi refresh employee mapping: {e}")
    
    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(8)
        main_layout.setContentsMargins(15, 15, 15, 15)
        
        # Header với tiêu đề và thông tin tháng
        header_panel = self.create_header_panel()
        main_layout.addWidget(header_panel)
        
        # Panel điều khiển
        control_panel = self.create_control_panel()
        main_layout.addWidget(control_panel)
        
        # Quy định loại công
        legend_panel = self.create_legend_panel()
        main_layout.addWidget(legend_panel)
        
        # Panel thông tin tổng quan
        self.info_panel = self.create_info_panel()
        main_layout.addWidget(self.info_panel)
        
        # Bảng tổng hợp
        self.table_widget = self.create_summary_table()
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.NoFrame)
        scroll_area.setWidget(self.table_widget)
        main_layout.addWidget(scroll_area)
    
    def create_import_icon(self):
        """Tạo icon import đơn giản"""
        pixmap = QPixmap(24, 24)
        pixmap.fill(Qt.transparent)
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Vẽ mũi tên xuống
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor("#007bff"))
        
        # Thân mũi tên
        painter.drawRect(10, 3, 4, 12)
        
        # Đầu mũi tên
        points = [
            QPoint(12, 15),  # Đỉnh
            QPoint(8, 11),   # Trái
            QPoint(16, 11)   # Phải
        ]
        painter.drawPolygon(points)
        
        # Đường ngang (biểu tượng file)
        painter.drawRect(6, 18, 12, 2)
        painter.drawRect(6, 21, 12, 2)
        
        painter.end()
        return QIcon(pixmap)
    
    def calculate_working_days(self, year, month):
        """Tính số ngày làm việc trong tháng (không tính chủ nhật)"""
        total_days = calendar.monthrange(year, month)[1]
        working_days = 0
        
        for day in range(1, total_days + 1):
            date = datetime(year, month, day)
            if date.weekday() != 6:  # 6 = Chủ nhật
                working_days += 1
        
        return working_days
    
    def create_header_panel(self):
        """Tạo header với tiêu đề và thông tin ngày làm việc"""
        header = QFrame()
        header.setStyleSheet("""
            QFrame {
                background-color: white;
                border-bottom: 1px solid #e9ecef;
                padding: 0px;
            }
        """)
        
        layout = QHBoxLayout(header)
        layout.setContentsMargins(0, 15, 0, 15)
        
        # Tiêu đề
        title = QLabel("Bảng công tổng hợp")
        title.setFont(QFont("Times New Roman", 18, QFont.Bold))
        title.setStyleSheet("color: #212529; background: transparent; border: none;")
        layout.addWidget(title)
        
        layout.addStretch()
        
        # Thông tin ngày làm việc
        self.working_days_info = QLabel()
        self.working_days_info.setFont(QFont("Times New Roman", 11))
        self.working_days_info.setStyleSheet("""
            color: #6c757d; 
            background: transparent; 
            border: none;
            padding: 0px;
        """)
        self.update_working_days_display()
        layout.addWidget(self.working_days_info)
        
        return header
    
    def update_working_days_display(self):
        """Cập nhật hiển thị số ngày làm việc dựa trên dữ liệu CSV"""
        try:
            # Lấy tháng từ combo box, đã được clean emoji
            if hasattr(self, 'combo_month'):
                month_text = self.combo_month.currentText()
                # Loại bỏ emoji và ký tự không phải số
                month_text_clean = ''.join(c for c in month_text if c.isdigit() or c == '/')
                if '/' in month_text_clean:
                    month = int(month_text_clean.split('/')[0])
                    year = int(month_text_clean.split('/')[1])
                else:
                    month = self.current_month
                    year = self.current_year
            else:
                month = self.current_month
                year = self.current_year
            
            month_year = f"{month:02d}/{year}"
            
            # Lấy số ngày từ dữ liệu
            total_days_in_data = self.get_max_days_from_data(month_year)
            
            # Tính số ngày làm việc thực tế (không tính chủ nhật)
            working_days = self.calculate_working_days(year, month)
            
            # Chỉ hiển thị thông tin của tháng đang được import
            if month_year in self.monthly_data and self.monthly_data[month_year]['is_loaded']:
                info_text = f"Tháng {month:02d}/{year}: {working_days}/{total_days_in_data} ngày làm việc"
                
                # Thêm thông tin export nếu có
                if hasattr(self, 'export_info') and self.export_info:
                    company = self.export_info.get('company', '')
                    export_date = self.export_info.get('export_date', '')
                    if export_date:
                        try:
                            dt = datetime.fromisoformat(export_date.replace('Z', '+00:00'))
                            export_date_formatted = dt.strftime('%d/%m/%Y %H:%M')
                        except:
                            export_date_formatted = export_date[:10]
                    else:
                        export_date_formatted = ""
                    
                    if company:
                        info_text += f" | {company}"
                    if export_date_formatted:
                        info_text += f" | Xuất: {export_date_formatted}"
            else:
                info_text = f"Tháng {month:02d}/{year}: Chưa có dữ liệu"
            
            # Kiểm tra xem working_days_info đã được tạo chưa
            if hasattr(self, 'working_days_info') and self.working_days_info:
                self.working_days_info.setText(info_text)
            
        except Exception as e:
            print(f"Lỗi update_working_days_display: {e}")
            if hasattr(self, 'working_days_info') and self.working_days_info:
                self.working_days_info.setText("Lỗi hiển thị thông tin ngày làm việc")
    
    def create_control_panel(self):
        """Tạo panel điều khiển với dropdown tháng và các nút"""
        panel = QFrame()
        panel.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 8px;
                padding: 10px;
            }
        """)
        
        layout = QHBoxLayout(panel)
        layout.setSpacing(15)
        
        # Dropdown chọn tháng
        month_label = QLabel("Tháng:")
        month_label.setFont(QFont("Arial", 10, QFont.Bold))
        layout.addWidget(month_label)
        
        self.combo_month = QComboBox()
        self.combo_month.setMinimumWidth(120)
        self.combo_month.setFont(QFont("Arial", 10))
        self.combo_month.currentTextChanged.connect(self.on_month_changed)
        layout.addWidget(self.combo_month)
        
        # Nút Load tháng
        self.btn_load_month = QPushButton("📂 Load tháng")
        self.btn_load_month.setStyleSheet("""
            QPushButton {
                background-color: #007bff;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
            QPushButton:pressed {
                background-color: #004085;
            }
        """)
        self.btn_load_month.clicked.connect(self.load_selected_month)
        layout.addWidget(self.btn_load_month)
        
        # Nút Gỡ import
        self.btn_unload_month = QPushButton("🗑️ Gỡ import")
        self.btn_unload_month.setStyleSheet("""
            QPushButton {
                background-color: #dc3545;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c82333;
            }
            QPushButton:pressed {
                background-color: #bd2130;
            }
        """)
        self.btn_unload_month.clicked.connect(self.unload_current_month)
        layout.addWidget(self.btn_unload_month)
        
        # Nút Import file
        self.btn_import = QPushButton("📁 Import file")
        self.btn_import.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #218838;
            }
            QPushButton:pressed {
                background-color: #1e7e34;
            }
        """)
        self.btn_import.clicked.connect(self.import_data)
        layout.addWidget(self.btn_import)
        
        # Nút Xóa file đã import
        self.btn_clear_imported = QPushButton("🗑️ Xóa file đã import")
        self.btn_clear_imported.setStyleSheet("""
            QPushButton {
                background-color: #ffc107;
                color: #212529;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #e0a800;
            }
            QPushButton:pressed {
                background-color: #d39e00;
            }
        """)
        self.btn_clear_imported.clicked.connect(self.clear_imported_file)
        layout.addWidget(self.btn_clear_imported)
        
        # Spacer
        layout.addStretch()
        
        # Thông tin trạng thái
        self.status_label = QLabel("Chưa có dữ liệu")
        self.status_label.setStyleSheet("color: #6c757d; font-style: italic;")
        layout.addWidget(self.status_label)
        
        # Cập nhật dropdown tháng
        self.update_month_dropdown()
        
        return panel
    
    def update_month_dropdown(self):
        """Cập nhật dropdown danh sách tháng"""
        try:
            self.combo_month.clear()
            
            # Thêm các tháng có dữ liệu
            available_periods = list(self.monthly_data.keys())
            available_periods.sort(reverse=True)  # Sắp xếp từ mới đến cũ
            
            for period in available_periods:
                status = "✅" if self.monthly_data[period]['is_loaded'] else "📁"
                display_text = f"{status} {period}"
                self.combo_month.addItem(display_text, period)
            
            # Thêm tháng hiện tại nếu chưa có
            if self.current_period not in available_periods:
                self.combo_month.addItem(f"📅 {self.current_period}", self.current_period)
            
            # Chọn tháng hiện tại
            index = self.combo_month.findData(self.current_period)
            if index >= 0:
                self.combo_month.setCurrentIndex(index)
                
        except Exception as e:
            print(f"❌ Lỗi update dropdown tháng: {e}")
    
    def on_month_changed(self, text):
        """Khi thay đổi tháng trong dropdown"""
        try:
            period = self.combo_month.currentData()
            if period and period != self.current_period:
                print(f"🔄 Chuyển sang tháng {period}")
                
                # Kiểm tra xem có phải đang import không
                if hasattr(self, '_is_importing') and self._is_importing:
                    print("⚠️ Đang trong quá trình import, bỏ qua chuyển tháng")
                    return
                    
                self.current_period = period
                try:
                    month_str, year_str = period.split('/')
                    self.current_month = int(month_str)
                    self.current_year = int(year_str)
                except Exception as e:
                    print(f"⚠️ Lỗi parse period {period}: {e}")
                
                # Chỉ cập nhật UI, không tự động load dữ liệu
                self.update_ui_with_data()
                self.update_status()
                
        except Exception as e:
            print(f"❌ Lỗi thay đổi tháng: {e}")
    
    def load_selected_month(self):
        """Load dữ liệu tháng được chọn"""
        try:
            period = self.combo_month.currentData()
            if period:
                print(f"📂 Load dữ liệu tháng {period}")
                
                # Kiểm tra xem đã load chưa
                if period in self.monthly_data and self.monthly_data[period]['is_loaded']:
                    reply = QMessageBox.question(
                        self,
                        "Xác nhận load lại",
                        f"Tháng {period} đã được load. Bạn có muốn load lại không?",
                        QMessageBox.Yes | QMessageBox.No,
                        QMessageBox.No
                    )
                    if reply == QMessageBox.No:
                        return
                
                # Load dữ liệu
                if period in self.monthly_data:
                    self.load_month_data(period)
                else:
                    self.find_and_load_month_file(period)
                
                # Cập nhật UI
                self.update_month_dropdown()
                self.update_status()
                
                if self.on_data_changed:
                    data_with_period = {
                        'data_chamcong': self.monthly_data[period].get('data_chamcong', {}),
                        'period': period
                    }
                    self.on_data_changed(data_with_period)
                
        except Exception as e:
            print(f"❌ Lỗi load tháng được chọn: {e}")
            QMessageBox.warning(self, "Lỗi", f"Không thể load dữ liệu tháng {period}: {str(e)}")
    
    def unload_current_month(self):
        """Gỡ dữ liệu tháng hiện tại"""
        try:
            period = self.current_period
            if period in self.monthly_data:
                reply = QMessageBox.question(
                    self, 
                    "Xác nhận gỡ dữ liệu", 
                    f"Bạn có chắc muốn gỡ dữ liệu tháng {period}?",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.No
                )
                
                if reply == QMessageBox.Yes:
                    self.unload_month_data(period)
                    self.update_month_dropdown()
                    self.update_status()
                    
        except Exception as e:
            print(f"❌ Lỗi gỡ dữ liệu tháng: {e}")
    
    def update_status(self):
        """Cập nhật thông tin trạng thái"""
        try:
            # Kiểm tra xem status_label đã được tạo chưa
            if not hasattr(self, 'status_label') or self.status_label is None:
                print("⚠️ status_label chưa được tạo, bỏ qua update_status")
                return
                
            period = self.current_period
            if period in self.monthly_data and self.monthly_data[period]['is_loaded']:
                data_count = len(self.monthly_data[period].get('data_chamcong', {}))
                # Chỉ hiển thị số nhân viên và tháng hiện tại
                self.status_label.setText(f"✅ Đã load {data_count} nhân viên - {period}")
                self.status_label.setStyleSheet("color: #28a745; font-weight: bold;")
            else:
                self.status_label.setText(f"📁 Chưa load dữ liệu - {period}")
                self.status_label.setStyleSheet("color: #6c757d; font-style: italic;")
                
        except Exception as e:
            print(f"❌ Lỗi update status: {e}")
            if hasattr(self, 'status_label') and self.status_label:
                self.status_label.setText("Lỗi cập nhật trạng thái")
    
    def update_ui_with_data(self):
        """Cập nhật UI với dữ liệu hiện tại"""
        try:
            # Cập nhật bảng tổng hợp (sử dụng method có sẵn)
            self.update_table()
            self.update_status()
            
        except Exception as e:
            print(f"❌ Lỗi update UI: {e}")
    
    def create_legend_panel(self):
        group = QGroupBox("Ký hiệu loại công")
        group.setFont(QFont("Times New Roman", 11))
        group.setStyleSheet("""
            QGroupBox {
                border: none;
                background-color: white;
                padding: 0px;
                font-family: "Times New Roman";
            }
            QGroupBox::title {
                color: #495057;
                subcontrol-origin: margin;
                left: 0px;
                padding: 0 5px 0 0px;
            }
        """)
        
        layout = QHBoxLayout(group)
        layout.setContentsMargins(0, 15, 0, 10)
        layout.setSpacing(30)
        
        # Tạo các ký hiệu đơn giản
        legend_items = [
            ("O", "Văn phòng"),
            ("W", "Công trường"),
            ("T", "Đào tạo"),
            ("P", "Nghỉ có phép"),
            ("N", "Nghỉ không phép")
        ]
        
        for code, desc in legend_items:
            item_layout = QHBoxLayout()
            item_layout.setSpacing(6)
            
            # Code
            code_label = QLabel(code)
            code_label.setFont(QFont("Times New Roman", 11, QFont.Bold))
            code_label.setStyleSheet("""
                color: #495057;
                background-color: #f8f9fa;
                border: 1px solid #ced4da;
                border-radius: 2px;
                padding: 2px 6px;
                min-width: 16px;
            """)
            code_label.setAlignment(Qt.AlignCenter)
            code_label.setFixedSize(24, 20)
            item_layout.addWidget(code_label)
            
            # Description
            desc_label = QLabel(desc)
            desc_label.setFont(QFont("Times New Roman", 10))
            desc_label.setStyleSheet("color: #6c757d;")
            item_layout.addWidget(desc_label)
            
            # Tạo widget container
            item_widget = QWidget()
            item_widget.setLayout(item_layout)
            layout.addWidget(item_widget)
        
        layout.addStretch()
        return group
    
    def create_summary_table(self):
        table = QTableWidget()
        table.setFont(QFont("Times New Roman", 10))
        
        # Khởi tạo với headers cơ bản, sẽ được cập nhật khi có dữ liệu
        headers = ["Tên nhân viên", "Chi tiết"]
        
        # Thêm các cột tổng hợp
        summary_headers = [
            "Tổng công\ntrường (W)", "Tổng văn\nphòng (O)", "Tổng đào\ntạo (T)", 
            "Nghỉ có\nphép (P)", "Nghỉ không\nphép (N)",
            "OT 150%\n(giờ)", "Chủ nhật\n200% (giờ)", "Lễ tết\n300% (giờ)",
            "Năng suất\nUT", "Năng suất\nPAUT", "Năng suất\nTOFD",
            "Ngày tính\nlương CB", "Tạm ứng\n(VNĐ)", "Chi phí\n(VNĐ)",
            "Khách sạn\n(VNĐ)", "Mua sắm\n(VNĐ)", "Điện thoại\n(VNĐ)", "Khác\n(VNĐ)",
            "Dự án", "Phương pháp\nNDT"
        ]
        headers.extend(summary_headers)
        
        table.setColumnCount(len(headers))
        table.setHorizontalHeaderLabels(headers)
        
        # Style cho table
        table.setStyleSheet("""
            QTableWidget {
                gridline-color: #e9ecef;
                font-family: "Times New Roman";
                font-size: 10pt;
                background-color: white;
                alternate-background-color: #fafbfc;
                border: 1px solid #e9ecef;
            }
            QHeaderView::section {
                background-color: #f8f9fa;
                padding: 8px 4px;
                border: none;
                border-right: 1px solid #e9ecef;
                border-bottom: 1px solid #e9ecef;
                font-weight: normal;
                font-family: "Times New Roman";
                font-size: 9pt;
                color: #495057;
                min-height: 40px;
            }
            QTableWidget::item {
                padding: 6px 4px;
                border: none;
                border-right: 1px solid #f1f3f4;
                border-bottom: 1px solid #f1f3f4;
                font-family: "Times New Roman";
            }
            QTableWidget::item:selected {
                border: 1px solid #ced4da;
            }
        """)
        
        # Resize columns - sẽ được cập nhật trong update_table
        header = table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Fixed)  # Tên nhân viên
        header.setSectionResizeMode(1, QHeaderView.Fixed)  # Chi tiết
        table.setColumnWidth(0, 150)
        table.setColumnWidth(1, 80)
        
        # Cố định chiều cao dòng - tăng lên để không bị che chữ
        table.verticalHeader().setDefaultSectionSize(40)
        table.verticalHeader().setSectionResizeMode(QHeaderView.Fixed)
        
        # Ẩn vertical header (số thứ tự dòng)
        table.verticalHeader().setVisible(False)
        
        # Alternating row colors
        table.setAlternatingRowColors(True)
        
        return table
    
    def create_info_panel(self):
        """Tạo panel hiển thị thông tin tổng quan"""
        panel = QGroupBox("Thông tin tổng quan")
        panel.setFont(QFont("Times New Roman", 10, QFont.Bold))
        panel.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #dee2e6;
                border-radius: 5px;
                margin-top: 1ex;
                padding-top: 10px;
                background-color: #f8f9fa;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: #495057;
            }
        """)
        
        layout = QHBoxLayout(panel)
        
        # Thông tin cơ bản
        basic_info = QLabel("Chưa có dữ liệu")
        basic_info.setFont(QFont("Times New Roman", 9))
        basic_info.setStyleSheet("color: #6c757d;")
        layout.addWidget(basic_info)
        
        # Thông tin chi tiết
        detail_info = QLabel("")
        detail_info.setFont(QFont("Times New Roman", 9))
        detail_info.setStyleSheet("color: #495057;")
        layout.addWidget(detail_info)
        
        # Lưu reference để cập nhật sau
        panel.basic_info = basic_info
        panel.detail_info = detail_info
        
        return panel
    
    def update_info_panel(self):
        """Cập nhật thông tin trong panel"""
        if not self.data_chamcong:
            self.info_panel.basic_info.setText("Chưa có dữ liệu")
            self.info_panel.detail_info.setText("")
            return
        
        # Tính toán thông tin tổng quan
        total_employees = len(self.data_chamcong)
        total_projects = set()
        total_methods = set()
        total_expenses = 0
        
        for employee_name, employee_data in self.data_chamcong.items():
            for month_year, month_data in employee_data.items():
                # Thu thập dự án và phương pháp
                days_detail = month_data.get('days_detail', {})
                for day_key, day_data in days_detail.items():
                    if isinstance(day_data, dict):
                        location = day_data.get('location', '')
                        if location:
                            total_projects.add(location)
                        
                        method = day_data.get('method', '')
                        if method:
                            total_methods.add(method)
                
                # Tổng chi phí = tổng các khoản: KS + MS + ĐT + Khác
                for day_key, day_data in month_data.get('days_detail', {}).items():
                    if isinstance(day_data, dict):
                        # Khách sạn
                        hotel = day_data.get('hotel_expense', 0)
                        total_expenses += float(hotel) if hotel else 0
                        
                        # Mua sắm
                        shopping = day_data.get('shopping_expense', 0)
                        total_expenses += float(shopping) if shopping else 0
                        
                        # Điện thoại
                        phone = day_data.get('phone_expense', 0)
                        total_expenses += float(phone) if phone else 0
                        
                        # Khác
                        other = day_data.get('other_expense', 0)
                        total_expenses += float(other) if other else 0
        
        # Cập nhật thông tin
        basic_text = f"Tổng nhân viên: {total_employees} | Dự án: {len(total_projects)} | Phương pháp NDT: {len(total_methods)}"
        detail_text = f"Tổng chi phí: {total_expenses:,} VNĐ | Dự án: {', '.join(list(total_projects)[:3])} | NDT: {', '.join(list(total_methods)[:3])}"
        
        self.info_panel.basic_info.setText(basic_text)
        self.info_panel.detail_info.setText(detail_text)
    
    def import_data(self):
        """Import dữ liệu chấm công từ file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            "Chọn file dữ liệu chấm công", 
            "", 
            "CSV Files (*.csv);;JSON Files (*.json);;Text Files (*.txt)"
        )
        
        if not file_path:
            return
        
        try:
            if file_path.endswith('.csv'):
                self.import_csv(file_path)
            elif file_path.endswith('.json'):
                self.import_json(file_path)
            elif file_path.endswith('.txt'):
                self.import_txt(file_path)
            
            # Lưu file đã import
            self.data_manager.save_imported_file("chamcong", file_path)
            
            self.update_table()
            self.update_info_panel()
            QMessageBox.information(self, "Thành công", "Đã import dữ liệu chấm công thành công!")
            
        except Exception as e:
            QMessageBox.warning(self, "Lỗi", f"Không thể import dữ liệu: {str(e)}")
    
    def import_csv(self, file_path):
        """Import từ file CSV"""
        with open(file_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                employee_name = row.get('ten_nv', '').strip()
                month_year = row.get('thang_nam', f"{self.current_month:02d}/{self.current_year}").strip()
                
                if employee_name and month_year:
                    if employee_name not in self.data_chamcong:
                        self.data_chamcong[employee_name] = {}
                    
                    # Import dữ liệu các ngày (format cũ cho bảng công)
                    days_data = {}
                    for i in range(1, 32):
                        day_value = row.get(f"ngay_{i}", "").strip()
                        if day_value:
                            days_data[f"day_{i}"] = day_value
                    
                    # Tạo days_detail (format mới cho phiếu lương)
                    days_detail = {}
                    
                    # Lấy các thông tin tổng từ CSV
                    total_ot_150 = float(row.get('ot_150', 0) or 0)
                    total_cn_200 = float(row.get('cn_200', 0) or 0)
                    total_le_300 = float(row.get('le_300', 0) or 0)
                    total_ns_ut = float(row.get('ns_ut', 0) or 0)
                    total_ns_paut = float(row.get('ns_paut', 0) or 0)
                    total_ns_tofd = float(row.get('ns_tofd', 0) or 0)
                    total_cp_mua_sam = float(row.get('cp_mua_sam', 0) or 0)
                    total_cp_khach_san = float(row.get('cp_khach_san', 0) or 0)
                    total_pc_di_lai = float(row.get('pc_di_lai', 0) or 0)
                    
                    # Đếm số ngày làm việc để phân bổ
                    working_days = sum(1 for i in range(1, 32) if row.get(f"ngay_{i}", "").strip() in ['W', 'O', 'T'])
                    
                    # Tạo days_detail từ dữ liệu CSV
                    for i in range(1, 32):
                        day_value = row.get(f"ngay_{i}", "").strip()
                        if day_value:
                            day_data = {
                                'type': day_value,
                                'overtime_hours': 0,
                                'location': '',
                                'method': '',
                                'phone_expense': 0,
                                'hotel_expense': 0,
                                'shopping_expense': 0,
                                'gas_expense': 0,
                                'paut_meters': 0,
                                'tofd_meters': 0,
                                'other_expense': 0
                            }
                            
                            # Phân bổ thêm giờ và chi phí cho các ngày làm việc
                            if day_value in ['W', 'O', 'T'] and working_days > 0:
                                # Phân bổ đều thêm giờ
                                day_data['overtime_hours'] = total_ot_150 / working_days if working_days > 0 else 0
                                
                                # Phân bổ chi phí
                                day_data['phone_expense'] = total_pc_di_lai / working_days if working_days > 0 else 0
                                day_data['hotel_expense'] = total_cp_khach_san / working_days if working_days > 0 else 0
                                day_data['shopping_expense'] = total_cp_mua_sam / working_days if working_days > 0 else 0
                                
                                # Phân bổ năng suất
                                day_data['paut_meters'] = total_ns_paut / working_days if working_days > 0 else 0
                                day_data['tofd_meters'] = total_ns_tofd / working_days if working_days > 0 else 0
                                
                                # Đặt địa điểm mặc định cho công trường
                                if day_value == 'W':
                                    day_data['location'] = 'Công trường'
                                    day_data['method'] = 'PAUT'
                            
                            days_detail[f"day_{i:02d}"] = day_data
                    
                    self.data_chamcong[employee_name][month_year] = {
                        'days': days_data,  # Format cũ cho bảng công
                        'days_detail': days_detail,  # Format mới cho phiếu lương
                        'ot_150': total_ot_150,
                        'sunday_200': total_cn_200,
                        'holiday_300': total_le_300,
                        'nang_suat_ut': total_ns_ut,
                        'nang_suat_paut': total_ns_paut,
                        'nang_suat_tofd': total_ns_tofd,
                        'ngay_tinh_luong': int(str(row.get('ngay_tinh_luong', 0) or 0)),
                        'tam_ung': float(row.get('tam_ung', 0) or 0),
                        'chi_phi_mua_sam': total_cp_mua_sam,
                        'chi_phi_khach_san': total_cp_khach_san,
                        'phu_cap_di_lai': total_pc_di_lai
                    }
        
        # Cập nhật trạng thái và available months
        self.is_data_imported = True
        self.available_months = []
        for employee_data in self.data_chamcong.values():
            for month_year in employee_data.keys():
                if month_year not in self.available_months:
                    self.available_months.append(month_year)
        
        # Cập nhật UI
        self.import_btn.setVisible(False)
        self.clear_btn.setVisible(True)
        
        # Cập nhật combo boxes với dữ liệu từ CSV
        self.populate_month_combo()
        self.populate_year_combo()
        if self.on_data_changed:
            # Truyền cả dữ liệu chấm công và period (nếu có)  
            data_with_period = {
                'data_chamcong': self.data_chamcong,
                'period': getattr(self, 'current_period', None)
            }
            self.on_data_changed(data_with_period)
    
    def import_json(self, file_path):
        """Import dữ liệu từ file JSON"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        
            # Kiểm tra format mới từ website
            if isinstance(data, dict) and 'employees' in data:
                print("Phát hiện format JSON mới từ website")
                self.import_website_format(data)
            else:
                # Format mới dạng period + data (mảng)
                if isinstance(data, dict) and 'period' in data and 'data' in data and isinstance(data.get('data'), list):
                    print("Phát hiện format JSON period+data (array)")
                    self.import_period_array_format(data)
                else:
                    print("Phát hiện format JSON cũ từ app")
                    self.import_app_format(data)
                
        except Exception as e:
            print(f"Lỗi import JSON: {e}")
            QMessageBox.critical(self, "Lỗi", f"Không thể import file JSON: {e}")
    
    def import_period_array_format(self, data):
        """Import JSON dạng { period: 'MM/YYYY', data: [[...], ...] }"""
        try:
            period = data.get('period', '')  # '07/2025'
            if not period or '/' not in period:
                raise ValueError("Thiếu hoặc sai định dạng period (MM/YYYY)")
            month_str, year_str = period.split('/')
            month_year = f"{int(month_str):02d}/{int(year_str)}"
            
            # Lưu period để truyền cho tab phiếu lương
            self.current_period = month_year
            
            rows = data.get('data', [])
            self.data_chamcong.clear()

            for row in rows:
                # Mapping chỉ mục:
                # 0: msnv, 1: name, 2: date dd/MM/YYYY, 3: type, 4: location, 5: method,
                # 6: day_shift '1'/'0', 7: night_shift '1'/'0',
                # 8: day_overtime_end HH:MM, 9: night_overtime_end HH:MM,
                # 10: overtime_hours (number),
                # 11: hotel_expense (number), 12: shopping_expense (number), 13: phone_expense (number), 14: other_expense (number),
                # 15: total_expense (number), 16: other_expense_desc, 17: work_note
                if not isinstance(row, list) or len(row) < 11:
                    continue
                msnv = str(row[0]).strip() if len(row) > 0 else ''
                name = str(row[1]).strip() if len(row) > 1 else ''
                date_str = str(row[2]).strip() if len(row) > 2 else ''
                work_type = str(row[3]).strip() if len(row) > 3 else ''
                location = str(row[4]).strip() if len(row) > 4 else ''
                method = str(row[5]).strip() if len(row) > 5 else ''
                day_shift = str(row[6]).strip() == '1' if len(row) > 6 else False
                night_shift = str(row[7]).strip() == '1' if len(row) > 7 else False
                day_ot_end = str(row[8]).strip() if len(row) > 8 else ''
                night_ot_end = str(row[9]).strip() if len(row) > 9 else ''
                try:
                    overtime_hours = float(row[10]) if len(row) > 10 and row[10] not in [None, ''] else 0.0
                except Exception:
                    overtime_hours = 0.0
                try:
                    hotel_expense = float(row[11]) if len(row) > 11 and row[11] not in [None, ''] else 0.0
                except Exception:
                    hotel_expense = 0.0
                try:
                    shopping_expense = float(row[12]) if len(row) > 12 and row[12] not in [None, ''] else 0.0
                except Exception:
                    shopping_expense = 0.0
                try:
                    phone_expense = float(row[13]) if len(row) > 13 and row[13] not in [None, ''] else 0.0
                except Exception:
                    phone_expense = 0.0
                try:
                    other_expense = float(row[14]) if len(row) > 14 and row[14] not in [None, ''] else 0.0
                except Exception:
                    other_expense = 0.0
                other_expense_desc = str(row[16]).strip() if len(row) > 16 else ''
                work_note = str(row[17]).strip() if len(row) > 17 else ''

                try:
                    day_num = int(date_str.split('/')[0])
                except Exception:
                    continue

                if not msnv:
                    # Theo yêu cầu mới: nếu không có MSNV thì bỏ qua record
                    continue

                # Lấy tên chuẩn theo MSNV từ cơ sở dữ liệu (nếu có)
                try:
                    mapped_name = self.employee_mapper.get_name_by_msnv(msnv)
                except Exception:
                    mapped_name = None
                effective_name = mapped_name or name or ''

                # Log kiểm soát map nhân viên (chỉ log một lần cho mỗi nhân viên)
                if msnv not in self.data_chamcong:
                    if mapped_name:
                        print(f"✅ ĐÃ TÌM THẤY NHÂN VIÊN TRONG DB: MSNV={msnv} | Tên='{mapped_name}'")
                    else:
                        print(f"⚠️ KHÔNG TÌM THẤY TRONG DB: MSNV={msnv} | Dùng tên từ file='{effective_name}'")

                # Khởi tạo cấu trúc nhân viên nếu chưa có (theo tháng/năm)
                if msnv not in self.data_chamcong:
                    self.data_chamcong[msnv] = {}
                
                # Khởi tạo cấu trúc cho tháng/năm cụ thể
                if month_year not in self.data_chamcong[msnv]:
                    self.data_chamcong[msnv][month_year] = {
                        'employee_info': {
                            'name': effective_name,
                            'msnv': msnv
                        },
                        'attendance_data': {},
                        'summary': {
                            'total_work_days': 0,
                            'total_office_days': 0,
                            'total_training_days': 0,
                            'total_leave_days': 0,
                            'total_absent_days': 0,
                            'total_overtime_hours': 0.0,
                            'total_expenses': 0.0,
                            'total_hotel': 0.0,
                            'total_shopping': 0.0,
                            'total_phone': 0.0,
                            'total_other': 0.0,
                            'paut_total_meters': 0.0,
                            'tofd_total_meters': 0.0,
                            'sunday_200_hours': 0.0,  # Khởi tạo giá trị mặc định
                            'construction_projects': [],
                            'ndt_methods_used': []
                        }
                    }

                # Lưu chi tiết theo ngày (key là '01','02',...)
                self.data_chamcong[msnv][month_year]['attendance_data'][f"{day_num:02d}"] = {
                    'type': work_type,
                    'location': location,
                    'method': method,
                    'day_shift': day_shift,
                    'night_shift': night_shift,
                    'day_overtime_end': day_ot_end,
                    'night_overtime_end': night_ot_end,
                    'overtime_hours': overtime_hours,
                    'hotel_expense': hotel_expense,
                    'shopping_expense': shopping_expense,
                    'phone_expense': phone_expense,
                    'other_expense': other_expense,
                    'paut_meters': 0.0,
                    'tofd_meters': 0.0,
                    'note': work_note,
                    'other_expense_desc': other_expense_desc
                }

                # Cập nhật tổng hợp cơ bản theo loại
                summary = self.data_chamcong[msnv][month_year]['summary']
                if work_type == 'W':
                    summary['total_work_days'] += 1
                elif work_type == 'O':
                    summary['total_office_days'] += 1
                elif work_type == 'T':
                    summary['total_training_days'] += 1
                elif work_type == 'P':
                    summary['total_leave_days'] += 1
                elif work_type == 'N':
                    summary['total_absent_days'] += 1

                # Thu thập dự án và phương pháp
                if location and location not in summary['construction_projects']:
                    summary['construction_projects'].append(location)
                if method and method not in summary['ndt_methods_used']:
                    summary['ndt_methods_used'].append(method)

                # Cộng dồn OT và chi phí
                summary['total_overtime_hours'] += overtime_hours
                summary['total_hotel'] += hotel_expense
                summary['total_shopping'] += shopping_expense
                summary['total_phone'] += phone_expense
                summary['total_other'] += other_expense
                summary['total_expenses'] += (hotel_expense + shopping_expense + phone_expense + other_expense)

                # Chủ nhật 200%: nếu là CN và có chấm công làm việc (W/O/T) → +8 giờ
                try:
                    # Thử parse theo format YYYY-MM-DD trước
                    if isinstance(date_str, str) and len(date_str.split('-')) == 3:
                        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
                    else:
                        # Nếu không được thì parse theo format dd/MM/YYYY
                        date_obj = datetime.strptime(date_str, '%d/%m/%Y')
                    
                    is_sunday = date_obj.weekday() == 6
                    if is_sunday:
                        print(f"📅 Ngày {date_str} là chủ nhật")
                except Exception as e:
                    print(f"⚠️ Lỗi kiểm tra chủ nhật cho ngày {date_str}: {e}")
                    is_sunday = False
                
                if is_sunday and work_type in ['W', 'O', 'T']:
                    if 'sunday_200_hours' not in summary:
                        summary['sunday_200_hours'] = 0.0
                    summary['sunday_200_hours'] += 8.0
                    print(f"✅ Cộng 8 giờ 200% cho ngày chủ nhật {date_str} - MSNV: {msnv}")

            # Cập nhật combo tháng/năm theo period hiện tại
            self.is_data_imported = True
            self.available_months = [month_year]
            self.import_btn.setVisible(False)
            self.clear_btn.setVisible(True)
            self.populate_month_combo()
            self.populate_year_combo()
            # Set tháng/năm đang chọn theo period
            self.combo_month.setCurrentText(f"{int(month_str):02d}")
            self.combo_year.setCurrentText(str(int(year_str)))
            self.update_working_days_display()
            # Refresh bảng để hiển thị dữ liệu tháng mới
            self.update_table()
            # Cập nhật info panel
            self.update_info_panel()
            if self.on_data_changed:
                # Truyền cả dữ liệu chấm công và period
                data_with_period = {
                    'data_chamcong': self.data_chamcong,
                    'period': getattr(self, 'current_period', month_year)
                }
                self.on_data_changed(data_with_period)
        except Exception as e:
            print(f"Lỗi import period+data format: {e}")
            raise e
    
    def import_website_format(self, data):
        """Import format JSON mới từ website"""
        try:
            # Đánh dấu đang trong quá trình import
            self._is_importing = True
            
            employees = data.get('employees', {})
            export_info = data.get('export_info', {})
            period = export_info.get('period', None)  # dạng 'MM/YYYY'
            
            if not period:
                raise ValueError("Thiếu thông tin period trong file")
                
            # Khởi tạo dữ liệu cho tháng mới
            if period not in self.monthly_data:
                self.monthly_data[period] = {
                    'data_chamcong': {},
                    'file_path': '',
                    'is_loaded': False
                }
            
            # Xử lý dữ liệu và tính toán chủ nhật 200%
            month_str, year_str = period.split('/')
            month = int(month_str)
            year = int(year_str)
            
            for msnv, employee_data in employees.items():
                attendance = employee_data.get('attendance', {})
                days_data = attendance.get('days', {})
                summary = attendance.get('summary', {})
                
                # Reset sunday_200_hours
                sunday_200_hours = 0.0
                
                # Duyệt qua tất cả các ngày để tìm chủ nhật có làm việc
                for day_key, day_data in days_data.items():
                    if isinstance(day_data, dict):
                        work_type = day_data.get('type', '')
                        
                        # Chỉ xử lý nếu có làm việc (W, O, T)
                        if work_type in ['W', 'O', 'T']:
                            # Xác định ngày từ key
                            day_num = None
                            try:
                                if day_key.startswith('day_'):
                                    day_num = int(day_key.replace('day_', ''))
                                elif day_key.isdigit():
                                    day_num = int(day_key)
                                elif '-' in day_key:  # Format YYYY-MM-DD
                                    day_num = int(day_key.split('-')[-1])
                            except:
                                continue
                                
                            if day_num and 1 <= day_num <= 31:
                                try:
                                    date_obj = datetime(year, month, day_num)
                                    is_sunday = date_obj.weekday() == 6
                                    
                                    if is_sunday:
                                        sunday_200_hours += 8.0
                                        print(f"✅ Tự động cộng 8 giờ 200% cho chủ nhật {day_num}/{month}/{year} - MSNV: {msnv}")
                                except ValueError:
                                    # Ngày không hợp lệ (như 31/2)
                                    continue
                
                # Cập nhật lại summary với giờ chủ nhật đã tính
                if 'summary' not in attendance:
                    attendance['summary'] = {}
                attendance['summary']['sunday_200_hours'] = sunday_200_hours
                
                # Cập nhật lại dữ liệu
                employee_data['attendance'] = attendance
                employees[msnv] = employee_data
            
            # Import dữ liệu đã được xử lý
            self.monthly_data[period]['data_chamcong'] = employees
            self.monthly_data[period]['is_loaded'] = True
            
            # Lưu dữ liệu vào file
            if not self.save_month_data(period):
                raise Exception("Không thể lưu dữ liệu vào file")
            
            # Cập nhật current_period và tháng/năm
            self.current_period = period
            try:
                month_str, year_str = period.split('/')
                self.current_month = int(month_str)
                self.current_year = int(year_str)
            except Exception as e:
                print(f"⚠️ Lỗi parse period {period}: {e}")
            
            # Cập nhật UI
            self.update_month_dropdown()
            
            # Đảm bảo combo box chọn đúng tháng vừa import
            if hasattr(self, 'combo_month'):
                index = self.combo_month.findText(period)
                if index >= 0:
                    self.combo_month.setCurrentIndex(index)
                    print(f"✅ Đã set combo box về tháng {period}")
            
            # Cập nhật bảng và thông tin
            self.update_ui_with_data()
            
            if self.on_data_changed:
                data_with_period = {
                    'data_chamcong': employees,
                    'period': period
                }
                self.on_data_changed(data_with_period)
            
            print(f"✅ Import thành công {len(employees)} nhân viên cho tháng {period}")
            QMessageBox.information(self, "Thành công", 
                f"Đã import thành công {len(employees)} nhân viên cho tháng {period}")
            
        except Exception as e:
            print(f"❌ Lỗi import website format: {e}")
            QMessageBox.critical(self, "Lỗi", f"Không thể import dữ liệu: {str(e)}")
            raise e
        finally:
            # Đảm bảo xóa flag khi import xong
            self._is_importing = False
    
    def import_app_format(self, data):
        """Import format JSON cũ từ app"""
        try:
            # Code cũ giữ nguyên
            if isinstance(data, list):
                self.data_chamcong.clear()
                
                for item in data:
                    if len(item) >= 3:
                        name = str(item[0]).strip()
                        msnv = str(item[2]).strip()
                        
                        if name and msnv:
                            # Cập nhật employee mapper
                            self.employee_mapper.update_employee(msnv, name, {
                                'name': name,
                                'msnv': msnv,
                                'cccd': str(item[1]) if len(item) > 1 else '',
                                'phone': str(item[3]) if len(item) > 3 else '',
                                'position': str(item[4]) if len(item) > 4 else '',
                                'department': str(item[5]) if len(item) > 5 else ''
                            })
                            
                            # Lưu dữ liệu với MSNV làm key
                            self.data_chamcong[msnv] = {
                                'employee_info': {
                                    'name': name,
                                    'msnv': msnv,
                                    'cccd': str(item[1]) if len(item) > 1 else '',
                                    'phone': str(item[3]) if len(item) > 3 else '',
                                    'position': str(item[4]) if len(item) > 4 else '',
                                    'department': str(item[5]) if len(item) > 5 else ''
                                },
                                'attendance_data': {},
                                'summary': {}
                            }
                
                print(f"Import thành công {len(self.data_chamcong)} nhân viên từ app")
                self.update_table()
                
        except Exception as e:
            print(f"Lỗi import app format: {e}")
            raise e
    
    def import_txt(self, file_path):
        """Import từ file TXT (format tùy chỉnh)"""
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()
            # Implement parsing logic based on your TXT format
            pass
        if self.on_data_changed:
            # Truyền cả dữ liệu chấm công và period (nếu có)
            data_with_period = {
                'data_chamcong': self.data_chamcong,
                'period': getattr(self, 'current_period', None)
            }
            self.on_data_changed(data_with_period)
    
    def highlight_sunday_columns(self, month, year, days_in_month):
        """Tô màu vàng cho các cột chủ nhật"""
        try:
            for day in range(1, days_in_month + 1):
                try:
                    date_obj = datetime(year, month, day)
                    weekday = date_obj.weekday()  # 0=Monday, 6=Sunday
                    
                    # Nếu là chủ nhật (weekday = 6)
                    if weekday == 6:
                        col_index = day + 1  # +2 cho "Tên nhân viên" và "Chi tiết", -1 vì day bắt đầu từ 1
                        
                        # Lưu thông tin cột chủ nhật để set background sau
                        if not hasattr(self, 'sunday_columns'):
                            self.sunday_columns = []
                        self.sunday_columns.append(col_index)
                        
                except ValueError:
                    # Bỏ qua ngày không hợp lệ
                    continue
                    
        except Exception as e:
            print(f"Lỗi khi tô màu chủ nhật: {e}")
    
    def get_max_days_from_data(self, month_year):
        """Lấy số ngày tối đa có trong dữ liệu CSV"""
        max_days = 0
        try:
            for employee in self.data_chamcong.values():
                if month_year in employee:
                    days_data = employee[month_year].get('days', {})
                    for day_key in days_data.keys():
                        if day_key.startswith('day_'):
                            try:
                                day_num = int(day_key.split('_')[1])
                                max_days = max(max_days, day_num)
                            except (ValueError, IndexError):
                                # Bỏ qua nếu format không đúng
                                continue
            
            # Fallback: nếu không có dữ liệu, dùng calendar
            if max_days == 0:
                try:
                    month = int(month_year.split('/')[0])
                    year = int(month_year.split('/')[1])
                    max_days = calendar.monthrange(year, month)[1]
                except (ValueError, IndexError):
                    # Fallback cuối cùng: dùng tháng hiện tại
                    max_days = 31
        except Exception as e:
            print(f"Lỗi trong get_max_days_from_data: {e}")
            max_days = 31
        
        return max_days

    def update_table(self):
        """Cập nhật bảng hiển thị"""
        try:
            # Kiểm tra xem table_widget đã được tạo chưa
            if not hasattr(self, 'table_widget') or self.table_widget is None:
                print("⚠️ table_widget chưa được tạo, bỏ qua update_table")
                return
                
            self.table_widget.setRowCount(0)
            # Xây header động gồm: Tên nhân viên | Chi tiết | Ngày 1..N | các cột tổng hợp
            
            # Sửa lỗi parsing combo box text chứa emoji
            if hasattr(self, 'combo_month'):
                month_text = self.combo_month.currentText()
                # Loại bỏ emoji và ký tự không phải số
                month_text_clean = ''.join(c for c in month_text if c.isdigit() or c == '/')
                if '/' in month_text_clean:
                    month = int(month_text_clean.split('/')[0])
                else:
                    month = self.current_month
            else:
                month = self.current_month
                
            if hasattr(self, 'combo_year'):
                year_text = self.combo_year.currentText()
                # Loại bỏ emoji và ký tự không phải số
                year_text_clean = ''.join(c for c in year_text if c.isdigit())
                if year_text_clean:
                    year = int(year_text_clean)
                else:
                    year = self.current_year
            else:
                year = self.current_year
                
            days_in_month = calendar.monthrange(year, month)[1]

            # Tạo header ngày kèm thứ (T2..T7, CN)
            def weekday_short_label(wd: int) -> str:
                # 0=Mon..6=Sun
                return ['T2', 'T3', 'T4', 'T5', 'T6', 'T7', 'CN'][wd]

            day_headers = []
            for d in range(1, days_in_month + 1):
                wd = datetime(year, month, d).weekday()
                day_headers.append(f"{d:02d}\n{weekday_short_label(wd)}")
            summary_headers = [
                "Tổng công\ntrường (W)", "Tổng văn\nphòng (O)", "Tổng đào\ntạo (T)",
                "Nghỉ có\nphép (P)", "Nghỉ không\nphép (N)",
                "OT 150%\n(giờ)", "Chủ nhật\n200% (giờ)", "Lễ tết\n300% (giờ)",
                "Năng suất\nUT", "Năng suất\nPAUT", "Năng suất\nTOFD",
                "Ngày tính\nlương CB", "Tạm ứng\n(VNĐ)", "Chi phí\n(VNĐ)",
                "Khách sạn\n(VNĐ)", "Mua sắm\n(VNĐ)", "Điện thoại\n(VNĐ)", "Khác\n(VNĐ)",
                "Dự án", "Phương pháp\nNDT"
            ]
            headers = ["Tên nhân viên", "Chi tiết"] + day_headers + summary_headers
            self.table_widget.setColumnCount(len(headers))
            self.table_widget.setHorizontalHeaderLabels(headers)

            # Resize tên + chi tiết
            header_view = self.table_widget.horizontalHeader()
            header_view.setSectionResizeMode(0, QHeaderView.Fixed)
            header_view.setSectionResizeMode(1, QHeaderView.Fixed)
            self.table_widget.setColumnWidth(0, 150)
            self.table_widget.setColumnWidth(1, 80)
            # Resize cột ngày
            for idx in range(2, 2 + days_in_month):
                header_view.setSectionResizeMode(idx, QHeaderView.Fixed)
                self.table_widget.setColumnWidth(idx, 40)
                # Tooltip chi tiết cho header ngày
                day_index = (idx - 2) + 1
                wd = datetime(year, month, day_index).weekday()
                tooltip = f"Ngày {day_index:02d}/{month:02d}/{year} - {['Thứ 2','Thứ 3','Thứ 4','Thứ 5','Thứ 6','Thứ 7','Chủ nhật'][wd]}"
                item = self.table_widget.horizontalHeaderItem(idx)
                if item:
                    item.setToolTip(tooltip)

            # Tính các cột chủ nhật
            sunday_cols = set()
            for d in range(1, days_in_month + 1):
                if datetime(year, month, d).weekday() == 6:
                    sunday_cols.add(2 + (d - 1))
            # Tô đậm chữ header cho các cột Chủ nhật
            for col in sunday_cols:
                header_item = self.table_widget.horizontalHeaderItem(col)
                if header_item:
                    font = header_item.font()
                    font.setBold(True)
                    header_item.setFont(font)

            # Màu theo loại công
            def color_for_type(t):
                if t == 'W':
                    return QColor("#d4edda")  # xanh lá
                if t == 'O':
                    return QColor("#d1ecf1")  # xanh dương nhạt
                if t == 'T':
                    return QColor("#fff3cd")  # vàng nhạt
                if t == 'P':
                    return QColor("#f8d7da")  # đỏ nhạt
                if t == 'N':
                    return QColor("#f5c6cb")  # đỏ đậm hơn
                return QColor("#f8f9fa")

            # Lấy tháng/năm hiện tại để hiển thị
            current_month_year = f"{month:02d}/{year}"
            
            # Lấy dữ liệu từ monthly_data thay vì data_chamcong
            if current_month_year not in self.monthly_data or not self.monthly_data[current_month_year]['is_loaded']:
                print(f"⚠️ Không có dữ liệu cho tháng {current_month_year}")
                return
            
            employees_data = self.monthly_data[current_month_year]['data_chamcong']
            print(f"🔍 Tìm thấy {len(employees_data)} nhân viên cho tháng {current_month_year}")
            
            # Đổ dữ liệu từng nhân viên
            for msnv, employee_data in employees_data.items():
                # Lấy thông tin nhân viên từ website format
                info = employee_data.get('info', {})
                attendance = employee_data.get('attendance', {})
                summary = attendance.get('summary', {})
                days_data = attendance.get('days', {})
                
                # Lấy tên từ info hoặc dùng MSNV
                employee_name = info.get('name', msnv)
                
                print(f"📋 Hiển thị nhân viên: {msnv} - {employee_name}")

                row = self.table_widget.rowCount()
                self.table_widget.insertRow(row)

                # Tên nhân viên
                self.table_widget.setItem(row, 0, QTableWidgetItem(employee_name))

                # Nút chi tiết
                detail_btn = QPushButton("Chi tiết")
                detail_btn.clicked.connect(lambda checked, m=msnv: self.show_detail(m))
                self.table_widget.setCellWidget(row, 1, detail_btn)

                # Cột ngày 1..N - chuyển đổi từ format website
                print(f"🔍 Debug dữ liệu cho {msnv}:")
                print(f"   - info keys: {list(info.keys())}")
                print(f"   - attendance keys: {list(attendance.keys())}")
                print(f"   - days_data keys: {list(days_data.keys()) if days_data else 'None'}")
                
                # Thử nhiều format key khác nhau
                for d in range(1, days_in_month + 1):
                    col = 2 + (d - 1)
                    day_value = ""
                    
                    # Thử các format key khác nhau
                    possible_keys = [
                        f"day_{d:02d}",      # day_01, day_02...
                        f"{d:02d}",          # 01, 02...
                        f"day_{d}",          # day_1, day_2...
                        str(d),              # 1, 2...
                        f"{d}",              # 1, 2...
                        f"2025-07-{d:02d}"   # YYYY-MM-DD format
                    ]
                    
                    for key in possible_keys:
                        if key in days_data:
                            day_info = days_data[key]
                            if isinstance(day_info, dict):
                                day_value = day_info.get('type', '')
                            else:
                                day_value = str(day_info)
                            if day_value:
                                print(f"   - Ngày {d}: key='{key}', value='{day_value}'")
                                break
                    
                    # Hiển thị dữ liệu
                    item = QTableWidgetItem(day_value)
                    # Chủ nhật tô vàng ưu tiên
                    if col in sunday_cols:
                        item.setBackground(QColor("#fff3cd"))
                        item.setData(Qt.UserRole, 'sunday')
                    else:
                        item.setBackground(color_for_type(day_value))
                    self.table_widget.setItem(row, col, item)

                # Bắt đầu cột tổng hợp sau các cột ngày
                base = 2 + days_in_month
                def set_summary(col_offset, value):
                    self.table_widget.setItem(row, base + col_offset, QTableWidgetItem(str(value)))

                # Lấy summary từ website format
                set_summary(0, summary.get('total_work_days', 0))
                set_summary(1, summary.get('total_office_days', 0))
                set_summary(2, summary.get('total_training_days', 0))
                set_summary(3, summary.get('total_leave_days', 0))
                set_summary(4, summary.get('total_absent_days', 0))
                set_summary(5, summary.get('total_overtime_hours', 0))
                set_summary(6, summary.get('sunday_200_hours', 0))
                set_summary(7, summary.get('holiday_300_hours', 0))
                set_summary(8, summary.get('ut_total_meters', 0))
                set_summary(9, summary.get('total_paut_meters', 0))
                set_summary(10, summary.get('total_tofd_meters', 0))
                set_summary(11, summary.get('base_salary_days', 0))
                set_summary(12, summary.get('advance_amount', 0))
                set_summary(13, summary.get('total_expenses', 0))
                set_summary(14, summary.get('total_hotel_expense', 0))
                set_summary(15, summary.get('total_shopping_expense', 0))
                set_summary(16, summary.get('total_phone_expense', 0))
                set_summary(17, summary.get('total_other_expense', 0))
                set_summary(18, ", ".join(summary.get('construction_projects', [])))
                set_summary(19, ", ".join(summary.get('ndt_methods_used', [])))
        
        except Exception as e:
            print(f"Lỗi update table: {e}")
    
    def show_detail(self, msnv):
        """Hiển thị chi tiết chấm công của nhân viên"""
        try:
            # Lấy tháng/năm hiện tại
            month = int(self.combo_month.currentText()) if hasattr(self, 'combo_month') else self.current_month
            year = int(self.combo_year.currentText()) if hasattr(self, 'combo_year') else self.current_year
            current_month_year = f"{month:02d}/{year}"
            
            if msnv in self.data_chamcong and current_month_year in self.data_chamcong[msnv]:
                data = self.data_chamcong[msnv][current_month_year]
                employee_info = data.get('employee_info', {})
                attendance_data = data.get('attendance_data', {})
                
                # Tạo dialog hiển thị chi tiết
                detail_dialog = QDialog(self)
                detail_dialog.setWindowTitle(f"Chi tiết chấm công - {employee_info.get('name', '')}")
                detail_dialog.setModal(True)
                detail_dialog.resize(800, 600)
                
                layout = QVBoxLayout()
                
                # Thông tin nhân viên
                info_label = QLabel(f"MSNV: {msnv} | Tên: {employee_info.get('name', '')}")
                layout.addWidget(info_label)
                
                # Bảng chi tiết
                table = QTableWidget()
                table.setColumnCount(8)
                table.setHorizontalHeaderLabels([
                    "Ngày", "Loại", "Địa điểm", "Phương pháp", 
                    "PAUT (m)", "TOFD (m)", "Ca", "Ghi chú"
                ])
                
                # Điền dữ liệu
                for day_num, day_data in attendance_data.items():
                    row = table.rowCount()
                    table.insertRow(row)
                    
                    table.setItem(row, 0, QTableWidgetItem(day_num))
                    table.setItem(row, 1, QTableWidgetItem(day_data.get('type', '')))
                    table.setItem(row, 2, QTableWidgetItem(day_data.get('location', '')))
                    table.setItem(row, 3, QTableWidgetItem(day_data.get('method', '')))
                    table.setItem(row, 4, QTableWidgetItem(str(day_data.get('paut_meters', 0))))
                    table.setItem(row, 5, QTableWidgetItem(str(day_data.get('tofd_meters', 0))))
                    
                    shift_text = ""
                    if day_data.get('day_shift'):
                        shift_text += "Ngày"
                    if day_data.get('night_shift'):
                        if shift_text:
                            shift_text += " + "
                        shift_text += "Đêm"
                    
                    table.setItem(row, 6, QTableWidgetItem(shift_text))
                    table.setItem(row, 7, QTableWidgetItem(day_data.get('note', '')))
                
                layout.addWidget(table)
                detail_dialog.setLayout(layout)
                detail_dialog.exec_()
                
        except Exception as e:
            print(f"Lỗi hiển thị chi tiết: {e}")
            QMessageBox.warning(self, "Lỗi", f"Không thể hiển thị chi tiết: {e}")
    
    def export_report(self):
        """Xuất báo cáo Excel"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, 
            "Lưu báo cáo", 
            f"BangCong_{self.combo_month.currentText()}_{self.combo_year.currentText()}.csv", 
            "CSV Files (*.csv)"
        )
        
        if file_path:
            try:
                # Export logic here
                QMessageBox.information(self, "Thành công", f"Đã xuất báo cáo: {file_path}")
            except Exception as e:
                QMessageBox.warning(self, "Lỗi", f"Không thể xuất báo cáo: {str(e)}") 

    def show_employee_selection(self):
        """Hiển thị dialog chọn nhân viên"""
        try:
            dialog = EmployeeSelectionDialog(self)
            if dialog.exec_() == QDialog.Accepted:
                self.selected_employees = dialog.get_selected_employees()
                self.save_selected_employees()
                self.update_table()
        except Exception as e:
            print(f"Lỗi hiển thị dialog chọn nhân viên: {e}")
    
    def refresh_employee_data(self):
        """Tự động cập nhật dữ liệu nhân viên khi có thay đổi"""
        try:
            print("Đang cập nhật dữ liệu nhân viên bảng công...")
            
            # Reload dữ liệu nhân viên
            self.load_selected_employees()
            
            # Refresh employee mapping
            self.refresh_employee_mapping()
            
            # Refresh employee selection dialog nếu đang mở
            if hasattr(self, 'employee_dialog') and self.employee_dialog:
                self.employee_dialog.load_employees_from_tabs()
            
            print("Đã cập nhật xong dữ liệu nhân viên bảng công")
            
        except Exception as e:
            print(f"Lỗi cập nhật dữ liệu nhân viên bảng công: {e}")
    
    def check_and_add_new_companies(self):
        """Kiểm tra và hiện popup thêm công ty mới ngay sau khi import"""
        try:
            # print("=== KIỂM TRA CÔNG TY MỚI SAU KHI IMPORT ===")
            
            # Khởi tạo CompanyMatcher
            company_matcher = CompanyMatcher()
            
            # Load quy định phụ cấp hiện tại
            ds_luong, ds_phu_cap = self.data_manager.load_quydinh_luong()
            if not ds_phu_cap:
                # print("Debug: Không có quy định phụ cấp nào")
                return
                
            # Tạo danh sách công ty chuẩn
            company_list = [phu_cap[0] for phu_cap in ds_phu_cap 
                          if isinstance(phu_cap, list) and len(phu_cap) >= 3 and phu_cap[0]]
            
            # print(f"Debug: Danh sách công ty hiện tại: {company_list}")
            
            # Thu thập tất cả location từ dữ liệu chấm công
            all_locations = set()
            for employee_name, employee_data in self.data_chamcong.items():
                for month_year, month_data in employee_data.items():
                    if isinstance(month_data, dict) and 'days_detail' in month_data:
                        for day_key, day_data in month_data['days_detail'].items():
                            if isinstance(day_data, dict) and 'location' in day_data:
                                location = day_data['location']
                                if location and location.strip():
                                    all_locations.add(location.strip())
            
            # print(f"Debug: Tất cả location tìm thấy: {sorted(all_locations)}")
            
            # Kiểm tra từng location
            new_companies = []
            for location in sorted(all_locations):
                matched_company, similarity_score = company_matcher.match_company(location, company_list)
                # print(f"Debug: '{location}' -> '{matched_company}' (score: {similarity_score:.3f})")
                
                if similarity_score < 0.7:
                    new_companies.append(location)
                    # print(f"Debug: Phát hiện công ty mới: '{location}'")
            
            # Hiện popup cho từng công ty mới
            if new_companies:
                print(f"Debug: Tìm thấy {len(new_companies)} công ty mới: {new_companies}")
                
                for i, company_name in enumerate(new_companies, 1):
                    # print(f"Debug: Hiện popup {i}/{len(new_companies)} cho '{company_name}'")
                    
                    # Hiện popup thêm công ty mới - BLOCK HOÀN TOÀN
                    dialog = NewCompanyDialog(company_name, self)
                    dialog.setWindowTitle(f"Thêm công ty mới ({i}/{len(new_companies)}): {company_name}")
                    
                    # Hiển thị popup và BLOCK tất cả thao tác khác
                    # User PHẢI điền xong và bấm Lưu mới được thoát
                    result = dialog.exec_()
                    
                    # Chỉ có thể là Accepted vì không có nút Hủy
                    if result == QDialog.Accepted:
                        result_data = dialog.get_result()
                        if result_data:
                            # Thêm công ty mới vào quy định phụ cấp
                            new_company = [
                                result_data['company_name'],
                                result_data['don_gia_le'],
                                result_data['chi_phi']
                            ]
                            
                            # Cập nhật danh sách phụ cấp
                            ds_phu_cap.append(new_company)
                            
                            # Lưu vào file
                            # print(f"Debug: Đang lưu công ty mới '{result_data['company_name']}' vào file...")
                            self.data_manager.save_quydinh_luong(ds_luong, ds_phu_cap)
                            # print(f"Debug: Đã lưu xong công ty mới '{result_data['company_name']}'")
                            
                            # Cập nhật CompanyMatcher
                            company_matcher.add_company_alias(
                                result_data['company_name'], 
                                result_data['company_name']
                            )
                            
                            # print(f"Debug: Đã thêm công ty mới '{result_data['company_name']}' vào quy định phụ cấp")
                            
                            # Cập nhật danh sách công ty chuẩn
                            company_list.append(result_data['company_name'])
                            
                            # Thông báo cho Tab quy định lương refresh
                            if self.on_quydinh_changed:
                                self.on_quydinh_changed()
                                # print(f"Debug: Đã thông báo refresh Tab quy định lương")
                        else:
                            # print(f"Debug: Lỗi - không có dữ liệu từ popup cho '{company_name}'")
                            pass
                    # Không còn else vì không có nút Hủy
                
                # Thông báo hoàn thành
                QMessageBox.information(
                    self, 
                    "Hoàn thành", 
                    f"Đã xử lý xong {len(new_companies)} công ty mới!\n\n"
                    "Các công ty mới đã được thêm vào quy định phụ cấp công trường."
                )
            else:
                # print("Debug: Không có công ty mới nào")
                pass
        except Exception as e:
            print(f"Lỗi kiểm tra công ty mới: {e}")
            import traceback
            traceback.print_exc()

    def populate_month_combo(self):
        """Cập nhật combo box tháng"""
        try:
            if hasattr(self, 'combo_month'):
                self.combo_month.clear()
                # Thêm các tháng có dữ liệu
                for period in sorted(self.available_months, reverse=True):
                    self.combo_month.addItem(period)
                # Chọn tháng hiện tại
                current_period = f"{self.current_month:02d}/{self.current_year}"
                index = self.combo_month.findText(current_period)
                if index >= 0:
                    self.combo_month.setCurrentIndex(index)
        except Exception as e:
            print(f"Lỗi populate_month_combo: {e}")

    def populate_year_combo(self):
        """Cập nhật combo box năm"""
        try:
            if hasattr(self, 'combo_year'):
                self.combo_year.clear()
                # Lấy danh sách năm từ available_months
                years = set()
                for period in self.available_months:
                    if '/' in period:
                        year = period.split('/')[1]
                        years.add(year)
                # Thêm các năm vào combo
                for year in sorted(years, reverse=True):
                    self.combo_year.addItem(year)
                # Chọn năm hiện tại
                index = self.combo_year.findText(str(self.current_year))
                if index >= 0:
                    self.combo_year.setCurrentIndex(index)
        except Exception as e:
            print(f"Lỗi populate_year_combo: {e}")

    def save_month_data(self, period):
        """Lưu dữ liệu tháng vào file"""
        try:
            if period not in self.monthly_data:
                return False
                
            # Tạo tên file theo format: chamcong_MM_YYYY.json
            month_str, year_str = period.split('/')
            filename = f"chamcong_{month_str}_{year_str}.json"
            file_path = os.path.join(self.data_manager.data_dir, filename)
            
            # Chuẩn bị dữ liệu để lưu
            save_data = {
                'export_info': {
                    'period': period,
                    'export_date': datetime.now().isoformat(),
                    'company': 'Hitech NDT'
                },
                'employees': self.monthly_data[period].get('data_chamcong', {})
            }
            
            # Lưu file
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(save_data, f, ensure_ascii=False, indent=2)
            
            # Cập nhật đường dẫn file trong monthly_data
            self.monthly_data[period]['file_path'] = file_path
            print(f"✅ Đã lưu dữ liệu tháng {period} vào file: {file_path}")
            return True
            
        except Exception as e:
            print(f"❌ Lỗi lưu dữ liệu tháng {period}: {e}")
            return False

    def auto_load_imported_file(self):
        """Tự động load file chấm công đã import trước đó"""
        try:
            imported_file_path = self.data_manager.get_imported_file_path("chamcong")
            if imported_file_path and os.path.exists(imported_file_path):
                print(f"🔄 Tự động load file đã import: {imported_file_path}")
                if imported_file_path.endswith('.json'):
                    self.import_json(imported_file_path)
                elif imported_file_path.endswith('.csv'):
                    self.import_csv(imported_file_path)
                elif imported_file_path.endswith('.txt'):
                    self.import_txt(imported_file_path)
                print("✅ Đã tự động load file chấm công đã import")
        except Exception as e:
            print(f"❌ Lỗi tự động load file đã import: {e}")

    def clear_imported_file(self):
        """Xóa file đã import để có thể import file mới"""
        try:
            reply = QMessageBox.question(
                self, 
                "Xác nhận", 
                "Bạn có chắc muốn xóa file đã import?\nSau đó bạn có thể import file mới.",
                QMessageBox.Yes | QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                self.data_manager.remove_imported_file("chamcong")
                # Xóa dữ liệu hiện tại
                self.monthly_data = {}
                self.data_chamcong = {}
                self.available_months = []
                self.update_table()
                self.update_info_panel()
                QMessageBox.information(self, "Thành công", "Đã xóa file đã import!")
        except Exception as e:
            QMessageBox.warning(self, "Lỗi", f"Không thể xóa file đã import: {str(e)}")

