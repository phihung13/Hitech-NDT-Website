from django.db import models
from django.contrib.auth.models import User
from django_ckeditor_5.fields import CKEditor5Field
from django.utils.text import slugify
from django.core.exceptions import ValidationError
from colorfield.fields import ColorField


class SiteSettings(models.Model):
    # Logo và thông tin công ty chính
    logo = models.ImageField(upload_to='site/', null=True, blank=True, verbose_name='Logo công ty (hiển thị trên navbar)')
    company_name = models.CharField(max_length=100, default='Hitech NDT', verbose_name='Tên công ty')
    company_slogan = models.CharField(max_length=200, default='Giải pháp công nghệ hàng đầu', verbose_name='Slogan công ty')
    company_description = models.TextField(default='Hitech NDT tự hào là đơn vị hàng đầu trong lĩnh vực kiểm tra không phá hủy và đào tạo chứng chỉ NDT tại Việt Nam', verbose_name='Mô tả công ty')
    
    # Cài đặt Navbar (Menu điều hướng)
    navbar_bg_color = ColorField(default='#212529', verbose_name='Màu nền Navbar')
    navbar_text_color = ColorField(default='#ffffff', verbose_name='Màu chữ Navbar')
    navbar_brand_size = models.CharField(max_length=10, default='18px', verbose_name='Kích thước chữ thương hiệu (px)')
    navbar_link_size = models.CharField(max_length=10, default='14px', verbose_name='Kích thước chữ menu (px)')
    navbar_sticky = models.BooleanField(default=True, verbose_name='Navbar dính (sticky)')
    
    # Cài đặt Footer (Chân trang)
    footer_bg_color = ColorField(default='#212529', verbose_name='Màu nền Footer')
    footer_text_color = ColorField(default='#ffffff', verbose_name='Màu chữ Footer')
    footer_link_color = ColorField(default='#6c757d', verbose_name='Màu liên kết Footer')
    footer_copyright = models.CharField(max_length=200, default='© 2024 Hitech NDT. Tất cả quyền được bảo lưu.', verbose_name='Bản quyền Footer')
    
    # Thông tin liên hệ hiển thị trên Footer
    footer_address = models.CharField(max_length=200, default='123 Đường ABC, Quận XYZ, TP.HCM', verbose_name='Địa chỉ công ty')
    footer_phone = models.CharField(max_length=20, default='+84 123 456 789', verbose_name='Số điện thoại chính')
    footer_email = models.EmailField(default='info@hitechndt.com', verbose_name='Email liên hệ chính')
    
    # Liên kết mạng xã hội
    facebook_url = models.URLField(blank=True, null=True, verbose_name='Facebook URL')
    linkedin_url = models.URLField(blank=True, null=True, verbose_name='LinkedIn URL')
    youtube_url = models.URLField(blank=True, null=True, verbose_name='YouTube URL')
    twitter_url = models.URLField(blank=True, null=True, verbose_name='Twitter URL')
    zalo_phone = models.CharField(max_length=15, blank=True, null=True, verbose_name='Số Zalo')
    
    # Màu sắc chung của website (cho các trang chưa có cấu hình riêng)
    primary_color = ColorField(default='#007bff', verbose_name='Màu chính (Primary)')
    secondary_color = ColorField(default='#6c757d', verbose_name='Màu phụ (Secondary)')
    success_color = ColorField(default='#28a745', verbose_name='Màu thành công (Success)')
    warning_color = ColorField(default='#ffc107', verbose_name='Màu cảnh báo (Warning)')
    danger_color = ColorField(default='#dc3545', verbose_name='Màu nguy hiểm (Danger)')
    
    # Cài đặt typography chung
    font_family = models.CharField(max_length=100, default='Roboto, sans-serif', verbose_name='Font chữ chính')
    heading_font_family = models.CharField(max_length=100, default='Roboto, sans-serif', verbose_name='Font chữ tiêu đề')
    
    # SEO chung
    site_title = models.CharField(max_length=200, default='Hitech NDT - Giải pháp kiểm tra không phá hủy', verbose_name='Tiêu đề website (Meta Title)')
    site_description = models.TextField(default='Công ty hàng đầu về kiểm tra không phá hủy (NDT) tại Việt Nam. Cung cấp dịch vụ chuyên nghiệp và đào tạo chứng chỉ NDT.', verbose_name='Mô tả website (Meta Description)')
    site_keywords = models.CharField(max_length=300, default='NDT, kiểm tra không phá hủy, Hitech NDT, chứng chỉ NDT', verbose_name='Từ khóa SEO')
    
    # Cài đặt hiển thị
    show_breadcrumb = models.BooleanField(default=True, verbose_name='Hiển thị breadcrumb (đường dẫn)')
    show_scroll_top = models.BooleanField(default=True, verbose_name='Hiển thị nút cuộn lên đầu trang')
    
    # Thông tin liên hệ nhanh (floating)
    enable_floating_contact = models.BooleanField(default=True, verbose_name='Bật liên hệ nhanh (floating)')
    floating_phone = models.CharField(max_length=20, blank=True, null=True, verbose_name='SĐT liên hệ nhanh')
    floating_zalo = models.CharField(max_length=15, blank=True, null=True, verbose_name='Số Zalo liên hệ nhanh')
    
    def clean(self):
        # Đảm bảo chỉ có một bản ghi cấu hình
        if not self.pk and SiteSettings.objects.exists():
            raise ValidationError('Chỉ có thể tạo một bản ghi cấu hình website')
    
    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f'Cấu hình chung website - {self.company_name}'
    
    class Meta:
        verbose_name = 'Cấu hình chung website'
        verbose_name_plural = 'Cấu hình chung website'


class ContactSettings(models.Model):
    recipient_email = models.EmailField(verbose_name='Email người nhận')
    address = models.TextField(verbose_name='Địa chỉ')
    phone_numbers = models.TextField(verbose_name='Số điện thoại', help_text='Mỗi số điện thoại một dòng')
    business_hours = models.TextField(verbose_name='Giờ làm việc', help_text='Định dạng: Thứ Hai - Thứ Sáu: 8:00 - 17:30')
    email_contact = models.TextField(verbose_name='Email liên hệ', help_text='Mỗi email một dòng')
    maps_embed = models.TextField(verbose_name='Mã nhúng Google Maps', help_text='Mã iframe từ Google Maps')
    maps_link = models.URLField(blank=True, null=True, verbose_name='Link Google Maps', 
                               help_text='Link trực tiếp đến Google Maps (VD: https://maps.app.goo.gl/A8TcFmJHawaxYMND6)')
    
    def clean(self):
        # Đảm bảo chỉ có một bản ghi cấu hình
        if not self.pk and ContactSettings.objects.exists():
            raise ValidationError('Chỉ có thể tạo một bản ghi cấu hình liên hệ')
    
    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return 'Cấu hình liên hệ'
    
    class Meta:
        verbose_name = 'Cấu hình liên hệ'
        verbose_name_plural = 'Cấu hình liên hệ'



class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    class Meta:
        verbose_name_plural = "Categories"

