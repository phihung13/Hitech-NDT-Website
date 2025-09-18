from django.http import JsonResponse
from .models import Course, Post, Category, Comment, ContactSettings, Tag, SiteSettings, AboutPage, HomePageSettings, UserProfile, Project, ProjectFile, ProjectProgress, CourseCategory, Equipment, PublicProject, Company, NDTMethod, Attendance, Document, DocumentCategory, DocumentTag, DocumentAccessLog, DocumentFileVersion
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from .forms import PostForm, CourseForm, CommentForm, ProjectFileForm, ProjectUpdateForm, ProjectCreateForm, DocumentForm
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
from django.utils.text import slugify
import json
from datetime import timedelta, date, datetime
import shutil
from .models import LeaveRequest
from django.db import models
from django.utils import timezone
from django.db.models import Q
from decimal import Decimal
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.views import redirect_to_login
from django.urls import reverse
from django import forms
from django.utils.decorators import method_decorator
from django.forms.models import model_to_dict
from .models import EmployeeProfile

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

@staff_member_required(login_url='staff_login')
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
                # ép đi thiết lập lần đầu nếu cần
                profile, _ = UserProfile.objects.get_or_create(user=user, defaults={
                    'role': 'staff',
                    'msnv': f'HTNV-{user.id:03d}'
                })
                if getattr(profile, 'must_change_password', False) or getattr(profile, 'must_set_email', False) or not user.email:
                    return redirect('first_time_setup')
                messages.success(request, f'Chào mừng {user.username}!')
                return redirect('staff_dashboard')
            else:
                messages.error(request, 'Bạn không có quyền truy cập hệ thống nội bộ.')
        else:
            messages.error(request, 'Tên đăng nhập hoặc mật khẩu không đúng.')
    
    return render(request, 'auth/login.html')

@login_required
def first_time_setup(request):
    """Bắt buộc thiết lập email và đổi mật khẩu lần đầu"""
    profile, _ = UserProfile.objects.get_or_create(user=request.user, defaults={
        'role': 'staff',
        'msnv': f'HTNV-{request.user.id:03d}'
    })
    
    if request.method == 'POST':
        new_email = request.POST.get('email', '').strip()
        new_password = request.POST.get('new_password', '')
        confirm_password = request.POST.get('confirm_password', '')
        
        if not new_email:
            messages.error(request, 'Vui lòng nhập email.')
            return render(request, 'auth/first_time_setup.html', {'user': request.user})
        
        if new_password != confirm_password or len(new_password) < 8:
            messages.error(request, 'Mật khẩu không hợp lệ hoặc không trùng khớp (tối thiểu 8 ký tự).')
            return render(request, 'auth/first_time_setup.html', {'user': request.user, 'email': new_email})
        
        # Cập nhật email và mật khẩu
        request.user.email = new_email
        request.user.set_password(new_password)
        request.user.save()
        
        # Cập nhật cờ
        profile.must_change_password = False
        profile.must_set_email = False
        profile.password_last_changed_at = timezone.now()
        profile.save(update_fields=['must_change_password', 'must_set_email', 'password_last_changed_at'])
        
        # Re-authenticate sau khi đổi password
        user = authenticate(request, username=request.user.username, password=new_password)
        if user:
            auth_login(request, user)
        
        messages.success(request, 'Thiết lập lần đầu thành công!')
        return redirect('staff_dashboard')
    
    # GET: hiển thị form
    return render(request, 'auth/first_time_setup.html', {
        'user': request.user,
        'email': request.user.email,
    })

@staff_required
def staff_dashboard(request):
    """Dashboard nội bộ cho nhân viên"""
    # Đảm bảo UserProfile tồn tại
    profile, created = UserProfile.objects.get_or_create(
        user=request.user,
        defaults={
            'role': 'staff',
            'msnv': f'HTNV-{request.user.id:03d}'  # Tạo MSNV mặc định
        }
    )
    
    if created:
        messages.info(request, f'Đã tạo hồ sơ người dùng với MSNV: {profile.msnv}')
    
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
    # Đảm bảo UserProfile tồn tại
    profile, created = UserProfile.objects.get_or_create(
        user=request.user,
        defaults={
            'role': 'staff',
            'msnv': f'HTNV-{request.user.id:03d}'  # Tạo MSNV mặc định
        }
    )
    
    if created:
        messages.info(request, f'Đã tạo hồ sơ người dùng với MSNV: {profile.msnv}')
    
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
    """Trang quản lý nhân viên - Read-only for non-admin/manager"""
    profile = getattr(request.user, 'user_profile', None)
    user_role = getattr(profile, 'role', 'staff')
    
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
        'user_role': user_role,
        'coming_soon': True
    }
    return render(request, 'erp_modules/staff.html', context)

@login_required
def export_staff_data(request):
    """API xuất dữ liệu nhân viên với MSNV cho app"""
    profile = getattr(request.user, 'user_profile', None)
    
    # Kiểm tra quyền truy cập
    if not profile or profile.role not in ['admin', 'manager']:
        return JsonResponse({'error': 'Không có quyền truy cập'}, status=403)
    
    try:
        # Lấy tất cả nhân viên
        staff_profiles = UserProfile.objects.select_related('user').all()
        
        staff_data = []
        for profile in staff_profiles:
            staff_info = {
                'name': profile.user.get_full_name() or profile.user.username,
                'msnv': profile.msnv or '',
                'cccd': '',  # Có thể thêm trường CCCD sau
                'phone': profile.phone or '',
                'birth_date': '',  # Có thể thêm trường ngày sinh sau
                'hometown': '',  # Có thể thêm trường quê quán sau
                'position': profile.position or '',
                'department': profile.department or '',
                'education': '',  # Có thể thêm trường học vấn sau
                'certificates': profile.certificates or '',
                'dependents': '',  # Có thể thêm trường người phụ thuộc sau
                'bank_account': '',  # Có thể thêm trường tài khoản ngân hàng sau
                'bank_name': ''  # Có thể thêm trường tên ngân hàng sau
            }
            staff_data.append(list(staff_info.values()))
        
        # Format giống với file nhanvien.json của app
        export_data = {
            'timestamp': timezone.now().isoformat(),
            'total_records': len(staff_data),
            'data': staff_data
        }
        
        return JsonResponse(export_data, safe=False)
        
    except Exception as e:
        return JsonResponse({'error': f'Lỗi xuất dữ liệu: {str(e)}'}, status=500)

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
    """View for managing documents with versioning support"""
    if request.method == 'POST':
        print("=== DEBUG: POST request received ===")
        print(f"Files: {request.FILES}")
        print(f"POST data: {request.POST}")
        
        # Handle file upload manually
        title = request.POST.get('title', '')
        file = request.FILES.get('file')
        description = request.POST.get('description', '')
        category_id = request.POST.get('category')
        parent_document_id = request.POST.get('parent_document_id')
        change_note = request.POST.get('change_note', '')
        
        print(f"Title: {title}")
        print(f"File: {file}")
        print(f"Description: {description}")
        print(f"Parent Document ID: {parent_document_id}")
        print(f"Change Note: {change_note}")
        
        if file:
            # Check if this is an update to existing document
            if parent_document_id:
                print("=== DEBUG: This is an UPDATE ===")
                try:
                    # This is an update - ghi đè lên tài liệu cũ
                    document = Document.objects.get(id=parent_document_id)
                    print(f"Document found: {document.title}")
                    
                    # Tắt trạng thái current của tất cả file cũ
                    document.file_versions.update(is_current=False)
                    
                    # Tạo phiên bản file mới
                    version_number = document.get_latest_version_number() + 1
                    file_version = DocumentFileVersion.objects.create(
                        document=document,
                        file=file,
                        file_name=file.name,
                        file_size=file.size,
                        file_type=file.name.split('.')[-1].lower() if '.' in file.name else '',
                        uploaded_by=request.user,
                        is_current=True,
                        change_note=change_note or f'Cập nhật lên v{version_number}',
                        version_number=version_number
                    )
                    
                    # Cập nhật file hiện tại của document
                    document.file = file
                    document.description = description or document.description
                    document.title = title or document.title
                    document.created_by = request.user  # Cập nhật người upload gần nhất
                    document.updated_at = timezone.now()
                    document.file_size = file.size
                    document.file_type = file_version.file_type
                    
                    print("=== DEBUG: Saving updated document ===")
                    document.save()
                    print(f"Document updated with ID: {document.id}, Version: v{version_number}")
                    
                    messages.success(request, f'Tài liệu đã được cập nhật thành công! Phiên bản mới: v{version_number}')
                    return redirect('documents_management')
                    
                except Document.DoesNotExist:
                    messages.error(request, 'Tài liệu không tồn tại.')
                    return redirect('documents_management')
                except Exception as e:
                    print(f"=== DEBUG: Error during update: {str(e)} ===")
                    messages.error(request, f'Lỗi khi cập nhật tài liệu: {str(e)}')
                    return redirect('documents_management')
            else:
                # This is a new document upload
                print("=== DEBUG: This is a NEW document ===")
                try:
                    category = DocumentCategory.objects.get(id=category_id) if category_id else None
                    
                    document = Document(
                        title=title,
                        file=file,
                        description=description,
                        category=category,
                        created_by=request.user
                    )
                    
                    print("=== DEBUG: Saving new document ===")
                    document.save()
                    print(f"New document saved with ID: {document.id}")
                    
                    # Tạo DocumentFileVersion cho file mới
                    file_version = DocumentFileVersion.objects.create(
                        document=document,
                        file=file,
                        file_name=file.name,
                        file_size=file.size,
                        file_type=file.name.split('.')[-1].lower() if '.' in file.name else '',
                        uploaded_by=request.user,
                        is_current=True,
                        change_note='File gốc',
                        version_number=1
                    )
                    
                    messages.success(request, f'Tài liệu "{document.title}" đã được upload thành công!')
                    return redirect('documents_management')
                    
                except Exception as e:
                    messages.error(request, f'Lỗi khi upload tài liệu: {str(e)}')
                    return redirect('documents_management')
        else:
            messages.error(request, 'Vui lòng chọn file để upload.')
            return redirect('documents_management')
    
    # GET request - show documents list
    documents = Document.objects.filter(is_active=True).order_by('-updated_at')
    categories = DocumentCategory.objects.all()
    
    context = {
        'documents': documents,
        'categories': categories,
        'title': 'Quản lý tài liệu'
    }
    return render(request, 'erp_modules/documents.html', context)

