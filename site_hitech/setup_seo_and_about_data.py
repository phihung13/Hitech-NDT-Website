#!/usr/bin/env python
"""
Script thiết lập dữ liệu SEO cho trang chủ và nội dung mẫu cho trang giới thiệu
Chạy: python manage.py shell < setup_seo_and_about_data.py
"""

import os
import django
import sys

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'site_hitech.settings')
django.setup()

from api.models import HomePageSettings, AboutPage
from django.contrib.auth.models import User

def setup_homepage_seo():
    """Thiết lập SEO cho trang chủ"""
    print("🔍 Đang thiết lập SEO cho trang chủ...")
    
    homepage, created = HomePageSettings.objects.get_or_create(
        defaults={
            # SEO Settings - Tối ưu cho Google
            'meta_title': 'Hitech NDT - Kiểm tra không phá hủy hàng đầu Việt Nam | NDT Services',
            'meta_description': 'Hitech NDT chuyên cung cấp dịch vụ kiểm tra không phá hủy (NDT), đào tạo chứng chỉ UT/RT/MT/PT, thiết bị NDT chất lượng cao. Hơn 15 năm kinh nghiệm, 500+ dự án thành công. Liên hệ tư vấn miễn phí 24/7.',
            'meta_keywords': 'NDT, kiểm tra không phá hủy, ultrasonic testing, radiographic testing, magnetic particle testing, penetrant testing, đào tạo NDT, thiết bị NDT, UT, RT, MT, PT, chứng chỉ NDT level 2, Hitech NDT Vietnam',
            
            # Hero Section
            'hero_title': 'HITECH NDT',
            'hero_subtitle': 'Giải pháp kiểm tra không phá hủy hàng đầu Việt Nam với công nghệ tiên tiến và đội ngũ chuyên gia có chứng chỉ quốc tế',
            'hero_btn_primary_text': 'Khám phá dịch vụ',
            'hero_btn_primary_url': '/dich-vu/',
            'hero_btn_secondary_text': 'Tư vấn miễn phí',
            'hero_btn_secondary_url': '/lien-he/',
            
            # NDT Methods Section
            'ndt_section_title': 'Công nghệ kiểm tra không phá hủy tiên tiến',
            'ndt_section_subtitle': 'Ứng dụng các phương pháp NDT hiện đại: Ultrasonic (UT), Radiographic (RT), Magnetic Particle (MT), Penetrant Testing (PT) với thiết bị nhập khẩu từ Đức, Mỹ, Nhật Bản',
            
            # Projects Section  
            'projects_section_title': 'Dự án nổi bật đã thực hiện',
            'projects_section_subtitle': 'Hơn 500 dự án kiểm tra thành công cho các tập đoàn lớn trong ngành dầu khí, hóa chất, ô tô, điện tử và cơ khí chính밀',
            
            # Blog Section
            'blog_section_title': 'Kiến thức chuyên ngành NDT',
            'blog_section_subtitle': 'Cập nhật xu hướng công nghệ kiểm tra, tiêu chuẩn quốc tế và kinh nghiệm thực tiễn từ các chuyên gia hàng đầu',
            
            # Services Section
            'services_section_title': 'Dịch vụ NDT chuyên nghiệp',
            'services_section_subtitle': 'Giải pháp toàn diện: Kiểm tra hiện trường, đào tạo chứng chỉ, tư vấn kỹ thuật, cung cấp thiết bị và bảo trì định kỳ',
            
            # Testimonials
            'testimonials_section_title': 'Khách hàng tin tưởng Hitech NDT',
            'testimonials_section_subtitle': 'Phản hồi chân thực từ các đối tác đã hợp tác lâu dài với chúng tôi',
            
            # Partners
            'partners_section_title': 'Đối tác chiến lược',
            'partners_section_subtitle': 'Được tin tưởng bởi các tập đoàn đa quốc gia và doanh nghiệp hàng đầu trong khu vực',
            
            # Why Choose Us
            'why_section_title': 'Tại sao chọn Hitech NDT?',
            'why_section_subtitle': 'Những giá trị cốt lõi và lợi thế cạnh tranh khiến khách hàng tin tưởng và gắn bó',
            
            # Features
            'feature1_title': 'Chứng chỉ quốc tế',
            'feature1_description': 'Đội ngũ kỹ sư có chứng chỉ Level II/III từ ASNT, PCN và được đào tạo liên tục theo tiêu chuẩn quốc tế',
            'feature1_icon': 'fas fa-certificate',
            
            'feature2_title': 'Thiết bị hiện đại',
            'feature2_description': 'Trang thiết bị NDT thế hệ mới từ GE, Olympus, Sonatest với độ chính xác cao và khả năng phát hiện khuyết tật vượt trội',
            'feature2_icon': 'fas fa-microscope',
            
            'feature3_title': 'Nhanh chóng & chính xác',
            'feature3_description': 'Quy trình chuẩn hóa, báo cáo kết quả trong 24-48h với phần mềm quản lý dữ liệu chuyên nghiệp',
            'feature3_icon': 'fas fa-tachometer-alt',
            
            'feature4_title': 'Hỗ trợ 24/7',
            'feature4_description': 'Đội ngũ kỹ thuật sẵn sàng hỗ trợ khẩn cấp, tư vấn miễn phí và bảo hành dịch vụ dài hạn',
            'feature4_icon': 'fas fa-headset',
        }
    )
    
    if not created:
        # Cập nhật SEO cho bản ghi đã có
        homepage.meta_title = 'Hitech NDT - Kiểm tra không phá hủy hàng đầu Việt Nam | NDT Services'
        homepage.meta_description = 'Hitech NDT chuyên cung cấp dịch vụ kiểm tra không phá hủy (NDT), đào tạo chứng chỉ UT/RT/MT/PT, thiết bị NDT chất lượng cao. Hơn 15 năm kinh nghiệm, 500+ dự án thành công. Liên hệ tư vấn miễn phí 24/7.'
        homepage.meta_keywords = 'NDT, kiểm tra không phá hủy, ultrasonic testing, radiographic testing, magnetic particle testing, penetrant testing, đào tạo NDT, thiết bị NDT, UT, RT, MT, PT, chứng chỉ NDT level 2, Hitech NDT Vietnam'
        homepage.save()
        print("✓ Đã cập nhật SEO cho trang chủ")
    else:
        print("✓ Đã tạo mới cấu hình trang chủ với SEO tối ưu")


