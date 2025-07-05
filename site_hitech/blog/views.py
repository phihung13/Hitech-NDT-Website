from django.shortcuts import render, get_object_or_404, redirect
from api.models import Post, Category, Tag, Comment
from api.forms import PostForm
from api.seo_analyzer import SEOAnalyzer
from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.text import slugify
import json

def blog_list(request):
    # Lọc theo chuyên mục nếu có
    category_slug = request.GET.get('category')
    if category_slug:
        posts = Post.objects.filter(published=True, category__slug=category_slug).order_by('-created_at')
    else:
        posts = Post.objects.filter(published=True).order_by('-created_at')
    
    # Phân trang
    paginator = Paginator(posts, 6)  # 6 bài viết mỗi trang
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Lấy danh mục và tags cho sidebar
    categories = Category.objects.annotate(post_count=Count('post'))
    tags = Tag.objects.all()
    recent_posts = Post.objects.filter(published=True).order_by('-created_at')[:5]
    
    context = {
        'posts': page_obj.object_list,
        'page_obj': page_obj,
        'categories': categories,
        'tags': tags,
        'recent_posts': recent_posts,
    }
    return render(request, 'blog/blog_list.html', context)

def blog_detail(request, category_slug, post_slug):
    from api.models import Post, Category
    post = get_object_or_404(Post, slug=post_slug, published=True, category__slug=category_slug)

    # Tăng lượt xem
    post.view_count += 1
    post.save()
    
    # Lấy bài viết liên quan
    related_posts = Post.objects.filter(category=post.category, published=True).exclude(id=post.id)[:3]
    
    # Lấy bình luận
    comments = post.comments.filter(is_active=True)
    
    # Lấy danh mục và tags cho sidebar
    categories = Category.objects.annotate(post_count=Count('post'))
    tags = Tag.objects.all()
    recent_posts = Post.objects.filter(published=True).order_by('-created_at')[:5]
    
    context = {
        'post': post,
        'related_posts': related_posts,
        'comments': comments,
        'categories': categories,
        'tags': tags,
        'recent_posts': recent_posts,
    }
    return render(request, 'blog/blog_detail.html', context)

def blog_category(request, category_slug):
    category = get_object_or_404(Category, slug=category_slug)
    posts = Post.objects.filter(category=category, published=True).order_by('-created_at')
    
    # Phân trang
    paginator = Paginator(posts, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Lấy danh mục và tags cho sidebar
    categories = Category.objects.annotate(post_count=Count('post'))
    tags = Tag.objects.all()
    recent_posts = Post.objects.filter(published=True).order_by('-created_at')[:5]
    
    context = {
        'category': category,
        'posts': page_obj,
        'categories': categories,
        'tags': tags,
        'recent_posts': recent_posts,
    }
    return render(request, 'blog/blog_category.html', context)

def blog_tag(request, tag_slug):
    tag = get_object_or_404(Tag, slug=tag_slug)
    posts = Post.objects.filter(tags=tag, published=True).order_by('-created_at')
    
    # Phân trang
    paginator = Paginator(posts, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Lấy danh mục và tags cho sidebar
    categories = Category.objects.annotate(post_count=Count('post'))
    tags = Tag.objects.all()
    recent_posts = Post.objects.filter(published=True).order_by('-created_at')[:5]
    
    context = {
        'tag': tag,
        'posts': page_obj,
        'categories': categories,
        'tags': tags,
        'recent_posts': recent_posts,
    }
    return render(request, 'blog_tag.html', context)

def search_results(request):
    query = request.GET.get('q', '')
    if query:
        # Tìm kiếm trong bài viết
        posts = Post.objects.filter(
            published=True
        ).filter(
            Q(title__icontains=query) |
            Q(content__icontains=query) |
            Q(excerpt__icontains=query)
        ).distinct()

        # Tìm kiếm trong khóa học
        from api.models import Course
        courses = Course.objects.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query)
        ).distinct()
    else:
        posts = Post.objects.none()
        courses = Course.objects.none()

    context = {
        'query': query,
        'posts': posts,
        'courses': courses,
    }
    return render(request, 'general/search_results.html', context)

