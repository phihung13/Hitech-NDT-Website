from django.http import JsonResponse
from .models import Course, Post, Category, Comment, ContactSettings, Tag, SiteSettings, AboutPage, HomePageSettings, UserProfile, Project, ProjectFile, ProjectProgress, CourseCategory, Equipment, PublicProject, Company, NDTMethod, Attendance
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from .forms import PostForm, CourseForm, CommentForm, ProjectFileForm, ProjectUpdateForm, ProjectCreateForm
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render
from django.conf import settings
import os
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from .permissions import admin_required, manager_required, staff_required, permission_required
from django.contrib.auth.models import User
from django.http import FileResponse, HttpResponse
from django.core.paginator import Paginator
from django.db.models import Q
import mimetypes
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from django.core.files.storage import default_storage
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.utils import translation
import json
from datetime import timedelta, date, datetime
import shutil
from .models import LeaveRequest
from django.db import models
from django.utils import timezone
from django.db.models import Q
from decimal import Decimal

def get_disk_usage():
    """Lấy thông tin dung lượng disk"""
    try:
        # Lấy thông tin disk cho thư mục project
        total, used, free = shutil.disk_usage('/')
        
        # Chuyển đổi sang GB
        total_gb = total / (1024**3)
        used_gb = used / (1024**3)
        free_gb = free / (1024**3)
        
        # Tính phần trăm đã sử dụng
        usage_percent = (used_gb / total_gb) * 100
        
        return {
            'total_gb': round(total_gb, 2),
            'used_gb': round(used_gb, 2),
            'free_gb': round(free_gb, 2),
            'usage_percent': round(usage_percent, 2),
            'status': 'danger' if usage_percent > 90 else 'warning' if usage_percent > 75 else 'success'
        }
    except Exception as e:
        # Fallback data nếu có lỗi
        return {
            'total_gb': 0,
            'used_gb': 0,
            'free_gb': 0,
            'usage_percent': 0,
            'status': 'info',
            'error': str(e)
        }

def home(request):
    # Lấy cấu hình trang chủ
    try:
        homepage_settings = HomePageSettings.objects.first()
    except HomePageSettings.DoesNotExist:
        homepage_settings = None
    
    # Lấy 5 bài viết mới nhất cho blog highlights (1 bài chính + 4 bài phụ)
    latest_posts = Post.objects.filter(published=True).order_by('-created_at')[:5]
    
    # Lấy 4 dự án nổi bật hoặc gần nhất có nhiều view nhất
    featured_projects = PublicProject.objects.filter(published=True)
    
    # Ưu tiên dự án được đánh dấu featured
    priority_projects = featured_projects.filter(is_featured=True).order_by('-view_count', '-created_at')[:4]
    
    # Nếu không đủ 4 dự án featured, bổ sung thêm từ dự án gần nhất
    if priority_projects.count() < 4:
        remaining_count = 4 - priority_projects.count()
        additional_projects = featured_projects.exclude(
            id__in=priority_projects.values_list('id', flat=True)
        ).order_by('-view_count', '-created_at')[:remaining_count]
        featured_projects = list(priority_projects) + list(additional_projects)
    else:
        featured_projects = priority_projects
    
    # Đảm bảo có đúng 4 dự án để hiển thị (cho responsive grid)
    featured_projects = featured_projects[:4]
    
    context = {
        'homepage_settings': homepage_settings,
        'latest_posts': latest_posts,
        'featured_projects': featured_projects,
        'popular_posts': latest_posts,  # Alias cho template compatibility
    }
    return render(request, 'general/home.html', context)

@login_required
def admin_home_customization(request):
    """View cho trang tùy chỉnh giao diện trang chủ trong admin panel"""
    try:
        site_settings = SiteSettings.objects.first()
        if not site_settings:
            site_settings = SiteSettings.objects.create()
    except Exception as e:
        messages.error(request, f'Lỗi khi tải cấu hình: {str(e)}')
        site_settings = None
    
    context = {
        'site_settings': site_settings,
        'title': 'Tùy chỉnh trang chủ',
    }
    return render(request, 'admin/admin_home_customization.html', context)

def blog_list(request):
    category_slug = request.GET.get('category')
    current_category = None
    
    if category_slug:
        current_category = get_object_or_404(Category, slug=category_slug)
        posts = Post.objects.filter(published=True, category=current_category).order_by('-created_at')
    else:
        posts = Post.objects.filter(published=True).order_by('-created_at')
    
    paginator = Paginator(posts, 9)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Lấy dữ liệu cho sidebar
    categories = Category.objects.all()
    tags = Tag.objects.all()[:10]  # Lấy 10 tags đầu tiên
    recent_posts = Post.objects.filter(published=True).order_by('-created_at')[:5]
    
    context = {
        'posts': page_obj,  # Đổi từ page_obj thành posts để template dễ sử dụng
        'page_obj': page_obj,  # Giữ lại cho pagination
        'is_paginated': page_obj.has_other_pages(),
        'categories': categories,
        'current_category': current_category,
        'tags': tags,
        'recent_posts': recent_posts,
    }
    
    return render(request, 'blog/blog_list.html', context)

def blog_detail(request, slug):
    post = get_object_or_404(Post, slug=slug, published=True)
    post.view_count += 1
    post.save()
    
    related_posts = Post.objects.filter(category=post.category, published=True).exclude(id=post.id)[:3]
    
    if request.method == 'POST':
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.post = post
            comment.save()
            return redirect('blog_detail', slug=slug)
    else:
        comment_form = CommentForm()
    
    context = {
        'post': post,
        'related_posts': related_posts,
        'comments': post.comments.filter(approved=True),
        'comment_form': comment_form,
    }
    return render(request, 'blog/blog_detail.html', context)

def course_list(request):
    courses = Course.objects.filter(published=True)
    
    paginator = Paginator(courses, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'course_list.html', context)

def course_detail(request, slug):
    course = get_object_or_404(Course, slug=slug, published=True)
    lessons = course.lessons.all()
    
    if request.method == 'POST':
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.course = course
            comment.save()
            return redirect('course_detail', slug=slug)
    else:
        comment_form = CommentForm()
    
    context = {
        'course': course,
        'lessons': lessons,
        'comments': course.comments.filter(approved=True),
        'comment_form': comment_form,
    }
    return render(request, 'course_detail.html', context)

@login_required
def create_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('blog_detail', slug=post.slug)
    else:
        form = PostForm()
    
    return render(request, 'blog/create_post.html', {'form': form})

@login_required
def create_course(request):
    if request.method == 'POST':
        form = CourseForm(request.POST, request.FILES)
        if form.is_valid():
            course = form.save(commit=False)
            course.instructor = request.user
            course.save()
            return redirect('course_detail', slug=course.slug)
    else:
        form = CourseForm()
    
    return render(request, 'create_course.html', {'form': form})

def about(request):
    """Trang giới thiệu về Hitech NDT"""
    try:
        about_page = AboutPage.objects.first()
    except AboutPage.DoesNotExist:
        about_page = None
    
    context = {
        'about_page': about_page
    }
    return render(request, 'general/about.html', context)

def contact(request):
    """Trang liên hệ với form gửi tin nhắn"""
    try:
        contact_settings = ContactSettings.objects.first()
    except ContactSettings.DoesNotExist:
        contact_settings = None
    
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        
        if contact_settings and contact_settings.recipient_email:
            # Gửi email thông báo
            from django.core.mail import send_mail
            email_subject = f'Tin nhắn liên hệ mới từ {name}'
            email_message = f'''Bạn nhận được tin nhắn mới từ form liên hệ:

Họ tên: {name}
Email: {email}
Số điện thoại: {phone}
Tiêu đề: {subject}
Nội dung:
{message}'''
            
            try:
                send_mail(
                    email_subject,
                    email_message,
                    settings.DEFAULT_FROM_EMAIL,
                    [contact_settings.recipient_email],
                    fail_silently=False,
                )
                messages.success(request, 'Tin nhắn của bạn đã được gửi thành công. Chúng tôi sẽ liên hệ lại trong thời gian sớm nhất.')
            except Exception as e:
                messages.error(request, 'Có lỗi xảy ra khi gửi tin nhắn. Vui lòng thử lại sau.')
        else:
            messages.warning(request, 'Hệ thống chưa được cấu hình email người nhận. Vui lòng liên hệ quản trị viên.')
        
        return redirect('contact')
    
    context = {
        'contact_settings': contact_settings
    }
    return render(request, 'general/contact.html', context)

def post_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        content = request.POST.get('content')
        
        if name and email and content:
            Comment.objects.create(
                post=post,
                name=name,
                email=email,
                content=content
            )
            messages.success(request, 'Bình luận của bạn đã được gửi thành công!')
        else:
            messages.error(request, 'Vui lòng điền đầy đủ thông tin!')
            
    return redirect('blog_detail', post_id=post_id)

@staff_member_required
def admin_chat_view(request):
    return render(request, 'admin/chat.html')

