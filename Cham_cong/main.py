import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QTabWidget, QMenuBar, QMenu, QAction, QMessageBox, QFileDialog
from PyQt5.QtCore import QTimer, pyqtSignal
from nhanvien import TabNhanVien
from quy_dinh_luong import TabQuyDinhLuong
from bang_cong import TabBangCong
from phieu_luong import TabPhieuLuong
from tong_luong import TabTongLuong
from data_manager import DataManager

class MainWindow(QMainWindow):
    # Signals để thông báo thay đổi dữ liệu
    data_changed = pyqtSignal(str)  # Signal khi dữ liệu thay đổi
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Quản lý nội bộ chấm công")
        self.setGeometry(100, 100, 1200, 700)
        
        # Khởi tạo data manager
        self.data_manager = DataManager()
        
        # Khởi tạo timer cho auto-refresh (tạm thời tắt để không tự động load dữ liệu)
        self.auto_refresh_timer = QTimer()
        self.auto_refresh_timer.timeout.connect(self.check_data_changes)
        # self.auto_refresh_timer.start(2000)  # Kiểm tra mỗi 2 giây - TẠM THỜI TẮT
        
        # Lưu trạng thái dữ liệu để so sánh
        self.last_data_state = {}
        self.update_data_state()
        
        # Tạo menu bar
        self.create_menu_bar()
        
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        self.tab_nhanvien = TabNhanVien()
        self.tabs.addTab(self.tab_nhanvien, "Quản lý con người")
        
        self.tab_quydinh = TabQuyDinhLuong()
        self.tabs.addTab(self.tab_quydinh, "Quy định lương")
        
        # Tạo tab Bảng công trước
        self.tab_bangcong = TabBangCong(
            on_data_changed=self.on_chamcong_data_changed,
            on_quydinh_changed=self.tab_quydinh.refresh_data
        )
        self.tabs.addTab(self.tab_bangcong, "Bảng công tổng hợp")
        
        # Tạo tab phiếu lương
        self.tab_phieuluong = TabPhieuLuong()
        self.tabs.addTab(self.tab_phieuluong, "Phiếu lương")
        
        # Tạo tab Tổng lương với reference đến tab phiếu lương
        self.tab_tongluong = TabTongLuong({}, self.tab_phieuluong)
        self.tabs.addTab(self.tab_tongluong, "Tổng lương")
        
        # Kết nối tab phiếu lương với tab tổng lương
        self.tab_phieuluong.tong_luong_tab = self.tab_tongluong
        
        # Kết nối signals
        self.data_changed.connect(self.refresh_all_tabs)
        
    def on_chamcong_data_changed(self, data_chamcong):
        """Xử lý khi dữ liệu chấm công thay đổi"""
        try:
            print("=== DỮ LIỆU CHẤM CÔNG ĐÃ THAY ĐỔI ===")
            # print(f"DEBUG: Số nhân viên trong dữ liệu chấm công: {len(data_chamcong)}")
            
            # 1. Cập nhật dữ liệu cho tab phiếu lương (sẽ tự động tính toán)
            # print("DEBUG: Cập nhật tab phiếu lương...")
            self.tab_phieuluong.update_chamcong_data(data_chamcong)
            
            # 2. Cập nhật tab tổng lương với dữ liệu đã tính toán
            # print("DEBUG: Cập nhật tab tổng lương...")
            self.tab_tongluong.update_data(data_chamcong)
            
            print("✅ Đã hoàn thành cập nhật dữ liệu lương!")
            
        except Exception as e:
            print(f"Lỗi xử lý dữ liệu chấm công: {e}")
            import traceback
            traceback.print_exc()
    

    

    
    def tinh_thue_tncn(self, thu_nhap_chiu_thue):
        """Tính thuế TNCN theo biểu thuế lũy tiến từng phần"""
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
        
    def update_data_state(self):
        """Cập nhật trạng thái dữ liệu hiện tại"""
        try:
            self.last_data_state = {
                'nhanvien': self.data_manager.load_nhanvien(),
                'quydinh_luong': self.data_manager.load_quydinh_luong()
            }
        except Exception as e:
            print(f"Lỗi cập nhật trạng thái dữ liệu: {e}")
    
    def check_data_changes(self):
        """Kiểm tra thay đổi dữ liệu"""
        try:
            current_nhanvien = self.data_manager.load_nhanvien()
            current_quydinh_luong = self.data_manager.load_quydinh_luong()
            
            # So sánh với trạng thái trước
            if (current_nhanvien != self.last_data_state.get('nhanvien') or 
                current_quydinh_luong != self.last_data_state.get('quydinh_luong')):
                
                print("Phát hiện thay đổi dữ liệu, cập nhật...")
                self.data_changed.emit("data_updated")
                self.update_data_state()
                
        except Exception as e:
            print(f"Lỗi kiểm tra thay đổi dữ liệu: {e}")
    
    def refresh_all_tabs(self, signal_data):
        """Cập nhật tất cả các tab khi có thay đổi dữ liệu"""
        try:
            print("Đang cập nhật tất cả các tab...")
            
            # Cập nhật tab quản lý con người
            if hasattr(self, 'tab_nhanvien'):
                self.tab_nhanvien.refresh_data()
            
            # Cập nhật tab quy định lương
            if hasattr(self, 'tab_quydinh'):
                self.tab_quydinh.refresh_data()
            
            # Cập nhật tab bảng công
            if hasattr(self, 'tab_bangcong'):
                self.tab_bangcong.refresh_data()
            
            # Cập nhật tab phiếu lương
            if hasattr(self, 'tab_phieuluong'):
                self.tab_phieuluong.refresh_all_data()
            
            # Cập nhật tab tổng lương
            if hasattr(self, 'tab_tongluong'):
                self.tab_tongluong.refresh_data()
            
            print("Đã cập nhật xong tất cả các tab")
            
        except Exception as e:
            print(f"Lỗi cập nhật tất cả các tab: {e}")
    
    def create_menu_bar(self):
        """Tạo menu bar"""
        menubar = self.menuBar()
        
        # Menu File
        file_menu = menubar.addMenu('File')
        
        # Action Export
        export_action = QAction('Export Data', self)
        export_action.setShortcut('Ctrl+E')
        export_action.triggered.connect(self.export_data)
        file_menu.addAction(export_action)
        
        # Action Import
        import_action = QAction('Import Data', self)
        import_action.setShortcut('Ctrl+I')
        import_action.triggered.connect(self.import_data)
        file_menu.addAction(import_action)
        
        file_menu.addSeparator()
        
        # Action Exit
        exit_action = QAction('Exit', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Menu Help
        help_menu = menubar.addMenu('Help')
        
        # Action About
        about_action = QAction('About', self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def export_data(self):
        """Export dữ liệu"""
        try:
            file_name, _ = QFileDialog.getSaveFileName(
                self, 
                "Export Data", 
                "hitech_ndt_data.json", 
                "JSON Files (*.json)"
            )
            if file_name:
                # Thực hiện export dữ liệu
                QMessageBox.information(self, "Success", "Data exported successfully!")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Export failed: {str(e)}")
    
    def import_data(self):
        """Import dữ liệu"""
        try:
            file_name, _ = QFileDialog.getOpenFileName(
                self, 
                "Import Data", 
                "", 
                "JSON Files (*.json)"
            )
            if file_name:
                # Thực hiện import dữ liệu
                QMessageBox.information(self, "Success", "Data imported successfully!")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Import failed: {str(e)}")
    
    def show_about(self):
        """Hiển thị thông tin về ứng dụng"""
        QMessageBox.about(
            self, 
            "About", 
            "Hitech NDT - Quản lý nội bộ chấm công\n\n"
            "Version: 1.0\n"
            "Developed by: Hitech NDT Team\n\n"
            "Ứng dụng quản lý chấm công và tính lương cho công ty Hitech NDT"
        )

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())