@login_required
def document_detail(request, slug):
    """View for displaying document details with version history"""
    document = get_object_or_404(Document, slug=slug, is_active=True)
    
    # Tăng view count
    document.view_count += 1
    document.save(update_fields=['view_count'])
    
    # Lấy lịch sử file
    file_versions = document.get_file_versions()
    
    # Lấy version hiện tại từ DocumentFileVersion
    current_file_version = document.current_file_version
    current_version = current_file_version.version_number if current_file_version else 1
    
    context = {
        'document': document,
        'file_versions': file_versions,
        'current_version': current_version,
    }
    return render(request, 'documents/document_detail.html', context)

@login_required
def document_download(request, slug):
    """Download document - tải file phiên bản mới nhất"""
    try:
        document = get_object_or_404(Document, slug=slug, is_active=True)
    except:
        # Fallback for documents without slug
        document = get_object_or_404(Document, id=slug, is_active=True)
    
    # Lấy file phiên bản hiện tại từ DocumentFileVersion
    current_file_version = document.current_file_version
    
    if current_file_version:
        # Tải file từ DocumentFileVersion
        file_to_download = current_file_version.file
        file_name = current_file_version.file_name
        file_size = current_file_version.file_size
    else:
        # Fallback về file gốc nếu không có DocumentFileVersion
        file_to_download = document.file
        file_name = document.file.name.split('/')[-1] if document.file.name else document.title
        file_size = document.file.size if document.file else 0
    
    # Log download
    try:
        DocumentAccessLog.objects.create(
            user=request.user,
            document=document,
            action='download'
        )
        
        # Increment download count
        document.download_count += 1
        document.save(update_fields=['download_count'])
    except:
        pass
    
    # Return file response với tên file chính xác
    if file_to_download:
        response = HttpResponse(file_to_download.read(), content_type='application/octet-stream')
        response['Content-Disposition'] = f'attachment; filename="{file_name}"'
        response['Content-Length'] = file_size
        return response
    else:
        messages.error(request, 'Không tìm thấy file để tải xuống.')
        return redirect('document_detail', slug=slug)

@login_required
def document_edit(request, slug):
    """Edit document"""
    document = get_object_or_404(Document, slug=slug, is_active=True)
    
    # Check permissions
    if not (request.user.is_superuser or request.user.is_staff or document.created_by == request.user):
        messages.error(request, 'You do not have permission to edit this document.')
        return redirect('documents_management')
    
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES, instance=document)
        if form.is_valid():
            form.save()
            messages.success(request, 'Document updated successfully!')
            return redirect('document_detail', slug=document.slug)
    else:
        form = DocumentForm(instance=document)
    
    context = {
        'form': form,
        'document': document,
        'title': f'Edit {document.title}'
    }
    return render(request, 'documents/document_edit.html', context)

@login_required
def document_delete(request, slug):
    """Delete document"""
    document = get_object_or_404(Document, slug=slug, is_active=True)
    
    # Check permissions
    if not (request.user.is_superuser or document.created_by == request.user):
        messages.error(request, 'You do not have permission to delete this document.')
        return redirect('documents_management')
    
    if request.method == 'POST':
        document.is_active = False
        document.save()
        messages.success(request, 'Document deleted successfully!')
        return redirect('documents_management')
    
    context = {
        'document': document,
        'title': f'Delete {document.title}'
    }
    return render(request, 'documents/document_delete.html', context)

@login_required
def document_share(request, slug):
    """Share document"""
    document = get_object_or_404(Document, slug=slug, is_active=True)
    
    # Log share
    DocumentAccessLog.objects.create(
        user=request.user,
        document=document,
        action='share'
    )
    
    context = {
        'document': document,
        'title': f'Share {document.title}'
    }
    return render(request, 'documents/document_share.html', context)

@login_required
def document_upload(request):
    """Upload tài liệu mới"""
    from .models import Document, DocumentCategory, DocumentTag, DocumentFileVersion
    from .forms import DocumentForm
    
    # Cho phép tất cả nhân viên upload tài liệu
    # Không cần kiểm tra role nữa - chỉ cần đăng nhập
    
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            document = form.save(commit=False)
            document.created_by = request.user
            
            # Đặt trạng thái mặc định là published theo logic mới
            document.status = 'published'
            
            document.save()
            form.save_m2m()  # Save tags
            
            # Tạo DocumentFileVersion cho file đầu tiên
            if document.file:
                try:
                    file_version = DocumentFileVersion.objects.create(
                        document=document,
                        file=document.file,
                        file_name=document.file.name.split('/')[-1],
                        file_size=document.file.size,
                        file_type=document.file.name.split('.')[-1].lower(),
                        uploaded_by=request.user,
                        is_current=True,
                        version_number=1,
                        change_note="Upload file đầu tiên"
                    )
                except Exception as e:
                    print(f"Lỗi tạo DocumentFileVersion: {e}")
            
            messages.success(request, f'Tài liệu "{document.title}" đã được upload thành công!')
            return redirect('document_detail', slug=document.slug)
        else:
            messages.error(request, 'Có lỗi xảy ra. Vui lòng kiểm tra lại thông tin.')
    else:
        form = DocumentForm()
    
    # Get categories and tags for context
    categories = DocumentCategory.objects.filter(is_active=True).order_by('order', 'name')
    tags = DocumentTag.objects.all().order_by('name')
    
    # Kiểm tra xem có danh mục nào không
    has_categories = categories.exists()
    
    context = {
        'form': form,
        'categories': categories,
        'tags': tags,
        'title': 'Upload tài liệu mới',
        'has_categories': has_categories
    }
    return render(request, 'documents/document_upload.html', context)

