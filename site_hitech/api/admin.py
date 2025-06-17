from django.contrib import admin
from .models import Category, Post, Course, Lesson, Comment, CourseCategory, ContactSettings, SiteSettings
from .models import UserProfile  # Thay đổi từ Profile thành UserProfile
from .models import ChatSettings, ChatMessage
from .models import AboutPage

@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    fieldsets = [
        ('Cài đặt Navbar', {
            'fields': ['navbar_bg_color', 'navbar_text_color', 'navbar_brand_size', 'navbar_link_size']
        }),
        ('Cài đặt Footer', {
            'fields': ['footer_bg_color', 'footer_text_color', 'footer_link_color']
        }),
        ('Cài đặt Hero Section', {
            'fields': ['hero_bg_image', 'hero_bg_color', 'hero_title', 'hero_subtitle', 'hero_image', 
                      'hero_btn_primary_text', 'hero_btn_primary_url', 'hero_btn_secondary_text', 'hero_btn_secondary_url']
        }),
        ('Cài đặt Services Section', {
            'fields': ['services_title', 'services_subtitle', 'services_bg_color']
        }),
        ('Cài đặt About Section', {
            'fields': ['about_title', 'about_content', 'about_image', 'about_bg_color']
        }),
        ('Cài đặt Projects Section', {
            'fields': ['projects_title', 'projects_subtitle', 'projects_bg_color']
        }),
        ('Cài đặt Testimonials Section', {
            'fields': ['testimonials_title', 'testimonials_bg_color']
        }),
        ('Cài đặt Clients Section', {
            'fields': ['clients_title', 'clients_bg_color', 'client_logo1', 'client_logo2', 'client_logo3', 
                      'client_logo4', 'client_logo5', 'client_logo6']
        }),
        ('Logo và thông tin công ty', {
            'fields': ['logo', 'company_name', 'company_slogan', 'company_description']
        }),
        ('Thông tin liên hệ Footer', {
            'fields': ['footer_address', 'footer_phone', 'footer_email']
        }),
        ('Liên kết mạng xã hội', {
            'fields': ['facebook_url', 'linkedin_url', 'youtube_url', 'twitter_url']
        }),
    ]
    
    def has_add_permission(self, request):
        # Chỉ cho phép tạo một bản ghi cấu hình
        return not SiteSettings.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        # Không cho phép xóa bản ghi cấu hình
        return False
        
    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}
        extra_context['show_home_customization_link'] = True
        return super().change_view(request, object_id, form_url, extra_context=extra_context)

@admin.register(ContactSettings)
class ContactSettingsAdmin(admin.ModelAdmin):
    fieldsets = [
        ('Thông tin liên hệ', {
            'fields': ['recipient_email', 'address', 'phone_numbers', 'business_hours', 'email_contact']
        }),
        ('Bản đồ', {
            'fields': ['maps_embed'],
            'classes': ['collapse']
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
    list_display = ('title', 'author', 'category', 'created_at', 'published', 'view_count')
    list_filter = ('published', 'category', 'created_at', 'tags')
    search_fields = ('title', 'content')
    prepopulated_fields = {'slug': ('title',)}
    date_hierarchy = 'created_at'
    filter_horizontal = ('tags',)

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
    list_display = ['user', 'role', 'department', 'phone']
    list_filter = ['role', 'department']
    search_fields = ['user__username', 'user__email', 'department']
    fieldsets = [
        ('Thông tin cơ bản', {
            'fields': ['user', 'role', 'department', 'phone', 'avatar', 'bio']
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

@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ('sender_name', 'sender_type', 'content', 'created_at', 'is_read')
    list_filter = ('sender_type', 'is_read', 'created_at')
    search_fields = ('sender_name', 'sender_email', 'content')
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)

@admin.register(AboutPage)
class AboutPageAdmin(admin.ModelAdmin):
    fieldsets = [
        ('Thông tin cơ bản', {
            'fields': ['title', 'subtitle', 'banner_image', 'content']
        }),
        ('Thông tin công ty', {
            'fields': ['vision', 'mission', 'core_values'],
            'classes': ['collapse']
        }),
        ('Thành tựu', {
            'fields': ['achievements'],
            'classes': ['collapse']
        }),
        ('Cột mốc thời gian', {
            'fields': ['timeline_section_title', 'timeline'],
            'classes': ['collapse']
        }),
        ('Đội ngũ', {
            'fields': ['team_section_title', 'team_section_description'],
            'classes': ['collapse']
        }),
        ('Chứng chỉ & Giấy phép', {
            'fields': ['certificates_section_title', 'certificates'],
            'classes': ['collapse']
        }),
        ('SEO', {
            'fields': ['meta_title', 'meta_description'],
            'classes': ['collapse']
        }),
    ]
    
    def has_add_permission(self, request):
        return not AboutPage.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        return False
