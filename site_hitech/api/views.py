from django.http import JsonResponse
from .models import Course, Post, Category, Comment, ContactSettings, Tag, SiteSettings, AboutPage, HomePageSettings, UserProfile, Project, ProjectFile, ProjectProgress, CourseCategory, Equipment, PublicProject, Company, NDTMethod
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
from datetime import timedelta
import shutil

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
    """Trang quản lý nhân viên"""
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
        'coming_soon': True
    }
    return render(request, 'erp_modules/staff.html', context)

@login_required
def attendance_management(request):
    """Trang quản lý chấm công"""
    context = {
        'title': 'Quản lý chấm công',
        'module_name': 'Quản lý chấm công',
        'description': 'Hệ thống chấm công tự động, theo dõi giờ làm việc và tính lương nhân viên.',
        'features': [
            'Chấm công bằng QR Code/NFC',
            'Theo dõi giờ vào/ra',
            'Tính toán giờ làm thêm',
            'Báo cáo chấm công theo tháng',
            'Quản lý nghỉ phép và nghỉ việc'
        ],
        'coming_soon': True
    }
    return render(request, 'erp_modules/attendance.html', context)

@login_required
def equipment_management(request):
    """Trang quản lý thiết bị"""
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
    """Trang quản lý chất lượng"""
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
        'coming_soon': True
    }
    return render(request, 'erp_modules/quality.html', context)

@login_required
def analytics_management(request):
    """Trang phân tích phát triển"""
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