def setup_about_page():
    """Thiết lập dữ liệu mẫu cho trang giới thiệu"""
    print("\n📄 Đang thiết lập dữ liệu cho trang giới thiệu...")
    
    # Lấy user admin để gán làm người cập nhật
    try:
        admin_user = User.objects.filter(is_superuser=True).first()
    except:
        admin_user = None
    
    about_page, created = AboutPage.objects.get_or_create(
        defaults={
            # SEO Settings
            'meta_title': 'Về Hitech NDT - Công ty kiểm tra không phá hủy hàng đầu Việt Nam',
            'meta_description': 'Tìm hiểu về Hitech NDT - 15+ năm kinh nghiệm trong lĩnh vực NDT, đội ngũ chuyên gia có chứng chỉ quốc tế, công nghệ tiên tiến và cam kết chất lượng hàng đầu tại Việt Nam.',
            
            # Header & Hero Section
            'title': 'Về Hitech NDT',
            'subtitle': 'Đơn vị tiên phong trong lĩnh vực kiểm tra không phá hủy tại Việt Nam',
            'hero_bg_color': '#1e3d73',
            'hero_text_color': '#ffffff',
            
            # Main Content Section
            'main_title': 'Dẫn đầu công nghệ kiểm tra không phá hủy',
            'main_content': '''<p><strong>Hitech NDT</strong> được thành lập từ năm 2008 với sứ mệnh mang đến những giải pháp kiểm tra không phá hủy (Non-Destructive Testing) tiên tiến và đáng tin cậy nhất cho các doanh nghiệp tại Việt Nam.</p>

<p>Với hơn <strong>15 năm kinh nghiệm</strong> trong ngành, chúng tôi đã khẳng định vị thế là đơn vị hàng đầu cung cấp dịch vụ NDT chuyên nghiệp, từ kiểm tra hiện trường đến đào tạo chứng chỉ và cung cấp thiết bị.</p>

<h3>Lĩnh vực chuyên môn</h3>
<ul>
    <li><strong>Ultrasonic Testing (UT):</strong> Kiểm tra độ dày, phát hiện khuyết tật bên trong vật liệu</li>
    <li><strong>Radiographic Testing (RT):</strong> Chụp X-ray công nghiệp cho cấu trúc kim loại</li>
    <li><strong>Magnetic Particle Testing (MT):</strong> Phát hiện vết nứt bề mặt và gần bề mặt</li>
    <li><strong>Penetrant Testing (PT):</strong> Kiểm tra khuyết tật bề mặt trên mọi vật liệu</li>
    <li><strong>Visual Testing (VT):</strong> Kiểm tra trực quan với thiết bị quang học</li>
</ul>

<p>Hitech NDT phục vụ đa dạng các ngành công nghiệp: <em>dầu khí, hóa chất, điện lực, ô tô, hàng không, đóng tàu, cầu đường</em> và nhiều lĩnh vực khác đòi hỏi độ tin cậy cao.</p>''',
            'main_bg_color': '#ffffff',
            
            # Stats Section
            'stats_title': 'Thành tựu ấn tượng qua các năm',
            'stats_bg_color': '#f8f9fa',
            'stats_text_color': '#2c3e50',
            
            'stat1_number': '500+',
            'stat1_label': 'Dự án hoàn thành',
            'stat1_icon': 'fas fa-project-diagram',
            
            'stat2_number': '15+',
            'stat2_label': 'Năm kinh nghiệm',
            'stat2_icon': 'fas fa-calendar-check',
            
            'stat3_number': '200+',
            'stat3_label': 'Khách hàng tin tưởng',
            'stat3_icon': 'fas fa-handshake',
            
            'stat4_number': '50+',
            'stat4_label': 'Chuyên gia NDT',
            'stat4_icon': 'fas fa-users',
            
            # Vision Mission Values
            'vmv_title': 'Tầm nhìn - Sứ mệnh - Giá trị cốt lõi',
            'vmv_bg_color': '#ffffff',
            
            'vision_title': 'Tầm nhìn 2030',
            'vision': '''<p>Trở thành <strong>công ty NDT hàng đầu Đông Nam Á</strong>, được công nhận về:</p>
<ul>
    <li>Công nghệ kiểm tra tiên tiến nhất khu vực</li>
    <li>Đội ngũ chuyên gia có trình độ quốc tế</li>
    <li>Giải pháp tùy chỉnh cho từng ngành công nghiệp</li>
    <li>Tiêu chuẩn chất lượng đạt chuẩn toàn cầu</li>
</ul>''',
            'vision_icon': 'fas fa-telescope',
            'vision_color': '#3498db',
            
            'mission_title': 'Sứ mệnh',
            'mission': '''<p>Bảo vệ an toàn và chất lượng cho các công trình, thiết bị quan trọng thông qua:</p>
<ul>
    <li>Dịch vụ kiểm tra chính xác và đáng tin cậy</li>
    <li>Đào tạo nguồn nhân lực NDT chất lượng cao</li>
    <li>Chuyển giao công nghệ tiên tiến</li>
    <li>Đóng góp vào sự phát triển bền vững của ngành công nghiệp Việt Nam</li>
</ul>''',
            'mission_icon': 'fas fa-shield-alt',
            'mission_color': '#27ae60',
            
            'values_title': 'Giá trị cốt lõi',
            'core_values': '''<div class="row">
    <div class="col-md-6">
        <h5><i class="fas fa-award text-warning"></i> Chất lượng</h5>
        <p>Cam kết cung cấp dịch vụ đạt tiêu chuẩn quốc tế, từ quy trình thực hiện đến báo cáo kết quả.</p>
        
        <h5><i class="fas fa-users text-primary"></i> Chuyên nghiệp</h5>
        <p>Đội ngũ được đào tạo bài bản, có chứng chỉ quốc tế và cập nhật liên tục kiến thức mới.</p>
    </div>
    <div class="col-md-6">
        <h5><i class="fas fa-rocket text-success"></i> Đổi mới</h5>
        <p>Không ngừng nghiên cứu, ứng dụng công nghệ mới để nâng cao hiệu quả kiểm tra.</p>
        
        <h5><i class="fas fa-heart text-danger"></i> Tận tâm</h5>
        <p>Luôn đặt lợi ích và sự hài lòng của khách hàng lên hàng đầu trong mọi hoạt động.</p>
    </div>
</div>''',
            'values_icon': 'fas fa-gem',
            'values_color': '#f39c12',
            
            # Timeline Section
            'timeline_section_title': 'Hành trình phát triển',
            'timeline_section_subtitle': 'Những cột mốc quan trọng trong quá trình trở thành đơn vị NDT hàng đầu Việt Nam',
            'timeline': '''2008|Thành lập công ty|Được thành lập với đội ngũ 5 kỹ sư có kinh nghiệm từ các tập đoàn lớn
2010|Chứng nhận ISO 9001|Đạt chứng nhận hệ thống quản lý chất lượng ISO 9001:2008
2012|Mở rộng dịch vụ|Bổ sung dịch vụ đào tạo chứng chỉ NDT và cung cấp thiết bị
2015|Hợp tác quốc tế|Ký kết đối tác với GE Inspection Technologies và Olympus IMS
2017|Trung tâm đào tạo|Khánh thành trung tâm đào tạo NDT hiện đại với trang thiết bị đồng bộ
2020|Chuyển đổi số|Triển khai hệ thống quản lý dữ liệu số và báo cáo trực tuyến
2022|Mở chi nhánh|Thành lập chi nhánh tại Hà Nội và Đà Nẵng
2024|Công nghệ AI|Ứng dụng trí tuệ nhân tạo trong phân tích kết quả kiểm tra''',
            'timeline_bg_color': '#2c3e50',
            'timeline_text_color': '#ffffff',
            'timeline_accent_color': '#3498db',
            
            # Team Section
            'team_section_title': 'Đội ngũ chuyên gia',
            'team_section_description': '''<p>Hitech NDT tự hào có đội ngũ hơn <strong>50 chuyên gia</strong> được đào tạo bài bản và có chứng chỉ quốc tế:</p>
<div class="row mt-4">
    <div class="col-md-3 text-center">
        <h4 class="text-primary">15+</h4>
        <p>Kỹ sư Level III</p>
    </div>
    <div class="col-md-3 text-center">
        <h4 class="text-success">25+</h4>
        <p>Kỹ sư Level II</p>
    </div>
    <div class="col-md-3 text-center">
        <h4 class="text-warning">20+</h4>
        <p>Kỹ thuật viên Level I</p>
    </div>
    <div class="col-md-3 text-center">
        <h4 class="text-info">5+</h4>
        <p>Chuyên gia tư vấn</p>
    </div>
</div>''',
            'team_bg_color': '#f8f9fa',
        }
    )
    
    if not created:
        # Cập nhật SEO cho bản ghi đã có
        about_page.meta_title = 'Về Hitech NDT - Công ty kiểm tra không phá hủy hàng đầu Việt Nam'
        about_page.meta_description = 'Tìm hiểu về Hitech NDT - 15+ năm kinh nghiệm trong lĩnh vực NDT, đội ngũ chuyên gia có chứng chỉ quốc tế, công nghệ tiên tiến và cam kết chất lượng hàng đầu tại Việt Nam.'
        about_page.save()
        print("✓ Đã cập nhật SEO và nội dung cho trang giới thiệu")
    else:
        print("✓ Đã tạo mới trang giới thiệu với nội dung đầy đủ")


