from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QHeaderView, QGroupBox, QHBoxLayout, QSizePolicy, QFrame, QPushButton, QScrollArea
from PyQt5.QtGui import QFont, QColor, QIcon
from PyQt5.QtCore import Qt
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import numpy as np
from data_manager import DataManager
import json
import os

class TabTongLuong(QWidget):
    def __init__(self, data_chamcong=None, phieu_luong_tab=None):
        super().__init__()
        self.data_chamcong = data_chamcong if data_chamcong is not None else {}
        self.phieu_luong_tab = phieu_luong_tab  # Reference đến tab phiếu lương
        self.data_manager = DataManager()
        
        # Dữ liệu lương thực tế từ phiếu lương
        self.salary_data_file = "data/salary_data.json"
        self.salary_data = self.load_salary_data()
        
        self.init_ui()

    def init_ui(self):
        # Layout chính
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(10, 10, 10, 10)

        # Tiêu đề nổi bật (cố định ở trên)
        title = QLabel("TỔNG CHI PHÍ TIỀN LƯƠNG THÁNG 08.2025")
        title.setFont(QFont("Times New Roman", 22, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: #007bff; margin-bottom: 10px; padding: 10px; background: white; border-radius: 8px;")
        main_layout.addWidget(title)

        # Tạo Scroll Area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background: transparent;
            }
            QScrollBar:vertical {
                background: #f0f0f0;
                width: 12px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background: #c0c0c0;
                border-radius: 6px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background: #a0a0a0;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
            QScrollBar:horizontal {
                background: #f0f0f0;
                height: 12px;
                border-radius: 6px;
            }
            QScrollBar::handle:horizontal {
                background: #c0c0c0;
                border-radius: 6px;
                min-width: 20px;
            }
            QScrollBar::handle:horizontal:hover {
                background: #a0a0a0;
            }
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
                width: 0px;
            }
        """)

        # Widget chứa nội dung có thể cuộn
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setSpacing(18)
        scroll_layout.setContentsMargins(20, 20, 20, 20)

        # Thông báo trạng thái
        self.status_label = QLabel("📋 Chưa có dữ liệu lương thực tế. Vui lòng tính toán lương trong tab Phiếu lương trước.")
        self.status_label.setFont(QFont("Times New Roman", 12))
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("color: #6c757d; padding: 10px; background: #f8f9fa; border-radius: 8px;")
        scroll_layout.addWidget(self.status_label)



        # Bảng tổng hợp lương
        group = QGroupBox()
        group.setStyleSheet("""
            QGroupBox {
                border: none;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #f8f9fa, stop:1 #e3f2fd);
                border-radius: 12px;
                margin-top: 10px;
            }
        """)
        group_layout = QVBoxLayout(group)
        
        self.table = QTableWidget()
        self.table.setFont(QFont("Times New Roman", 12))
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["SỐ TT", "NHÂN VIÊN", "MSNV", "TIỀN LƯƠNG/THÁNG (VNĐ)", "TRẠNG THÁI"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        # Thiết lập chiều cao hàng và header
        self.table.verticalHeader().setDefaultSectionSize(40)  # Chiều cao mỗi hàng
        self.table.verticalHeader().setVisible(False)  # Ẩn số thứ tự hàng
        header_height = 50  # Chiều cao header
        self.table.horizontalHeader().setFixedHeight(header_height)
        self.table.setStyleSheet("""
            QTableWidget {
                background: transparent;
                border: none;
                font-size: 15px;
            }
            QHeaderView::section {
                background: #7fff00;
                color: #222;
                font-size: 15px;
                border-radius: 0px;
                padding: 10px 0px;
                font-weight: bold;
            }
            QTableWidget::item {
                background: transparent;
                border: none;
                padding: 8px 0px;
            }
        """)
        group_layout.addWidget(self.table)
        
        # Dòng tổng chi
        self.tong_chi_label = QLabel()
        self.tong_chi_label.setFont(QFont("Times New Roman", 14, QFont.Bold))
        self.tong_chi_label.setAlignment(Qt.AlignRight)
        self.tong_chi_label.setStyleSheet("color: #e83e8c; padding: 8px 12px;")
        group_layout.addWidget(self.tong_chi_label)
        scroll_layout.addWidget(group)

        # Thống kê tổng hợp
        summary_group = QGroupBox("📈 Thống kê tổng hợp")
        summary_group.setStyleSheet("""
            QGroupBox {
                border: 2px solid #ffc107;
                border-radius: 8px;
                background: white;
                font-weight: bold;
                color: #856404;
            }
        """)
        summary_layout = QHBoxLayout(summary_group)
        
        self.summary_labels = {}
        summary_items = [
            ("Tổng nhân viên", "0"),
            ("Tổng lương cơ bản", "0 VNĐ"),
            ("Tổng phụ cấp", "0 VNĐ"),
            ("Tổng thêm giờ", "0 VNĐ"),
            ("Tổng KPI", "0 VNĐ"),
            ("Tổng thực nhận", "0 VNĐ")
        ]
        
        for label_text, value_text in summary_items:
            item_frame = QFrame()
            item_frame.setStyleSheet("border: 1px solid #dee2e6; border-radius: 6px; padding: 8px;")
            item_layout = QVBoxLayout(item_frame)
            
            label = QLabel(label_text)
            label.setFont(QFont("Times New Roman", 10))
            label.setAlignment(Qt.AlignCenter)
            label.setStyleSheet("color: #6c757d;")
            
            value = QLabel(value_text)
            value.setFont(QFont("Times New Roman", 12, QFont.Bold))
            value.setAlignment(Qt.AlignCenter)
            value.setStyleSheet("color: #007bff;")
            
            item_layout.addWidget(label)
            item_layout.addWidget(value)
            summary_layout.addWidget(item_frame)
            
            self.summary_labels[label_text] = value
        
        scroll_layout.addWidget(summary_group)

        # Biểu đồ cột - Hàng riêng, full width
        bar_group = QGroupBox("📊 Biểu đồ cột lương nhân viên")
        bar_group.setStyleSheet("""
            QGroupBox {
                border: 2px solid #007bff;
                border-radius: 12px;
                background: white;
                font-weight: bold;
                color: #007bff;
                margin-top: 10px;
                padding: 15px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 10px 0 10px;
                font-size: 14px;
            }
        """)
        bar_layout = QVBoxLayout(bar_group)
        bar_layout.setContentsMargins(10, 20, 10, 10)
        bar_layout.setSpacing(10)
        
        self.bar_canvas = FigureCanvas(plt.Figure(figsize=(12, 7)))
        self.bar_canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.bar_canvas.setMinimumHeight(500)
        bar_layout.addWidget(self.bar_canvas)
        
        scroll_layout.addWidget(bar_group)

        # Biểu đồ tròn - Hàng riêng, full width
        pie_group = QGroupBox("🥧 Phân bổ chi phí lương")
        pie_group.setStyleSheet("""
            QGroupBox {
                border: 2px solid #28a745;
                border-radius: 12px;
                background: white;
                font-weight: bold;
                color: #28a745;
                margin-top: 10px;
                padding: 15px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 10px 0 10px;
                font-size: 14px;
            }
        """)
        pie_layout = QVBoxLayout(pie_group)
        pie_layout.setContentsMargins(10, 20, 10, 10)
        pie_layout.setSpacing(10)
        
        self.pie_canvas = FigureCanvas(plt.Figure(figsize=(12, 6)))
        self.pie_canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.pie_canvas.setMinimumHeight(400)
        pie_layout.addWidget(self.pie_canvas)
        
        scroll_layout.addWidget(pie_group)
        
        # Thêm scroll content vào scroll area
        scroll_area.setWidget(scroll_content)
        
        # Thêm scroll area vào main layout
        main_layout.addWidget(scroll_area)

        # Panel nút thao tác
        action_panel = QHBoxLayout()
        action_panel.setSpacing(10)
        action_panel.setContentsMargins(0, 10, 0, 0)
        
        # Nút xóa hết dữ liệu
        self.btn_xoa_du_lieu = QPushButton("🗑️ Xóa hết dữ liệu")
        self.btn_xoa_du_lieu.setFont(QFont("Times New Roman", 12, QFont.Bold))
        self.btn_xoa_du_lieu.setStyleSheet("""
            QPushButton {
                background: linear-gradient(135deg, #dc3545, #c82333);
                color: black;
                border: none;
                border-radius: 8px;
                padding: 12px 24px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: linear-gradient(135deg, #c82333, #bd2130);
                transform: translateY(-2px);
            }
            QPushButton:pressed {
                background: linear-gradient(135deg, #bd2130, #a71e2a);
            }
        """)
        self.btn_xoa_du_lieu.clicked.connect(self.xoa_het_du_lieu)

        delete_box = QVBoxLayout()
        delete_box.setSpacing(4)
        delete_box.setAlignment(Qt.AlignHCenter)
        delete_box.addWidget(self.btn_xoa_du_lieu)

        red_bar = QWidget()
        red_bar.setFixedHeight(15)
        red_bar.setStyleSheet("background-color: #dc3545; border-radius: 3px;")
        delete_box.addWidget(red_bar)

        action_panel.addLayout(delete_box)
        
        # Thêm spacing để căn phải
        action_panel.addStretch()
        
        main_layout.addLayout(action_panel)
        
        # Cập nhật dữ liệu ban đầu
        self.update_display()

    def load_salary_data(self):
        """Tải dữ liệu lương thực tế từ file"""
        try:
            if os.path.exists(self.salary_data_file):
                with open(self.salary_data_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            print(f"Lỗi tải dữ liệu lương: {e}")
            return {}

    def save_salary_data(self):
        """Lưu dữ liệu lương thực tế vào file"""
        try:
            os.makedirs(os.path.dirname(self.salary_data_file), exist_ok=True)
            with open(self.salary_data_file, 'w', encoding='utf-8') as f:
                json.dump(self.salary_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Lỗi lưu dữ liệu lương: {e}")

    def add_salary_data(self, employee_name, salary_info):
        """Thêm dữ liệu lương thực tế cho một nhân viên"""
        print(f"=== THÊM DỮ LIỆU LƯƠNG CHO {employee_name} ===")
        print(f"Debug: salary_info = {salary_info}")
        self.salary_data[employee_name] = salary_info
        self.save_salary_data()
        self.update_display()

    def xoa_het_du_lieu(self):
        """Xóa hết dữ liệu lương"""
        try:
            # Xóa dữ liệu trong memory
            self.salary_data = {}
            
            # Xóa file dữ liệu
            if os.path.exists(self.salary_data_file):
                os.remove(self.salary_data_file)
                print(f"Đã xóa file: {self.salary_data_file}")
            
            # Cập nhật giao diện
            self.update_display()
            
            # Cập nhật thông báo trạng thái
            self.status_label.setText("🗑️ Đã xóa hết dữ liệu lương")
            self.status_label.setStyleSheet("color: #dc3545; padding: 10px; background: #f8d7da; border-radius: 8px;")
            
            print("=== ĐÃ XÓA HẾT DỮ LIỆU LƯƠNG ===")
            
        except Exception as e:
            print(f"Lỗi khi xóa dữ liệu: {e}")

    def refresh_data(self):
        """Làm mới dữ liệu từ file"""
        self.salary_data = self.load_salary_data()
        self.update_display()
        
        if self.salary_data:
            self.status_label.setText(f"✅ Đã tải {len(self.salary_data)} bản ghi lương thực tế")
            self.status_label.setStyleSheet("color: #28a745; padding: 10px; background: #d4edda; border-radius: 8px;")
        else:
            self.status_label.setText("📋 Chưa có dữ liệu lương thực tế. Vui lòng tính toán lương trong tab Phiếu lương trước.")
            self.status_label.setStyleSheet("color: #6c757d; padding: 10px; background: #f8f9fa; border-radius: 8px;")

    def update_display(self):
        """Cập nhật hiển thị bảng và biểu đồ"""
        print("=== CẬP NHẬT HIỂN THỊ TỔNG LƯƠNG ===")
        print(f"Debug: salary_data = {self.salary_data}")
        if not self.salary_data:
            print("Debug: Không có dữ liệu lương")
            self.table.setRowCount(0)
            self.tong_chi_label.setText("<b>TỔNG CHI (VNĐ):</b> <span style='color:red; font-weight:bold;'>0</span>")
            self.update_empty_charts()
            self.update_empty_summary()
            return

        # Cập nhật bảng
        employees = list(self.salary_data.keys())
        self.table.setRowCount(len(employees))
        
        # Tự động điều chỉnh chiều cao bảng dựa trên số lượng nhân viên
        self.adjust_table_height(len(employees))
        
        total_thuc_nhan = 0
        total_luong_co_ban = 0
        total_phu_cap = 0
        total_them_gio = 0
        total_kpi = 0
        
        bar_names = []
        bar_values = []
        pie_values = [0, 0, 0, 0, 0, 0, 0, 0]  # Lương cơ bản, Phụ cấp, Thêm giờ, KPI, Bảo hiểm, Thuế TNCN, Tạm ứng/Vi phạm, Thực nhận
        
        for row, emp in enumerate(employees):
            salary_info = self.salary_data[emp]
            
            # Lấy dữ liệu
            msnv = salary_info.get('msnv', '')
            thuc_nhan = salary_info.get('thuc_nhan', 0)
            luong_co_ban = salary_info.get('luong_co_ban', 0)
            tong_phu_cap = salary_info.get('tong_phu_cap', 0)
            tong_them_gio = salary_info.get('tong_them_gio', 0)
            tong_kpi = salary_info.get('tong_kpi', 0)
            bao_hiem = salary_info.get('bao_hiem', 0)
            thue_tncn = salary_info.get('thue_tncn', 0)
            tam_ung = salary_info.get('tam_ung', 0)
            vi_pham = salary_info.get('vi_pham', 0)
            
            # Cập nhật tổng
            total_thuc_nhan += thuc_nhan
            total_luong_co_ban += luong_co_ban
            total_phu_cap += tong_phu_cap
            total_them_gio += tong_them_gio
            total_kpi += tong_kpi
            
            # Số TT
            item_stt = QTableWidgetItem(str(row+1))
            item_stt.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, 0, item_stt)
            
            # Nhân viên
            item_name = QTableWidgetItem(emp)
            item_name.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            self.table.setItem(row, 1, item_name)
            
            # MSNV
            item_msnv = QTableWidgetItem(msnv)
            item_msnv.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, 2, item_msnv)
            
            # Tiền lương/tháng
            item_luong = QTableWidgetItem(f"{thuc_nhan:,.0f}")
            item_luong.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.table.setItem(row, 3, item_luong)
            
            # Trạng thái
            status = "✅ Đã tính toán"
            item_status = QTableWidgetItem(status)
            item_status.setTextAlignment(Qt.AlignCenter)
            item_status.setForeground(QColor("#28a745"))
            self.table.setItem(row, 4, item_status)
            
            # Dữ liệu cho biểu đồ
            bar_names.append(emp)
            bar_values.append(thuc_nhan)
            
            # Cập nhật dữ liệu biểu đồ tròn
            pie_values[0] += luong_co_ban
            pie_values[1] += tong_phu_cap
            pie_values[2] += tong_them_gio
            pie_values[3] += tong_kpi
            pie_values[4] += bao_hiem
            pie_values[5] += thue_tncn
            pie_values[6] += tam_ung + vi_pham
            pie_values[7] += thuc_nhan

        # Cập nhật tổng chi
        self.tong_chi_label.setText(f"<b>TỔNG CHI (VNĐ):</b> <span style='color:red; font-weight:bold;'>{total_thuc_nhan:,.0f}</span>")
        
        # Cập nhật biểu đồ
        self.update_bar_chart(bar_names, bar_values)
        self.update_pie_chart(pie_values)
        
        # Cập nhật thống kê
        self.update_summary(len(employees), total_luong_co_ban, total_phu_cap, total_them_gio, total_kpi, total_thuc_nhan)

    def update_empty_charts(self):
        """Cập nhật biểu đồ khi không có dữ liệu"""
        # Biểu đồ cột trống
        self.bar_canvas.figure.clear()
        ax = self.bar_canvas.figure.add_subplot(111)
        ax.text(0.5, 0.5, 'Chưa có dữ liệu lương\nVui lòng tính toán lương trong tab Phiếu lương', 
               ha='center', va='center', transform=ax.transAxes, 
               fontsize=16, fontweight='bold', color='#7f8c8d',
               bbox=dict(boxstyle="round,pad=0.3", facecolor='#ecf0f1', alpha=0.8))
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.axis('off')
        self.bar_canvas.figure.patch.set_facecolor('#f8f9fa')
        self.bar_canvas.draw()
        
        # Biểu đồ tròn trống
        self.pie_canvas.figure.clear()
        ax = self.pie_canvas.figure.add_subplot(111)
        ax.text(0.5, 0.5, 'Chưa có dữ liệu lương\nVui lòng tính toán lương trong tab Phiếu lương', 
               ha='center', va='center', transform=ax.transAxes, 
               fontsize=16, fontweight='bold', color='#7f8c8d',
               bbox=dict(boxstyle="round,pad=0.3", facecolor='#ecf0f1', alpha=0.8))
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.axis('off')
        self.pie_canvas.figure.patch.set_facecolor('#f8f9fa')
        self.pie_canvas.draw()

    def update_bar_chart(self, names, values):
        """Cập nhật biểu đồ cột"""
        print(f"=== CẬP NHẬT BIỂU ĐỒ CỘT ===")
        print(f"Debug: names = {names}")
        print(f"Debug: values = {values}")
        self.bar_canvas.figure.clear()
        ax = self.bar_canvas.figure.add_subplot(111)
        
        # Tạo màu gradient đẹp
        colors = plt.cm.viridis(np.linspace(0, 1, len(names)))
        bars = ax.bar(range(len(names)), values, color=colors, alpha=0.8, edgecolor='white', linewidth=2)
        
        # Thêm khoảng trống phía trên để tránh đè chữ
        if len(values) > 0:
            ymax = max(values)
            ax.set_ylim(0, ymax * 1.2)
        
        # Thêm giá trị trên cột với format đẹp
        for bar, value in zip(bars, values):
            height = bar.get_height()
            if height > 0:
                ax.text(bar.get_x() + bar.get_width()/2., height + max(height*0.03, ymax*0.02),
                       f'{value:,.0f}', ha='center', va='bottom', 
                       fontsize=11, fontweight='bold', color='#2c3e50')
        
        # Cải thiện style
        ax.set_xlabel('Nhân viên', fontsize=14, fontweight='bold', color='#2c3e50')
        ax.set_ylabel('Lương (VNĐ)', fontsize=14, fontweight='bold', color='#2c3e50')
        ax.set_title('Biểu đồ lương nhân viên', fontsize=16, fontweight='bold', color='#2c3e50', pad=20)
        ax.set_xticks(range(len(names)))
        ax.set_xticklabels(names, rotation=45, ha='right', fontsize=12, fontweight='bold')
        
        # Grid và background
        ax.grid(True, alpha=0.3, linestyle='--', color='#bdc3c7')
        ax.set_facecolor('#f8f9fa')
        self.bar_canvas.figure.patch.set_facecolor('#f8f9fa')
        
        # Thêm border cho biểu đồ
        for spine in ax.spines.values():
            spine.set_color('#bdc3c7')
            spine.set_linewidth(1.5)
        
        self.bar_canvas.figure.tight_layout()
        self.bar_canvas.draw()

    def update_pie_chart(self, values):
        """Cập nhật biểu đồ tròn"""
        print(f"=== CẬP NHẬT BIỂU ĐỒ TRÒN ===")
        print(f"Debug: values = {values}")
        self.pie_canvas.figure.clear()
        ax = self.pie_canvas.figure.add_subplot(111)
        
        labels = ['Lương cơ bản', 'Phụ cấp', 'Thêm giờ', 'KPI', 'Bảo hiểm', 'Thuế TNCN', 'Tạm ứng/Vi phạm', 'Thực nhận']
        colors = ['#3498db', '#e74c3c', '#2ecc71', '#f39c12', '#9b59b6', '#34495e', '#e67e22', '#1abc9c']
        
        # Chỉ hiển thị các phần có giá trị > 0
        non_zero_values = []
        non_zero_labels = []
        non_zero_colors = []
        
        for i, value in enumerate(values):
            if value > 0:
                non_zero_values.append(value)
                non_zero_labels.append(labels[i])
                non_zero_colors.append(colors[i])
        
        if non_zero_values:
            # Tạo biểu đồ tròn với style đẹp
            wedges, texts, autotexts = ax.pie(non_zero_values, labels=non_zero_labels, colors=non_zero_colors, 
                                             autopct='%1.1f%%', startangle=90, 
                                             explode=[0.05] * len(non_zero_values),  # Tách các phần
                                             shadow=True,  # Thêm bóng
                                             textprops={'fontsize': 11, 'fontweight': 'bold'})
            
            # Cải thiện style cho text
            for autotext in autotexts:
                autotext.set_color('white')
                autotext.set_fontweight('bold')
                autotext.set_fontsize(10)
            
            for text in texts:
                text.set_fontsize(11)
                text.set_fontweight('bold')
                text.set_color('#2c3e50')
            
            ax.set_title('Phân bổ chi phí lương', fontsize=16, fontweight='bold', color='#2c3e50', pad=20)
            
            # Thêm legend
            ax.legend(wedges, [f'{label}: {value:,.0f} VNĐ' for label, value in zip(non_zero_labels, non_zero_values)],
                     title="Chi tiết", loc="center left", bbox_to_anchor=(1, 0, 0.5, 1),
                     fontsize=10, title_fontsize=12)
        else:
            ax.text(0.5, 0.5, 'Chưa có dữ liệu', ha='center', va='center', transform=ax.transAxes, 
                   fontsize=16, fontweight='bold', color='#7f8c8d')
            ax.set_xlim(0, 1)
            ax.set_ylim(0, 1)
            ax.axis('off')
        
        # Background
        self.pie_canvas.figure.patch.set_facecolor('#f8f9fa')
        
        self.pie_canvas.figure.tight_layout()
        self.pie_canvas.draw()

    def update_empty_summary(self):
        """Cập nhật thống kê khi không có dữ liệu"""
        for label_text in self.summary_labels:
            if "Tổng nhân viên" in label_text:
                self.summary_labels[label_text].setText("0")
            else:
                self.summary_labels[label_text].setText("0 VNĐ")

    def update_summary(self, total_employees, total_basic, total_allowance, total_overtime, total_kpi, total_salary):
        """Cập nhật thống kê tổng hợp"""
        self.summary_labels["Tổng nhân viên"].setText(str(total_employees))
        self.summary_labels["Tổng lương cơ bản"].setText(f"{total_basic:,.0f} VNĐ")
        self.summary_labels["Tổng phụ cấp"].setText(f"{total_allowance:,.0f} VNĐ")
        self.summary_labels["Tổng thêm giờ"].setText(f"{total_overtime:,.0f} VNĐ")
        self.summary_labels["Tổng KPI"].setText(f"{total_kpi:,.0f} VNĐ")
        self.summary_labels["Tổng thực nhận"].setText(f"{total_salary:,.0f} VNĐ")

    def update_data(self, data_chamcong):
        """Cập nhật dữ liệu chấm công (không tự động tính toán)"""
        self.data_chamcong = data_chamcong
        # Không tự động tính toán gì cả, chỉ cập nhật hiển thị
        self.update_display()

    def adjust_table_height(self, num_employees):
        """Tự động điều chỉnh chiều cao bảng dựa trên số lượng nhân viên"""
        try:
            # Chiều cao header
            header_height = 50
            
            # Chiều cao mỗi hàng
            row_height = 40
            
            # Chiều cao tối thiểu (ít nhất 3 hàng)
            min_height = header_height + (3 * row_height)
            
            # Chiều cao tối đa (tối đa 15 hàng)
            max_height = header_height + (15 * row_height)
            
            # Tính chiều cao dựa trên số lượng nhân viên
            if num_employees == 0:
                calculated_height = min_height
            else:
                calculated_height = header_height + (num_employees * row_height)
                # Giới hạn trong khoảng min-max
                calculated_height = max(min_height, min(calculated_height, max_height))
            
            # Áp dụng chiều cao cho bảng
            self.table.setFixedHeight(int(calculated_height))
            
            print(f"Debug: Điều chỉnh chiều cao bảng - {num_employees} nhân viên, chiều cao: {calculated_height}px")
            
        except Exception as e:
            print(f"Lỗi điều chỉnh chiều cao bảng: {e}") 