#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script test tính toán lương cho 3 nhân viên tháng 08/2025
"""

import json
import os

def test_salary_calculation():
    """Test tính toán lương cho 3 nhân viên"""
    
    # Load dữ liệu quy định lương
    with open("data/quydinh_luong.json", "r", encoding="utf-8") as f:
        quydinh_data = json.load(f)
    
    # Load dữ liệu chấm công
    with open("data/chamcong_3_nhanvien_08_2025.json", "r", encoding="utf-8") as f:
        chamcong_data = json.load(f)
    
    print("=== TEST TÍNH TOÁN LƯƠNG THÁNG 08/2025 ===\n")
    
    # Lấy danh sách nhân viên từ quy định lương
    luong_nv = quydinh_data.get("luong_nv", [])
    
    # Lấy dữ liệu chấm công
    employees = chamcong_data.get("employees", {})
    
    for nv in luong_nv:
        if len(nv) >= 4:
            msnv = nv[0]
            ho_ten = nv[1]
            luong_co_ban_thang = float(nv[3]) if nv[3] else 0
            
            print(f"👤 {ho_ten} ({msnv})")
            print(f"   Lương cơ bản tháng: {luong_co_ban_thang:,} VNĐ")
            
            # Tìm dữ liệu chấm công
            if ho_ten in employees:
                attendance = employees[ho_ten].get("attendance", {})
                summary = attendance.get("summary", {})
                
                total_work_days = summary.get("total_work_days", 0)
                total_office_days = summary.get("total_office_days", 0)
                total_training_days = summary.get("total_training_days", 0)
                total_overtime_hours = summary.get("total_overtime_hours", 0)
                
                # Tính số ngày làm việc thực tế
                total_working_days = total_work_days + total_office_days + total_training_days
                
                # Số ngày làm việc chuẩn tháng 08/2025 (26 ngày)
                working_days_in_month = 26
                
                # Tính lương cơ bản thực tế
                luong_1_ngay = luong_co_ban_thang / working_days_in_month
                luong_co_ban_thuc_te = luong_1_ngay * total_working_days
                
                print(f"   Số ngày làm việc thực tế: {total_working_days} ngày")
                print(f"   Số ngày làm việc chuẩn tháng: {working_days_in_month} ngày")
                print(f"   Lương 1 ngày: {luong_1_ngay:,.0f} VNĐ")
                print(f"   Lương cơ bản thực tế: {luong_co_ban_thuc_te:,.0f} VNĐ")
                print(f"   Thêm giờ: {total_overtime_hours} giờ")
                print()
            else:
                print(f"   ❌ Không tìm thấy dữ liệu chấm công!")
                print()

if __name__ == "__main__":
    test_salary_calculation() 