class Post(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, null=True, blank=True)
    content = CKEditor5Field(config_name='advanced')
    summary = models.TextField(blank=True, null=True)
    featured_image = models.ImageField(upload_to='blog/%Y/%m/', null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published = models.BooleanField(default=False)
    view_count = models.PositiveIntegerField(default=0)
    tags = models.ManyToManyField('Tag', blank=True)
    
    # SEO Fields
    meta_title = models.CharField(max_length=60, blank=True, null=True, verbose_name='Meta Title', 
                                 help_text='Tiêu đề hiển thị trên Google (tối đa 60 ký tự). Để trống sẽ sử dụng tiêu đề bài viết.')
    meta_description = models.TextField(max_length=160, blank=True, null=True, verbose_name='Meta Description',
                                       help_text='Mô tả hiển thị trên Google (tối đa 160 ký tự).')
    meta_keywords = models.CharField(max_length=255, blank=True, null=True, verbose_name='Keywords',
                                    help_text='Từ khóa SEO, phân cách bằng dấu phẩy.')
    
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return f'/blog/{self.category.slug}/{self.slug}/'
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

class CourseCategory(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True, help_text='Font Awesome class name')
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    class Meta:
        verbose_name_plural = "Course Categories"

class Course(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, null=True, blank=True)
    description = CKEditor5Field()
    summary = models.TextField(null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    thumbnail = models.ImageField(upload_to='courses/%Y/%m/', null=True, blank=True)
    instructor = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    category = models.ForeignKey(CourseCategory, on_delete=models.SET_NULL, null=True, related_name='courses')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published = models.BooleanField(default=False)
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

class Lesson(models.Model):
    title = models.CharField(max_length=200)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='lessons')
    content = CKEditor5Field()
    order = models.PositiveIntegerField()
    video_url = models.URLField(blank=True, null=True)
    
    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return f"{self.course.title} - {self.title}"


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments', null=True, blank=True)
    name = models.CharField(max_length=100)
    email = models.EmailField()
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-created_at']
        
    def __str__(self):
        return f'Comment by {self.name} on {self.post.title if self.post else "unknown post"}'


class Tag(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['name']


class ChatSettings(models.Model):
    auto_reply_message = models.TextField(verbose_name='Tin nhắn tự động trả lời', 
        default='Cảm ơn bạn đã liên hệ. Chúng tôi sẽ phản hồi sớm nhất có thể.')
    zalo_phone = models.CharField(max_length=15, verbose_name='Số điện thoại Zalo')
    is_chat_enabled = models.BooleanField(default=True, verbose_name='Bật/tắt chat')
    
    def clean(self):
        if not self.pk and ChatSettings.objects.exists():
            raise ValidationError('Chỉ có thể tạo một bản ghi cấu hình chat')
    
    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return 'Cấu hình chat'
    
    class Meta:
        verbose_name = 'Cấu hình chat'
        verbose_name_plural = 'Cấu hình chat'

class ChatMessage(models.Model):
    SENDER_CHOICES = [
        ('USER', 'Người dùng'),
        ('ADMIN', 'Quản trị viên'),
        ('AUTO', 'Tự động'),
    ]
    
    sender_type = models.CharField(max_length=5, choices=SENDER_CHOICES)
    sender_name = models.CharField(max_length=100)
    sender_email = models.EmailField(null=True, blank=True)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Tin nhắn'
        verbose_name_plural = 'Tin nhắn'
    
    def __str__(self):
        return f'Tin nhắn từ {self.sender_name} - {self.created_at}'


class AboutPage(models.Model):
    # Header & Hero Section
    title = models.CharField(max_length=200, default="Về Chúng Tôi", verbose_name='Tiêu đề trang')
    subtitle = models.CharField(max_length=300, blank=True, help_text="Phụ đề hiển thị bên dưới tiêu đề chính", verbose_name='Phụ đề')
    hero_bg_image = models.ImageField(upload_to='about/hero/', null=True, blank=True, verbose_name='Ảnh nền Hero Section')
    hero_bg_color = ColorField(default='#003d99', verbose_name='Màu nền Hero (khi không có ảnh)')
    hero_text_color = ColorField(default='#ffffff', verbose_name='Màu chữ Hero')
    
    # Main Content Section
    main_title = models.CharField(max_length=200, default="Công ty của chúng tôi", verbose_name='Tiêu đề chính')
    main_content = CKEditor5Field(verbose_name='Nội dung chính', help_text='Nội dung giới thiệu chính về công ty', 
                                 default='<p>Hitech NDT là đơn vị hàng đầu trong lĩnh vực kiểm tra không phá hủy tại Việt Nam. Với đội ngũ kỹ sư giàu kinh nghiệm và trang thiết bị hiện đại, chúng tôi cam kết mang đến những dịch vụ chất lượng cao nhất cho khách hàng.</p>')
    main_image = models.ImageField(upload_to='about/', null=True, blank=True, verbose_name='Ảnh chính')
    main_bg_color = ColorField(default='#ffffff', verbose_name='Màu nền phần nội dung chính')
    
    # Stats Section  
    stats_title = models.CharField(max_length=200, default="Con số ấn tượng", verbose_name='Tiêu đề phần thống kê')
    stats_bg_color = ColorField(default='#f8f9fa', verbose_name='Màu nền phần thống kê')
    stats_text_color = ColorField(default='#333333', verbose_name='Màu chữ phần thống kê')
    
    # Stat items
    stat1_number = models.CharField(max_length=20, default="500+", verbose_name='Số liệu 1')
    stat1_label = models.CharField(max_length=100, default="Dự án hoàn thành", verbose_name='Nhãn số liệu 1')
    stat1_icon = models.CharField(max_length=50, default="fas fa-project-diagram", verbose_name='Icon số liệu 1 (FontAwesome)')
    
    stat2_number = models.CharField(max_length=20, default="15+", verbose_name='Số liệu 2')
    stat2_label = models.CharField(max_length=100, default="Năm kinh nghiệm", verbose_name='Nhãn số liệu 2')
    stat2_icon = models.CharField(max_length=50, default="fas fa-calendar-alt", verbose_name='Icon số liệu 2 (FontAwesome)')
    
    stat3_number = models.CharField(max_length=20, default="100+", verbose_name='Số liệu 3')
    stat3_label = models.CharField(max_length=100, default="Khách hàng tin tưởng", verbose_name='Nhãn số liệu 3')
    stat3_icon = models.CharField(max_length=50, default="fas fa-handshake", verbose_name='Icon số liệu 3 (FontAwesome)')
    
    stat4_number = models.CharField(max_length=20, default="24/7", verbose_name='Số liệu 4')
    stat4_label = models.CharField(max_length=100, default="Hỗ trợ khách hàng", verbose_name='Nhãn số liệu 4')
    stat4_icon = models.CharField(max_length=50, default="fas fa-clock", verbose_name='Icon số liệu 4 (FontAwesome)')
    
    # Vision Mission Values Section
    vmv_title = models.CharField(max_length=200, default="Tầm nhìn - Sứ mệnh - Giá trị", verbose_name='Tiêu đề phần VMV')
    vmv_bg_color = ColorField(default='#ffffff', verbose_name='Màu nền phần VMV')
    vmv_bg_image = models.ImageField(upload_to='about/vmv/', null=True, blank=True, verbose_name='Ảnh nền phần VMV')
    
    # Vision
    vision_title = models.CharField(max_length=100, default="Tầm nhìn", verbose_name='Tiêu đề Tầm nhìn')
    vision = CKEditor5Field(verbose_name='Nội dung Tầm nhìn', null=True, blank=True)
    vision_icon = models.CharField(max_length=50, default="fas fa-eye", verbose_name='Icon Tầm nhìn')
    vision_color = ColorField(default='#007bff', verbose_name='Màu chủ đạo Tầm nhìn')
    
    # Mission
    mission_title = models.CharField(max_length=100, default="Sứ mệnh", verbose_name='Tiêu đề Sứ mệnh')
    mission = CKEditor5Field(verbose_name='Nội dung Sứ mệnh', null=True, blank=True)
    mission_icon = models.CharField(max_length=50, default="fas fa-bullseye", verbose_name='Icon Sứ mệnh')
    mission_color = ColorField(default='#28a745', verbose_name='Màu chủ đạo Sứ mệnh')
    
    # Core Values
    values_title = models.CharField(max_length=100, default="Giá trị cốt lõi", verbose_name='Tiêu đề Giá trị cốt lõi')
    core_values = CKEditor5Field(verbose_name='Nội dung Giá trị cốt lõi', null=True, blank=True)
    values_icon = models.CharField(max_length=50, default="fas fa-gem", verbose_name='Icon Giá trị cốt lõi')
    values_color = ColorField(default='#ffc107', verbose_name='Màu chủ đạo Giá trị cốt lõi')
    
    # Timeline Section
    timeline_section_title = models.CharField(max_length=200, verbose_name='Tiêu đề phần cột mốc', default='Cột mốc phát triển')
    timeline_section_subtitle = models.TextField(blank=True, verbose_name='Mô tả phần cột mốc', help_text='Mô tả ngắn về phần lịch sử phát triển')
    timeline = models.TextField(verbose_name='Cột mốc thời gian', null=True, blank=True, help_text='Nhập theo format: Năm|Tiêu đề|Mô tả, mỗi cột mốc một dòng')
    timeline_bg_image = models.ImageField(upload_to='about/timeline/', null=True, blank=True, verbose_name='Ảnh nền phần Timeline')
    timeline_bg_color = ColorField(default='#f8f9fa', verbose_name='Màu nền phần Timeline')
    timeline_text_color = ColorField(default='#333333', verbose_name='Màu chữ Timeline')
    timeline_accent_color = ColorField(default='#007bff', verbose_name='Màu nhấn Timeline (đường kẻ, điểm)')
    
    # Timeline Overlay Settings (khi có ảnh nền)
    timeline_overlay_color = ColorField(default='#f8f9fa', verbose_name='Màu overlay Timeline (khi có ảnh nền)')
    timeline_overlay_opacity = models.DecimalField(max_digits=3, decimal_places=2, default=0.95, 
                                                   verbose_name='Độ mờ overlay Timeline (0.0-1.0)',
                                                   help_text='0.0 = hoàn toàn trong suốt, 1.0 = hoàn toàn mờ')
    
    # Team Section
    team_section_title = models.CharField(max_length=200, verbose_name='Tiêu đề phần đội ngũ', default='Đội ngũ của chúng tôi')
    team_section_description = CKEditor5Field(verbose_name='Mô tả phần đội ngũ', null=True, blank=True)
    team_bg_color = ColorField(default='#ffffff', verbose_name='Màu nền phần Đội ngũ')
    team_bg_image = models.ImageField(upload_to='about/team/', null=True, blank=True, verbose_name='Ảnh nền phần Đội ngũ')
    
    # Services/Capabilities Section
    services_title = models.CharField(max_length=200, default="Dịch vụ của chúng tôi", verbose_name='Tiêu đề phần Dịch vụ')
    services_subtitle = models.TextField(blank=True, verbose_name='Mô tả phần Dịch vụ')
    services_bg_color = ColorField(default='#f8f9fa', verbose_name='Màu nền phần Dịch vụ')
    services_content = CKEditor5Field(verbose_name='Nội dung phần Dịch vụ', null=True, blank=True, help_text='Danh sách các dịch vụ/năng lực chính')
    
    # Achievements Section
    achievements_title = models.CharField(max_length=200, default="Thành tựu & Chứng nhận", verbose_name='Tiêu đề phần Thành tựu')
    achievements = CKEditor5Field(verbose_name='Nội dung Thành tựu', null=True, blank=True)
    achievements_bg_color = ColorField(default='#ffffff', verbose_name='Màu nền phần Thành tựu')
    achievements_image = models.ImageField(upload_to='about/achievements/', null=True, blank=True, verbose_name='Ảnh phần Thành tựu')
    
    # Certificates Section
    certificates_section_title = models.CharField(max_length=200, verbose_name='Tiêu đề phần chứng chỉ', default='Chứng chỉ & Giấy phép')
    certificates_section_subtitle = models.TextField(blank=True, verbose_name='Mô tả phần Chứng chỉ')
    certificates = CKEditor5Field(verbose_name='Nội dung Chứng chỉ', null=True, blank=True)
    certificates_bg_color = ColorField(default='#f8f9fa', verbose_name='Màu nền phần Chứng chỉ')
    
    # CTA Section
    cta_title = models.CharField(max_length=200, default="Sẵn sàng hợp tác?", verbose_name='Tiêu đề Call to Action')
    cta_subtitle = models.TextField(default="Liên hệ với chúng tôi ngay hôm nay để được tư vấn miễn phí", verbose_name='Mô tả CTA')
    cta_button_text = models.CharField(max_length=50, default="Liên hệ ngay", verbose_name='Văn bản nút CTA')
    cta_button_url = models.CharField(max_length=200, default="/lien-he/", verbose_name='Liên kết nút CTA')
    cta_bg_color = ColorField(default='#007bff', verbose_name='Màu nền CTA')
    cta_text_color = ColorField(default='#ffffff', verbose_name='Màu chữ CTA')
    cta_button_color = ColorField(default='#ffffff', verbose_name='Màu nút CTA')
    cta_button_text_color = ColorField(default='#007bff', verbose_name='Màu chữ nút CTA')
    
    # Layout Settings
    container_max_width = models.CharField(max_length=20, default='1200px', verbose_name='Chiều rộng tối đa container')
    section_padding = models.CharField(max_length=20, default='80px 0', verbose_name='Padding cho các section')
    
    # Typography
    heading_font_family = models.CharField(max_length=100, default='Roboto, sans-serif', verbose_name='Font chữ tiêu đề')
    body_font_family = models.CharField(max_length=100, default='Open Sans, sans-serif', verbose_name='Font chữ nội dung')
    heading_color = ColorField(default='#333333', verbose_name='Màu tiêu đề chính')
    body_color = ColorField(default='#666666', verbose_name='Màu chữ nội dung')
    
    # Banner/Featured Image (backward compatibility)
    banner_image = models.ImageField(upload_to='about/', verbose_name='Ảnh banner chính', null=True, blank=True)
    content = CKEditor5Field(verbose_name='Nội dung cũ (tương thích)', null=True, blank=True, help_text='Trường này để tương thích, khuyến khích dùng main_content')
    
    # SEO
    meta_title = models.CharField(max_length=200, verbose_name='Meta Title', null=True, blank=True)
    meta_description = models.TextField(verbose_name='Meta Description', null=True, blank=True)
    
    def get_timeline_items(self):
        """Parse timeline text into structured data"""
        if not self.timeline:
            return []
        
        items = []
        for line in self.timeline.strip().split('\n'):
            if '|' in line:
                parts = line.split('|')
                if len(parts) >= 3:
                    items.append({
                        'year': parts[0].strip(),
                        'title': parts[1].strip(),
                        'description': parts[2].strip()
                    })
        return items
    
    def clean(self):
        if not self.pk and AboutPage.objects.exists():
            raise ValidationError('Chỉ có thể tạo một trang giới thiệu')
    
    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.title
    
    class Meta:
        verbose_name = 'Trang giới thiệu'
        verbose_name_plural = 'Trang giới thiệu'


class UserProfile(models.Model):
    ROLE_CHOICES = [
        ('company', 'Công ty'),
        ('manager', 'Quản lý'),
        ('team_lead', 'Trưởng nhóm'),
        ('staff', 'Nhân viên'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='user_profile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='staff', verbose_name='Vai trò')
    department = models.CharField(max_length=100, blank=True, null=True, verbose_name='Phòng ban')
    phone = models.CharField(max_length=20, blank=True, null=True, verbose_name='Số điện thoại')
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True, verbose_name='Ảnh đại diện')
    bio = models.TextField(blank=True, null=True, verbose_name='Giới thiệu')
    
    # Thông tin chuyên môn
    position = models.CharField(max_length=100, blank=True, null=True, verbose_name='Vị trí công việc')
    certificates = models.TextField(blank=True, null=True, verbose_name='Chứng chỉ', help_text='Danh sách chứng chỉ, mỗi chứng chỉ một dòng')
    skills = models.TextField(blank=True, null=True, verbose_name='Kỹ năng', help_text='Danh sách kỹ năng, mỗi kỹ năng một dòng')
    
    # Thông tin dự án hiện tại
    current_project = models.ForeignKey('Project', on_delete=models.SET_NULL, null=True, blank=True, 
                                       related_name='current_members', verbose_name='Dự án hiện tại')
    project_position = models.CharField(max_length=100, blank=True, null=True, verbose_name='Vị trí trong dự án')
    
    # Thông tin liên hệ khẩn cấp
    emergency_contact = models.CharField(max_length=100, blank=True, null=True, verbose_name='Liên hệ khẩn cấp')
    emergency_phone = models.CharField(max_length=20, blank=True, null=True, verbose_name='SĐT khẩn cấp')
    
    # Ngày tham gia công ty
    join_date = models.DateField(null=True, blank=True, verbose_name='Ngày tham gia')
    
    # Trạng thái
    is_active = models.BooleanField(default=True, verbose_name='Đang hoạt động')
    is_team_lead = models.BooleanField(default=False, verbose_name='Là trưởng nhóm')
    
    # Quyền hạn chi tiết
    can_create_posts = models.BooleanField(default=True, verbose_name='Có thể tạo bài viết')
    can_edit_all_posts = models.BooleanField(default=False, verbose_name='Có thể chỉnh sửa tất cả bài viết')
    can_delete_posts = models.BooleanField(default=False, verbose_name='Có thể xóa bài viết')
    can_publish_posts = models.BooleanField(default=False, verbose_name='Có thể xuất bản bài viết')
    
    can_create_courses = models.BooleanField(default=True, verbose_name='Có thể tạo khóa học')
    can_edit_all_courses = models.BooleanField(default=False, verbose_name='Có thể chỉnh sửa tất cả khóa học')
    can_delete_courses = models.BooleanField(default=False, verbose_name='Có thể xóa khóa học')
    
    can_manage_users = models.BooleanField(default=False, verbose_name='Có thể quản lý người dùng')
    can_view_analytics = models.BooleanField(default=False, verbose_name='Có thể xem thống kê')
    can_manage_settings = models.BooleanField(default=False, verbose_name='Có thể quản lý cài đặt')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def save(self, *args, **kwargs):
        # Tự động cấp quyền dựa trên vai trò
        if self.role == 'admin':
            self.can_edit_all_posts = True
            self.can_delete_posts = True
            self.can_publish_posts = True
            self.can_edit_all_courses = True
            self.can_delete_courses = True
            self.can_manage_users = True
            self.can_view_analytics = True
            self.can_manage_settings = True
            self.user.is_superuser = True
            self.user.is_staff = True
        elif self.role == 'manager':
            self.can_edit_all_posts = True
            self.can_delete_posts = True
            self.can_publish_posts = True
            self.can_edit_all_courses = True
            self.can_delete_courses = True
            self.can_manage_users = False  # Chỉ admin mới quản lý user
            self.can_view_analytics = True
            self.can_manage_settings = False
            self.user.is_staff = True
        elif self.role == 'staff':
            self.can_edit_all_posts = False
            self.can_delete_posts = False
            self.can_publish_posts = False
            self.can_edit_all_courses = False
            self.can_delete_courses = False
            self.can_manage_users = False
            self.can_view_analytics = False
            self.can_manage_settings = False
            self.user.is_staff = True
        
        self.user.save()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f'{self.user.username} - {self.get_role_display()}'
    
    class Meta:
        verbose_name = 'Hồ sơ người dùng'
        verbose_name_plural = 'Hồ sơ người dùng'

# Signal để tự động tạo profile khi tạo user
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'profile'):
        instance.profile.save()

class Company(models.Model):
    """Model cho công ty khách hàng"""
    name = models.CharField(max_length=200, verbose_name='Tên công ty')
    code = models.CharField(max_length=20, unique=True, verbose_name='Mã công ty')
    address = models.TextField(verbose_name='Địa chỉ')
    contact_person = models.CharField(max_length=100, verbose_name='Người liên hệ')
    phone = models.CharField(max_length=20, verbose_name='Số điện thoại')
    email = models.EmailField(verbose_name='Email')
    tax_code = models.CharField(max_length=20, blank=True, verbose_name='Mã số thuế')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = 'Công ty'
        verbose_name_plural = 'Công ty'

class NDTMethod(models.Model):
    """Model cho phương pháp NDT"""
    name = models.CharField(max_length=100, verbose_name='Tên phương pháp')
    code = models.CharField(max_length=10, unique=True, verbose_name='Mã phương pháp')
    description = models.TextField(blank=True, verbose_name='Mô tả')
    
    def __str__(self):
        return f'{self.code} - {self.name}'
    
    class Meta:
        verbose_name = 'Phương pháp NDT'
        verbose_name_plural = 'Phương pháp NDT'

class Equipment(models.Model):
    """Model cho thiết bị NDT"""
    name = models.CharField(max_length=200, verbose_name='Tên thiết bị')
    model = models.CharField(max_length=100, verbose_name='Model')
    serial_number = models.CharField(max_length=100, unique=True, verbose_name='Số serial')
    manufacturer = models.CharField(max_length=100, verbose_name='Nhà sản xuất')
    calibration_date = models.DateField(verbose_name='Ngày hiệu chuẩn')
    next_calibration = models.DateField(verbose_name='Ngày hiệu chuẩn tiếp theo')
    status = models.CharField(max_length=20, choices=[
        ('active', 'Đang sử dụng'),
        ('maintenance', 'Bảo trì'),
        ('retired', 'Ngừng sử dụng')
    ], default='active', verbose_name='Trạng thái')
    
    def __str__(self):
        return f'{self.name} - {self.model}'
    
    class Meta:
        verbose_name = 'Thiết bị'
        verbose_name_plural = 'Thiết bị'

class Project(models.Model):
    """Model cho dự án NDT (nội bộ)"""
    STATUS_CHOICES = [
        ('planning', 'Lập kế hoạch'),
        ('active', 'Đang thực hiện'),
        ('pending', 'Tạm dừng'),
        ('completed', 'Hoàn thành'),
        ('cancelled', 'Đã hủy')
    ]
    
    # Thông tin cơ bản
    name = models.CharField(max_length=200, verbose_name='Tên dự án')
    code = models.CharField(max_length=50, unique=True, verbose_name='Mã dự án')
    
    # Thông tin dự án
    company = models.ForeignKey(Company, on_delete=models.CASCADE, verbose_name='Công ty')
    description = models.TextField(verbose_name='Mô tả dự án')
    location = models.CharField(max_length=200, verbose_name='Địa điểm')
    start_date = models.DateField(verbose_name='Ngày bắt đầu')
    end_date = models.DateField(verbose_name='Ngày kết thúc')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='planning', verbose_name='Trạng thái')
    project_manager = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name='Quản lý dự án')
    methods = models.ManyToManyField(NDTMethod, verbose_name='Phương pháp NDT')
    equipment = models.ManyToManyField(Equipment, verbose_name='Thiết bị sử dụng')
    staff = models.ManyToManyField(User, related_name='assigned_projects', verbose_name='Nhân viên')
    contract_value = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, verbose_name='Giá trị hợp đồng')
    
    # Progress tracking
    completion_percentage = models.PositiveIntegerField(default=0, verbose_name='Phần trăm hoàn thành')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f'{self.code} - {self.name}'
    
    class Meta:
        verbose_name = 'Dự án (Nội bộ)'
        verbose_name_plural = 'Dự án (Nội bộ)'
        ordering = ['-created_at']