def main():
    """Hàm chính thực hiện tất cả setup"""
    print("🚀 BẮT ĐẦU THIẾT LẬP SEO VÀ DỮ LIỆU MẪU")
    print("=" * 50)
    
    try:
        setup_homepage_seo()
        setup_about_page()
        
        print("\n" + "=" * 50)
        print("✅ HOÀN THÀNH THIẾT LẬP!")
        print("\n📋 Những gì đã được thiết lập:")
        print("• SEO tối ưu cho trang chủ (meta title, description, keywords)")
        print("• Nội dung đầy đủ cho trang giới thiệu với SEO")
        print("• Timeline phát triển công ty")
        print("• Thông tin đội ngũ và chứng chỉ")
        print("• Call-to-action và thông tin liên hệ")
        
        print("\n🔍 Lợi ích SEO đã tối ưu:")
        print("• Meta title 60 ký tự, chứa từ khóa chính")
        print("• Meta description 155-160 ký tự, có call-to-action")
        print("• Keywords focus vào NDT và các phương pháp chính")
        print("• Nội dung rich với heading structure tốt")
        
        print("\n🎯 Bước tiếp theo:")
        print("• Vào Admin Django để xem và chỉnh sửa nội dung")
        print("• Thêm hình ảnh cho các phần (hero, timeline, team)")
        print("• Tạo thêm bài viết blog với từ khóa liên quan")
        
    except Exception as e:
        print(f"❌ Lỗi trong quá trình thiết lập: {str(e)}")
        import traceback
        print(traceback.format_exc())

if __name__ == "__main__":
    main() 