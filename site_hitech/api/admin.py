from django.contrib import admin
from .models import Category, Post, Course, Lesson, Comment, CourseCategory, ContactSettings, SiteSettings
from .models import UserProfile  # Thay đổi từ Profile thành UserProfile
from .models import ChatSettings, ChatMessage
from .models import AboutPage, HomePageSettings
from .models import DocumentCategory, Document, DocumentTag, DocumentVersion, DocumentAccess
from .models import Project, PublicProject
from .seo_analyzer import SEOAnalyzer
from django.utils.html import format_html
from django.urls import path
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    list_display = ['company_name', 'footer_phone', 'footer_email']
    fieldsets = [
        ('🏢 Thông tin công ty & Logo', {
            'fields': ['logo', 'company_name', 'company_slogan', 'company_description'],
            'classes': ['wide'],
            'description': 'Logo sẽ hiển thị trên navbar. Thông tin công ty dùng cho SEO và giới thiệu chung.'
        }),
        ('🧭 Cài đặt Navbar (Menu điều hướng)', {
            'fields': ['navbar_bg_color', 'navbar_text_color', 'navbar_brand_size', 'navbar_link_size', 'navbar_sticky'],
            'classes': ['collapse']
        }),
        ('🦶 Cài đặt Footer (Chân trang)', {
            'fields': ['footer_bg_color', 'footer_text_color', 'footer_link_color', 'footer_copyright'],
            'classes': ['collapse']
        }),
        ('📍 Thông tin liên hệ Footer', {
            'fields': ['footer_address', 'footer_phone', 'footer_email'],
            'classes': ['wide']
        }),
        ('🌐 Liên kết mạng xã hội', {
            'fields': ['facebook_url', 'linkedin_url', 'youtube_url', 'twitter_url', 'zalo_phone'],
            'classes': ['collapse']
        }),
        ('🎨 Màu sắc chung website', {
            'fields': ['primary_color', 'secondary_color', 'success_color', 'warning_color', 'danger_color'],
            'classes': ['collapse'],
            'description': 'Màu sắc mặc định cho các trang chưa có cấu hình riêng.'
        }),
        ('✍️ Typography (Font chữ)', {
            'fields': ['font_family', 'heading_font_family'],
            'classes': ['collapse']
        }),
        ('🔍 SEO chung cho website', {
            'fields': ['site_title', 'site_description', 'site_keywords'],
            'classes': ['wide'],
            'description': 'Meta tags mặc định cho toàn website. Các trang riêng có thể ghi đè.'
        }),
        ('⚙️ Cài đặt hiển thị', {
            'fields': ['show_breadcrumb', 'show_scroll_top'],
            'classes': ['collapse']
        }),
        ('📞 Liên hệ nhanh (Floating)', {
            'fields': ['enable_floating_contact', 'floating_phone', 'floating_zalo'],
            'classes': ['collapse'],
            'description': 'Nút liên hệ nhanh hiển thị cố định ở góc màn hình.'
        }),
    ]
    
    def has_add_permission(self, request):
        # Chỉ cho phép tạo một bản ghi cấu hình
        return not SiteSettings.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        # Không cho phép xóa bản ghi cấu hình
        return False