class TestReport(models.Model):
    """Model cho báo cáo kiểm tra"""
    project = models.ForeignKey(Project, on_delete=models.CASCADE, verbose_name='Dự án')
    report_number = models.CharField(max_length=50, unique=True, verbose_name='Số báo cáo')
    test_date = models.DateField(verbose_name='Ngày kiểm tra')
    inspector = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Người kiểm tra')
    method = models.ForeignKey(NDTMethod, on_delete=models.CASCADE, verbose_name='Phương pháp')
    equipment_used = models.ManyToManyField(Equipment, verbose_name='Thiết bị sử dụng')
    test_location = models.CharField(max_length=200, verbose_name='Vị trí kiểm tra')
    test_results = models.TextField(verbose_name='Kết quả kiểm tra')
    defects_found = models.TextField(blank=True, verbose_name='Khuyết tật phát hiện')
    recommendations = models.TextField(blank=True, verbose_name='Khuyến nghị')
    report_file = models.FileField(upload_to='reports/%Y/%m/', blank=True, verbose_name='File báo cáo')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f'{self.report_number} - {self.project.name}'
    
    class Meta:
        verbose_name = 'Báo cáo kiểm tra'
        verbose_name_plural = 'Báo cáo kiểm tra'
        ordering = ['-created_at']

