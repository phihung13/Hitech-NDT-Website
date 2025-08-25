#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dialog popup để thêm công ty mới vào quy định phụ cấp công trường
"""

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QPushButton, QMessageBox, QFormLayout
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

class NewCompanyDialog(QDialog):
    def __init__(self, company_name, parent=None):
        super().__init__(parent)
        self.company_name = company_name
        self.result_data = None
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle("Thêm quy định phụ cấp công ty mới")
        self.setFixedSize(400, 200)
        self.setModal(True)
        # Vô hiệu hóa nút X và các phím tắt
        self.setWindowFlags(Qt.Dialog | Qt.WindowStaysOnTopHint | Qt.WindowCloseButtonHint)
        self.setAttribute(Qt.WA_DeleteOnClose, False)
        # Vô hiệu hóa nút X
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowCloseButtonHint)
        
        layout = QVBoxLayout()
        
        # Tiêu đề
        title = QLabel(f"Phát hiện công ty mới: '{self.company_name}'")
        title.setStyleSheet("font-weight: bold; font-size: 14px; color: #2c3e50;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        subtitle = QLabel("Vui lòng nhập thông tin phụ cấp cho công ty này:")
        subtitle.setStyleSheet("font-size: 12px; color: #7f8c8d;")
        subtitle.setAlignment(Qt.AlignCenter)
        layout.addWidget(subtitle)
        
        warning = QLabel("⚠️ Bạn phải điền xong thông tin và bấm Lưu để tiếp tục!")
        warning.setStyleSheet("font-size: 11px; color: #e74c3c; font-weight: bold;")
        warning.setAlignment(Qt.AlignCenter)
        layout.addWidget(warning)
        
        # Form nhập liệu
        form_layout = QFormLayout()
        
        # Tên công ty (đã điền sẵn)
        self.input_company_name = QLineEdit()
        self.input_company_name.setText(self.company_name)
        self.input_company_name.setReadOnly(True)
        self.input_company_name.setStyleSheet("background-color: #ecf0f1;")
        form_layout.addRow("Tên công ty:", self.input_company_name)
        
        # Số lần
        self.input_don_gia_le = QLineEdit()
        self.input_don_gia_le.setPlaceholderText("Nhập số lần...")
        form_layout.addRow("Số lần:", self.input_don_gia_le)
        
        # Chi phí xăng xe
        self.input_chi_phi = QLineEdit()
        self.input_chi_phi.setPlaceholderText("Nhập chi phí xăng xe...")
        form_layout.addRow("Chi phí xăng xe:", self.input_chi_phi)
        
        layout.addLayout(form_layout)
        
        # Nút thao tác
        button_layout = QHBoxLayout()
        
        self.btn_save = QPushButton("Lưu")
        self.btn_save.setStyleSheet("""
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
        self.btn_save.clicked.connect(self.save_company)
        
        # KHÔNG CÓ NÚT HỦY - User phải điền xong mới được thoát
        # self.btn_cancel = QPushButton("Hủy")
        # self.btn_cancel.setStyleSheet("""
        #     QPushButton {
        #         background-color: #e74c3c;
        #         color: white;
        #         border: none;
        #         padding: 8px 16px;
        #         border-radius: 4px;
        #         font-weight: bold;
        #     }
        #     QPushButton:hover {
        #         background-color: #c0392b;
        #     }
        # """)
        # self.btn_cancel.clicked.connect(self.reject)
        
        button_layout.addWidget(self.btn_save)
        # button_layout.addWidget(self.btn_cancel)  # Không có nút hủy
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
        
    def save_company(self):
        """Lưu thông tin công ty mới"""
        don_gia_le = self.input_don_gia_le.text().strip()
        chi_phi = self.input_chi_phi.text().strip()
        
        # Validation
        if not don_gia_le:
            QMessageBox.warning(self, "Thiếu thông tin", "Vui lòng nhập số lần!")
            self.input_don_gia_le.setFocus()
            return
            
        if not chi_phi:
            QMessageBox.warning(self, "Thiếu thông tin", "Vui lòng nhập chi phí xăng xe!")
            self.input_chi_phi.setFocus()
            return
            
        # Kiểm tra định dạng số
        try:
            float(don_gia_le.replace(',', ''))
            float(chi_phi.replace(',', ''))
        except ValueError:
            QMessageBox.warning(self, "Sai định dạng", "Số lần và chi phí phải là số!")
            return
        
        # Lưu kết quả
        self.result_data = {
            'company_name': self.company_name,
            'don_gia_le': don_gia_le,
            'chi_phi': chi_phi
        }
        
        # print(f"Debug: Đã thêm công ty mới - {self.company_name}")
        # print(f"Debug: Đơn giá lệ: {don_gia_le}")
        # print(f"Debug: Chi phí xăng xe: {chi_phi}")
        
        self.accept()
        
    def get_result(self):
        """Lấy kết quả từ dialog"""
        return self.result_data
    
    def closeEvent(self, event):
        """Vô hiệu hóa nút X - không cho phép đóng"""
        event.ignore()
    
    def keyPressEvent(self, event):
        """Vô hiệu hóa phím Escape và Alt+F4"""
        if event.key() == Qt.Key_Escape:
            # Không làm gì - vô hiệu hóa Escape
            event.ignore()
        elif event.key() == Qt.Key_F4 and event.modifiers() == Qt.AltModifier:
            # Không làm gì - vô hiệu hóa Alt+F4
            event.ignore()
        else:
            super().keyPressEvent(event) 