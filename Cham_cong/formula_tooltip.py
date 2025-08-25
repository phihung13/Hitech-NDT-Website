#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tooltip đơn giản cho các ô thành tiền trong phiếu lương
"""

from PyQt5.QtWidgets import QToolTip
from PyQt5.QtCore import QTimer, QPoint

class SimpleFormulaTooltip:
    def __init__(self):
        self.timer = QTimer()
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.show_tooltip)
        self.current_widget = None
        self.formula_text = ""
        
    def setup_tooltip(self, widget, formula_text, delay_ms=3000):
        """Thiết lập tooltip cho widget"""
        widget.mousePressEvent = lambda event: self.on_mouse_press(widget, formula_text, delay_ms, event)
        widget.mouseReleaseEvent = lambda event: self.on_mouse_release(event)
        widget.leaveEvent = lambda event: self.on_leave(event)
        
    def on_mouse_press(self, widget, formula_text, delay_ms, event):
        """Khi nhấn chuột vào widget"""
        self.current_widget = widget
        self.formula_text = formula_text
        self.timer.start(delay_ms)
        
    def on_mouse_release(self, event):
        """Khi thả chuột"""
        self.timer.stop()
        
    def on_leave(self, event):
        """Khi chuột rời khỏi widget"""
        self.timer.stop()
        QToolTip.hideText()
        
    def show_tooltip(self):
        """Hiển thị tooltip với công thức"""
        if self.current_widget and self.formula_text:
            # Lấy vị trí của widget
            pos = self.current_widget.mapToGlobal(QPoint(0, 0))
            
            # Tạo tooltip đơn giản
            tooltip_html = f"""
            <div style="
                background-color: #2c3e50;
                color: white;
                padding: 8px;
                border-radius: 4px;
                font-size: 11px;
                max-width: 250px;
                border: 1px solid #3498db;
            ">
                <div style="font-weight: bold; color: #3498db; margin-bottom: 3px;">
                    🔍 CÔNG THỨC
                </div>
                <div style="color: #ecf0f1;">
                    {self.formula_text}
                </div>
            </div>
            """
            
            QToolTip.showText(pos, tooltip_html, self.current_widget)

def get_formula_text(component_name):
    """Lấy text công thức cho từng component"""
    formulas = {
        "luong_co_ban": "Lương cơ bản = Số ngày làm việc × Lương cơ bản/ngày",
        "them_gio_150": "Thêm giờ 150% = Số giờ × Lương 1 giờ × 1.5",
        "them_gio_200": "Thêm giờ 200% = Số giờ × Lương 1 giờ × 2.0", 
        "them_gio_300": "Thêm giờ 300% = Số giờ × Lương 1 giờ × 3.0",
        "tong_them_gio": "Tổng thêm giờ = 150% + 200% + 300%",
        "phu_cap_cong_truong": "PC công trường = Số ngày công trường × Mức phụ cấp",
        "phu_cap_dao_tao": "PC đào tạo = Số ngày đào tạo × (Mức PC công trường × 0.4)",
        "phu_cap_van_phong": "PC văn phòng = Số ngày văn phòng × (Mức PC công trường × 0.2)",
        "phu_cap_chuc_danh": "PC chức danh = (Số ngày công trường / Số ngày làm việc tháng) × Mức phụ cấp",
        "xang_xe": "Xăng xe = Tổng từ dữ liệu chấm công (theo công ty)",
        "dien_thoai": "Điện thoại = Tổng từ dữ liệu chấm công",
        "khach_san": "Khách sạn = Tổng từ dữ liệu chấm công",
        "tong_phu_cap": "Tổng phụ cấp = Công trình + Đào tạo + Văn phòng + Chức danh + Xăng xe + Điện thoại + Khách sạn",
        "kpi_paut": "KPI PAUT = Số mét vượt × Đơn giá PAUT",
        "kpi_tofd": "KPI TOFD = Số mét vượt × Đơn giá TOFD",
        "tong_kpi": "Tổng KPI = PAUT + TOFD",
        "bhxh": "BHXH = Lương cơ sở BHXH × 10.5%",
        "thue_tncn": "Thuế TNCN = Tính theo bậc thuế lũy tiến",
        "tam_ung": "Tạm ứng = Số tiền tạm ứng (nhập thủ công)",
        "vi_pham": "Vi phạm = Số tiền vi phạm (nhập thủ công)",
        "tong_khau_tru": "Tổng khấu trừ = BHXH + Thuế TNCN + Tạm ứng + Vi phạm",
        "mua_sam": "Mua sắm = Tổng chi phí mua sắm từ dữ liệu chấm công",
        "tong_cong": "Tổng cộng (I) = Lương cơ bản + Thêm giờ + Phụ cấp + KPI",
        "thuc_nhan": "Thực nhận = Tổng cộng (I) - Tổng khấu trừ (E) + Mua sắm (F)"
    }
    
    return formulas.get(component_name, f"Công thức cho {component_name} chưa được định nghĩa") 