class ThicknessData(models.Model):
    """Model cho dữ liệu đo độ dày"""
    project = models.ForeignKey(Project, on_delete=models.CASCADE, verbose_name='Dự án')
    measurement_point = models.CharField(max_length=100, verbose_name='Điểm đo')
    thickness_value = models.DecimalField(max_digits=8, decimal_places=3, verbose_name='Giá trị độ dày (mm)')
    minimum_thickness = models.DecimalField(max_digits=8, decimal_places=3, verbose_name='Độ dày tối thiểu (mm)')
    measurement_date = models.DateTimeField(verbose_name='Thời gian đo')
    inspector = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Người đo')
    equipment = models.ForeignKey(Equipment, on_delete=models.CASCADE, verbose_name='Thiết bị đo')
    temperature = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name='Nhiệt độ (°C)')
    notes = models.TextField(blank=True, verbose_name='Ghi chú')
    
    @property
    def is_acceptable(self):
        return self.thickness_value >= self.minimum_thickness
    
    def __str__(self):
        return f'{self.project.code} - {self.measurement_point}'
    
    class Meta:
        verbose_name = 'Dữ liệu độ dày'
        verbose_name_plural = 'Dữ liệu độ dày'
        ordering = ['-measurement_date']

class WeldData(models.Model):
    """Model cho dữ liệu mối hàn"""
    project = models.ForeignKey(Project, on_delete=models.CASCADE, verbose_name='Dự án')
    weld_id = models.CharField(max_length=100, verbose_name='Mã mối hàn')
    weld_type = models.CharField(max_length=50, verbose_name='Loại mối hàn')
    material = models.CharField(max_length=100, verbose_name='Vật liệu')
    thickness = models.DecimalField(max_digits=8, decimal_places=3, verbose_name='Độ dày (mm)')
    welding_process = models.CharField(max_length=50, verbose_name='Quy trình hàn')
    test_method = models.ForeignKey(NDTMethod, on_delete=models.CASCADE, verbose_name='Phương pháp kiểm tra')
    test_date = models.DateField(verbose_name='Ngày kiểm tra')
    inspector = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Người kiểm tra')
    result = models.CharField(max_length=20, choices=[
        ('accept', 'Đạt'),
        ('reject', 'Không đạt'),
        ('repair', 'Cần sửa chữa')
    ], verbose_name='Kết quả')
    defect_description = models.TextField(blank=True, verbose_name='Mô tả khuyết tật')
    repair_required = models.BooleanField(default=False, verbose_name='Cần sửa chữa')
    
    def __str__(self):
        return f'{self.project.code} - {self.weld_id}'
    
    class Meta:
        verbose_name = 'Dữ liệu mối hàn'
        verbose_name_plural = 'Dữ liệu mối hàn'
        ordering = ['-test_date']
# Thêm vào cuối file models.py

class ProjectFile(models.Model):
    """Model cho file dự án"""
    FILE_TYPES = [
        ('excel', 'Excel'),
        ('pdf', 'PDF'),
        ('word', 'Word'),
        ('image', 'Hình ảnh'),
        ('other', 'Khác')
    ]
    
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='files', verbose_name='Dự án')
    name = models.CharField(max_length=255, verbose_name='Tên file')
    file = models.FileField(upload_to='project_files/%Y/%m/%d/', verbose_name='File')
    file_type = models.CharField(max_length=20, choices=FILE_TYPES, verbose_name='Loại file')
    description = models.TextField(blank=True, verbose_name='Mô tả')
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Người upload')
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name='Thời gian upload')
    version = models.PositiveIntegerField(default=1, verbose_name='Phiên bản')
    is_active = models.BooleanField(default=True, verbose_name='Đang sử dụng')
    
    class Meta:
        verbose_name = 'File dự án'
        verbose_name_plural = 'File dự án'
        ordering = ['-uploaded_at']
    
    def __str__(self):
        return f'{self.name} - {self.project.name}'

class ProjectProgress(models.Model):
    """Model theo dõi tiến độ dự án"""
    project = models.OneToOneField(Project, on_delete=models.CASCADE, related_name='progress')
    completion_percentage = models.PositiveIntegerField(default=0, verbose_name='Phần trăm hoàn thành')
    milestones_completed = models.PositiveIntegerField(default=0, verbose_name='Cột mốc hoàn thành')
    total_milestones = models.PositiveIntegerField(default=0, verbose_name='Tổng cột mốc')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Ngày tạo')  # Thêm trường này
    last_updated = models.DateTimeField(auto_now=True, verbose_name='Cập nhật cuối')
    updated_by = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Người cập nhật')
    notes = models.TextField(blank=True, verbose_name='Ghi chú')
    
    class Meta:
        verbose_name = 'Tiến độ dự án'
        verbose_name_plural = 'Tiến độ dự án'
        ordering = ['-created_at']

# ========== DOCUMENT MANAGEMENT MODELS ==========

class DocumentCategory(models.Model):
    """Danh mục tài liệu"""
    name = models.CharField(max_length=100, verbose_name='Tên danh mục')
    slug = models.SlugField(unique=True, verbose_name='Slug')
    icon = models.CharField(max_length=50, default='fas fa-folder', verbose_name='Icon FontAwesome')
    description = models.TextField(blank=True, verbose_name='Mô tả')
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, 
                              related_name='children', verbose_name='Danh mục cha')
    order = models.PositiveIntegerField(default=0, verbose_name='Thứ tự hiển thị')
    is_active = models.BooleanField(default=True, verbose_name='Kích hoạt')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = 'Danh mục tài liệu'
        verbose_name_plural = 'Danh mục tài liệu'
        ordering = ['order', 'name']

