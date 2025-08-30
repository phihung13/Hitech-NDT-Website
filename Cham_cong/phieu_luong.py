from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QTableWidget, QTableWidgetItem,
    QPushButton, QMessageBox, QLabel, QComboBox, QGroupBox, QFormLayout, QHeaderView,
    QFrame, QSpacerItem, QSizePolicy, QScrollArea, QDialog, QFileDialog, QApplication,
    QCalendarWidget
)
from PyQt5.QtCore import Qt, QSize, QDate, QTimer
from PyQt5.QtGui import QFont, QColor, QPalette, QPixmap
import calendar
from datetime import datetime, date
from data_manager import DataManager
from company_matcher import CompanyMatcher
from new_company_dialog import NewCompanyDialog
from formula_tooltip import SimpleFormulaTooltip, get_formula_text
import json
import os
import traceback
import re
import glob

class TaxTableDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Bảng thuế thu nhập cá nhân (Theo Luật Việt Nam)")
        self.setFixedSize(600, 400)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Tiêu đề
        title = QLabel("BẢNG THUẾ THU NHẬP CÁ NHÂN")
        title.setStyleSheet("font-weight: bold; font-size: 14px; color: #2c3e50;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        subtitle = QLabel("(Theo Luật Thuế TNCN 2007, sửa đổi 2012)")
        subtitle.setStyleSheet("font-size: 12px; color: #7f8c8d;")
        subtitle.setAlignment(Qt.AlignCenter)
        layout.addWidget(subtitle)
        
        # Bảng thuế
        table = QTableWidget(7, 4)
        table.setHorizontalHeaderLabels(["Bậc thuế", "Thu nhập tính thuế/tháng", "Thuế suất", "Cách tính"])
        
        # Dữ liệu bảng thuế theo luật Việt Nam
        tax_data = [
            ("1", "Đến 5 triệu", "5%", "0 tr + 5% TNTT"),
            ("2", "Trên 5 triệu đến 10 triệu", "10%", "0.25 tr + 10% TNTT trên 5 tr"),
            ("3", "Trên 10 triệu đến 18 triệu", "15%", "0.75 tr + 15% TNTT trên 10 tr"),
            ("4", "Trên 18 triệu đến 32 triệu", "20%", "1.95 tr + 20% TNTT trên 18 tr"),
            ("5", "Trên 32 triệu đến 52 triệu", "25%", "4.75 tr + 25% TNTT trên 32 tr"),
            ("6", "Trên 52 triệu đến 80 triệu", "30%", "9.75 tr + 30% TNTT trên 52 tr"),
            ("7", "Trên 80 triệu", "35%", "18.15 tr + 35% TNTT trên 80 tr")
        ]
        
        for i, (level, range_val, rate, calc) in enumerate(tax_data):
            table.setItem(i, 0, QTableWidgetItem(level))
            table.setItem(i, 1, QTableWidgetItem(range_val))
            table.setItem(i, 2, QTableWidgetItem(rate))
            table.setItem(i, 3, QTableWidgetItem(calc))
        
        # Format bảng
        table.verticalHeader().setVisible(False)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        table.setSelectionMode(QTableWidget.NoSelection)
        table.setEditTriggers(QTableWidget.NoEditTriggers)
        
        # Style cho bảng
        table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #bdc3c7;
                gridline-color: #ecf0f1;
                font-size: 11px;
            }
            QHeaderView::section {
                background-color: #34495e;
                color: white;
                padding: 8px;
                border: 1px solid #2c3e50;
                font-weight: bold;
            }
            QTableWidget::item {
                padding: 6px;
                border: 1px solid #ecf0f1;
            }
        """)
        
        layout.addWidget(table)
        
        # Thông tin bổ sung
        info_label = QLabel("""
        <b>Lưu ý:</b><br>
        • Thu nhập tính thuế = Tổng thu nhập - Bảo hiểm bắt buộc (10.5%) - Giảm trừ gia cảnh<br>
        • Giảm trừ bản thân: 11 triệu/tháng<br>
        • Giảm trừ người phụ thuộc: 4.4 triệu/người/tháng<br>
        • Tối đa 9 người phụ thuộc
        """)
        info_label.setStyleSheet("font-size: 10px; color: #7f8c8d; background-color: #f8f9fa; padding: 10px; border-radius: 5px;")
        info_label.setWordWrap(True)
        layout.addWidget(info_label)
        
        # Nút đóng
        close_btn = QPushButton("Đóng")
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 8px 20px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        close_btn.clicked.connect(self.close)
        layout.addWidget(close_btn)

# Cập nhật class HolidayInputDialog
class HolidayInputDialog(QDialog):
    def __init__(self, year, month, parent=None):
        super().__init__(parent)
        self.year = year
        self.month = month
        self.holiday_dates = []
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle("Quản lý ngày lễ tết")
        self.setModal(True)
        self.resize(400, 500)
        layout = QVBoxLayout()
        
        # Label hướng dẫn
        label = QLabel(f"Quản lý ngày lễ tết tháng {self.month}/{self.year}:")
        layout.addWidget(label)
        
        # Calendar widget
        self.calendar = QCalendarWidget()
        self.calendar.setGridVisible(True)
        layout.addWidget(self.calendar)
        
        # Hiển thị ngày đã chọn
        self.selected_label = QLabel("Ngày đã chọn: ")
        layout.addWidget(self.selected_label)
        
        # Danh sách ngày lễ đã chọn
        self.holiday_list_label = QLabel("Ngày lễ đã chọn:")
        layout.addWidget(self.holiday_list_label)
        
        # Buttons
        button_layout = QHBoxLayout()
        add_btn = QPushButton("Thêm ngày lễ")
        remove_btn = QPushButton("Xóa ngày lễ")
        clear_btn = QPushButton("Xóa tất cả")
        no_holiday_btn = QPushButton("Tháng này không có lễ tết")
        ok_btn = QPushButton("Xác nhận")
        
        add_btn.clicked.connect(self.add_holiday)
        remove_btn.clicked.connect(self.remove_holiday)
        clear_btn.clicked.connect(self.clear_holidays)
        no_holiday_btn.clicked.connect(self.no_holidays)
        ok_btn.clicked.connect(self.accept)
        
        button_layout.addWidget(add_btn)
        button_layout.addWidget(remove_btn)
        button_layout.addWidget(clear_btn)
        button_layout.addWidget(no_holiday_btn)
        button_layout.addWidget(ok_btn)
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        self.calendar.clicked.connect(self.update_selected_label)
        self.update_holiday_list()
    
    def update_selected_label(self):
        selected_date = self.calendar.selectedDate()
        self.selected_label.setText(f"Ngày đã chọn: {selected_date.toString('dd/MM/yyyy')}")
    
    def add_holiday(self):
        selected_date = self.calendar.selectedDate()
        holiday_date = date(selected_date.year(), selected_date.month(), selected_date.day())
        
        if holiday_date not in self.holiday_dates:
            self.holiday_dates.append(holiday_date)
            self.holiday_dates.sort()  # Sắp xếp theo thứ tự
            QMessageBox.information(self, "Thành công", f"Đã thêm ngày lễ: {holiday_date.strftime('%d/%m/%Y')}")
            self.update_holiday_list()
        else:
            QMessageBox.warning(self, "Lỗi", "Ngày này đã được thêm!")
    
    def remove_holiday(self):
        selected_date = self.calendar.selectedDate()
        holiday_date = date(selected_date.year(), selected_date.month(), selected_date.day())
        
        if holiday_date in self.holiday_dates:
            self.holiday_dates.remove(holiday_date)
            QMessageBox.information(self, "Thành công", f"Đã xóa ngày lễ: {holiday_date.strftime('%d/%m/%Y')}")
            self.update_holiday_list()
        else:
            QMessageBox.warning(self, "Lỗi", "Ngày này không có trong danh sách!")
    
    def clear_holidays(self):
        self.holiday_dates = []
        QMessageBox.information(self, "Thành công", "Đã xóa tất cả ngày lễ!")
        self.update_holiday_list()
    
    def no_holidays(self):
        self.holiday_dates = []
        QMessageBox.information(self, "Thành công", "Đã xác nhận tháng này không có lễ tết!")
        self.update_holiday_list()
    
    def update_holiday_list(self):
        if self.holiday_dates:
            holiday_text = "\n".join([d.strftime('%d/%m/%Y') for d in self.holiday_dates])
            self.holiday_list_label.setText(f"Ngày lễ đã chọn:\n{holiday_text}")
        else:
            self.holiday_list_label.setText("Ngày lễ đã chọn: Không có")
    
    def get_holiday_dates(self):
        return self.holiday_dates

class InputDialog(QDialog):
    def __init__(self, title, label_text, current_value="", parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setFixedSize(350, 150)
        self.current_value = current_value
        self.label_text = label_text
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        
        # Label
        label = QLabel(self.label_text)
        label.setStyleSheet("font-weight: bold; color: #2c3e50;")
        layout.addWidget(label)
        
        # Input
        self.input_field = QLineEdit()
        self.input_field.setText(str(self.current_value))
        self.input_field.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 2px solid #bdc3c7;
                border-radius: 4px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border-color: #3498db;
            }
        """)
        layout.addWidget(self.input_field)
        
        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        cancel_btn = QPushButton("Hủy")
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
        """)
        cancel_btn.clicked.connect(self.reject)
        
        save_btn = QPushButton("Lưu")
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #229954;
            }
        """)
        save_btn.clicked.connect(self.accept)
        
        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(save_btn)
        layout.addLayout(btn_layout)

    def get_value(self):
        """Lấy giá trị đã nhập"""
        try:
            text = self.input_field.text().replace(',', '').replace('.', '').strip()
            return int(text) if text else 0
        except ValueError:
            return 0

