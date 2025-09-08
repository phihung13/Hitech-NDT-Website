#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script test để kiểm tra việc load dữ liệu chấm công trong TabPhieuLuong
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from phieu_luong import TabPhieuLuong
from PyQt5.QtWidgets import QApplication

def test_load_data():
    """Test load dữ liệu chấm công"""
    app = QApplication(sys.argv)
    
    # Khởi tạo tab phiếu lương
    tab = TabPhieuLuong()
    
    print("=== TEST LOAD DỮ LIỆU ===")
    print(f"Số nhân viên có dữ liệu chấm công: {len(tab.data_chamcong)}")
    print(f"Danh sách nhân viên: {list(tab.data_chamcong.keys())}")
    
    # Test với một nhân viên cụ thể
    if tab.data_chamcong:
        first_employee = list(tab.data_chamcong.keys())[0]
        print(f"\nTest với nhân viên: {first_employee}")
        
        employee_data = tab.data_chamcong[first_employee]
        print(f"Các tháng có dữ liệu: {list(employee_data.keys())}")
        
        if employee_data:
            first_month = list(employee_data.keys())[0]
            month_data = employee_data[first_month]
            print(f"\nDữ liệu tháng {first_month}:")
            print(f"- days_detail: {bool(month_data.get('days_detail', {}))}")
            print(f"- summary: {month_data.get('summary', {})}")
    
    app.quit()

if __name__ == "__main__":
    test_load_data() 