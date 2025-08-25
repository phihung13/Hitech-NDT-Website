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
            }
                         QHeaderView::section {
                 background-color: #f8f9fa;
                 padding: 8px 4px;
                 border: 1px solid #e9ecef;
                 font-weight: bold;
                 font-family: "Times New Roman";
                 color: #495057;
                 min-height: 40px;
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
        self.data_manager = DataManager()  # Thêm data_manager
        self.data_chamcong = {}  # Dictionary lưu dữ liệu chấm công
        self.current_month = datetime.now().month
        self.current_year = datetime.now().year
        self.is_data_imported = False  # Trạng thái đã import dữ liệu
        self.available_months = []  # Danh sách tháng có trong CSV
        self.on_data_changed = on_data_changed
        self.on_quydinh_changed = on_quydinh_changed  # Callback để refresh quy định lương
        self.selected_employees = set()  # Set nhân viên được chọn để hiển thị
        self.load_selected_employees()  # Tải danh sách nhân viên đã chọn
        self.init_ui()
    
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
        main_layout.addWidget(self.table_widget)
    
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
        month = int(self.combo_month.currentText()) if hasattr(self, 'combo_month') else self.current_month
        year = int(self.combo_year.currentText()) if hasattr(self, 'combo_year') else self.current_year
        month_year = f"{month:02d}/{year}"
        
        # Lấy số ngày từ dữ liệu CSV
        total_days_in_data = self.get_max_days_from_data(month_year)
        
        # Tính số ngày làm việc thực tế (không tính chủ nhật)
        working_days = self.calculate_working_days(year, month)
        
        info_text = f"Tháng {month:02d}/{year}: {working_days}/{total_days_in_data} ngày làm việc"
        
        # Thêm thông tin export nếu có
        if hasattr(self, 'export_info') and self.export_info:
            company = self.export_info.get('company', '')
            export_date = self.export_info.get('export_date', '')
            if export_date:
                try:
                    # Format ngày xuất
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
        
        self.working_days_info.setText(info_text)
    
    def create_control_panel(self):
        group = QGroupBox()
        group.setStyleSheet("""
            QGroupBox {
                border: none;
                background-color: white;
                padding: 0px;
                font-family: "Times New Roman";
            }
        """)
        
        layout = QHBoxLayout(group)
        layout.setContentsMargins(0, 10, 0, 10)
        layout.setSpacing(20)
        
        # Import/Clear dữ liệu
        self.import_btn = QPushButton("Import dữ liệu")
        self.import_btn.setFont(QFont("Times New Roman", 10))
        self.import_btn.setStyleSheet("""
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
        self.import_btn.clicked.connect(self.import_data)
        layout.addWidget(self.import_btn)
        
        # Nút Clear (ẩn ban đầu)
        self.clear_btn = QPushButton("Gỡ import")
        self.clear_btn.setFont(QFont("Times New Roman", 10))
        self.clear_btn.setStyleSheet("""
            QPushButton {
                background-color: #dc3545;
                color: white;
                border: none;
                border-radius: 2px;
                padding: 8px 16px;
                font-family: "Times New Roman";
            }
            QPushButton:hover {
                background-color: #c82333;
            }
        """)
        self.clear_btn.clicked.connect(self.clear_data)
        self.clear_btn.setVisible(False)  # Ẩn ban đầu
        layout.addWidget(self.clear_btn)
        
        # Nút Select nhân viên
        self.select_employees_btn = QPushButton("Select nhân viên")
        self.select_employees_btn.setFont(QFont("Times New Roman", 10))
        self.select_employees_btn.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                border: none;
                border-radius: 2px;
                padding: 8px 16px;
                font-family: "Times New Roman";
            }
            QPushButton:hover {
                background-color: #218838;
            }
        """)
        self.select_employees_btn.clicked.connect(self.show_employee_selection)
        layout.addWidget(self.select_employees_btn)
        

        
        layout.addStretch()
        
        # Chọn tháng/năm đơn giản
        month_label = QLabel("Tháng:")
        month_label.setFont(QFont("Times New Roman", 10))
        month_label.setStyleSheet("color: #495057;")
        layout.addWidget(month_label)
        
        self.combo_month = QComboBox()
        self.combo_month.setFont(QFont("Times New Roman", 10))
        self.combo_month.setStyleSheet("""
            QComboBox {
                border: 1px solid #ced4da;
                border-radius: 2px;
                padding: 6px 8px;
                background-color: white;
                font-family: "Times New Roman";
                min-width: 50px;
            }
            QComboBox:focus {
                border-color: #495057;
            }
        """)
        self.populate_month_combo()
        self.combo_month.currentTextChanged.connect(self.on_month_year_changed)
        layout.addWidget(self.combo_month)
        
        year_label = QLabel("Năm:")
        year_label.setFont(QFont("Times New Roman", 10))
        year_label.setStyleSheet("color: #495057;")
        layout.addWidget(year_label)
        
        self.combo_year = QComboBox()
        self.combo_year.setFont(QFont("Times New Roman", 10))
        self.combo_year.setStyleSheet("""
            QComboBox {
                border: 1px solid #ced4da;
                border-radius: 2px;
                padding: 6px 8px;
                background-color: white;
                font-family: "Times New Roman";
                min-width: 70px;
            }
            QComboBox:focus {
                border-color: #495057;
            }
        """)
        self.populate_year_combo()
        self.combo_year.currentTextChanged.connect(self.on_month_year_changed)
        layout.addWidget(self.combo_year)
        
        layout.addStretch()
        
        # Xuất báo cáo đơn giản
        export_btn = QPushButton("Xuất báo cáo")
        export_btn.setFont(QFont("Times New Roman", 10))
        export_btn.setStyleSheet("""
            QPushButton {
                background-color: white;
                color: #495057;
                border: 1px solid #ced4da;
                border-radius: 2px;
                padding: 8px 16px;
                font-family: "Times New Roman";
            }
            QPushButton:hover {
                background-color: #f8f9fa;
                border-color: #495057;
            }
        """)
        export_btn.clicked.connect(self.export_report)
        layout.addWidget(export_btn)
        
        return group
    
    def populate_month_combo(self):
        """Populate month combo dựa trên trạng thái import"""
        self.combo_month.blockSignals(True)
        self.combo_month.clear()
        
        if self.is_data_imported:
            # Chỉ hiển thị các tháng có trong dữ liệu CSV
            for month_year in sorted(self.available_months):
                month = month_year.split('/')[0]
                if month not in [self.combo_month.itemText(i) for i in range(self.combo_month.count())]:
                    self.combo_month.addItem(month)
            if self.combo_month.count() > 0:
                self.combo_month.setCurrentIndex(0)
        else:
            # Hiển thị tất cả tháng
            for i in range(1, 13):
                self.combo_month.addItem(f"{i:02d}")
            self.combo_month.setCurrentText(f"{self.current_month:02d}")
        
        self.combo_month.blockSignals(False)
    
    def populate_year_combo(self):
        """Populate year combo dựa trên trạng thái import"""
        self.combo_year.blockSignals(True)
        self.combo_year.clear()
        
        if self.is_data_imported:
            # Chỉ hiển thị các năm có trong dữ liệu CSV
            years = set()
            for month_year in self.available_months:
                year = month_year.split('/')[1]
                years.add(year)
            for year in sorted(years):
                self.combo_year.addItem(year)
            if self.combo_year.count() > 0:
                self.combo_year.setCurrentIndex(0)
        else:
            # Hiển thị tất cả năm
            for year in range(2020, 2030):
                self.combo_year.addItem(str(year))
            self.combo_year.setCurrentText(str(self.current_year))
        
        self.combo_year.blockSignals(False)
    
    def on_month_year_changed(self):
        """Xử lý khi thay đổi tháng/năm"""
        self.update_working_days_display()
        self.update_table()
    
    def clear_data(self):
        """Gỗ bỏ dữ liệu import và reset về trạng thái ban đầu"""
        reply = QMessageBox.question(
            self, 
            "Xác nhận", 
            "Bạn có chắc muốn gỡ bỏ dữ liệu đã import?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # Reset dữ liệu
            self.data_chamcong = {}
            self.available_months = []
            self.is_data_imported = False
            
            # Cập nhật UI
            self.import_btn.setVisible(True)
            self.clear_btn.setVisible(False)
            
            # Reset combo boxes
            self.populate_month_combo()
            self.populate_year_combo()
            
            # Clear table
            self.table_widget.setRowCount(0)
            
            # Reset working days display
            self.update_working_days_display()
            
            # Update info panel
            self.update_info_panel()
            
            QMessageBox.information(self, "Thành công", "Đã gỡ bỏ dữ liệu import!")
            if self.on_data_changed:
                self.on_data_changed(self.data_chamcong)
    
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
                selection-background-color: #f8f9fa;
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
                background-color: #f8f9fa;
                color: #495057;
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
                    
                    # Import dữ liệu các ngày
                    days_data = {}
                    for i in range(1, 32):
                        day_value = row.get(f"ngay_{i}", "").strip()
                        if day_value:
                            days_data[f"day_{i}"] = day_value
                    
                    self.data_chamcong[employee_name][month_year] = {
                        'days': days_data,
                        'ot_150': float(row.get('ot_150', 0) or 0),
                        'sunday_200': float(row.get('cn_200', 0) or 0),
                        'holiday_300': float(row.get('le_300', 0) or 0),
                        'nang_suat_ut': float(row.get('ns_ut', 0) or 0),
                        'nang_suat_paut': float(row.get('ns_paut', 0) or 0),
                        'nang_suat_tofd': float(row.get('ns_tofd', 0) or 0),
                        'ngay_tinh_luong': int(str(row.get('ngay_tinh_luong', 0) or 0)),
                        'tam_ung': float(row.get('tam_ung', 0) or 0),
                        'chi_phi_mua_sam': float(row.get('cp_mua_sam', 0) or 0),
                        'chi_phi_khach_san': float(row.get('cp_khach_san', 0) or 0),
                        'phu_cap_di_lai': float(row.get('pc_di_lai', 0) or 0)
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
            self.on_data_changed(self.data_chamcong)
    
    def import_json(self, file_path):
        """Import từ file JSON với cấu trúc mới từ website"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
                
                # Kiểm tra format mới từ website
                if 'export_info' in data and 'employees' in data:
                    # Format đúng từ website
                    employees_data = data['employees']
                    export_info = data['export_info']
                    
                    # Lấy thông tin tháng/năm từ export_info
                    period = export_info.get('period', '')
                    if period and '/' in period:
                        try:
                            month, year = period.split('/')
                            if month.strip() and year.strip():
                                self.current_month = int(month.strip())
                                self.current_year = int(year.strip())
                                # Cập nhật combo boxes
                                self.combo_month.setCurrentText(f"{self.current_month:02d}")
                                self.combo_year.setCurrentText(str(self.current_year))
                            else:
                                # Fallback nếu month hoặc year rỗng
                                self.current_month = datetime.now().month
                                self.current_year = datetime.now().year
                        except (ValueError, IndexError):
                            # Fallback nếu format period không đúng
                            self.current_month = datetime.now().month
                            self.current_year = datetime.now().year
                    else:
                        # Fallback nếu không có period
                        self.current_month = datetime.now().month
                        self.current_year = datetime.now().year
                    
                    # Lưu thông tin export
                    self.export_info = export_info
                    
                    # Danh sách nhân viên trong file JSON
                    json_employees = []
                    # Danh sách nhân viên được hiển thị
                    displayed_employees = []
                    # Danh sách nhân viên không được hiển thị
                    hidden_employees = []
                    # Danh sách nhân viên trong JSON nhưng không có trong danh sách
                    unknown_employees = []
                    
                    # Lấy danh sách tất cả nhân viên có thể có
                    all_possible_employees = set()
                    if self.selected_employees:
                        all_possible_employees.update(self.selected_employees)
                    # Thêm nhân viên từ data_chamcong (nếu có)
                    all_possible_employees.update(self.data_chamcong.keys())
                    
                    for msnv, employee_data in employees_data.items():
                        if 'info' in employee_data and 'attendance' in employee_data:
                            employee_info = employee_data['info']
                            attendance_data = employee_data['attendance']
                            
                            employee_name = employee_info.get('name', msnv)
                            if not employee_name or not employee_name.strip():
                                continue  # Bỏ qua nếu tên rỗng
                                
                            json_employees.append(employee_name)
                            
                            # Import tất cả nhân viên có trong file JSON, không kiểm tra danh sách
                            displayed_employees.append(employee_name)
                            
                            if employee_name not in self.data_chamcong:
                                self.data_chamcong[employee_name] = {}
                            
                            # Xử lý dữ liệu ngày
                            days_converted = {}
                            days_detail = {}
                            
                            for day_key, day_info in attendance_data.get('days', {}).items():
                                if isinstance(day_info, dict):
                                    work_type = day_info.get('type', '')
                                    days_converted[day_key] = work_type
                                    days_detail[day_key] = day_info
                            
                            # Lấy summary từ attendance
                            summary = attendance_data.get('summary', {})
                            
                            # Tính toán thêm từ dữ liệu chi tiết
                            total_work_days = summary.get('total_work_days', 0)
                            total_office_days = summary.get('total_office_days', 0)
                            total_training_days = summary.get('total_training_days', 0)
                            total_leave_days = summary.get('total_leave_days', 0)
                            total_absent_days = summary.get('total_absent_days', 0)
                            
                            # Tính năng suất PAUT/TOFD
                            def _to_float(value):
                                try:
                                    return float(value)
                                except Exception:
                                    return 0.0

                            paut_total = _to_float(summary.get('paut_total_meters', 0))
                            tofd_total = _to_float(summary.get('tofd_total_meters', 0))

                            # Nếu summary chưa có hoặc bằng 0, cộng dồn từ từng ngày
                            if (paut_total == 0.0 and tofd_total == 0.0):
                                for _day_key, _day_info in attendance_data.get('days', {}).items():
                                    if isinstance(_day_info, dict):
                                        paut_total += _to_float(_day_info.get('paut_meters', 0))
                                        tofd_total += _to_float(_day_info.get('tofd_meters', 0))
                            
                            # Lưu dữ liệu với format mới
                            self.data_chamcong[employee_name][f"{self.current_month:02d}/{self.current_year}"] = {
                                'days': days_converted,
                                'days_detail': days_detail,
                                'ot_150': summary.get('total_overtime_hours', 0),
                                'sunday_200': 0,  # Sẽ tính toán sau
                                'holiday_300': 0,  # Sẽ tính toán sau
                                'nang_suat_ut': 0,  # Sẽ tính toán sau
                                'nang_suat_paut': paut_total,
                                'nang_suat_tofd': tofd_total,
                                'ngay_tinh_luong': total_work_days + total_office_days + total_training_days,
                                'tam_ung': 0,  # Sẽ nhập sau
                                'chi_phi_mua_sam': summary.get('shopping_expenses', 0),
                                'chi_phi_khach_san': summary.get('hotel_expenses', 0),
                                'phu_cap_di_lai': summary.get('total_expenses', 0)
                            }
                    
                    # Tạo thông báo chi tiết
                    message_parts = []
                    message_parts.append(f"Đã import thành công {len(displayed_employees)} nhân viên.")
                    
                    if hidden_employees:
                        hidden_list = ", ".join(hidden_employees)
                        message_parts.append(f"\nNhân viên không được hiển thị ({len(hidden_employees)} người):\n{hidden_list}")
                    
                    if unknown_employees:
                        unknown_list = ", ".join(unknown_employees)
                        message_parts.append(f"\nNhân viên trong file JSON không có trong danh sách ({len(unknown_employees)} người):\n{unknown_list}")
                    
                    # Kiểm tra nhân viên được chọn nhưng không có trong JSON
                    if self.selected_employees:
                        missing_employees = [emp for emp in self.selected_employees if emp not in json_employees]
                        if missing_employees:
                            missing_list = ", ".join(missing_employees)
                            message_parts.append(f"\nNhân viên được chọn nhưng không có trong file JSON ({len(missing_employees)} người):\n{missing_list}")
                    
                    # Hiển thị thông báo
                    full_message = "\n".join(message_parts)
                    if len(message_parts) > 1:
                        full_message += "\n\nĐể hiển thị tất cả, hãy chọn 'Tất cả' trong Select nhân viên."
                    
                    QMessageBox.information(self, "Thông báo Import", full_message)
                else:
                    # Format cũ (fallback)
                    # Danh sách nhân viên trong file JSON
                    json_employees = []
                    # Danh sách nhân viên được hiển thị
                    displayed_employees = []
                    # Danh sách nhân viên không được hiển thị
                    hidden_employees = []
                    # Danh sách nhân viên trong JSON nhưng không có trong danh sách
                    unknown_employees = []
                    
                    # Lấy danh sách tất cả nhân viên có thể có
                    all_possible_employees = set()
                    if self.selected_employees:
                        all_possible_employees.update(self.selected_employees)
                    # Thêm nhân viên từ data_chamcong (nếu có)
                    all_possible_employees.update(self.data_chamcong.keys())
                    
                    for employee_name, employee_data in data.items():
                        if not employee_name or not employee_name.strip():
                            continue  # Bỏ qua nếu tên rỗng
                            
                        json_employees.append(employee_name)
                        
                        # Import tất cả nhân viên có trong file JSON, không kiểm tra danh sách
                        displayed_employees.append(employee_name)
                        
                        if employee_name not in self.data_chamcong:
                            self.data_chamcong[employee_name] = {}
                            
                            for month_year, month_data in employee_data.items():
                                # Chuyển đổi days data
                                days_converted = {}
                                for day_key, day_info in month_data.get('days', {}).items():
                                    if isinstance(day_info, dict):
                                        days_converted[day_key] = day_info.get('type', '')
                                    else:
                                        days_converted[day_key] = day_info
                                
                                # Lưu cả thông tin chi tiết và summary
                                self.data_chamcong[employee_name][month_year] = {
                                    'days': days_converted,
                                    'days_detail': month_data.get('days', {}),  # Lưu chi tiết
                                    'ot_150': month_data.get('summary', {}).get('ot_150', 0),
                                    'sunday_200': month_data.get('summary', {}).get('sunday_200', 0),
                                    'holiday_300': month_data.get('summary', {}).get('holiday_300', 0),
                                    'nang_suat_ut': month_data.get('summary', {}).get('nang_suat_ut', 0),
                                    'nang_suat_paut': month_data.get('summary', {}).get('nang_suat_paut', 0),
                                    'nang_suat_tofd': month_data.get('summary', {}).get('nang_suat_tofd', 0),
                                    'ngay_tinh_luong': month_data.get('summary', {}).get('ngay_tinh_luong', 0),
                                    'tam_ung': month_data.get('summary', {}).get('tam_ung', 0),
                                    'chi_phi_mua_sam': month_data.get('summary', {}).get('chi_phi_mua_sam', 0),
                                    'chi_phi_khach_san': month_data.get('summary', {}).get('chi_phi_khach_san', 0),
                                    'phu_cap_di_lai': month_data.get('summary', {}).get('phu_cap_di_lai', 0)
                                }
                    
                    # Tạo thông báo chi tiết
                    message_parts = []
                    message_parts.append(f"Đã import thành công {len(displayed_employees)} nhân viên.")
                    
                    if hidden_employees:
                        hidden_list = ", ".join(hidden_employees)
                        message_parts.append(f"\nNhân viên không được hiển thị ({len(hidden_employees)} người):\n{hidden_list}")
                    
                    if unknown_employees:
                        unknown_list = ", ".join(unknown_employees)
                        message_parts.append(f"\nNhân viên trong file JSON không có trong danh sách ({len(unknown_employees)} người):\n{unknown_list}")
                    
                    # Kiểm tra nhân viên được chọn nhưng không có trong JSON
                    if self.selected_employees:
                        missing_employees = [emp for emp in self.selected_employees if emp not in json_employees]
                        if missing_employees:
                            missing_list = ", ".join(missing_employees)
                            message_parts.append(f"\nNhân viên được chọn nhưng không có trong file JSON ({len(missing_employees)} người):\n{missing_list}")
                    
                    # Hiển thị thông báo
                    full_message = "\n".join(message_parts)
                    if len(message_parts) > 1:
                        full_message += "\n\nĐể hiển thị tất cả, hãy chọn 'Tất cả' trong Select nhân viên."
                    
                    QMessageBox.information(self, "Thông báo Import", full_message)
            
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
            
            # Cập nhật combo boxes với dữ liệu từ JSON
            self.populate_month_combo()
            self.populate_year_combo()
            
            # KIỂM TRA VÀ HIỆN POPUP THÊM CÔNG TY MỚI
            self.check_and_add_new_companies()
            
            if self.on_data_changed:
                self.on_data_changed(self.data_chamcong)
                
        except Exception as e:
            QMessageBox.critical(self, "Lỗi Import", f"Không thể import file JSON: {str(e)}")
            print(f"Lỗi import JSON: {e}")
    
    def import_txt(self, file_path):
        """Import từ file TXT (format tùy chỉnh)"""
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()
            # Implement parsing logic based on your TXT format
            pass
        if self.on_data_changed:
            self.on_data_changed(self.data_chamcong)
    
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
        """Cập nhật bảng theo tháng/năm được chọn"""
        try:
            month = int(self.combo_month.currentText())
            year = int(self.combo_year.currentText())
            month_year = f"{month:02d}/{year}"
        except (ValueError, AttributeError):
            # Fallback nếu combo box không có giá trị
            month = datetime.now().month
            year = datetime.now().year
            month_year = f"{month:02d}/{year}"
        
        # Lấy số ngày từ dữ liệu CSV thay vì tính theo calendar
        days_in_month = self.get_max_days_from_data(month_year)
        
        headers = ["Tên\nnhân viên", "Chi tiết"]
        
        for day in range(1, days_in_month + 1):
            headers.append(f"{day}")
        
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
        
        self.table_widget.setColumnCount(len(headers))
        self.table_widget.setHorizontalHeaderLabels(headers)
        
        # Cập nhật column width cho các cột ngày và tổng hợp
        header = self.table_widget.horizontalHeader()
        
        # Các cột ngày
        for i in range(2, 2 + days_in_month):
            header.setSectionResizeMode(i, QHeaderView.Fixed)
            self.table_widget.setColumnWidth(i, 35)
        
        # Các cột tổng hợp
        for i in range(2 + days_in_month, len(headers)):
            header.setSectionResizeMode(i, QHeaderView.Fixed)
            self.table_widget.setColumnWidth(i, 100)
        
        # Cập nhật dữ liệu - lọc theo nhân viên được chọn
        all_employees = list(self.data_chamcong.keys())
        
        # Lọc nhân viên theo danh sách đã chọn
        if self.selected_employees:
            # Hiển thị cả nhân viên đã chọn mà chưa có dữ liệu
            employees = list(self.selected_employees)
            # Thêm nhân viên có dữ liệu nhưng chưa được chọn (nếu cần)
            for emp in all_employees:
                if emp not in employees:
                    employees.append(emp)
        else:
            employees = all_employees  # Hiển thị tất cả nếu chưa chọn ai
            
        self.table_widget.setRowCount(len(employees))
        
        # Cập nhật thông tin header
        self.update_working_days_display()
        
        for row, employee in enumerate(employees):
            try:
                # Tìm dữ liệu cho tháng hiện tại
                employee_data = {}
                if employee in self.data_chamcong:
                    employee_data = self.data_chamcong[employee].get(month_year, {})
                    
                    if not employee_data:
                        # Tìm tháng gần nhất có dữ liệu
                        for existing_month in self.data_chamcong[employee].keys():
                            employee_data = self.data_chamcong[employee][existing_month]
                            break
                
                # Tên nhân viên (có thể click để xem thông tin chi tiết)
                employee_info = employee_data.get('info', {})
                if employee_info:
                    # Tạo button cho tên nhân viên
                    name_btn = QPushButton(employee)
                    name_btn.setFont(QFont("Times New Roman", 9))
                    name_btn.setStyleSheet("""
                        QPushButton {
                            background-color: transparent;
                            color: #007bff;
                            border: none;
                            text-decoration: underline;
                            font-family: "Times New Roman";
                            text-align: left;
                            padding: 4px 8px;
                        }
                        QPushButton:hover {
                            color: #0056b3;
                            background-color: #f8f9fa;
                        }
                    """)
                    name_btn.clicked.connect(lambda checked, emp=employee, info=employee_info: self.show_employee_info(emp, info))
                    self.table_widget.setCellWidget(row, 0, name_btn)
                else:
                    # Fallback nếu không có thông tin chi tiết
                    self.table_widget.setItem(row, 0, QTableWidgetItem(employee))
                
                # Nút chi tiết
                detail_btn = QPushButton("Chi tiết")
                detail_btn.setFont(QFont("Times New Roman", 9))
                detail_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #f8f9fa;
                        color: #495057;
                        border: 1px solid #ced4da;
                        border-radius: 2px;
                        padding: 4px 8px;
                        font-family: "Times New Roman";
                    }
                    QPushButton:hover {
                        background-color: #e9ecef;
                        border-color: #495057;
                    }
                """)
                detail_btn.clicked.connect(lambda checked, emp=employee, data=employee_data: self.show_detail(emp, data))
                self.table_widget.setCellWidget(row, 1, detail_btn)
                
                # Dữ liệu các ngày
                days_data = employee_data.get('days', {})
                
                for day in range(1, days_in_month + 1):
                    # Thử cả 2 format: day_01 và day_1
                    work_type = days_data.get(f"day_{day:02d}", days_data.get(f"day_{day}", ""))
                    item = QTableWidgetItem(work_type)
                    item.setTextAlignment(Qt.AlignCenter)
                    
                    # Thêm màu sắc cho các loại công
                    if work_type == 'W':
                        item.setBackground(QColor("#e3f2fd"))  # Xanh nhạt cho công trường
                    elif work_type == 'O':
                        item.setBackground(QColor("#f3e5f5"))  # Tím nhạt cho văn phòng
                    elif work_type == 'T':
                        item.setBackground(QColor("#e8f5e8"))  # Xanh lá nhạt cho đào tạo
                    elif work_type == 'P':
                        item.setBackground(QColor("#fff3e0"))  # Cam nhạt cho nghỉ phép
                    elif work_type == 'N':
                        item.setBackground(QColor("#ffebee"))  # Đỏ nhạt cho nghỉ không phép
                    else:
                        # Nếu chưa có dữ liệu, để trống
                        item = QTableWidgetItem("")
                        item.setTextAlignment(Qt.AlignCenter)
                    
                    self.table_widget.setItem(row, 1 + day, item)
                
                # Tính tổng các loại công
                work_counts = self.calculate_work_summary(days_data, days_in_month)
                
                col_offset = 2 + days_in_month
                
                # Tính tổng số tiền cho từng loại chi phí
                days_detail = employee_data.get('days_detail', {})
                hotel_total = 0
                shopping_total = 0
                phone_total = 0
                other_total = 0
                
                # Thu thập thông tin dự án và phương pháp NDT
                projects = set()
                ndt_methods = set()
                
                # Chỉ tính toán nếu có dữ liệu
                if days_detail:
                    for day_key in days_detail.keys():
                        if day_key.startswith('day_'):
                            day_data = days_detail[day_key]
                            if isinstance(day_data, dict):
                                # Tính tổng tiền khách sạn
                                hotel = day_data.get('hotel_expense', 0)
                                hotel_total += float(hotel) if hotel else 0
                                
                                # Tính tổng tiền mua sắm
                                shopping = day_data.get('shopping_expense', 0)
                                shopping_total += float(shopping) if shopping else 0
                                
                                # Tính tổng tiền điện thoại
                                phone = day_data.get('phone_expense', 0)
                                phone_total += float(phone) if phone else 0
                                
                                # Tính tổng tiền khác
                                other = day_data.get('other_expense', 0)
                                other_total += float(other) if other else 0
                                
                                # Thu thập dự án và phương pháp
                                location = day_data.get('location', '')
                                if location and location.strip():
                                    projects.add(location)
                                
                                method = day_data.get('method', '')
                                if method and method.strip():
                                    ndt_methods.add(method)
                
                # Tính tổng chi phí = tổng các khoản: KS + MS + ĐT + Khác
                total_chi_phi = hotel_total + shopping_total + phone_total + other_total
                
                # Lấy thông tin từ summary nếu có
                summary = employee_data.get('summary', {})
                if summary:
                    projects.update(summary.get('construction_projects', []))
                    ndt_methods.update(summary.get('ndt_methods_used', []))
                
                # Format dự án và phương pháp
                projects_text = ", ".join(list(projects)[:3])  # Giới hạn 3 dự án
                if len(projects) > 3:
                    projects_text += "..."
                
                ndt_methods_text = ", ".join(list(ndt_methods)[:3])  # Giới hạn 3 phương pháp
                if len(ndt_methods) > 3:
                    ndt_methods_text += "..."
                
                summary_values = [
                    work_counts['W'], work_counts['O'], work_counts['T'], 
                    work_counts['P'], work_counts['N'],
                    employee_data.get('ot_150', 0), employee_data.get('sunday_200', 0), employee_data.get('holiday_300', 0),
                    employee_data.get('nang_suat_ut', 0), employee_data.get('nang_suat_paut', 0), employee_data.get('nang_suat_tofd', 0),
                    employee_data.get('ngay_tinh_luong', 0), employee_data.get('tam_ung', 0), total_chi_phi,
                    hotel_total, shopping_total, phone_total, other_total,
                    projects_text, ndt_methods_text
                ]
                
                # Format số tiền với dấu phẩy và số ngày
                for i in range(len(summary_values)):
                    if i == 12:  # Cột tạm ứng (VNĐ)
                        if isinstance(summary_values[i], (int, float)) and summary_values[i] > 0:
                            summary_values[i] = f"{summary_values[i]:,}"
                        else:
                            summary_values[i] = ""
                    elif i == 13:  # Cột chi phí (VNĐ)
                        if isinstance(summary_values[i], (int, float)) and summary_values[i] > 0:
                            summary_values[i] = f"{summary_values[i]:,}"
                        else:
                            summary_values[i] = ""
                    elif i >= 14 and i <= 17:  # Các cột tiền (Khách sạn, Mua sắm, Điện thoại, Khác)
                        if isinstance(summary_values[i], (int, float)) and summary_values[i] > 0:
                            summary_values[i] = f"{summary_values[i]:,}"
                        else:
                            summary_values[i] = ""
                    elif i >= 18:  # Các cột text (Dự án, Phương pháp NDT)
                        if summary_values[i]:
                            summary_values[i] = str(summary_values[i])
                        else:
                            summary_values[i] = ""
                    elif i == 5:  # Cột giờ tăng ca (OT 150%)
                        if isinstance(summary_values[i], (int, float)) and summary_values[i] > 0:
                            summary_values[i] = f"{summary_values[i]:.1f}"
                        else:
                            summary_values[i] = ""
                
                for i, value in enumerate(summary_values):
                    item = QTableWidgetItem(str(value))
                    item.setTextAlignment(Qt.AlignCenter)
                    self.table_widget.setItem(row, col_offset + i, item)
                    
            except Exception as e:
                print(f"Lỗi khi xử lý nhân viên {employee}: {e}")
                # Tạo row trống nếu có lỗi
                self.table_widget.setItem(row, 0, QTableWidgetItem(employee))
                for col in range(1, self.table_widget.columnCount()):
                    self.table_widget.setItem(row, col, QTableWidgetItem(""))
    
    def calculate_work_summary(self, days_data, days_in_month):
        """Tính tổng số ngày cho mỗi loại công"""
        work_counts = {'W': 0, 'O': 0, 'T': 0, 'P': 0, 'N': 0}
        
        for day in range(1, days_in_month + 1):
            # Thử cả 2 format: day_01 và day_1
            work_type = days_data.get(f"day_{day:02d}", days_data.get(f"day_{day}", ""))
            if work_type in work_counts:
                work_counts[work_type] += 1
        
        return work_counts
    
    def show_employee_info(self, employee_name, employee_info):
        """Hiển thị thông tin chi tiết của nhân viên"""
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Thông tin nhân viên - {employee_name}")
        dialog.setModal(True)
        dialog.resize(400, 300)
        
        layout = QVBoxLayout(dialog)
        
        # Tiêu đề
        title = QLabel(f"Thông tin chi tiết - {employee_name}")
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont("Times New Roman", 14, QFont.Bold))
        layout.addWidget(title)
        
        # Form thông tin
        form_layout = QFormLayout()
        
        info_fields = [
            ("MSNV", employee_info.get('msnv', '')),
            ("Email", employee_info.get('email', '')),
            ("Chức vụ", employee_info.get('position', '')),
            ("Phòng ban", employee_info.get('department', '')),
            ("Số điện thoại", employee_info.get('phone', ''))
        ]
        
        for label, value in info_fields:
            label_widget = QLabel(label)
            label_widget.setFont(QFont("Times New Roman", 10, QFont.Bold))
            value_widget = QLabel(value if value else "Chưa có thông tin")
            value_widget.setFont(QFont("Times New Roman", 10))
            value_widget.setStyleSheet("color: #495057;")
            form_layout.addRow(label_widget, value_widget)
        
        layout.addLayout(form_layout)
        
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
        close_btn.clicked.connect(dialog.close)
        layout.addWidget(close_btn)
        
        dialog.exec_()
    
    def show_detail(self, employee_name, employee_data):
        """Hiển thị chi tiết bảng công của nhân viên"""
        # Ưu tiên sử dụng days_detail nếu có (từ JSON website)
        days_detail = employee_data.get('days_detail', {})
        
        # Nếu không có days_detail, sử dụng days thông thường
        if not days_detail:
            days_detail = employee_data.get('days', {})
        
        dialog = BangCongDialog(employee_name, days_detail, self)
        dialog.exec_()
    
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