class Document(models.Model):
    """Tài liệu nội bộ"""
    FILE_TYPES = [
        ('pdf', 'PDF'),
        ('doc', 'Word Document'),
        ('docx', 'Word Document (DOCX)'),
        ('xls', 'Excel'),
        ('xlsx', 'Excel (XLSX)'),
        ('ppt', 'PowerPoint'),
        ('pptx', 'PowerPoint (PPTX)'),
        ('txt', 'Text'),
        ('image', 'Hình ảnh'),
        ('video', 'Video'),
        ('zip', 'Archive'),
        ('other', 'Khác')
    ]
    
    ACCESS_LEVELS = [
        ('public', 'Công khai'),
        ('internal', 'Nội bộ'),
        ('restricted', 'Hạn chế'),
        ('confidential', 'Bí mật')
    ]
    
    STATUS_CHOICES = [
        ('draft', 'Bản nháp'),
        ('review', 'Đang xem xét'),
        ('approved', 'Đã phê duyệt'),
        ('published', 'Đã xuất bản'),
        ('archived', 'Lưu trữ')
    ]
    
    title = models.CharField(max_length=200, verbose_name='Tiêu đề tài liệu')
    slug = models.SlugField(unique=True, blank=True, verbose_name='Slug')
    category = models.ForeignKey(DocumentCategory, on_delete=models.CASCADE, 
                                related_name='documents', verbose_name='Danh mục')
    description = models.TextField(blank=True, verbose_name='Mô tả')
    file = models.FileField(upload_to='documents/%Y/%m/%d/', verbose_name='File tài liệu')
    file_type = models.CharField(max_length=20, choices=FILE_TYPES, verbose_name='Loại file')
    file_size = models.PositiveIntegerField(null=True, blank=True, verbose_name='Kích thước file (bytes)')
    
    # Metadata
    version = models.CharField(max_length=10, default='1.0', verbose_name='Phiên bản')
    document_code = models.CharField(max_length=50, unique=True, verbose_name='Mã tài liệu')
    tags = models.ManyToManyField('DocumentTag', blank=True, verbose_name='Thẻ tags')
    
    # Access control
    access_level = models.CharField(max_length=20, choices=ACCESS_LEVELS, 
                                   default='internal', verbose_name='Mức độ truy cập')
    allowed_roles = models.CharField(max_length=100, blank=True, 
                                    help_text='Các vai trò được phép truy cập (admin,manager,staff)',
                                    verbose_name='Vai trò được phép')
    
    # Status và approval
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, 
                             default='draft', verbose_name='Trạng thái')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, 
                                  related_name='created_documents', verbose_name='Người tạo')
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name='approved_documents', verbose_name='Người phê duyệt')
    approved_at = models.DateTimeField(null=True, blank=True, verbose_name='Thời gian phê duyệt')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Ngày tạo')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Ngày cập nhật')
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                  related_name='updated_documents', verbose_name='Người cập nhật cuối')
    
    # Analytics
    download_count = models.PositiveIntegerField(default=0, verbose_name='Số lượt tải')
    view_count = models.PositiveIntegerField(default=0, verbose_name='Số lượt xem')
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        
        # Auto-detect file type from extension
        if self.file and not self.file_type:
            ext = self.file.name.split('.')[-1].lower()
            type_mapping = {
                'pdf': 'pdf', 'doc': 'doc', 'docx': 'docx',
                'xls': 'xls', 'xlsx': 'xlsx', 'ppt': 'ppt', 'pptx': 'pptx',
                'txt': 'txt', 'jpg': 'image', 'jpeg': 'image', 'png': 'image', 
                'gif': 'image', 'mp4': 'video', 'avi': 'video', 'zip': 'zip', 'rar': 'zip'
            }
            self.file_type = type_mapping.get(ext, 'other')
        
        # Get file size
        if self.file and hasattr(self.file, 'size'):
            self.file_size = self.file.size
            
        super().save(*args, **kwargs)
    
    def get_file_icon(self):
        """Trả về icon FontAwesome cho loại file"""
        icons = {
            'pdf': 'fas fa-file-pdf text-danger',
            'doc': 'fas fa-file-word text-primary', 
            'docx': 'fas fa-file-word text-primary',
            'xls': 'fas fa-file-excel text-success',
            'xlsx': 'fas fa-file-excel text-success',
            'ppt': 'fas fa-file-powerpoint text-warning',
            'pptx': 'fas fa-file-powerpoint text-warning',
            'txt': 'fas fa-file-alt text-secondary',
            'image': 'fas fa-file-image text-info',
            'video': 'fas fa-file-video text-purple',
            'zip': 'fas fa-file-archive text-dark',
            'other': 'fas fa-file text-muted'
        }
        return icons.get(self.file_type, icons['other'])
    
    def get_file_size_display(self):
        """Hiển thị kích thước file dễ đọc"""
        if not self.file_size:
            return 'N/A'
        
        size = self.file_size
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} TB"
    
    def can_access(self, user):
        """Kiểm tra quyền truy cập của user"""
        if not user.is_authenticated:
            return self.access_level == 'public'
        
        if user.is_superuser:
            return True
            
        profile = getattr(user, 'user_profile', None)
        if not profile:
            return False
            
        # Check role-based access
        if self.allowed_roles:
            allowed = [role.strip() for role in self.allowed_roles.split(',')]
            if profile.role not in allowed:
                return False
        
        # Check access level
        if self.access_level == 'public':
            return True
        elif self.access_level == 'internal':
            return True
        elif self.access_level == 'restricted':
            return profile.role in ['manager', 'admin']
        elif self.access_level == 'confidential':
            return profile.role == 'admin'
            
        return False
    
    def __str__(self):
        return self.title
    
    class Meta:
        verbose_name = 'Tài liệu'
        verbose_name_plural = 'Tài liệu'
        ordering = ['-created_at']

class DocumentTag(models.Model):
    """Tags cho tài liệu"""
    name = models.CharField(max_length=50, unique=True, verbose_name='Tên tag')
    slug = models.SlugField(unique=True, verbose_name='Slug')
    color = models.CharField(max_length=7, default='#007bff', verbose_name='Màu hiển thị')
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = 'Tag tài liệu'
        verbose_name_plural = 'Tag tài liệu'
        ordering = ['name']

class DocumentVersion(models.Model):
    """Lịch sử phiên bản tài liệu"""
    document = models.ForeignKey(Document, on_delete=models.CASCADE, 
                                related_name='versions', verbose_name='Tài liệu')
    version = models.CharField(max_length=10, verbose_name='Số phiên bản')
    file = models.FileField(upload_to='document_versions/%Y/%m/%d/', verbose_name='File phiên bản')
    change_log = models.TextField(verbose_name='Nhật ký thay đổi')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Người tạo')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Ngày tạo')
    
    def __str__(self):
        return f"{self.document.title} v{self.version}"
    
    class Meta:
        verbose_name = 'Phiên bản tài liệu'
        verbose_name_plural = 'Phiên bản tài liệu'
        ordering = ['-created_at']
        unique_together = ['document', 'version']

class DocumentAccess(models.Model):
    """Log truy cập tài liệu"""
    ACTION_CHOICES = [
        ('view', 'Xem'),
        ('download', 'Tải xuống'),
        ('share', 'Chia sẻ')
    ]
    
    document = models.ForeignKey(Document, on_delete=models.CASCADE, 
                                related_name='access_logs', verbose_name='Tài liệu')
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Người dùng')
    action = models.CharField(max_length=20, choices=ACTION_CHOICES, verbose_name='Hành động')
    ip_address = models.GenericIPAddressField(verbose_name='Địa chỉ IP')
    user_agent = models.TextField(blank=True, verbose_name='User Agent')
    accessed_at = models.DateTimeField(auto_now_add=True, verbose_name='Thời gian truy cập')
    
    def __str__(self):
        return f'{self.user.username} - {self.document.title} - {self.action}'
    
    class Meta:
        verbose_name = 'Lịch sử truy cập'
        verbose_name_plural = 'Lịch sử truy cập'
        ordering = ['-accessed_at']

