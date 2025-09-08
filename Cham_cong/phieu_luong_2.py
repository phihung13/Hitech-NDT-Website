#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Phiếu Lương 2 - Form phiếu lương đầy đủ
Mục tiêu: Tạo phiếu lương hoàn chỉnh với đầy đủ thành phần
"""

import sys
import os
from datetime import datetime
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtPrintSupport import QPrinter, QPrintDialog
from data_manager import DataManager
from employee_mapper import EmployeeMapper

# Import thư viện tạo PDF đẹp
try:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import cm, mm
    from reportlab.lib import colors
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
    from reportlab.pdfgen import canvas
    from reportlab.lib.utils import ImageReader
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False
    print("⚠️ ReportLab không có sẵn. Cài đặt: pip install reportlab")

# Import PIL để xử lý ảnh
try:
    from PIL import Image as PILImage
    from PIL import ImageDraw, ImageFont
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    print("⚠️ PIL không có sẵn. Cài đặt: pip install pillow")


class PhieuLuong2(QWidget):
    """Phiếu lương 2 - Form phiếu lương đầy đủ"""
    
    def __init__(self, bang_cong_tab=None):
        super().__init__()
        self.bang_cong_tab = bang_cong_tab
        self.current_employee_data = None
        self.current_period = None
        self.current_msnv = None
        
        # Khởi tạo data manager và employee mapper
        self.data_manager = DataManager()
        self.employee_mapper = EmployeeMapper()
        
        # Load dữ liệu từ database
        self.load_database_data()
        
        self.init_ui()
    
    def load_database_data(self):
        """Load dữ liệu từ database"""
        try:
            # Load dữ liệu nhân viên
            self.ds_nhanvien = self.data_manager.load_nhanvien()
            self.employee_mapper.load_from_nhanvien_data(self.ds_nhanvien)
            
            # Load quy định lương
            self.ds_luong_nv, self.ds_phu_cap_ct = self.data_manager.load_quydinh_luong()
            
            print(f"✅ Loaded {len(self.ds_nhanvien)} employees and {len(self.ds_luong_nv)} salary records")
            
        except Exception as e:
            print(f"❌ Lỗi load database: {e}")
            self.ds_nhanvien = []
            self.ds_luong_nv = []
            self.ds_phu_cap_ct = []
        
    def init_ui(self):
        """Khởi tạo giao diện form phiếu lương"""
        self.setWindowTitle("PHIẾU LƯƠNG NHÂN VIÊN")
        self.setMinimumSize(900, 800)
        
        # Main layout
        main_layout = QVBoxLayout()
        
        # Header section
        self.create_header_section(main_layout)
        
        # Employee selection section
        self.create_selection_section(main_layout)
        
        # Scroll area for salary form
        scroll = QScrollArea()
        scroll_widget = QWidget()
        self.form_layout = QVBoxLayout(scroll_widget)
        
        # Create salary form sections
        self.create_employee_info_section()
        self.create_salary_calculation_section()
        self.create_allowance_section()
        self.create_overtime_section()
        self.create_kpi_section()
        self.create_deduction_section()
        self.create_summary_section()
        
        scroll.setWidget(scroll_widget)
        scroll.setWidgetResizable(True)
        main_layout.addWidget(scroll)
        
        # Action buttons
        self.create_action_buttons(main_layout)
        
        self.setLayout(main_layout)
        
        # Apply styles
        self.apply_styles()
        
    def create_header_section(self, layout):
        """Tạo phần header"""
        header_frame = QFrame()
        header_frame.setFrameStyle(QFrame.NoFrame)
        header_frame.setStyleSheet("background-color: #f8f9fa;")
        
        header_layout = QVBoxLayout(header_frame)
        
        # Company info
        company_label = QLabel("HITECH NDT CO., LTD.")
        company_label.setAlignment(Qt.AlignCenter)
        company_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #007bff;")
        header_layout.addWidget(company_label)
        
        # Title
        title_label = QLabel("PHIẾU LƯƠNG NHÂN VIÊN")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #dc3545; margin: 10px;")
        header_layout.addWidget(title_label)
        
        # Date
        date_label = QLabel(f"Ngày tạo: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
        date_label.setAlignment(Qt.AlignCenter)
        date_label.setStyleSheet("font-size: 12px; color: #666;")
        header_layout.addWidget(date_label)
        
        layout.addWidget(header_frame)
    
    def create_selection_section(self, layout):
        """Tạo phần chọn nhân viên và tháng"""
        selection_frame = QFrame()
        selection_frame.setFrameStyle(QFrame.Box)
        selection_layout = QHBoxLayout(selection_frame)
        
        # Period selection
        period_label = QLabel("Tháng:")
        period_label.setStyleSheet("font-weight: bold;")
        self.period_combo = QComboBox()
        self.period_combo.setMinimumWidth(150)
        self.period_combo.currentTextChanged.connect(self.on_period_changed)
        
        # Employee selection
        employee_label = QLabel("Nhân viên:")
        employee_label.setStyleSheet("font-weight: bold;")
        self.employee_combo = QComboBox()
        self.employee_combo.setMinimumWidth(300)
        self.employee_combo.currentTextChanged.connect(self.on_employee_changed)
        
        # Load button
        self.btn_load = QPushButton("🔄 Tải dữ liệu")
        self.btn_load.clicked.connect(self.load_data)
        self.btn_load.setStyleSheet("padding: 8px; background-color: #28a745; color: white; font-weight: bold;")
        
        selection_layout.addWidget(period_label)
        selection_layout.addWidget(self.period_combo)
        selection_layout.addWidget(employee_label)
        selection_layout.addWidget(self.employee_combo)
        selection_layout.addWidget(self.btn_load)
        selection_layout.addStretch()
        
        layout.addWidget(selection_frame)
    
    def create_employee_info_section(self):
        """Tạo section thông tin nhân viên"""
        group = QGroupBox("THÔNG TIN NHÂN VIÊN")
        group.setStyleSheet("QGroupBox { font-weight: bold; color: #007bff; }")
        layout = QGridLayout(group)
        
        # Create form fields
        self.emp_msnv = QLineEdit()
        self.emp_msnv.setReadOnly(True)
        self.emp_name = QLineEdit()
        self.emp_name.setReadOnly(True)
        self.emp_position = QLineEdit()
        self.emp_position.setReadOnly(True)
        self.emp_department = QLineEdit()
        self.emp_department.setReadOnly(True)
        self.emp_email = QLineEdit()
        self.emp_email.setReadOnly(True)
        
        # Add to layout
        layout.addWidget(QLabel("MSNV:"), 0, 0)
        layout.addWidget(self.emp_msnv, 0, 1)
        layout.addWidget(QLabel("Họ tên:"), 0, 2)
        layout.addWidget(self.emp_name, 0, 3)
        
        layout.addWidget(QLabel("Chức vụ:"), 1, 0)
        layout.addWidget(self.emp_position, 1, 1)
        layout.addWidget(QLabel("Phòng ban:"), 1, 2)
        layout.addWidget(self.emp_department, 1, 3)
        
        layout.addWidget(QLabel("Email:"), 2, 0)
        layout.addWidget(self.emp_email, 2, 1, 1, 3)
        
        self.form_layout.addWidget(group)
    
    def create_salary_calculation_section(self):
        """Tạo section tính lương cơ bản"""
        group = QGroupBox("LƯƠNG CƠ BẢN")
        group.setStyleSheet("QGroupBox { font-weight: bold; color: #28a745; }")
        layout = QGridLayout(group)
        
        # Fields
        self.basic_salary = QLineEdit("13,000,000")
        self.work_days = QLineEdit("0")
        self.office_days = QLineEdit("0")
        self.training_days = QLineEdit("0")
        self.overseas_days = QLineEdit("0")
        self.total_work_days = QLineEdit("0")
        self.total_work_days.setReadOnly(True)
        self.basic_amount = QLineEdit("0")
        self.basic_amount.setReadOnly(True)
        
        # Connect signals for auto calculation
        self.basic_salary.textChanged.connect(self.calculate_all)
        self.work_days.textChanged.connect(self.calculate_basic_salary)
        self.office_days.textChanged.connect(self.calculate_basic_salary)
        self.training_days.textChanged.connect(self.calculate_basic_salary)
        self.overseas_days.textChanged.connect(self.calculate_basic_salary)
        
        # Layout
        layout.addWidget(QLabel("Lương cơ bản (VNĐ):"), 0, 0)
        layout.addWidget(self.basic_salary, 0, 1)
        layout.addWidget(QLabel("Ngày công trường:"), 0, 2)
        layout.addWidget(self.work_days, 0, 3)
        
        layout.addWidget(QLabel("Ngày văn phòng:"), 1, 0)
        layout.addWidget(self.office_days, 1, 1)
        layout.addWidget(QLabel("Ngày đào tạo:"), 1, 2)
        layout.addWidget(self.training_days, 1, 3)
        
        layout.addWidget(QLabel("Ngày đi nước ngoài:"), 2, 0)
        layout.addWidget(self.overseas_days, 2, 1)
        layout.addWidget(QLabel("Tổng ngày làm:"), 2, 2)
        layout.addWidget(self.total_work_days, 2, 3)
        
        layout.addWidget(QLabel("Thành tiền:"), 3, 0)
        layout.addWidget(self.basic_amount, 3, 1)
        
        self.form_layout.addWidget(group)
    
    def create_allowance_section(self):
        """Tạo section phụ cấp"""
        group = QGroupBox("PHỤ CẤP")
        group.setStyleSheet("QGroupBox { font-weight: bold; color: #ffc107; }")
        layout = QGridLayout(group)
        
        # Fields
        self.work_allowance_rate = QLineEdit("150,000")
        self.work_allowance = QLineEdit("0")
        self.work_allowance.setReadOnly(True)
        
        self.training_allowance_rate = QLineEdit("40,000")
        self.training_allowance = QLineEdit("0")
        self.training_allowance.setReadOnly(True)
        
        self.office_allowance_rate = QLineEdit("20,000")
        self.office_allowance = QLineEdit("0")
        self.office_allowance.setReadOnly(True)
        
        # Thêm phụ cấp đi nước ngoài
        self.overseas_allowance_rate = QLineEdit("500,000")
        self.overseas_allowance = QLineEdit("0")
        self.overseas_allowance.setReadOnly(True)
        
        # Hệ số chức danh
        self.position_coefficient = QLineEdit("0.44")
        self.position_coefficient.setReadOnly(True)
        
        self.gas_allowance_rate = QLineEdit("36,000")
        self.gas_allowance = QLineEdit("0")
        self.gas_allowance.setReadOnly(True)
        
        # Thêm phụ cấp điện thoại
        self.phone_allowance_rate = QLineEdit("50,000")
        self.phone_allowance = QLineEdit("0")
        self.phone_allowance.setReadOnly(True)
        
        # Thêm phụ cấp khách sạn
        self.hotel_allowance_rate = QLineEdit("200,000")
        self.hotel_allowance = QLineEdit("0")
        self.hotel_allowance.setReadOnly(True)
        
        self.total_allowance = QLineEdit("0")
        self.total_allowance.setReadOnly(True)
        
        # Connect signals
        self.work_allowance_rate.textChanged.connect(self.calculate_allowances)
        self.training_allowance_rate.textChanged.connect(self.calculate_allowances)
        self.office_allowance_rate.textChanged.connect(self.calculate_allowances)
        self.overseas_allowance_rate.textChanged.connect(self.calculate_allowances)
        self.gas_allowance_rate.textChanged.connect(self.calculate_allowances)
        self.phone_allowance_rate.textChanged.connect(self.calculate_allowances)
        self.hotel_allowance_rate.textChanged.connect(self.calculate_allowances)
        
        # Layout
        layout.addWidget(QLabel("PC công trường (W)/ngày:"), 0, 0)
        layout.addWidget(self.work_allowance_rate, 0, 1)
        layout.addWidget(QLabel("Thành tiền:"), 0, 2)
        layout.addWidget(self.work_allowance, 0, 3)
        
        layout.addWidget(QLabel("PC đi nước ngoài/ngày:"), 1, 0)
        layout.addWidget(self.overseas_allowance_rate, 1, 1)
        layout.addWidget(QLabel("Thành tiền:"), 1, 2)
        layout.addWidget(self.overseas_allowance, 1, 3)
        
        layout.addWidget(QLabel("PC văn phòng (O)/ngày:"), 2, 0)
        layout.addWidget(self.office_allowance_rate, 2, 1)
        layout.addWidget(QLabel("Thành tiền:"), 2, 2)
        layout.addWidget(self.office_allowance, 2, 3)
        
        layout.addWidget(QLabel("Chức danh (hệ số):"), 3, 0)
        layout.addWidget(self.position_coefficient, 3, 1)
        layout.addWidget(QLabel(""), 3, 2)
        layout.addWidget(QLabel(""), 3, 3)
        
        layout.addWidget(QLabel("Xăng xe/ngày:"), 4, 0)
        layout.addWidget(self.gas_allowance_rate, 4, 1)
        layout.addWidget(QLabel("Thành tiền:"), 4, 2)
        layout.addWidget(self.gas_allowance, 4, 3)
        
        layout.addWidget(QLabel("PC điện thoại/ngày:"), 5, 0)
        layout.addWidget(self.phone_allowance_rate, 5, 1)
        layout.addWidget(QLabel("Thành tiền:"), 5, 2)
        layout.addWidget(self.phone_allowance, 5, 3)
        
        layout.addWidget(QLabel("PC khách sạn/ngày:"), 6, 0)
        layout.addWidget(self.hotel_allowance_rate, 6, 1)
        layout.addWidget(QLabel("Thành tiền:"), 6, 2)
        layout.addWidget(self.hotel_allowance, 6, 3)
        
        layout.addWidget(QLabel("TỔNG PHỤ CẤP:"), 7, 2)
        layout.addWidget(self.total_allowance, 7, 3)
        
        self.form_layout.addWidget(group)
    
    def create_overtime_section(self):
        """Tạo section thêm giờ"""
        group = QGroupBox("THÊM GIỜ")
        group.setStyleSheet("QGroupBox { font-weight: bold; color: #dc3545; }")
        layout = QGridLayout(group)
        
        # Fields
        self.overtime_150_hours = QLineEdit("0")
        self.overtime_150_amount = QLineEdit("0")
        self.overtime_150_amount.setReadOnly(True)
        
        self.sunday_200_hours = QLineEdit("0")
        self.sunday_200_amount = QLineEdit("0")
        self.sunday_200_amount.setReadOnly(True)
        
        self.holiday_300_hours = QLineEdit("0")
        self.holiday_300_amount = QLineEdit("0")
        self.holiday_300_amount.setReadOnly(True)
        
        self.total_overtime = QLineEdit("0")
        self.total_overtime.setReadOnly(True)
        
        # Connect signals
        self.overtime_150_hours.textChanged.connect(self.calculate_overtime)
        self.sunday_200_hours.textChanged.connect(self.calculate_overtime)
        self.holiday_300_hours.textChanged.connect(self.calculate_overtime)
        
        # Layout
        layout.addWidget(QLabel("Thêm giờ 150% (giờ):"), 0, 0)
        layout.addWidget(self.overtime_150_hours, 0, 1)
        layout.addWidget(QLabel("Thành tiền:"), 0, 2)
        layout.addWidget(self.overtime_150_amount, 0, 3)
        
        layout.addWidget(QLabel("Chủ nhật 200% (giờ):"), 1, 0)
        layout.addWidget(self.sunday_200_hours, 1, 1)
        layout.addWidget(QLabel("Thành tiền:"), 1, 2)
        layout.addWidget(self.sunday_200_amount, 1, 3)
        
        layout.addWidget(QLabel("Lễ tết 300% (giờ):"), 2, 0)
        layout.addWidget(self.holiday_300_hours, 2, 1)
        layout.addWidget(QLabel("Thành tiền:"), 2, 2)
        layout.addWidget(self.holiday_300_amount, 2, 3)
        
        layout.addWidget(QLabel("TỔNG THÊM GIỜ:"), 3, 2)
        layout.addWidget(self.total_overtime, 3, 3)
        
        self.form_layout.addWidget(group)
    
    def create_kpi_section(self):
        """Tạo section KPI"""
        group = QGroupBox("KPI - THƯỞNG HIỆU SUẤT")
        group.setStyleSheet("QGroupBox { font-weight: bold; color: #17a2b8; }")
        layout = QGridLayout(group)
        
        # Fields
        self.paut_meters = QLineEdit("0")
        self.paut_rate = QLineEdit("50,000")
        self.paut_amount = QLineEdit("0")
        self.paut_amount.setReadOnly(True)
        
        self.tofd_meters = QLineEdit("0")
        self.tofd_rate = QLineEdit("60,000")
        self.tofd_amount = QLineEdit("0")
        self.tofd_amount.setReadOnly(True)
        
        self.other_kpi = QLineEdit("0")
        self.total_kpi = QLineEdit("0")
        self.total_kpi.setReadOnly(True)
        
        # Connect signals
        self.paut_meters.textChanged.connect(self.calculate_kpi)
        self.paut_rate.textChanged.connect(self.calculate_kpi)
        self.tofd_meters.textChanged.connect(self.calculate_kpi)
        self.tofd_rate.textChanged.connect(self.calculate_kpi)
        self.other_kpi.textChanged.connect(self.calculate_kpi)
        
        # Layout
        layout.addWidget(QLabel("PAUT (mét):"), 0, 0)
        layout.addWidget(self.paut_meters, 0, 1)
        layout.addWidget(QLabel("Đơn giá:"), 0, 2)
        layout.addWidget(self.paut_rate, 0, 3)
        layout.addWidget(QLabel("Thành tiền:"), 0, 4)
        layout.addWidget(self.paut_amount, 0, 5)
        
        layout.addWidget(QLabel("TOFD (mét):"), 1, 0)
        layout.addWidget(self.tofd_meters, 1, 1)
        layout.addWidget(QLabel("Đơn giá:"), 1, 2)
        layout.addWidget(self.tofd_rate, 1, 3)
        layout.addWidget(QLabel("Thành tiền:"), 1, 4)
        layout.addWidget(self.tofd_amount, 1, 5)
        
        layout.addWidget(QLabel("KPI khác:"), 2, 0)
        layout.addWidget(self.other_kpi, 2, 1)
        layout.addWidget(QLabel("TỔNG KPI:"), 2, 4)
        layout.addWidget(self.total_kpi, 2, 5)
        
        self.form_layout.addWidget(group)
    
    def create_deduction_section(self):
        """Tạo section khấu trừ"""
        group = QGroupBox("KHẤU TRỪ")
        group.setStyleSheet("QGroupBox { font-weight: bold; color: #6f42c1; }")
        layout = QGridLayout(group)
        
        # Fields
        self.insurance_deduction = QLineEdit("0")
        self.tax_deduction = QLineEdit("0")
        self.advance_deduction = QLineEdit("0")
        self.other_deduction = QLineEdit("0")
        
        # Thêm các trường thuế
        self.personal_income = QLineEdit("0")
        self.personal_income.setReadOnly(True)
        self.personal_income.setStyleSheet("background-color: #f8f9fa;")
        
        self.family_deduction = QLineEdit("11,000,000")
        self.family_deduction.setStyleSheet("background-color: #fff3cd;")
        
        self.taxable_income = QLineEdit("0")
        self.taxable_income.setReadOnly(True)
        self.taxable_income.setStyleSheet("background-color: #f8f9fa;")
        
        self.tax_bracket = QLineEdit("0")
        self.tax_bracket.setReadOnly(True)
        self.tax_bracket.setStyleSheet("background-color: #f8f9fa;")
        
        self.total_deduction = QLineEdit("0")
        self.total_deduction.setReadOnly(True)
        
        # Connect signals
        self.insurance_deduction.textChanged.connect(self.calculate_deductions)
        self.tax_deduction.textChanged.connect(self.calculate_deductions)
        self.advance_deduction.textChanged.connect(self.calculate_deductions)
        self.other_deduction.textChanged.connect(self.calculate_deductions)
        self.family_deduction.textChanged.connect(self.calculate_tax)
        
        # Layout - Phần khấu trừ cơ bản
        layout.addWidget(QLabel("Bảo hiểm:"), 0, 0)
        layout.addWidget(self.insurance_deduction, 0, 1)
        layout.addWidget(QLabel("Thuế TNCN:"), 0, 2)
        layout.addWidget(self.tax_deduction, 0, 3)
        
        layout.addWidget(QLabel("Tạm ứng:"), 1, 0)
        layout.addWidget(self.advance_deduction, 1, 1)
        layout.addWidget(QLabel("Khấu trừ khác:"), 1, 2)
        layout.addWidget(self.other_deduction, 1, 3)
        
        # Layout - Phần tính thuế
        layout.addWidget(QLabel("Thu nhập cá nhân:"), 2, 0)
        layout.addWidget(self.personal_income, 2, 1)
        layout.addWidget(QLabel("Giảm trừ gia cảnh:"), 2, 2)
        layout.addWidget(self.family_deduction, 2, 3)
        
        layout.addWidget(QLabel("Thu nhập chịu thuế:"), 3, 0)
        layout.addWidget(self.taxable_income, 3, 1)
        layout.addWidget(QLabel("Bậc thuế (%):"), 3, 2)
        layout.addWidget(self.tax_bracket, 3, 3)
        
        layout.addWidget(QLabel("TỔNG KHẤU TRỪ:"), 4, 2)
        layout.addWidget(self.total_deduction, 4, 3)
        
        self.form_layout.addWidget(group)
    
    def create_summary_section(self):
        """Tạo section tổng kết"""
        group = QGroupBox("TỔNG KẾT LƯƠNG")
        group.setStyleSheet("QGroupBox { font-weight: bold; color: #e83e8c; font-size: 14px; }")
        layout = QGridLayout(group)
        
        # Fields
        self.gross_salary = QLineEdit("0")
        self.gross_salary.setReadOnly(True)
        self.gross_salary.setStyleSheet("font-size: 14px; font-weight: bold; background-color: #e7f3ff;")
        
        self.net_salary = QLineEdit("0")
        self.net_salary.setReadOnly(True)
        self.net_salary.setStyleSheet("font-size: 16px; font-weight: bold; background-color: #d4edda; color: #155724;")
        
        # Layout
        layout.addWidget(QLabel("Tổng lương (trước khấu trừ):"), 0, 0)
        layout.addWidget(self.gross_salary, 0, 1)
        
        layout.addWidget(QLabel("LƯƠNG THỰC LĨNH:"), 1, 0)
        layout.addWidget(self.net_salary, 1, 1)
        
        self.form_layout.addWidget(group)
    
    def create_action_buttons(self, layout):
        """Tạo các nút hành động"""
        button_layout = QHBoxLayout()
        
        self.btn_calculate = QPushButton("💰 Tính lương")
        self.btn_calculate.clicked.connect(self.calculate_all)
        self.btn_calculate.setStyleSheet("padding: 10px; background-color: #007bff; color: white; font-weight: bold;")
        
        self.btn_print = QPushButton("🖨️ In phiếu lương")
        self.btn_print.clicked.connect(self.show_print_dialog)
        self.btn_print.setStyleSheet("padding: 10px; background-color: #6c757d; color: white; font-weight: bold;")
        
        self.btn_save = QPushButton("💾 Lưu")
        self.btn_save.clicked.connect(self.save_salary_data)
        self.btn_save.setStyleSheet("padding: 10px; background-color: #28a745; color: white; font-weight: bold;")
        
        self.btn_clear = QPushButton("🗑️ Xóa form")
        self.btn_clear.clicked.connect(self.clear_form)
        self.btn_clear.setStyleSheet("padding: 10px; background-color: #dc3545; color: white; font-weight: bold;")
        
        button_layout.addWidget(self.btn_calculate)
        button_layout.addWidget(self.btn_print)
        button_layout.addWidget(self.btn_save)
        button_layout.addWidget(self.btn_clear)
        button_layout.addStretch()
        
        layout.addLayout(button_layout)
    
    def apply_styles(self):
        """Áp dụng styles cho form"""
        self.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #cccccc;
                border-radius: 5px;
                margin-top: 1ex;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
            QLineEdit {
                border: 1px solid #ccc;
                border-radius: 3px;
                padding: 5px;
                font-size: 11px;
            }
            QLineEdit:read-only {
                background-color: #f8f9fa;
            }
            QComboBox {
                border: 1px solid #ccc;
                border-radius: 3px;
                padding: 5px;
                font-size: 11px;
            }
            QLabel {
                font-size: 11px;
            }
        """)
    
    def load_data(self):
        """Load dữ liệu từ tab bảng công"""
        try:
            # Clear combos first
            self.period_combo.clear()
            self.employee_combo.clear()
            
            if not self.bang_cong_tab or not hasattr(self.bang_cong_tab, 'monthly_data'):
                QMessageBox.warning(self, "Lỗi", "Không có dữ liệu từ tab bảng công!")
                return
            
            monthly_data = self.bang_cong_tab.monthly_data
            
            # Load periods
            loaded_periods = [period for period, data in monthly_data.items() 
                            if data.get('is_loaded', False)]
            
            if not loaded_periods:
                QMessageBox.warning(self, "Lỗi", "Không có period nào được load!")
                return
            
            self.period_combo.addItems(loaded_periods)
            
            # Load employees for first period
            if loaded_periods:
                self.load_employees_for_period(loaded_periods[0])
            
            QMessageBox.information(self, "Thành công", f"Đã load {len(loaded_periods)} tháng!")
            
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Lỗi load dữ liệu: {str(e)}")
    
    def load_employees_for_period(self, period):
        """Load danh sách nhân viên cho period"""
        try:
            if not self.bang_cong_tab or not hasattr(self.bang_cong_tab, 'monthly_data'):
                return
            
            monthly_data = self.bang_cong_tab.monthly_data
            if period not in monthly_data or not monthly_data[period].get('is_loaded'):
                return
            
            employees_data = monthly_data[period].get('data_chamcong', {})
            
            # Clear and populate employee combo
            self.employee_combo.clear()
            
            employee_items = []
            for msnv, emp_data in employees_data.items():
                info = emp_data.get('info', {})
                name = info.get('name', msnv)
                employee_items.append(f"{msnv} - {name}")
            
            self.employee_combo.addItems(employee_items)
            
        except Exception as e:
            print(f"Lỗi load employees: {e}")
    
    def on_period_changed(self, period):
        """Xử lý khi thay đổi period"""
        if period:
            self.load_employees_for_period(period)
    
    def on_employee_changed(self, employee_text):
        """Xử lý khi thay đổi nhân viên"""
        if employee_text and " - " in employee_text:
            msnv = employee_text.split(" - ")[0]
            period = self.period_combo.currentText()
            self.fill_employee_data(period, msnv)
    
    def fill_employee_data(self, period, msnv):
        """Fill dữ liệu nhân viên vào form từ database và dữ liệu chấm công"""
        try:
            self.current_period = period
            self.current_msnv = msnv
            
            # 1. Lấy thông tin nhân viên từ database theo MSNV
            employee_info = self.employee_mapper.get_employee_info(msnv)
            if employee_info:
                self.emp_msnv.setText(msnv)
                self.emp_name.setText(employee_info.get('name', ''))
                self.emp_position.setText(employee_info.get('position', ''))
                self.emp_department.setText(employee_info.get('department', ''))
                self.emp_email.setText('')  # Email không có trong database hiện tại
            else:
                # Fallback: lấy từ JSON nếu không tìm thấy trong database
                self.fill_employee_from_json(period, msnv)
            
            # 2. Lấy lương cơ bản từ quy định lương theo tên nhân viên
            employee_name = employee_info.get('name', '') if employee_info else ''
            basic_salary = self.get_basic_salary_from_db(employee_name)
            if basic_salary > 0:
                self.basic_salary.setText(self.format_number(basic_salary))
            
            # 3. Fill dữ liệu chấm công từ tab bảng công
            self.fill_attendance_data(period, msnv)
            
            # 4. Tính toán tất cả
            self.calculate_all()
            
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Lỗi fill dữ liệu: {str(e)}")
    
    def fill_employee_from_json(self, period, msnv):
        """Fallback: Fill thông tin nhân viên từ JSON chấm công"""
        try:
            if not self.bang_cong_tab or not hasattr(self.bang_cong_tab, 'monthly_data'):
                return
            
            monthly_data = self.bang_cong_tab.monthly_data
            if period not in monthly_data:
                return
            
            employees_data = monthly_data[period].get('data_chamcong', {})
            if msnv not in employees_data:
                return
            
            employee_data = employees_data[msnv]
            info = employee_data.get('info', {})
            
            self.emp_msnv.setText(msnv)
            self.emp_name.setText(info.get('name', ''))
            self.emp_position.setText(info.get('position', ''))
            self.emp_department.setText(info.get('department', ''))
            self.emp_email.setText(info.get('email', ''))
            
        except Exception as e:
            print(f"Lỗi fill từ JSON: {e}")
    
    def get_basic_salary_from_db(self, employee_name):
        """Lấy lương cơ bản từ database quy định lương"""
        try:
            if not employee_name or not self.ds_luong_nv:
                print(f"❌ Không có tên nhân viên hoặc dữ liệu lương")
                return 20000000  # Default salary
            
            print(f"🔍 Tìm lương cho nhân viên: '{employee_name}'")
            print(f"📊 Số lượng bản ghi lương: {len(self.ds_luong_nv)}")
            
            # Tìm lương cơ bản theo tên nhân viên
            for i, luong_record in enumerate(self.ds_luong_nv):
                if isinstance(luong_record, list) and len(luong_record) >= 4:
                    name_in_db = str(luong_record[1]).strip()  # Tên ở index 1
                    salary_str = str(luong_record[3]).strip()  # Lương ở index 3
                    print(f"   📋 Bản ghi {i}: Tên='{name_in_db}', Lương='{salary_str}'")
                    
                    if name_in_db.lower() == employee_name.lower():
                        # Parse salary (có thể có dấu phẩy)
                        salary = float(salary_str.replace(',', '').replace(' ', ''))
                        print(f"✅ Tìm thấy lương cho '{employee_name}': {salary:,.0f} VNĐ")
                        return salary
            
            print(f"⚠️ Không tìm thấy lương cho nhân viên: '{employee_name}'")
            return 20000000  # Default nếu không tìm thấy
            
        except Exception as e:
            print(f"❌ Lỗi lấy lương cơ bản: {e}")
            return 20000000
    
    def fill_attendance_data(self, period, msnv):
        """Fill dữ liệu chấm công từ tab bảng công"""
        try:
            if not self.bang_cong_tab or not hasattr(self.bang_cong_tab, 'monthly_data'):
                return
            
            monthly_data = self.bang_cong_tab.monthly_data
            if period not in monthly_data:
                return
            
            employees_data = monthly_data[period].get('data_chamcong', {})
            if msnv not in employees_data:
                return
            
            employee_data = employees_data[msnv]
            self.current_employee_data = employee_data
            
            # Fill attendance data
            attendance = employee_data.get('attendance', {})
            summary = attendance.get('summary', {})
            
            if summary:
                self.work_days.setText(str(summary.get('total_work_days', 0)))
                self.office_days.setText(str(summary.get('total_office_days', 0)))
                self.training_days.setText(str(summary.get('total_training_days', 0)))
                
                self.overtime_150_hours.setText(str(summary.get('total_overtime_hours', 0)))
                self.sunday_200_hours.setText(str(summary.get('sunday_200_hours', 0)))
                self.holiday_300_hours.setText(str(summary.get('holiday_300_hours', 0)))
                
                self.paut_meters.setText(str(summary.get('total_paut_meters', 0)))
                self.tofd_meters.setText(str(summary.get('total_tofd_meters', 0)))
            
        except Exception as e:
            print(f"Lỗi fill attendance: {e}")
    
    def get_number_value(self, text):
        """Chuyển đổi text thành số, xử lý N/A"""
        try:
            if not text or text.strip() == "" or text.strip().upper() == "N/A":
                return 0
            # Loại bỏ dấu phẩy và khoảng trắng
            clean_text = text.replace(',', '').replace(' ', '').strip()
            return float(clean_text)
        except (ValueError, AttributeError):
            return 0
    
    def format_number(self, value):
        """Format số với dấu phẩy"""
        return f"{int(value):,}"
    
    def calculate_basic_salary(self):
        """Tính lương cơ bản"""
        try:
            work_days = self.get_number_value(self.work_days.text())
            office_days = self.get_number_value(self.office_days.text())
            training_days = self.get_number_value(self.training_days.text())
            overseas_days = self.get_number_value(self.overseas_days.text())
            basic_salary = self.get_number_value(self.basic_salary.text())
            
            total_days = work_days + office_days + training_days + overseas_days
            self.total_work_days.setText(str(int(total_days)))
            
            # Tính lương cơ bản (giả sử 26 ngày/tháng)
            daily_rate = basic_salary / 26
            basic_amount = total_days * daily_rate
            self.basic_amount.setText(self.format_number(basic_amount))
            
            self.calculate_allowances()
            self.calculate_final_totals()
            
        except Exception as e:
            print(f"Lỗi tính lương cơ bản: {e}")
    
    def calculate_allowances(self):
        """Tính phụ cấp"""
        try:
            work_days = self.get_number_value(self.work_days.text())
            office_days = self.get_number_value(self.office_days.text())
            training_days = self.get_number_value(self.training_days.text())
            overseas_days = self.get_number_value(self.overseas_days.text())
            
            work_rate = self.get_number_value(self.work_allowance_rate.text())
            training_rate = self.get_number_value(self.training_allowance_rate.text())
            office_rate = self.get_number_value(self.office_allowance_rate.text())
            overseas_rate = self.get_number_value(self.overseas_allowance_rate.text())
            gas_rate = self.get_number_value(self.gas_allowance_rate.text())
            phone_rate = self.get_number_value(self.phone_allowance_rate.text())
            hotel_rate = self.get_number_value(self.hotel_allowance_rate.text())
            
            work_allowance = work_days * work_rate
            training_allowance = training_days * training_rate
            office_allowance = office_days * office_rate
            overseas_allowance = overseas_days * overseas_rate
            gas_allowance = work_days * gas_rate
            phone_allowance = work_days * phone_rate
            hotel_allowance = work_days * hotel_rate
            
            self.work_allowance.setText(self.format_number(work_allowance))
            self.training_allowance.setText(self.format_number(training_allowance))
            self.office_allowance.setText(self.format_number(office_allowance))
            self.overseas_allowance.setText(self.format_number(overseas_allowance))
            self.gas_allowance.setText(self.format_number(gas_allowance))
            self.phone_allowance.setText(self.format_number(phone_allowance))
            self.hotel_allowance.setText(self.format_number(hotel_allowance))
            
            total = work_allowance + training_allowance + office_allowance + overseas_allowance + gas_allowance + phone_allowance + hotel_allowance
            self.total_allowance.setText(self.format_number(total))
            
            self.calculate_final_totals()
            
        except Exception as e:
            print(f"Lỗi tính phụ cấp: {e}")
    
    def calculate_overtime(self):
        """Tính thêm giờ"""
        try:
            basic_salary = self.get_number_value(self.basic_salary.text())
            hourly_rate = basic_salary / 26 / 8  # 26 ngày, 8 giờ/ngày
            
            overtime_150_hours = self.get_number_value(self.overtime_150_hours.text())
            sunday_200_hours = self.get_number_value(self.sunday_200_hours.text())
            holiday_300_hours = self.get_number_value(self.holiday_300_hours.text())
            
            overtime_150_amount = overtime_150_hours * hourly_rate * 1.5
            sunday_200_amount = sunday_200_hours * hourly_rate * 2.0
            holiday_300_amount = holiday_300_hours * hourly_rate * 3.0
            
            self.overtime_150_amount.setText(self.format_number(overtime_150_amount))
            self.sunday_200_amount.setText(self.format_number(sunday_200_amount))
            self.holiday_300_amount.setText(self.format_number(holiday_300_amount))
            
            total = overtime_150_amount + sunday_200_amount + holiday_300_amount
            self.total_overtime.setText(self.format_number(total))
            
            self.calculate_final_totals()
            
        except Exception as e:
            print(f"Lỗi tính thêm giờ: {e}")
    
    def calculate_kpi(self):
        """Tính KPI"""
        try:
            paut_meters = self.get_number_value(self.paut_meters.text())
            paut_rate = self.get_number_value(self.paut_rate.text())
            tofd_meters = self.get_number_value(self.tofd_meters.text())
            tofd_rate = self.get_number_value(self.tofd_rate.text())
            other_kpi = self.get_number_value(self.other_kpi.text())
            
            paut_amount = paut_meters * paut_rate
            tofd_amount = tofd_meters * tofd_rate
            
            self.paut_amount.setText(self.format_number(paut_amount))
            self.tofd_amount.setText(self.format_number(tofd_amount))
            
            total = paut_amount + tofd_amount + other_kpi
            self.total_kpi.setText(self.format_number(total))
            
            self.calculate_final_totals()
            
        except Exception as e:
            print(f"Lỗi tính KPI: {e}")
    
    def calculate_deductions(self):
        """Tính khấu trừ"""
        try:
            insurance = self.get_number_value(self.insurance_deduction.text())
            tax = self.get_number_value(self.tax_deduction.text())
            advance = self.get_number_value(self.advance_deduction.text())
            other = self.get_number_value(self.other_deduction.text())
            
            total = insurance + tax + advance + other
            self.total_deduction.setText(self.format_number(total))
            
            self.calculate_final_totals()
            
        except Exception as e:
            print(f"Lỗi tính khấu trừ: {e}")
    
    def calculate_tax(self):
        """Tính thuế thu nhập cá nhân"""
        try:
            # Tính thu nhập cá nhân
            basic_amount = self.get_number_value(self.basic_amount.text())
            total_allowance = self.get_number_value(self.total_allowance.text())
            total_overtime = self.get_number_value(self.total_overtime.text())
            total_kpi = self.get_number_value(self.total_kpi.text())
            
            personal_income = basic_amount + total_allowance + total_overtime + total_kpi
            self.personal_income.setText(self.format_number(personal_income))
            
            # Tính thu nhập chịu thuế
            family_deduction = self.get_number_value(self.family_deduction.text())
            taxable_income = max(0, personal_income - family_deduction)
            self.taxable_income.setText(self.format_number(taxable_income))
            
            # Tính thuế theo bậc
            tax_amount = self.calculate_tax_by_bracket(taxable_income)
            self.tax_deduction.setText(self.format_number(tax_amount))
            
            # Cập nhật bậc thuế
            bracket = self.get_tax_bracket(taxable_income)
            self.tax_bracket.setText(f"{bracket}%")
            
            self.calculate_deductions()
            
        except Exception as e:
            print(f"Lỗi tính thuế: {e}")
    
    def calculate_tax_by_bracket(self, taxable_income):
        """Tính thuế theo bậc thuế"""
        if taxable_income <= 5000000:
            return taxable_income * 0.05
        elif taxable_income <= 10000000:
            return 250000 + (taxable_income - 5000000) * 0.10
        elif taxable_income <= 18000000:
            return 750000 + (taxable_income - 10000000) * 0.15
        elif taxable_income <= 32000000:
            return 1950000 + (taxable_income - 18000000) * 0.20
        elif taxable_income <= 52000000:
            return 4750000 + (taxable_income - 32000000) * 0.25
        elif taxable_income <= 80000000:
            return 9750000 + (taxable_income - 52000000) * 0.30
        else:
            return 18150000 + (taxable_income - 80000000) * 0.35
    
    def get_tax_bracket(self, taxable_income):
        """Lấy bậc thuế"""
        if taxable_income <= 5000000:
            return 5
        elif taxable_income <= 10000000:
            return 10
        elif taxable_income <= 18000000:
            return 15
        elif taxable_income <= 32000000:
            return 20
        elif taxable_income <= 52000000:
            return 25
        elif taxable_income <= 80000000:
            return 30
        else:
            return 35
    
    def calculate_final_totals(self):
        """Tính tổng cuối cùng"""
        try:
            basic_amount = self.get_number_value(self.basic_amount.text())
            total_allowance = self.get_number_value(self.total_allowance.text())
            total_overtime = self.get_number_value(self.total_overtime.text())
            total_kpi = self.get_number_value(self.total_kpi.text())
            total_deduction = self.get_number_value(self.total_deduction.text())
            
            gross_salary = basic_amount + total_allowance + total_overtime + total_kpi
            net_salary = gross_salary - total_deduction
            
            self.gross_salary.setText(self.format_number(gross_salary))
            self.net_salary.setText(self.format_number(net_salary))
            
        except Exception as e:
            print(f"Lỗi tính tổng: {e}")
    
    def calculate_all(self):
        """Tính toàn bộ"""
        self.calculate_basic_salary()
        self.calculate_allowances()
        self.calculate_overtime()
        self.calculate_kpi()
        self.calculate_deductions()
        self.calculate_final_totals()
    
    def show_print_dialog(self):
        """Hiển thị dialog in phiếu lương"""
        try:
            # Kiểm tra dữ liệu cơ bản trước khi thu thập
            if not self.current_msnv or not self.current_period:
                QMessageBox.warning(self, "Cảnh báo", 
                    "Vui lòng chọn nhân viên và tháng/năm trước khi in!")
                return
            
            # Thu thập dữ liệu hiện tại
            salary_data = self.collect_salary_data()
            
            # Kiểm tra chi tiết dữ liệu nhân viên
            employee_name = salary_data.get('name', '').strip()
            if not employee_name or employee_name == 'N/A' or employee_name == '':
                # Thêm thông tin debug để giúp người dùng
                debug_info = f"""
Thông tin debug:
- MSNV hiện tại: {self.current_msnv or 'Chưa chọn'}
- Tháng/năm: {self.current_period or 'Chưa chọn'}
- Tên nhân viên: '{employee_name}'
- Trường emp_name: '{self.emp_name.text()}'

Vui lòng:
1. Chọn nhân viên từ dropdown
2. Đảm bảo đã load dữ liệu từ tab bảng công
3. Kiểm tra dữ liệu nhân viên trong database
                """
                QMessageBox.warning(self, "Cảnh báo", 
                    f"Không tìm thấy thông tin nhân viên!\n{debug_info}")
                return
            
            # Hiển thị dialog in
            dialog = SalaryPrintDialog(salary_data, self)
            dialog.exec_()
            
        except Exception as e:
            QMessageBox.warning(self, "Lỗi", f"Không thể hiển thị dialog in: {e}")
    
    def collect_salary_data(self):
        """Thu thập dữ liệu lương đã tính sẵn để in"""
        try:
            return {
                # Thông tin nhân viên
                'msnv': self.emp_msnv.text(),
                'name': self.emp_name.text(),
                'position': self.emp_position.text(),
                'department': self.emp_department.text(),
                'period': self.current_period or f"{datetime.now().month:02d}/{datetime.now().year}",
                
                # Lương cơ bản
                'basic_salary': self.basic_salary.text(),
                'basic_amount': self.basic_amount.text(),
                'work_days': self.work_days.text(),
                
                # Thêm giờ
                'overtime_150_hours': self.overtime_150_hours.text(),
                'overtime_150_amount': self.overtime_150_amount.text(),
                'sunday_200_hours': self.sunday_200_hours.text(),
                'sunday_200_amount': self.sunday_200_amount.text(),
                'holiday_300_hours': self.holiday_300_hours.text(),
                'holiday_300_amount': self.holiday_300_amount.text(),
                'total_overtime': self.total_overtime.text(),
                
                # Phụ cấp
                'work_allowance': self.work_allowance.text(),
                'training_allowance': self.training_allowance.text(),
                'office_allowance': self.office_allowance.text(),
                'overseas_allowance': self.overseas_allowance.text(),
                'gas_allowance': self.gas_allowance.text(),
                'phone_allowance': self.phone_allowance.text(),
                'hotel_allowance': self.hotel_allowance.text(),
                'total_allowance': self.total_allowance.text(),
                'training_days': self.training_days.text(),
                'office_days': self.office_days.text(),
                'overseas_days': self.overseas_days.text(),
                
                # KPI
                'paut_meters': self.paut_meters.text(),
                'paut_amount': self.paut_amount.text(),
                'tofd_meters': self.tofd_meters.text(),
                'tofd_amount': self.tofd_amount.text(),
                'total_kpi': self.total_kpi.text(),
                
                # Tổng thu nhập
                'gross_salary': self.gross_salary.text(),
                
                # Khấu trừ
                'insurance_deduction': self.insurance_deduction.text(),
                'tax_deduction': self.tax_deduction.text(),
                'advance_deduction': self.advance_deduction.text(),
                'other_deduction': self.other_deduction.text(),
                'total_deduction': self.total_deduction.text(),
                
                # Thuế
                'taxable_income': self.taxable_income.text(),
                'family_deduction': self.family_deduction.text(),
                'tax_bracket': self.tax_bracket.text(),
                
                # Thực nhận
                'net_salary': self.net_salary.text()
            }
        except Exception as e:
            print(f"Lỗi thu thập dữ liệu lương: {e}")
            return {}
    
    def save_salary_data(self):
        """Lưu dữ liệu lương"""
        try:
            if not self.current_msnv or not self.current_period:
                QMessageBox.warning(self, "Lỗi", "Chưa chọn nhân viên!")
                return
            
            # Tạo dữ liệu lương
            salary_data = {
                'msnv': self.current_msnv,
                'period': self.current_period,
                'employee_info': {
                    'name': self.emp_name.text(),
                    'position': self.emp_position.text(),
                    'department': self.emp_department.text(),
                    'email': self.emp_email.text()
                },
                'basic_salary': {
                    'amount': self.get_number_value(self.basic_salary.text()),
                    'work_days': self.get_number_value(self.work_days.text()),
                    'office_days': self.get_number_value(self.office_days.text()),
                    'training_days': self.get_number_value(self.training_days.text()),
                    'overseas_days': self.get_number_value(self.overseas_days.text()),
                    'total_amount': self.get_number_value(self.basic_amount.text())
                },
                'allowances': {
                    'work_allowance': self.get_number_value(self.work_allowance.text()),
                    'training_allowance': self.get_number_value(self.training_allowance.text()),
                    'office_allowance': self.get_number_value(self.office_allowance.text()),
                    'gas_allowance': self.get_number_value(self.gas_allowance.text()),
                    'phone_allowance': self.get_number_value(self.phone_allowance.text()),
                    'hotel_allowance': self.get_number_value(self.hotel_allowance.text()),
                    'total_allowance': self.get_number_value(self.total_allowance.text())
                },
                'overtime': {
                    'overtime_150': self.get_number_value(self.overtime_150_amount.text()),
                    'sunday_200': self.get_number_value(self.sunday_200_amount.text()),
                    'holiday_300': self.get_number_value(self.holiday_300_amount.text()),
                    'total_overtime': self.get_number_value(self.total_overtime.text())
                },
                'kpi': {
                    'paut_amount': self.get_number_value(self.paut_amount.text()),
                    'tofd_amount': self.get_number_value(self.tofd_amount.text()),
                    'other_kpi': self.get_number_value(self.other_kpi.text()),
                    'total_kpi': self.get_number_value(self.total_kpi.text())
                },
                'deductions': {
                    'insurance': self.get_number_value(self.insurance_deduction.text()),
                    'tax': self.get_number_value(self.tax_deduction.text()),
                    'advance': self.get_number_value(self.advance_deduction.text()),
                    'other': self.get_number_value(self.other_deduction.text()),
                    'total_deduction': self.get_number_value(self.total_deduction.text())
                },
                'totals': {
                    'gross_salary': self.get_number_value(self.gross_salary.text()),
                    'net_salary': self.get_number_value(self.net_salary.text())
                },
                'created_date': datetime.now().isoformat()
            }
            
            # Lưu vào file
            import json
            filename = f"data/salary_{self.current_msnv}_{self.current_period.replace('/', '_')}.json"
            
            # Tạo thư mục nếu chưa có
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(salary_data, f, ensure_ascii=False, indent=2)
            
            QMessageBox.information(self, "Thành công", f"Đã lưu phiếu lương vào {filename}")
            
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Lỗi lưu dữ liệu: {str(e)}")
    
    def clear_form(self):
        """Xóa form"""
        reply = QMessageBox.question(self, "Xác nhận", "Bạn có chắc muốn xóa toàn bộ form?", 
                                   QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            # Clear employee info
            self.emp_msnv.clear()
            self.emp_name.clear()
            self.emp_position.clear()
            self.emp_department.clear()
            self.emp_email.clear()
            
            # Reset values to default
            self.basic_salary.setText("N/A")
            self.work_days.setText("N/A")
            self.office_days.setText("N/A")
            self.training_days.setText("N/A")
            
            self.work_allowance_rate.setText("N/A")
            self.training_allowance_rate.setText("N/A")
            self.office_allowance_rate.setText("N/A")
            self.gas_allowance_rate.setText("N/A")
            self.phone_allowance_rate.setText("N/A")
            self.hotel_allowance_rate.setText("N/A")
            
            self.overtime_150_hours.setText("N/A")
            self.sunday_200_hours.setText("N/A")
            self.holiday_300_hours.setText("N/A")
            
            self.paut_meters.setText("N/A")
            self.paut_rate.setText("N/A")
            self.tofd_meters.setText("N/A")
            self.tofd_rate.setText("N/A")
            self.other_kpi.setText("N/A")
            
            self.insurance_deduction.setText("N/A")
            self.tax_deduction.setText("N/A")
            self.advance_deduction.setText("N/A")
            self.other_deduction.setText("N/A")
            self.personal_income.setText("N/A")
            self.family_deduction.setText("N/A")
            self.taxable_income.setText("N/A")
            self.tax_bracket.setText("N/A")
            
            # Clear calculated fields
            self.calculate_all()
            
            self.current_employee_data = None
            self.current_period = None
            self.current_msnv = None


class SalaryPrintDialog(QDialog):
    """Dialog in phiếu lương với preview đẹp sử dụng ReportLab"""
    
    def __init__(self, salary_data, parent=None):
        super().__init__(parent)
        # Chuẩn hóa dữ liệu: thay mọi "N/A" bằng "-" để hiển thị
        self.salary_data = {k: (('-' if isinstance(v, str) and v.strip().upper() == 'N/A' else v)) for k, v in salary_data.items()}
        self.setWindowTitle("In Phiếu Lương - Hitech NDT")
        self.setModal(True)
        self.setMinimumSize(1000, 800)
        self.resize(1200, 900)
        
        self.init_ui()
        self.generate_preview()
    
    def init_ui(self):
        """Khởi tạo giao diện"""
        layout = QVBoxLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Toolbar
        toolbar = QHBoxLayout()
        
        self.btn_copy = QPushButton("🖼️ Copy ảnh")
        self.btn_copy.clicked.connect(self.copy_image)
        self.btn_copy.setStyleSheet("""
            QPushButton {
                background-color: #17a2b8;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #138496; }
        """)
        
        self.btn_save = QPushButton("💾 Lưu ảnh")
        self.btn_save.clicked.connect(self.save_image)
        self.btn_save.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #218838; }
        """)
        
        self.btn_pdf = QPushButton(" Xuất PDF")
        self.btn_pdf.clicked.connect(self.export_pdf)
        self.btn_pdf.setStyleSheet("""
            QPushButton {
                background-color: #dc3545;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #c82333; }
        """)
        
        self.btn_print = QPushButton("️ In")
        self.btn_print.clicked.connect(self.print_document)
        self.btn_print.setStyleSheet("""
            QPushButton {
                background-color: #6c757d;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #5a6268; }
        """)
        
        toolbar.addWidget(self.btn_copy)
        toolbar.addWidget(self.btn_save)
        toolbar.addWidget(self.btn_pdf)
        toolbar.addWidget(self.btn_print)
        toolbar.addStretch()
        
        layout.addLayout(toolbar)
        
        # Preview area
        self.preview_label = QLabel()
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setStyleSheet("""
            QLabel {
                border: 2px solid #dee2e6;
                border-radius: 8px;
                background-color: #f8f9fa;
            }
        """)
        
        # Scroll area cho preview
        scroll = QScrollArea()
        scroll.setWidget(self.preview_label)
        scroll.setWidgetResizable(True)
        scroll.setMinimumHeight(600)
        
        layout.addWidget(scroll)
        
        # Close button
        close_btn = QPushButton("Đóng")
        close_btn.clicked.connect(self.accept)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #6c757d;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 4px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover { background-color: #5a6268; }
        """)
        layout.addWidget(close_btn)
        
        self.setLayout(layout)
    
    def generate_preview(self):
        """Tạo preview phiếu lương"""
        try:
            # Luôn tạo ảnh preview chi tiết bằng PIL để hiển thị giống mẫu
            temp_pdf = "temp_salary.pdf"
            self.create_pdf_report(temp_pdf)
            if os.path.exists(temp_pdf):
                self.convert_pdf_to_image(temp_pdf)
                os.remove(temp_pdf)
            else:
                self.convert_pdf_to_image("")
        except Exception as e:
            print(f"Lỗi tạo preview: {e}")
            self.convert_pdf_to_image("")
    
    def create_pdf_report(self, filename):
        """Tạo PDF report y chang như hình mẫu"""
        try:
            doc = SimpleDocTemplate(filename, pagesize=A4, 
                                  rightMargin=1*cm, leftMargin=1*cm,
                                  topMargin=1*cm, bottomMargin=1*cm)
            
            # Styles
            styles = getSampleStyleSheet()
            
            # Company title style
            company_style = ParagraphStyle(
                'Company',
                parent=styles['Normal'],
                fontSize=14,
                spaceAfter=5,
                alignment=TA_CENTER,
                textColor=colors.darkblue,
                fontName='Helvetica-Bold'
            )
            
            # Main title style
            title_style = ParagraphStyle(
                'Title',
                parent=styles['Normal'],
                fontSize=16,
                spaceAfter=12,
                alignment=TA_CENTER,
                textColor=colors.darkblue,
                fontName='Helvetica-Bold'
            )
            
            # Sub header style
            sub_style = ParagraphStyle(
                'Sub',
                parent=styles['Normal'],
                fontSize=9,
                alignment=TA_LEFT,
                textColor=colors.black,
                fontName='Helvetica'
            )
            
            # Story
            story = []
            
            # Header with logo + title
            logo_path = "logo_hitech.png"
            header_cells = []
            if os.path.exists(logo_path):
                header_logo = Image(logo_path, width=2.2*cm, height=2.2*cm)
            else:
                header_logo = Paragraph("", sub_style)
            header_cells.append([header_logo, Paragraph("PHIẾU LƯƠNG", title_style), Paragraph("", sub_style)])
            header_table = Table(header_cells, colWidths=[2.5*cm, 11*cm, 1.5*cm])
            header_table.setStyle(TableStyle([
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('ALIGN', (1, 0), (1, 0), 'CENTER'),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ]))
            story.append(header_table)
            story.append(Spacer(1, 6))
            story.append(Paragraph("🏢 CÔNG TY TNHH DỊCH VỤ KIỂM TRA KHÔNG PHÁ HỦY CÔNG NGHỆ CAO", company_style))
            story.append(Spacer(1, 4))
            
            # Thông tin nhân viên
            period = self.salary_data.get('period', '-')
            month, year = period.split('/') if '/' in period else ('-', '-')
            
            # Bảng thông tin nhân viên
            emp_info_data = [
                ['Tháng:', month, 'Năm:', year],
                ['Nhân Viên:', self.salary_data.get('name', '-').upper(), 'Mã số:', self.salary_data.get('msnv', '-')],
                ['Phòng Ban:', self.salary_data.get('department', '-'), 'Chức vụ:', self.salary_data.get('position', '-')]
            ]
            
            emp_info_table = Table(emp_info_data, colWidths=[2.5*cm, 6*cm, 2*cm, 5*cm])
            emp_info_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('BACKGROUND', (0, 0), (0, -1), colors.whitesmoke),
                ('BACKGROUND', (2, 0), (2, -1), colors.whitesmoke),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('LEFTPADDING', (0, 0), (-1, -1), 6),
                ('RIGHTPADDING', (0, 0), (-1, -1), 6),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('BOX', (0, 0), (-1, -1), 1.2, colors.red),
            ]))
            
            story.append(emp_info_table)
            story.append(Spacer(1, 10))
            
            # Helpers
            def section_header_bg(start, end):
                # paint light green band like sample
                return ('BACKGROUND', start, end, colors.lightgreen)
            def amount_yellow(start, end):
                return ('BACKGROUND', start, end, colors.yellow)
            
            # (A) LƯƠNG CƠ BẢN - dùng số ngày thực tế
            work_days_val = self.salary_data.get('work_days', '-')
            basic_data = [
                ['(A) LƯƠNG CƠ BẢN', 'Số ngày làm việc bình thường:', 'Thành tiền (vnđ):'],
                ['', work_days_val, self.format_currency(self.salary_data.get('basic_amount', '-'))]
            ]
            
            basic_table = Table(basic_data, colWidths=[4*cm, 7*cm, 4.5*cm])
            basic_table.setStyle(TableStyle([
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                section_header_bg((0, 0), (0, 1)),
                amount_yellow((1, 2), (1, 2)),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('ALIGN', (0, 0), (0, 1), 'CENTER'),
                ('VALIGN', (0, 0), (0, 1), 'MIDDLE'),
                ('ALIGN', (1, 0), (1, 0), 'LEFT'),
                ('ALIGN', (1, 1), (1, 1), 'RIGHT'),
                ('ALIGN', (2, 0), (2, 0), 'LEFT'),
                ('ALIGN', (2, 0), (2, -1), 'RIGHT'),
                ('LEFTPADDING', (0, 0), (-1, -1), 6),
                ('RIGHTPADDING', (0, 0), (-1, -1), 6),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('SPAN', (0, 0), (1, 0)),
                ('BOX', (0, 0), (-1, -1), 1.2, colors.red),
            ]))
            
            story.append(basic_table)
            story.append(Spacer(1, 8))
            
            # (B) THÊM GIỜ
            overtime_data = [
                ['(B) THÊM GIỜ', 'Loại thêm giờ', 'Số giờ', 'Thành tiền (vnđ)'],
                ['', '150%', self.salary_data.get('overtime_150_hours', '-'), self.format_currency(self.salary_data.get('overtime_150_amount', '-'))],
                ['', '200%', self.salary_data.get('sunday_200_hours', '-'), self.format_currency(self.salary_data.get('sunday_200_amount', '-'))],
                ['', '300%', self.salary_data.get('holiday_300_hours', '-'), self.format_currency(self.salary_data.get('holiday_300_amount', '-'))],
                ['', 'Tổng thu nhập thêm giờ:', '', self.format_currency(self.salary_data.get('total_overtime', '-'))]
            ]
            
            overtime_table = Table(overtime_data, colWidths=[4*cm, 4*cm, 2.5*cm, 5*cm])
            overtime_table.setStyle(TableStyle([
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                section_header_bg((0, 0), (0, 3)),
                ('BACKGROUND', (1, 0), (3, 0), colors.whitesmoke),
                amount_yellow((4, 3), (4, 3)),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('ALIGN', (0, 0), (0, 4), 'CENTER'),
                ('VALIGN', (0, 0), (0, 4), 'MIDDLE'),
                ('ALIGN', (1, 0), (1, -1), 'LEFT'),
                ('ALIGN', (2, 0), (2, -1), 'RIGHT'),
                ('ALIGN', (3, 0), (3, -1), 'RIGHT'),
                ('LEFTPADDING', (0, 0), (-1, -1), 6),
                ('RIGHTPADDING', (0, 0), (-1, -1), 6),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                # Bỏ merge dọc để tránh lỗi span ReportLab
                # ('SPAN', (0, 0), (4, 0)),
                ('BOX', (0, 0), (-1, -1), 1.2, colors.red),
            ]))
            
            story.append(overtime_table)
            story.append(Spacer(1, 8))
            
            # (C) PHỤ CẤP
            allowance_data = [
                ['(C) PHỤ CẤP', 'Loại phụ cấp', 'Số ngày', 'Thành tiền (vnđ)'],
                ['', 'Công trường (W)', self.salary_data.get('work_days', '-'), self.format_currency(self.salary_data.get('work_allowance', '-'))],
                ['', 'Đào tạo (T)', self.salary_data.get('training_days', '-'), self.format_currency(self.salary_data.get('training_allowance', '-'))],
                ['', 'Văn Phòng (O)', self.salary_data.get('office_days', '-'), self.format_currency(self.salary_data.get('office_allowance', '-'))],
                ['', 'Chức danh (hệ số)', self.salary_data.get('position_coefficient', '0.41'), '-'],
                ['', 'Xăng xe', self.salary_data.get('work_days', '-'), self.format_currency(self.salary_data.get('gas_allowance', '-'))],
                ['', 'Điện thoại', self.salary_data.get('work_days', '-'), self.format_currency(self.salary_data.get('phone_allowance', '-'))],
                ['', 'Khách sạn', self.salary_data.get('work_days', '-'), self.format_currency(self.salary_data.get('hotel_allowance', '-'))],
                ['', 'Tổng thu nhập phụ cấp:', '', self.format_currency(self.salary_data.get('total_allowance', '-'))]
            ]
            
            allowance_table = Table(allowance_data, colWidths=[4*cm, 5*cm, 2.5*cm, 5*cm])
            allowance_table.setStyle(TableStyle([
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                section_header_bg((0, 0), (0, 3)),
                ('BACKGROUND', (1, 0), (3, 0), colors.whitesmoke),
                amount_yellow((8, 3), (8, 3)),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('ALIGN', (0, 0), (0, 8), 'CENTER'),
                ('VALIGN', (0, 0), (0, 8), 'MIDDLE'),
                ('ALIGN', (1, 0), (1, -1), 'LEFT'),
                ('ALIGN', (2, 0), (2, -1), 'RIGHT'),
                ('ALIGN', (3, 0), (3, -1), 'RIGHT'),
                ('LEFTPADDING', (0, 0), (-1, -1), 6),
                ('RIGHTPADDING', (0, 0), (-1, -1), 6),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                # Bỏ merge dọc để tránh lỗi span ReportLab
                # ('SPAN', (0, 0), (8, 0)),
                ('BOX', (0, 0), (-1, -1), 1.2, colors.red),
            ]))
            
            story.append(allowance_table)
            story.append(Spacer(1, 8))
            
            # (D) KPI
            kpi_data = [
                ['(D) KPI (NĂNG SUẤT)', 'Số mét vượt', '', 'Thành tiền (vnđ)'],
                ['', 'PAUT', self.salary_data.get('paut_meters', '-'), self.format_currency(self.salary_data.get('paut_amount', '-'))],
                ['', 'UT', self.salary_data.get('tofd_meters', '-'), self.format_currency(self.salary_data.get('tofd_amount', '-'))],
                ['', 'Tổng thu nhập năng suất:', '', self.format_currency(self.salary_data.get('total_kpi', '-'))]
            ]
            
            kpi_table = Table(kpi_data, colWidths=[4*cm, 3*cm, 4*cm, 5*cm])
            kpi_table.setStyle(TableStyle([
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                section_header_bg((0, 0), (0, 3)),
                ('BACKGROUND', (1, 0), (3, 0), colors.whitesmoke),
                amount_yellow((3, 3), (3, 3)),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('ALIGN', (0, 0), (0, 3), 'CENTER'),
                ('VALIGN', (0, 0), (0, 3), 'MIDDLE'),
                # Bỏ merge hàng tiêu đề phụ để an toàn
                # ('SPAN', (1, 0), (2, 0)),
                ('ALIGN', (1, 0), (1, 0), 'CENTER'),
                ('FONTNAME', (1, 0), (2, 0), 'Helvetica'),
                ('ALIGN', (1, 0), (1, -1), 'LEFT'),
                ('ALIGN', (2, 0), (2, -1), 'RIGHT'),
                ('ALIGN', (3, 0), (3, -1), 'RIGHT'),
                ('LEFTPADDING', (0, 0), (-1, -1), 6),
                ('RIGHTPADDING', (0, 0), (-1, -1), 6),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                # Bỏ merge dọc để tránh lỗi span ReportLab
                # ('SPAN', (0, 0), (3, 0)),
                ('BOX', (0, 0), (-1, -1), 1.2, colors.red),
            ]))
            
            story.append(kpi_table)
            story.append(Spacer(1, 8))
            
            # TỔNG CỘNG
            total_data = [
                ['(I) Tổng cộng (vnđ)=(A)+(B)+(C)+(D):', self.format_currency(self.salary_data.get('gross_salary', '-'))]
            ]
            
            total_table = Table(total_data, colWidths=[10*cm, 5*cm])
            total_table.setStyle(TableStyle([
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                amount_yellow((1, 0), (1, 0)),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 11),
                ('ALIGN', (0, 0), (0, 0), 'LEFT'),
                ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('LEFTPADDING', (0, 0), (-1, -1), 6),
                ('RIGHTPADDING', (0, 0), (-1, -1), 6),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('BOX', (0, 0), (-1, -1), 1.2, colors.red),
            ]))
            
            story.append(total_table)
            story.append(Spacer(1, 8))
            
            # (E) CÁC KHOẢN KHẤU TRỪ
            deductions_data = [
                ['(E) CÁC KHOẢN KHẤU TRỪ', 'Hệ số bảo hiểm', 'Thành tiền (vnđ)'],
                ['', '10.50%', self.format_currency(self.salary_data.get('insurance_deduction', '-'))],
                ['', 'Thuế TNCN:', self.format_currency(self.salary_data.get('tax_deduction', '-'))],
                ['', 'Thu nhập chịu thuế:', self.format_currency(self.salary_data.get('taxable_income', '-'))],
                ['', 'Giảm trừ gia cảnh:', self.format_currency(self.salary_data.get('family_deduction', '-'))],
                ['', 'Bậc thuế:', self.salary_data.get('tax_bracket', '-')],
                ['', 'Tạm ứng:', self.format_currency(self.salary_data.get('advance_deduction', '-'))],
                ['', 'Vi phạm:', self.format_currency(self.salary_data.get('other_deduction', '-'))],
                ['', 'Tiền đào tạo (UT ISO):', '-'],
                ['', 'Tổng khấu trừ:', self.format_currency(self.salary_data.get('total_deduction', '-'))]
            ]
            deductions_table = Table(deductions_data, colWidths=[4*cm, 9*cm, 5*cm])
            deductions_table.setStyle(TableStyle([
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                section_header_bg((0, 0), (0, 9)),
                ('BACKGROUND', (1, 0), (2, 0), colors.whitesmoke),
                amount_yellow((9, 2), (9, 2)),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('ALIGN', (0, 0), (0, 9), 'CENTER'),
                ('VALIGN', (0, 0), (0, 9), 'MIDDLE'),
                ('ALIGN', (1, 0), (1, -1), 'LEFT'),
                ('ALIGN', (2, 0), (2, -1), 'RIGHT'),
                ('LEFTPADDING', (0, 0), (-1, -1), 6),
                ('RIGHTPADDING', (0, 0), (-1, -1), 6),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('SPAN', (0, 0), (9, 0)),
                ('BOX', (0, 0), (-1, -1), 1.2, colors.red),
            ]))
            story.append(deductions_table)
            story.append(Spacer(1, 8))
            
            # (F) THANH TOÁN MUA SẮM
            purchases_total = self.format_currency('-')
            purchases_data = [
                ['(F) THANH TOÁN MUA SẮM', purchases_total]
            ]
            purchases_table = Table(purchases_data, colWidths=[10*cm, 5*cm])
            purchases_table.setStyle(TableStyle([
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('ALIGN', (0, 0), (0, 0), 'LEFT'),
                ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
                ('LEFTPADDING', (0, 0), (-1, -1), 6),
                ('RIGHTPADDING', (0, 0), (-1, -1), 6),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('BOX', (0, 0), (-1, -1), 1.2, colors.red),
            ]))
            story.append(purchases_table)
            story.append(Spacer(1, 8))
            
            # THỰC NHẬN (thanh đỏ)
            net_data = [
                ['THỰC NHẬN (VNĐ)=I-E+F:', self.format_currency(self.salary_data.get('net_salary', '-'))]
            ]
            net_table = Table(net_data, colWidths=[10*cm, 5*cm])
            net_table.setStyle(TableStyle([
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('BACKGROUND', (0, 0), (-1, -1), colors.yellow),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.red),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 14),
                ('ALIGN', (0, 0), (0, 0), 'LEFT'),
                ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
                ('LEFTPADDING', (0, 0), (-1, -1), 6),
                ('RIGHTPADDING', (0, 0), (-1, -1), 6),
                ('TOPPADDING', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
                ('BOX', (0, 0), (-1, -1), 1.2, colors.red),
            ]))
            story.append(net_table)
            story.append(Spacer(1, 4))
            
            # Build PDF
            doc.build(story)
            return True
            
        except Exception as e:
            print(f"Lỗi tạo PDF: {e}")
            return False
    
    def convert_pdf_to_image(self, pdf_path):
        """Convert PDF thành ảnh để hiển thị"""
        try:
            if PIL_AVAILABLE:
                # Tạo ảnh từ PDF thật
                self.create_preview_from_pdf(pdf_path)
            else:
                self.create_simple_preview()
        except Exception as e:
            print(f"Lỗi convert PDF: {e}")
            self.create_simple_preview()
    
    def create_preview_from_pdf(self, pdf_path):
        """Tạo preview từ PDF thật với bảng merge cell đẹp"""
        try:
            # Tạm thời tạo ảnh đẹp từ dữ liệu
            width, height = 800, 1200
            img = PILImage.new('RGB', (width, height), 'white')
            draw = ImageDraw.Draw(img)
            
            # Font
            try:
                font_large = ImageFont.truetype("arial.ttf", 18)
                font_medium = ImageFont.truetype("arial.ttf", 14)
                font_small = ImageFont.truetype("arial.ttf", 10)
                font_bold = ImageFont.truetype("arialbd.ttf", 12)
            except:
                font_large = ImageFont.load_default()
                font_medium = ImageFont.load_default()
                font_small = ImageFont.load_default()
                font_bold = ImageFont.load_default()
            
            y = 30
            
            # Header
            # Logo (nếu có)
            try:
                logo_path = "logo_hitech.png"
                if os.path.exists(logo_path):
                    logo_img = PILImage.open(logo_path).convert('RGBA')
                    logo_img = logo_img.resize((80, 80))
                    img.paste(logo_img, (30, y-10), logo_img)
            except Exception as _:
                pass

            draw.text((width//2 - 240, y), "CÔNG TY TNHH DỊCH VỤ KIỂM TRA KHÔNG PHÁ HỦY CÔNG NGHỆ CAO", fill='darkblue', font=font_large)
            y += 40
            draw.text((width//2 - 60, y), "PHIẾU LƯƠNG", fill='darkblue', font=font_large)
            y += 60
            
            # Thông tin nhân viên
            period = self.salary_data.get('period', '-')
            month, year = period.split('/') if '/' in period else ('-', '-')
            
            # Vẽ bảng thông tin nhân viên
            self.draw_merged_table(draw, 20, y, width-40, 80, [
                ['Tháng:', month, 'Năm:', year],
                ['Nhân Viên:', self.salary_data.get('name', 'N/A').upper(), 'Mã số:', self.salary_data.get('msnv', 'N/A')],
                ['Phòng Ban:', self.salary_data.get('department', 'N/A'), 'Chức vụ:', self.salary_data.get('position', 'N/A')]
            ], font_small)
            y += 100
            
            # (A) LƯƠNG CƠ BẢN - Bảng 2x3 với merge cell
            self.draw_merged_table(draw, 20, y, width-40, 60, [
                ['(A) LƯƠNG CƠ BẢN', 'Số ngày làm việc bình thường:', 'Thành tiền (vnđ):'],
                ['', self.salary_data.get('work_days', '-'), self.format_currency(self.salary_data.get('basic_amount', '-'))]
            ], font_small, merge_cells=[(0, 0, 1, 0)], bg_color='lightgreen')
            y += 80
            
            # (B) THÊM GIỜ - Bảng với merge cell
            self.draw_merged_table(draw, 20, y, width-40, 120, [
                ['(B) THÊM GIỜ', 'Loại thêm giờ', 'Số giờ', 'Thành tiền (vnđ)'],
                ['', '150%', self.salary_data.get('overtime_150_hours', '-'), self.format_currency(self.salary_data.get('overtime_150_amount', '-'))],
                ['', '200%', self.salary_data.get('sunday_200_hours', '-'), self.format_currency(self.salary_data.get('sunday_200_amount', '-'))],
                ['', '300%', self.salary_data.get('holiday_300_hours', '-'), self.format_currency(self.salary_data.get('holiday_300_amount', '-'))],
                ['', 'Tổng thu nhập thêm giờ:', '', self.format_currency(self.salary_data.get('total_overtime', '-'))]
            ], font_small, merge_cells=[(0, 0, 4, 0)])
            y += 140
            
            # (C) PHỤ CẤP - Bảng với merge cell
            self.draw_merged_table(draw, 20, y, width-40, 200, [
                ['(C) PHỤ CẤP', 'Loại phụ cấp', 'Số ngày', 'Thành tiền (vnđ)'],
                ['', 'Công trường (W)', self.salary_data.get('work_days', '-'), self.format_currency(self.salary_data.get('work_allowance', '-'))],
                ['', 'Đào tạo (T)', self.salary_data.get('training_days', '-'), self.format_currency(self.salary_data.get('training_allowance', '-'))],
                ['', 'Văn Phòng (O)', self.salary_data.get('office_days', '-'), self.format_currency(self.salary_data.get('office_allowance', '-'))],
                ['', 'Chức danh (hệ số)', self.salary_data.get('position_coefficient', '0.41'), '-'],
                ['', 'Xăng xe', self.salary_data.get('work_days', '-'), self.format_currency(self.salary_data.get('gas_allowance', '-'))],
                ['', 'Điện thoại', self.salary_data.get('work_days', '-'), self.format_currency(self.salary_data.get('phone_allowance', '-'))],
                ['', 'Khách sạn', self.salary_data.get('work_days', '-'), self.format_currency(self.salary_data.get('hotel_allowance', '-'))],
                ['', 'Tổng thu nhập phụ cấp:', '', self.format_currency(self.salary_data.get('total_allowance', '-'))]
            ], font_small, merge_cells=[(0, 0, 8, 0)])
            y += 220
            
            # (D) KPI - Bảng với merge cell
            self.draw_merged_table(draw, 20, y, width-40, 80, [
                ['(D) KPI (NĂNG SUẤT)', 'Số mét vượt', '', 'Thành tiền (vnđ)'],
                ['', 'PAUT', self.salary_data.get('paut_meters', '-'), self.format_currency(self.salary_data.get('paut_amount', '-'))],
                ['', 'UT', self.salary_data.get('tofd_meters', '-'), self.format_currency(self.salary_data.get('tofd_amount', '-'))],
                ['', 'Tổng thu nhập năng suất:', '', self.format_currency(self.salary_data.get('total_kpi', '-'))]
            ], font_small, merge_cells=[(0, 0, 3, 0), (0, 1, 0, 2)], colored_merges=[((0, 0, 3, 0), 'lightgreen')])
            y += 100
            
            # TỔNG CỘNG
            self.draw_merged_table(draw, 20, y, width-40, 40, [
                ['(I) Tổng cộng (vnđ)=(A)+(B)+(C)+(D):', self.format_currency(self.salary_data.get('gross_salary', '-'))]
            ], font_small)
            y += 60
            
            # (E) KHẤU TRỪ - Bảng với merge cell
            self.draw_merged_table(draw, 20, y, width-40, 180, [
                ['(E) CÁC KHOẢN KHẤU TRỪ', 'Hệ số bảo hiểm', 'Thành tiền (vnđ)'],
                ['', '10.50%', self.format_currency(self.salary_data.get('insurance_deduction', '-'))],
                ['', 'Thuế TNCN:', self.format_currency(self.salary_data.get('tax_deduction', '-'))],
                ['', 'Thu nhập chịu thuế:', self.format_currency(self.salary_data.get('taxable_income', '-'))],
                ['', 'Giảm trừ gia cảnh:', self.format_currency(self.salary_data.get('family_deduction', '-'))],
                ['', 'Bậc thuế:', self.salary_data.get('tax_bracket', '-')],
                ['', 'Tạm ứng:', self.format_currency(self.salary_data.get('advance_deduction', '-'))],
                ['', 'Vi phạm:', self.format_currency(self.salary_data.get('other_deduction', '-'))],
                ['', 'Tiền đào tạo (UT ISO):', '-'],
                ['', 'Tổng khấu trừ:', self.format_currency(self.salary_data.get('total_deduction', '-'))]
            ], font_small, merge_cells=[(0, 0, 9, 0)])
            y += 200
            
            # (F) THANH TOÁN MUA SẮM
            self.draw_merged_table(
                draw,
                20,
                y,
                width-40,
                40,
                [['(F) THANH TOÁN MUA SẮM', self.format_currency('-')]],
                font_small,
                merge_cells=[(0, 0, 0, 0)],
                colored_merges=[((0, 0, 0, 0), 'lightgreen')]
            )
            y += 60
            
            # THỰC NHẬN (nền vàng, chữ đỏ, font lớn)
            self.draw_merged_table(
                draw,
                20,
                y,
                width-40,
                40,
                [['THỰC NHẬN (VNĐ)=I-E+F:', self.format_currency(self.salary_data.get('net_salary', '-'))]],
                font_medium,
                merge_cells=None,
                text_color='red',
                colored_merges=[((0, 0, 0, 1), 'yellow')]
            )
            
            # Convert PIL Image to QPixmap
            img_bytes = img.tobytes('raw', 'RGB')
            qimg = QImage(img_bytes, width, height, QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(qimg)
            
            self.preview_label.setPixmap(pixmap.scaled(800, 1200, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            
        except Exception as e:
            print(f"Lỗi tạo preview từ PDF: {e}")
            self.create_simple_preview()
    
    def draw_merged_table(self, draw, x, y, width, height, data, font, merge_cells=None, bg_color='lightgreen', text_color='black', colored_merges=None):
        """Vẽ bảng với merge cell"""
        try:
            rows = len(data)
            cols = len(data[0]) if data else 0
            cell_width = width // cols
            cell_height = height // rows
            
            # Nếu có colored_merges mà không có merge_cells, vẫn cho phép tô nền theo vùng chỉ định
            if (colored_merges and (not merge_cells or len(merge_cells) == 0)):
                for cm, color in colored_merges:
                    sr, sc, er, ec = cm
                    merge_x = x + sc * cell_width
                    merge_y = y + sr * cell_height
                    merge_width = (ec - sc + 1) * cell_width
                    merge_height = (er - sr + 1) * cell_height
                    draw.rectangle([merge_x, merge_y, merge_x + merge_width, merge_y + merge_height], fill=color)
            
            # Vẽ background cho merge cells TRƯỚC, và ghi nhớ vùng merge để bỏ các đường kẻ bên trong
            if merge_cells:
                for merge in merge_cells:
                    start_row, start_col, end_row, end_col = merge
                    merge_x = x + start_col * cell_width
                    merge_y = y + start_row * cell_height
                    merge_width = (end_col - start_col + 1) * cell_width
                    merge_height = (end_row - start_row + 1) * cell_height
                    
                    # Vẽ background
                    fill_color = None
                    if colored_merges:
                        for cm, color in colored_merges:
                            if cm == merge:
                                fill_color = color
                                break
                    else:
                        fill_color = bg_color
                    if fill_color:
                        draw.rectangle([merge_x, merge_y, merge_x + merge_width, merge_y + merge_height], fill=fill_color)
            
            # Vẽ đường kẻ, bỏ các đường kẻ bên trong vùng merge
            def inside_any_merge_line_h(hy):
                if not merge_cells:
                    return False
                for mr in merge_cells:
                    sr, sc, er, ec = mr
                    if sr < er:  # có chiều dọc
                        y1 = y + sr * cell_height
                        y2 = y + (er + 1) * cell_height
                        if y1 < hy < y2:
                            # nếu đường ngang nằm trong cột bị merge, bỏ đoạn từ cột sc đến ec
                            return True
                return False
            def inside_any_merge_line_v(vx):
                if not merge_cells:
                    return False
                for mr in merge_cells:
                    sr, sc, er, ec = mr
                    if sc < ec:
                        x1 = x + sc * cell_width
                        x2 = x + (ec + 1) * cell_width
                        if x1 < vx < x2:
                            return True
                return False

            for i in range(rows + 1):
                hy = y + i * cell_height
                if inside_any_merge_line_h(hy):
                    # vẽ 2 đoạn tách bên ngoài vùng merge
                    for mr in merge_cells or []:
                        sr, sc, er, ec = mr
                        if sr < er and (y + sr * cell_height) < hy < (y + (er + 1) * cell_height):
                            left_x = x
                            right_x = x + cols * cell_width
                            merge_left = x + sc * cell_width
                            merge_right = x + (ec + 1) * cell_width
                            draw.line([left_x, hy, merge_left, hy], fill='black', width=1)
                            draw.line([merge_right, hy, right_x, hy], fill='black', width=1)
                    continue
                draw.line([x, hy, x + width, hy], fill='black', width=1)

            for j in range(cols + 1):
                vx = x + j * cell_width
                if inside_any_merge_line_v(vx):
                    for mr in merge_cells or []:
                        sr, sc, er, ec = mr
                        if sc < ec and (x + sc * cell_width) < vx < (x + (ec + 1) * cell_width):
                            top_y = y
                            bottom_y = y + rows * cell_height
                            merge_top = y + sr * cell_height
                            merge_bottom = y + (er + 1) * cell_height
                            draw.line([vx, top_y, vx, merge_top], fill='black', width=1)
                            draw.line([vx, merge_bottom, vx, bottom_y], fill='black', width=1)
                    continue
                draw.line([vx, y, vx, y + height], fill='black', width=1)
            
            # Vẽ text
            for i, row in enumerate(data):
                for j, cell in enumerate(row):
                    if cell:  # Chỉ vẽ nếu cell không rỗng
                        # Kiểm tra xem cell có bị merge không
                        is_merged = False
                        if merge_cells:
                            for merge in merge_cells:
                                start_row, start_col, end_row, end_col = merge
                                if start_row <= i <= end_row and start_col <= j <= end_col:
                                    is_merged = True
                                    break
                        
                        if not is_merged:  # Chỉ vẽ text nếu cell không bị merge
                            text_x = x + j * cell_width + 5
                            text_y = y + i * cell_height + 5
                            draw.text((text_x, text_y), str(cell), fill=text_color, font=font)
            
            # Vẽ text cho merge cells
            if merge_cells:
                for merge in merge_cells:
                    start_row, start_col, end_row, end_col = merge
                    merge_x = x + start_col * cell_width
                    merge_y = y + start_row * cell_height
                    merge_width = (end_col - start_col + 1) * cell_width
                    merge_height = (end_row - start_row + 1) * cell_height
                    
                    # Lấy text từ cell đầu tiên
                    text = str(data[start_row][start_col])
                    if text:
                        # Căn giữa text trong merge cell
                        text_x = merge_x + merge_width // 2 - len(text) * 3
                        text_y = merge_y + merge_height // 2 - 5
                        draw.text((text_x, text_y), text, fill=text_color, font=font)
                    # Viền ngoài vùng merge: vẽ mảnh để đồng nhất với các ô khác
                    draw.rectangle([merge_x, merge_y, merge_x + merge_width, merge_y + merge_height], outline='black', width=1)
            
        except Exception as e:
            print(f"Lỗi vẽ bảng merge: {e}")
    
    def create_simple_preview(self):
        """Tạo preview đơn giản khi không có ReportLab"""
        try:
            # Tạo ảnh đơn giản với PIL
            if PIL_AVAILABLE:
                width, height = 800, 1000
                img = PILImage.new('RGB', (width, height), 'white')
                draw = ImageDraw.Draw(img)
                
                # Font
                try:
                    font_large = ImageFont.truetype("arial.ttf", 20)
                    font_medium = ImageFont.truetype("arial.ttf", 14)
                    font_small = ImageFont.truetype("arial.ttf", 10)
                except:
                    font_large = ImageFont.load_default()
                    font_medium = ImageFont.load_default()
                    font_small = ImageFont.load_default()
                
                y = 20
                
                # Header
                draw.text((width//2 - 100, y), "CÔNG TY TNHH HITECH NDT", fill='darkblue', font=font_large)
                y += 40
                draw.text((width//2 - 50, y), "PHIẾU LƯƠNG", fill='darkblue', font=font_large)
                y += 60
                
                # Thông tin nhân viên
                period = self.salary_data.get('period', 'N/A')
                month, year = period.split('/') if '/' in period else ('N/A', 'N/A')
                
                info_text = f"Tháng: {month} | Năm: {year} | Nhân viên: {self.salary_data.get('name', 'N/A')}"
                draw.text((20, y), info_text, fill='black', font=font_medium)
                y += 30
                
                info_text2 = f"Mã số: {self.salary_data.get('msnv', 'N/A')} | Phòng ban: {self.salary_data.get('department', 'N/A')}"
                draw.text((20, y), info_text2, fill='black', font=font_medium)
                y += 50
                
                # Các section
                sections = [
                    ("(A) LƯƠNG CƠ BẢN", f"Số ngày: {self.salary_data.get('work_days', 'N/A')} | Thành tiền: {self.format_currency(self.salary_data.get('basic_amount', 'N/A'))}"),
                    ("(B) THÊM GIỜ", f"Tổng: {self.format_currency(self.salary_data.get('total_overtime', 'N/A'))}"),
                    ("(C) PHỤ CẤP", f"Tổng: {self.format_currency(self.salary_data.get('total_allowance', 'N/A'))}"),
                    ("(D) KPI", f"Tổng: {self.format_currency(self.salary_data.get('total_kpi', 'N/A'))}"),
                    ("TỔNG CỘNG", f"{self.format_currency(self.salary_data.get('gross_salary', 'N/A'))}"),
                    ("(E) KHẤU TRỪ", f"Tổng: {self.format_currency(self.salary_data.get('total_deduction', 'N/A'))}"),
                    ("THỰC NHẬN", f"{self.format_currency(self.salary_data.get('net_salary', 'N/A'))}")
                ]
                
                for title, content in sections:
                    draw.text((20, y), title, fill='darkblue', font=font_medium)
                    y += 25
                    draw.text((40, y), content, fill='black', font=font_small)
                    y += 35
                
                # Convert PIL Image to QPixmap
                img_bytes = img.tobytes('raw', 'RGB')
                qimg = QImage(img_bytes, width, height, QImage.Format_RGB888)
                pixmap = QPixmap.fromImage(qimg)
                
                self.preview_label.setPixmap(pixmap.scaled(800, 1000, Qt.KeepAspectRatio, Qt.SmoothTransformation))
                
            else:
                # Fallback: tạo text đơn giản
                text = f"""
                CÔNG TY TNHH HITECH NDT
                PHIẾU LƯƠNG
                
                Tháng: {self.salary_data.get('period', 'N/A')}
                Nhân viên: {self.salary_data.get('name', 'N/A')}
                Mã số: {self.salary_data.get('msnv', 'N/A')}
                
                (A) LƯƠNG CƠ BẢN: {self.format_currency(self.salary_data.get('basic_amount', 'N/A'))}
                (B) THÊM GIỜ: {self.format_currency(self.salary_data.get('total_overtime', 'N/A'))}
                (C) PHỤ CẤP: {self.format_currency(self.salary_data.get('total_allowance', 'N/A'))}
                (D) KPI: {self.format_currency(self.salary_data.get('total_kpi', 'N/A'))}
                
                TỔNG CỘNG: {self.format_currency(self.salary_data.get('gross_salary', 'N/A'))}
                
                (E) KHẤU TRỪ: {self.format_currency(self.salary_data.get('total_deduction', 'N/A'))}
                
                THỰC NHẬN: {self.format_currency(self.salary_data.get('net_salary', 'N/A'))}
                """
                
                self.preview_label.setText(text)
                self.preview_label.setStyleSheet("""
                    QLabel {
                        font-family: 'Courier New', monospace;
                        font-size: 12px;
                        color: black;
                        background-color: white;
                        padding: 20px;
                        border: 2px solid #dee2e6;
                        border-radius: 8px;
                    }
                """)
                
        except Exception as e:
            print(f"Lỗi tạo preview đơn giản: {e}")
            self.preview_label.setText("Không thể tạo preview")
    
    def format_currency(self, value):
        """Format số tiền với dấu phẩy"""
        try:
            if not value or value == '0' or str(value).strip().upper() == 'N/A' or str(value).strip() == '-':
                return '-'
            num = float(str(value).replace(',', '').replace(' ', ''))
            return f"{num:,.0f}"
        except:
            return '-'
    
    def copy_image(self):
        """Copy ảnh vào clipboard"""
        try:
            clipboard = QApplication.clipboard()
            clipboard.setPixmap(self.preview_label.pixmap())
            QMessageBox.information(self, "Thành công", "Đã copy ảnh vào clipboard!")
        except Exception as e:
            QMessageBox.warning(self, "Lỗi", f"Không thể copy ảnh: {e}")
    
    def save_image(self):
        """Lưu ảnh"""
        try:
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Lưu ảnh phiếu lương", 
                f"phieu_luong_{self.salary_data.get('msnv', 'unknown')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png",
                "PNG Files (*.png);;JPEG Files (*.jpg);;All Files (*)"
            )
            
            if file_path:
                self.preview_label.pixmap().save(file_path)
                QMessageBox.information(self, "Thành công", f"Đã lưu ảnh: {file_path}")
        except Exception as e:
            QMessageBox.warning(self, "Lỗi", f"Không thể lưu ảnh: {e}")
    
    def export_pdf(self):
        """Xuất PDF"""
        try:
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Xuất PDF phiếu lương", 
                f"phieu_luong_{self.salary_data.get('msnv', 'unknown')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                "PDF Files (*.pdf);;All Files (*)"
            )
            
            if file_path:
                if REPORTLAB_AVAILABLE:
                    self.create_pdf_report(file_path)
                    QMessageBox.information(self, "Thành công", f"Đã xuất PDF: {file_path}")
                else:
                    QMessageBox.warning(self, "Lỗi", "ReportLab không có sẵn. Cài đặt: pip install reportlab")
        except Exception as e:
            QMessageBox.warning(self, "Lỗi", f"Không thể xuất PDF: {e}")
    
    def print_document(self):
        """In tài liệu"""
        try:
            printer = QPrinter(QPrinter.HighResolution)
            dialog = QPrintDialog(printer, self)
            
            if dialog.exec_() == QPrintDialog.Accepted:
                painter = QPainter(printer)
                if self.preview_label.pixmap():
                    painter.drawPixmap(0, 0, self.preview_label.pixmap())
                painter.end()
                QMessageBox.information(self, "Thành công", "Đã gửi tài liệu đến máy in!")
        except Exception as e:
            QMessageBox.warning(self, "Lỗi", f"Không thể in tài liệu: {e}")
    
    def add_logo_to_pdf(self, story):
        """Thêm logo vào PDF"""
        try:
            # Kiểm tra xem có file logo không
            logo_path = "logo_hitech.png"
            if os.path.exists(logo_path):
                logo = Image(logo_path, width=2*cm, height=2*cm)
                logo.hAlign = 'CENTER'
                story.append(logo)
                story.append(Spacer(1, 10))
            else:
                # Nếu không có logo, dùng text
                story.append(Paragraph("", ParagraphStyle(
                    'Logo',
                    parent=styles['Normal'],
                    fontSize=24,
                    alignment=TA_CENTER,
                    textColor=colors.darkblue
                )))
                story.append(Spacer(1, 5))
        except Exception as e:
            print(f"Lỗi thêm logo: {e}")