@admin.register(ContactSettings)
class ContactSettingsAdmin(admin.ModelAdmin):
    fieldsets = [
        ('Thông tin liên hệ', {
            'fields': ['recipient_email', 'address', 'phone_numbers', 'business_hours', 'email_contact']
        }),
        ('Bản đồ', {
            'fields': ['maps_link', 'maps_embed'],
            'classes': ['collapse'],
            'description': 'Link Google Maps sẽ được dùng cho nút "Xem bản đồ". Mã nhúng để hiển thị bản đồ trên trang.'
        })
    ]
    
    def has_add_permission(self, request):
        # Chỉ cho phép tạo một bản ghi cấu hình
        return not ContactSettings.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        # Không cho phép xóa bản ghi cấu hình
        return False

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'category', 'created_at', 'published', 'view_count', 'seo_score_display')
    list_filter = ('published', 'category', 'created_at', 'tags')
    search_fields = ('title', 'content', 'meta_title', 'meta_description', 'meta_keywords')
    prepopulated_fields = {'slug': ('title',)}
    date_hierarchy = 'created_at'
    filter_horizontal = ('tags',)
    
    # Thêm custom template với SEO analyzer
    change_form_template = 'admin/api/post/change_form.html'
    add_form_template = 'admin/api/post/change_form.html'
    
    fieldsets = [
        ('📝 Thông tin cơ bản', {
            'fields': ['title', 'slug', 'author', 'category', 'featured_image']
        }),
        ('📖 Nội dung', {
            'fields': ['summary', 'content'],
            'classes': ['wide']
        }),
        ('🔍 SEO & Meta Tags', {
            'fields': ['meta_title', 'meta_description', 'meta_keywords'],
            'classes': ['wide'],
            'description': 'Tối ưu hóa cho công cụ tìm kiếm. Để trống sẽ sử dụng giá trị mặc định.'
        }),
        ('🏷️ Phân loại', {
            'fields': ['tags'],
            'classes': ['collapse']
        }),
        ('⚙️ Cài đặt xuất bản', {
            'fields': ['published'],
            'classes': ['collapse']
        }),
    ]
    
    def seo_score_display(self, obj):
        """Hiển thị điểm SEO trong list view"""
        if obj.title and obj.content:
            # Khởi tạo SEOAnalyzer với tham số bắt buộc
            analyzer = SEOAnalyzer(
                title=obj.meta_title or obj.title,
                description=obj.meta_description or '',
                content=obj.content,
                keywords=obj.meta_keywords or ''
            )
            analysis = analyzer.analyze_seo(
                title=obj.meta_title or obj.title,
                meta_description=obj.meta_description or '',
                content=obj.content,
                keywords=obj.meta_keywords or '',
                slug=obj.slug,
                featured_image=obj.featured_image.url if obj.featured_image else None
            )
            score = analysis['percentage']
            
            if score >= 80:
                color = '#28a745'  # Xanh lá
                icon = '✅'
            elif score >= 60:
                color = '#ffc107'  # Vàng
                icon = '⚠️'
            else:
                color = '#dc3545'  # Đỏ
                icon = '❌'
                
            return format_html(
                '<span style="color: {}; font-weight: bold;">{} {}%</span>',
                color, icon, score
            )
        return format_html('<span style="color: #6c757d;">—</span>')
    
    seo_score_display.short_description = 'Điểm SEO'
    seo_score_display.admin_order_field = 'title'
    
    def get_urls(self):
        """Thêm URL cho AJAX SEO analysis"""
        urls = super().get_urls()
        custom_urls = [
            path('seo-analysis/', self.admin_site.admin_view(self.seo_analysis_view), name='post_seo_analysis'),
        ]
        return custom_urls + urls
    
    @csrf_exempt
    def seo_analysis_view(self, request):
        """API endpoint để phân tích SEO real-time"""
        if request.method == 'POST':
            try:
                data = json.loads(request.body)
                
                title = data.get('title', '')
                meta_title = data.get('meta_title', '')
                meta_description = data.get('meta_description', '')
                content = data.get('content', '')
                keywords = data.get('meta_keywords', '')
                slug = data.get('slug', '')
                
                # Khởi tạo SEOAnalyzer với tham số bắt buộc
                analyzer = SEOAnalyzer(
                    title=meta_title or title,
                    description=meta_description,
                    content=content,
                    keywords=keywords
                )
                analysis = analyzer.analyze_seo(
                    title=meta_title or title,
                    meta_description=meta_description,
                    content=content,
                    keywords=keywords,
                    slug=slug,
                    featured_image=None  # Không thể analyze file upload real-time
                )
                
                return JsonResponse({
                    'success': True,
                    'analysis': analysis
                })
                
            except Exception as e:
                return JsonResponse({
                    'success': False,
                    'error': str(e)
                })
        
        return JsonResponse({'success': False, 'error': 'Method not allowed'})
    
    def save_model(self, request, obj, form, change):
        """Tự động set author và tạo meta fields nếu trống"""
        if not change:  # Tạo mới
            if not obj.author:
                obj.author = request.user
        
        # Tự động tạo meta_title nếu trống
        if not obj.meta_title and obj.title:
            obj.meta_title = obj.title[:60]  # Giới hạn 60 ký tự
            
        # Tự động tạo meta_description nếu trống
        if not obj.meta_description and obj.summary:
            obj.meta_description = obj.summary[:160]  # Giới hạn 160 ký tự
        
        super().save_model(request, obj, form, change)