class HomePageSettings(models.Model):
    """Model quản lý nội dung trang chủ"""
    
    # Hero Section
    hero_title = models.CharField(max_length=200, default='HITECH NDT', verbose_name='Tiêu đề Hero')
    hero_subtitle = models.TextField(default='Giải pháp kiểm tra không phá hủy hàng đầu Việt Nam', verbose_name='Phụ đề Hero')
    hero_bg_image = models.ImageField(upload_to='homepage/hero/', null=True, blank=True, verbose_name='Ảnh nền Hero')
    hero_bg_color = ColorField(default='#003d99', verbose_name='Màu nền Hero (khi không có ảnh)')
    hero_btn_primary_text = models.CharField(max_length=50, default='Khám phá dịch vụ', verbose_name='Nút chính - Text')
    hero_btn_primary_url = models.CharField(max_length=100, default='/dich-vu/', verbose_name='Nút chính - URL')
    hero_btn_secondary_text = models.CharField(max_length=50, default='Liên hệ ngay', verbose_name='Nút phụ - Text')
    hero_btn_secondary_url = models.CharField(max_length=100, default='/lien-he/', verbose_name='Nút phụ - URL')
    
    # NDT Methods Section
    ndt_section_title = models.CharField(max_length=200, default='Phương pháp NDT chuyên nghiệp', verbose_name='Tiêu đề phần Phương pháp NDT')
    ndt_section_subtitle = models.TextField(default='Ứng dụng các công nghệ kiểm tra không phá hủy tiên tiến nhất', verbose_name='Phụ đề phần NDT')
    ndt_bg_image = models.ImageField(upload_to='homepage/sections/', null=True, blank=True, verbose_name='Ảnh nền phần NDT')
    ndt_bg_color = ColorField(default='#f8f9fa', verbose_name='Màu nền phần NDT (khi không có ảnh)')
    ndt_overlay_opacity = models.DecimalField(max_digits=3, decimal_places=2, default=0.85, verbose_name='Độ mờ overlay NDT (0.0-1.0)')
    
    # Projects Section
    projects_section_title = models.CharField(max_length=200, default='Dự án nổi bật', verbose_name='Tiêu đề phần Dự án')
    projects_section_subtitle = models.TextField(default='Những dự án tiêu biểu đã thực hiện thành công', verbose_name='Phụ đề phần Dự án')
    projects_bg_color = ColorField(default='#ffffff', verbose_name='Màu nền phần Dự án')
    
    # Blog Section
    blog_section_title = models.CharField(max_length=200, default='Tin tức & Bài viết', verbose_name='Tiêu đề phần Blog')
    blog_section_subtitle = models.TextField(default='Cập nhật những thông tin mới nhất về công nghệ NDT', verbose_name='Phụ đề phần Blog')
    blog_bg_color = ColorField(default='#f8f9fa', verbose_name='Màu nền phần Blog')
    
    # Services Section
    services_section_title = models.CharField(max_length=200, default='Dịch vụ chuyên nghiệp', verbose_name='Tiêu đề phần Dịch vụ')
    services_section_subtitle = models.TextField(default='Giải pháp toàn diện cho mọi nhu cầu kiểm tra và đào tạo', verbose_name='Phụ đề phần Dịch vụ')
    services_bg_color = ColorField(default='#ffffff', verbose_name='Màu nền phần Dịch vụ')
    
    # Testimonials Section
    testimonials_section_title = models.CharField(max_length=200, default='Khách hàng nói về chúng tôi', verbose_name='Tiêu đề phần Testimonials')
    testimonials_section_subtitle = models.TextField(default='Phản hồi từ những khách hàng đã tin tưởng sử dụng dịch vụ', verbose_name='Phụ đề phần Testimonials')
    testimonials_bg_image = models.ImageField(upload_to='homepage/sections/', null=True, blank=True, verbose_name='Ảnh nền phần Testimonials')
    testimonials_bg_color = ColorField(default='#667eea', verbose_name='Màu nền phần Testimonials (khi không có ảnh)')
    testimonials_overlay_opacity = models.DecimalField(max_digits=3, decimal_places=2, default=0.90, verbose_name='Độ mờ overlay Testimonials (0.0-1.0)')
    
    # Testimonials Content Management
    testimonial1_content = models.TextField(default='Hitech NDT đã cung cấp dịch vụ kiểm tra chất lượng cao cho dự án của chúng tôi. Đội ngũ chuyên nghiệp, thiết bị hiện đại và báo cáo chi tiết, chính xác.', verbose_name='Testimonial 1 - Nội dung')
    testimonial1_name = models.CharField(max_length=100, default='Trần Văn Long', verbose_name='Testimonial 1 - Tên')
    testimonial1_position = models.CharField(max_length=100, default='Trưởng phòng kỹ thuật', verbose_name='Testimonial 1 - Chức vụ')
    testimonial1_company = models.CharField(max_length=100, default='Công ty TNHH ABC', verbose_name='Testimonial 1 - Công ty')
    testimonial1_avatar = models.ImageField(upload_to='homepage/testimonials/', null=True, blank=True, verbose_name='Testimonial 1 - Ảnh đại diện')
    
    testimonial2_content = models.TextField(default='Dịch vụ đào tạo chứng chỉ NDT Level II tại Hitech rất chuyên nghiệp. Giáo viên giàu kinh nghiệm, tài liệu đầy đủ và thiết bị thực hành hiện đại.', verbose_name='Testimonial 2 - Nội dung')
    testimonial2_name = models.CharField(max_length=100, default='Nguyễn Thanh Huy', verbose_name='Testimonial 2 - Tên')
    testimonial2_position = models.CharField(max_length=100, default='Kỹ sư NDT', verbose_name='Testimonial 2 - Chức vụ')
    testimonial2_company = models.CharField(max_length=100, default='Tập đoàn Dầu khí Việt Nam', verbose_name='Testimonial 2 - Công ty')
    testimonial2_avatar = models.ImageField(upload_to='homepage/testimonials/', null=True, blank=True, verbose_name='Testimonial 2 - Ảnh đại diện')
    
    testimonial3_content = models.TextField(default='Hitech NDT luôn đáp ứng đúng tiến độ và chất lượng cam kết. Đây là đối tác tin cậy cho các dự án kiểm tra của chúng tôi.', verbose_name='Testimonial 3 - Nội dung')
    testimonial3_name = models.CharField(max_length=100, default='Mai Thị Thuỷ', verbose_name='Testimonial 3 - Tên')
    testimonial3_position = models.CharField(max_length=100, default='Giám đốc kỹ thuật', verbose_name='Testimonial 3 - Chức vụ')
    testimonial3_company = models.CharField(max_length=100, default='Công ty Cơ khí XYZ', verbose_name='Testimonial 3 - Công ty')
    testimonial3_avatar = models.ImageField(upload_to='homepage/testimonials/', null=True, blank=True, verbose_name='Testimonial 3 - Ảnh đại diện')
    
    testimonial4_content = models.TextField(default='Thiết bị kiểm tra được Hitech cung cấp rất hiện đại và chính xác. Hỗ trợ kỹ thuật 24/7 giúp chúng tôi yên tâm trong quá trình thực hiện dự án.', verbose_name='Testimonial 4 - Nội dung')
    testimonial4_name = models.CharField(max_length=100, default='Phạm Văn Dũng', verbose_name='Testimonial 4 - Tên')
    testimonial4_position = models.CharField(max_length=100, default='Chuyên viên kiểm tra', verbose_name='Testimonial 4 - Chức vụ')
    testimonial4_company = models.CharField(max_length=100, default='Nhà máy Thép Hòa Phát', verbose_name='Testimonial 4 - Công ty')
    testimonial4_avatar = models.ImageField(upload_to='homepage/testimonials/', null=True, blank=True, verbose_name='Testimonial 4 - Ảnh đại diện')
    
    testimonial5_content = models.TextField(default='Báo cáo kiểm tra từ Hitech luôn chi tiết, rõ ràng và đúng tiêu chuẩn quốc tế. Điều này giúp chúng tôi thuyết phục được khách hàng quốc tế.', verbose_name='Testimonial 5 - Nội dung')
    testimonial5_name = models.CharField(max_length=100, default='Lê Minh Khang', verbose_name='Testimonial 5 - Tên')
    testimonial5_position = models.CharField(max_length=100, default='QA Manager', verbose_name='Testimonial 5 - Chức vụ')
    testimonial5_company = models.CharField(max_length=100, default='Samsung Electronics Vietnam', verbose_name='Testimonial 5 - Công ty')
    testimonial5_avatar = models.ImageField(upload_to='homepage/testimonials/', null=True, blank=True, verbose_name='Testimonial 5 - Ảnh đại diện')
    
    # Partners Section
    partners_section_title = models.CharField(max_length=200, default='Đối tác tin cậy', verbose_name='Tiêu đề phần Đối tác')
    partners_section_subtitle = models.TextField(default='Được tin tưởng bởi các doanh nghiệp hàng đầu trong và ngoài nước', verbose_name='Phụ đề phần Đối tác')
    partners_bg_image = models.ImageField(upload_to='homepage/sections/', null=True, blank=True, verbose_name='Ảnh nền phần Đối tác')
    partners_bg_color = ColorField(default='#f5f7fa', verbose_name='Màu nền phần Đối tác (khi không có ảnh)')
    partners_overlay_opacity = models.DecimalField(max_digits=3, decimal_places=2, default=0.95, verbose_name='Độ mờ overlay Đối tác (0.0-1.0)')
    
    # Trust Indicators (Partners section)
    trust_stat1_number = models.CharField(max_length=20, default='100+', verbose_name='Số liệu tin cậy 1')
    trust_stat1_label = models.CharField(max_length=100, default='Đối tác tin cậy', verbose_name='Nhãn số liệu 1')
    trust_stat2_number = models.CharField(max_length=20, default='500+', verbose_name='Số liệu tin cậy 2')
    trust_stat2_label = models.CharField(max_length=100, default='Dự án thành công', verbose_name='Nhãn số liệu 2')
    trust_stat3_number = models.CharField(max_length=20, default='15+', verbose_name='Số liệu tin cậy 3')
    trust_stat3_label = models.CharField(max_length=100, default='Năm kinh nghiệm', verbose_name='Nhãn số liệu 3')
    trust_stat4_number = models.CharField(max_length=20, default='24/7', verbose_name='Số liệu tin cậy 4')
    trust_stat4_label = models.CharField(max_length=100, default='Hỗ trợ khách hàng', verbose_name='Nhãn số liệu 4')
    
    # Why Choose Us Section
    why_section_title = models.CharField(max_length=200, default='Vì sao chọn Hitech NDT?', verbose_name='Tiêu đề phần Vì sao chọn')
    why_section_subtitle = models.TextField(default='Những giá trị cốt lõi làm nên thương hiệu Hitech NDT', verbose_name='Phụ đề phần Vì sao chọn')
    why_bg_color = ColorField(default='#ffffff', verbose_name='Màu nền phần Vì sao chọn')
    
    # Partner Logos Management
    partner1_name = models.CharField(max_length=100, default='PetroVietnam', verbose_name='Đối tác 1 - Tên')
    partner1_logo = models.ImageField(upload_to='homepage/partners/', null=True, blank=True, verbose_name='Đối tác 1 - Logo')
    partner1_icon = models.CharField(max_length=50, default='fas fa-industry', verbose_name='Đối tác 1 - Icon (fallback)')
    
    partner2_name = models.CharField(max_length=100, default='Samsung', verbose_name='Đối tác 2 - Tên')
    partner2_logo = models.ImageField(upload_to='homepage/partners/', null=True, blank=True, verbose_name='Đối tác 2 - Logo')
    partner2_icon = models.CharField(max_length=50, default='fas fa-mobile-alt', verbose_name='Đối tác 2 - Icon (fallback)')
    
    partner3_name = models.CharField(max_length=100, default='Hòa Phát', verbose_name='Đối tác 3 - Tên')
    partner3_logo = models.ImageField(upload_to='homepage/partners/', null=True, blank=True, verbose_name='Đối tác 3 - Logo')
    partner3_icon = models.CharField(max_length=50, default='fas fa-industry', verbose_name='Đối tác 3 - Icon (fallback)')
    
    partner4_name = models.CharField(max_length=100, default='Vingroup', verbose_name='Đối tác 4 - Tên')
    partner4_logo = models.ImageField(upload_to='homepage/partners/', null=True, blank=True, verbose_name='Đối tác 4 - Logo')
    partner4_icon = models.CharField(max_length=50, default='fas fa-building', verbose_name='Đối tác 4 - Icon (fallback)')
    
    partner5_name = models.CharField(max_length=100, default='FPT', verbose_name='Đối tác 5 - Tên')
    partner5_logo = models.ImageField(upload_to='homepage/partners/', null=True, blank=True, verbose_name='Đối tác 5 - Logo')
    partner5_icon = models.CharField(max_length=50, default='fas fa-laptop-code', verbose_name='Đối tác 5 - Icon (fallback)')
    
    partner6_name = models.CharField(max_length=100, default='Viettel', verbose_name='Đối tác 6 - Tên')
    partner6_logo = models.ImageField(upload_to='homepage/partners/', null=True, blank=True, verbose_name='Đối tác 6 - Logo')
    partner6_icon = models.CharField(max_length=50, default='fas fa-satellite-dish', verbose_name='Đối tác 6 - Icon (fallback)')
    
    partner7_name = models.CharField(max_length=100, default='VNSteel', verbose_name='Đối tác 7 - Tên')
    partner7_logo = models.ImageField(upload_to='homepage/partners/', null=True, blank=True, verbose_name='Đối tác 7 - Logo')
    partner7_icon = models.CharField(max_length=50, default='fas fa-hammer', verbose_name='Đối tác 7 - Icon (fallback)')
    
    partner8_name = models.CharField(max_length=100, default='Honda', verbose_name='Đối tác 8 - Tên')
    partner8_logo = models.ImageField(upload_to='homepage/partners/', null=True, blank=True, verbose_name='Đối tác 8 - Logo')
    partner8_icon = models.CharField(max_length=50, default='fas fa-motorcycle', verbose_name='Đối tác 8 - Icon (fallback)')
    
    partner9_name = models.CharField(max_length=100, default='Toyota', verbose_name='Đối tác 9 - Tên')
    partner9_logo = models.ImageField(upload_to='homepage/partners/', null=True, blank=True, verbose_name='Đối tác 9 - Logo')
    partner9_icon = models.CharField(max_length=50, default='fas fa-car', verbose_name='Đối tác 9 - Icon (fallback)')
    
    partner10_name = models.CharField(max_length=100, default='SABIC', verbose_name='Đối tác 10 - Tên')
    partner10_logo = models.ImageField(upload_to='homepage/partners/', null=True, blank=True, verbose_name='Đối tác 10 - Logo')
    partner10_icon = models.CharField(max_length=50, default='fas fa-flask', verbose_name='Đối tác 10 - Icon (fallback)')
    
    partner11_name = models.CharField(max_length=100, default='Chevron', verbose_name='Đối tác 11 - Tên')
    partner11_logo = models.ImageField(upload_to='homepage/partners/', null=True, blank=True, verbose_name='Đối tác 11 - Logo')
    partner11_icon = models.CharField(max_length=50, default='fas fa-oil-can', verbose_name='Đối tác 11 - Icon (fallback)')
    
    partner12_name = models.CharField(max_length=100, default='General Electric', verbose_name='Đối tác 12 - Tên')
    partner12_logo = models.ImageField(upload_to='homepage/partners/', null=True, blank=True, verbose_name='Đối tác 12 - Logo')
    partner12_icon = models.CharField(max_length=50, default='fas fa-bolt', verbose_name='Đối tác 12 - Icon (fallback)')
    
    # Why Choose Us Features
    feature1_title = models.CharField(max_length=100, default='Chuyên nghiệp', verbose_name='Tính năng 1 - Tiêu đề')
    feature1_description = models.TextField(default='Đội ngũ kỹ sư có chứng chỉ quốc tế và kinh nghiệm thực tiễn', verbose_name='Tính năng 1 - Mô tả')
    feature1_icon = models.CharField(max_length=50, default='fas fa-medal', verbose_name='Tính năng 1 - Icon')
    
    feature2_title = models.CharField(max_length=100, default='Công nghệ tiên tiến', verbose_name='Tính năng 2 - Tiêu đề')
    feature2_description = models.TextField(default='Trang thiết bị hiện đại nhập khẩu từ các nước phát triển', verbose_name='Tính năng 2 - Mô tả')
    feature2_icon = models.CharField(max_length=50, default='fas fa-rocket', verbose_name='Tính năng 2 - Icon')
    
    feature3_title = models.CharField(max_length=100, default='Nhanh chóng', verbose_name='Tính năng 3 - Tiêu đề')
    feature3_description = models.TextField(default='Thời gian thực hiện nhanh, báo cáo kết quả chính xác', verbose_name='Tính năng 3 - Mô tả')
    feature3_icon = models.CharField(max_length=50, default='fas fa-clock', verbose_name='Tính năng 3 - Icon')
    
    feature4_title = models.CharField(max_length=100, default='Tin cậy', verbose_name='Tính năng 4 - Tiêu đề')
    feature4_description = models.TextField(default='Được hàng trăm khách hàng lớn tin tưởng và hợp tác lâu dài', verbose_name='Tính năng 4 - Mô tả')
    feature4_icon = models.CharField(max_length=50, default='fas fa-handshake', verbose_name='Tính năng 4 - Icon')
    
    # SEO Settings
    meta_title = models.CharField(max_length=200, blank=True, verbose_name='Meta Title')
    meta_description = models.TextField(blank=True, verbose_name='Meta Description')
    meta_keywords = models.CharField(max_length=300, blank=True, verbose_name='Meta Keywords')
    
    # General Settings
    show_ndt_section = models.BooleanField(default=True, verbose_name='Hiển thị phần Phương pháp NDT')
    show_projects_section = models.BooleanField(default=True, verbose_name='Hiển thị phần Dự án')
    show_blog_section = models.BooleanField(default=True, verbose_name='Hiển thị phần Blog')
    show_services_section = models.BooleanField(default=True, verbose_name='Hiển thị phần Dịch vụ')
    show_testimonials_section = models.BooleanField(default=True, verbose_name='Hiển thị phần Testimonials')
    show_partners_section = models.BooleanField(default=True, verbose_name='Hiển thị phần Đối tác')
    show_why_section = models.BooleanField(default=True, verbose_name='Hiển thị phần Vì sao chọn')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Người cập nhật cuối')
    
    def clean(self):
        # Đảm bảo chỉ có một bản ghi cấu hình
        if not self.pk and HomePageSettings.objects.exists():
            raise ValidationError('Chỉ có thể tạo một bản ghi cấu hình trang chủ')
    
    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return 'Cấu hình trang chủ'
    
    class Meta:
        verbose_name = 'Cấu hình trang chủ'
        verbose_name_plural = 'Cấu hình trang chủ'