def staff_login(request):
    """View đăng nhập cho nhân viên qua web interface"""
    if request.user.is_authenticated:
        return redirect('staff_dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            if user.is_staff:  # Chỉ cho phép staff đăng nhập
                auth_login(request, user)
                messages.success(request, f'Chào mừng {user.username}!')
                return redirect('staff_dashboard')
            else:
                messages.error(request, 'Bạn không có quyền truy cập hệ thống nội bộ.')
        else:
            messages.error(request, 'Tên đăng nhập hoặc mật khẩu không đúng.')
    
    return render(request, 'auth/login.html')

@staff_required
def staff_dashboard(request):
    """Dashboard nội bộ cho nhân viên"""
    profile = request.user.user_profile
    
    # Thống kê cơ bản
    total_posts = Post.objects.count()
    published_posts = Post.objects.filter(published=True).count()
    draft_posts = total_posts - published_posts
    total_courses = Course.objects.count()
    
    # Thêm dữ liệu dự án thật
    projects = Project.objects.all().order_by('-created_at')[:10]  # Lấy 10 dự án mới nhất
    total_projects = Project.objects.count()
    active_projects = Project.objects.filter(status='active').count()
    completed_projects = Project.objects.filter(status='completed').count()
    
    # Thống kê thiết bị
    total_equipment = Equipment.objects.count()
    active_equipment = Equipment.objects.filter(status='active').count()
    maintenance_equipment = Equipment.objects.filter(status='maintenance').count()
    
    # Thống kê cá nhân
    if profile.role == 'staff':
        user_posts = Post.objects.filter(author=request.user)
        user_courses = Course.objects.filter(instructor=request.user)
        # Dự án mà user tham gia
        user_projects = Project.objects.filter(staff=request.user)
    else:
        user_posts = Post.objects.all()[:5]
        user_courses = Course.objects.all()[:5]
        user_projects = projects
    
    # Thêm danh sách nhân viên
    staff_list = UserProfile.objects.select_related('user').all()
    
    # Lấy thông tin disk usage
    disk_info = get_disk_usage()
    
    context = {
        'profile': profile,
        'total_posts': total_posts,
        'published_posts': published_posts,
        'draft_posts': draft_posts,
        'total_courses': total_courses,
        'user_posts': user_posts,
        'user_courses': user_courses,
        'recent_posts': Post.objects.order_by('-created_at')[:5],
        # Thêm dữ liệu dự án
        'projects': projects,
        'user_projects': user_projects,
        'total_projects': total_projects,
        'active_projects': active_projects,
        'completed_projects': completed_projects,
        'staff_list': staff_list,
        # Thống kê thiết bị
        'total_equipment': total_equipment,
        'active_equipment': active_equipment,
        'maintenance_equipment': maintenance_equipment,
        # Thông tin dung lượng disk
        'disk_info': disk_info,
    }
    return render(request, 'dashboard/staff_dashboard.html', context)

@manager_required
def admin_dashboard(request):
    """Dashboard cho admin và manager"""
    profile = request.user.profile
    
    # Thống kê chi tiết
    total_users = User.objects.filter(is_staff=True).count()
    total_posts = Post.objects.count()
    published_posts = Post.objects.filter(published=True).count()
    draft_posts = total_posts - published_posts
    total_courses = Course.objects.count()
    
    # Thống kê theo vai tròng
    admin_count = UserProfile.objects.filter(role='admin').count()
    manager_count = UserProfile.objects.filter(role='manager').count()
    staff_count = UserProfile.objects.filter(role='staff').count()
    
    context = {
        'profile': profile,
        'total_users': total_users,
        'total_posts': total_posts,
        'published_posts': published_posts,
        'draft_posts': draft_posts,
        'total_courses': total_courses,
        'admin_count': admin_count,
        'manager_count': manager_count,
        'staff_count': staff_count,
        'recent_posts': Post.objects.order_by('-created_at')[:10],
        'recent_users': User.objects.filter(is_staff=True).order_by('-date_joined')[:5],
    }
    return render(request, 'admin_dashboard.html', context)

@admin_required
def user_management(request):
    """Quản lý người dùng - chỉ admin"""
    users = User.objects.filter(is_staff=True).select_related('profile')
    
    context = {
        'users': users,
    }
    return render(request, 'user_management.html', context)

@permission_required('can_create_posts')
def create_post_secure(request):
    """Tạo bài viết với kiểm tra quyền"""
    # Logic tạo bài viết
    return create_post(request)

@permission_required('can_publish_posts')
def publish_post(request, post_id):
    """Xuất bản bài viết - chỉ manager và admin"""
    post = get_object_or_404(Post, id=post_id)
    
    # Kiểm tra quyền chỉnh sửa
    profile = request.user.profile
    if not profile.can_edit_all_posts and post.author != request.user:
        messages.error(request, 'Bạn chỉ có thể xuất bản bài viết của mình.')
        return redirect('staff_dashboard')
    
    post.published = True
    post.save()
    messages.success(request, f'Đã xuất bản bài viết "{post.title}"')
    return redirect('staff_dashboard')

@permission_required('can_delete_posts')
def delete_post(request, post_id):
    """Xóa bài viết - chỉ manager và admin"""
    post = get_object_or_404(Post, id=post_id)
    
    if request.method == 'POST':
        title = post.title
        post.delete()
        messages.success(request, f'Đã xóa bài viết "{title}"')
        return redirect('staff_dashboard')
    
    return render(request, 'confirm_delete.html', {'object': post, 'type': 'bài viết'})

@login_required
def staff_logout(request):
    """View đăng xuất"""
    auth_logout(request)
    messages.success(request, 'Đã đăng xuất thành công.')
    return redirect('home')

@login_required
def project_management_detail(request, project_id):
    """Chi tiết dự án cho quản lý nội bộ"""
    project = get_object_or_404(Project, id=project_id)
    
    # Kiểm tra quyền xem dự án
    if not (request.user.user_profile.role in ['admin', 'manager'] or 
            request.user in project.staff.all() or 
            request.user == project.project_manager):
        messages.error(request, 'Bạn không có quyền xem dự án này.')
        return redirect('projects_management')
    
    project_files = ProjectFile.objects.filter(project=project).order_by('-uploaded_at')
    
    context = {
        'project': project,
        'project_files': project_files,
    }
    return render(request, 'projects/project_detail.html', context)

@login_required
def upload_file(request, project_id):
    """Upload file với auto-detect loại file"""
    project = get_object_or_404(Project, id=project_id)
    
    # Kiểm tra quyền upload
    if not (request.user.user_profile.role in ['admin', 'manager'] or 
            request.user in project.staff.all() or 
            request.user == project.project_manager):
        messages.error(request, 'Bạn không có quyền upload file cho dự án này.')
        return redirect('project_detail', project_id=project.id)
    
    if request.method == 'POST':
        file = request.FILES.get('file')
        description = request.POST.get('description', '').strip()
        
        if not file:
            messages.error(request, 'Vui lòng chọn file để upload.')
            return redirect('project_detail', project_id=project.id)
        
        # Tự động phát hiện loại file từ extension
        file_ext = file.name.split('.')[-1].lower() if '.' in file.name else ''
        
        if file_ext in ['xlsx', 'xls']:
            file_type = 'excel'
        elif file_ext == 'pdf':
            file_type = 'pdf'
        elif file_ext in ['docx', 'doc']:
            file_type = 'word'
        elif file_ext in ['jpg', 'jpeg', 'png', 'gif']:
            file_type = 'image'
        else:
            file_type = 'other'
        
        # Tạo project file
        project_file = ProjectFile.objects.create(
            project=project,
            name=file.name,
            file=file,
            file_type=file_type,
            description=description,
            uploaded_by=request.user
        )
        
        messages.success(request, f'Đã upload file "{file.name}" thành công!')
        return redirect('project_detail', project_id=project.id)
    
    return redirect('project_detail', project_id=project.id)

@login_required
def download_file(request, project_id, file_id):
    project_file = get_object_or_404(ProjectFile, id=file_id, project_id=project_id)
    
    if project_file.file and default_storage.exists(project_file.file.name):
        response = FileResponse(
            project_file.file.open('rb'),
            as_attachment=True,
            filename=project_file.name  # Sửa từ 'file_name' thành 'name'
        )
        return response
    else:
        return HttpResponse("File not found", status=404)

@login_required
def update_project(request, project_id):
    """Cập nhật thông tin dự án"""
    project = get_object_or_404(Project, id=project_id)
    
    # Kiểm tra quyền sửa
    if not (request.user.user_profile.role in ['admin', 'manager'] or 
            request.user == project.project_manager):
        if request.headers.get('Content-Type') == 'application/x-www-form-urlencoded':
            return JsonResponse({'success': False, 'error': 'Bạn không có quyền sửa dự án này.'})
        messages.error(request, 'Bạn không có quyền sửa dự án này.')
        return redirect('project_detail', project_id=project.id)
    
    if request.method == 'POST':
        try:
            # Cập nhật các trường được phép
            project.name = request.POST.get('name', project.name)
            project.location = request.POST.get('location', project.location) 
            project.status = request.POST.get('status', project.status)
            project.description = request.POST.get('description', project.description)
            
            # Cập nhật completion_percentage nếu có
            completion = request.POST.get('completion_percentage')
            if completion:
                try:
                    completion_value = max(0, min(100, int(completion)))
                    project.completion_percentage = completion_value
                except ValueError:
                    return JsonResponse({'success': False, 'error': 'Tiến độ không hợp lệ'})
            
            project.save()
            
            # Kiểm tra nếu request là AJAX
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': True, 'message': 'Cập nhật dự án thành công!'})
            
            messages.success(request, 'Cập nhật dự án thành công!')
            
        except Exception as e:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'error': str(e)})
            messages.error(request, f'Có lỗi xảy ra: {str(e)}')
        
    return redirect('project_detail', project_id=project.id)

