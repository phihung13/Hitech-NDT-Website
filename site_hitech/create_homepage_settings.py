#!/usr/bin/env python
import os
import sys
import django

# Thiết lập môi trường Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'site_hitech.settings')
sys.path.append('/c:/Hitech-NDT-Website/site_hitech')

django.setup()

from api.models import HomePageSettings

def create_homepage_settings():
    # Kiểm tra xem đã có cấu hình nào chưa
    if HomePageSettings.objects.exists():
        print("✓ Cấu hình trang chủ đã tồn tại")
        return
    
    # Tạo cấu hình mặc định
    settings = HomePageSettings.objects.create(
        # Hero Section
        hero_title='HITECH NDT',
        hero_subtitle='Giải pháp kiểm tra không phá hủy hàng đầu Việt Nam với công nghệ tiên tiến và đội ngũ chuyên gia giàu kinh nghiệm',
        hero_btn_primary_text='Khám phá dịch vụ',
        hero_btn_primary_url='/dich-vu/',
        hero_btn_secondary_text='Liên hệ ngay',
        hero_btn_secondary_url='/lien-he/',
        
        # NDT Methods Section
        ndt_section_title='Phương pháp NDT chuyên nghiệp',
        ndt_section_subtitle='Ứng dụng các công nghệ kiểm tra không phá hủy tiên tiến nhất theo tiêu chuẩn quốc tế',
        
        # Projects Section
        projects_section_title='Dự án nổi bật',
        projects_section_subtitle='Những dự án tiêu biểu đã thực hiện thành công với chất lượng cao',
        
        # Blog Section
        blog_section_title='Tin tức & Bài viết',
        blog_section_subtitle='Cập nhật những thông tin mới nhất về công nghệ NDT và ngành công nghiệp',
        
        # Services Section
        services_section_title='Dịch vụ chuyên nghiệp',
        services_section_subtitle='Giải pháp toàn diện cho mọi nhu cầu kiểm tra và đào tạo chứng chỉ NDT',
        
        # Testimonials Section
        testimonials_section_title='Khách hàng nói về chúng tôi',
        testimonials_section_subtitle='Phản hồi từ những khách hàng đã tin tưởng sử dụng dịch vụ',
        
        # Testimonials Content
        testimonial1_content='Hitech NDT đã cung cấp dịch vụ kiểm tra chất lượng cao cho dự án của chúng tôi. Đội ngũ chuyên nghiệp, thiết bị hiện đại và báo cáo chi tiết, chính xác.',
        testimonial1_name='Trần Văn Long',
        testimonial1_position='Trưởng phòng kỹ thuật',
        testimonial1_company='Công ty TNHH ABC',
        
        testimonial2_content='Dịch vụ đào tạo chứng chỉ NDT Level II tại Hitech rất chuyên nghiệp. Giáo viên giàu kinh nghiệm, tài liệu đầy đủ và thiết bị thực hành hiện đại.',
        testimonial2_name='Nguyễn Thanh Huy',
        testimonial2_position='Kỹ sư NDT',
        testimonial2_company='Tập đoàn Dầu khí Việt Nam',
        
        testimonial3_content='Hitech NDT luôn đáp ứng đúng tiến độ và chất lượng cam kết. Đây là đối tác tin cậy cho các dự án kiểm tra của chúng tôi.',
        testimonial3_name='Mai Thị Thuỷ',
        testimonial3_position='Giám đốc kỹ thuật',
        testimonial3_company='Công ty Cơ khí XYZ',
        
        testimonial4_content='Thiết bị kiểm tra được Hitech cung cấp rất hiện đại và chính xác. Hỗ trợ kỹ thuật 24/7 giúp chúng tôi yên tâm trong quá trình thực hiện dự án.',
        testimonial4_name='Phạm Văn Dũng',
        testimonial4_position='Chuyên viên kiểm tra',
        testimonial4_company='Nhà máy Thép Hòa Phát',
        
        testimonial5_content='Báo cáo kiểm tra từ Hitech luôn chi tiết, rõ ràng và đúng tiêu chuẩn quốc tế. Điều này giúp chúng tôi thuyết phục được khách hàng quốc tế.',
        testimonial5_name='Lê Minh Khang',
        testimonial5_position='QA Manager',
        testimonial5_company='Samsung Electronics Vietnam',
        
        # Partners Section
        partners_section_title='Đối tác tin cậy',
        partners_section_subtitle='Được tin tưởng bởi các doanh nghiệp hàng đầu trong và ngoài nước',
        
        # Partner Management
        partner1_name='PetroVietnam',
        partner1_icon='fas fa-industry',
        partner2_name='Samsung',
        partner2_icon='fas fa-mobile-alt',
        partner3_name='Hòa Phát',
        partner3_icon='fas fa-industry',
        partner4_name='Vingroup',
        partner4_icon='fas fa-building',
        partner5_name='FPT',
        partner5_icon='fas fa-laptop-code',
        partner6_name='Viettel',
        partner6_icon='fas fa-satellite-dish',
        partner7_name='VNSteel',
        partner7_icon='fas fa-hammer',
        partner8_name='Honda',
        partner8_icon='fas fa-motorcycle',
        partner9_name='Toyota',
        partner9_icon='fas fa-car',
        partner10_name='SABIC',
        partner10_icon='fas fa-flask',
        partner11_name='Chevron',
        partner11_icon='fas fa-oil-can',
        partner12_name='General Electric',
        partner12_icon='fas fa-bolt',
        
        # Trust Indicators
        trust_stat1_number='100+',
        trust_stat1_label='Đối tác tin cậy',
        trust_stat2_number='500+',
        trust_stat2_label='Dự án thành công',
        trust_stat3_number='15+',
        trust_stat3_label='Năm kinh nghiệm',
        trust_stat4_number='24/7',
        trust_stat4_label='Hỗ trợ khách hàng',
        
        # Why Choose Us Section
        why_section_title='Vì sao chọn Hitech NDT?',
        why_section_subtitle='Những giá trị cốt lõi làm nên thương hiệu Hitech NDT',
        
        # Features
        feature1_title='Chuyên nghiệp',
        feature1_description='Đội ngũ kỹ sư có chứng chỉ quốc tế và kinh nghiệm thực tiễn',
        feature1_icon='fas fa-medal',
        
        feature2_title='Công nghệ tiên tiến',
        feature2_description='Trang thiết bị hiện đại nhập khẩu từ các nước phát triển',
        feature2_icon='fas fa-rocket',
        
        feature3_title='Nhanh chóng',
        feature3_description='Thời gian thực hiện nhanh, báo cáo kết quả chính xác',
        feature3_icon='fas fa-clock',
        
        feature4_title='Tin cậy',
        feature4_description='Được hàng trăm khách hàng lớn tin tưởng và hợp tác lâu dài',
        feature4_icon='fas fa-handshake',
        
        # SEO Settings
        meta_title='Hitech NDT - Giải pháp kiểm tra không phá hủy hàng đầu Việt Nam',
        meta_description='Hitech NDT cung cấp dịch vụ kiểm tra không phá hủy chuyên nghiệp, đào tạo chứng chỉ NDT và thiết bị hiện đại. Liên hệ ngay để được tư vấn miễn phí.',
        meta_keywords='NDT, kiểm tra không phá hủy, ultrasonic, radiography, magnetic particle, penetrant testing, đào tạo NDT, thiết bị NDT',
        
        # General Settings
        show_ndt_section=True,
        show_projects_section=True,
        show_blog_section=True,
        show_services_section=True,
        show_testimonials_section=True,
        show_partners_section=True,
        show_why_section=True,
    )
    
    print("✓ Đã tạo cấu hình trang chủ mặc định thành công!")
    print(f"  - Hero title: {settings.hero_title}")
    print(f"  - Testimonials: {settings.testimonials_section_title}")
    print(f"  - Số testimonials: 5")
    print(f"  - Đối tác: 12")
    print(f"  - SEO title: {settings.meta_title}")

if __name__ == '__main__':
    create_homepage_settings() 