class PublicProject(models.Model):
    """Model cho dự án công khai (khoe dự án)"""
    STATUS_CHOICES = [
        ('completed', 'Hoàn thành'),
        ('ongoing', 'Đang thực hiện'),
        ('featured', 'Nổi bật'),
    ]
    
    # Thông tin cơ bản
    title = models.CharField(max_length=200, verbose_name='Tiêu đề dự án')
    slug = models.SlugField(unique=True, blank=True, verbose_name='Slug URL')
    featured_image = models.ImageField(upload_to='public_projects/%Y/%m/', null=True, blank=True, verbose_name='Ảnh đại diện')
    
    # Nội dung
    summary = models.TextField(verbose_name='Tóm tắt dự án')
    content = CKEditor5Field(verbose_name='Nội dung chi tiết')
    
    # Thông tin hiển thị
    client_name = models.CharField(max_length=200, verbose_name='Tên khách hàng')
    location = models.CharField(max_length=200, verbose_name='Địa điểm')
    project_type = models.CharField(max_length=100, verbose_name='Loại dự án')
    completion_date = models.DateField(verbose_name='Ngày hoàn thành')
    project_value = models.CharField(max_length=100, blank=True, verbose_name='Giá trị dự án (text)')
    
    # Tags và categories
    tags = models.CharField(max_length=200, blank=True, help_text='Các tag cách nhau bằng dấu phẩy', verbose_name='Tags')
    
    # Trạng thái
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='completed', verbose_name='Trạng thái')
    is_featured = models.BooleanField(default=False, verbose_name='Dự án nổi bật')
    published = models.BooleanField(default=True, verbose_name='Xuất bản')
    
    # SEO
    meta_title = models.CharField(max_length=200, blank=True, verbose_name='Meta Title')
    meta_description = models.TextField(blank=True, verbose_name='Meta Description')
    
    # Analytics
    view_count = models.PositiveIntegerField(default=0, verbose_name='Lượt xem')
    
    # Author and timestamps
    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Người tạo')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Ngày tạo')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Ngày cập nhật')
    
    def save(self, *args, **kwargs):
        if not self.slug:
            from django.utils.text import slugify
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1
            while PublicProject.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return f'/dich-vu/du-an/{self.slug}/'
    
    def get_tags_list(self):
        if self.tags:
            return [tag.strip() for tag in self.tags.split(',')]
        return []
    
    def __str__(self):
        return self.title
    
    class Meta:
        verbose_name = 'Dự án công khai'
        verbose_name_plural = 'Dự án công khai'
        ordering = ['-created_at']


class LeaveRequest(models.Model):
    """Model cho yêu cầu nghỉ phép với hệ thống 3 cấp phê duyệt"""
    
    STATUS_CHOICES = [
        ('pending', 'Chờ phê duyệt'),
        ('approved', 'Đã duyệt'),
        ('rejected', 'Từ chối'),
        ('cancelled', 'Đã hủy')
    ]
    
    LEAVE_TYPE_CHOICES = [
        ('annual', 'Nghỉ phép năm'),
        ('sick', 'Nghỉ ốm'),
        ('personal', 'Nghỉ việc riêng'),
        ('maternity', 'Nghỉ thai sản'),
        ('other', 'Khác')
    ]
    
    # Thông tin cơ bản
    employee = models.ForeignKey(User, on_delete=models.CASCADE, related_name='leave_requests', verbose_name='Nhân viên')
    leave_type = models.CharField(max_length=20, choices=LEAVE_TYPE_CHOICES, verbose_name='Loại nghỉ phép')
    start_date = models.DateField(verbose_name='Ngày bắt đầu')
    end_date = models.DateField(verbose_name='Ngày kết thúc')
    total_days = models.PositiveIntegerField(verbose_name='Tổng số ngày')
    reason = models.TextField(verbose_name='Lý do nghỉ phép')
    
    # Thông tin bàn giao
    handover_person = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, 
                                       related_name='handover_requests', verbose_name='Người bàn giao')
    handover_tasks = models.TextField(blank=True, verbose_name='Công việc bàn giao')
    
    # Trạng thái tổng thể
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='Trạng thái')
    final_decision_reason = models.TextField(blank=True, verbose_name='Lý do quyết định cuối cùng')
    
    # Phê duyệt 3 cấp: Người bàn giao, Quản lý, Công ty
    handover_approval = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='Phê duyệt người bàn giao')
    handover_approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, 
                                             related_name='handover_approvals', verbose_name='Người bàn giao phê duyệt')
    handover_approved_at = models.DateTimeField(null=True, blank=True, verbose_name='Thời gian phê duyệt người bàn giao')
    handover_rejection_reason = models.TextField(blank=True, verbose_name='Lý do từ chối người bàn giao')

    # Cấp 2: Quản lý
    manager_approval = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='Phê duyệt quản lý')
    manager_approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, 
                                          related_name='manager_approvals', verbose_name='Quản lý phê duyệt')
    manager_approved_at = models.DateTimeField(null=True, blank=True, verbose_name='Thời gian phê duyệt quản lý')
    manager_rejection_reason = models.TextField(blank=True, verbose_name='Lý do từ chối quản lý')

    # Cấp 3: Công ty
    company_approval = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='Phê duyệt công ty')
    company_approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, 
                                          related_name='company_approvals', verbose_name='Công ty phê duyệt')
    company_approved_at = models.DateTimeField(null=True, blank=True, verbose_name='Thời gian phê duyệt công ty')
    company_rejection_reason = models.TextField(blank=True, verbose_name='Lý do từ chối công ty')

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Ngày tạo')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Ngày cập nhật')

    def __str__(self):
        return f'{self.employee.get_full_name()} - {self.get_leave_type_display()} ({self.start_date} đến {self.end_date})'

    def get_final_status(self):
        """Lấy trạng thái cuối cùng dựa trên logic phân cấp"""
        # Nếu có cấp cao từ chối thì từ chối
        if self.company_approval == 'rejected':
            return 'rejected', 'Công ty từ chối', self.company_rejection_reason
        elif self.manager_approval == 'rejected':
            return 'rejected', 'Quản lý từ chối', self.manager_rejection_reason
        elif self.handover_approval == 'rejected':
            return 'rejected', 'Người bàn giao từ chối', self.handover_rejection_reason
        # Nếu tất cả cấp đã duyệt thì duyệt
        if (self.handover_approval == 'approved' and 
            self.manager_approval == 'approved' and 
            self.company_approval == 'approved'):
            return 'approved', 'Đã duyệt', ''
        # Nếu chưa có cấp nào từ chối và chưa đủ cấp duyệt thì chờ
        return 'pending', 'Chờ phê duyệt', ''

    def can_approve(self, user):
        """Kiểm tra user có thể phê duyệt không"""
        user_role = getattr(user.user_profile, 'role', 'staff')
        
        # Admin có thể phê duyệt ở BẤT KỲ cấp nào còn pending
        if user_role == 'admin':
            return (self.company_approval == 'pending' or 
                   self.manager_approval == 'pending' or 
                   self.handover_approval == 'pending')
        
        # Công ty có thể phê duyệt ở BẤT KỲ cấp nào còn pending
        if user_role == 'company':
            return (self.company_approval == 'pending' or 
                   self.manager_approval == 'pending' or 
                   self.handover_approval == 'pending')
            
        # Quản lý có thể phê duyệt cấp manager và handover
        if user_role == 'manager':
            return (self.manager_approval == 'pending' or 
                   self.handover_approval == 'pending')
            
        # Người bàn giao chỉ có thể phê duyệt cấp của mình (cấp 1)
        if self.handover_person and user == self.handover_person:
            return self.handover_approval == 'pending'
            
        return False

    def get_required_approvals(self, requester_role):
        """Lấy danh sách cấp cần phê duyệt dựa trên vai trò người yêu cầu"""
        if requester_role == 'company':
            return []  # Công ty không cần phê duyệt
        if requester_role == 'manager':
            return ['company']  # Quản lý chỉ cần công ty phê duyệt
        if requester_role == 'staff':
            return ['handover', 'manager', 'company']  # Nhân viên cần tất cả 3 cấp
        return ['handover', 'manager', 'company']  # Mặc định

    def get_pending_approvals(self):
        """Lấy danh sách các cấp đang chờ phê duyệt"""
        pending = []
        if self.handover_approval == 'pending':
            pending.append('handover')
        if self.manager_approval == 'pending':
            pending.append('manager')
        if self.company_approval == 'pending':
            pending.append('company')
        return pending

    class Meta:
        verbose_name = 'Yêu cầu nghỉ phép'
        verbose_name_plural = 'Yêu cầu nghỉ phép'
        ordering = ['-created_at']