@admin.register(CourseCategory)
class CourseCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'instructor', 'category', 'price', 'created_at', 'published')
    list_filter = ('published', 'category', 'created_at')
    search_fields = ('title', 'description')
    prepopulated_fields = {'slug': ('title',)}
    date_hierarchy = 'created_at'

@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'order')
    list_filter = ('course',)
    search_fields = ('title', 'content')

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    # Thay 'approved' bằng 'is_active'
    list_display = ['name', 'email', 'post', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'email', 'content']
    actions = ['approve_comments']
    
    def approve_comments(self, request, queryset):
        queryset.update(is_active=True)
    approve_comments.short_description = "Approve selected comments"

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'msnv', 'role', 'department', 'phone']
    list_filter = ['role', 'department']
    search_fields = ['user__username', 'user__email', 'department', 'msnv']
    fieldsets = [
        ('Thông tin cơ bản', {
            'fields': ['user', 'msnv', 'role', 'department', 'phone', 'avatar', 'bio']
        }),
        ('Thông tin chuyên môn', {
            'fields': ['position', 'certificates', 'skills', 'current_project', 'project_position']
        }),
        ('Thông tin liên hệ khẩn cấp', {
            'fields': ['emergency_contact', 'emergency_phone', 'join_date']
        }),
        ('Quyền hạn bài viết', {
            'fields': ['can_create_posts', 'can_edit_all_posts', 'can_delete_posts', 'can_publish_posts']
        }),
        ('Quyền hạn khóa học', {
            'fields': ['can_create_courses', 'can_edit_all_courses', 'can_delete_courses']
        }),
        ('Quyền hạn hệ thống', {
            'fields': ['can_manage_users', 'can_view_analytics', 'can_manage_settings']
        }),
    ]

@admin.register(ChatSettings)
class ChatSettingsAdmin(admin.ModelAdmin):
    fieldsets = [
        ('Cài đặt chung', {
            'fields': ['is_chat_enabled', 'auto_reply_message', 'zalo_phone']
        }),
    ]
    
    def has_add_permission(self, request):
        return not ChatSettings.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        return False

# ========== DOCUMENT MANAGEMENT ADMIN ==========

@admin.register(DocumentCategory)
class DocumentCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'parent', 'order', 'is_active')
    list_filter = ('parent', 'is_active')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    ordering = ('order', 'name')
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('parent')

@admin.register(DocumentTag)
class DocumentTagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'color')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}
    ordering = ('name',)

