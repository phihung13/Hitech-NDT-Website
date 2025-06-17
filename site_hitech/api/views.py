from django.http import JsonResponse
from .models import Course, Post
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from .models import Post, Category, Comment, ContactSettings, Tag, SiteSettings
from .forms import PostForm, CourseForm, CommentForm
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render
from django.conf import settings
import os
# Thêm import này vào đầu file
from .models import AboutPage
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect
from .permissions import admin_required, manager_required, staff_required, permission_required
from django.contrib.auth.models import User
from .models import UserProfile

def home(request):
    latest_posts = Post.objects.filter(published=True).order_by('-created_at')[:3]
    featured_projects = Post.objects.filter(
        category__slug='du-an',
        published=True
    ).order_by('-created_at')[:3]
    
    context = {
        'latest_posts': latest_posts,
        'featured_projects': featured_projects,
    }
    return render(request, 'home.html', context)

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
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        posts = Post.objects.filter(published=True, category=category).order_by('-created_at')
    else:
        posts = Post.objects.filter(published=True).order_by('-created_at')
    
    paginator = Paginator(posts, 9)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'categories': Category.objects.all(),
    }
    
    # Giả sử template hiện đặt trong thư mục gốc templates/
    return render(request, 'blog_list.html', context)

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
    return render(request, 'blog_detail.html', context)

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
    
    return render(request, 'create_post.html', {'form': form})

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
    return render(request, 'about.html', context)

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
    return render(request, 'contact.html', context)

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
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render

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
    
    return render(request, 'login.html')

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
    }
    return render(request, 'staff_dashboard.html', context)

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

# Thêm vào cuối file views.py

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Project, ProjectFile, ProjectProgress
from .forms import ProjectFileForm, ProjectUpdateForm, ProjectCreateForm
import os
import mimetypes

@login_required
def project_detail(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    project_files = ProjectFile.objects.filter(project=project).order_by('-uploaded_at')
    progress_records = ProjectProgress.objects.filter(project=project).order_by('-last_updated')
    
    context = {
        'project': project,
        'project_files': project_files,
        'progress_records': progress_records,
        'file_form': ProjectFileForm(),
        'update_form': ProjectUpdateForm(instance=project),
    }
    return render(request, 'project_detail.html', context)

@login_required
def upload_file(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    
    if request.method == 'POST':
        form = ProjectFileForm(request.POST, request.FILES)
        if form.is_valid():
            project_file = form.save(commit=False)
            project_file.project = project
            project_file.uploaded_by = request.user
            project_file.save()
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
    project = get_object_or_404(Project, id=project_id)
    
    if request.method == 'POST':
        form = ProjectUpdateForm(request.POST, instance=project)
        if form.is_valid():
            form.save()
            return redirect('project_detail', project_id=project.id)
    
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
    return render(request, 'create_project.html', context)