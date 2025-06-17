from django.db import models
from django.contrib.auth.models import User
from ckeditor.fields import RichTextField
from django.utils.text import slugify
from django.core.exceptions import ValidationError
from colorfield.fields import ColorField


class SiteSettings(models.Model):
    # Cài đặt Navbar
    navbar_bg_color = ColorField(default='#212529', verbose_name='Màu nền Navbar')
    navbar_text_color = ColorField(default='#ffffff', verbose_name='Màu chữ Navbar')
    navbar_brand_size = models.CharField(max_length=10, default='18px', verbose_name='Kích thước chữ thương hiệu (px)')
    navbar_link_size = models.CharField(max_length=10, default='14px', verbose_name='Kích thước chữ menu (px)')
    
    # Cài đặt Footer
    footer_bg_color = ColorField(default='#212529', verbose_name='Màu nền Footer')
    footer_text_color = ColorField(default='#ffffff', verbose_name='Màu chữ Footer')
    footer_link_color = ColorField(default='#6c757d', verbose_name='Màu liên kết Footer')
    
    # Cài đặt Hero Section
    hero_bg_image = models.ImageField(upload_to='hero/', null=True, blank=True, verbose_name='Hình nền Hero Section')
    hero_bg_color = ColorField(default='#003d99', verbose_name='Màu nền Hero Section (khi không có hình)')
    hero_title = models.CharField(max_length=100, default='HITECH NDT', verbose_name='Tiêu đề Hero Section')
    hero_subtitle = models.TextField(default='Công nghệ kiểm tra không phá hủy hàng đầu Việt Nam với các giải pháp tiên tiến và đội ngũ chuyên gia giàu kinh nghiệm', verbose_name='Mô tả Hero Section')
    hero_image = models.ImageField(upload_to='hero/', null=True, blank=True, verbose_name='Hình ảnh Hero Section')
    hero_btn_primary_text = models.CharField(max_length=50, default='Khám phá dịch vụ', verbose_name='Nút chính - Văn bản')
    hero_btn_primary_url = models.CharField(max_length=100, default='/dich-vu', verbose_name='Nút chính - Liên kết')
    hero_btn_secondary_text = models.CharField(max_length=50, default='Liên hệ ngay', verbose_name='Nút phụ - Văn bản')
    hero_btn_secondary_url = models.CharField(max_length=100, default='/lien-he', verbose_name='Nút phụ - Liên kết')
    
    # Cài đặt Services Section
    services_title = models.CharField(max_length=100, default='Dịch vụ chuyên nghiệp', verbose_name='Tiêu đề phần Dịch vụ')
    services_subtitle = models.TextField(blank=True, null=True, verbose_name='Mô tả phần Dịch vụ')
    services_bg_color = ColorField(default='#ffffff', verbose_name='Màu nền phần Dịch vụ')
    
    # Cài đặt About Section
    about_title = models.CharField(max_length=100, default='Tại sao chọn Hitech NDT?', verbose_name='Tiêu đề phần Giới thiệu')
    about_content = models.TextField(default='Hitech NDT là đơn vị hàng đầu trong lĩnh vực kiểm tra không phá hủy tại Việt Nam. Với đội ngũ kỹ sư giàu kinh nghiệm và trang thiết bị hiện đại, chúng tôi cam kết mang đến những dịch vụ chất lượng cao nhất.', verbose_name='Nội dung phần Giới thiệu')
    about_image = models.ImageField(upload_to='about/', null=True, blank=True, verbose_name='Hình ảnh phần Giới thiệu')
    about_bg_color = ColorField(default='#f8f9fa', verbose_name='Màu nền phần Giới thiệu')
    
    # Cài đặt Projects Section
    projects_title = models.CharField(max_length=100, default='Dự án tiêu biểu', verbose_name='Tiêu đề phần Dự án')
    projects_subtitle = models.TextField(blank=True, null=True, verbose_name='Mô tả phần Dự án')
    projects_bg_color = ColorField(default='#ffffff', verbose_name='Màu nền phần Dự án')
    
    # Cài đặt Testimonials Section
    testimonials_title = models.CharField(max_length=100, default='Khách hàng nói gì về chúng tôi', verbose_name='Tiêu đề phần Đánh giá')
    testimonials_bg_color = ColorField(default='#f8f9fa', verbose_name='Màu nền phần Đánh giá')
    
    # Cài đặt Clients Section
    clients_title = models.CharField(max_length=100, default='Đối tác của chúng tôi', verbose_name='Tiêu đề phần Đối tác')
    clients_bg_color = ColorField(default='#ffffff', verbose_name='Màu nền phần Đối tác')
    client_logo1 = models.ImageField(upload_to='clients/', null=True, blank=True, verbose_name='Logo đối tác 1')
    client_logo2 = models.ImageField(upload_to='clients/', null=True, blank=True, verbose_name='Logo đối tác 2')
    client_logo3 = models.ImageField(upload_to='clients/', null=True, blank=True, verbose_name='Logo đối tác 3')
    client_logo4 = models.ImageField(upload_to='clients/', null=True, blank=True, verbose_name='Logo đối tác 4')
    client_logo5 = models.ImageField(upload_to='clients/', null=True, blank=True, verbose_name='Logo đối tác 5')
    client_logo6 = models.ImageField(upload_to='clients/', null=True, blank=True, verbose_name='Logo đối tác 6')
    
    # Logo và thông tin công ty
    logo = models.ImageField(upload_to='site/', null=True, blank=True, verbose_name='Logo công ty')
    company_name = models.CharField(max_length=100, default='Hitech NDT', verbose_name='Tên công ty')
    company_slogan = models.CharField(max_length=200, default='Giải pháp công nghệ hàng đầu', verbose_name='Slogan công ty')
    company_description = models.TextField(default='Hitech NDT tự hào là đơn vị hàng đầu trong lĩnh vực kiểm tra không phá hủy và đào tạo chứng chỉ NDT tại Việt Nam', verbose_name='Mô tả công ty')
    
    # Thông tin liên hệ Footer
    footer_address = models.CharField(max_length=200, default='123 Đường ABC, Quận XYZ, TP.HCM', verbose_name='Địa chỉ')
    footer_phone = models.CharField(max_length=20, default='+84 123 456 789', verbose_name='Số điện thoại')
    footer_email = models.EmailField(default='info@hitechndt.com', verbose_name='Email')
    
    # Liên kết mạng xã hội
    facebook_url = models.URLField(blank=True, null=True, verbose_name='Facebook URL')
    linkedin_url = models.URLField(blank=True, null=True, verbose_name='LinkedIn URL')
    youtube_url = models.URLField(blank=True, null=True, verbose_name='YouTube URL')
    twitter_url = models.URLField(blank=True, null=True, verbose_name='Twitter URL')
    
    def clean(self):
        # Đảm bảo chỉ có một bản ghi cấu hình
        if not self.pk and SiteSettings.objects.exists():
            raise ValidationError('Chỉ có thể tạo một bản ghi cấu hình website')
    
    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return 'Cấu hình website'
    
    class Meta:
        verbose_name = 'Cấu hình website'
        verbose_name_plural = 'Cấu hình website'