class BHXHSettingsDialog(QDialog):
    def __init__(self, parent=None, current_salary_base=5307200):
        super().__init__(parent)
        self.setWindowTitle("Cài đặt mức lương cơ sở BHXH")
        self.setFixedSize(350, 150)
        self.current_salary_base = current_salary_base
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        
        # Label giải thích
        info_label = QLabel("Mức lương cơ sở để tính BHXH:")
        info_label.setStyleSheet("font-weight: bold; color: #2c3e50;")
        layout.addWidget(info_label)
        
        # Input nhập mức lương
        input_layout = QHBoxLayout()
        self.salary_input = QLineEdit()
        self.salary_input.setText(f"{self.current_salary_base:,}")
        self.salary_input.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 2px solid #bdc3c7;
                border-radius: 4px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border-color: #3498db;
            }
        """)
        input_layout.addWidget(self.salary_input)
        input_layout.addWidget(QLabel("VNĐ"))
        layout.addLayout(input_layout)
        
        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        cancel_btn = QPushButton("Hủy")
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
        """)
        cancel_btn.clicked.connect(self.reject)
        
        save_btn = QPushButton("Lưu")
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #229954;
            }
        """)
        save_btn.clicked.connect(self.accept)
        
        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(save_btn)
        layout.addLayout(btn_layout)

    def get_salary_base(self):
        """Lấy mức lương cơ sở đã nhập"""
        try:
            text = self.salary_input.text().replace(',', '').replace('.', '').strip()
            return int(text) if text else self.current_salary_base
        except ValueError:
            return self.current_salary_base

class TabPhieuLuong(QWidget):
    # Constants sẽ được định nghĩa trong class

    def __init__(self):
        super().__init__()
        # Định nghĩa constants
        self.PHIEU_LUONG_WIDTH = 800  # Cố định chiều rộng phiếu lương
        
        # Khởi tạo data manager
        self.data_manager = DataManager()
        
        # Khởi tạo company matcher để nhận diện thông minh tên công ty
        self.company_matcher = CompanyMatcher()
        
        # Load dữ liệu
        self.ds_nhanvien = self.data_manager.load_nhanvien()
        self.ds_luong = self.data_manager.load_quydinh_luong()
        self.data_chamcong = {}  # Sẽ được cập nhật từ tab bảng công
        
        # Thông tin hiện tại
        self.current_employee = None
        self.current_month_year = None
        
        # Mức lương cơ sở BHXH (có thể thay đổi)
        self.bhxh_salary_base = 5307200  # Mặc định 5,307,200 VNĐ
        
        # Lưu trữ dữ liệu tạm ứng và vi phạm cho từng nhân viên/tháng
        self.tam_ung_vi_pham_data = {}  # Format: {employee_name: {month_year: {"tam_ung": amount, "vi_pham": amount}}}
        
        # Tải dữ liệu đã lưu từ file
        self.load_tam_ung_vi_pham_from_file()
        
        self.init_ui()

    def calculate_working_days(self, year, month):
        """
        Tính số ngày làm việc trong tháng (không bao gồm chủ nhật)
        """
        try:
            # Validation input
            if not isinstance(year, int) or not isinstance(month, int):
                raise ValueError("Năm và tháng phải là số nguyên")
            if not (1 <= month <= 12):
                raise ValueError(f"Tháng không hợp lệ: {month}")
            if year < 1900 or year > 2100:
                raise ValueError(f"Năm không hợp lệ: {year}")
            
            # Sử dụng calendar.monthrange() - thư viện chuẩn Python
            first_weekday, days_in_month = calendar.monthrange(year, month)
            
            working_days = 0
            
            # Duyệt qua từng ngày trong tháng
            for day in range(1, days_in_month + 1):
                # Tạo đối tượng datetime - thư viện chuẩn Python
                date_obj = datetime(year, month, day)
                
                # Lấy thứ trong tuần: 0=Monday, 1=Tuesday, ..., 6=Sunday
                weekday = date_obj.weekday()
                
                if weekday != 6:  # Không phải chủ nhật
                    working_days += 1
            
            return working_days
            
        except Exception as e:
            print(f"Lỗi tính toán ngày làm việc cho {month}/{year}: {e}")
            # Fallback: ước tính an toàn
            return 26  # Giá trị mặc định

    def get_month_info(self, year, month):
        """
        Lấy thông tin chi tiết về tháng
        """
        try:
            # Validation
            if not (1 <= month <= 12):
                raise ValueError(f"Tháng không hợp lệ: {month}")
            if not (1900 <= year <= 2100):
                raise ValueError(f"Năm không hợp lệ: {year}")
            
            # Tính toán cơ bản
            days_in_month = calendar.monthrange(year, month)[1]
            is_leap = calendar.isleap(year)
            working_days = self.calculate_working_days(year, month)
            sundays_count = days_in_month - working_days
            
            # Tên tháng tiếng Việt
            month_names = [
                "", "Tháng Một", "Tháng Hai", "Tháng Ba", "Tháng Tư", "Tháng Năm", "Tháng Sáu",
                "Tháng Bảy", "Tháng Tám", "Tháng Chín", "Tháng Mười", "Tháng Mười Một", "Tháng Mười Hai"
            ]
            
            # Thông tin đặc biệt
            special_info = ""
            if month == 2:
                if is_leap:
                    special_info = f"Năm nhuận - {days_in_month} ngày"
                else:
                    special_info = f"Năm thường - {days_in_month} ngày"
            elif days_in_month == 30:
                special_info = "Tháng nhỏ - 30 ngày"
            elif days_in_month == 31:
                special_info = "Tháng lớn - 31 ngày"
            
            # Tính phần trăm ngày làm việc
            work_percentage = round((working_days / days_in_month) * 100, 1)
            
            return {
                'days_in_month': days_in_month,
                'is_leap_year': is_leap,
                'month_name': month_names[month],
                'special_info': special_info,
                'working_days': working_days,
                'sundays_count': sundays_count,
                'work_percentage': work_percentage,
                'validation_passed': True
            }
            
        except Exception as e:
            print(f"Lỗi lấy thông tin tháng {month}/{year}: {e}")
            return {
                'days_in_month': 30,
                'working_days': 26,
                'validation_passed': False,
                'error': str(e)
            }

    def update_working_days_display(self):
        """Cập nhật hiển thị số ngày làm việc"""
        try:
            # Lấy tháng và năm được chọn
            month, year = self.get_selected_month_year()
            
            # Tính số ngày làm việc
            working_days = self.calculate_working_days(year, month)
            
            # Lấy thông tin chi tiết
            month_info = self.get_month_info(year, month)
            
            if month_info:
                # Cập nhật label nếu có reference
                if hasattr(self, 'working_days_value_label'):
                    self.working_days_value_label.setText(str(working_days))
                    
                    # Tạo tooltip đơn giản
                    tooltip_text = f"""
{month_info['month_name']} {year}
Tổng số ngày: {month_info['days_in_month']} ngày
Số ngày làm việc: {working_days} ngày
Số chủ nhật: {month_info['days_in_month'] - working_days}
{month_info['special_info']}
                    """
                    self.working_days_value_label.setToolTip(tooltip_text.strip())
            
            return working_days
            
        except Exception as e:
            print(f"Lỗi cập nhật hiển thị: {e}")
            return 0

    def init_ui(self):
        # Layout chính
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(5)  # Giảm spacing từ 10 xuống 5
        main_layout.setContentsMargins(10, 10, 10, 10)

        # Panel chọn thông tin (nằm ngoài scroll area)
        filter_panel = self.create_filter_panel()
        main_layout.addWidget(filter_panel, 0, Qt.AlignHCenter)

        # Layout chứa phần nội dung chính (có 3 phần: trái, giữa, phải)
        content_main_layout = QHBoxLayout()
        
        # Panel bên trái - thông tin nghỉ phép
        left_panel = self.create_left_panel()
        content_main_layout.addWidget(left_panel)

        # Tạo scroll area cho phiếu lương (giữa)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setFixedWidth(self.PHIEU_LUONG_WIDTH + 20)
        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollBar:vertical {
                width: 10px;
                background: #f0f0f0;
            }
            QScrollBar::handle:vertical {
                background: #c1c1c1;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical:hover {
                background: #a8a8a8;
            }
        """)

        # Widget chứa nội dung phiếu lương
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setSpacing(3)  # Giảm spacing từ 8 xuống 3
        content_layout.setContentsMargins(5, 5, 5, 5)

        # Phiếu lương container
        phieu_luong_container = QGroupBox()
        phieu_luong_container.setFixedWidth(self.PHIEU_LUONG_WIDTH)
        phieu_luong_container.setStyleSheet("""
            QGroupBox {
                border: 2px solid #ddd;
                border-radius: 8px;
                background-color: white;
                font-family: "Times New Roman";
            }
            QLabel {
                font-family: "Times New Roman";
            }
            QTableWidget {
                font-family: "Times New Roman";
            }
        """)
        phieu_layout = QVBoxLayout(phieu_luong_container)
        phieu_layout.setSpacing(3)  # Giảm spacing từ 8 xuống 3
        phieu_layout.setContentsMargins(8, 8, 8, 8)  # Giảm margins từ 10 xuống 8

        # Tiêu đề phiếu lương
        title = self.create_title()
        phieu_layout.addWidget(title)

        # Thông tin cơ bản
        info_panel = self.create_info_panel()
        phieu_layout.addWidget(info_panel)

        # Thông tin kỳ lương và ngày xuất
        period_panel = self.create_period_panel()
        phieu_layout.addWidget(period_panel)

        # Các phần chi tiết lương
        # Tạo các bảng và gán tên
        self.tableLuongCoBan = self.create_luong_coban_table()
        self.tableThemGio = self.create_them_gio_table()
        self.tablePhuCap = self.create_phu_cap_table()
        self.tableKPI = self.create_kpi_table()
        
        sections = [
            ("A) LƯƠNG CƠ BẢN", self.tableLuongCoBan),
            ("B) THÊM GIỜ", self.tableThemGio),
            ("C) PHỤ CẤP", self.tablePhuCap),
            ("D) KPI (NĂNG SUẤT)", self.tableKPI)
        ]

        for title, table in sections:
            section = self.create_section(title, table)
            phieu_layout.addWidget(section)

        # Tổng cộng I
        tong_cong = self.create_tong_cong_panel()
        phieu_layout.addWidget(tong_cong)

        # Khấu trừ và thanh toán
        self.tableKhauTru = self.create_khau_tru_table()
        self.tableMuaSam = self.create_mua_sam_table()
        
        khau_tru = self.create_section("E) CÁC KHOẢN KHẤU TRỪ", self.tableKhauTru)
        mua_sam = self.create_section("F) THANH TOÁN MUA SẮM", self.tableMuaSam)
        phieu_layout.addWidget(khau_tru)
        phieu_layout.addWidget(mua_sam)

        # Thực nhận
        thuc_nhan = self.create_thuc_nhan_panel()
        phieu_layout.addWidget(thuc_nhan)

        # Thêm phiếu lương container vào content layout
        content_layout.addWidget(phieu_luong_container, 0, Qt.AlignRight)

        # Đặt content widget vào scroll area
        scroll.setWidget(content_widget)
        content_main_layout.addWidget(scroll)

        # Panel bên phải - nút bảng thuế
        right_panel = self.create_right_panel()
        content_main_layout.addWidget(right_panel)

        main_layout.addLayout(content_main_layout)

        # Panel nút thao tác (nằm ngoài scroll area)
        action_panel = self.create_action_panel()
        action_panel.setFixedWidth(self.PHIEU_LUONG_WIDTH)
        main_layout.addWidget(action_panel, 0, Qt.AlignHCenter)
        
        # Tooltip đã được thiết lập trực tiếp khi tạo các item

    def create_filter_panel(self):
        """Tạo panel lọc dữ liệu"""
        filter_panel = QGroupBox("Lọc dữ liệu")
        filter_layout = QHBoxLayout()  # Thêm dòng này
        
        # Tháng
        month_label = QLabel("Tháng:")
        self.comboThang = QComboBox()
        self.populate_month_combo()
        
        # Năm
        year_label = QLabel("Năm:")
        self.comboNam = QComboBox()
        self.populate_year_combo()
        
        # Nhân viên
        employee_label = QLabel("Nhân viên:")
        self.comboNhanVien = QComboBox()
        self.populate_employee_combo()
        
        # Thêm các widget vào layout
        filter_layout.addWidget(month_label)
        filter_layout.addWidget(self.comboThang)
        filter_layout.addWidget(year_label)
        filter_layout.addWidget(self.comboNam)
        filter_layout.addWidget(employee_label)
        filter_layout.addWidget(self.comboNhanVien)
        
        # Nút quản lý ngày lễ tết
        holiday_btn = QPushButton("Quản lý ngày lễ tết")
        holiday_btn.clicked.connect(self.show_holiday_manager)
        holiday_btn.setStyleSheet("""
            QPushButton {
                background-color: #17a2b8;
                color: white;
                border: none;
                padding: 8px 15px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #138496;
            }
        """)
        filter_layout.addWidget(holiday_btn)
        
        # Nút refresh dữ liệu
        refresh_btn = QPushButton("🔄 Refresh")
        refresh_btn.clicked.connect(self.refresh_all_data)
        refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                border: none;
                padding: 8px 15px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #218838;
            }
        """)
        refresh_btn.setToolTip("Cập nhật dữ liệu mới từ bảng công và quy định lương")
        filter_layout.addWidget(refresh_btn)
        

        
        # Kết nối signals
        self.comboThang.currentTextChanged.connect(self.on_month_changed)
        self.comboNam.currentTextChanged.connect(self.on_month_changed)
        self.comboNhanVien.currentTextChanged.connect(self.on_employee_changed)
        
        filter_panel.setLayout(filter_layout)
        return filter_panel

    def get_salary_month_and_year(self):
        """
        Xác định tháng và năm lương dựa trên quy tắc công ty:
        - Trước ngày 16: tháng lương = tháng trước
        - Từ ngày 16 trở đi: tháng lương = tháng hiện tại
        """
        try:
            from datetime import datetime
            
            today = datetime.now()
            current_day = today.day
            current_month = today.month
            current_year = today.year
            
            if current_day < 16:
                # Trước ngày 16 → tháng lương là tháng trước
                if current_month == 1:
                    salary_month = 12
                    salary_year = current_year - 1
                else:
                    salary_month = current_month - 1
                    salary_year = current_year
            else:
                # Từ ngày 16 trở đi → tháng lương là tháng hiện tại
                salary_month = current_month
                salary_year = current_year
            
            return salary_month, salary_year
            
        except Exception as e:
            print(f"Lỗi xác định tháng lương: {e}")
            # Fallback về tháng hiện tại
            today = datetime.now()
            return today.month, today.year

    def populate_month_combo(self):
        """Tạo danh sách tháng đơn giản (1-12)"""
        try:
            # Lấy tháng lương mặc định theo logic ngày 16
            default_month, default_year = self.get_salary_month_and_year()
            
            # Tạo danh sách tháng đơn giản
            months = []
            for i in range(1, 13):
                months.append(f"Tháng {i}")
            
            # Thêm vào combobox
            self.comboThang.clear()
            self.comboThang.addItems(months)
            
            # Set mặc định từ dữ liệu chấm công nếu có, nếu không thì dùng logic ngày 16
            if self.data_chamcong:
                # Tìm tháng/năm có dữ liệu
                available_months = set()
                for employee_data in self.data_chamcong.values():
                    for month_year in employee_data.keys():
                        if '/' in month_year:
                            month, year = month_year.split('/')
                            available_months.add((int(month), int(year)))
                
                if available_months:
                    # Lấy tháng/năm đầu tiên có dữ liệu
                    first_month, first_year = sorted(available_months)[0]
                    default_month = first_month
                    default_year = first_year
            
            # Set mặc định
            default_index = default_month - 1  # Index từ 0
            if 0 <= default_index < 12:
                self.comboThang.setCurrentIndex(default_index)
                
        except Exception as e:
            print(f"Lỗi tạo danh sách tháng: {e}")

    def populate_year_combo(self):
        """Tạo danh sách năm đơn giản"""
        try:
            # Lấy năm lương mặc định theo logic ngày 16
            _, default_year = self.get_salary_month_and_year()
            
            # Tạo danh sách năm đơn giản
            years = []
            for year in range(default_year - 3, default_year + 3):
                years.append(str(year))
            
            # Thêm vào combobox
            self.comboNam.clear()
            self.comboNam.addItems(years)
            
            # Set mặc định từ dữ liệu chấm công nếu có, nếu không thì dùng logic ngày 16
            if self.data_chamcong:
                # Tìm tháng/năm có dữ liệu
                available_months = set()
                for employee_data in self.data_chamcong.values():
                    for month_year in employee_data.keys():
                        if '/' in month_year:
                            month, year = month_year.split('/')
                            available_months.add((int(month), int(year)))
                
                if available_months:
                    # Lấy tháng/năm đầu tiên có dữ liệu
                    first_month, first_year = sorted(available_months)[0]
                    default_year = first_year
            
            # Set mặc định
            default_index = self.comboNam.findText(str(default_year))
            if default_index >= 0:
                self.comboNam.setCurrentIndex(default_index)
                
        except Exception as e:
            print(f"Lỗi tạo danh sách năm: {e}")

    def get_selected_month_year(self):
        """Lấy tháng và năm được chọn"""
        try:
            # Lấy tháng từ comboThang (format: "Tháng X")
            month_text = self.comboThang.currentText()
            if not month_text or month_text.strip() == "":
                # Nếu combo tháng trống, sử dụng index
                month = self.comboThang.currentIndex() + 1
                if month <= 0:
                    month = 8  # Mặc định tháng 8
            elif "Tháng " in month_text:
                month = int(month_text.replace("Tháng ", ""))
            else:
                # Fallback: lấy index + 1
                month = self.comboThang.currentIndex() + 1
            
            # Lấy năm từ comboNam
            year_text = self.comboNam.currentText()
            if not year_text or year_text.strip() == "":
                # Nếu combo năm trống, sử dụng năm hiện tại
                year = 2025
            else:
                year = int(year_text)
            
            # Validation
            if not (1 <= month <= 12):
                print(f"Tháng không hợp lệ: {month}, sử dụng tháng 8")
                month = 8
            if not (1900 <= year <= 2100):
                print(f"Năm không hợp lệ: {year}, sử dụng năm 2025")
                year = 2025
            
            return month, year
            
        except Exception as e:
            print(f"Lỗi lấy tháng/năm được chọn: {e}")
            # Fallback về tháng lương mặc định
            return 8, 2025  # Tháng 8/2025

    def on_month_changed(self):
        """Xử lý khi thay đổi tháng"""
        self.update_working_days_display()
        # Cập nhật thông tin tháng/năm trong panel thông tin
        if hasattr(self, 'labelThangNam'):
            selected_month, selected_year = self.get_selected_month_year()
            self.labelThangNam.setText(f"Tháng {selected_month:02d}/{selected_year}")
        
        # Xóa dữ liệu cũ trước khi tải dữ liệu mới
        self.clear_salary_data()
        
        # Tự động điền lại dữ liệu nếu đã chọn nhân viên
        if self.current_employee:
            self.auto_fill_salary_data()
            # Tải dữ liệu tạm ứng và vi phạm cho tháng mới
            self.load_tam_ung_vi_pham_data()

    def on_employee_changed(self):
        """Xử lý khi thay đổi nhân viên"""
        try:
            selected_employee = self.comboNhanVien.currentText()
            # print(f"Debug: on_employee_changed - selected_employee = {selected_employee}")
            
            # Xóa dữ liệu cũ trước khi tải dữ liệu mới
            self.clear_salary_data()
            
            if selected_employee and selected_employee != "---":
                self.current_employee = selected_employee
                # print(f"Debug: Đã chọn nhân viên: {self.current_employee}")
                self.update_employee_info()
                self.auto_fill_salary_data()
            else:
                self.current_employee = None
                # print("Debug: Không chọn nhân viên nào")
                self.update_employee_info()
        except Exception as e:
            print(f"Lỗi khi thay đổi nhân viên: {e}")
            import traceback
            traceback.print_exc()

    def auto_fill_salary_data(self):
        """Tự động điền dữ liệu lương dựa trên nhân viên và tháng được chọn"""
        try:
            # print("=== BẮT ĐẦU auto_fill_salary_data ===")
            
            if not self.current_employee:
                # print("Debug: Không có nhân viên được chọn")
                return
            
            # print(f"Debug: Nhân viên hiện tại = {self.current_employee}")
            
            # Lấy tháng và năm được chọn
            month, year = self.get_selected_month_year()
            # print(f"Debug: Tháng/Năm được chọn = {month}/{year}")
            
            # Lấy dữ liệu chấm công
            month_year = f"{month:02d}/{year}"
            # print(f"Debug: month_year = {month_year}")
            
            chamcong_data = self.get_chamcong_data(month_year)
            # print(f"Debug: chamcong_data từ get_chamcong_data = {chamcong_data}")
            
            # Lấy dữ liệu lương
            luong_data = self.get_luong_data()
            # print(f"Debug: luong_data = {luong_data}")
            
            # Điền dữ liệu chấm công
            if chamcong_data:
                # print("Debug: Có dữ liệu chấm công, gọi fill_chamcong_data")
                try:
                    self.fill_chamcong_data(chamcong_data)
                    # print("Debug: Đã gọi xong fill_chamcong_data")
                except Exception as e:
                    # print(f"Debug: LỖI khi gọi fill_chamcong_data: {e}")
                    pass
                    import traceback
                    traceback.print_exc()
            else:
                # print("Debug: KHÔNG CÓ dữ liệu chấm công!")
                pass
                # Xóa dữ liệu cũ nếu không có dữ liệu mới
                self.clear_salary_data()
            
            # Điền dữ liệu lương
            if luong_data:
                # print("Debug: Có dữ liệu lương, gọi fill_luong_data")
                self.fill_luong_data(luong_data)
            else:
                # print("Debug: KHÔNG CÓ dữ liệu lương!")
                pass
                # Xóa dữ liệu cũ nếu không có dữ liệu mới
                self.clear_salary_data()
            
            # print("=== KẾT THÚC auto_fill_salary_data ===")
            
            # Đảm bảo tổng cộng được cập nhật cuối cùng
            self.update_totals()

            # Căn giữa toàn bộ bảng sau khi dữ liệu đã được điền
            self.center_all_tables()
            
            # Tooltip đã được thiết lập tự động khi điền dữ liệu
            
            # Tự động gửi dữ liệu sang tab tổng lương
            if self.current_employee:
                print("=== TỰ ĐỘNG GỬI DỮ LIỆU SANG TỔNG LƯƠNG ===")
                self.send_salary_data_to_tong_luong()
            
        except Exception as e:
            print(f"Lỗi tự động điền dữ liệu lương: {e}")
            import traceback
            traceback.print_exc()

    def get_chamcong_data(self, month_year):
        """Lấy dữ liệu chấm công cho tháng/năm cụ thể"""
        try:
            print(f"🔍 TÌM DỮ LIỆU CHẤM CÔNG: {self.current_employee} - {month_year}")
            
            if not self.data_chamcong:
                print("❌ Không có dữ liệu chấm công!")
                return None
            
            if not self.current_employee:
                print("❌ Không có nhân viên được chọn!")
                return None
            
            # Lấy tên nhân viên
            employee_name = self.current_employee
            if isinstance(employee_name, dict):
                employee_name = employee_name.get('ho_ten', '')
            
            # Tìm dữ liệu cho nhân viên theo tên
            employee_data = self.data_chamcong.get(employee_name, {})
            
            if not employee_data:
                print(f"❌ Không tìm thấy dữ liệu cho nhân viên: {employee_name}")
                print(f"   Danh sách nhân viên có dữ liệu: {list(self.data_chamcong.keys())}")
                return None
            
            # Lấy dữ liệu cho tháng/năm cụ thể
            chamcong_data = employee_data.get(month_year, {})
            
            if not chamcong_data:
                # Thử tìm với tháng/năm khác nếu không tìm thấy
                available_months = [key for key in employee_data.keys() if isinstance(key, str) and '/' in key]
                print(f"❌ Không tìm thấy dữ liệu cho tháng {month_year}")
                print(f"   Các tháng có sẵn: {available_months}")
                
                if available_months:
                    # Lấy tháng đầu tiên có dữ liệu
                    chamcong_data = employee_data.get(available_months[0], {})
                    print(f"✅ Sử dụng dữ liệu tháng: {available_months[0]}")
            
            if chamcong_data:
                pass
            else:
                pass
            
            return chamcong_data
            
        except Exception as e:
            print(f"Lỗi lấy dữ liệu chấm công: {e}")
            import traceback
            traceback.print_exc()
            return None

    def get_luong_data(self):
        """Lấy dữ liệu quy định lương cho nhân viên"""
        try:
            if not self.current_employee:
                return {}
            
            if self.ds_luong:
                # ds_luong là tuple với 2 phần: (nhan_vien_list, cong_ty_list)
                if isinstance(self.ds_luong, tuple) and len(self.ds_luong) >= 2:
                    nhan_vien_list = self.ds_luong[0]  # Phần 1: danh sách nhân viên
                    
                    for i, luong in enumerate(nhan_vien_list):
                        # Format: [msnv, ho_ten, cccd, luong_co_ban, ...]
                        if isinstance(luong, list) and len(luong) > 1:
                            ho_ten = luong[1] if luong[1] else ""  # Index 1 là họ tên
                            
                            if ho_ten == self.current_employee:
                                # print(f"🔍 TÌM THẤY DỮ LIỆU LƯƠNG: {ho_ten}")
                                # print(f"   MSNV: {luong[0]}")
                                # try:
                                #     luong_co_ban = int(luong[3]) if luong[3] else 0
                                #     print(f"   Lương cơ bản: {luong_co_ban:,} VNĐ")
                                # except:
                                #     print(f"   Lương cơ bản: {luong[3]} VNĐ")
                                return luong
                else:
                    # Fallback: xử lý như list thông thường
                    for i, luong in enumerate(self.ds_luong):
                        if isinstance(luong, list) and len(luong) > 0:
                            ho_ten = luong[0] if luong[0] else ""
                        elif isinstance(luong, dict) and 'ho_ten' in luong:
                            ho_ten = luong['ho_ten']
                        else:
                            continue
                        
                        if ho_ten == self.current_employee:
                            # print(f"🔍 TÌM THẤY DỮ LIỆU LƯƠNG: {ho_ten}")
                            return luong
                
            print(f"❌ KHÔNG TÌM THẤY dữ liệu lương cho: {self.current_employee}")
            return {}
        except Exception as e:
            print(f"Lỗi lấy dữ liệu lương: {e}")
            import traceback
            traceback.print_exc()
            return {}

    def fill_chamcong_data(self, chamcong_data):
        """Điền dữ liệu từ chấm công vào các bảng"""
        try:
            print("=== BẮT ĐẦU fill_chamcong_data ===")
            
            # Xử lý cấu trúc dữ liệu mới từ file JSON
            days_detail = chamcong_data.get('days_detail', {})
            if not days_detail:
                # print("Debug: Không có days_detail trong chamcong_data")
                return
            
            # Tính toán từ dữ liệu chi tiết
            ngay_tinh_luong = 0
            ot_150_hours = 0
            sunday_200_hours = 0
            holiday_300_hours = 0
            ngay_cong_truong = 0
            ngay_dao_tao = 0
            ngay_van_phong = 0
            ngay_nghi_co_phep = 0  # Số ngày nghỉ có phép
            ngay_nghi_khong_phep = 0  # Số ngày nghỉ không phép
            tong_xang_xe = 0  # Tổng xăng xe từ tất cả ngày
            tong_dien_thoai = 0  # Tổng điện thoại từ tất cả ngày
            tong_khach_san = 0  # Tổng khách sạn từ tất cả ngày
            nang_suat_paut = 0  # Tổng số mét vượt PAUT
            nang_suat_tofd = 0  # Tổng số mét vượt TOFD
            
            # Xử lý từng ngày
            for day_key, day_data in days_detail.items():
                if isinstance(day_data, dict):
                    day_type = day_data.get('type', '')
                    overtime_hours = day_data.get('overtime_hours', 0)
                    location = day_data.get('location', '')
                    
                    # Đếm ngày làm việc
                    if day_type in ['W', 'O', 'T']:
                        ngay_tinh_luong += 1
                    
                    # Phân loại ngày
                    if day_type == 'W':  # Công trường
                        ngay_cong_truong += 1
                    elif day_type == 'O':  # Văn phòng
                        ngay_van_phong += 1
                    elif day_type == 'T':  # Đào tạo
                        ngay_dao_tao += 1
                    elif day_type == 'P':  # Nghỉ có phép
                        ngay_nghi_co_phep += 1
                    elif day_type == 'N':  # Nghỉ không phép
                        ngay_nghi_khong_phep += 1
                    
                    # Tính thêm giờ (giả sử tất cả là OT 150%)
                    if overtime_hours > 0:
                        ot_150_hours += overtime_hours
                    
                    # Tính xăng xe cho ngày công trường có địa điểm
                    if day_type == 'W' and location:
                        try:
                            ds_luong, ds_phu_cap = self.data_manager.load_quydinh_luong()
                            if ds_phu_cap:
                                # Tạo danh sách tên công ty từ quy định phụ cấp
                                company_list = [phu_cap[0] for phu_cap in ds_phu_cap 
                                              if isinstance(phu_cap, list) and len(phu_cap) >= 3 and phu_cap[0]]
                                
                                # Sử dụng company matcher để tìm công ty phù hợp
                                matched_company, similarity_score = self.company_matcher.match_company(location, company_list)
                                
                                print(f"Debug Company Matching: '{location}' -> '{matched_company}' (score: {similarity_score:.3f})")
                                
                                # Kiểm tra xem có phải công ty mới không
                                if similarity_score < 0.7:
                                    # print(f"Debug: Phát hiện công ty mới '{location}' - Hiện popup thêm mới")
                                    
                                    # Hiện popup thêm công ty mới
                                    dialog = NewCompanyDialog(location, self)
                                    if dialog.exec_() == QDialog.Accepted:
                                        result = dialog.get_result()
                                        if result:
                                            # Thêm công ty mới vào quy định phụ cấp
                                            new_company = [
                                                result['company_name'],
                                                result['don_gia_le'],
                                                result['chi_phi']
                                            ]
                                            
                                            # Cập nhật danh sách phụ cấp
                                            ds_phu_cap.append(new_company)
                                            
                                            # Lưu vào file
                                            self.data_manager.save_quydinh_luong(ds_luong, ds_phu_cap)
                                            
                                            # Cập nhật CompanyMatcher
                                            self.company_matcher.add_company_alias(
                                                result['company_name'], 
                                                result['company_name']
                                            )
                                            
                                            # print(f"Debug: Đã thêm công ty mới '{result['company_name']}' vào quy định phụ cấp")
                                            
                                            # Tính xăng xe với công ty mới
                                            gas_amount = float(str(result['chi_phi']).replace(',', '')) if result['chi_phi'] else 0
                                            tong_xang_xe += gas_amount
                                            # print(f"Debug: Gas amount cho công ty mới: {gas_amount:,}")
                                        else:
                                            pass
                                            # print(f"Debug: User hủy thêm công ty mới '{location}'")
                                    else:
                                        pass
                                        # print(f"Debug: User hủy popup thêm công ty mới '{location}'")
                                else:
                                    # Tìm địa điểm trong quy định phụ cấp công trường
                                    for phu_cap in ds_phu_cap:
                                        if isinstance(phu_cap, list) and len(phu_cap) >= 3:
                                            dia_diem = phu_cap[0] if phu_cap[0] else ""
                                            # Sử dụng kết quả matching thay vì so sánh trực tiếp
                                            if dia_diem == matched_company or (similarity_score >= 0.7 and dia_diem.lower() == matched_company.lower()):
                                                gas_amount = float(str(phu_cap[2]).replace(',', '')) if phu_cap[2] else 0
                                                tong_xang_xe += gas_amount
                                                # print(f"Debug: Matched company '{dia_diem}' -> Gas amount: {gas_amount:,}")
                                                break
                        except Exception as e:
                            print(f"Lỗi tính xăng xe cho ngày {day_key}: {e}")
                    
                    # Tính điện thoại và khách sạn từ dữ liệu JSON
                    phone_expense = day_data.get('phone_expense', 0)
                    hotel_expense = day_data.get('hotel_expense', 0)
                    
                    # Tính điện thoại: lấy trực tiếp số tiền
                    if isinstance(phone_expense, (int, float)):
                        tong_dien_thoai += phone_expense
                    
                    # Tính khách sạn: lấy trực tiếp số tiền
                    if isinstance(hotel_expense, (int, float)):
                        tong_khach_san += hotel_expense
                    
                    # Tính số mét vượt PAUT và TOFD
                    paut_meters = day_data.get('paut_meters', 0)
                    tofd_meters = day_data.get('tofd_meters', 0)
                    
                    if isinstance(paut_meters, (int, float)) and paut_meters > 0:
                        nang_suat_paut += paut_meters
                    
                    if isinstance(tofd_meters, (int, float)) and tofd_meters > 0:
                        nang_suat_tofd += tofd_meters
            
            print(f"=== DEBUG: DỮ LIỆU CHẤM CÔNG ===")
            print(f"Ngày làm việc: {ngay_tinh_luong} ngày")
            print(f"Phân loại: Công trường={ngay_cong_truong}, Văn phòng={ngay_van_phong}, Đào tạo={ngay_dao_tao}")
            print(f"Thêm giờ: {ot_150_hours} giờ")
            print(f"Phụ cấp: Xăng xe={tong_xang_xe:,}, Điện thoại={tong_dien_thoai:,}, Khách sạn={tong_khach_san:,}")
            print(f"Năng suất: PAUT={nang_suat_paut:.2f}m, TOFD={nang_suat_tofd:.2f}m")
            
            # A) LƯƠNG CƠ BẢN - Số ngày làm việc
            if hasattr(self, 'tableLuongCoBan'):
                self.tableLuongCoBan.setItem(0, 0, QTableWidgetItem(str(ngay_tinh_luong)))
        
            # B) THÊM GIỜ - Lấy từ dữ liệu chấm công
            if hasattr(self, 'tableThemGio'):
                # Lấy lương cơ bản để tính thành tiền thêm giờ
                luong_data = self.get_luong_data()
                luong_co_ban = 0
                if luong_data and isinstance(luong_data, list) and len(luong_data) > 3:
                    luong_co_ban = float(str(luong_data[3]).replace(',', '')) if luong_data[3] else 0  # Index 3 là lương cơ bản
                
                # Tính thành tiền thêm giờ
                luong_1_gio = luong_co_ban / 176  # Lương 1 giờ
                thanh_tien_150 = luong_1_gio * ot_150_hours * 1.5  # 150%
                thanh_tien_200 = luong_1_gio * sunday_200_hours * 2.0  # 200%
                thanh_tien_300 = luong_1_gio * holiday_300_hours * 3.0  # 300%
                
                            # Điền số giờ và thành tiền vào bảng với tooltip
            self.tableThemGio.setItem(0, 1, QTableWidgetItem(f"{ot_150_hours:.2f}"))
            thanh_tien_150_item = QTableWidgetItem(f"{thanh_tien_150:,.0f}")
            thanh_tien_150_item.setToolTip("🔍 CÔNG THỨC\nThêm giờ 150% = Số giờ × Lương 1 giờ × 1.5")
            self.tableThemGio.setItem(0, 2, thanh_tien_150_item)
            
            self.tableThemGio.setItem(1, 1, QTableWidgetItem(f"{sunday_200_hours:.2f}"))
            thanh_tien_200_item = QTableWidgetItem(f"{thanh_tien_200:,.0f}")
            thanh_tien_200_item.setToolTip("🔍 CÔNG THỨC\nThêm giờ 200% = Số giờ × Lương 1 giờ × 2.0")
            self.tableThemGio.setItem(1, 2, thanh_tien_200_item)
            
            self.tableThemGio.setItem(2, 1, QTableWidgetItem(f"{holiday_300_hours:.2f}"))
            thanh_tien_300_item = QTableWidgetItem(f"{thanh_tien_300:,.0f}")
            thanh_tien_300_item.setToolTip("🔍 CÔNG THỨC\nThêm giờ 300% = Số giờ × Lương 1 giờ × 3.0")
            self.tableThemGio.setItem(2, 2, thanh_tien_300_item)
            
            # Tính tổng thu nhập thêm giờ
            total_overtime_hours = ot_150_hours + sunday_200_hours + holiday_300_hours
            total_overtime_amount = thanh_tien_150 + thanh_tien_200 + thanh_tien_300
            
            self.tableThemGio.setItem(3, 1, QTableWidgetItem(f"{total_overtime_hours:.2f}"))
            total_overtime_item = QTableWidgetItem(f"{total_overtime_amount:,.0f}")
            total_overtime_item.setToolTip("🔍 CÔNG THỨC\nTổng thêm giờ = Thành tiền 150% + Thành tiền 200% + Thành tiền 300%")
            self.tableThemGio.setItem(3, 2, total_overtime_item)
            
            # print(f"=== DEBUG: THÊM GIỜ ===")
                        # print(f"Lương cơ bản: {luong_co_ban:,}")
            # print(f"Lương 1 giờ: {luong_1_gio:,.0f} = {luong_co_ban:,} ÷ 176")
            # print(f"150%: {ot_150_hours} giờ × {luong_1_gio:,.0f} × 1.5 = {thanh_tien_150:,.0f}")
            # print(f"200%: {sunday_200_hours} giờ × {luong_1_gio:,.0f} × 2.0 = {thanh_tien_200:,.0f}")
            # print(f"300%: {holiday_300_hours} giờ × {luong_1_gio:,.0f} × 3.0 = {thanh_tien_300:,.0f}")
            # print(f"Tổng thêm giờ: {total_overtime_amount:,.0f}")
            
            # C) PHỤ CẤP - Đếm số ngày theo loại
            if hasattr(self, 'tablePhuCap'):
                # Điền số ngày vào bảng phụ cấp với kiểm tra
                try:
                    # Kiểm tra xem bảng có item sẵn không
                    for i in range(3):
                        if not self.tablePhuCap.item(i, 1):
                            self.tablePhuCap.setItem(i, 1, QTableWidgetItem(""))
                    
                    # Điền trực tiếp vào item có sẵn
                    self.tablePhuCap.item(0, 1).setText(str(ngay_cong_truong))
                    self.tablePhuCap.item(1, 1).setText(str(ngay_dao_tao))
                    self.tablePhuCap.item(2, 1).setText(str(ngay_van_phong))
                    
                    # Tính thành tiền phụ cấp
                    if luong_data and isinstance(luong_data, list) and len(luong_data) > 6:
                        pc_cong_truong = float(str(luong_data[4]).replace(',', '')) if luong_data[4] else 0  # PC-công trường (index 4)
                        pc_chuc_danh = float(str(luong_data[5]).replace(',', '')) if luong_data[5] else 0  # PC-chức danh (index 5)
                        
                        # print(f"=== DEBUG: PHỤ CẤP ===")
                        # print(f"PC-công trường: {pc_cong_truong:,}")
                        # print(f"PC-chức danh: {pc_chuc_danh:,}")
                        # print(f"Số ngày: Công trường={ngay_cong_truong}, Đào tạo={ngay_dao_tao}, Văn phòng={ngay_van_phong}")
                        
                        # Tính thành tiền theo công thức
                        thanh_tien_cong_truong = ngay_cong_truong * pc_cong_truong
                        thanh_tien_dao_tao = ngay_dao_tao * (pc_cong_truong * 0.4)
                        thanh_tien_van_phong = ngay_van_phong * (pc_cong_truong * 0.2)
                        
                        # print(f"Công trường: {ngay_cong_truong} ngày × {pc_cong_truong:,} = {thanh_tien_cong_truong:,}")
                        # print(f"Đào tạo: {ngay_dao_tao} ngày × {pc_cong_truong:,} × 0.4 = {thanh_tien_dao_tao:,}")
                        # print(f"Văn phòng: {ngay_van_phong} ngày × {pc_cong_truong:,} × 0.2 = {thanh_tien_van_phong:,}")
                        
                        # Tính số ngày chức danh
                        month_year = self.get_selected_month_year()
                        if month_year:
                            year, month = month_year
                            ngay_lam_viec_thang = self.calculate_working_days(year, month)
                        else:
                            ngay_lam_viec_thang = 27
                        
                        if ngay_lam_viec_thang > 0:
                            ngay_chuc_danh = (ngay_cong_truong / ngay_lam_viec_thang)
                        else:
                            ngay_chuc_danh = 0
                        
                        thanh_tien_chuc_danh = ngay_chuc_danh * pc_chuc_danh
                        
                        # print(f"Chức danh: {ngay_chuc_danh:.2f} ngày × {pc_chuc_danh:,} = {thanh_tien_chuc_danh:,}")
                        # print(f"Xăng xe: {tong_xang_xe:,}")
                        # print(f"Điện thoại: {tong_dien_thoai:,}")
                        # print(f"Khách sạn: {tong_khach_san:,}")
                        
                        # Điền thành tiền vào bảng với tooltip
                        pc_cong_truong_item = QTableWidgetItem(f"{thanh_tien_cong_truong:,.0f}")
                        pc_cong_truong_item.setToolTip("🔍 CÔNG THỨC\nPC Công trường = Số ngày công trường × Mức phụ cấp công trường")
                        self.tablePhuCap.setItem(0, 2, pc_cong_truong_item)
                        
                        pc_dao_tao_item = QTableWidgetItem(f"{thanh_tien_dao_tao:,.0f}")
                        pc_dao_tao_item.setToolTip("🔍 CÔNG THỨC\nPC Đào tạo = Số ngày đào tạo × (Mức phụ cấp công trường × 0.4)")
                        self.tablePhuCap.setItem(1, 2, pc_dao_tao_item)
                        
                        pc_van_phong_item = QTableWidgetItem(f"{thanh_tien_van_phong:,.0f}")
                        pc_van_phong_item.setToolTip("🔍 CÔNG THỨC\nPC Văn phòng = Số ngày văn phòng × (Mức phụ cấp công trường × 0.2)")
                        self.tablePhuCap.setItem(2, 2, pc_van_phong_item)
                        
                        self.tablePhuCap.setItem(3, 1, QTableWidgetItem(f"{ngay_chuc_danh:.2f}"))
                        pc_chuc_danh_item = QTableWidgetItem(f"{thanh_tien_chuc_danh:,.0f}")
                        pc_chuc_danh_item.setToolTip("🔍 CÔNG THỨC\nPC Chức danh = (Số ngày công trường ÷ Số ngày làm việc chuẩn tháng) × Mức phụ cấp chức danh")
                        self.tablePhuCap.setItem(3, 2, pc_chuc_danh_item)
                        
                        # Thêm xăng xe, điện thoại, khách sạn vào bảng phụ cấp với tooltip
                        self.tablePhuCap.setItem(4, 1, QTableWidgetItem(""))
                        xang_xe_item = QTableWidgetItem(f"{tong_xang_xe:,.0f}")
                        xang_xe_item.setToolTip("🔍 CÔNG THỨC\nXăng xe = Tổng chi phí xăng xe từ dữ liệu chấm công (theo công ty)")
                        self.tablePhuCap.setItem(4, 2, xang_xe_item)
                        
                        self.tablePhuCap.setItem(5, 1, QTableWidgetItem(""))
                        dien_thoai_item = QTableWidgetItem(f"{tong_dien_thoai:,.0f}")
                        dien_thoai_item.setToolTip("🔍 CÔNG THỨC\nĐiện thoại = Tổng chi phí điện thoại từ dữ liệu chấm công")
                        self.tablePhuCap.setItem(5, 2, dien_thoai_item)
                        
                        self.tablePhuCap.setItem(6, 1, QTableWidgetItem(""))
                        khach_san_item = QTableWidgetItem(f"{tong_khach_san:,.0f}")
                        khach_san_item.setToolTip("🔍 CÔNG THỨC\nKhách sạn = Tổng chi phí khách sạn từ dữ liệu chấm công")
                        self.tablePhuCap.setItem(6, 2, khach_san_item)
                    else:
                        print("Không có dữ liệu PC để tính thành tiền!")
                    
                    # Force update table
                    self.tablePhuCap.update()
                    
                except Exception as e:
                    print(f"Lỗi khi điền bảng phụ cấp: {e}")
                    import traceback
                    traceback.print_exc()
            
            # D) KPI - Năng suất
            if hasattr(self, 'tableKPI'):
                nang_suat_ut = chamcong_data.get('nang_suat_ut', 0)
                # Số mét vượt PAUT/TOFD lấy từ tính toán ở trên
                
                # Lấy dữ liệu lương để tính phụ cấp năng suất
                luong_data = self.get_luong_data()
                pc_nang_suat_paut = 0
                pc_nang_suat_tofd = 0
                
                if luong_data and isinstance(luong_data, list) and len(luong_data) > 8:
                    pc_nang_suat_paut = float(str(luong_data[8]).replace(',', '')) if luong_data[8] else 0  # PAUT
                if luong_data and isinstance(luong_data, list) and len(luong_data) > 9:
                    pc_nang_suat_tofd = float(str(luong_data[9]).replace(',', '')) if luong_data[9] else 0  # TOFD
                
                # Tính tiền năng suất PAUT và TOFD
                tien_nang_suat_paut = nang_suat_paut * pc_nang_suat_paut
                tien_nang_suat_tofd = nang_suat_tofd * pc_nang_suat_tofd
                
                # Hàng 0 = PAUT, Hàng 1 = TOFD
                self.tableKPI.setItem(0, 1, QTableWidgetItem(f"{nang_suat_paut:.2f}"))
                self.tableKPI.setItem(1, 1, QTableWidgetItem(f"{nang_suat_tofd:.2f}"))
                
                # Điền thành tiền vào cột 2 với tooltip
                kpi_paut_item = QTableWidgetItem(f"{tien_nang_suat_paut:,.0f}")
                kpi_paut_item.setToolTip("🔍 CÔNG THỨC\nKPI PAUT = Số mét vượt PAUT × Đơn giá phụ cấp PAUT")
                self.tableKPI.setItem(0, 2, kpi_paut_item)
                
                kpi_tofd_item = QTableWidgetItem(f"{tien_nang_suat_tofd:,.0f}")
                kpi_tofd_item.setToolTip("🔍 CÔNG THỨC\nKPI TOFD = Số mét vượt TOFD × Đơn giá phụ cấp TOFD")
                self.tableKPI.setItem(1, 2, kpi_tofd_item)
                
                # Hàng tổng (row 2) = PAUT + TOFD
                tong_ns_amount = tien_nang_suat_paut + tien_nang_suat_tofd
                tong_kpi_item = QTableWidgetItem(f"{tong_ns_amount:,.0f}")
                tong_kpi_item.setToolTip("🔍 CÔNG THỨC\nTổng KPI = Thành tiền KPI PAUT + Thành tiền KPI TOFD")
                self.tableKPI.setItem(2, 2, tong_kpi_item)
                
                # print(f"=== DEBUG: KPI NĂNG SUẤT ===")
                # print(f"PAUT: {nang_suat_paut:.2f}m × {pc_nang_suat_paut:,} = {tien_nang_suat_paut:,.0f}")
                # print(f"TOFD: {nang_suat_tofd:.2f}m × {pc_nang_suat_tofd:,} = {tien_nang_suat_tofd:,.0f}")
                # print(f"Tổng KPI: {tong_ns_amount:,.0f}")

            # Điền vào bảng khấu trừ
            if hasattr(self, 'tableKhauTru'):
                tam_ung = chamcong_data.get('tam_ung', 0)
                # Tạm ứng nên ở ô (5,1), không phải (0,1)
                # Ô (0,1) là cho BHXH
                # self.tableKhauTru.setItem(0, 1, QTableWidgetItem(str(tam_ung)))  # Dòng cũ, sai vị trí
            
            # Điền vào bảng mua sắm (lấy từ bảng công)
            if hasattr(self, 'tableMuaSam'):
                # Tính tổng mua sắm từ dữ liệu chấm công
                tong_mua_sam = 0
                if 'days_detail' in chamcong_data:
                    for day_key, day_data in chamcong_data['days_detail'].items():
                        if isinstance(day_data, dict):
                            # Lấy chi phí mua sắm từ từng ngày
                            shopping_expense = day_data.get('shopping_expense', 0)
                            if isinstance(shopping_expense, (int, float)):
                                tong_mua_sam += shopping_expense
                
                mua_sam_item = QTableWidgetItem(f"{tong_mua_sam:,}")
                mua_sam_item.setToolTip("🔍 CÔNG THỨC\nMua sắm = Tổng chi phí mua sắm từ dữ liệu chấm công")
                self.tableMuaSam.setItem(0, 1, mua_sam_item)
            
            # Cập nhật tổng cộng và thực nhận
            self.update_totals()  # Bật lại để tính thành tiền cho phần B
            
            # Tải dữ liệu tạm ứng và vi phạm đã lưu
            self.load_tam_ung_vi_pham_data()
            
            # Cập nhật thông tin nghỉ phép trên giao diện
            self.update_attendance_info(ngay_nghi_co_phep, ngay_nghi_khong_phep)
            
            # print("=== KẾT THÚC fill_chamcong_data ===")
                
        except Exception as e:
            print(f"Lỗi điền dữ liệu chấm công: {e}")
            import traceback
            traceback.print_exc()

    def update_attendance_info(self, ngay_nghi_co_phep, ngay_nghi_khong_phep):
        """Cập nhật thông tin nghỉ phép trên giao diện"""
        try:
            # Cập nhật số ngày nghỉ có phép
            if hasattr(self, 'nghi_co_phep_label'):
                self.nghi_co_phep_label.setText(str(ngay_nghi_co_phep))
            
            # Cập nhật số ngày nghỉ không phép
            if hasattr(self, 'nghi_khong_phep_label'):
                self.nghi_khong_phep_label.setText(str(ngay_nghi_khong_phep))
            
            # Tính số ngày bị trừ (ngày nghỉ không phép sẽ bị trừ lương)
            ngay_bi_tru = ngay_nghi_khong_phep
            if hasattr(self, 'ngay_bi_tru_label'):
                self.ngay_bi_tru_label.setText(str(ngay_bi_tru))
            
            print(f"✅ Cập nhật thông tin nghỉ phép: Có phép={ngay_nghi_co_phep}, Không phép={ngay_nghi_khong_phep}, Bị trừ={ngay_bi_tru}")
            
        except Exception as e:
            print(f"Lỗi cập nhật thông tin nghỉ phép: {e}")

    def fill_luong_data(self, luong_data):
        """Điền dữ liệu từ quy định lương vào các bảng"""
        try:
            print(f"💰 ĐIỀN DỮ LIỆU LƯƠNG: {type(luong_data)}")
            
            # Xử lý format dữ liệu lương
            if isinstance(luong_data, list) and len(luong_data) > 0:
                # Format: [msnv, ho_ten, cccd, luong_co_ban, ngay_tinh_luong, pc_cong_trinh, pc_chuc_danh, pc_xang, pc_dien_thoai, ...]
                luong_co_ban = luong_data[3] if len(luong_data) > 3 and luong_data[3] else ""
                ngay_tinh_luong = luong_data[4] if len(luong_data) > 4 and luong_data[4] else ""
                pc_cong_trinh = luong_data[5] if len(luong_data) > 5 and luong_data[5] else ""
                pc_chuc_danh = luong_data[6] if len(luong_data) > 6 and luong_data[6] else ""
                pc_xang = luong_data[7] if len(luong_data) > 7 and luong_data[7] else ""
                pc_dien_thoai = luong_data[8] if len(luong_data) > 8 and luong_data[8] else ""
                print(f"   Lấy từ list - Lương cơ bản: {luong_co_ban}")
            elif isinstance(luong_data, dict):
                # Format: dict
                luong_co_ban = luong_data.get('luong_co_ban', "")
                ngay_tinh_luong = luong_data.get('ngay_tinh_luong', "")
                pc_cong_trinh = luong_data.get('pc_cong_trinh', "")
                pc_chuc_danh = luong_data.get('pc_chuc_danh', "")
                pc_xang = luong_data.get('pc_xang', "")
                pc_dien_thoai = luong_data.get('pc_dien_thoai', "")
                print(f"   Lấy từ dict - Lương cơ bản: {luong_co_ban}")
            else:
                # Fallback
                luong_co_ban = ngay_tinh_luong = pc_cong_trinh = pc_chuc_danh = pc_xang = pc_dien_thoai = ""
                print(f"   Fallback - Lương cơ bản: {luong_co_ban}")
            
            # Định dạng lương cơ bản với dấu phẩy
            def format_currency(value):
                """Định dạng số tiền với dấu phẩy"""
                try:
                    if value and str(value).strip():
                        # Chuyển thành số nguyên
                        num = int(float(str(value).replace(',', '')))
                        # Định dạng với dấu phẩy
                        return f"{num:,}"
                    return ""
                except:
                    return str(value) if value else ""
            
            # Điền vào bảng lương cơ bản
            if hasattr(self, 'tableLuongCoBan'):
                # Lấy số ngày làm việc thực tế từ dữ liệu chấm công
                month, year = self.get_selected_month_year()
                month_year = f"{month:02d}/{year}"
                chamcong_data = self.get_chamcong_data(month_year)
                
                # Tính số ngày làm việc thực tế
                total_working_days = 0
                if chamcong_data:
                    # Kiểm tra format dữ liệu
                    days_data = None
                    if 'days_detail' in chamcong_data:
                        # Format mới từ website
                        days_data = chamcong_data['days_detail']
                        # print("Debug: Sử dụng format mới (days_detail)")
                        # Đếm số ngày có type W, O, T
                        for day_key, day_info in days_data.items():
                            if isinstance(day_info, dict):
                                day_type = day_info.get('type', '')
                                if day_type in ['W', 'O', 'T']:  # Công trường, Văn phòng, Đào tạo
                                    total_working_days += 1
                    elif 'days' in chamcong_data:
                        # Format cũ
                        days_data = chamcong_data['days']
                        print("Debug: Sử dụng format cũ (days)")
                        # Đếm số ngày có dữ liệu chấm công (loại W, O, T)
                        for day_key, day_type in days_data.items():
                            if day_type in ['W', 'O', 'T']:  # Công trường, Văn phòng, Đào tạo
                                total_working_days += 1
                
                # Nếu không có dữ liệu chấm công, sử dụng số ngày làm việc trong tháng
                if total_working_days == 0:
                    print("⚠️ Không có dữ liệu chấm công, sử dụng số ngày làm việc chuẩn")
                    total_working_days = self.calculate_working_days(year, month)
                
                print(f"📅 Số ngày làm việc thực tế: {total_working_days}")
                print(f"📅 Số ngày làm việc chuẩn tháng: {self.calculate_working_days(year, month)}")
                
                # Tính lương cơ bản cho số ngày làm việc thực tế
                luong_co_ban_so = 0
                try:
                    if luong_co_ban and str(luong_co_ban).strip():
                        luong_co_ban_so = float(str(luong_co_ban).replace(',', ''))
                        print(f"💰 Lương cơ bản từ dữ liệu: {luong_co_ban_so:,} VNĐ")
                    else:
                        print(f"❌ Lương cơ bản rỗng hoặc None: {luong_co_ban}")
                except Exception as e:
                    print(f"❌ Lỗi parse lương cơ bản '{luong_co_ban}': {e}")
                    luong_co_ban_so = 0
                
                # Tính lương cơ bản 1 ngày
                working_days_in_month = self.calculate_working_days(year, month)
                luong_1_ngay = luong_co_ban_so / working_days_in_month if working_days_in_month > 0 else 0
                
                # Tính lương cơ bản cho số ngày làm việc thực tế
                luong_co_ban_thuc_te = luong_1_ngay * total_working_days
                
                print(f"🧮 TÍNH TOÁN LƯƠNG CƠ BẢN:")
                print(f"   Lương cơ bản tháng: {luong_co_ban_so:,} VNĐ")
                print(f"   Số ngày làm việc chuẩn: {working_days_in_month} ngày")
                print(f"   Lương 1 ngày: {luong_co_ban_so:,} ÷ {working_days_in_month} = {luong_1_ngay:,.0f} VNĐ")
                print(f"   Số ngày làm việc thực tế: {total_working_days} ngày")
                print(f"   Lương cơ bản thực tế: {total_working_days} × {luong_1_ngay:,.0f} = {luong_co_ban_thuc_te:,.0f} VNĐ")
                
                # Kiểm tra nếu lương cơ bản thực tế bằng 0 hoặc quá thấp
                if luong_co_ban_thuc_te == 0:
                    print("⚠️ CẢNH BÁO: Lương cơ bản thực tế = 0!")
                    print(f"   - Lương cơ bản tháng: {luong_co_ban_so:,}")
                    print(f"   - Số ngày làm việc thực tế: {total_working_days}")
                    print(f"   - Lương 1 ngày: {luong_1_ngay:,}")
                elif luong_co_ban_thuc_te < 1000000:  # Dưới 1 triệu
                    print("⚠️ CẢNH BÁO: Lương cơ bản thực tế quá thấp!")
                    print(f"   - Lương cơ bản thực tế: {luong_co_ban_thuc_te:,}")
                    print(f"   - Lương cơ bản tháng: {luong_co_ban_so:,}")
                    print(f"   - Số ngày làm việc thực tế: {total_working_days}")
                
                # Điền vào bảng với tooltip
                ngay_lam_item = QTableWidgetItem(str(total_working_days))
                ngay_lam_item.setToolTip("🔍 CÔNG THỨC\nSố ngày làm việc thực tế = Tổng số ngày có type W, O, T")
                self.tableLuongCoBan.setItem(0, 0, ngay_lam_item)
                
                luong_co_ban_item = QTableWidgetItem(f"{luong_co_ban_thuc_te:,.0f}")
                luong_co_ban_item.setToolTip("🔍 CÔNG THỨC\nLương cơ bản = Số ngày làm việc thực tế × (Lương cơ bản tháng ÷ Số ngày làm việc chuẩn tháng)")
                self.tableLuongCoBan.setItem(0, 2, luong_co_ban_item)
                
                ngay_tinh_item = QTableWidgetItem(str(ngay_tinh_luong))
                ngay_tinh_item.setToolTip("🔍 CÔNG THỨC\nSố ngày làm việc chuẩn trong tháng")
                self.tableLuongCoBan.setItem(1, 1, ngay_tinh_item)
            
            # Điền vào bảng phụ cấp - TẠM THỜI TẮT để tránh đè dữ liệu từ chamcong_data
            # if hasattr(self, 'tablePhuCap'):
            #     self.tablePhuCap.setItem(0, 1, QTableWidgetItem(format_currency(pc_cong_trinh)))
            #     self.tablePhuCap.setItem(1, 1, QTableWidgetItem(format_currency(pc_chuc_danh)))
            #     self.tablePhuCap.setItem(2, 1, QTableWidgetItem(format_currency(pc_xang)))
            #     self.tablePhuCap.setItem(3, 1, QTableWidgetItem(format_currency(pc_dien_thoai)))
                
            # Cập nhật tổng cộng sau khi điền dữ liệu lương
            self.update_totals()
            
            # Cập nhật tính toán BHXH
            self.update_bhxh_calculation()
                
        except Exception as e:
            print(f"Lỗi điền dữ liệu lương: {e}")

    def clear_salary_data(self):
        """Xóa tất cả dữ liệu trong form phiếu lương"""
        try:
            # print("Debug: Bắt đầu xóa dữ liệu phiếu lương")
            
            # Xóa thông tin nhân viên
            if hasattr(self, 'labelHoTen'):
                self.labelHoTen.setText("")
            if hasattr(self, 'labelMaSo'):
                self.labelMaSo.setText("")
            if hasattr(self, 'labelPhongBan'):
                self.labelPhongBan.setText("")
            if hasattr(self, 'labelChucVu'):
                self.labelChucVu.setText("")
            
            # Xóa bảng lương cơ bản
            if hasattr(self, 'tableLuongCoBan'):
                for row in range(self.tableLuongCoBan.rowCount()):
                    for col in range(self.tableLuongCoBan.columnCount()):
                        self.tableLuongCoBan.setItem(row, col, QTableWidgetItem(""))
            
            # Xóa bảng thêm giờ
            if hasattr(self, 'tableThemGio'):
                for row in range(self.tableThemGio.rowCount()):
                    for col in range(self.tableThemGio.columnCount()):
                        if col > 0:  # Giữ lại cột đầu (loại thêm giờ)
                            self.tableThemGio.setItem(row, col, QTableWidgetItem(""))
            
            # Xóa bảng phụ cấp
            if hasattr(self, 'tablePhuCap'):
                for row in range(self.tablePhuCap.rowCount()):
                    for col in range(self.tablePhuCap.columnCount()):
                        if col > 0:  # Giữ lại cột đầu (loại phụ cấp)
                            self.tablePhuCap.setItem(row, col, QTableWidgetItem(""))
            
            # Xóa bảng KPI
            if hasattr(self, 'tableKPI'):
                for row in range(self.tableKPI.rowCount()):
                    for col in range(self.tableKPI.columnCount()):
                        if col > 0:  # Giữ lại cột đầu
                            self.tableKPI.setItem(row, col, QTableWidgetItem(""))
            
            # Xóa bảng khấu trừ
            if hasattr(self, 'tableKhauTru'):
                for row in range(self.tableKhauTru.rowCount()):
                    for col in range(self.tableKhauTru.columnCount()):
                        if col > 0:  # Giữ lại cột đầu
                            self.tableKhauTru.setItem(row, col, QTableWidgetItem(""))
            
            # Xóa bảng mua sắm
            if hasattr(self, 'tableMuaSam'):
                for row in range(self.tableMuaSam.rowCount()):
                    for col in range(self.tableMuaSam.columnCount()):
                        if col > 0:  # Giữ lại cột đầu
                            self.tableMuaSam.setItem(row, col, QTableWidgetItem(""))
            
            # Xóa tổng cộng và thực nhận
            if hasattr(self, 'tong_cong_label'):
                self.tong_cong_label.setText("")
            if hasattr(self, 'thuc_nhan_label'):
                self.thuc_nhan_label.setText("")
            
            # Reset thông tin nghỉ phép
            if hasattr(self, 'nghi_co_phep_label'):
                self.nghi_co_phep_label.setText("")
            if hasattr(self, 'nghi_khong_phep_label'):
                self.nghi_khong_phep_label.setText("")
            if hasattr(self, 'ngay_bi_tru_label'):
                self.ngay_bi_tru_label.setText("")
            
            # print("Debug: Đã xóa xong tất cả dữ liệu phiếu lương")
                
        except Exception as e:
            print(f"Lỗi xóa dữ liệu phiếu lương: {e}")
            import traceback
            traceback.print_exc()

    def update_employee_info(self):
        """Cập nhật thông tin nhân viên từ dropdown"""
        try:
            if hasattr(self, 'comboNhanVien'):
                selected_name = self.comboNhanVien.currentText()
                print(f"🔍 Đang cập nhật thông tin cho: {selected_name}")
                
                if selected_name and selected_name != "-- Chọn nhân viên --":
                    # Cập nhật họ tên
                    if hasattr(self, 'labelHoTen'):
                        self.labelHoTen.setText(selected_name.upper())
                        print(f"✅ Đã cập nhật họ tên: {selected_name.upper()}")
                    
                    # Tìm thông tin chi tiết từ dữ liệu nhân viên
                    if self.ds_nhanvien:
                        print(f"📋 Tìm kiếm trong {len(self.ds_nhanvien)} nhân viên")
                        found = False
                        
                        for i, nv in enumerate(self.ds_nhanvien):
                            if isinstance(nv, list) and len(nv) >= 8:
                                # Cấu trúc: [ho_ten, cccd, msnv, sdt, ngay_sinh, que_quan, chuc_vu, phong_ban, trinh_do, ...]
                                ho_ten = nv[0] if nv[0] else ""
                                print(f"   So sánh: '{ho_ten}' vs '{selected_name}'")
                                
                                if ho_ten == selected_name:  # So sánh họ tên
                                    found = True
                                    print(f"✅ Tìm thấy nhân viên tại index {i}")
                                    
                                    # Cập nhật thông tin chi tiết
                                    if hasattr(self, 'labelChucVu'):
                                        chuc_vu = nv[6] if len(nv) > 6 and nv[6] else ""
                                        self.labelChucVu.setText(chuc_vu)
                                        print(f"   Chức vụ: {chuc_vu}")
                                    
                                    if hasattr(self, 'labelMSNV'):
                                        msnv = nv[2] if len(nv) > 2 and nv[2] else ""
                                        self.labelMSNV.setText(msnv)
                                        print(f"   MSNV: {msnv}")
                                    
                                    if hasattr(self, 'labelPhongBan'):
                                        phong_ban = nv[7] if len(nv) > 7 and nv[7] else ""
                                        self.labelPhongBan.setText(phong_ban)
                                        print(f"   Phòng ban: {phong_ban}")
                                    break
                        
                        if not found:
                            print(f"❌ Không tìm thấy nhân viên '{selected_name}' trong danh sách")
                            # Hiển thị danh sách nhân viên có sẵn để debug
                            print("📋 Danh sách nhân viên có sẵn:")
                            for i, nv in enumerate(self.ds_nhanvien[:5]):  # Chỉ hiển thị 5 nhân viên đầu
                                if isinstance(nv, list) and len(nv) > 0:
                                    print(f"   {i}: {nv[0]}")
                    else:
                        print("❌ Không có dữ liệu nhân viên (self.ds_nhanvien)")
                else:
                    print("❌ Không có nhân viên được chọn")
                    # Xóa thông tin khi không chọn nhân viên
                    if hasattr(self, 'labelHoTen'):
                        self.labelHoTen.setText("")
                    if hasattr(self, 'labelChucVu'):
                        self.labelChucVu.setText("")
                    if hasattr(self, 'labelMSNV'):
                        self.labelMSNV.setText("")
                    if hasattr(self, 'labelPhongBan'):
                        self.labelPhongBan.setText("")
        except Exception as e:
            print(f"❌ Lỗi cập nhật thông tin nhân viên: {e}")
            import traceback
            traceback.print_exc()

    def create_title(self):
        """Tạo tiêu đề phiếu lương"""
        title_container = QWidget()
        title_layout = QHBoxLayout(title_container)
        title_layout.setContentsMargins(0, 0, 0, 0)

        # Thêm logo
        logo_label = QLabel()
        logo_pixmap = QPixmap("logo_hitech.png")
        scaled_logo = logo_pixmap.scaled(60, 60, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        logo_label.setPixmap(scaled_logo)
        logo_label.setFixedSize(60, 60)
        title_layout.addWidget(logo_label)

        # Tiêu đề chính
        title_label = QLabel("PHIẾU LƯƠNG")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("""
            font-size: 20px;
            font-weight: bold;
            color: #2196F3;
            margin-top: 10px;
            margin-bottom: 10px;
        """)
        title_layout.addWidget(title_label)

        return title_container

    def create_info_panel(self):
        group = QGroupBox()
        group.setStyleSheet("""
            QGroupBox {
                border: none;
                background-color: #f8f9fa;
                padding: 1px;
                font-family: "Times New Roman";
            }
            QLabel {
                color: #495057;
                font-family: "Times New Roman";
            }
        """)
        # Giảm chiều cao để vừa đủ với nội dung
        group.setMaximumHeight(80)  # Thu hẹp để fit với chữ
        group.setFixedWidth(800) 
        # Layout chính ngang để chia 2 cột
        main_layout = QHBoxLayout(group)
        main_layout.setSpacing(30)  # Khoảng cách giữa 2 cột
        main_layout.setContentsMargins(8, 5, 8, 5)  # Giảm khoảng cách từ chữ đến mép trên/dưới
        
        # Thêm spacer bên trái để đẩy nội dung sang phải
        spacer = QSpacerItem(200, 10, QSizePolicy.Fixed, QSizePolicy.Minimum)
        main_layout.addItem(spacer)

        # Layout cho cột trái
        left_layout = QFormLayout()
        left_layout.setSpacing(5)  # Giảm spacing để gọn hơn
        
        # Tạo các label thông tin
        self.labelHoTen = QLabel("")
        self.labelMSNV = QLabel("")  # Mã số nhân viên
        
        # Cập nhật họ tên từ dropdown khi khởi tạo
        self.update_employee_info()
        
        left_layout.addRow("Họ và tên:", self.labelHoTen)
        left_layout.addRow("Mã số:", self.labelMSNV)
        
        # Layout cho cột phải
        right_layout = QFormLayout()
        right_layout.setSpacing(5)  # Giảm spacing để gọn hơn
        
        self.labelChucVu = QLabel("")
        self.labelPhongBan = QLabel("")
        
        right_layout.addRow("Chức vụ:", self.labelChucVu)
        right_layout.addRow("Phòng ban:", self.labelPhongBan)
        
        # Thêm 2 cột vào layout chính
        left_widget = QWidget()
        left_widget.setLayout(left_layout)
        right_widget = QWidget()
        right_widget.setLayout(right_layout)
        
        main_layout.addWidget(left_widget)
        main_layout.addWidget(right_widget)
        
        # Thêm spacer bên phải để cân đối
        spacer = QSpacerItem(20, 10, QSizePolicy.Fixed, QSizePolicy.Minimum)
        main_layout.addItem(spacer)
        
        return group

    def create_period_panel(self):
        """Tạo panel thông tin kỳ lương và ngày xuất"""
        group = QGroupBox()
        group.setStyleSheet("""
            QGroupBox {
                border: none;
                background-color: #f8f9fa;
                padding: 1px;
                font-family: "Times New Roman";
            }
            QLabel {
                color: #495057;
                font-family: "Times New Roman";
            }
        """)
        # Giảm chiều cao để vừa đủ với nội dung
        group.setMaximumHeight(60)  # Giảm thêm để ôm sát nội dung
        
        # Layout chính ngang để chia 2 cột
        main_layout = QHBoxLayout(group)
        main_layout.setSpacing(30)  # Khoảng cách giữa 2 cột
        main_layout.setContentsMargins(8, 1, 8, 1)  # Giảm khoảng cách từ chữ đến mép trên/dưới
        
        # Cột trái - Kỳ lương
        left_layout = QFormLayout()
        left_layout.setSpacing(5)  # Giảm spacing để gọn hơn
        
        # Lấy tháng và năm đã chọn
        selected_month, selected_year = self.get_selected_month_year()
        self.labelThangNam = QLabel(f"Tháng {selected_month:02d}/{selected_year}")
        
        left_layout.addRow("Kỳ lương:", self.labelThangNam)
        
        # Cột phải - Ngày xuất
        right_layout = QFormLayout()
        right_layout.setSpacing(5)  # Giảm spacing để gọn hơn
        
        # Ngày xuất phiếu (ngày hiện tại với giờ)
        current_date = datetime.now()
        self.labelNgayXuat = QLabel(current_date.strftime("%d/%m/%Y %H:%M"))
        
        right_layout.addRow("Ngày xuất:", self.labelNgayXuat)
        
        # Thêm 2 cột vào layout chính
        left_widget = QWidget()
        left_widget.setLayout(left_layout)
        right_widget = QWidget()
        right_widget.setLayout(right_layout)
        
        main_layout.addWidget(left_widget)
        main_layout.addWidget(right_widget)

        return group

    def create_section(self, title, content):
        group = QGroupBox()
        group.setFixedWidth(self.PHIEU_LUONG_WIDTH - 40)  # Trừ đi padding
        group.setStyleSheet("""
            QGroupBox {
                border: 1px solid #e9ecef;
                border-radius: 4px;
                margin-top: 5px;
                padding: 5px;
            }
            QLabel {
                color: #2c3e50;
                font-weight: bold;
                margin-bottom: 2px;
            }
        """)
        layout = QVBoxLayout(group)
        layout.setSpacing(1)  # Giảm spacing từ 2 xuống 1
        layout.setContentsMargins(3, 3, 3, 3)  # Giảm margins từ 5 xuống 3
        
        label = QLabel(title)
        font = QFont()
        font.setBold(True)
        label.setFont(font)
        
        layout.addWidget(label)
        layout.addWidget(content)
        return group

    def format_table(self, table):
        # Cố định kích thước bảng
        table_width = self.PHIEU_LUONG_WIDTH - 40  # Tăng chiều rộng để bằng với tổng cộng/thực nhận
        table.setFixedWidth(table_width)

        # Ẩn cột số thứ tự bên trái
        table.verticalHeader().setVisible(False)

        # Vô hiệu hóa selection và interaction
        table.setSelectionMode(QTableWidget.NoSelection)
        table.setFocusPolicy(Qt.NoFocus)
        table.setEditTriggers(QTableWidget.NoEditTriggers)

        table.setStyleSheet("""
            QTableWidget {
                border: none;
                gridline-color: #dee2e6;
                font-family: "Times New Roman";
            }
            QHeaderView::section {
                background-color: #f8f9fa;
                padding: 3px;
                border: 1px solid #dee2e6;
                font-weight: bold;
                color: #495057;
                font-family: "Times New Roman";
            }
            QTableWidget::item {
                padding: 3px;
                border: 1px solid #dee2e6;
                font-family: "Times New Roman";
            }
            QTableWidget::item:selected {
                background-color: transparent;
            }
        """)

        # Cố định chiều cao dòng - đủ để hiển thị nội dung
        table.verticalHeader().setDefaultSectionSize(25)
        table.verticalHeader().setSectionResizeMode(QHeaderView.Fixed)
        
        # Tắt scroll bars
        table.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        table.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        # Cố định độ rộng cột và vô hiệu hóa resize
        header = table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Fixed)
        header.setSectionsClickable(False)  # Vô hiệu hóa click header
        header.setDefaultAlignment(Qt.AlignCenter)  # Căn giữa tiêu đề cột
        
        # Tính toán và cố định độ rộng cho mỗi cột với kích thước mới
        num_columns = table.columnCount()
        if num_columns == 2:
            col_widths = [int(table_width * 0.6), int(table_width * 0.4)]
        elif num_columns == 3:
            # Điều chỉnh độ rộng cho bảng khấu trừ có 3 cột
            if table == getattr(self, 'tableKhauTru', None):
                col_widths = [int(table_width * 0.35), int(table_width * 0.25), int(table_width * 0.4)]
            else:
                col_widths = [int(table_width * 0.4), int(table_width * 0.3), int(table_width * 0.3)]
        
        for col, width in enumerate(col_widths):
            table.setColumnWidth(col, width)

        # Cố định kích thước bảng - chiều cao = header + các dòng nội dung
        rows = table.rowCount()
        header_height = 30  # Header thường cao hơn
        row_height = 28     # Chiều cao mỗi dòng nội dung
        total_height = header_height + (rows * (row_height+4))
        table.setFixedHeight(total_height)
        
        # Căn chỉnh text và cố định các ô
        for row in range(table.rowCount()):
            for col in range(table.columnCount()):
                item = table.item(row, col)
                if item:
                    # Vô hiệu hóa hoàn toàn việc chỉnh sửa và tương tác
                    item.setFlags(Qt.ItemIsEnabled)  # Chỉ cho phép hiển thị, không cho tương tác
                    
                    # Căn giữa cho tất cả các ô
                    item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)

        table.setAlternatingRowColors(True)
        table.setShowGrid(True)

    def center_table_content(self, table):
        """Căn giữa toàn bộ nội dung bảng (tiêu đề và tất cả ô)."""
        try:
            if not table:
                return
            # Căn giữa tiêu đề cột
            table.horizontalHeader().setDefaultAlignment(Qt.AlignCenter)
            # Căn giữa toàn bộ ô
            for row in range(table.rowCount()):
                for col in range(table.columnCount()):
                    item = table.item(row, col)
                    if item is None:
                        item = QTableWidgetItem("")
                        table.setItem(row, col, item)
                    item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        except Exception as e:
            print(f"Lỗi căn giữa bảng: {e}")

    def center_all_tables(self):
        """Căn giữa toàn bộ nội dung cho tất cả các bảng trong tab Phiếu lương."""
        try:
            for tbl_name in [
                "tableLuongCoBan",
                "tableThemGio",
                "tablePhuCap",
                "tableKPI",
                "tableKhauTru",
                "tableMuaSam",
            ]:
                if hasattr(self, tbl_name):
                    self.center_table_content(getattr(self, tbl_name))
        except Exception as e:
            print(f"Lỗi căn giữa tất cả bảng: {e}")

    def create_action_panel(self):
        group = QGroupBox()
        group.setStyleSheet("""
            QGroupBox {
                border: none;
            }
            QPushButton {
                padding: 8px 15px;
                border-radius: 4px;
                color: white;
                font-weight: bold;
                min-width: 100px;
            }
            QPushButton#print {
                background-color: #28a745;
            }
            QPushButton#print:hover {
                background-color: #218838;
            }
            QPushButton#excel {
                background-color: #17a2b8;
            }
            QPushButton#excel:hover {
                background-color: #138496;
            }
        """)
        layout = QHBoxLayout(group)

        self.btnInPhieu = QPushButton("In phiếu lương")
        self.btnInPhieu.setObjectName("print")
        self.btnXuatExcel = QPushButton("Xuất Excel")
        self.btnXuatExcel.setObjectName("excel")
        self.btnGuiTongLuong = QPushButton("📊 Gửi sang Tổng lương")
        self.btnGuiTongLuong.setObjectName("print")

        layout.addStretch()
        layout.addWidget(self.btnInPhieu)
        layout.addWidget(self.btnXuatExcel)
        layout.addWidget(self.btnGuiTongLuong)

        # Kết nối sự kiện
        self.btnInPhieu.clicked.connect(self.in_phieu_luong)
        self.btnXuatExcel.clicked.connect(self.xuat_excel)
        self.btnGuiTongLuong.clicked.connect(self.gui_sang_tong_luong)
        self.comboNhanVien.currentIndexChanged.connect(self.update_employee_info)
        self.comboNhanVien.currentIndexChanged.connect(self.load_phieu_luong)
        self.comboThang.currentIndexChanged.connect(self.load_phieu_luong)

        return group

    # [Giữ nguyên các hàm tạo bảng và xử lý sự kiện như cũ]
    def create_luong_coban_table(self):
        table = QTableWidget(1, 3)
        table.setHorizontalHeaderLabels(["Số ngày làm việc bình thường", "", "Thành tiền (vnđ)"])
        
        # Tạo item với tooltip
        ngay_lam_item = QTableWidgetItem("")
        ngay_lam_item.setToolTip("🔍 CÔNG THỨC\nSố ngày làm việc thực tế = Tổng số ngày có type W, O, T")
        table.setItem(0, 0, ngay_lam_item)
        
        luong_co_ban_item = QTableWidgetItem("")
        luong_co_ban_item.setToolTip("🔍 CÔNG THỨC\nLương cơ bản = Số ngày làm việc thực tế × (Lương cơ bản tháng ÷ Số ngày làm việc chuẩn tháng)")
        table.setItem(0, 2, luong_co_ban_item)
        
        self.format_table(table)
        return table

    def create_them_gio_table(self):
        table = QTableWidget(4, 3)
        table.setHorizontalHeaderLabels(["Loại thêm giờ", "Số giờ", "Thành tiền (vnđ)"])
        
        # Tạo các item với tooltip
        items = [
            ("150%", "", ""),
            ("200%", "", ""),
            ("300%", "", ""),
            ("Tổng thu nhập thêm giờ:", "", "")
        ]
        
        tooltips = [
            "🔍 CÔNG THỨC\nThêm giờ 150% = Số giờ × Lương 1 giờ × 1.5",
            "🔍 CÔNG THỨC\nThêm giờ 200% = Số giờ × Lương 1 giờ × 2.0",
            "🔍 CÔNG THỨC\nThêm giờ 300% = Số giờ × Lương 1 giờ × 3.0",
            "🔍 CÔNG THỨC\nTổng thêm giờ = Thành tiền 150% + Thành tiền 200% + Thành tiền 300%"
        ]
        
        for i, (loai, gio, tien) in enumerate(items):
            table.setItem(i, 0, QTableWidgetItem(loai))
            table.setItem(i, 1, QTableWidgetItem(gio))
            
            tien_item = QTableWidgetItem(tien)
            tien_item.setToolTip(tooltips[i])
            table.setItem(i, 2, tien_item)
            
        self.format_table(table)
        return table

    def create_phu_cap_table(self):
        table = QTableWidget(8, 3)
        table.setHorizontalHeaderLabels(["Loại phụ cấp", "Số ngày", "Thành tiền (vnđ)"])
        
        items = [
            ("Công trình (W)", "", ""),
            ("Đào tạo (T)", "", ""),
            ("Văn Phòng (O)", "", ""),
            ("Chức danh (hệ số)", "", ""),
            ("Xăng xe", "", ""),
            ("Điện thoại", "", ""),
            ("Khách sạn", "", ""),
            ("Tổng thu nhập phụ cấp:", "", "")
        ]
        
        tooltips = [
            "🔍 CÔNG THỨC\nPC Công trường = Số ngày công trường × Mức phụ cấp công trường",
            "🔍 CÔNG THỨC\nPC Đào tạo = Số ngày đào tạo × (Mức phụ cấp công trường × 0.4)",
            "🔍 CÔNG THỨC\nPC Văn phòng = Số ngày văn phòng × (Mức phụ cấp công trường × 0.2)",
            "🔍 CÔNG THỨC\nPC Chức danh = (Số ngày công trường ÷ Số ngày làm việc chuẩn tháng) × Mức phụ cấp chức danh",
            "🔍 CÔNG THỨC\nXăng xe = Tổng chi phí xăng xe từ dữ liệu chấm công (theo công ty)",
            "🔍 CÔNG THỨC\nĐiện thoại = Tổng chi phí điện thoại từ dữ liệu chấm công",
            "🔍 CÔNG THỨC\nKhách sạn = Tổng chi phí khách sạn từ dữ liệu chấm công",
            "🔍 CÔNG THỨC\nTổng phụ cấp = PC Công trường + PC Đào tạo + PC Văn phòng + PC Chức danh + Xăng xe + Điện thoại + Khách sạn"
        ]
        
        for i, (loai, ngay, tien) in enumerate(items):
            table.setItem(i, 0, QTableWidgetItem(loai))
            table.setItem(i, 1, QTableWidgetItem(ngay))
            
            tien_item = QTableWidgetItem(tien)
            tien_item.setToolTip(tooltips[i])
            table.setItem(i, 2, tien_item)
            
        self.format_table(table)
        return table

    def create_kpi_table(self):
        table = QTableWidget(3, 3)
        table.setHorizontalHeaderLabels(["", "Số mét vượt", "Thành tiền (vnđ)"])
        table.setItem(0, 0, QTableWidgetItem("PAUT"))
        table.setItem(1, 0, QTableWidgetItem("TOFD"))
        table.setItem(2, 0, QTableWidgetItem("Tổng thu nhập năng suất:"))
        self.format_table(table)
        return table

    def create_khau_tru_table(self):
        table = QTableWidget(8, 2)
        table.setHorizontalHeaderLabels(["Hệ số bảo hiểm", "Thành tiền (vnđ)"])
        items = [
            ("", ""),  # Sẽ được cập nhật bởi update_bhxh_calculation
            ("Thuế TNCN", ""),
            ("Thu nhập chịu thuế", ""),
            ("Giảm trừ gia cảnh", ""),
            ("Bậc thuế", ""),
            ("Tạm ứng:", "0"),
            ("Vi phạm:", "0"),
            ("Tổng khấu trừ:", "")
        ]
        for i, (ten, tien) in enumerate(items):
            table.setItem(i, 0, QTableWidgetItem(ten))
            table.setItem(i, 1, QTableWidgetItem(tien))
        
        self.format_table(table)
        return table

    def create_mua_sam_table(self):
        table = QTableWidget(1, 2)
        table.setHorizontalHeaderLabels(["", "Thành tiền (vnđ)"])
        
        # Mua sắm lấy từ bảng công, không nhập tay
        table.setItem(0, 0, QTableWidgetItem("Mua sắm:"))
        table.setItem(0, 1, QTableWidgetItem("0"))
        
        self.format_table(table)
        return table

    def create_tong_cong_panel(self):
        group = QGroupBox()
        group.setFixedWidth(self.PHIEU_LUONG_WIDTH - 40)  # Đồng nhất với các bảng
        group.setStyleSheet("""
            QGroupBox {
                border: 1px solid #e9ecef;
                border-radius: 4px;
                background-color: #f8f9fa;
            }
            QLabel {
                color: #2c3e50;
                font-weight: bold;
            }
        """)
        layout = QHBoxLayout(group)
        layout.setContentsMargins(8, 5, 8, 5)  # Giảm margins của tổng cộng
        layout.addWidget(QLabel("(I)Tổng cộng (vnđ)=(A)+(B)+(C)+(D):"))
        tong = QLabel("")
        tong.setAlignment(Qt.AlignCenter)  # Căn giữa như cột thành tiền
        tong.setToolTip("🔍 CÔNG THỨC\nTổng cộng = Lương cơ bản + Thêm giờ + Phụ cấp + KPI")
        layout.addWidget(tong)
        
        # Lưu reference để có thể cập nhật sau
        self.tong_cong_label = tong
        
        return group

    def create_thuc_nhan_panel(self):
        group = QGroupBox()
        group.setFixedWidth(self.PHIEU_LUONG_WIDTH - 40)  # Đồng nhất với các bảng
        group.setStyleSheet("""
            QGroupBox {
                border: 2px solid #495057;
                border-radius: 4px;
                background-color: #f8f9fa;
            }
        """)
        layout = QHBoxLayout(group)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Label tiêu đề với font lớn hơn một chút
        title_label = QLabel("THỰC NHẬN (VNĐ)=I-E+F:")
        title_font = QFont("Times New Roman")
        title_font.setBold(True)
        title_font.setPointSize(12)  # Tăng nhẹ từ default
        title_label.setFont(title_font)
        title_label.setStyleSheet("color: #495057; font-family: 'Times New Roman';")
        layout.addWidget(title_label)
        
        # Số tiền với font lớn hơn và đậm
        thuc_nhan = QLabel("")
        thuc_nhan.setAlignment(Qt.AlignCenter)
        money_font = QFont("Times New Roman")
        money_font.setBold(True)
        money_font.setPointSize(14)  # Lớn hơn nhưng vừa phải
        thuc_nhan.setFont(money_font)
        thuc_nhan.setStyleSheet("""
            QLabel {
                color: #212529;
                font-weight: bold;
                font-family: "Times New Roman";
            }
        """)
        thuc_nhan.setToolTip("🔍 CÔNG THỨC\nThực nhận = Tổng cộng - Tổng khấu trừ + Mua sắm")
        layout.addWidget(thuc_nhan)
        
        # Lưu reference để có thể cập nhật sau
        self.thuc_nhan_label = thuc_nhan
        
        return group

    def create_left_panel(self):
        group = QGroupBox("Thông tin chấm công")
        group.setFixedWidth(220)
        group.setStyleSheet("""
            QGroupBox {
                border: 2px solid #007bff;
                border-radius: 8px;
                background-color: #f8f9fa;
                font-weight: bold;
                color: #007bff;
                padding-top: 15px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                background-color: #f8f9fa;
            }
        """)
        
        layout = QVBoxLayout(group)
        layout.setSpacing(15)
        layout.setContentsMargins(15, 20, 15, 15)
        
        # Tính số ngày làm việc trong tháng hiện tại
        current_date = QDate.currentDate()
        working_days = self.calculate_working_days(current_date.year(), current_date.month())
        
        # Thông tin chấm công
        info_items = [
            ("Số ngày trong tháng tối đa\n(không bao gồm chủ nhật):", str(working_days), "#28a745", True, "working_days"),
            ("Số ngày nghỉ có phép\ntrong tháng:", "", "#17a2b8", False, "nghi_co_phep"),
            ("Số ngày nghỉ không phép\ntrong tháng:", "", "#ffc107", False, "nghi_khong_phep"), 
            ("Số ngày bị trừ:", "", "#dc3545", False, "ngay_bi_tru")
        ]
        
        for i, (label_text, value, color, is_working_days, field_name) in enumerate(info_items):
            # Container cho mỗi item
            item_container = QFrame()
            item_container.setStyleSheet(f"""
                QFrame {{
                    background-color: white;
                    border: 1px solid {color};
                    border-radius: 6px;
                    padding: 8px;
                }}
            """)
            
            item_layout = QVBoxLayout(item_container)
            item_layout.setSpacing(5)
            item_layout.setContentsMargins(8, 8, 8, 8)
            
            # Label
            label = QLabel(label_text)
            label.setWordWrap(True)
            label.setAlignment(Qt.AlignCenter)
            label.setStyleSheet(f"""
                QLabel {{
                    color: #495057;
                    font-size: 11px;
                    font-weight: normal;
                    border: none;
                }}
            """)
            
            # Value
            value_label = QLabel(value)
            value_label.setAlignment(Qt.AlignCenter)
            value_label.setStyleSheet(f"""
                QLabel {{
                    font-weight: bold; 
                    color: {color};
                    font-size: 18px;
                    border: none;
                    padding: 5px;
                }}
            """)
            
            # Lưu reference cho các label để có thể cập nhật sau
            if field_name == "working_days":
                self.working_days_value_label = value_label
                # Thêm tooltip mặc định
                month_info = self.get_month_info(current_date.year(), current_date.month())
                if month_info:
                    tooltip_text = f"""
{month_info['month_name']} {current_date.year()}
Tổng số ngày: {month_info['days_in_month']}
Số ngày làm việc: {working_days}
Số chủ nhật: {month_info['days_in_month'] - working_days}
{month_info['special_info']}
                    """
                    value_label.setToolTip(tooltip_text.strip())
            elif field_name == "nghi_co_phep":
                self.nghi_co_phep_label = value_label
                # Khởi tạo với giá trị 0
                self.nghi_co_phep_label.setText("0")
            elif field_name == "nghi_khong_phep":
                self.nghi_khong_phep_label = value_label
                # Khởi tạo với giá trị 0
                self.nghi_khong_phep_label.setText("0")
            elif field_name == "ngay_bi_tru":
                self.ngay_bi_tru_label = value_label
                # Khởi tạo với giá trị 0
                self.ngay_bi_tru_label.setText("0")
            
            item_layout.addWidget(label)
            item_layout.addWidget(value_label)
            layout.addWidget(item_container)
        
        # Thêm một chút space ở cuối
        layout.addStretch()
        
        return group

    def create_right_panel(self):
        """Tạo panel bên phải với nút thuế và nhập liệu"""
        right_panel = QWidget()
        right_panel.setStyleSheet("""
            QWidget {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 5px;
                padding: 15px;
            }
        """)
        
        layout = QVBoxLayout(right_panel)
        layout.setSpacing(10)
        
        # Tiêu đề
        title_label = QLabel("Bảng thuế")
        title_label.setStyleSheet("""
            QLabel {
                font-weight: bold;
                font-size: 14px;
                color: #495057;
                margin-bottom: 10px;
            }
        """)
        layout.addWidget(title_label)
        
        # Nút bảng thuế - fit content
        btn_tax_table = QPushButton("Bảng thuế TNCN")
        btn_tax_table.setStyleSheet("""
            QPushButton {
                background-color: #17a2b8;
                color: white;
                border: none;
                padding: 8px 12px;
                border-radius: 4px;
                font-size: 13px;
                text-align: center;
            }
            QPushButton:hover {
                background-color: #138496;
            }
        """)
        btn_tax_table.clicked.connect(self.show_tax_table)
        layout.addWidget(btn_tax_table)
        
        # Nút cài đặt BHXH - fit content  
        btn_bhxh_settings = QPushButton("Cài đặt BHXH")
        btn_bhxh_settings.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                border: none;
                padding: 6px 10px;
                border-radius: 4px;
                font-size: 12px;
                text-align: center;
            }
            QPushButton:hover {
                background-color: #218838;
            }
        """)
        btn_bhxh_settings.clicked.connect(self.show_bhxh_settings)
        layout.addWidget(btn_bhxh_settings)
        
        # Thêm separator
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        separator.setStyleSheet("background-color: #dee2e6; margin: 10px 0;")
        layout.addWidget(separator)
        
        # Tiêu đề nhập liệu
        input_title = QLabel("Nhập liệu")
        input_title.setStyleSheet("""
            QLabel {
                font-weight: bold;
                font-size: 14px;
                color: #495057;
                margin-bottom: 10px;
            }
        """)
        layout.addWidget(input_title)
        
        # Nút nhập tạm ứng
        btn_tam_ung = QPushButton("Nhập tạm ứng")
        btn_tam_ung.setStyleSheet("""
            QPushButton {
                background-color: #ffc107;
                color: #212529;
                border: none;
                padding: 6px 10px;
                border-radius: 4px;
                font-size: 12px;
                text-align: center;
            }
            QPushButton:hover {
                background-color: #e0a800;
            }
        """)
        btn_tam_ung.clicked.connect(lambda: self.show_input_dialog("tam_ung", "Nhập số tiền tạm ứng:"))
        layout.addWidget(btn_tam_ung)
        
        # Nút nhập vi phạm
        btn_vi_pham = QPushButton("Nhập vi phạm")
        btn_vi_pham.setStyleSheet("""
            QPushButton {
                background-color: #dc3545;
                color: white;
                border: none;
                padding: 6px 10px;
                border-radius: 4px;
                font-size: 12px;
                text-align: center;
            }
            QPushButton:hover {
                background-color: #c82333;
            }
        """)
        btn_vi_pham.clicked.connect(lambda: self.show_input_dialog("vi_pham", "Nhập số tiền vi phạm:"))
        layout.addWidget(btn_vi_pham)
        
        layout.addStretch()
        
        # Set size policy để fit content
        right_panel.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
        
        return right_panel

    def show_tax_table(self):
        dialog = TaxTableDialog(self)
        dialog.exec_()

    def show_bhxh_settings(self):
        """Hiển thị dialog cài đặt mức lương cơ sở BHXH"""
        dialog = BHXHSettingsDialog(self, self.bhxh_salary_base)
        if dialog.exec_() == QDialog.Accepted:
            self.bhxh_salary_base = dialog.get_salary_base()
            # Cập nhật lại tính toán BHXH
            self.update_bhxh_calculation()
    
    def show_input_dialog(self, field_type, label_text):
        """Hiển thị dialog nhập liệu cho tạm ứng hoặc vi phạm"""
        try:
            # Lấy giá trị hiện tại
            current_value = 0
            if hasattr(self, 'tableKhauTru'):
                if field_type == "tam_ung":
                    item = self.tableKhauTru.item(5, 1)
                elif field_type == "vi_pham":
                    item = self.tableKhauTru.item(6, 1)
                else:
                    return
                
                if item and item.text():
                    try:
                        current_value = int(item.text().replace(',', ''))
                    except:
                        current_value = 0
            
            # Hiển thị dialog
            dialog = InputDialog(f"Nhập {field_type.replace('_', ' ').title()}", label_text, current_value, self)
            if dialog.exec_() == QDialog.Accepted:
                new_value = dialog.get_value()
                
                # Cập nhật vào bảng khấu trừ với tooltip
                if hasattr(self, 'tableKhauTru'):
                    month, year = self.get_selected_month_year()
                    month_year = f"{month:02d}/{year}"
                    
                    if field_type == "tam_ung":
                        tam_ung_item = QTableWidgetItem(f"{new_value:,}")
                        tam_ung_item.setToolTip(f"🔍 TẠM ỨNG\n💰 Số tiền tạm ứng: {new_value:,} VNĐ\n\n👤 Nhân viên: {self.current_employee}\n📅 Tháng: {month_year}\n\n📋 Thông tin:\n• Vừa cập nhật số tiền tạm ứng\n• Sẽ được trừ vào lương tháng này\n• Dữ liệu đã được lưu tự động\n\n✏️ Để chỉnh sửa: Click đúp vào ô này")
                        self.tableKhauTru.setItem(5, 1, tam_ung_item)
                    elif field_type == "vi_pham":
                        vi_pham_item = QTableWidgetItem(f"{new_value:,}")
                        vi_pham_item.setToolTip(f"🔍 VI PHẠM\n💰 Số tiền phạt: {new_value:,} VNĐ\n\n👤 Nhân viên: {self.current_employee}\n📅 Tháng: {month_year}\n\n📋 Thông tin:\n• Vừa cập nhật số tiền phạt\n• Sẽ được trừ vào lương tháng này\n• Dữ liệu đã được lưu tự động\n\n✏️ Để chỉnh sửa: Click đúp vào ô này")
                        self.tableKhauTru.setItem(6, 1, vi_pham_item)
                
                # Lưu dữ liệu cho nhân viên và tháng hiện tại
                self.save_tam_ung_vi_pham_data(field_type, new_value)
                
                # Cập nhật tổng khấu trừ và thực nhận
                self.update_total_deduction()
                
        except Exception as e:
            print(f"Lỗi hiển thị dialog nhập liệu: {e}")
    
    def save_tam_ung_vi_pham_data(self, field_type, value):
        """Lưu dữ liệu tạm ứng hoặc vi phạm cho nhân viên và tháng hiện tại"""
        try:
            if not self.current_employee:
                return
            
            # Lấy tháng/năm hiện tại
            month, year = self.get_selected_month_year()
            month_year = f"{month:02d}/{year}"
            
            # Khởi tạo dữ liệu cho nhân viên nếu chưa có
            if self.current_employee not in self.tam_ung_vi_pham_data:
                self.tam_ung_vi_pham_data[self.current_employee] = {}
            
            # Khởi tạo dữ liệu cho tháng/năm nếu chưa có
            if month_year not in self.tam_ung_vi_pham_data[self.current_employee]:
                self.tam_ung_vi_pham_data[self.current_employee][month_year] = {
                    "tam_ung": 0,
                    "vi_pham": 0
                }
            
            # Lưu giá trị mới
            self.tam_ung_vi_pham_data[self.current_employee][month_year][field_type] = value
            
            # Lưu vào file để không bị mất khi tắt ứng dụng
            self.save_tam_ung_vi_pham_to_file()
            
            print(f"Debug: Đã lưu {field_type} = {value:,} cho {self.current_employee} tháng {month_year}")
            
        except Exception as e:
            print(f"Lỗi lưu dữ liệu {field_type}: {e}")
    
    def load_tam_ung_vi_pham_data(self):
        """Tải dữ liệu tạm ứng và vi phạm cho nhân viên và tháng hiện tại"""
        try:
            if not self.current_employee or not hasattr(self, 'tableKhauTru'):
                return
            
            # Lấy tháng/năm hiện tại
            month, year = self.get_selected_month_year()
            month_year = f"{month:02d}/{year}"
            
            # Kiểm tra xem có dữ liệu đã lưu không
            if (self.current_employee in self.tam_ung_vi_pham_data and 
                month_year in self.tam_ung_vi_pham_data[self.current_employee]):
                
                data = self.tam_ung_vi_pham_data[self.current_employee][month_year]
                tam_ung = data.get("tam_ung", 0)
                vi_pham = data.get("vi_pham", 0)
                
                # Cập nhật vào bảng với tooltip
                tam_ung_item = QTableWidgetItem(f"{tam_ung:,}")
                tam_ung_item.setToolTip(f"🔍 TẠM ỨNG\n💰 Số tiền tạm ứng: {tam_ung:,} VNĐ\n\n👤 Nhân viên: {self.current_employee}\n📅 Tháng: {month_year}\n\n📋 Thông tin:\n• Đây là số tiền đã tạm ứng trước\n• Sẽ được trừ vào lương tháng này\n• Dữ liệu được lưu tự động\n\n✏️ Để chỉnh sửa: Click đúp vào ô này")
                self.tableKhauTru.setItem(5, 1, tam_ung_item)
                
                vi_pham_item = QTableWidgetItem(f"{vi_pham:,}")
                vi_pham_item.setToolTip(f"🔍 VI PHẠM\n💰 Số tiền phạt: {vi_pham:,} VNĐ\n\n👤 Nhân viên: {self.current_employee}\n📅 Tháng: {month_year}\n\n📋 Thông tin:\n• Đây là số tiền phạt do vi phạm\n• Sẽ được trừ vào lương tháng này\n• Dữ liệu được lưu tự động\n\n✏️ Để chỉnh sửa: Click đúp vào ô này")
                self.tableKhauTru.setItem(6, 1, vi_pham_item)
                
                # print(f"Debug: Đã tải dữ liệu cho {self.current_employee} tháng {month_year}: Tạm ứng={tam_ung:,}, Vi phạm={vi_pham:,}")
            else:
                # Nếu không có dữ liệu đã lưu, đặt về 0 với tooltip
                tam_ung_item = QTableWidgetItem("0")
                tam_ung_item.setToolTip(f"🔍 TẠM ỨNG\n💰 Số tiền tạm ứng: 0 VNĐ\n\n👤 Nhân viên: {self.current_employee}\n📅 Tháng: {month_year}\n\n📋 Thông tin:\n• Chưa có tạm ứng nào\n• Nếu có tạm ứng, sẽ được trừ vào lương\n\n✏️ Để nhập tạm ứng: Click đúp vào ô này")
                self.tableKhauTru.setItem(5, 1, tam_ung_item)
                
                vi_pham_item = QTableWidgetItem("0")
                vi_pham_item.setToolTip(f"🔍 VI PHẠM\n💰 Số tiền phạt: 0 VNĐ\n\n👤 Nhân viên: {self.current_employee}\n📅 Tháng: {month_year}\n\n📋 Thông tin:\n• Chưa có vi phạm nào\n• Nếu có vi phạm, sẽ được trừ vào lương\n\n✏️ Để nhập vi phạm: Click đúp vào ô này")
                self.tableKhauTru.setItem(6, 1, vi_pham_item)
                print(f"Debug: Không có dữ liệu đã lưu cho {self.current_employee} tháng {month_year}")
            
        except Exception as e:
            print(f"Lỗi tải dữ liệu tạm ứng/vi phạm: {e}")
    
    def save_tam_ung_vi_pham_to_file(self):
        """Lưu dữ liệu tạm ứng và vi phạm vào file"""
        try:
            file_path = os.path.join(self.data_manager.data_dir, "tam_ung_vi_pham.json")
            data = {
                "timestamp": datetime.now().isoformat(),
                "data": self.tam_ung_vi_pham_data
            }
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"Debug: Đã lưu dữ liệu tạm ứng/vi phạm vào {file_path}")
        except Exception as e:
            print(f"Lỗi lưu dữ liệu tạm ứng/vi phạm vào file: {e}")
    
    def load_tam_ung_vi_pham_from_file(self):
        """Tải dữ liệu tạm ứng và vi phạm từ file"""
        try:
            file_path = os.path.join(self.data_manager.data_dir, "tam_ung_vi_pham.json")
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.tam_ung_vi_pham_data = data.get("data", {})
                print(f"Debug: Đã tải dữ liệu tạm ứng/vi phạm từ {file_path}")
            else:
                print("Debug: Chưa có file dữ liệu tạm ứng/vi phạm")
        except Exception as e:
            print(f"Lỗi tải dữ liệu tạm ứng/vi phạm từ file: {e}")
            self.tam_ung_vi_pham_data = {}
    
    def get_deduction_amount(self, row):
        """Lấy số tiền khấu trừ từ bảng theo row"""
        try:
            if hasattr(self, 'tableKhauTru'):
                item = self.tableKhauTru.item(row, 1)
                if item and item.text():
                    # Bỏ qua các giá trị không phải số (như "Bậc 1")
                    if not item.text().startswith("Bậc"):
                        return int(item.text().replace(',', ''))
            return 0
        except:
            return 0
    
    def update_total_deduction(self):
        """Cập nhật tổng khấu trừ (E) = BHXH(10.5%) + Thuế TNCN + Tạm ứng + Vi phạm"""
        try:
            if not hasattr(self, 'tableKhauTru'):
                return
            
            total_deduction = 0
            
            # Chỉ cộng các khoản khấu trừ cần thiết:
            # Row 0: BHXH (10.5%)
            # Row 1: Thuế TNCN  
            # Row 5: Tạm ứng
            # Row 6: Vi phạm
            deduction_rows = [0, 1, 5, 6]
            
            for row in deduction_rows:
                item = self.tableKhauTru.item(row, 1)
                if item and item.text():
                    try:
                        # Bỏ qua các giá trị không phải số (như "Bậc 1")
                        if not item.text().startswith("Bậc"):
                            amount = int(item.text().replace(',', ''))
                            total_deduction += amount
                    except:
                        continue
            
            # Cập nhật tổng khấu trừ vào row 7
            bhxh_amount = self.get_deduction_amount(0)
            thue_tncn_amount = self.get_deduction_amount(1)
            tam_ung_amount = self.get_deduction_amount(5)
            vi_pham_amount = self.get_deduction_amount(6)
            
            total_deduction_item = QTableWidgetItem(f"{total_deduction:,}")
            total_deduction_item.setToolTip(f"🔍 TỔNG KHẤU TRỪ\n💰 Tổng số tiền bị khấu trừ: {total_deduction:,} VNĐ\n\n📊 Bao gồm các khoản:\n• BHXH: {bhxh_amount:,} VNĐ\n• Thuế TNCN: {thue_tncn_amount:,} VNĐ\n• Tạm ứng: {tam_ung_amount:,} VNĐ\n• Vi phạm: {vi_pham_amount:,} VNĐ\n\n🧮 Tổng cộng:\n{bhxh_amount:,} + {thue_tncn_amount:,} + {tam_ung_amount:,} + {vi_pham_amount:,} = {total_deduction:,} VNĐ\n\n💡 Số tiền này sẽ được trừ vào lương thực nhận")
            self.tableKhauTru.setItem(7, 1, total_deduction_item)
            
            # Cập nhật thực nhận = I - E + F
            self.update_final_salary()
            
            # print(f"=== DEBUG: TỔNG KHẤU TRỪ (E) ===")
            # print(f"BHXH (10.5%): {self.get_deduction_amount(0):,}")
            # print(f"Thuế TNCN: {self.get_deduction_amount(1):,}")
            # print(f"Tạm ứng: {self.get_deduction_amount(5):,}")
            # print(f"Vi phạm: {self.get_deduction_amount(6):,}")
            # print(f"Tổng khấu trừ (E): {total_deduction:,}")
            
        except Exception as e:
            print(f"Lỗi cập nhật tổng khấu trừ: {e}")
    
    def update_final_salary(self):
        """Cập nhật thực nhận = I - E + F"""
        try:
            # Lấy tổng cộng (I)
            total_income = 0
            if hasattr(self, 'tong_cong_label') and self.tong_cong_label.text():
                try:
                    total_income = float(self.tong_cong_label.text().replace(',', ''))
                except:
                    total_income = 0
            
            # Lấy tổng khấu trừ (E)
            total_deduction = 0
            if hasattr(self, 'tableKhauTru'):
                deduction_item = self.tableKhauTru.item(7, 1)
                if deduction_item and deduction_item.text():
                    try:
                        total_deduction = float(deduction_item.text().replace(',', ''))
                    except:
                        total_deduction = 0
            
            # Lấy mua sắm (F)
            mua_sam_amount = 0
            if hasattr(self, 'tableMuaSam'):
                # Giả sử mua sắm ở row 0, col 1
                mua_sam_item = self.tableMuaSam.item(0, 1)
                if mua_sam_item and mua_sam_item.text():
                    try:
                        mua_sam_amount = float(mua_sam_item.text().replace(',', ''))
                    except:
                        mua_sam_amount = 0
            
            # Tính thực nhận = I - E + F
            final_salary = total_income - total_deduction + mua_sam_amount
            
            # Cập nhật hiển thị
            if hasattr(self, 'thuc_nhan_label'):
                self.thuc_nhan_label.setText(f"{final_salary:,.0f}")
            
            # Chỉ in một lần khi cập nhật thực nhận
            if not hasattr(self, '_last_final_salary') or self._last_final_salary != final_salary:
                print(f"=== THỰC NHẬN CUỐI CÙNG ===")
                print(f"Tổng cộng (I): {total_income:,}")
                print(f"Tổng khấu trừ (E): {total_deduction:,}")
                print(f"Mua sắm (F): {mua_sam_amount:,}")
                print(f"Thực nhận = I - E + F: {total_income:,} - {total_deduction:,} + {mua_sam_amount:,} = {final_salary:,}")
                self._last_final_salary = final_salary
            
        except Exception as e:
            print(f"Lỗi cập nhật thực nhận: {e}")

    def in_phieu_luong(self):
        """Chụp ảnh phiếu lương, hiển thị preview, cho phép lưu PNG hoặc copy clipboard"""
        try:
            print("=== BẮT ĐẦU IN PHIẾU LƯƠNG ===")
            # Gửi dữ liệu lương thực tế sang tab tổng lương
            self.send_salary_data_to_tong_luong()
            
            # Tìm widget phiếu lương (QGroupBox) trong content layout
            phieu_luong_widget = None
            for child in self.findChildren(QGroupBox):
                if child.title() == "":  # GroupBox không có tiêu đề là phiếu lương chính
                    phieu_luong_widget = child
                    break
            print(f"Debug: Tìm thấy {len(self.findChildren(QGroupBox))} GroupBox")
            if phieu_luong_widget is None:
                print("Debug: Không tìm thấy GroupBox phiếu lương")
                QMessageBox.warning(self, "Lỗi", "Không tìm thấy phiếu lương để in!")
                return
            print("Debug: Đã tìm thấy GroupBox phiếu lương")

            # Render widget thành QPixmap
            pixmap = phieu_luong_widget.grab()

            # Scale nhỏ lại để preview (70% kích thước gốc)
            scaled_pixmap = pixmap.scaled(
                int(pixmap.width() * 0.5), 
                int(pixmap.height() * 0.5), 
                Qt.KeepAspectRatio, 
                Qt.SmoothTransformation
            )

            # Hiển thị preview popup
            preview_dialog = QDialog(self)
            preview_dialog.setWindowTitle("Xem trước phiếu lương")
            preview_dialog.setModal(True)
            preview_dialog.resize(scaled_pixmap.width()+40, scaled_pixmap.height()+100)

            vbox = QVBoxLayout(preview_dialog)
            vbox.setContentsMargins(10, 10, 10, 10)
            vbox.setSpacing(10)

            # Hiển thị ảnh preview (đã scale nhỏ)
            img_label = QLabel()
            img_label.setPixmap(scaled_pixmap)
            img_label.setAlignment(Qt.AlignCenter)
            vbox.addWidget(img_label)

            # Nút chức năng
            hbox = QHBoxLayout()
            btn_save = QPushButton("Lưu PNG")
            btn_copy = QPushButton("Copy hình ảnh")
            btn_cancel = QPushButton("Đóng")
            hbox.addStretch()
            hbox.addWidget(btn_save)
            hbox.addWidget(btn_copy)
            hbox.addWidget(btn_cancel)
            vbox.addLayout(hbox)

            # Xử lý lưu file
            def save_image():
                from PyQt5.QtWidgets import QFileDialog
                file_path, _ = QFileDialog.getSaveFileName(preview_dialog, "Lưu phiếu lương", "phieu_luong.png", "PNG Files (*.png)")
                if file_path:
                    pixmap.save(file_path, "PNG")
                    QMessageBox.information(preview_dialog, "Thành công", f"Đã lưu phiếu lương: {file_path}")

            # Xử lý copy clipboard
            def copy_image():
                clipboard = QApplication.clipboard()
                clipboard.setPixmap(pixmap)
                QMessageBox.information(preview_dialog, "Đã copy", "Hình ảnh đã được copy vào clipboard!")

            btn_save.clicked.connect(save_image)
            btn_copy.clicked.connect(copy_image)
            btn_cancel.clicked.connect(preview_dialog.close)

            preview_dialog.exec_()
        except Exception as e:
            QMessageBox.warning(self, "Lỗi", f"Không thể in phiếu lương: {e}")

    def xuat_excel(self):
        # Gửi dữ liệu lương thực tế sang tab tổng lương
        self.send_salary_data_to_tong_luong()
        QMessageBox.information(self, "Thông báo", "Chức năng xuất Excel đang được phát triển")

    def gui_sang_tong_luong(self):
        """Gửi dữ liệu lương hiện tại sang tab tổng lương"""
        try:
            if not self.current_employee:
                QMessageBox.warning(self, "Cảnh báo", "Vui lòng chọn nhân viên trước!")
                return
            
            # Gửi dữ liệu lương thực tế sang tab tổng lương
            self.send_salary_data_to_tong_luong()
            
            QMessageBox.information(self, "Thành công", 
                                  f"Đã gửi dữ liệu lương của {self.current_employee} sang tab Tổng lương!\n"
                                  "Vui lòng chuyển sang tab Tổng lương để xem biểu đồ.")
            
        except Exception as e:
            QMessageBox.warning(self, "Lỗi", f"Không thể gửi dữ liệu sang tab tổng lương: {e}")

    def load_phieu_luong(self):
        # Hàm này sẽ load dữ liệu phiếu lương khi chọn nhân viên hoặc tháng khác
        # Sau này sẽ lấy dữ liệu từ CSDL
        pass 

    def populate_employee_combo(self):
        """Populate dropdown nhân viên từ dữ liệu quản lý con người"""
        try:
            # Thêm item mặc định "---" vào đầu
            self.comboNhanVien.addItem("---")
            
            # print(f"Debug: ds_nhanvien = {self.ds_nhanvien}")
            
            # Hiển thị tất cả nhân viên từ quản lý con người
            if self.ds_nhanvien:
                for nv in self.ds_nhanvien:
                    # Xử lý cả 2 format: list và dict
                    if isinstance(nv, list) and len(nv) > 0:
                        # Format: list of lists [ho_ten, cccd, msnv, ...]
                        ho_ten = nv[0] if nv[0] else ""
                    elif isinstance(nv, dict) and 'ho_ten' in nv:
                        # Format: list of dicts {'ho_ten': '...', ...}
                        ho_ten = nv['ho_ten']
                    else:
                        continue
                    
                    if ho_ten and ho_ten.strip():
                        # print(f"Debug: Thêm nhân viên {ho_ten}")
                        self.comboNhanVien.addItem(ho_ten)
            else:
                # print("Debug: ds_nhanvien rỗng hoặc None")
                # Fallback: thêm một số nhân viên mẫu
                sample_employees = ["Nguyễn Văn An", "Trần Thị Bình", "Lê Văn Cường"]
                for emp in sample_employees:
                    self.comboNhanVien.addItem(emp)
            
            # TÍNH TOÁN SẴN LƯƠNG CHO TẤT CẢ NHÂN VIÊN (chỉ khi có dữ liệu chấm công)
            # ĐÃ TẮT TÍNH NĂNG NÀY VÌ KHÔNG CẦN THIẾT VÀ CÓ THỂ GÂY SAI SỐ
            # if self.data_chamcong:
            #     print("🚀 BẮT ĐẦU TÍNH TOÁN SẴN LƯƠNG CHO TẤT CẢ NHÂN VIÊN...")
            #     self.calculate_all_employees_salary()
                    
        except Exception as e:
            print(f"Lỗi populate employee combo: {e}")
            # Fallback: thêm một số nhân viên mẫu
            sample_employees = ["Nguyễn Văn An", "Trần Thị Bình", "Lê Văn Cường"]
            for emp in sample_employees:
                self.comboNhanVien.addItem(emp)
    
    def calculate_all_employees_salary(self):
        """Tính toán sẵn lương cho tất cả nhân viên và lưu vào chamcong_data"""
        try:
            if not self.data_chamcong:
                return
            
            # Lấy tháng/năm hiện tại (mặc định tháng 8/2025)
            current_month = "08/2025"
            
            # Tính toán cho từng nhân viên
            for employee_name in self.data_chamcong.keys():
                # Lưu nhân viên hiện tại để tính toán
                original_employee = self.current_employee
                self.current_employee = employee_name
                
                # Tính toán lương cho nhân viên này
                self.calculate_and_save_salary_data(employee_name, current_month)
                
                # Khôi phục nhân viên gốc
                self.current_employee = original_employee
            
        except Exception as e:
            pass

    def calculate_and_save_salary_data(self, employee_name, month_year):
        """Tính toán và lưu dữ liệu lương cho một nhân viên"""
        # Khởi tạo biến trước
        days_detail = {}
        
        try:
            # Lấy dữ liệu lương
            luong_data = self.get_luong_data()
            if not luong_data:
                return
            
            # Lấy dữ liệu chấm công
            chamcong_data = self.get_chamcong_data(month_year)
            if not chamcong_data:
                return
            
            # Tính toán các thành phần lương
            # Lương cơ bản - luong_data là list, index 3 là lương cơ bản
            luong_co_ban_thang = 0
            if isinstance(luong_data, list) and len(luong_data) > 3:
                try:
                    luong_co_ban_thang = int(luong_data[3]) if luong_data[3] else 0
                except (ValueError, TypeError):
                    luong_co_ban_thang = 0
            elif isinstance(luong_data, dict):
                luong_co_ban_thang = luong_data.get('luong_co_ban', 0)
            
            # Lấy dữ liệu chi tiết ngày làm việc
            days_detail = chamcong_data.get('days_detail', {})
            # print(f"Debug: days_detail = {days_detail}")
            
            # Tính lương cơ bản theo số ngày thực tế
            ngay_lam_viec_thuc_te = len(days_detail) if days_detail else 0
            ngay_lam_viec_chuan = 26  # Số ngày làm việc chuẩn trong tháng
            luong_co_ban = (luong_co_ban_thang / ngay_lam_viec_chuan) * ngay_lam_viec_thuc_te
            
            # Phụ cấp (tính từ dữ liệu chấm công)
            tong_phu_cap = 0
            for day_key, day_data in days_detail.items():
                if isinstance(day_data, dict):
                    phone_expense = day_data.get('phone_expense', 0)
                    hotel_expense = day_data.get('hotel_expense', 0)
                    tong_phu_cap += phone_expense + hotel_expense
            
            # Thêm giờ (tính từ dữ liệu chấm công)
            tong_them_gio = 0
            for day_key, day_data in days_detail.items():
                if isinstance(day_data, dict):
                    overtime_hours = day_data.get('overtime_hours', 0)
                    if overtime_hours > 0:
                        luong_1_ngay = luong_co_ban_thang / ngay_lam_viec_chuan
                        luong_1_gio = luong_1_ngay / 8
                        tong_them_gio += overtime_hours * luong_1_gio * 1.5
            
            # KPI (tính từ dữ liệu chấm công)
            tong_kpi = 0
            for day_key, day_data in days_detail.items():
                if isinstance(day_data, dict):
                    paut_meters = day_data.get('paut_meters', 0)
                    tofd_meters = day_data.get('tofd_meters', 0)
                    if paut_meters > 0:
                        tong_kpi += paut_meters * 50000  # Đơn giá PAUT
                    if tofd_meters > 0:
                        tong_kpi += tofd_meters * 60000  # Đơn giá TOFD
            
            # Tổng thu nhập
            tong_thu_nhap = luong_co_ban + tong_phu_cap + tong_them_gio + tong_kpi
            
            # Bảo hiểm (10.5%)
            bao_hiem = 5307200 * 0.105
            
            # Thuế TNCN
            so_nguoi_phu_thuoc = 0  # Lấy từ thông tin nhân viên
            giam_tru_ban_than = 11000000
            giam_tru_phu_thuoc = 4400000 * so_nguoi_phu_thuoc
            thu_nhap_chiu_thue = max(0, tong_thu_nhap - bao_hiem - giam_tru_ban_than - giam_tru_phu_thuoc)
            thue_tncn = self.tinh_thue_tncn(thu_nhap_chiu_thue)
            
            # Tạm ứng và vi phạm
            tam_ung = 0
            vi_pham = 0
            
            # Tổng khấu trừ
            tong_khau_tru = bao_hiem + thue_tncn + tam_ung + vi_pham
            
            # Thực nhận
            thuc_nhan = tong_thu_nhap - tong_khau_tru
            
            # Lưu kết quả vào chamcong_data
            if employee_name in self.data_chamcong and month_year in self.data_chamcong[employee_name]:
                self.data_chamcong[employee_name][month_year].update({
                    'luong_co_ban_thang': luong_co_ban_thang,  # Lương cơ bản tháng đầy đủ
                    'luong_co_ban': luong_co_ban,  # Lương cơ bản theo số ngày thực tế
                    'ngay_lam_viec_thuc_te': ngay_lam_viec_thuc_te,
                    'tong_phu_cap': tong_phu_cap,
                    'tong_them_gio': tong_them_gio,
                    'tong_kpi': tong_kpi,
                    'tong_thu_nhap': tong_thu_nhap,
                    'bao_hiem': bao_hiem,
                    'thue_tncn': thue_tncn,
                    'tam_ung': tam_ung,
                    'vi_pham': vi_pham,
                    'tong_khau_tru': tong_khau_tru,
                    'thuc_nhan': thuc_nhan
                })
            
        except Exception as e:
            pass

    def tinh_thue_tncn(self, thu_nhap_chiu_thue):
        """Tính thuế TNCN theo biểu thuế lũy tiến từng phần"""
        # Biểu thuế lũy tiến từng phần (VNĐ)
        bac = [5000000, 10000000, 18000000, 32000000, 52000000, 80000000]
        ty_le = [0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.35]
        thue = 0
        thu_nhap = thu_nhap_chiu_thue
        
        for i, m in enumerate(bac):
            if thu_nhap > m:
                thue += (m if i == 0 else m-bac[i-1]) * ty_le[i]
            else:
                thue += (thu_nhap if i == 0 else thu_nhap-bac[i-1]) * ty_le[i]
                return max(0, thue)
        
        thue += (thu_nhap-bac[-1]) * ty_le[-1]
        return max(0, thue)

    def update_chamcong_data(self, data_chamcong):
        """Cập nhật dữ liệu chấm công từ tab bảng công"""
        self.data_chamcong = data_chamcong
        
        # TỰ ĐỘNG TÍNH TOÁN SẴN LƯƠNG CHO TẤT CẢ NHÂN VIÊN
        self.calculate_all_employees_salary()
        
        # Refresh month/year combo với dữ liệu mới
        self.populate_month_combo()
        self.populate_year_combo()
        
        # Tự động điền dữ liệu nếu đang chọn nhân viên
        if self.current_employee:
            self.auto_fill_salary_data()
    
    def refresh_data(self):
        """Tự động cập nhật dữ liệu khi có thay đổi"""
        try:
            print("Đang cập nhật dữ liệu phiếu lương...")
            
            # Reload dữ liệu từ data manager
            self.ds_nhanvien = self.data_manager.load_nhanvien()
            self.ds_luong = self.data_manager.load_quydinh_luong()
            
            # Refresh employee combo
            self.comboNhanVien.clear()
            self.populate_employee_combo()
            
            # Refresh month/year combo
            self.populate_month_combo()
            self.populate_year_combo()
            
            # Nếu đang chọn nhân viên, tự động điền lại dữ liệu
            if self.current_employee:
                self.auto_fill_salary_data()
            
            print("Đã cập nhật xong dữ liệu phiếu lương")
            
        except Exception as e:
            print(f"Lỗi cập nhật dữ liệu phiếu lương: {e}") 

    def show_holiday_manager(self):
        """Hiển thị dialog quản lý ngày lễ tết"""
        month, year = self.get_selected_month_year()
        holiday_dialog = HolidayInputDialog(year, month, self)
        
        # Khôi phục ngày lễ đã lưu (nếu có)
        if hasattr(self, 'holiday_dates'):
            holiday_dialog.holiday_dates = self.holiday_dates.copy()
            holiday_dialog.update_holiday_list()
        
        if holiday_dialog.exec_() == QDialog.Accepted:
            self.holiday_dates = holiday_dialog.get_holiday_dates()
            # Tự động cập nhật dữ liệu thêm giờ khi thay đổi ngày lễ
            self.update_overtime_data()
    
    def update_overtime_data(self):
        """Cập nhật dữ liệu thêm giờ dựa trên dữ liệu thực tế từ chấm công"""
        try:
            # Lấy dữ liệu chấm công hiện tại
            month, year = self.get_selected_month_year()
            month_year = f"{month:02d}/{year}"
            chamcong_data = self.get_chamcong_data(month_year)
            
            if not chamcong_data or 'days_detail' not in chamcong_data:
                print("Debug: Không có dữ liệu chi tiết chấm công")
                return
            
            # Lấy dữ liệu lương cơ bản
            luong_data = self.get_luong_data()
            if not luong_data:
                # print("Debug: Không có dữ liệu lương")
                return
            
            # Lấy lương cơ bản từ dữ liệu lương
            luong_co_ban = 0
            if isinstance(luong_data, list) and len(luong_data) > 3:
                try:
                    luong_co_ban = float(str(luong_data[3]).replace(',', ''))
                except:
                    luong_co_ban = 0
            elif isinstance(luong_data, dict):
                luong_co_ban = float(str(luong_data.get('luong_co_ban', 0)).replace(',', ''))
            
            print(f"Debug: Lương cơ bản = {luong_co_ban:,}")
            
            # Tính số ngày làm việc trong tháng
            working_days = self.calculate_working_days(year, month)
            print(f"Debug: Số ngày làm việc = {working_days}")
            
            # Tính lương cơ bản 1 ngày
            luong_1_ngay = luong_co_ban / working_days if working_days > 0 else 0
            print(f"Debug: Lương 1 ngày = {luong_1_ngay:,}")
            
            # Tính lương cơ bản 1 giờ (chia cho 8 tiếng)
            luong_1_gio = luong_1_ngay / 8
            print(f"Debug: Lương 1 giờ = {luong_1_gio:,}")
            
            # Tính toán thêm giờ theo loại
            ot_150_hours = 0
            ot_200_hours = 0
            ot_300_hours = 0
            
            days_detail = chamcong_data.get('days_detail', {})
            for day_key, day_data in days_detail.items():
                # Lấy ngày từ day_key (day_01, day_02, ...)
                day_num = int(day_key.split('_')[1])
                current_date = date(year, month, day_num)
                
                # Lấy loại ngày và số giờ thêm giờ thực tế
                day_type = day_data.get('type', '')
                overtime_hours = day_data.get('overtime_hours', 0)
                
                # Kiểm tra có phải chủ nhật hoặc ngày lễ không
                is_sunday = self.is_sunday(current_date)
                is_holiday = hasattr(self, 'holiday_dates') and current_date in self.holiday_dates
                
                if is_holiday:
                    # Ngày lễ tết: 8 tiếng × 300% (cố định)
                    ot_300_hours += 8
                elif is_sunday:
                    # Chủ nhật: 8 tiếng × 200% (cố định)
                    ot_200_hours += 8
                elif day_type == 'W' and overtime_hours > 0:
                    # Ngày thường có tăng ca: Số giờ thực tế × 150%
                    ot_150_hours += overtime_hours
            
            print(f"Debug: Tính toán thêm giờ - OT150: {ot_150_hours}, OT200: {ot_200_hours}, OT300: {ot_300_hours}")
            
            # Tính thành tiền theo từng hệ số
            thanh_tien_150 = luong_1_gio * 1.5 * ot_150_hours
            thanh_tien_200 = luong_1_gio * 2.0 * ot_200_hours
            thanh_tien_300 = luong_1_gio * 3.0 * ot_300_hours
            
            print(f"Debug: Thành tiền - 150%: {thanh_tien_150:,}, 200%: {thanh_tien_200:,}, 300%: {thanh_tien_300:,}")
            
            # Cập nhật bảng thêm giờ
            if hasattr(self, 'tableThemGio'):
                # Cập nhật số giờ
                self.tableThemGio.setItem(0, 1, QTableWidgetItem(f"{ot_150_hours:.2f}"))
                self.tableThemGio.setItem(1, 1, QTableWidgetItem(f"{ot_200_hours:.2f}"))
                self.tableThemGio.setItem(2, 1, QTableWidgetItem(f"{ot_300_hours:.2f}"))
                
                # Cập nhật thành tiền với tooltip
                thanh_tien_150_item = QTableWidgetItem(f"{thanh_tien_150:,.0f}")
                thanh_tien_150_item.setToolTip("🔍 CÔNG THỨC\nThêm giờ 150% = Số giờ × Lương 1 giờ × 1.5")
                self.tableThemGio.setItem(0, 2, thanh_tien_150_item)
                
                thanh_tien_200_item = QTableWidgetItem(f"{thanh_tien_200:,.0f}")
                thanh_tien_200_item.setToolTip("🔍 CÔNG THỨC\nThêm giờ 200% = Số giờ × Lương 1 giờ × 2.0")
                self.tableThemGio.setItem(1, 2, thanh_tien_200_item)
                
                thanh_tien_300_item = QTableWidgetItem(f"{thanh_tien_300:,.0f}")
                thanh_tien_300_item.setToolTip("🔍 CÔNG THỨC\nThêm giờ 300% = Số giờ × Lương 1 giờ × 3.0")
                self.tableThemGio.setItem(2, 2, thanh_tien_300_item)
                
                # Tính tổng thu nhập thêm giờ
                total_overtime = ot_150_hours + ot_200_hours + ot_300_hours
                total_overtime_amount = thanh_tien_150 + thanh_tien_200 + thanh_tien_300
                self.tableThemGio.setItem(3, 1, QTableWidgetItem(f"{total_overtime:.2f}"))
            total_overtime_item = QTableWidgetItem(f"{total_overtime_amount:,.0f}")
            total_overtime_item.setToolTip("🔍 CÔNG THỨC\nTổng thêm giờ = Thành tiền 150% + Thành tiền 200% + Thành tiền 300%")
            self.tableThemGio.setItem(3, 2, total_overtime_item)
                
        except Exception as e:
            print(f"Lỗi cập nhật dữ liệu thêm giờ: {e}")
            import traceback
            traceback.print_exc()
    
    def is_sunday(self, check_date):
        """Kiểm tra có phải chủ nhật không"""
        return check_date.weekday() == 6  # 6 = Sunday 

    def update_totals(self):
        """Tính toán và cập nhật tổng cộng và thực nhận"""
        try:
            # print("=== BẮT ĐẦU update_totals ===")
            def parse_amount_cell(item):
                try:
                    if not item:
                        return 0.0
                    text = item.text() if hasattr(item, 'text') else str(item)
                    if not text:
                        return 0.0
                    # Chuẩn hóa: bỏ dấu phẩy, khoảng trắng và ký tự khác số
                    import re
                    cleaned = re.sub(r"[^0-9\.-]", "", text.replace(",", ""))
                    return float(cleaned) if cleaned else 0.0
                except Exception as e:
                    print(f"parse_amount_cell error with '{item}': {e}")
                    return 0.0
            total_basic = 0
            total_overtime = 0
            total_allowance = 0
            total_kpi = 0
            
            # Tính lương cơ bản
            if hasattr(self, 'tableLuongCoBan'):
                amount_item = self.tableLuongCoBan.item(0, 2)
                total_basic = parse_amount_cell(amount_item)
            
            # Tính thêm giờ
            if hasattr(self, 'tableThemGio'):
                # Chỉ lấy dòng tổng (row 3) để tránh cộng trùng các dòng 150/200/300%
                total_overtime = parse_amount_cell(self.tableThemGio.item(3, 2))
            
            # Tính phụ cấp
            if hasattr(self, 'tablePhuCap'):
                # Cộng các dòng phụ cấp (0..6), bỏ dòng tổng (7)
                temp_allowance = 0
                for row in range(self.tablePhuCap.rowCount()):
                    if row == 7:  # bỏ dòng tổng
                        continue
                    temp_allowance += parse_amount_cell(self.tablePhuCap.item(row, 2))
                # print(f"Debug: Tổng phụ cấp (sum rows 0..6) = {temp_allowance:,}")
                # Cập nhật tổng phụ cấp vào dòng 7 với tooltip
                tong_phu_cap_item = QTableWidgetItem(f"{temp_allowance:,.0f}")
                tong_phu_cap_item.setToolTip("🔍 CÔNG THỨC\nTổng phụ cấp = PC Công trường + PC Đào tạo + PC Văn phòng + PC Chức danh + Xăng xe + Điện thoại + Khách sạn")
                self.tablePhuCap.setItem(7, 2, tong_phu_cap_item)
                # Lấy từ dòng tổng (đã cập nhật) để tính tổng cộng
                total_allowance = parse_amount_cell(self.tablePhuCap.item(7, 2))
            
            # Tính KPI
            if hasattr(self, 'tableKPI'):
                # Chỉ lấy dòng tổng (row 2)
                total_kpi = parse_amount_cell(self.tableKPI.item(2, 2))
            
            # Tính tổng cộng (I)
            total_gross = total_basic + total_overtime + total_allowance + total_kpi
            # print(f"=== DEBUG: TỔNG CỘNG (I) ===")
            # print(f"A (Lương cơ bản): {total_basic:,}")
            # print(f"B (Thêm giờ): {total_overtime:,}")
            # print(f"C (Phụ cấp): {total_allowance:,}")
            # print(f"D (KPI): {total_kpi:,}")
            # print(f"Tổng cộng (I) = A + B + C + D: {total_basic:,} + {total_overtime:,} + {total_allowance:,} + {total_kpi:,} = {total_gross:,}")
             
            # Cập nhật hiển thị tổng cộng
            if hasattr(self, 'tong_cong_label'):
                self.tong_cong_label.setText(f"{total_gross:,}")
            
            # Cập nhật tính toán thuế và khấu trừ
            self.update_bhxh_calculation()
            
            # Cập nhật thực nhận theo công thức mới: I - E + F
            self.update_final_salary()
            
            # print("=== KẾT THÚC update_totals ===")
        except Exception as e:
            print(f"Lỗi tính tổng: {e}")
            import traceback
            traceback.print_exc()

    def update_bhxh_calculation(self):
        """Cập nhật tính toán BHXH dựa trên tỷ lệ trong quy định lương và mức lương cơ sở"""
        try:
            if not hasattr(self, 'tableKhauTru') or not self.current_employee:
                return
                
            # Lấy tỷ lệ BHXH từ quy định lương
            luong_data = self.get_luong_data()
            bhxh_rate = 0
            
            if luong_data and isinstance(luong_data, list) and len(luong_data) > 11:
                # Cột BHXH ở index 11 (sau khi bỏ cột PC-UT)
                bhxh_value = luong_data[11] if luong_data[11] else ""
                if isinstance(bhxh_value, str) and '%' in bhxh_value:
                    # Lấy số từ chuỗi "10.5%" 
                    try:
                        bhxh_rate = float(bhxh_value.replace('%', '').strip())
                    except ValueError:
                        bhxh_rate = 10.5  # Mặc định 10.5%
                elif isinstance(bhxh_value, (int, float)):
                    bhxh_rate = float(bhxh_value)
                else:
                    bhxh_rate = 10.5  # Mặc định 10.5%
            else:
                bhxh_rate = 10.5  # Mặc định 10.5%
            
            # Tính thành tiền BHXH
            bhxh_amount = self.bhxh_salary_base * (bhxh_rate / 100)
            
            # Cập nhật vào bảng khấu trừ
            # Hàng 0: Hệ số bảo hiểm
            bhxh_rate_item = QTableWidgetItem(f"{bhxh_rate:.1f}%")
            bhxh_rate_item.setToolTip(f"🔍 TỶ LỆ BHXH\nTỷ lệ hiện tại: {bhxh_rate:.1f}%\n\n📋 Cách xác định:\n• Lấy từ tab 'Quy định lương'\n• Cột 'BHXH' của nhân viên này\n• Nếu không có dữ liệu → mặc định 10.5%\n\n💡 Lưu ý: Tỷ lệ này do công ty quy định")
            self.tableKhauTru.setItem(0, 0, bhxh_rate_item)
            
            bhxh_amount_item = QTableWidgetItem(f"{bhxh_amount:,.0f}")
            bhxh_amount_item.setToolTip(f"🔍 CÁCH TÍNH BHXH\n💰 Số tiền BHXH: {bhxh_amount:,.0f} VNĐ\n\n📊 Công thức:\nLương cơ sở × Tỷ lệ BHXH\n\n🧮 Tính toán:\n{self.bhxh_salary_base:,} VNĐ × {bhxh_rate:.1f}% = {bhxh_amount:,.0f} VNĐ\n\n📋 Lương cơ sở BHXH: {self.bhxh_salary_base:,} VNĐ")
            self.tableKhauTru.setItem(0, 1, bhxh_amount_item)
            
            # print(f"Debug BHXH: Tỷ lệ {bhxh_rate}% × Lương cơ sở {self.bhxh_salary_base:,} = {bhxh_amount:,.0f}")
            
            # Cập nhật thuế và các khoản khấu trừ khác
            self.update_tax_calculation()
            
            # Cập nhật tổng khấu trừ
            self.update_total_deduction()
            
        except Exception as e:
            print(f"Lỗi cập nhật tính toán BHXH: {e}")
            import traceback
            traceback.print_exc()

    def update_tax_calculation(self):
        """Cập nhật tính toán thuế TNCN và các khoản khấu trừ khác (theo luật Việt Nam)"""
        try:
            if not hasattr(self, 'tableKhauTru'):
                return
            
            # Lấy tổng thu nhập (I) để tính thuế
            total_income = 0
            if hasattr(self, 'tong_cong_label') and self.tong_cong_label.text():
                try:
                    total_income = float(self.tong_cong_label.text().replace(',', ''))
                except:
                    total_income = 0
            
            # Tính giảm trừ gia cảnh theo luật Việt Nam
            # Theo Nghị định 65/2013/NĐ-CP và Thông tư 111/2013/TT-BTC
            so_nguoi_phu_thuoc = self.get_so_nguoi_phu_thuoc()
            giam_tru_ban_than = 11000000  # Giảm trừ bản thân
            giam_tru_nguoi_phu_thuoc = so_nguoi_phu_thuoc * 4400000  # 4.4 triệu/người phụ thuộc
            giam_tru_gia_canh = giam_tru_ban_than + giam_tru_nguoi_phu_thuoc
            
            # Cập nhật giảm trừ gia cảnh với tooltip
            giam_tru_item = QTableWidgetItem(f"{giam_tru_gia_canh:,}")
            giam_tru_item.setToolTip(f"🔍 GIẢM TRỪ GIA CẢNH\n💰 Tổng giảm trừ: {giam_tru_gia_canh:,} VNĐ\n\n📊 Cách tính:\n• Giảm trừ bản thân: 11,000,000 VNĐ\n• Giảm trừ người phụ thuộc: {so_nguoi_phu_thuoc} người × 4,400,000 VNĐ\n\n🧮 Chi tiết:\n• Bản thân: 11,000,000 VNĐ\n• Người phụ thuộc: {giam_tru_nguoi_phu_thuoc:,} VNĐ\n• Tổng cộng: {giam_tru_gia_canh:,} VNĐ\n\n📋 Số người phụ thuộc ({so_nguoi_phu_thuoc}) được lấy từ tab 'Quản lý nhân viên'\n💡 Tối đa 9 người theo quy định pháp luật")
            self.tableKhauTru.setItem(3, 1, giam_tru_item)
            
            # Thu nhập chịu thuế = Tổng thu nhập - Bảo hiểm bắt buộc (10.5%) - Giảm trừ gia cảnh
            # Hệ số bảo hiểm chung: 10.5% lương cơ sở
            
            bhxh_amount = 0
            bhxh_item = self.tableKhauTru.item(0, 1)
            if bhxh_item and bhxh_item.text():
                try:
                    bhxh_amount = float(bhxh_item.text().replace(',', ''))
                except:
                    bhxh_amount = 0
            
            thu_nhap_chiu_thue = max(0, total_income - bhxh_amount - giam_tru_gia_canh)
            thu_nhap_item = QTableWidgetItem(f"{thu_nhap_chiu_thue:,.0f}")
            thu_nhap_item.setToolTip(f"🔍 THU NHẬP CHỊU THUẾ\n💰 Thu nhập chịu thuế: {thu_nhap_chiu_thue:,} VNĐ\n\n📊 Cách tính:\nTổng thu nhập - BHXH - Giảm trừ gia cảnh\n\n🧮 Chi tiết:\n• Tổng thu nhập: {total_income:,} VNĐ\n• Trừ BHXH: -{bhxh_amount:,} VNĐ\n• Trừ giảm trừ gia cảnh: -{giam_tru_gia_canh:,} VNĐ\n• Còn lại: {thu_nhap_chiu_thue:,} VNĐ\n\n💡 Đây là số tiền dùng để tính thuế TNCN")
            self.tableKhauTru.setItem(2, 1, thu_nhap_item)
            
            # Tính thuế TNCN theo bậc thuế thực tế
            thue_tncn, bac_thue = self.calculate_personal_income_tax_with_bracket(thu_nhap_chiu_thue)
            thue_item = QTableWidgetItem(f"{thue_tncn:,.0f}")
            thue_item.setToolTip(f"🔍 THUẾ THU NHẬP CÁ NHÂN\n💰 Thuế TNCN: {thue_tncn:,} VNĐ\n📊 Bậc thuế: {bac_thue}\n\n🧮 Tính từ thu nhập chịu thuế: {thu_nhap_chiu_thue:,} VNĐ\n\n📋 Bảng thuế lũy tiến từng phần:\n• Bậc 1: ≤ 5 triệu (5%)\n• Bậc 2: 5-10 triệu (10%)\n• Bậc 3: 10-18 triệu (15%)\n• Bậc 4: 18-32 triệu (20%)\n• Bậc 5: 32-52 triệu (25%)\n• Bậc 6: 52-80 triệu (30%)\n• Bậc 7: > 80 triệu (35%)\n\n➜ Thu nhập của bạn thuộc Bậc {bac_thue}")
            self.tableKhauTru.setItem(1, 1, thue_item)
            
            # Hiển thị bậc thuế
            bac_thue_item = QTableWidgetItem(f"Bậc {bac_thue}")
            bac_thue_item.setToolTip(f"🔍 BẬC THUẾ\n📊 Bậc thuế hiện tại: Bậc {bac_thue}\n💰 Thu nhập chịu thuế: {thu_nhap_chiu_thue:,} VNĐ\n\n📋 Bảng phân bậc thuế:\n🟢 Bậc 1: ≤ 5 triệu (thuế suất 5%)\n🟡 Bậc 2: 5-10 triệu (thuế suất 10%)\n🟠 Bậc 3: 10-18 triệu (thuế suất 15%)\n🔴 Bậc 4: 18-32 triệu (thuế suất 20%)\n🟣 Bậc 5: 32-52 triệu (thuế suất 25%)\n🔵 Bậc 6: 52-80 triệu (thuế suất 30%)\n⚫ Bậc 7: > 80 triệu (thuế suất 35%)\n\n➜ Thu nhập của bạn thuộc Bậc {bac_thue}")
            self.tableKhauTru.setItem(4, 1, bac_thue_item)
            
            # print(f"=== DEBUG: THUẾ TNCN ===")
            # print(f"Tổng thu nhập (I): {total_income:,}")
            # print(f"BHXH (10.5%): {bhxh_amount:,}")
            # print(f"Giảm trừ bản thân: {giam_tru_ban_than:,}")
            # print(f"Giảm trừ người phụ thuộc: {so_nguoi_phu_thuoc} người × 4,400,000 = {giam_tru_nguoi_phu_thuoc:,}")
            # print(f"Tổng giảm trừ gia cảnh: {giam_tru_gia_canh:,}")
            # print(f"Thu nhập chịu thuế: {total_income:,} - {bhxh_amount:,} - {giam_tru_gia_canh:,} = {thu_nhap_chiu_thue:,}")
            # print(f"Thuế TNCN (Bậc {bac_thue}): {thue_tncn:,}")
            
        except Exception as e:
            print(f"Lỗi cập nhật tính toán thuế: {e}")
            import traceback
            traceback.print_exc()

    def get_so_nguoi_phu_thuoc(self):
        """Lấy số người phụ thuộc từ dữ liệu nhân viên (theo luật Việt Nam)"""
        try:
            if not self.current_employee or not self.ds_nhanvien:
                return 0
            
            # Tìm nhân viên trong danh sách
            for nv in self.ds_nhanvien:
                if isinstance(nv, list) and len(nv) > 0:
                    ho_ten = nv[0] if nv[0] else ""
                    if ho_ten == self.current_employee:
                        # Số người phụ thuộc thường ở cột 10 (index 10)
                        if len(nv) > 10:
                            try:
                                so_nguoi = int(str(nv[10]).strip()) if nv[10] else 0
                                # Giới hạn theo luật: tối đa 9 người phụ thuộc
                                return min(max(0, so_nguoi), 9)
                            except:
                                return 0
                        break
            return 0
        except Exception as e:
            print(f"Lỗi lấy số người phụ thuộc: {e}")
            return 0
    
    def validate_nguoi_phu_thuoc(self, so_nguoi):
        """Kiểm tra điều kiện người phụ thuộc theo luật Việt Nam"""
        # Theo Nghị định 65/2013/NĐ-CP
        # Người phụ thuộc phải đáp ứng các điều kiện:
        # 1. Con dưới 18 tuổi hoặc từ 18-22 tuổi đang học
        # 2. Con từ 22 tuổi trở lên bị khuyết tật
        # 3. Vợ/chồng không có thu nhập hoặc thu nhập < 1 triệu/tháng
        # 4. Cha mẹ không có thu nhập hoặc thu nhập < 1 triệu/tháng
        # 5. Các đối tượng khác theo quy định
        
        # Hiện tại chỉ kiểm tra số lượng, cần bổ sung validation chi tiết
        return 0 <= so_nguoi <= 9

    def calculate_personal_income_tax_with_bracket(self, taxable_income):
        """Tính thuế thu nhập cá nhân theo bậc thuế và trả về cả bậc thuế"""
        if taxable_income <= 5000000:
            return taxable_income * 0.05, 1
        elif taxable_income <= 10000000:
            return 5000000 * 0.05 + (taxable_income - 5000000) * 0.10, 2
        elif taxable_income <= 18000000:
            return 5000000 * 0.05 + 5000000 * 0.10 + (taxable_income - 10000000) * 0.15, 3
        elif taxable_income <= 32000000:
            return 5000000 * 0.05 + 5000000 * 0.10 + 8000000 * 0.15 + (taxable_income - 18000000) * 0.20, 4
        elif taxable_income <= 52000000:
            return 5000000 * 0.05 + 5000000 * 0.10 + 8000000 * 0.15 + 14000000 * 0.20 + (taxable_income - 32000000) * 0.25, 5
        elif taxable_income <= 80000000:
            return 5000000 * 0.05 + 5000000 * 0.10 + 8000000 * 0.15 + 14000000 * 0.20 + 20000000 * 0.25 + (taxable_income - 52000000) * 0.30, 6
        else:
            return 5000000 * 0.05 + 5000000 * 0.10 + 8000000 * 0.15 + 14000000 * 0.20 + 20000000 * 0.25 + 28000000 * 0.30 + (taxable_income - 80000000) * 0.35, 7

    def calculate_personal_income_tax(self, taxable_income):
        """Tính thuế thu nhập cá nhân theo bậc thuế (giữ lại để tương thích)"""
        thue, _ = self.calculate_personal_income_tax_with_bracket(taxable_income)
        return thue

    def refresh_all_data(self):
        """Hard refresh - Tải lại toàn bộ dữ liệu từ file và cập nhật giao diện"""
        try:
            print("=== BẮT ĐẦU HARD REFRESH ===")
            
            # Lưu lại nhân viên và tháng/năm đang chọn
            current_employee = self.comboNhanVien.currentText()
            current_month_text = self.comboThang.currentText()
            current_year = self.comboNam.currentText()
            
            # 1. Reload tất cả dữ liệu từ file
            print("1. Đang tải lại dữ liệu nhân viên...")
            self.ds_nhanvien = self.data_manager.load_nhanvien()
            
            print("2. Đang tải lại quy định lương...")
            self.ds_luong = self.data_manager.load_quydinh_luong()
            
            print("3. Đang tải lại dữ liệu chấm công...")
            # Reload dữ liệu chấm công từ data manager
            # Tìm file JSON mới nhất trong thư mục data
            json_files = glob.glob(os.path.join(self.data_manager.data_dir, "*.json"))
            chamcong_files = [f for f in json_files if "chamcong" in os.path.basename(f).lower()]
            if chamcong_files:
                # Sắp xếp theo thời gian sửa đổi, lấy file mới nhất
                latest_file = max(chamcong_files, key=os.path.getmtime)
                print(f"File chấm công mới nhất: {latest_file}")
                
                # Cập nhật đường dẫn file chấm công trong data manager
                self.data_manager.chamcong_file = latest_file
            
            self.data_chamcong = self.data_manager.load_chamcong()
            print(f"Debug: Đã load {len(self.data_chamcong)} nhân viên từ chấm công")
            
            # 2. Refresh tất cả dropdown
            print("4. Đang cập nhật dropdown nhân viên...")
            self.comboNhanVien.clear()
            self.populate_employee_combo()
            
            print("5. Đang cập nhật dropdown tháng/năm...")
            self.populate_month_combo()
            self.populate_year_combo()
            
            # 3. Khôi phục lại lựa chọn trước đó (nếu có)
            if current_employee and current_employee != "---":
                employee_index = self.comboNhanVien.findText(current_employee)
                if employee_index >= 0:
                    self.comboNhanVien.setCurrentIndex(employee_index)
                    # Gọi trực tiếp on_employee_changed để xử lý đầy đủ
                    self.on_employee_changed()
                    print(f"Đã khôi phục nhân viên: {current_employee}")
            
            if current_month_text:
                month_index = self.comboThang.findText(current_month_text)
                if month_index >= 0:
                     self.comboThang.setCurrentIndex(month_index)
            
            if current_year:
                year_index = self.comboNam.findText(current_year)
                if year_index >= 0:
                     self.comboNam.setCurrentIndex(year_index)
            
            # 4. Dữ liệu đã được tải trong on_employee_changed() ở trên
            print("6. Đã hoàn thành khôi phục dữ liệu")
            
            print("=== HOÀN THÀNH HARD REFRESH ===")
            
            # Hiển thị thông báo thành công
            if self.current_employee:
                QMessageBox.information(self, "Thành công", 
                                      f"Đã cập nhật thành công dữ liệu mới cho {self.current_employee}!")
            else:
                QMessageBox.information(self, "Thành công", 
                                      "Đã cập nhật thành công dữ liệu mới từ bảng công!\n"
                                      "Vui lòng chọn nhân viên để xem dữ liệu cập nhật.")
            
        except Exception as e:
            print(f"Lỗi hard refresh: {e}")
            import traceback
            traceback.print_exc()
            QMessageBox.warning(self, "Lỗi", f"Có lỗi khi cập nhật dữ liệu:\n{str(e)}")

    # Hàm test_simple_tooltip đã được loại bỏ vì không cần thiết

    # Hàm setup_formula_tooltips đã được loại bỏ vì tooltip được thiết lập trực tiếp khi tạo/cập nhật item
    
    # Các hàm add_tooltip_to_table_cell và add_tooltip_to_label đã được loại bỏ vì không cần thiết

    def create_formula_tooltip(self, title, formula):
        """Tạo tooltip với format đẹp và chữ màu đen"""
        return f"""
            <div style="background-color: #ffffff; color: #2c3e50; padding: 10px; border-radius: 6px; font-size: 12px; border: 2px solid #3498db; box-shadow: 0 2px 8px rgba(0,0,0,0.2);">
                <div style="font-weight: bold; color: #3498db; margin-bottom: 8px; font-size: 14px;">🔍 {title}</div>
                <div style="color: #2c3e50;">{formula}</div>
            </div>
        """



    # Hàm setup_tooltips_after_data_loaded đã được loại bỏ vì tooltip được thiết lập trực tiếp

    def send_salary_data_to_tong_luong(self):
        """Gửi dữ liệu lương thực tế sang tab tổng lương"""
        try:
            if not self.current_employee:
                print("Không có nhân viên được chọn để gửi dữ liệu lương")
                return
            
            # Lấy tháng/năm hiện tại
            month = self.comboThang.currentText()
            year = self.comboNam.currentText()
            month_year = f"{month}/{year}"
            
            # Lấy dữ liệu lương từ các bảng
            salary_data = self.get_current_salary_data()
            
            if salary_data:
                # Gửi dữ liệu sang tab tổng lương
                if hasattr(self, 'tong_luong_tab') and self.tong_luong_tab:
                    self.tong_luong_tab.add_salary_data(self.current_employee, salary_data)
                    print(f"✅ Đã gửi dữ liệu lương thực tế cho {self.current_employee} sang tab tổng lương")
                else:
                    print("❌ Không tìm thấy tab tổng lương để gửi dữ liệu")
            else:
                print("❌ Không có dữ liệu lương để gửi")
                
        except Exception as e:
            print(f"❌ Lỗi gửi dữ liệu lương sang tab tổng lương: {e}")
            import traceback
            traceback.print_exc()

    def get_current_salary_data(self):
        """Lấy dữ liệu lương hiện tại từ các bảng"""
        try:
            # Lấy tháng/năm hiện tại
            month = self.comboThang.currentText()
            year = self.comboNam.currentText()
            month_year = f"{month}/{year}"
            
            # Lấy MSNV từ dữ liệu nhân viên
            msnv = ""
            if self.ds_nhanvien:
                for nv in self.ds_nhanvien:
                    if isinstance(nv, list) and len(nv) > 0:
                        if str(nv[0]).strip().upper() == self.current_employee.upper():
                            msnv = str(nv[2]).strip() if len(nv) > 2 and nv[2] else ""
                            break
            
            # Lấy dữ liệu từ bảng lương cơ bản
            luong_co_ban = 0
            if hasattr(self, 'tableLuongCoBan') and self.tableLuongCoBan.item(0, 2):
                luong_co_ban_text = self.tableLuongCoBan.item(0, 2).text()
                luong_co_ban = float(luong_co_ban_text.replace(',', '')) if luong_co_ban_text else 0
            
            # Lấy dữ liệu từ bảng thêm giờ
            tong_them_gio = 0
            if hasattr(self, 'tableThemGio') and self.tableThemGio.item(3, 2):
                them_gio_text = self.tableThemGio.item(3, 2).text()
                tong_them_gio = float(them_gio_text.replace(',', '')) if them_gio_text else 0
            
            # Lấy dữ liệu từ bảng phụ cấp
            tong_phu_cap = 0
            if hasattr(self, 'tablePhuCap') and self.tablePhuCap.item(7, 2):
                phu_cap_text = self.tablePhuCap.item(7, 2).text()
                tong_phu_cap = float(phu_cap_text.replace(',', '')) if phu_cap_text else 0
            
            # Lấy dữ liệu từ bảng KPI
            tong_kpi = 0
            if hasattr(self, 'tableKPI') and self.tableKPI.item(2, 2):
                kpi_text = self.tableKPI.item(2, 2).text()
                tong_kpi = float(kpi_text.replace(',', '')) if kpi_text else 0
            
            # Lấy dữ liệu từ bảng tổng cộng
            tong_thu_nhap = 0
            if hasattr(self, 'tableTongCong') and self.tableTongCong.item(0, 1):
                thu_nhap_text = self.tableTongCong.item(0, 1).text()
                tong_thu_nhap = float(thu_nhap_text.replace(',', '')) if thu_nhap_text else 0
            
            # Lấy dữ liệu từ bảng khấu trừ
            bao_hiem = 0
            thue_tncn = 0
            if hasattr(self, 'tableKhauTru'):
                if self.tableKhauTru.item(0, 1):
                    bao_hiem_text = self.tableKhauTru.item(0, 1).text()
                    bao_hiem = float(bao_hiem_text.replace(',', '')) if bao_hiem_text else 0
                if self.tableKhauTru.item(1, 1):
                    thue_text = self.tableKhauTru.item(1, 1).text()
                    thue_tncn = float(thue_text.replace(',', '')) if thue_text else 0
            
            # Lấy dữ liệu tạm ứng/vi phạm
            tam_ung = 0
            vi_pham = 0
            if hasattr(self, 'tableTamUngViPham'):
                if self.tableTamUngViPham.item(0, 1):
                    tam_ung_text = self.tableTamUngViPham.item(0, 1).text()
                    tam_ung = float(tam_ung_text.replace(',', '')) if tam_ung_text else 0
                if self.tableTamUngViPham.item(1, 1):
                    vi_pham_text = self.tableTamUngViPham.item(1, 1).text()
                    vi_pham = float(vi_pham_text.replace(',', '')) if vi_pham_text else 0
            
            # Lấy dữ liệu thực nhận từ biến đã tính toán
            thuc_nhan = 0
            # Ưu tiên lấy từ biến đã tính toán
            if hasattr(self, '_last_final_salary'):
                thuc_nhan = self._last_final_salary
                print(f"Debug: Thực nhận lấy từ biến _last_final_salary: {thuc_nhan:,.0f}")
            elif hasattr(self, 'thuc_nhan_label') and self.thuc_nhan_label.text():
                thuc_nhan_text = self.thuc_nhan_label.text()
                thuc_nhan = float(thuc_nhan_text.replace(',', '')) if thuc_nhan_text else 0
                print(f"Debug: Thực nhận lấy từ label: {thuc_nhan:,.0f}")
            # Fallback: lấy từ bảng nếu không có label
            elif hasattr(self, 'tableThucNhan') and self.tableThucNhan.item(0, 1):
                thuc_nhan_text = self.tableThucNhan.item(0, 1).text()
                thuc_nhan = float(thuc_nhan_text.replace(',', '')) if thuc_nhan_text else 0
                print(f"Debug: Thực nhận lấy từ bảng: {thuc_nhan:,.0f}")
            else:
                print("Debug: Không tìm thấy nguồn thực nhận!")
            
            # Tạo dictionary dữ liệu lương
            salary_data = {
                'msnv': msnv,
                'luong_co_ban': luong_co_ban,
                'tong_them_gio': tong_them_gio,
                'tong_phu_cap': tong_phu_cap,
                'tong_kpi': tong_kpi,
                'tong_thu_nhap': tong_thu_nhap,
                'bao_hiem': bao_hiem,
                'thue_tncn': thue_tncn,
                'tam_ung': tam_ung,
                'vi_pham': vi_pham,
                'thuc_nhan': thuc_nhan,
                'month_year': month_year
            }
            
            print(f"=== DỮ LIỆU LƯƠNG ĐÃ TẠO ===")
            print(f"Nhân viên: {self.current_employee}")
            print(f"Thực nhận: {thuc_nhan:,.0f} VNĐ")
            print(f"Lương cơ bản: {luong_co_ban:,.0f} VNĐ")
            print(f"Tổng phụ cấp: {tong_phu_cap:,.0f} VNĐ")
            print(f"Tổng thêm giờ: {tong_them_gio:,.0f} VNĐ")
            print(f"Tổng KPI: {tong_kpi:,.0f} VNĐ")
            
            # Debug đã được thêm ở trên
            
            return salary_data
            
        except Exception as e:
            print(f"❌ Lỗi lấy dữ liệu lương hiện tại: {e}")
            import traceback
            traceback.print_exc()
            return None

