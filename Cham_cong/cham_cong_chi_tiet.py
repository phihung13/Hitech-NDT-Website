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
from employee_mapper import EmployeeMapper

class TabChamCongChiTiet(QWidget):
    """Tab chấm công chi tiết hiển thị từng ngày"""
    
    def __init__(self, on_data_changed=None):
        super().__init__()
        self.on_data_changed = on_data_changed
        self.data_manager = DataManager()
        self.employee_mapper = EmployeeMapper()
        self.data_chamcong = {}
        self.current_month = datetime.now().month
        self.current_year = datetime.now().year
        
        self.init_ui()
        self.load_data()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Header với thông tin tháng
        header_layout = QHBoxLayout()
        
        # Chọn tháng/năm
        month_label = QLabel("Tháng:")
        self.month_combo = QComboBox()
        for i in range(1, 13):
            self.month_combo.addItem(f"{i:02d}", i)
        self.month_combo.setCurrentIndex(self.current_month - 1)
        self.month_combo.currentIndexChanged.connect(self.on_month_changed)
        
        year_label = QLabel("Năm:")
        self.year_combo = QComboBox()
        current_year = datetime.now().year
        for year in range(current_year - 2, current_year + 3):
            self.year_combo.addItem(str(year), year)
        self.year_combo.setCurrentText(str(self.current_year))
        self.year_combo.currentTextChanged.connect(self.on_year_changed)
        
        header_layout.addWidget(month_label)
        header_layout.addWidget(self.month_combo)
        header_layout.addWidget(year_label)
        header_layout.addWidget(self.year_combo)
        header_layout.addStretch()
        
        # Nút import
        self.btn_import = QPushButton("Import dữ liệu")
        self.btn_import.clicked.connect(self.import_data)
        header_layout.addWidget(self.btn_import)
        
        layout.addLayout(header_layout)
        
        # Bảng chấm công chi tiết
        self.create_detail_table()
        layout.addWidget(self.table_widget)
        
        # Thông tin tổng quan
        self.create_summary_panel()
        layout.addWidget(self.summary_panel)
    
    def create_detail_table(self):
        """Tạo bảng chấm công chi tiết từng ngày"""
        self.table_widget = QTableWidget()
        self.table_widget.setFont(QFont("Times New Roman", 9))
        
        # Headers: Tên nhân viên, MSNV, Ngày 1, Ngày 2, ..., Ngày 31
        headers = ["Tên nhân viên", "MSNV"]
        days_in_month = calendar.monthrange(self.current_year, self.current_month)[1]
        
        for day in range(1, days_in_month + 1):
            date_obj = datetime(self.current_year, self.current_month, day)
            weekday = date_obj.strftime("%a")  # Mon, Tue, etc.
            headers.append(f"{day:02d}\n{weekday}")
        
        self.table_widget.setColumnCount(len(headers))
        self.table_widget.setHorizontalHeaderLabels(headers)
        
        # Style
        self.table_widget.setStyleSheet("""
            QTableWidget {
                gridline-color: #e9ecef;
                font-family: "Times New Roman";
                font-size: 9pt;
                background-color: white;
                border: 1px solid #e9ecef;
            }
            QHeaderView::section {
                background-color: #f8f9fa;
                padding: 4px 2px;
                border: none;
                border-right: 1px solid #e9ecef;
                border-bottom: 1px solid #e9ecef;
                font-weight: normal;
                font-family: "Times New Roman";
                font-size: 8pt;
                color: #495057;
                min-height: 50px;
            }
            QTableWidget::item {
                padding: 4px 2px;
                border: none;
                border-right: 1px solid #f1f3f4;
                border-bottom: 1px solid #f1f3f4;
                text-align: center;
            }
        """)
        
        # Resize columns
        header = self.table_widget.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Fixed)  # Tên nhân viên
        header.setSectionResizeMode(1, QHeaderView.Fixed)  # MSNV
        self.table_widget.setColumnWidth(0, 150)
        self.table_widget.setColumnWidth(1, 100)
        
        # Các cột ngày
        for i in range(2, len(headers)):
            header.setSectionResizeMode(i, QHeaderView.Fixed)
            self.table_widget.setColumnWidth(i, 60)
        
        # Tô màu chủ nhật
        self.highlight_sundays()
    
    def create_summary_panel(self):
        """Tạo panel thông tin tổng quan"""
        self.summary_panel = QGroupBox("Thông tin tổng quan")
        self.summary_panel.setFont(QFont("Times New Roman", 10, QFont.Bold))
        
        layout = QHBoxLayout(self.summary_panel)
        
        self.total_employees_label = QLabel("Tổng nhân viên: 0")
        self.total_work_days_label = QLabel("Tổng ngày làm việc: 0")
        self.total_overtime_label = QLabel("Tổng giờ OT: 0")
        self.total_expenses_label = QLabel("Tổng chi phí: 0 VNĐ")
        
        layout.addWidget(self.total_employees_label)
        layout.addWidget(self.total_work_days_label)
        layout.addWidget(self.total_overtime_label)
        layout.addWidget(self.total_expenses_label)
        layout.addStretch()
    
    def highlight_sundays(self):
        """Tô màu vàng cho các cột chủ nhật"""
        days_in_month = calendar.monthrange(self.current_year, self.current_month)[1]
        
        for day in range(1, days_in_month + 1):
            date_obj = datetime(self.current_year, self.current_month, day)
            if date_obj.weekday() == 6:  # Chủ nhật
                col_index = day + 1  # +2 cho "Tên nhân viên" và "MSNV", -1 vì day bắt đầu từ 1
                
                # Tô màu header
                header_item = self.table_widget.horizontalHeaderItem(col_index)
                if header_item:
                    header_item.setBackground(QColor("#fff3cd"))
    
    def on_month_changed(self, index):
        """Xử lý khi thay đổi tháng"""
        self.current_month = self.month_combo.itemData(index)
        self.refresh_table()
    
    def on_year_changed(self, text):
        """Xử lý khi thay đổi năm"""
        try:
            self.current_year = int(text)
            self.refresh_table()
        except ValueError:
            pass
    
    def load_data(self):
        """Load dữ liệu chấm công"""
        try:
            # Load employee mapping
            nhanvien_data = self.data_manager.load_nhanvien()
            self.employee_mapper.load_from_nhanvien_data(nhanvien_data)
            
            # Load dữ liệu chấm công từ file JSON
            self.load_chamcong_data()
            
        except Exception as e:
            print(f"Lỗi load data: {e}")
    
    def load_chamcong_data(self):
        """Load dữ liệu chấm công từ file JSON"""
        try:
            # Tìm file JSON chấm công cho tháng hiện tại
            month_str = f"{self.current_month:02d}"
            year_str = str(self.current_year)
            
            # Tìm file phù hợp
            import os
            data_dir = "data"
            if os.path.exists(data_dir):
                for filename in os.listdir(data_dir):
                    if filename.startswith("chamcong") and month_str in filename and year_str in filename:
                        file_path = os.path.join(data_dir, filename)
                        self.import_json(file_path)
                        break
                        
        except Exception as e:
            print(f"Lỗi load chamcong data: {e}")
    
    def import_data(self):
        """Import dữ liệu từ file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Chọn file dữ liệu", "", 
            "JSON files (*.json);;CSV files (*.csv);;All files (*)"
        )
        
        if file_path:
            if file_path.endswith('.json'):
                self.import_json(file_path)
            elif file_path.endswith('.csv'):
                self.import_csv(file_path)
    
    def import_json(self, file_path):
        """Import từ file JSON"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Xử lý format mới từ website
            if isinstance(data, dict) and 'data' in data:
                self.process_website_format(data)
            else:
                print("Format JSON không được hỗ trợ")
                
        except Exception as e:
            print(f"Lỗi import JSON: {e}")
            QMessageBox.critical(self, "Lỗi", f"Không thể import file JSON: {e}")
    
    def process_website_format(self, data):
        """Xử lý format JSON mới từ website"""
        try:
            attendance_data = data.get('data', [])
            self.data_chamcong.clear()
            
            # Nhóm dữ liệu theo MSNV
            for record in attendance_data:
                if len(record) >= 3:
                    msnv = str(record[0]).strip()
                    name = str(record[1]).strip()
                    date_str = str(record[2]).strip()
                    
                    if msnv not in self.data_chamcong:
                        self.data_chamcong[msnv] = {
                            'name': name,
                            'msnv': msnv,
                            'days': {}
                        }
                    
                    # Parse ngày
                    try:
                        date_obj = datetime.strptime(date_str, '%d/%m/%Y')
                        day_num = date_obj.day
                        
                        self.data_chamcong[msnv]['days'][day_num] = {
                            'type': record[3] if len(record) > 3 else '',
                            'location': record[4] if len(record) > 4 else '',
                            'method': record[5] if len(record) > 5 else '',
                            'day_shift': record[6] == '1' if len(record) > 6 else False,
                            'night_shift': record[7] == '1' if len(record) > 7 else False,
                            'overtime_hours': float(record[10]) if len(record) > 10 else 0,
                            'expense_amount': float(record[15]) if len(record) > 15 else 0
                        }
                    except ValueError:
                        continue
            
            self.refresh_table()
            print(f"Đã import {len(self.data_chamcong)} nhân viên")
            
        except Exception as e:
            print(f"Lỗi process website format: {e}")
    
    def refresh_table(self):
        """Refresh bảng hiển thị"""
        try:
            # Tạo lại bảng với số ngày mới
            self.create_detail_table()
            
            # Điền dữ liệu
            row = 0
            total_work_days = 0
            total_overtime = 0
            total_expenses = 0
            
            for msnv, data in self.data_chamcong.items():
                name = data.get('name', '')
                days_data = data.get('days', {})
                
                # Lấy tên từ employee mapper nếu có
                display_name = self.employee_mapper.get_name_by_msnv(msnv) or name
                
                self.table_widget.insertRow(row)
                self.table_widget.setItem(row, 0, QTableWidgetItem(display_name))
                self.table_widget.setItem(row, 1, QTableWidgetItem(msnv))
                
                days_in_month = calendar.monthrange(self.current_year, self.current_month)[1]
                
                for day in range(1, days_in_month + 1):
                    col_index = day + 1
                    
                    if day in days_data:
                        day_info = days_data[day]
                        work_type = day_info.get('type', '')
                        
                        # Tạo item với màu sắc
                        item = QTableWidgetItem(work_type)
                        
                        # Màu sắc theo loại công việc
                        if work_type == 'W':
                            item.setBackground(QColor("#d4edda"))  # Xanh lá - Công trường
                        elif work_type == 'O':
                            item.setBackground(QColor("#d1ecf1"))  # Xanh dương - Văn phòng
                        elif work_type == 'T':
                            item.setBackground(QColor("#fff3cd"))  # Vàng - Đào tạo
                        elif work_type == 'P':
                            item.setBackground(QColor("#f8d7da"))  # Đỏ nhạt - Nghỉ có phép
                        elif work_type == 'N':
                            item.setBackground(QColor("#f5c6cb"))  # Đỏ - Nghỉ không phép
                        
                        self.table_widget.setItem(row, col_index, item)
                        
                        # Tính tổng
                        if work_type in ['W', 'O', 'T']:
                            total_work_days += 1
                        
                        total_overtime += day_info.get('overtime_hours', 0)
                        total_expenses += day_info.get('expense_amount', 0)
                    else:
                        # Ngày không có dữ liệu
                        item = QTableWidgetItem("")
                        item.setBackground(QColor("#f8f9fa"))  # Xám nhạt
                        self.table_widget.setItem(row, col_index, item)
                
                row += 1
            
            # Cập nhật thông tin tổng quan
            self.total_employees_label.setText(f"Tổng nhân viên: {len(self.data_chamcong)}")
            self.total_work_days_label.setText(f"Tổng ngày làm việc: {total_work_days}")
            self.total_overtime_label.setText(f"Tổng giờ OT: {total_overtime:.1f}")
            self.total_expenses_label.setText(f"Tổng chi phí: {total_expenses:,.0f} VNĐ")
            
        except Exception as e:
            print(f"Lỗi refresh table: {e}")
    
    def import_csv(self, file_path):
        """Import từ file CSV"""
        # Implement CSV import logic here
        pass 