@login_required
def update_progress(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    
    if request.method == 'POST':
        progress_data = request.POST.get('progress_data')
        notes = request.POST.get('notes')
        
        ProjectProgress.objects.create(
            project=project,
            progress_data=progress_data,
            notes=notes,
            updated_by=request.user
        )
        
        return redirect('project_detail', project_id=project.id)
    
    return redirect('project_detail', project_id=project.id)

@login_required
def create_project(request):
    """View tạo dự án mới"""
    # Kiểm tra quyền: chỉ admin và manager mới được tạo dự án
    if not hasattr(request.user, 'user_profile') or request.user.user_profile.role not in ['admin', 'manager']:
        messages.error(request, 'Bạn không có quyền tạo dự án mới.')
        return redirect('staff_dashboard')
    
    if request.method == 'POST':
        form = ProjectCreateForm(request.POST)
        if form.is_valid():
            project = form.save()
            messages.success(request, f'Dự án "{project.name}" đã được tạo thành công!')
            return redirect('project_detail', project_id=project.id)
        else:
            messages.error(request, 'Có lỗi xảy ra. Vui lòng kiểm tra lại thông tin.')
    else:
        form = ProjectCreateForm()
    
    context = {
        'form': form,
        'title': 'Tạo dự án mới'
    }
    return render(request, 'projects/create_project.html', context)

def service_list(request):
    from .models import CourseCategory
    
    # Lấy tất cả các danh mục khóa học để hiển thị như dịch vụ
    service_categories = CourseCategory.objects.all()
    
    context = {
        'title': 'Các dịch vụ của chúng tôi',
        'service_categories': service_categories,
    }
    return render(request, 'services/service_list.html', context)

def service_detail(request, slug):
    from .models import CourseCategory, Course
    from django.shortcuts import get_object_or_404
    
    # Lấy danh mục dịch vụ
    category = get_object_or_404(CourseCategory, slug=slug)
    
    # Lấy các khóa học trong danh mục này
    courses = Course.objects.filter(category=category, published=True)
    
    context = {
        'title': f'Dịch vụ {category.name}',
        'category': category,
        'courses': courses,
    }
    return render(request, 'services/service_detail.html', context)

@login_required
@require_http_methods(["GET", "POST"])
def phan_cong_nhan_vien(request):
    if request.method == "GET":
        projects = Project.objects.all().values('id', 'name')
        users = User.objects.filter(is_active=True).values('id', 'username', 'first_name', 'last_name')
        return JsonResponse({
            'projects': list(projects),
            'users': list(users)
        })
    elif request.method == "POST":
        project_id = request.POST.get('project_id')
        user_ids = request.POST.getlist('user_ids[]')
        try:
            project = Project.objects.get(id=project_id)
            users = User.objects.filter(id__in=user_ids)
            project.staff.set(users)
            project.save()
            return JsonResponse({'success': True, 'message': 'Phân công nhân viên thành công!'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})

def staff_assign(request):
    return render(request, 'management/staff_assign.html')

def equipment_schedule(request):
    return render(request, 'management/equipment_schedule.html')

def report_generate(request):
    return render(request, 'reports/report_generate.html')

# ============ ERP MODULE VIEWS ============

@login_required
def dashboard_overview(request):
    """Trang tổng quan dashboard chính"""
    # Sử dụng logic giống staff_dashboard
    profile = getattr(request.user, 'user_profile', None)
    if not profile:
        messages.error(request, 'Bạn cần có hồ sơ người dùng để truy cập dashboard.')
        return redirect('home')
    
    # Thống kê cơ bản
    total_posts = Post.objects.count()
    published_posts = Post.objects.filter(published=True).count()
    draft_posts = total_posts - published_posts
    total_courses = Course.objects.count()
    
    # Thống kê dự án
    projects = Project.objects.all()
    total_projects = projects.count()
    active_projects = projects.filter(status='active').count()
    completed_projects = projects.filter(status='completed').count()
    
    # Phân quyền xem dữ liệu
    if profile.role == 'staff':
        user_posts = Post.objects.filter(author=request.user)
        user_courses = Course.objects.filter(instructor=request.user)
        user_projects = Project.objects.filter(staff=request.user)
    else:
        user_posts = Post.objects.all()[:5]
        user_courses = Course.objects.all()[:5]
        user_projects = projects
    
    # Danh sách nhân viên
    staff_list = UserProfile.objects.select_related('user').all()
    
    context = {
        'profile': profile,
        'total_posts': total_posts,
        'published_posts': published_posts,
        'draft_posts': draft_posts,
        'total_courses': total_courses,
        'user_posts': user_posts,
        'user_courses': user_courses,
        'recent_posts': Post.objects.order_by('-created_at')[:5],
        'projects': projects,
        'user_projects': user_projects,
        'total_projects': total_projects,
        'active_projects': active_projects,
        'completed_projects': completed_projects,
        'staff_list': staff_list,
        'today': timezone.now().date(),
    }
    return render(request, 'dashboard/staff_dashboard.html', context)

@login_required
def projects_management(request):
    """Trang quản lý dự án hiện đại"""
    profile = getattr(request.user, 'user_profile', None)
    if not profile:
        messages.error(request, 'Bạn cần có hồ sơ người dùng để truy cập trang này.')
        return redirect('home')
    
    # Lấy dữ liệu dự án dựa trên quyền
    if profile.role == 'staff':
        projects = Project.objects.filter(staff=request.user).select_related('company', 'project_manager')
    else:
        projects = Project.objects.all().select_related('company', 'project_manager')
    
    # Bộ lọc và tìm kiếm
    search = request.GET.get('search', '')
    status_filter = request.GET.get('status', '')
    sort_by = request.GET.get('sort', '-created_at')
    
    if search:
        projects = projects.filter(
            Q(name__icontains=search) |
            Q(code__icontains=search) |
            Q(company__name__icontains=search) |
            Q(description__icontains=search)
        )
    
    if status_filter:
        projects = projects.filter(status=status_filter)
    
    # Sắp xếp
    if sort_by in ['-created_at', 'created_at', 'name', '-name', 'start_date', '-start_date', 'end_date', '-end_date']:
        projects = projects.order_by(sort_by)
    
    # Thống kê tổng quan
    total_projects = projects.count()
    active_projects = projects.filter(status='active').count()
    completed_projects = projects.filter(status='completed').count()
    planning_projects = projects.filter(status='planning').count()
    pending_projects = projects.filter(status='pending').count()
    
    # Pagination
    paginator = Paginator(projects, 12)  # 12 projects per page - 4x3 grid
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Dữ liệu bổ sung
    companies = Company.objects.all()
    ndt_methods = NDTMethod.objects.all()
    staff_list = User.objects.filter(user_profile__role='staff').select_related('user_profile')
    equipment_list = Equipment.objects.filter(status='active')
    
    # Dự án gần đây
    recent_projects = projects.order_by('-created_at')[:5]
    
    # Dự án sắp đến hạn (trong 7 ngày tới)
    upcoming_deadline = timezone.now().date() + timedelta(days=7)
    upcoming_projects = projects.filter(
        end_date__lte=upcoming_deadline,
        end_date__gte=timezone.now().date(),
        status__in=['active', 'planning']
    ).order_by('end_date')
    
    context = {
        'projects': page_obj,
        'search': search,
        'status_filter': status_filter,
        'sort_by': sort_by,
        'total_projects': total_projects,
        'active_projects': active_projects,
        'completed_projects': completed_projects,
        'planning_projects': planning_projects,
        'pending_projects': pending_projects,
        'companies': companies,
        'ndt_methods': ndt_methods,
        'staff_list': staff_list,
        'equipment_list': equipment_list,
        'recent_projects': recent_projects,
        'upcoming_projects': upcoming_projects,
        'profile': profile,
        'status_choices': Project.STATUS_CHOICES,
    }
    return render(request, 'erp_modules/projects.html', context)

@login_required  
def staff_management(request):
    """Trang quản lý nhân viên - Chỉ Manager/Admin"""
    profile = getattr(request.user, 'user_profile', None)
    
    # Kiểm tra quyền truy cập
    if not profile or profile.role not in ['admin', 'manager']:
        messages.error(request, 'Bạn không có quyền truy cập module quản lý nhân viên.')
        return redirect('dashboard_overview')
    
    context = {
        'title': 'Quản lý nhân viên',
        'module_name': 'Quản lý nhân viên',
        'description': 'Quản lý thông tin nhân viên, chuyên môn, chứng chỉ NDT và phân quyền hệ thống.',
        'features': [
            'Quản lý hồ sơ nhân viên',
            'Theo dõi chứng chỉ NDT Level',
            'Quản lý chuyên môn và kỹ năng',
            'Phân quyền hệ thống',
            'Đánh giá hiệu suất làm việc'
        ],
        'user_role': profile.role,
        'coming_soon': True
    }
    return render(request, 'erp_modules/staff.html', context)

@login_required
def attendance_management(request):
    """Trang quản lý chấm công"""
    # Chỉ lấy staff, không lấy admin/manager/company
    staff_list = UserProfile.objects.filter(
        role='staff'
    ).select_related('user').exclude(
        user__username__in=['admin_test', 'staff_test', 'admin_cascade', 'staff_cascade']
    )
    context = {
        'title': 'Quản lý chấm công',
        'module_name': 'Quản lý chấm công', 
        'description': 'Hệ thống chấm công tự động, theo dõi giờ làm việc và tính lương nhân viên.',
        'staff_list': staff_list,
    }
    return render(request, 'erp_modules/attendance.html', context)

@login_required
def equipment_management(request):
    """Trang quản lý thiết bị - Manager/Admin có full access, Staff chỉ xem"""
    profile = getattr(request.user, 'user_profile', None)
    
    # Kiểm tra quyền truy cập cơ bản
    if not profile:
        messages.error(request, 'Bạn cần có hồ sơ người dùng để truy cập trang này.')
        return redirect('dashboard_overview')
    
    # Phân quyền theo role
    can_manage = profile.role in ['admin', 'manager']
    
    context = {
        'title': 'Quản lý thiết bị',
        'module_name': 'Quản lý thiết bị',
        'description': 'Quản lý thiết bị NDT, lịch bảo trì, hiệu chuẩn và theo dõi tình trạng hoạt động.',
        'features': [
            'Danh mục thiết bị NDT chi tiết',
            'Lịch bảo trì và hiệu chuẩn',
            'Theo dõi tình trạng thiết bị',
            'Quản lý phụ tùng thay thế',
            'Báo cáo hiệu suất thiết bị'
        ],
        'user_role': profile.role,
        'can_manage': can_manage,
        'coming_soon': True
    }
    return render(request, 'erp_modules/equipment.html', context)

@login_required
def documents_management(request):
    """Quản lý tài liệu nội bộ"""
    from .models import Document, DocumentCategory, DocumentTag
    from django.db.models import Q
    
    # Get filter parameters
    category_filter = request.GET.get('category')
    tag_filter = request.GET.get('tag') 
    search_query = request.GET.get('search')
    
    # Base queryset - only documents user can access
    documents = Document.objects.filter(status='published')
    accessible_docs = []
    
    for doc in documents:
        if doc.can_access(request.user):
            accessible_docs.append(doc.id)
    
    documents = Document.objects.filter(id__in=accessible_docs).select_related('category', 'created_by')
    
    # Apply filters
    if category_filter:
        documents = documents.filter(category__slug=category_filter)
    
    if tag_filter:
        documents = documents.filter(tags__slug=tag_filter)
        
    if search_query:
        documents = documents.filter(
            Q(title__icontains=search_query) | 
            Q(description__icontains=search_query) |
            Q(document_code__icontains=search_query)
        )
    
    # Get categories and tags for filters
    categories = DocumentCategory.objects.filter(is_active=True).order_by('order', 'name')
    tags = DocumentTag.objects.all().order_by('name')
    
    # Stats for dashboard
    total_documents = documents.count()
    user_downloads = 0
    if hasattr(request.user, 'documentaccess_set'):
        user_downloads = request.user.documentaccess_set.filter(action='download').count()
    
    # Recent documents
    recent_docs = documents.order_by('-created_at')[:10]
    
    context = {
        'title': 'Tài liệu nội bộ',
        'documents': documents.order_by('-created_at'),
        'categories': categories,
        'tags': tags,
        'recent_docs': recent_docs,
        'total_documents': total_documents,
        'user_downloads': user_downloads,
        'current_category': category_filter,
        'current_tag': tag_filter,
        'search_query': search_query,
        'user_role': getattr(request.user.user_profile, 'role', 'staff') if hasattr(request.user, 'user_profile') else 'staff'
    }
    return render(request, 'erp_modules/documents.html', context)

@login_required
def document_detail(request, slug):
    """Chi tiết tài liệu"""
    from .models import Document, DocumentAccess
    
    document = get_object_or_404(Document, slug=slug, status='published')
    
    # Check access permission
    if not document.can_access(request.user):
        messages.error(request, 'Bạn không có quyền truy cập tài liệu này.')
        return redirect('documents_management')
    
    # Log view access
    DocumentAccess.objects.create(
        document=document,
        user=request.user,
        action='view',
        ip_address=get_client_ip(request),
        user_agent=request.META.get('HTTP_USER_AGENT', '')
    )
    
    # Increment view count
    document.view_count += 1
    document.save(update_fields=['view_count'])
    
    # Get related documents
    related_docs = Document.objects.filter(
        category=document.category, 
        status='published'
    ).exclude(id=document.id)[:5]
    
    accessible_related = []
    for doc in related_docs:
        if doc.can_access(request.user):
            accessible_related.append(doc)
    
    context = {
        'document': document,
        'related_docs': accessible_related,
    }
    return render(request, 'documents/document_detail.html', context)

@login_required
def document_download(request, slug):
    """Tải xuống tài liệu"""
    from .models import Document, DocumentAccess
    from django.http import FileResponse, Http404
    import os
    
    document = get_object_or_404(Document, slug=slug, status='published')
    
    # Check access permission
    if not document.can_access(request.user):
        raise Http404("Tài liệu không tồn tại hoặc bạn không có quyền truy cập")
    
    # Check if file exists
    if not document.file or not default_storage.exists(document.file.name):
        messages.error(request, 'File tài liệu không tồn tại.')
        return redirect('document_detail', slug=slug)
    
    # Log download access
    DocumentAccess.objects.create(
        document=document,
        user=request.user,
        action='download',
        ip_address=get_client_ip(request),
        user_agent=request.META.get('HTTP_USER_AGENT', '')
    )
    
    # Increment download count
    document.download_count += 1
    document.save(update_fields=['download_count'])
    
    # Return file response
    try:
        response = FileResponse(
            document.file.open('rb'),
            as_attachment=True,
            filename=os.path.basename(document.file.name)
        )
        return response
    except Exception as e:
        messages.error(request, f'Lỗi khi tải file: {str(e)}')
        return redirect('document_detail', slug=slug)

def get_client_ip(request):
    """Lấy IP của client"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

@login_required
def document_upload(request):
    """Upload tài liệu mới"""
    from .models import Document, DocumentCategory, DocumentTag
    from .forms import DocumentForm
    
    # Kiểm tra quyền upload (chỉ manager và admin)
    if not hasattr(request.user, 'user_profile') or request.user.user_profile.role not in ['admin', 'manager']:
        messages.error(request, 'Bạn không có quyền upload tài liệu.')
        return redirect('documents_management')
    
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            document = form.save(commit=False)
            document.created_by = request.user
            document.updated_by = request.user  # Set người cập nhật cuối
            document.status = 'published'  # Auto approve for admin/manager
            document.approved_by = request.user
            document.approved_at = timezone.now()
            document.save()
            form.save_m2m()  # Save tags
            
            messages.success(request, f'Tài liệu "{document.title}" đã được upload thành công!')
            return redirect('document_detail', slug=document.slug)
        else:
            messages.error(request, 'Có lỗi xảy ra. Vui lòng kiểm tra lại thông tin.')
    else:
        form = DocumentForm()
    
    # Get categories and tags for context
    categories = DocumentCategory.objects.filter(is_active=True).order_by('order', 'name')
    tags = DocumentTag.objects.all().order_by('name')
    
    context = {
        'form': form,
        'categories': categories,
        'tags': tags,
        'title': 'Upload tài liệu mới'
    }
    return render(request, 'documents/document_upload.html', context)

@login_required
def document_edit(request, slug):
    """Chỉnh sửa tài liệu"""
    from .models import Document
    from .forms import DocumentForm
    
    document = get_object_or_404(Document, slug=slug)
    
    # Kiểm tra quyền edit
    user_profile = getattr(request.user, 'user_profile', None)
    if not user_profile:
        messages.error(request, 'Bạn không có quyền chỉnh sửa tài liệu.')
        return redirect('documents_management')
    
    # Chỉ admin, manager hoặc người tạo mới được edit
    if user_profile.role not in ['admin', 'manager'] and document.created_by != request.user:
        messages.error(request, 'Bạn chỉ có thể chỉnh sửa tài liệu của mình.')
        return redirect('document_detail', slug=slug)
    
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES, instance=document)
        if form.is_valid():
            document = form.save(commit=False)
            document.updated_by = request.user
            document.save()
            messages.success(request, f'Tài liệu "{document.title}" đã được cập nhật!')
            return redirect('document_detail', slug=document.slug)
    else:
        form = DocumentForm(instance=document)
    
    context = {
        'form': form,
        'document': document,
        'title': f'Chỉnh sửa: {document.title}'
    }
    return render(request, 'documents/document_upload.html', context)

@login_required
def document_delete(request, slug):
    """Xóa tài liệu"""
    from .models import Document
    
    document = get_object_or_404(Document, slug=slug)
    
    # Kiểm tra quyền xóa (chỉ admin hoặc người tạo)
    user_profile = getattr(request.user, 'user_profile', None)
    if not user_profile or (user_profile.role != 'admin' and document.created_by != request.user):
        messages.error(request, 'Bạn không có quyền xóa tài liệu này.')
        return redirect('document_detail', slug=slug)
    
    if request.method == 'POST':
        title = document.title
        document.delete()
        messages.success(request, f'Tài liệu "{title}" đã được xóa.')
        return redirect('documents_management')
    
    context = {
        'document': document,
        'title': f'Xóa tài liệu: {document.title}'
    }
    return render(request, 'documents/document_delete.html', context)

@login_required
def manage_categories(request):
    """Quản lý danh mục tài liệu"""
    from .models import DocumentCategory
    from .forms import DocumentCategoryForm
    
    # Kiểm tra quyền (chỉ admin)
    if not hasattr(request.user, 'user_profile') or request.user.user_profile.role != 'admin':
        messages.error(request, 'Bạn không có quyền quản lý danh mục.')
        return redirect('documents_management')
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'create':
            form = DocumentCategoryForm(request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, f'Danh mục "{form.cleaned_data["name"]}" đã được tạo!')
                return redirect('manage_categories')
        
        elif action == 'edit':
            category_id = request.POST.get('category_id')
            try:
                category = DocumentCategory.objects.get(id=category_id)
                form = DocumentCategoryForm(request.POST, instance=category)
                if form.is_valid():
                    form.save()
                    messages.success(request, f'Danh mục "{form.cleaned_data["name"]}" đã được cập nhật!')
                    return redirect('manage_categories')
            except DocumentCategory.DoesNotExist:
                messages.error(request, 'Danh mục không tồn tại!')
            return redirect('manage_categories')
        
        elif action == 'delete':
            category_id = request.POST.get('category_id')
            delete_documents = request.POST.get('delete_documents') == 'yes'
            
            try:
                category = DocumentCategory.objects.get(id=category_id)
                
                # Kiểm tra danh mục con
                children_count = category.children.count()
                if children_count > 0:
                    messages.error(request, f'Không thể xóa danh mục "{category.name}" vì đang có {children_count} danh mục con!')
                    return redirect('manage_categories')
                
                # Kiểm tra tài liệu
                doc_count = category.documents.count()
                if doc_count > 0:
                    if delete_documents:
                        # Xóa tất cả tài liệu trong danh mục
                        deleted_docs = []
                        for doc in category.documents.all():
                            deleted_docs.append(doc.title)
                            doc.delete()
                        
                        category_name = category.name
                        category.delete()
                        messages.success(request, f'Đã xóa danh mục "{category_name}" và {len(deleted_docs)} tài liệu!')
                    else:
                        # Chuyển tài liệu về danh mục mặc định hoặc danh mục khác
                        default_category = DocumentCategory.objects.filter(
                            slug='tai-lieu-tong-hop'
                        ).first()
                        
                        if not default_category:
                            # Tạo danh mục mặc định nếu chưa có
                            default_category = DocumentCategory.objects.create(
                                name='Tài liệu tổng hợp',
                                slug='tai-lieu-tong-hop',
                                description='Danh mục mặc định cho các tài liệu không phân loại',
                                icon='fas fa-folder',
                                order=999
                            )
                        
                        # Chuyển tất cả tài liệu sang danh mục mặc định
                        moved_docs = []
                        for doc in category.documents.all():
                            doc.category = default_category
                            doc.save()
                            moved_docs.append(doc.title)
                        
                        category_name = category.name
                        category.delete()
                        messages.success(
                            request, 
                            f'Đã xóa danh mục "{category_name}" và chuyển {len(moved_docs)} tài liệu về danh mục "{default_category.name}"!'
                        )
                else:
                    # Xóa danh mục trống
                    category_name = category.name
                    category.delete()
                    messages.success(request, f'Danh mục "{category_name}" đã được xóa!')
                    
            except DocumentCategory.DoesNotExist:
                messages.error(request, 'Danh mục không tồn tại!')
            return redirect('manage_categories')
    
    # GET request - hiển thị trang quản lý
    form = DocumentCategoryForm()
    categories = DocumentCategory.objects.all().order_by('order', 'name')
    
    # Thống kê cho mỗi danh mục
    categories_stats = []
    for category in categories:
        doc_count = category.documents.count()
        children_count = category.children.count()
        categories_stats.append({
            'category': category,
            'doc_count': doc_count,
            'children_count': children_count,
            'can_delete': children_count == 0  # Chỉ cần kiểm tra danh mục con
        })
    
    context = {
        'form': form,
        'categories_stats': categories_stats,
        'title': 'Quản lý danh mục tài liệu'
    }
    return render(request, 'management/manage_categories.html', context)

@login_required
def manage_tags(request):
    """Quản lý tags tài liệu"""
    from .models import DocumentTag
    from .forms import DocumentTagForm
    
    # Kiểm tra quyền (admin và manager)
    if not hasattr(request.user, 'user_profile') or request.user.user_profile.role not in ['admin', 'manager']:
        messages.error(request, 'Bạn không có quyền quản lý tags.')
        return redirect('documents_management')
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'create':
            form = DocumentTagForm(request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, f'Tag "{form.cleaned_data["name"]}" đã được tạo!')
                return redirect('manage_tags')
        
        elif action == 'delete':
            tag_id = request.POST.get('tag_id')
            try:
                tag = DocumentTag.objects.get(id=tag_id)
                tag_name = tag.name
                tag.delete()
                messages.success(request, f'Tag "{tag_name}" đã được xóa!')
            except DocumentTag.DoesNotExist:
                messages.error(request, 'Tag không tồn tại!')
            return redirect('manage_tags')
    
    form = DocumentTagForm()
    tags = DocumentTag.objects.all().order_by('name')
    
    # Thống kê sử dụng tags
    tags_stats = []
    for tag in tags:
        doc_count = tag.document_set.count()
        tags_stats.append({
            'tag': tag,
            'doc_count': doc_count
        })
    
    context = {
        'form': form,
        'tags_stats': tags_stats,
        'title': 'Quản lý Tags tài liệu'
    }
    return render(request, 'management/manage_tags.html', context)

@login_required
def quality_management(request):
    """Trang quản lý chất lượng - Manager/Admin"""
    profile = getattr(request.user, 'user_profile', None)
    
    # Kiểm tra quyền truy cập
    if not profile or profile.role not in ['admin', 'manager']:
        messages.error(request, 'Bạn không có quyền truy cập module quản lý chất lượng.')
        return redirect('dashboard_overview')
    
    context = {
        'title': 'Quản lý chất lượng',
        'module_name': 'Quản lý chất lượng',
        'description': 'Hệ thống quản lý chất lượng ISO 9001, kiểm soát quy trình và đảm bảo tiêu chuẩn NDT.',
        'features': [
            'Checklist chất lượng theo tiêu chuẩn',
            'Audit nội bộ và đánh giá',
            'Quản lý đơn hàng và khiếu nại',
            'Báo cáo chất lượng định kỳ',
            'Cải tiến liên tục (Kaizen)'
        ],
        'user_role': profile.role,
        'coming_soon': True
    }
    return render(request, 'erp_modules/quality.html', context)

@login_required
def analytics_management(request):
    """Trang phân tích phát triển - Manager/Admin"""
    profile = getattr(request.user, 'user_profile', None)
    
    # Kiểm tra quyền truy cập
    if not profile or profile.role not in ['admin', 'manager']:
        messages.error(request, 'Bạn không có quyền truy cập module phân tích dữ liệu.')
        return redirect('dashboard_overview')
    
    context = {
        'title': 'Phân tích phát triển',
        'module_name': 'Phân tích & Business Intelligence',
        'description': 'Dashboard phân tích doanh thu, hiệu suất và xu hướng phát triển công ty.',
        'features': [
            'Dashboard doanh thu và lợi nhuận',
            'Phân tích hiệu suất nhân viên',
            'Báo cáo xu hướng thị trường NDT',
            'Dự đoán và lập kế hoạch',
            'KPIs và metrics quan trọng'
        ],
        'user_role': profile.role,
        'coming_soon': True
    }
    return render(request, 'erp_modules/analytics.html', context)

def project_list(request):
    """Trang danh sách dự án công khai"""
    projects = PublicProject.objects.filter(published=True).order_by('-created_at')
    
    # Search functionality
    search = request.GET.get('search')
    if search:
        projects = projects.filter(
            Q(title__icontains=search) | 
            Q(summary__icontains=search) |
            Q(content__icontains=search) |
            Q(client_name__icontains=search) |
            Q(tags__icontains=search)
        )
    
    # Filter by project type
    project_type = request.GET.get('type')
    if project_type:
        projects = projects.filter(project_type__icontains=project_type)
    
    # Pagination
    paginator = Paginator(projects, 9)  # 9 projects per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get project types for filter
    project_types = PublicProject.objects.filter(published=True).values_list('project_type', flat=True).distinct()
    
    context = {
        'projects': page_obj,
        'search': search,
        'project_type': project_type,
        'project_types': project_types,
        'total_projects': projects.count(),
    }
    return render(request, 'projects/project_list.html', context)

def project_detail(request, slug):
    """Trang chi tiết dự án công khai"""
    project = get_object_or_404(PublicProject, slug=slug, published=True)
    
    # Increment view count
    project.view_count += 1
    project.save(update_fields=['view_count'])
    
    # Get related projects (same type or random)
    related_projects = PublicProject.objects.filter(
        published=True
    ).exclude(id=project.id)
    
    # Try to get same project type first
    same_type_projects = related_projects.filter(project_type=project.project_type)
    if same_type_projects.exists():
        related_projects = same_type_projects
    
    related_projects = related_projects.order_by('-created_at')[:3]
    
    context = {
        'project': project,
        'related_projects': related_projects,
    }
    return render(request, 'projects/project_detail_public.html', context)

@csrf_exempt
@require_POST
def change_language(request):
    """API để thay đổi ngôn ngữ"""
    language = request.POST.get('language')
    if language:
        translation.activate(language)
        request.session['_language'] = language  # Sửa thành string constant
    return JsonResponse({'success': True})

@login_required
def ndt_methods_management(request):
    """View quản lý phương pháp NDT"""
    if not hasattr(request.user, 'user_profile') or request.user.user_profile.role not in ['admin', 'manager']:
        messages.error(request, 'Bạn không có quyền truy cập trang này.')
        return redirect('staff_dashboard')
    
    methods = NDTMethod.objects.all().order_by('code')
    
    context = {
        'methods': methods,
        'title': 'Quản lý Phương pháp NDT'
    }
    return render(request, 'management/ndt_methods.html', context)

@login_required
def create_ndt_method(request):
    """Tạo phương pháp NDT mới"""
    if not hasattr(request.user, 'user_profile') or request.user.user_profile.role not in ['admin', 'manager']:
        messages.error(request, 'Bạn không có quyền tạo phương pháp NDT.')
        return redirect('staff_dashboard')
    
    if request.method == 'POST':
        code = request.POST.get('code', '').strip().upper()
        name = request.POST.get('name', '').strip()
        description = request.POST.get('description', '').strip()
        
        if not code or not name:
            messages.error(request, 'Mã và tên phương pháp không được để trống.')
            return redirect('ndt_methods_management')
        
        if NDTMethod.objects.filter(code=code).exists():
            messages.error(request, f'Mã phương pháp "{code}" đã tồn tại.')
            return redirect('ndt_methods_management')
        
        NDTMethod.objects.create(
            code=code,
            name=name,
            description=description
        )
        messages.success(request, f'Đã tạo phương pháp NDT "{code} - {name}" thành công.')
        return redirect('ndt_methods_management')
    
    return redirect('ndt_methods_management')

@login_required 
def delete_ndt_method(request, method_id):
    """Xóa phương pháp NDT"""
    if not hasattr(request.user, 'user_profile') or request.user.user_profile.role not in ['admin', 'manager']:
        messages.error(request, 'Bạn không có quyền xóa phương pháp NDT.')
        return redirect('staff_dashboard')
    
    try:
        method = NDTMethod.objects.get(id=method_id)
        method_name = f"{method.code} - {method.name}"
        method.delete()
        messages.success(request, f'Đã xóa phương pháp NDT "{method_name}" thành công.')
    except NDTMethod.DoesNotExist:
        messages.error(request, 'Phương pháp NDT không tồn tại.')
    
    return redirect('ndt_methods_management')

@login_required
def create_default_ndt_methods(request):
    """Tạo các phương pháp NDT mặc định"""
    if not hasattr(request.user, 'user_profile') or request.user.user_profile.role not in ['admin', 'manager']:
        messages.error(request, 'Bạn không có quyền thực hiện chức năng này.')
        return redirect('staff_dashboard')
    
    default_methods = [
        {'code': 'UT', 'name': 'Ultrasonic Testing (Siêu âm)', 'description': 'Kiểm tra bằng sóng siêu âm để phát hiện khuyết tật bên trong vật liệu'},
        {'code': 'RT', 'name': 'Radiographic Testing (X-quang)', 'description': 'Kiểm tra bằng tia X hoặc gamma để tạo ảnh bên trong vật liệu'},
        {'code': 'MT', 'name': 'Magnetic Particle Testing (Từ tính)', 'description': 'Kiểm tra khuyết tật bề mặt và cận bề mặt bằng từ trường'},
        {'code': 'PT', 'name': 'Liquid Penetrant Testing (Chất thấm)', 'description': 'Kiểm tra khuyết tật bề mặt bằng chất thấm màu hoặc huỳnh quang'},
        {'code': 'VT', 'name': 'Visual Testing (Quan sát)', 'description': 'Kiểm tra trực quan bằng mắt thường hoặc dụng cụ hỗ trợ'},
        {'code': 'ET', 'name': 'Eddy Current Testing (Dòng xoáy)', 'description': 'Kiểm tra bằng dòng điện xoáy để phát hiện khuyết tật và đo độ dày'},
        {'code': 'TOFD', 'name': 'Time of Flight Diffraction', 'description': 'Kỹ thuật siêu âm tiên tiến để định vị và định kích thước khuyết tật'},
        {'code': 'PA', 'name': 'Phased Array Ultrasonic', 'description': 'Siêu âm mảng pha cho hình ảnh chi tiết hơn'},
        {'code': 'TT', 'name': 'Thickness Testing (Đo độ dày)', 'description': 'Đo độ dày vật liệu bằng siêu âm'},
        {'code': 'HT', 'name': 'Hardness Testing (Đo độ cứng)', 'description': 'Kiểm tra độ cứng bề mặt vật liệu'}
    ]
    
    created_count = 0
    for method_data in default_methods:
        method, created = NDTMethod.objects.get_or_create(
            code=method_data['code'],
            defaults={
                'name': method_data['name'],
                'description': method_data['description']
            }
        )
        if created:
            created_count += 1
    
    if created_count > 0:
        messages.success(request, f'Đã tạo {created_count} phương pháp NDT mặc định.')
    else:
        messages.info(request, 'Tất cả phương pháp NDT mặc định đã tồn tại.')
    
    return redirect('ndt_methods_management')

# ============ PROJECT FILE MANAGEMENT VIEWS ============

@login_required
def edit_project_file(request, project_id, file_id):
    """Sửa thông tin file dự án"""
    project = get_object_or_404(Project, id=project_id)
    project_file = get_object_or_404(ProjectFile, id=file_id, project=project)
    
    # Kiểm tra quyền
    if not (request.user.user_profile.role in ['admin', 'manager'] or 
            request.user == project.project_manager or
            request.user == project_file.uploaded_by):
        return JsonResponse({'success': False, 'error': 'Không có quyền sửa file này'})
    
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        description = request.POST.get('description', '').strip()
        
        if not name:
            return JsonResponse({'success': False, 'error': 'Tên file không được để trống'})
        
        project_file.name = name
        project_file.description = description
        project_file.save()
        
        return JsonResponse({'success': True, 'message': 'Cập nhật file thành công'})
    
    return JsonResponse({'success': False, 'error': 'Phương thức không hợp lệ'})

@login_required  
def delete_project_file(request, project_id, file_id):
    """Xóa file dự án"""
    project = get_object_or_404(Project, id=project_id)
    project_file = get_object_or_404(ProjectFile, id=file_id, project=project)
    
    # Kiểm tra quyền
    if not (request.user.user_profile.role in ['admin', 'manager'] or 
            request.user == project.project_manager or
            request.user == project_file.uploaded_by):
        messages.error(request, 'Bạn không có quyền xóa file này.')
        return redirect('project_detail', project_id=project.id)
    
    if request.method == 'POST':
        file_name = project_file.name
        
        # Xóa file thực tế nếu tồn tại
        if project_file.file and default_storage.exists(project_file.file.name):
            default_storage.delete(project_file.file.name)
        
        # Xóa record từ database
        project_file.delete()
        messages.success(request, f'Đã xóa file "{file_name}" thành công.')
    
    return redirect('project_detail', project_id=project.id)

@csrf_exempt
@require_http_methods(["POST"])
@login_required
def create_leave_request(request):
    """API tạo yêu cầu nghỉ phép"""
    try:
        data = json.loads(request.body)
        
        # Lấy thông tin người bàn giao
        handover_person_id = data.get('handoverPersonId')
        handover_person = None
        if handover_person_id:
            try:
                handover_person = User.objects.get(id=handover_person_id)
            except User.DoesNotExist:
                pass
        
        # Tạo yêu cầu nghỉ phép
        leave_request = LeaveRequest.objects.create(
            employee=request.user,
            leave_type=data.get('leave_type', 'personal'),
            start_date=data.get('startDate'),
            end_date=data.get('endDate'),
            total_days=1,  # Tính toán sau
            reason=data.get('reason'),
            handover_person=handover_person,
            handover_tasks=data.get('handoverTasks', '')
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Yêu cầu nghỉ phép đã được tạo thành công',
            'request_id': leave_request.id
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Lỗi: {str(e)}'
        }, status=400)

@require_http_methods(["GET"])
@login_required
def get_leave_requests(request):
    """API lấy danh sách yêu cầu nghỉ phép"""
    try:
        user_role = getattr(request.user.user_profile, 'role', 'staff')
        
        if user_role in ['admin', 'company']:
            # Admin/Company thấy tất cả
            requests = LeaveRequest.objects.all()
        elif user_role == 'manager':
            # Manager thấy tất cả
            requests = LeaveRequest.objects.all()
        else:
            # Staff chỉ thấy của mình và những yêu cầu mà họ là người được bàn giao (cấp 1)
            requests = LeaveRequest.objects.filter(
                Q(employee=request.user) | 
                Q(handover_person=request.user)
            )
        
        requests_data = []
        for req in requests.order_by('-created_at'):
            requests_data.append({
                'id': str(req.id),
                'startDate': req.start_date.strftime('%Y-%m-%d'),
                'endDate': req.end_date.strftime('%Y-%m-%d'),
                'reason': req.reason,
                'handoverPerson': req.handover_person.get_full_name() if req.handover_person else '',
                'handoverPersonId': str(req.handover_person.id) if req.handover_person else '',
                'handoverTasks': req.handover_tasks,
                'status': req.status,
                'submittedAt': req.created_at.isoformat(),
                'submittedBy': req.employee.get_full_name(),
                'userId': req.employee.id,
                'employeeName': req.employee.get_full_name(),
                
                'handoverApproval': req.handover_approval,
                'managerApproval': req.manager_approval,
                'companyApproval': req.company_approval,
                
                'handoverApprovedBy': req.handover_approved_by.get_full_name() if req.handover_approved_by else '',
                'handoverApprovedAt': req.handover_approved_at.isoformat() if req.handover_approved_at else None,
                'handoverRejectionReason': req.handover_rejection_reason,
                
                'managerApprovedBy': req.manager_approved_by.get_full_name() if req.manager_approved_by else '',
                'managerApprovedAt': req.manager_approved_at.isoformat() if req.manager_approved_at else None,
                'managerRejectionReason': req.manager_rejection_reason,
                
                'companyApprovedBy': req.company_approved_by.get_full_name() if req.company_approved_by else '',
                'companyApprovedAt': req.company_approved_at.isoformat() if req.company_approved_at else None,
                'companyRejectionReason': req.company_rejection_reason,
            })
        
        return JsonResponse({
            'success': True,
            'requests': requests_data
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Lỗi: {str(e)}'
        }, status=400)

@csrf_exempt
@require_http_methods(["POST"])
@login_required
def approve_leave_request(request):
    """API phê duyệt yêu cầu nghỉ phép"""
    try:
        data = json.loads(request.body)
        request_id = data.get('request_id')
        level = data.get('level')  # 'handover', 'manager', 'company'
        action = data.get('action')  # 'approve', 'reject'
        reason = data.get('reason', '')
        
        leave_request = LeaveRequest.objects.get(id=request_id)
        
        # Kiểm tra quyền phê duyệt
        if not leave_request.can_approve(request.user):
            return JsonResponse({
                'success': False,
                'message': 'Bạn không có quyền phê duyệt yêu cầu này'
            }, status=403)
        
        # Xác định cấp phê duyệt phù hợp dựa trên quyền của user
        user_role = getattr(request.user.user_profile, 'role', 'staff')
        
        # Nếu admin/company phê duyệt, ưu tiên cấp cao nhất còn pending
        if (user_role == 'admin' or user_role == 'company') and level == 'company':
            # Công ty phê duyệt/từ chối
            leave_request.company_approval = 'approved' if action == 'approve' else 'rejected'
            leave_request.company_approved_by = request.user
            leave_request.company_approved_at = timezone.now()
            if action == 'reject':
                leave_request.company_rejection_reason = reason
            else:
                # Nếu công ty duyệt, tự động duyệt các cấp dưới
                if leave_request.manager_approval == 'pending':
                    leave_request.manager_approval = 'approved'
                    leave_request.manager_approved_by = request.user
                    leave_request.manager_approved_at = timezone.now()
                if leave_request.handover_approval == 'pending':
                    leave_request.handover_approval = 'approved'
                    leave_request.handover_approved_by = request.user
                    leave_request.handover_approved_at = timezone.now()
                    
        elif (user_role == 'admin' or user_role == 'company') and level == 'manager':
            # Admin phê duyệt ở cấp manager
            leave_request.manager_approval = 'approved' if action == 'approve' else 'rejected'
            leave_request.manager_approved_by = request.user
            leave_request.manager_approved_at = timezone.now()
            if action == 'reject':
                leave_request.manager_rejection_reason = reason
            else:
                # Nếu admin duyệt manager, tự động duyệt handover (nếu chưa duyệt)
                if leave_request.handover_approval == 'pending':
                    leave_request.handover_approval = 'approved'
                    leave_request.handover_approved_by = request.user
                    leave_request.handover_approved_at = timezone.now()
                    
        elif (user_role == 'admin' or user_role == 'company') and level == 'handover':
            # Admin phê duyệt ở cấp handover
            leave_request.handover_approval = 'approved' if action == 'approve' else 'rejected'
            leave_request.handover_approved_by = request.user
            leave_request.handover_approved_at = timezone.now()
            if action == 'reject':
                leave_request.handover_rejection_reason = reason
                
        elif level == 'manager':
            # Quản lý phê duyệt/từ chối
            leave_request.manager_approval = 'approved' if action == 'approve' else 'rejected'
            leave_request.manager_approved_by = request.user
            leave_request.manager_approved_at = timezone.now()
            if action == 'reject':
                leave_request.manager_rejection_reason = reason
            else:
                # Nếu quản lý duyệt, tự động duyệt cấp handover (nếu chưa duyệt)
                if leave_request.handover_approval == 'pending':
                    leave_request.handover_approval = 'approved'
                    leave_request.handover_approved_by = request.user
                    leave_request.handover_approved_at = timezone.now()
                    
        elif level == 'handover':
            # Người bàn giao chỉ có thể phê duyệt cấp của mình
            leave_request.handover_approval = 'approved' if action == 'approve' else 'rejected'
            leave_request.handover_approved_by = request.user
            leave_request.handover_approved_at = timezone.now()
            if action == 'reject':
                leave_request.handover_rejection_reason = reason
        
        # Cập nhật trạng thái tổng thể
        final_status, _, _ = leave_request.get_final_status()
        leave_request.status = final_status
        
        leave_request.save()
        
        # Tự động tạo/cập nhật bản ghi chấm công
        from .models import Attendance
        
        if final_status == 'approved':
            # Nếu được duyệt, tạo bản ghi chấm công cho các ngày nghỉ phép
            Attendance.create_from_leave_request(leave_request, work_type='P')
        elif final_status == 'rejected':
            # Nếu bị từ chối, tạo bản ghi chấm công cho các ngày nghỉ không phép
            Attendance.create_from_leave_request(leave_request, work_type='N')
        else:
            # Nếu vẫn đang chờ, cập nhật bản ghi chấm công hiện có (nếu có)
            Attendance.update_from_leave_request(leave_request)
        
        return JsonResponse({
            'success': True,
            'message': f'Đã {"phê duyệt" if action == "approve" else "từ chối"} yêu cầu nghỉ phép'
        })
        
    except LeaveRequest.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Không tìm thấy yêu cầu nghỉ phép'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Lỗi: {str(e)}'
        }, status=400)

@csrf_exempt
@require_http_methods(["DELETE"])
@login_required
def delete_leave_request(request, request_id):
    """API xóa yêu cầu nghỉ phép (chỉ người tạo mới được xóa).
    Khi xóa, đồng thời xóa các bản ghi chấm công được tạo/gắn từ yêu cầu này.
    """
    try:
        leave_request = LeaveRequest.objects.get(id=request_id)
        
        # Chỉ người tạo mới được xóa yêu cầu của mình
        if leave_request.employee != request.user:
            return JsonResponse({
                'success': False,
                'message': 'Bạn chỉ có thể xóa yêu cầu nghỉ phép của chính mình'
            }, status=403)
        
        # Xóa các bản ghi Attendance liên quan trước
        from .models import Attendance
        Attendance.delete_for_leave_request(leave_request)
        
        # Sau đó xóa yêu cầu nghỉ
        leave_request.delete()
        
        return JsonResponse({
            'success': True,
            'message': 'Đã xóa yêu cầu nghỉ phép và dữ liệu chấm công liên quan'
        })
        
    except LeaveRequest.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Không tìm thấy yêu cầu nghỉ phép'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Lỗi: {str(e)}'
        }, status=400)

@login_required
def get_system_notifications(request):
    """API lấy thông báo hệ thống chung"""
    try:
        user_role = getattr(request.user.user_profile, 'role', 'staff')
        notifications = []
        
        # Thông báo về leave requests mới
        recent_leave_requests = LeaveRequest.objects.filter(
            status='pending'
        ).order_by('-created_at')[:5]
        
        for req in recent_leave_requests:
            # Kiểm tra quyền xem leave request
            can_view = False
            if user_role in ['admin', 'company', 'manager']:
                can_view = True
            elif req.employee == request.user:
                can_view = True
            elif req.handover_person == request.user:
                can_view = True
            
            notifications.append({
                'type': 'leave_request',
                'message': f'{req.employee.get_full_name()} vừa xin nghỉ phép chờ phê duyệt',
                'time': req.created_at.strftime('%H:%M'),
                'date': req.created_at.strftime('%d/%m/%Y'),
                'url': '/dashboard/attendance/',
                'can_view': can_view
            })
        
        # Thông báo về documents mới (nếu có)
        from .models import Document
        if Document.objects.exists():
            recent_docs = Document.objects.filter(
                status='published'
            ).order_by('-created_at')[:3]
            
            for doc in recent_docs:
                # Kiểm tra quyền xem document
                can_view = False
                if user_role in ['admin', 'company', 'manager']:
                    can_view = True
                elif doc.created_by == request.user:
                    can_view = True
                elif hasattr(doc, 'access_level') and doc.access_level == 'public':
                    can_view = True
                
                notifications.append({
                    'type': 'document',
                    'message': f'{doc.created_by.get_full_name()} vừa thêm tài liệu {doc.title}',
                    'time': doc.created_at.strftime('%H:%M'),
                    'date': doc.created_at.strftime('%d/%m/%Y'),
                    'url': f'/documents/{doc.slug}/',
                    'can_view': can_view
                })
        
        # Thông báo về projects mới (nếu có)
        from .models import Project
        if Project.objects.exists():
            recent_projects = Project.objects.filter(
                status='in_progress'
            ).order_by('-created_at')[:3]
            
            for project in recent_projects:
                # Kiểm tra quyền xem project
                can_view = False
                if user_role in ['admin', 'company', 'manager']:
                    can_view = True
                elif hasattr(project, 'assigned_to') and project.assigned_to == request.user:
                    can_view = True
                elif hasattr(project, 'created_by') and project.created_by == request.user:
                    can_view = True
                
                notifications.append({
                    'type': 'project',
                    'message': f'Dự án {project.name} đang được thực hiện',
                    'time': project.created_at.strftime('%H:%M'),
                    'date': project.created_at.strftime('%d/%m/%Y'),
                    'url': f'/projects/{project.id}/',
                    'can_view': can_view
                })
        
        # Sắp xếp theo thời gian mới nhất
        notifications.sort(key=lambda x: f"{x['date']} {x['time']}", reverse=True)
        
        return JsonResponse({
            'success': True,
            'notifications': notifications[:10],  # Chỉ lấy 10 thông báo mới nhất
            'count': len(notifications)
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Lỗi: {str(e)}'
        }, status=400)

@csrf_exempt
@require_http_methods(["GET"])
@login_required
def get_attendance_data(request):
    """API lấy dữ liệu chấm công của user"""
    try:
        from .models import Attendance
        
        # Lấy dữ liệu chấm công của user hiện tại
        attendances = Attendance.objects.filter(employee=request.user).order_by('-date')
        
        # Chuyển đổi thành format JSON
        data = []
        for attendance in attendances:
            data.append({
                'id': attendance.id,
                'date': attendance.date.strftime('%Y-%m-%d'),
                'workType': attendance.work_type,
                'constructionName': attendance.construction_name or '',
                'ndtMethod': attendance.ndt_method or '',
                'pautMeters': float(attendance.paut_meters) if attendance.paut_meters else 0,
                'tofdMeters': float(attendance.tofd_meters) if attendance.tofd_meters else 0,
                'dayShift': attendance.day_shift,
                'nightShift': attendance.night_shift,
                'dayOvertimeEnd': attendance.day_overtime_end.strftime('%H:%M') if attendance.day_overtime_end else '',
                'nightOvertimeEnd': attendance.night_overtime_end.strftime('%H:%M') if attendance.night_overtime_end else '',
                'overtimeHours': str(attendance.overtime_hours),
                'hotelExpense': float(attendance.hotel_expense) if attendance.hotel_expense else 0,
                'shoppingExpense': float(attendance.shopping_expense) if attendance.shopping_expense else 0,
                'phoneExpense': float(attendance.phone_expense) if attendance.phone_expense else 0,
                'otherExpense': float(attendance.other_expense) if attendance.other_expense else 0,
                'otherExpenseDesc': attendance.other_expense_desc or '',
                'workNote': attendance.work_note or '',
                'isAutoGenerated': attendance.is_auto_generated,
                'canBeEdited': attendance.can_be_edited,
                'timestamp': attendance.created_at.isoformat(),
                'leaveRequestId': attendance.leave_request.id if attendance.leave_request else None
            })
        
        return JsonResponse({
            'success': True,
            'data': data
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Lỗi: {str(e)}'
        }, status=400)

@csrf_exempt
@require_http_methods(["POST"])
@login_required
def save_attendance_data(request):
    """API lưu dữ liệu chấm công"""
    try:
        from .models import Attendance
        from datetime import datetime
        
        data = json.loads(request.body)
        date = data.get('date')
        work_type = data.get('workType')
        
        # Kiểm tra dữ liệu bắt buộc
        if not date or not work_type:
            return JsonResponse({
                'success': False,
                'message': 'Thiếu thông tin bắt buộc'
            }, status=400)
        
        # Chuyển đổi ngày
        try:
            attendance_date = datetime.strptime(date, '%Y-%m-%d').date()
        except ValueError:
            return JsonResponse({
                'success': False,
                'message': 'Định dạng ngày không hợp lệ'
            }, status=400)
        
        # Kiểm tra xem đã có bản ghi cho ngày này chưa
        existing_record = Attendance.objects.filter(
            employee=request.user,
            date=attendance_date
        ).first()
        
        if existing_record:
            # Cập nhật bản ghi hiện có
            if not existing_record.can_edit(request.user):
                return JsonResponse({
                    'success': False,
                    'message': 'Bạn không có quyền chỉnh sửa bản ghi này'
                }, status=403)
            
            # Cập nhật thông tin
            existing_record.work_type = work_type
            existing_record.construction_name = data.get('constructionName', '')
            existing_record.ndt_method = data.get('ndtMethod', '')
            existing_record.paut_meters = float(data.get('pautMeters', 0))
            existing_record.tofd_meters = float(data.get('tofdMeters', 0))
            existing_record.day_shift = data.get('dayShift', False)
            existing_record.night_shift = data.get('nightShift', False)
            
            # Xử lý thời gian tăng ca
            day_overtime = data.get('dayOvertimeEnd', '')
            if day_overtime:
                try:
                    existing_record.day_overtime_end = datetime.strptime(day_overtime, '%H:%M').time()
                except ValueError:
                    existing_record.day_overtime_end = None
            else:
                existing_record.day_overtime_end = None
                
            night_overtime = data.get('nightOvertimeEnd', '')
            if night_overtime:
                try:
                    existing_record.night_overtime_end = datetime.strptime(night_overtime, '%H:%M').time()
                except ValueError:
                    existing_record.night_overtime_end = None
            else:
                existing_record.night_overtime_end = None
            
            existing_record.overtime_hours = float(data.get('overtimeHours', 0))
            
            # Xử lý chi phí - chuyển từ boolean sang số tiền
            hotel_expense = data.get('hotelExpense', 0)
            shopping_expense = data.get('shoppingExpense', 0)
            phone_expense = data.get('phoneExpense', 0)
            other_expense = data.get('otherExpense', 0)
            
            # Chuyển đổi sang số tiền nếu là boolean
            if isinstance(hotel_expense, bool):
                existing_record.hotel_expense = 200000 if hotel_expense else 0
            else:
                existing_record.hotel_expense = float(hotel_expense) if hotel_expense else 0
                
            if isinstance(shopping_expense, bool):
                existing_record.shopping_expense = 0  # Không có giá trị mặc định cho mua sắm
            else:
                existing_record.shopping_expense = float(shopping_expense) if shopping_expense else 0
                
            if isinstance(phone_expense, bool):
                existing_record.phone_expense = 0  # Không có giá trị mặc định cho điện thoại
            else:
                existing_record.phone_expense = float(phone_expense) if phone_expense else 0
                
            if isinstance(other_expense, bool):
                existing_record.other_expense = 0  # Không có giá trị mặc định cho chi phí khác
            else:
                existing_record.other_expense = float(other_expense) if other_expense else 0
                
            existing_record.other_expense_desc = data.get('otherExpenseDesc', '')
            existing_record.work_note = data.get('workNote', '')
            existing_record.updated_by = request.user
            existing_record.save()
            
            record = existing_record
        else:
            # Tạo bản ghi mới
            # Xử lý chi phí cho bản ghi mới
            hotel_expense = data.get('hotelExpense', 0)
            shopping_expense = data.get('shoppingExpense', 0)
            phone_expense = data.get('phoneExpense', 0)
            other_expense = data.get('otherExpense', 0)
            
            # Chuyển đổi sang số tiền nếu là boolean
            if isinstance(hotel_expense, bool):
                hotel_amount = 200000 if hotel_expense else 0
            else:
                hotel_amount = float(hotel_expense) if hotel_expense else 0
                
            if isinstance(shopping_expense, bool):
                shopping_amount = 0
            else:
                shopping_amount = float(shopping_expense) if shopping_expense else 0
                
            if isinstance(phone_expense, bool):
                phone_amount = 0
            else:
                phone_amount = float(phone_expense) if phone_expense else 0
                
            if isinstance(other_expense, bool):
                other_amount = 0
            else:
                other_amount = float(other_expense) if other_expense else 0
            
            record = Attendance.objects.create(
                employee=request.user,
                date=attendance_date,
                work_type=work_type,
                construction_name=data.get('constructionName', ''),
                ndt_method=data.get('ndtMethod', ''),
                paut_meters=float(data.get('pautMeters', 0)),
                tofd_meters=float(data.get('tofdMeters', 0)),
                day_shift=data.get('dayShift', False),
                night_shift=data.get('nightShift', False),
                overtime_hours=float(data.get('overtimeHours', 0)),
                hotel_expense=hotel_amount,
                shopping_expense=shopping_amount,
                phone_expense=phone_amount,
                other_expense=other_amount,
                other_expense_desc=data.get('otherExpenseDesc', ''),
                work_note=data.get('workNote', ''),
                created_by=request.user,
                updated_by=request.user
            )
        
        return JsonResponse({
            'success': True,
            'message': 'Lưu chấm công thành công',
            'record_id': record.id
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Lỗi: {str(e)}'
        }, status=400)

@csrf_exempt
@require_http_methods(["DELETE"])
@login_required
def delete_attendance_record(request, record_id):
    """API xóa bản ghi chấm công"""
    try:
        from .models import Attendance
        
        record = Attendance.objects.get(id=record_id)
        
        # Kiểm tra quyền xóa
        if not record.can_edit(request.user):
            return JsonResponse({
                'success': False,
                'message': 'Bạn không có quyền xóa bản ghi này'
            }, status=403)
        
        record.delete()
        
        return JsonResponse({
            'success': True,
            'message': 'Xóa bản ghi thành công'
        })
        
    except Attendance.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Không tìm thấy bản ghi'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Lỗi: {str(e)}'
        }, status=400)

def export_attendance_data(request):
    """Xuất dữ liệu chấm công theo tháng cho toàn bộ nhân viên"""
    print(f"Export request from user: {request.user.username}")
    print(f"User is authenticated: {request.user.is_authenticated}")
    print(f"User is superuser: {request.user.is_superuser}")
    
    if not request.user.is_authenticated:
        print("User not authenticated")
        return JsonResponse({'error': 'Unauthorized'}, status=401)
    
    # Lấy tháng/năm từ request
    month = request.GET.get('month')
    year = request.GET.get('year')
    
    print(f"Export parameters: month={month}, year={year}")
    
    if not month or not year:
        print("Missing month or year parameters")
        return JsonResponse({'error': 'Thiếu tháng hoặc năm'}, status=400)
    
    try:
        month = int(month)
        year = int(year)
    except ValueError:
        return JsonResponse({'error': 'Tháng và năm phải là số'}, status=400)
    
    # Tính ngày đầu và cuối tháng
    start_date = date(year, month, 1)
    if month == 12:
        end_date = date(year + 1, 1, 1) - timedelta(days=1)
    else:
        end_date = date(year, month + 1, 1) - timedelta(days=1)
    
    # Lấy tất cả nhân viên có chấm công trong tháng
    employees = User.objects.filter(
        attendances__date__gte=start_date,
        attendances__date__lte=end_date
    ).distinct()
    
    print(f"Found {employees.count()} employees with attendance data")
    
    # Cấu trúc dữ liệu xuất
    export_data = {
        "export_info": {
            "company": "Hitech NDT",
            "period": f"{month:02d}/{year}",
            "export_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "version": "1.0",
            "total_employees": employees.count()
        },
        "employees": {}
    }
    
    # Xử lý từng nhân viên
    for employee in employees:
        employee_data = {
            "info": {
                "name": employee.get_full_name() or employee.username,
                "msnv": employee.username,
                "email": employee.email,
                "position": getattr(employee.user_profile, 'position', ''),
                "department": getattr(employee.user_profile, 'department', ''),
                "phone": getattr(employee.user_profile, 'phone', '')
            },
            "attendance": {
                "days": {},
                "summary": {
                    "total_work_days": 0,
                    "total_office_days": 0,
                    "total_training_days": 0,
                    "total_leave_days": 0,
                    "total_absent_days": 0,
                    "total_overtime_hours": 0,
                    "total_expenses": 0,
                    "hotel_expenses": 0,
                    "shopping_expenses": 0,
                    "phone_expenses": 0,
                    "other_expenses": 0,
                    "paut_total_meters": 0,
                    "tofd_total_meters": 0,
                    "construction_projects": [],
                    "ndt_methods_used": []
                }
            }
        }
        
        # Lấy dữ liệu chấm công của nhân viên trong tháng
        attendances = Attendance.objects.filter(
            employee=employee,
            date__gte=start_date,
            date__lte=end_date
        ).order_by('date')
        
        # Xử lý từng ngày
        for attendance in attendances:
            day_key = f"day_{attendance.date.day:02d}"
            
            day_data = {
                "type": attendance.work_type,
                "location": attendance.construction_name or "",
                "method": attendance.ndt_method or "",
                "paut_meters": float(attendance.paut_meters) if attendance.paut_meters else 0,
                "tofd_meters": float(attendance.tofd_meters) if attendance.tofd_meters else 0,
                "day_shift": attendance.day_shift,
                "night_shift": attendance.night_shift,
                "day_overtime_end": attendance.day_overtime_end.strftime("%H:%M") if attendance.day_overtime_end else "",
                "night_overtime_end": attendance.night_overtime_end.strftime("%H:%M") if attendance.night_overtime_end else "",
                "overtime_hours": float(attendance.overtime_hours) if attendance.overtime_hours else 0,
                "hotel_expense": float(attendance.hotel_expense) if attendance.hotel_expense else 0,
                "shopping_expense": float(attendance.shopping_expense) if attendance.shopping_expense else 0,
                "phone_expense": float(attendance.phone_expense) if attendance.phone_expense else 0,
                "other_expense": float(attendance.other_expense) if attendance.other_expense else 0,
                "other_expense_desc": attendance.other_expense_desc or "",
                "note": attendance.work_note or "",
                "created_at": attendance.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                "updated_at": attendance.updated_at.strftime("%Y-%m-%d %H:%M:%S")
            }
            
            employee_data["attendance"]["days"][day_key] = day_data
            
            # Cập nhật summary
            if attendance.work_type == 'W':
                employee_data["attendance"]["summary"]["total_work_days"] += 1
                if attendance.construction_name and attendance.construction_name not in employee_data["attendance"]["summary"]["construction_projects"]:
                    employee_data["attendance"]["summary"]["construction_projects"].append(attendance.construction_name)
                if attendance.ndt_method and attendance.ndt_method not in employee_data["attendance"]["summary"]["ndt_methods_used"]:
                    employee_data["attendance"]["summary"]["ndt_methods_used"].append(attendance.ndt_method)
                
                # Thống kê số mét vượt PAUT và TOFD
                if attendance.paut_meters and attendance.paut_meters > 0:
                    if "paut_total_meters" not in employee_data["attendance"]["summary"]:
                        employee_data["attendance"]["summary"]["paut_total_meters"] = 0
                    employee_data["attendance"]["summary"]["paut_total_meters"] += float(attendance.paut_meters)
                
                if attendance.tofd_meters and attendance.tofd_meters > 0:
                    if "tofd_total_meters" not in employee_data["attendance"]["summary"]:
                        employee_data["attendance"]["summary"]["tofd_total_meters"] = 0
                    employee_data["attendance"]["summary"]["tofd_total_meters"] += float(attendance.tofd_meters)
            elif attendance.work_type == 'O':
                employee_data["attendance"]["summary"]["total_office_days"] += 1
            elif attendance.work_type == 'T':
                employee_data["attendance"]["summary"]["total_training_days"] += 1
            elif attendance.work_type == 'P':
                employee_data["attendance"]["summary"]["total_leave_days"] += 1
            elif attendance.work_type == 'N':
                employee_data["attendance"]["summary"]["total_absent_days"] += 1
            
            # Cập nhật thống kê khác
            employee_data["attendance"]["summary"]["total_overtime_hours"] += float(attendance.overtime_hours) if attendance.overtime_hours else 0
            
            # Tính tổng chi phí
            total_expenses = (float(attendance.hotel_expense or 0) + 
                            float(attendance.shopping_expense or 0) + 
                            float(attendance.phone_expense or 0) + 
                            float(attendance.other_expense or 0))
            employee_data["attendance"]["summary"]["total_expenses"] += total_expenses
            
            # Cập nhật từng loại chi phí
            if attendance.hotel_expense and attendance.hotel_expense > 0:
                employee_data["attendance"]["summary"]["hotel_expenses"] += float(attendance.hotel_expense)
            if attendance.shopping_expense and attendance.shopping_expense > 0:
                employee_data["attendance"]["summary"]["shopping_expenses"] += float(attendance.shopping_expense)
            if attendance.phone_expense and attendance.phone_expense > 0:
                employee_data["attendance"]["summary"]["phone_expenses"] += float(attendance.phone_expense)
            if attendance.other_expense and attendance.other_expense > 0:
                employee_data["attendance"]["summary"]["other_expenses"] += float(attendance.other_expense)
        
        # Tính toán thêm
        total_days = (employee_data["attendance"]["summary"]["total_work_days"] + 
                     employee_data["attendance"]["summary"]["total_office_days"] + 
                     employee_data["attendance"]["summary"]["total_training_days"])
        
        employee_data["attendance"]["summary"]["total_working_days"] = total_days
        employee_data["attendance"]["summary"]["total_days_in_month"] = end_date.day
        
        export_data["employees"][employee.username] = employee_data
    
    # Trả về JSON
    json_content = json.dumps(export_data, ensure_ascii=False, indent=2)
    print(f"Generated JSON content length: {len(json_content)} characters")
    
    response = HttpResponse(
        json_content,
        content_type='application/json'
    )
    response['Content-Disposition'] = f'attachment; filename="chamcong_{month:02d}_{year}.json"'
    response['Access-Control-Allow-Origin'] = '*'
    response['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    response['Access-Control-Allow-Headers'] = 'Content-Type, X-Requested-With'
    
    print("Export completed successfully")
    return response

@require_http_methods(["GET"])
@login_required
def get_handover_candidates(request):
    """Trả về danh sách người có thể bàn giao công việc (active users, loại trừ chính mình).
    Hỗ trợ tìm kiếm q và giới hạn limit.
    """
    try:
        query = (request.GET.get('q') or '').strip()
        try:
            limit = int(request.GET.get('limit', '50'))
        except ValueError:
            limit = 50
        
        users_qs = (User.objects.select_related('user_profile')
                    .filter(is_active=True)
                    .exclude(id=request.user.id))
        
        if query:
            users_qs = users_qs.filter(
                Q(username__icontains=query) |
                Q(first_name__icontains=query) |
                Q(last_name__icontains=query) |
                Q(email__icontains=query)
            )
        
        users_qs = users_qs.order_by('first_name', 'last_name', 'username')[:limit]
        
        users = [{
            'id': u.id,
            'username': u.username,
            'full_name': u.get_full_name() or u.username,
            'email': u.email,
            'role': getattr(u.user_profile, 'role', '')
        } for u in users_qs]
        
        return JsonResponse({'success': True, 'users': users})
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Lỗi: {str(e)}'}, status=400)