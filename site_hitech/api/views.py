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