@login_required
def document_versions(request, document_id):
    parent_doc = Document.objects.get(id=document_id)
    versions = parent_doc.get_all_versions()
    
    context = {
        'parent_doc': parent_doc,
        'versions': versions,
    }
    return render(request, 'documents/document_versions.html', context)

@login_required
@require_http_methods(["POST"])
def restore_document_version(request, document_id):
    try:
        version_to_restore = Document.objects.get(id=document_id)
        parent_doc = version_to_restore.parent_document
        
        # Create new version with the restored file
        new_doc = Document(
            title=parent_doc.title,
            file=version_to_restore.file,
            description=version_to_restore.description,
            category=parent_doc.category,
            created_by=request.user,
            parent_document=parent_doc
        )
        new_doc.save()
        new_doc.tags.set(parent_doc.tags.all())
        
        return JsonResponse({
            'success': True,
            'message': f'Version restored successfully! New version: {new_doc.version}'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })

@login_required
@require_http_methods(["DELETE"])
def delete_document(request, document_id):
    try:
        document = Document.objects.get(id=document_id)
        parent_doc = document.parent_document
        
        # Delete all versions of this document
        Document.objects.filter(parent_document=parent_doc).delete()
        
        return JsonResponse({
            'success': True,
            'message': 'Document and all versions deleted successfully!'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })

