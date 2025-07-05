#!/usr/bin/env python
"""
Script cập nhật SiteSettings với dữ liệu mặc định cho cấu hình chung website
"""
import os
import sys
import django

# Setup Django
if __name__ == "__main__":
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'site_hitech.settings')
    django.setup()

    from api.models import SiteSettings

    # Tạo hoặc cập nhật SiteSettings
    settings, created = SiteSettings.objects.get_or_create(pk=1)
    
    if created:
        print("✅ Đã tạo mới SiteSettings")
    else:
        print("🔄 Đang cập nhật SiteSettings hiện tại")
    
    # Cập nhật thông tin cơ bản
    settings.company_name = "Hitech NDT"
    settings.company_slogan = "Giải pháp kiểm tra không phá hủy hàng đầu"
    settings.company_description = "Hitech NDT tự hào là đơn vị hàng đầu trong lĩnh vực kiểm tra không phá hủy và đào tạo chứng chỉ NDT tại Việt Nam với đội ngũ chuyên gia giàu kinh nghiệm và trang thiết bị hiện đại."
    
    # Cấu hình navbar
    settings.navbar_bg_color = "#212529"
    settings.navbar_text_color = "#ffffff"
    settings.navbar_brand_size = "20px"
    settings.navbar_link_size = "16px"
    settings.navbar_sticky = True
    
    # Cấu hình footer
    settings.footer_bg_color = "#212529"
    settings.footer_text_color = "#ffffff"
    settings.footer_link_color = "#adb5bd"
    settings.footer_copyright = "© 2024 Hitech NDT. Tất cả quyền được bảo lưu."
    
    # Thông tin liên hệ
    settings.footer_address = "Số 123, Đường ABC, Phường XYZ, Quận 1, TP. Hồ Chí Minh"
    settings.footer_phone = "+84 123 456 789"
    settings.footer_email = "info@hitechndt.com"
    
    # Mạng xã hội
    settings.facebook_url = "https://facebook.com/hitechndt"
    settings.linkedin_url = "https://linkedin.com/company/hitechndt"
    settings.youtube_url = "https://youtube.com/@hitechndt"
    settings.zalo_phone = "0123456789"
    
    # Màu sắc chung
    settings.primary_color = "#007bff"
    settings.secondary_color = "#6c757d"
    settings.success_color = "#28a745"
    settings.warning_color = "#ffc107"
    settings.danger_color = "#dc3545"
    
    # Typography
    settings.font_family = "Roboto, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif"
    settings.heading_font_family = "Roboto, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif"
    
    # SEO
    settings.site_title = "Hitech NDT - Giải pháp kiểm tra không phá hủy hàng đầu Việt Nam"
    settings.site_description = "Công ty hàng đầu về kiểm tra không phá hủy (NDT) tại Việt Nam. Cung cấp dịch vụ kiểm tra chuyên nghiệp, đào tạo chứng chỉ NDT và tư vấn kỹ thuật với đội ngũ chuyên gia giàu kinh nghiệm."
    settings.site_keywords = "NDT, kiểm tra không phá hủy, ultrasonic testing, radiographic testing, magnetic particle testing, dye penetrant testing, visual testing, chứng chỉ NDT, Hitech NDT, đào tạo NDT"
    
    # Hiển thị
    settings.show_breadcrumb = True
    settings.show_scroll_top = True
    
    # Liên hệ nhanh
    settings.enable_floating_contact = True
    settings.floating_phone = "+84 123 456 789"
    settings.floating_zalo = "0123456789"
    
    settings.save()
    
    print("🎉 SiteSettings đã được cập nhật thành công!")
    print(f"📄 Tên công ty: {settings.company_name}")
    print(f"💡 Slogan: {settings.company_slogan}")
    print(f"📧 Email: {settings.footer_email}")
    print(f"📱 Phone: {settings.footer_phone}")
    print("🔗 Truy cập /admin/api/sitesettings/ để tùy chỉnh thêm.") 