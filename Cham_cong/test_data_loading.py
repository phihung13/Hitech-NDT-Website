#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script test load dữ liệu chấm công và lương
"""

from data_manager import DataManager

def test_data_loading():
    """Test load dữ liệu"""
    print("=== TEST LOAD DỮ LIỆU ===\n")
    
    # Khởi tạo data manager
    dm = DataManager()
    
    # Load dữ liệu chấm công
    print("1. LOAD DỮ LIỆU CHẤM CÔNG:")
    chamcong_data = dm.load_chamcong()
    print(f"   Kết quả: {len(chamcong_data)} nhân viên")
    if chamcong_data:
        for employee, data in chamcong_data.items():
            print(f"   - {employee}: {list(data.keys())}")
    print()
    
    # Load dữ liệu lương
    print("2. LOAD DỮ LIỆU LƯƠNG:")
    ds_luong, ds_phu_cap = dm.load_quydinh_luong()
    print(f"   Số nhân viên: {len(ds_luong)}")
    print(f"   Số công ty phụ cấp: {len(ds_phu_cap)}")
    
    for i, nv in enumerate(ds_luong):
        if len(nv) >= 4:
            try:
                luong = int(nv[3]) if nv[3] else 0
                print(f"   - {nv[1]} ({nv[0]}): {luong:,} VNĐ")
            except:
                print(f"   - {nv[1]} ({nv[0]}): {nv[3]} VNĐ")
    print()
    
    # Test tìm dữ liệu cho một nhân viên cụ thể
    print("3. TEST TÌM DỮ LIỆU NHÂN VIÊN:")
    test_employee = "Phan Hoàng Diệp"
    
    # Tìm trong dữ liệu lương
    luong_data = None
    for nv in ds_luong:
        if len(nv) >= 2 and nv[1] == test_employee:
            luong_data = nv
            break
    
    if luong_data:
        print(f"   ✅ Tìm thấy lương cho {test_employee}")
        print(f"      MSNV: {luong_data[0]}")
        print(f"      Lương cơ bản: {luong_data[3]:,} VNĐ")
    else:
        print(f"   ❌ Không tìm thấy lương cho {test_employee}")
    
    # Tìm trong dữ liệu chấm công
    if test_employee in chamcong_data:
        print(f"   ✅ Tìm thấy chấm công cho {test_employee}")
        months = list(chamcong_data[test_employee].keys())
        print(f"      Các tháng: {months}")
        
        for month in months:
            month_data = chamcong_data[test_employee][month]
            days_count = len(month_data.get('days_detail', {}))
            print(f"      Tháng {month}: {days_count} ngày")
    else:
        print(f"   ❌ Không tìm thấy chấm công cho {test_employee}")

if __name__ == "__main__":
    test_data_loading() 