def get_client_ip(request):
    """Lấy IP của client"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

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
    """Manage document categories"""
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'add':
            # Xử lý thêm danh mục mới
            name = request.POST.get('name')
            description = request.POST.get('description', '')
            icon = request.POST.get('icon', 'fas fa-folder')
            
            if name:
                try:
                    # Tạo slug từ tên danh mục
                    slug = slugify(name)
                    
                    # Kiểm tra slug đã tồn tại chưa
                    counter = 1
                    original_slug = slug
                    while DocumentCategory.objects.filter(slug=slug).exists():
                        slug = f"{original_slug}-{counter}"
                        counter += 1
                    
                    # Tạo danh mục mới
                    category = DocumentCategory.objects.create(
                        name=name,
                        slug=slug,
                        description=description,
                        icon=icon
                    )
                    messages.success(request, f'Đã thêm danh mục "{name}" thành công!')
                except Exception as e:
                    messages.error(request, f'Lỗi khi thêm danh mục: {str(e)}')
        
        elif action == 'edit':
            # Xử lý sửa danh mục
            category_id = request.POST.get('category_id')
            name = request.POST.get('name')
            description = request.POST.get('description', '')
            icon = request.POST.get('icon', 'fas fa-folder')
            
            if category_id and name:
                try:
                    category = DocumentCategory.objects.get(id=category_id)
                    old_name = category.name
                    
                    # Cập nhật thông tin
                    category.name = name
                    category.description = description
                    category.icon = icon
                    
                    # Tạo slug mới nếu tên thay đổi
                    if old_name != name:
                        slug = slugify(name)
                        counter = 1
                        original_slug = slug
                        while DocumentCategory.objects.filter(slug=slug).exclude(id=category_id).exists():
                            slug = f"{original_slug}-{counter}"
                            counter += 1
                        category.slug = slug
                    
                    category.save()
                    messages.success(request, f'Đã cập nhật danh mục "{name}" thành công!')
                except DocumentCategory.DoesNotExist:
                    messages.error(request, 'Không tìm thấy danh mục!')
                except Exception as e:
                    messages.error(request, f'Lỗi khi cập nhật danh mục: {str(e)}')
        
        elif action == 'delete':
            # Xử lý xóa danh mục
            category_id = request.POST.get('category_id')
            
            if category_id:
                try:
                    category = DocumentCategory.objects.get(id=category_id)
                    category_name = category.name
                    
                    # Kiểm tra xem danh mục có tài liệu không
                    doc_count = category.document_set.count()
                    if doc_count > 0:
                        messages.error(request, f'Không thể xóa danh mục "{category_name}" vì còn {doc_count} tài liệu!')
                    else:
                        category.delete()
                        messages.success(request, f'Đã xóa danh mục "{category_name}" thành công!')
                except DocumentCategory.DoesNotExist:
                    messages.error(request, 'Không tìm thấy danh mục!')
                except Exception as e:
                    messages.error(request, f'Lỗi khi xóa danh mục: {str(e)}')
        
        return redirect('manage_categories')
    
    # GET request - hiển thị danh sách
    categories = DocumentCategory.objects.all()
    
    # Get document count for each category
    for category in categories:
        try:
            doc_count = category.document_set.count()
        except:
            doc_count = 0
        category.doc_count = doc_count
    
    context = {
        'categories': categories,
        'title': 'Quản lý danh mục'
    }
    return render(request, 'management/manage_categories.html', context)

@login_required
def manage_tags(request):
    """Manage document tags"""
    tags = DocumentTag.objects.all()
    
    # Get document count for each tag
    for tag in tags:
        try:
            doc_count = tag.document_set.count()
        except:
            doc_count = 0
        tag.doc_count = doc_count
    
    context = {
        'tags': tags,
        'title': 'Quản lý tags'
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
@login_required
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
    """API lấy dữ liệu chấm công của user - hỗ trợ nhiều ca trong 1 ngày với dữ liệu riêng biệt"""
    try:
        from .models import Attendance
        from datetime import datetime
        
        # Lấy tháng và năm từ request parameters
        month = request.GET.get('month')
        year = request.GET.get('year')
        
        # Lấy dữ liệu chấm công của user hiện tại
        attendances = Attendance.objects.filter(employee=request.user)
        
        # Lọc theo tháng/năm nếu có
        if month and year:
            try:
                month = int(month)
                year = int(year)
                attendances = attendances.filter(
                    date__year=year,
                    date__month=month
                )
                print(f"DEBUG get_attendance_data: Filtering by month={month}, year={year}")
            except ValueError:
                print(f"DEBUG get_attendance_data: Invalid month/year parameters: month={month}, year={year}")
        
        attendances = attendances.order_by('-date')
        
        # Nhóm theo ngày để xử lý nhiều ca
        attendance_by_date = {}
        
        for attendance in attendances:
            date_str = attendance.date.strftime('%Y-%m-%d')
            
            if date_str not in attendance_by_date:
                attendance_by_date[date_str] = {
                    'id': attendance.id,
                    'date': date_str,
                    'dayShift': False,
                    'nightShift': False,
                    'dayOvertimeEnd': '',
                    'nightOvertimeEnd': '',
                    'overtimeHours': '0',
                    'hotelExpense': 0,
                    'shoppingExpense': 0,
                    'phoneExpense': 0,
                    'otherExpense': 0,
                    'otherExpenseDesc': '',
                    'dayPautMeters': 0,
                    'dayTofdMeters': 0,
                    'nightPautMeters': 0,
                    'nightTofdMeters': 0,
                    'isAutoGenerated': getattr(attendance, 'is_auto_generated', False),
                    'canBeEdited': getattr(attendance, 'can_be_edited', True),
                    'timestamp': attendance.created_at.isoformat(),
                    'leaveRequestId': getattr(attendance, 'leave_request', None)
                }
            
            # Cập nhật thông tin tổng hợp
            if attendance.day_shift:
                attendance_by_date[date_str]['dayShift'] = True
                attendance_by_date[date_str]['dayWorkType'] = attendance.work_type
                attendance_by_date[date_str]['dayConstructionName'] = attendance.construction_name or ''
                attendance_by_date[date_str]['dayNdtMethod'] = attendance.ndt_method or ''
                attendance_by_date[date_str]['dayPautMeters'] = float(attendance.paut_meters or 0)
                attendance_by_date[date_str]['dayTofdMeters'] = float(attendance.tofd_meters or 0)
                attendance_by_date[date_str]['dayOvertimeEnd'] = attendance.day_overtime_end.strftime('%H:%M') if attendance.day_overtime_end else ''
                attendance_by_date[date_str]['dayWorkNote'] = attendance.work_note or ''
            
            if attendance.night_shift:
                attendance_by_date[date_str]['nightShift'] = True
                attendance_by_date[date_str]['nightWorkType'] = attendance.work_type
                attendance_by_date[date_str]['nightConstructionName'] = attendance.construction_name or ''
                attendance_by_date[date_str]['nightNdtMethod'] = attendance.ndt_method or ''
                attendance_by_date[date_str]['nightPautMeters'] = float(attendance.paut_meters or 0)
                attendance_by_date[date_str]['nightTofdMeters'] = float(attendance.tofd_meters or 0)
                attendance_by_date[date_str]['nightOvertimeEnd'] = attendance.night_overtime_end.strftime('%H:%M') if attendance.night_overtime_end else ''
                attendance_by_date[date_str]['nightWorkNote'] = attendance.work_note or ''
            
            # Chi phí chỉ được lưu một lần cho mỗi ngày (không cộng dồn)
            # Lấy từ ca đầu tiên hoặc ghi đè nếu có giá trị mới
            if not attendance_by_date[date_str].get('hotelExpense') or float(attendance.hotel_expense or 0) > 0:
                attendance_by_date[date_str]['hotelExpense'] = float(attendance.hotel_expense or 0)
            if not attendance_by_date[date_str].get('shoppingExpense') or float(attendance.shopping_expense or 0) > 0:
                attendance_by_date[date_str]['shoppingExpense'] = float(attendance.shopping_expense or 0)
            if not attendance_by_date[date_str].get('phoneExpense') or float(attendance.phone_expense or 0) > 0:
                attendance_by_date[date_str]['phoneExpense'] = float(attendance.phone_expense or 0)
            if not attendance_by_date[date_str].get('otherExpense') or float(attendance.other_expense or 0) > 0:
                attendance_by_date[date_str]['otherExpense'] = float(attendance.other_expense or 0)
            
            # Ghi chú: lấy từ ca đầu tiên hoặc gộp từ nhiều ca
            if not attendance_by_date[date_str].get('workNote'):
                attendance_by_date[date_str]['workNote'] = attendance.work_note or ''
            elif attendance.work_note and attendance.work_note not in attendance_by_date[date_str].get('workNote', ''):
                attendance_by_date[date_str]['workNote'] += f" | {attendance.work_note}"
        
        # Chuyển đổi thành list
        data = list(attendance_by_date.values())
        print(f"DEBUG get_attendance_data: Total records found: {len(attendances)}")
        print(f"DEBUG get_attendance_data: Records after grouping: {len(data)}")
        print(f"DEBUG get_attendance_data returning data: {data}")
        
        return JsonResponse({
            'success': True,
            'data': data
        })
        
    except Exception as e:
        import traceback
        print(f"Error in get_attendance_data: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
        return JsonResponse({
            'success': False,
            'message': f'Lỗi: {str(e)}'
        }, status=400)

def _parse_time(time_str):
    """Parse thời gian từ string sang time object"""
    if not time_str:
        return None
    try:
        return datetime.strptime(time_str, '%H:%M').time()
    except ValueError:
        return None

def _parse_expense(expense):
    """Parse chi phí từ boolean hoặc số sang số tiền"""
    if isinstance(expense, bool):
        return 200000 if expense else 0
    return float(expense) if expense else 0

def _parse_meters(meters):
    """Parse số mét vượt từ string hoặc số sang float"""
    if not meters or meters == '':
        return 0.0
    try:
        return float(meters)
    except (ValueError, TypeError):
        return 0.0

def _calculate_overtime_hours(overtime_end, shift='day', both_shifts=False):
    """Tính số giờ tăng ca theo quy tắc:
    - Nếu làm cả 2 ca (both_shifts=True): OT = 0
    - Ca ngày: OT tính từ 17:00 tới thời điểm kết thúc nếu muộn hơn 17:00
    - Ca đêm: OT tính sau 04:00 (thời điểm kết thúc > 04:00)
    """
    if both_shifts:
        return 0.0
    if not overtime_end:
        return 0.0
    try:
        end_time = datetime.strptime(overtime_end, '%H:%M').time()
        if shift == 'day':
            base_time = datetime.strptime('17:00', '%H:%M').time()
            if end_time <= base_time:
                return 0.0
            diff_minutes = ((end_time.hour - base_time.hour) * 60) + (end_time.minute - base_time.minute)
            return round(diff_minutes / 60.0, 2)
        else:
            base_time = datetime.strptime('04:00', '%H:%M').time()
            if end_time <= base_time:
                return 0.0
            diff_minutes = ((end_time.hour - base_time.hour) * 60) + (end_time.minute - base_time.minute)
            return round(diff_minutes / 60.0, 2)
    except ValueError:
        return 0.0

@csrf_exempt
@require_POST
@login_required
def save_attendance_data(request):
    """API lưu dữ liệu chấm công - hỗ trợ nhiều ca trong 1 ngày với dữ liệu riêng biệt"""
    try:
        from .models import Attendance
        from datetime import datetime
        
        data = json.loads(request.body)
        print(f"DEBUG save_attendance_data received data: {data}")
        date = data.get('date')
        day_shift = data.get('dayShift', False)
        night_shift = data.get('nightShift', False)
        
        # Kiểm tra dữ liệu bắt buộc
        if not date:
            return JsonResponse({
                'success': False,
                'message': 'Thiếu thông tin ngày chấm công'
            }, status=400)
        
        # Kiểm tra có chọn ca nào không
        if not day_shift and not night_shift:
            return JsonResponse({
                'success': False,
                'message': 'Vui lòng chọn ít nhất 1 ca làm việc'
            }, status=400)
        
        # Chuyển đổi ngày
        try:
            attendance_date = datetime.strptime(date, '%Y-%m-%d').date()
        except ValueError:
            return JsonResponse({
                'success': False,
                'message': 'Định dạng ngày không hợp lệ'
            }, status=400)
        
        # Xóa các bản ghi cũ của ngày này (nếu có)
        Attendance.objects.filter(
            employee=request.user,
            date=attendance_date
        ).delete()
        
        # Tạo record cho ca ngày nếu được chọn
        if day_shift:
            day_work_type = data.get('dayWorkType', '')
            if not day_work_type:
                return JsonResponse({
                    'success': False,
                    'message': 'Vui lòng chọn loại công việc cho ca ngày'
                }, status=400)
            
            day_record = Attendance.objects.create(
                employee=request.user,
                date=attendance_date,
                work_type=day_work_type,
                construction_name=data.get('dayConstructionName', '') or '',
                ndt_method=data.get('dayNdtMethod', '') or '',
                paut_meters=_parse_meters(data.get('dayPautMeters', 0)),
                tofd_meters=_parse_meters(data.get('dayTofdMeters', 0)),
                day_shift=True,
                night_shift=False,
                day_overtime_end=_parse_time(data.get('dayOvertimeEnd', '')),
                night_overtime_end=None,
                overtime_hours=_calculate_overtime_hours(data.get('dayOvertimeEnd', ''), shift='day', both_shifts=day_shift and night_shift),
                hotel_expense=_parse_expense(data.get('hotelExpense', 0)),
                shopping_expense=_parse_expense(data.get('shoppingExpense', 0)),
                phone_expense=_parse_expense(data.get('phoneExpense', 0)),
                other_expense=_parse_expense(data.get('otherExpense', 0)),
                other_expense_desc=data.get('otherExpenseDesc', '') or '',
                work_note=data.get('dayWorkNote', '') or '',
                created_by=request.user,
                updated_by=request.user
            )
        
        # Tạo record cho ca đêm nếu được chọn
        if night_shift:
            night_work_type = data.get('nightWorkType', '')
            if not night_work_type:
                return JsonResponse({
                    'success': False,
                    'message': 'Vui lòng chọn loại công việc cho ca đêm'
                }, status=400)
            
            night_record = Attendance.objects.create(
                employee=request.user,
                date=attendance_date,
                work_type=night_work_type,
                construction_name=data.get('nightConstructionName', '') or '',
                ndt_method=data.get('nightNdtMethod', '') or '',
                paut_meters=_parse_meters(data.get('nightPautMeters', 0)),
                tofd_meters=_parse_meters(data.get('nightTofdMeters', 0)),
                day_shift=False,
                night_shift=True,
                day_overtime_end=None,
                night_overtime_end=_parse_time(data.get('nightOvertimeEnd', '')),
                overtime_hours=_calculate_overtime_hours(data.get('nightOvertimeEnd', ''), shift='night', both_shifts=day_shift and night_shift),
                hotel_expense=_parse_expense(data.get('hotelExpense', 0)),
                shopping_expense=_parse_expense(data.get('shoppingExpense', 0)),
                phone_expense=_parse_expense(data.get('phoneExpense', 0)),
                other_expense=_parse_expense(data.get('otherExpense', 0)),
                other_expense_desc=data.get('otherExpenseDesc', '') or '',
                work_note=data.get('nightWorkNote', '') or '',
                created_by=request.user,
                updated_by=request.user
            )
        
        # Đếm số record đã tạo
        total_records = (1 if day_shift else 0) + (1 if night_shift else 0)
        
        return JsonResponse({
            'success': True,
            'message': f'Lưu chấm công thành công cho {total_records} ca',
            'total_shifts': total_records
        })
        
    except Exception as e:
        import traceback
        print(f"Error in save_attendance_data: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
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

@login_required
def export_attendance_data(request):
    """API xuất dữ liệu chấm công theo format chuẩn cho app - hỗ trợ nhiều ca trong 1 ngày"""
    profile = getattr(request.user, 'user_profile', None)
    
    # Kiểm tra quyền truy cập
    if not profile or profile.role not in ['admin', 'manager']:
        return JsonResponse({'error': 'Không có quyền truy cập'}, status=403)
    
    try:
        # Lấy tháng/năm từ request
        month = int(request.GET.get('month', timezone.now().month))
        year = int(request.GET.get('year', timezone.now().year))
    
        # Lấy tất cả nhân viên có MSNV
        staff_profiles = UserProfile.objects.filter(
            msnv__isnull=False
        ).exclude(msnv='').select_related('user')
        
        # Format mới: mỗi ca = 1 record riêng biệt
        attendance_data = []
        
        for profile in staff_profiles:
            msnv = profile.msnv
            name = profile.user.get_full_name() or profile.user.username
            
            # Lấy dữ liệu chấm công của nhân viên trong tháng
            attendances = Attendance.objects.filter(
                employee=profile.user,
                date__year=year,
                date__month=month
            ).order_by('date')
            
            # Tạo dữ liệu cho từng ca (mỗi ca = 1 record)
            for attendance in attendances:
                # Xác định ca làm việc
                if attendance.day_shift and attendance.night_shift:
                    # Cả 2 ca - tạo 2 record riêng biệt
                    # Record ca ngày
                    day_row = [
                        msnv,  # MSNV
                        name,  # Tên nhân viên
                        attendance.date.strftime('%d/%m/%Y'),  # Ngày
                        attendance.work_type,  # Loại công việc
                        attendance.construction_name or '',  # Địa điểm
                        attendance.ndt_method or '',  # Phương pháp NDT
                        '1',  # Ca ngày
                        '0',  # Ca đêm
                        attendance.day_overtime_end.strftime('%H:%M') if attendance.day_overtime_end else '',  # Giờ kết thúc OT ca ngày
                        '',  # Giờ kết thúc OT ca đêm
                        float(attendance.overtime_hours or 0),  # Số giờ OT
                        float(attendance.hotel_expense or 0),  # Chi phí khách sạn
                        float(attendance.shopping_expense or 0),  # Chi phí mua sắm
                        float(attendance.phone_expense or 0),  # Chi phí điện thoại
                        float(attendance.other_expense or 0),  # Chi phí khác
                        float((attendance.hotel_expense or 0) + (attendance.shopping_expense or 0) + (attendance.phone_expense or 0) + (attendance.other_expense or 0)),  # Tổng số tiền chi phí
                        attendance.other_expense_desc or '',  # Mô tả chi phí khác
                        f"Ca ngày: {attendance.work_note or ''}"  # Ghi chú
                    ]
                    attendance_data.append(day_row)
                    
                    # Record ca đêm
                    night_row = [
                        msnv,  # MSNV
                        name,  # Tên nhân viên
                        attendance.date.strftime('%d/%m/%Y'),  # Ngày
                        attendance.work_type,  # Loại công việc
                        attendance.construction_name or '',  # Địa điểm
                        attendance.ndt_method or '',  # Phương pháp NDT
                        '0',  # Ca ngày
                        '1',  # Ca đêm
                        '',  # Giờ kết thúc OT ca ngày
                        attendance.night_overtime_end.strftime('%H:%M') if attendance.night_overtime_end else '',  # Giờ kết thúc OT ca đêm
                        float(attendance.overtime_hours or 0),  # Số giờ OT
                        float(attendance.hotel_expense or 0),  # Chi phí khách sạn
                        float(attendance.shopping_expense or 0),  # Chi phí mua sắm
                        float(attendance.phone_expense or 0),  # Chi phí điện thoại
                        float(attendance.other_expense or 0),  # Chi phí khác
                        float((attendance.hotel_expense or 0) + (attendance.shopping_expense or 0) + (attendance.phone_expense or 0) + (attendance.other_expense or 0)),  # Tổng số tiền chi phí
                        attendance.other_expense_desc or '',  # Mô tả chi phí khác
                        f"Ca đêm: {attendance.work_note or ''}"  # Ghi chú
                    ]
                    attendance_data.append(night_row)
                    
                elif attendance.day_shift:
                    # Chỉ ca ngày
                    day_row = [
                        msnv,  # MSNV
                        name,  # Tên nhân viên
                        attendance.date.strftime('%d/%m/%Y'),  # Ngày
                        attendance.work_type,  # Loại công việc
                        attendance.construction_name or '',  # Địa điểm
                        attendance.ndt_method or '',  # Phương pháp NDT
                        '1',  # Ca ngày
                        '0',  # Ca đêm
                        attendance.day_overtime_end.strftime('%H:%M') if attendance.day_overtime_end else '',  # Giờ kết thúc OT ca ngày
                        '',  # Giờ kết thúc OT ca đêm
                        float(attendance.overtime_hours or 0),  # Số giờ OT
                        float(attendance.hotel_expense or 0),  # Chi phí khách sạn
                        float(attendance.shopping_expense or 0),  # Chi phí mua sắm
                        float(attendance.phone_expense or 0),  # Chi phí điện thoại
                        float(attendance.other_expense or 0),  # Chi phí khác
                        float((attendance.hotel_expense or 0) + (attendance.shopping_expense or 0) + (attendance.phone_expense or 0) + (attendance.other_expense or 0)),  # Tổng số tiền chi phí
                        attendance.other_expense_desc or '',  # Mô tả chi phí khác
                        attendance.work_note or ''  # Ghi chú
                    ]
                    attendance_data.append(day_row)
                    
                elif attendance.night_shift:
                    # Chỉ ca đêm
                    night_row = [
                        msnv,  # MSNV
                        name,  # Tên nhân viên
                        attendance.date.strftime('%d/%m/%Y'),  # Ngày
                        attendance.work_type,  # Loại công việc
                        attendance.construction_name or '',  # Địa điểm
                        attendance.ndt_method or '',  # Phương pháp NDT
                        '0',  # Ca ngày
                        '1',  # Ca đêm
                        '',  # Giờ kết thúc OT ca ngày
                        attendance.night_overtime_end.strftime('%H:%M') if attendance.night_overtime_end else '',  # Giờ kết thúc OT ca đêm
                        float(attendance.overtime_hours or 0),  # Số giờ OT
                        float(attendance.hotel_expense or 0),  # Chi phí khách sạn
                        float(attendance.shopping_expense or 0),  # Chi phí mua sắm
                        float(attendance.phone_expense or 0),  # Chi phí điện thoại
                        float(attendance.other_expense or 0),  # Chi phí khác
                        float((attendance.hotel_expense or 0) + (attendance.shopping_expense or 0) + (attendance.phone_expense or 0) + (attendance.other_expense or 0)),  # Tổng số tiền chi phí
                        attendance.other_expense_desc or '',  # Mô tả chi phí khác
                        attendance.work_note or ''  # Ghi chú
                    ]
                    attendance_data.append(night_row)
        
        # Format đơn giản giống với file nhanvien.json
        export_data = {
            'timestamp': timezone.now().isoformat(),
            'period': f'{month:02d}/{year}',
            'total_records': len(attendance_data),
            'data': attendance_data
        }
        
        return JsonResponse(export_data, safe=False)
        
    except Exception as e:
        return JsonResponse({'error': f'Lỗi xuất dữ liệu chấm công: {str(e)}'}, status=500)

@require_http_methods(["GET"])
@login_required
def export_attendance_json(request):
    """API xuất dữ liệu chấm công theo format JSON chuẩn cho app - chỉ lấy những nhân viên có dữ liệu trong tháng"""
    profile = getattr(request.user, 'user_profile', None)
    
    # Cho phép admin/manager/company
    if not profile or profile.role not in ['admin', 'manager', 'company']:
        return JsonResponse({'error': 'Không có quyền truy cập'}, status=403)
    
    try:
        # Lấy tháng/năm từ request
        month = int(request.GET.get('month', timezone.now().month))
        year = int(request.GET.get('year', timezone.now().year))
        
        # Lấy tất cả bản ghi chấm công trong tháng
        month_attendances = Attendance.objects.filter(
            date__year=year,
            date__month=month
        ).select_related('employee', 'employee__user_profile').order_by('date')
        
        # Gom theo nhân viên có dữ liệu
        employees_data = {}
        
        for attendance in month_attendances:
            user = attendance.employee
            user_profile = getattr(user, 'user_profile', None)
            msnv = getattr(user_profile, 'msnv', '') or (user.username or str(user.id))
            name = user.get_full_name() or user.username
            
            if msnv not in employees_data:
                employees_data[msnv] = {
                    'info': {
                        'name': name,
                        'msnv': msnv,
                        'email': user.email or '',
                        'position': getattr(user_profile, 'position', ''),
                        'department': getattr(user_profile, 'department', ''),
                        'phone': getattr(user_profile, 'phone', '')
                    },
                    'attendance': {
                        'days': {},
                        'summary': {
                            'total_work_days': 0,
                            'total_office_days': 0,
                            'total_training_days': 0,
                            'total_leave_days': 0,
                            'total_absent_days': 0,
                            'total_overtime_hours': 0,
                            'total_hotel': 0,
                            'total_shopping': 0,
                            'total_phone': 0,
                            'total_other': 0,
                            'total_paut_meters': 0,
                            'total_tofd_meters': 0,
                            'construction_projects': [],
                            'ndt_methods_used': []
                        }
                    }
                }
            
            employee_data = employees_data[msnv]
            days = employee_data['attendance']['days']
            date_str = attendance.date.strftime('%Y-%m-%d')
            
            if date_str not in days:
                both_shifts = bool(attendance.day_shift and attendance.night_shift)
                end_str = (
                    attendance.day_overtime_end.strftime('%H:%M') if (attendance.day_shift and attendance.day_overtime_end) else
                    (attendance.night_overtime_end.strftime('%H:%M') if attendance.night_overtime_end else '')
                )
                overtime_val = 0.0 if both_shifts else _calculate_overtime_hours(
                    end_str,
                    shift=('day' if attendance.day_shift else 'night'),
                    both_shifts=both_shifts
                )
                days[date_str] = {
                    'type': attendance.work_type,
                    'location': attendance.construction_name or '',
                    'method': attendance.ndt_method or '',
                    'paut_meters': float(attendance.paut_meters or 0),
                    'tofd_meters': float(attendance.tofd_meters or 0),
                    'day_shift': attendance.day_shift,
                    'night_shift': attendance.night_shift,
                    'overtime': float(overtime_val),
                    'hotel_expense': float(attendance.hotel_expense or 0),
                    'shopping_expense': float(attendance.shopping_expense or 0),
                    'phone_expense': float(attendance.phone_expense or 0),
                    'other_expense': float(attendance.other_expense or 0),
                    'other_expense_desc': attendance.other_expense_desc or '',
                    'note': attendance.work_note or '',
                    'created_at': attendance.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                    'updated_at': attendance.updated_at.strftime('%Y-%m-%d %H:%M:%S')
                }
            else:
                existing = days[date_str]
                existing['day_shift'] = existing['day_shift'] or attendance.day_shift
                existing['night_shift'] = existing['night_shift'] or attendance.night_shift
                both_shifts = bool(existing['day_shift'] and existing['night_shift'])
                end_str = (
                    attendance.day_overtime_end.strftime('%H:%M') if (attendance.day_shift and attendance.day_overtime_end) else
                    (attendance.night_overtime_end.strftime('%H:%M') if attendance.night_overtime_end else '')
                )
                ot_add = _calculate_overtime_hours(
                    end_str,
                    shift=('day' if attendance.day_shift else 'night'),
                    both_shifts=both_shifts
                )
                if both_shifts:
                    existing['overtime'] = 0.0
                else:
                    existing['overtime'] = float((existing.get('overtime', 0) or 0)) + ot_add
                existing['paut_meters'] += float(attendance.paut_meters or 0)
                existing['tofd_meters'] += float(attendance.tofd_meters or 0)
                if attendance.work_note and attendance.work_note not in existing['note']:
                    existing['note'] += f" | {attendance.work_note}"
        
        # Tính summary cho từng nhân viên
        for msnv, employee_data in employees_data.items():
            summary = employee_data['attendance']['summary']
            for day_data in employee_data['attendance']['days'].values():
                if day_data['type'] == 'W':
                    summary['total_work_days'] += 1
                elif day_data['type'] == 'O':
                    summary['total_office_days'] += 1
                elif day_data['type'] == 'T':
                    summary['total_training_days'] += 1
                elif day_data['type'] == 'P':
                    summary['total_leave_days'] += 1
                elif day_data['type'] == 'N':
                    summary['total_absent_days'] += 1
                
                summary['total_overtime_hours'] += day_data.get('overtime', 0)
                summary['total_hotel'] += day_data['hotel_expense']
                summary['total_shopping'] += day_data['shopping_expense']
                summary['total_phone'] += day_data['phone_expense']
                summary['total_other'] += day_data['other_expense']
                summary['total_paut_meters'] += day_data['paut_meters']
                summary['total_tofd_meters'] += day_data['tofd_meters']
                
                if day_data['location'] and day_data['location'] not in summary['construction_projects']:
                    summary['construction_projects'].append(day_data['location'])
                if day_data['method'] and day_data['method'] not in summary['ndt_methods_used']:
                    summary['ndt_methods_used'].append(day_data['method'])
        
        export_data = {
            'export_info': {
                'company': 'Hitech NDT',
                'period': f'{month:02d}/{year}',
                'export_date': timezone.now().strftime('%Y-%m-%d %H:%M:%S'),
                'version': '1.0',
                'total_employees': len(employees_data)
            },
            'employees': employees_data
        }
        
        return JsonResponse(export_data, safe=False)
    
    except Exception as e:
        return JsonResponse({'error': f'Lỗi xuất dữ liệu chấm công JSON: {str(e)}'}, status=500)

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

@csrf_exempt
@require_http_methods(["PUT"])
@login_required
def update_attendance_data(request, date):
    """API cập nhật dữ liệu chấm công"""
    try:
        from .models import Attendance
        from datetime import datetime
        
        data = json.loads(request.body)
        print(f"DEBUG update_attendance_data received data: {data}")
        day_shift = data.get('dayShift', False)
        night_shift = data.get('nightShift', False)
        
        # Kiểm tra có chọn ca nào không
        if not day_shift and not night_shift:
            return JsonResponse({
                'success': False,
                'message': 'Vui lòng chọn ít nhất 1 ca làm việc'
            }, status=400)
        
        # Chuyển đổi ngày
        try:
            attendance_date = datetime.strptime(date, '%Y-%m-%d').date()
        except ValueError:
            return JsonResponse({
                'success': False,
                'message': 'Định dạng ngày không hợp lệ'
            }, status=400)
        
        # Xóa các bản ghi cũ của ngày này
        Attendance.objects.filter(
            employee=request.user,
            date=attendance_date
        ).delete()
        
        # Tạo record cho ca ngày nếu được chọn
        if day_shift:
            day_work_type = data.get('dayWorkType', '')
            if not day_work_type:
                return JsonResponse({
                    'success': False,
                    'message': 'Vui lòng chọn loại công việc cho ca ngày'
                }, status=400)
            
            day_record = Attendance.objects.create(
                employee=request.user,
                date=attendance_date,
                work_type=day_work_type,
                construction_name=data.get('dayConstructionName', '') or '',
                ndt_method=data.get('dayNdtMethod', '') or '',
                paut_meters=_parse_meters(data.get('dayPautMeters', 0)),
                tofd_meters=_parse_meters(data.get('dayTofdMeters', 0)),
                day_shift=True,
                night_shift=False,
                day_overtime_end=_parse_time(data.get('dayOvertimeEnd', '')),
                night_overtime_end=None,
                overtime_hours=_calculate_overtime_hours(data.get('dayOvertimeEnd', '')),
                hotel_expense=_parse_expense(data.get('hotelExpense', 0)),
                shopping_expense=_parse_expense(data.get('shoppingExpense', 0)),
                phone_expense=_parse_expense(data.get('phoneExpense', 0)),
                other_expense=_parse_expense(data.get('otherExpense', 0)),
                other_expense_desc=data.get('otherExpenseDesc', '') or '',
                work_note=data.get('dayWorkNote', '') or '',
                created_by=request.user,
                updated_by=request.user
            )
        
        # Tạo record cho ca đêm nếu được chọn
        if night_shift:
            night_work_type = data.get('nightWorkType', '')
            if not night_work_type:
                return JsonResponse({
                    'success': False,
                    'message': 'Vui lòng chọn loại công việc cho ca đêm'
                }, status=400)
            
            night_record = Attendance.objects.create(
                employee=request.user,
                date=attendance_date,
                work_type=night_work_type,
                construction_name=data.get('nightConstructionName', '') or '',
                ndt_method=data.get('nightNdtMethod', '') or '',
                paut_meters=_parse_meters(data.get('nightPautMeters', 0)),
                tofd_meters=_parse_meters(data.get('nightTofdMeters', 0)),
                day_shift=False,
                night_shift=True,
                day_overtime_end=None,
                night_overtime_end=_parse_time(data.get('nightOvertimeEnd', '')),
                overtime_hours=_calculate_overtime_hours(data.get('nightOvertimeEnd', ''), shift='night', both_shifts=day_shift and night_shift),
                hotel_expense=_parse_expense(data.get('hotelExpense', 0)),
                shopping_expense=_parse_expense(data.get('shoppingExpense', 0)),
                phone_expense=_parse_expense(data.get('phoneExpense', 0)),
                other_expense=_parse_expense(data.get('otherExpense', 0)),
                other_expense_desc=data.get('otherExpenseDesc', '') or '',
                work_note=data.get('nightWorkNote', '') or '',
                created_by=request.user,
                updated_by=request.user
            )
        
        # Đếm số record đã tạo
        total_records = (1 if day_shift else 0) + (1 if night_shift else 0)
        
        return JsonResponse({
            'success': True,
            'message': f'Cập nhật chấm công thành công cho {total_records} ca',
            'total_shifts': total_records
        })
        
    except Exception as e:
        import traceback
        print(f"Error in update_attendance_data: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
        return JsonResponse({
            'success': False,
            'message': f'Lỗi: {str(e)}'
        }, status=400)

@csrf_exempt
@require_http_methods(["DELETE"])
@login_required
def delete_attendance_data(request, date):
    """API xóa dữ liệu chấm công"""
    try:
        from .models import Attendance
        from datetime import datetime
        
        # Chuyển đổi ngày
        try:
            attendance_date = datetime.strptime(date, '%Y-%m-%d').date()
        except ValueError:
            return JsonResponse({
                'success': False,
                'message': 'Định dạng ngày không hợp lệ'
            }, status=400)
        
        # Xóa tất cả bản ghi chấm công của ngày này
        deleted_count = Attendance.objects.filter(
            employee=request.user,
            date=attendance_date
        ).delete()[0]
        
        if deleted_count == 0:
            return JsonResponse({
                'success': False,
                'message': 'Không tìm thấy dữ liệu chấm công để xóa'
            }, status=404)
        
        return JsonResponse({
            'success': True,
            'message': f'Đã xóa {deleted_count} bản ghi chấm công thành công'
        })
        
    except Exception as e:
        import traceback
        print(f"Error in delete_attendance_data: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
        return JsonResponse({
            'success': False,
            'message': f'Lỗi: {str(e)}'
        }, status=400)

@login_required
def documents_view(request):
    """Legacy view for backward compatibility"""
    return documents_management(request)

@login_required
def document_update(request, document_id):
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            # Get the parent document
            parent_doc = Document.objects.get(id=document_id)
            
            # Create new version
            new_doc = form.save(commit=False)
            new_doc.created_by = request.user
            new_doc.parent_document = parent_doc
            new_doc.version = None  # Will be auto-calculated
            new_doc.title = parent_doc.title
            new_doc.category = parent_doc.category
            new_doc.tags.set(parent_doc.tags.all())
            new_doc.access_level = getattr(parent_doc, 'access_level', 'public')
            new_doc.allowed_roles = getattr(parent_doc, 'allowed_roles', 'all')
            new_doc.status = getattr(parent_doc, 'status', 'published')
            new_doc.slug = ''  # để model tự tạo slug mới
            new_doc.save()
            messages.success(request, f'Document updated successfully! New version: {new_doc.version}')
            return redirect('documents')
    else:
        form = DocumentForm()
    
    parent_doc = Document.objects.get(id=document_id)
    context = {
        'form': form,
        'parent_doc': parent_doc,
    }
    return render(request, 'documents/document_update.html', context)

@login_required
def document_versions(request, document_id):
    parent_doc = Document.objects.get(id=document_id)
    versions = parent_doc.get_all_versions()
    
    context = {
        'parent_doc': parent_doc,
        'versions': versions,
    }
    return render(request, 'documents/document_versions.html', context)


@login_required
@require_http_methods(["DELETE"])
def delete_document(request, document_id):
    try:
        document = Document.objects.get(id=document_id)
        parent_doc = document.parent_document
        
        # Delete all versions of this document
        Document.objects.filter(parent_document=parent_doc).delete()
        
        return JsonResponse({
            'success': True,
            'message': 'Document and all versions deleted successfully!'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })

@login_required
def notifications_api(request):
    """Simple notifications API"""
    return JsonResponse({
        'success': True,
        'notifications': [],
        'count': 0
    })

@login_required
def document_versions_api(request, document_id):
    """API to get document versions"""
    try:
        document = Document.objects.get(id=document_id)
        versions = document.get_all_versions()
        
        versions_data = []
        for version in versions:
            versions_data.append({
                'id': version.id,
                'version': version.version,
                'updated_at': version.updated_at.strftime('%d/%m/%Y %H:%M'),
                'created_by': version.created_by.get_full_name() or version.created_by.username,
                'file_size': version.get_file_size_display(),
                'file_url': version.file.url,
                'is_latest': version.is_latest_version()
            })
        
        return JsonResponse({
            'success': True,
            'versions': versions_data
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })

class DocumentForm(forms.Form):
    title = forms.CharField(max_length=200, widget=forms.TextInput(attrs={'class': 'form-control'}))
    file = forms.FileField(widget=forms.FileInput(attrs={'class': 'form-control'}))
    description = forms.CharField(required=False, widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}))
    category = forms.ModelChoiceField(queryset=DocumentCategory.objects.all(), widget=forms.Select(attrs={'class': 'form-control'}))
    tags = forms.ModelMultipleChoiceField(queryset=DocumentTag.objects.all(), required=False, widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}))

@login_required
def document_update_view(request, document_id):
    """Dedicated view for updating documents"""
    if request.method == 'POST':
        try:
            document = Document.objects.get(id=document_id)
            file = request.FILES.get('file')
            description = request.POST.get('description', '')
            change_note = request.POST.get('change_note', '')
            
            if file:
                # Tắt trạng thái current của tất cả file cũ
                document.file_versions.update(is_current=False)
                
                # Tạo phiên bản file mới
                version_number = document.get_latest_version_number() + 1
                file_version = DocumentFileVersion.objects.create(
                    document=document,
                    file=file,
                    file_name=file.name,
                    file_size=file.size,
                    file_type=file.name.split('.')[-1].lower() if '.' in file.name else '',
                    uploaded_by=request.user,
                    is_current=True,
                    change_note=change_note or f'Cập nhật lên v{version_number}',
                    version_number=version_number
                )
                
                # Cập nhật file hiện tại của document
                document.file = file
                document.description = description or document.description
                document.created_by = request.user  # Cập nhật người upload gần nhất
                document.updated_at = timezone.now()
                document.file_size = file.size
                document.file_type = file_version.file_type
                
                document.save()
                
                messages.success(request, f'Tài liệu đã được cập nhật thành công! Phiên bản mới: v{version_number}')
                return redirect('documents_management')
            else:
                messages.error(request, 'Vui lòng chọn file để cập nhật.')
        except Exception as e:
            messages.error(request, f'Lỗi khi cập nhật tài liệu: {str(e)}')
    
    return redirect('documents_management')

@login_required
@require_http_methods(["POST"])
def document_update(request, document_id):
	try:
		parent_doc = Document.objects.get(id=document_id)
		new_file = request.FILES.get('file')
		description = request.POST.get('description', '')

		if not new_file:
			messages.error(request, 'Vui lòng chọn file để cập nhật.')
			return redirect('documents_management')

		# Đặt title theo tên file mới (không đuôi)
		base_title = os.path.splitext(new_file.name)[0]

		new_doc = Document(
			title=base_title,
			file=new_file,
			description=description or parent_doc.description,
			category=parent_doc.category,
			created_by=request.user,
			parent_document=parent_doc,
			version=None
		)
		# copy các trường "di sản"
		new_doc.access_level = getattr(parent_doc, 'access_level', 'public')
		new_doc.allowed_roles = getattr(parent_doc, 'allowed_roles', 'all')
		new_doc.status = getattr(parent_doc, 'status', 'published')
		new_doc.slug = ''  # để model tự tạo slug mới duy nhất

		new_doc.save()
		new_doc.tags.set(parent_doc.tags.all())

		messages.success(request, f'Đã tạo phiên bản mới v{new_doc.version} cho tài liệu.')
		return redirect('documents_management')

	except Exception as e:
		messages.error(request, f'Lỗi khi cập nhật tài liệu: {e}')
		return redirect('documents_management')


@login_required
def document_detail_by_id(request, pk):
	document = get_object_or_404(Document, pk=pk, is_active=True)
	return redirect('document_detail', slug=document.slug)

@login_required
@require_http_methods(["GET", "POST"])
def staff_api_list(request):
    """List/Create EmployeeProfile. Trả JSON.
    GET: ?search=&project=&role=&active=
    POST: name, msnv, ... (JSON hoặc form)
    """
    if request.method == 'GET':
        qs = EmployeeProfile.objects.all()
        search = request.GET.get('search')
        role = request.GET.get('role')
        project = request.GET.get('project')
        active = request.GET.get('active')
        if search:
            qs = qs.filter(Q(name__icontains=search) | Q(msnv__icontains=search) | Q(phone__icontains=search))
        if role:
            qs = qs.filter(role=role)
        if project:
            qs = qs.filter(current_project_id=project)
        if active in ['true','false','1','0']:
            qs = qs.filter(is_active=active in ['true','1'])
        data = [model_to_dict(x) for x in qs]
        return JsonResponse({'success': True, 'results': data})
    # POST create
    payload = request.POST or request.GET
    if request.content_type == 'application/json':
        try:
            payload = json.loads(request.body.decode('utf-8'))
        except Exception:
            payload = {}
    try:
        emp = EmployeeProfile.objects.create(
            name=payload.get('name','').strip(),
            cccd=payload.get('cccd') or None,
            msnv=payload.get('msnv','').strip(),
            phone=payload.get('phone') or None,
            birth_date=payload.get('birthDate') or None,
            hometown=payload.get('hometown') or None,
            role=payload.get('role') or 'employee',
            education=payload.get('education') or None,
            dependents=int(payload.get('dependents') or 0),
            bank_account=payload.get('bankAccount') or None,
            bank=payload.get('bank') or None,
            join_date=payload.get('joinDate') or None,
            current_project_id=payload.get('currentProject') or None,
            project_position=payload.get('projectPosition') or None,
            certificates=payload.get('certificates') or None,
            avatar_data_url=payload.get('avatar') or None,
            is_active=True,
        )
        return JsonResponse({'success': True, 'data': model_to_dict(emp)}, status=201)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)

@login_required
@require_http_methods(["GET", "PUT", "PATCH", "DELETE"])
def staff_api_detail(request, employee_id):
    try:
        emp = EmployeeProfile.objects.get(pk=employee_id)
    except EmployeeProfile.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Not found'}, status=404)
    if request.method == 'GET':
        return JsonResponse({'success': True, 'data': model_to_dict(emp)})
    if request.method in ['PUT','PATCH']:
        payload = {}
        if request.content_type == 'application/json':
            try:
                payload = json.loads(request.body.decode('utf-8'))
            except Exception:
                payload = {}
        else:
            payload = request.POST
        for field, key in [
            ('name','name'),('cccd','cccd'),('msnv','msnv'),('phone','phone'),
            ('hometown','hometown'),('role','role'),('education','education'),
            ('bank_account','bankAccount'),('bank','bank'),('project_position','projectPosition'),
            ('certificates','certificates'),('avatar_data_url','avatar')
        ]:
            if key in payload:
                setattr(emp, field, payload.get(key))
        if 'dependents' in payload:
            emp.dependents = int(payload.get('dependents') or 0)
        if 'currentProject' in payload:
            emp.current_project_id = payload.get('currentProject') or None
        if 'isActive' in payload:
            emp.is_active = bool(payload.get('isActive'))
        if 'birthDate' in payload:
            emp.birth_date = payload.get('birthDate') or None
        if 'joinDate' in payload:
            emp.join_date = payload.get('joinDate') or None
        try:
            emp.save()
            return JsonResponse({'success': True, 'data': model_to_dict(emp)})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)
    # DELETE
    emp.delete()
    return JsonResponse({'success': True})