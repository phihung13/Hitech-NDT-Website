import json
import os
from typing import Dict, List, Optional, Tuple

class EmployeeMapper:
    """Quản lý mapping giữa MSNV và tên nhân viên để tránh lỗi so sánh tên"""
    
    def __init__(self):
        self.msnv_to_name: Dict[str, str] = {}  # MSNV -> Tên nhân viên
        self.name_to_msnv: Dict[str, str] = {}  # Tên nhân viên -> MSNV
        self.employee_data: Dict[str, dict] = {}  # MSNV -> Thông tin chi tiết
        
    def load_from_nhanvien_data(self, nhanvien_data: List[List]):
        """Load mapping từ dữ liệu nhân viên"""
        self.msnv_to_name.clear()
        self.name_to_msnv.clear()
        self.employee_data.clear()
        
        for nv in nhanvien_data:
            if len(nv) >= 3:
                name = str(nv[0]).strip()
                msnv = str(nv[2]).strip()
                
                if name and msnv:
                    self.msnv_to_name[msnv] = name
                    self.name_to_msnv[name] = msnv
                    
                    # Lưu thông tin chi tiết
                    self.employee_data[msnv] = {
                        'name': name,
                        'msnv': msnv,
                        'cccd': str(nv[1]) if len(nv) > 1 else '',
                        'phone': str(nv[3]) if len(nv) > 3 else '',
                        'birth_date': str(nv[4]) if len(nv) > 4 else '',
                        'hometown': str(nv[5]) if len(nv) > 5 else '',
                        'position': str(nv[6]) if len(nv) > 6 else '',
                        'department': str(nv[7]) if len(nv) > 7 else '',
                        'education': str(nv[8]) if len(nv) > 8 else '',
                        'certificates': str(nv[9]) if len(nv) > 9 else '',
                        'dependents': str(nv[10]) if len(nv) > 10 else '',
                        'bank_account': str(nv[11]) if len(nv) > 11 else '',
                        'bank_name': str(nv[12]) if len(nv) > 12 else ''
                    }
    
    def get_name_by_msnv(self, msnv: str) -> Optional[str]:
        """Lấy tên nhân viên theo MSNV"""
        return self.msnv_to_name.get(msnv)
    
    def get_msnv_by_name(self, name: str) -> Optional[str]:
        """Lấy MSNV theo tên nhân viên"""
        return self.name_to_msnv.get(name)
    
    def get_employee_info(self, msnv: str) -> Optional[dict]:
        """Lấy thông tin chi tiết nhân viên theo MSNV"""
        return self.employee_data.get(msnv)
    
    def get_all_msnv(self) -> List[str]:
        """Lấy danh sách tất cả MSNV"""
        return list(self.msnv_to_name.keys())
    
    def get_all_names(self) -> List[str]:
        """Lấy danh sách tất cả tên nhân viên"""
        return list(self.name_to_msnv.keys())
    
    def find_employee_by_name_fuzzy(self, search_name: str) -> Optional[str]:
        """Tìm MSNV theo tên nhân viên (fuzzy search)"""
        search_name = search_name.strip().lower()
        
        # Tìm chính xác trước
        for name, msnv in self.name_to_msnv.items():
            if name.lower() == search_name:
                return msnv
        
        # Tìm gần đúng
        for name, msnv in self.name_to_msnv.items():
            name_lower = name.lower()
            if (search_name in name_lower or 
                name_lower in search_name or
                self._similar_names(search_name, name_lower)):
                return msnv
        
        return None
    
    def _similar_names(self, name1: str, name2: str) -> bool:
        """Kiểm tra tên tương tự (bỏ qua dấu, thứ tự từ)"""
        # Loại bỏ dấu và chuyển về chữ thường
        def normalize_name(name: str) -> str:
            import unicodedata
            # Loại bỏ dấu
            name = unicodedata.normalize('NFD', name)
            name = ''.join(c for c in name if not unicodedata.combining(c))
            # Chuyển về chữ thường và loại bỏ khoảng trắng thừa
            name = ' '.join(name.lower().split())
            return name
        
        norm1 = normalize_name(name1)
        norm2 = normalize_name(name2)
        
        # So sánh từng từ
        words1 = set(norm1.split())
        words2 = set(norm2.split())
        
        # Nếu có ít nhất 2 từ giống nhau
        return len(words1.intersection(words2)) >= 2
    
    def save_mapping(self, file_path: str = "data/employee_mapping.json"):
        """Lưu mapping vào file"""
        try:
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            data = {
                'msnv_to_name': self.msnv_to_name,
                'name_to_msnv': self.name_to_msnv,
                'employee_data': self.employee_data
            }
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Lỗi lưu mapping: {e}")
    
    def load_mapping(self, file_path: str = "data/employee_mapping.json"):
        """Load mapping từ file"""
        try:
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.msnv_to_name = data.get('msnv_to_name', {})
                    self.name_to_msnv = data.get('name_to_msnv', {})
                    self.employee_data = data.get('employee_data', {})
        except Exception as e:
            print(f"Lỗi load mapping: {e}")
    
    def update_employee(self, msnv: str, name: str, info: dict = None):
        """Cập nhật thông tin nhân viên"""
        old_name = self.msnv_to_name.get(msnv)
        
        # Xóa mapping cũ
        if old_name and old_name in self.name_to_msnv:
            del self.name_to_msnv[old_name]
        
        # Thêm mapping mới
        self.msnv_to_name[msnv] = name
        self.name_to_msnv[name] = msnv
        
        # Cập nhật thông tin chi tiết
        if info:
            self.employee_data[msnv] = info
        elif msnv in self.employee_data:
            self.employee_data[msnv]['name'] = name
    
    def remove_employee(self, msnv: str):
        """Xóa nhân viên khỏi mapping"""
        name = self.msnv_to_name.get(msnv)
        if name:
            del self.msnv_to_name[msnv]
            if name in self.name_to_msnv:
                del self.name_to_msnv[name]
        if msnv in self.employee_data:
            del self.employee_data[msnv] 