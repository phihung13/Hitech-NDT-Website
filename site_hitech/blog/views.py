from django.shortcuts import render, get_object_or_404, redirect
from api.models import Post, Category, Tag, Comment
from django.core.paginator import Paginator
from django.db.models import Count
from django.contrib import messages

def blog_list(request):
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
        'posts': page_obj,
        'categories': categories,
        'tags': tags,
        'recent_posts': recent_posts,
    }
    return render(request, 'blog_list.html', context)

def blog_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id, published=True)
    
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
    return render(request, 'blog_detail.html', context)

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
    return render(request, 'blog_category.html', context)

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
            models.Q(title__icontains=query) |
            models.Q(content__icontains=query) |
            models.Q(excerpt__icontains=query)
        ).distinct()

        # Tìm kiếm trong khóa học
        from api.models import Course
        courses = Course.objects.filter(
            models.Q(title__icontains=query) |
            models.Q(description__icontains=query)
        ).distinct()
    else:
        posts = Post.objects.none()
        courses = Course.objects.none()

    context = {
        'query': query,
        'posts': posts,
        'courses': courses,
    }
    return render(request, 'search_results.html', context)

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