class ContactSettings(models.Model):
    recipient_email = models.EmailField(verbose_name='Email người nhận')
    address = models.TextField(verbose_name='Địa chỉ')
    phone_numbers = models.TextField(verbose_name='Số điện thoại', help_text='Mỗi số điện thoại một dòng')
    business_hours = models.TextField(verbose_name='Giờ làm việc', help_text='Định dạng: Thứ Hai - Thứ Sáu: 8:00 - 17:30')
    email_contact = models.TextField(verbose_name='Email liên hệ', help_text='Mỗi email một dòng')
    maps_embed = models.TextField(verbose_name='Mã nhúng Google Maps', help_text='Mã iframe từ Google Maps')
    
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
    content = RichTextField()
    summary = models.TextField(blank=True, null=True)
    featured_image = models.ImageField(upload_to='blog/%Y/%m/', null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published = models.BooleanField(default=False)
    view_count = models.PositiveIntegerField(default=0)
    tags = models.ManyToManyField('Tag', blank=True)
    
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return f'/blog/{self.id}/'
    
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
    description = RichTextField()
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
    content = RichTextField()
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
    title = models.CharField(max_length=200, default="Về Chúng Tôi")
    subtitle = models.CharField(max_length=300, blank=True, help_text="Phụ đề hiển thị bên dưới tiêu đề chính")
    banner_image = models.ImageField(upload_to='about/', verbose_name='Ảnh banner')
    content = RichTextField(verbose_name='Nội dung')
    
    # Thông tin công ty
    vision = RichTextField(verbose_name='Tầm nhìn', null=True, blank=True)
    mission = RichTextField(verbose_name='Sứ mệnh', null=True, blank=True)
    core_values = RichTextField(verbose_name='Giá trị cốt lõi', null=True, blank=True)
    
    # Thành tựu
    achievements = RichTextField(verbose_name='Thành tựu', null=True, blank=True)
    
    # Thêm vào class AboutPage
    timeline_section_title = models.CharField(max_length=200, verbose_name='Tiêu đề phần cột mốc', default='Cột mốc phát triển')
    timeline = models.TextField(verbose_name='Cột mốc thời gian', null=True, blank=True, help_text='Nhập theo format: Năm|Tiêu đề|Mô tả, mỗi cột mốc một dòng')
    
    # Đội ngũ
    team_section_title = models.CharField(max_length=200, verbose_name='Tiêu đề phần đội ngũ', default='Đội ngũ của chúng tôi')
    team_section_description = RichTextField(verbose_name='Mô tả phần đội ngũ', null=True, blank=True)
    
    # Chứng chỉ & Giấy phép
    certificates_section_title = models.CharField(max_length=200, verbose_name='Tiêu đề phần chứng chỉ', default='Chứng chỉ & Giấy phép')
    certificates = RichTextField(verbose_name='Danh sách chứng chỉ', null=True, blank=True)
    
    # SEO
    meta_title = models.CharField(max_length=200, verbose_name='Meta Title', null=True, blank=True)
    meta_description = models.TextField(verbose_name='Meta Description', null=True, blank=True)
    
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
        ('admin', 'Quản trị viên'),
        ('manager', 'Quản lý'),
        ('staff', 'Nhân viên'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='user_profile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='staff', verbose_name='Vai trò')
    department = models.CharField(max_length=100, blank=True, null=True, verbose_name='Phòng ban')
    phone = models.CharField(max_length=20, blank=True, null=True, verbose_name='Số điện thoại')
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True, verbose_name='Ảnh đại diện')
    bio = models.TextField(blank=True, null=True, verbose_name='Giới thiệu')
    
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
    """Model cho dự án NDT"""
    STATUS_CHOICES = [
        ('planning', 'Lập kế hoạch'),
        ('active', 'Đang thực hiện'),
        ('pending', 'Tạm dừng'),
        ('completed', 'Hoàn thành'),
        ('cancelled', 'Đã hủy')
    ]
    
    name = models.CharField(max_length=200, verbose_name='Tên dự án')
    code = models.CharField(max_length=50, unique=True, verbose_name='Mã dự án')
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
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f'{self.code} - {self.name}'
    
    class Meta:
        verbose_name = 'Dự án'
        verbose_name_plural = 'Dự án'
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