def blog_search(request):
    query = request.GET.get('q', '')
    posts = Post.objects.filter(title__icontains=query, published=True).order_by('-created_at')
    
    # Phân trang
    paginator = Paginator(posts, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Lấy danh mục và tags cho sidebar
    categories = Category.objects.annotate(post_count=Count('post'))
    tags = Tag.objects.all()
    recent_posts = Post.objects.filter(published=True).order_by('-created_at')[:5]
    
    context = {
        'query': query,
        'posts': page_obj,
        'categories': categories,
        'tags': tags,
        'recent_posts': recent_posts,
    }
    return render(request, 'blog_search.html', context)

def post_comment(request, post_id):
    print(f"DEBUG: post_id = {post_id}")
    print(f"DEBUG: request.method = {request.method}")
    print(f"DEBUG: request.POST = {request.POST}")
    
    try:
        post = get_object_or_404(Post, id=post_id)
        print(f"DEBUG: Found post = {post.title}")
    except Exception as e:
        print(f"DEBUG: Error finding post: {e}")
        messages.error(request, 'Không tìm thấy bài viết!')
        return redirect('blog_list')
    
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        content = request.POST.get('content', '').strip()
        
        print(f"DEBUG: name = '{name}', email = '{email}', content = '{content}'")
        
        # Validation
        if not name or len(name) < 2:
            messages.error(request, 'Tên phải có ít nhất 2 ký tự!')
        elif not email or '@' not in email:
            messages.error(request, 'Email không hợp lệ!')
        elif not content or len(content) < 10:
            messages.error(request, 'Nội dung bình luận phải có ít nhất 10 ký tự!')
        else:
            try:
                Comment.objects.create(
                    post=post,
                    name=name,
                    email=email,
                    content=content
                )
                messages.success(request, 'Bình luận của bạn đã được gửi thành công!')
                print(f"DEBUG: Comment created successfully")
            except Exception as e:
                print(f"DEBUG: Error creating comment: {e}")
                messages.error(request, 'Có lỗi xảy ra khi gửi bình luận. Vui lòng thử lại!')
            
    return redirect('blog_detail', category_slug=post.category.slug, post_slug=post.slug)

@login_required
def create_post(request):
    """Redirect đến Django Admin để tạo bài viết với SEO analyzer"""
    # Redirect đến admin add Post với tham số quay lại
    return redirect('/admin/api/post/add/?_changelist_filters=author__id__exact%3D' + str(request.user.id))

@login_required
def edit_post(request, post_id):
    """Trang chỉnh sửa bài viết"""
    post = get_object_or_404(Post, id=post_id)
    
    # Kiểm tra quyền chỉnh sửa
    if not request.user.is_superuser and post.author != request.user:
        messages.error(request, 'Bạn không có quyền chỉnh sửa bài viết này!')
        return redirect('blog_list')
    
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            post = form.save(commit=False)
            
            # Tạo slug mới nếu title thay đổi
            new_title = form.cleaned_data['title']
            if new_title != post.title:  # Title đã thay đổi
                base_slug = slugify(new_title)
                slug = base_slug
                counter = 1
                # Kiểm tra slug trùng lặp, loại trừ bài viết hiện tại
                while Post.objects.filter(slug=slug).exclude(id=post.id).exists():
                    slug = f"{base_slug}-{counter}"
                    counter += 1
                post.slug = slug
            
            post.save()
            form.save_m2m()
            
            messages.success(request, 'Bài viết đã được cập nhật thành công!')
            return redirect('edit_post', post_id=post.id)
    else:
        form = PostForm(instance=post)
    
    # Phân tích SEO
    seo_analyzer = SEOAnalyzer()
    seo_analysis = seo_analyzer.analyze_seo(
        title=post.title,
        meta_description=post.meta_description or '',
        content=post.content,
        keywords=post.keywords or '',
        slug=post.slug,
        featured_image=post.featured_image
    )
    
    context = {
        'form': form,
        'post': post,
        'seo_analysis': seo_analysis,
        'categories': Category.objects.all(),
        'tags': Tag.objects.all(),
    }
    return render(request, 'blog/edit_post.html', context)

@login_required
def my_posts(request):
    """Trang quản lý bài viết của tôi"""
    posts = Post.objects.filter(author=request.user).order_by('-created_at')
    
    # Tính toán thống kê
    total_views = sum(post.view_count for post in posts)
    latest_post = posts.first()
    latest_post_date = latest_post.created_at.strftime('%d/%m') if latest_post else '--'
    
    # Phân trang
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'posts': page_obj.object_list,
        'page_obj': page_obj,
        'total_views': total_views,
        'latest_post_date': latest_post_date,
    }
    return render(request, 'blog/my_posts.html', context)

@login_required
def delete_post(request, post_id):
    """Xóa bài viết"""
    post = get_object_or_404(Post, id=post_id)
    
    # Kiểm tra quyền xóa
    if not request.user.is_superuser and post.author != request.user:
        messages.error(request, 'Bạn không có quyền xóa bài viết này!')
        return redirect('my_posts')
    
    if request.method == 'POST':
        post.delete()
        messages.success(request, 'Bài viết đã được xóa thành công!')
        return redirect('my_posts')
    
    context = {
        'post': post,
    }
    return render(request, 'blog/delete_post.html', context)