@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'version', 'created_by', 'created_at', 'updated_at', 'is_active']
    list_filter = ['category', 'created_at', 'is_active', 'tags']
    search_fields = ['title', 'description']
    readonly_fields = ['created_at', 'updated_at', 'version', 'file_size', 'file_hash']
    filter_horizontal = ['tags']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'file', 'description', 'category')
        }),
        ('Metadata', {
            'fields': ('tags', 'version', 'parent_document', 'is_active')
        }),
        ('File Information', {
            'fields': ('file_size', 'file_hash'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('category', 'created_by', 'parent_document').prefetch_related('tags')

@admin.register(DocumentVersion)
class DocumentVersionAdmin(admin.ModelAdmin):
    list_display = ('document', 'version', 'created_by', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('document__title', 'version', 'change_log')
    readonly_fields = ('created_at',)
    
    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

@admin.register(DocumentAccess)
class DocumentAccessAdmin(admin.ModelAdmin):
    list_display = ('user', 'document', 'action', 'ip_address', 'accessed_at')
    list_filter = ('action', 'accessed_at')
    search_fields = ('user__username', 'document__title', 'ip_address')
    readonly_fields = ('accessed_at',)
    date_hierarchy = 'accessed_at'
    
    def has_add_permission(self, request):
        return False  # Chỉ được tạo tự động từ code
    
    def has_change_permission(self, request, obj=None):
        return False  # Không cho phép chỉnh sửa log

@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ('sender_name', 'sender_type', 'content', 'created_at', 'is_read')
    list_filter = ('sender_type', 'is_read', 'created_at')
    search_fields = ('sender_name', 'sender_email', 'content')
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)

@admin.register(HomePageSettings)
class HomePageSettingsAdmin(admin.ModelAdmin):
    fieldsets = [
        ('🏠 Hero Section', {
            'fields': ['hero_title', 'hero_subtitle', 'hero_bg_image', 'hero_bg_color', 
                      'hero_btn_primary_text', 'hero_btn_primary_url', 
                      'hero_btn_secondary_text', 'hero_btn_secondary_url'],
            'classes': ['wide']
        }),
        ('🔬 Phương pháp NDT', {
            'fields': ['show_ndt_section', 'ndt_section_title', 'ndt_section_subtitle', 
                      'ndt_bg_image', 'ndt_bg_color', 'ndt_overlay_opacity'],
            'classes': ['collapse'],
            'description': 'Hình nền sẽ được ưu tiên sử dụng. Overlay opacity từ 0.0 (trong suốt) đến 1.0 (hoàn toàn mờ).'
        }),
        ('🏢 Dự án nổi bật', {
            'fields': ['show_projects_section', 'projects_section_title', 'projects_section_subtitle', 'projects_bg_color'],
            'classes': ['collapse']
        }),
        ('📰 Blog/Tin tức', {
            'fields': ['show_blog_section', 'blog_section_title', 'blog_section_subtitle', 'blog_bg_color'],
            'classes': ['collapse']
        }),
        ('🛠️ Dịch vụ', {
            'fields': ['show_services_section', 'services_section_title', 'services_section_subtitle', 'services_bg_color'],
            'classes': ['collapse']
        }),
        ('💬 Khách hàng testimonials', {
            'fields': ['show_testimonials_section', 'testimonials_section_title', 'testimonials_section_subtitle', 
                      'testimonials_bg_image', 'testimonials_bg_color', 'testimonials_overlay_opacity'],
            'classes': ['collapse'],
            'description': 'Hình nền sẽ được ưu tiên sử dụng. Overlay opacity để điều chỉnh độ mờ của lớp phủ.'
        }),
        ('💬 Quản lý nội dung Testimonials', {
            'fields': [
                ('testimonial1_content',),
                ('testimonial1_name', 'testimonial1_position', 'testimonial1_company'),
                ('testimonial1_avatar',),
                ('testimonial2_content',),
                ('testimonial2_name', 'testimonial2_position', 'testimonial2_company'),
                ('testimonial2_avatar',),
                ('testimonial3_content',),
                ('testimonial3_name', 'testimonial3_position', 'testimonial3_company'),
                ('testimonial3_avatar',),
                ('testimonial4_content',),
                ('testimonial4_name', 'testimonial4_position', 'testimonial4_company'),
                ('testimonial4_avatar',),
                ('testimonial5_content',),
                ('testimonial5_name', 'testimonial5_position', 'testimonial5_company'),
                ('testimonial5_avatar',),
            ],
            'classes': ['collapse'],
            'description': 'Quản lý nội dung, tên, chức vụ, công ty và ảnh đại diện của 5 testimonials.'
        }),
        ('🤝 Đối tác', {
            'fields': ['show_partners_section', 'partners_section_title', 'partners_section_subtitle', 
                      'partners_bg_image', 'partners_bg_color', 'partners_overlay_opacity'],
            'classes': ['collapse'],
            'description': 'Hình nền section và overlay opacity.'
        }),
        ('🏢 Quản lý Logo Đối tác', {
            'fields': [
                ('partner1_name', 'partner1_logo', 'partner1_icon'),
                ('partner2_name', 'partner2_logo', 'partner2_icon'),
                ('partner3_name', 'partner3_logo', 'partner3_icon'),
                ('partner4_name', 'partner4_logo', 'partner4_icon'),
                ('partner5_name', 'partner5_logo', 'partner5_icon'),
                ('partner6_name', 'partner6_logo', 'partner6_icon'),
                ('partner7_name', 'partner7_logo', 'partner7_icon'),
                ('partner8_name', 'partner8_logo', 'partner8_icon'),
                ('partner9_name', 'partner9_logo', 'partner9_icon'),
                ('partner10_name', 'partner10_logo', 'partner10_icon'),
                ('partner11_name', 'partner11_logo', 'partner11_icon'),
                ('partner12_name', 'partner12_logo', 'partner12_icon'),
            ],
            'classes': ['collapse'],
            'description': 'Quản lý tên và logo của 12 đối tác. Icon sẽ hiển thị khi không có logo.'
        }),
        ('📊 Số liệu tin cậy (Trust Indicators)', {
            'fields': ['trust_stat1_number', 'trust_stat1_label', 'trust_stat2_number', 'trust_stat2_label',
                      'trust_stat3_number', 'trust_stat3_label', 'trust_stat4_number', 'trust_stat4_label'],
            'classes': ['collapse']
        }),
        ('⭐ Vì sao chọn chúng tôi', {
            'fields': ['show_why_section', 'why_section_title', 'why_section_subtitle', 'why_bg_color'],
            'classes': ['collapse']
        }),
        ('🏆 Tính năng nổi bật', {
            'fields': ['feature1_title', 'feature1_description', 'feature1_icon',
                      'feature2_title', 'feature2_description', 'feature2_icon',
                      'feature3_title', 'feature3_description', 'feature3_icon',
                      'feature4_title', 'feature4_description', 'feature4_icon'],
            'classes': ['collapse']
        }),
        ('🔍 SEO Settings', {
            'fields': ['meta_title', 'meta_description', 'meta_keywords'],
            'classes': ['collapse']
        }),
        ('⚙️ Thông tin hệ thống', {
            'fields': ['updated_by', 'created_at', 'updated_at'],
            'classes': ['collapse']
        })
    ]
    
    readonly_fields = ('created_at', 'updated_at')
    
    def has_add_permission(self, request):
        # Chỉ cho phép tạo nếu chưa có bản ghi nào
        return not HomePageSettings.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        # Không cho phép xóa cấu hình trang chủ
        return False
    
    def save_model(self, request, obj, form, change):
        # Tự động ghi nhận người cập nhật
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)
    
    class Meta:
        verbose_name = 'Cấu hình trang chủ'
        verbose_name_plural = 'Cấu hình trang chủ'


@admin.register(AboutPage)
class AboutPageAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        # Chỉ cho phép tạo nếu chưa có bản ghi nào
        return not AboutPage.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        # Không cho phép xóa trang giới thiệu
        return False
    
    fieldsets = [
        ('Cài đặt SEO', {
            'fields': ['meta_title', 'meta_description'],
            'classes': ['collapse']
        }),
        ('Header & Hero Section', {
            'fields': [
                'title', 'subtitle', 
                'hero_bg_image', 'hero_bg_color', 'hero_text_color'
            ]
        }),
        ('Nội dung chính', {
            'fields': [
                'main_title', 'main_content', 'main_image', 'main_bg_color'
            ]
        }),
        ('Phần thống kê', {
            'fields': [
                'stats_title', 'stats_bg_color', 'stats_text_color',
                ('stat1_number', 'stat1_label', 'stat1_icon'),
                ('stat2_number', 'stat2_label', 'stat2_icon'),
                ('stat3_number', 'stat3_label', 'stat3_icon'),
                ('stat4_number', 'stat4_label', 'stat4_icon'),
            ]
        }),
        ('Tầm nhìn - Sứ mệnh - Giá trị', {
            'fields': [
                'vmv_title', 'vmv_bg_color', 'vmv_bg_image',
                ('vision_title', 'vision_icon', 'vision_color'),
                'vision',
                ('mission_title', 'mission_icon', 'mission_color'),
                'mission',
                ('values_title', 'values_icon', 'values_color'),
                'core_values',
            ]
        }),
        ('Phần Timeline/Cột mốc', {
            'fields': [
                'timeline_section_title', 'timeline_section_subtitle',
                'timeline_bg_image', 'timeline_bg_color', 'timeline_text_color', 'timeline_accent_color',
                ('timeline_overlay_color', 'timeline_overlay_opacity'),
                'timeline'
            ],
            'description': 'Overlay chỉ áp dụng khi có ảnh nền Timeline. Độ mờ từ 0.0 (trong suốt) đến 1.0 (hoàn toàn mờ).'
        }),
        ('Phần đội ngũ', {
            'fields': [
                'team_section_title', 'team_section_description',
                'team_bg_color', 'team_bg_image'
            ]
        }),
        ('Phần dịch vụ', {
            'fields': [
                'services_title', 'services_subtitle', 'services_bg_color', 'services_content'
            ]
        }),
        ('Phần thành tựu', {
            'fields': [
                'achievements_title', 'achievements', 'achievements_bg_color', 'achievements_image'
            ]
        }),
        ('Phần chứng chỉ', {
            'fields': [
                'certificates_section_title', 'certificates_section_subtitle',
                'certificates_bg_color', 'certificates'
            ]
        }),
        ('Call to Action', {
            'fields': [
                'cta_title', 'cta_subtitle',
                'cta_button_text', 'cta_button_url',
                'cta_bg_color', 'cta_text_color', 'cta_button_color', 'cta_button_text_color'
            ]
        }),
        ('Cài đặt Layout & Typography', {
            'fields': [
                'container_max_width', 'section_padding',
                'heading_font_family', 'body_font_family',
                'heading_color', 'body_color'
            ],
            'classes': ['collapse']
        }),
        ('Tương thích cũ', {
            'fields': ['banner_image', 'content'],
            'classes': ['collapse'],
            'description': 'Các trường này để tương thích với template cũ. Khuyến khích sử dụng các trường mới ở trên.'
        })
    ]
    
    class Media:
        css = {
            'all': ('admin/css/about_page_admin.css',)
        }
        js = ('admin/js/about_page_admin.js',)

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'company', 'status', 'project_manager', 'created_at')
    list_filter = ('status', 'created_at', 'methods')
    search_fields = ('name', 'code', 'description')
    date_hierarchy = 'created_at'
    filter_horizontal = ('methods', 'equipment', 'staff')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = [
        ('Thông tin cơ bản', {
            'fields': ['name', 'code', 'company', 'project_manager']
        }),
        ('Chi tiết dự án', {
            'fields': ['description', 'location', 'start_date', 'end_date', 'status', 'contract_value']
        }),
        ('Phân công', {
            'fields': ['methods', 'equipment', 'staff']
        }),
        ('Thống kê', {
            'fields': ['created_at', 'updated_at'],
            'classes': ['collapse']
        }),
    ]
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('company', 'project_manager')

@admin.register(PublicProject)
class PublicProjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'client_name', 'project_type', 'status', 'is_featured', 'published', 'view_count', 'created_at')
    list_filter = ('status', 'is_featured', 'published', 'project_type', 'created_at')
    search_fields = ('title', 'summary', 'content', 'client_name', 'tags')
    prepopulated_fields = {'slug': ('title',)}
    date_hierarchy = 'created_at'
    readonly_fields = ('view_count', 'created_at', 'updated_at')
    
    fieldsets = [
        ('Thông tin cơ bản', {
            'fields': ['title', 'slug', 'featured_image', 'author']
        }),
        ('Nội dung', {
            'fields': ['summary', 'content']
        }),
        ('Thông tin dự án', {
            'fields': ['client_name', 'location', 'project_type', 'completion_date', 'project_value', 'tags']
        }),
        ('Trạng thái', {
            'fields': ['status', 'is_featured', 'published']
        }),
        ('SEO', {
            'fields': ['meta_title', 'meta_description'],
            'classes': ['collapse']
        }),
        ('Thống kê', {
            'fields': ['view_count', 'created_at', 'updated_at'],
            'classes': ['collapse']
        }),
    ]
    
    def save_model(self, request, obj, form, change):
        if not change:  # Nếu tạo mới
            obj.author = request.user
        super().save_model(request, obj, form, change)
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('author')
