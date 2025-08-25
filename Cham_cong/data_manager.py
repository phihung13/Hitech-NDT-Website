import json
import os
from datetime import datetime

class DataManager:
    def __init__(self):
        self.data_dir = "data"
        self.ensure_data_directory()
        
        # Đường dẫn các file dữ liệu (chỉ 2 module cố định)
        self.nhanvien_file = os.path.join(self.data_dir, "nhanvien.json")
        self.quydinh_file = os.path.join(self.data_dir, "quydinh_luong.json")
        self.chamcong_file = os.path.join(self.data_dir, "chamcong_3_nhanvien_08_2025.json")
        
    def ensure_data_directory(self):
        """Tạo thư mục data nếu chưa có"""
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
    
    def save_nhanvien(self, ds_nhanvien):
        """Lưu danh sách nhân viên"""
        data = {
            "timestamp": datetime.now().isoformat(),
            "total_records": len(ds_nhanvien),
            "data": ds_nhanvien
        }
        self._save_data(self.nhanvien_file, data)
    
    def load_nhanvien(self):
        """Tải danh sách nhân viên"""
        data = self._load_data(self.nhanvien_file)
        if data:
            ds_nhanvien = data.get("data", [])
            # Tương thích dữ liệu cũ: thêm cột "Phòng ban" nếu thiếu
            updated_data = []
            for nv in ds_nhanvien:
                if isinstance(nv, list):
                    if len(nv) == 12:  # Dữ liệu cũ (12 cột)
                        # Thêm "Phòng ban" trống ở vị trí index 7 (sau "Chức vụ")
                        new_nv = nv[:7] + [""] + nv[7:]
                        updated_data.append(new_nv)
                    elif len(nv) >= 13:  # Dữ liệu mới (13 cột trở lên)
                        updated_data.append(nv[:13])  # Chỉ lấy 13 cột đầu
                    else:
                        # Dữ liệu thiếu, bổ sung đến 13 cột
                        while len(nv) < 13:
                            nv.append("")
                        updated_data.append(nv)
                else:
                    updated_data.append(nv)
            return updated_data
        return []
    
    def save_quydinh_luong(self, ds_luong_nv, ds_phu_cap_ct):
        """Lưu quy định lương"""
        data = {
            "timestamp": datetime.now().isoformat(),
            "luong_nv": ds_luong_nv,
            "phu_cap_ct": ds_phu_cap_ct
        }
        self._save_data(self.quydinh_file, data)
    
    def load_quydinh_luong(self):
        """Tải quy định lương"""
        data = self._load_data(self.quydinh_file)
        if data:
            return data.get("luong_nv", []), data.get("phu_cap_ct", [])
        return [], []
    
    def save_chamcong(self, chamcong_data):
        """Lưu dữ liệu chấm công"""
        data = {
            "timestamp": datetime.now().isoformat(),
            "chamcong_data": chamcong_data
        }
        self._save_data(self.chamcong_file, data)
    
    def load_chamcong(self):
        """Tải dữ liệu chấm công"""
        data = self._load_data(self.chamcong_file)
        if data:
            print(f"📁 LOAD CHẤM CÔNG từ: {self.chamcong_file}")
            chamcong_data = {}
            
            # Kiểm tra format dữ liệu
            if "employees" in data:
                # Format từ website (mới)
                print("✅ Phát hiện format website")
                employees_data = data.get("employees", {})
                export_info = data.get("export_info", {})
                month_year = export_info.get("period", "08/2025")  # Lấy từ export_info.period
                
                print(f"📅 Tháng/năm: {month_year}")
                print(f"👥 Số nhân viên: {len(employees_data)}")
                
                for msnv, employee_info in employees_data.items():
                    employee_name = employee_info.get("info", {}).get("name", "")
                    if employee_name:
                        # Tạo cấu trúc dữ liệu theo format mong đợi
                        chamcong_data[employee_name] = {
                            month_year: {
                                "days_detail": employee_info.get("attendance", {}).get("days", {}),
                                "summary": employee_info.get("attendance", {}).get("summary", {})
                            }
                        }
                        print(f"   ✅ Loaded {employee_name} for {month_year}")
            
            elif "chamcong_data" in data:
                # Format từ ứng dụng desktop (cũ) 
                print("⚠️ Phát hiện format desktop cũ")
                chamcong_data = data.get("chamcong_data", {})
            
            else:
                # Format trực tiếp (có thể từ export khác)
                print("⚠️ Phát hiện format trực tiếp")
                chamcong_data = data
             
            print(f"✅ Đã load {len(chamcong_data)} nhân viên")
            print(f"   Danh sách: {list(chamcong_data.keys())}")
            return chamcong_data
        print("❌ Không có dữ liệu chấm công")
        return {}

    def _save_data(self, file_path, data):
        """Lưu dữ liệu vào file JSON"""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"Lỗi lưu file {file_path}: {e}")
            return False
    
    def _load_data(self, file_path):
        """Tải dữ liệu từ file JSON"""
        try:
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Lỗi tải file {file_path}: {e}")
        return None
    
    def backup_all_data(self, backup_dir="backup"):
        """Tạo backup toàn bộ dữ liệu"""
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = os.path.join(backup_dir, f"backup_{timestamp}")
        os.makedirs(backup_path)
        
        # Copy file dữ liệu cố định
        files_to_backup = [
            self.nhanvien_file,
            self.quydinh_file,
            self.chamcong_file
        ]
        
        for file_path in files_to_backup:
            if os.path.exists(file_path):
                import shutil
                filename = os.path.basename(file_path)
                backup_file = os.path.join(backup_path, filename)
                shutil.copy2(file_path, backup_file)
        
        return backup_path
    
    def restore_from_backup(self, backup_path):
        """Khôi phục dữ liệu từ backup"""
        if not os.path.exists(backup_path):
            return False
        
        try:
            import shutil
            files_to_restore = [
                "nhanvien.json",
                "quydinh_luong.json",
                "chamcong_3_nhanvien.json"
            ]
            
            for filename in files_to_restore:
                backup_file = os.path.join(backup_path, filename)
                if os.path.exists(backup_file):
                    target_file = os.path.join(self.data_dir, filename)
                    shutil.copy2(backup_file, target_file)
            
            return True
        except Exception as e:
            print(f"Lỗi khôi phục backup: {e}")
            return False
    
    def get_data_info(self):
        """Lấy thông tin về dữ liệu hiện tại"""
        info = {}
        files = [
            ("nhanvien", self.nhanvien_file),
            ("quydinh_luong", self.quydinh_file),
            ("chamcong", self.chamcong_file)
        ]
        
        for name, file_path in files:
            if os.path.exists(file_path):
                try:
                    data = self._load_data(file_path)
                    if data:
                        info[name] = {
                            "exists": True,
                            "timestamp": data.get("timestamp", "Unknown"),
                            "records": data.get("total_records", 0)
                        }
                    else:
                        info[name] = {"exists": False}
                except:
                    info[name] = {"exists": False}
            else:
                info[name] = {"exists": False}
        
        return info 