# Thêm vào cuối file models.py

class Attendance(models.Model):
    """Model cho dữ liệu chấm công"""
    
    WORK_TYPE_CHOICES = [
        ('W', 'Công trường'),
        ('O', 'Văn phòng'),
        ('T', 'Đào tạo'),
        ('P', 'Nghỉ có phép'),
        ('N', 'Nghỉ không phép'),
    ]
    
    # Thông tin cơ bản
    employee = models.ForeignKey(User, on_delete=models.CASCADE, related_name='attendances', verbose_name='Nhân viên')
    date = models.DateField(verbose_name='Ngày chấm công')
    work_type = models.CharField(max_length=1, choices=WORK_TYPE_CHOICES, verbose_name='Loại công việc')
    
    # Thông tin công trường (nếu work_type = 'W')
    construction_name = models.CharField(max_length=200, blank=True, verbose_name='Tên công trình')
    ndt_method = models.CharField(max_length=100, blank=True, verbose_name='Phương pháp NDT')
    
    # Số mét vượt cho PAUT và TOFD
    paut_meters = models.DecimalField(max_digits=8, decimal_places=2, default=0, verbose_name='Số mét vượt PAUT')
    tofd_meters = models.DecimalField(max_digits=8, decimal_places=2, default=0, verbose_name='Số mét vượt TOFD')
    
    # Ca làm việc
    day_shift = models.BooleanField(default=False, verbose_name='Ca ngày')
    night_shift = models.BooleanField(default=False, verbose_name='Ca đêm')
    day_overtime_end = models.TimeField(null=True, blank=True, verbose_name='Tăng ca ngày đến')
    night_overtime_end = models.TimeField(null=True, blank=True, verbose_name='Tăng ca đêm đến')
    overtime_hours = models.DecimalField(max_digits=4, decimal_places=2, default=0, verbose_name='Số giờ tăng ca')
    
    # Chi phí
    hotel_expense = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='Chi phí khách sạn (VNĐ)')
    shopping_expense = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='Chi phí mua sắm (VNĐ)')
    phone_expense = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='Chi phí điện thoại (VNĐ)')
    other_expense = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='Chi phí khác (VNĐ)')
    other_expense_desc = models.TextField(blank=True, verbose_name='Mô tả chi phí khác')
    
    # Ghi chú
    work_note = models.TextField(blank=True, verbose_name='Ghi chú công việc')
    
    # Liên kết với LeaveRequest (nếu có)
    leave_request = models.ForeignKey(LeaveRequest, on_delete=models.SET_NULL, null=True, blank=True, 
                                     related_name='attendance_records', verbose_name='Yêu cầu nghỉ phép liên quan')
    
    # Trạng thái
    is_auto_generated = models.BooleanField(default=False, verbose_name='Tự động tạo từ yêu cầu nghỉ phép')
    can_be_edited = models.BooleanField(default=True, verbose_name='Có thể chỉnh sửa')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Ngày tạo')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Ngày cập nhật')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_attendances', 
                                  verbose_name='Người tạo')
    updated_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='updated_attendances', 
                                  verbose_name='Người cập nhật cuối')
    
    class Meta:
        verbose_name = 'Chấm công'
        verbose_name_plural = 'Chấm công'
        unique_together = ['employee', 'date']
        ordering = ['-date', '-created_at']
    
    def __str__(self):
        return f'{self.employee.get_full_name()} - {self.date} - {self.get_work_type_display()}'
    
    def get_work_type_display_name(self):
        """Lấy tên hiển thị của loại công việc"""
        return dict(self.WORK_TYPE_CHOICES).get(self.work_type, self.work_type)
    
    def get_shift_display(self):
        """Lấy hiển thị ca làm việc"""
        shifts = []
        if self.day_shift:
            shifts.append('Ca ngày')
        if self.night_shift:
            shifts.append('Ca đêm')
        return ' + '.join(shifts) if shifts else '-'
    
    def get_expense_display(self):
        """Lấy hiển thị chi phí"""
        expenses = []
        total_amount = 0
        
        if self.hotel_expense and self.hotel_expense > 0:
            expenses.append(f'KS: {self.hotel_expense:,.0f}đ')
            total_amount += self.hotel_expense
        
        if self.shopping_expense and self.shopping_expense > 0:
            expenses.append(f'MS: {self.shopping_expense:,.0f}đ')
            total_amount += self.shopping_expense
        
        if self.phone_expense and self.phone_expense > 0:
            expenses.append(f'ĐT: {self.phone_expense:,.0f}đ')
            total_amount += self.phone_expense
        
        if self.other_expense and self.other_expense > 0:
            expenses.append(f'Khác: {self.other_expense:,.0f}đ')
            total_amount += self.other_expense
        
        if expenses:
            result = ', '.join(expenses)
            if total_amount > 0:
                result += f' (Tổng: {total_amount:,.0f}đ)'
            return result
        return '-'
    
    def can_edit(self, user):
        """Kiểm tra user có thể chỉnh sửa không"""
        if not self.can_be_edited:
            return False
        
        # Nhân viên chỉ có thể sửa bản ghi của mình
        if user == self.employee:
            return True
        
        # Admin/Manager có thể sửa tất cả
        user_role = getattr(user.user_profile, 'role', 'staff')
        return user_role in ['admin', 'manager', 'company']
    
    @classmethod
    def create_from_leave_request(cls, leave_request, work_type='P'):
        """Tạo HOẶC liên kết/cập nhật bản ghi chấm công từ yêu cầu nghỉ phép.
        - Nếu chưa có bản ghi cho ngày đó: tạo mới và gắn `leave_request`
        - Nếu đã có bản ghi: gắn `leave_request` vào bản ghi hiện có và cập nhật `work_type`
        """
        from datetime import timedelta
        
        current_date = leave_request.start_date
        end_date = leave_request.end_date
        
        while current_date <= end_date:
            existing_record = cls.objects.filter(
                employee=leave_request.employee,
                date=current_date
            ).first()
            
            if not existing_record:
                # Tạo bản ghi mới
                cls.objects.create(
                    employee=leave_request.employee,
                    date=current_date,
                    work_type=work_type,  # 'P' cho nghỉ có phép, 'N' cho nghỉ không phép
                    leave_request=leave_request,
                    is_auto_generated=True,
                    can_be_edited=True,
                    created_by=leave_request.employee,
                    updated_by=leave_request.employee
                )
            else:
                # Liên kết và cập nhật bản ghi hiện có cho phù hợp với kết quả phê duyệt
                existing_record.leave_request = leave_request
                existing_record.work_type = work_type
                # Không tự động đổi cờ is_auto_generated để tránh xóa nhầm bản ghi do người dùng tạo
                existing_record.updated_by = leave_request.employee
                existing_record.save()
            
            current_date += timedelta(days=1)
    
    @classmethod
    def update_from_leave_request(cls, leave_request):
        """Cập nhật bản ghi chấm công khi trạng thái yêu cầu nghỉ phép thay đổi"""
        final_status, _, _ = leave_request.get_final_status()
        
        if final_status == 'approved':
            cls.objects.filter(
                leave_request=leave_request
            ).update(work_type='P')
        elif final_status == 'rejected':
            cls.objects.filter(
                leave_request=leave_request
            ).update(work_type='N')
    
    @classmethod
    def delete_for_leave_request(cls, leave_request):
        """Xóa tất cả bản ghi chấm công gắn với một yêu cầu nghỉ phép.
        Dùng khi người dùng xóa yêu cầu nghỉ => dữ liệu chấm công tương ứng cũng biến mất.
        """
        cls.objects.filter(leave_request=leave_request).delete()